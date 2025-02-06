import sys
import os
import re
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel


COLUMN_GETLIST = 'AppName'
JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
APPNAME_COLUMN = 'AppName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'


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


def checkJobConditionNoneList(df_job, list_condition):
    found_list = []
    for row in df_job.itertuples(index=False):
        if getattr(row, JOBNAME_COLUMN) in list_condition:
            continue
        condition = getattr(row, CONDITION_COLUMN)
        
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        #print(condition)
        #print(condition_list)
        found_condition_list = []
        for sub_condition in condition_list:
            if sub_condition in list_condition:
                found_condition_list.append(sub_condition)
        if found_condition_list:
            found_list.append({
                APPNAME_COLUMN: getattr(row, APPNAME_COLUMN),
                JOBNAME_COLUMN: getattr(row, JOBNAME_COLUMN),
                JOBTYPE_COLUMN: getattr(row, JOBTYPE_COLUMN),
                BOXNAME_COLUMN: getattr(row, BOXNAME_COLUMN),
                CONDITION_COLUMN: condition,
                'Found_Condition': ", ".join(found_condition_list)
            })
    return found_list


def checkJobOtherDepenJob(df_job):
    found_list_by_value = []
    for index, value in enumerate(df_job[COLUMN_GETLIST].unique().tolist()):
        print(f"{index}: {value}")
        list_filtered_value = getListDatabyColumnValue(df_job, COLUMN_GETLIST, value)
        found_list = checkJobConditionNoneList(df_job, list_filtered_value)
        df_condition_matched = pd.DataFrame(found_list)
        found_list_by_value.append((value[:31], df_condition_matched))
    return found_list_by_value

def main():
    df_job = getDataExcel()
    #value = inputColumnValue(df_job, COLUMN_GETLIST)
    
    found_list_by_value = checkJobOtherDepenJob(df_job)
    createExcel('depen_other_app.xlsx', *found_list_by_value)
    
    
if __name__ == '__main__':
    main()