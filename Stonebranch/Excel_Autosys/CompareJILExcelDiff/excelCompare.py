import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel

OUTPUT_FILE = 'Difference.xlsx'
COMPARE_COLUMN = 'Name'


def compareData(dfm, dfc, compare_column = None):
    main_columns = dfm.columns.tolist()
    main_columns_compare = [col for col in main_columns if col not in compare_column]
    
    dfm = dfm.map(lambda x: x.strip() if isinstance(x, str) else x)
    dfc = dfc.map(lambda x: x.strip() if isinstance(x, str) else x)
    
    new = dfm[~dfm[compare_column].isin(dfc[compare_column])]
    delete = dfc[~dfc[compare_column].isin(dfm[compare_column])]
    
    merge_data = pd.merge(dfm, dfc, on=compare_column, suffixes=('_new', '_old'))
    merge_data = merge_data.fillna('')
    update_list = []
        
    for _, row in merge_data.iterrows():
        for col in main_columns_compare:
            if row[col+'_new'] != row[col+'_old']:
                update_list.append(pd.DataFrame({
                    'jobName': [row[compare_column]],
                    'fieldname': [col],
                    'old_value': [row[col+'_old']],
                    'new_value': [row[col+'_new']]
                }))
    if update_list:
        update = pd.concat(update_list, ignore_index=True)
    else:
        update = pd.DataFrame(columns=['jobName', 'fieldname', 'old_value', 'new_value'])
        
    difference_data = {
        'new': new,
        'delete': delete,
        'update': update
    }
    return difference_data


def main():
    dfnew_sheet = getDataExcel("Enter PATH of the newer file and sheetname [pathfile/sheetname]: ")
    dfold_sheet = getDataExcel("Enter PATH of the older file and sheetname [pathfile/sheetname]: ")
    
    print("comparing data . . .")
    diff_data = compareData(dfnew_sheet, dfold_sheet, compare_column = COMPARE_COLUMN)
    
    new = ('New', diff_data['new'])
    delete = ('Deleted', diff_data['delete'])
    update = ('Updated', diff_data['update'])
    
    createExcel(OUTPUT_FILE, new, delete, update)
    
if __name__ == "__main__":
    main()