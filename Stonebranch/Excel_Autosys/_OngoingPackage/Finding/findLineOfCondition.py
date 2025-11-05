import sys
import os
import json
import pandas as pd
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Line Of Condition XXXXX.xlsx'
OUTPUT_SHEETNAME = 'List'

JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'

CONDITION_COLUMN = 'condition'
MAIN_BOX_COLUMN = 'Main Box'

def findLineOfCondition(df_job):
    row_condition_list = []
    
    main_box_list = df_job[MAIN_BOX_COLUMN].unique().tolist()
    main_box_rows = df_job[df_job[JOBNAME_COLUMN].isin(main_box_list)]
    
    for index, row in main_box_rows.iterrows():
        condition = row[CONDITION_COLUMN]
        if pd.notna(condition) and condition != '':
            # แยก condition โดยใช้ & และ | เป็นตัวแยก
            split_conditions = re.split(r'[&|]', condition)
            #split_conditions = [cond.strip() for cond in split_conditions if cond.strip() != '']
            
            row_data = {
                JOBNAME_COLUMN: row[JOBNAME_COLUMN],
                MAIN_BOX_COLUMN: row[MAIN_BOX_COLUMN],
            }
            condition_details = createDetailsOfCondition(split_conditions, df_job)
            row_data.update(condition_details)
            
            row_condition_list.append(row_data)
    
    df_result = pd.DataFrame(row_condition_list)
    
    return df_result


def createDetailsOfCondition(split_conditions, df_job):
    condition_details = {}
    count = 0
    for i, cond in enumerate(split_conditions):
        cond = cond.strip()
        if cond == '' or cond.startswith('v('):
            continue
        else:
            cond_string = extractFromCondition(cond)
            #print(f"Extracted condition: {cond_string} from {cond}")
            matching_jobs = df_job[df_job[JOBNAME_COLUMN] == cond_string]
            if not matching_jobs.empty:
                main_box = matching_jobs.iloc[0][MAIN_BOX_COLUMN]
            else:
                main_box = 'N/A'
            condition_details[f'condition_{count+1}'] = cond
            condition_details[f'condition_{count+1}_MainBox'] = main_box
            count += 1
    return condition_details

def extractFromCondition(condition_string):
    pattern = r'[a-zA-Z0-9?]\((.*?)\)'
    match = re.search(pattern, condition_string)
    if match:
        return match.group(1)
    else:
        return condition_string

def main():
    df_job = getDataExcel("input main job file")
    
    df_result_line_of_condition = findLineOfCondition(df_job)
    

    createExcel(OUTPUT_EXCEL_NAME,(OUTPUT_SHEETNAME, df_result_line_of_condition))
if __name__ == '__main__':
    main()