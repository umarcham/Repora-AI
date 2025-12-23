# Runbook: Testing AI DOCX Editor

## Local Setup
1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set API Key (optional for mock test).

## Running Tests
Run basic verification:
```bash
pytest
```

## Running the App
```bash
flask run
```

## Manual Verification Steps
1. Open http://localhost:5000
2. Upload a simple `.docx` file.
3. Verify text appears in the right pane.
4. Type "Replace all occurrences of 'the' with 'THE'" in instruction box.
5. Click **Edit with AI**.
6. Wait for process.
7. Verify text updates in logic.
8. Click **Download DOCX**.
9. Open downloaded file and check changes.
