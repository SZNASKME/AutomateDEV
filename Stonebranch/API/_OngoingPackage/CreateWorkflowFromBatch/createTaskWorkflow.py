import sys
import os
import copy
import json
import pandas as pd
from pathlib import Path



sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


from utils.stbAPI import *
from utils.readFile import loadJson
from utils.readExcel import getDataSheetMultiExcelFile
from utils.createFile import createExcel

AVAILABLE_SHEETNAME_DATA = 'available_sheetname_data'
OUTPUT_EXCEL_FILE = 'CreateWorkflowFromBatch_Output_Log_Dumb.xlsx'
WORKFLOW_SHEET = 'Workflow_Creation_Log'
TASK_SHEET = 'Task_Creation_Log'
EDIT_TASK_SHEET = 'Edit_Task_to_Workflow_Log'
WORKFLOWLIST_SHEET = 'Workflow_List'
TASKLIST_SHEET = 'Task_List'

CREATE_WORKFLOW_FLAG = False
CREATE_TASK_FLAG = False
EDIT_TASK_TO_WORKFLOW_FLAG = False

CREATE_WINDOWS_TASK_FLAG = True
CREATE_FTP_TASK_FLAG = True
CREATE_UNIVERSAL_TASK_FLAG = True
CREATE_TIMER_TASK_FLAG = True

WORKFLOW_COLUMN = 'workflow'
HOSTNAME_COLUMN = 'hostname'
TASKNAME_COLUMN = 'jobname'
TASKTYPE_COLUMN = 'jobtype'

WINDOWSTASK_TYPE = 'CMD'
FTPTASK_TYPE = 'FTP'
GNUPGTASK_TYPE = 'GNUPG'
TIMERTASK_TYPE = 'Timer'

FILTER_SHEET_NAME = 'Main'
FILTER_COLUMN = "use_not_use"
FILTER_VALUE = 'Use'
RENAME_COLUMN = 'use / not use'


SUFFIX_WORKFLOW_NAME = 'WF'

workflow_configs_temp = {
    'name': None,
    'type': 'taskWorkflow',
}

task_configs_temp = {
    'name': None,
    'type': None,
}

get_task_configs_temp = {
    'taskname': None
}

list_task_configs_temp = {
    'name': None
}

depen_configs_temp = {
    "condition": {
        "value": "Success"
    },
    "sourceId": {
        "taskName": None,
        "value": None
    },
    "targetId": {
        "taskName": None,
        "value": None
    }
}

vertex_configs_temp = {
    "alias": None,
    "task":{
        "value": None
    },
    "vertexX": None,
    "vertexY": None,
}


#############################################################################################################

def iterFileSheetDF(dfs_sheet):
    for file_name, v in (dfs_sheet or {}).items():
        # Case 1: already a DataFrame
        if hasattr(v, "columns"):
            yield file_name, None, v
            continue

        # Case 2: dict of sheets -> DataFrame
        if isinstance(v, dict):
            for sheet_name, df in v.items():
                yield file_name, sheet_name, df
            continue

        raise TypeError(f"Unsupported dfs_sheet structure at key={file_name!r}: {type(v)}")

def prepareWorkflowList(dfs_sheet):
    workflow_list_dict = {}
    for file_name, sheet_name, df in iterFileSheetDF(dfs_sheet):
        if sheet_name != FILTER_SHEET_NAME:
            continue
        hostname = os.path.splitext(os.path.basename(file_name))[0]
        
        #df.columns = df.columns.str.lower()
        df_duplicates_removed = df.drop_duplicates(subset=[WORKFLOW_COLUMN, FILTER_COLUMN])
        df = df_duplicates_removed.reset_index(drop=True)
        for row in df.itertuples(index=False):
            workflow_name = getattr(row, WORKFLOW_COLUMN).replace('&', '_')
            filter_flag = getattr(row, FILTER_COLUMN)
            #print('Workflow Name:', workflow_name, 'Filter:', filter_flag)
            if filter_flag == FILTER_VALUE:
                if workflow_name not in workflow_list_dict:
                    workflow_list_dict[workflow_name] = []
                workflow_list_dict[workflow_name].append({
                    'host': hostname, 
                    'sheet': sheet_name,
                    'data': row
                })
    return workflow_list_dict


