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
    return value if pd.notna(value) else None

def mapRootTime(df_time_dict, job_name):
    
    root_data = df_time_dict.get(job_name)
    return {
        'jobName': job_name,
        'rootBox': replaceNan(root_data['rootBox']),
        'rootBoxType': replaceNan(root_data['rootBoxType']),
        'rootBoxStartTime': replaceNan(root_data['rootBoxStartTime']),
        'rootBoxCondition': replaceNan(root_data['rootBoxCondition']),
        'rootBoxRunCalender': replaceNan(root_data['rootBoxRunCalender']),
        'rootBoxExcludeCalender': replaceNan(root_data['rootBoxExcludeCalender']),
    }
    
    
def recursiveSearchRootTimeName(df_time_dict, df_dict, job_name, chache):
    
    row_data = df_time_dict.get(job_name)
    if row_data:
        root_start_time = row_data['rootBoxStartTime']
        root_box_condition = row_data['rootBoxCondition']
        root_run_calender = row_data['rootBoxRunCalender']
        root_exclude_calender = row_data['rootBoxExcludeCalender']
        #print(f"{row_data['jobName'].values[0]} - {root_start_time} - {root_box_condition} -")
        if pd.notna(root_start_time):
            job_name = next((key for key, value in df_time_dict.items() if value == row_data), None)
            chache.append(job_name)
        elif pd.notna(root_box_condition) and pd.isna(root_start_time) and pd.isna(root_run_calender) and pd.isna(root_exclude_calender):
            sub_condition_list = getNamefromCondition(root_box_condition)
            #print(sub_condition_list)
            for sub_condition in sub_condition_list:
                chache = recursiveSearchRootTimeName(df_time_dict, df_dict, sub_condition, chache)
    return chache

def breakThroughtRootTimeProcess(row, df_dict, df_time_dict):
    job_name = row.jobName
    job_root_time = mapRootTime(df_time_dict, job_name)
    
    break_throught_job_root_time_list = []
    cache = []
    break_throught_job_name_list = recursiveSearchRootTimeName(df_time_dict, df_dict, job_name, cache)
    if break_throught_job_name_list:
        for value in break_throught_job_name_list:
            break_throught_job_root_time = mapRootTime(df_time_dict, value)
            break_throught_job_root_time['jobName'] = job_name
            if break_throught_job_root_time not in break_throught_job_root_time_list:
                break_throught_job_root_time_list.append(break_throught_job_root_time)
    else:
        break_throught_job_root_time_list.append(job_root_time)
        
    return break_throught_job_root_time_list


def searchRootTimeBreakThrought(df, df_time):
    job_root_time_breakthorught_list = []
    count = 0
    number_of_rows = len(df)
    df_dict = df.set_index('jobName').to_dict(orient='index')
    df_time_dict = df_time.set_index('jobName').to_dict(orient='index')
    
    for row in df.itertuples(index=False):
        job_root_time_list = breakThroughtRootTimeProcess(row, df_dict, df_time_dict)
        job_root_time_breakthorught_list.extend(job_root_time_list)
        
        count += 1
        print(f'{count}/{number_of_rows} done | {row.jobName} {len(job_root_time_list)}/{len(job_root_time_breakthorught_list)}')
    
    return job_root_time_breakthorught_list


def main():
    
    df_selected = getDataExcel("Enter the path of the JobMaster excel file")
    df_time = getDataExcel("Enter the path of the Start time excel file")
    
    result_list = searchRootTimeBreakThrought(df_selected, df_time)
    df_result = pd.DataFrame(result_list)
    df_result = df_result.drop_duplicates(keep='first' ,subset = ['jobName', 'rootBox', 'rootBoxType', 'rootBoxStartTime', 'rootBoxCondition', 'rootBoxRunCalender', 'rootBoxExcludeCalender'])
    createJson("RootTimeBT.json", result_list)
    createExcel("RootTimeBreakThroughtOpt.xlsx", (df_result, 'RootTime'))
    
    
    
    
    
    
if __name__ == "__main__":
    main()