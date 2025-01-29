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
    stack = [(task_name, 0, None)]  # (task_name, depth, parent_task)
    result = {}  # {condition_name: (depth, parent_task)}
    
    while stack:
        current_task, current_depth, parent_task = stack.pop()
        
        if current_task in cache:
            for cond, (depth, parent) in cache[current_task].items():
                if cond not in result or result[cond][0] < depth:
                    result[cond] = (depth, parent)
            continue
        
        row_data = df_dict.get(current_task)
        if row_data:
            condition = row_data[CONDITION_COLUMN]
            box_name = row_data[BOXNAME_COLUMN]
            
            if pd.notna(condition):
                condition_name_list = getNamefromCondition(condition)
                for condition_name in condition_name_list:
                    if condition_name not in result or result[condition_name][0] < current_depth + 1:
                        stack.append((condition_name, current_depth + 1, current_task))
                        result[condition_name] = (current_depth + 1, current_task)
            elif pd.notna(box_name):
                if box_name not in result or result[box_name][0] < current_depth + 1:
                    stack.append((box_name, current_depth + 1, current_task))
                    result[box_name] = (current_depth + 1, current_task)
        
        cache[current_task] = result.copy()
    
    return result


def searchBeforeJob(df_jil):
    df_jil_processed = df_jil.copy()
    df_dict = df_jil_processed.set_index(JOBNAME_COLUMN).to_dict(orient='index')
    
    job_before_list = []
    sorted_conditions_dict = defaultdict(dict)
    for row in df_jil_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        app_name = getattr(row, 'AppName')
        cache = {}
        result = iterativeSearchPreviousDepenCondition(df_dict, job_name, cache)
        
        # Sort conditions by depth (descending)
        sorted_conditions = sorted(result.items(), key=lambda x: x[1][0], reverse=True)
        sorted_conditions_dict[job_name] = {cond: depth for cond, (depth, parent) in sorted_conditions}
        depth_len = max([depth for cond, (depth, parent) in sorted_conditions], default=0)
        
        all_sorted_condition_names = [f"{cond} (from {parent})" for cond, (depth, parent) in sorted_conditions]
        previous_depth_condition = [f"{cond} (from {parent})" for cond, (depth, parent) in sorted_conditions if depth == 1]
        furthest_depth_condition = [f"{cond} (from {parent})" for cond, (depth, parent) in sorted_conditions if depth == depth_len]

        row = [app_name, job_name] + [", ".join(previous_depth_condition)] + [", ".join(furthest_depth_condition)] + [", ".join(all_sorted_condition_names)]
        job_before_list.append(row)
    
    columns = ['AppName','JobName', 'Previous conditions', 'Furthest conditions', 'All Before Conditions']
    df_jil_before = pd.DataFrame(job_before_list, columns=columns)

    return df_jil_before, sorted_conditions_dict


########################################################################################


def buildDependencyDict(df_dict, task_name, cache, visited=None):
    if visited is None:
        visited = set()
    
    if task_name in cache:
        return cache[task_name]
    
    # Prevent infinite recursion due to circular references
    if task_name in visited:
        return {}

    visited.add(task_name)  # Mark task as visited
    row_data = df_dict.get(task_name, {})
    
    dependencies = {}
    
    if row_data:
        condition = row_data.get(CONDITION_COLUMN)
        box_name = row_data.get(BOXNAME_COLUMN)

        if pd.notna(condition):
            condition_names = getNamefromCondition(condition)
            for condition_name in condition_names:
                dependencies[condition_name] = buildDependencyDict(df_dict, condition_name, cache, visited.copy())

        if pd.notna(box_name):
            dependencies[box_name] = buildDependencyDict(df_dict, box_name, cache, visited.copy())

    cache[task_name] = dependencies
    return dependencies

def getAllNestedKeys(data, result=None):
    if result is None:
        result = set()

    if isinstance(data, dict):
        for key, value in data.items():
            result.add(key)  # Store the key
            getAllNestedKeys(value, result)  # Recurse into nested dict

    return result

def searchBeforeJobTree(df_jil):
    df_jil_processed = df_jil.copy()
    df_dict = df_jil_processed.set_index(JOBNAME_COLUMN).to_dict(orient='index')

    job_dependency_tree = {}
    cache = {}
    job_processed = set()

    for row in df_jil_processed.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        if job_name not in job_processed:
            job_dependency_tree[job_name] = buildDependencyDict(df_dict, job_name, cache)
            print(f"Processed {job_name}")
            job_processed = job_processed.union(getAllNestedKeys(job_dependency_tree[job_name]))
    
    return job_dependency_tree


########################################################################################

def main():
    
    df_jil = getDataExcel()
    print("Processing Previous job dependencies . . .")
    #df_jil_before, stored_conditions_dict = searchBeforeJobTree(df_jil)
    job_dependency_tree = searchBeforeJobTree(df_jil)
    createJson('stored_conditions_tree.json', job_dependency_tree)
    #createExcel(OUTPUT_EXCEL_FILE, ("Before", df_jil_before))
    
    
    
    
if __name__ == '__main__':
    main()