def prepareTaskList(dfs_sheet):
    task_list_dict = {}
    for file_name, sheet_name, df in iterFileSheetDF(dfs_sheet):
        if sheet_name != FILTER_SHEET_NAME:
            continue

        hostname = os.path.splitext(os.path.basename(file_name))[0]
        #if not duplicated_task.empty:
            #print(f'Duplicate task names found in file {file_name}:')
            #print(duplicated_task[[TASKNAME_COLUMN]])
        #df.columns = df.columns.str.lower()
        df_duplicates_removed = df.drop_duplicates(subset=[TASKNAME_COLUMN, FILTER_COLUMN])
        df = df_duplicates_removed.reset_index(drop=True)
        for row in df.itertuples(index=False):
            task_name = getattr(row, TASKNAME_COLUMN).replace('&', '_')
            workflow = getattr(row, WORKFLOW_COLUMN).replace('&', '_')
            filter_flag = getattr(row, FILTER_COLUMN)
            if filter_flag == FILTER_VALUE:
                if task_name not in task_list_dict:
                    task_list_dict[task_name] = []
                task_list_dict[task_name].append({
                    'host': hostname, 
                    'workflow': workflow, 
                    'sheet': sheet_name, 
                    'data': row
                })
    return task_list_dict


def prepareTaskDataSheet(dfs_sheet, configs_file):
    task_data_dict = {}
    for file_name, sheet_name, df in iterFileSheetDF(dfs_sheet):
        if sheet_name != FILTER_SHEET_NAME and sheet_name in configs_file[AVAILABLE_SHEETNAME_DATA]:
            hostname = os.path.splitext(os.path.basename(file_name))[0]
            #df.columns = df.columns.str.lower()
            for row in df.itertuples(index=False):
                task_name = getattr(row, TASKNAME_COLUMN).replace('&', '_')
                if task_name not in task_data_dict:
                    task_data_dict[task_name] = []
                task_data_dict[task_name].append({
                    'host': hostname, 
                    'sheet': sheet_name, 
                    'data': row
                })
    return task_data_dict

############################################################################################################

def checkIgnoreCaseName(string, list):
    if string.lower() in (name.lower() for name in list if name != string):
        return True 
    return False

def selectDataRow(data_list, sheet_name, host):
    for item in data_list:
        if item['sheet'] == sheet_name and item['host'] == host:
            return item['data']
    return None
    
def countNumberOfWorkflows(workflow_name, workflow_dict):
        #print(workflow_dict[workflow_name])
        workflow_count = len(workflow_dict[workflow_name]) if workflow_name in workflow_dict else 0
        return workflow_count


def createWorkflowFromBatch(workflow_list_dict, configs_file):
    
    def prepareWorkflowConfigs(name, data):
        workflow_configs = workflow_configs_temp.copy()
        workflow_configs['name'] = name
        # Add more configurations based on data if needed
        return workflow_configs

    workflow_list_configs = []
    workflow_name_list = []
    print('\nPreparing Workflows to be created...')
    for workflow_name, data_list in workflow_list_dict.items():
        if len(data_list) > 1 or checkIgnoreCaseName(workflow_name, workflow_list_dict.keys()):
            
            for item in data_list:
                host = item['host']
                data = item['data']
                new_workflow_name = f"{workflow_name}_{host}_{SUFFIX_WORKFLOW_NAME}"
                workflow_configs = prepareWorkflowConfigs(new_workflow_name, data)
                workflow_list_configs.append(workflow_configs)
                workflow_name_list.append({
                    'workflow_name': new_workflow_name,
                    'host': host,
                })
        else:
            data = data_list[0]['data']
            new_workflow_name = f"{workflow_name}_{SUFFIX_WORKFLOW_NAME}"
            workflow_configs = prepareWorkflowConfigs(new_workflow_name, data)
            workflow_list_configs.append(workflow_configs)
            workflow_name_list.append({
                'workflow_name': new_workflow_name,
                'host': data_list[0]['host'],
            })
    print(f'Total Workflows to be created: {len(workflow_list_configs)}')
    workflow_created_log = []

    for workflow_configs in workflow_list_configs:
        if CREATE_WORKFLOW_FLAG:
            response = createTaskAPI(workflow_configs)
            if response.status_code == 200:
                print(f"Workflow '{workflow_configs['name']}' created successfully.")
                workflow_created_log.append({
                    'Workflow Name': workflow_configs['name'],
                    'Status': 'Created Successfully',
                    'Configuration': workflow_configs
                })
            else:
                print(f"Error creating workflow '{workflow_configs['name']}': {response.text}")
                workflow_created_log.append({
                    'Workflow Name': workflow_configs['name'],
                    'Status': f'Error: {response.text}',
                    'Configuration': workflow_configs
                })
        else:
            workflow_created_log.append({
                'Workflow Name': workflow_configs['name'],
                'Status': 'Creation Skipped (CREATE_WORKFLOW_FLAG is False)',
                'Configuration': workflow_configs
            })
    if not CREATE_WORKFLOW_FLAG:
        print('CREATE_WORKFLOW_FLAG is set to False. No workflows were created.')

    df_workflow_created_log = pd.DataFrame(workflow_created_log)
    df_workflow_name_list = pd.DataFrame(workflow_name_list)
    return df_workflow_created_log, df_workflow_name_list


