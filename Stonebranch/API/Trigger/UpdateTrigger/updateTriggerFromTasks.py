import sys
import os
import json
import pandas as pd
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from utils.stbAPI import updateURI, updateAuth, updateTriggerAPI, getTriggerAPI, getListTriggerAdvancedAPI
from utils.readFile import loadJson
from utils.createFile import createJson
from utils.readExcel import getDataExcel
from utils.createFile import createExcel


ENABLE_UPDATE = True


trigger_configs_temp = {
    "triggername": None
}

trigger_list_configs_temp = {
    "name": "*",
    "type": "Time"
}

# "description" = "summary" // only does not exist
# "command" = largeTextField1["value"]
# "application" = customField1["value"]

specific_field_list = [
    "Group",
    "Detail"
]

TASKNAME = "TaskName"
TRIGGERNAME = "name"


def cleanValue(value):
    if isinstance(value, str):
        return value.strip()
    if pd.isna(value):
        return ''
    return value

def prepareUpdateTrigger(df_update, specific_field_list = [], ignore_empty = True):
    df_dict = {}
    for row in df_update.itertuples(index=False):
        for field in df_update.columns:
            if specific_field_list == [] or field in specific_field_list:
                if ignore_empty and not cleanValue(getattr(row, field)):
                    continue
                if getattr(row, TASKNAME) not in df_dict:
                    df_dict[getattr(row, TASKNAME)] = {}
                df_dict[getattr(row, TASKNAME)][field] = cleanValue(getattr(row, field))
    return df_dict


def prepareUpdateTriggerConfigs(trigger_data, update_fields):
    
    def getTimeDetail(detail_str):
        # Example detail_str: "08:00:00 every 1 day" "14:00:00 on day 5,6,7,8 of January,February,March,April,May,June,July,August,September,October,November,December"
        # Get only "HH:MM" in string
        time_part = detail_str.split(' ')[0]
        hh_mm = ':'.join(time_part.split(':')[:2])
        return hh_mm
    
    def timeDescription(time_str, current_description):
        # Example time_str: "08:00"
        # Example current_description: "08:00:00 every 1 day" "14:00:00 on day 5,6,7,8 of January,February,March,April,May,June,July,August,September,October,November,December"
        # Return description with time part updated
        time_part = current_description.split(' ')[1:]  # Get parts after time
        new_description = f"{time_str}:00 " + ' '.join(time_part)
        return new_description
    
    
    trigger_update = copy.deepcopy(trigger_data)  # Create a copy of the original dictionary
    #print(trigger_update)
    print(update_fields)
    success_fields = []
    no_change_fields = []
    for field, value in update_fields.items():
        #print(f"{field} - {value}")
        #if field == "description":
        #    if task_update.get("summary", "") != value:
        #        #if task_update.get("summary", "") == "":
        #        task_update["summary"] = value
        #        success_fields.append(field)
        #    else:
        #        no_change_fields.append(field)
            #print(trigger_update.get("summary", ""))
        
        if field == "Group":
            if trigger_update.get("opswiseGroups", "") != [value]:
                if value == "":
                    trigger_update["opswiseGroups"] = []
                else:
                    trigger_update["opswiseGroups"] = [value]
                success_fields.append(field)
            else:
                no_change_fields.append(field)
                
        if field == "Detail":
            current_description = trigger_update.get('description', '')
            current_time = trigger_update.get('time', '')
            new_time = getTimeDetail(value)
            
            if current_description:
                current_time_from_desc = getTimeDetail(current_description)
            else:
                current_time_from_desc = current_time
            
            
            print(f"Updating Detail to {value} from {current_description} (time check: {current_time} vs {new_time}, desc_time: {current_time_from_desc})")
            
            # เปรียบเทียบทั้ง description และ time
            if current_description != value or current_time != new_time:
                time_desc = timeDescription(current_time, trigger_update["description"])
                trigger_update["description"] = time_desc
                success_fields.append(field)
            else:
                no_change_fields.append(field)
            
    
    return trigger_update, success_fields, no_change_fields


def updateTrigger(df_update, list_trigger_data):
    
    def getUpdateFieldFromTaskName(taskname, update_dict):
        return update_dict.get(taskname, {})
    
    
    
    not_found = []
    no_change = []
    success = []
    error = []
    update_dict = prepareUpdateTrigger(df_update, specific_field_list, False)
    update_list = list(update_dict.keys())
    #print(json.dumps(df_dict, indent=4))
    #print(len(df_dict))
    for row in list_trigger_data:
        triggername = row.get("name", "")
        tasks = row.get("tasks", [])
        #print(f"Processing Trigger: {triggername}")
        if tasks[0] in update_list:
            taskname = tasks[0]
            update_configs = getUpdateFieldFromTaskName(taskname, update_dict)
            
            # trigger_data = response_trigger.json()
            #print(triggername)
            trigger_update, success_fields, no_change_fields = prepareUpdateTriggerConfigs(row, update_configs)
            #print(row)
            #print(trigger_update)
            if trigger_update == row:
                #print(json.dumps(trigger_data, indent=4))
                #print(json.dumps(trigger_update, indent=4))
                print(f"No changes for {triggername}")
                no_change.append({
                    "triggername": triggername,
                    "no_change_fields": no_change_fields
                })
                continue
            #print(update_fields)

            if ENABLE_UPDATE:
                print(f"Updating {triggername}")
                #print(json.dumps(trigger_update, indent=4, ensure_ascii=False))
                response = updateTriggerAPI(trigger_update, False)
                if response.status_code == 200:
                    print(f"Trigger {triggername} updated successfully")
                    success.append({
                        "triggername": triggername,
                        "success_fields": success_fields
                    })
                else:
                    print(f"Error updating {triggername}")
                    error.append({
                        "triggername": triggername,
                        "message": response.text
                    })
            else:
                print(f"Update process disabled")
        else:
            print(f"Out of update list: {triggername}")
            not_found.append({
                "triggername": triggername
            })
        print("\n")
    
    df_not_found = pd.DataFrame(not_found, columns=["triggername"])
    df_no_change = pd.DataFrame(no_change, columns=["triggername", "no_change_fields"])
    df_success = pd.DataFrame(success, columns=["triggername", "success_fields"])
    df_error = pd.DataFrame(error, columns=["triggername", "message"])
    return df_not_found, df_no_change, df_success, df_error



def getListTrigger():
    
    list_trigger_response = getListTriggerAdvancedAPI(trigger_list_configs_temp)
    if list_trigger_response.status_code == 200:
        list_trigger_data = list_trigger_response.json()
        print(f"Total triggers: {len(list_trigger_data)}")
        
    else:
        print("Failed to get list of triggers")
        list_trigger_data = []
    return list_trigger_data

def main():
    auth = loadJson('Auth.json')
    userpass = auth['ASKME_STB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.181']
    #domain = domain_url['1.86']
    updateURI(domain)
    
    df_update = getDataExcel()
    list_trigger_data = getListTrigger()
    #print(df_update)
    df_not_found, df_no_change, df_success, df_error = updateTrigger(df_update, list_trigger_data)
    createExcel("Update_Trigger_Select_Field_Result.xlsx",
        ("Not_Found", df_not_found),
        ("No_Change", df_no_change),
        ("Success", df_success),
        ("Error", df_error)
    )
    
if __name__ == '__main__':
    main()
    
    
    
## update some field of task in UAC