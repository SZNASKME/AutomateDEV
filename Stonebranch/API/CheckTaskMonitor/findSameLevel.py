import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTaskAdvancedAPI, getListTaskAPI, getTaskAPI, updateURI, updateAuth
from utils.createExcel import createExcel
from utils.loadFile import loadJson

task_adv_configs_temp = {
    'taskname': '*',
    'type': 1,
    'businessServices': 'A0076 - Data Warehouse ETL',
}

task_configs_temp = {
    'name': '*',
    'type': 1,
    'businessServices': 'A0076 - Data Warehouse ETL',
}


SUFFIX = '-TM'



def getWorkflow():
    #response = getListTaskAdvancedAPI(task_adv_configs_temp)
    response = getListTaskAPI(task_configs_temp)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def checkSameLevelTaskMonitorEach(workflow_list):
    same_level_task_monitor_workflow_dict = {}
    for task in workflow_list:
        if task['type'] != 'Workflow':
            continue
        
        task_configs = {
            'taskid': task['sysId'],
        }
        response_workflow = getTaskAPI(task_configs)
        
        if response_workflow.status_code == 200:
            workflow = response_workflow.json()
            same_level_task_monitor_dict = {}
            if workflow['workflowVertices']:
                for vertex in workflow['workflowVertices']:
                    if checkSuffix(vertex['task']['value'], SUFFIX):
                        for vertex_check in workflow['workflowVertices']:
                            if vertex_check['task']['value'] == getNameWithoutSuffix(vertex['task']['value'], SUFFIX):
                                same_level_task_monitor_dict[vertex['task']['value']] = vertex_check['task']['value']
            if same_level_task_monitor_dict:
                same_level_task_monitor_workflow_dict[workflow['name']] = same_level_task_monitor_dict
        elif response_workflow.status_code != 200:
            return same_level_task_monitor_workflow_dict
        
    return same_level_task_monitor_workflow_dict

def checkSameLevelTaskMonitorSingle(workflow_list):
    same_level_task_monitor_workflow_dict = {}
    for workflow in workflow_list:
        same_level_task_monitor_dict = {}
        if workflow['type'] == 'taskWorkflow' and workflow['workflowVertices']:
            for vertex in workflow['workflowVertices']:
                if checkSuffix(vertex['task']['value'], SUFFIX):
                    for vertex_check in workflow['workflowVertices']:
                        if vertex_check['task']['value'] == getNameWithoutSuffix(vertex['task']['value'], SUFFIX):
                            same_level_task_monitor_dict[vertex['task']['value']] = vertex_check['task']['value']
        if same_level_task_monitor_dict:
            same_level_task_monitor_workflow_dict[workflow['name']] = same_level_task_monitor_dict
    return same_level_task_monitor_workflow_dict

def checkSuffix(task_name:str, suffix:str):
    if task_name.endswith(suffix):
        return True
    else:
        return False
    
def getNameWithoutSuffix(task_name:str, suffix:str):
    if checkSuffix(task_name, suffix):
        return task_name[:-len(suffix)]
    else:
        return task_name


# https://ttbdevstb.stonebranch.cloud/resources
def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain = "https://ttbdevstb.stonebranch.cloud/resources"
    updateURI(domain)
    reponse_workflow = getWorkflow()
    print(len(reponse_workflow))
    same_level_task_monitor = checkSameLevelTaskMonitorEach(reponse_workflow)
    print(json.dumps(same_level_task_monitor, indent=4))
    
    #createExcel
    
    
    
    
if __name__ == "__main__":
    main()