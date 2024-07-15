####################    API    ########################################
import requests
import http

from compareDataApp import LIST_TASK_URI, LIST_TASK_ADV_URI, SHEET_NAME, task_configs, task_adv_configs, auth


def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    return uri


def getListTask():
    response = requests.post(url=LIST_TASK_URI, json=task_configs, auth=auth, headers={'Accept': 'application/json'})
    return response

def getListTaskAdvanced():
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    print(uri)
    response = requests.get(url=uri, auth=auth, headers={'Accept': 'application/json'})
    return response

def getDataAPI(mode = 0):
    
    if mode == 0:
        response = getListTask()
    else:
        response = getListTaskAdvanced()
        
    status = http.HTTPStatus(response.status_code)
    print(f"{response.status_code} - {status.phrase}: {status.description}")
    if response.status_code == 200:
        size = len(response.content)
        print("Size of API data: ", size / 1024, "KB")
        return response.json()
    else:
        return None
    
    
####################    Excel    ########################################
import pandas as pd

def inputMethod():
    def get_path_and_sheetname(prompt):
        print(prompt)
        input_value = input().strip()
        if '/' in input_value:
            path, sheetname = input_value.split('/', 1)
        else:
            path, sheetname = input_value, None
        return path, sheetname
    
    path, sheetname = get_path_and_sheetname("Enter PATH of the file and sheetname [pathfile/sheetname]: ")
    
    return {'path': path, 'sheetname': sheetname }
    

def readExcelMultipleSheet(pathfile, sheetname=None):
    try:
        return pd.read_excel(pathfile, sheet_name=sheetname, engine='openpyxl')
    except Exception as e:
        print(f"Error reading {pathfile}: {e}")
        return None

def selectSheet(dfs, sheetname):
    if sheetname == None:
        return dfs[SHEET_NAME]
    else:
        return dfs[sheetname]


def getDataExcel():
    excel_configs = inputMethod()
    print('Reading excel file...')
    dfs = readExcelMultipleSheet(excel_configs['path'], excel_configs['sheetname'])
    if dfs is None:
        print('Error reading excel file')
        return None
    
    print('selecting sheet . . .')
    dfs_sheet = selectSheet(dfs, excel_configs['sheetname'])
    
    print('Excel data read successfully')
    return dfs_sheet