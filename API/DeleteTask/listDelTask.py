import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json
from readExcel import getDataExcel
import http
import pandas as pd
import multiprocessing
from delProcess import deleteProcess

TASK_URI = "http://172.16.1.85:8080/uc/resources/task"
LIST_TASK_ADV_URI = "http://172.16.1.85:8080/uc/resources/task/listadv"
LIST_TASK_URI = "http://172.16.1.85:8080/uc/resources/task/list"
LIST_TRIGGER_ADV_URI = "http://172.16.1.85:8080/uc/resources/trigger/listadv"
LIST_TRIGGER_URI = "http://172.16.1.85:8080/uc/resources/trigger/list"

BUSINESS_SERVICES = "A0417 - AML Management System"

TASK_TYPE = ['taskWorkflow','taskUniversal','taskSleep','taskMonitor','taskFileMonitor']

task_adv_configs_temp = {
    'taskname': '*',
    #'type': None,
    #'businessServices': None,
}

task_configs_temp = {
    'name': '*',
    #'type': None,
    #'businessServices': None,
    'updatedTime': 'd',
}

trigger_configs_temp = {
    'name': None,
}

trigger_adv_configs_temp = {
    'triggername': None,
}

auth = HTTPBasicAuth('ops.admin','p@ssw0rd')

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri


def getListTaskAPI(task_configs):
    response = requests.post(url=LIST_TASK_URI, json = task_configs, auth=auth, headers={'Accept': 'application/json'})
    return response

def multiGetListTaskAPI(task_configs):
    response = requests.post(url=LIST_TASK_URI, json = task_configs, auth=auth, headers={'Accept': 'application/json'})
    status = http.HTTPStatus(response.status_code)
    print(f"{response.status_code} - {status.phrase}: {status.description} - {task_configs['name']}")
    return response


def getListTaskAdvancedAPI(task_adv_configs):
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    return response

def multiGetListTaskAdvancedAPI(task_adv_configs):
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    status = http.HTTPStatus(response.status_code)
    if response.status_code == 200:
        with count.get_lock():
            count.value += 1
    print(f"{count.value} {response.status_code} - {status.phrase}: {status.description} - {task_adv_configs['taskname']}")
    return response


def getListTriggerAPI(trigger_configs):
    response = requests.post(url = LIST_TRIGGER_URI, json = trigger_configs, auth = auth, headers={'Accept': 'application/json'})
    return response

def multiGetListTriggerAPI(trigger_configs):
    response = requests.post(url = LIST_TRIGGER_URI, json = trigger_configs, auth = auth, headers={'Accept': 'application/json'})
    status = http.HTTPStatus(response.status_code)
    print(f"{response.status_code} - {status.phrase}: {status.description} - {trigger_configs['name']}")
    return response


