# Schemas for validation

EDIT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "oneOf": [
            {
                "properties": {
                    "action": {"const": "replace_paragraph"},
                    "section_id": {"type": "string"},
                    "paragraph_id": {"type": "string"},
                    "new_text": {"type": "string"},
                    "style_type": {"enum": ["h1", "h2", "h3", "text", "list_item", "title"]}
                },
                "required": ["action", "section_id", "paragraph_id", "new_text"]
            },
            {
                "properties": {
                    "action": {"const": "insert_paragraph"},
                    "section_id": {"type": "string"},
                    "after_paragraph_id": {"type": "string"},
                    "before_paragraph_id": {"type": "string"},
                    "new_text": {"type": "string"}
                },
                "required": ["action", "section_id", "new_text"]
            },
            {
                "properties": {
                    "action": {"const": "delete_paragraph"},
                    "section_id": {"type": "string"},
                    "paragraph_id": {"type": "string"}
                },
                "required": ["action", "section_id", "paragraph_id"]
            },
             {
                "properties": {
                    "action": {"const": "update_table_cell"},
                    "table_id": {"type": "string"},
                    "row": {"type": "integer"},
                    "col": {"type": "integer"},
                    "new_text": {"type": "string"}
                },
                "required": ["action", "table_id", "row", "col", "new_text"]
            },
            {
                "properties": {
                    "action": {"const": "update_paragraph_style"},
                    "section_id": {"type": "string"},
                    "paragraph_id": {"type": "string"},
                    "style_type": {"enum": ["h1", "h2", "h3", "text", "list_item", "title"]}
                },
                "required": ["action", "section_id", "paragraph_id", "style_type"]
            },
            {
                "properties": {
                    "action": {"const": "replace_text_globally"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                    "case_sensitive": {"type": "boolean"}
                },
                "required": ["action", "old_text", "new_text"]
            },
            {
                "properties": {
                    "action": {"const": "rewrite_section"},
                    "section_id": {"type": "string"},
                    "style": {"enum": ["simplify", "concise", "formal", "expand"]},
                    "max_sentences": {"type": "integer"}
                },
                "required": ["action", "section_id"]
            },
            {
                "properties": {
                    "action": {"const": "clarify"},
                    "question": {"type": "string"}
                },
                "required": ["action", "question"]
            },
            {
                "properties": {
                    "action": {"const": "update_style_font"},
                    "style_name": {"type": "string"},
                    "size_pt": {"type": "integer"},
                    "bold": {"type": "boolean"},
                    "italic": {"type": "boolean"},
                    "justification": {"enum": ["left", "center", "right", "justified"]}
                },
                "required": ["action", "style_name", "size_pt"]
            },
            {
                "properties": {
                    "action": {"const": "noop"},
                    "reason": {"type": "string"}
                },
                "required": ["action"]
            }
        ]
    }
}
