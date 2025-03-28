import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from io import StringIO
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, runReportAPI, updateAPIAuth

EXCEL_NAME = 'AllWorkflowTaskReport.xlsx'

report_configs_temp = {
    #'reporttitle': 'UAC - Task List Credential By Task',
    'reporttitle': 'UAC - Workflow List Of Tasks By Workflow',
}




def getReport():
    
    response_csv = runReportAPI(report_configs=report_configs_temp, format_str='csv')
    if response_csv.status_code == 200:
        print("Report generated successfully")
        #print(response_csv.text)
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        createExcel(EXCEL_NAME, ('Task', df))
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
    getReport()
    
    

if __name__ == '__main__':
    main()
    
    
## Get specific task report