def createTaskFromBatch(task_list_dict, task_data_dict, workflow_list_dict , configs_file):
    
    def mapTaskName(name, host, taskname_dict):
        taskname_list = taskname_dict.get(name, [])
        
        for item in taskname_list:
            if item['host'] == host:
                return item['new_task_name'], item['new_workflow_name']
        return name , None
    
    def createOputPath(input_path):
        output_path = Path(input_path).parent
        output_path = str(output_path)
        return output_path
    
    def prepareWindowsTaskConfigs(task_configs, data):
        task_configs['type'] = 'taskWindows'
        command = getattr(data, 'command', '')
        command = command.replace("\"%SUBFILENAME%\"", "${_date('YYYY-MM-dd')}")
        task_configs['command'] = command
        task_configs['exitCodes'] = 0
        
        return task_configs
        
    
    def prepareFTPTaskConfigs(task_configs, data):
        task_configs['type'] = 'taskFtp'
        task_configs['serverType'] = getattr(data, 'protocol', '')
        task_configs['command'] = getattr(data, 'command', '')
        task_configs['remoteServer'] = getattr(data, 'remoteserver', '')
        if getattr(data, 'command', '') == 'DELETE' or getattr(data, 'command', '') == 'MDELETE':
            task_configs['localFilename'] = "${EMPTY_FILE}"
            task_configs['remoteFilename'] = getattr(data, 'sourcepath', '')
        else:
            task_configs['localFilename'] = getattr(data, 'sourcepath', '')
            task_configs['remoteFilename'] = getattr(data, 'despath', '')
        
        task_configs['remoteCredVar'] = '${REMOTE_SERVER_CREDENTIAL}'
        task_configs['move'] = True if getattr(data, 'move', '').strip().lower() == 'y' else False
        task_configs['exitCodes'] = 0
        
        
        return task_configs

    def prepareTimerTaskConfigs(task_configs, data):
        task_configs.pop('agentVar', None)
        task_configs['type'] = 'taskSleep'
        task_configs['sleepType'] = 'Seconds'
        task_configs['sleepAmount'] = getattr(data, 'duration', '')
        
        return task_configs
    
    def prepareGNUPGTaskConfigs(task_configs, data):
        task_configs['type'] = 'taskUniversal'
        task_configs['actions'] = {
            "abortActions" : [],
            "emailNotifications" : [],
            "setVariableActions" : [],
            "snmpNotifications" : [],
            "systemOperations" : []
        }
        task_configs['template'] = "GnuPG-AskMe"
        task_configs['textField1'] = {
            "label" : "GPG Home",
            "name" : "gpg_home",
            "value" : "{GPG_HOME}"
        }
        task_configs['textField6'] = {
            "label" : "Input Path or Pattern",
            "name" : "input_path",
            "value" : getattr(data, 'sourcefile', '')
        }
        task_configs['textField3'] = {
            "label" : "Output Path",
            "name" : "output_path",
            "value" : getattr(data, 'desfile', '') if getattr(data, 'desfile', '') != '' else createOputPath(getattr(data, 'sourcefile', ''))
        }
        task_configs['choiceField5'] = {
            "label" : "File Extension",
            "name" : "file_extension",
            "value" : ".gpg (GNUPG)"
        }
        task_configs['booleanField5'] = {
            "label" : "Overwrite Output Files",
            "name" : "overwrite_output_files",
            "value" : True
        }
        method = getattr(data, 'method', '').strip().lower()
        if method == 'encrypt':
            task_configs['choiceField1'] =  {
                "label" : "Action",
                "name" : "action",
                "value" : "Encrypt With Local Keystore"
            }
            task_configs["choiceField4"] = {
                "label" : "Local Certificates",
                "name" : "local_key",
                "value" : "{GPG_LOCAL_CERTIFICATES}"
            }
        elif method == 'decrypt':
            task_configs['choiceField1'] =  {
                "label" : "Action",
                "name" : "action",
                "value" : "Decrypt With Local Keystore"
            }
            task_configs["credentialVarField1"] = {
                "label" : "Name & Passphrase",
                "name" : "passphrase_key",
                "value" : "{GPG_PASSPHRASE_KEY}"
            }
        else:
            print(f'Unknown GNUPG method "{method}" for task "{task_configs["name"]}". Skipping GNUPG task creation.')


        task_configs['exitCodes'] = 0
            
        
        return task_configs
    
    def prepareTaskConfigs(name, host, data, task_data_dict):
        task_configs = task_configs_temp.copy()
        
        new_task_name, new_workflow_name = mapTaskName(name, host, taskname_dict)
        task_configs['name'] = new_task_name
        task_configs['agentVar'] = '${' + host + '}'
        
        
        task_type = getattr(data, TASKTYPE_COLUMN, '').strip()
        
        #print(f'Preparing task "{name}" of type "{task_type}" on host "{host}" for workflow "{workflow}".')
        if task_type == WINDOWSTASK_TYPE:
            command = getattr(data, 'command', '')
            if pd.isna(command) or command.strip() == '':
                print(f'No command found for task "{name}" on host "{host}". Skipping task creation.')
                return None
            if command.lower() in [cmd.lower() for cmd in configs_file.get('except_command', [])]:
                print(f'Skipping task "{name}" on host "{host}" due to excepted command "{command}".')
                return None
            if any(command.lower().startswith(prefix.lower()) for prefix in configs_file.get('except_startwith_command', [])):
                print(f'Skipping task "{name}" on host "{host}" due to excepted command prefix "{command}".')
                return None
            task_configs.update(prepareWindowsTaskConfigs(task_configs, data))
        elif task_type == FTPTASK_TYPE:
            data_list = task_data_dict.get(name, [])
            task_ftp_data_row = selectDataRow(data_list, 'FTP', host)
            if task_ftp_data_row:
                data = task_ftp_data_row
            task_configs.update(prepareFTPTaskConfigs(task_configs, data))
        elif task_type == TIMERTASK_TYPE:
            data_list = task_data_dict.get(name, [])
            task_timer_data_row = selectDataRow(data_list, 'Timer', host)
            if task_timer_data_row:
                data = task_timer_data_row
            task_configs.update(prepareTimerTaskConfigs(task_configs, data))
        elif task_type == GNUPGTASK_TYPE:
            data_list = task_data_dict.get(name, [])
            task_gnupg_data_row = selectDataRow(data_list, 'GNUPG', host)
            if task_gnupg_data_row:
                data = task_gnupg_data_row
            task_configs.update(prepareGNUPGTaskConfigs(task_configs, data))
        else:
            print(f'Unknown task type "{task_type}" for task "{name}". Skipping task creation.')
        
        return task_configs
    

    
    taskname_dict = {}
    task_list_configs = []
    task_created_log = []
    task_name_list = []
    workflow_list = list(workflow_list_dict.keys())
    for task_name, data_list in task_list_dict.items():
        for item in data_list:
            host = item['host']
            workflow = item['workflow']
            data = item['data']
            
            new_task_name = task_name.replace(workflow,f"{workflow}_{host}") if countNumberOfWorkflows(workflow, workflow_list_dict) > 1 or checkIgnoreCaseName(workflow, workflow_list) else task_name
            new_workflow_name = f"{workflow}_{host}_{SUFFIX_WORKFLOW_NAME}" if countNumberOfWorkflows(workflow, workflow_list_dict) > 1 or checkIgnoreCaseName(workflow, workflow_list) else f"{workflow}_{SUFFIX_WORKFLOW_NAME}"
            if task_name not in taskname_dict:
                taskname_dict[task_name] = []
            taskname_dict[task_name].append({
                'host': host,
                'new_workflow_name': new_workflow_name,
                'new_task_name': new_task_name
            })
    
    for task_name, data_list in task_list_dict.items():
        for item in data_list:
            host = item['host']
            workflow = item['workflow']
            data = item['data']
            task_type = getattr(data, TASKTYPE_COLUMN, '').strip()
            if (task_type == WINDOWSTASK_TYPE and not CREATE_WINDOWS_TASK_FLAG) or \
               (task_type == FTPTASK_TYPE and not CREATE_FTP_TASK_FLAG) or \
                (task_type == TIMERTASK_TYPE and not CREATE_TIMER_TASK_FLAG) or \
                (task_type not in [WINDOWSTASK_TYPE, FTPTASK_TYPE, TIMERTASK_TYPE] and not CREATE_UNIVERSAL_TASK_FLAG):
                print(f'Skipping task "{task_name}" of type "{task_type}" on host "{host}".')
                task_created_log.append({
                    'Task Name': task_name,
                    'Status': f'Skipped (Type: {task_type})',
                    'Command': getattr(data, 'command', ''),
                    'Note': {}
                })
                continue
            
            

            task_configs = prepareTaskConfigs(task_name, host, data, task_data_dict)
            if task_configs:
                task_list_configs.append(task_configs)
                task_name, workflow_name = mapTaskName(task_name, host, taskname_dict)
                task_name_list.append({
                    'taskname': task_configs['name'],
                    'workflow': workflow_name,
                    'host': host
                })
            else:
                print(f'Skipping task "{task_name}" on host "{host}" due to empty configuration.')
                task_created_log.append({
                    'Task Name': task_name,
                    'Status': 'Skipped (Empty Configuration)',
                    'Command': getattr(data, 'command', ''),
                    'Note': {}
                })
    
    print(f'Total Tasks to be created: {len(task_list_configs)}')
    
    
    for task_configs in task_list_configs:
        if CREATE_TASK_FLAG:
            response = createTaskAPI(task_configs)
            if response.status_code == 200:
                print(f"Task '{task_configs['name']}' created successfully.")
                task_created_log.append({
                    'Task Name': task_configs['name'],
                    'Status': 'Created Successfully',
                    'Command': task_configs.get('command', ''),
                    'Note': task_configs
                })
            else:
                print(f"Error creating task '{task_configs['name']}': {response.text}")
                task_created_log.append({
                    'Task Name': task_configs['name'],
                    'Status': f'Error: {response.text}',
                    'Command': task_configs.get('command', ''),
                    'Note': task_configs
                })
        else:
            task_created_log.append({
                'Task Name': task_configs['name'],
                'Status': 'Creation Skipped (CREATE_TASK_FLAG is False)',
                'Command': task_configs.get('command', ''),
                'Note': task_configs
            })
    if not CREATE_TASK_FLAG:
        print('CREATE_TASK_FLAG is set to False. No tasks were created.')
    
    df_task_created_log = pd.DataFrame(task_created_log)
    df_task_name_list = pd.DataFrame(task_name_list)
    return df_task_created_log, df_task_name_list



