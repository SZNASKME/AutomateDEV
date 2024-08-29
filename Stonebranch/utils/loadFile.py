import os
import json
from pathlib import Path

def loadJson(filename='config.json'):
    # Determine the relative path to the repository root
    repo_root = Path(__file__).resolve().parent.parent.parent  # Adjust the number of '.parent' as needed to reach the repo root
    
    # Construct the full path to the JSON file
    json_path = repo_root / filename
    
    # Open and load the JSON file
    with open(json_path, 'r') as file:
        config_data = json.load(file)

    return config_data
