import os
import shutil
import json
import time
from werkzeug.utils import secure_filename
from doc_editor import parsers, utils

BASE_DIR = os.path.join(os.getcwd(), 'data')

def create_document(file):
    doc_id = str(int(time.time() * 1000)) # Simple ID
    doc_dir = os.path.join(BASE_DIR, doc_id)
    os.makedirs(doc_dir, exist_ok=True)
    os.makedirs(os.path.join(doc_dir, 'revisions'), exist_ok=True)
    
    original_path = os.path.join(doc_dir, 'original.docx')
    file.save(original_path)
    
    # Initial Parse
    structure = parsers.parse_docx_to_structure(original_path)
    with open(os.path.join(doc_dir, 'structure.json'), 'w') as f:
        json.dump(structure, f)
        
    # Initial Revision 0
    shutil.copy(original_path, os.path.join(doc_dir, 'revisions', '0.docx'))
    
    # Init History
    history = [{
        "rev_id": "0",
        "timestamp": time.time(),
        "instruction": "Original Upload",
        "changes": []
    }]
    with open(os.path.join(doc_dir, 'history.json'), 'w') as f:
        json.dump(history, f)
        
    return doc_id

def get_structure(doc_id):
    path = os.path.join(BASE_DIR, doc_id, 'structure.json')
    if not os.path.exists(path):
        raise FileNotFoundError()
    with open(path, 'r') as f:
        return json.load(f)

def save_revision(doc_id, structure, changes, instruction):
    doc_dir = os.path.join(BASE_DIR, doc_id)
    rev_id = str(int(time.time() * 1000))
    
    # Save JSON structure
    with open(os.path.join(doc_dir, 'structure.json'), 'w') as f:
        json.dump(structure, f)
        
    # Create DOCX Patch
    # We base off 'original.docx' and apply edits? 
    # OR we base off the LAST revision?
    # Ideally base off the previous revision to keep accumulation? 
    # Or always original + current structure? 
    # parsers.patch_docx_from_structure implementation currently works on *an* input file.
    # If we use original.docx, we lose previous structural changes if our pacther isn't perfect.
    # Let's use original to serve as the template, assuming structure has full state.
    original_path = os.path.join(doc_dir, 'original.docx')
    rev_path = os.path.join(doc_dir, 'revisions', f'{rev_id}.docx')
    
    parsers.patch_docx_from_structure(original_path, structure, rev_path)
    
    # Update History
    hist_path = os.path.join(doc_dir, 'history.json')
    with open(hist_path, 'r') as f:
        history = json.load(f)
        
    history.append({
        "rev_id": rev_id,
        "timestamp": time.time(),
        "instruction": instruction,
        "changes": changes
    })
    
    # Keep only last 10
    if len(history) > 10:
        history = history[-10:]
        
    with open(hist_path, 'w') as f:
        json.dump(history, f)
        
    return rev_id

def get_latest_revision_id(doc_id):
    hist_path = os.path.join(BASE_DIR, doc_id, 'history.json')
    if not os.path.exists(hist_path):
        return "0"
    with open(hist_path, 'r') as f:
        history = json.load(f)
    if not history:
        return "0"
    return history[-1]['rev_id']

def get_revision_path(doc_id, rev_id):
    return os.path.join(BASE_DIR, doc_id, 'revisions', f'{rev_id}.docx')
