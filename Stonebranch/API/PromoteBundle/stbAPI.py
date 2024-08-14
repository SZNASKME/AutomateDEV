from requests.auth import HTTPBasicAuth
import requests
import urllib.parse
import http

DOMAIN = "http://172.16.1.86:8080/uc/resources"


TASK_URI = f"{DOMAIN}/task"
LIST_TASK_URI = f"{DOMAIN}/task/list"
LIST_TASK_ADV_URI = f"{DOMAIN}/listadv"


TRIGGER_URI = f"{DOMAIN}/trigger"
LIST_TRIGGER_URI = f"{DOMAIN}/trigger/list"
LIST_TRIGGER_ADV_URI = f"{DOMAIN}/trigger/listadv"

BUNDLE_URI = f"{DOMAIN}/bundle"
PROMOTE_BUNDLE_URI = f"{DOMAIN}/bundle/promote"


auth = HTTPBasicAuth('ops.admin','p@ssw0rd')

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri

###########################################################################################

def getTaskAPI(task_configs, show_response = True):
    response = requests.get(url = TASK_URI, json = task_configs, auth = auth, headers = {'Accept': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def createTaskAPI(task_configs, show_response = True):
    response = requests.post(url = TASK_URI, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def updateTaskAPI(task_configs, show_response = True):
    response = requests.put(url = TASK_URI, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def deleteTaskAPI(task_configs, show_response = True):
    uri = createURI(TASK_URI, task_configs)
    response = requests.delete(url = uri, auth = auth)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###########################################################################################

def getListTaskAPI(task_configs, show_response = True):
    response = requests.post(url=LIST_TASK_URI, json = task_configs, auth=auth, headers={'Accept': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def getListTaskAdvancedAPI(task_adv_configs, show_response = True):
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###########################################################################################

def getTriggerAPI(trigger_configs, show_response = True):
    response = requests.get(url = TRIGGER_URI, json = trigger_configs, auth = auth, headers = {'Accept': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def createTriggerAPI(trigger_configs, show_response = True):
    response = requests.post(url = TRIGGER_URI, json = trigger_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response
    
def updateTriggerAPI(trigger_configs, show_response = True):
    response = requests.put(url = TRIGGER_URI, json = trigger_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def deleteTriggerAPI(trigger_configs, show_response = True):
    uri = createURI(TRIGGER_URI, trigger_configs)
    response = requests.delete(url = uri, auth = auth)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###########################################################################################

def getListTriggerAPI(trigger_configs, show_response = True):
    response = requests.post(url = LIST_TRIGGER_URI, json = trigger_configs, auth = auth, headers={'Accept': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def getListTriggerAdvancedAPI(trigger_configs, show_response = True):
    uri = createURI(LIST_TRIGGER_URI, trigger_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###########################################################################################

def getBundleAPI(bundle_configs, show_response = True):
    uri = createURI(BUNDLE_URI, bundle_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def promoteBundleAPI(bundle_configs, show_response = True):
    response = requests.post(url = PROMOTE_BUNDLE_URI, json = bundle_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

