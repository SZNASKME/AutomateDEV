import sys
import os
import pandas as pd
import re
import math
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel
from utils.createFile import createJson


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

def mapRootTime(df_time, job_name):
    
    job_box = findSpecificRowSpecificColumn(df_time, 'jobName', job_name, 'rootBox')
    
    job_box_type = findSpecificRowSpecificColumn(df_time, 'jobName', job_name, 'rootBoxType')
    job_start_time = findSpecificRowSpecificColumn(df_time, 'jobName', job_name, 'rootBoxStartTime')
    job_condition = findSpecificRowSpecificColumn(df_time, 'jobName', job_name, 'rootBoxCondition')
    job_run_calender = findSpecificRowSpecificColumn(df_time, 'jobName', job_name, 'rootBoxRunCalender')
    job_exclude_calender = findSpecificRowSpecificColumn(df_time, 'jobName', job_name, 'rootBoxExcludeCalender')
    
    return {
        'jobName': job_name,
        'rootBox': replaceNan(job_box),
        'rootBoxType': replaceNan(job_box_type),
        'rootBoxStartTime': replaceNan(job_start_time),
        'rootBoxCondition': replaceNan(job_condition),
        'rootBoxRunCalender': replaceNan(job_run_calender),
        'rootBoxExcludeCalender': replaceNan(job_exclude_calender),
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

def breakThroughtRootTimeProcess(row, df_time):
    job_name = row['jobName']
    job_root_time = mapRootTime(df_time, job_name)
    
    break_throught_job_name_list = []
    break_throught_job_root_time_list = []
    break_throught_job_name_list = recursiveSearchRootTimeName(df_time, job_name, [])
    if break_throught_job_name_list:
        for break_throught_job_name in break_throught_job_name_list:
            break_throught_job_root_time = mapRootTime(df_time, break_throught_job_name)
            if break_throught_job_root_time not in break_throught_job_root_time_list:
                break_throught_job_root_time_list.append(break_throught_job_root_time)
    else:
        break_throught_job_root_time_list.append(job_root_time)
    
    return break_throught_job_root_time_list


def searchRootTimeBreakThrought(df, df_time):
    job_root_time_breakthorught_list = []
    count = 0
    number_of_rows = len(df)
    for index, row in df.iterrows():
        job_root_time_list = breakThroughtRootTimeProcess(row, df_time)
        job_root_time_breakthorught_list.extend(job_root_time_list)
        #print(len(job_root_time_list), len(job_root_time_breakthorught_list))
        count += 1
        print(f'{count}/{number_of_rows} done | {row["jobName"]} {len(job_root_time_list)}')
    
    return job_root_time_breakthorught_list


def main():
    
    df_selected = getDataExcel("Enter the path of the JobMaster excel file")
    df_time = getDataExcel("Enter the path of the Start time excel file")    
    
    result_list = searchRootTimeBreakThrought(df_selected, df_time)
    df_result = pd.DataFrame(result_list)
    df_result = df_result.drop_duplicates()
    createJson("RootTimeBT.json", result_list)
    createExcel("RootTimeBreakThrought.xlsx", (df_result, 'RootTime'))
    
    
    
    
    
    
if __name__ == "__main__":
    main()