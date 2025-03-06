import sys
import os
import pandas as pd
import math
import re
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

APPNAME_COLUMN = 'AppName'
UAC_APPNAME_COLUMN = 'UAC Bussiness Service'
JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'

ROOT_BOX_COLUMN = 'rootBox'
ROOT_BOX_FOUND_CONDITION_COLUMN = 'rootBox_Found_Condition'

CUT_COLUMN_LIST = [APPNAME_COLUMN, UAC_APPNAME_COLUMN, JOBNAME_COLUMN, BOXNAME_COLUMN, ROOT_BOX_COLUMN]

FOUND_CONDITION_COLUMN_OUTPUT = 'Found_Condition'

ALL_AFTER = 'All After Job'
BEFORE_DEPEN = 'Before Job Depen List'
JIL_CUT = 'Original Job List'
AFTER_DEPEN = 'After Job Depen List'
ALL_BEFORE = 'All Before Job'
EXCEL_FILENAME = 'MultiLevel_Before_After_XXX.xlsx'
LEVEL = 'Depend Level'

SELECTED_COLUMN = 'jobName'
FILTER_COLUMN = 'rootBox'
#FILTER_VALUE_LIST = ['DWH_MTHLY_B']


def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list



################ Before Job ####################

def findBehindCondition(job_name, cond_dict):
    found_list = []
    for key, value in cond_dict.items():
        if job_name in value:
            found_list.append(key)
    return found_list



