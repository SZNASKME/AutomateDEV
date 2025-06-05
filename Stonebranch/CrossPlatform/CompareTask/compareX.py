import sys
import os
import pandas as pd
import re


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from collections import defaultdict
from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson
from utils.readFile import loadJson
from utils.stbAPI import *

WORKFLOW_VERTEX_REPORT_TITLE = 'AskMe - Workflow Vertices'
TASK_REPORT_TITLE = 'AskMe - Task Report'
PROD_VERTEX_REPORT_TITLE = 'UAC - Workflow List Of Tasks By Workflow'

JOBNAME = 'jobName'
JOBTYPE = 'jobType'
BOXNAME = 'box_name'
CONDITION = 'condition'
ROOT_BOX = 'root_box'

SELF_START_NAME = 'Self Start'

TASK_MONITOR_SUFFIX = '-TM'

TASKNAME_COLUMN = 'Name'
BUSINESS_SERVICE = 'Business Services'

#BASE_ON_EXCEL_SHEET_NAME = 'Base On JIL'
#BASE_ON_SYSTEM_SHEET_NAME = 'Base On UAC'
BASE_ON_ROOT_BOX_SHEET_NAME = 'Base On Root Task | Workflow'
OUT_OF_RELATE_SHEET_NAME = 'Out of Related'
OUTPUT_EXCEL_NAME = 'CompareTaskInWorkflow.xlsx'

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


def findOtherWorkflow(task_parent_workflow_dict, task_name, workflow_name):
    other_workflow_list = []
    if task_name in task_parent_workflow_dict:
        workflow_list = task_parent_workflow_dict[task_name]
        if len(workflow_list) > 1:
            for workflow in workflow_list:
                if workflow != workflow_name:
                    other_workflow_list.append(workflow)
            return ', '.join(other_workflow_list)
        elif len(workflow_list) == 1:
            if workflow_list[0] != workflow_name:
                return workflow_list[0]
            else:
                return None
    else:
        return 'Not Found'

    
def findWorkflowName(workflow_vertex_dict, task_name):
    workflow_list = []
    for workflow_name, tasks in workflow_vertex_dict.items():
        if task_name in tasks:
            workflow_list.append(workflow_name)
    if workflow_list:
        return ', '.join(workflow_list)
    return 'Not Found'

def recursiveFindValueDict(target_dict, main_key : str, result_set, tree_result_set):
    if main_key in target_dict:
        value_list = target_dict[main_key]
        for value in value_list:
            if value not in tree_result_set:
                tree_result_set.add(value)
            recursiveFindValueDict(target_dict, value, result_set, tree_result_set)
    else:
        result_set.add(main_key)
        
def recursiveFindValueKeyDict(target_dict, main_key : str, result_set):
    if main_key in target_dict:
        value_list = target_dict[main_key]
        for value in value_list:
            if value not in result_set:
                result_set.add(value)
            recursiveFindValueKeyDict(target_dict, value, result_set)
    else:
        result_set.add(main_key)        



def findRootTask(task_parent_workflow_dict, task_list):
    root_task_dict = {}
    tree_root_task_dict = {}
    for task_name in task_list:
        if task_name in task_parent_workflow_dict:
            workflow_list = task_parent_workflow_dict[task_name]
        else:
            workflow_list = []
        root_workflow_dict = {}
        tree_root_workflow_dict = {}
        for workflow_name in workflow_list:
            root_workflow = set()
            tree_root_workflows = set()
            recursiveFindValueDict(task_parent_workflow_dict, workflow_name, root_workflow, tree_root_workflows)
            root_workflow_dict[workflow_name] = [root_name for root_name in root_workflow]
            tree_root_workflow_dict[workflow_name] = [root_workflow_name for root_workflow_name in tree_root_workflows]
        if root_workflow_dict:
            root_task_dict[task_name] = root_workflow_dict
            tree_root_task_dict[task_name] = tree_root_workflow_dict
    return root_task_dict, tree_root_task_dict


def findChildrenTask(workflow_children_dict, task_list):
    children_task_dict = {}
    for task_name in task_list:
        children_task = set()
        recursiveFindValueKeyDict(workflow_children_dict, task_name, children_task)
        children_task_dict[task_name] = [children_task_name for children_task_name in children_task if children_task_name != task_name]
    return children_task_dict




def transposeNestedDict(nested_dict):
    transpose_dict = defaultdict(list)
    for key, sub_dict in nested_dict.items():
        for sub_key, value_list in sub_dict.items():
            for value in value_list:
                transpose_dict[value].append(sub_key)     
            
    return transpose_dict

