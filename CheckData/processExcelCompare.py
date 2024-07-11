import pandas as pd
import os

SHEET_NAME = "Sheet"
OUTPUT_FILE = 'Difference.xlsx'
COMPARE_COLUMN = 'jobName'

def inputMethod():
    def get_path_and_sheetname(prompt):
        print(prompt)
        input_value = input().strip()
        if '/' in input_value:
            path, sheetname = input_value.split('/', 1)
        else:
            path, sheetname = input_value, None
        return path, sheetname
    
    path_m, sheetname_m = get_path_and_sheetname("Enter PATH of the main file and sheetname [pathfile/sheetname]: ")
    path_c, sheetname_c = get_path_and_sheetname("Enter PATH of the compare file and sheetname [pathfile/sheetname]: ")
    
    return {'path_m': path_m, 'sheetname_m': sheetname_m, 'path_c': path_c, 'sheetname_c': sheetname_c}
    

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

def compareData(dfm, dfc, compare_column = None):
    main_columns = dfm.columns.tolist()
    main_columns_compare = [col for col in main_columns if col not in compare_column]
    
    new = dfm[~dfm[compare_column].isin(dfc[compare_column])]
    delete = dfc[~dfc[compare_column].isin(dfm[compare_column])]
    
    merge_data = pd.merge(dfm, dfc, on=compare_column, suffixes=('_main', '_compare'))
    merge_data = merge_data.fillna('')
    update_list = []
        
    for _, row in merge_data.iterrows():
        for col in main_columns_compare:
            if row[col+'_main'] != row[col+'_compare']:
                update_list.append(pd.DataFrame({
                    'jobName': [row[compare_column]],
                    'fieldname': [col],
                    'old_value': [row[col+'_compare']],
                    'new_value': [row[col+'_main']]
                }))
    if update_list:
        update = pd.concat(update_list, ignore_index=True)
    else:
        update = pd.DataFrame(columns=['jobName', 'fieldname', 'old_value', 'new_value'])
        
    difference_data = {
        'main_new_from_compare': new,
        'compare_delete_from_main': delete,
        'main_update_from_compare': update
    }
    return difference_data

def createExcel(diff_data, outputfile):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            diff_data['main_new_from_compare'].to_excel(writer, sheet_name='New', index=False)
            diff_data['compare_delete_from_main'].to_excel(writer, sheet_name='Deleted', index=False)
            diff_data['main_update_from_compare'].to_excel(writer, sheet_name='Updated', index=False)
        print("Difference file created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")

def main():
    input = inputMethod()
    
    print("reading main file . . .")
    dfm = readExcelMultipleSheet(input['path_m'], input['sheetname_m'])
    if dfm is None:
        print("Error reading main file")
        return
    
    print("reading compare file . . .")
    dfc = readExcelMultipleSheet(input['path_c'], input['sheetname_c'])
    if dfc is None:
        print("Error reading compare file")
        return
    
    print("selecting sheet . . .")
    dfm_sheet = selectSheet(dfm, input['sheetname_m'])
    dfc_sheet = selectSheet(dfc, input['sheetname_c'])
    
    print("comparing data . . .")
    diff_data = compareData(dfm_sheet, dfc_sheet, compare_column = COMPARE_COLUMN)
    
    
    createExcel(diff_data, OUTPUT_FILE)