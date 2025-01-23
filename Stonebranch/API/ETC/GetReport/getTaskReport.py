import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from io import StringIO
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, runReportAPI

EXCEL_NAME = 'TaskReport.xlsx'

report_configs_temp = {
    'reporttitle': 'AskMe - Tasks Report',
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
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    getReport()
    
    

if __name__ == '__main__':
    main()
    
    
## Get specific task report