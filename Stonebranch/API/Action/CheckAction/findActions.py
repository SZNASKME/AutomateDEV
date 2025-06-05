import sys
import os
import pandas as pd
import re
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import *

ABORT_ACTION_REPORT_TITLE = 'All Actions which Abort Tasks'
SYS_OPS_ACTION_REPORT_TITLE = 'All Actions which Run Task Instance Commands'
    
ABORT_ACTION_SHEETNAME = 'Abort Action'
SYS_OPS_ACTION_SHEETNAME = 'System Operations Action'
    
OUTPUT_EXCEL_NAME = 'Action Case.xlsx'

JOBNAME_COLUMN = 'jobName'
TASKNAME = 'Task (ops_notification)'


report_configs_temp = {
    #'reporttitle': 'UAC - Task List Credential By Task',
    'reporttitle': None,
}


def getReport(title_name):
    
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = title_name
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')
    if response_csv.status_code == 200:
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        print("Error generating report")
        return None
    
    
    
def main():
    
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    df_selecting_job = getDataExcel()
    job_list = df_selecting_job[JOBNAME_COLUMN].tolist()
    
    
    df_abort_action = getReport(ABORT_ACTION_REPORT_TITLE)
    df_sys_ops_action = getReport(SYS_OPS_ACTION_REPORT_TITLE)

    
    
    df_abort_action_filtered = df_abort_action[df_abort_action[TASKNAME].isin(job_list)]
    df_sys_ops_action_filtered = df_sys_ops_action[df_sys_ops_action[TASKNAME].isin(job_list)]
    
    createExcel(OUTPUT_EXCEL_NAME, (ABORT_ACTION_SHEETNAME, df_abort_action_filtered), (SYS_OPS_ACTION_SHEETNAME, df_sys_ops_action_filtered))
    

if __name__ == "__main__":
    main()