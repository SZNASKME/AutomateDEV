import sys
import os
import json
from unittest import result
import pandas as pd
import math
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import *
from utils.readFile import loadJson
from utils.createFile import createJson, createExcel
from utils.readExcel import getDataExcel

JSON_PATH = 'C:\\Dev\\AutomateDEV\\Stonebranch\\API\\_OngoingPackage\\CreateFromWindowsScheduler\\config\\'

EXCEL_SHEETNAME_DUPLICATE = 'Duplicate Task Names'
EXCEL_SHEET_TASKNAME = 'Task Creation Log'
EXCEL_SHEET_TRIGGERNAME = 'Trigger Creation Log'
EXCEL_OUTPUT_NAME = 'Task_Trigger_Creation_Log.xlsx'
EXCEL_TASKNAME_COLUMN = 'Name'

TASK_COLUMN_MAPPING_PATHNAME = 'Task_Column_Mapping.json'
TRIGGER_COLUMN_MAPPING_PATHNAME = 'Trigger_Column_Mapping.json'

WINDOWS_TASKTYPE = "taskWindows"
COMMAND_TYPE = "Command"
OUTPUT_TYPE = "OUTERR"

TASKNAME_COLUMN = "name"
COMMAND_COLUMN = "command"
AGENT_COLUMN = "agent"
ARGUMENTS_COLUMN = "arguments"
WORKING_DIRECTORY_COLUMN = "working_directory"

TRIGGERNAME_COLUMN = "name"
TRIGGER_TYPE_LIST = ["Daily", "Weekly", "Monthly", "One Time"]
TRIGGER_TYPE_COLUMN = "triggerType"
TRIGGER_TIME_COLUMN = "triggerTime"
TRIGGER_DESCRIPTION_COLUMN = "description"

TIMEZONE_DEFAULT = "UTC"
TRIGGER_TYPE = "triggerTime"
TIME_FORMAT = "HH:MM"







def restructureWindowsTaskConfigs(task_configs):
    new_task_configs = {}
    
    new_task_configs['name'] = task_configs[TASKNAME_COLUMN]
    
    new_task_configs['type'] = WINDOWS_TASKTYPE
    
    ###### For test only ######
    #new_task_configs['agentVar'] = "STBWS227 - AGNT0001"
    
    ###### Real use ######
    new_task_configs['agentVar'] = '${' + task_configs.get(AGENT_COLUMN, "") + '}'
    
    new_task_configs['commandOrScript'] = COMMAND_TYPE
    
    if ARGUMENTS_COLUMN in task_configs:
        new_task_configs['command'] = task_configs.get(COMMAND_COLUMN, "") + " " + task_configs.get(ARGUMENTS_COLUMN, "")
    else:
        new_task_configs['command'] = task_configs.get(COMMAND_COLUMN, "")
    
    if WORKING_DIRECTORY_COLUMN in task_configs:
        new_task_configs['runtimeDir'] = task_configs.get(WORKING_DIRECTORY_COLUMN, "")
        
    new_task_configs['outputReturnType'] = OUTPUT_TYPE
    
    new_task_configs['waitForOutput'] = True
    
    new_task_configs["exitCodes"] = "0"
    
    return new_task_configs




