import pandas as pd

from utils.readFile import loadJson
from shareplum import Site
from shareplum import Office365
from io import BytesIO


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


def getDataExcel(prompt="Enter PATH of the file and sheetname [pathfile/sheetname]: "):
    excel_configs = inputMethod(prompt)
    if excel_configs is None:
        print('Error getting excel configs')
        return None
    
    print('Reading excel file...')
    dfs = readExcelMultipleSheet(excel_configs['path'], excel_configs['sheetname'])
    if dfs is None:
        print('Error reading excel file')
        return None
    
    
    if isinstance(dfs, dict) and excel_configs['sheetname'] is not None:
        print('selecting sheet . . .')
        dfs_sheet = selectSheet(dfs, excel_configs['sheetname'])
    else:
        dfs_sheet = dfs
    
    print('Excel data read successfully')
    return dfs_sheet


# def getDataExcelOnline(prompt="Enter Sharepoint Folder PATH of the file, and sheetname [folderpath|filename|sheetname]: "):
#     excel_configs = inputMethod(prompt, 'sharepoint')
#     print('Loading Sharepoint credentials...')
#     auth = loadJson('Auth.json')
#     userpass = auth['Sharepoint']
#     URL, site_url, username, password = userpass['URL'], userpass['SITE_URL'], userpass['USERNAME'], userpass['PASSWORD']
#     authcookie = Office365(URL, username = username, password = password).GetCookies()
#     print('Connecting to Sharepoint...')
#     site = Site(site_url, authcookie=authcookie)
#     if site is None:
#         print('Error connecting to Sharepoint')
#         return None
#     folder = site.Folder(excel_configs['folderpath'])
#     file = folder.get_file(excel_configs['filename'])
#     file_content = BytesIO(file)
#     print('Reading excel file...')
#     dfs = readExcelMultipleSheet(file_content, excel_configs['sheetname'])
#     if dfs is None:
#         print('Error reading excel file')
#         return None
    
#     if isinstance(dfs, dict) and excel_configs['sheetname'] is not None:
#         print('selecting sheet . . .')
#         dfs_sheet = selectSheet(dfs, excel_configs['sheetname'])
#     else:
#         dfs_sheet = dfs
        
#     print('Excel data read successfully')
#     return dfs_sheet