import sys
import os
import pandas as pd
from io import StringIO

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getListTaskAPI, getTaskAPI, updateTaskAPI, runReportAPI
from utils.readFile import loadJson
from utils.createFile import createJson, createExcel

report_configs_temp = {
    'reporttitle': None,
}


SOURCE_REPORT_NAME = 'AskMe - Tasks Report more details'
DES_REPORT_NAME = 'AskMe - Tasks Report more details'

SOURCE_AUTH = 'TTB'
DES_AUTH = 'ASKME_STB'
SOURCE_DOMAIN = 'TTB_UAT'
DES_DOMAIN = '1.86'

def getTaskListFromReport(name):
    
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = name
    
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')

    if response_csv.status_code == 200:
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        print("Report generated successfully")
        return df
    else:
        print("Error generating report")
        return None
    
def updateUACurl(target_auth, target_domain):
    userpass = auth[target_auth]
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    
    domain = domain_url[target_domain]
    updateURI(domain)

def compareTask(source_task_report, des_task_report):
    print(source_task_report)
    print(des_task_report)




def main():
    global auth
    auth = loadJson('auth.json')
    global domain_url
    domain_url = loadJson('Domain.json')
    
    updateUACurl(SOURCE_AUTH, SOURCE_DOMAIN)
    source_task_report = getTaskListFromReport(SOURCE_REPORT_NAME)
    
    # Update the UAC URL
    updateUACurl(DES_AUTH, DES_DOMAIN)
    des_task_report = getTaskListFromReport(DES_REPORT_NAME)

    if source_task_report is None or des_task_report is None:
        print("Error generating report")
        return
    else:
        print("Processing task report...")
        
    compareTask(source_task_report, des_task_report)

    
    
if __name__ == '__main__':
    main()