def editTaskToWorkflow(task_list, workflow_list_dict, configs_file):
    
    def prepareVertexConfigsList(tasks, existing_task_names):
        vertex_configs_list = []
        vertex_id = 2
        vertex_id_increment = 1
        vertex_x = 0
        vertex_y = 0
        y_increment = 150

        cleaned_tasks = [task for task in tasks if task['taskname'] in existing_task_names]
        ordered_tasks = sorted(cleaned_tasks, key=lambda x: (x['sequence'] is None, x['sequence']))
       
        for task in ordered_tasks:
            vertex_configs = copy.deepcopy(vertex_configs_temp)
            vertex_configs['task']['value'] = task['taskname']
            vertex_configs['vertexId'] = vertex_id
            vertex_id += vertex_id_increment
            vertex_configs['vertexX'] = vertex_x
            vertex_configs['vertexY'] = vertex_y
            vertex_y += y_increment
            vertex_configs_list.append(vertex_configs)
        
        return vertex_configs_list
    
    def prepareEdgeConfigsList(vertex_configs_list):
        edge_configs_list = []
        for i in range(len(vertex_configs_list) - 1):
            edge_configs = {
                "sourceId": {
                    "taskName": vertex_configs_list[i]['task']['value'],
                    "value": vertex_configs_list[i]['vertexId']
                },
                "targetId": {
                    "taskName": vertex_configs_list[i + 1]['task']['value'],
                    "value": vertex_configs_list[i + 1]['vertexId']
                },
                "condition": {
                    "value": "Success"
                }
            }
            edge_configs_list.append(edge_configs)
        return edge_configs_list
    
    
    
    
    task_edit_log = []
    print('\nEditing Tasks to Workflows...')
    workflow_list = list(workflow_list_dict.keys())
    task_workflow_dict = {}
    for task_name, data_list in task_list.items():
        for item in data_list:
            host = item['host']
            workflow = item['workflow']
            data = item['data']
            
            new_task_name = task_name.replace(workflow,f"{workflow}_{host}") if countNumberOfWorkflows(workflow, workflow_list_dict) > 1 or checkIgnoreCaseName(workflow, workflow_list) else task_name
            new_workflow_name = f"{workflow}_{host}_{SUFFIX_WORKFLOW_NAME}" if countNumberOfWorkflows(workflow, workflow_list_dict) > 1 or checkIgnoreCaseName(workflow, workflow_list) else f"{workflow}_{SUFFIX_WORKFLOW_NAME}"
            
            task_type = getattr(data, TASKTYPE_COLUMN, '').strip()
            
            if task_type == WINDOWSTASK_TYPE:
                command = getattr(data, 'command', '')
                if pd.isna(command) or command.strip() == '':
                    task_edit_log.append({
                        'Task Name': new_task_name,
                        'Workflow Name': new_workflow_name,
                        'Status': 'Skipped (Empty Command)',
                        'Command': command,
                        'Note': {}
                    })
                    continue
                if command.lower() in [cmd.lower() for cmd in configs_file.get('except_command', [])]:
                    task_edit_log.append({
                        'Task Name': new_task_name,
                        'Workflow Name': new_workflow_name,
                        'Status': f'Skipped (Excepted Command: {command})',
                        'Command': command,
                        'Note': {}
                    })
                    continue
                if any(command.lower().startswith(prefix.lower()) for prefix in configs_file.get('except_startwith_command', [])):
                    task_edit_log.append({
                        'Task Name': new_task_name,
                        'Workflow Name': new_workflow_name,
                        'Status': f'Skipped (Excepted Command Prefix: {command})',
                        'Command': command,
                        'Note': {}
                    })
                    continue
                
            if new_workflow_name not in task_workflow_dict:
                task_workflow_dict[new_workflow_name] = []
            task_workflow_dict[new_workflow_name].append({
                'host': host,
                'workflow': new_workflow_name,
                'taskname': new_task_name,
                'sequence': getattr(data, 'sequence', None)
            })
            
    list_task_configs = list_task_configs_temp.copy()
    task_configs_list = getListTaskAPI(list_task_configs)
    existing_task_names = [task['name'] for task in task_configs_list.json()]
    ## edit tasks to workflow
    for workflow_name, tasks in task_workflow_dict.items():
        task_configs = get_task_configs_temp.copy()
        task_configs['taskname'] = workflow_name
        workflow_configs = getTaskAPI(task_configs)
        if workflow_configs.status_code != 200:
            print(f"Error retrieving workflow '{workflow_name}': {workflow_configs.text}")
            continue
        workflow_data = workflow_configs.json()
        
        #vexter_configs = workflow_data.get('workflowVertices', [])
        #edge_configs = workflow_data.get('workflowEdges', [])
        
        vertex_configs_list = prepareVertexConfigsList(tasks, existing_task_names)
        edge_configs_list = prepareEdgeConfigsList(vertex_configs_list)
        #print(json.dumps(vertex_configs_list, indent=4))
        #print(json.dumps(edge_configs_list, indent=4))
        workflow_data['workflowVertices'] = copy.deepcopy(vertex_configs_list)
        workflow_data['workflowEdges'] = copy.deepcopy(edge_configs_list)
        
        if EDIT_TASK_TO_WORKFLOW_FLAG:
            #print(json.dumps(workflow_data, indent=4))
            response = updateTaskAPI(workflow_data)
            if response.status_code == 200:
                print(f"Tasks edited to workflow '{workflow_name}' successfully.")
                task_edit_log.append({
                    'Workflow Name': workflow_name,
                    'Status': 'Tasks Edited Successfully',
                    'Tasks': [task['taskname'] for task in tasks],
                    'Note': workflow_data
                })
            else:
                print(f"Error editing tasks to workflow '{workflow_name}': {response.text}")
                task_edit_log.append({
                    'Workflow Name': workflow_name,
                    'Status': f'Error: {response.text}',
                    'Tasks': [task['taskname'] for task in tasks],
                    'Note': workflow_data
                })
        
    return pd.DataFrame(task_edit_log)
            
            

