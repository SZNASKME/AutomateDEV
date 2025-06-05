import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from io import StringIO
from utils.createFile import createExcel, createImagePng
from utils.readFile import loadJson
from utils.stbAPI import *

EXCEL_NAME = 'TEST.png'
IMAGE_REPORT_NAME = 'UAC - Monthly Task Instance Executions'

report_configs_temp = {
    #'reporttitle': 'UAC - Task List Credential By Task',
    #'reporttitle': 'UAC - Monthly Task Instance Executions',
}


def getReport(title_name):
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = title_name
    response_image = runReportAPI(report_configs=report_configs, format_str='image')
    if response_image.status_code == 200:
        image_data = response_image.content
        return image_data
    else:
        print("Error generating report")
        return None
    
    
    
    


def main():
    auth = loadJson('Auth.json')
    userpass = auth['ASKME_STB']
    #userpass = auth['TTB']
    #userpass = auth['TTB_PROD']
    #updateAPIAuth(userpass['API_KEY'])
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.161']
    #domain = domain_url['TTB_UAT']
    #domain = domain_url['TTB_PROD']
    updateURI(domain)
    image_report = getReport(IMAGE_REPORT_NAME)
    if image_report:
        createImagePng(EXCEL_NAME, image_report)
        print(f"Image report saved as {EXCEL_NAME}")
    else:
        print("Failed to generate image report")



if __name__ == '__main__':
    main()