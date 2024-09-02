import sys
import os
import json



sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTriggerAdvancedAPI, getListTriggerAPI, getTaskAPI, updateURI, updateAuth, getListQualifyingTriggerAPI, getListTaskAPI, viewParentTaskAPI
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
    'businessServices': 'A0076 - Data Warehouse ETL',
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
    for trigger in trigger_list:
        if task_name in trigger['tasks']:
            trigger_name_list.append(trigger['name'])
    return trigger_name_list

def checkTimeDifference(task_monitor_qualifying_time, trigger_qualifying_time):
    
    task_monitor_qualifying_datetime = [datetime.strptime(date_str, DATETIME_FORMAT) for date_str in task_monitor_qualifying_time]
    trigger_qualifying_datetime = [datetime.strptime(date_str, DATETIME_FORMAT) for date_str in trigger_qualifying_time]
    
    period = timedelta(days = DAY_PERIOD)
    task_monitor_index = 0
    trigger_index = 0
    task_monitor_datetime = None
    trigger_datetime = None
    condition = True
    while condition:
        #print(task_monitor_datetime, trigger_datetime, task_monitor_index, trigger_index)
        if task_monitor_index == 0 and trigger_index == 0:
            task_monitor_datetime = task_monitor_qualifying_datetime[task_monitor_index]
            trigger_datetime = trigger_qualifying_datetime[trigger_index]
        
        if task_monitor_datetime - trigger_datetime > period:
            return True
        
        if task_monitor_datetime <= trigger_datetime:
            task_monitor_index += 1
            if task_monitor_index < len(task_monitor_qualifying_datetime):
                task_monitor_datetime = task_monitor_qualifying_datetime[task_monitor_index]
            else:
                condition = False
        elif task_monitor_datetime > trigger_datetime:
            trigger_index += 1
            if trigger_index < len(trigger_qualifying_datetime):
                trigger_datetime = trigger_qualifying_datetime[trigger_index]
            else:
                condition = False
                
    return False
    
######################################################################################################################

def recursiveSearchTaskMonitorInWorkflow(task_name, task_monitor_list, workflow_list = []):
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
                        task_monitor_list = recursiveSearchTaskMonitorInWorkflow(vertex['task']['value'], task_monitor_list, workflow_list)
        elif task_data['type'] == 'taskMonitor':
            task_monitor_list.append(task_data)
    return task_monitor_list

def recursiveSearchParentTimeTrigger(task_name, trigger_list, parent_trigger_name_list):
    parent_configs = parent_configs_temp.copy()
    parent_configs['taskname'] = task_name
    response = viewParentTaskAPI(parent_configs)
    if response.status_code == 200:
        parent_data = response.json()
        if parent_data:
            for parent in parent_data:
                parent_name =  parent['name']
                parent_trigger_name_list = recursiveSearchParentTimeTrigger(parent_name, trigger_list, parent_trigger_name_list)
        else:
            trigger_name = getTriggerNameFromTask(task_name, trigger_list)
            parent_trigger_name_list.extend(trigger_name)
    
    return parent_trigger_name_list

######################################################################################################################


def transformTime(time_string:str) -> str:
    date_object = parser.parse(time_string)
    formatted_date = date_object.strftime("%d/%m/%y-%H:%M:%S")
    return formatted_date

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

def getQualifyingTimeTaskMonitor(task_monitor_list, trigger_list):
    task_monitor_qualifying_time_dict = {}
    for task_monitor in task_monitor_list:
        task_to_monitor = task_monitor['taskMonName']
        trigger_name_list = recursiveSearchParentTimeTrigger(task_to_monitor, trigger_list, [])
        print(task_monitor['name'], trigger_name_list)
        all_trigger_qualifying_time = []
        for trigger_name in trigger_name_list:
            trigger_qulifying_time = getQualifyingTimeTrigger(trigger_name)
            print(trigger_name, len(trigger_qulifying_time))
            for qualifying_time in trigger_qulifying_time:
                if qualifying_time not in all_trigger_qualifying_time:
                    all_trigger_qualifying_time.append(qualifying_time)
        task_monitor_qualifying_time_dict[task_monitor['name']] = all_trigger_qualifying_time
    return task_monitor_qualifying_time_dict

def compareQualifyingTime(trigger_qualifying_time_list, task_qualifying_time_dict):
    result_list = []
    for task_name, task_dict in task_qualifying_time_dict.items():
        for task_monitor, task_monitor_qualifying_time in task_dict.items():
            print(task_monitor, len(task_monitor_qualifying_time), len(trigger_qualifying_time_list))
            if len(task_monitor_qualifying_time) == 0:
                continue
            elif checkTimeDifference(task_monitor_qualifying_time, trigger_qualifying_time_list):
                result_list.append(task_monitor)
    return result_list

######################################################################################################################

def checkTimeTrigger(trigger_list, workflow_list = []):
    task_monitor_dict = {}
    for trigger in trigger_list:
        if trigger['type'] != 'triggerTime':
            continue
        #trigger_qualifying_time_dict[trigger['name']] = getQualifyingTimeTrigger(trigger['name'])
        trigger_qualifying_time_list = getQualifyingTimeTrigger(trigger['name'])
        task_monitor_dict[trigger['name']] = {}
        task_monitor_qualifying_time_dict = {}
        task_list = trigger['tasks']
        for task_name in task_list:
            task_monitor_list = recursiveSearchTaskMonitorInWorkflow(task_name, [], workflow_list)
            #print(len(task_monitor_list))
            task_monitor_qualifying_time_dict[task_name] = getQualifyingTimeTaskMonitor(task_monitor_list, trigger_list)
        #print(json.dumps(trigger_qualifying_time_list, indent=4))
        #print(json.dumps(task_monitor_qualifying_time_dict, indent=4))
        
        task_monitor_dict[trigger['name']] = compareQualifyingTime(trigger_qualifying_time_list, task_monitor_qualifying_time_dict)
    
    return task_monitor_dict

######################################################################################################################

def main():
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    response_trigger = getListTrigger()
    response_workflow = getListWorkflow()
    workflow_name_list = getListSpecificField(response_workflow,'name')
    #print(json.dumps(response_trigger, indent=4))
    #print(json.dumps(workflow_name_list, indent=4))
    result = checkTimeTrigger(response_trigger, workflow_name_list)
    print(json.dumps(result, indent=4))
    
    
    
if __name__ == '__main__':
    main()