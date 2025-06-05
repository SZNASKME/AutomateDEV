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

VERTEX_REPORT_TITLE = 'AskMe - Workflow Vertices'#'UAC - Workflow List Of Tasks By Workflow'
DEPEN_REPORT_TITLE = 'AskMe - Workflow Dependencies'
WORKFLOW_REPORT_TITLE = 'AskMe - Workflow Report'



TASK_MONITOR_SUFFIX = '-TM'
FILE_TRIGGER_SUFFIX = '.TRIG_001_F'


CHILDREN = 'Task In Workflow'
MONITOR_OUTSIDE_OF_LIST = 'Task Monitor Outside of List'
MONITOR_PARENT = 'Task Monitor Parent Workflow'
MONITOR_INSIDE_OF_LIST = 'Task Monitor Inside of List'

OUTPUT_EXCEL_NAME = 'TaskOutOfList.xlsx'

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

def checkFileTrigger(task_name : str):
    if task_name.endswith(FILE_TRIGGER_SUFFIX):
        return True
    return False
    
#############################################################################################################################################
        
def findTaskMonitorOutOfList(main_children_list, input_children_list):
    children_name_list = [child['Task'] for child in main_children_list]
    
    monitor_outside_of_list = []
    for task in input_children_list:
        task_name = task['Task']
        workflow_name = task['Workflow']
        if checkTaskMonitor(task_name):
            task_to_monitor = task_name.replace(TASK_MONITOR_SUFFIX, '')
        elif checkFileTrigger(task_name):
            task_to_monitor = task_name.replace(FILE_TRIGGER_SUFFIX, '')
        
        if task_to_monitor not in children_name_list:
            monitor_outside_of_list.append({
                'Task Monitor': task_name,
                'Workflow': workflow_name
            })
            
    return monitor_outside_of_list
        
def findParentOfTaskMonitor(input_children_list, task_parent_dict):
    monitor_parent = []
    
    for task in input_children_list:
        task_name = task['Task']
        #workflow_name = task['Workflow']
        if checkTaskMonitor(task_name):
            task_to_monitor = task_name.replace(TASK_MONITOR_SUFFIX, '')
        elif checkFileTrigger(task_name):
            task_to_monitor = task_name.replace(FILE_TRIGGER_SUFFIX, '')
        
        if task_name in task_parent_dict:
            parent_workflow_list = task_parent_dict[task_name]
            for parent_workflow in parent_workflow_list:
                monitor_parent.append({
                    'Task Monitor': task_name,
                    'Parent Workflow': parent_workflow,
                    'Task to Monitor': task_to_monitor,
                    'Task to Monitor Parent': ', '.join(task_parent_dict.get(task_to_monitor, []))
                })
                
        else:
            monitor_parent.append({
                'Task Monitor': task_name,
                'Parent Workflow': '',
                'Task to Monitor': task_to_monitor,
                'Task to Monitor Parent': ', '.join(task_parent_dict.get(task_to_monitor, []))
            })
        
    return monitor_parent

def findTaskMonitorInList(input_children_list, task_parent_dict):
    monitor_inside_of_list = []
    
    children_name_list = [child['Task'] for child in input_children_list]
    
    for task_name in task_parent_dict:
        if checkTaskMonitor(task_name) or checkFileTrigger(task_name):
            task_parent_list = task_parent_dict[task_name]
            if checkTaskMonitor(task_name):
                task_to_monitor = task_name.replace(TASK_MONITOR_SUFFIX, '')
            elif checkFileTrigger(task_name):
                task_to_monitor = task_name.replace(FILE_TRIGGER_SUFFIX, '')
            for parent in task_parent_list:
                if parent not in children_name_list and task_to_monitor in children_name_list:
                    monitor_inside_of_list.append({
                        'Task Monitor': task_name,
                        'Parent Workflow': parent,
                        'Task to Monitor': task_to_monitor,
                    })
        
    return monitor_inside_of_list
        
#############################################################################################################################################

def findBeforeTaskInWorkflow(workflow_vertex_dict, workflow_depen_dict, workflow_list, output_task_list):

    

    before_search_stack = {}

    visited = {}
    
    for task in output_task_list:
        
        task_name = task['Task']
        workflow_name = task['Workflow']
        
        if workflow_name not in before_search_stack:
            before_search_stack[workflow_name] = []
        
        if workflow_name not in visited:
            visited[workflow_name] = set()
        
        if task_name not in visited[workflow_name]:
            before_search_stack[workflow_name].append(task_name)
            visited[workflow_name].add(task_name)
            
        



###############################################################################################################################################

def createDependencyDict(df_workflow_depen, df_workflow_vertex):
    vertex_to_task = df_workflow_vertex.set_index('Vertex Id')['Task'].to_dict()

    depen_dict = {}
    for workflow, group in df_workflow_depen.groupby('Workflow'):
        depen_dict[workflow] = [
            {
                'Source Vertex Id': row['Source Vertex Id'],
                'Source Task': vertex_to_task.get(row['Source Vertex Id'], None),
                'Target Vertex Id': row['Target Vertex Id'],
                'Target Task': vertex_to_task.get(row['Target Vertex Id'], None),
                'Condition': row.get('Condition', None)
            }
            for _, row in group.iterrows()
        ]

    return depen_dict

