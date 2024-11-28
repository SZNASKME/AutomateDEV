import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

from utils.stbAPI import updateAuth, updateURI, getListTaskAPI
from utils.readFile import loadJson


APPNAME_COLUMN = 'AppName'
JOBNAME_COLUMN = 'jobName'

BUSINESS_SERVICES_LIST = [
    'A0076 - Data Warehouse ETL',
    'A0128 - Marketing Data Mart',
    'A0140 - NCB Data Submission',
    'A0329 - ODS',
    'A0356 - Big Data Foundation Platform',
    'A0356 - Big Data Foundation Platform (None-PRD)',
    'A0033 - BOT DMS (Data Management System)',
    'A0031 - Data Mart',
    'A0360 - Oracle Financial Services Analytical App',
    'A00000 - AskMe - Delete Tasks'
]


task_configs = {
    'name': '*',
    'businessServices': None,
}

def getUniqueList(df, column):
    return df[column].unique().tolist()

def getTaskListbyBusinessServices():
    task_list_by_BU = {}
    for business_service in BUSINESS_SERVICES_LIST:
        task_configs['businessServices'] = business_service
        response = getListTaskAPI(task_configs)
        if response.status_code == 200:
            task_list = response.json()
            for task in task_list:
                #task['name'] = trimSuffix(task['name'])
                if task['name'] in task_list_by_BU:
                    print(f"Warning: {task['name']} is duplicated in {business_service} task list")
                task_list_by_BU[task['name']] = business_service
        else:
            print(f"Error: {response.status_code} {business_service} task list will be empty")
            task_list_by_BU[business_service] = []
    return task_list_by_BU

def trimSuffix(task_name):
    if task_name.endswith('-WF'):
        return task_name[:-3]
    return task_name


def compareBusinessServices(df_jil, task_dict):
    task_log = []
    new_df_jil = df_jil.copy()
    new_df_jil[APPNAME_COLUMN] = None
    exist_task_dict = task_dict.copy()
    row_count = 0
    change_count = 0
    err_count = 0
    max_count = len(task_dict)
    for row in df_jil.itertuples(index=False):
        row_count += 1
        job_name = getattr(row, JOBNAME_COLUMN)
        app_name = getattr(row, APPNAME_COLUMN)
        if job_name in exist_task_dict:
            exist_task_dict.pop(job_name)
        business_service = task_dict.get(job_name)
        if business_service:
            if app_name != business_service:
                change_count += 1
                print(f"{row_count}/{max_count} | ({change_count}) {job_name} change Business Service to {business_service}")
                task_log.append({
                    'jobName': job_name,
                    'oldBusinessService': app_name,
                    'newBusinessService': business_service,
                    'remark': 'Business Service not match',
                })
                new_df_jil.loc[new_df_jil[JOBNAME_COLUMN] == job_name, APPNAME_COLUMN] = business_service
            else:
                new_df_jil.loc[new_df_jil[JOBNAME_COLUMN] == job_name, APPNAME_COLUMN] = app_name
        else:
            err_count += 1
            print(f"{row_count}/{max_count} | ({err_count}) {job_name} is not found in UAC")
            task_log.append({
                'jobName': job_name,
                'oldBusinessService': None,
                'newBusinessService': None,
                'remark': 'job not found in UAC',
            })
    exist_jobname = []
    for task_name, business_service in exist_task_dict.items():
        exist_jobname.append({
            'taskName': task_name,
            'businessService': business_service
        })
    df_exist_jobname = pd.DataFrame(exist_jobname)
    
    return df_exist_jobname, task_log, new_df_jil

def main():
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.86']
    updateURI(domain)
    
    df_jil = getDataExcel()
    list_task_by_BU = getTaskListbyBusinessServices()
    createJson('task_by_BU.json', list_task_by_BU)
    print("Task list by Business Services created successfully")
    df_jobname, task_log, new_df_jil = compareBusinessServices(df_jil, list_task_by_BU)
    df_task_log = pd.DataFrame(task_log)
    #createJson('not_found_in UAC.json',jobname_list)
    createExcel('RearrangeBusinessServices.xlsx',('REARRANGE_JIL', new_df_jil), ('log', df_task_log), ('not_found_in_excel', df_jobname))
    #print("Task log created successfully")
    
    
if __name__ == '__main__':
    main()

