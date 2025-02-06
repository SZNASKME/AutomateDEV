import sys
import os
import re
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel

COLUMN_JOBNAME = 'jobName'
COLUMN_CONDITION = 'condition'
ROOT_TIME_COLUMN = ['jobName', 'rootBox', 'rootBoxStartTime', 'rootBoxCondition', 'rootBoxRunCalendar', 'rootBoxExcludeCalendar']

def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list


def recursiveSearchRootTime(df_job, df_time, job_name, condition):
    
    return None

def getAttrRootTime(job_name, df_time):
    row_data = df_time[df_time[COLUMN_JOBNAME] == job_name]
    row_data_filtered = row_data.filter(ROOT_TIME_COLUMN)
    if row_data_filtered.empty:
        return None
    if len(row_data_filtered) > 1:
        print("Multiple rows found for job name: {}".format(job_name))
        return row_data_filtered.todict('records')
    return row_data_filtered.iloc[0].to_dict()


def compareSameRootTime(job_root_time, sub_condition_root_time, exclude_list = []):
    for key, value in job_root_time.items():
        if key in exclude_list:
            continue
        if key not in sub_condition_root_time:
            return False
        if value != sub_condition_root_time[key]:
            return False
    return True



def compareStartRun(df_job, df_time):
    job_root_time_compare_list = []
    job_root_time_condition_multi_root_time_list = []
    number_of_rows = len(df_job)
    count = 0
    df_dict = df_job.set_index(COLUMN_JOBNAME).to_dict(orient='index')
    for row in df_job.itertuples(index=False):
        count += 1
        
        job_root_time_dict = {}
        job_name = getattr(row, COLUMN_JOBNAME)
        condition = getattr(row, COLUMN_CONDITION)
        if pd.isna(condition):
            print(f"{count}/{number_of_rows} no condition | {job_name}")
            continue
        condition_list = getNamefromCondition(condition)
        
        job_root_time = getAttrRootTime(job_name, df_time)
        if job_root_time is None:
            print(f"Job {job_name} not found Root Time")
            continue
        if isinstance(job_root_time, list):
            print(f"Multiple rows found for job name: {job_name}")
            continue
        for sub_condition in condition_list:
            job_root_time_dict = job_root_time.copy()
            #root_time = recursiveSearchRootTime(df_dict, df_time, job_name, sub_condition)
            sub_condition_root_time = getAttrRootTime(sub_condition, df_time)
            if sub_condition_root_time is not None:
                if compareSameRootTime(job_root_time, sub_condition_root_time, exclude_list = [COLUMN_JOBNAME]):
                    continue
                for key, value in sub_condition_root_time.items():
                    job_root_time_dict[f"{key}_sub_condition"] = value
                job_root_time_compare_list.append(job_root_time_dict)
        
        print(f'{count}/{number_of_rows} done | {job_name}')
    df_job_root_time = pd.DataFrame(job_root_time_compare_list)
    
    return df_job_root_time

def main():
    df_job = getDataExcel('Enter the path of the JIL file')
    df_time = getDataExcel('Enter the path of the Time file')
    df_job_root_time = compareStartRun(df_job, df_time)
    createExcel('job_root_time_compare.xlsx', ('job_root_time_compare', df_job_root_time))

if __name__ == '__main__':
    main()