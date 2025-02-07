import sys
import os
import pandas as pd
import re


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, runReportAPI, getTaskAPI



WORKFLOW_REPORT_NAME = 'AskMe - Workflow Report'

# JIL Columns
APPNAME_COLUMN = 'AppName'
JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'


# Report Columns
UAC_WORKFLOW_COLUMN = 'Name'
UAC_MEMBER_OF_BUSINESS_SERVICE_COLUMN = 'Member of Business Services'
UAC_NUMBER_OF_TASKS_COLUMN = 'Number Of Tasks'

# Suffix
TASK_MONITOR_SUFFIX = '-TM'

BUSINESS_SERVICES_LIST = [
    'A0076 - Data Warehouse ETL',
    'A0128 - Marketing Data Mart',
    'A0140 - NCB Data Submission',
    'A0329 - ODS',
    'A0356 - Big Data Foundation Platform',
    #'A0356 - Big Data Foundation Platform (None-PRD)',
    'A0033 - BOT DMS (Data Management System)',
    'A0031 - Data Mart',
    'A0360 - Oracle Financial Services Analytical App',
    #'A00000 - AskMe - Delete Tasks'
]




SELECTED_COLUMN = 'jobName'
FILTER_COLUMN = 'rootBox'

EXCEL_NAME = 'TaskAndConditionComparison.xlsx'

ZERO_TASK_LOG = 'Zero Task Log'
TASK_LOG = 'Task Log'
CONDITION_LOG = 'Condition Log'



report_configs_temp = {
    'reporttitle': None,
}

workflow_configs_temp = {
    'taskname': None,
}



def getSpecificColumn(df, column_name, filter_column_name = None, filter_value_list = None):
    column_list_dict = {}
    for filter_value in filter_value_list:
        df_filtered = df.copy()
        if filter_column_name is not None:
            df_filtered = df_filtered[df_filtered[filter_column_name].isin([filter_value])]

        #column_list_dict[filter_value] = []
        column_list_dict[filter_value] = df[df[column_name] == filter_value][column_name].tolist()
        if filter_column_name is not None:
            for index, row in df_filtered.iterrows():
                if row[column_name] not in column_list_dict[filter_value]:
                    column_list_dict[filter_value].append(row[column_name])
        
    return column_list_dict  

def getReport(report_title):
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = report_title
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')
    if response_csv.status_code == 200:
        print("Report generated successfully")
        #print(response_csv.text)
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        print("Error generating report")
        return None

def cleanNoneDF(df):
    df = df.astype(str).fillna('')
    df = df.replace('nan', '')
    return df

def renameTaskMonitor(task_name:str):
    new_task_name = task_name
    if task_name.endswith(TASK_MONITOR_SUFFIX):
        new_task_name = task_name[:-len(TASK_MONITOR_SUFFIX)]
    return new_task_name


# def compareTaskInWorkflow(df_job, workflow_name, workflow_data):
#     #excel_job_log = []
#     #uac_task_log = []
#     task_log = []
#     df_job_in_box = df_job[df_job[BOXNAME_COLUMN] == workflow_name]
#     df_workflow_job = df_job[df_job[JOBNAME_COLUMN] == workflow_name]
#     if df_workflow_job.empty:
#         print(f"Workflow {workflow_name} not found in job list")
#         task_log.append({
#             'workflow': workflow_name,
#             'taskname': None,
#             'category': 'workflow not found',
#             'message': 'Workflow not found in job list'
#         })
#     if df_job_in_box.empty:
#         print(f"No tasks found in workflow {workflow_name}")
#         task_log.append({
#             'workflow': workflow_name,
#             'taskname': None,
#             'category': 'no children tasks ',
#             'message': 'No tasks found in workflow'
#         })
#     #print(f"Workflow: {workflow_name}")
#     #print(f"Total tasks in job list: {len(df_job_in_box)}")
#     job_in_box_list = df_job_in_box[JOBNAME_COLUMN].tolist()
#     job_in_box_set = set(job_in_box_list)
    
#     workflow_vertex = workflow_data['workflowVertices']
#     workflow_vertex_name = [vertex['task']['value'] for vertex in workflow_vertex]
#     #print(f"Total tasks in workflow: {len(workflow_vertex_name)}")
#     workflow_vertex_name_without_task_monitor = [vertex_name for vertex_name in workflow_vertex_name if not vertex_name.endswith(TASK_MONITOR_SUFFIX)]
#     workflow_vertex_name_set = set(workflow_vertex_name_without_task_monitor)
    
