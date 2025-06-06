import sys
import os
import pandas as pd
import math
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel

JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
BOXNAME_COLUMN = 'box_name'
SPECIFIC_COLUMN_LIST = ['Update Survey', 'date_conditions', 'days_of_week', 'start_times', 'run_calendar', 'exclude_calendar']

JOB_COLUMN_OUTPUT = 'jobName'
BOX_COLUMN_OUTPUT = 'box_name'
SPECIFIC_COLUMN_LIST_OUTPUT = ['Update Survey', 'date_conditions', 'days_of_week', 'start_times', 'run_calendar', 'exclude_calendar']
CONDITION_COLUMN_OUTPUT = 'Condition'
FOUND_CONDITION_COLUMN_OUTPUT = 'Found_Condition'

EXCEL_FILENAME = 'job_condition_depend_INACT_All.xlsx'

SELECTED_COLUMN = 'jobName'
FILTER_COLUMN = 'rootBox'
#FILTER_VALUE_LIST = ['DWH_MTHLY_B']
FILTER_VALUE_LIST = [
    'ODS_DAILY_B'
    ,'DWH_P_RM_D_B'
    ,'DWH_P_ST_D_B'
    ,'DWH_P_IM_MTTXN_D_B'
    ,'DWH_P_ALS_D_B'
    ,'DWH_P_ALSBILL_D_B'
    ,'DWH_P_CTUNI_D_B'
    ,'DWH_P_EC_ENTERPRISE_CUSTOMER_D_B'
    ,'DWH_P_ALSPAMC_D_B'
    ,'DWH_P_ST_MTTXN_D_B'
    ,'DWH_P_CTUNI_GN_B'
    ,'DWH_INS_DAILY_B'
    ,'DWH_P_HP_MODEL_D_B'
    ,'DWH_P_FLPN_MODEL_D_B'
    ,'DWH_P_IM_D_B'
    ,'DWH_P_RM_RMCONSENT_D_B'
    ,'DWH_P_CTUNI_MIB_B'
    ,'DWH_P_CC_D_B'
    ,'DWH_P_MF_D_B'
    ,'DWH_P_SCS_MODEL_D_B'
    ,'DWH_AL_EXT_DAILY_B'
    ,'DWH_IC4_DAILY_B'
    ,'DWH_DAILY_BATCH.TRIG1_C'
    ,'DWH_DAILY_BATCH.TRIG2_C'
    ,'DWH_DAILY_BATCH.TRIG3_C'
    ,'DWH_SCV.D.UPD_AR_LN_C.TRIG_C'
    ,'DWH_P_HPFP_OREG_D_C'
    ,'DWH_POFSAA_DAILY_B'
    ,'DWH_CUS.D.UPD_RMCUS_MAP.NEW_C.TRIG_C'
    ,'DWH_DPD_COMS_ONLINE_B'
    ,'DWH_DAILY_BATCH.TRIG4_C'
    ,'DWH_DAILY_BATCH.TRIG5_C'
    ,'DWH_DAILY_BATCH.TRIG6_C'
    ,'DWH_P_CTUNI_FD_B'
    ,'DWH_AL_HP_CA_INFO_DAIL_B'
    ,'DWH_RM_UBO_DAILY_B'
    ,'DWH_TDR_RELIEF_DAILY_B'
]

def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list

def checkJobConditionInList(df_job, in_list_condition_dict):
    found_list_dict = {}
    for in_list_name, in_list_condition in in_list_condition_dict.items():
        #print(in_list_name, len(in_list_condition))
        #print(in_list_condition)
        found_list = []
        for index, row in df_job.iterrows():
            if row[JOBNAME_COLUMN] in in_list_condition:
                continue
            condition = row[CONDITION_COLUMN]
            
            if pd.isna(condition):
                continue
            condition_list = getNamefromCondition(condition)
            #print(condition)
            #print(condition_list)
            found_condition_list = []
            for sub_condition in condition_list:
                if sub_condition in in_list_condition:
                    found_condition_list.append(sub_condition)
            
            if len(found_condition_list) == 0:
                continue
            row_data = {}
            row_data[JOB_COLUMN_OUTPUT] = row[JOBNAME_COLUMN]
            row_data[BOX_COLUMN_OUTPUT] = row[BOXNAME_COLUMN]
            for specific_column in SPECIFIC_COLUMN_LIST:
                index = SPECIFIC_COLUMN_LIST.index(specific_column)
                row_data[specific_column] = row[SPECIFIC_COLUMN_LIST_OUTPUT[index]]
            row_data[CONDITION_COLUMN_OUTPUT] = condition
            row_data[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(found_condition_list)
            
            found_list.append(row_data)
        df_condition_matched = pd.DataFrame(found_list)
        found_list_dict[in_list_name] = df_condition_matched
        print(in_list_name," completed")
    return found_list_dict
    
def getSpecificColumn(df_root, column_name, filter_column_name = None, filter_value_list = None):
    column_list_dict = {}
    for filter_value in filter_value_list:
        df_filtered = df_root.copy()
        if filter_column_name is not None:
            df_filtered = df_filtered[df_filtered[filter_column_name].isin([filter_value])]

        #column_list_dict[filter_value] = []
        column_list_dict[filter_value] = df_root[df_root[column_name] == filter_value][column_name].tolist()
        for index, row in df_filtered.iterrows():
            if row[column_name] not in column_list_dict[filter_value]:
                column_list_dict[filter_value].append(row[column_name])
        
    return column_list_dict

def restructureDataFarmeDict(df_dict):
    pre_df = pd.concat(df_dict.values(), ignore_index=True)
    post_df = pre_df.drop_duplicates(subset=[JOB_COLUMN_OUTPUT], keep='first')
    output_df = post_df.copy()
    for index, row in post_df.iterrows():
        job_name = row[JOB_COLUMN_OUTPUT]
        found_condition_list = []
        filtered_df = pre_df[pre_df[JOB_COLUMN_OUTPUT] == job_name]
        for index, row in filtered_df.iterrows():
            found_condition_list.append(row[FOUND_CONDITION_COLUMN_OUTPUT])
        found_condition = ", ".join(found_condition_list)
        output_df.loc[output_df[JOB_COLUMN_OUTPUT] == job_name, FOUND_CONDITION_COLUMN_OUTPUT] = found_condition
    return output_df

def main():
    
    
    df_job = getDataExcel("Enter the path of the main excel file")
    df_root = getDataExcel("Enter the path of the excel file with the conditions to be checked")
    
    in_list_condition_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, FILTER_VALUE_LIST)
    for key, value in in_list_condition_dict.items():
        print(key, len(value))
    found_condition_matched_dict = checkJobConditionInList(df_job, in_list_condition_dict)
    is_merge_sheet = input("Do you want to merge the sheets? (y/n): ")
    if is_merge_sheet == 'y':
        df_found_condition_matched_non_dup = restructureDataFarmeDict(found_condition_matched_dict)
        createExcel(EXCEL_FILENAME, ('All', df_found_condition_matched_non_dup))
    else:
        df_found_condition_matched_list = []
        for name, df in found_condition_matched_dict.items():
            df_found_condition_matched_list.append((name, df))
        createExcel(EXCEL_FILENAME, *df_found_condition_matched_list)
    
if __name__ == '__main__':
    main()