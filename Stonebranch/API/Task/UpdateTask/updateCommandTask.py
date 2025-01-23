import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, getTaskAPI, updateTaskAPI
from utils.readFile import loadJson
from utils.createFile import createJson


API_TASK_TYPE = [3,4,99]


task_list_configs_temp = {
    "name": "*",
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

def updateCommandTask(task_list):
    update_log = []
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
            new_char = "\\\""
            if char in command:
                command = command.replace(new_char, char)
                command = command.replace(char, new_char)
            task_data['largeTextField1']['value'] = command
            response_update = updateTaskAPI(task_data)
            if response_update.status_code == 200:
                update_log.append({
                    "taskname": task['name'],
                    "message": "Command updated"
                })
            elif response_update.status_code != 200:
                update_log.append({
                    "taskname": task['name'],
                    "error": f"{response_update.status_code} - {response_update.text}"
                })
                
        
           
    return update_log


def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.170']
    updateURI(domain)
    
    task_list = getTaskList()
    print(len(task_list))
    if not task_list:
        print("No task found.")
    else:
        update_log = updateCommandTask(task_list)
        print(json.dumps(update_log, indent=4))
        createJson('CommandTaskLog.json', update_log)


        
if __name__ == '__main__':
    main()
    