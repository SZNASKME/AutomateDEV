import sys
import os
import json
import pandas as pd


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTriggerAdvancedAPI, getTaskAPI, updateURI, updateAuth, getListQualifyingTriggerAPI, getListTaskAPI, viewParentTaskAPI
from utils.readFile import loadJson
from utils.createFile import createJson
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from dateutil import parser


parent_configs_temp = {
    'taskname': None,
}

task_adv_configs_temp = {
    'taskname': None,
}

workflow_configs_temp = {
    'name': '*',
    'type': 1,
    #'businessServices': 'A0076 - Data Warehouse ETL',
}

trigger_configs_temp = {
    'triggername': None,
}

trigger_adv_configs_temp = {
    'triggername': '*',
    'type': 2,
    #'enabled': True,
    'businessServices': 'A0076 - Data Warehouse ETL',
}

trigger_qulifying_time_temp = {
    'triggername': None,
    'count': 60,
}

SUFFIX = '-TM'
DATETIME_FORMAT = '%d/%m/%y-%H:%M:%S'
DAY_PERIOD = 7
MAX_WORKERS = 8
#test_trigger_list = [
#    "DWH_HL_BUNDLE_CC_DAILY_B-TR001",
#    "DWH_DAILY_B-TR001",
#    "DWH_CSM_BIC_DAILY_B-TR001",
#]

######################################################################################################################

def getListTrigger():
    response = getListTriggerAdvancedAPI(trigger_adv_configs_temp)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def getListWorkflow():
    response = getListTaskAPI(workflow_configs_temp)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def getListSpecificField(workflow_list, field = 'name'):
    workflow_name_list = []
    for workflow in workflow_list:
        workflow_name_list.append(workflow[field])
    return workflow_name_list

def checkSuffix(name, suffix):
    if name.endswith(suffix):
        return True
    return False

def getTriggerNameFromTask(task_name, trigger_list):
    trigger_name_list = []
    is_in_list = True
    for trigger in trigger_list:
        if task_name in trigger['tasks']:
            trigger_name_list.append(trigger['name'])
    
    if len(trigger_name_list) == 0:
        is_in_list = False
    return trigger_name_list, is_in_list

def transformTime(time_string:str) -> str:
    date_object = parser.parse(time_string)
    formatted_date = date_object.strftime("%d/%m/%y-%H:%M:%S")
    return formatted_date

######################################################################################################################

def checkTimeDifferenceProblem(task_qualifying_time, trigger_qualifying_time, day_period = DAY_PERIOD):
    
    task_qualifying_datetime = [datetime.strptime(date_str, DATETIME_FORMAT) for date_str in task_qualifying_time]
    trigger_qualifying_datetime = [datetime.strptime(date_str, DATETIME_FORMAT) for date_str in trigger_qualifying_time]
    exist_period = timedelta(days = day_period)
    
    if not task_qualifying_datetime or not trigger_qualifying_datetime:
        return False
    
    last_task_time = max(task_qualifying_datetime)
    for trigger_time in trigger_qualifying_datetime:
        if trigger_time <= last_task_time:
            exist_task_time = trigger_time - exist_period
            exist_task_run = False
            for task_time in task_qualifying_datetime:
                if task_time >= exist_task_time and task_time <= trigger_time:
                    exist_task_run = True
                    break
                if task_time > trigger_time:
                    break
            if not exist_task_run:
                return True
        else:
            break
                
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

def recursiveSearchParentTimeTrigger(task_name, trigger_list, parent_trigger_name_list = [], out_of_trigger_list = False):
    parent_configs = parent_configs_temp.copy()
    parent_configs['taskname'] = task_name
    response = viewParentTaskAPI(parent_configs)
    if response.status_code == 200:
        parent_data = response.json()
        if parent_data:
            for parent in parent_data:
                parent_name =  parent['name']
                parent_trigger_name_list, out_of_trigger_list = recursiveSearchParentTimeTrigger(parent_name, trigger_list, parent_trigger_name_list, out_of_trigger_list)
        else:
            trigger_name, is_in_list = getTriggerNameFromTask(task_name, trigger_list)
            parent_trigger_name_list.extend(trigger_name)
            if not is_in_list:
                out_of_trigger_list = True
    
    return parent_trigger_name_list, out_of_trigger_list

######################################################################################################################