################################################################################################################

def renameColumnsInDfs(dfs_sheet):
    """
    Rename columns for both:
      - dfss[file] = DataFrame
      - dfss[file][sheet] = DataFrame
    Returns structure in the same shape as input.
    """
    renamed = {}

    for file_name, v in (dfs_sheet or {}).items():
        if hasattr(v, "columns"):
            df = v
            df.columns = df.columns.str.lower().str.strip()
            if RENAME_COLUMN in df.columns:
                df = df.rename(columns={RENAME_COLUMN: FILTER_COLUMN})
            
            renamed[file_name] = df
            continue

        if isinstance(v, dict):
            renamed[file_name] = {}
            for sheet_name, df in v.items():
                df.columns = df.columns.str.lower().str.strip()
                if RENAME_COLUMN in df.columns:
                    df = df.rename(columns={RENAME_COLUMN: FILTER_COLUMN})
                renamed[file_name][sheet_name] = df
            continue

        raise TypeError(f"Unsupported dfss structure at key={file_name!r}: {type(v)}")

    return renamed

def replaceColumnsNaNWithEmptyString(dfs_sheet):
    """
    Replace NaN values with empty string for both:
      - dfss[file] = DataFrame
      - dfss[file][sheet] = DataFrame
    Returns structure in the same shape as input.
    """
    replaced = {}

    for file_name, v in (dfs_sheet or {}).items():
        if hasattr(v, "columns"):
            df = v.fillna('')
            replaced[file_name] = df
            continue

        if isinstance(v, dict):
            replaced[file_name] = {}
            for sheet_name, df in v.items():
                df = df.fillna('')
                replaced[file_name][sheet_name] = df
            continue

        raise TypeError(f"Unsupported dfss structure at key={file_name!r}: {type(v)}")

    return replaced



