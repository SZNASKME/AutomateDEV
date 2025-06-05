import sys
import os
import pandas as pd
import re
import json
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson
from utils.readFile import loadJson
from utils.stbAPI import *


BUNDLE_NAME = 'CH25-0011820 A0076 DWH-LOAN_CLASS_MTH_END'
EXCEL_NAME = 'bundle_items.xlsx'
EXCEL_SHEET_NAME = 'Bundle items'

bundle_configs_temp = {
    'bundlename': None,
}



def getBundleReport(title_name):
        
        bundle_configs = bundle_configs_temp.copy()
        bundle_configs['bundlename'] = title_name
        response = getBundleAPI(bundle_configs)
        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            print("Error generating report")
            return None





# Recursive function to extract all "name" values
def extractNames(obj, parent_key=None):
    names_list = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "name":
                names_list.append({
                    "parent": parent_key,
                    "name": value,
                    "type": obj.get("type", None),  # Add type if available
                })
            else:
                names_list.extend(extractNames(value, key))
    elif isinstance(obj, list):
        for item in obj:
            names_list.extend(extractNames(item, parent_key))
    return names_list





def main():
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)


    # Get the bundle report
    bundle_data = getBundleReport(BUNDLE_NAME)
    # Extract "name" values
    #print(bundle_data)
    name_values = extractNames(bundle_data)
    
    df_names = pd.DataFrame(name_values)
    
    # Save the DataFrame to an Excel file
    createExcel(EXCEL_NAME, (EXCEL_SHEET_NAME, df_names))
    
    
    
    
if __name__ == '__main__':
    main()