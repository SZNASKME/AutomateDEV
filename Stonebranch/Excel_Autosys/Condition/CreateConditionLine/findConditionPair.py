import sys
import os
import pandas as pd
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createFile import createJson, createExcel
from utils.readExcel import getDataExcel



def getAllInnermostSubstrings(string, start_char, end_char):
    pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
    
    # Find all substrings that match the pattern
    matches = re.findall(pattern, string)
    
    return matches

def getNamefromCondition(condition):
    name_list = getAllInnermostSubstrings(condition, '(', ')')
    return name_list



def findConditionPair(df_job):
    condition_pair_list = []
    df_dict = df_job.set_index('jobName').to_dict(orient='index')
    number_of_rows = len(df_job)
    count = 0
    for row in df_job.itertuples(index=False):
        count += 1
        condition = row.condition
        if pd.isna(condition):
            print(f'{count}/{number_of_rows} no have condition | {row.jobName}')
            continue
        if pd.isna(row.box_name):
            box_name = None
        else:
            box_name = row.box_name
        condition_list = getNamefromCondition(condition)
        for sub_condition in condition_list:
            condition_pair_list.append({
                'soureJobName': sub_condition,
                'destinationJobName': row.jobName,
                'box_name': box_name
            })
        
        print(f'{count}/{number_of_rows} done | {row.jobName}')
        
    return condition_pair_list


def findRootConditionLine(condition_pair_list):
    root_condition_line_list = []
    soureJobName_list = []
    destinationJobName_list = []
    box_name_list = []
    for condition_pair in condition_pair_list:
        soureJobName_list.append(condition_pair['soureJobName'])
        destinationJobName_list.append(condition_pair['destinationJobName'])
    
    for soureJobName in soureJobName_list:
        if soureJobName not in destinationJobName_list and soureJobName not in box_name_list:
            if soureJobName not in root_condition_line_list:
                root_condition_line_list.append(soureJobName)
            
    return root_condition_line_list





def main():
    df_job = getDataExcel()
    
    condition_pair_list = findConditionPair(df_job)
    print(len(condition_pair_list))
    createJson('conditionPair.json', condition_pair_list)
    
    root_condition_line_list = findRootConditionLine(condition_pair_list)
    print(len(root_condition_line_list))
    createJson('rootConditionLine.json', root_condition_line_list)
    
    
if __name__ == '__main__':
    main()