def checkUseCorrectly(dfs_sheet):
    error_list = []
    for file_name, sheet_name, df in iterFileSheetDF(dfs_sheet):
        where = f"{file_name}" + (f" | sheet={sheet_name}" if sheet_name else "")

        if FILTER_COLUMN not in df.columns:
            print(f'Error: {FILTER_COLUMN} column not found in {where}. Please ensure the column is present.')
            return False

        workflow_list = df[WORKFLOW_COLUMN].tolist()
        for workflow_name in workflow_list:
            key = (file_name, sheet_name, workflow_name)
            if key not in error_list:
                df_filtered = df[df[WORKFLOW_COLUMN] == workflow_name]
                use_values = df_filtered[FILTER_COLUMN].unique()
                if len(use_values) > 1:
                    print(
                        f'Error: Inconsistent {FILTER_COLUMN} values for workflow "{workflow_name}" in {where}. '
                        f'Please ensure all entries for the same workflow have the same {FILTER_COLUMN} value.'
                    )
                    error_list.append(key)

    if error_list:
        print('\nPlease correct the above errors before proceeding.')
        return False
    return True



def validateWorkflowDuplicate(workflow_list_dict):
    all_duplicated_workflow_names = []
    for workflow_name, data_list in workflow_list_dict.items():
        if len(data_list) > 1:
            #print(f'Duplicate workflow name found: {workflow_name}')
            all_duplicated_workflow_names.append({"workflow_name": workflow_name, "hosts": [item['host'] for item in data_list]})
            
    if all_duplicated_workflow_names == []:
        print('No duplicate workflow names found across all files.')
    else:
        print('\nDuplicate workflow names found. Please resolve before proceeding.')
        for workflow_name in all_duplicated_workflow_names:
            print(f'- {workflow_name["workflow_name"]} found in hosts: {", ".join(workflow_name["hosts"])}')

