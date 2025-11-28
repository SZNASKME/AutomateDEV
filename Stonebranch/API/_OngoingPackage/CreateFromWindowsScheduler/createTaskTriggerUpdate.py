import sys
import os
import json
from unittest import result
import pandas as pd
import math
import re
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import *
from utils.readFile import loadJson
from utils.createFile import createJson, createExcel
from utils.readExcel import getDataExcel

JSON_PATH = 'C:\\Dev\\AutomateDEV\\Stonebranch\\API\\_OngoingPackage\\CreateFromWindowsScheduler\\config\\'

JOB_COLUMN = "Name"
MACHINE_COLUMN = "HostName"

EXCEL_SHEETNAME_DUPLICATE = 'Duplicate Task Names'
EXCEL_SHEET_TASKNAME = 'Task Creation Log'
EXCEL_SHEET_TRIGGERNAME = 'Trigger Creation Log'
EXCEL_OUTPUT_NAME = 'Task_Trigger_Creation_Log.xlsx'
EXCEL_TASKNAME_COLUMN = 'Name'

TASK_COLUMN_MAPPING_PATHNAME = 'Task_Column_Mapping_Update.json'
TRIGGER_COLUMN_MAPPING_PATHNAME = 'Trigger_Column_Mapping_Update.json'

WINDOWS_TASKTYPE = "taskWindows"
COMMAND_TYPE = "Command"
OUTPUT_TYPE = "OUTERR"
OUTPUT_STARTLINE = 1
OUTPUT_NLINE = 100

TASKNAME_COLUMN = "name"
COMMAND_COLUMN = "command"
AGENT_COLUMN = "agent"
ARGUMENTS_COLUMN = "arguments"
WORKING_DIRECTORY_COLUMN = "working_directory"

TRIGGERNAME_COLUMN = "name"
TRIGGER_TASKNAME_COLUMN = "tasks"
TRIGGER_TYPE_LIST = ["Daily", "Weekly", "Monthly", "One Time"]
TRIGGER_TYPE_COLUMN = "triggerType"
TRIGGER_TIME_COLUMN = "triggerTime"
TRIGGER_DESCRIPTION_COLUMN = "description"
TRIGGER_STATUS_COLUMN = "status"

TIMEZONE_DEFAULT = "UTC"
TIME_TRIGGER_TYPE = "triggerTime"
MANUAL_TRIGGER_TYPE = "triggerManual"
TIME_FORMAT = "HH:MM"
MONTH_CUSTOM_DAY_FORMAT = "MNTHD#"




def checkDuplicateIgnoreSensitive(value, value_list):
    count = 0
    for v in value_list:
        if v.lower() == value.lower():
            count += 1
    if count > 1:
        return True
    else:
        return False


def restructureWindowsTaskConfigs(task_configs):
    new_task_configs = {}
    
    new_task_configs['name'] = task_configs[TASKNAME_COLUMN]
    
    new_task_configs['type'] = WINDOWS_TASKTYPE
    
    ###### For test only ######
    #new_task_configs['agentVar'] = "STBWS227 - AGNT0001"
    
    ###### Real use ######
    new_task_configs['agentVar'] = '${' + task_configs.get(AGENT_COLUMN, "") + '}'
    
    if task_configs.get(AGENT_COLUMN, "") in task_configs.get(TASKNAME_COLUMN, ""):
        original_task_name = task_configs.get(TASKNAME_COLUMN, "").replace(f"_{task_configs.get(AGENT_COLUMN, '')}", "")
        new_task_configs['summary'] = f"Original Task Name: {original_task_name}"
    
    new_task_configs['commandOrScript'] = COMMAND_TYPE
    
    if ARGUMENTS_COLUMN in task_configs:
        new_task_configs['command'] = task_configs.get(COMMAND_COLUMN, "") + " " + task_configs.get(ARGUMENTS_COLUMN, "")
    else:
        new_task_configs['command'] = task_configs.get(COMMAND_COLUMN, "")
    
    if WORKING_DIRECTORY_COLUMN in task_configs:
        new_task_configs['runtimeDir'] = task_configs.get(WORKING_DIRECTORY_COLUMN, "")
        
    new_task_configs['outputReturnType'] = OUTPUT_TYPE
    
    new_task_configs['waitForOutput'] = True
    
    new_task_configs['outputReturnSline'] = OUTPUT_STARTLINE
    
    new_task_configs['outputReturnNline'] = OUTPUT_NLINE
    
    new_task_configs["exitCodes"] = "0"
    
    return new_task_configs




