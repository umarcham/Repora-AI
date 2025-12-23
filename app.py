import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret")
    
    # CORS
    allowed_origin = os.environ.get("ALLOWED_ORIGIN", "*")
    CORS(app, resources={r"/*": {"origins": allowed_origin}})

    # Config
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data')
    
    # Ensure data directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from doc_editor.routes import doc_bp
    app.register_blueprint(doc_bp)

    @app.route('/health')
    def health():
        return jsonify({"status": "ok"})

    return app

app = create_app()

if __name__ == '__main__':
    # Run server
    # Must use 0.0.0.0 so Docker container can access via host.docker.internal
    # Port 5000 is often taken by AirPlay (AirTunes) on Mac. Using 5001 to be safe.
    app.run(host='0.0.0.0', debug=True, port=5001)
