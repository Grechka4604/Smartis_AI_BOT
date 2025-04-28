import json
import os



MAPPING_FILE = "file_mappings.json"


def load_mappings(output_dir):
    path = os.path.join(output_dir, MAPPING_FILE)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_mappings(mappings, output_dir):
    path = os.path.join(output_dir, MAPPING_FILE)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)