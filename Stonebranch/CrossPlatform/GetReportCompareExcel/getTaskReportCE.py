import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from io import StringIO
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, runReportAPI, updateAPIAuth
from utils.readExcel import getDataExcel

OUTPUT_TASK_EXCEL_NAME = 'AllTaskReport.xlsx'
OUTPUT_WORKFLOW_EXCEL_NAME = 'AllWorkflowTaskReport.xlsx'

REPORT_TASK_TITLE = 'UAC - Task List Credential By Task'
REPORT_WORKFLOW_TITLE = 'UAC - Workflow List Of Tasks By Workflow'



report_configs_temp = {
    'reporttitle': None,
}




def getReport(report_title, excel_name):
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = report_title
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')
    if response_csv.status_code == 200:
        print("Report generated successfully")
        #print(response_csv.text)
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        createExcel(excel_name, ('Task', df))
        return df
    else:
        print("Error generating report")
        return None
    
    
    
    
def main():
    auth = loadJson('Auth.json')
    #userpass = auth['TTB']
    userpass = auth['TTB_PROD']
    updateAPIAuth(userpass['API_KEY'])
    #updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['TTB_PROD']
    updateURI(domain)
    df_workflow = getReport(REPORT_WORKFLOW_TITLE, OUTPUT_WORKFLOW_EXCEL_NAME)
    
    df_task = getReport(REPORT_TASK_TITLE, OUTPUT_TASK_EXCEL_NAME)
    

if __name__ == '__main__':
    main()
    
    
## Get specific task report