def validateTaskDuplicate(task_list_dict):
    all_duplicated_task_names = []
    for task_name, data_list in task_list_dict.items():
        if len(data_list) > 1:
            #print(f'Duplicate task name found: {task_name}')
            all_duplicated_task_names.append({"task_name": task_name, "hosts": [item['host'] for item in data_list]})           
    if all_duplicated_task_names == []:
        print('No duplicate task names found across all files.')
    else:
        print('\nDuplicate task names found. Please resolve before proceeding.')
        for task_name in all_duplicated_task_names:
            print(f'- {task_name["task_name"]} found in hosts: {", ".join(task_name["hosts"])}')


def printWorkflow(workflow_dict, count=False, detailed=False):
    
    if count:
        workflow_count = 0
        for workflow_name, data_list in workflow_dict.items():
            workflow_count += 1
        print(f'\nTotal Workflows to be created: {workflow_count}')
    if detailed:
        for workflow_name, data_list in workflow_dict.items():
            print(f'Workflow: {workflow_name}, Hosts: {", ".join([item["host"] for item in data_list])}')
    
def printTask(task_dict, count=False, detailed=False):
    if count:
        task_count = 0
        for task_name, data_list in task_dict.items():
            task_count += 1
        print(f'\nTotal Tasks to be created: {task_count}')
    if detailed:
        for task_name, data_list in task_dict.items():
            print(f'Task: {task_name}, Host: {", ".join([item["host"] for item in data_list])}')


