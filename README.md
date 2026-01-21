# Repora: AI-Powered DOCX Report Generator

Repora is a high-performance web application designed to automate and enhance the creation of professional reports. Leveraging the power of Gemini, Repora allows users to edit and generate complex DOCX files using intuitive natural language instructions.

## 🚀 Key Features

- **Intuitive AI Editing**: Edit documents using commands like *"Make paragraph 1 bold"*, *"Rewrite the executive summary to be more persuasive"*, or *"Replace all instances of 'Acme' with 'AcmeCorp'"*.
- **Autonomous Agent Orchestration**: A multi-agent system that routes requests to specialized agents for content generation, formatting, and visual elements.
- **Batch Report Generation**: Generate comprehensive reports from scratch based on a topic or research prompt.
- **Real-time Preview**: Interactive two-pane interface with a live synchronized preview of changes.
- **Rich Document Support**: Advanced structural parsing and application logic for complex `.docx` manipulations.
- **Version Control & History**: Track revisions and maintain a history of edits for easy rollbacks.

## 🛠️ Tech Stack

- **Backend**: Python / Flask
- **AI Core**: Google Gemini (Direct API Integration)
- **Document Engine**: Python-docx, custom structural parsers
- **Frontend**: Vanilla JS, CSS (Responsive & Modern)
- **Deployment**: Dockerized, ready for Heroku/Render/AWS

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.9+
- Gemini API Key

### 2. Local Installation
```bash
# Clone the repository
git clone <repo_url>
cd briefdeck

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```bash
cp .env.example .env
# Open .env and add your GEMINI_API_KEY
```

### 4. Running the Application
```bash
flask run --port=5001
# Navigate to http://localhost:5001
```

## 🏗️ Architecture

For a deep dive into the system design, agent orchestration, and data flow, please refer to the **[System Architecture Documentation](ARCHITECTURE.md)**.

## 🧪 Development

- Core logic resides in `doc_editor/`.
- Frontend assets are in `static/`.
- Run tests: `pytest`.

---

*Repora: Transforming natural language into professional documents.*
