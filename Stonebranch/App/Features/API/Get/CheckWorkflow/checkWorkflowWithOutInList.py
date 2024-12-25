import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, getTaskAPI

workflow_configs_temp = {
    'name': '*',
    'type': 1,
    'businessServices': 'A0076 - Data Warehouse ETL',
}

task_configs_temp = {
    'taskname': None,
}


def getWorkflow():
    response = getListTaskAPI(workflow_configs_temp)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def getSpecificColumn(df, column_name, filter_column_name = None, *filter_value):
    column_list = []
    if filter_column_name is not None:
        df = df[df[filter_column_name].isin(filter_value)]
        
    for index, row in df.iterrows():
        column_list.append(row[column_name])
    return column_list

def checkSuffix(jobName, suffix_list):
    for suffix in suffix_list:
        if jobName.endswith(suffix):
            return True
    return False

def getStartWithTask(taskName, in_list):
    for in_task in in_list:
        if taskName.startswith(in_task):
            return in_task
    return None

def checkDependencyInList(workflow_with_out_in_list, in_list):
    err_Depen_list = []
    err_NonDepen_list = []
    count = 0
    for workflow in workflow_with_out_in_list:
        count += 1
        if workflow['name'] in in_list:
            print(f'{count}/{len(workflow_with_out_in_list)} Error: {workflow["name"]} is in the list')
            continue
        workflow_name = workflow['name']
        task_configs = task_configs_temp.copy()
        task_configs['taskname'] = workflow_name
        response_task = getTaskAPI(task_configs, False)
        if response_task.status_code == 200:
            workflow_data = response_task.json()
            dependency_list = workflow_data['workflowEdges']
            vertice_list = workflow_data['workflowVertices']
            if len(dependency_list) != 0:
                for dependency in dependency_list:
                        if dependency['sourceId']['taskName'].startswith(tuple(in_list)):
                            err_Depen_list.append({
                                'workflow': workflow_name,
                                'sourceTask': dependency['sourceId']['taskName'],
                                'destinationTask': dependency['targetId']['taskName'],
                            })
            else:
                for vertice in vertice_list:
                    if vertice['task']['value'].startswith(tuple(in_list)):
                        err_NonDepen_list.append({
                            'workflow': workflow_name,
                            'taskName': vertice['task']['value'],
                        })
            print(f'{count}/{len(workflow_with_out_in_list)} done | {workflow_name}')
        else:
            print(f'{count}/{len(workflow_with_out_in_list)} Error: {workflow_name} not found')

    return err_Depen_list, err_NonDepen_list

def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.86']
    updateURI(domain)
    
    df = getDataExcel()
    workflow_list = getWorkflow()
    in_list_condition = getSpecificColumn(df, 'jobName', 'rootBox', 'DWH_ONICE_ONHOLD_B')
    err_Depen_list, err_NonDepen_list = checkDependencyInList(workflow_list, in_list_condition)
    
    df_err_Depen = pd.DataFrame(err_Depen_list)
    df_err_NonDepen = pd.DataFrame(err_NonDepen_list)
    
    createExcel('depend_in_list.xlsx', ('Have Depen', df_err_Depen), ('Non Depen', df_err_NonDepen))

if __name__ == '__main__':
    main()