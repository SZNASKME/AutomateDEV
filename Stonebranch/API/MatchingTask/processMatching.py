import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import json
import pandas as pd
import math
from Stonebranch.utils.readFile import loadJson
from utils.stbAPI import updateURI, updateAuth, getListTaskAPI


task_configs_temp = {
    'name': '*',
}


TASK_TYPE = ['Workflow','Timer','Windows','Linux/Unix','z/OS','Agent File Monitor','Manual','Email','File Transfer','SQL','Remote File Monitor','Task Monitor','Stored Procedure','Universal Command','System Monitor','Application Control','SAP','Variable Monitor','Web Service','Email Monitor','PeopleSoft','Recurring','Universal Monitor','Universal']
API_TASK_TYPE = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,99]

ORIGINAL_BUSSINESS_SERVICES = ['A0076 - Data Warehouse ETL']
DESTINATION_BUSSINESS_SERVICES = ['A0076 - Data Warehouse ETL']


###########################################################################################

def compareTaskTypeDict(ori_task_type_dict, des_task_type_dict):
    complete_dict = {}
    error_dict = {}
    for type in API_TASK_TYPE:
        complete_list, error_list = compareTaskList(ori_task_type_dict[type], des_task_type_dict[type], 'name', 'sysId')
        complete_dict[type] = complete_list
        error_dict[type] = error_list
    return {
        "valid": complete_dict,
        "err": error_dict
    }
    
def compareTaskList(ori_task_list, des_task_list, matching_field, compare_field):
    complete_list = []
    error_list = []
    ori_df = pd.DataFrame(ori_task_list)
    des_df = pd.DataFrame(des_task_list)
    if ori_df.empty:
        return complete_list, error_list
    if des_df.empty:
        return complete_list, error_list
    
    merge_df = pd.merge(ori_df, des_df, on = matching_field, how = 'outer', suffixes = ('_ori','_des'))
    ori_not_found = merge_df[merge_df[compare_field+'_des'].isna()]
    des_not_found = merge_df[merge_df[compare_field+'_ori'].isna()]
    both_found = merge_df[merge_df[compare_field+'_ori'].notna() & merge_df[compare_field+'_des'].notna()]
    not_match = merge_df[merge_df[compare_field+'_ori'] != merge_df[compare_field+'_des']]
    
    for index, row in ori_not_found.iterrows():
        error_list.append({row[matching_field]: {'ori': row[compare_field+'_ori'], 'des': None}})
    for index, row in des_not_found.iterrows():
        error_list.append({row[matching_field]: {'ori': None, 'des': row[compare_field+'_des']}})
    for index, row in not_match.iterrows():
        error_list.append({row[matching_field]: {'ori': row[compare_field+'_ori'], 'des': row[compare_field+'_des']}})
    
    for index, row in both_found.iterrows():
        complete_list.append({row[matching_field]: {'ori': row[compare_field+'_ori'], 'des': row[compare_field+'_des']}})
    
    return complete_list, error_list


def getTaskListByType(api_task_type, bussiness_service_list):
    task_list_type_dict = { type: [] for type in api_task_type}
    for type in api_task_type:
        for bussiness_service in bussiness_service_list:
            task_configs = task_configs_temp.copy()
            task_configs['businessServices'] = bussiness_service
            task_configs['type'] = type
            response_task_list = getListTaskAPI(task_configs)
            if response_task_list.status_code == 200:
                for task in response_task_list.json():
                    if task['name'] not in task_list_type_dict[type]:
                        task_list_type_dict[type].append(task)
    return task_list_type_dict


###########################################################################################

def analysisCase(compared_dict):
    ori_not_found = []
    des_not_found = []
    both_not_found = []
    not_match = []
    for key, value in compared_dict.items():
        if value:
            print(f"Task Type: {key}")
            for task in value:
                for task_name, task_info in task.items():
                    if task_info['ori'] == None and task_info['des'] != None:
                        ori_not_found.append(f"{task_name} {key}")
                    elif task_info['des'] == None and task_info['ori'] != None:
                        des_not_found.append(f"{task_name} {key}")
                    elif task_info['ori'] == None and task_info['des'] == None:
                        both_not_found.append(f"{task_name} {key}")
                    elif task_info['ori'] != None and task_info['des'] != None and task_info['ori'] != task_info['des']:
                        not_match.append(f"{task_name} {key}")

    if len(ori_not_found) > 0:
        print(f"Original Task not found:\n{json.dumps(ori_not_found, indent=4)}")
    if len(des_not_found) > 0:
        print(f"Destination Task not found:\n{json.dumps(des_not_found, indent=4)}")
    if len(both_not_found) > 0:
        print(f"Both Task not found:\n{json.dumps(both_not_found, indent=4)}")
    if len(not_match) > 0:
        print(f"Task not match:\n{json.dumps(not_match, indent=4)}")
        
    print(f"Total Task not found in Original: {len(ori_not_found)}")
    print(f"Total Task not found in Destination: {len(des_not_found)}")
    print(f"Total Task not found in Both: {len(both_not_found)}")
    print(f"Total Task not match: {len(not_match)}")

# http://172.16.1.86:8080/u/resources
# https://ttbdevstb.stonebranch.cloud/resources

def main():
    try:
        auth = loadJson('Auth.json')
        userpass = auth['ASKME_STB']
        updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
        origin_domain = 'http://172.16.1.86:8080/uc/resources'
        updateURI(origin_domain)
        #print(API.LIST_TASK_URI)
        ori_task_type_dict = getTaskListByType(API_TASK_TYPE, ORIGINAL_BUSSINESS_SERVICES)

        destination_domain = 'https://ttbdevstb.stonebranch.cloud/resources'
        updateURI(destination_domain)
        Auth = loadJson('Auth.json')
        userpass = Auth['TTB']
        updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
        
        #print(API.LIST_TASK_URI)
        des_task_type_dict = getTaskListByType(API_TASK_TYPE, DESTINATION_BUSSINESS_SERVICES)
        compared_dict = compareTaskTypeDict(ori_task_type_dict, des_task_type_dict)
    finally:
        
        print(json.dumps(compared_dict['err'], indent=4))
        analysisCase(compared_dict['err'])
    
    
    
    
    
    
if __name__ == "__main__":
    main()