def restructureTriggerConfigs(trigger_configs_list):
    
    def getTriggerDetails(trigger_configs_list):
        trigger_details_list = []
        for value in trigger_configs_list:
            #if TRIGGER_TYPE_COLUMN in value:
            trigger_name = value.get(TRIGGERNAME_COLUMN, "")
            trigger_task_name = value.get(TRIGGER_TASKNAME_COLUMN, "")
            trigger_type = value.get(TRIGGER_TYPE_COLUMN, "")
            trigger_description = value.get(TRIGGER_DESCRIPTION_COLUMN, "")
            trigger_time = value.get(TRIGGER_TIME_COLUMN, "")
            trigger_status = value.get(TRIGGER_STATUS_COLUMN, "")
            trigger_details_list.append({
                "name": trigger_name,
                "tasks": trigger_task_name,
                "type": trigger_type,
                "description": trigger_description,
                "time": trigger_time,
                "status": trigger_status
            })
                    
        return trigger_details_list
    
    def analyzeTriggerType(trigger_details_list):
        type_list = [type_detail['type'] for type_detail in trigger_details_list]
        unique_types = set(type_list)
        analyze_trigger_type = list(unique_types)
        return analyze_trigger_type

    
    def timeFormatConversion(time_str, time_format):
        ## Remove Date in time string if exists
        time_only_str = time_str.split(' ')[-1]
        if time_format == "HH:MM":
            time_parts = time_only_str.split(':')
            if len(time_parts) >= 2:
                return f"{time_parts[0]}:{time_parts[1]}"
            else:
                return time_only_str
        else:
            return time_only_str
    
    def shortenDescription(description):
        # remove At  in string
        #new_description = description.replace("At ", "")
        # remove MM/DD/YYYY in string
        date_pattern = r'At \b\d{1,2}/\d{1,2}/\d{4}\b'
        new_description = re.sub(date_pattern, "", description).strip()
        return new_description
    
    def calculateDayOfWeekFromDescription(description):
        days_of_week = {
            "Sunday": "sun",
            "Monday": "mon",
            "Tuesday": "tue",
            "Wednesday": "wed",
            "Thursday": "thu",
            "Friday": "fri",
            "Saturday": "sat"
        }
        found_days = {}
        for day, abbrev in days_of_week.items():
            if day.lower() in description.lower():
                found_days[abbrev] = True
        return found_days
    
    def calculateMonthDayFromDescription(description):
        def parseDaysMonths(text: str):
            m = re.search(r'on day (.+?) of (.+)$', text)
            if not m:
                return [], []
            days_part = m.group(1)
            months_part = m.group(2)
            days = [d.strip() for d in days_part.split(',') if d.strip()]
            months = [mth.strip() for mth in months_part.split(',') if mth.strip()]

            return days, months
        
        date_adjectives = ""
        date_nouns = []
        date_qualifiers = []
        
        mapping_months = {
            "January": "Jan",
            "February": "Feb",
            "March": "Mar",
            "April": "Apr",
            "May": "May",
            "June": "Jun",
            "July": "Jul",
            "August": "Aug",
            "September": "Sep",
            "October": "Oct",
            "November": "Nov",
            "December": "Dec"
        }
            
        # "on day 1,2,3 . . .,Last of" continue sequences string
        # "of January,February, . . .,December" continue sequences string
        date_nouns_list, date_qualifiers_list = parseDaysMonths(description)
        
        for match in date_qualifiers_list:
            month_abbrev = mapping_months.get(match, "")
            if month_abbrev:
                date_qualifiers.append({
                    "value": month_abbrev
                })
        
        for match in date_nouns_list:
            if match == "Last":
                date_nouns.append({
                    "value": "Last"
                })
            else:
                if len(date_qualifiers) == 12:
                    ## 01, 02, ..., 31 two digit format
                    match_int = int(match)
                    if 1 <= match_int <= 31:
                        match_str = f"{match_int:02}"
                    date_nouns.append({
                        "value": f"{MONTH_CUSTOM_DAY_FORMAT}{match_str}"
                    })
                else:
                    ## 1, 2, ..., 31 one digit format
                    for month_qualifier in date_qualifiers:
                        month_abbrev_upper = month_qualifier['value'].upper()
                        match_int = int(match)
                        if 1 <= match_int <= 31:
                            match_str = f"{match_int:02}"
                        date_nouns.append({
                            "value": f"{month_abbrev_upper}#{match_str}"
                        })
                

        
        ### Handle special cases
        if len(date_nouns) == 1 and date_nouns[0]['value'] == "Last":
            date_adjectives = "Last"
            date_nouns = [{
                "value": "Day"
            }]
        elif len(date_nouns) > 1 and any(n['value'] == "Last" for n in date_nouns):
            ## Remove Last if there are other days
            date_nouns = [n for n in date_nouns if n['value'] != "Last"]
            date_adjectives = "Every"
        else:
            date_adjectives = "Every"
                
        if len(date_qualifiers) == 12:
            date_qualifiers = [{
                "value": "Year"
            }]
            
        return date_adjectives, date_nouns, date_qualifiers

    
    
    new_trigger_configs_list = []
    trigger_not_created_list = []
    #print(trigger_configs_list)
    trigger_details_list = getTriggerDetails(trigger_configs_list)
    analyze_trigger_type = analyzeTriggerType(trigger_details_list)
    
    based_task_name = trigger_details_list[0].get("name", "N/A") if len(trigger_details_list) > 0 else "N/A"
    #print(f"{based_task_name} --> {analyze_trigger_type}")
    if len(analyze_trigger_type) == 0:
        print("No Trigger Type found in the input configurations.")
        
        trigger_not_created_list.append({
            "name": based_task_name,
            "message": "No Trigger Type found in the input configurations."
        })
        return new_trigger_configs_list, trigger_not_created_list
    elif len(analyze_trigger_type) >= 1:
        time_trigger_count = 0
        manual_trigger_count = 0
        previous_task_name = ""
        for task_detail in trigger_details_list:
            ### Reset count if new based task name
            if previous_task_name != task_detail.get("tasks", ""):
                time_trigger_count = 0
                manual_trigger_count = 0
                previous_task_name = task_detail.get("tasks", "")
                print("Reset Counts for new Task Name:", previous_task_name)
            
            if task_detail['type'] == "Daily":
                task_name = task_detail.get("name", "")
                trigger_task_name = task_detail.get("tasks", "")
                trigger_time = task_detail.get("time", "")
                description = task_detail.get("description", "")
                trigger_status = task_detail.get("status", "")
                time_str = timeFormatConversion(trigger_time, TIME_FORMAT)
                description_str = shortenDescription(description)
                if len(time_str) == 0:
                    trigger_not_created_list.append({
                        "name": f"{task_name}",
                        "message": "No valid time found for Daily trigger."
                    })
                    time_trigger_count += 1
                    continue
                new_trigger_configs = {}
                new_trigger_configs['name'] = f"{trigger_task_name}_TR00{time_trigger_count+1}"
                new_trigger_configs['tasks'] = [trigger_task_name]
                new_trigger_configs['type'] = TIME_TRIGGER_TYPE
                new_trigger_configs['time'] = time_str
                new_trigger_configs['description'] = f"{description_str} ({trigger_status})"
                new_trigger_configs_list.append(new_trigger_configs)
                time_trigger_count += 1
                
            if task_detail['type'] == "Weekly":
                task_name = task_detail.get("name", "")
                trigger_task_name = task_detail.get("tasks", "")
                trigger_time = task_detail.get("time", "")
                description = task_detail.get("description", "")
                trigger_status = task_detail.get("status", "")
                time_str = timeFormatConversion(trigger_time, TIME_FORMAT)
                description_str = shortenDescription(description)
                day_of_weeks_dict = calculateDayOfWeekFromDescription(description_str)
                if not day_of_weeks_dict:
                    trigger_not_created_list.append({
                        "name": f"{trigger_task_name}",
                        "message": "No valid day of week found in description for Weekly trigger."
                    })
                    time_trigger_count += 1
                    continue
                new_trigger_configs = {}
                new_trigger_configs['simpleDateType'] = "Specific Days"
                new_trigger_configs['name'] = f"{trigger_task_name}_TR00{time_trigger_count+1}"
                new_trigger_configs['tasks'] = [trigger_task_name]
                new_trigger_configs["type"] = TIME_TRIGGER_TYPE
                new_trigger_configs['time'] = time_str
                new_trigger_configs.update(day_of_weeks_dict)
                new_trigger_configs['description'] = f"{description_str} ({trigger_status})"
                new_trigger_configs_list.append(new_trigger_configs)
                time_trigger_count += 1
        
            if task_detail['type'] == "Monthly":
                task_name = task_detail.get("name", "")
                trigger_task_name = task_detail.get("tasks", "")
                trigger_time = task_detail.get("time", "")
                description = task_detail.get("description", "")
                trigger_status = task_detail.get("status", "")
                time_str = timeFormatConversion(trigger_time, TIME_FORMAT)
                description_str = shortenDescription(description)
                date_adjectives, date_nouns, date_qualifiers = calculateMonthDayFromDescription(description)
                if len(time_str) == 0:
                    trigger_not_created_list.append({
                        "name": f"{trigger_task_name}",
                        "message": "No valid time found for Monthly trigger."
                    })
                    time_trigger_count += 1
                    continue
                new_trigger_configs = {}
                new_trigger_configs['dayStyle'] = "Complex"
                new_trigger_configs['name'] = f"{trigger_task_name}_TR00{time_trigger_count+1}"
                new_trigger_configs['tasks'] = [trigger_task_name]
                new_trigger_configs['type'] = TIME_TRIGGER_TYPE
                new_trigger_configs['time'] = time_str
                new_trigger_configs['dateAdjective'] = date_adjectives
                new_trigger_configs['dateNouns'] = date_nouns
                new_trigger_configs['dateQualifiers'] = date_qualifiers
                new_trigger_configs['description'] = f"{description_str} ({trigger_status})"
                new_trigger_configs_list.append(new_trigger_configs)
                time_trigger_count += 1
                
            if task_detail['type'] == "One Time":
                task_name = task_detail.get("name", "")
                trigger_task_name = task_detail.get("tasks", "")
                trigger_time = task_detail.get("time", "")
                description = task_detail.get("description", "")
                trigger_status = task_detail.get("status", "")
                time_str = timeFormatConversion(trigger_time, TIME_FORMAT)
                description_str = shortenDescription(description)
                if len(time_str) == 0:
                    trigger_not_created_list.append({
                        "name": f"{trigger_task_name}",
                        "message": "No valid time found for One Time trigger."
                    })
                    manual_trigger_count += 1
                    continue
                new_trigger_configs = {}
                new_trigger_configs['name'] = f"{trigger_task_name}_MN00{manual_trigger_count+1}"
                new_trigger_configs['tasks'] = [trigger_task_name]
                new_trigger_configs['type'] = MANUAL_TRIGGER_TYPE
                new_trigger_configs['description'] = f"[Manual] ({trigger_status})"
                new_trigger_configs_list.append(new_trigger_configs)
                manual_trigger_count += 1
    else:
        trigger_not_created_list.append({
            "name": based_task_name,
            "message": "Supported Trigger Types are Daily, Weekly, Monthly, One Time."
        })
    
    
    return new_trigger_configs_list, trigger_not_created_list



