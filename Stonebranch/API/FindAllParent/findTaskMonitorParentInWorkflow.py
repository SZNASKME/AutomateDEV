import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, viewParentTaskAPI, getTaskAPI
from utils.createFile import createExcel, createJson



task_adv_configs_temp = {
    'taskname': None,
}


workflow_list = [
    'DWH_BOX_INACTIVE_23.55_B'
]


def getTaskMonitorList():
    list_task_monitor_dict = {}
    for workflow in workflow_list:
        task_adv_configs = task_adv_configs_temp.copy()
        task_adv_configs['taskname'] = workflow
        response = getTaskAPI(task_adv_configs)
        if response.status_code == 200:
            task_data = response.json()
            task_name = task_data['name']
            list_task_monitor_dict[task_name] = []
            if task_data['type'] == 'taskWorkflow':
                vertex_list = task_data['workflowVertices']
                for vertex in vertex_list:
                    vertex_name = vertex['task']['value']
                    if vertex_name.endswith('-TM'):
                        list_task_monitor_dict[task_data['name']].append(vertex_name)
                
    return list_task_monitor_dict


def findAllParentTaskMonitor(list_task_monitor_dict):
    all_parent_task_monitor_dict = {}
    for workflow in list_task_monitor_dict:
        for task_monitor_name in list_task_monitor_dict[workflow]:
            task_adv_configs = task_adv_configs_temp.copy()
            task_adv_configs['taskname'] = task_monitor_name
            response_parent = viewParentTaskAPI(task_adv_configs)
            if response_parent.status_code == 200:
                if task_monitor_name not in all_parent_task_monitor_dict:
                    all_parent_task_monitor_dict[task_monitor_name] = []
                parent_data = response_parent.json()
                for parent in parent_data:
                    parent_name = parent['name']
                    if parent_name not in all_parent_task_monitor_dict[task_monitor_name]:
                        all_parent_task_monitor_dict[task_monitor_name].append(parent_name)
    
    return all_parent_task_monitor_dict


def prepareDataFrameFromDictList(all_parent_task_monitor_dict):
    list_parent_task_monitor = []
    for task_monitor, parent_list in all_parent_task_monitor_dict.items():
        for parent in parent_list:
            list_parent_task_monitor.append({
                'Task Monitor': task_monitor,
                'Parent': parent
            })
    df_list_parent_task_monitor = pd.DataFrame(list_parent_task_monitor)
    return df_list_parent_task_monitor


def main():
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    list_task_monitor_dict = getTaskMonitorList()
    all_parent_task_monitor_dict = findAllParentTaskMonitor(list_task_monitor_dict)
    df_parent_task_monitor = prepareDataFrameFromDictList(all_parent_task_monitor_dict)
    print(json.dumps(all_parent_task_monitor_dict, indent=4))
    
    createJson('allParentTaskMonitorList.json', all_parent_task_monitor_dict)
    createExcel('ParentTaskMonitorList.xlsx', ('Parent Task Monitor', df_parent_task_monitor))
    
    
    
    
if __name__ == '__main__':
    main()