
import sys
import os
import http
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.stbAPI import createTaskAPI, updateTaskAPI, getTaskAPI, createDependencyInWorkflowAPI, getListTaskAPI, getListTaskAdvancedAPI
from prefix import prefix_businessService
from collections import OrderedDict

BUSINESS_SERVICES = "A0417 - AML Management System"

task_adv_configs_temp = {
    'taskname': '*',
    'type': None,
    'businessServices': None,
    #'updatedTime': '-100d',
}

task_configs_temp = {
    'name': '*',
    'type': None,
    #'businessServices': None,
    'updatedTime': 'd',
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

###################################      workflow processing        ##############################################

def processingWorkflow(df, wfn, businessService = None):
    print("creating workflow...")
    createWorkflow(wfn, businessService)
    df_selected = df[df['box_name'].isin(wfn)]
    #print(df_selected)
    task_adv_configs = task_adv_configs_temp.copy()
    task_adv_configs['type'] = 1
    task_adv_configs['businessServices'] = businessService
    response_workflow_list = getListTaskAdvancedAPI(task_adv_configs)
    if response_workflow_list.status_code != 200:
        status = http.HTTPStatus(response_workflow_list.status_code)
        print(f"{response_workflow_list.status_code} - {status.phrase}: {status.description}")
        return None
    print("adding task in workflow...")
    addVertex(df_selected, response_workflow_list.json())
    print("adding dependency in workflow...")
    #addDependency(df_selected, wfn)
    

def createWorkflow(wfn, businessService):
    max_workflow = len(wfn)
    count_workflow = 0
    wfc_list = []
    task_configs = task_configs_temp.copy()
    task_configs['type'] = 1
    task_configs['businessServices'] = businessService
    response_list_task = getListTaskAPI(task_configs)
    if response_list_task.status_code != 200:
        status = http.HTTPStatus(response_list_task.status_code)
        print(f"{response_list_task.status_code} - {status.phrase}: {status.description}")
        return None
    #print(json.dumps(response_list_task.json(), indent=4))
    workflow_list = response_list_task.json()
    
    # check if workflow already exists
    businessService_list = addToList(businessService)
    for value in wfn:
        if not any(workflow.get('name') == value for workflow in workflow_list):
            json_data = {
                "type": "taskWorkflow",
                "name": value,
                "opswiseGroups": businessService_list,
            }
            wfc_list.append(json_data)
    
    if len(wfc_list) == 0:
        print("All workflow already exists")
        return None
    
    for value in wfc_list:
        response = createTaskAPI(value)
        status = http.HTTPStatus(response.status_code)
        if response.status_code == 200:
            count_workflow += 1
        print(f"{count_workflow}/{max_workflow} {response.status_code} - {status.phrase}: {status.description}")
        if response.status_code == 401:
            print("Authentication failed")
            return None
    return None


def findAvailableVertexId(api_data, vertex_dict, workflow_name):
    vertex_list = [0,1]
    for value in api_data:
        if value['name'] == workflow_name:
            for vertex in value['workflowVertices']:
                vertex_list.append(vertex['vertexId'])
            break
    
    for wfn, vertex_configs in vertex_dict.items():
        if wfn == workflow_name:
            for vertex in vertex_configs:
                vertex_list.append(vertex['vertexId'])
    
    vertex_list.sort()
    for i in range(len(vertex_list)):
        if i != vertex_list[i]:
            return i
    return len(vertex_list)+2

def addVertex(excel_data, api_data):
    max_vertex = 0
    count_vertex = 0
    previous_wfn = None
    freq_vertex_dict_api = {}
    freq_vertex_dict_excel = {}
    vertex_dict = OrderedDict()
    # create frequency list of workflow from API data
    for value in api_data:
        freq_dict = createFrequencyList(value.get('workflowVertices'), 'task', 'value')
        freq_vertex_dict_api[value['name']] = freq_dict
        
                               
    print(json.dumps(freq_vertex_dict_api, indent=4))
    
    for index, row in excel_data.iterrows():
        freq_vertex_dict_excel = updateFrequencyDict(freq_vertex_dict_excel, row['jobName'], row['box_name'])
        if freq_vertex_dict_excel[row['box_name']].get(row['jobName']) <= freq_vertex_dict_api[row['box_name']].get(row['jobName'], 0):
            continue
        if previous_wfn != row['box_name']:
            Xpos = 0
            Ypos = 0
        vertex_configs = {
            "alias": None,
            "task":{
                "value": row['jobName']
            },
            "vertexId": findAvailableVertexId(api_data, vertex_dict, row['box_name']),
            "vertexX": Xpos,
            "vertexY": Ypos,
        }
        Xpos += 50
        Ypos += 150
        previous_wfn = row['box_name']
        if row['box_name'] not in vertex_dict:
            vertex_dict[row['box_name']] = []
        vertex_dict[row['box_name']].append(vertex_configs)
        max_vertex += 1
        
    #print(json.dumps(vertex_dict, indent=4))
    
    for workflow_name, vertex_configs in vertex_dict.items():
        workflow_data = OrderedDict()
        for value in api_data:
            if value['name'] == workflow_name:
                workflow_data = value
                break
        vertex_configs.extend(workflow_data.get('workflowVertices'))
        workflow_data['workflowVertices'] = vertex_configs
        
        print(json.dumps(workflow_data['workflowVertices'], indent=4))
        response = updateTaskAPI(workflow_data)
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
                    if depen_configs['sourceId']['value'] is None:
                        continue
                    depen_configs['targetId']['value'] = getSourceTargetId(row['jobName'], workflow_vertex)
                    if depen_configs['targetId']['value'] is None:
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

#################################     utils       ########################################################

def getListTaskname(data):
    list_taskname = []
    for task in data:
        list_taskname.append(task['name'])
    return list_taskname

def startWithAny(prefix_list, string):
    for prefix in prefix_list:
        if string.startswith(prefix):
            return True
    return False

def getWorkflowExcel(df, taskname_list = None, prefix_list = None):
    workflow = []
    for index, row in df.iterrows():
        if taskname_list is not None and row['jobName'] not in taskname_list and row['jobType'] == 'BOX':
            if prefix_list is not None and startWithAny(prefix_list, row['jobName']):
                    workflow.append(row['jobName'])
        elif taskname_list is None and row['jobType'] == 'BOX':
            if prefix_list is not None and startWithAny(prefix_list, row['jobName']):
                    workflow.append(row['jobName'])
    return workflow

def getPrefix(businessService:str):
    for key, value in prefix_businessService.items():
        if key.lower() == businessService.lower():
            return value


def getSubstringBetween(s, start_char, end_char):
    try:
        return s.split(start_char)[1].split(end_char)[0]
    except IndexError:
        return None

def addToList(new_items):
    target_list = []
    if isinstance(new_items, str):
        target_list.append(new_items)
    elif isinstance(new_items, list):
        target_list.extend(new_items)
    else:
        raise TypeError("new_items must be a string or a list of strings")
    
    return target_list

def createFrequencyList(data, *dict_indices):
    freq_dict = {}
    for value in data:
        # Navigate to the target value using dict_indices
        for key in dict_indices:
            value = value[key]

        if value in freq_dict:
            freq_dict[value] += 1
        else:
            freq_dict[value] = 1

    return freq_dict

def updateFrequencyDict(existing_freq_dict, value, *dict_indices):
    current_dict = existing_freq_dict
    for key in dict_indices[:-1]:
        if key not in current_dict:
            current_dict[key] = {}
        current_dict = current_dict[key]
    final_key = dict_indices[-1]
    if final_key not in current_dict:
        current_dict[final_key] = {}
    
    if value in current_dict[final_key]:
        current_dict[final_key][value] += 1
    else:
        current_dict[final_key][value] = 1

    return existing_freq_dict

###############################           main       ########################################################
def main():
    prefix_list = getPrefix(BUSINESS_SERVICES)
    print(prefix_list)
    #taskname_list = getListTaskname(API_Data.json())
    #print(taskname_list) # list of workflow tasks
    df = getDataExcel()
    #print(df)
    wfn = getWorkflowExcel(df, prefix_list = prefix_list)
    processingWorkflow(df, wfn, BUSINESS_SERVICES)

if __name__ == "__main__":
    main()