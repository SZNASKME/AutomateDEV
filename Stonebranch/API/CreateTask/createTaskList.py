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
    
    fields_map = {
        "largeTextField1": {"label" : "Command", "name": "command"},
        "textField1": {"label" : "Profile File", "name": "profile_file"},
        "textField2": {"label" : "STDOUT File", "name": "stdout_file"},
        "textField3": {"label" : "STDERR File", "name": "stderr_file"},
        "customField1": {"label" : "Application"}
    }
    for field, field_data in fields_map.items():
        if field in task_configs:
            new_task_configs[field] = field_data.copy()
            new_task_configs[field]["value"] = task_configs[field]
    
    task_type = task_configs.get("type")
    if task_type == "BOX":
        new_task_configs["type"] = "taskWorkflow"
    elif task_type == "CMD":
        new_task_configs["type"] = "taskUniversal"
        # Check for Linux or Windows based on fields
        if "/" in task_configs.get("largeTextField1", ""):
            new_task_configs["template"] = "Enhanced Linux"
        elif "\\" in task_configs.get("largeTextField1", ""):
            new_task_configs["template"] = "Enhanced Windows"
    elif task_type == "FW":
        new_task_configs["type"] = "taskFileMonitor"
    
    if task_type != "BOX" and "credentials" in task_configs:
        new_task_configs["credentials"] = task_configs["credentials"]    
    
    if "retryMaximum" in task_configs:
        new_task_configs["retryMaximum"] = int(task_configs["retryMaximum"])
    

    for key, value in task_configs.items():
        if key not in new_task_configs and key not in fields_map and key != "type":
            new_task_configs[key] = value
    
    # Additional configurations
    new_task_configs["exitCodes"] = "0"
        
    return new_task_configs



def createTaskList(df, map_fields):

    for _, row in df.iterrows():
        task_configs = createTaskConfigs(row, map_fields)
        print(json.dumps(task_configs, indent=4))
        task_configs = restructureTaskConfigs(task_configs)
        print(json.dumps(task_configs, indent=4))
        response = createTaskAPI(task_configs)
        if response.status_code == 200:
            print(f"Task {task_configs["name"]} created")
        else:
            print(f"Task {task_configs["name"]} failed to create")
            break



def main():
    auth = loadJson("auth.json")
    userpass = auth["ASKME_STB"]
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = "http://172.16.1.161:8080/uc/resources"
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