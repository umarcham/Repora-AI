# AI DOCX Editor MVP

A production-ready web application to edit DOCX files using natural language instructions powered by Gemini.

## Features
- **Upload**: Support for `.docx` files.
- **Preview**: Two-pane interface with editable preview.
- **AI Editing**: "Make paragraph 1 bold", "Rewrite section 3", "Replace 'Acme' with 'AcmeCorp'".
- **Download**: Get the modified `.docx` file.
- **Undo/History**: Track revisions (MVP limits).

## Setup

1.  **Clone & Install**
    ```bash
    git clone <repo_url>
    cd ai-docx-editor
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment**
    ```bash
    cp .env.example .env
    # Edit .env and set GEMINI_API_KEY
    ```

3.  **Run Locally**
    ```bash
    flask run
    # Open http://localhost:5000
    ```

## Development
- Application logic is in `doc_editor/`.
- Frontend assets in `static/`.
- Run tests: `pytest`.

## Deployment
Procfile is included for Heroku/Render.
```bash
gunicorn wsgi:app
```
