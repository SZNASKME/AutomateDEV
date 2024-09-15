import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getListTriggerAdvancedAPI
from utils.loadFile import loadJson

API_TRIGGER_TYPE = [1,2,3,4,5,6,8,9,10,11,12]

trigger_adv_configs_temp = {
    'triggername': '*',
    'businessServices': 'A0076 - Data Warehouse ETL',
}

def getListTrigger():
    
    trigger_list = []
    
    for type in API_TRIGGER_TYPE:
        trigger_adv_configs = trigger_adv_configs_temp.copy()
        trigger_adv_configs['type'] = type
        response = getListTriggerAdvancedAPI(trigger_adv_configs)
        if response.status_code == 200:
            trigger_list.extend(response.json())
            
    return trigger_list


def findTaskMultiTrigger(trigger_list):
    task_count_trigger_dict = {}
    task_multi_trigger = []
    task_trigger_list = []
    for trigger in trigger_list:
        tasks = trigger['tasks']
        for task in tasks:
            if task not in task_count_trigger_dict:
                task_count_trigger_dict[task] = []
            task_count_trigger_dict[task].append(trigger['name'])
                
    
    for task, triggers in task_count_trigger_dict.items():
        if len(triggers) > 1:
            task_multi_trigger.append({
                'Task': task,
                'Triggers': triggers
            })
        task_trigger_list.append({
            'Task': task,
            'Triggers': triggers
        })
            
    return task_multi_trigger, task_trigger_list, task_count_trigger_dict
    
    

def createJsonFile(outputfile, data):
    with open(outputfile, 'w') as file:
        json.dump(data, file, indent=4)


def main():
    
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain = "https://ttbdevstb.stonebranch.cloud/resources"
    #domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)

    trigger_list = getListTrigger()
    print(len(trigger_list))
    task_multi_trigger, task_trigger_list, task_count_trigger_dict = findTaskMultiTrigger(trigger_list)
    
    #print(json.dumps(task_count_trigger_dict, indent=4))
    #print("\n\nTask with multiple triggers:")
    #print(json.dumps(task_multi_trigger, indent=4))
    createJsonFile('Task_Multi_Trigger.json', task_multi_trigger)
    createJsonFile('Task_Trigger_List.json', task_trigger_list)
    
if __name__ == "__main__":
    main()