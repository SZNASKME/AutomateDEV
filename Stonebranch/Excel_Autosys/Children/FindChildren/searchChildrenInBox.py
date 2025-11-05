import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Children in XXXXX.xlsx'
OUTPUT_SHEETNAME = 'All Children in Box'

JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'

box_list = [

]

# def recursiveSearchChildrenInBoxToSet(df_job, box_name, children_set=None, box_children_dict=None):
#     if children_set is None:
#         children_set = set()
#     if box_children_dict is None:
#         box_children_dict = {}

#     if box_name not in df_job[JOBNAME_COLUMN].values:
#         return None

#     if box_name not in box_children_dict:
#         df_job_filtered = df_job[df_job[BOXNAME_COLUMN] == box_name]
#         box_children_dict[box_name] = df_job_filtered[JOBNAME_COLUMN].tolist()
#         children_set.add(box_name)

#     for job_name in box_children_dict[box_name]:
#         if job_name in df_job[BOXNAME_COLUMN].values:
#             children_set = recursiveSearchChildrenInBoxToSet(df_job, job_name, children_set, box_children_dict)
#         else:
#             children_set.add(job_name)

#     return children_set


def recursiveSearchChildrenInBox(df_job, box_name):
    
    children_dict = {}
    if box_name not in df_job['jobName'].values:
        return None
    df_job_filtered = df_job[df_job['box_name'] == box_name]
    for row in df_job_filtered.itertuples(index=False):
        job_name = getattr(row, 'jobName')

        if job_name in df_job['box_name'].values:
            children_dict[job_name] = recursiveSearchChildrenInBox(df_job, job_name)
        else:
            children_dict[job_name] = None

    return children_dict

def searchAllChildrenInBox(df_job, box_list):
    all_children_dict = {}
    for box_name in box_list:
        children_dict = recursiveSearchChildrenInBox(df_job, box_name)
        if children_dict is not None:
            all_children_dict[box_name] = children_dict
        else:
            print(f"Box {box_name} not found in JIL")
        
    return all_children_dict

# def getAllChildrenJob(df_job, all_process_job):
#     all_child_job = set()
#     df_job_processed = df_job.copy()
#     # for row in df_job_processed.itertuples(index=False):
#     #     job_name = getattr(row, JOBNAME_COLUMN)
#     #     box_name = getattr(row, BOXNAME_COLUMN)
        
#     #     if job_name in all_process_job or box_name in all_process_job:
#     #         all_child_job.add(job_name)
    
#     for row in df_job_processed.itertuples(index=False):
#         job_name = getattr(row, JOBNAME_COLUMN)
#         job_type = getattr(row, JOBTYPE_COLUMN)
#         if job_name in all_process_job:
#             if job_type == 'BOX':
#                 children_set = recursiveSearchChildrenInBoxToSet(df_job, job_name)
#                 if children_set is not None:
#                     all_child_job.update(children_set)
#             else:
#                     all_child_job.add(job_name)
    
#     return list(all_child_job)

def flattenHierarchy(nested_dict, parent_path = None, depth = 0):
    if parent_path is None:
        parent_path = []
    
    rows = []
    for key, value in nested_dict.items():
        current_path = parent_path + [key]
        if isinstance(value, dict):
            rows.append({
                "Path": current_path,
                "Child": key
            })
            rows.extend(flattenHierarchy(value, parent_path=current_path, depth=depth + 1))
        else:
            rows.append({
                "Path": current_path,
                "Child": key
            })
    return rows

def listNestedDictToDataFrame(nested_dict):
    df_children_list = []
    for box_name, children in nested_dict.items():
        if children is None:
            print(f"Box {box_name} has no children")
            continue
        list_all_children = flattenHierarchy(children)
        max_depth = max(len(row["Path"]) for row in list_all_children) if list_all_children else 0
        columns = ["jobName", "Job Level", "Main Box"] + [f"Level {i+1}" for i in range(max_depth)]
        input_data = []
        input_data.append([box_name, 0, box_name] + [""] * (max_depth - 1))
        for row in list_all_children:
            padded_row = row["Path"] + [""] * (max_depth - len(row["Path"]))
            input_data.append([row["Child"], len(row["Path"]), box_name] + padded_row)
        df_children = pd.DataFrame(input_data, columns=columns)
        df_children_list.append(df_children)
    
    df_all_children = pd.concat(df_children_list, ignore_index=True)
    return df_all_children


def main():
    df_job = getDataExcel("input main job file")
    df_list = getDataExcel("input list of jobs")
    box_list = df_list[JOBNAME_COLUMN].tolist()
    all_children_dict = searchAllChildrenInBox(df_job, box_list)
    createJson('all_children.json', all_children_dict)
    #print(json.dumps(all_children_dict, indent=4))
    df_all_children = listNestedDictToDataFrame(all_children_dict)
    #print(json.dumps(list_all_children, indent=4))
    
    #list_to_excel = [(box_name, df_children) for box_name, df_children in df_all_children.items()]
    createExcel(OUTPUT_EXCEL_NAME,(OUTPUT_SHEETNAME, df_all_children))
    
    
if __name__ == '__main__':
    main()