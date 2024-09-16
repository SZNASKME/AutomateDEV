import http

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateURI, updateAuth, getListTaskAdvancedAPI, createVariableAPI, createTaskAPI, updateTaskAPI
from utils.loadFile import loadJson

TASK_MONITOR_SUBFIX = '-TM'
VARIABLE_SUBFIX = '_ST_FLAG'
VARIABLE_MONITOR_SUBFIX = '-VM'

OUTPUT_FILE = 'Excel_API.xlsx'


task_adv_configs = {
    'taskname': '*',
    'type': 12,
    'businessServices': 'A0417 - AML MANAGEMENT SYSTEM',
    #'updatedTime': '-100d',
}


################################################################

def getData():
    
    response = getListTaskAdvancedAPI()
        
    status = http.HTTPStatus(response.status_code)
    print(f"{response.status_code} - {status.phrase}: {status.description}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

############################################################
#def createDataFrame(API_data):
#    if API_data:
#        columns = list(API_data[0].keys())
#        try:
#            return pd.DataFrame(API_data, columns=columns)
#        except Exception as e:
#            print(f"Error converting JSON to DataFrame: {e}")
#            return None
#    else:
#        return None 
############################################################

def getVariableNameCustomTrim(source_str, trim_str, replace_str):
    new_str = source_str.replace(trim_str, replace_str)
    new_str = new_str.strip()
    new_str = new_str.replace('.', '_')
    return new_str

def getTaskNameCustomTrim(source_str, trim_str):
    new_str = source_str.replace(trim_str, '')
    new_str = new_str.strip()
    return new_str

def getTaskData(data, task_name):
    for value in data:
        if value['name'] == task_name:
            return value
    return None


################################################################



def createVariable(data):
    successful_count = 0
    number_of_variable = 0
    for value in data:
        #print(value['opswiseGroups'])
        if value['name'].find(TASK_MONITOR_SUBFIX) != -1:
            number_of_variable += 1
            name = getVariableNameCustomTrim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
            json_data = {
                "name": name,
                "opswiseGroups": value['opswiseGroups'],
                "value": "success",
            }
            #print(json_data)
            response = createVariableAPI(json_data)
            status = http.HTTPStatus(response.status_code)
            if response.status_code == 200:
                successful_count += 1
            print(f"{response.status_code} - {status.phrase}: {status.description}")
    print(f"Number of successful variable creation: {successful_count} / {number_of_variable}\n")
    return None


def createVariableMonitor(data):
    successful_count = 0
    number_of_task = 0
    for value in data:
        if value['name'].find(TASK_MONITOR_SUBFIX) != -1:
            number_of_task += 1
            task_name = getVariableNameCustomTrim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_MONITOR_SUBFIX)
            var_name = getVariableNameCustomTrim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
            json_data = {
                "type": "taskVariableMonitor",
                "name": task_name,
                "opswiseGroups": value['opswiseGroups'],
                "valueMonitorType": 3,
                "variableName": var_name,
                "value": "success",
            }
            #print(json_data)
            response = createTaskAPI(json_data)
            status = http.HTTPStatus(response.status_code)
            if response.status_code == 200:
                successful_count += 1
            print(f"{response.status_code} - {status.phrase}: {status.description}")
    print(f"Number of successful task creation: {successful_count} / {number_of_task}\n")
    return None


def addActionToTask(data):
    number_of_task = 0
    successful_count = 0
    for value in data:
        if value['name'].find(TASK_MONITOR_SUBFIX) != -1:
            number_of_task += 1
            task_data = getTaskData(data, value['taskMonName'])
            var_name = getVariableNameCustomTrim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
            task_data["actions"]["setVariableActions"] = [
                {
                    "notificationOption": "Operation Failure",
                    "status": "Defined",
                    "variableName": var_name,
                    "variableScope": "Global",
                    "variableValue": "running"
                },
                {
                    "notificationOption": "Operation Failure",
                    "status": "Finished,\nSuccess",
                    "variableName": var_name,
                    "variableScope": "Global",
                    "variableValue": "success"
                }
            ]
            response = updateTaskAPI(task_data)
            status = http.HTTPStatus(response.status_code)
            if response.status_code == 200:
                successful_count += 1
            print(f"{response.status_code} - {status.phrase}: {status.description}")
    print(f"Number of task to be updated: {successful_count} / {number_of_task}\n")
    
    return None

#def addTaskInWorkflow(data):
#    
#    for value in data:
#        if value['name'].find(TASK_MONITOR_SUBFIX) != -1:
            
    

################################################################
        
def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = "http://172.16.1.161:8080/uc/resources"
    updateURI(domain)
    #APIdata = getData()
    #print("Number of Response:",len(APIdata),"\n")
    print("create variable")
    #createVariable(APIdata)
    print("create variable monitor")
    #createVariableMonitor(APIdata)
    print("add action to task")
    #addActionToTask(APIdata)






if __name__ == "__main__":
    main()