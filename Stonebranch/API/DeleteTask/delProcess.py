import json
import math
import ast
import multiprocessing
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel, selectSheet
from utils.stbAPI import deleteTaskAPI, deleteTriggerAPI, updateTaskAPI, getTaskAPI, updateURI, updateAuth
from Stonebranch.utils.readFile import loadJson
task_configs_temp = {
   'taskid': None,
   #'taskname': None,
}

trigger_configs_temp = {
    'triggerid': None,
    #'triggername': None,
}


##########################################################################################

def delTask(df, num_process = 4):
    if df.empty:
        return {
            "200": 0,
            "403": [],
            "404": []
        }
    count = multiprocessing.Value('i', 0)
    success = 0
    cannot_delete = []
    not_found = []
    task_configs_list = addDataToConfigs(df, task_configs_temp, col_name = 'taskid', df_col_name = 'sysId')
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_task:
        result_task = pool_task.map(deleteTaskAPI, task_configs_list)
    
    pool_task.close()
    pool_task.join()
    
    for res in result_task:
        if res.status_code == 200:
            success += 1
        if res.status_code == 403:
            cannot_delete.append(res.text)
        if res.status_code == 404:
            not_found.append(res.text)
            
    return {
        "200": success,
        "403": cannot_delete,
        "404": not_found
    }
        

def delTrigger(df, num_process = 4):
    if df.empty:
        return {
            "200": 0,
            "403": [],
            "404": []
        }
    count = multiprocessing.Value('i', 0)
    success = 0
    cannot_delete = []
    not_found = []
    trigger_configs_list = addDataToConfigs(df, trigger_configs_temp, col_name = 'triggerid', df_col_name = 'sysId')
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_trigger:
        result_trigger = pool_trigger.map(deleteTriggerAPI, trigger_configs_list)
    
    pool_trigger.close()
    pool_trigger.join()
    
    for res in result_trigger:
        if res.status_code == 200:
            success += 1
        if res.status_code == 403:
            cannot_delete.append(res.text)
        if res.status_code == 404:
            not_found.append(res.text)
            
    return {
        "200": success,
        "403": cannot_delete,
        "404": not_found
    }


def updateEmptyWorkflow(df, num_process = 4):
    if df.empty:
        return {
            "200": 0,
            "403": [],
            "404": []
        }
    dfworkflow = df[df['type'] == 'Workflow']
    count = multiprocessing.Value('i', 0)
    success = 0
    cannot_delete = []
    not_found = []
    workflow_configs_list = []
    for index, row in dfworkflow.iterrows():
        task_id = row['sysId']
        response_workflow = getTaskAPI({'taskid': task_id})
        if response_workflow.status_code == 200:
            workflow = response_workflow.json()
            task_configs = getConfigs(workflow)
            task_configs['runCriteria']= []
            task_configs['workflowEdges'] = []
            task_configs['workflowVertices'] = []
            workflow_configs_list.append(task_configs)
        
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_workflow:
        result_workflow = pool_workflow.map(updateTaskAPI, workflow_configs_list)
        
    pool_workflow.close()
    pool_workflow.join()
    
    for res in result_workflow:
        if res.status_code == 200:
            success += 1
        if res.status_code == 403:
            cannot_delete.append(res.text)
        if res.status_code == 404:
            not_found.append(res.text)
            
    return {
        "200": success,
        "403": cannot_delete,
        "404": not_found
    }

##########################################################################################

def initializer(cnt):
    global count
    count = cnt

def getListExcel(df, col_name = 'jobName'):
    del_list = []
    for index, row in df.iterrows():
        del_list.append(row[col_name])
    return del_list


def cleanValueDataFrame(value):
    if isinstance(value, str):
        if value.startswith("{") and value.endswith("}") or value.startswith("[") and value.endswith("]"):
            return ast.literal_eval(value)
        else:
            return value.strip()
    elif isinstance(value, float) and math.isnan(value):
        return None
    elif isinstance(value, float):
        return int(value)
    else:
        return value

