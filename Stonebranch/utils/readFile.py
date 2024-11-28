
import json
import pandas as pd
from pathlib import Path


def loadJson(filename='config.json', parent_dir_level=3, *dirs):
    repo_root = Path(__file__).resolve()
    for _ in range(parent_dir_level):
        repo_root = repo_root.parent
    if dirs:
        for dir in dirs:
            repo_root = repo_root.joinpath(dir)
    json_path = repo_root / filename
    try:
        with open(json_path, 'r') as file:
            config_data = json.load(file)
        print(f"{filename} loaded successfully")
        return config_data
    except Exception as e:
        print(f"Error loading {json_path}: {e}")
        return None

def loadText(filename='config.txt', parent_dir_level=3, *dirs):
    repo_root = Path(__file__).resolve()
    for _ in range(parent_dir_level):
        repo_root = repo_root.parent
    if dirs:
        for dir in dirs:
            repo_root = repo_root.joinpath(dir)
    text_path = repo_root / filename
    try:
        with open(text_path, 'r') as file:
            text_data = file.read()
        print(f"{text_path} loaded successfully")
        return text_data
    except Exception as e:
        print(f"Error loading {text_path}: {e}")
        return None


def readCSV(filename='config.csv', parent_dir_level=3, *dirs):
    repo_root = Path(__file__).resolve()
    for _ in range(parent_dir_level):
        repo_root = repo_root.parent
    if dirs:
        for dir in dirs:
            repo_root = repo_root.joinpath(dir)
    csv_path = repo_root / filename
    
    try:
        df = pd.read_csv(csv_path)
        print(f"{csv_path} loaded successfully")
        return df
    except Exception as e:
        print(f"Error loading {csv_path}: {e}")
        return None
    
    
def readFolderTextFiles(folder_path, *file_names):
    try:
        folder = Path(folder_path)
        files = {}
        for file_name in file_names:
            file_path = folder / file_name
            with open(file_path, 'r') as file:
                files[file_name] = file.readlines()
            print(f"{file_path} loaded successfully")
        return files
    except Exception as e:
        print(f"Error loading files from {folder_path}: {e}")
        return None