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
SPECIFIC_COLUMN_01 = 'From Survey'

JOB_COLUMN_OUTPUT = 'jobName'
BOX_COLUMN_OUTPUT = 'box_name'
SPECIFIC_COLUMN_01_OUTPUT = 'From Survey'
CONDITION_COLUMN_OUTPUT = 'Condition'
FOUND_CONDITION_COLUMN_OUTPUT = 'Found_Condition'

SELECTED_COLUMN = 'jobName'
FILTER_COLUMN = 'rootBox'
FILTER_VALUE_01 = 'DWH_ONICE_ONHOLD_B'

# Check condition job that Depen ONICE ONHOLD

def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list

def checkJobConditionInList(df_jil, in_list_condition):
    found_list = []
    for index, row in df_jil.iterrows():
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
        
        found_list.append({
            JOB_COLUMN_OUTPUT: row[JOBNAME_COLUMN],
            BOX_COLUMN_OUTPUT: row[BOXNAME_COLUMN],
            SPECIFIC_COLUMN_01_OUTPUT: row[SPECIFIC_COLUMN_01],
            CONDITION_COLUMN_OUTPUT: condition,
            FOUND_CONDITION_COLUMN_OUTPUT: ", ".join(found_condition_list)
        })
    df_condition_matched = pd.DataFrame(found_list)
    return df_condition_matched
    
def getSpecificColumn(df, column_name, filter_column_name = None, *filter_value):
    column_list = []
    if filter_column_name is not None:
        df = df[df[filter_column_name].isin(filter_value)]
        
    for index, row in df.iterrows():
        column_list.append(row[column_name])
    return column_list

def main():
    
    
    df_jil = getDataExcel("Enter the path of the main excel file")
    df_in_list_condition = getDataExcel("Enter the path of the excel file with the conditions to be checked")
    in_list_condition = getSpecificColumn(df_in_list_condition, SELECTED_COLUMN, FILTER_COLUMN, FILTER_VALUE_01)
    print(len(in_list_condition))
    df_condition_matched = checkJobConditionInList(df_jil, in_list_condition)
    
    createExcel('job_condition_matched_r.xlsx', (df_condition_matched, 'job Condition Matched'))
    
if __name__ == '__main__':
    main()