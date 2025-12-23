import os
import requests
import json
from jsonschema import validate, ValidationError
from doc_editor.models import EDIT_SCHEMA

GEMINI_API_KEY = "gemini_api_key"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def get_edit_actions(instruction, full_structure, context_pid=None):
    # Context trimming logic
    # If context_pid is provided, find it and grab neighbors.
    # Else send simplified structure.
    
    doc_context = full_structure # Start with full
    if context_pid:
        # TODO: Implement context windowing
        pass
        
    system_prompt = (
        "System: You are DocEdit Assistant. You will receive (1) a short user instruction, and "
        "(2) a JSON document_extract with document structure. "
        "Return ONLY a JSON array of edit action objects sticking to EDIT_SCHEMA. "
        "Supported actions: replace_paragraph, insert_paragraph, delete_paragraph, update_table_cell, "
        "replace_text_globally, rewrite_section, update_paragraph_style, update_style_font, clarify, noop. "
        "\nIMPORTANT CONTENT GENERATION RULES (STRICT):\n"
        "1. **STYLE DEFINITIONS**: If the user asks to change font size/style (e.g. 'Heading 1 size 16'), use `update_style_font`.\n"
        "   - `style_name` options: 'Heading 1', 'Heading 2', 'Heading 3', 'Normal', 'Title'.\n"
        "   - Example: `{\"action\": \"update_style_font\", \"style_name\": \"Heading 1\", \"size_pt\": 16, \"justification\": \"center\"}`.\n"
        "2. **NO META-DESCRIPTIONS**: Write current report content directly. Never say 'Here is the section...'.\n"
        "2. **ANTI-PLACEHOLDER RULE**: YOU ARE STRICTLY FORBIDDEN from using brackets like '[Insert Date]', '[Professor Name]'.\n"
        "   - **CREATIVE REALISM**: Do NOT use 'John Doe', 'Jane Smith', or 'University of Technology'. Invent SPECIFIC names (e.g., 'Dr. Aris Thorne', 'Prof. Elena Vossen', 'Institute of Advanced Systems').\n"
        "   - **EXCEPTIONS**: For **Certificates** or **Letters** where a name is CRITICAL, use the 'clarify' action. For *Reports*, always invent.\n"
        "3. **CITATION QUALITY**: \n"
        "   - **DO NOT** use weak citations like 'Smith et al. (2023)'.\n"
        "   - **MUST USE** detailed formats: 'Smith, J., & Doe, A. (2023). title. *journal/conference name*, volume(issue).'\n"
        "4. **TECHNICAL DEPTH & SPECIFICITY (CRITICAL)**:\n"
        "   - **NO GENERIC TECH**: Never just say 'database' or 'backend'. Specify versions: 'PostgreSQL 15', 'Python 3.11 with FastAPI', 'TensorFlow 2.14'.\n"
        "   - **MECHANISM OF ACTION**: Explain **HOW** it works. (e.g., 'The Feedback Engine analyzes error patterns using Cosine Similarity on TF-IDF vectors...').\n"
        "   - **JUSTIFY CHOICES**: 'Redis was selected for sub-millisecond session caching...'.\n"
        "   - **VISUALS OVER TEXT**: For 'Architecture', you **MUST** generate a **MERMAID** diagram (graph TD). Format:\n"
        "     ```mermaid\n"
        "     graph TD; A[User] --> B[System];\n"
        "     ```\n"
        "5. **SENTENCE VARIETY**:\n"
        "   - **BAN REPETITION**: It is UNACCEPTABLE to start 3 sentences with 'The system...'.\n"
        "   - **VARY STRUCTURE**: Use 'To achieve X, ...', 'By leveraging Y, ...', 'Crucially, the module...'.\n"
        "   - **ACTIVE VOICE**: Use strong verbs.\n"
        "6. **FORMATTING RULES**:\n"
        "   - **NO MARKDOWN HEADERS**: PROHIBITED: `## Title`. You MUST use the JSON `insert_paragraph` with `style_type='h1'` (or h2/h3).\n"
        "   - **BOLDING**: Use bold keys (`**key**`) but NOT for full lines.\n"
        "   - **DO NOT** wrap entire headers or list items in bold. Only bold specific keywords.\n"
        "   - Correct: `* **Key Point**: Description`\n"
        "   - Incorrect: `** * Key Point: Description**` (This breaks the parser)\n"
        "   - Use standard markdown lists (`*` or `1.`).\n"
        "6. **SECTION-SPECIFIC RULES**:\n"
        "   - **LITERATURE SURVEY**: Compare at least 3 distinct approaches. \n"
        "   - **REQUIREMENTS**: Make them testable and specific to the user's likely topic.\n"
        "   - **ADMINISTRATIVE**: For 'Certificate', 'Declaration', or 'Acknowledgement', write standard academic boilerplate text if empty.\n"
        "7. **Format**: Use 'style_type': 'list_item' for any lists.\n"
        "8. **Direct Execution**: Write the actual report content, not guidelines.\n"
        "\nSCHEMA RULES:\n"
        "- **KEY NAMES**: Always use 'action' (NOT 'op', 'operation', or 'command').\n"
        "- Use 'new_text' for replacements/insertions.\n"
        "- 'section_id' required for paragraph actions.\n"
        "-For 'clarify', use 'question' (NOT 'prompt').\n"
        "- For 'update_paragraph_style', use 'style_type' (NOT 'new_type'). Enum: h1, h2, h3, list_item.\n"
        "- Do not return markdown code fences. JSON only.\n"
    )
    
    prompt = f"User Instruction: {instruction}\n\nDocument Extract: {json.dumps(doc_context)}"
    
    # Mock response if no API Key (for testing/safety)
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
         # Fallback mock for testing
         if "Acme" in instruction:
             return [{"action":"replace_text_globally","old_text":"Acme","new_text":"AcmeCorp","case_sensitive":False}]
         return [{"action": "noop", "reason": "API Key missing"}]

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": system_prompt + "\n\n" + prompt}]
        }],
        "generationConfig": {
            "temperature": 0.4, # Slightly higher for creativity/length
            "maxOutputTokens": 8192,
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Gemini API Error: {response.text}")
        
    result = response.json()
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
        print(f"DEBUG: RAW LLM RESPONSE: \n{text}\n-------------------")
        
        # Smart Extraction: Find the outer brackets of the JSON list
        # This preserves ``` inside the JSON strings (for mermaid etc)
        start_idx = text.find('[')
        end_idx = text.rfind(']')
        
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx : end_idx + 1]
        else:
            # Fallback if no brackets found (rare)
            pass
            
        actions = json.loads(text)
        
        # ROBUSTNESS FIX: Auto-correct common LLM schema errors
        for action in actions:
            # Fix commonly hallucinated 'op' key
            if 'op' in action and 'action' not in action:
                print("DEBUG: Auto-correcting 'op' to 'action'")
                action['action'] = action.pop('op')

            if action.get('action') == 'clarify' and 'prompt' in action and 'question' not in action:
                print("DEBUG: Auto-correcting 'prompt' to 'question' in clarify action")
                action['question'] = action.pop('prompt')

            # Fix justification enum
            if action.get('action') == 'update_style_font' and action.get('justification') == 'justify':
                action['justification'] = 'justified'
        
        # Validate
        validate(instance=actions, schema=EDIT_SCHEMA)
        
        return actions
    except (json.JSONDecodeError) as e:
        # Handle truncation or malformed JSON gracefully
        return [{
            "action": "noop", 
            "reason": "The AI response was too long and got cut off. Please try generating the report section-by-section (e.g., 'Generate Introduction', then 'Generate Objective') to avoid size limits."
        }]
    except (KeyError, IndexError, ValidationError) as e:
        # Fallback to verify if it returned a clarify naturally?
        raise Exception(f"Invalid LLM Response: {e}")
