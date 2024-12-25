import json
import pandas as pd
from io import StringIO
from pathlib import Path

# Create JSON file
def createJson(filename, data, show_response = True):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        if show_response:
            print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")

# Create XML file
def createXml(filename, data, show_response = True):
    try:
        with open(filename, 'w') as file:
            file.write(data)
        if show_response:
            print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")

# Create text file
def createText(filename, data, show_response = True):
    try:
        with open(filename , 'wb') as file:
            file.write(data)
        if show_response:
            print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")

# Create Excel file
def createExcel(outputfile, *data):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            for sheetname, df in data:
                df.to_excel(writer, sheet_name=sheetname, index=False)
        print("File created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")

# Prepare output file based on the format
def prepareOutputFile(data_response, filename, format_str, sheetname = 'Sheet'):
    if format_str == "csv":
        data = pd.read_csv(StringIO(data_response.text))
        createExcel(f"{filename}.xlsx", (sheetname, data))
    elif format_str == "json":
        data = data_response.json()
        createJson(f"{filename}.json", data)
    elif format_str == "xml":
        data = data_response.text
        createXml(f"{filename}.xml", data)
        
# Create folder
def createFolder(foldername):
    try:
        Path(foldername).mkdir(parents=True, exist_ok=True)
        print(f"{foldername} folder created successfully")
    except Exception as e:
        print(f"Error creating {foldername} folder: {e}")