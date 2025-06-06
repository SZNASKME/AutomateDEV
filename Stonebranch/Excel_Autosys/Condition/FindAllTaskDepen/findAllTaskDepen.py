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

ROOT_BOX_COLUMN = 'rootBox'
ROOT_BOX_FOUND_CONDITION_COLUMN = 'rootBox_Found_Condition'

CUT_COLUMN_LIST = [APPNAME_COLUMN, UAC_APPNAME_COLUMN, JOBNAME_COLUMN, BOXNAME_COLUMN, ROOT_BOX_COLUMN]

FOUND_CONDITION_COLUMN_OUTPUT = 'Found_Condition'

ALL_AFTER = 'All After Job'
ONE_LEVEL_AFTER = 'One Level After Job'
JIL_CUT = 'Job List'
ALL_BEFORE = 'All Before Job'
ONE_LEVEL_BEFORE = 'One Level Before Job'
EXCEL_FILENAME = 'All_Before_After_XXX.xlsx'

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

def iterativeSearchPreviousDepenCondition(df_dict, task_name, cache):
    stack = [(task_name, 0)]  # Initialize stack with the root task and depth
    result = {}  # Track conditions and their depths
    
    while stack:
        current_task, current_depth = stack.pop()
        
        if current_task in cache:
            for cond, depth in cache[current_task].items():
                if cond not in result or result[cond] < depth:
                    result[cond] = depth
            continue
        
        row_data = df_dict.get(current_task)
        if row_data:
            condition = row_data[CONDITION_COLUMN]
            box_name = row_data[BOXNAME_COLUMN]
            
            if pd.notna(condition):
                condition_name_list = getNamefromCondition(condition)
                for condition_name in condition_name_list:
                    if condition_name not in result or result[condition_name] < current_depth + 1:
                        stack.append((condition_name, current_depth + 1))
                        result[condition_name] = current_depth + 1
            elif pd.notna(box_name):
                if box_name not in result or result[box_name] < current_depth + 1:
                    stack.append((box_name, current_depth + 1))
                    result[box_name] = current_depth + 1
        
        cache[current_task] = result.copy()
    
    return result


