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
BEFORE_OF_AFTER_DEPEN = 'Before of After Job Depen List'
EXCEL_FILENAME = 'MultiLevel_Before_After_XXXX.xlsx'
LEVEL = 'Depend Level'

SELECTED_COLUMN = 'jobName'
FILTER_COLUMN = 'rootBox'
#FILTER_VALUE_LIST = ['DWH_MTHLY_B']

except_root_list = [
    'DWH_ONICE_ONHOLD_B',
    #'DWH_DAILY_B',
    #'DWH_MTHLY_B'
    #'DI_DWH_AMLO_DAILY_B',
    #'DI_DWH_AMLO_02_DAILY_B',
    #'DI_DWH_AMLO_03_DAILY_B'
]



def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list



def prepareReverseConditionDict(df_job):
    cond_dict = {}
    df_job_processed = df_job.copy()
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        #if job_name not in all_process_job:
        #    continue
        condition = getattr(row, CONDITION_COLUMN)
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        for condition_name in condition_list:
            if condition_name not in cond_dict:
                cond_dict[condition_name] = []
            if job_name not in cond_dict[condition_name]:
                cond_dict[condition_name].append(job_name)
                
    return cond_dict

def prepareConditionDict(df_job):
    cond_dict = {}
    df_job_processed = df_job.copy()
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        #if job_name not in all_process_job:
        #    continue
        condition = getattr(row, CONDITION_COLUMN)
        if pd.isna(condition):
            continue
        condition_list = getNamefromCondition(condition)
        for condition_name in condition_list:
            if job_name not in cond_dict:
                cond_dict[job_name] = []
            if condition_name not in cond_dict[job_name]:
                cond_dict[job_name].append(condition_name)
                
    return cond_dict

################ Before Job ####################

def findBehindCondition(job_name, cond_dict, processed_jobs):
    found_list = []
    if job_name in cond_dict.keys():
        found_list.extend(cond_dict[job_name])
    return found_list

