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

OUTPUT_EXCEL_NAME = 'RootTask.xlsx'
OUTPUT_EXCEL_SHEET_NAME = 'RootTask'


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
    

def recursiveFindRootWorkflows(task_parent_dict, workflow_name, root_workflows):


    if workflow_name in task_parent_dict:
        workflows = task_parent_dict[workflow_name]
        for workflow in workflows:
            recursiveFindRootWorkflows(task_parent_dict, workflow, root_workflows)
    else:
        # If no parent workflows exist, this is a root workflow
        root_workflows.add(workflow_name)
    

def findRootTaskProcess(df_workflow_vertex):
        
        #workflow_vertex_dict = df_workflow_vertex.groupby('Workflow')['Task'].apply(list).to_dict()
        task_parent_dict = df_workflow_vertex.groupby('Task')['Workflow'].apply(list).to_dict()
        task_list = df_workflow_vertex['Task'].unique()
        
        createJson('task_parent_dict.json', task_parent_dict)
        root_workflow_list = []
        
        for task_name in task_list:
            if task_name in task_parent_dict:
                workflows = task_parent_dict[task_name]
            else:
                workflows = []
            root_workflow_dict = {}
            for workflow_name in workflows:
                root_workflow = set()
                recursiveFindRootWorkflows(task_parent_dict, workflow_name, root_workflow)
                root_workflow_dict[workflow_name] = ' '.join(f'({root})' for root in root_workflow)
                
            if root_workflow_dict:
                root_workflow_list.append({
                    'Task': task_name,
                    'Workflows': ' '.join([f'[{workflow_name}]' for workflow_name in root_workflow_dict.keys()]),
                    'Root Workflow List': ' | '.join([f'[{workflow_name}] {root_workflow_dict[workflow_name]}' for workflow_name in root_workflow_dict])
                })

        df_root_workflow = pd.DataFrame(root_workflow_list)
        
        return df_root_workflow


def main():
    
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    
    df_workflow_vertex = getReport(VERTEX_REPORT_TITLE)
    
    
    
    df_root_workflow = findRootTaskProcess(df_workflow_vertex)
    
    
    
    
    createExcel(OUTPUT_EXCEL_NAME, (OUTPUT_EXCEL_SHEET_NAME, df_root_workflow))
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()