#     task_union_set = job_in_box_set.union(workflow_vertex_name_set)
#     # Check if all the tasks in the workflow are in the job list
#     if task_union_set == job_in_box_set == workflow_vertex_name_set:
#         #print("All tasks in the workflow are in the job list")
#         task_log.append({
#             'workflowname': workflow_name,
#             'taskname': None,
#             'category': 'all match',
#             'source': 'UAC/Excel',
#             'remark': 'All tasks in the job list'
#         })
#         for task_name in task_union_set:
#             task_log.append({
#                 'workflowname': workflow_name,
#                 'taskname': task_name,
#                 'category': 'match',
#                 'source': 'UAC/Excel',
#                 'remark': 'Task is in both job list and workflow'
#             })
#     else:
#         #print("Have some tasks not in the job list")
#         tasks_not_in_job = workflow_vertex_name_set - job_in_box_set
#         jobs_not_in_workflow = job_in_box_set - workflow_vertex_name_set
#         # UAC Task Log
#         if tasks_not_in_job:
#             task_log.append({
#                 'workflowname': workflow_name,
#                 'taskname': None,
#                 'category': 'task not found in job list',
#                 'source': 'UAC',
#                 'remark': 'Have some UAC tasks not in job list'
#             })
#         elif jobs_not_in_workflow:
#             task_log.append({
#                 'workflowname': workflow_name,
#                 'taskname': None,
#                 'category': 'job not found in workflow',
#                 'source': 'Excel',
#                 'remark': 'Have some tasks not in workflow'
#             })
#         for task_name in task_union_set:
#             if task_name in tasks_not_in_job:
#                 task_log.append({
#                     'workflowname': workflow_name,
#                     'taskname': task_name,
#                     'category': 'task not found',
#                     'source': 'UAC',
#                     'remark': 'Task is in UAC but not in job list'
#                 })
#             elif task_name in jobs_not_in_workflow:
#                 task_log.append({
#                     'workflowname': workflow_name,
#                     'taskname': task_name,
#                     'category': 'job not found',
#                     'source': 'Excel',
#                     'remark': 'Task is in job list but not in workflow'
#                 })
#             else:
#                 task_log.append({
#                     'workflowname': workflow_name,
#                     'taskname': task_name,
#                     'category': 'match',
#                     'source': 'UAC/Excel',
#                     'remark': 'Task is in both job list and workflow'
#                 })
            
#     return task_log

def compareTaskInWorkflow(df_job, workflow_name, workflow_data):
    task_log = []

    # Filter job list for the given workflow
    df_job_in_box = df_job[df_job[BOXNAME_COLUMN] == workflow_name]
    df_workflow_job = df_job[df_job[JOBNAME_COLUMN] == workflow_name]

    # Handle missing workflows
    if df_workflow_job.empty:
        task_log.append({
            'workflowname': workflow_name,
            'taskname': None,
            'Excel status': 'workflow not found',
            'UAC status': None,
            'source': 'No Data',
            'remark': 'Workflow not found in excel list'
        })
        return task_log  # No need to continue

    # Handle missing tasks in workflow
    if df_job_in_box.empty:
        task_log.append({
            'workflowname': workflow_name,
            'taskname': None,
            'Excel status': 'no children tasks',
            'UAC status': None,
            'source': 'No Data',
            'remark': 'Not found job in workflow'
        })
        return task_log  # No need to continue

    # Get tasks from job list
    job_in_box_set = set(df_job_in_box[JOBNAME_COLUMN].tolist())

    # Get tasks from workflow data
    workflow_vertex = workflow_data['workflowVertices']
    workflow_vertex_name_set = {
        vertex['task']['value'] for vertex in workflow_vertex 
        if not vertex['task']['value'].endswith(TASK_MONITOR_SUFFIX)
    }

    # Compare job list and workflow tasks
    tasks_not_in_job = workflow_vertex_name_set - job_in_box_set
    jobs_not_in_workflow = job_in_box_set - workflow_vertex_name_set
    # tasks_not_in_job is [tasks in the workflow] but not in the job list
    # jobs_not_in_workflow is [tasks in the job list] but not in the workflow
    
    # Log the comparison results
    task_log.append({
        'workflowname': workflow_name,
        'taskname': None,
        'Excel status': 'all found' if workflow_vertex_name_set == job_in_box_set else ('some found' if tasks_not_in_job or jobs_not_in_workflow else 'not found'),
        'UAC status': 'all found' if workflow_vertex_name_set == job_in_box_set else ('some found' if tasks_not_in_job or jobs_not_in_workflow else 'not found'),
        'source': 'UAC/Excel' if workflow_vertex_name_set == job_in_box_set else 'Excel' if tasks_not_in_job else 'UAC',
        'remark': 'All tasks in the job list' if workflow_vertex_name_set == job_in_box_set else ('Have some UAC tasks not in job list' if tasks_not_in_job else 'Have some tasks not in workflow')
    })

    for task_name in job_in_box_set | workflow_vertex_name_set:  # Union of both sets
        task_log.append({
            'workflowname': workflow_name,
            'taskname': task_name,
            'Excel status': 'found' if task_name in job_in_box_set else 'not found',
            'UAC status': 'found' if task_name in workflow_vertex_name_set else 'not found',
            'source': 'UAC/Excel' if task_name in job_in_box_set and task_name in workflow_vertex_name_set else 'Excel' if task_name in job_in_box_set else 'UAC',
            'remark': 'Task is in both job list and workflow' if task_name in job_in_box_set and task_name in workflow_vertex_name_set else 'Task is in job list but not in workflow' if task_name in job_in_box_set else 'Task is in UAC but not in job list'
        })

    return task_log
     

