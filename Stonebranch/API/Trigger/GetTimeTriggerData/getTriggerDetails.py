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


EXCEL_NAME = 'TriggerData.xlsx'
EXCEL_SHEET_NAME = 'TriggerData'


trigger_configs_temp = {
    'triggername': None,
}




list_trigger_configs_temp = {
    'name': None,
    'type': None,
}



def getTriggerList():
    trigger_configs = list_trigger_configs_temp.copy()
    trigger_configs['name'] = '*'
    trigger_configs['type'] = 2
    
    response = getListTriggerAPI(trigger_configs)
    print(response.content)
    if response.status_code == 200:
        #print("Response: ", response.text)
        json_data = response.json()
       # print(json.dumps(json_data, indent=4))
        trigger_list = [trigger['name'] for trigger in json_data]
        return trigger_list
    else:
        print("Error generating report")
        return None
    




def listTriggersDetails(trigger_list):
    
    trigger_data_dict = {}
    
    
    #list_trigger_configs = list_trigger_adv_configs_temp.copy()
    #list_trigger_configs['triggername'] = '*'
    #list_trigger_configs['type'] = 2
    
    for trigger_name in trigger_list:
        trigger_configs = trigger_configs_temp.copy()
        trigger_configs['triggername'] = trigger_name
    
        response = getTriggerAPI(trigger_configs)
        if response.status_code == 200:
            json_data = response.json()
            date_nouns = json_data.get('dateNouns', [])
            forecast = json_data.get('forecast', [])
            date_nouns_list = [date_noun['value'] for date_noun in date_nouns]
            
            trigger_data_dict[trigger_name] = {
                'trigger_name': trigger_name,
                'date_nouns': date_nouns_list,
                'forecast': forecast,
            }
            
            # Extract the "name" values from the JSON data
        
    
    return trigger_data_dict
    

def prepareTriggerData(trigger_list, trigger_data_dict_source1, trigger_data_dict_source2):
    
    trigger_data_list = []

    for trigger_name in trigger_list:
        date_nouns_source1 = trigger_data_dict_source1[trigger_name]['date_nouns'] 
        date_nouns_source2 = trigger_data_dict_source2[trigger_name]['date_nouns']
    
        trigger_data_list.append({
            'Trigger Name': trigger_name,
            'CHECK SAME': 'YES' if date_nouns_source1 == date_nouns_source2 else 'NO',
            'Date Nouns Source 1': ', '.join(date_nouns_source1),
            'Date Nouns Source 2': ', '.join(date_nouns_source2),
        })
        
        
    df_trigger_data = pd.DataFrame(trigger_data_list)
    
    
    return df_trigger_data
        
        
        
        
def main():
    auth = loadJson('auth.json')
    userpass = auth['TTB_PROD']
    #updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    updateAPIAuth(userpass['API_KEY'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_PROD']
    updateURI(domain)


    #df_trigger_list = getDataExcel()
    #trigger_list = df_trigger_list['Name'].tolist()
    trigger_list = getTriggerList()
    print(len(trigger_list))
    # trigger_data_dict_source1 = listTriggersDetails(trigger_list)
    
    
    # userpass = auth['TTB']
    # clearAuth()
    # updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    # domain = domain_url['TTB_UAT']
    # updateURI(domain)
    
    # trigger_data_dict_source2 = listTriggersDetails(trigger_list)

    # df_trigger_data = prepareTriggerData(trigger_list, trigger_data_dict_source1, trigger_data_dict_source2)
    
    
    # createExcel(EXCEL_NAME, (EXCEL_SHEET_NAME, df_trigger_data))
    
    
    
    

if __name__ == '__main__':
    main()


