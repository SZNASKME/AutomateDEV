import pandas as pd
import os

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
    elif method == 'folder':
        folderpath, sheetname = getPathAndSheetname(prompt)
        return {'folderpath': folderpath, 'sheetname': sheetname }
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
        if sheetname not in dfs:
            print(f"Sheetname {sheetname} not found")
            return None
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
    excel_configs = inputMethod(prompt)
    print('Reading excel file...')
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


def getDataSheetMultiExcelFile(prompt="Enter PATH of the folder, sheetname [folderpath/sheetname]: ", all_sheets=False):
    
    def getExcelProcessAllFiles(folderpath, sheetname=None):
        print('Reading excel files in folder...')
        excel_files = [f for f in os.listdir(folderpath) if f.endswith(('.xlsx', '.xls'))]
        if not excel_files:
            print('No excel files found in the folder')
            return None
        
        dfs_sheets = {}
        for excel_file in excel_files:
            pathfile = os.path.join(folderpath, excel_file)
            print(f'Reading file: {excel_file}')
            dfs_sheet = getExcelProcess(pathfile, sheetname)
            if dfs_sheet is not None:
                dfs_sheets[excel_file] = dfs_sheet
            else:
                print(f'Error reading file: {excel_file}')
        
        print('All excel files processed successfully')
        return dfs_sheets
    
    def getExcelProcessAllFilesAndSheets(folderpath):
        print('Reading excel files in folder...')
        excel_files = [f for f in os.listdir(folderpath) if f.endswith(('.xlsx', '.xls'))]
        if not excel_files:
            print('No excel files found in the folder')
            return None
        
        dfs_sheets = {}
        for excel_file in excel_files:
            pathfile = os.path.join(folderpath, excel_file)
            print(f'Reading file: {excel_file}')
            excel_file_obj = pd.ExcelFile(pathfile)
            sheet_names = excel_file_obj.sheet_names
            dfs_sheets[excel_file] = {}
            for sheet_name in sheet_names:
                print(f'  Reading sheet: {sheet_name}')
                df_sheet = pd.read_excel(pathfile, sheet_name=sheet_name, engine='openpyxl')
                dfs_sheets[excel_file][sheet_name] = df_sheet
        
        print('All excel files and sheets processed successfully')
        return dfs_sheets

    excel_configs = inputMethod(prompt, method='folder')
    if all_sheets:
        dfs_sheets = getExcelProcessAllFilesAndSheets(excel_configs['folderpath'])
    else:
        dfs_sheets = getExcelProcessAllFiles(excel_configs['folderpath'], excel_configs['sheetname'])
        
    return dfs_sheets
        



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


def readExcelRecord(df):
    record_count = len(df)
    print(f"Number of records: {record_count}")
    return record_count


def readAllExcelSheetRecord(dfs):
    record_summary = {}
    for sheet_name, df in dfs.items():
        record_count = readExcelRecord(df)
        record_summary[sheet_name] = record_count
        print(f"Sheet: {sheet_name} | Number of records: {record_count}")
    print("Summary of records per sheet:", record_summary)
    return dfs, record_summary


