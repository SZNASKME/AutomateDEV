import sys
import os
import json
import math

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from utils.readExcel import getDataExcel
from utils.stbAPI import updateURI, updateAuth, createTaskAPI, createBusinessServiceAPI, getBusinessServiceAPI
from utils.readFile import loadJson
from utils.createFile import createJson

JOB_COLUMN = "jobName"
WORKFLOW_CATEGORY = "BOX"
UNIVERSAL_CATEGORY = "CMD"
FILE_MONITOR_CATEGORY = "FW"

MAP_EXCEL_JSON = "STB_Map_Excel.json"
CREATE_TASK_JSON = "logs\\createTaskLog.json"


# def prepareCreatingTaskList(df, exist_task_list):
#     dfnew = df[~df[JOB_COLUMN].isin(exist_task_list)]
    
#     return dfnew

business_service_configs_temp = {
    "name": None,
}

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

def restructureTaskConfigs(task_configs, business_service = None):
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
    if task_type == WORKFLOW_CATEGORY:
        new_task_configs["type"] = "taskWorkflow"
    elif task_type == UNIVERSAL_CATEGORY:
        new_task_configs["type"] = "taskUniversal"
        new_task_configs["exitCodes"] = "0"
        # Check for Linux or Windows based on fields
        if "/" in task_configs.get("largeTextField1", ""):
            new_task_configs["template"] = "Enhanced Linux"
            command = task_configs.get("largeTextField1", "")
            command = command.replace("\\\"", "\"")
            command = command.replace("\"", "\\\"")
            new_task_configs["largeTextField1"]["value"] = command
        elif "\\" in task_configs.get("largeTextField1", ""):
            new_task_configs["template"] = "Enhanced Windows"
    elif task_type == FILE_MONITOR_CATEGORY:
        new_task_configs["type"] = "taskFileMonitor"
    
    if task_type != WORKFLOW_CATEGORY and "credentials" in task_configs:
        new_task_configs["credentials"] = task_configs["credentials"]    
    
    if "retryMaximum" in task_configs:
        new_task_configs["retryMaximum"] = int(task_configs["retryMaximum"])
    

    for key, value in task_configs.items():
        if key not in new_task_configs and key not in fields_map and key != "type":
            new_task_configs[key] = value
    
    # Additional configurations
    
    if business_service:
        if not isinstance(business_service, list):
            business_service = [business_service]
        new_task_configs["opswiseGroups"] = business_service
        
    return new_task_configs



def createBusinessService(business_service = None):
    if business_service:
        business_service_configs = business_service_configs_temp.copy()
        business_service_configs["name"] = business_service
        response_get = getBusinessServiceAPI(business_service_configs, False)
        if response_get.status_code == 200:
            print(f"Business Service {business_service} already exists")
            return
        response_create = createBusinessServiceAPI(business_service_configs)
        if response_create.status_code == 200:
            print(f"Business Service {business_service} created")
        else:
            print(f"Business Service {business_service} failed to create")
    


def createTaskList(df, map_fields, business_service = None):
    create_log = []
    for _, row in df.iterrows():
        task_configs = createTaskConfigs(row, map_fields)
        #print(json.dumps(task_configs, indent=4))
        task_configs = restructureTaskConfigs(task_configs, business_service)
        #print(json.dumps(task_configs, indent=4))
        response = createTaskAPI(task_configs)
        if response.status_code == 200:
            create_log.append({
                "name": task_configs['name'],
                "status": "Success"
            })
            print(f"Task {task_configs['name']} created")

        else:
            create_log.append({
                "name": task_configs['name'],
                "status": "Failed"
            })
            print(f"Task {task_configs['name']} failed to create")

    return create_log

def main():
    auth = loadJson("auth.json")
    userpass = auth["ASKME_STB"]
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['1.86']
    updateURI(domain)
    
    new_task_df = getDataExcel("Get New Task from Excel")
    business_service_input = input("Enter Business Service: ")
    #new_task_df = prepareCreatingTaskList(df, exist_task_list)
    createBusinessService(business_service_input)
    map_fields = loadJson(MAP_EXCEL_JSON)
    create_log = createTaskList(new_task_df, map_fields, business_service_input)
    createJson(CREATE_TASK_JSON, create_log)
    count = 0
    for log in create_log:
        if log["status"] == "Success":
            count += 1
    print(f"{count} tasks created successfully")


if __name__ == "__main__":
    main()