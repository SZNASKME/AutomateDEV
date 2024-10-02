import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createExcel import createExcel
from Stonebranch.utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, getListTaskAdvancedAPI, viewParentTaskAPI

TASK_TYPE_API = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,99]

list_task_adv_configs_temp = {
    'taskname': '*',
    'type': 1,
}


def getListTask():
    task_list = []
    for type in TASK_TYPE_API:
        list_task_adv_configs = list_task_adv_configs_temp.copy()
        list_task_adv_configs['type'] = type
        response = getListTaskAdvancedAPI(list_task_adv_configs)
        if response.status_code == 200:
            task_list.extend(response.json())
    return task_list

def checkMultiParent(task_list):
    multi_parent_list = []
    for task in task_list:
        task_configs = {
            'taskname': task['name'],
        }
        response_parent = viewParentTaskAPI(task_configs)
        if response_parent.status_code == 200:
            parent_data = response_parent.json()
            if len(parent_data) > 1:
                parent_list = [x['name'] for x in parent_data]
                multi_parent_list.append({
                    'Task': task['name'],
                    'Parent': ', '.join(parent_list)
                })
    return multi_parent_list
    

def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = 'http://172.16.2.144:8080/uc/resources'
    updateURI(domain)
    
    response_task_list = getListTask()
    multi_parent_list = checkMultiParent(response_task_list)
    #print(json.dumps(multi_parent_dict, indent=4))
    df_multi_parent = pd.DataFrame(multi_parent_list)
    df_multi_parent = df_multi_parent.astype({'Task': str, 'Parent': str})
    createExcel("MultiParentTask.xlsx", (df_multi_parent,"MultiParentTask"))
    
    
if __name__ == '__main__':
    main()

    
    
    
    