#####################################################################################################

def createTaskFromAPI(df, column_mapping, creating=True):
    
    def renameDuplicateColumns(task_df, original_col, append_col, new_col=None, is_duplicate_name=False):
        task_df = pd.DataFrame(task_df)
        dedup_task_df = task_df.drop_duplicates([original_col, append_col])
        
        for index, row in dedup_task_df.iterrows():
            task_name = row[original_col]
            machine_name = row[append_col]
            if len(dedup_task_df) > 1 or is_duplicate_name:
                new_name = f"{task_name}_{machine_name}"
            else:
                new_name = f"{task_name}"
            if new_col:
                dedup_task_df.at[index, new_col] = new_name
            else:
                dedup_task_df.at[index, original_col] = new_name
            
        return dedup_task_df

    
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
    
    task_list = df[JOB_COLUMN].unique()
    
    for task in task_list:
        task_df = df[df[JOB_COLUMN] == task]
        if len(task_df) > 1:
            if checkDuplicateIgnoreSensitive(task, task_list):
                is_duplicate_name = True
            else:
                is_duplicate_name = False
            task_df = renameDuplicateColumns(task_df, JOB_COLUMN, MACHINE_COLUMN, is_duplicate_name=is_duplicate_name)
        for index, row in task_df.iterrows():
            task_configs = createTaskConfigs(row, column_mapping)
            restructured_task_configs = restructureWindowsTaskConfigs(task_configs)

            if not creating:
                task_created_log.append({
                    "Task Name": restructured_task_configs['name'],
                    "Status": "Pending",
                    "Details": "Task creation initiated"
                })
                continue
            task_response = createTaskAPI(restructured_task_configs)
            if task_response.status_code == 200:
                task_created_log.append({
                    "Task Name": restructured_task_configs['name'],
                    "Status": "Created",
                    "Details": task_response.text
                })
            else:
                task_created_log.append({
                    "Task Name": restructured_task_configs['name'],
                    "Status": "Failed",
                    "Details": task_response.text
                })
    
    df_task_log = pd.DataFrame(task_created_log)
    return df_task_log


