import sys
import os
import re
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel


COLUMN_GETLIST = 'AppName'
JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
APPNAME_COLUMN = 'AppName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'

sys.setrecursionlimit(10000)

def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list

def inputColumnValue(df, column):
    def showListColumn():
        return df[column].unique().tolist()
    is_show_list = input(f"Show list {column}? (y/n): ")
    if is_show_list == 'y':
        for index, value in enumerate(showListColumn()):
            print(f"{index}: {value}")
    else:
        pass
    value = input(f"Input value: ")
    return value

def getListDatabyColumnValue(df, column, value):
    df_filtered_value = df[df[column] == value]
    list_value = df_filtered_value[JOBNAME_COLUMN].unique().tolist()
    return list_value

def iterativeSearchDepenCondition(df_dict, task_name, cache):
    stack = [task_name]  # Initialize stack with the root task
    result = set()  # Track unique conditions
    while stack:
        current_task = stack.pop()
        if current_task in cache:
            result.update(cache[current_task])
            continue
        row_data = df_dict.get(current_task)
        if row_data:
            condition = row_data[CONDITION_COLUMN]
            box_name = row_data[BOXNAME_COLUMN]
            if pd.notna(condition):
                condition_list = getNamefromCondition(condition)
                for condition in condition_list:
                    if condition not in result:
                        stack.append(condition)
                result.update(condition_list)
            elif pd.notna(box_name) and box_name not in result:
                    stack.append(box_name)
        cache[current_task] = list(result)
    return list(result)


def checkJobConditionNoneList(df_jil, list_condition):
    found_list = []
    df_dict = df_jil.set_index(JOBNAME_COLUMN).to_dict(orient='index')
    
    
    for row in df_jil.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        if job_name in list_condition:
            continue
        cache = {}
        breakthrough_condition_list = iterativeSearchDepenCondition(df_dict, job_name, cache)
        
        found_condition_list = [condition for condition in breakthrough_condition_list if condition in list_condition]
        #print(len(breakthrough_condition_list), len(found_condition_list))
        if found_condition_list:
            found_list.append({
                APPNAME_COLUMN: getattr(row, APPNAME_COLUMN),
                JOBNAME_COLUMN: job_name,
                JOBTYPE_COLUMN: getattr(row, JOBTYPE_COLUMN),
                BOXNAME_COLUMN: getattr(row, BOXNAME_COLUMN),
                'NumberOfAllCondition': len(breakthrough_condition_list),
                'NumberOfFoundCondition': len(found_condition_list),
                'FoundCondition': ", ".join(found_condition_list)
            })
    
    return found_list

def checkJobOtherDepenJob(df_jil):
    found_list_by_value = []
    for index, value in enumerate(df_jil[COLUMN_GETLIST].unique().tolist()):
        if pd.isna(value):
            continue
        print(f"{index}: {value}")
        list_filtered_value = getListDatabyColumnValue(df_jil, COLUMN_GETLIST, value)
        found_list = checkJobConditionNoneList(df_jil, list_filtered_value)
        df_condition_matched = pd.DataFrame(found_list)
        found_list_by_value.append((f"{index} {value[:28]}", df_condition_matched))
    return found_list_by_value


def main():
    df_jil = getDataExcel()
    #value = inputColumnValue(df_jil, COLUMN_GETLIST)
    
    found_list_by_value = checkJobOtherDepenJob(df_jil)
    createExcel('depen_other_app_bt.xlsx', *found_list_by_value)
    
    
if __name__ == '__main__':
    main()