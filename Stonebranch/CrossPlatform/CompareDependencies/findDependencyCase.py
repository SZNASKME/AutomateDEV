import sys
import os
import pandas as pd
import re
import json
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson
from utils.readFile import loadJson
from utils.stbAPI import *

VERTEX_REPORT_TITLE = 'AskMe - Workflow Vertices'
DEPEN_REPORT_TITLE = 'AskMe - Workflow Dependencies'
WORKFLOW_REPORT_TITLE = 'AskMe - Workflow Report'
TASK_MONITOR_TRIGGER_REPORT_TITLE = 'AskMe - Task Monitor Triggers'

TASK_REPORT_TITLE = 'AskMe - Task Report'



CONDITION_SHEETNAME = 'All Conditions'
NON_SIMILAR_CONDITION_SHEETNAME = 'Non Similar Condition'
GOLIVED_NOT_IN_PROCESS = 'Golived Task Not in UAT Task'

OUTPUT_EXCEL_NAME = 'CompareDependency.xlsx'

PATTERN = r'\b[sfd]\([^\)]+\)'

JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
BOX_NAME_COLUMN = 'box_name'


TASK_COLUMN = 'Taskname'
TASK_REPORT_COLUMN = 'Name'

TASK_MONITOR_COLUMN = 'TaskMonitor'
TASKS_COLUMN = 'Tasks'


TASK_MONITOR_SUFFIX = '-TM'
TASK_MONITOR_OF_TRIGGER_SUFFIX = '-ND-TM'

exclude_condition_containing = [
    'Start_'
]

break_through_condition = [
    'startDummy'
]


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




#################################################################################


def prepareWorkflowVertexDict(df_workflow_vertex, workflow_list):
    workflow_vertex_dict = {}
    filtered_df = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(workflow_list)]

    for _, row in filtered_df.iterrows():
        workflow = row['Workflow']
        vertex_id = row['Vertex Id']
        task_name = row['Task']

        if workflow not in workflow_vertex_dict:
            workflow_vertex_dict[workflow] = {}
        workflow_vertex_dict[workflow][vertex_id] = task_name

    for workflow in workflow_list:
        if workflow not in workflow_vertex_dict:
            workflow_vertex_dict[workflow] = {}

    return workflow_vertex_dict

def prepareTaskVertexDict(df_workflow_vertex, workflow_list):
    task_vertex_dict = {}
    filtered_df = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(workflow_list)]

    for _, row in filtered_df.iterrows():
        workflow_name = row['Workflow']
        vertex_id = row['Vertex Id']
        task_name = row['Task']

        if task_name not in task_vertex_dict:
            task_vertex_dict[task_name] = []
        if workflow_name not in task_vertex_dict[task_name]:
            task_vertex_dict[task_name].append(workflow_name)

    return task_vertex_dict
    

def createDependencyDict(df_workflow_depen, workflow_vertex_dict):
    depen_dict = {}
    grouped_workflow_depen_dict = df_workflow_depen.groupby('Workflow')
    
    for workflow, group in grouped_workflow_depen_dict:
        if workflow not in depen_dict:
            depen_dict[workflow] = []
        
        for _, row in group.iterrows():
            source_vertex_id = row['Source Vertex Id']
            target_vertex_id = row['Target Vertex Id']
            condition = row['Condition']

            source_task = workflow_vertex_dict[workflow].get(source_vertex_id, None)
            target_task = workflow_vertex_dict[workflow].get(target_vertex_id, None)
            
            #####
            #if source_task is None or target_task is None:
            #    continue
            
            if any(exclude in source_task for exclude in exclude_condition_containing) or any(exclude in target_task for exclude in exclude_condition_containing):
                continue
            #####
            
            if source_task and target_task:
                depen_dict[workflow].append({
                    'Source Vertex Id': source_vertex_id,
                    'Source Task': source_task,
                    'Target Vertex Id': target_vertex_id,
                    'Target Task': target_task,
                    'Condition': condition
                })


    return depen_dict

def prepareTaskDependencyDict(workflow_list, workflow_depen_dict):
    task_depen_dict = {}
    for workflow_name in workflow_list:
        if workflow_name in workflow_depen_dict:
            for depen in workflow_depen_dict[workflow_name]:
                source_task = depen['Source Task'].replace(TASK_MONITOR_SUFFIX, '')
                target_task = depen['Target Task'].replace(TASK_MONITOR_SUFFIX, '')
                condition = depen['Condition']
                if target_task not in task_depen_dict:
                    task_depen_dict[target_task] = []
                task_depen_dict[target_task].append({
                    'Workflow': workflow_name,
                    'Source Task': source_task,
                    'Condition': condition
                })
        #else:
        #    task_depen_dict[workflow_name] = []

    return task_depen_dict


