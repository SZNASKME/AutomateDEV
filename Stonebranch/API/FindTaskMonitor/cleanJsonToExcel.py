import sys
import os
import json
import pandas as pd


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createExcel import createExcel
from Stonebranch.utils.readFile import loadJson

JSON_PATH = './Stonebranch/API/FindTaskMonitor/UAT_result_restructure.json'

def findAllTaskMonitorList(json_data):
    unique_task_monitor_list = []
    for trigger_name, trigger_data in json_data.items():
        for workflow_name, workflow_data in trigger_data.items():
            for task_name, task_monitor_list in workflow_data.items():
                for task_monitor_name, task_to_monitor in task_monitor_list.items():
                    if task_monitor_name not in unique_task_monitor_list:
                        unique_task_monitor_list.append(task_monitor_name)
    return unique_task_monitor_list

def prepareTaskMonitorRowsSummary(json_data, unique_task_monitor_list):
    task_monitor_summary_rows = []
    for task_monitor in unique_task_monitor_list:
        task_list = []
        task_to_monitor_list = []
        workflow_list = []
        trigger_list = []
        for trigger_name, trigger_data in json_data.items():
            for workflow_name, workflow_data in trigger_data.items():
                for task_name, task_monitor_list in workflow_data.items():
                    for task_monitor_name, task_to_monitor in task_monitor_list.items():
                        #print(task_to_monitor)
                        if task_monitor in task_monitor_name:
                            if task_to_monitor not in task_to_monitor_list:
                                if task_to_monitor is None:
                                    task_to_monitor = 'Not Found'
                                task_to_monitor_list.append(task_to_monitor)
                            if workflow_name not in workflow_list:
                                workflow_list.append(workflow_name)
                            if task_name not in task_list:
                                task_list.append(task_name)
                            if trigger_name not in trigger_list:
                                trigger_list.append(trigger_name)
        #print(json.dumps(task_to_monitor_list, indent=4))
        task_monitor_summary_row = {
            'Task Monitor': task_monitor,
            'Task to Monitor': ', '.join(task_to_monitor_list),
            'Trigger workflow': ', '.join(workflow_list),
            'Sub workflow': ', '.join(task_list),
            'Triggers': ', '.join(trigger_list)
        }
        task_monitor_summary_rows.append(task_monitor_summary_row)
    return task_monitor_summary_rows

def prepareTaskMonitorRowsExpand(json_data):
    task_monitor_rows = []
    for trigger_name, trigger_data in json_data.items():
        for workflow_name, workflow_data in trigger_data.items():
            for task_name, task_monitor_list in workflow_data.items():
                for task_monitor_name, task_to_monitor in task_monitor_list.items():
                    if task_to_monitor is None:
                        task_to_monitor = 'Not Found'
                    task_monitor_row = {
                        'Trigger Name': trigger_name,
                        'Trigger workflow Name': workflow_name,
                        'Sub workflow Name': task_name,
                        'Task Monitor': task_monitor_name,
                        'Task to Monitor': task_to_monitor
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
    createExcel('UAT_TaskMonitor_List.xlsx', (sum_df, 'Summary'), (expand_df, 'Expand'))
    
    
if __name__ == '__main__':
    main()