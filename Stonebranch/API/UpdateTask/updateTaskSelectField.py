import sys
import os
import json
import pandas as pd
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.stbAPI import updateURI, updateAuth, updateTaskAPI, getTaskAPI
from utils.readFile import loadJson
from utils.createFile import createJson
from utils.readExcel import getDataExcel
from utils.createFile import createExcel


ENABLE_UPDATE = False


task_configs_temp = {
    "taskname": None
}

# "description" = "summary" // only does not exist
# "command" = largeTextField1["value"]
# "application" = customField1["value"]

specific_field_list = [
    "description",
    "command",
    "application"
]



def cleanValue(value):
    if isinstance(value, str):
        return value.strip()
    if pd.isna(value):
        return ''
    return value

def prepareUpdateTask(df_update, specific_field_list = []):
    df_dict = {}
    for row in df_update.itertuples(index=False):
        field = row.fieldname
        if specific_field_list == [] or field in specific_field_list:
            if row.jobName not in df_dict:
                df_dict[row.jobName] = {}
            df_dict[row.jobName][field] = cleanValue(row.new_value)
    return df_dict

def prepareUpdateTaskConfigs(task_data, update_fields):
    task_update = copy.deepcopy(task_data)  # Create a copy of the original dictionary
    success_fields = []
    no_change_fields = []
    for field, value in update_fields.items():
        #print(f"{field} - {value}")
        if field == "description":
            if task_update.get("summary", "") != value:
                if task_update.get("summary", "") == "":
                    task_update["summary"] = value
                    success_fields.append(field)
                else:
                    no_change_fields.append(field)
        if field == "command":
            if "largeTextField1" not in task_update:
                task_update["largeTextField1"] = {"label": "Command", "name": "command"}
            if task_update["largeTextField1"].get("value", "") != value:
                value = value.replace("\\\"", "\"")
                value = value.replace("\"", "\\\"")
                task_update["largeTextField1"]["value"] = value
                success_fields.append(field)
            else:
                no_change_fields.append(field)
        if field == "application":
            if "customField1" not in task_update:
                task_update["customField1"] = {"label": "Application"}
            if task_update["customField1"].get("value", "") != value:
                task_update["customField1"]["value"] = value
                success_fields.append(field)
            else:
                no_change_fields.append(field)
            
    
    return task_update, success_fields, no_change_fields



def updateTask(df_update):
    not_found = []
    no_change = []
    success = []
    df_dict = prepareUpdateTask(df_update, specific_field_list)
    #print(json.dumps(df_dict, indent=4))
    print(len(df_dict))
    for taskname, update_fields in df_dict.items():
        print("\n")
        task_configs = task_configs_temp.copy()
        task_configs["taskname"] = taskname
        response_task = getTaskAPI(task_configs, False)
        if response_task.status_code == 200:
            task_data = response_task.json()
            print(taskname)
            task_update, success_fields, no_change_fields = prepareUpdateTaskConfigs(task_data, update_fields)
            if task_update == task_data:
                #print(json.dumps(task_data, indent=4))
                #print(json.dumps(task_update, indent=4))
                print(f"No changes for {taskname}")
                no_change.append({
                    "taskname": taskname,
                    "no_change_fields": no_change_fields
                })
                continue
            #print(update_fields)
            success.append({
                "taskname": taskname,
                "success_fields": success_fields
            })
            if ENABLE_UPDATE:
                print(f"Updating {taskname}")
                response = updateTaskAPI(task_update, False)
                if response.status_code == 200:
                    print(f"Task {taskname} updated successfully")
                else:
                    print(f"Error updating {taskname}")
            else:
                print(f"Update process disabled")
        else:
            print(f"Error getting {taskname}")
            not_found.append(taskname)
        #print("\n")
    return {
        "not_found": not_found,
        "no_change": no_change,
        "success": success
    }

def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain = "https://ttbdevstb.stonebranch.cloud/resources"
    #domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    
    df_update = getDataExcel()
    #print(df_update)
    result = updateTask(df_update)
    print(json.dumps(result, indent=4))
    createJson("updateTaskResult.json", result)
    
if __name__ == '__main__':
    main()