def comapreConditionInWorkflow(df_job, workflow_name, workflow_data):
    condition_log = []
    
    return condition_log



def compareTaskAndCondition(df_job, df_workflow_report, list_dict):
    
    task_logs = []
    condition_logs = []
    
    all_list = [job_name for job_name_list in list_dict.values() for job_name in job_name_list]
    
    df_job = cleanNoneDF(df_job)
    df_workflow_report = cleanNoneDF(df_workflow_report)
    df_workflow_report[UAC_NUMBER_OF_TASKS_COLUMN] = pd.to_numeric(df_workflow_report[UAC_NUMBER_OF_TASKS_COLUMN], errors='coerce').astype('Int64')
    
    #df_job_in_list = df_job[df_job[JOBNAME_COLUMN].isin(all_list)]
    
    df_workflow_report_filtered_bussiness_service = df_workflow_report[df_workflow_report[UAC_MEMBER_OF_BUSINESS_SERVICE_COLUMN].isin(BUSINESS_SERVICES_LIST)]
    df_workflow_report_filtered_bussiness_service_zero_task = df_workflow_report_filtered_bussiness_service[df_workflow_report_filtered_bussiness_service[UAC_NUMBER_OF_TASKS_COLUMN] == 0]
    df_workflow_report_filtered_bussiness_service_zero_task_in_list = df_workflow_report_filtered_bussiness_service_zero_task[df_workflow_report_filtered_bussiness_service_zero_task[UAC_WORKFLOW_COLUMN].isin(all_list)]
    zero_task_workflow_in_list = df_workflow_report_filtered_bussiness_service_zero_task_in_list[UAC_WORKFLOW_COLUMN].tolist()
    ####
    zero_task_workflow_logs = [{UAC_WORKFLOW_COLUMN: workflow_name, UAC_NUMBER_OF_TASKS_COLUMN: 0} for workflow_name in zero_task_workflow_in_list]
    ####
    
    
    df_workflow_report_filtered_bussiness_service_non_zero_task = df_workflow_report_filtered_bussiness_service[df_workflow_report_filtered_bussiness_service[UAC_NUMBER_OF_TASKS_COLUMN] > 0]
    df_workflow_report_filtered_bussiness_service_non_zero_task_in_list = df_workflow_report_filtered_bussiness_service_non_zero_task[df_workflow_report_filtered_bussiness_service_non_zero_task[UAC_WORKFLOW_COLUMN].isin(all_list)]
    non_zero_task_workflow_list = df_workflow_report_filtered_bussiness_service_non_zero_task_in_list[UAC_WORKFLOW_COLUMN].tolist()
    ####
    
    # Get the task and condition of the workflow with non zero tasks
    print("Getting task and condition of the workflow with non zero tasks")
    #print("Workflow search : " + len(non_zero_task_workflow_list))
    for workflow_name in non_zero_task_workflow_list:
        workflow_config = workflow_configs_temp.copy()
        workflow_config['taskname'] = workflow_name
        response_workflow = getTaskAPI(workflow_config)
        if response_workflow.status_code == 200:
            workflow_data = response_workflow.json()
            task_log = compareTaskInWorkflow(df_job, workflow_name, workflow_data)
            condition_log = comapreConditionInWorkflow(df_job, workflow_name, workflow_data)
            
            task_logs.extend(task_log)
            
            condition_logs.extend(condition_log)
            
        else:
            print(f"Error getting workflow {workflow_name}")
        
    
    return zero_task_workflow_logs, task_logs, condition_logs




def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    df_job = getDataExcel('get Excel path with main job file')
    root_list_option = input("Do you want to use the root or list or all? (r/l/a): ")
    if root_list_option == 'a':
        all_list_job = df_job[JOBNAME_COLUMN].tolist()
        list_dict = {"ALL": all_list_job}
    else:
        if root_list_option == 'r':
            df_root = getDataExcel("Enter the path of the excel file with the root jobs")
        df_list_job = getDataExcel("Enter the path of the excel file with the list of jobs")
        list_job_name = df_list_job[JOBNAME_COLUMN].tolist()
        if root_list_option == 'r':
            list_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, list_job_name)
        else:
            list_dict = getSpecificColumn(df_job, SELECTED_COLUMN, None, list_job_name)
    print("---------------------------------")
    for key, value in list_dict.items():
        print(key, len(value))
    print("---------------------------------")
    
    df_workflow_report = getReport(WORKFLOW_REPORT_NAME)
    
    zero_task_logs, task_logs, condition_logs = compareTaskAndCondition(df_job, df_workflow_report, list_dict)
    
    zero_task_logs_df = pd.DataFrame(zero_task_logs)
    task_logs_df = pd.DataFrame(task_logs)
    condition_logs_df = pd.DataFrame(condition_logs)
    
    createExcel(EXCEL_NAME, (ZERO_TASK_LOG,zero_task_logs_df), (TASK_LOG, task_logs_df), (CONDITION_LOG, condition_logs_df))
    
    
    
    
if __name__ == '__main__':
    main()