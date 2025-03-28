import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from io import StringIO
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, runReportAPI, updateAPIAuth, clearAuth
from utils.readExcel import getDataExcel

#OUTPUT_TASK_EXCEL_NAME = 'AllTaskReport.xlsx'
#OUTPUT_WORKFLOW_EXCEL_NAME = 'AllWorkflowTaskReport.xlsx'
COMPARE_EXCEL_NAME = 'Comparison_Workflow_Report.xlsx'

REPORT_TASK_TITLE = 'UAC - Task List Credential By Task'
REPORT_WORKFLOW_TITLE = 'UAC - Workflow List Of Tasks By Workflow'

WORKFLOW = 'Workflow'
TASKNAME = 'Name'

report_configs_temp = {
    'reporttitle': None,
}




def getReport(report_title):
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = report_title
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')
    if response_csv.status_code == 200:
        print("Report generated successfully")
        #print(response_csv.text)
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        #createExcel(excel_name, ('Task', df))
        return df
    else:
        print("Error generating report")
        return None


def compareWorkflow(df_workflow_prod, df_workflow_uat):
    
    compare_list = []
    compare_log = []
    
    prod_workflow_list = df_workflow_prod[WORKFLOW].tolist()
    uat_workflow_list = df_workflow_uat[WORKFLOW].tolist()
    
    merge_workflow_list = list(set(prod_workflow_list) | set(uat_workflow_list))
    
    for workflow_name in merge_workflow_list:

        df_prod_child = df_workflow_prod[df_workflow_prod[WORKFLOW] == workflow_name]
        df_uat_child = df_workflow_uat[df_workflow_uat[WORKFLOW] == workflow_name]
        
        if df_prod_child.empty and df_uat_child.empty:
            compare_log.append({'Workflow': workflow_name, 'Status': 'Not in both PROD and UAT'})
            continue
        elif not df_prod_child.empty and not df_uat_child.empty:
            compare_log.append({'Workflow': workflow_name, 'Status': 'In both PROD and UAT'})
        elif not df_prod_child.empty:
            compare_log.append({'Workflow': workflow_name, 'Status': 'In PROD only'})
        elif not df_uat_child.empty:
            compare_log.append({'Workflow': workflow_name, 'Status': 'In UAT only'})
        
        prod_task_list = df_prod_child['Task'].tolist()
        uat_task_list = df_uat_child['Task'].tolist()
        
        merge_task_list = list(set(prod_task_list) | set(uat_task_list))
        
        for task_name in merge_task_list:
            if task_name in prod_task_list and task_name in uat_task_list:
                compare_list.append({'Workflow': workflow_name, 'Task': task_name, 'Status': 'In both PROD and UAT'})
            elif task_name in prod_task_list:
                compare_list.append({'Workflow': workflow_name, 'Task': task_name, 'Status': 'In PROD only'})
            elif task_name in uat_task_list:
                compare_list.append({'Workflow': workflow_name, 'Task': task_name, 'Status': 'In UAT only'})
    
    df_prod_workflow_list = pd.DataFrame(list(set(prod_workflow_list)), columns=[WORKFLOW])
    df_workflow_compare = pd.DataFrame(compare_list)
    df_workflow_compare_log = pd.DataFrame(compare_log)
    
    return df_prod_workflow_list, df_workflow_compare, df_workflow_compare_log
    

def compareTask(df_task_prod, df_task_uat):
    
    prod_task_list = df_task_prod[TASKNAME].tolist()
    uat_task_list = df_task_uat[TASKNAME].tolist()
    
    merge_task_list = list(set(prod_task_list) | set(uat_task_list))
    compare_list = []
    
    for task_name in merge_task_list:
        if task_name in prod_task_list and task_name in uat_task_list:
            compare_list.append({'Task': task_name, 'Status': 'In both PROD and UAT'})
        elif task_name in prod_task_list:
            compare_list.append({'Task': task_name, 'Status': 'In PROD only'})
        elif task_name in uat_task_list:
            compare_list.append({'Task': task_name, 'Status': 'In UAT only'})
            
    df_task_compare = pd.DataFrame(compare_list)
    return df_task_compare
            
    
    
def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB_PROD']
    updateAPIAuth(userpass['API_KEY'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_PROD']
    updateURI(domain)
    df_workflow_prod = getReport(REPORT_WORKFLOW_TITLE)
    df_task_prod = getReport(REPORT_TASK_TITLE)
    
    clearAuth()
    
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    df_workflow_uat = getReport(REPORT_WORKFLOW_TITLE)
    df_task_uat = getReport(REPORT_TASK_TITLE)
    
    # Compare the two dataframes
    
    print("Comparing workflow...")
    prod_workflow_list, workflow_comparison_result, workflow_comparison_log = compareWorkflow(df_workflow_prod, df_workflow_uat)
    print("Comparing task...")
    task_comparison_result = compareTask(df_task_prod, df_task_uat)
    print("Comparison completed.")

    
    
    # Save the comparison result to an Excel file
    createExcel(COMPARE_EXCEL_NAME, ('PROD Workflow', prod_workflow_list), ('Workflow Compare', workflow_comparison_result), ('Workflow Compare Log', workflow_comparison_log), ('Task', task_comparison_result))
    #print(f"Comparison report saved as {COMPARE_EXCEL_NAME}.")

if __name__ == '__main__':
    main()
    
    
## Get specific task report