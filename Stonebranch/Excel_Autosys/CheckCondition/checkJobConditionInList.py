import sys
import os
import pandas as pd
import math
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel

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
        if row['jobName'] in in_list_condition:
            continue
        condition = row['condition']
        
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
            'jobName': row['jobName'],
            'box_name': row['box_name'],
            'From Survey': row['From Survey'],
            'Condition': condition,
            'Found_Condition': ", ".join(found_condition_list)
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
    in_list_condition = getSpecificColumn(df_in_list_condition, 'jobName', 'rootBox', 'DWH_ONICE_ONHOLD_B')
    print(len(in_list_condition))
    df_condition_matched = checkJobConditionInList(df_jil, in_list_condition)
    
    createExcel('job_condition_matched_r.xlsx', (df_condition_matched, 'job Condition Matched'))
    
if __name__ == '__main__':
    main()