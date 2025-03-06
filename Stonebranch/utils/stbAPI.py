from requests.auth import HTTPBasicAuth
import requests
import urllib.parse
import http

DOMAIN = "http://?.?.?.?:?/uc/resources"


TASK_URI = f"{DOMAIN}/task"
LIST_TASK_URI = f"{DOMAIN}/task/list"
LIST_TASK_ADV_URI = f"{DOMAIN}/listadv"


TRIGGER_URI = f"{DOMAIN}/trigger"
LIST_TRIGGER_URI = f"{DOMAIN}/trigger/list"
LIST_TRIGGER_ADV_URI = f"{DOMAIN}/trigger/listadv"
LIST_QUALIFYING_TRIGGER_URI = f"{DOMAIN}/trigger/qualifyingtimes"

PROMOTE_BUNDLE_URI = f"{DOMAIN}/bundle/promote"

TASK_IN_WORKFLOW_URI = f"{DOMAIN}/workflow/vertices"
DEPEN_IN_WORKFLOW_URI = f"{DOMAIN}/workflow/edges"

VARIABLE_URI = f"{DOMAIN}/variable"

LIST_PARENT_TASK_URI = f"{DOMAIN}/task/parent/list"

RUN_REPORT_URI = f"{DOMAIN}/report/run"

BUSINESS_SERVICE_URI = f"{DOMAIN}/businessservice"

auth = HTTPBasicAuth('?','?')

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri

def updateURI(changed_domain):
    global TASK_URI, LIST_TASK_URI, LIST_TASK_ADV_URI, TRIGGER_URI, LIST_TRIGGER_URI
    global LIST_TRIGGER_ADV_URI, LIST_QUALIFYING_TRIGGER_URI, PROMOTE_BUNDLE_URI, TASK_IN_WORKFLOW_URI
    global DEPEN_IN_WORKFLOW_URI, VARIABLE_URI, LIST_PARENT_TASK_URI, RUN_REPORT_URI, BUSINESS_SERVICE_URI
    TASK_URI = f"{changed_domain}/task"
    LIST_TASK_URI = f"{changed_domain}/task/list"
    LIST_TASK_ADV_URI = f"{changed_domain}/task/listadv"
    TRIGGER_URI = f"{changed_domain}/trigger"
    LIST_TRIGGER_URI = f"{changed_domain}/trigger/list"
    LIST_TRIGGER_ADV_URI = f"{changed_domain}/trigger/listadv"
    LIST_QUALIFYING_TRIGGER_URI = f"{changed_domain}/trigger/qualifyingtimes"
    PROMOTE_BUNDLE_URI = f"{changed_domain}/bundle/promote"
    TASK_IN_WORKFLOW_URI = f"{changed_domain}/workflow/vertices"
    DEPEN_IN_WORKFLOW_URI = f"{changed_domain}/workflow/edges"
    VARIABLE_URI = f"{changed_domain}/variable"
    LIST_PARENT_TASK_URI = f"{changed_domain}/task/parent/list"
    RUN_REPORT_URI = f"{changed_domain}/report/run"
    BUSINESS_SERVICE_URI = f"{changed_domain}/businessservice"

def updateAuth(username, password):
    global auth
    auth = HTTPBasicAuth(username, password)

def formatHeader(key, format_str):
    if format_str == "json":
        return {key: 'application/json'}
    elif format_str == "xml":
        return {key: 'application/xml'}
    elif format_str == "text":
        return {key: 'text/plain'}
    elif format_str == "csv":
        return {key: 'text/csv'}


###########################           Task           #####################################

def getTaskAPI(task_configs, show_response = True, format_str ='json'):
    uri = createURI(TASK_URI, task_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def createTaskAPI(task_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = TASK_URI, json = task_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def updateTaskAPI(task_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.put(url = TASK_URI, json = task_configs, auth = auth, headers = header)
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

###########################          List Task           #####################################

def getListTaskAPI(task_configs, show_response = True, format_str ='json'):
    header = formatHeader('Accept', format_str)
    response = requests.post(url=LIST_TASK_URI, json = task_configs, auth=auth, headers=header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def getListTaskAdvancedAPI(task_adv_configs, show_response = True, format_str ='json'):
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers=header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

#############################           Trigger           #######################################

def getTriggerAPI(trigger_configs, show_response = True, format_str ='json'):
    uri = createURI(TRIGGER_URI, trigger_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def createTriggerAPI(trigger_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = TRIGGER_URI, json = trigger_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response
    
def updateTriggerAPI(trigger_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.put(url = TRIGGER_URI, json = trigger_configs, auth = auth, headers = header)
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

def getListQualifyingTriggerAPI(trigger_configs, show_response = True, format_str ='json'):
    uri = createURI(LIST_QUALIFYING_TRIGGER_URI, trigger_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###########################           List Trigger           #####################################

def getListTriggerAPI(trigger_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = LIST_TRIGGER_URI, json = trigger_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def getListTriggerAdvancedAPI(trigger_configs, show_response = True, format_str ='json'):
    uri = createURI(LIST_TRIGGER_ADV_URI, trigger_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###########################           Bundle/Promote           #####################################


def promoteBundleAPI(bundle_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = PROMOTE_BUNDLE_URI, json = bundle_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response


###############################           Workflow           #########################################

def createTaskInWorkflowAPI(task_configs, workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = uri, json = task_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def updateTaskInWorkflowAPI(task_configs, workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Content-Type', format_str)
    response = requests.put(url = uri, json = task_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def deleteTaskInWorkflowAPI( workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Content-Type', format_str)
    response = requests.delete(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response


def ListWorkflowForecastAPI(workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###############################           Vertices           #########################################

def getListTaskInWorkflowAPI(workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###############################           Dependency           #########################################

def getListDependencyInWorkflowAPI(workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(DEPEN_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def createDependencyInWorkflowAPI(dependency_configs, workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(DEPEN_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = uri, json = dependency_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

def updateDependencyInWorkflowAPI(dependency_configs, workflow_configs, show_response = True, format_str ='json'):
    uri = createURI(DEPEN_IN_WORKFLOW_URI, workflow_configs)
    header = formatHeader('Content-Type', format_str)
    response = requests.put(url = uri, json = dependency_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###############################           Parent           #########################################

def viewParentTaskAPI(task_configs, show_response = True, format_str ='json'):
    uri = createURI(LIST_PARENT_TASK_URI, task_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

###############################           Variable           #########################################

def createVariableAPI(variable_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = VARIABLE_URI, json = variable_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response

##############################             Report              ##########################################

def runReportAPI(report_configs, show_response = True, format_str ='json'):
    uri = createURI(RUN_REPORT_URI, report_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, json = report_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response


##############################             Business Service              ##########################################

def getBusinessServiceAPI(business_service_configs, show_response = True, format_str ='json'):
    uri = createURI(BUSINESS_SERVICE_URI, business_service_configs)
    header = formatHeader('Accept', format_str)
    response = requests.get(url = uri, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response


def createBusinessServiceAPI(business_service_configs, show_response = True, format_str ='json'):
    header = formatHeader('Content-Type', format_str)
    response = requests.post(url = BUSINESS_SERVICE_URI, json = business_service_configs, auth = auth, headers = header)
    if show_response:
        status = http.HTTPStatus(response.status_code)
        print(f"{response.status_code} - {status.phrase}: {status.description}")
    return response