def analyzeTriggerConfigs(trigger_configs):

    def numberOfDigitsInDict(dict_obj):
        digit_count = 0
        for key in dict_obj.keys():
            if key.isdigit():
                digit_count += 1
        return digit_count

    def getTriggerDetails(trigger_configs):
        trigger_details_list = []
        for key, value in trigger_configs.items():
            if key.isdigit():
                trigger_type = value.get(TRIGGER_TYPE_COLUMN, "")
                trigger_description = value.get(TRIGGER_DESCRIPTION_COLUMN, "")
                trigger_time = value.get(TRIGGER_TIME_COLUMN, "")
                trigger_details_list.append({
                    "index": key,
                    "type": trigger_type,
                    "description": trigger_description,
                    "time": trigger_time
                })
                    
        return trigger_details_list
    
    def findNumberOfTriggerType(trigger_details_list):
        trigger_type_count = {}
        for trigger_detail in trigger_details_list:
            trigger_type = trigger_detail['type']
            if trigger_type in TRIGGER_TYPE_LIST:
                if trigger_type not in trigger_type_count:
                    trigger_type_count[trigger_type] = 0
                trigger_type_count[trigger_type] += 1
        return trigger_type_count
    
    def calculateTimeFromTriggerDescription(trigger_type, description):
        ## Find Time Format (HH:MM:SS) in String ## 
        if trigger_type == "Daily" or "Weekly" and "every" in description:
            time_pattern = r'\b(\d{2}:\d{2}:\d{2})\b'
            time_match = re.search(time_pattern, description)
            if time_match:
                time_only = time_match.group(1)
                return time_only
    
    # Start analysis #
    analysis_result = {}
    number_of_digits = numberOfDigitsInDict(trigger_configs)
    trigger_details_list = getTriggerDetails(trigger_configs)
    trigger_type_count = findNumberOfTriggerType(trigger_details_list)
    # Analyze trigger time format
    
    
    analysis_result['based_trigger_name'] = trigger_configs[TRIGGERNAME_COLUMN]
    analysis_result['trigger_type_count'] = trigger_type_count
    
    if number_of_digits > 0:
        if number_of_digits == trigger_type_count.get("Daily", 0):
            analysis_result['trigger_type'] = "Daily"
            for trigger_detail in trigger_details_list:
                if trigger_detail['type'] == "Daily":
                    calculated_time = calculateTimeFromTriggerDescription("Daily", trigger_detail['description'])
                    if 'trigger_time' not in analysis_result:
                        analysis_result['trigger_time'] = []
                    if calculated_time:
                        analysis_result['trigger_time'].append((calculated_time, trigger_detail['description']))
        elif number_of_digits == trigger_type_count.get("Weekly", 0):
            analysis_result['trigger_type'] = "Weekly"
            for trigger_detail in trigger_details_list:
                if trigger_detail['type'] == "Weekly":
                    calculated_time = calculateTimeFromTriggerDescription("Weekly", trigger_detail['description'])
                    if 'trigger_time' not in analysis_result:
                        analysis_result['trigger_time'] = []
                    if calculated_time:
                        analysis_result['trigger_time'].append((calculated_time, trigger_detail['description']))
        elif number_of_digits == trigger_type_count.get("Monthly", 0):
            analysis_result['trigger_type'] = "Monthly"
        elif number_of_digits == trigger_type_count.get("One Time", 0):
            analysis_result['trigger_type'] = "One Time"
        else:
            
            # example: Daily: 2 || Weekly: 1 || Monthly: 1
            trigger_string = ' || '.join([f"{k}: {v}" for k, v in trigger_type_count.items()])
            analysis_result['trigger_type'] = trigger_string
    else:
        analysis_result['trigger_type'] = "None"
            
    return analysis_result



def restructureTriggerConfigs(trigger_configs):
    
    def timeFormatConversion(time, time_format):
        if time_format == "HH:MM":
            # Assuming input time is in HH:MM:SS format
            hh_mm = time[:5]
            return hh_mm
        return time
    
    def shortenDescription(description):
        # remove At  in string
        new_description = description.replace("At ", "")
        # remove MM/DD/YYYY in string
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b'
        new_description = re.sub(date_pattern, "", new_description).strip()
        return new_description
    
    
    new_trigger_configs_list = []
    trigger_not_created_list = []
    
    analysis_trigger_result = analyzeTriggerConfigs(trigger_configs)
    #print(f"Analysis Trigger Result: {analysis_trigger_result}")
    #print(f"Number of trigger <{based_trigger_name}> to create: {number_of_triggers}")
    based_trigger_name = analysis_trigger_result['based_trigger_name']
    trigger_type_count = analysis_trigger_result['trigger_type_count']
    trigger_type = analysis_trigger_result['trigger_type']
    trigger_time_list = analysis_trigger_result.get('trigger_time', [])
    
    if trigger_type == "Daily":
        count = 0
        for trigger_time, description in trigger_time_list:
            time_str = timeFormatConversion(trigger_time, TIME_FORMAT)
            description_str = shortenDescription(description)
            new_trigger_configs = {}
            new_trigger_configs['name'] = f"{based_trigger_name}_TR00{count+1}"
            new_trigger_configs['tasks'] = [based_trigger_name]
            #new_trigger_configs['timeZone'] = TIMEZONE_DEFAULT
            new_trigger_configs['type'] = TRIGGER_TYPE
            new_trigger_configs['time'] = time_str
            new_trigger_configs['description'] = description_str
            new_trigger_configs_list.append(new_trigger_configs)
            count += 1
    else:
        trigger_not_created_list.append({
            "name": based_trigger_name,
            "message": f"Trigger type <{trigger_type}> not supported for creation"
        })
    
    
    return new_trigger_configs_list, trigger_not_created_list



