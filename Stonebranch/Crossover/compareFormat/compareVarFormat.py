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


TASK_REPORT_NAME = 'AskMe - Tasks Report'
FILE_MONITOR_REPORT_NAME = 'AskMe - Agent File Monitor Report'

# JIL Columns
APPNAME_COLUMN = 'AppName'
JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'

PROFILE_COLUMN = 'profile'
COMMAND_COLUMN = 'command'
STDOUT_COLUMN = 'std_out_file'
STDERR_COLUMN = 'std_err_file'
MACHINE_COLUMN = 'machine'
OWNER_COLUMN = 'owner'
WATCH_FILE_COLUMN = 'watch_file'


# UAC Columns
UAC_TASK_COLUMN = 'Name'
UAC_PROFILE_COLUMN = 'Profile File'
UAC_AGENT_CLUSTER_COLUMN = 'Agent Cluster'
UAC_CREDENTIAL_COLUMN = 'Credentials'
UAC_COMMAND_COLUMN = 'Command'
UAC_STDOUT_COLUMN = 'STDOUT File'
UAC_STDERR_COLUMN = 'STDERR File'
UAC_FILE_MONITOR_COLUMN = 'Monitor File(s)'
UAC_MIN_FILE_SIZE_COLUMN = 'Minimum File Size'

# Compare result
TRUE_COMPARE = 'Yes'
FALSE_COMPARE = 'No'

FORMAT_DATE_COLUMN = 'Format Date'
VARIABLE_PATH_COLUMN = 'Variable Path'

OUTPUT_EXCEL_NAME = 'TaskReport.xlsx'


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


def compareValueNormal(value1, value2):
    if value1 != value2:
        return FALSE_COMPARE
    else:
        return TRUE_COMPARE


def compareTaskValue(row_jil, row_task_report, format_date, variable_path):
    result = {}
    
    # compare command
    row_jil_command = row_jil[COMMAND_COLUMN]
    if not '$(date' in row_jil_command:
        row_jil_command = row_jil_command.replace('\"', '\\\"')
    result[UAC_COMMAND_COLUMN] = compareValueNormal(row_jil_command, row_task_report[UAC_COMMAND_COLUMN])
    
    # compare stdout
    row_jil_stdout = row_jil[STDOUT_COLUMN]
    row_jil_stdout = re.sub('AUTO_JOB_NAME', r'{ops_task_name}', row_jil_stdout)
    row_jil_stdout = row_jil_stdout.replace('\%', '%')
    result[UAC_STDOUT_COLUMN] = compareValueNormal(row_jil_stdout, row_task_report[UAC_STDOUT_COLUMN])

    # compare stderr
    row_jil_stderr = row_jil[STDERR_COLUMN]
    row_jil_stderr = re.sub('AUTO_JOB_NAME', r'{ops_task_name}', row_jil_stderr)
    row_jil_stderr = row_jil_stderr.replace('\%', '%')
    result[UAC_STDERR_COLUMN] = compareValueNormal(row_jil_stderr, row_task_report[UAC_STDERR_COLUMN])
    
    # compare Agent Cluster
    result[UAC_AGENT_CLUSTER_COLUMN] = compareValueNormal(row_jil[MACHINE_COLUMN], row_task_report[UAC_AGENT_CLUSTER_COLUMN])
        
    # compare Credentials
    result[UAC_CREDENTIAL_COLUMN] = compareValueNormal(row_jil[OWNER_COLUMN], row_task_report[UAC_CREDENTIAL_COLUMN])
        
    # compare format date
    result[FORMAT_DATE_COLUMN] = compareValueNormal(format_date['JIL'], format_date['STB'])
    
    # compare variable path
    result[VARIABLE_PATH_COLUMN] = compareValueNormal(variable_path['JIL'], variable_path['STB'])
    
    return result
    
def compareFileMonitorValue(row_jil, row_file_monitor_report, format_date, variable_path):
    result = {}
    
    # compare watch file
    result[UAC_FILE_MONITOR_COLUMN] = compareValueNormal(row_jil[WATCH_FILE_COLUMN], row_file_monitor_report[UAC_FILE_MONITOR_COLUMN])
        
    # compare Agent Cluster
    result[UAC_AGENT_CLUSTER_COLUMN] = compareValueNormal(row_jil[MACHINE_COLUMN], row_file_monitor_report[UAC_AGENT_CLUSTER_COLUMN])
        
    # compare Credentials
    result[UAC_CREDENTIAL_COLUMN] = compareValueNormal(row_jil[OWNER_COLUMN], row_file_monitor_report[UAC_CREDENTIAL_COLUMN])
    
    # compare format date
    result[FORMAT_DATE_COLUMN] = compareValueNormal(format_date['JIL'], format_date['STB'])
    
    # compare variable path
    result[VARIABLE_PATH_COLUMN] = compareValueNormal(variable_path['JIL'], variable_path['STB'])
    
    
    #print(result)
    return result



