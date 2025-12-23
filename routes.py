from flask import Blueprint, request, jsonify, send_file, current_app, abort, url_for
import os
import time
import requests
from werkzeug.utils import secure_filename
from doc_editor import storage, parsers, llm, applyer, pdf_gen, onlyoffice

doc_bp = Blueprint('doc', __name__)

# --- OnlyOffice Routes ---

@doc_bp.route('/doc/<doc_id>/onlyoffice/config')
def get_onlyoffice_config(doc_id):
    # Requirement: Return JSON config for OnlyOffice
    # We need to provide the URL where the Docker container can download the file from US.
    # Since we are running on host, and docker is container, we need external URL.
    
    # For MVP, assume the user configured host alias or is using public IP.
    # We will construct a URL using `request.host_url` but replaced with HOST_URL config if set.
    
    # For MVP, assume the user configured host alias or is using public IP.
    # We will construct a URL using `request.host_url` but replaced with HOST_URL config if set.
    
    # detected IP from previous step: 192.168.0.2
    # This is required because 'localhost' refers to the container itself inside Docker.
    # 'host.docker.internal' often works but can be flaky. IP is safest for local dev.
    # Port changed to 5001 to avoid AirPlay conflict.
    # REVISION: Reverting to explicit IP as host.docker.internal failed for user.
    # Updated IP for current session
    base_url = "http://192.168.0.2:5001"
    
    download_url = f"{base_url}/doc/{doc_id}/raw"
    callback_url = f"{base_url}/doc/{doc_id}/onlyoffice/callback"
    
    print(f"DEBUG: OnlyOffice Config - Download URL: {download_url}")
    print(f"DEBUG: OnlyOffice Config - Callback URL: {callback_url}")
    
    # Filename
    filename = "document.docx" # Default
    
    config = onlyoffice.get_config(
        doc_id, 
        filename, 
        request.remote_addr, 
        download_url, 
        callback_url
    )
    return jsonify(config)

@doc_bp.route('/doc/<doc_id>/onlyoffice/callback', methods=['POST'])
def onlyoffice_callback(doc_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": 0})
        
    result = onlyoffice.process_callback(data, doc_id, None)
    
    if result.get("action") == "save":
        content = result["content"]
        # Save as new revision
        storage.save_revision(doc_id, content, f"Edited in OnlyOffice")
        # Note: This might create concurrency issues if frontend is outdated.
        
    return jsonify({"error": 0})

@doc_bp.route('/doc/<doc_id>/raw')
def get_raw_doc(doc_id):
    # Helper to serve the latest DOCX for OnlyOffice
    rev_id = storage.get_latest_revision_id(doc_id)
    if rev_id == "0":
         path = storage.get_revision_path(doc_id, "0")
         # Fallback check
         if not os.path.exists(path):
             path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc_id, 'original.docx')
    else:
         path = storage.get_revision_path(doc_id, rev_id)
         
    return send_file(path)


@doc_bp.route('/doc/<doc_id>/preview.pdf')
def get_pdf_preview(doc_id):
    # Determine which revision? Default to 'original' or 'latest'?
    # Requirement: "Apply edits to DOCX... then regenerate the PDF preview"
    # So we probably want the LATEST revision.
    
    # Get latest revision ID from history or conventions
    # storage needs a helper `get_latest_revision_path(doc_id)`
    
    # For MVP, we can read history.
    try:
        rev_id = storage.get_latest_revision_id(doc_id)
        if rev_id == "0":
             docx_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc_id, 'original.docx') # or revs/0.docx
             docx_path = storage.get_revision_path(doc_id, "0")
        else:
             docx_path = storage.get_revision_path(doc_id, rev_id)

        # Generate PDF
        # We store PDF in a 'previews' folder or temp?
        # Let's verify if PDF exists for this rev_id to cache it.
        pdf_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], doc_id, 'previews')
        pdf_name = f"{rev_id}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_name)
        
        if not os.path.exists(pdf_path):
             # Generate
             generated_path = pdf_gen.convert_to_pdf(docx_path, pdf_dir)
             # Rename if soffice didn't match our naming convention (soffice uses input basename)
             # pdf_gen returns actual path.
             if generated_path != pdf_path:
                 os.rename(generated_path, pdf_path)
                 
        return send_file(pdf_path)
    except Exception as e:
        current_app.logger.error(f"PDF Gen Error: {e}")
        return jsonify({"error": str(e)}), 500

