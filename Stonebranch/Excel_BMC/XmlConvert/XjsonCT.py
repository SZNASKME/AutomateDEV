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
SHEETNAME_LIST = ["SMART_FOLDER","FOLDER","JOB","VARIABLE"]


def prepareXJson(json_dict):
    xjson_dict_source = json_dict[ROOT_KEY]
    xjson_dict = {}
    for key, value in xjson_dict_source.items():
        if not key.startswith(JSON_COLUMN_CHAR):
            xjson_dict[key] = value
    return xjson_dict


def recursiveFlattenSheetDict(xjson, sheet_dict = {}, key_column = None, parent_key = None):
    #print(len(xjson), type(xjson))
    if isinstance(xjson, dict):
        #print(xjson.keys())
        row_data = {}
        for key, value in xjson.items():
            
            if not key.startswith(JSON_COLUMN_CHAR):
                if key not in sheet_dict:
                    sheet_dict[key] = []
                sheet_dict = recursiveFlattenSheetDict(value, sheet_dict, key)
            else:
                row_data[key] = value
        if key_column is not None:
            print("D")
            sheet_dict[key_column].append(row_data)
    elif isinstance(xjson, list):
        print("L")
        for value in xjson:
            sheet_dict = recursiveFlattenSheetDict(value, sheet_dict, key_column)
    elif isinstance(xjson, str):
        print("S")
        sheet_dict[key_column].append(xjson)
    
    return sheet_dict

def XJsonToDataFrame(xjson_dict):
    
    sheet_dict = recursiveFlattenSheetDict(xjson_dict, {})
    
    #print(json.dumps(sheet_dict, indent=4))
    df_list = []
    for key, value in sheet_dict.items():
        df = pd.DataFrame(value)
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