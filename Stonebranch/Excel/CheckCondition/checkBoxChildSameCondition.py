import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel
from utils.readFile import loadJson





def compareCondition(df_jil):
    error_list = []
    workflow_list = []
    
    df_box = df_jil[df_jil['jobType'] == 'BOX']
    df_box_filtered = df_box[['jobName', 'condition']]
            
    df_cmd = df_jil[df_jil['jobType'] == 'CMD']
    df_cmd_filtered = df_cmd[['jobName', 'condition','box_name']]
    
    for index, row in df_box_filtered.iterrows():
        condition = row['condition']
        same_condition_rows = df_cmd_filtered[(df_cmd_filtered['condition'] == condition) & (df_cmd_filtered['condition'] != '')]
        
        for index, same_condition_row in same_condition_rows.iterrows():
            if row['jobName'] == same_condition_row['box_name']:
                error_list.append({
                    'boxName': row['jobName'],
                    'boxCondition': row['condition'],
                    'jobCondition': same_condition_row['condition'],
                    'jobName': same_condition_row['jobName'],
                })
            
    df_same_condition = pd.DataFrame(error_list)
                    
    return df_same_condition
        
def main():
    
    
    df_jil = getDataExcel()
    print(df_jil)
    df_same_condition = compareCondition(df_jil)
    createExcel('box_job_same_condition.xlsx', (df_same_condition, 'box_job_same_condition'))




if __name__ == '__main__':
    main()
