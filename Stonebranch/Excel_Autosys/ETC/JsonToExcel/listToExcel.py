import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readFile import loadJson
from utils.createFile import createExcel

pathfile = 'output.xlsx'

def createExcelFromJson(json_data, pathfile):
    
    # Create a Pandas dataframe from the data.
    dfs = {}
    for key, value in json_data.items():
        dfs[key] = pd.DataFrame(value)
        
    sheets = [(key, value) for key, value in dfs.items()]
    
    createExcel(pathfile, *sheets)
    print('Excel file created successfully')
    return True


def main():
    input_path = input("Enter the path of the json file: ")
    json_data = loadJson(input_path)
    createExcelFromJson(json_data, pathfile)
    print("Excel creation process completed")
    
    
if __name__ == '__main__':
    main()