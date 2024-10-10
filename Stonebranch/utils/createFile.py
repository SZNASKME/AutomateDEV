import json
import pandas as pd
from io import StringIO

def createJson(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")
        
def createXml(filename, data):
    try:
        with open(filename, 'w') as file:
            file.write(data)
        print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")
        
def createText(filename, data):
    try:
        with open(filename , 'wb') as file:
            file.write(data)
        print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")
        
def createExcel(outputfile, *data):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            for df, sheetname in data:
                df.to_excel(writer, sheet_name=sheetname, index=False)
        print("File created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")
        
def prepareOutputFile(data_response, filename, format_str):
    if format_str == "csv":
        data = pd.read_csv(StringIO(data_response.text))
        createExcel(f"{filename}.xlsx", (data, "Forecast Report"))
    elif format_str == "json":
        data = data_response.json()
        createJson(f"{filename}.json", data)
    elif format_str == "xml":
        data = data_response.text
        createXml(f"{filename}.xml", data)