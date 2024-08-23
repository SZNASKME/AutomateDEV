from requests.auth import HTTPBasicAuth
import requests
import urllib.parse
import http

DOMAIN = "http://172.16.1.85:8080/uc/resources"


TASK_URI = f"{DOMAIN}/task"
LIST_TASK_URI = f"{DOMAIN}/task/list"
LIST_TASK_ADV_URI = f"{DOMAIN}/listadv"


TRIGGER_URI = f"{DOMAIN}/trigger"
LIST_TRIGGER_URI = f"{DOMAIN}/trigger/list"
LIST_TRIGGER_ADV_URI = f"{DOMAIN}/trigger/listadv"

PROMOTE_BUNDLE_URI = f"{DOMAIN}/bundle/promote"

TASK_IN_WORKFLOW_URI = f"{DOMAIN}/workflow/vertices"
DEPEN_IN_WORKFLOW_URI = f"{DOMAIN}/workflow/edges"

VARIABLE_URI = f"{DOMAIN}/variable"

auth = HTTPBasicAuth('ops.admin','p@ssw0rd')

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri

def updateURI(changed_domain):
    global TASK_URI, LIST_TASK_URI, LIST_TASK_ADV_URI, TRIGGER_URI, LIST_TRIGGER_URI, LIST_TRIGGER_ADV_URI, PROMOTE_BUNDLE_URI
    TASK_URI = f"{changed_domain}/task"
    LIST_TASK_URI = f"{changed_domain}/task/list"
    LIST_TASK_ADV_URI = f"{changed_domain}/task/listadv"
    TRIGGER_URI = f"{changed_domain}/trigger"
    LIST_TRIGGER_URI = f"{changed_domain}/trigger/list"
    LIST_TRIGGER_ADV_URI = f"{changed_domain}/trigger/listadv"
    PROMOTE_BUNDLE_URI = f"{changed_domain}/bundle/promote"

def updateAuth(username, password):
    global auth
    auth = HTTPBasicAuth(username, password)

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


def promoteBundleAPI(bundle_configs, show_response = True):
    response = requests.post(url = PROMOTE_BUNDLE_URI, json = bundle_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response


###########################################################################################

def createTaskInWorkflowAPI(task_configs, workflow_configs):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    #print(uri)
    response = requests.post(url = uri, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def updateTaskInWorkflowAPI(task_configs, workflow_configs):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    response = requests.put(url = uri, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def createDependencyInWorkflowAPI(dependency_configs, workflow_configs):
    uri = createURI(DEPEN_IN_WORKFLOW_URI, workflow_configs)
    response = requests.post(url = uri, json = dependency_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def updateDependencyInWorkflowAPI(dependency_configs, workflow_configs):
    uri = createURI(DEPEN_IN_WORKFLOW_URI, workflow_configs)
    response = requests.put(url = uri, json = dependency_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response


###########################################################################################

def createVariableAPI(variable_configs):
    response = requests.post(url = VARIABLE_URI, json = variable_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response