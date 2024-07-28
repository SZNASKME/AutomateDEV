import requests
from requests.auth import HTTPBasicAuth
import http
import urllib.parse 

LIST_TASK_URI = "http://172.16.1.85:8080/uc/resources/task/list"
LIST_TASK_ADV_URI = "http://172.16.1.85:8080/uc/resources/task/listadv"
TASK_URI = "http://172.16.1.85:8080/uc/resources/task"
VARIABLE_URI = "http://172.16.1.85:8080/uc/resources/variable"

TASK_MONITOR_SUBFIX = '-TM'
VARIABLE_SUBFIX = '_ST_FLAG'
VARIABLE_MONITOR_SUBFIX = '-VM'

OUTPUT_FILE = 'Excel_API.xlsx'

task_configs = {
    'name': '*',
    'type':  12,
    'businessServices': 'A0417 - AML MANAGEMENT SYSTEM',
}

task_adv_configs = {
    'taskname': '*',
    #'type': 12,
    'businessServices': 'A0417 - AML MANAGEMENT SYSTEM',
    #'updatedTime': '-100d',
}


auth = HTTPBasicAuth('ops.admin','p@ssw0rd')

new_order = ['name', 'type', 'description','sysId','version']

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri


def getListTaskAPI():
    response = requests.post(url=LIST_TASK_URI, json = task_configs, auth=auth, headers={'Accept': 'application/json'})
    return response

def getListTaskAdvancedAPI():
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    #print(uri)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    return response


def createVariableMonitorAPI(variable_monitor_configs):
    response = requests.post(url = TASK_URI, json = variable_monitor_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def createVariableAPI(variable_configs):
    response = requests.post(url = VARIABLE_URI, json = variable_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def modifyTaskAPI(task_modify_configs_list):
    response = requests.put(url = TASK_URI, json = task_modify_configs_list, auth = auth, headers = {'Content-Type': 'application/json'})
    return response
    

################################################################

def getData(mode = 0):
    
    if mode == 0:
        response = getListTaskAPI()
    else:
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

def get_variable_name_custom_trim(source_str, trim_str, replace_str):
    new_str = source_str.replace(trim_str, replace_str)
    new_str = new_str.strip()
    new_str = new_str.replace('.', '_')
    return new_str

def get_task_name_custom_trim(source_str, trim_str):
    new_str = source_str.replace(trim_str, '')
    new_str = new_str.strip()
    return new_str

def get_task_data(data, task_name):
    for value in data:
        if value['name'] == task_name:
            return value
    return None


################################################################



def create_variable(data):
    successful_count = 0
    number_of_variable = 0
    for value in data:
        #print(value['opswiseGroups'])
        if value['name'].find(TASK_MONITOR_SUBFIX) != -1:
            number_of_variable += 1
            name = get_variable_name_custom_trim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
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


def create_variable_monitor(data):
    successful_count = 0
    number_of_task = 0
    for value in data:
        if value['name'].find(TASK_MONITOR_SUBFIX) != -1:
            number_of_task += 1
            task_name = get_variable_name_custom_trim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_MONITOR_SUBFIX)
            var_name = get_variable_name_custom_trim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
            json_data = {
                "type": "taskVariableMonitor",
                "name": task_name,
                "opswiseGroups": value['opswiseGroups'],
                "valueMonitorType": 3,
                "variableName": var_name,
                "value": "success",
            }
            #print(json_data)
            response = createVariableMonitorAPI(json_data)
            status = http.HTTPStatus(response.status_code)
            if response.status_code == 200:
                successful_count += 1
            print(f"{response.status_code} - {status.phrase}: {status.description}")
    print(f"Number of successful task creation: {successful_count} / {number_of_task}\n")
    return None


def add_action_to_task(data):
    number_of_task = 0
    successful_count = 0
    for value in data:
        if value['name'].find(TASK_MONITOR_SUBFIX) != -1:
            number_of_task += 1
            task_data = get_task_data(data, value['taskMonName'])
            var_name = get_variable_name_custom_trim(value['name'], TASK_MONITOR_SUBFIX, VARIABLE_SUBFIX)
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
            response = modifyTaskAPI(task_data)
            status = http.HTTPStatus(response.status_code)
            if response.status_code == 200:
                successful_count += 1
            print(f"{response.status_code} - {status.phrase}: {status.description}")
    print(f"Number of task to be updated: {successful_count} / {number_of_task}\n")
    
    return None


################################################################
        
def main():
    APIdata = getData(1)
    print("Number of Response:",len(APIdata),"\n")
    print("create variable")
    create_variable(APIdata)
    print("create variable monitor")
    create_variable_monitor(APIdata)
    print("add action to task")
    add_action_to_task(APIdata)






if __name__ == "__main__":
    main()