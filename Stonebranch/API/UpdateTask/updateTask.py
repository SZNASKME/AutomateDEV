import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.stbAPI import updateURI, updateAuth, updateTaskAPI, getTaskAPI
from utils.readFile import loadJson

task_configs_temp = {
    "taskname": "DWH_LON_WRITEOFF.M.MAIN_C"
}

def getTask():
    task_configs = task_configs_temp.copy()
    response = getTaskAPI(task_configs)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def updateTask(task_data):
    response = updateTaskAPI(task_data)
    if response.status_code == 200:
        return response
    else:
        return None
    


def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    
    response_task = getTask()
    print(json.dumps(response_task, indent=4))
    if response_task:
        response_update = updateTask(response_task)
        print(response_update)
        
        
if __name__ == '__main__':
    main()