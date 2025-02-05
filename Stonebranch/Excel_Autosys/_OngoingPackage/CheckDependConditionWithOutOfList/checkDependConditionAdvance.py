import sys
import os
import pandas as pd
import math
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel

APPNAME_COLUMN = 'AppName'
UAC_APPNAME_COLUMN = 'UAC Bussiness Service'
JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
BOXNAME_COLUMN = 'box_name'

CUT_COLUMN_LIST = [APPNAME_COLUMN, UAC_APPNAME_COLUMN, JOBNAME_COLUMN, BOXNAME_COLUMN]

FOUND_CONDITION_COLUMN_OUTPUT = 'Found_Condition'

DEPEND_TO_OTHER = 'Depend to other'
JIL_CUT = 'Job List'
OTHER_DEPEND_TO = 'Other depend to'
EXCEL_FILENAME = 'condition_depend_XXX.xlsx'

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

def checkJobInListConditionDependToOther(df_jil, in_list_condition_dict): # check job in list depend to other
    all_list_condition_except = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list] 
    found_list = []
    for index, row in df_jil.iterrows():
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
        row_data[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(found_condition_list)
        
        found_list.append(row_data)
    column_jil = df_jil.columns.tolist()
    column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
    columns = CUT_COLUMN_LIST + [FOUND_CONDITION_COLUMN_OUTPUT] + column_jil
    df_job_in_list_depend_to_other = pd.DataFrame(found_list, columns=columns)
    df_job_in_list_depend_to_other.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (run after list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (in list)'}, inplace=True)
    return df_job_in_list_depend_to_other



def checkOtherConditionDependToJobInList(df_jil, in_list_condition_dict): # check the other depend to the job in list
    all_list_condition = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list] 
    found_list = []
    for index, row in df_jil.iterrows():
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
        row_data[FOUND_CONDITION_COLUMN_OUTPUT] = ", ".join(found_condition_list)
        
        found_list.append(row_data)
        
    column_jil = df_jil.columns.tolist()
    column_jil = [x for x in column_jil if x not in CUT_COLUMN_LIST]
    columns = CUT_COLUMN_LIST + [FOUND_CONDITION_COLUMN_OUTPUT] + column_jil
    df_other_depend_to_job_in_list = pd.DataFrame(found_list, columns=columns)
    df_other_depend_to_job_in_list.rename(columns={JOBNAME_COLUMN: JOBNAME_COLUMN + ' (in list)', FOUND_CONDITION_COLUMN_OUTPUT: FOUND_CONDITION_COLUMN_OUTPUT + ' (run before list)'}, inplace=True)
    return df_other_depend_to_job_in_list

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

# def restructureDataFarmeDict(df_dict):
#     pre_df = pd.concat(df_dict.values(), ignore_index=True)
#     post_df = pre_df.drop_duplicates(subset=[JOB_COLUMN_OUTPUT], keep='first')
#     output_df = post_df.copy()
#     for index, row in post_df.iterrows():
#         job_name = row[JOB_COLUMN_OUTPUT]
#         found_condition_list = []
#         filtered_df = pre_df[pre_df[JOB_COLUMN_OUTPUT] == job_name]
#         for index, row in filtered_df.iterrows():
#             found_condition_list.append(row[FOUND_CONDITION_COLUMN_OUTPUT])
#         found_condition = ", ".join(found_condition_list)
#         output_df.loc[output_df[JOB_COLUMN_OUTPUT] == job_name, FOUND_CONDITION_COLUMN_OUTPUT] = found_condition
#     return output_df

def matchJobInList(df, in_list_condition_dict):
    all_list_condition = [job_name for job_name_list in in_list_condition_dict.values() for job_name in job_name_list] 
    found_list = []
    for index, row in df.iterrows():
        if row[JOBNAME_COLUMN] not in all_list_condition: # skip the job not in list
            continue
        row_data = row.copy()
        found_list.append(row_data)
        
    df_job_in_list = pd.DataFrame(found_list)
    return df_job_in_list

def main():
    
    
    df_jil = getDataExcel("Enter the path of the main excel file")
    root_list_option = input("Do you want to use the root or list? (r/l): ")
    if root_list_option == 'r':
        df_root = getDataExcel("Enter the path of the excel file with the root jobs")
    df_list_job = getDataExcel("Enter the path of the excel file with the list of jobs")
    list_job_name = df_list_job[JOBNAME_COLUMN].tolist()
    if root_list_option == 'r':
        job_in_list_condition_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, list_job_name)
    else:
        job_in_list_condition_dict = getSpecificColumn(df_jil, SELECTED_COLUMN, None, list_job_name)
    print("---------------------------------")
    for key, value in job_in_list_condition_dict.items():
        print(key, len(value))
    print("---------------------------------")
    print("processing job in list depend to other . . .")
    df_job_condition = checkJobInListConditionDependToOther(df_jil, job_in_list_condition_dict)
    print("processing other depend to job in list . . .")
    df_other_condition = checkOtherConditionDependToJobInList(df_jil, job_in_list_condition_dict)
    print("processing job in list . . .")
    df_jil_in_list = matchJobInList(df_jil, job_in_list_condition_dict)
    print("---------------------------------")
    createExcel(EXCEL_FILENAME, (OTHER_DEPEND_TO, df_other_condition), (JIL_CUT, df_jil_in_list), (DEPEND_TO_OTHER, df_job_condition))
    
if __name__ == '__main__':
    main()