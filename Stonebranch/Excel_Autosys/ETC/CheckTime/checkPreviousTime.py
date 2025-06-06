import sys
import os
import re
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel

JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'
ROOTBOX_COLUMN = 'rootBox'
ROOTTIME_COLUMN = 'rootBoxStartTime'
ROOTCONDITION_COLUMN = 'rootBoxCondition'
ROOTCALENDAR_COLUMN = 'rootBoxRunCalendar'
ROOTEXCLUDE_COLUMN = 'rootBoxExcludeCalendar'


def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list


def getJobFoundConditionList(df_job, job):
    found_condition_list = []
    for row in df_job.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        condition = getattr(row, CONDITION_COLUMN)
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        for sub_condition in condition_list:
            if sub_condition == job:
                if job_name not in found_condition_list:
                    found_condition_list.append(job_name)
    return found_condition_list



def checkPreviousTime(df_job, df_roottime, job_list):
    pre_list = []
    err_list = []
    for job in job_list:
        if df_job[df_job[JOBNAME_COLUMN] == job].empty:
            print(f"Job {job} not found in JIL")
            err_list.append({
                'jobName': job,
                'remark': 'Job not found in JIL'
            })
            continue
        
        roottime_row = df_roottime[df_roottime[JOBNAME_COLUMN] == job]
        if roottime_row.empty:
            print(f"Job {job} not found in RootTime")
            err_list.append({
                'jobName': job,
                'remark': 'Job not found in RootTime'
            })
            continue

        job_found_condition_list = getJobFoundConditionList(df_job, job)
        #print(job_found_condition_list)
        if job_found_condition_list:
            for job_cond_found in job_found_condition_list:
                roottime_row_found = df_roottime[df_roottime[JOBNAME_COLUMN] == job_cond_found]
                if roottime_row_found.empty:
                    print(f"Job (Condition) {job_cond_found} not found in RootTime")
                    err_list.append({
                        'jobName': job,
                        'remark': 'Job (Condition) not found in RootTime'
                    })
                    continue
                #print(roottime_row.iloc[0][ROOTTIME_COLUMN], roottime_row_found.iloc[0][ROOTTIME_COLUMN])
                pre_list.append({
                    'Task to Monitor Name (Task Monitor)': job,
                    'Task to Monitor rootBox': roottime_row.iloc[0][ROOTBOX_COLUMN],
                    'Task Depen Task Monitor': job_cond_found,
                    'Task Depen Task Monitor rootBox': roottime_row_found.iloc[0][ROOTBOX_COLUMN],
                    'rootBoxStartTime': roottime_row.iloc[0][ROOTTIME_COLUMN],
                    'rootBoxStartTime_foundCondition': roottime_row_found.iloc[0][ROOTTIME_COLUMN],
                    'rootBoxCondition': roottime_row.iloc[0][ROOTCONDITION_COLUMN],
                    'rootBoxCondition_foundCondition': roottime_row_found.iloc[0][ROOTCONDITION_COLUMN],
                    'rootBoxRunCalendar': roottime_row.iloc[0][ROOTCALENDAR_COLUMN],
                    'rootBoxRunCalendar_foundCondition': roottime_row_found.iloc[0][ROOTCALENDAR_COLUMN],
                    'rootBoxExcludeCalendar': roottime_row.iloc[0][ROOTEXCLUDE_COLUMN],
                    'rootBoxExcludeCalendar_foundCondition': roottime_row_found.iloc[0][ROOTEXCLUDE_COLUMN]
                })
    
    df_pre_list = pd.DataFrame(pre_list)
    df_err_list = pd.DataFrame(err_list)
    return df_pre_list, df_err_list

def main():
    
    df_job = getDataExcel("JIL")
    df_roottime = getDataExcel("RootTime")
    df_list = getDataExcel("List")
    job_list = df_list[JOBNAME_COLUMN].tolist()
    print(len(job_list))
    df_pre_list, df_err_list = checkPreviousTime(df_job, df_roottime, job_list)
    
    createExcel('prelist.xlsx', ('Previous Time',df_pre_list), ('Error List',df_err_list))
    
    
    
if __name__ == '__main__':
    main()