import sys
import os
import re
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcelAllSheet, getDataExcel
from utils.createFile import createExcel


JOBNAME_COLUMN = 'jobName'
SELECT_MAP_COLUMN = 'Taskname'
EXCEL_NAME = 'mappedJobs-Interval.xlsx'



def getSpecificColumn(df, column_name):
    column_list = []
    for index, row in df.iterrows():
        column_list.append(row[column_name])
    return column_list
    
def getJobMap(dfs):
    job_map = {}
    for name, df in dfs.items():
        job_map[name] = getSpecificColumn(df, SELECT_MAP_COLUMN)
    return job_map



def mapJobFromName(df_job, map_dict):
    mapped_dfs = {}
    for name, df in map_dict.items():
        mapped_dfs[name] = df_job[df_job[JOBNAME_COLUMN].isin(df)]
        #print(mapped_dfs[name])
    return mapped_dfs
    


def main():
    df_job = getDataExcel("Enter the path of the main excel file")
    dfs = getDataExcelAllSheet("Enter the path of the excel file with multiple sheets")
    #print(dfs)
    map_dict = getJobMap(dfs)
    #print(map_dict)
    mapped_dfs = mapJobFromName(df_job, map_dict)
    df_all = pd.concat(mapped_dfs.values(), ignore_index=True)
    df_list = [(name, df) for name, df in mapped_dfs.items()]
    df_list.append(('All', df_all))
    createExcel(EXCEL_NAME, *df_list)



if __name__ == '__main__':
    main()