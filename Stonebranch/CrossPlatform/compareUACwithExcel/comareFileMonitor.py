import sys
import os
import pandas as pd
import re


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import *

REPORT_TITLE = 'AskMe - Agent File Monitors'

JOBNAME = 'jobName'
JOBTYPE = 'jobType'
BOXNAME = 'box_name'
CONDITION = 'condition'
WATCHFILE = 'watch_file'
MACHINE = 'machine'

TASKNAME = 'Name'
MONITORFILE = 'Monitor File(s)'



LOG_SHEET_NAME = 'Agent File Monitor Log'
ERROR_SHEET_NAME = 'Error Log'
OUTPUT_EXCEL_NAME = 'FileMonitor.xlsx'

report_configs_temp = {
    #'reporttitle': 'UAC - Task List Credential By Task',
    'reporttitle': None,
}


format_date_patterns = [
    r"(`[^`]+`)",                        # backticks
    r"(\$\([^\$]*?\$\([^)]+\)[^)]+\))",  # nested shell subshell $() inside $()
    r"(\$\([^)]+\))",                   # shell subshell $()
    r"(\$\{_date\([^\{\}]*\{[^\}]+\}[^\}]*\)\})",  # ${_date(...${...}...)}
    r"(\$\{_date\([^\}]+\)\})"         # ${_date(...)}

]

operation_pairs = [
    {
        'char': r'${FILPTH}',
        'new_char': r'${DWH_EXA_FILPTH}',
        'active_condition': {
            'machine': 'dwhprod_vr'
        },
        'exclude_pairs': []
    },
    {
        'char': r'$FILPTH',
        'new_char': r'${DWH_EXA_FILPTH}',
        'active_condition': {
            'machine': 'dwhprod_vr'
        },
        'exclude_pairs': []
    },
    {
        'char': r'${FXFILPTH}',
        'new_char': r'${DWH_EXA_FXFILPTH}',
        'active_condition': {
            'machine': 'dwhprod_vr'
        },
        'exclude_pairs': []
        
    },
    {
        'char': r'$FXFILPTH',
        'new_char': r'${DWH_EXA_FXFILPTH}',
        'active_condition': {
            'machine': 'dwhprod_vr'
        },
        'exclude_pairs': []
    },
    
    {
        'char': r'${FILPTH}',
        'new_char': r'${DWH_DS_FILPTH}',
        'active_condition': {
            'machine': 'dsdbprd_vr'
        },
        'exclude_pairs': []
    },
    {
        'char': r'$FILPTH',
        'new_char': r'${DWH_DS_FILPTH}',
        'active_condition': {
            'machine': 'dsdbprd_vr'
        },
        'exclude_pairs': []
    },
    # {
    #     'char': r'$FILPTH',
    #     'new_char': r'${DWH_DS_FILPTH}',
    #     'active_condition': {
    #         'machine': 'dsdbprd_vr'
    #     },
    #     'exclude_pairs': []
    # },
    
    
]





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
    

def getFilePath(file_path):

    if file_path.startswith('$'):
        return file_path.split('/', 1)[1] if '/' in file_path else file_path
    return file_path




def comparePath(monitor_file, watch_file):
        
    return monitor_file == watch_file


# def getFormatDate(file_path : str):

#     new_file_path = getFilePath(file_path)
    
#     format_date = []
    
#     for pattern in format_date_patterns:
#         match = re.search(pattern, new_file_path)
#         if match:
#             format_date.append(match.group(0))
    
    
#     return ', '.join(format_date) if format_date else None

def getFormatDate(file_path: str):
    new_file_path = getFilePath(file_path)
    
    combined_pattern = "|".join(format_date_patterns)

    # Find all matches
    matches = list(re.finditer(combined_pattern, new_file_path))

    if not matches:
        return None

    # Determine the outermost match
    start, end = matches[0].span()
    for match in matches[1:]:
        match_start, match_end = match.span()
        if match_start <= start and match_end >= end:
            start, end = match_start, match_end

    return new_file_path[start:end]
            

def replaceFilePath(file_path, string, new_string, exclude_pairs):
    replaced_file_path = file_path
    # Find all exclude ranges
    exclude_ranges = []
    for value in exclude_pairs:
        start = value['start']
        end = value['end']
        for match in re.finditer(f"{re.escape(start)}.*?{re.escape(end)}", replaced_file_path):
            exclude_ranges.append((match.start(), match.end()))
    # Function to check if a position is inside any exclude range
    def isInExcludeRange(pos):
        return any(start <= pos < end for start, end in exclude_ranges)

    # Iterate through text and replace only when outside the excluded ranges
    result = []
    i = 0
    while i < len(replaced_file_path):
        if replaced_file_path[i:i+len(string)] == string and not isInExcludeRange(i):
            result.append(new_string)
            i += len(string)  # Skip past the replaced target
        else:
            result.append(replaced_file_path[i])
            i += 1

    return ''.join(result)


