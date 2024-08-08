import pandas as pd


SHEET_NAME = "New"

def inputMethod():
    def get_path_and_sheetname(prompt):
        print(prompt)
        input_value = input().strip()
        if '/' in input_value:
            path, sheetname = input_value.split('/', 1)
        else:
            path, sheetname = input_value, None
        return path, sheetname
    
    path_m, sheetname_m = get_path_and_sheetname("Enter PATH of the excel file and sheetname [pathfile/sheetname]: ")
    
    return {'path': path_m, 'sheetname': sheetname_m}
    


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
    
def create_JIL(df):
    with open('JIL.txt', 'w') as f:
        for index, row in df.iterrows():
            jil_job = "\n\n"
            jil_job += f"/* ----------------- {row['jobName']} ----------------- */ \n\n"
            jil_job += f"insert_job: {row['jobName']}   job_type: {row['jobType']}\n"
            for col in df.columns:
                if col not in ['jobName', 'jobType'] and not pd.isnull(row[col]):
                    if isinstance(row[col], (int, float)):
                        jil_job += f"{col}: {int(row[col])}\n"
                    elif col == 'description':
                        jil_job += f"{col}: \"{row[col]}\"\n"
                    else:
                        jil_job += f"{col}: {row[col]}\n"
            #if index < len(df) - 1:
            #    jil_job += "\n"
            f.write(jil_job)
    return None
    
def main():
    input_data = inputMethod()

    df = readExcelMultipleSheet(input_data['path'], input_data['sheetname'])
    if df is None:
        print("Error reading excel file")
        return
    
    df_selected = selectSheet(df, input_data['sheetname'])
    
    create_JIL(df_selected)