############################################################################################################
def extractOutermostPatterns(text, start_pattern, end_pattern, start_len=0):
    
    stack = []
    results = []
    
    i = 0
    while i < len(text):
        if text[i:i+start_len] == start_pattern:  # Start of a new pattern
            stack.append(i)
        elif text[i] == end_pattern and stack:  # Closing brace for a pattern
            start = stack.pop()
            if not stack:  # Only store the outermost pattern
                results.append(text[start:i+1])
        i += 1
    
    return results

def getTaskFormatDate(row_jil, row_task_report):
    format_date = {}
    
    jil_matches = extractOutermostPatterns(row_jil[COMMAND_COLUMN], '$(date', ')', 6)
    task_matches = extractOutermostPatterns(row_task_report[UAC_COMMAND_COLUMN], '$(date', ')', 6)
    
    format_date['JIL'] = ','.join(jil_matches)
    format_date['STB'] = ','.join(task_matches)
    
    return format_date

def getFileMonitorFormatDate(row_jil, row_file_monitor_report):
    format_date = {}
    
    jil_matches = extractOutermostPatterns(row_jil[WATCH_FILE_COLUMN], '$(date', ')', 6)
    task_matches = extractOutermostPatterns(row_file_monitor_report[UAC_FILE_MONITOR_COLUMN], '${_date', '}', 7)
    
    format_date['JIL'] = ','.join(jil_matches)
    format_date['STB'] = ','.join(task_matches)
    
    return format_date

############################################################################################################
def removeIndexContainIn(list_data, pattern):
    return [data for data in list_data if pattern not in data]

def getVariablePath(row_jil, row_task_report, jil_column, task_column):
    variable_path = {}
    pattern = r"(\$\{.*?\})|(\$.*?\/)"
    
    jil_matches = re.findall(pattern, row_jil[jil_column])
    jil_matches = [match[0] if match[0] else match[1].replace('/','') for match in jil_matches]
    jil_matches = removeIndexContainIn(jil_matches, 'date')
    jil_matches = removeIndexContainIn(jil_matches, 'TZ')
    
    task_matches = re.findall(pattern, row_task_report[task_column])
    task_matches = [match[0] if match[0] else match[1].replace('/','') for match in task_matches]
    task_matches = removeIndexContainIn(task_matches, 'date')
    task_matches = removeIndexContainIn(task_matches, 'TZ')

    variable_path['JIL'] = ','.join(jil_matches)
    variable_path['STB'] = ','.join(task_matches)
    
    return variable_path



############################################################################################################


