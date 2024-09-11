import sys
import os
import json
import pandas as pd


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createExcel import createExcel
from utils.loadFile import loadJson

JSON_PATH = './Stonebranch/API/CheckTaskMonitor/TTB_result.json'


def findAllTaskMonitorList(json_data):
    unique_task_monitor_list = []
    for trigger_name, trigger_data in json_data.items():
        for workflow_name, workflow_data in trigger_data.items():
            for task_name, task_monitor_list in workflow_data.items():
                for task_monitor in task_monitor_list:
                    if task_monitor not in unique_task_monitor_list:
                        unique_task_monitor_list.append(task_monitor)
    return unique_task_monitor_list

def prepareTaskMonitorRowsSummary(json_data, unique_task_monitor_list):
    task_monitor_summary_rows = []
    for task_monitor in unique_task_monitor_list:
        task_list = []
        workflow_list = []
        trigger_list = []
        for trigger_name, trigger_data in json_data.items():
            for workflow_name, workflow_data in trigger_data.items():
                for task_name, task_monitor_list in workflow_data.items():
                    if task_monitor in task_monitor_list:
                        if task_name not in task_list:
                            task_list.append(task_name)
                        if workflow_name not in workflow_list:
                            workflow_list.append(workflow_name)
                        if trigger_name not in trigger_list:
                            trigger_list.append(trigger_name)
        task_monitor_summary_row = {
            'Task Monitor': task_monitor,
            'Main workflow': ', '.join(task_list),
            'Sub workflow': ', '.join(workflow_list),
            'Triggers': ', '.join(trigger_list)
        }
        task_monitor_summary_rows.append(task_monitor_summary_row)
    return task_monitor_summary_rows

def prepareTaskMonitorRowsExpand(json_data):
    task_monitor_rows = []
    for trigger_name, trigger_data in json_data.items():
        for workflow_name, workflow_data in trigger_data.items():
            for task_name, task_monitor_list in workflow_data.items():
                for task_monitor in task_monitor_list:
                    task_monitor_row = {
                        'Trigger Name': trigger_name,
                        'Main workflow Name': task_name,
                        'Sub workflow Name': workflow_name,
                        'Task Monitor': task_monitor
                    }
                    task_monitor_rows.append(task_monitor_row)
    return task_monitor_rows


def createDataFrameFromJson(json_data):
    task_monitor_list = findAllTaskMonitorList(json_data)
    task_monitor_summary_rows = prepareTaskMonitorRowsSummary(json_data, task_monitor_list)
    task_monitor_summary_df = pd.DataFrame(task_monitor_summary_rows)
    
    
    task_monitor_expand_rows = prepareTaskMonitorRowsExpand(json_data)
    task_monitor_expand_df = pd.DataFrame(task_monitor_expand_rows)
    
    return task_monitor_summary_df, task_monitor_expand_df


def main():
    json_data = loadJson(JSON_PATH)
    sum_df,expand_df = createDataFrameFromJson(json_data)
    createExcel('TTB_TaskMonitor_Convert_new.xlsx', (sum_df, 'Summary'), (expand_df, 'Expand'))
    
    
if __name__ == '__main__':
    main()