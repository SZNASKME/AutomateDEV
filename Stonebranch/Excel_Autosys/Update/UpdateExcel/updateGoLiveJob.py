import sys
import os
import json
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcelAllSheet, getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.createFile import createJson

SELECTED_COLUMN = "MAIN"
JOBNAME_COLUMN = "jobName"
ROOTBOX_COLUMN = "rootBox"
WORKFLOW_COLUMN = "GOLIVING Workflow"
UPDATE_COLUMN = "Update Survey"
UPDATE_VALUE = "GOLIVING"
UPDATED_VALUE = "GOLIVED"
SELF_ROOTBOX = "Self Start"

OUTPUT_EXCEL_FILE = "Updated Excel.xlsx"
OUTPUT_EXCEL_SHEET = "Updated Excel"

JSON_DICT_STORE_FILENAME = "goliving_dict.json"
JSON_LIST_STORE_FILENAME = "goliving_list.json"

def getSpecificColumn(df, column_name):
    column_list = []
    for index, row in df.iterrows():
        column_list.append(row[column_name])
    return column_list

def getSpecificColumnMultiSheet(df_dict, column_name):
    column_value_dict = {}
    column_value_list = []
    #print(df_dict)
    for name, df in df_dict.items():
        if df is None:
            column_value_dict[name] = []
        elif column_name in df.columns:
            column_value_dict[name] = getSpecificColumn(df, column_name)
            value = getSpecificColumn(df, column_name)
            for v in value:
                if v not in column_value_list:
                    column_value_list.append(v)

        
    return column_value_dict, column_value_list

def restructureDictofList(dict_list):
    new_dict = {}
    for key, value in dict_list.items():
        for v in value:
            if v not in new_dict.values():
                new_dict[v] = key
            else:
                new_dict[v] = new_dict[v] + ", " + key
            
            
    return new_dict

def findKeyFromDictList(dict_list, value):
    for key, values in dict_list.items():
        if value in values:
            return key
    return None

# def updateExcelProcess(job_df, root_start_df, golive_workflow_list, include_workflow_list):
#     updating_df = job_df.copy()
#     if include_workflow_list is None:
#         include_workflow_list = []
#     golive_root_start_list = set(golive_workflow_list + include_workflow_list)
#     golive_all_list = []
#     print("getting all children list . . .")
#     count = 0
#     for row in root_start_df.itertuples(index=False):
#         count += 1
#         job_name = getattr(row, JOBNAME_COLUMN)
#         root_box = getattr(row, ROOTBOX_COLUMN)
#         if job_name or root_box in golive_root_start_list:
#             golive_all_list.append(job_name)
#         print(f"Count: {count}", end="\r")
#     print("Updating Excel . . .")
#     count = 0
#     for row in job_df.itertuples(index=False):
#         count += 1
#         job_name = getattr(row, JOBNAME_COLUMN)
#         if job_name in golive_all_list:
#             updating_df.loc[updating_df[JOBNAME_COLUMN] == job_name, UPDATE_COLUMN] = UPDATE_VALUE
#         print(f"Count: {count}", end="\r")
        
#     return updating_df

def updateExcelProcess(job_df, root_start_df, goliving_workflow_list, include_workflow_list):
    # Combine lists directly
    if include_workflow_list is None:
        include_workflow_list = []
    #golive_root_start_list = set(goliving_workflow_list + include_workflow_list)  # Use a set for faster lookups
    
    # Filter rows in root_start_df based on the golive_root_start_list
    print("Filtering rows in root_start_df . . .")
    goliving_all_list = set(
        root_start_df.loc[
            root_start_df[JOBNAME_COLUMN].isin(goliving_workflow_list) | 
            root_start_df[ROOTBOX_COLUMN].isin(goliving_workflow_list),
            JOBNAME_COLUMN
        ]
    )
    golived_all_list = set(
        root_start_df.loc[
            root_start_df[JOBNAME_COLUMN].isin(include_workflow_list) | 
            root_start_df[ROOTBOX_COLUMN].isin(include_workflow_list),
            JOBNAME_COLUMN
        ]
    )
    
    # Update job_df based on the filtered golive_all_list
    print("Updating Excel (Go-Living) . . .")
    updating_df = job_df.copy()
    updating_df[UPDATE_COLUMN] = np.where(
        updating_df[JOBNAME_COLUMN].isin(goliving_all_list),
        UPDATE_VALUE,
        updating_df[UPDATE_COLUMN]
    )
    print("Updating Excel (Go-Lived) . . .")
    updating_df[UPDATE_COLUMN] = np.where(
        updating_df[JOBNAME_COLUMN].isin(golived_all_list),
        UPDATED_VALUE,
        updating_df[UPDATE_COLUMN]
    )
    return updating_df

