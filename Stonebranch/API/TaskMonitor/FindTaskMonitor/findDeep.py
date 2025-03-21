import sys
import os
import json
import pandas as pd


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import getListTriggerAdvancedAPI, getTaskAPI, updateURI, updateAuth, getListQualifyingTriggerAPI, getListTaskAPI, viewParentTaskAPI
from utils.readFile import loadJson
from utils.createFile import createJson

API_TRIGGER_TYPE = [1,2,3,4,5,6,8,9,10,11,12]

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


task_adv_configs_temp = {
    'taskname': None,
}

workflow_configs_temp = {
    'name': '*',
    'type': 1,
    'businessServices': None,
}

trigger_adv_configs_temp = {
    'triggername': '*',
    #'type': 2,
    #'enabled': True,
    'businessServices': None,
}

SUFFIX = '-TM'

#test_trigger_list = [
#    "DWH_HL_BUNDLE_CC_DAILY_B-TR001",
#    "DWH_DAILY_B-TR001",
#    "DWH_CSM_BIC_DAILY_B-TR001",
#]

######################################################################################################################

def getListTrigger():
    
    trigger_list = []

    for type in API_TRIGGER_TYPE:
        for business_service in BUSINESS_SERVICES_LIST:
            trigger_adv_configs = trigger_adv_configs_temp.copy()
            trigger_adv_configs['type'] = type
            trigger_adv_configs['businessServices'] = business_service
            response = getListTriggerAdvancedAPI(trigger_adv_configs)
            if response.status_code == 200:
                trigger_list.extend(response.json())
            
    return trigger_list
    

def getListWorkflow():
    
    workflow_list = []
    
    for business_service in BUSINESS_SERVICES_LIST:
        workflow_configs = workflow_configs_temp.copy()
        workflow_configs['businessServices'] = business_service
        response = getListTaskAPI(workflow_configs)
        if response.status_code == 200:
            workflow_list.extend(response.json())
    
    return workflow_list

def getListSpecificField(workflow_list, field='name'):
    workflow_name_list = []
    for workflow in workflow_list:
        workflow_name_list.append(workflow[field])
    return workflow_name_list

def checkSuffix(name, suffix):
    if name.endswith(suffix):
        return True
    return False

######################################################################################################################

def recursiveSearchTaskMonitorInWorkflow(task_name:str, task_monitor_dict:dict, workflow_name:str, workflow_list = []):
    task_configs = task_adv_configs_temp.copy()
    task_configs['taskname'] = task_name
    response = getTaskAPI(task_configs)
    if response.status_code == 200:
        task_data = response.json()
        if task_data['type'] == 'taskWorkflow':
            workflow = response.json()
            if workflow['workflowVertices']:
                for vertex in workflow['workflowVertices']:
                    if (vertex['task']['value'] in workflow_list 
                        or checkSuffix(vertex['task']['value'], SUFFIX)):
                        task_monitor_dict = recursiveSearchTaskMonitorInWorkflow(vertex['task']['value'], task_monitor_dict, workflow['name'], workflow_list)
        elif task_data['type'] == 'taskMonitor':
            if workflow_name not in task_monitor_dict.keys():
                task_monitor_dict[workflow_name] = []
            task_monitor_dict[workflow_name].append(task_data)
    return task_monitor_dict

######################################################################################################################

def listTaskToMonitor(task_monitor_dict):
    task_to_monitor_dict = {}
    for workflow_name, task_monitor_list in task_monitor_dict.items():
        task_to_monitor_dict[workflow_name] = {}
        for task_monitor in task_monitor_list:
            task_name = task_monitor['name']
            task_to_monitor_name = task_monitor['taskMonName']
            task_to_monitor_dict[workflow_name][task_name] = task_to_monitor_name
    
    return task_to_monitor_dict
    
######################################################################################################################

def findTaskMonitors(trigger_list, workflow_list = []):
    result_task_monitor_dict = {}
    
    for trigger in trigger_list:
        result_task_monitor_dict[trigger['name']] = {}
        task_list = trigger['tasks']
        for task_name in task_list:
            task_monitor_dict = recursiveSearchTaskMonitorInWorkflow(task_name, {}, '', workflow_list)
            result_task_monitor_dict[trigger['name']][task_name] = listTaskToMonitor(task_monitor_dict)
    
    return result_task_monitor_dict

######################################################################################################################


######################################################################################################################

def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.86']
    updateURI(domain)
    response_trigger = getListTrigger()
    response_workflow = getListWorkflow()
    workflow_name_list = getListSpecificField(response_workflow,'name')
    result = findTaskMonitors(response_trigger, workflow_name_list)
    createJson('UAT_result_restructure.json', result)
    
if __name__ == '__main__':
    main()
    
## Get Task and Trigger Information from UAC and restructure to JSON
## To create Excel file, go to cleanJsonToExcel.py