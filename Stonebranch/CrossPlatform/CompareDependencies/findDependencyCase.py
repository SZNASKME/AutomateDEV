import sys
import os
import pandas as pd
import re
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import *

VERTEX_REPORT_TITLE = 'AskMe - Workflow Vertices'
DEPEN_REPORT_TITLE = 'AskMe - Workflow Dependencies'
WORKFLOW_REPORT_TITLE = 'AskMe - Workflow Report'

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
TASK_MONITOR_SUFFIX = '-TM'

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

# def prepareWorkflowVertexDict(df_workflow_vertex, workflow_list):
#     workflow_vertex_dict = {}
#     for workflow in workflow_list:
#         workflow_vertex_rows = df_workflow_vertex[df_workflow_vertex['Workflow'] == workflow]
#         if not workflow_vertex_rows.empty:
#             for _, row in workflow_vertex_rows.iterrows():
#                 vertex_id = row['Vertex Id']
#                 task_name = row['Task']
#                 if workflow not in workflow_vertex_dict:
#                     workflow_vertex_dict[workflow] = {}
#                 if vertex_id not in workflow_vertex_dict[workflow]:
#                     workflow_vertex_dict[workflow][vertex_id] = task_name
                
#         else:
#             workflow_vertex_dict[workflow] = {}
            
#     return workflow_vertex_dict

def prepareWorkflowVertexDict(df_workflow_vertex, workflow_list):
    # Initialize an empty dictionary to store the result
    workflow_vertex_dict = {}

    # Filter the DataFrame to include only workflows in the workflow_list
    filtered_df = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(workflow_list)]

    # Iterate through the filtered DataFrame and populate the dictionary
    for _, row in filtered_df.iterrows():
        workflow = row['Workflow']
        vertex_id = row['Vertex Id']
        task_name = row['Task']

        if workflow not in workflow_vertex_dict:
            workflow_vertex_dict[workflow] = {}
        workflow_vertex_dict[workflow][vertex_id] = task_name

    # Ensure all workflows in the workflow_list are included, even if empty
    for workflow in workflow_list:
        if workflow not in workflow_vertex_dict:
            workflow_vertex_dict[workflow] = {}

    return workflow_vertex_dict

def prepareTaskVertexDict(df_workflow_vertex, workflow_list):
    # Initialize an empty dictionary to store the result
    task_vertex_dict = {}

    # Filter the DataFrame to include only workflows in the workflow_list
    filtered_df = df_workflow_vertex[df_workflow_vertex['Workflow'].isin(workflow_list)]

    # Iterate through the filtered DataFrame and populate the dictionary
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
        
        #####
        # temp_depen_dict = depen_dict[workflow].copy()
        # for depen in temp_depen_dict:
        #     source_task = depen['Source Task']
        #     target_vertex_id = depen['Target Vertex Id']
        #     target_task = depen['Target Task']
        #     condition = depen['Condition']
        #     if any(break_condition in source_task for break_condition in break_through_condition):
                
        #         new_depen_list = findAllTargetDepen(source_task, temp_depen_dict)
                
        #         for new_depen in new_depen_list:
        #             new_info_depen = {
        #                 'Source Vertex Id': new_depen['Source Vertex Id'],
        #                 'Source Task': new_depen['Source Task'],
        #                 'Target Vertex Id': target_vertex_id,
        #                 'Target Task': target_task,
        #                 'Condition': condition
        #             }
        #             depen_dict[workflow].append(new_info_depen)
                
                
        #         depen_dict[workflow].remove(depen)
        #####
            
        
        

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
        else:
            task_depen_dict[workflow_name] = []

    return task_depen_dict

##############################################################################


def findAllTargetDepen(task_name, depen_dict):
    new_depen_list = []
    for depen in depen_dict:
        if depen['Target Task'] == task_name:
            new_depen_list.append(depen)

    return new_depen_list


##############################################################################

def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list


def getAllInnermostSubstringsWithStatus(string, pattern):
    # Find all substrings that match the pattern
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
    job_condition_not_found = []
    task_condition_not_found = []
    for job_condition in job_condition_list:
        if job_condition in task_condition_list:
            both_condition.append(job_condition)
        else:
            job_condition_not_found.append(job_condition)
    
    for task_condition in task_condition_list:
        if task_condition not in job_condition_list:
            task_condition_not_found.append(task_condition)

    return both_condition, job_condition_not_found, task_condition_not_found


