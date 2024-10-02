import sys
import os
import json
import pandas as pd


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTriggerAdvancedAPI, getTaskAPI, updateURI, updateAuth, getListQualifyingTriggerAPI, getListTaskAPI, viewParentTaskAPI
from utils.readFile import loadJson
from utils.createExcel import createExcel
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

def checkTimeDifference(task_qualifying_time, trigger_qualifying_time):
    
    task_qualifying_datetime = [datetime.strptime(date_str, DATETIME_FORMAT) for date_str in task_qualifying_time]
    trigger_qualifying_datetime = [datetime.strptime(date_str, DATETIME_FORMAT) for date_str in trigger_qualifying_time]
    #print("Time",len(task_qualifying_datetime), len(trigger_qualifying_datetime))
    period = timedelta(days = DAY_PERIOD)
    task_index = 0
    trigger_index = 0
    task_datetime = None
    trigger_datetime = None
    condition = True
    while condition:
        
        if task_index == 0 and trigger_index == 0:
            task_datetime = task_qualifying_datetime[task_index]
            trigger_datetime = trigger_qualifying_datetime[trigger_index]
        #print("Task",task_datetime, " Trigger",trigger_datetime, task_index, trigger_index)
        #print(abs(task_datetime - trigger_datetime))
        if abs(task_datetime - trigger_datetime) > period:
            previous_task_datetime = task_qualifying_datetime[task_index - 1]
            previous_trigger_datetime = trigger_qualifying_datetime[trigger_index - 1]
            #print(f"{task_datetime} - {trigger_datetime}")
            if abs(previous_trigger_datetime - trigger_datetime) < period:
                #print(f">>>{task_datetime} - {trigger_datetime} | {previous_trigger_datetime - trigger_datetime}")
                return True
        
        # slide the window
        if task_datetime <= trigger_datetime:
            task_index += 1
            if task_index < len(task_qualifying_datetime):
                task_datetime = task_qualifying_datetime[task_index]
            else:
                condition = False
        elif task_datetime > trigger_datetime:
            trigger_index += 1
            if trigger_index < len(trigger_qualifying_datetime):
                trigger_datetime = trigger_qualifying_datetime[trigger_index]
            else:
                condition = False
                
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
                elif checkTimeDifference(task_qualifying_time, trigger_qualifying_time_list):
                    result_list.append(task_monitor)
            if len(result_list) > 0:
                result_workflow_dict[workflow_name] = result_list
        result_dict[task_name] = result_workflow_dict
    return result_dict

######################################################################################################################

def checkTimeTrigger(trigger_list, workflow_list = []):
    result_task_monitor_dict = {}
    result_task_monitor_out_of_trigger_list_dict = {}
    for trigger in trigger_list:
        if trigger['type'] != 'triggerTime':
            continue
        #if trigger['name'] in test_trigger_list:
        #trigger_qualifying_time_dict[trigger['name']] = getQualifyingTimeTrigger(trigger['name'])
        trigger_qualifying_time_list = getQualifyingTimeTrigger(trigger['name'])
        result_task_monitor_dict[trigger['name']] = {}
        workflow_qualifying_time_dict = {}
        workflow_out_of_trigger_dict = {}
        task_list = trigger['tasks']
        for task_name in task_list:
            task_monitor_dict = recursiveSearchTaskMonitorInWorkflow(task_name, {}, '', workflow_list)
            workflow_qualifying_time_dict[task_name], workflow_out_of_trigger_dict[task_name] = getQualifyingTimeTaskMonitor(task_monitor_dict, trigger_list)

        result_task_monitor_dict[trigger['name']] = compareQualifyingTime(trigger_qualifying_time_list, workflow_qualifying_time_dict)
        result_task_monitor_out_of_trigger_list_dict[trigger['name']] = workflow_out_of_trigger_dict
    return result_task_monitor_dict, result_task_monitor_out_of_trigger_list_dict

######################################################################################################################

def createJsonFile(outputfile, data):
    with open(outputfile, 'w') as file:
        json.dump(data, file, indent=4)


######################################################################################################################

def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain = "https://ttbdevstb.stonebranch.cloud/resources"
    #domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    response_trigger = getListTrigger()
    response_workflow = getListWorkflow()
    workflow_name_list = getListSpecificField(response_workflow,'name')
    #print(json.dumps(response_trigger, indent=4))
    #print(json.dumps(workflow_name_list, indent=4))
    result, result_out_of_trigger = checkTimeTrigger(response_trigger, workflow_name_list)
    createJsonFile('TTB_result_restructure.json', result)
    createJsonFile('TTB_result_out_of_trigger.json', result_out_of_trigger)
    
if __name__ == '__main__':
    main()