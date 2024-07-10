import pandas as pd
import os

SHEET_NAME = "Sheet"

def inputMehod():
    print("Enter PATH of the main file and sheetname [pathfile/sheetname]: ")
    input1 = input()
    if input1.find('/') == -1:
        path1 = input1
        sheetname1 = None
    else:
        path1 = input1.split('/')[0]
        sheetname1 = input1.split('/')[1]
    
    print("Enter PATH of the compare file and sheetname [pathfile/sheetname]: ")
    input2 = input()
    if input2.find('/') == -1:
        path2 = input2
        sheetname2 = None
    else:
        path2 = input2.split('/')[0]
        sheetname2 = input2.split('/')[1]
    
    return {
        'path_m': path1,
        'sheetname_m': sheetname1,
        'path_c': path2,
        'sheetname_c': sheetname2
    }
    

def readExcelMultipleSheet(pathfile, sheetname = None):
    pathfile = pathfile
    dfs = pd.read_excel(pathfile, sheet_name= sheetname, engine='openpyxl')
    return dfs

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
        
    for index, row in merge_data.iterrows():
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
    with pd.ExcelWriter(outputfile) as writer:
        diff_data['main_new_from_compare'].to_excel(writer, sheet_name='New', index=False)
        diff_data['compare_delete_from_main'].to_excel(writer, sheet_name='Deleted', index=False)
        diff_data['main_update_from_compare'].to_excel(writer, sheet_name='Updated', index=False)
        
    print("Difference file created successfully")

def main():
    input = inputMehod()
    
    print("reading main file . . .")
    dfm = readExcelMultipleSheet(input['path_m'], input['sheetname_m'])
    print("completed reading main file")
    
    print("reading compare file . . .")
    dfc = readExcelMultipleSheet(input['path_c'], input['sheetname_c'])
    print("completed reading compare file")
    
    dfm_sheet = selectSheet(dfm, input['sheetname_m'])
    dfc_sheet = selectSheet(dfc, input['sheetname_c'])
    print("comparing data . . .")
    diff_data = compareData(dfm_sheet, dfc_sheet, compare_column = 'jobName')
    print("completed comparing data")
    
    outputfile = 'Difference.xlsx'
    createExcel(diff_data, outputfile)