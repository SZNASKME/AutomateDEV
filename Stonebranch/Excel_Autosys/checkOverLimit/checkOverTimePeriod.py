import sys
import os
import pandas as pd
import re
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel, getExcelProcess
from utils.createFile import createExcel


DAY_PERIOD = 7


def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    matches = re.findall(pattern, string)
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list

def replaceNan(value):
    if pd.isna(value):
        return ''
    return value

def findSpecificRowSpecificColumn(df_time, column_name, row_value , column_name_get_value):
    row_data = df_time[df_time[column_name] == row_value]
    if row_data.empty:
        return None
    return row_data[column_name_get_value].values[0]

def mapRootTime(df_time,task_name):

    task_start_time = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'rootBoxStartTime')
    task_condition = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'rootBoxCondition')
    task_run_calender = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'rootBoxRunCalender')
    task_exclude_calender = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'rootBoxExcludeCalender')
        
    return {
        'start_times': replaceNan(task_start_time),
        'condition': replaceNan(task_condition),
        'run_calender': replaceNan(task_run_calender),
        'exclude_calender': replaceNan(task_exclude_calender),
    }
    
    
def recursiveSearchRootTimeName(df_time, job_name, root_time_name_list = []):
    
    row_data = df_time[df_time['jobName'] == job_name]
    if not row_data.empty:
        
        root_start_time = row_data['rootBoxStartTime'].values[0]
        root_box_condition = row_data['rootBoxCondition'].values[0]
        root_run_calender = row_data['rootBoxRunCalender'].values[0]
        root_exclude_calender = row_data['rootBoxExcludeCalender'].values[0]
        #print(f"{row_data['jobName'].values[0]} - {root_start_time} - {root_box_condition} -")
        if pd.notna(root_start_time):
            root_time_name_list.append(row_data['jobName'].values[0])
        elif pd.notna(root_box_condition) and pd.isna(root_start_time) and pd.isna(root_run_calender) and pd.isna(root_exclude_calender):
            sub_condition_list = getNamefromCondition(root_box_condition)
            for sub_condition in sub_condition_list:
                root_time_name_list = recursiveSearchRootTimeName(df_time, sub_condition, root_time_name_list)
    return root_time_name_list

def calculateRunTime(job_name, df_time, df_stdcal, df_extcal):
    job_run_list = []
    break_throught_job_name_list = []
    break_throught_job_root_time_list = []
    job_root_time = mapRootTime(df_time, job_name)
    break_throught_job_name_list = recursiveSearchRootTimeName(df_time, job_name, [])
    print(job_name, break_throught_job_name_list)
    for break_throught_job_name in break_throught_job_name_list:
        break_throught_job_root_time = mapRootTime(df_time, break_throught_job_name)
        if break_throught_job_root_time not in break_throught_job_root_time_list:
            break_throught_job_root_time_list.append(break_throught_job_root_time)
    
    if job_name not in break_throught_job_name_list:
        print(job_name)
        print(job_root_time)
        print(break_throught_job_root_time_list)
        print("\n\n")
    return job_run_list


def checkOverLimitCondition(df, df_time, df_stdcal, df_extcal):
    error_list = []
    count = 0
    for index, row in df.iterrows():
        condition = row['condition']
        if not isinstance(condition,str) or (isinstance(condition,float) and math.isnan(condition)):
            continue
        count += 1
        print(count)
        job_run_list = calculateRunTime(row['jobName'], df_time, df_stdcal, df_extcal)
        sub_condition_list = getNamefromCondition(condition)
        #for sub_condition in sub_condition_list:
        #    sub_condition_root_time = mapRootTime(df_time,sub_condition)
            
    
    
    
    

    return error_list

def main():
    
    df_selected = getDataExcel("Enter the path of the JobMaster excel file")
    df_time = getDataExcel("Enter the path of the Start time excel file")    
    
    df_stdcal = getExcelProcess(".\\SEP16_2024_stdcal.xlsx")
    df_extcal = getExcelProcess(".\\SEP16_2024_extcal.xlsx")
    
    
    result_list = checkOverLimitCondition(df_selected, df_time, df_stdcal, df_extcal)
    
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()