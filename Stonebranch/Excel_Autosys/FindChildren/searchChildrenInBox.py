import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Children in Lonclass & RDT.xlsx'
OUTPUT_SHEETNAME = 'All Children in Box'

box_list = [
    'DI_DWH_LCS_S.CHK_DATA_B',
    'DI_DWH_LON_CLASS_B',
    'DWH_LCS_W.CHK_DATA_B',
    'DWH_LON_CLASS_WEEKLY_B',
    'DWH_RDT_ACS_PREP_M_B',
    'DWH_RDT_BU_MATRIX_Q_B',
    'DWH_RDT_DAILY_B',
    'DWH_RDT_G1_MTHLY_B',
    'DWH_RDT_G2_MTHLY_B',
    'DWH_RDT_INBOUND_D_B',
    'DWH_RDT_INBOUND_M_B',
    'DWH_RDT_ONETIME_M_B'
]


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
        max_depth = max(len(row["Path"]) for row in list_all_children)
        columns = ["jobName", "Job Level", "Main Box"] + [f"Level {i+1}" for i in range(max_depth)]
        input_data = []
        input_data.append([box_name, 0, box_name] + [""] * (max_depth - 1))
        for row in list_all_children:
            padded_row = row["Path"] + [""] * (max_depth - len(row["Path"]))
            input_data.append([row["Child"], len(row["Path"]), box_name] + padded_row)
        df_list_children = pd.DataFrame(input_data, columns=columns)
        df_children_list.append(df_list_children)
    
    df_all_children = pd.concat(df_children_list, ignore_index=True)
    return df_all_children


def main():
    df_job = getDataExcel()
    
    all_children_dict = searchAllChildrenInBox(df_job, box_list)
    createJson('all_children.json', all_children_dict)
    #print(json.dumps(all_children_dict, indent=4))
    df_all_children = listNestedDictToDataFrame(all_children_dict)
    #print(json.dumps(list_all_children, indent=4))
    
    #list_to_excel = [(box_name, df_children) for box_name, df_children in df_all_children.items()]
    createExcel(OUTPUT_EXCEL_NAME,(OUTPUT_SHEETNAME, df_all_children))
    
    
if __name__ == '__main__':
    main()