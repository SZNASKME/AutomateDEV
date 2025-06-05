import sys
import os
import pandas as pd
import re
import json
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson
from utils.readFile import loadJson
from utils.stbAPI import *

VERTEX_REPORT_TITLE = 'AskMe - Workflow Vertices'
DEPEN_REPORT_TITLE = 'AskMe - Workflow Dependencies'



OUTPUT_EXCEL_NAME = 'Dependency.xlsx'
OUTPUT_EXCEL_SHEET_NAME = 'Dependency'


exclude_condition_containing = [
    'Start_'
]


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

def prepareWorkflowVertexDict(df_workflow_vertex, workflow_list):
    workflow_vertex_dict = {}
    filtered_df = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(workflow_list)]

    for _, row in filtered_df.iterrows():
        workflow = row['Workflow']
        vertex_id = row['Vertex Id']
        task_name = row['Task']

        if workflow not in workflow_vertex_dict:
            workflow_vertex_dict[workflow] = {}
        workflow_vertex_dict[workflow][vertex_id] = task_name

    for workflow in workflow_list:
        if workflow not in workflow_vertex_dict:
            workflow_vertex_dict[workflow] = {}

    return workflow_vertex_dict

def createDependencyDict(df_workflow_depen, workflow_vertex_dict):
    depen_dict = {}
    grouped_workflow_depen_dict = df_workflow_depen.groupby('Workflow')
    
    for workflow, group in grouped_workflow_depen_dict:
        if workflow not in depen_dict:
            depen_dict[workflow] = []
        
        for _, row in group.iterrows():
            source_vertex_id = row['Source Vertex Id']
            target_vertex_id = row['Target Vertex Id']
            condition = row['Condition']

            source_task = workflow_vertex_dict[workflow].get(source_vertex_id, None)
            target_task = workflow_vertex_dict[workflow].get(target_vertex_id, None)
            
            #####
            #if source_task is None or target_task is None:
            #    continue
            
            #if any(exclude in source_task for exclude in exclude_condition_containing) or any(exclude in target_task for exclude in exclude_condition_containing):
            #    continue
            #####
            
            if source_task and target_task:
                depen_dict[workflow].append({
                    'Source Vertex Id': source_vertex_id,
                    'Source Task': source_task,
                    'Target Vertex Id': target_vertex_id,
                    'Target Task': target_task,
                    'Condition': condition
                })


    return depen_dict

def prepareTaskDependencyDict(workflow_list, workflow_depen_dict):
    task_depen_dict = {}
    for workflow_name in workflow_list:
        if workflow_name in workflow_depen_dict:
            for depen in workflow_depen_dict[workflow_name]:
                source_task = depen['Source Task']#.replace(TASK_MONITOR_SUFFIX, '')
                target_task = depen['Target Task']#.replace(TASK_MONITOR_SUFFIX, '')
                condition = depen['Condition']
                if target_task not in task_depen_dict:
                    task_depen_dict[target_task] = []
                task_depen_dict[target_task].append({
                    'Workflow': workflow_name,
                    'Source Task': source_task,
                    'Condition': condition
                })
        #else:
        #    task_depen_dict[workflow_name] = []

    return task_depen_dict

def findTaskDependencyFromSurce(df_workflow_vertex, df_workflow_depen, workflow_list, list_task_to_check):
    
    list_task_dependency = []
    
    workflow_vertex_dict = prepareWorkflowVertexDict(df_workflow_vertex, workflow_list)
    workflow_depen_dict = createDependencyDict(df_workflow_depen, workflow_vertex_dict)
    
    task_depen_dict = prepareTaskDependencyDict(workflow_list, workflow_depen_dict)
    #createJson('task_depen_dict.json', task_depen_dict)
    
    for taskname, task_dependency_list in task_depen_dict.items():
        for task_dependency in task_dependency_list:
            workflow = task_dependency['Workflow']
            source_task = task_dependency['Source Task']
            condition = task_dependency['Condition']
            if source_task in list_task_to_check:
                list_task_dependency.append({
                    'Workflow': workflow,
                    'Task': taskname,
                    'Source Task': source_task,
                    'Condition': condition
                })
            
    
    df_list_task_dependency = pd.DataFrame(list_task_dependency)
    return df_list_task_dependency


def main():
        
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    df_list = getDataExcel()
    
    task_list_to_check = df_list['Name'].tolist()
    
    
    df_workflow_vertex = getReport(VERTEX_REPORT_TITLE)
    df_workflow_depen = getReport(DEPEN_REPORT_TITLE)
    
    workflow_list = df_workflow_vertex['Workflow'].tolist()
    
    workflow_list = list(set(workflow_list))
    
    df_task_dependency = findTaskDependencyFromSurce(df_workflow_vertex, df_workflow_depen, workflow_list, task_list_to_check)
    
    createExcel(OUTPUT_EXCEL_NAME, (OUTPUT_EXCEL_SHEET_NAME, df_task_dependency))
    
    
    
if __name__ == "__main__":
    main()