def findRelatedWorkflow(children_task_dict, job_list):
    relate_workflow_list = []
    for task_name, children_list in children_task_dict.items():
        if children_list:
            if any(child in job_list for child in children_list):
                relate_workflow_list.append(task_name)
    return relate_workflow_list


        
# def compareTaskInWorkflowBaseExcel(df_job, df_workflow_vertex, df_task):
#     # Initialize dictionaries and lists
#     workflow_vertex_dict = df_workflow_vertex.groupby('Workflow')['Task'].apply(list).to_dict()
#     task_parent_workflow_dict = df_workflow_vertex.groupby('Task')['Workflow'].apply(list).to_dict()

#     task_list = set(df_task[TASKNAME_COLUMN].unique())
#     business_services_map = df_task.set_index(TASKNAME_COLUMN)['Member of Business Services'].to_dict()
#     compare_job_list = []

#     # Iterate over jobs
#     for row in df_job.itertuples(index=False):
#         job_name = getattr(row, JOBNAME)
#         #job_type = getattr(row, JOBTYPE)
#         box_name = getattr(row, BOXNAME)
#         root_box = getattr(row, ROOT_BOX)
#         #condition = getattr(row, CONDITION)

#         # Handle NaN values for box_name
#         box_name = None if pd.isna(box_name) else box_name

        
        
#         workflow_list = task_parent_workflow_dict.get(job_name, [])
#         workflow_list_root_dict = {}
#         if workflow_list:
#             for workflow_name in workflow_list:
#                 root_workflow = set()
#                 tree_root_workflow = set()
#                 recursiveFindRootWorkflows(task_parent_workflow_dict, workflow_name, root_workflow, tree_root_workflow)
#                 workflow_list_root_dict[workflow_name] = ', '.join(f'{root}' for root in root_workflow)
#         # ' | '.join([f'[{workflow_name}] {root_workflow_dict[workflow_name]}' for workflow_name in root_workflow_dict])
#         # Find other workflows and workflow details
#         other_workflow = ' // '.join(
#             [f'[{wf}] ({workflow_list_root_dict[wf]})' for wf in task_parent_workflow_dict.get(job_name, []) if wf != box_name]
#         ) or None
#         in_same_workflow = box_name in workflow_vertex_dict and job_name in workflow_vertex_dict[box_name]
#         in_other_workflow = other_workflow is not None
#         where_workflow = ' '.join([f'[{workflow_name}]' for workflow_name in workflow_list]) or 'Not Found in any Workflow'
#         where_workflow_with_root = ' // '.join([f'[{workflow_name}] ({workflow_list_root_dict[workflow_name]})' for workflow_name in workflow_list_root_dict]) or ''
#         business_service = business_services_map.get(job_name, 'Not Found') if job_name in task_list else 'Task Not Found'
#         root_or_child = 'CHILD' if box_name else 'ROOT'

#         # Append log entry
#         compare_job_list.append({
#             BUSINESS_SERVICE: business_service,
#             'Task Name': job_name,
#             'Root/Child': root_or_child,
#             'In Same Workflow': 'TRUE' if in_same_workflow else 'FALSE',
#             'In Other Workflow': 'TRUE' if in_other_workflow else 'FALSE',
#             'Box Name': box_name,
#             'Root Box': root_box,
#             'Task Parent': where_workflow,
#             'Task Parent With Root': where_workflow_with_root,
#             'Other Workflow': other_workflow,
#         })

#     # Convert lists to DataFrames
#     df_job = pd.DataFrame(compare_job_list)

#     return df_job


# def compareTaskInWorkflowBaseSystem(df_job, df_workflow_vertex, df_task):
    
#     workflow_vertex_dict = df_workflow_vertex.groupby('Workflow')['Task'].apply(list).to_dict()
#     task_parent_workflow_dict = df_workflow_vertex.groupby('Task')['Workflow'].apply(list).to_dict()
    
#     root_box_list = df_job[ROOT_BOX].unique()
    
#     job_list = df_job[JOBNAME].unique()
#     task_list = set(df_task[TASKNAME_COLUMN].unique())
    
