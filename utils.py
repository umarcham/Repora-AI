import json

def to_json(data):
    return json.dumps(data, indent=2)

def from_json(json_str):
    return json.loads(json_str)