def main():
    configs_file = loadJson('C:\\Dev\\AutomateDEV\\Stonebranch\\API\\_OngoingPackage\\CreateWorkflowFromBatch\\config\\configs.json')
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['1.227']
    updateURI(domain)
    
    dfs_sheet = getDataSheetMultiExcelFile(all_sheets=True)
    
    dfs_sheet = renameColumnsInDfs(dfs_sheet)
    
    #if not checkUseCorrectly(dfs_sheet):
    #    return
    dfs_sheet = replaceColumnsNaNWithEmptyString(dfs_sheet)
    
    workflow_list_dict = prepareWorkflowList(dfs_sheet)
    task_list_dict = prepareTaskList(dfs_sheet)
    task_data_dict = prepareTaskDataSheet(dfs_sheet, configs_file)
    #print(workflow_list_dict)
    #print(task_list_dict)
    #print(json.dumps(task_data_dict, indent=4))
    validateWorkflowDuplicate(workflow_list_dict)
    validateTaskDuplicate(task_list_dict)
    
    # printWorkflow(workflow_list_dict, count=True)
    # printTask(task_list_dict, count=True)
    
    print('\nWorkflow and Task lists prepared successfully.')
    print('Creating Workflows and Tasks...')
    
    df_workflow_created_log, df_workflow_name_list = createWorkflowFromBatch(workflow_list_dict, configs_file)
    df_task_created_log, df_task_name_list = createTaskFromBatch(task_list_dict, task_data_dict, workflow_list_dict, configs_file)
    
    df_edit_task_to_workflow_log = editTaskToWorkflow(task_list_dict, workflow_list_dict, configs_file)

    createExcel(OUTPUT_EXCEL_FILE, (WORKFLOW_SHEET, df_workflow_created_log), (TASK_SHEET, df_task_created_log), (EDIT_TASK_SHEET, df_edit_task_to_workflow_log), (WORKFLOWLIST_SHEET, df_workflow_name_list),(TASKLIST_SHEET, df_task_name_list))

if __name__ == "__main__":
    main()