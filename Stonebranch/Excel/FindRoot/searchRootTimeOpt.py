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


def recursiveSearchStartBox(df_dict, task_name, cache):
    if task_name in cache:
        return cache[task_name]
    
    # Find row in pre-indexed dataframe dictionary
    row_data = df_dict.get(task_name)
    if row_data:
        box_name = row_data['box_name']
        if pd.notna(box_name):
            result = recursiveSearchStartBox(df_dict, box_name, cache)
            cache[task_name] = result  # Cache the result
            return result
        cache[task_name] = row_data  # Cache final result if no recursion
        return row_data
    else:
        cache[task_name] = None  # Cache empty result
        return None
        
def searchRootTime(df):
    job_start_root_time = []
    number_of_rows = len(df)
    count = 0
    df_dict = df.set_index('jobName').to_dict(orient='index')
    cache = {}
    for row in df.itertuples(index=False):
        #print(row)
        start_row = recursiveSearchStartBox(df_dict, row.jobName, cache)
        #print(start_row)
        if start_row is None:
            job_start_root_time.append({
                'jobName': row.jobName,
                'rootBox': None,
            })
        else:
            start_row_job_name = next((key for key, value in df_dict.items() if value == start_row), None)
            if start_row_job_name == row.jobName:
                job_start_root_time.append({
                    'jobName': row.jobName,
                    'jobType': replaceNan(row.jobType),
                    'rootBox': 'Self Start',
                    'rootBoxStartTime': replaceNan(row.start_times),
                    'rootBoxCondition': replaceNan(row.condition),
                    'rootBoxRunCalender': replaceNan(row.run_calendar),
                    'rootBoxExcludeCalender': replaceNan(row.exclude_calendar),
                })
            else:
                job_start_root_time.append({
                    'jobName': row.jobName,
                    'jobBox': row.box_name,
                    'jobType': replaceNan(row.jobType),
                    'jobStartTime': replaceNan(row.start_times),
                    'jobCondition': replaceNan(row.condition),
                    'jobRunCalender': replaceNan(row.run_calendar),
                    'jobExcludeCalender': replaceNan(row.exclude_calendar),
                    'rootBox': start_row_job_name,
                    'rootBoxType': replaceNan(start_row['jobType']),
                    'rootBoxStartTime': replaceNan(start_row['start_times']),
                    'rootBoxCondition': replaceNan(start_row['condition']),
                    'rootBoxRunCalender': replaceNan(start_row['run_calendar']),
                    'rootBoxExcludeCalender': replaceNan(start_row['exclude_calendar']),
                })
        count += 1
        print(f'{count}/{number_of_rows} done | {row.jobName}')
    return job_start_root_time

def main():
    
    df_selected = getDataExcel()
    
    insert_start_list = searchRootTime(df_selected)
    createJson('RootTime.json', insert_start_list)
    df_insert_start = pd.DataFrame(insert_start_list, 
                                   columns=['jobName', 'jobType', 'jobBox', 'rootBox', 'rootBoxType', 'rootBoxStartTime', 
                                            'rootBoxCondition','rootBoxRunCalender', 'rootBoxExcludeCalender', 
                                            'jobStartTime', 'jobCondition', 'jobRunCalender', 'jobExcludeCalender'])
    createExcel('RootTime.xlsx', (df_insert_start, 'Start Root Time'))
    
    
if __name__ == "__main__":
    main()