def prepareTaskMonitorTriggerDependencyDict(df_task_monitor_trigger):
    task_monitor_trigger_dict = {}
    df_task_monitor_trigger = df_task_monitor_trigger.rename(columns={'Task Monitor': TASK_MONITOR_COLUMN, 'Task(s)': TASKS_COLUMN})
    for row in df_task_monitor_trigger.itertuples():
        
        source_task = getattr(row, TASK_MONITOR_COLUMN)
        #print(source_task)
        source_task = source_task.replace(TASK_MONITOR_OF_TRIGGER_SUFFIX, '')
        target_task_list = getattr(row, TASKS_COLUMN)
        target_task_list = target_task_list.split(',') if isinstance(target_task_list, str) else []
        #print(target_task_list)
        target_task_list = [task.strip() for task in target_task_list if task.strip()]  # Remove empty strings
        for target_task in target_task_list:
            if target_task not in task_monitor_trigger_dict:
                task_monitor_trigger_dict[target_task] = []
            task_monitor_trigger_dict[target_task].append({
                'Workflow': 'Task Monitor Trigger',
                'Source Task': source_task,
                'Condition': 'Success'
            })
            
    return task_monitor_trigger_dict


def combineDepenDict(task_depen_dict, task_monitor_trigger_depen_dict):
    combined_task_depen_dict = task_depen_dict.copy()
    
    for target_task, depen_list in task_monitor_trigger_depen_dict.items():
        if target_task not in combined_task_depen_dict:
            combined_task_depen_dict[target_task] = []
        combined_task_depen_dict[target_task].extend(depen_list)
    
    return combined_task_depen_dict



##############################################################################



##############################################################################

def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list


def getAllInnermostSubstringsWithStatus(string, pattern):
    matches = re.findall(pattern, string)
    return matches

def getConditionList(condition):
    condition_list = getAllInnermostSubstringsWithStatus(condition, PATTERN)
    return condition_list

def createStatusCondition(status_condition):
    status_condition_select = {
        'Success': 's',
        'Failure': 'f',
        'Success/Failure': 'd'
    }
    return status_condition_select.get(status_condition, None)


#####
def compareConditionString(condition_string, task_condition_string):
    
    job_condition_list = getConditionList(condition_string)
    task_condition_list = getConditionList(task_condition_string)
    
    both_condition = []
    only_found_in_job_condition = []
    only_found_in_task_condition = []
    for job_condition in job_condition_list:
        if job_condition in task_condition_list:
            both_condition.append(job_condition)
        else:
            only_found_in_job_condition.append(job_condition)
    
    for task_condition in task_condition_list:
        if task_condition not in job_condition_list:
            only_found_in_task_condition.append(task_condition)

    return both_condition, only_found_in_job_condition, only_found_in_task_condition


