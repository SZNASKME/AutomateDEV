from readExcel import getDataExcel, selectSheet
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import http
import json
import math
import ast
import multiprocessing

TASK_URI = "http://172.16.1.85:8080/uc/resources/task"
TRIGGER_URI = "http://172.16.1.85:8080/uc/resources/trigger"

auth = HTTPBasicAuth('ops.admin','p@ssw0rd')


task_configs_temp = {
   'taskid': None,
   #'taskname': None,
}

trigger_configs_temp = {
    'triggerid': None,
    #'triggername': None,
}


def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri

def getTaskAPI(task_configs):
    response = requests.get(url = TASK_URI, json = task_configs, auth = auth, headers = {'Accept': 'application/json'})
    return response

def updateTaskAPI(task_configs):
    response = requests.put(url = TASK_URI, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def multiUpdateTaskAPI(task_configs):
    response = requests.put(url = TASK_URI, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    status = http.HTTPStatus(response.status_code)
    if response.status_code == 200:
        with count.get_lock():
            count.value += 1
    print(f"{count.value} {response.status_code} - {response.text}")
    return response

def deleteTaskAPI(task_configs):
    uri = createURI(TASK_URI, task_configs)
    response = requests.delete(url = uri, auth = auth)
    return response

def multiDeleteTaskAPI(task_configs):
    uri = createURI(TASK_URI, task_configs)
    response = requests.delete(url = uri , auth = auth)
    status = http.HTTPStatus(response.status_code)
    if response.status_code == 200:
        with count.get_lock():
            count.value += 1
    print(f"{count.value} {response.status_code} - {response.text}")
    return response

def deleteTriggerAPI(trigger_configs):
    uri = createURI(TRIGGER_URI, trigger_configs)
    response = requests.delete(url = uri, auth = auth)
    return response

def multiDeleteTriggerAPI(trigger_configs):
    uri = createURI(TRIGGER_URI, trigger_configs)
    response = requests.delete(url = uri, auth = auth)
    status = http.HTTPStatus(response.status_code)
    if response.status_code == 200:
        with count.get_lock():
            count.value += 1
    print(f"{count.value} {response.status_code} - {response.text}")
    return response 

##########################################################################################

def delTask(df, num_process = 4):
    count = multiprocessing.Value('i', 0)
    success = 0
    cannot_delete = []
    not_found = []
    task_configs_list = addDataToConfigs(df, task_configs_temp, col_name = 'taskid', df_col_name = 'sysId')
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_task:
        result_task = pool_task.map(multiDeleteTaskAPI, task_configs_list)
    
    pool_task.close()
    pool_task.join()
    
    for res in result_task:
        if res.status_code == 200:
            success += 1
        if res.status_code == 403:
            cannot_delete.append(res.text)
        if res.status_code == 404:
            not_found.append(res.text)
            
    return {
        "200": success,
        "403": cannot_delete,
        "404": not_found
    }
        

def delTrigger(df, num_process = 4):
    count = multiprocessing.Value('i', 0)
    success = 0
    cannot_delete = []
    not_found = []
    trigger_configs_list = addDataToConfigs(df, trigger_configs_temp, col_name = 'triggerid', df_col_name = 'sysId')
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_trigger:
        result_trigger = pool_trigger.map(multiDeleteTriggerAPI, trigger_configs_list)
    
    pool_trigger.close()
    pool_trigger.join()
    
    for res in result_trigger:
        if res.status_code == 200:
            success += 1
        if res.status_code == 403:
            cannot_delete.append(res.text)
        if res.status_code == 404:
            not_found.append(res.text)
            
    return {
        "200": success,
        "403": cannot_delete,
        "404": not_found
    }


def updateEmptyWorkflow(df, num_process = 4):
    dfworkflow = df[df['type'] == 'taskWorkflow']
    count = multiprocessing.Value('i', 0)
    success = 0
    cannot_delete = []
    not_found = []
    workflow_configs_list = []
    for index, row in dfworkflow.iterrows():
        task_configs = getConfigs(row)
        task_configs['workflowEdges'] = []
        task_configs['workflowVertices'] = []
        workflow_configs_list.append(task_configs)
        
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_workflow:
        result_workflow = pool_workflow.map(multiUpdateTaskAPI, workflow_configs_list)
        
    pool_workflow.close()
    pool_workflow.join()
    
    for res in result_workflow:
        if res.status_code == 200:
            success += 1
        if res.status_code == 403:
            cannot_delete.append(res.text)
        if res.status_code == 404:
            not_found.append(res.text)
            
    return {
        "200": success,
        "403": cannot_delete,
        "404": not_found
    }

##########################################################################################

def initializer(cnt):
    global count
    count = cnt

def getListExcel(df, col_name = 'jobName'):
    del_list = []
    for index, row in df.iterrows():
        del_list.append(row[col_name])
    return del_list


def cleanValueDataFrame(value):
    if isinstance(value, str):
        if value.startswith("{") and value.endswith("}") or value.startswith("[") and value.endswith("]"):
            return ast.literal_eval(value)
        else:
            return value.strip()
    elif isinstance(value, float) and math.isnan(value):
        return None
    elif isinstance(value, float):
        return int(value)
    else:
        return value

def getConfigs(row):
    new_dict = {}
    for key in row.keys():
        value = cleanValueDataFrame(row[key])
        new_dict[key] = value
    return new_dict

def addDataToConfigs(dataframe, configs, col_name = 'name', df_col_name = 'name'):
    new_list = []
    for index, data in dataframe.iterrows():
        new_configs = configs.copy()
        new_configs[col_name] = data[df_col_name]
        new_list.append(new_configs)
    return new_list
    
    
##########################################################################################

def viewResult(result_dict):
    print("Enter status code (200,403,404) to view result")
    choice = input()
    if choice == '200':
        for key_res, res in result_dict.items():
            for key_value, value in res.items():
                if key_value == '200':
                    print(key_res)
                    print(json.dumps(value, indent = 4))
    if choice == '403':
        for key_res, res in result_dict.items():
            for key_value, value in res.items():
                if key_value == '403':
                    print(key_res)
                    print(json.dumps(value, indent = 4))
    if choice == '404':
        for key_res, res in result_dict.items():
            for key_value, value in res.items():
                if key_value == '404':
                    print(key_res)
                    print(json.dumps(value, indent = 4))



def deleteProcess(dftask_dict, dftrigger):
    print("Delete Process ...")
    
    print("Delete Trigger ...")
    result_trigger = delTrigger(dftrigger)
    print("Empty Workflow ...")
    result_empty_workflow = updateEmptyWorkflow(dftask_dict['taskWorkflow'])
    print("Delete Task Monitor ...")
    result_task_monitor = delTask(dftask_dict['taskMonitor'])
    print("Delete File Monitor ...")
    result_file_monitor = delTask(dftask_dict['taskFileMonitor'])
    print("Delete Univerasl Task ...")
    result_universal_task = delTask(dftask_dict['taskUniversal'])
    print("Delete Timer Task ...")
    result_timer_task = delTask(dftask_dict['taskSleep'])
    print("Delete Workflow Task ...")
    result_workflow = delTask(dftask_dict['taskWorkflow'])

    print("Complete Process ...")
    result = {
        "trigger": result_trigger,
        "emptyWorkflow": result_empty_workflow,
        "taskMonitor": result_task_monitor,
        "fileMonitor": result_file_monitor,
        "universal": result_universal_task,
        "timer": result_timer_task,
        "workflow": result_workflow
    }
    
    viewResult(result)
    
def main():
    df = getDataExcel()
    dfworkflow = selectSheet(df, 'Workflow')
    dfuniversal = selectSheet(df, 'Universal')
    dfsleep = selectSheet(df, 'Timer')
    dfmonitor = selectSheet(df, 'TaskMonitor')
    dffilemonitor = selectSheet(df, 'AgentFileMonitor')
    
    dftask_dict = {
        'taskWorkflow': dfworkflow,
        'taskUniversal': dfuniversal,
        'taskSleep': dfsleep,
        'taskMonitor': dfmonitor,
        'taskFileMonitor': dffilemonitor,
    }
    dftrigger = selectSheet(df, 'Trigger')
    deleteProcess(dftask_dict, dftrigger)
    
    
if __name__ == '__main__':
    main()