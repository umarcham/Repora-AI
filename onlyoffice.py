import os
import json
import time

# Configuration
# For local dev with Docker on Mac, host.docker.internal is usually available.
# Otherwise user must configure their IP.
HOST_URL = os.environ.get("ONLYOFFICE_HOST_URL", "http://host.docker.internal:5000")

def get_config(doc_id, filename, user_ip, download_url, callback_url):
    """
    Generates the configuration JSON for OnlyOffice Editor.
    """
    file_ext = filename.split('.')[-1]
    
    # Generate a unique key for the document revision. 
    # In production, this should change every time the document is edited.
    # We can use doc_id + timestamp or rev_id.
    key = f"{doc_id}_{int(time.time())}"
    
    config = {
        "document": {
            "fileType": file_ext,
            "key": key,
            "title": filename,
            "url": download_url,
            "permissions": {
                "download": True,
                "edit": True,
                "print": True
            }
        },
        "documentType": "word", # 'cell' or 'slide' for others
        "editorConfig": {
            "callbackUrl": callback_url,
            "user": {
                "id": user_ip,
                "name": "User " + user_ip
            },
            "customization": {
                "forcesave": True,
                "autosave": True
            }
        }
    }
    return config

def process_callback(data, doc_id, save_path_func):
    """
    Handles the callback from OnlyOffice.
    data: dict parsed from request body
    save_path_func: function(doc_id) -> path to save
    """
    status = data.get("status")
    
    # Status 2 = Ready for saving (user closed logic) or 6 (Force save)
    if status == 2 or status == 6:
        download_url = data.get("url")
        if not download_url:
            return {"error": 0} # No error, just nothing to do
            
        # Download the file from OnlyOffice Document Server
        import requests
        try:
            resp = requests.get(download_url, stream=True)
            if resp.status_code == 200:
                # Save to revisions
                # We need to trigger a new revision in our system
                # But here we just get the path
                pass
                # The caller (route) should handle the actual saving to storage
                # returning the content context
                return {
                    "action": "save",
                    "content": resp.content,
                    "filename": "onlyoffice_update.docx"
                }
        except Exception as e:
            print(f"Error downloading from OnlyOffice: {e}")
            return {"error": 1}
            
    return {"error": 0}
