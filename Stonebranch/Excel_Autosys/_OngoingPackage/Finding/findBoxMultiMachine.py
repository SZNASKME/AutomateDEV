import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Multi Machine Box.xlsx'
OUTPUT_SHEETNAME = 'Job List'

JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'
MACHINE_COLUMN = 'machine'

FILTER_VALUE = 'BOX'


def findBoxesWithMultipleMachines(df_job):
    box_machine_list = []
    box_multi_machine_list = []
    
    box_name_list = df_job[df_job[JOBTYPE_COLUMN] == FILTER_VALUE][JOBNAME_COLUMN].unique().tolist()

    for box_name in box_name_list:
        df_box_children = df_job[df_job[BOXNAME_COLUMN] == box_name]
        
        machines = df_box_children[MACHINE_COLUMN].unique().tolist()
        machines = [machine for machine in machines if pd.notna(machine)]
        machines.sort()
        if len(machines) > 1:
            box_multi_machine_list.append({
                BOXNAME_COLUMN: box_name,
                MACHINE_COLUMN: "<" + "> | <".join(machines) + ">"
            })
        box_machine_list.append({
            BOXNAME_COLUMN: box_name,
            MACHINE_COLUMN: "<" + "> | <".join(machines) + ">"
        })

    df_result_original = pd.DataFrame(box_machine_list)
    df_result = pd.DataFrame(box_multi_machine_list)

    return df_result_original, df_result





def main():
    df_job = getDataExcel("input main job file")
    
    df_result_original, df_result = findBoxesWithMultipleMachines(df_job)

    createExcel(OUTPUT_EXCEL_NAME,(OUTPUT_SHEETNAME, df_result), (OUTPUT_SHEETNAME + " Original", df_result_original))
if __name__ == '__main__':
    main()