def recursiveFindBeforeJob(df_job, df_root, job_list, root_mode=None, before_job_dict=None, all_process_job=None, cond_dict=None, processed_jobs=None, all_found_list=None, level=None):
    
    if level is None:
        level = 1
    print("Before Level:", level)
    if all_process_job is None:
        if root_mode is None:
            all_process_job = job_list
        else:
            all_process_job = getAllChildrenJob(df_job, job_list)
    else:
        all_process_job = getAllChildrenJob(df_job, all_process_job)
    
    if processed_jobs is None:
        processed_jobs = set()
    
    if before_job_dict is None:
        before_job_dict = {}
    
    for job_name in all_process_job:
        if job_name not in before_job_dict:
            before_job_dict[job_name] = level

    print("Current process jobs:", len(all_process_job))
    if cond_dict is None:
        cond_dict = {}
    if all_found_list is None:
        all_found_list = []
    

    df_job_processed = df_job.copy()
  
    #print(cond_dict.keys())
    found_list = []
    add_all_process_job = []
    for index, row in df_job_processed.iterrows():
        job_name = row[JOBNAME_COLUMN]
        if job_name in processed_jobs:
            continue


        #behind_condition_list = findBehindCondition(job_name, cond_dict, processed_jobs)
        if job_name in cond_dict.keys():
            behind_condition_list = cond_dict[job_name]
            if job_name not in all_process_job and any(condition in all_process_job for condition in behind_condition_list):
                edited_row = row.copy()
                edited_row[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == job_name][ROOT_BOX_COLUMN].values[0]
                relate_behind_condition_list = [job_name for job_name in behind_condition_list if job_name in all_process_job]
                edited_row[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(relate_behind_condition_list)
                root_before_box = list({job_name for job_name in df_root[df_root[JOBNAME_COLUMN].isin(relate_behind_condition_list)][ROOT_BOX_COLUMN].values})
                edited_row[ROOT_BOX_FOUND_CONDITION_COLUMN] = ", ".join(root_before_box)
                
                edited_row[LEVEL] = level
                found_list.append(edited_row)
                add_all_process_job.append(job_name)
                processed_jobs.add(job_name)
            
    print("Total related items:", len(found_list))
    print("---------------------------------")
    all_found_list += found_list
    if not found_list:
        print("No found additional depend job: before")
        column_jil = df_job.columns.tolist()
        column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
        columns = CUT_COLUMN_LIST + [LEVEL, FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
        df_all_before_depen_job = pd.DataFrame(all_found_list, columns=columns) if all_found_list else pd.DataFrame(columns=columns)
        df_all_before_depen_job.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run before list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
        return df_all_before_depen_job, before_job_dict
    
    new_all_process_job = all_process_job + add_all_process_job
    return recursiveFindBeforeJob(df_job, df_root, job_list, before_job_dict, new_all_process_job, cond_dict, processed_jobs, all_found_list, level + 1)



def checkRelteCondition(behind_condition_list, relate_condition_job_name_list):
    for condition_name in behind_condition_list:
        if condition_name in relate_condition_job_name_list:
            return True
    return False




def recursiveFindBeforeJobOptimize(df_job, df_root, job_list, before_job_dict=None, all_process_job=None, cond_dict=None, processed_jobs=None, all_found_list=None, level=None, root_mode=None):
    
    if level is None:
        level = 1
    if root_mode is None:
        root_mode = False
    print("Before Level:", level)
    if all_process_job is None:
        if root_mode is False:
            all_process_job = job_list
        elif root_mode is True:
            all_process_job = getAllChildrenJob(df_job, job_list)
    else:
        all_process_job = getAllChildrenJob(df_job, all_process_job)
    
    if processed_jobs is None:
        processed_jobs = set()
    
    if before_job_dict is None:
        before_job_dict = {}
    
    for job_name in all_process_job:
        if job_name not in before_job_dict:
            before_job_dict[job_name] = level

    print("All process jobs:", len(all_process_job))
    if cond_dict is None:
        cond_dict = {}
    if all_found_list is None:
        all_found_list = []
    

    df_job_processed = df_job.copy()
  
    #print(cond_dict.keys())
    found_list = []
    add_all_process_job = []
    current_outside_relate_condition_list = []
    current_outside_job_list = []
    
    
    ###### find outside condition ######
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN, None)
        if job_name in all_process_job:
        
            condition = getattr(row, CONDITION_COLUMN, None)
            if pd.isna(condition):
                continue
            
            condition_list = getNamefromCondition(condition)
            outside_condition_list = [sc for sc in condition_list if sc not in all_process_job]
            
            if not outside_condition_list:
                continue
            #if job_name not in current_outside_job_list:
            #    current_outside_job_list.append(job_name)
            current_outside_relate_condition_list.extend(outside_condition_list)
    current_outside_relate_condition_list = list(set(current_outside_relate_condition_list))
        
    
    ###### add outside condition ######
    for index, row in df_job_processed.iterrows():
        job_name = row[JOBNAME_COLUMN]
        condition = row[CONDITION_COLUMN]
        
        if job_name in current_outside_relate_condition_list:
            behind_condition_list = cond_dict.get(job_name, [])
        
            edited_row = df_job[df_job[JOBNAME_COLUMN] == job_name].copy()
            if edited_row.empty:
                continue
            #print("Found job:", job_name)
            root_box_values = df_root[df_root[JOBNAME_COLUMN] == job_name][ROOT_BOX_COLUMN].values
            edited_row[ROOT_BOX_COLUMN] = root_box_values[0] if len(root_box_values) > 0 else None
        
            relate_behind_condition_list = [j for j in behind_condition_list if j in all_process_job]
            edited_row[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(relate_behind_condition_list)
            
            root_before_box = list(set(df_root[df_root[JOBNAME_COLUMN].isin(relate_behind_condition_list)][ROOT_BOX_COLUMN].values))
            edited_row[ROOT_BOX_FOUND_CONDITION_COLUMN] = ", ".join(root_before_box)
            
            edited_row[LEVEL] = level
            
            found_list.append(edited_row)
            add_all_process_job.append(job_name)
            processed_jobs.add(job_name)
            
            
    print("Total related items:", len(found_list))
    print("---------------------------------")
    all_found_list += found_list
    if not found_list:
        print("No found additional depend job: before")
        column_jil = df_job.columns.tolist()
        column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
        columns = CUT_COLUMN_LIST + [LEVEL, FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
        df_all_before_depen_job = pd.concat(all_found_list, ignore_index=True) if all_found_list else pd.DataFrame(columns=columns)
        df_all_before_depen_job = df_all_before_depen_job[columns]
        df_all_before_depen_job.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run before list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
        
        return df_all_before_depen_job, before_job_dict
    
    new_all_process_job = all_process_job + add_all_process_job
    return recursiveFindBeforeJobOptimize(df_job, df_root, job_list, before_job_dict, new_all_process_job, cond_dict, processed_jobs, all_found_list, level + 1)


############ After Job ####################



# Depend to Other (After)
    

def recursiveFindAfterJob(df_job, df_root, job_list, after_job_dict=None, all_process_job=None, cond_dict=None, processed_jobs=None, all_found_list=None, level=None, root_mode=None):
    if level is None:
        level = 1
    if root_mode is None:
        root_mode = False

    if all_found_list is None:
        all_found_list = []
    if processed_jobs is None:
        processed_jobs = set()
    if after_job_dict is None:
        after_job_dict = {}
    if cond_dict is None:
        cond_dict = {}
        
    print("After Level:", level)
    if all_process_job is None:
        if root_mode is False:
            all_process_job = job_list
        elif root_mode is True:
            all_process_job = getAllChildrenJob(df_job, job_list)
    else:
        all_process_job = getAllChildrenJob(df_job, all_process_job)
    if after_job_dict is None:
        after_job_dict = {}
        
    found_list = []
    add_all_process_job = []

    found_jobs = set()
    if all_found_list:
        for row in all_found_list:
            job_name = getattr(row, JOBNAME_COLUMN)
            found_jobs.add(job_name)

    for job_name in all_process_job:
        if job_name not in after_job_dict:
            after_job_dict[job_name] = level
        
    print("Current process jobs:", len(all_process_job))

        
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
        found_condition_list = [sub_condition for sub_condition in condition_list if sub_condition in all_process_job]
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
        
        if job_name in cond_dict.keys() and job_name not in all_process_job:
            row_data = row.copy()
            job_cond_list = cond_dict[job_name]
            row_data[ROOT_BOX_COLUMN] = df_root[df_root[JOBNAME_COLUMN] == row[JOBNAME_COLUMN]][ROOT_BOX_COLUMN].values[0]
            row_data[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(job_cond_list) if job_cond_list else ""
            root_after_box = list({job for job in df_root[df_root[JOBNAME_COLUMN].isin(job_cond_list)][ROOT_BOX_COLUMN].values}) if job_cond_list else []
            row_data[ROOT_BOX_FOUND_CONDITION_COLUMN] = ", ".join(root_after_box)
            row_data[LEVEL] = level
            found_list.append(row_data)
            add_all_process_job.append(job_name)
            processed_jobs.add(job_name)
        
        
    print("Total related items:", len(found_list))
    print("---------------------------------")
    all_found_list.extend(found_list)
    if not found_list:
        print("No found additional depend job: after")
        column_jil = df_job.columns.tolist()
        column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
        columns = CUT_COLUMN_LIST + [LEVEL, FOUND_CONDITION_COLUMN_OUTPUT, ROOT_BOX_FOUND_CONDITION_COLUMN] + column_jil
        df_all_after_depen_job = pd.DataFrame(all_found_list, columns=columns)
        df_all_after_depen_job.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run after list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
        return df_all_after_depen_job, after_job_dict
    
    new_all_process_job = all_process_job + add_all_process_job
    
    return recursiveFindAfterJob(df_job, df_root, job_list, after_job_dict, new_all_process_job, cond_dict, processed_jobs, all_found_list, level + 1)


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
        
    df_job_in_list = pd.DataFrame(found_list) if found_list else pd.DataFrame(columns=df.columns)
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
    
    df_job_in_list = pd.DataFrame(found_list) if found_list else pd.DataFrame(columns=df.columns)
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
        children_set.add(box_name)

    for job_name in box_children_dict[box_name]:
        if job_name in df_job[BOXNAME_COLUMN].values:
            children_set = recursiveSearchChildrenInBoxToSet(df_job, job_name, children_set, box_children_dict)
        else:
            children_set.add(job_name)

    return children_set


def getAllChildrenJob(df_job, all_process_job):
    all_child_job = set()
    df_job_processed = df_job.copy()
    # for row in df_job_processed.itertuples(index=False):
    #     job_name = getattr(row, JOBNAME_COLUMN)
    #     box_name = getattr(row, BOXNAME_COLUMN)
        
    #     if job_name in all_process_job or box_name in all_process_job:
    #         all_child_job.add(job_name)
    
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        job_type = getattr(row, JOBTYPE_COLUMN)
        if job_name in all_process_job:
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
    except_root_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, except_root_list)
    print("---------------------------------")
    for key, value in job_in_list_condition_dict.items():
        print(key, len(value))
        
    print("---------------------------------")
    list_except_job_name = [job_name for job_name_list in except_root_dict.values() for job_name in job_name_list]
    df_job = df_job[~df_job[JOBNAME_COLUMN].isin(list_except_job_name)]
    cond_dict = prepareConditionDict(df_job)
    reversed_cond_dict = prepareReverseConditionDict(df_job)
    print("processing find all before job . . .")
    createJson("cond_dict.json", cond_dict)
    createJson("reversed_cond_dict.json", reversed_cond_dict)
    #df_all_before_depen_job, before_job_dict = recursiveFindBeforeJob(df_job, df_root, job_in_list_condition_dict, cond_dict=reversed_cond_dict)
    job_list = [job_name for job_name_list in job_in_list_condition_dict.values() for job_name in job_name_list]
    df_all_before_depen_job, before_job_dict = recursiveFindBeforeJobOptimize(df_job, df_root, job_list, cond_dict=reversed_cond_dict)
    print("processing find all after job . . .")
    df_all_after_depen_job, after_job_dict = recursiveFindAfterJob(df_job, df_root, job_list)
    print("processing find all before of after job . . .")
    after_job_list = df_all_after_depen_job[JOBNAME_COLUMN + ' (run after list)'].tolist()
    df_all_before_of_after_depen_job, before_of_after_job_dict = recursiveFindBeforeJobOptimize(df_job, df_root, after_job_list, cond_dict=reversed_cond_dict, root_mode=True)
    print("processing job in list . . .")  # Uncommenting this line to display the processing status
    df_job_in_list = matchJobInList(df_job, df_root, job_in_list_condition_dict)
    df_all_before_job = matchJobDict(df_job, df_root, before_job_dict)
    df_all_after_job = matchJobDict(df_job, df_root, after_job_dict)
    #df_all_before_of_after_job = matchJobDict(df_job, df_root, before_of_after_job_dict)
    
    print("---------------------------------")  # Uncommenting this line to display a separator for output
    sheet_set = (
        (BEFORE_DEPEN, df_all_before_depen_job),
        (ALL_BEFORE, df_all_before_job),
        (JIL_CUT, df_job_in_list),
        (ALL_AFTER, df_all_after_job),
        (AFTER_DEPEN, df_all_after_depen_job),
        (BEFORE_OF_AFTER_DEPEN, df_all_before_of_after_depen_job),
    )
    createExcel(EXCEL_FILENAME, *sheet_set)



if __name__ == '__main__':
    main()