def prepareCompareCondition(df_job, task_depen_dict, task_monitor_trigger_depen_dict, task_vertex_dict, df_processing_task, df_golived_task):
    all_condition_log = []
    non_simular_condition = []
    processing_task_set = set(df_processing_task[TASK_COLUMN].tolist())
    golived_task_set = set(df_golived_task[TASK_COLUMN].tolist())
    
    business_services_map = df_processing_task.set_index(TASK_COLUMN)['Member of Business Services'].to_dict()
    total_count = len(df_job)
    count = 0
    for row in df_job.itertuples():
        job_name = getattr(row, JOBNAME_COLUMN)
        job_condition = getattr(row, CONDITION_COLUMN)
        box_name = getattr(row, BOX_NAME_COLUMN)
        
        if pd.isna(job_condition):
            job_condition = ''

        
        task_condition_list = []
        advance_task_condition_list = []
        
        task_depen_list = task_depen_dict.get(job_name, [])
        task_monitor_trigger_depen_list = task_monitor_trigger_depen_dict.get(job_name, [])
        #print(json.dumps(task_depen_list, indent=4))
        #if job_condition and task_depen_list == []:
        #    print(f'{job_name} | {job_condition} : {task_condition_list}')
        if task_depen_list:
            for condition_dict in task_depen_list:
                #print(condition_dict)
                workflow_name = condition_dict['Workflow']
                source_task = condition_dict['Source Task']
                condition = condition_dict['Condition']
                
                new_structure_condition = f'{createStatusCondition(condition)}({source_task})'
                task_condition_list.append(new_structure_condition)
                new_advance_structure_condition = f'{createStatusCondition(condition)}({source_task}) [{workflow_name}]'
                advance_task_condition_list.append(new_advance_structure_condition)

        task_monitor_trigger_condition_list = []
        advance_task_monitor_trigger_condition_list = []
        
        if task_monitor_trigger_depen_list:
            for condition_dict in task_monitor_trigger_depen_list:
                workflow_name = condition_dict['Workflow']
                source_task = condition_dict['Source Task']
                condition = condition_dict['Condition']
                
                new_structure_condition = f'{createStatusCondition(condition)}({source_task})'
                task_monitor_trigger_condition_list.append(new_structure_condition)
                new_advance_structure_condition = f'{createStatusCondition(condition)}({source_task}) [{workflow_name}]'
                advance_task_monitor_trigger_condition_list.append(new_advance_structure_condition)
        
        # Remove duplicates from the lists
        task_condition_set = list(set(task_condition_list))
        task_monitor_trigger_condition_set = list(set(task_monitor_trigger_condition_list))
        
        advance_task_condition_set = list(set(advance_task_condition_list))
        advance_task_monitor_trigger_condition_set = list(set(advance_task_monitor_trigger_condition_list))
        
        # Config Condition String
        task_condition_string = f"{' & '.join(task_condition_set)}{' | ' if task_condition_set and task_monitor_trigger_condition_set else ''}{' | '.join(task_monitor_trigger_condition_set)}"
        #task_condition_string += 
        #task_condition_string += ' | '.join(task_monitor_trigger_condition_set)
        
        advance_task_condition_string = f"{' & '.join(advance_task_condition_set)}{' | ' if advance_task_condition_set and advance_task_monitor_trigger_condition_set else ''}{' | '.join(advance_task_monitor_trigger_condition_set)}"
        #advance_task_condition_string += ' | ' if advance_task_condition_set and advance_task_monitor_trigger_condition_set else ''
        #advance_task_condition_string += ' | '.join(advance_task_monitor_trigger_condition_set)  # Join the conditions
        
        both_condition, only_found_in_job_condition, only_found_in_task_condition = compareConditionString(job_condition, task_condition_string)
        compare_result = 'Different' if only_found_in_job_condition or only_found_in_task_condition else 'Similar'
        
        all_condition_log.append({
            'UAT Business Services': business_services_map.get(job_name, 'Not Found') if job_name in processing_task_set else 'Not Found',
            'Check Golived': 'YES' if job_name in golived_task_set else 'NO',
            TASK_COLUMN: job_name,
            'Box Name': box_name,
            'Workflow Name': ' '.join(list(set(f'[{workflow_name}]' for workflow_name in task_vertex_dict.get(job_name, [])))),
            'Compare Result': compare_result,
            'Job Condition': job_condition,
            'Task Condition': task_condition_string,
            'Advance Task Condition': advance_task_condition_string,
            'Both Condition': ' // '.join(both_condition),
            'Only Found in Job Condition': ' // '.join(only_found_in_job_condition),
            'Only Found in Task Condition': ' // '.join(only_found_in_task_condition),
            
        })
        
        
        if compare_result == 'Different':
            non_simular_condition.append({
                'UAT Business Services': business_services_map.get(job_name, 'Not Found') if job_name in processing_task_set else 'Not Found',
                'Check Golived': 'YES' if job_name in golived_task_set else 'NO',
                TASK_COLUMN: job_name,
                'Box Name': box_name,
                'Workflow Name': ' '.join(list(set(f'[{workflow_name}]' for workflow_name in task_vertex_dict.get(job_name, [])))),
                'Job Condition': job_condition,
                'Task Condition': task_condition_string,
                'Advance Task Condition': advance_task_condition_string,
                'Both Condition': ' // '.join(both_condition),
                'Only Found in Job Condition': ' // '.join(only_found_in_job_condition),
                'Only Found in Task Condition': ' // '.join(only_found_in_task_condition),
                
            })
        count += 1
        if count % 1000 == 0:
            print(f'Processed {count} out of {total_count} rows')
            
    # Create DataFrames for all conditions and non-similar conditions
    df_all_condition_log = pd.DataFrame(all_condition_log)
    df_non_simular_condition = pd.DataFrame(non_simular_condition)
    print(f'Process complete. Total {len(df_all_condition_log)} rows.')
    return df_all_condition_log, df_non_simular_condition
                


#############################################################################

