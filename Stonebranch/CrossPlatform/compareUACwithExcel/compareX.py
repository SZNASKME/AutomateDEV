import sys
import os
import pandas as pd
import re


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import *

REPORT_TITLE = 'AskMe - Workflow Vertices'

JOBNAME = 'jobName'
JOBTYPE = 'jobType'
BOXNAME = 'box_name'
CONDITION = 'condition'

TASK_MONITOR_SUFFIX = '-TM'


LOG_SHEET_NAME = 'Task In Workflow'
SELF_START_SHEET_NAME = 'Self Start Task'
OUTPUT_EXCEL_NAME = 'TaskInWorkflow.xlsx'

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


def findOtherWorkflow(transpose_workflow_vertex_dict, task_name, workflow_name):
    other_workflow_list = []
    if task_name in transpose_workflow_vertex_dict:
        workflow_list = transpose_workflow_vertex_dict[task_name]
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

# def compareTaskInWorkflow(df_job, df_workflow_vertex):
#     log_list = []
#     self_start_list = []
    
#     workflow_vertex_dict = {}
#     transpose_workflow_vertex_dict = {}
#     workflow_task_monitor_vertex_dict = {}
#     transpose_task_monitor_vertex_dict = {}
    
#     for vertex_row in df_workflow_vertex.itertuples(index=False):
#         workflow_name = getattr(vertex_row, 'Workflow')
#         task_name = getattr(vertex_row, 'Task')
        
#         if workflow_name not in workflow_vertex_dict:
#             workflow_vertex_dict[workflow_name] = []
#         if task_name not in transpose_workflow_vertex_dict:
#             transpose_workflow_vertex_dict[task_name] = []
            
#         #if workflow_name not in workflow_task_monitor_vertex_dict:
#         #    workflow_task_monitor_vertex_dict[workflow_name] = []
#         #if task_name not in transpose_task_monitor_vertex_dict:
#         #    transpose_task_monitor_vertex_dict[task_name] = []
        
#         if checkTaskMonitor(task_name):
#             #if task_name not in workflow_task_monitor_vertex_dict[workflow_name]:
#             #    workflow_task_monitor_vertex_dict[workflow_name].append(task_name)
#             #if workflow_name not in transpose_task_monitor_vertex_dict[task_name]:
#             #    transpose_task_monitor_vertex_dict[task_name].append(workflow_name)
#             continue
#         else:
#             if task_name not in workflow_vertex_dict[workflow_name]:
#                 workflow_vertex_dict[workflow_name].append(task_name)
#             if workflow_name not in transpose_workflow_vertex_dict[task_name]:
#                 transpose_workflow_vertex_dict[task_name].append(workflow_name)

    
    
    
#     for row in df_job.itertuples(index=False):
#         job_name = getattr(row, JOBNAME)
#         job_type = getattr(row, JOBTYPE)
#         box_name = getattr(row, BOXNAME)
#         condition = getattr(row, CONDITION)

#         if pd.isna(box_name):
#             box_name = None

#         if box_name is None and job_type == 'BOX':
#             self_start_list.append({
#                 JOBNAME: job_name,
#                 JOBTYPE: job_type,
#                 CONDITION: condition,
#             })
#             #continue
#         #print(f'job_name: {job_name}, job_type: {job_type}, box_name: {box_name}')
#         other_workflow = findOtherWorkflow(transpose_workflow_vertex_dict, job_name, box_name)
#         if box_name in workflow_vertex_dict and job_name in workflow_vertex_dict[box_name]:
#             log_list.append({
#                 JOBNAME: job_name,
#                 JOBTYPE: job_type,
#                 BOXNAME: box_name,
#                 'Root/Child': 'CHILD',
#                 'In Same Workflow': 'TRUE',
#                 'In Other Workflow': 'TRUE' if (other_workflow != 'Not Found' or other_workflow is None) else 'FALSE',
#                 'Where': findWorkflowName(workflow_vertex_dict, job_name),
#                 'Other Workflow': other_workflow if other_workflow != 'Not Found' else None
#             })
#         elif box_name in workflow_vertex_dict and job_name not in workflow_vertex_dict[box_name]:
#             log_list.append({
#                 JOBNAME: job_name,
#                 JOBTYPE: job_type,
#                 BOXNAME: box_name,
#                 'Root/Child': 'CHILD',
#                 'In Same Workflow': 'FALSE',
#                 'In Other Workflow': 'TRUE' if other_workflow != 'Not Found' else 'FALSE',
#                 'Where': findWorkflowName(workflow_vertex_dict, job_name),
#                 'Other Workflow': other_workflow if other_workflow != 'Not Found' else None
#             })
#         elif box_name is None and job_name in workflow_vertex_dict:
#             log_list.append({
#                 JOBNAME: job_name,
#                 JOBTYPE: job_type,
#                 BOXNAME: box_name,
#                 'Root/Child': 'ROOT',
#                 'In Same Workflow': 'FALSE',
#                 'In Other Workflow': 'TRUE',
#                 'Where': findWorkflowName(workflow_vertex_dict, job_name),
#                 'Other Workflow': other_workflow if other_workflow != 'Not Found' else None
#             })
#         elif box_name is None and job_name not in workflow_vertex_dict:
#             log_list.append({
#                 JOBNAME: job_name,
#                 JOBTYPE: job_type,
#                 BOXNAME: box_name,
#                 'Root/Child': 'ROOT',
#                 'In Same Workflow': 'FALSE',
#                 'In Other Workflow': 'FALSE',
#                 'Where': findWorkflowName(workflow_vertex_dict, job_name),
#                 'Other Workflow': other_workflow if other_workflow != 'Not Found' else None
#             })
            
