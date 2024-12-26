import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createFile import createJson, createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, viewParentTaskAPI


BUSSINESS_SERVICE_LIST = [
    "A0329 - ODS",
    "A0128 - Marketing Data Mart",
    "A0076 - Data Warehouse ETL",
    "A0031 - Data Mart"
    
]


task_configs_temp = {
    'name': '*',
    'type': 12,
    'businessServices': None,
}

parent_task_configs_temp = {
    'taskname': None,
}


def getListTaskbyBussinessService(business_service_list):
    task_list = []
    for business_service in business_service_list:
        task_configs = task_configs_temp.copy()
        task_configs['businessServices'] = business_service
        response = getListTaskAPI(task_configs)
        if response.status_code == 200:
            task_list.extend(response.json())
        
    return task_list


def checkParentTaskMonitor(task_list):
    parent_list = []
    non_parent_list = []
    count = 0
    for task in task_list:
        parent_task_configs = parent_task_configs_temp.copy()
        parent_task_configs = {
            'taskname': task['name'],
        }
        response_parent_list = viewParentTaskAPI(parent_task_configs, False)
        if response_parent_list.status_code == 200:
            parent_task = response_parent_list.json()
            if parent_task != []:
                parent_workflow_list = ", ".join([parent['name'] for parent in parent_task])
                parent_list.append({
                    'taskName': task['name'],
                    'parent': parent_workflow_list
                })
            else:
                non_parent_list.append({
                    'taskName': task['name'],
                })

        print(f'{count}/{len(task_list)} | {task["name"]} is done')
        count += 1
        
        
    return parent_list, non_parent_list
    




def CheckParentTaskMonitor():
    task_monitor_list = getListTaskbyBussinessService(BUSSINESS_SERVICE_LIST)
    parent_list, non_parent_list = checkParentTaskMonitor(task_monitor_list)
    df_parent = pd.DataFrame(parent_list)
    df_non_parent = pd.DataFrame(non_parent_list)
    
    createExcel('ParentTaskMonitor.xlsx', ('Parent Task Monitor', df_parent), ('Non Parent Task Monitor',df_non_parent))