import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createJson, createExcel

def replaceNan(value):
    if pd.isna(value):
        return ''
    return value


def recursiveSearchStartBox(df, task_name):
    
    row_data = df[df['jobName'] == task_name]
    if not row_data.empty:
        box_name = row_data['box_name'].values[0]
        if pd.notna(box_name):
            return recursiveSearchStartBox(df, box_name)
        return row_data
    else:
        return pd.DataFrame()
        
def searchRootTime(df):
    job_insert_start_list = []
    number_of_rows = len(df)
    count = 0
    for index, row in df.iterrows():
        
        start_rows = recursiveSearchStartBox(df,row['jobName'])
        if start_rows.empty:
            job_insert_start_list.append({
                'jobName': row['jobName'],
                'rootBox': '',
            })
        else:
            for index, start_row in start_rows.iterrows():
                
                if start_row['jobName'] == row['jobName']:
                    job_insert_start_list.append({
                        'jobName': row['jobName'],
                        'rootBox': 'Self Start',
                        'rootBoxType': replaceNan(row['jobType']),
                        'rootBoxStartTime': replaceNan(row['start_times']),
                        'rootBoxCondition': replaceNan(row['condition']),
                        'rootBoxRunCalender': replaceNan(row['run_calendar']),
                        'rootBoxExcludeCalender': replaceNan(row['exclude_calendar']),
                    })
                else:
                    job_insert_start_list.append({
                        'jobName': row['jobName'],
                        'rootBox': start_row['jobName'],
                        'rootBoxType': replaceNan(start_row['jobType']),
                        'rootBoxStartTime': replaceNan(start_row['start_times']),
                        'rootBoxCondition': replaceNan(start_row['condition']),
                        'rootBoxRunCalender': replaceNan(start_row['run_calendar']),
                        'rootBoxExcludeCalender': replaceNan(start_row['exclude_calendar']),
                    })
        count += 1
        print(f'{count}/{number_of_rows} done | {row["jobName"]}')
    return job_insert_start_list

def main():
    
    df_selected = getDataExcel()
    
    insert_start_list = searchRootTime(df_selected)
    createJson('job_insert_start.json', insert_start_list)
    df_insert_start = pd.DataFrame(insert_start_list)
    createExcel('job_insert_start.xlsx', (df_insert_start, 'job Insert Start'))
    
    
if __name__ == "__main__":
    main()