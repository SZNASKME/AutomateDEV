import sys
import os
import json
import math

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.readExcel import getDataExcel
from utils.stbAPI import updateURI, updateAuth, createTaskAPI, getListTaskAPI
from utils.loadFile import loadJson

task_configs_temp = {
    "name": "*",
    "businessServices": "A0076 - Data Warehouse ETL",
}




def ListTask():
    task_configs = task_configs_temp.copy()
    response = getListTaskAPI(task_configs)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def prepareCreatingTaskList(df, exist_task_list):
    dfnew = df[~df["jobName"].isin(exist_task_list)]
    
    return dfnew

def createTaskConfigs(data, map_fields):
    task_configs = {}
    for key, value in data.items():
        matching_key = None
        for map_key, map_value in map_fields.items():
            if key == map_value:
                matching_key = map_key
                break
        if matching_key and not (isinstance(value, float) and math.isnan(value)):
            task_configs[matching_key] = value
    return task_configs

def restructureTaskConfigs(task_configs):
    new_task_configs = {}
    if task_configs["type"] == "BOX":
        new_task_configs["type"] = "taskWorkflow"
    if task_configs["type"] == "CMD":
        new_task_configs["type"] = "taskUniversal"
    
    if 'name' in task_configs:
        new_task_configs["name"] = task_configs["name"]
    if 'credentials' in task_configs:
        if task_configs['type'] != 'BOX':
            new_task_configs["credentials"] = task_configs["credentials"]
    
    if "summary" in task_configs:
        new_task_configs["summary"] = task_configs["summary"]
    
    if "largeTextField1" in task_configs:
        new_task_configs["largeTextField1"] = {
            "label": "Command",
            "name": "command",
            "value": task_configs["largeTextField1"]
        }
    if "textField1" in task_configs:
        new_task_configs["textField1"] = {
            "label": "Profile File",
            "name": "profile_file",
            "value": task_configs["textField1"]
        }
    if "textField2" in task_configs:
        new_task_configs["textField2"] = {
            "label": "STDOUT File",
            "name": "stdout_file",
            "value": task_configs["textField2"]
        }
    if "textField3" in task_configs:
        new_task_configs["textField3"] = {
            "label": "STDERR File",
            "name": "stderr_file",
            "value": task_configs["textField3"]
        }

    if "retryMaximum" in task_configs:
        new_task_configs["retryMaximum"] = int(task_configs["retryMaximum"])
    if "agentCluster" in task_configs:
        new_task_configs["agentCluster"] = task_configs["agentCluster"]
    
    if "customField1" in task_configs:
        new_task_configs["customField1"] = {
            "label": "Application",
            "value": task_configs["customField1"]
        }   
    
    return new_task_configs



def createTaskList(df, map_fields):

    for _, row in df.iterrows():
        task_configs = createTaskConfigs(row, map_fields)
        print(json.dumps(task_configs, indent=4))
        task_configs = restructureTaskConfigs(task_configs)
        print(json.dumps(task_configs, indent=4))
        #response = createTaskAPI(task_configs)
        #if response.status_code == 200:
        #    print(f"Task {task_configs["jobName"]} created")
        #else:
        #    print(f"Task {task_configs["jobName"]} failed to create")




def main():
    auth = loadJson("auth.json")
    userpass = auth["ASKME_STB"]
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = "http://172.16.1.86:8080/uc/resources"
    updateURI(domain)
    
    df = getDataExcel()
    exist_task_list = ListTask()
    
    new_task_df = prepareCreatingTaskList(df, exist_task_list)
    map_fields = loadJson("STB_Excel.json")
    createTaskList(new_task_df, map_fields)
    print(f"Total Task to create: {len(new_task_df)}")
    print(new_task_df)


if __name__ == "__main__":
    main()