def createCompareTaskRow(row_jil, row_task_report, format_date, variable_path, compare_result):
    row_data = {}
    row_data[APPNAME_COLUMN] = row_jil[APPNAME_COLUMN]
    row_data[JOBNAME_COLUMN] = row_jil[JOBNAME_COLUMN]
    row_data[BOXNAME_COLUMN] = row_jil[BOXNAME_COLUMN]
    
    row_data['JIL ' + COMMAND_COLUMN] = row_jil[COMMAND_COLUMN]
    row_data['STB ' + UAC_COMMAND_COLUMN] = row_task_report[UAC_COMMAND_COLUMN]
    row_data[UAC_COMMAND_COLUMN + ' Compare'] = compare_result[UAC_COMMAND_COLUMN]
    
    row_data['JIL ' + STDOUT_COLUMN] = row_jil[STDOUT_COLUMN]
    row_data['STB ' + UAC_STDOUT_COLUMN] = row_task_report[UAC_STDOUT_COLUMN]
    row_data[UAC_STDOUT_COLUMN + ' Compare'] = compare_result[UAC_STDOUT_COLUMN]
    
    row_data['JIL ' + STDERR_COLUMN] = row_jil[STDERR_COLUMN]
    row_data['STB ' + UAC_STDERR_COLUMN] = row_task_report[UAC_STDERR_COLUMN]
    row_data[UAC_STDERR_COLUMN + ' Compare'] = compare_result[UAC_STDERR_COLUMN]
    
    row_data['JIL ' + MACHINE_COLUMN] = row_jil[MACHINE_COLUMN]
    row_data['STB ' + UAC_AGENT_CLUSTER_COLUMN] = row_task_report[UAC_AGENT_CLUSTER_COLUMN]
    row_data[UAC_AGENT_CLUSTER_COLUMN + ' Compare'] = compare_result[UAC_AGENT_CLUSTER_COLUMN]
    
    row_data['JIL ' + OWNER_COLUMN] = row_jil[OWNER_COLUMN]
    row_data['STB ' + UAC_CREDENTIAL_COLUMN] = row_task_report[UAC_CREDENTIAL_COLUMN]
    row_data[UAC_CREDENTIAL_COLUMN + ' Compare'] = compare_result[UAC_CREDENTIAL_COLUMN]
    
    row_data['JIL ' + VARIABLE_PATH_COLUMN] = variable_path['JIL']
    row_data['STB ' + VARIABLE_PATH_COLUMN] = variable_path['STB']
    row_data[VARIABLE_PATH_COLUMN + ' Compare'] = compare_result[VARIABLE_PATH_COLUMN]
    
    row_data['JIL ' + FORMAT_DATE_COLUMN] = format_date['JIL']
    row_data['STB ' + FORMAT_DATE_COLUMN] = format_date['STB']
    row_data[FORMAT_DATE_COLUMN + ' Compare'] = compare_result[FORMAT_DATE_COLUMN]
    
    
    return row_data

def createCompareFileMonitorRow(row_jil, row_file_monitor_report, format_date, variable_path, compare_result):
    row_data = {}
    row_data[APPNAME_COLUMN] = row_jil[APPNAME_COLUMN]
    row_data[JOBNAME_COLUMN] = row_jil[JOBNAME_COLUMN]
    row_data[BOXNAME_COLUMN] = row_jil[BOXNAME_COLUMN]
    
    row_data['JIL ' + WATCH_FILE_COLUMN] = row_jil[WATCH_FILE_COLUMN]
    row_data['STB ' + UAC_FILE_MONITOR_COLUMN] = row_file_monitor_report[UAC_FILE_MONITOR_COLUMN]
    row_data[UAC_FILE_MONITOR_COLUMN + ' Compare'] = compare_result[UAC_FILE_MONITOR_COLUMN]
    
    row_data['JIL ' + MACHINE_COLUMN] = row_jil[MACHINE_COLUMN]
    row_data['STB ' + UAC_AGENT_CLUSTER_COLUMN] = row_file_monitor_report[UAC_AGENT_CLUSTER_COLUMN]
    row_data[UAC_AGENT_CLUSTER_COLUMN + ' Compare'] = compare_result[UAC_AGENT_CLUSTER_COLUMN]
    
    row_data['JIL ' + OWNER_COLUMN] = row_jil[OWNER_COLUMN]
    row_data['STB ' + UAC_CREDENTIAL_COLUMN] = row_file_monitor_report[UAC_CREDENTIAL_COLUMN]
    row_data[UAC_CREDENTIAL_COLUMN + ' Compare'] = compare_result[UAC_CREDENTIAL_COLUMN]
    
    row_data['JIL ' + VARIABLE_PATH_COLUMN] = variable_path['JIL']
    row_data['STB ' + VARIABLE_PATH_COLUMN] = variable_path['STB']
    row_data[VARIABLE_PATH_COLUMN + ' Compare'] = compare_result[VARIABLE_PATH_COLUMN]
    
    row_data['JIL ' + FORMAT_DATE_COLUMN] = format_date['JIL']
    row_data['STB ' + FORMAT_DATE_COLUMN] = format_date['STB']
    row_data[FORMAT_DATE_COLUMN + ' Compare'] = compare_result[FORMAT_DATE_COLUMN]
    
    return row_data



def cleanNoneDF(df):
    df = df.astype(str).fillna('')
    df = df.replace('nan', '')
    return df

