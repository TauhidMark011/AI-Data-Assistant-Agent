#Schema Dispatcher Logic — dynamically map input dataset paths to their schema files.
import json

def load_schema_by_dataset(file_path: str) -> dict:
    if "imdb" in file_path.lower():
        schema_file = "schemas/imdb_schema.json"
    elif "cafe" in file_path.lower():
        schema_file = "schemas/cafe_schema.json"
    else:
        raise ValueError("No matching schema found for dataset.")

    with open(schema_file, 'r', encoding='utf-8') as f:
        return json.load(f)
