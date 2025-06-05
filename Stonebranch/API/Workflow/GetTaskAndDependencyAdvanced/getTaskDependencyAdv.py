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

VERTEX_REPORT_TITLE = 'UAC - Workflow List Of Tasks By Workflow'
DEPEN_REPORT_TITLE = 'AskMe - Workflow Dependencies'
RUN_CRITERIA_REPORT_TITLE = 'AskMe - Task Run Criteria'


OUTPUT_EXCEL_NAME = 'Dependency_ADVANCE.xlsx'
DEPEN_EXCEL_SHEET_NAME = 'Dependency'
VERTEX_EXCEL_SHEET_NAME = 'Vertex'
RUN_CRTTERIA_SEET_NAME = 'Task Run Criteria'


task_configs_temp = {
    'taskname': None
}



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
           # print('Workflow: ', workflow, 'Source Vertex Id:', source_vertex_id, 'Target Vertex Id:', target_vertex_id, 'Condition:', condition)
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



def prepareTaskRunCriteria(workflow_list):
    
    task_run_criteria_list = []
    
    for workflow_name in workflow_list:
        task_config = task_configs_temp.copy()
        task_config['taskname'] = workflow_name
        response = getTaskAPI(task_config)
        if response.status_code == 200:
            response_json = response.json()
            task_run_criteria = response_json.get('runCriteria', [])
            
            for criteria in task_run_criteria:
                criteria_dict = {}
                criteria_dict['Workflow'] = workflow_name
                criteria_dict['task'] = ''
                criteria_dict['type'] = ''
                for key, value in criteria.items():
                    if value is None or value is False or key == 'sysId':
                        continue
                    else:
                        criteria_dict[key] = value
                
                task_run_criteria_list.append(criteria_dict)
            
    return task_run_criteria_list
    
    
    

def findTaskDependencyFromList(df_workflow_vertex, df_workflow_depen, list_to_check):
    
    list_task_dependency = []
    df_task_vertex = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(list_to_check)]
    df_workflow_depen = df_workflow_depen[df_workflow_depen['Workflow'].isin(list_to_check)]
    workflow_list = df_workflow_vertex['Workflow'].unique().tolist()
    
    workflow_vertex_dict = prepareWorkflowVertexDict(df_workflow_vertex, workflow_list)
    workflow_depen_dict = createDependencyDict(df_workflow_depen, workflow_vertex_dict)
    
    task_depen_dict = prepareTaskDependencyDict(workflow_list, workflow_depen_dict)
    #createJson('task_depen_dict.json', task_depen_dict)
    
    for taskname, task_dependency_list in task_depen_dict.items():
        for task_dependency in task_dependency_list:
            workflow = task_dependency['Workflow']
            source_task = task_dependency['Source Task']
            condition = task_dependency['Condition']
            list_task_dependency.append({
                'Workflow': workflow,
                'Source Task': source_task,
                'Target Task': taskname,
                'Condition': condition
            })
    
    workflow_run_criteria_list = prepareTaskRunCriteria(list_to_check)
    
            
    
    df_task_vertex = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(list_to_check)]
    df_task_dependency = pd.DataFrame(list_task_dependency)
    df_task_run_criteria = pd.DataFrame(workflow_run_criteria_list)
    
    return df_task_vertex, df_task_dependency, df_task_run_criteria


def main():
        
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    #userpass = auth['TTB_PROD']
    #updateAPIAuth(userpass['API_KEY'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    #domain = domain_url['TTB_PROD']
    updateURI(domain)
    
    
    df_list = getDataExcel()
    
    workflow_list = df_list['Name'].tolist()
    
    
    df_workflow_vertex = getReport(VERTEX_REPORT_TITLE)
    df_workflow_depen = getReport(DEPEN_REPORT_TITLE)
    
    #clearAuth()
    #userpass = auth['TTB']
    #updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    #domain = domain_url['TTB_UAT']
    
    #df_run_criteria = getReport(RUN_CRITERIA_REPORT_TITLE)
    
    #workflow_list = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(task_list_to_check)]['Workflow'].tolist()
    
    #orkflow_list = list(set(workflow_list))
    
    df_task_vertex, df_task_dependency, df_task_run_criteria = findTaskDependencyFromList(df_workflow_vertex, df_workflow_depen, workflow_list)
    
    createExcel(OUTPUT_EXCEL_NAME, (VERTEX_EXCEL_SHEET_NAME, df_task_vertex), (DEPEN_EXCEL_SHEET_NAME, df_task_dependency), (RUN_CRTTERIA_SEET_NAME, df_task_run_criteria))
    
    
    
if __name__ == "__main__":
    main()