def getQualifyingTimeTrigger(trigger_name, count = 60):
    qualifying_time_list = []
    trigger_qulifying_time = trigger_qulifying_time_temp.copy()
    trigger_qulifying_time['triggername'] = trigger_name
    trigger_qulifying_time['count'] = count
    response = getListQualifyingTriggerAPI(trigger_qulifying_time)
    if response.status_code == 200:
        qualifying_time = response.json()['qualifyingTimes']
        for time in qualifying_time:
            qualifying_time_list.append(transformTime(time['userTimeZone']))
    return qualifying_time_list

def getQualifyingTimeTaskMonitor(task_monitor_dict, trigger_list):
    
    workflow_qualifying_time_dict = {}
    workflow_out_of_trigger_dict = {}
    for workflow_name, task_monitor_list in task_monitor_dict.items():
        task_monitor_qualifying_time_dict = {}
        task_monitor_out_of_trigger_list = []
        for task_monitor in task_monitor_list:
            task_to_monitor = task_monitor['taskMonName']
            trigger_name_list, out_of_trigger_list = recursiveSearchParentTimeTrigger(task_to_monitor, trigger_list, [], False)
            if out_of_trigger_list:
                task_monitor_out_of_trigger_list.append(task_monitor['name'])
                continue
            all_trigger_qualifying_time = []
            for trigger_name in trigger_name_list:
                trigger_qulifying_time = getQualifyingTimeTrigger(trigger_name)
                for qualifying_time in trigger_qulifying_time:
                    if qualifying_time not in all_trigger_qualifying_time:
                        all_trigger_qualifying_time.append(qualifying_time)
            task_monitor_qualifying_time_dict[task_monitor['name']] = all_trigger_qualifying_time
        workflow_qualifying_time_dict[workflow_name] = task_monitor_qualifying_time_dict
        workflow_out_of_trigger_dict[workflow_name] = task_monitor_out_of_trigger_list
        
        
        
    return workflow_qualifying_time_dict, workflow_out_of_trigger_dict

def compareQualifyingTime(trigger_qualifying_time_list, task_qualifying_time_dict:dict):
    result_dict = {}
    for task_name, workflow_dict in task_qualifying_time_dict.items():
        result_workflow_dict = {}
        for workflow_name, task_dict in workflow_dict.items():
            result_list = []
            for task_monitor, task_qualifying_time in task_dict.items():
                if len(task_qualifying_time) == 0:
                    continue
                elif checkTimeDifferenceProblem(task_qualifying_time, trigger_qualifying_time_list, DAY_PERIOD):
                    result_list.append(task_monitor)
            if len(result_list) > 0:
                result_workflow_dict[workflow_name] = result_list
        result_dict[task_name] = result_workflow_dict
    return result_dict

######################################################################################################################

def checkTimeTrigger(trigger_list, workflow_list = []):
    result_task_monitor_dict = {}
    result_task_monitor_out_of_trigger_list_dict = {}
    
    def processMultiTrigger(trigger):
        print(f"Processing trigger {trigger['name']} | type: {trigger['type']}")
        if trigger['type'] != 'triggerTime':
            return None, None

        trigger_qualifying_time_list = getQualifyingTimeTrigger(trigger['name'])
        result_task_monitor_dict[trigger['name']] = {}
        workflow_qualifying_time_dict = {}
        workflow_out_of_trigger_dict = {}
        
        task_list = trigger['tasks']
        for task_name in task_list:
            task_monitor_dict = recursiveSearchTaskMonitorInWorkflow(task_name, {}, '', workflow_list)
            workflow_qualifying_time_dict[task_name], workflow_out_of_trigger_dict[task_name] = getQualifyingTimeTaskMonitor(task_monitor_dict, trigger_list)

        result = compareQualifyingTime(trigger_qualifying_time_list, workflow_qualifying_time_dict)
        return result, workflow_out_of_trigger_dict
        
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(processMultiTrigger, trigger_list))
        
    for trigger, (result, workflow_out_of_trigger_dict) in zip(trigger_list, results):
        if result:
            result_task_monitor_dict[trigger['name']] = result
        if workflow_out_of_trigger_dict:       
            result_task_monitor_out_of_trigger_list_dict[trigger['name']] = workflow_out_of_trigger_dict

    return result_task_monitor_dict, result_task_monitor_out_of_trigger_list_dict

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
    #print(json.dumps(response_trigger, indent=4))
    #print(json.dumps(workflow_name_list, indent=4))
    result, result_out_of_trigger = checkTimeTrigger(response_trigger, workflow_name_list)
    createJson('UAT_result.json', result)
    createJson('UAT_result_out_of_trigger.json', result_out_of_trigger)
    
if __name__ == '__main__':
    main()