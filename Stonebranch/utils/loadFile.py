import os
import json
from pathlib import Path

def loadJson(filename='config.json', parent_dir_level=3):
    # Determine the relative path to the repository root
    repo_root = Path(__file__).resolve()  # Adjust the number of '.parent' as needed to reach the repo root
    
    for _ in range(parent_dir_level):
        repo_root = repo_root.parent
    # Construct the full path to the JSON file
    json_path = repo_root / filename
    
    # Open and load the JSON file
    with open(json_path, 'r') as file:
        config_data = json.load(file)

    return config_data
