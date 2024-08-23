import os
import json
from pathlib import Path

def load_json(filename='config.json'):
    # Determine the default path based on the script's directory
    relative_path = Path(f'{filename}')
    base_dir = Path(__file__).resolve().parent
    json_path = base_dir / relative_path
    default_path = os.path.join(os.path.dirname(__file__), filename)
    # Open and load the JSON file
    with open(json_path, 'r') as file:
        config_data = json.load(file)

    return config_data