def getListTriggerAdvancedAPI(trigger_configs):
    uri = createURI(LIST_TRIGGER_URI, trigger_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    return response

def multiGetListTriggerAdvancedAPI(trigger_configs):
    uri = createURI(LIST_TRIGGER_URI, trigger_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    status = http.HTTPStatus(response.status_code)
    print(f"{response.status_code} - {status.phrase}: {status.description} - {trigger_configs['triggername']}")
    return response


def deleteTask(task_configs):
    uri = createURI(TASK_URI, task_configs)
    response = requests.delete(url = uri, auth = auth)
    return response


###########################################################################################

def getDeleteTaskTrigger(del_list, prefix_list = []):
    del_task_count = 0
    del_trigger_count = 0
    max_del = len(del_list)
    del_task_list_api = []
    del_trigger_list_api = []
    del_list = addWildCardSuffix(del_list)
    
    for del_name in del_list:
        task_configs = task_configs_temp.copy()
        task_configs['name'] = del_name
        trigger_configs = trigger_configs_temp.copy()
        trigger_configs['name'] = del_name
        response_task_list = getListTaskAPI(task_configs)
        response_trigger_list = getListTriggerAPI(trigger_configs)
        #task_status = http.HTTPStatus(response_task_list.status_code)
        #trigger_status = http.HTTPStatus(response_trigger_list.status_code)
        if response_task_list.status_code == 200:
            del_task_count += 1
            for task in response_task_list.json():
                if task['name'] not in del_task_list_api and startWithAny(prefix_list, task['name']):
                    del_task_list_api.append(task)
        if response_trigger_list.status_code == 200:
            del_trigger_count += 1
            for trigger in response_trigger_list.json():
                if trigger['name'] not in del_trigger_list_api and startWithAny(prefix_list, trigger['name']):
                    del_trigger_list_api.append(trigger)
        print(f"{del_task_count},{del_trigger_count}/{max_del} {response_task_list.status_code} - {response_trigger_list.status_code} {del_name}")
        
    return del_task_list_api, del_trigger_list_api
    

def getDeleteTaskTriggerMultiProcessing(del_list, prefix_list = [], num_process=4):
    task_list_api = []
    trigger_list_api = []
    del_list_wildcard = addWildCardSuffix(del_list)
    task_configs_list = addDataToConfigs(del_list_wildcard, task_adv_configs_temp, col_name = 'taskname')
    count = multiprocessing.Value('i', 0)
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_task:
        result_task = pool_task.map(multiGetListTaskAdvancedAPI, task_configs_list)
        #result_task = async_result_task.get()
        print("Waiting for all subprocesses done...")
    pool_task.close()
    pool_task.join()
    trigger_configs = trigger_configs_temp.copy()
    trigger_configs['name'] = '*'
    result_trigger = getListTriggerAPI(trigger_configs)

    print("All subprocesses done.")
    for result in result_task:
        if result.status_code == 200:
            for task in result.json():
                if task['name'] not in task_list_api and startWithAny(prefix_list, task['name']):
                    task_list_api.append(task)
                    
    if result_trigger.status_code == 200:
        for trigger in result_trigger.json():
            if trigger['name'] not in trigger_list_api and startWithAny(prefix_list, trigger['name']):
                trigger_list_api.append(trigger)
    print(count)
    return task_list_api, trigger_list_api

def separateTaskType(task_list, task_type_list):
    task_type_dict = {}
    for task_type in task_type_list:
        task_type_dict[task_type] = []
    
    for task in task_list:
        if task['type'] in task_type_list:
            task_type_dict[task['type']].append(task)
    
    return task_type_dict



#################################    utils      ###########################################

def initializer(cnt):
    global count
    count = cnt

def startWithAny(prefix_list, string: str):
    for prefix in prefix_list:
        if string.startswith(prefix):
            return True
    return False

def getFristPrefixList(data_list):
    prefix_list = []
    for data in data_list:
        prefix_list.append(data.split('_')[0])
    return prefix_list

def addWildCardSuffix(data_list):
    new_list = []
    for i in range(len(data_list)):
        new_list.append(data_list[i] + '*')
    return new_list

def getListExcel(df, col_name = 'jobName'):
    del_list = []
    for index, row in df.iterrows():
        del_list.append(row[col_name])
    return del_list

def groupingName(task_list):
    grouping_list = []
    for row in task_list:
        prefix_row = row.split('.')[0]
        if prefix_row not in grouping_list:
            grouping_list.append(prefix_row)
    return grouping_list

def compareStartWith(list_excel, list_api):
    compared_list = []
    for task in list_api:
        if startWithAny(list_excel, task['name']) or task['name'] in list_excel:
            if task not in compared_list:
                compared_list.append(task)
    
    return compared_list

def getUniqueList(list):
    new_list = []
    for item in list:
        if item not in new_list:
            new_list.append(item)
    return new_list

def createExcel(outputfile, *data):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            for df, sheetname in data:
                df.to_excel(writer, sheet_name=sheetname, index=False)
        print("Delete file created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")

def addDataToConfigs(data_list, configs, col_name = 'name'):
    new_list = []
    for data in data_list:
        new_configs = configs.copy()
        new_configs[col_name] = data
        new_list.append(new_configs)
    return new_list

###########################################################################################
def main():
    df = getDataExcel()
    
    del_list_excel = getListExcel(df)
    print(len(del_list_excel))
    group_task_list = groupingName(del_list_excel)
    print(len(group_task_list))
    
    del_task_list_api, del_trigger_list_api = getDeleteTaskTriggerMultiProcessing(del_list_excel, del_list_excel, num_process=4)
    #del_task_list_api, del_trigger_list_api = getDeleteTaskTriggerMultiProcessing(group_task_list, del_list_excel, num_process=4)
    print(len(del_task_list_api), len(del_trigger_list_api))
    del_task_list_clean = getUniqueList(del_task_list_api)
    del_trigger_list_clean = getUniqueList(del_trigger_list_api)
    print(len(del_task_list_clean), len(del_trigger_list_clean))
    del_task_type_dict = separateTaskType(del_task_list_clean, TASK_TYPE)
    #print(json.dumps(compared_del_task_list, indent=4))
    
    dfworkflow = pd.DataFrame(del_task_type_dict['taskWorkflow'])
    dfuniversal = pd.DataFrame(del_task_type_dict['taskUniversal'])
    dfsleep = pd.DataFrame(del_task_type_dict['taskSleep'])
    dfmonitor = pd.DataFrame(del_task_type_dict['taskMonitor'])
    dffilemonitor = pd.DataFrame(del_task_type_dict['taskFileMonitor'])
    dftrigger = pd.DataFrame(del_trigger_list_clean)
    
    createExcel('delete_task_trigger.xlsx', (dfworkflow, 'Workflow'), (dfuniversal, 'Universal'), (dfsleep, 'Timer'), (dfmonitor, 'TaskMonitor'), (dffilemonitor, 'AgentFileMonitor'), (dftrigger, 'Trigger'))
    dftask_dict = {
        'taskWorkflow': dfworkflow,
        'taskUniversal': dfuniversal,
        'taskSleep': dfsleep,
        'taskMonitor': dfmonitor,
        'taskFileMonitor': dffilemonitor,
    }
    print("Do you want to delete these tasks and triggers? (y/n)")
    choice = input().lower()
    if choice == 'y':
        confirm = input("confirm to continue delete? (confirm/...)").lower()
        if confirm == 'confirm':
            deleteProcess(dftask_dict, dftrigger)
    
if __name__ == "__main__":
    main()