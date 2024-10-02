import http

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateURI, updateAuth, getTaskAPI, createVariableAPI, createTaskAPI, updateTaskAPI
from Stonebranch.utils.readFile import loadJson
from utils.readExcel import getDataExcel

TASK_MONITOR_SUBFIX = '-TM'
VARIABLE_SUBFIX = '_ST_FLAG'
VARIABLE_MONITOR_SUBFIX = '-VM'


task_adv_configs = {
    'taskname': '*',
    'type': 12,
    'businessServices': 'A0417 - AML MANAGEMENT SYSTEM',
    #'updatedTime': '-100d',
}

task_configs_temp = {
    'taskname': '',
}


def getVariableNameCustomReplace(source_str, trim_str, replace_str):
    new_str = source_str.replace(trim_str, replace_str)
    new_str = new_str.strip()
    new_str = new_str.replace('.', '_')
    return new_str

def getTaskNameCustomTrim(source_str, trim_str):
    new_str = source_str.replace(trim_str, '')
    new_str = new_str.strip()
    return new_str

def getTaskData(data, task_name):
    for value in data:
        if value['name'] == task_name:
            return value
    return None


################################################################


def createVariable(df):
    for index, value in df.iterrows():
        #print(value['opswiseGroups'])
        if value['Task Monitor'].find(TASK_MONITOR_SUBFIX) != -1:
            task_configs = task_configs_temp.copy()
            task_configs['taskname'] = value['Task Monitor']
            response_task_monitor = getTaskAPI(task_configs)
            if response_task_monitor.status_code != 200:
                print(f"Task {value['Task Monitor']} not found")
                continue
            task_monitor_data = response_task_monitor.json()
            var_name = getVariableNameCustomReplace(value['Task Monitor'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
            json_data = {
                "name": var_name,
                "opswiseGroups": task_monitor_data['opswiseGroups'],
                "value": "success",
            }
            #print(json_data)
            response_update = createVariableAPI(json_data)
            if response_update.status_code == 200:
                print(f"Create variable {var_name} successfully")
            else:
                print(f"Create variable {var_name} failed")
    return None


def createVariableMonitor(df):
    for index, value in df.iterrows():
        if value['Task Monitor'].find(TASK_MONITOR_SUBFIX) != -1:
            task_configs = task_configs_temp.copy()
            task_configs['taskname'] = value['Task Monitor']
            response_task_monitor = getTaskAPI(task_configs)
            if response_task_monitor.status_code != 200:
                print(f"Task {value['Task Monitor']} not found")
                continue
            task_monitor_data = response_task_monitor.json()
            task_name = getVariableNameCustomReplace(value['Task Monitor'], TASK_MONITOR_SUBFIX, VARIABLE_MONITOR_SUBFIX)
            var_name = getVariableNameCustomReplace(value['Task Monitor'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
            json_data = {
                "type": "taskVariableMonitor",
                "name": task_name,
                "opswiseGroups": task_monitor_data['opswiseGroups'],
                "valueMonitorType": 3,
                "variableName": var_name,
                "value": "success",
            }
            #print(json_data)
            response_update = createTaskAPI(json_data)
            if response_update.status_code == 200:
                print(f"Create variable monitor {task_name} successfully")
            else:
                print(f"Create variable monitor {task_name} failed")
    return None


def addActionToTask(df):
    for index, value in df.iterrows():
        if value['Task Monitor'].find(TASK_MONITOR_SUBFIX) != -1:
            task_monitor_configs = task_configs_temp.copy()
            task_monitor_configs['taskname'] = value['Task Monitor']
            response_task_monitor = getTaskAPI(task_monitor_configs)
            if response_task_monitor.status_code != 200:
                print(f"Task Monitor {value['Task Monitor']} not found")
                continue
            task_monitor_data = response_task_monitor.json()
            task_name = task_monitor_data['taskMonName']
            var_name = getVariableNameCustomReplace(value['Task Monitor'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
            task_configs = task_configs_temp.copy()
            task_configs['taskname'] = task_name
            response_task = getTaskAPI(task_configs)
            if response_task.status_code != 200:
                print(f"Task {task_name} not found")
                continue
            task_data = response_task.json()
            task_data["actions"]["setVariableActions"] = [
                {
                    "notificationOption": "Operation Failure",
                    "status": "Defined",
                    "variableName": var_name,
                    "variableScope": "Global",
                    "variableValue": "running"
                },
                {
                    "notificationOption": "Operation Failure",
                    "status": "Finished,\nSuccess",
                    "variableName": var_name,
                    "variableScope": "Global",
                    "variableValue": "success"
                }
            ]
            response_update = updateTaskAPI(task_data)
            if response_update.status_code == 200:
                print(f"Add action to task {task_name} successfully")
            else:
                print(f"Add action to task {task_name} failed")
    return None

def replaceTaskInWorkflow(df):
    workflow_name_list = []
    for index, value in df.iterrows():
        if value['Task Monitor'].find(TASK_MONITOR_SUBFIX) != -1:
            workflow_list = value['Sub workflow'].split(',')
            workflow_list = [x.strip() for x in workflow_list]
            for workflow_name in workflow_list:
                if workflow_name not in workflow_name_list:
                    workflow_name_list.append(workflow_name)
    for workflow_name in workflow_name_list:
        task_configs = task_configs_temp.copy()
        task_configs['taskname'] = workflow_name
        response_workflow = getTaskAPI(task_configs)
        if response_workflow.status_code != 200:
            print(f"Task {workflow_name} not found")
            continue
        workflow_data = response_workflow.json()
        for index, value in df.iterrows():
            if value['Task Monitor'].find(TASK_MONITOR_SUBFIX) != -1 and workflow_name in value['Sub workflow']:
                variable_monitor_name = getVariableNameCustomReplace(value['Task Monitor'], TASK_MONITOR_SUBFIX, VARIABLE_MONITOR_SUBFIX)
                for vertex in workflow_data['workflowVertices']:
                    if vertex['task']['value'] == value['Task Monitor']:
                        vertex['task']['value'] = variable_monitor_name
                        break
                for edge in workflow_data['workflowEdges']:
                    if edge['sourceId']['taskName'] == value['Task Monitor']:
                        edge['sourceId']['taskName'] = variable_monitor_name
                    if edge['targetId']['taskName'] == value['Task Monitor']:
                        edge['targetId']['taskName'] = variable_monitor_name
        if workflow_data == response_workflow.json():
            print(f"Task {workflow_name} not changed")
            continue
        response_update = updateTaskAPI(workflow_data)
        if response_update.status_code == 200:
            print(f"Replace task in workflow {workflow_name} successfully")
        else:
            print(f"Replace task in workflow {workflow_name} failed")
    return None
            
            
    

################################################################
        
def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = "http://172.16.1.161:8080/uc/resources"
    updateURI(domain)
    df = getDataExcel()
    #APIdata = getData()
    print(df)
    #print("Number of Response:",len(APIdata),"\n")
    print("create variable")
    #createVariable(df)
    print("create variable monitor")
    #createVariableMonitor(df)
    print("add action to task")
    #addActionToTask(df)
    print("replace task in workflow")
    replaceTaskInWorkflow(df)






if __name__ == "__main__":
    main()