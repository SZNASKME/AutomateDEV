import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel
from utils.readFile import loadJson

JOBNAME_COLUMN = 'jobName'
JOBTYPE_COLUMN = 'jobType'
BOXNAME_COLUMN = 'box_name'
CONDITION_COLUMN = 'condition'

WORKFLOW_CATEGORY = 'BOX'
COMMAND_CATEGORY = 'CMD'

BOX_COLUMN_OUTPUT = 'boxName'
BOX_CONDITION_COLUMN_OUTPUT = 'boxCondition'
JOB_CONDITION_COLUMN_OUTPUT = 'jobCondition'
JOB_COLUMN_OUTPUT = 'jobName'

# Check if the box job has the same condition as the child job

def compareCondition(df_jil):
    error_list = []
    
    df_box = df_jil[df_jil[JOBTYPE_COLUMN] == WORKFLOW_CATEGORY]
    df_box_filtered = df_box[[JOBNAME_COLUMN, CONDITION_COLUMN]]
            
    df_cmd = df_jil[df_jil[JOBTYPE_COLUMN] == COMMAND_CATEGORY]
    df_cmd_filtered = df_cmd[[JOBNAME_COLUMN, CONDITION_COLUMN,BOXNAME_COLUMN]]
    
    for index, row in df_box_filtered.iterrows():
        condition = row[CONDITION_COLUMN]
        same_condition_rows = df_cmd_filtered[(df_cmd_filtered[CONDITION_COLUMN] == condition) & (df_cmd_filtered[CONDITION_COLUMN] != '')]
        
        for index, same_condition_row in same_condition_rows.iterrows():
            if row[JOBNAME_COLUMN] == same_condition_row[BOXNAME_COLUMN]:
                error_list.append({
                    BOX_COLUMN_OUTPUT: row[JOBNAME_COLUMN],
                    BOX_CONDITION_COLUMN_OUTPUT: row[CONDITION_COLUMN],
                    JOB_CONDITION_COLUMN_OUTPUT: same_condition_row[CONDITION_COLUMN],
                    JOB_COLUMN_OUTPUT: same_condition_row[JOBNAME_COLUMN],
                })
            
    df_same_condition = pd.DataFrame(error_list)
                    
    return df_same_condition
        
def main():
    
    
    df_jil = getDataExcel()
    print(df_jil)
    df_same_condition = compareCondition(df_jil)
    createExcel('box_job_same_condition.xlsx', ('box_job_same_condition', df_same_condition))




if __name__ == '__main__':
    main()
