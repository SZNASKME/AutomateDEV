import multiprocessing
import time
import requests
from requests.auth import HTTPBasicAuth
import http
import urllib.parse
import json
from readExcel import getDataExcel
from concurrent.futures import ThreadPoolExecutor, as_completed

TASK_URI = "http://172.16.1.151:8080/uc/resources/task"
TASK_IN_WORKFLOW_URI = "http://172.16.1.151:8080/uc/resources/workflow/vertices"
DEPEN_IN_WORKFLOW_URI = "http://172.16.1.151:8080/uc/resources/workflow/edges"
TASK_ADV_URI = "http://172.16.1.85:8080/uc/resources/task/listadv"

PREFIX = "AMMS_"

task_adv_configs = {
    'taskname': '*',
    'type': 1,
    'businessServices': 'A0417 - AML MANAGEMENT SYSTEM',
    #'updatedTime': '-100d',
}

depen_configs_temp = {
    "condition": {
        "value": "Success"
    },
    "sourceId": {
        "taskName": None,
    },
    "targetId": {
        "taskName": None,
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

auth = HTTPBasicAuth('ops.admin','p@ssw0rd')

############################################################################################################

def getSubstringBetween(s, start_char, end_char):
    try:
        return s.split(start_char)[1].split(end_char)[0]
    except IndexError:
        return None

############################################################################################################

def authCheck(auth):
    return auth

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri

def getListTaskAdvancedAPI():
    uri = createURI(TASK_ADV_URI, task_adv_configs)
    print(uri)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    return response

def createTaskAPI(task_configs):
    response = requests.post(url = TASK_URI, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def getTaskAPI(task_configs):
    uri = createURI(TASK_URI, task_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    return response

def createTaskInWorkflowAPI(task_configs, workflow_configs):
    uri = createURI(TASK_IN_WORKFLOW_URI, workflow_configs)
    #print(uri)
    response = requests.post(url = uri, json = task_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

def createDependencyInWorkflowAPI(dependency_configs, workflow_configs):
    uri = createURI(DEPEN_IN_WORKFLOW_URI, workflow_configs)
    response = requests.post(url = uri, json = dependency_configs, auth = auth, headers = {'Content-Type': 'application/json'})
    return response

############################################################################################################

def processingWorkflow(df, wfn):
    print("creating workflow...")
    #createWorkflow(wfn)
    df_selected = df[df['box_name'].isin(wfn)]
    #print(df_selected)
    print("adding task in workflow...")
    #addVertex(df_selected)
    print("adding dependency in workflow...")
    addDependency(df_selected, wfn)
    

def addVertex(data):
    vertex_list = []
    previous_wfn = None
    max_vertex = len(data)
    count_vertex = 0
    print("MAX Vertex",max_vertex)
    for index, row in data.iterrows():
        if previous_wfn != row['box_name']:
            Xpos = 0
            Ypos = 0
        workflow_configs = {
            "workflowname": row['box_name'],
        }
        vertex_configs = {
            "alias": None,
            "task":{
                "value": row['jobName']
            },
            "vertexX": Xpos,
            "vertexY": Ypos,
        }
        Xpos += 150
        Ypos += 150
        previous_wfn = row['box_name']
        vertex_list.append((vertex_configs, workflow_configs))
        #print(json.dumps(vertex_configs, indent=4))
    
    for vertex_configs, workflow_configs in vertex_list:
        #print(vertex_configs)
        #print(workflow_configs)
        response = createTaskInWorkflowAPI(vertex_configs, workflow_configs)
        status = http.HTTPStatus(response.status_code)
        if response.status_code == 200:
            count_vertex += 1
        print(f"{count_vertex}/{max_vertex} {response.status_code} - {status.phrase}: {status.description}")
        if response.status_code == 401:
            print("Authentication failed")
            return None
    return None



def getVertex(data):
    vertex_list = []
    for vertex in data:
        vertex_list.append(vertex["task"]["value"])
    return vertex_list

def getConditionStatus(condition):
    if condition.startswith("s"):
        return "Success"
    elif condition.startswith("f"):
        return "Failure"
    elif condition.startswith("d"):
        return "Success/Failure"

def getSourceTargetId(name, workflow_vertex):
    Id = None
    for vertex in workflow_vertex:
        if vertex["task"]["value"] == name:
            Id = vertex["vertexId"]
            break
    return Id


def addDependency(df, workflow_name):
    count_dependency = 0
    for value in workflow_name:
        response_workflow = getTaskAPI({'taskname': value})
        workflow_vertex = response_workflow.json().get('workflowVertices')
        #print(workflow_vertex)
        vertex_name = getVertex(workflow_vertex)
        dfv = df[df["jobName"].isin(vertex_name)]
        
        
        for index, row in dfv.iterrows():
            if isinstance(row['condition'], str):
                condition_list = row['condition'].split('&')
                condition_list = [x.strip() for x in condition_list]
                for condition in condition_list:
                    depen_configs = depen_configs_temp.copy()
                    workflow_configs = {
                        "workflowname": value,
                    }
                    depen_configs['sourceId']['value'] = getSourceTargetId(getSubstringBetween(condition, '(', ')'), workflow_vertex)
                    if depen_configs['sourceId']['value'] == None:
                        continue
                    depen_configs['targetId']['value'] = getSourceTargetId(row['jobName'], workflow_vertex)
                    if depen_configs['targetId']['value'] == None:
                        continue
                    depen_configs['condition']['value'] = getConditionStatus(condition)
                    #print(depen_configs)
                    response = createDependencyInWorkflowAPI(depen_configs, workflow_configs)
                    status = http.HTTPStatus(response.status_code)
                    if response.status_code == 200:
                        count_dependency += 1
                    print(f"{count_dependency} {response.status_code} - {status.phrase}: {status.description}")
                    if response.status_code == 401:
                        print("Authentication failed")
                        return None



def getListTaskname(data):
    list_taskname = []
    for task in data:
        list_taskname.append(task['name'])
    return list_taskname



def getWorkflowExcel(df, taskname_list = None, prefix = None):
    workflow = []
    for index, row in df.iterrows():
        if taskname_list != None and row['jobName'] not in taskname_list and row['jobType'] == 'BOX':
            if prefix != None and row['jobName'].startswith(prefix):
                    workflow.append(row['jobName'])
        elif taskname_list == None and row['jobType'] == 'BOX':
            if prefix != None and row['jobName'].startswith(prefix):
                    workflow.append(row['jobName'])
    return workflow



def createWorkflow(wfn):
    max_workflow = len(wfn)
    count_workflow = 0
    for value in wfn:
        json_data = {
            "type": "taskWorkflow",
            "name": value,
            #"opswiseGroups": "A0417 - AML MANAGEMENT"
        }
        response = createTaskAPI(json_data)
        status = http.HTTPStatus(response.status_code)
        if response.status_code == 200:
            count_workflow += 1
        print(f"{count_workflow}/{max_workflow} {response.status_code} - {status.phrase}: {status.description}")
        if response.status_code == 401:
            print("Authentication failed")
            return None
    return None


############################################################################################################

def main():
    #API_Data = getListTaskAdvancedAPI()
    #taskname_list = getListTaskname(API_Data.json())
    #print(taskname_list) # list of workflow tasks
    df = getDataExcel()
    print(df)
    wfn = getWorkflowExcel(df, prefix = PREFIX)
    processingWorkflow(df, wfn)

if __name__ == "__main__":
    main()