def compareFormat(df_jil, list_dict, df_task_report, df_file_monitor_report):
    all_list = [job_name for job_name_list in list_dict.values() for job_name in job_name_list]
    
    df_jil = cleanNoneDF(df_jil)
    df_task_report = cleanNoneDF(df_task_report)
    df_file_monitor_report = cleanNoneDF(df_file_monitor_report)
    
    print("Comparing formats")
    #print(df_jil.columns)
    df_jil_in_list = df_jil[df_jil[JOBNAME_COLUMN].isin(all_list)]
    #print(len(all_list))
    #print(df_task_report.columns)
    df_task_report_in_list = df_task_report[df_task_report[UAC_TASK_COLUMN].isin(all_list)]
    #print(df_file_monitor_report.columns)
    df_file_monitor_report_in_list = df_file_monitor_report[df_file_monitor_report[UAC_TASK_COLUMN].isin(all_list)]
    
    print("JIL in list: ", len(df_jil_in_list))
    print("Command Task in list: ", len(df_task_report_in_list))
    print("File monitor in list: ", len(df_file_monitor_report_in_list))
    
    #print("JIL not in list: ", len(df_jil) - len(df_jil_in_list))
    #print("Task not in list: ", len(df_task_report) - len(df_task_report_in_list))
    #print("File monitor not in list: ", len(df_file_monitor_report) - len(df_file_monitor_report_in_list))
    task_in_list = []
    file_monitor_in_list = []
    
    for index, row in df_jil_in_list.iterrows():
        job_name = row[JOBNAME_COLUMN]
        
        task_row_data = df_task_report_in_list[df_task_report_in_list[UAC_TASK_COLUMN] == job_name]
        file_monitor_row_data = df_file_monitor_report_in_list[df_file_monitor_report_in_list[UAC_TASK_COLUMN] == job_name]
        
        row_compare = {}

        if len(task_row_data) != 0:
            task_row_data = task_row_data.iloc[0]
            format_date = getTaskFormatDate(row, task_row_data)
            variable_path = getVariablePath(row, task_row_data, COMMAND_COLUMN, UAC_COMMAND_COLUMN)
            compare_task_result = compareTaskValue(row, task_row_data, format_date, variable_path)
            
            row_data = createCompareTaskRow(row, task_row_data, format_date, variable_path, compare_task_result)
            task_in_list.append(row_data)
            
        if len(file_monitor_row_data) != 0:
            row_compare[JOBNAME_COLUMN] = job_name
            file_monitor_row_data = file_monitor_row_data.iloc[0]
            format_date = getFileMonitorFormatDate(row, file_monitor_row_data)
            variable_path = getVariablePath(row, file_monitor_row_data, WATCH_FILE_COLUMN, UAC_FILE_MONITOR_COLUMN)
            compare_file_monitor_result =  compareFileMonitorValue(row, file_monitor_row_data, format_date, variable_path)
            
            row_data = createCompareFileMonitorRow(row, file_monitor_row_data, format_date, variable_path, compare_file_monitor_result)
            file_monitor_in_list.append(row_data)
            
        if len(task_row_data) == 0 and len(file_monitor_row_data) == 0:
            continue
    print("Results")
    print("Task in list: ", len(task_in_list))
    print("File monitor in list: ", len(file_monitor_in_list))
    
    df_command = pd.DataFrame(task_in_list)
    df_file_monitor = pd.DataFrame(file_monitor_in_list)
    return df_command, df_file_monitor
    
            
        

    
def main():
    
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    df_jil = getDataExcel('get Excel path with main job file')
    root_list_option = input("Do you want to use the root or list? (r/l): ")
    if root_list_option == 'r':
        df_root = getDataExcel("Enter the path of the excel file with the root jobs")
    df_list_job = getDataExcel("Enter the path of the excel file with the list of jobs")
    list_job_name = df_list_job[JOBNAME_COLUMN].tolist()
    if root_list_option == 'r':
        list_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, list_job_name)
    else:
        list_dict = getSpecificColumn(df_jil, SELECTED_COLUMN, None, list_job_name)
    print("---------------------------------")
    for key, value in list_dict.items():
        print(key, len(value))
    print("---------------------------------")
    df_task_report = getReport(TASK_REPORT_NAME)
    df_file_monitor_report = getReport(FILE_MONITOR_REPORT_NAME)
    
    df_command, df_file_monitor = compareFormat(df_jil, list_dict, df_task_report, df_file_monitor_report)
    createExcel(OUTPUT_EXCEL_NAME, ('Command', df_command), ('File Monitor', df_file_monitor))
    
    
    
    
if __name__ == '__main__':
    main()