#     business_services_map = df_task.set_index(TASKNAME_COLUMN)['Member of Business Services'].to_dict()
    
        
    
    
    
    
    
    
def compareTaskInWorkflowBaseRootBox(df_job, df_workflow_vertex, df_workflow_vertex_prod, df_task):
    
    compare_task_list = []
    task_out_of_jil_list = []
    
    prod_workflow_list = df_workflow_vertex_prod['Workflow'].unique()
    prod_task_list = df_workflow_vertex_prod['Task'].unique()
    all_prod_task_list = set(prod_task_list) | set(prod_workflow_list)
    
    #workflow_vertex_dict = df_workflow_vertex.groupby('Workflow')['Task'].apply(list).to_dict()
    task_parent_workflow_dict = df_workflow_vertex.groupby('Task')['Workflow'].apply(list).to_dict()
    workflow_children_dict = df_workflow_vertex.groupby('Workflow')['Task'].apply(list).to_dict()
    #root_box_list = df_job[ROOT_BOX].unique()
    box_list = df_job[BOXNAME].unique()
    job_list = df_job[JOBNAME].unique()
    task_list = set(df_task[TASKNAME_COLUMN].unique())
    
    print("Processing Find Root Task...")
    root_task_dict, tree_root_task_dict = findRootTask(task_parent_workflow_dict, task_list)
    print("Processing Find Children Task...")
    children_task_dict = findChildrenTask(workflow_children_dict, task_list)
    print("Processing Find Related Workflow...")
    related_workflow_list = findRelatedWorkflow(children_task_dict, job_list)
    #createJson('children_task_dict.json', children_task_dict)
    print("Processing Transpose Root Task...")
    root_all_workflow_dict = transposeNestedDict(root_task_dict)
    #tree_root_all_workflow_dict = transposeNestedDict(tree_root_task_dict)
    #createJson('root_task_dict.json', root_task_dict)
    business_services_map = df_task.set_index(TASKNAME_COLUMN)['Member of Business Services'].to_dict()
    task_type_map = df_task.set_index(TASKNAME_COLUMN)['Type'].to_dict()
    
    print("Processing Compare Task...")
    max_merge_count = len(set(task_list) | set(job_list))
    count = 0
    for task_name in set(task_list) | set(job_list):
        

        box_name = None
        root_box_name = None
        workflow_list = []
        root_workflow_list = []
        tree_root_workflow_list = []
        workflow_list_in_root = {}
        
        if task_name in job_list:
            box_name = df_job.loc[df_job[JOBNAME] == task_name, BOXNAME].values[0] if task_name in df_job[JOBNAME].values else None
            root_box_name = df_job.loc[df_job[JOBNAME] == task_name, ROOT_BOX].values[0] if task_name in df_job[JOBNAME].values else None
            job_type = df_job.loc[df_job[JOBNAME] == task_name, JOBTYPE].values[0] if task_name in df_job[JOBNAME].values else None
            if root_box_name is SELF_START_NAME:
                root_box_name = task_name
                        
        if task_name in task_list:
            if task_name in task_parent_workflow_dict:
                workflow_list = task_parent_workflow_dict[task_name]
            else:
                workflow_list = []
            
            task_type = task_type_map.get(task_name, '')
            root_workflow_dict = root_task_dict.get(task_name, {})
            tree_root_workflow_dict = tree_root_task_dict.get(task_name, {})
            all_children_workflow_dict = children_task_dict.get(task_name, {})
            root_workflow_list = [root_workflow_name for workflow_name, root_workflow_list in root_workflow_dict.items() for root_workflow_name in root_workflow_list]
            tree_root_workflow_list = [tree_root_workflow_name for workflow_name, tree_root_workflow_list in tree_root_workflow_dict.items() for tree_root_workflow_name in tree_root_workflow_list]
            workflow_list_in_root = {}
            for root_workflow_name in root_workflow_list:
                if root_workflow_name in root_all_workflow_dict:
                    workflow_list_in_root[root_workflow_name] = []
                    workflow_list_in_root[root_workflow_name] = ', '.join(set([workflow_name for workflow_name in root_all_workflow_dict[root_workflow_name] if workflow_name in workflow_list]))
        
        if task_name in task_list and task_name in job_list:
            source = 'Both'
            type_of_task = task_type
        elif task_name in task_list and task_name not in job_list:
            source = 'Task'
            type_of_task = task_type
        elif task_name not in task_list and task_name in job_list:
            source = 'Job'
            type_of_task = job_type
        else:
            type_of_task = ''
            source = 'Not Found in any Source'
            
        if (any(workflow in box_list for workflow in workflow_list) or
            any(tree_root_workflow in related_workflow_list for tree_root_workflow in tree_root_workflow_list) or
            any(children in job_list for children in all_children_workflow_dict) or
            #any(task_name in related_task_list for task_name in related_task_list) or
            task_name in job_list):
            
                    
            if source == 'Task':
                remark_message = 'Task in System Only'
            elif source == 'Job':
                remark_message = 'Not Found Job in System'
            elif box_name in workflow_list and any(box_name != wf for wf in workflow_list):
                remark_message = 'Correct Workflow, Have Other Workflow'
            elif box_name in workflow_list and not any(box_name != wf for wf in workflow_list):
                remark_message = 'Correct Workflow'
            elif box_name not in workflow_list and any(box_name != wf for wf in workflow_list):
                if not box_name and workflow_list:
                    remark_message = 'Not in Box, Have Other Workflow'
                else:
                    remark_message = 'Not Same Workflow, Have Other Workflow'
            elif box_name not in workflow_list and not any(box_name != wf for wf in workflow_list):
                if box_name is None and workflow_list == []:
                    remark_message = 'Float Task, Not in any Workflow'
                elif box_name and not workflow_list:
                    remark_message = 'Remove from Workflow'
                else:
                    remark_message = 'Not Found in any Workflow'
            else:
                remark_message = 'Out of Category'        

            
            compare_task_list.append({
                'Source': source,
                'Golived': 'Golived' if task_name in all_prod_task_list else 'Not Golived',
                BUSINESS_SERVICE: business_services_map.get(task_name, 'Not Found') if task_name in task_list else 'Task Not Found',
                'Task Name': task_name,
                'Category Remark': remark_message,
                'Task Type': type_of_task,
                'Box Name': box_name,
                'Task Parent': ' '.join([f'[{workflow_name}]' for workflow_name in workflow_list]) if workflow_list else '',
                'Root Box': root_box_name,
                'Root Parent': ' '.join([f'[{root_workflow_name}]' for root_workflow_name in root_workflow_list]) if root_workflow_list else '',
                'Task Parent With Root': ' // '.join(f'({root_task_name}) [{workflow_name}]' for root_task_name, workflow_name in workflow_list_in_root.items()) if workflow_list_in_root else '',
                'Other Workflow': ', '.join([f'[{workflow_name}]' for workflow_name in workflow_list if workflow_name != box_name]) if workflow_list else None,
            })
        else:
            task_out_of_jil_list.append({
                'Source': source,
                'Golived': 'Golived' if task_name in all_prod_task_list else 'Not Golived',
                BUSINESS_SERVICE: business_services_map.get(task_name, 'Not Found') if task_name in task_list else 'Task Not Found',
                'Task Name': task_name,
                'Task Type': type_of_task,
                'Task Parent': ' '.join([f'[{workflow_name}]' for workflow_name in workflow_list]) if workflow_list else '',
                'Root Parent': ' '.join([f'[{workflow_name}]' for workflow_name in root_workflow_list]) if root_workflow_list else '',
                'Task Parent With Root': ' // '.join(f'({root_task_name}) [{workflow_name}]' for root_task_name, workflow_name in workflow_list_in_root.items()) if workflow_list_in_root else '',
            })
        count += 1
        if count % 100 == 0:
            print(f"Processing {count} / {max_merge_count}...", end='\r')
        if count == max_merge_count:
            print(f"Processing {count} / {max_merge_count}...")
        
    print("Processing Compare Task Done...")
    # Convert lists to DataFrames
    df_task = pd.DataFrame(compare_task_list)
    df_task_out_of_jil = pd.DataFrame(task_out_of_jil_list)
    
    return df_task, df_task_out_of_jil


def main():
    
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    df_job = getDataExcel()
    df_workflow_vertex = getReport(WORKFLOW_VERTEX_REPORT_TITLE)
    df_task = getReport(TASK_REPORT_TITLE)
    
    userpass = auth['TTB_PROD']
    clearAuth()
    updateAPIAuth(userpass['API_KEY'])
    #updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_PROD']
    updateURI(domain)
    df_workflow_vertex_prod = getReport(PROD_VERTEX_REPORT_TITLE)
    #df_task_in_workflow_base_on_jil = compareTaskInWorkflowBaseExcel(df_job, df_workflow_vertex, df_task)
    #df_task_in_workflow_base_on_system = compareTaskInWorkflowBaseSystem(df_job, df_workflow_vertex, df_task)
    df_task_in_workflow_base_on_root_box, df_task_out_of_jil = compareTaskInWorkflowBaseRootBox(df_job, df_workflow_vertex, df_workflow_vertex_prod, df_task)
    
    
    createExcel(OUTPUT_EXCEL_NAME, (BASE_ON_ROOT_BOX_SHEET_NAME, df_task_in_workflow_base_on_root_box), (OUT_OF_RELATE_SHEET_NAME, df_task_out_of_jil))

if __name__ == "__main__":
    main()