def recursiveSearchChildrenInWorkflow(workflow_vertex_dict, workflow_list, children_list=None, child_search_stack=None):

    if children_list is None:
        children_list = []
    
    if child_search_stack is None:
        child_search_stack = []

    visited = set()  # To track visited tasks and avoid duplicates
    for task in child_search_stack:
        children_list.append({
            'Task': task,
            'Workflow': 'Main Workflow'
        })

    while child_search_stack:
        current_child = child_search_stack.pop()

        # Skip if already visited
        if current_child in visited:
            continue
        visited.add(current_child)

        # If the current child is a workflow, process its children
        # workflow_vertex_dict[current_child][vertex_id] = task_name
        if current_child in workflow_vertex_dict:
            for vertex_id, task_name in workflow_vertex_dict[current_child].items():
                if task_name not in visited:
                    children_list.append({
                        'Task': task_name,
                        'Workflow': current_child
                    })
                    child_search_stack.append(task_name)

    return children_list


def prepareWorkflowVertexDict(df_workflow_vertex, workflow_list):
    workflow_vertex_dict = {}
    for workflow in workflow_list:
        workflow_vertex_rows = df_workflow_vertex[df_workflow_vertex['Workflow'] == workflow]
        if not workflow_vertex_rows.empty:
            for _, row in workflow_vertex_rows.iterrows():
                vertex_id = row['Vertex Id']
                task_name = row['Task']
                if workflow not in workflow_vertex_dict:
                    workflow_vertex_dict[workflow] = {}
                if vertex_id not in workflow_vertex_dict[workflow]:
                    workflow_vertex_dict[workflow][vertex_id] = task_name
                
        else:
            workflow_vertex_dict[workflow] = {}
            
    return workflow_vertex_dict
        


################################################################################################################################################

def findAllTaskOutOfList(df_workflow_vertex, df_workflow_depen, df_workflow, task_list):
    
    ## find all children in workflow
    children_list = []
    child_search_stack = []
    child_search_stack.extend(task_list)
    
    workflow_list = df_workflow['Name'].tolist()
    
    workflow_vertex_dict = prepareWorkflowVertexDict(df_workflow_vertex, workflow_list)
    task_parent_dict = df_workflow_vertex.groupby('Task')['Workflow'].apply(list).to_dict()
    
    workflow_depen_dict = createDependencyDict(df_workflow_depen, df_workflow_vertex)

    children_list = recursiveSearchChildrenInWorkflow(workflow_vertex_dict, workflow_list, children_list, child_search_stack)
    children_list_exclude_task_monitor = [child for child in children_list if not checkTaskMonitor(child['Task']) and not checkFileTrigger(child['Task'])]
    children_list_only_task_monitor = [child for child in children_list if checkTaskMonitor(child['Task']) or checkFileTrigger(child['Task'])]
    
    monitor_outside_of_list = findTaskMonitorOutOfList(children_list_exclude_task_monitor, children_list_only_task_monitor)
    
    monitor_parent = findParentOfTaskMonitor(children_list_only_task_monitor, task_parent_dict)
    
    outside_monitor_inside_of_list = findTaskMonitorInList(children_list_exclude_task_monitor, task_parent_dict)
    
    
    
    
    before_task_list = findBeforeTaskInWorkflow(workflow_vertex_dict, workflow_depen_dict, workflow_list, children_list_exclude_task_monitor)
    
    #after_task_list = findAfterTaskInWorkflow(workflow_vertex_dict, workflow_list, children_list_exclude_task_monitor)
    
    #print("children_list", len(children_list))
    #print("children_list_exclude_task_monitor", len(children_list_exclude_task_monitor))
    
    
    df_children = pd.DataFrame(children_list)
    df_monitor_outside_of_list = pd.DataFrame(monitor_outside_of_list)
    df_monitor_parent = pd.DataFrame(monitor_parent)
    df_monitor_inside_of_list = pd.DataFrame(outside_monitor_inside_of_list)
    
    return {
        'children': df_children,
        'monitor_outside_of_list': df_monitor_outside_of_list,
        'monitor_parent': df_monitor_parent,
        'monitor_inside_of_list': df_monitor_inside_of_list
    }




def main():
    
    auth = loadJson('auth.json')
    #userpass = auth['TTB']
    #updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    userpass = auth['TTB_PROD']
    updateAPIAuth(userpass['API_KEY'])

    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['TTB_PROD']
    updateURI(domain)
    
    
    #### Get the workflow list
    df_job = getDataExcel()
    task_list = df_job['jobName'].tolist()
    
    df_workflow_vertex = getReport(VERTEX_REPORT_TITLE)
    df_workflow_depen = getReport(DEPEN_REPORT_TITLE)
    df_workflow = getReport(WORKFLOW_REPORT_TITLE)
    df_all_output = findAllTaskOutOfList(df_workflow_vertex, df_workflow_depen, df_workflow, task_list)
    df_children = df_all_output['children']
    df_monitor_outside_of_list = df_all_output['monitor_outside_of_list']
    df_monitor_parent = df_all_output['monitor_parent']
    df_monitor_inside_of_list = df_all_output['monitor_inside_of_list']

    
    
    
    createExcel(OUTPUT_EXCEL_NAME, (CHILDREN, df_children), (MONITOR_OUTSIDE_OF_LIST, df_monitor_outside_of_list), (MONITOR_PARENT, df_monitor_parent), (MONITOR_INSIDE_OF_LIST, df_monitor_inside_of_list))


if __name__ == "__main__":
    main()