import pandas as pd

SHEET_NAME = "Sheet"

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
    
    
    if isinstance(dfs, dict):
        print('selecting sheet . . .')
        dfs_sheet = selectSheet(dfs, excel_configs['sheetname'])
    else:
        dfs_sheet = dfs
    
    print('Excel data read successfully')
    return dfs_sheet