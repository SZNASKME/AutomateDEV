import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import getListTaskAPI, updateURI, updateAuth, viewParentTaskAPI
from utils.readFile import loadJson
from utils.createFile import createExcel


EXCEL_FILE_NAME = 'TaskMonitorWithoutParent.xlsx'

TASKNAME = 'taskname'

task_configs_temp = {
    'name': '*',
    'type': 12,
    'businessServices': None,
}

parent_configs_temp = {
    'taskname': None
}

def listTaskMonitor():
    response = getListTaskAPI(task_configs_temp)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def prepareTaskMonitorList(response_task_monitor):
    task_monitor_list = []
    for task_monitor in response_task_monitor:
        task_monitor_list.append(task_monitor['name'])
        
    return task_monitor_list


def findTaskMonitorWithoutParent(task_monitor_list):
    task_monitor_log = []
    for task_monitor in task_monitor_list:
        task_monitor_config = parent_configs_temp.copy()
        task_monitor_config[TASKNAME] = task_monitor
        response = viewParentTaskAPI(task_monitor_config)
        if response.status_code == 200:
            parent_task = response.json()
            if not parent_task:
                task_monitor_log.append({
                    'Task Monitor': task_monitor,
                    'note': 'Not in Workflow'
                })
        else:
            task_monitor_log.append({
                'Task Monitor': task_monitor,
                'note': 'Not found'
            })         
    #print(task_monitor_log)
    return task_monitor_log



def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.86']
    updateURI(domain)
    
    response_task_monitor = listTaskMonitor()
    task_monitor_list = prepareTaskMonitorList(response_task_monitor)
    task_monitor_log = findTaskMonitorWithoutParent(task_monitor_list)
    df_task_monitor_log = pd.DataFrame(task_monitor_log)
    createExcel(EXCEL_FILE_NAME, ("Log",df_task_monitor_log))
    
    
    
if __name__ == '__main__':
    main()