def recursiveFindBeforeJob(df_job, df_root, in_list_condition_dict, before_job_dict=None, current_process_job=None, cond_dict=None, processed_jobs=None, all_found_list=None, level=None):
    
    if level is None:
        level = 1
    print("Before Level:", level)
    if current_process_job is None:
        current_process_job = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list]
    else:
        current_process_job = getAllChildrenJob(df_job, current_process_job)
    
    if processed_jobs is None:
        processed_jobs = set()
    
    if before_job_dict is None:
        before_job_dict = {}
    
    for job_name in current_process_job:
        if job_name not in before_job_dict:
            before_job_dict[job_name] = level

    print("Current process jobs:", len(current_process_job))
    if cond_dict is None:
        cond_dict = {}
    if all_found_list is None:
        all_found_list = []
    

    df_job_processed = df_job.copy()
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        if job_name not in current_process_job:
            continue
        condition = getattr(row, CONDITION_COLUMN)
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        found_condition_list = [sub_condition for sub_condition in condition_list if sub_condition not in current_process_job]
        if not found_condition_list:
            continue
        for condition_name in found_condition_list:
            if job_name not in cond_dict:
                cond_dict[job_name] = []
            if condition_name not in cond_dict[job_name]:
                cond_dict[job_name].append(condition_name)
    #print(cond_dict)
    found_list = []
    add_current_process_job = []
    for index, row in df_job_processed.iterrows():
        job_name = row[JOBNAME_COLUMN]
        if job_name in processed_jobs:
            continue
        behind_condition_list = findBehindCondition(job_name, cond_dict)
        if behind_condition_list and job_name not in current_process_job:
            edited_row = row.copy()
            edited_row[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == job_name][ROOT_BOX_COLUMN].values[0]
            edited_row[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(behind_condition_list)
            root_before_box = list({job_name for job_name in df_root[df_root[JOBNAME_COLUMN].isin(behind_condition_list)][ROOT_BOX_COLUMN].values})
            edited_row[ROOT_BOX_FOUND_CONDITION_COLUMN] = ", ".join(root_before_box)
            
            edited_row[LEVEL] = level
            found_list.append(edited_row)
            add_current_process_job.append(job_name)
            processed_jobs.add(job_name)
            
    print("Total found items:", len(found_list))
    print("---------------------------------")
    all_found_list += found_list
    if not found_list:
        print("No found additional depend job: before")
        column_jil = df_job.columns.tolist()
        column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
        columns = CUT_COLUMN_LIST + [LEVEL, FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
        df_all_before_depen_job = pd.DataFrame(all_found_list, columns=columns)
        df_all_before_depen_job.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run before list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
        return df_all_before_depen_job, before_job_dict
    
    new_current_process_job = current_process_job + add_current_process_job
    return recursiveFindBeforeJob(df_job, df_root, in_list_condition_dict, before_job_dict, new_current_process_job, cond_dict, processed_jobs, all_found_list, level + 1)


############ After Job ####################



# Depend to Other (After)
    

def recursiveFindAfterJob(df_job, df_root, in_list_condition_dict, after_job_dict=None, current_process_job=None, cond_dict=None, processed_jobs=None, all_found_list=None, level=None):
    if level is None:
        level = 1
    print("After Level:", level)
    if current_process_job is None:
        current_process_job = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list]
    else:
        current_process_job = getAllChildrenJob(df_job, current_process_job)
    if after_job_dict is None:
        after_job_dict = {}
        
    if cond_dict is None:
        cond_dict = {}
    if processed_jobs is None:
        processed_jobs = set()

    for job_name in current_process_job:
        if job_name not in after_job_dict:
            after_job_dict[job_name] = level
        
    print("Current process jobs:", len(current_process_job))
    if all_found_list is None:
        all_found_list = []
        
    found_list = []
    add_current_process_job = []
    
    
    found_jobs = set()
    if all_found_list:
        for row in all_found_list:
            job_name = getattr(row, JOBNAME_COLUMN)
            found_jobs.add(job_name)

    df_job_processed = df_job.copy()
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        if job_name in processed_jobs:
            continue
        condition = getattr(row, CONDITION_COLUMN)
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        found_condition_list = [sub_condition for sub_condition in condition_list if sub_condition in current_process_job]
        if not found_condition_list:
            continue
        for condition_name in found_condition_list:
            if job_name not in cond_dict:
                cond_dict[job_name] = []
            if condition_name not in cond_dict[job_name]:
                cond_dict[job_name].append(condition_name)
                
    #print(json.dumps(cond_dict, indent=4))
    #job_name_list = [job_name for job_name_list in cond_dict.values() for job_name in job_name_list]
    for index, row in df_job.iterrows():
        
        job_name = row[JOBNAME_COLUMN]
        if job_name in processed_jobs:
            continue
        
        if job_name in cond_dict.keys() and job_name not in current_process_job:
            row_data = row.copy()
            job_cond_list = cond_dict[job_name]
            row_data[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == row[JOBNAME_COLUMN]][ROOT_BOX_COLUMN].values[0]
            row_data[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(job_cond_list) if job_cond_list else ""
            root_after_box = list({job for job in df_root[df_root[JOBNAME_COLUMN].isin(job_cond_list)][ROOT_BOX_COLUMN].values}) if job_cond_list else []
            row_data[ROOT_BOX_FOUND_CONDITION_COLUMN] = ", ".join(root_after_box)
            row_data[LEVEL] = level
            found_list.append(row_data)
            add_current_process_job.append(job_name)
            processed_jobs.add(job_name)
        
        
    print("Total found items:", len(found_list))
    print("---------------------------------")
    all_found_list += found_list
    if not found_list:
        print("No found additional depend job: after")
        column_jil = df_job.columns.tolist()
        column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
        columns = CUT_COLUMN_LIST + [LEVEL, FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
        df_all_after_depen_job = pd.DataFrame(all_found_list, columns=columns)
        df_all_after_depen_job.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run after list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
        return df_all_after_depen_job, after_job_dict
    
    new_current_process_job = current_process_job + add_current_process_job
    
    return recursiveFindAfterJob(df_job, df_root, in_list_condition_dict, after_job_dict, new_current_process_job, cond_dict, processed_jobs, all_found_list, level + 1)


#############################################################################################################

def getSpecificColumn(df, column_name, filter_column_name = None, filter_value_list = None):
    column_list_dict = {}
    for filter_value in filter_value_list:
        df_filtered = df.copy()
        if filter_column_name is not None:
            df_filtered = df_filtered[df_filtered[filter_column_name].isin([filter_value])]

        #column_list_dict[filter_value] = []
        column_list_dict[filter_value] = df[df[column_name] == filter_value][column_name].tolist()
        if filter_column_name is not None:
            for row in df_filtered.itertuples(index=False):
                column_name_value = getattr(row, column_name)
                if column_name_value not in column_list_dict[filter_value]:
                    column_list_dict[filter_value].append(column_name_value)
        
    return column_list_dict


def matchJobInList(df, df_root, in_list_condition_dict):
    all_in_list_job = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list] 
    found_list = []
    for index, row in df.iterrows():
        if row[JOBNAME_COLUMN] not in all_in_list_job: # skip the job not in list
            continue
        row_data = row.copy()
        found_list.append(row_data)
        
    df_job_in_list = pd.DataFrame(found_list)
    df_job_in_list[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN].isin(df_job_in_list[JOBNAME_COLUMN])][ROOT_BOX_COLUMN].values
    df_job_in_list = moveColumnAfter(df_job_in_list, ROOT_BOX_COLUMN, BOXNAME_COLUMN)
    return df_job_in_list


def matchJobDict(df, df_root, job_dict):
    
    job_list = [job_name for job_name, level in job_dict.items() ]
    found_list = []
    for index, row in df.iterrows():
        if row[JOBNAME_COLUMN] not in job_list: # skip the job not in list
            continue
        row_data = row.copy()
        row_data[LEVEL] = job_dict[row[JOBNAME_COLUMN]]
        found_list.append(row_data)
    
    df_job_in_list = pd.DataFrame(found_list)
    #print(df_job_in_list)
    #df_job_in_list[LEVEL] = df_job_in_list[JOBNAME_COLUMN].map(job_dict)
    df_job_in_list[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN].isin(df_job_in_list[JOBNAME_COLUMN])][ROOT_BOX_COLUMN].values
    df_job_in_list = moveColumnAfter(df_job_in_list, LEVEL, JOBNAME_COLUMN)
    df_job_in_list = moveColumnAfter(df_job_in_list, ROOT_BOX_COLUMN, BOXNAME_COLUMN)
    
    return df_job_in_list