def updateExcelProcessAdvance(job_df, root_start_df, goliving_workflow_list, include_workflow_list, goliving_workflow_dict):
    # Combine lists directly
    if include_workflow_list is None:
        include_workflow_list = []
    #golive_root_start_list = set(goliving_workflow_list + include_workflow_list)  # Use a set for faster lookups
    
    # Filter rows in root_start_df based on the golive_root_start_list
    print("Filtering rows in root_start_df . . .")
    goliving_all_list = set(
        root_start_df.loc[
            root_start_df[JOBNAME_COLUMN].isin(goliving_workflow_list) | 
            root_start_df[ROOTBOX_COLUMN].isin(goliving_workflow_list),
            JOBNAME_COLUMN
        ]
    )
    
    reverse_structure_goliving_dict = {}
    for value in goliving_all_list:
        root_box = root_start_df.loc[root_start_df[JOBNAME_COLUMN] == value, ROOTBOX_COLUMN].values[0]
        if root_box == SELF_ROOTBOX:
            root_box = value
        reverse_structure_goliving_dict[value] = findKeyFromDictList(goliving_workflow_dict, root_box)

    
    golived_all_list = set(
        root_start_df.loc[
            root_start_df[JOBNAME_COLUMN].isin(include_workflow_list) | 
            root_start_df[ROOTBOX_COLUMN].isin(include_workflow_list),
            JOBNAME_COLUMN
        ]
    )
    
    # reverse_structure_golived_dict = {}
    # for value in golived_all_list:
    #     root_box = root_start_df.loc[root_start_df[JOBNAME_COLUMN] == value, ROOTBOX_COLUMN].values[0]
    #     reverse_structure_golived_dict[value] = root_box
            
    
    # Update job_df based on the filtered golive_all_list
    print("Updating Excel (Go-Living) . . .")
    updating_df = job_df.copy()
    updating_df[UPDATE_COLUMN] = np.where(
        updating_df[JOBNAME_COLUMN].isin(goliving_all_list),
        UPDATE_VALUE,
        updating_df[UPDATE_COLUMN]
    )
    print("Updating Excel (Go-Lived) . . .")
    updating_df[UPDATE_COLUMN] = np.where(
        updating_df[JOBNAME_COLUMN].isin(golived_all_list),
        UPDATED_VALUE,
        updating_df[UPDATE_COLUMN]
    )
    
    updating_df[WORKFLOW_COLUMN] = updating_df[JOBNAME_COLUMN].map(reverse_structure_goliving_dict).fillna("Others")
    columns = updating_df.columns.tolist()
    UPDATE_COLUMN_index = columns.index(UPDATE_COLUMN)
    new_columns = columns[:UPDATE_COLUMN_index+1] + [WORKFLOW_COLUMN] + columns[UPDATE_COLUMN_index+1:-1]
    updating_df = updating_df[new_columns]
    
    return updating_df

def main():
    goliving_dfs = getDataExcelAllSheet("Multi Sheet Excel")
    job_df = getDataExcel("Job Excel")
    root_start_df = getDataExcel("Root Start Excel")
    
    golived_list = loadJson("golived.json", 2, "Excel_Autosys\\UpdateExcel")
    
    goliving_workflow_dict, goliving_workflow_list = getSpecificColumnMultiSheet(goliving_dfs, SELECTED_COLUMN)
    createJson(JSON_DICT_STORE_FILENAME, goliving_workflow_dict)
    createJson(JSON_LIST_STORE_FILENAME, goliving_workflow_list)
    #print(json.dumps(goliving_workflow_list, indent=4))
    #print(json.dumps(restructure_goliving_dict, indent=4))
    #print(json.dumps(golive_workflow_dict, indent=4))
    #print(json.dumps(golived_list, indent=4))
    #updated_df = updateExcelProcess(job_df, root_start_df, goliving_workflow_list, golived_list)
    updated_df = updateExcelProcessAdvance(job_df, root_start_df, goliving_workflow_list, golived_list, goliving_workflow_dict)
    createExcel(OUTPUT_EXCEL_FILE, (OUTPUT_EXCEL_SHEET, updated_df))
    
    
    
if __name__ == "__main__":
    main()