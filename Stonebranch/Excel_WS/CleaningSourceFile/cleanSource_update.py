import sys
import os
import json
from unittest import result
import pandas as pd
import math
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readFile import loadJson
from utils.createFile import createJson, createExcel
from utils.readExcel import getDataExcel

TRIGGER_TYPE_LIST = ["Daily", "Weekly", "Monthly", "One Time"]

JOB_COLUMN = "Name"
MACHINE_COLUMN = "HostName"
TASKNAME_COLUMN = "TaskName"

TASK_COLUMN = ["Name","Status","IPV4","HostName","Path","SourceFile","Command_1","Arguments_1","WorkingDirectory_1"]
TRIGGER_COLUMN = ["TriggerType","StartBoundary","Detail","TriggerStatus"]

ORDERED_COLUMNS = ["Name","TaskName","Status","IPV4","HostName","Path","SourceFile","TriggerType","StartBoundary","Detail","TriggerStatus","Command_1","Arguments_1","WorkingDirectory_1"]


TRIGGER_TIME_COLUMN = "StartBoundary"
DESCRIPTION_COLUMN = "Detail"




def cleaningTimeFormat(time_str):
    # Format DD/MM/YYYY HH:MM:SS to HH:MM:SS
    time_pattern = r'(\d{2}):(\d{2}):(\d{2})'
    match = re.search(time_pattern, str(time_str))
    if match:
        return f"{match.group(1)}:{match.group(2)}:{match.group(3)}"
    

def cleanDescriptionData(description) -> str:
    # remove 'At DD/MM/YYYY' pattern
    remove_pattern = r'At \d{2}/\d{2}/\d{4}'
    cleaned_description = re.sub(remove_pattern, '', str(description)).strip()
    return cleaned_description


def createDataFrameRow(task_df):
    new_row = {}
    # single row task info
    task_info = task_df.iloc[0]
    for col in task_info.index:
        if pd.notna(task_info[col]):
            if col in TRIGGER_TIME_COLUMN:
                time = cleaningTimeFormat(task_info[col])
                new_row[col] = time
            elif col in DESCRIPTION_COLUMN:
                new_row[col] = cleanDescriptionData(task_info[col])
            else:
                new_row[col] = task_info[col]
    return new_row
    
    
def renameDuplicateColumns(task_df, original_col, append_col, is_duplicate_name=False):
    new_task_df = pd.DataFrame(task_df)
    dedup_task_df = new_task_df.drop_duplicates([original_col, append_col])
    
    for index, row in new_task_df.iterrows():
        task_name = row[original_col]
        machine_name = row[append_col]
        if len(dedup_task_df) > 1 or is_duplicate_name:
            new_name = f"{task_name}_{machine_name}"
        else:
            new_name = f"{task_name}"
        new_task_df.at[index, original_col] = new_name
        
    return new_task_df

def cloneColumn(df, original_column, new_column):
    new_df = pd.DataFrame(df)
    new_df[new_column] = new_df[original_column]
    return new_df

def checkDuplicateIgnoreSensitive(task_name, task_list):
    count = 0
    for task in task_list:
        if task.lower() == task_name.lower():
            count += 1
    if count > 1:
        return True
    else:
        return False

def cleanDataProcess(df):

    df_new = df.copy()
    task_list = df_new[JOB_COLUMN].unique()
    
    task_data_list = []
    
    for task in task_list:
        task_df = df_new[df_new[JOB_COLUMN] == task]
        new_task_df = cloneColumn(task_df, JOB_COLUMN, TASKNAME_COLUMN)
        if len(task_df) > 1:
            if checkDuplicateIgnoreSensitive(task, task_list):
                is_duplicate_name = True
            else:
                is_duplicate_name = False
            new_task_df = renameDuplicateColumns(new_task_df, TASKNAME_COLUMN, MACHINE_COLUMN, is_duplicate_name)
            
        for index, row in new_task_df.iterrows():
            new_row = createDataFrameRow(row.to_frame().T)
            task_data_list.append(new_row)

        
        
        
    df_new = pd.DataFrame(task_data_list, columns=ORDERED_COLUMNS)
            
    return df_new
    
    
    

def main():
    df = getDataExcel()
    
    df_cleaned = cleanDataProcess(df)
    
    createExcel('Cleaned_Source_File.xlsx', ('CleanedData', df_cleaned))
    
    
    
if __name__ == "__main__":
    main()