def createTriggerFromAPI(df, column_mapping, creating=True):
    
    def cloneValuesInList(configs_list, original_key, new_key):
        new_configs_list = []
        for config in configs_list:
            new_config = config.copy()
            new_config[new_key] = new_config.get(original_key, "")
            new_configs_list.append(new_config)
        return new_configs_list
    
    def renameDuplicateValuesInList(configs_list, original_key, append_key, is_duplicate_name=False):
        
        seen = set()
        deduped_values = []
        for config in configs_list:
            key = (config.get(original_key, ""), config.get(append_key, ""))
            if key not in seen:
                deduped_values.append(key)
                seen.add(key)
        #print(deduped_values)
        
        for config in configs_list:
            original_value = config.get(original_key, "")
            append_value = config.get(append_key, "")
            if len(deduped_values) > 1 or is_duplicate_name:
                new_value = f"{original_value}_{append_value}"
            else:
                new_value = original_value
            config[original_key] = new_value
        
        return configs_list
    
    def convertDatetimeToString(configs_list):
        for config in configs_list:
            for key, value in config.items():
                if isinstance(value, (datetime, pd.Timestamp)):
                    config[key] = value.strftime('%H:%M:%S') if hasattr(value, 'strftime') else str(value)
        return configs_list
    
    def createTriggerConfigs(data, map_fields):
        trigger_configs = {}
        for key, value in data.items():
            matching_key = None
            for map_key, map_value in map_fields.items():
                if key == map_value:
                    matching_key = map_key
                    break
            if matching_key and not (isinstance(value, float) and math.isnan(value)):
                trigger_configs[matching_key] = value
        return trigger_configs
    
    
    trigger_created_log = []
    trigger_based_list = df[JOB_COLUMN].unique()
    
    for trigger_based in trigger_based_list:
        trigger_df = df[df[JOB_COLUMN] == trigger_based]
        trigger_configs_list = []
        for index, row in trigger_df.iterrows():
            trigger_configs = createTriggerConfigs(row, column_mapping)
            #print(json.dumps(trigger_configs, indent=4))
            trigger_configs_list.append(trigger_configs)
        #print(len(trigger_configs_list), trigger_based)
        trigger_configs_list = cloneValuesInList(trigger_configs_list, TRIGGERNAME_COLUMN, TRIGGER_TASKNAME_COLUMN)
        trigger_configs_list = convertDatetimeToString(trigger_configs_list)
        if len(trigger_configs_list) > 1:
            is_duplicate_name = checkDuplicateIgnoreSensitive(trigger_based, trigger_based_list)
            trigger_configs_list = renameDuplicateValuesInList(trigger_configs_list, TRIGGER_TASKNAME_COLUMN, AGENT_COLUMN, is_duplicate_name=is_duplicate_name)
        
        #print(json.dumps(trigger_configs_list, indent=4))
        restructured_trigger_configs_list, trigger_not_created_list = restructureTriggerConfigs(trigger_configs_list)
        
        if not creating:
            for restructured_trigger_configs in restructured_trigger_configs_list:
                trigger_created_log.append({
                    "Trigger Name": restructured_trigger_configs['name'],
                    "Task Name": ",".join(restructured_trigger_configs['tasks']),
                    "Status": "Pending",
                    "Details": "Trigger creation initiated"
                })
            continue
        # print(json.dumps(restructured_trigger_configs_list, indent=4))
        if len(restructured_trigger_configs_list) > 0:
            for restructured_trigger_configs in restructured_trigger_configs_list:
                
                
                trigger_response = createTriggerAPI(restructured_trigger_configs)
                
                if trigger_response.status_code == 200:
                    #print(f"Trigger for Task {restructured_trigger_configs['name']} created")
                    trigger_created_log.append({
                        "Trigger Name": restructured_trigger_configs['name'],
                        "Task Name": ",".join(restructured_trigger_configs['tasks']),
                        "Status": "Created",
                        "Details": trigger_response.text
                    })
                else:
                    #print(f"Failed to create Trigger for Task {restructured_trigger_configs['name']}: {trigger_response.text}")
                    trigger_created_log.append({
                        "Trigger Name": restructured_trigger_configs['name'],
                        "Task Name": ",".join(restructured_trigger_configs['tasks']),
                        "Status": "Failed",
                        "Details": trigger_response.text
                    })
                    
        if len(trigger_not_created_list) > 0:
            for trigger_not_created in trigger_not_created_list:
                trigger_created_log.append({
                    "Trigger Name": trigger_not_created['name'],
                    "Task Name": "",
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
    df_task_log = createTaskFromAPI(df, task_column_mapping, False)
    df_trigger_log = createTriggerFromAPI(df, trigger_column_mapping, False)
    
    #createExcel(EXCEL_OUTPUT_NAME, (EXCEL_SHEETNAME_DUPLICATE, df_duplicates), (EXCEL_SHEET_TASKNAME, df_task_log))
    #createExcel(EXCEL_OUTPUT_NAME, (EXCEL_SHEETNAME_DUPLICATE, df_duplicates), (EXCEL_SHEET_TRIGGERNAME, df_trigger_log))
    createExcel(EXCEL_OUTPUT_NAME, (EXCEL_SHEETNAME_DUPLICATE, df_duplicates), (EXCEL_SHEET_TASKNAME, df_task_log), (EXCEL_SHEET_TRIGGERNAME, df_trigger_log))
    

if __name__ == "__main__":
    main()