def findNonSimilarCondition(df_job, df_workflow, df_workflow_depen, df_workflow_vertex, df_task_monitor_trigger, df_processing_task, df_golived_task):

    workflow_list = df_workflow['Name'].tolist()

    print('Preparing workflow vertex dict...')
    workflow_vertex_dict = prepareWorkflowVertexDict(df_workflow_vertex, workflow_list)
    
    print('Preparing task vertex dict...')
    task_vertex_dict = prepareTaskVertexDict(df_workflow_vertex, workflow_list)
    
    print('Preparing workflow dependency dict...')
    workflow_depen_dict = createDependencyDict(df_workflow_depen, workflow_vertex_dict)
    
    print('Preparing task dependency dict...')
    task_depen_dict = prepareTaskDependencyDict(workflow_list, workflow_depen_dict)
    
    print('Preparing task monitor trigger dict...')
    task_monitor_trigger_depen_dict = prepareTaskMonitorTriggerDependencyDict(df_task_monitor_trigger)
    #createJson('task_monitor_trigger_depen_dict.json', task_monitor_trigger_depen_dict)
    
    #print('Combining task dependency dict...')
    #combined_task_depen_dict = combineDepenDict(task_depen_dict, task_monitor_trigger_depen_dict)

    print('Comparing conditions...')
    all_condition_log, non_simular_condition = prepareCompareCondition(df_job=df_job, 
                                                                       task_depen_dict=task_depen_dict, 
                                                                       task_monitor_trigger_depen_dict=task_monitor_trigger_depen_dict, 
                                                                       task_vertex_dict=task_vertex_dict, 
                                                                       df_processing_task=df_processing_task, 
                                                                       df_golived_task=df_golived_task)

    
    df_all_condition_log = pd.DataFrame(all_condition_log)
    df_non_simular_condition = pd.DataFrame(non_simular_condition)
    
    return df_all_condition_log, df_non_simular_condition
    

def delayTimes(seconds):
    time.sleep(seconds)


#############################################################################

def main():
    
    auth = loadJson('auth.json')
    userpass = auth['TTB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    updateURI(domain)
    
    
    df_job = getDataExcel()
    
    df_workflow_vertex = getReport(VERTEX_REPORT_TITLE)
    delayTimes(10)
    df_workflow_depen = getReport(DEPEN_REPORT_TITLE)
    delayTimes(10)
    df_workflow = getReport(WORKFLOW_REPORT_TITLE)
    delayTimes(10)
    df_processing_task = getReport(TASK_REPORT_TITLE)
    delayTimes(10)
    df_task_monitor_trigger = getReport(TASK_MONITOR_TRIGGER_REPORT_TITLE)
    #df_workflow = df_processing_task[df_processing_task['Type'] == 'Workflow']
    if df_processing_task is None:
        print("Error generating task report UAT")
        return
    
    if df_task_monitor_trigger is None:
        print("Error generating task monitor trigger report UAT")
        return
    
    df_processing_task = df_processing_task[['Name', 'Member of Business Services']]
    df_processing_task.rename(columns={'Name': TASK_COLUMN} , inplace=True)
    
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain = domain_url['1.174']
    updateURI(domain)
    df_golived_task = getReport(TASK_REPORT_TITLE)
    if df_golived_task is None:
        print("Error generating task report PROD")
        return
    df_golived_task = df_golived_task[['Name', 'Member of Business Services']]
    df_golived_task.rename(columns={'Name': TASK_COLUMN} , inplace=True)
    
    df_golived_task_not_in_processing = df_golived_task[~df_golived_task[TASK_COLUMN].isin(df_processing_task[TASK_COLUMN])]
    #df_golived_task_not_in_processing = df_golived_task_not_in_processing[[TASK_COLUMN, 'Member of Business Services']]
    
    
    df_all_condition_log, df_non_simular_condition = findNonSimilarCondition(df_job=df_job, 
                                                                             df_workflow=df_workflow, 
                                                                             df_workflow_depen=df_workflow_depen, 
                                                                             df_workflow_vertex=df_workflow_vertex, 
                                                                             df_task_monitor_trigger=df_task_monitor_trigger, 
                                                                             df_processing_task=df_processing_task, 
                                                                             df_golived_task=df_golived_task
                                                                             )
    
    createExcel(OUTPUT_EXCEL_NAME, (CONDITION_SHEETNAME, df_all_condition_log), (NON_SIMILAR_CONDITION_SHEETNAME, df_non_simular_condition), (GOLIVED_NOT_IN_PROCESS, df_golived_task_not_in_processing))
    
    
    
if __name__ == "__main__":
    main()