import copy

def apply_actions(structure, actions):
    new_structure = copy.deepcopy(structure)
    changes = []
    
    for action in actions:
        act_type = action.get("action")
        
        if act_type == "noop":
            changes.append(f"No change: {action.get('reason', 'None')}")
            continue
            
        if act_type == "clarify":
            changes.append(f"Question: {action.get('question')}")
            continue
            
        if act_type == "replace_text_globally":
            old = action["old_text"]
            new = action["new_text"]
            count = 0
            for sec in new_structure["sections"]:
                for p in sec["paragraphs"]:
                    if old in p["text"]:
                        p["text"] = p["text"].replace(old, new)
                        count += 1
            changes.append(f"Replaced {count} occurrences of '{old}' with '{new}'")
            
        if act_type == "replace_paragraph":
            pid = action["paragraph_id"]
            new_text = action["new_text"]
            new_style = action.get("style_type")
            found = False
            for sec in new_structure["sections"]:
                for p in sec["paragraphs"]:
                    if p["id"] == pid:
                        p["text"] = new_text
                        if new_style:
                            p["type"] = new_style
                        found = True
                        changes.append(f"Updated paragraph {pid}")
                        break
            if not found:
                changes.append(f"Failed to find paragraph {pid}")
                
        if act_type == "delete_paragraph":
            pid = action["paragraph_id"]
            for sec in new_structure["sections"]:
                initial_len = len(sec["paragraphs"])
                sec["paragraphs"] = [p for p in sec["paragraphs"] if p["id"] != pid]
                if len(sec["paragraphs"]) < initial_len:
                    changes.append(f"Deleted paragraph {pid}")
                    
        if act_type == "update_paragraph_style":
            pid = action["paragraph_id"]
            new_type = action["style_type"]
            found = False
            for sec in new_structure["sections"]:
                for p in sec["paragraphs"]:
                    if p["id"] == pid:
                        p["type"] = new_type
                        found = True
                        changes.append(f"Changed paragraph {pid} style to {new_type}")
                        break
            if not found:
                changes.append(f"Failed to find paragraph {pid} for style update")

        if act_type == "insert_paragraph":
            sec_id = action.get("section_id")
            new_text = action["new_text"]
            after_pid = action.get("after_paragraph_id")
            before_pid = action.get("before_paragraph_id")
            
            # Generate new PID (simple logic)
            import time
            new_pid = f"{sec_id}_new_{int(time.time()*1000)}_{len(changes)}"
            
            new_p = {"id": new_pid, "text": new_text, "type": "text"}
            
            # Find section
            target_sec = None
            for sec in new_structure["sections"]:
                if sec["id"] == sec_id:
                    target_sec = sec
                    break
            
            if target_sec:
                if after_pid:
                    try:
                        idx = next(i for i, p in enumerate(target_sec["paragraphs"]) if p["id"] == after_pid)
                        target_sec["paragraphs"].insert(idx + 1, new_p)
                        changes.append(f"Inserted paragraph after {after_pid}")
                    except StopIteration:
                        # Fallback append
                        target_sec["paragraphs"].append(new_p)
                        changes.append(f"Inserted paragraph (fallback append) in {sec_id}")
                elif before_pid:
                    try:
                        idx = next(i for i, p in enumerate(target_sec["paragraphs"]) if p["id"] == before_pid)
                        target_sec["paragraphs"].insert(idx, new_p)
                        changes.append(f"Inserted paragraph before {before_pid}")
                    except StopIteration:
                        target_sec["paragraphs"].insert(0, new_p)
                        changes.append(f"Inserted paragraph (fallback prepend) in {sec_id}")
                else:
                    # Append
                    target_sec["paragraphs"].append(new_p)
                    changes.append(f"Inserted paragraph in {sec_id}")
            else:
                changes.append(f"Failed to find section {sec_id} for insertion")
             
        if act_type == "update_style_font":
            style_name = action["style_name"]
            size = action["size_pt"]
            
            # We need to store this in structure so parser can pick it up.
            # Let's add a 'styles' dict to meta if not exists.
            if "styles" not in new_structure["meta"]:
                new_structure["meta"]["styles"] = {}
                
            new_structure["meta"]["styles"][style_name] = {
                "size_pt": size,
                "bold": action.get("bold"),
                "italic": action.get("italic"),
                "justification": action.get("justification")
            }
            changes.append(f"Updated style '{style_name}' to {size}pt")

    return new_structure, changes
