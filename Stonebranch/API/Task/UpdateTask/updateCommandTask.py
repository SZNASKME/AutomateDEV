import sys
import os
import json
import re
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, getTaskAPI, updateTaskAPI, getBusinessServiceAPI
from utils.readFile import loadJson
from utils.createFile import createJson, createExcel


API_TASK_TYPE = [6, 99]
TASK_TYPE_LIST = ["taskFileMonitor", "taskUniversal"]


BUSINESS_SERVICES_LIST = [
    # 'A0076 - Data Warehouse ETL',
    # 'A0128 - Marketing Data Mart',
    # 'A0140 - NCB Data Submission',
    # 'A0329 - ODS',
    # 'A0356 - Big Data Foundation Platform',
    # 'A0356 - Big Data Foundation Platform (None-PRD)',
    # 'A0033 - BOT DMS (Data Management System)',
    # 'A0031 - Data Mart',
    # 'A0360 - Oracle Financial Services Analytical App',
    # 'A00000 - AskMe - Delete Tasks',
    'FEB24_2025'
]

task_list_configs_temp = {
    "name": "*",
    'businessServices': None,
    "type": None,
}

task_configs_temp = {
    'taskname': None,
}

JSON_OUTPUT_FILE = 'CommandTaskLog_NEW.json'
EXCEL_OUTPUT_FILE = 'CommandTaskLog_NEW.xlsx'
EXCEL_OUTPUT_SHEET = 'TaskLog'

operation_pairs = [
    {
        'char': r'${FILPTH}',
        'new_char': r'${DWH_EXA_FILPTH}',
        'active_condition': {
            'agentCluster': 'dwhprod_vr'
        },
        'exclude_pairs': []
    },
    {
        'char': r'${DWH_DWHPROD_FILPTH}',
        'new_char': r'${DWH_EXA_FILPTH}',
        'active_condition': {
            'agentCluster': 'dwhprod_vr'
        },
        'exclude_pairs': []
    },
    {
        'char': r'${DWH_DWHPROD_FXFILPTH}',
        'new_char': r'${DWH_EXA_FXFILPTH}',
        'active_condition': {
            'agentCluster': 'dwhprod_vr'
        },
        'exclude_pairs': []
        
    },
    {
        'char': r'${FXFILPTH}',
        'new_char': r'${DWH_EXA_FXFILPTH}',
        'active_condition': {
            'agentCluster': 'dwhprod_vr'
        },
    },
    
    {
        'char': r'${FILPTH}',
        'new_char': r'${DWH_DS_FILPTH}',
        'active_condition': {
            'agentCluster': 'dsdbprd_vr'
        },
        'exclude_pairs': []
    },
    {
        'char': r'${DWH_DSDB_FILPTH}',
        'new_char': r'${DWH_DS_FILPTH}',
        'active_condition': {
            'agentCluster': 'dsdbprd_vr'
        },
        'exclude_pairs': []
    },
    {
        'char': r'$FILPTH',
        'new_char': r'${DWH_DS_FILPTH}',
        'active_condition': {
            'agentCluster': 'dsdbprd_vr'
        },
        'exclude_pairs': []
    },
    
    {
        'char': '\"',
        'new_char': '\\\"',
        'active_condition': {},
        'exclude_pairs': [
            {
               "start": '$(',
               "end": ')'
            },
            {
               "start": '${',
               "end": '}'
            }
        ]
    }
]
exclude_pairs_range = [
        #{
        #    "start": '$(',
        #    "end": ')'
        #},
        #{
        #    "start": '${',
        #    "end": '}'
        #}
]


def getTaskList():
    task_list = []
    for type in API_TASK_TYPE:
        for service in BUSINESS_SERVICES_LIST:
            task_configs = task_list_configs_temp.copy()
            task_configs['type'] = type
            task_configs['businessServices'] = service
            response = getListTaskAPI(task_configs)
            if response.status_code == 200:
                task_list.extend(response.json())
    
    return task_list


def replaceCommand(command, string, new_string, exclude_pairs):
    replaced_command = command
    # Find all exclude ranges
    exclude_ranges = []
    for value in exclude_pairs:
        start = value['start']
        end = value['end']
        for match in re.finditer(f"{re.escape(start)}.*?{re.escape(end)}", replaced_command):
            exclude_ranges.append((match.start(), match.end()))
    # Function to check if a position is inside any exclude range
    def isInExcludeRange(pos):
        return any(start <= pos < end for start, end in exclude_ranges)

    # Iterate through text and replace only when outside the excluded ranges
    result = []
    i = 0
    while i < len(replaced_command):
        if replaced_command[i:i+len(string)] == string and not isInExcludeRange(i):
            result.append(new_string)
            i += len(string)  # Skip past the replaced target
        else:
            result.append(replaced_command[i])
            i += 1

    return ''.join(result)


def updateCommandTask(task_list):
    update_log = []
    for task in task_list:
        task_config = task_configs_temp.copy()
        task_config['taskname'] = task['name']
        response_task = getTaskAPI(task_config)
        if response_task.status_code != 200:
            continue
        task_data = response_task.json()
        
        if task_data['type'] in TASK_TYPE_LIST:
            if task_data['type'] == "taskFileMonitor":
                text_to_replace = task_data['fileName']
            elif task_data['type'] == "taskUniversal":
                text_to_replace = task_data['largeTextField1']['value']
            else:
                text_to_replace = None
        else:
            continue
        replaced_text = text_to_replace
        have_task_update = False
        
        
        for operation in operation_pairs:
            char = operation['char']
            new_char = operation['new_char']
            active_condition = operation['active_condition']
            exclude_pairs = operation['exclude_pairs']
            update_text = False
            
            if not active_condition:
                update_text= True
            else:
                update_text = all(task_data.get(key) == value for key, value in active_condition.items())
            
            if text_to_replace and update_text:
                if char in text_to_replace:
                    replaced_text = replaceCommand(replaced_text, new_char, char, exclude_pairs)
                    replaced_text = replaceCommand(replaced_text, char, new_char, exclude_pairs)
                    have_task_update = True
                    
        if not have_task_update:
            update_log.append({
                "taskname": task['name'],
                "message": "No any target char in command"
            })
            continue
        
        if task_data['type'] == "taskFileMonitor":
            task_data['fileName'] = replaced_text
        elif task_data['type'] == "taskUniversal":
            task_data['largeTextField1']['value'] = replaced_text
        
        response_update = updateTaskAPI(task_data)
        if response_update.status_code == 200:
            update_log.append({
                "taskname": task['name'],
                "message": "Command updated"
            })
        else:
            update_log.append({
                "taskname": task['name'],
                "error": f"{response_update.status_code} - {response_update.text}"
            })
    
                
    return update_log


def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.226']
    updateURI(domain)
    
    task_list = getTaskList()
    print(len(task_list))
    if not task_list:
        print("No task found.")
    else:
        update_log = updateCommandTask(task_list)
        print(json.dumps(update_log, indent=4))
        createJson(JSON_OUTPUT_FILE, update_log)
        df_log = pd.DataFrame(update_log)
        createExcel(EXCEL_OUTPUT_FILE, (EXCEL_OUTPUT_SHEET, df_log))


        
if __name__ == '__main__':
    main()
