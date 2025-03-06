import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Children in All DWH_DAILY.xlsx'
OUTPUT_SHEETNAME = 'All Children in Box'

box_list = [
    "DWH_P_CTUNI_GN_B",
    "DWH_P_IM_D_B",
    "DWH_P_SK_SKPY_CMCRSC_01_D_C.TRIG_C",
    "DWH_P_CTUNI_FD_B",
    "DWH_P_GN_D_B",
    "DWH_P_RM_D_B.FINISH_MAIL_C",
    "DWH_P_ALS_D_B",
    "DWH_P_HCM_LST_D_B",
    "DWH_P_OFSA_COR_INTRNL_ORG_XXX_D_B",
    "DWH_P_RM_D_B",
    "DWH_P_RM_D_B.START_MAIL_C",
    "DWH_ACCT_CROSS_REF_APP_D_B",
    "DWH_P_CC_D_B",
    "DWH_P_ST_D_B",
    "DWH_DAILY_B",
    "ODS_DAILY_B",
    "DWH_P_MF_D_B",
    "DWH_MIB_IMPORT_MTHLY_B",
    "DWH_DEP_D.STMT_ODS_B",
    "DWH_TDR_RELIEF_DAILY_B",
    "DWH_EMAIL_STATUS_LOG_B",
    "DWH_HPBD_DAILY_B.CHECK_DT_C",
    "DWH_SCS_DISPUTE_TRANSACTION_D_TRIGGER_B",
    "DWH_P_RM_RMCONSENT_D_B",
    "DWH_AUTO_LOAN_DAILY_B",
    "DWH_P_ESTAMP_DUTY_D_B",
    "DWH_CMS_API_D_B",
    "DWH_PROMPTPAY_INFO_D_B",
    "DWH_SCV.D.UPD_AR_LN_C.TRIG_C",
    "DWH_P_HCM_D_B",
    "DWH_P_MIB_D_B",
    "DWH_CUS.D.UPD_RMCUS_MAP.NEW_C.TRIG_C",
    "DWH_CHQ_CHEQUE_IN_RETURN_D_B",
    "DWH_MIB_IMPORT_DAILY_B",
    "DWH_SCS_INTEREST_AND_CHARGES_D_TRIGGER_B",
    "DWH_ALS_PAST_DUE_DAILY_B",
    "DWH_P_EC_ENTERPRISE_CUSTOMER_D_B",
    "DWH_P_CTUNI_D_B",
    "DWH_P_IM_MTTXN_D_B",
    "DWH_P_CTUNI_MIB_B",
    "DWH_P_SCS_MODEL_D_B",
    "DWH_P_ST_MTTXN_D_B",
    "DWH_P_ALSPAMC_D_B",
    "DWH_P_ALSBILL_D_B",
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
    
    all_children_dict = searchAllChildrenInBox(df_job, box_list)
    createJson('all_children.json', all_children_dict)
    #print(json.dumps(all_children_dict, indent=4))
    df_all_children = listNestedDictToDataFrame(all_children_dict)
    #print(json.dumps(list_all_children, indent=4))
    
    #list_to_excel = [(box_name, df_children) for box_name, df_children in df_all_children.items()]
    createExcel(OUTPUT_EXCEL_NAME,(OUTPUT_SHEETNAME, df_all_children))
    
    
if __name__ == '__main__':
    main()