import sys
import os
import re
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateURI, updateAuth, updateTaskAPI, getTaskAPI, createDependencyInWorkflowAPI
from utils.readFile import loadJson
from utils.createFile import createJson
from utils.readExcel import getDataExcel
from utils.createFile import createExcel


ENABLE_UPDATE = True

COLUMN_GETLIST = 'AppName'
JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
APPNAME_COLUMN = 'AppName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'


CONDITION_LIST = 'condition_list'

PATTERN = r'\b[sfd]\([^\)]+\)'



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


sys.setrecursionlimit(10000)

def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list


def getAllInnermostSubstringsWithStatus(string, pattern):
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getConditionList(condition):
    condition_list = getAllInnermostSubstringsWithStatus(condition, PATTERN)
    return condition_list


def listConditionJob(df_job):
    list_condition_dict = {}
    for index, row in df_job.iterrows():
        condition = row[CONDITION_COLUMN]
        job_name = row[JOBNAME_COLUMN]
        list_condition_dict[job_name] = {}
        list_condition_dict[job_name][BOXNAME_COLUMN] = row[BOXNAME_COLUMN]
        list_condition_dict[job_name][CONDITION_LIST] = []
        if pd.isna(condition):
            continue
        #condition_list = getNamefromCondition(condition)
        condition_list = getConditionList(condition)
        for sub_condition in condition_list:
            list_condition_dict[job_name][CONDITION_LIST].append(sub_condition)
            
    
    return list_condition_dict


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

def getSubstringBetween(s, start_char, end_char):
    try:
        return s.split(start_char)[1].split(end_char)[0]
    except IndexError:
        return None


def addDependency(df, workflow_name):
    for value in workflow_name:
        response_workflow = getTaskAPI({'taskname': value})
        workflow_vertex = response_workflow.json().get('workflowVertices')
        #print(workflow_vertex)
        vertex_name = getVertex(workflow_vertex)
        dfv = df[df[JOBNAME_COLUMN].isin(vertex_name)]
        
        for index, row in dfv.iterrows():
            if isinstance(row[CONDITION_COLUMN], str):
                condition_list = row[CONDITION_COLUMN].split('&')
                condition_list = [x.strip() for x in condition_list]
                for condition in condition_list:
                    depen_configs = depen_configs_temp.copy()
                    workflow_configs = {
                        "workflowname": value,
                    }
                    depen_configs['sourceId']['value'] = getSourceTargetId(getSubstringBetween(condition, '(', ')'), workflow_vertex)
                    if depen_configs['sourceId']['value'] is None:
                        continue
                    depen_configs['targetId']['value'] = getSourceTargetId(row[JOBNAME_COLUMN], workflow_vertex)
                    if depen_configs['targetId']['value'] is None:
                        continue
                    depen_configs['condition']['value'] = getConditionStatus(condition)
                    #print(depen_configs)
                    #response = createDependencyInWorkflowAPI(depen_configs, workflow_configs)
                    #if response.status_code == 200:


def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.161']
    updateURI(domain)
    
    df_job = getDataExcel('Get New Task from Excel')
    list_condition_dict = listConditionJob(df_job)
    print(json.dumps(list_condition_dict, indent=4))
    
    
if __name__ == "__main__":
    main()