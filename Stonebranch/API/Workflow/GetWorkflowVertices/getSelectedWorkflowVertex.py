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

VERTEX_REPORT_TITLE = 'UAC - Workflow List Of Tasks By Workflow'



OUTPUT_EXCEL_NAME = 'Vertex Case UAT.xlsx'
EXCEL_SHEET_NAME = 'Vetex Select'




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
    #userpass = auth['TTB_PROD']
    #updateAPIAuth(userpass['API_KEY'])

    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_PROD']
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    df_vertex = getReport(VERTEX_REPORT_TITLE)
    
    df_selecting = getDataExcel()
    
    df_selecting_vertex = df_vertex[df_vertex['Workflow'].isin(df_selecting['Name'])]
    
    createExcel(OUTPUT_EXCEL_NAME, (EXCEL_SHEET_NAME, df_selecting_vertex))
    

if __name__ == "__main__":
    main()