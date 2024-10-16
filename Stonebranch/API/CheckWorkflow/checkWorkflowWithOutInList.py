import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, getListDependencyInWorkflowAPI

workflow_configs_temp = {
    'name': '*',
    'type': 1,
    'businessServices': 'A0076 - Data Warehouse ETL',
}

task_configs_temp = {
    'workflowname': None,
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

def checkDependencyInList(workflow_with_out_in_list, in_list):
    err_TM_list = []
    err_Task_list = []
    for workflow in workflow_with_out_in_list:
        if workflow['name'] in in_list:
            continue
        workflow_name = workflow['name']
        task_configs = task_configs_temp.copy()
        task_configs['workflowname'] = workflow_name
        response_dependency = getListDependencyInWorkflowAPI(task_configs)
        if response_dependency.status_code == 200:
            dependency_list = response_dependency.json()
            for dependency in dependency_list:
                if dependency['sourceId']['taskName'].endswith('-TM'):
                    source =  dependency['sourceId']['taskName'].replace('-TM', '')
                    if source in in_list:
                        err_TM_list.append({
                            'workflow': workflow_name,
                            'sourceTask': dependency['sourceId']['taskName'],
                            'destinationTask': dependency['targetId']['taskName'],
                        })
                else:
                    source = dependency['sourceId']['taskName']
                    if source in in_list:
                        err_Task_list.append({
                            'workflow': workflow_name,
                            'sourceTask': dependency['sourceId']['taskName'],
                            'destinationTask': dependency['targetId']['taskName'],
                        })

    return err_TM_list, err_Task_list

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
    err_TM_list, err_Task_list = checkDependencyInList(workflow_list, in_list_condition)
    
    df_err_TM = pd.DataFrame(err_TM_list)
    df_err_Task = pd.DataFrame(err_Task_list)
    
    createExcel('depend_in_list.xlsx', (df_err_TM, 'TM'), (df_err_Task, 'Task'))

if __name__ == '__main__':
    main()