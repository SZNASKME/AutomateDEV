import sys
import os
import pandas as pd
import re
import json


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from collections import defaultdict
from io import StringIO
from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson
from utils.readFile import loadJson
from utils.stbAPI import *


EXCEL_OUTPUT_NAME = 'TriggerListFromTasks.xlsx'
SHEETNAME = 'TriggerListFromTasks'



list_trigger_configs_temp = {
    'triggername': None
}





def getTriggerList():
    trigger_configs = list_trigger_configs_temp.copy()
    trigger_configs['triggername'] = '*'
    
    response = getListTriggerAdvancedAPI(trigger_configs)
    
    if response.status_code == 200:
        json_data = response.json()
        
        return json_data
    else:
        print("Error generating report")
        return None
    
def prepareTaskList(df):
    
    
    task_list_dict = {}
    df_duplicates_removed = df.drop_duplicates(subset=['TaskName'])
    df = df_duplicates_removed.reset_index(drop=True)
    for index, row in df.iterrows():
        task_name = row['TaskName']
        task_host = row['HostName']
        task_list_dict[task_name] = task_host
        
    return task_list_dict




def getTriggerListFromTasks(task_list_dict):
    trigger_list_data = []
    
    trigger_list = getTriggerList()
    
    for trigger in trigger_list:
        trigger_name = trigger['name']
        task_list = trigger.get('tasks', [])
        
        for task in task_list:
            if task in task_list_dict.keys():
                trigger_info = {
                    'Trigger Name': trigger_name,
                    'Task Name': task,
                    'Task Agent': task_list_dict[task]
                    
                }
                trigger_list_data.append(trigger_info)
    
    df_trigger_list = pd.DataFrame(trigger_list_data)
    
    return df_trigger_list


    
def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    #updateAPIAuth(userpass['API_KEY'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.181']
    updateURI(domain)
    
    df = getDataExcel()
    task_list_dict = prepareTaskList(df)
    
    df_trigger_list = getTriggerListFromTasks(task_list_dict)
    
    createExcel(EXCEL_OUTPUT_NAME,(SHEETNAME, df_trigger_list))
    
    
if __name__ == "__main__":
    main()