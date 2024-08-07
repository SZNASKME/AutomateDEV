from readExcel import getDataExcel, selectSheet
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import http
import json
import math
import ast

TASK_URI = "http://172.16.1.86:8080/uc/resources/task"
TRIGGER_URI = "http://172.16.1.86:8080/uc/resources/trigger"

auth = HTTPBasicAuth('ops.admin','p@ssw0rd')


task_configs_temp = {
   # 'taskid': None,
   'taskname': None,
}

trigger_configs_temp = {
    #'triggerid': None,
    'triggername': None,
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

def deleteTaskAPI(task_configs):
    uri = createURI(TASK_URI, task_configs)
    response = requests.delete(url = uri, auth = auth)
    return response

def deleteTriggerAPI(trigger_configs):
    uri = createURI(TRIGGER_URI, trigger_configs)
    response = requests.delete(url = uri, auth = auth)
    return response

##########################################################################################

def delTask(df):
    del_count = 0
    del_max = len(df)
    #ordered_del_list = sorted(del_list, reverse=True)
    for index, row in df.iterrows():
        task_configs = task_configs_temp.copy()
        task_configs['taskname'] = row['name']
        print(json.dumps(task_configs, indent=4))
        #response = deleteTaskAPI(task_configs)
        #status = http.HTTPStatus(response.status_code)
        #if response.status_code == 200:
        #    del_count += 1
        #if response.status_code == 404:
        #    print("Task not found")
        #print(f"{del_count}/{del_max} {response.status_code} - {status.phrase}: {status.description}")

def delTrigger(df):
    del_count = 0
    del_max = len(df)
    for index, row in df.iterrows():
        trigger_configs = trigger_configs_temp.copy()
        trigger_configs['triggername'] = row['name']
        print(json.dumps(trigger_configs, indent=4))
        #response = deleteTriggerAPI(trigger_configs)
        #status = http.HTTPStatus(response.status_code)
        #if response.status_code == 200:
        #    del_count += 1
        #print(f"{del_count}/{del_max} {response.status_code} - {status.phrase}: {status.description}")


def updateEmptyWorkflow(df):
    dfworkflow = df[df['type'] == 'taskWorkflow']
    print(dfworkflow)
    #configs_temp = createFormatConfigs(dfworkflow)
    for index, row in dfworkflow.iterrows():
        task_configs = getConfigs(row)
        task_configs['workflowEdges'] = []
        task_configs['workflowVertices'] = []
        print(json.dumps(task_configs, indent=4))
        #response = updateTaskAPI(task_configs)
        #status = http.HTTPStatus(response.status_code)
        #print(f"{response.status_code} - {status.phrase}: {status.description}")
    return None

##########################################################################################

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
    elif math.isnan(value):
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
    
    
##########################################################################################


def deleteProcess(dftask_dict, dftrigger):
    delTrigger(dftrigger)
    updateEmptyWorkflow(dftask_dict['taskWorkflow'])

    delTask(dftask_dict['taskMonitor'])
    delTask(dftask_dict['taskFileMonitor'])
    delTask(dftask_dict['taskUniversal'])
    delTask(dftask_dict['taskSleep'])
    delTask(dftask_dict['taskWorkflow'])
    #delTask(dftask)
    
    
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