# Other depend to (Before)
def findAllBeforeJob(df_job, df_root, in_list_condition_dict): # check the other depend to the job in list
    
    
    all_in_list_job = set(job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list) 
    all_job_before_dict = {}
    all_level_found_list = []
    
    df_job_processed = df_job.copy()
    df_dict = df_job_processed.set_index(JOBNAME_COLUMN).to_dict(orient='index')
    job_conditions_dict = {}
    all_condition_name_except_in_list_dict = {}
    
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        condition = getattr(row, CONDITION_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        if pd.notna(condition):
            condition_name_list = getNamefromCondition(condition)
            for condition_name in condition_name_list:
                if condition_name not in job_conditions_dict:
                    job_conditions_dict[condition_name] = []
                if condition_name not in job_conditions_dict[condition_name]:
                    job_conditions_dict[condition_name].append(job_name)
            
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        if job_name not in all_in_list_job: # skip the job not in list
            continue
        
        condition = getattr(row, CONDITION_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        # find related condition : if not related condition --> skip
        found_before_condition_list = []
        if pd.notna(condition):
            condition_name_list = getNamefromCondition(condition)
            for condition_name in condition_name_list:
                if condition_name not in all_in_list_job:
                    found_before_condition_list.append(condition_name)
                    
        if not found_before_condition_list:
            continue
         
        cache = {}
        result = iterativeSearchPreviousDepenCondition(df_dict, job_name, cache)
        sorted_conditions = sorted(result.items(), key=lambda x: x[1], reverse=True)
        all_sorted_condition_names = [cond for cond, depth in sorted_conditions]
        
        all_condition_name_except_in_list_dict[job_name] = [condition_name for condition_name in all_sorted_condition_names if condition_name not in all_in_list_job]
        if not all_condition_name_except_in_list_dict[job_name]:
            continue
        
    all_job_before_dict = restructureKeyValue(all_condition_name_except_in_list_dict)
    for index, row in df_job_processed.iterrows():
        job_name = row[JOBNAME_COLUMN]
        
        if job_name in all_job_before_dict and job_name not in all_in_list_job:
            edited_row = row.copy()
            edited_row[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == job_name][ROOT_BOX_COLUMN].values[0]
            edited_row[FOUND_CONDITION_COLUMN_OUTPUT] = all_job_before_dict[job_name]
            edited_row[ROOT_BOX_FOUND_CONDITION_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == all_job_before_dict[job_name]][ROOT_BOX_COLUMN].values[0]
            all_level_found_list.append(edited_row)
        
        
    # Prepare the output DataFrame


    column_jil = df_job.columns.tolist()
    column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
    columns = CUT_COLUMN_LIST + [FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
    df_all_before_job = pd.DataFrame(all_level_found_list, columns=columns)
    df_all_before_job.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run before list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
    return df_all_before_job



# Other depend to (Before)
def checkOtherConditionDependToJobInList(df_job, df_root, in_list_condition_dict): # check the other depend to the job in list
    all_list_condition = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list] 
    found_list = []
    for index, row in df_job.iterrows():
        if row[JOBNAME_COLUMN] not in all_list_condition: # skip the job not in list
            continue
        condition = row[CONDITION_COLUMN]
        
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        found_condition_list = []
        for sub_condition in condition_list: # check if the condition is not in the list
            if sub_condition not in all_list_condition:
                found_condition_list.append(sub_condition)
        
        if len(found_condition_list) == 0:
            continue
        row_data = row.copy()
        row_data[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == row[JOBNAME_COLUMN]][ROOT_BOX_COLUMN].values[0]
        row_data[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(found_condition_list)
        root_box_found_condition_list = []
        for sub_condition in found_condition_list:
            root_box_found_condition = df_root[df_root[JOBNAME_COLUMN] == sub_condition][ROOT_BOX_COLUMN].values
            if root_box_found_condition.size > 0:
                if root_box_found_condition[0] not in root_box_found_condition_list:
                    root_box_found_condition_list.append(root_box_found_condition[0])
        row_data[ROOT_BOX_FOUND_CONDITION_COLUMN] = ", ".join(root_box_found_condition_list)
        found_list.append(row_data)
        
    column_jil = df_job.columns.tolist()
    column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
    columns = CUT_COLUMN_LIST + [FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
    df_other_depend_to_job_in_list = pd.DataFrame(found_list, columns=columns)
    df_other_depend_to_job_in_list.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (in list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (run before list)'}, inplace=True)
    return df_other_depend_to_job_in_list





############ After Job ####################

def iterativeSearchAfterDepenCondition(job_conditions_dict, job_child_dict, task_name, cache):
    stack = [(task_name, 0)]  # Initialize stack with the root task and depth
    result = {}  # Track conditions and their depths
    
    while stack:
        current_task, current_depth = stack.pop()
        
        if current_task in cache:
            for cond, depth in cache[current_task].items():
                if cond not in result or result[cond] < depth:
                    result[cond] = depth
            continue
        
        if current_task in job_conditions_dict:
            for job_name in job_conditions_dict[current_task]:
                if job_name not in result or result[job_name] < current_depth + 1:
                    stack.append((job_name, current_depth + 1))
                    result[job_name] = current_depth + 1
        if current_task in job_child_dict:
            for child_name in job_child_dict[current_task]:
                if child_name not in result or result[child_name] < current_depth + 1:
                    stack.append((child_name, current_depth + 1))
                    result[child_name] = current_depth + 1
        
        cache[current_task] = result.copy()
    
    return result

def checkBehindConditionInList(job_name, job_conditions_dict, job_child_dict, all_in_list_job):
    found_after_condition_list = []
    if job_name in job_conditions_dict:
        for condition in job_conditions_dict[job_name]:
            if condition in all_in_list_job:
                if condition not in found_after_condition_list:
                    found_after_condition_list.append(condition)
    
    if job_name in job_child_dict:
        for child in job_child_dict[job_name]:
            if child in all_in_list_job:
                if child not in found_after_condition_list:
                    found_after_condition_list.append(child)
    
    return found_after_condition_list



# Depend to Other (After)
def findAllAfterJob(df_job, df_root, in_list_condition_dict): # check job in list depend to other
    all_in_list_job = set(job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list) 
    all_level_found_list = []

    df_job_processed = df_job.copy()
    job_conditions_dict = {}
    job_child_dict = {}
    all_condition_name_except_in_list_dict = {}
    
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        condition = getattr(row, CONDITION_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        if pd.notna(condition):
            condition_name_list = getNamefromCondition(condition)
            for condition_name in condition_name_list:
                if condition_name not in job_conditions_dict:
                    job_conditions_dict[condition_name] = []
                if job_name not in job_conditions_dict[condition_name]:
                    job_conditions_dict[condition_name].append(job_name)
        elif pd.notna(box_name):
            if box_name not in job_child_dict:
                job_child_dict[box_name] = []
            if job_name not in job_child_dict[box_name]:
                job_child_dict[box_name].append(job_name)
    
    
    
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        if job_name not in all_in_list_job: # skip the job in list
            continue
        condition = getattr(row, CONDITION_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        
        # check condition behind the job (depen job)
        found_after_condition_list = checkBehindConditionInList(job_name, job_conditions_dict, job_child_dict, all_in_list_job)
        # if have no condition --> skip
        if not found_after_condition_list:
            continue
        
        
        #app_name = getattr(row, 'AppName')
        cache = {}
        result = iterativeSearchAfterDepenCondition(job_conditions_dict, job_child_dict, job_name, cache)
        sorted_conditions = sorted(result.items(), key=lambda x: x[1], reverse=True)
        all_sorted_condition_names = [cond for cond, depth in sorted_conditions]
        
        all_condition_name_except_in_list_dict[job_name] = [condition_name for condition_name in all_sorted_condition_names if condition_name not in all_in_list_job]
        if not all_condition_name_except_in_list_dict[job_name]:
            continue
    
    createJson('AAAAA.json', all_condition_name_except_in_list_dict)
    all_job_after_dict = restructureKeyValue(all_condition_name_except_in_list_dict)
    createJson('YYYYY.json', all_job_after_dict)
    for index, row in df_job_processed.iterrows():
        job_name = row[JOBNAME_COLUMN]
        
        if job_name in all_job_after_dict and job_name not in all_in_list_job:
            edited_row = row.copy()
            edited_row[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == job_name][ROOT_BOX_COLUMN].values[0]
            edited_row[FOUND_CONDITION_COLUMN_OUTPUT] = all_job_after_dict[job_name]
            edited_row[ROOT_BOX_FOUND_CONDITION_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == all_job_after_dict[job_name]][ROOT_BOX_COLUMN].values[0]
            all_level_found_list.append(edited_row)
    # Prepare the output DataFrame
    column_jil = df_job.columns.tolist()
    column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
    columns = CUT_COLUMN_LIST + [FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
    df_all_after_job = pd.DataFrame(all_level_found_list, columns=columns)
    df_all_after_job.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run after list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
    return df_all_after_job




# Depend to Other (After)
def checkJobInListConditionDependToOther(df_job, df_root, in_list_condition_dict): # check job in list depend to other
    all_list_condition_except = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list] 
    found_list = []
    for index, row in df_job.iterrows():
        if row[JOBNAME_COLUMN] in all_list_condition_except: # skip the job in list
            continue
        condition = row[CONDITION_COLUMN]
        
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        found_condition_list = []
        for sub_condition in condition_list: # check if the condition is in the list
            if sub_condition in all_list_condition_except:
                found_condition_list.append(sub_condition)
        
        if len(found_condition_list) == 0:
            continue
        row_data = row.copy()
        row_data[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == row[JOBNAME_COLUMN]][ROOT_BOX_COLUMN].values[0]
        row_data[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(found_condition_list)
        root_box_found_condition_list = []
        for sub_condition in found_condition_list:
            root_box_found_condition = df_root[df_root[JOBNAME_COLUMN] == sub_condition][ROOT_BOX_COLUMN].values
            if root_box_found_condition.size > 0:
                if root_box_found_condition[0] not in root_box_found_condition_list:
                    root_box_found_condition_list.append(root_box_found_condition[0])
        row_data[ROOT_BOX_FOUND_CONDITION_COLUMN] = ", ".join(root_box_found_condition_list)
        
        found_list.append(row_data)
    column_jil = df_job.columns.tolist()
    column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
    columns = CUT_COLUMN_LIST + [FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
    df_job_in_list_depend_to_other = pd.DataFrame(found_list, columns=columns)
    
    df_job_in_list_depend_to_other.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run after list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
    
    return df_job_in_list_depend_to_other


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
            for index, row in df_filtered.iterrows():
                if row[column_name] not in column_list_dict[filter_value]:
                    column_list_dict[filter_value].append(row[column_name])
        
    return column_list_dict


def matchJobInList(df, in_list_condition_dict):
    all_in_list_job = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list] 
    found_list = []
    for index, row in df.iterrows():
        if row[JOBNAME_COLUMN] not in all_in_list_job: # skip the job not in list
            continue
        row_data = row.copy()
        found_list.append(row_data)
        
    df_job_in_list = pd.DataFrame(found_list)
    return df_job_in_list


def restructureKeyValue(dict_list):
    new_dict = {}
    for key, value in dict_list.items():
        if key not in new_dict.keys():
            new_dict[key] = key
        for v in value:
            if v not in new_dict.keys():
                new_dict[v] = key
    return new_dict



def moveColumnAfter(df, column_to_move, target_column):
    col = df.pop(column_to_move)  # Remove the column
    target_index = df.columns.get_loc(target_column)  # Get the index of the target column
    df.insert(target_index + 1, column_to_move, col)  # Insert after the target column
    return df



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
    df_all_before_job = findAllBeforeJob(df_job, df_root, job_in_list_condition_dict)
    print("processing find all after job . . .")
    df_all_after_job = findAllAfterJob(df_job, df_root, job_in_list_condition_dict)
    #print("processing job in list . . .")
    df_job_in_list = matchJobInList(df_job, job_in_list_condition_dict)
    df_job_in_list_insert_root = df_job_in_list.copy()
    df_job_in_list_insert_root[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN].isin(df_job_in_list[JOBNAME_COLUMN])][ROOT_BOX_COLUMN].values
    df_job_in_list_insert_root = moveColumnAfter(df_job_in_list_insert_root, ROOT_BOX_COLUMN, BOXNAME_COLUMN)
    print("---------------------------------")  # Uncommenting this line to display a separator for output
    sheet_set = (
        (ALL_BEFORE, df_all_before_job), 
        (JIL_CUT, df_job_in_list_insert_root),
        (ALL_AFTER, df_all_after_job)
    )
    createExcel(EXCEL_FILENAME, *sheet_set)
    
if __name__ == '__main__':
    main()