def prepareCompareCondition(df_job, task_depen_dict, task_vertex_dict, df_processing_task, df_golived_task):
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
        #print(json.dumps(task_depen_list, indent=4))
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
                
        task_condition_set = list(set(task_condition_list))  # Remove duplicates
        task_condition_string = ' & '.join(task_condition_set)  # Join the conditions
        advance_task_condition_string = ' & '.join(advance_task_condition_list)  # Join the conditions

        both_condition, job_condition_not_found, task_condition_not_found = compareConditionString(job_condition, task_condition_string)
        compare_result = 'Different' if job_condition_not_found or task_condition_not_found else 'Similar'
        
        all_condition_log.append({
            'UAT Business Services': business_services_map.get(job_name, 'Not Found') if job_name in processing_task_set else 'Not Found',
            'Check Golived': 'YES' if job_name in golived_task_set else 'NO',
            TASK_COLUMN: job_name,
            'Box Name': box_name,
            'Workflow Name': ' '.join(list(set(f'[{workflow_name}]' for workflow_name in task_vertex_dict.get(job_name, [])))),
            'Compare Result': compare_result,
            'Job Condition': job_condition,
            'Task Condition': task_condition_string,
            'Both Condition': ' // '.join(both_condition),
            'Job Condition Not Found': ' // '.join(job_condition_not_found),
            'Task Condition Not Found': ' // '.join(task_condition_not_found),
            'Advance Task Condition': advance_task_condition_string
        })
        
        
        if compare_result == 'Different':
            non_simular_condition.append({
                'UAT Business Services': business_services_map.get(job_name, 'Not Found') if job_name in processing_task_set else 'Not Found',
                'Check Golived': 'YES' if job_name in golived_task_set else 'NO',
                TASK_COLUMN: job_name,
                'Box Name': box_name,
                'Workflow Name': ' '.join(list(set(f'[{workflow_name}]' for workflow_name in task_vertex_dict.get(job_name, [])))),
                'Condition': job_condition,
                'Task Condition': task_condition_string,
                'Advance Task Condition': advance_task_condition_string
            })
        count += 1
        if count % 1000 == 0:
            print(f'Processed {count} out of {total_count} rows')
            
    # Create DataFrames for all conditions and non-similar conditions
    df_all_condition_log = pd.DataFrame(all_condition_log)
    df_non_simular_condition = pd.DataFrame(non_simular_condition)
    print(f'Process complete. Total {len(df_all_condition_log)} rows.')
    return df_all_condition_log, df_non_simular_condition
                

# def mapGolivedTask(df_process, df_current_task, df_golived_task):
    
#     df_processing = df_process.copy()
    
#     current_task_list = df_current_task[TASK_COLUMN].tolist()
#     golived_list = df_golived_task[TASK_COLUMN].tolist()
    
#     for index, row in df_processing.iterrows():
#         task_name = row[TASK_COLUMN]
#         if task_name in golived_list:
#             df_processing.at[index, 'Check Golived'] = 'Golived'
#         else:
#             df_processing.at[index, 'Check Golived'] = 'Not Golive'
#         if task_name in current_task_list:
#             df_processing.at[index, 'Member of Business Services'] = df_current_task[df_current_task[TASK_COLUMN] == task_name]['Member of Business Services'].values[0]
#         else:
#             df_processing.at[index, 'Member of Business Services'] = 'Not Found'
    
#     df_processing = df_processing[['Member of Business Services', TASK_COLUMN, 'Box Name', 'Workflow Name', 'Check Golived', 'Compare Result', 'Job Condition', 'Task Condition', 'Both Condition', 'Job Condition Not Found', 'Task Condition Not Found', 'Advance Task Condition']]
#     df_processing.rename(columns={'Member of Business Services': 'Business Services', TASK_COLUMN: TASK_REPORT_COLUMN}, inplace=True)
    
#     return df_processing
        



#############################################################################

def findNonSimilarCondition(df_job, df_workflow, df_workflow_depen, df_workflow_vertex, df_processing_task, df_golived_task):

    workflow_list = df_workflow['Name'].tolist()

    print('Preparing workflow vertex dict...')
    workflow_vertex_dict = prepareWorkflowVertexDict(df_workflow_vertex, workflow_list)
    
    print('Preparing task vertex dict...')
    task_vertex_dict = prepareTaskVertexDict(df_workflow_vertex, workflow_list)
    
    print('Preparing workflow dependency dict...')
    workflow_depen_dict = createDependencyDict(df_workflow_depen, workflow_vertex_dict)
    
    print('Preparing task dependency dict...')
    task_depen_dict = prepareTaskDependencyDict(workflow_list, workflow_depen_dict)

    print('Comparing conditions...')
    all_condition_log, non_simular_condition = prepareCompareCondition(df_job, task_depen_dict, task_vertex_dict, df_processing_task, df_golived_task)

    
    df_all_condition_log = pd.DataFrame(all_condition_log)
    df_non_simular_condition = pd.DataFrame(non_simular_condition)
    
    return df_all_condition_log, df_non_simular_condition
    




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
    df_workflow_depen = getReport(DEPEN_REPORT_TITLE)
    df_workflow = getReport(WORKFLOW_REPORT_TITLE)
    df_processing_task = getReport(TASK_REPORT_TITLE)
    #df_workflow = df_processing_task[df_processing_task['Type'] == 'Workflow']
    if df_processing_task is None:
        print("Error generating task report UAT")
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
    
    
    df_all_condition_log, df_non_simular_condition = findNonSimilarCondition(df_job, df_workflow, df_workflow_depen, df_workflow_vertex, df_processing_task, df_golived_task)
    
    createExcel(OUTPUT_EXCEL_NAME, (CONDITION_SHEETNAME, df_all_condition_log), (NON_SIMILAR_CONDITION_SHEETNAME, df_non_simular_condition), (GOLIVED_NOT_IN_PROCESS, df_golived_task_not_in_processing))
    
    
    
if __name__ == "__main__":
    main()