import pandas as pd

SHEET_NAME = "Sheet"

def inputMethod(prompt, method='excel'):
    def getPathAndSheetname(prompt):
        print(prompt)
        input_value = input().strip()
        if '/' in input_value:
            path, sheetname = input_value.split('/', 1)
        else:
            path, sheetname = input_value, None
        return path, sheetname
    
    def getFolderFilenameAndSheetname(prompt):
        print(prompt)
        input_value = input().strip()
        if '|' in input_value:
            folderpath, filename, sheetname = input_value.split('|', 2)
        else:
            folderpath, filename, sheetname = input_value, None, None
        return folderpath, filename, sheetname
    
    if method == 'excel':
        path, sheetname = getPathAndSheetname(prompt)
        return {'path': path, 'sheetname': sheetname }
    elif method == 'sharepoint':
        folderpath, filename, sheetname = getFolderFilenameAndSheetname(prompt)
        return {'folderpath': folderpath, 'filename': filename, 'sheetname': sheetname }
    else:
        return None
    
def inputSheetName(prompt="Enter sheetname: "):
    print(prompt)
    return input().strip()
    

def readExcelMultipleSheet(pathfile, sheetname=None):
    try:
        return pd.read_excel(pathfile, sheet_name=sheetname, engine='openpyxl')
    except Exception as e:
        print(f"Error reading {pathfile}: {e}")
        return None

def selectSheet(dfs, sheetname):
    if sheetname == None:
        return dfs[SHEET_NAME]
    elif isinstance(dfs, pd.DataFrame):
        return dfs
    else:
        return dfs[sheetname]

def getExcelProcess(pathfile, sheetname=None):
    print('Reading excel file...')
    excel_file = pd.ExcelFile(pathfile)
    if excel_file is None:
        print('Error reading excel file')
        return None
    sheet_names = excel_file.sheet_names
    if len(sheet_names) == 1:
        dfs_sheet = pd.read_excel(pathfile, sheet_name=sheet_names[0], engine='openpyxl')
    else:
        dfs = readExcelMultipleSheet(pathfile, sheetname)
        if dfs is None:
            print('Error reading excel file')
            return None
        
        if isinstance(dfs, dict) and sheetname is not None:
            print('selecting sheet . . .')
            dfs_sheet = selectSheet(dfs, sheetname)
        elif isinstance(dfs, dict) and sheetname is None:
            print('Multiple sheets found in the excel file')
            for i, sheet_name in enumerate(sheet_names):
                print(f"{i+1}. {sheet_name}")
            sheet_name = inputSheetName()
            dfs_sheet = selectSheet(dfs, sheet_name)
        else:
            dfs_sheet = dfs
    
    print('Excel data read successfully')
    return dfs_sheet


def getDataExcel(prompt="Enter PATH of the file and sheetname [pathfile/sheetname]: "):
    excel_configs = inputMethod(prompt)
    if excel_configs is None:
        print('Error getting excel configs')
        return None
    
    dfs_sheet = getExcelProcess(excel_configs['path'], excel_configs['sheetname'])
    
    return dfs_sheet


def getDataExcelAllSheet(prompt="Enter PATH of the file and sheetname [pathfile/sheetname]: "):
    print('Reading excel file...')
    excel_configs = inputMethod(prompt)
    pathfile = excel_configs['path']
    excel_file = pd.ExcelFile(pathfile)
    if excel_file is None:
        print('Error reading excel file')
        return None
    sheet_names = excel_file.sheet_names
    dfs = {}
    for sheet_name in sheet_names:
        dfs[sheet_name] = pd.read_excel(pathfile, sheet_name=sheet_name, engine='openpyxl')
    
    print('Excel data read successfully')
    return dfs