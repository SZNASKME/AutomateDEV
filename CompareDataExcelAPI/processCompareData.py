import pandas as pd

def ListJSON_to_DataFrame(json_data):
    
    if json_data:
        columns = list(json_data[0].keys())
        try:
            return pd.DataFrame(json_data, columns=columns)
        except Exception as e:
            print(f"Error converting JSON to DataFrame: {e}")
            return None
    else:
        return None


def compareDataExcelAPI(excel_data, API_data, api_compare_column = None, compare_column = None):
    main_columns = excel_data.columns.tolist()
    main_columns_compare = [col for col in main_columns if col not in compare_column]
    
    dfsys = ListJSON_to_DataFrame(API_data)
    dfsys = dfsys.rename(columns={api_compare_column: compare_column})
    dfex = excel_data
    print(f"Excel: {len(dfex)}")
    print(f"API: {len(dfsys)}")
    new = dfsys[~dfsys[compare_column].isin(dfex[compare_column])]
    delete = dfex[~dfex[compare_column].isin(dfsys[compare_column])]
    
    print(f"New: {len(new)}")
    print(f"Delete: {len(delete)}")
    
    #merge_data = pd.merge(dfsys, dfex, on=compare_column, suffixes=('_main', '_compare'))
    #merge_data = merge_data.fillna('')
    #update_list = []
        
    #for _, row in merge_data.iterrows():
    #    for col in main_columns_compare:
    #        if row[col+'_main'] != row[col+'_compare']:
    #            update_list.append(pd.DataFrame({
    #                'jobName': [row[compare_column]],
    #                'fieldname': [col],
    #                'old_value': [row[col+'_compare']],
    #                'new_value': [row[col+'_main']]
    #            }))
    #if update_list:
    #    update = pd.concat(update_list, ignore_index=True)
    #else:
    #    update = pd.DataFrame(columns=['jobName', 'fieldname', 'old_value', 'new_value'])
        
    difference_data = {
        'new_from_excel': new,
        'delete_from_system': delete,
        #'main_update_from_compare': update
    }
    return difference_data


def createExcel(diff_data, outputfile):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            diff_data['new_from_excel'].to_excel(writer, sheet_name='New', index=False)
            diff_data['delete_from_system'].to_excel(writer, sheet_name='Deleted', index=False)
            #diff_data['main_update_from_compare'].to_excel(writer, sheet_name='Updated', index=False)
        print("Difference file created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")