import sys
import os
import json
import pandas as pd
import re
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
BOXNAME_COLUMN = 'box_name'




OUTPUT_EXCEL_FILE = 'FindBeforeAfter.xlsx'

CONDITION_PATTERN = re.compile(r"[a-z]\([A-Za-z0-9_\.]+\)")
PARENTHESES_PATTERN = re.compile(r"\(([^()]+)\)")


# def getAllInnermostSubstrings(string, start_char, end_char):
#     pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
#     # Find all substrings that match the pattern
#     matches = re.findall(pattern, string)
#     return matches

# def getNamefromCondition(condition):
#     name_list = getAllInnermostSubstrings(condition, '(', ')')
#     return name_list

def getNamefromCondition(condition):
    return PARENTHESES_PATTERN.findall(condition)
        


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


def searchBeforeJob(df_job):
    df_job_processed = df_job.copy()
    df_dict = df_job_processed.set_index(JOBNAME_COLUMN).to_dict(orient='index')
    
    job_before_list = []
    
    #stored_conditions_dict = {}
    #max_depth = 0
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        #app_name = getattr(row, 'AppName')
        cache = {}
        result = iterativeSearchPreviousDepenCondition(df_dict, job_name, cache)
        #print(json.dumps(result, indent=4))
        # Sort conditions by depth (descending)
        sorted_conditions = sorted(result.items(), key=lambda x: x[1], reverse=True)
        #stored_conditions_dict[job_name] = sorted_conditions
        depth_len = max([depth for cond, depth in sorted_conditions], default=0)
        #max_depth = max(max_depth, depth_len)
        all_sorted_condition_names = [cond for cond, depth in sorted_conditions]
        previous_depth_condition = [cond for cond, depth in sorted_conditions if depth == 1]
        furthest_depth_condition = [cond for cond, depth in sorted_conditions if depth == depth_len]
        row = [job_name] + [", ".join(previous_depth_condition)] + [", ".join(furthest_depth_condition)] + [", ".join(all_sorted_condition_names)]
        job_before_list.append(row)
    
    columns = ['JobName', 'Previous conditions', 'Furthest conditions', 'All Before Conditions']
    #df_job_before = pd.DataFrame(job_before_list)
    
    # for job_name, sorted_conditions in stored_conditions_dict.items():
    #     # Create a list of all condition names
    #     all_sorted_condition_names = [cond for cond, _ in sorted_conditions]

    #     # Organize conditions by depth
    #     depth_condition = defaultdict(list)
    #     for cond, depth in sorted_conditions:
    #         depth_condition[depth].append(cond)

    #     # Prepare row data: Job Name, All Conditions, and Conditions by Depth
    #     row = [job_name] + [
    #         ", ".join(all_sorted_condition_names)
    #     ] + [
    #         ", ".join(depth_condition.get(depth, [])) for depth in range(1, max_depth + 1)
    #     ]
    #     job_before_list.append(row)

    # Create the column names dynamically based on max depth
    # columns = ['Job Name', 'All Before'] + [f'Before Condition {i}' for i in range(1, max_depth + 1)]
    df_job_before = pd.DataFrame(job_before_list, columns=columns)



    return df_job_before


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
            for condition_name in job_conditions_dict[current_task]:
                if condition_name not in result or result[condition_name] < current_depth + 1:
                    stack.append((condition_name, current_depth + 1))
                    result[condition_name] = current_depth + 1
        if current_task in job_child_dict:
            for child_name in job_child_dict[current_task]:
                if child_name not in result or result[child_name] < current_depth + 1:
                    stack.append((child_name, current_depth + 1))
                    result[child_name] = current_depth + 1
        
        cache[current_task] = result.copy()
    
    return result


def searchAfterJob(df_job):
    df_job_processed = df_job.copy()
    df_dict = df_job_processed.set_index(JOBNAME_COLUMN).to_dict(orient='index')
    job_conditions_dict = {}
    job_child_dict = {}
    job_after_list = []
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        condition = getattr(row, CONDITION_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        if pd.notna(condition):
            condition_name_list = getNamefromCondition(condition)
            for condition_name in condition_name_list:
                if condition_name not in job_conditions_dict:
                    job_conditions_dict[condition_name] = []
                job_conditions_dict[condition_name].append(job_name)
        elif pd.notna(box_name):
            if box_name not in job_child_dict:
                job_child_dict[box_name] = []
            job_child_dict[box_name].append(job_name)
            
                
    for row in df_job_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        #app_name = getattr(row, 'AppName')
        cache = {}
        result = iterativeSearchAfterDepenCondition(job_conditions_dict, job_child_dict, job_name, cache)
        # Sort conditions by depth (descending)
        sorted_conditions = sorted(result.items(), key=lambda x: x[1], reverse=True)
        depth_len = max([depth for cond, depth in sorted_conditions], default=0)
        all_sorted_condition_names = [cond for cond, depth in sorted_conditions]
        next_depth_condition = [cond for cond, depth in sorted_conditions if depth == 1]
        furthest_depth_condition = [cond for cond, depth in sorted_conditions if depth == depth_len]
        row = [job_name] + [", ".join(next_depth_condition)] + [", ".join(furthest_depth_condition)] + [", ".join(all_sorted_condition_names)]
        job_after_list.append(row)

            
    columns = ['JobName', 'Next conditions', 'Furthest conditions', 'All After Conditions']
    df_job_after = pd.DataFrame(job_after_list, columns=columns)
    return df_job_after





def main():
    
    df_job = getDataExcel()
    print("Processing Previous job dependencies . . .")
    df_job_before = searchBeforeJob(df_job)
    print("Processing After job dependencies . . .")
    df_job_after = searchAfterJob(df_job)
    #createJson('stored_conditions.json', stored_conditions_dict)
    createExcel(OUTPUT_EXCEL_FILE, ("Before", df_job_before), ("After", df_job_after))
    
    
    
    
if __name__ == '__main__':
    main()