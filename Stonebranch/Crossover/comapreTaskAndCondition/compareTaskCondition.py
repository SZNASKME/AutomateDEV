import sys
import os
import pandas as pd
import re


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import runReportAPI, updateAuth, updateURI



WORKFLOW_REPORT_NAME = 'AskMe - Workflow Report'

# JIL Columns
APPNAME_COLUMN = 'AppName'
JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'

SELECTED_COLUMN = 'jobName'
FILTER_COLUMN = 'rootBox'




report_configs_temp = {
    'reporttitle': None,
}





def getSpecificColumn(df, column_name, filter_column_name = None, filter_value_list = None):
    column_list_dict = {}
    for filter_value in filter_value_list:
        df_filtered = df.copy()
        if filter_column_name is not None:
            df_filtered = df_filtered[df_filtered[filter_column_name].isin([filter_value])]

        #column_list_dict[filter_value] = []
        column_list_dict[filter_value] = df[df[column_name] == filter_value][column_name].tolist()
        if filter_column_name is not None:
            for index, row in df_filtered.iterrows():
                if row[column_name] not in column_list_dict[filter_value]:
                    column_list_dict[filter_value].append(row[column_name])
        
    return column_list_dict  

def getReport(report_title):
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = report_title
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')
    if response_csv.status_code == 200:
        print("Report generated successfully")
        #print(response_csv.text)
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        print("Error generating report")
        return None

def cleanNoneDF(df):
    df = df.astype(str).fillna('')
    df = df.replace('nan', '')
    return df

def compareTaskinWorkflow(df_job, df_workflow_report, list_dict):
    all_list = [job_name for job_name_list in list_dict.values() for job_name in job_name_list]
    
    df_job = cleanNoneDF(df_job)
    df_workflow_report = cleanNoneDF(df_workflow_report)
    
    df_job_in_list = df_job[df_job[JOBNAME_COLUMN].isin(all_list)]
    


def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    df_job = getDataExcel('get Excel path with main job file')
    root_list_option = input("Do you want to use the root or list or all? (r/l/a): ")
    if root_list_option == 'a':
        all_list_job = df_job[JOBNAME_COLUMN].tolist()
        list_dict = [{job_name: [job_name]} for job_name in all_list_job]
    else:
        if root_list_option == 'r':
            df_root = getDataExcel("Enter the path of the excel file with the root jobs")
        df_list_job = getDataExcel("Enter the path of the excel file with the list of jobs")
        list_job_name = df_list_job[JOBNAME_COLUMN].tolist()
        if root_list_option == 'r':
            list_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, list_job_name)
        else:
            list_dict = getSpecificColumn(df_job, SELECTED_COLUMN, None, list_job_name)
    print("---------------------------------")
    for key, value in list_dict.items():
        print(key, len(value))
    print("---------------------------------")
    
    df_workflow_report = getReport(WORKFLOW_REPORT_NAME)
    
    compareTaskinWorkflow(df_job, df_workflow_report, list_dict)