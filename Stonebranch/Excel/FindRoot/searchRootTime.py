import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel
from utils.createFile import createJson
from concurrent.futures import ProcessPoolExecutor, as_completed



MAX_WORKERS = 8

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
        
        #print("T",task_name,"B",box_name)
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

# def process_batch(df, rows):
#     """Process a batch of rows to find the start boxes and return job insert details."""
#     job_insert_start_list = []
    
#     for row in rows:
#         start_rows = recursiveSearchStartBox(df, row['jobName'])
#         for index, start_row in start_rows.iterrows():
#             if start_row['jobName'] == row['jobName']:
#                 job_insert_start_list.append({
#                     'jobName': row['jobName'],
#                     'startBox': '',
#                     'startBoxType': row['jobType'],
#                     'startBoxStartTime': row['start_times'],
#                     'startBoxCondition': row['condition'],
#                     'startBoxRunCalender': row['run_calendar'],
#                     'startBoxExcludeCalender': row['exclude_calendar'],
#                 })
#             else:
#                 job_insert_start_list.append({
#                     'jobName': row['jobName'],
#                     'startBox': start_row['jobName'],
#                     'startBoxType': start_row['jobType'],
#                     'startBoxStartTime': start_row['start_times'],
#                     'startBoxCondition': start_row['condition'],
#                     'startBoxRunCalender': start_row['run_calendar'],
#                     'startBoxExcludeCalender': start_row['exclude_calendar'],
#                 })
#     return job_insert_start_list

# def reverseSearchStartMulti(df, batch_size=100):
#     """Parallel search start for job insert, with batch processing for improved performance."""
#     job_insert_start_list = []
#     number_of_rows = len(df)

#     # Convert the DataFrame to a list of dictionaries for faster access
#     row_list = df.to_dict('records')

#     # Split rows into batches to reduce the overhead of many small parallel tasks
#     row_batches = np.array_split(row_list, max(1, number_of_rows // batch_size))

#     # Parallel execution using ProcessPoolExecutor
#     with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         futures = {executor.submit(process_batch, df, batch): batch for batch in row_batches}

#         for count, future in enumerate(as_completed(futures), 1):
#             job_insert_start_list.extend(future.result())  # Collect the results from the completed future
#             print(f'{count}/{len(row_batches)} batches done')

#     return pd.DataFrame(job_insert_start_list)

def main():
    
    df_selected = getDataExcel()
    
    insert_start_list = searchRootTime(df_selected)
    createJson('job_insert_start.json', insert_start_list)
    df_insert_start = pd.DataFrame(insert_start_list)
    createExcel('job_insert_start.xlsx', (df_insert_start, 'job Insert Start'))
    
    
if __name__ == "__main__":
    main()