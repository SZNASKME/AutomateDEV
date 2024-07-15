import requests
import http

LIST_TASK_URI = "http://172.16.1.85:8080/uc/resources/task/list"
LIST_TASK_ADV_URI = "http://172.16.1.85:8080/uc/resources/task/listadv"

task_configs = {
    'name': '*',
    'type':  'Timer'
}

task_adv_configs = {
    'taskname': '*',
    'type': 'Timer',
    'updatedTime': '-10d',
}


auth = ('ops.admin','p@ssw0rd')

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    return uri




def getListTask():
    response = requests.post(url=LIST_TASK_URI, json=task_configs, auth=auth, headers={'Accept': 'application/json'})
    return response

def getListTaskAdvanced():
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    print(uri)
    response = requests.get(url=uri, auth=auth, headers={'Accept': 'application/json'})
    return response

def getData(mode = 0):
    
    if mode == 0:
        response = getListTask()
    else:
        response = getListTaskAdvanced()
        
    status = http.HTTPStatus(response.status_code)
    print(f"{response.status_code} - {status.phrase}: {status.description}")
    if response.status_code == 200:
        return response.text
    else:
        return None