def moveColumnAfter(df, column_to_move, target_column):
    col = df.pop(column_to_move)  # Remove the column
    target_index = df.columns.get_loc(target_column)  # Get the index of the target column
    df.insert(target_index + 1, column_to_move, col)  # Insert after the target column
    return df


def recursiveSearchChildrenInBoxToSet(df_job, box_name, children_set=None, box_children_dict=None):
    if children_set is None:
        children_set = set()
    if box_children_dict is None:
        box_children_dict = {}

    if box_name not in df_job[JOBNAME_COLUMN].values:
        return None

    if box_name not in box_children_dict:
        df_job_filtered = df_job[df_job[BOXNAME_COLUMN] == box_name]
        box_children_dict[box_name] = df_job_filtered[JOBNAME_COLUMN].tolist()

    for job_name in box_children_dict[box_name]:
        if job_name in df_job[BOXNAME_COLUMN].values:
            children_set = recursiveSearchChildrenInBoxToSet(df_job, job_name, children_set, box_children_dict)
        else:
            children_set.add(job_name)

    return children_set


def getAllChildrenJob(df_job, current_process_job):
    all_child_job = set()
    df_job_processed = df_job.copy()
    # for row in df_job_processed.itertuples(index=False):
    #     job_name = getattr(row, JOBNAME_COLUMN)
    #     box_name = getattr(row, BOXNAME_COLUMN)
        
    #     if job_name in current_process_job or box_name in current_process_job:
    #         all_child_job.add(job_name)
    
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        job_type = getattr(row, JOBTYPE_COLUMN)
        if job_name in current_process_job:
            if job_type == 'BOX':
                children_set = recursiveSearchChildrenInBoxToSet(df_job, job_name)
                if children_set is not None:
                    all_child_job.update(children_set)
            else:
                    all_child_job.add(job_name)
    
    return list(all_child_job)


def main():
    
    
    df_job = getDataExcel("Enter the path of the main excel file")
    root_list_option = input("Do you want to use the root or list? (r/l): ")
    df_root = getDataExcel("Enter the path of the excel file with the root jobs")
    df_list_job = getDataExcel("Enter the path of the excel file with the list of jobs")
    
    list_job_name = df_list_job[JOBNAME_COLUMN].tolist()
    if root_list_option == 'r':
        job_in_list_condition_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, list_job_name)
    else:
        job_in_list_condition_dict = getSpecificColumn(df_job, SELECTED_COLUMN, None, list_job_name)
    print("---------------------------------")
    for key, value in job_in_list_condition_dict.items():
        print(key, len(value))
        
    print("---------------------------------")
    print("processing find all before job . . .")
    df_all_before_depen_job, before_job_dict = recursiveFindBeforeJob(df_job, df_root, job_in_list_condition_dict)
    #df_all_before_depen_job, before_job_dict = {}, {}
    print("processing find all after job . . .")
    df_all_after_depen_job, after_job_dict = recursiveFindAfterJob(df_job, df_root, job_in_list_condition_dict)
    print("processing job in list . . .")  # Uncommenting this line to display the processing status
    df_job_in_list = matchJobInList(df_job, df_root, job_in_list_condition_dict)
    df_all_before_job = matchJobDict(df_job, df_root, before_job_dict)
    df_all_after_job = matchJobDict(df_job, df_root, after_job_dict)
    
    print("---------------------------------")  # Uncommenting this line to display a separator for output
    sheet_set = (
        (BEFORE_DEPEN, df_all_before_depen_job),
        (ALL_BEFORE, df_all_before_job),
        (JIL_CUT, df_job_in_list),
        (ALL_AFTER, df_all_after_job),
        (AFTER_DEPEN, df_all_after_depen_job)
    )
    createExcel(EXCEL_FILENAME, *sheet_set)



if __name__ == '__main__':
    main()