#         # else:
#         #     log_list.append({
#         #         JOBNAME: job_name,
#         #         JOBTYPE: job_type,
#         #         BOXNAME: box_name,
#         #         'In Same Workflow': 'NOT IN CASE',
#         #         'In Other Workflow': 'NOT IN CASE',
#         #         'Where': 'NOT IN CASE',
#         #         'Other Workflow': 'NOT IN CASE'
#         #     })
        
#     df_log = pd.DataFrame(log_list)
#     df_self_start = pd.DataFrame(self_start_list)
#     return df_log, df_self_start
        
def compareTaskInWorkflow(df_job, df_workflow_vertex):
    # Initialize dictionaries and lists
    workflow_vertex_dict = df_workflow_vertex.groupby('Workflow')['Task'].apply(list).to_dict()
    transpose_workflow_vertex_dict = df_workflow_vertex.groupby('Task')['Workflow'].apply(list).to_dict()

    log_list = []
    self_start_list = []

    # Iterate over jobs
    for row in df_job.itertuples(index=False):
        job_name = getattr(row, JOBNAME)
        job_type = getattr(row, JOBTYPE)
        box_name = getattr(row, BOXNAME)
        condition = getattr(row, CONDITION)

        # Handle NaN values for box_name
        box_name = None if pd.isna(box_name) else box_name

        # Identify self-start tasks
        if box_name is None and job_type == 'BOX':
            self_start_list.append({
                JOBNAME: job_name,
                JOBTYPE: job_type,
                CONDITION: condition,
            })

        # Find other workflows and workflow details
        other_workflow = ', '.join(
            [wf for wf in transpose_workflow_vertex_dict.get(job_name, []) if wf != box_name]
        ) or None
        in_same_workflow = box_name in workflow_vertex_dict and job_name in workflow_vertex_dict[box_name]
        in_other_workflow = other_workflow is not None
        where_workflow = ', '.join(transpose_workflow_vertex_dict.get(job_name, [])) or 'Not Found'

        # Determine root/child status
        root_or_child = 'CHILD' if box_name else 'ROOT'

        # Append log entry
        log_list.append({
            JOBNAME: job_name,
            JOBTYPE: job_type,
            BOXNAME: box_name,
            'Root/Child': root_or_child,
            'In Same Workflow': 'TRUE' if in_same_workflow else 'FALSE',
            'In Other Workflow': 'TRUE' if in_other_workflow else 'FALSE',
            'Where': where_workflow,
            'Other Workflow': other_workflow,
        })

    # Convert lists to DataFrames
    df_log = pd.DataFrame(log_list)
    df_self_start = pd.DataFrame(self_start_list)

    return df_log, df_self_start                

def main():
    
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    
    df_job = getDataExcel()
    df_workflow_vertex = getReport(REPORT_TITLE)
    df_task_in_workflow_log, df_self_start = compareTaskInWorkflow(df_job, df_workflow_vertex)

    
    
    
    createExcel(OUTPUT_EXCEL_NAME, (LOG_SHEET_NAME, df_task_in_workflow_log), (SELF_START_SHEET_NAME, df_self_start))


if __name__ == "__main__":
    main()