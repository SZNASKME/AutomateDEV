import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel

def replaceNan(value):
    if pd.isna(value):
        return ''
    return value


def findSpecificRowSpecificColumn(df_time, column_name, row_value , column_name_get_value):
    row_data = df_time[df_time[column_name] == row_value]
    if row_data.empty:
        return None
    return row_data[column_name_get_value].values[0]

def mapStartTime(df, df_time):
    dfc = df.copy()
    for index, row in dfc.iterrows():
        task_name = row['Task Monitor']
        task_start_time = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'startBoxStartTime')
        task_condition = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'startBoxCondition')
        task_run_calender = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'startBoxRunCalender')
        task_exclude_calender = findSpecificRowSpecificColumn(df_time, 'jobName', task_name, 'startBoxExcludeCalender')
        dfc.at[index, 'Task Start Time'] = replaceNan(task_start_time)
        dfc.at[index, 'Task Condition'] = replaceNan(task_condition)
        dfc.at[index, 'Task Run Calender'] = replaceNan(task_run_calender)
        dfc.at[index, 'Task Exclude Calender'] = replaceNan(task_exclude_calender)
        
        trigger_name = row['Trigger workflow Name']
        trigger_start_time = findSpecificRowSpecificColumn(df_time, 'jobName', trigger_name, 'startBoxStartTime')
        trigger_condition = findSpecificRowSpecificColumn(df_time, 'jobName', trigger_name, 'startBoxCondition')
        trigger_run_calender = findSpecificRowSpecificColumn(df_time, 'jobName', trigger_name, 'startBoxRunCalender')
        trigger_exclude_calender = findSpecificRowSpecificColumn(df_time, 'jobName', trigger_name, 'startBoxExcludeCalender')
        dfc.at[index, 'Trigger Start Time'] = replaceNan(trigger_start_time)
        dfc.at[index, 'Trigger Condition'] = replaceNan(trigger_condition)
        dfc.at[index, 'Trigger Run Calender'] = replaceNan(trigger_run_calender)
        dfc.at[index, 'Trigger Exclude Calender'] = replaceNan(trigger_exclude_calender)
        
    return dfc




def main():
        
    df = getDataExcel("Enter PATH of the Task Monitor file and sheetname [pathfile/sheetname]: ")
    df_time = getDataExcel("Enter PATH of the Time file and sheetname [pathfile/sheetname]: ")

    df_mapped = mapStartTime(df, df_time)
    
    createExcel("MappedStartTime.xlsx", (df_mapped, 'MappedStartTime'))
    
    
if __name__ == "__main__":
    main()