import sys
import os
import xmltodict
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createFile import createJson, createExcel
from utils.readFile import loadText



XML_PATH = './Stonebranch/Excel_BMC/XmlConvert/Open-CTE1-20092024.xml'

ROOT_KEY = 'DEFTABLE'
JSON_COLUMN_CHAR = '@'
JOBNAME_COLUMN = ["@JOBNAME"]

SHEETNAME_LIST = ["SMART_FOLDER","FOLDER","JOB","VARIABLE"]


def prepareXJson(json_dict):
    xjson_dict_source = json_dict[ROOT_KEY]
    xjson_dict = {}
    for key, value in xjson_dict_source.items():
        if not key.startswith(JSON_COLUMN_CHAR):
            xjson_dict[key] = value
    return xjson_dict


def recursiveFlattenSheetDict(xjson_value, sheet_dict = {}, key_column = None, parent_key = None, parent_name = None):
    #print(len(xjson), type(xjson))
    if isinstance(xjson_value, dict):
        #print(xjson.keys())
        row_data = {}
        for key, value in xjson_value.items():
            if key in JOBNAME_COLUMN:
                parent_key = key
                parent_name = value
            if not key.startswith(JSON_COLUMN_CHAR):
                if key not in sheet_dict:
                    sheet_dict[key] = []
                sheet_dict = recursiveFlattenSheetDict(value, sheet_dict, key, parent_key, parent_name)
            else:
                row_data[key] = value
        if key_column is not None:
            if parent_key not in row_data and parent_key is not None:
                row_data[parent_key] = parent_name
            sheet_dict[key_column].append(row_data)
    elif isinstance(xjson_value, list):
        for value in xjson_value:
            sheet_dict = recursiveFlattenSheetDict(value, sheet_dict, key_column, parent_key, parent_name)
    #elif isinstance(xjson, str):
    #    print("S")
    #    sheet_dict[key_column].append(xjson)
    
    return sheet_dict

def XJsonToDataFrame(xjson_dict):
    
    sheet_dict = recursiveFlattenSheetDict(xjson_dict, {})
    
    #print(json.dumps(sheet_dict, indent=4))
    df_list = []
    for key, value in sheet_dict.items():
        df = pd.DataFrame(value)
        df.columns = df.columns.str.replace('@', '', regex=False)
        df_list.append((df, key))
        
    
    return df_list




def main():
    XML_text = loadText(XML_PATH)
    json_data = xmltodict.parse(XML_text)
    xjson_dict = prepareXJson(json_data)
    
    createJson('XmlCT.json', xjson_dict)
    #print(json.dumps(xjson_dict, indent=4))
    
    df_list = XJsonToDataFrame(xjson_dict)
    createExcel('XmlCT.xlsx', *df_list)

if __name__ == '__main__':
    main()