def getConfigs(row):
    new_dict = {}
    for key in row.keys():
        value = cleanValueDataFrame(row[key])
        new_dict[key] = value
    return new_dict

def addDataToConfigs(dataframe, configs, col_name = 'name', df_col_name = 'name'):
    new_list = []
    for index, data in dataframe.iterrows():
        new_configs = configs.copy()
        new_configs[col_name] = data[df_col_name]
        new_list.append(new_configs)
    return new_list
    
    
##########################################################################################

def viewResult(result_dict):
    print("Enter status code (200,403,404) to view result")
    choice = input()
    if choice == '200':
        for key_res, res in result_dict.items():
            for key_value, value in res.items():
                if key_value == '200':
                    print(key_res)
                    print(json.dumps(value, indent = 4))
    if choice == '403':
        for key_res, res in result_dict.items():
            for key_value, value in res.items():
                if key_value == '403':
                    print(key_res)
                    print(json.dumps(value, indent = 4))
    if choice == '404':
        for key_res, res in result_dict.items():
            for key_value, value in res.items():
                if key_value == '404':
                    print(key_res)
                    print(json.dumps(value, indent = 4))


def countResult(result_dict):
    _200 = 0
    _403 = 0
    _404 = 0
    for key_res, res in result_dict.items():
        for key_value, value in res.items():
            if key_value == '200':
                _200 += 1
            if key_value == '403':
                _403 += 1
            if key_value == '404':
                _404 += 1
    print(f"200: {_200}")
    print(f"403: {_403}")
    print(f"404: {_404}")


def deleteProcess(dftask_dict, dftrigger):
    print("Delete Process ...")
    
    print("Delete Trigger ...")
    result_trigger = delTrigger(dftrigger)
    print("Empty Workflow ...")
    result_empty_workflow = updateEmptyWorkflow(dftask_dict['Workflow'])

    print("Delete File Monitor ...")
    result_file_monitor = delTask(dftask_dict['Agent File Monitor'])
    print("Delete Remote Monitor ...")
    result_remote_monitor = delTask(dftask_dict['Remote File Monitor'])
    print("Delete Task Monitor ...")
    result_task_monitor = delTask(dftask_dict['Task Monitor'])
    print("Delete System Monitor ...")
    result_system_monitor = delTask(dftask_dict['System Monitor'])
    print("Delete Variable Monitor ...")
    result_variable_monitor = delTask(dftask_dict['Variable Monitor'])
    print("Delete Email Monitor ...")
    result_email_monitor = delTask(dftask_dict['Email Monitor'])
    print("Delete Universal Monitor ...")
    result_universal_monitor = delTask(dftask_dict['Universal Monitor'])
    
    print("Delete Timer Task ...")
    result_timer_task = delTask(dftask_dict['Timer'])
    print("Delete Windows Task ...")
    result_window = delTask(dftask_dict['Windows'])
    print("Delete Linux Unix Task ...")
    result_linux = delTask(dftask_dict['Linux Unix'])
    print("Delete zOS Task ...")
    result_zos = delTask(dftask_dict['zOS'])
    print("Delete Manual Task ...")
    result_manual = delTask(dftask_dict['Manual'])
    print("Delete Email Task ...")
    result_email = delTask(dftask_dict['Email'])
    print("Delete File Transfer Task ...")
    result_file_transfer = delTask(dftask_dict['File Transfer'])
    print("Delete SQL Task ...")
    result_sql = delTask(dftask_dict['SQL'])
    print("Delete Stored Procedure Task ...")
    result_stored = delTask(dftask_dict['Stored Procedure'])
    print("Delete Application Control Task ...")
    result_appcontrol = delTask(dftask_dict['Application Control'])
    print("Delete SAP Task ...")
    result_sap = delTask(dftask_dict['SAP'])
    print("Delete Web Service Task ...")
    result_webservice = delTask(dftask_dict['Web Service'])
    print("Delete PeopleSoft Task ...")
    result_peoplesoft = delTask(dftask_dict['PeopleSoft'])
    print("Delete Recurring Task ...")
    result_recurring = delTask(dftask_dict['Recurring'])
    print("Delete Universal Task ...")
    result_universal_task = delTask(dftask_dict['Universal'])

    print("Delete Workflow Task ...")
    result_workflow = delTask(dftask_dict['Workflow'])

    print("Complete Process ...")
    result = {
        'Trigger': result_trigger,
        'Empty Workflow': result_empty_workflow,
        'Agent File Monitor': result_file_monitor,
        'Remote File Monitor': result_remote_monitor,
        'Task Monitor': result_task_monitor,
        'System Monitor': result_system_monitor,
        'Variable Monitor': result_variable_monitor,
        'Email Monitor': result_email_monitor,
        'Universal Monitor': result_universal_monitor,
        'Timer': result_timer_task,
        'Windows': result_window,
        'Linux Unix': result_linux,
        'zOS': result_zos,
        'Manual': result_manual,
        'Email': result_email,
        'File Transfer': result_file_transfer,
        'SQL': result_sql,
        'Stored Procedure': result_stored,
        'Application Control': result_appcontrol,
        'SAP': result_sap,
        'Web Service': result_webservice,
        'PeopleSoft': result_peoplesoft,
        'Recurring': result_recurring,
        'Universal': result_universal_task,
        'Workflow': result_workflow,
    }
    countResult(result)
    viewResult(result)
    
