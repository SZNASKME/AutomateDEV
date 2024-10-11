import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, getTaskAPI
from utils.readFile import loadJson
from utils.createFile import createJson


API_TASK_TYPE = [3,4,99]


task_list_configs_temp = {
    "name": "*",
    "businessServices": "A0076 - Data Warehouse ETL",
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
        response = getListTaskAPI(task_configs)
        if response.status_code == 200:
            task_list.extend(response.json())
    
    return task_list

def checkCommandTask(task_list):
    err_list = []
    for task in task_list:
        task_config = task_configs_temp.copy()
        task_config['taskname'] = task['name']
        response_task = getTaskAPI(task_config)
        if response_task.status_code != 200:
            continue
        task_data = response_task.json()
        if task_data['type'] == "taskUnix" or task_data['type'] == "taskWindows":
            command = task_data['command']
        elif task_data['type'] == "taskUniversal":
            command = task_data['largeTextField1']['value']
        else:
            continue
        if command:
            char = "\""
            indices = [i for i, c in enumerate(command) if c == char]
            for index in indices:
                if command[index-1] != "\\":
                    err_list.append({
                        "taskname": task['name'],
                        "command": command,
                        "index": index,
                    })
    return err_list


def main():
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    task_list = getTaskList()
    print(len(task_list))
    if not task_list:
        print("No task found.")
    else:
        err_list = checkCommandTask(task_list)
        print(json.dumps(err_list, indent=4))
        createJson('CommandTaskError.json', err_list)


        
if __name__ == '__main__':
    main()
    