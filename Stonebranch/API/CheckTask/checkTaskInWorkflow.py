import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readFile import loadJson
from utils.createFile import createJson, createExcel
from utils.stbAPI import updateURI, updateAuth, getTaskAPI, viewParentTaskAPI

TASK_NAME = "startDummy"

parent_configs_temp = {
    'taskname': 'None',
}

task_configs_temp = {
    'taskname': '',
}


def getParentList():
    task_configs = parent_configs_temp.copy()
    task_configs['taskname'] = TASK_NAME
    response = viewParentTaskAPI(task_configs)
    if response.status_code == 200:
        parent_list = response.json()
        return parent_list
    else:
        return None


def checkTaskRootVertex(workflow, task_name):
    
    for dependency in workflow['workflowEdges']:
        source = dependency['targetId']['taskName']
        #print(source, task_name)
        if source == task_name:
            #print("Found")
            return False
    return True
        

def findTaskRootVertex(parent_list, task_name):
    
    root_vertex_list = []
    for parent in parent_list:
        workflow_name = parent['name']
        
        workflow_configs = task_configs_temp.copy()
        workflow_configs['taskname'] = workflow_name
        response = getTaskAPI(workflow_configs)
        if response.status_code == 200:
            workflow = response.json()
            if checkTaskRootVertex(workflow, task_name):
                root_vertex_list.append({
                    "jobName": task_name,
                    "box_name": workflow_name
                    })
    return root_vertex_list
        



def main():
    auth = loadJson('Auth.json')
    #userpass = auth['TTB']
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    #domain = "https://ttbdevstb.stonebranch.cloud/resources"
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    parent_list = getParentList()
    print(len(parent_list))
    root_vertex_list = findTaskRootVertex(parent_list, TASK_NAME)
    #print(root_vertex_list)
    print(len(root_vertex_list))
    createJson('rootVertex.json', root_vertex_list)
    root_vertex_df = pd.DataFrame(root_vertex_list)
    createExcel(f'86_rootVertex_{TASK_NAME}.xlsx', (root_vertex_df, 'Root Vertex'))

if __name__ == '__main__':
    main()