def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    
    
    df = getDataExcel()
    dfworkflow = selectSheet(df, 'Workflow')
    dftimer = selectSheet(df, 'Timer')
    dfwindow = selectSheet(df, 'Windows')
    dflinux = selectSheet(df, 'Linux Unix')
    dfzos = selectSheet(df, 'zOS')
    dffilemonitor = selectSheet(df, 'Agent File Monitor')
    dfmanual = selectSheet(df, 'Manual')
    dfemail = selectSheet(df, 'Email')
    dffiletransfer = selectSheet(df, 'File Transfer')
    dfsql = selectSheet(df, 'SQL')
    dfremote = selectSheet(df, 'Remote File Monitor')
    dfmonitor = selectSheet(df, 'Task Monitor')
    dfstored = selectSheet(df, 'Stored Procedure')
    dfuniversal = selectSheet(df, 'Universal Command')
    dfsystem = selectSheet(df, 'System Monitor')
    dfappcontrol = selectSheet(df, 'Application Control')
    dfsap = selectSheet(df, 'SAP')
    dfvariable = selectSheet(df, 'Variable Monitor')
    dfwebservice = selectSheet(df, 'Web Service')
    dfemailmonitor = selectSheet(df, 'Email Monitor')
    dfpeople = selectSheet(df, 'PeopleSoft')
    dfrecurring = selectSheet(df, 'Recurring')
    dfuniversalmonitor = selectSheet(df, 'Universal Monitor')
    dfuniversal = selectSheet(df, 'Universal')
    
    dftask_dict = {
        'Workflow': dfworkflow,
        'Timer': dftimer,
        'Windows': dfwindow,
        'Linux Unix': dflinux,
        'zOS': dfzos,
        'Agent File Monitor': dffilemonitor,
        'Manual': dfmanual,
        'Email': dfemail,
        'File Transfer': dffiletransfer,
        'SQL': dfsql,
        'Remote File Monitor': dfremote,
        'Task Monitor': dfmonitor,
        'Stored Procedure': dfstored,
        'Universal Command': dfuniversal,
        'System Monitor': dfsystem,
        'Application Control': dfappcontrol,
        'SAP': dfsap,
        'Variable Monitor': dfvariable,
        'Web Service': dfwebservice,
        'Email Monitor': dfemailmonitor,
        'PeopleSoft': dfpeople,
        'Recurring': dfrecurring,
        'Universal Monitor': dfuniversalmonitor,
        'Universal': dfuniversal,
    }
    dftrigger = selectSheet(df, 'Trigger')
    deleteProcess(dftask_dict, dftrigger)
    
    
if __name__ == '__main__':
    main()