import sys
import os
import json
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, getTaskAPI, updateTaskAPI
from utils.readFile import loadJson
from utils.createFile import createJson


API_TASK_TYPE = [6,99]
TASK_TYPE_LIST = ["taskFileMonitor", "taskWorkflow", "taskUniversal"]

BUSINESS_SERVICE_LIST = [
    "AskMe - New Floor Plan"
]

task_list_configs_temp = {
    "name": "*",
    'businessServices': None,
    "type": None,
}

task_configs_temp = {
    'taskname': None,
}


def getTaskList():
    task_list = []
    for type in API_TASK_TYPE:
        task_configs = task_list_configs_temp.copy()
        task_configs['type'] = type
        task_configs['businessServices'] = BUSINESS_SERVICE_LIST[0]
        response = getListTaskAPI(task_configs)
        if response.status_code == 200:
            task_list.extend(response.json())
    
    return task_list


def updateActionTask(task_list):
    update_log = []
    for task in task_list:
        task_config = task_configs_temp.copy()
        task_config['taskname'] = task['name']
        response_task = getTaskAPI(task_config)
        if response_task.status_code != 200:
            continue
        task_data = response_task.json()
        #if task_data['type'] == "taskUnix" or task_data['type'] == "taskWindows":
        #    command = task_data['command']
        if task_data['type'] in TASK_TYPE_LIST:
            action = task_data['actions']['emailNotifications']
        else:
            continue
        if action:
            task_data['actions']['emailNotifications'] = []
            response_update = updateTaskAPI(task_data)
            if response_update.status_code == 200:
                update_log.append({
                    "taskname": task['name'],
                    "message": "Email Noti updated"
                })
            elif response_update.status_code != 200:
                update_log.append({
                    "taskname": task['name'],
                    "error": f"{response_update.status_code} - {response_update.text}"
                })
        else:
            update_log.append({
                "taskname": task['name'],
                "message": "No Email Noti found"
            })
            
    return update_log


def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.226']
    updateURI(domain)
    
    task_list = getTaskList()
    print(len(task_list))
    if not task_list:
        print("No task found.")
    else:
        update_log = updateActionTask(task_list)
        print(json.dumps(update_log, indent=4))
        createJson('CommandTaskLog.json', update_log)


        
if __name__ == '__main__':
    main()
    