#####################################################################################################

def createTaskFromAPI(df, column_mapping):
    
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
    
    task_created_log = []
    
    for index, row in df.iterrows():
        
        task_configs = createTaskConfigs(row, column_mapping)
        #print(task_configs)
        restructured_task_configs = restructureWindowsTaskConfigs(task_configs)
        #print(json.dumps(restructured_task_configs, indent=4))
        task_response = createTaskAPI(restructured_task_configs)
        if task_response.status_code == 200:
            #print(f"Task {restructured_task_configs['name']} created")
            task_created_log.append({
                "Task Name": restructured_task_configs['name'],
                "Status": "Created",
                "Details": task_response.text
            })
        else:
            #print(f"Failed to create Task {restructured_task_configs['name']}: {task_response.text}")
            task_created_log.append({
                "Task Name": restructured_task_configs['name'],
                "Status": "Failed",
                "Details": task_response.text
            })
    
    df_task_log = pd.DataFrame(task_created_log)
    return df_task_log

def createTriggerFromAPI(df, column_mapping):
    
    def createTriggerConfigs(data, map_fields):
        trigger_configs = {}
        for key, value in data.items():
            matching_key = None
            index_matching_key = None
            for map_key, map_value in map_fields.items():
                if key == map_value:
                    matching_key = map_key
                    break
            if matching_key and not (isinstance(value, float) and math.isnan(value)):
                trigger_configs[matching_key] = value
                continue
            
            for map_key, map_value in map_fields.items():
                if key.startswith(map_value + '_'):
                    matching_key = map_key
                    index_matching_key = key.split('_', 1)[-1]
                    break
            if matching_key and not (isinstance(value, float) and math.isnan(value)):
                if index_matching_key not in trigger_configs:
                    trigger_configs[index_matching_key] = {}
                trigger_configs[index_matching_key][matching_key] = str(value)
            
        return trigger_configs
    
    
    
    trigger_created_log = []
    
    for index, row in df.iterrows():
        
        trigger_configs = createTriggerConfigs(row, column_mapping)
        #print(json.dumps(trigger_configs, indent=4))
        restructured_trigger_configs_list, trigger_not_created_list = restructureTriggerConfigs(trigger_configs)
        
        if len(restructured_trigger_configs_list) > 0:
            for restructured_trigger_configs in restructured_trigger_configs_list:
                #print(json.dumps(restructured_trigger_configs, indent=4))
                trigger_response = createTriggerAPI(restructured_trigger_configs)
                
                if trigger_response.status_code == 200:
                    #print(f"Trigger for Task {restructured_trigger_configs['name']} created")
                    trigger_created_log.append({
                        "Task Name": restructured_trigger_configs['name'],
                        "Status": "Created",
                        "Details": trigger_response.text
                    })
                else:
                    #print(f"Failed to create Trigger for Task {restructured_trigger_configs['name']}: {trigger_response.text}")
                    trigger_created_log.append({
                        "Task Name": restructured_trigger_configs['name'],
                        "Status": "Failed",
                        "Details": trigger_response.text
                    })
                    
        if len(trigger_not_created_list) > 0:
            for trigger_not_created in trigger_not_created_list:
                trigger_created_log.append({
                    "Task Name": trigger_not_created['name'],
                    "Status": "Not Created",
                    "Details": trigger_not_created['message']
                })
    
    df_trigger_log = pd.DataFrame(trigger_created_log)
    return df_trigger_log


def main():
    
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['1.227']
    updateURI(domain)
    
    task_column_mapping = loadJson(TASK_COLUMN_MAPPING_PATHNAME, 0, JSON_PATH)
    trigger_column_mapping = loadJson(TRIGGER_COLUMN_MAPPING_PATHNAME, 0, JSON_PATH)
    #print(task_column_mapping)
    
    df = getDataExcel()
    df_duplicates = df[df.duplicated([EXCEL_TASKNAME_COLUMN], keep=False)]
    df_task_log = createTaskFromAPI(df, task_column_mapping)
    df_trigger_log = createTriggerFromAPI(df, trigger_column_mapping)
    
    createExcel(EXCEL_OUTPUT_NAME, (EXCEL_SHEETNAME_DUPLICATE, df_duplicates), (EXCEL_SHEET_TASKNAME, df_task_log), (EXCEL_SHEET_TRIGGERNAME, df_trigger_log))
    

if __name__ == "__main__":
    main()