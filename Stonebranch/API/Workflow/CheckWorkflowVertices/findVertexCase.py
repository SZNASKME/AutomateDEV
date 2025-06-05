import sys
import os
import pandas as pd
import re
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import *

VERTEX_REPORT_TITLE = 'UAC - Workflow List Of Tasks By Workflow'
    
DUPLICATE_TASK = 'Duplicate Task'
MULTI_PARENT_TASK = 'Multi Parent Task'
MONITOR = 'Task Monitor & Task Same place'
    
OUTPUT_EXCEL_NAME = 'Vertex Case PROD.xlsx'

TASK_MONITOR_SUFFIX = '-TM'

report_configs_temp = {
    #'reporttitle': 'UAC - Task List Credential By Task',
    'reporttitle': None,
}


def getReport(title_name):
    
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = title_name
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')
    if response_csv.status_code == 200:
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        print("Error generating report")
        return None
    
    
    
def checkTaskMonitor(task_name : str):
    if task_name.endswith(TASK_MONITOR_SUFFIX):
        return True
    return False


def findNumberOfParent(workflow_list):

    normalized_workflow_list = [
        re.sub(r'^[^a-zA-Z0-9]*|[^a-zA-Z0-9]*$', '', workflow_name) for workflow_name in workflow_list
    ]

    unique_workflows = set(normalized_workflow_list)
    filtered_workflows = set()

    for workflow_name in unique_workflows:
        if not any(
            workflow_name != other_workflow and workflow_name in other_workflow
            for other_workflow in unique_workflows
        ):
            filtered_workflows.add(workflow_name)

    return len(filtered_workflows)

def checkDupTaskInWorkflow(df_vertex):
    
    duplicate_task_in_worflow_list = []
    
    workflow_list = df_vertex['Workflow'].unique()
    
    for workflow_name in workflow_list:
        duplicate_task_list = []
        task_list = df_vertex[df_vertex['Workflow'] == workflow_name]['Task'].tolist()
        
        for task_name in task_list:
            if task_list.count(task_name) > 1 and not checkTaskMonitor(task_name):
                if task_name not in duplicate_task_list:
                    duplicate_task_list.append(task_name)
        
        for task_name in duplicate_task_list:
            duplicate_task_in_worflow_list.append({
                'Workflow': workflow_name,
                'Task': task_name
            })
        
        
    
    df_duplicate_task = pd.DataFrame(duplicate_task_in_worflow_list)
    
    return df_duplicate_task



def findTaskMonitorAndTaskSamePlace(df_vertex):
    
    task_monitor_and_task_same_place_list = []
    
    workflow_list = df_vertex['Workflow'].unique()

    for workflow_name in workflow_list:
        vertex_row = df_vertex[df_vertex['Workflow'] == workflow_name]

        task_list = vertex_row['Task'].tolist()
        
        for task_name in task_list:
            if checkTaskMonitor(task_name):
                temp_name = task_name.replace(TASK_MONITOR_SUFFIX, '')
                
                if temp_name in task_list:
                    task_monitor_and_task_same_place_list.append({
                        'Workflow': workflow_name,
                        'Task Monitor': task_name,
                        'Task': temp_name
                    })
            
        
    df_task_monitor_and_task_same_place = pd.DataFrame(task_monitor_and_task_same_place_list)

    return df_task_monitor_and_task_same_place




def findMultiParentTask(df_vertex):
        
        multi_parent_task_list = []
        
        task_list = df_vertex['Task'].unique()
        
        for task_name in task_list:
            workflow_list = df_vertex[df_vertex['Task'] == task_name]['Workflow'].tolist()
        
            if not checkTaskMonitor(task_name) and findNumberOfParent(workflow_list) > 1:
                multi_parent_task_list.append({
                    'Task': task_name,
                    'Workflows': ' '.join([f'[{workflow_name}]' for workflow_name in workflow_list])
                })
                
            
        
        df_multi_parent_task = pd.DataFrame(multi_parent_task_list)
        
        return df_multi_parent_task

def main():
    
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    #userpass = auth['TTB_PROD']
    #updateAPIAuth(userpass['API_KEY'])
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_PROD']
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    df_vertex = getReport(VERTEX_REPORT_TITLE)
    
    print("Processing duplicate task in workflow...")
    df_dup_task = checkDupTaskInWorkflow(df_vertex)
    
    print("Processing task monitor and task in same workflow...")
    df_monitor_same_place = findTaskMonitorAndTaskSamePlace(df_vertex)
    
    print("Processing multi parent task...")
    df_multi_parent_task = findMultiParentTask(df_vertex)
    
    
    
    
    createExcel(OUTPUT_EXCEL_NAME, (DUPLICATE_TASK, df_dup_task), (MONITOR, df_monitor_same_place), (MULTI_PARENT_TASK, df_multi_parent_task))
    

if __name__ == "__main__":
    main()