def renewFilePath(text_to_replace, advanced_field_value = None):
    
    have_task_update = False
    
    for operation in operation_pairs:
        char = operation['char']
        new_char = operation['new_char']
        active_condition = operation['active_condition']
        exclude_pairs = operation['exclude_pairs']
        update_text = False
        
        if not active_condition:
            update_text= True
        else:
            update_text = all(advanced_field_value == value for key, value in active_condition.items())
        
        if text_to_replace and update_text:
            
            if char in text_to_replace:
                replaced_text = replaceFilePath(text_to_replace, char, new_char, exclude_pairs)
                have_task_update = True

    if not have_task_update:
        replaced_text = text_to_replace
    #print(replaced_text)
    return replaced_text


def compareFileMonitor(df_job, df_file_monitor, df_file_monitor_exclude):
    
    file_monitor_log = []
    error_log = []
    
    agent_file_monitor_dict = df_file_monitor.set_index(TASKNAME).to_dict(orient='index')
    agent_file_monitor_exclude_list = df_file_monitor_exclude[TASKNAME].tolist()
    
    df_job_file_monitor = df_job[df_job[JOBTYPE] == 'FW']
    
    for row in df_job_file_monitor.itertuples(index=False):
        job_name = getattr(row, JOBNAME)
        box_name = getattr(row, BOXNAME)
        watch_file = getattr(row, WATCHFILE)
        machine = getattr(row, MACHINE)

        if job_name in agent_file_monitor_exclude_list:
            error_log.append({
                'Name': job_name,
                BOXNAME: box_name,
                'Status': 'File Monitor Go-Lived',
                MONITORFILE: watch_file,
            })
            continue
        
        monitor_file = agent_file_monitor_dict.get(job_name, {}).get(MONITORFILE, None)
    
        if monitor_file is None:
            #print(f"No monitor file found for job: {job_name} in box: {box_name}")
            error_log.append({
                'Name': job_name,
                BOXNAME: box_name,
                'Status': 'No monitor file found in UAC',
                WATCHFILE: watch_file,
            })
            continue
        
        watch_file_format_date = getFormatDate(watch_file)
        monitor_file_format_date = getFormatDate(monitor_file)
        
        has_format_date = None
        if watch_file_format_date and monitor_file_format_date:
            has_format_date = 'Both'
        elif watch_file_format_date and not monitor_file_format_date:            
            has_format_date = 'Only Job Master'
        elif not watch_file_format_date and monitor_file_format_date:
            has_format_date = 'Only UAC'
        else:
            has_format_date = 'No Format Date'
        
        watch_file_result_path = renewFilePath(watch_file, machine)
        watch_file_for_compare = watch_file_result_path.replace(watch_file_format_date, '') if watch_file_format_date else watch_file_result_path
        monitor_file_for_compare = monitor_file.replace(monitor_file_format_date, '') if monitor_file_format_date else monitor_file
        file_monitor_log.append({
            JOBNAME: job_name,
            BOXNAME: box_name,
            f'Original {WATCHFILE}': watch_file,
            MACHINE: machine,
            'Same Path': 'TRUE' if comparePath(monitor_file_for_compare, watch_file_for_compare) else 'FALSE',
            f'Renew {WATCHFILE}': watch_file_result_path,
            MONITORFILE: monitor_file,
            'Format Date Status': has_format_date,
            'Job Master Format Date': watch_file_format_date,
            'UAC Format Date': monitor_file_format_date
            
        })            
    
    
    for name, monitor_file in agent_file_monitor_dict.items():
        if name not in df_job_file_monitor[JOBNAME].values:
            #print(f"Job {name} not found in Job List")
            error_log.append({
                'Name': name,
                'Status': 'No monitor file found in Job List',
                MONITORFILE: monitor_file[MONITORFILE],
            })
    
    
    df_file_monitor_log = pd.DataFrame(file_monitor_log)
    df_error_log = pd.DataFrame(error_log)
    
    return df_file_monitor_log, df_error_log

    
    
def main():
    
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    df_file_monitor = getReport(REPORT_TITLE)
    
    userpass_exclude = auth['ASKME_STB']
    updateAuth(userpass_exclude['USERNAME'], userpass_exclude['PASSWORD'])
    domain_exclude = domain_url['1.174']
    updateURI(domain_exclude)
    
    df_file_monitor_exclude = getReport(REPORT_TITLE)
    
    #df_file_monitor = df_file_monitor_main[~df_file_monitor_main[TASKNAME].isin(df_file_monitor_exclude[TASKNAME])]
    
    
    df_job = getDataExcel()
    
    df_file_monitor_log, df_error_log = compareFileMonitor(df_job, df_file_monitor, df_file_monitor_exclude)

    
    
    
    createExcel(OUTPUT_EXCEL_NAME, (LOG_SHEET_NAME, df_file_monitor_log),(ERROR_SHEET_NAME, df_error_log))


if __name__ == "__main__":
    main()