@doc_bp.route('/')
def landing():
    return current_app.send_static_file('index.html')

@doc_bp.route('/app')
def index():
    return current_app.send_static_file('index1.html')

@doc_bp.route('/login')
def login():
    return current_app.send_static_file('login.html')

@doc_bp.route('/signup')
def signup():
    return current_app.send_static_file('signup.html')

@doc_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.docx'):
        # Save and parse
        doc_id = storage.create_document(file)
        structure = storage.get_structure(doc_id)
        return jsonify({"document_id": doc_id, "structure": structure})
    return jsonify({"error": "Invalid file type"}), 400

@doc_bp.route('/doc/<doc_id>/structure', methods=['GET'])
def get_structure(doc_id):
    try:
        structure = storage.get_structure(doc_id)
        return jsonify(structure)
    except FileNotFoundError:
        return jsonify({"error": "Document not found"}), 404

@doc_bp.route('/doc/<doc_id>/edit', methods=['POST'])
def edit_document(doc_id):
    data = request.json
    instruction = data.get('instruction')
    context_pid = data.get('context')
    
    if not instruction:
        return jsonify({"error": "Instruction is required"}), 400

    try:
        structure = storage.get_structure(doc_id)
        
        # Rate limiting logic could go here (using storage or redis)
        
        # Call LLM
        actions = llm.get_edit_actions(instruction, structure, context_pid)
        print(f"DEBUG: LLM Actions: {actions}")
        
        # Check for clarification
        clarify_action = next((a for a in actions if a['action'] == 'clarify'), None)
        if clarify_action:
            return jsonify({
                "status": "clarification_needed",
                "question": clarify_action['question']
            })
        
        # Validate and apply (in-memory for preview)
        new_structure, changes = applyer.apply_actions(structure, actions)
        
        # We don't save to JSON storage yet effectively, but we might want to return 
        # the predicted changes to the frontend or applied structure.
        # For the MVP flow described: "If valid, apply edits to the stored AST and generate... Patched DOCX file saved as a new revision."
        
        # Let's save the revision immediately as per requirements
        rev_id = storage.save_revision(doc_id, new_structure, changes, instruction)
        
        return jsonify({
            "status": "ok",
            "preview_html_url": f"/doc/{doc_id}/structure", # Frontend re-fetches structure
            "docx_download_url": f"/doc/{doc_id}/download/{rev_id}",
            "changes": changes,
            "actions": actions # Debugging safely
        })
        
    except Exception as e:
        current_app.logger.error(f"Edit failed: {e}")
        return jsonify({"error": str(e)}), 500

@doc_bp.route('/doc/<doc_id>/download/<rev_id>', methods=['GET'])
def download_revision(doc_id, rev_id):
    path = storage.get_revision_path(doc_id, rev_id)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return jsonify({"error": "Revision not found"}), 404

@doc_bp.route('/doc/<doc_id>/apply', methods=['POST'])
def apply_manual_edits(doc_id):
    # This endpoint is strictly if the user manually edited the contenteditable HTML
    # and wants to sync it back to the backend structure.
    # For MVP, if we rely on LLM edits primarily, this might be a "save" feature.
    # However, the requirement says: "backend must accept direct text edits from the frontend"
    
    # We'll expect the full structure back or just the modified paragraphs.
    # Receiving full structure is safer for MVP consistency.
    data = request.json
    new_structure = data.get('structure')
    if not new_structure:
         return jsonify({"error": "Structure required"}), 400
         
    rev_id = storage.save_revision(doc_id, new_structure, [{"type": "manual", "desc": "User manual edit"}], "Manual Edit")
    return jsonify({"status": "ok", "docx_download_url": f"/doc/{doc_id}/download/{rev_id}"})
