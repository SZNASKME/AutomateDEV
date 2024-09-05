import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTriggerAPI, getListTriggerAdvancedAPI, updateURI, updateAuth
from utils.loadFile import loadJson
from utils.readExcel import getDataExcel
import json

trigger_configs_temp = {
    "name": '*',
}

trigger_adv_configs_temp = {
    "triggername": '*',
}

TRIIGER_TYPE = ['Cron','Time','Agent File Monitor','Temporary','Task Monitor','Manual','Application Monitor','Composite','Variable Monitor','Email Monitor','Universal Monitor']

API_TRIGGER_TYPE = [1,2,3,4,5,6,8,9,10,11,12]


BUSSINESS_SERVICES = ['A0329 - Data Warehouse ETL (ODS)']

def getTriggerListByBussinessServices(api_trigger_type, bussiness_service_list):
    trigger_list_type_dict = { type: [] for type in api_trigger_type}
    for type in api_trigger_type:
        for bussiness_service in bussiness_service_list:
            trigger_configs = trigger_adv_configs_temp.copy()
            trigger_configs['businessServices'] = bussiness_service
            trigger_configs['type'] = type
            response_trigger_list = getListTriggerAdvancedAPI(trigger_configs)
            if response_trigger_list.status_code == 200:
                for trigger in response_trigger_list.json():
                    if trigger['name'] not in trigger_list_type_dict[type]:
                        trigger_list_type_dict[type].append(trigger)
        print(len(trigger_list_type_dict[type]),type)
    return trigger_list_type_dict

def getTriggerListByType(api_trigger_type, bussiness_service_list):
    trigger_list_type_dict = { type: [] for type in api_trigger_type}
    for type in api_trigger_type:
        for bussiness_service in bussiness_service_list:
            trigger_configs = trigger_configs_temp.copy()
            #trigger_configs['businessServices'] = bussiness_service
            trigger_configs['type'] = type
            response_trigger_list = getListTriggerAPI(trigger_configs)
            if response_trigger_list.status_code == 200:
                for trigger in response_trigger_list.json():
                    if trigger['name'] not in trigger_list_type_dict[type]:
                        trigger_list_type_dict[type].append(trigger)
        print(len(trigger_list_type_dict[type]),type)
    return trigger_list_type_dict

def compareTriggerType(trigger_type_key, trigger_type_list):
    if trigger_type_key == 1 or trigger_type_key == 'Cron':
        return trigger_type_list[0]
    elif trigger_type_key == 2 or trigger_type_key == 'Time':
        return trigger_type_list[1]
    elif trigger_type_key == 3 or trigger_type_key == 'File Trigger':
        return trigger_type_list[2]
    elif trigger_type_key == 4 or trigger_type_key == 'Temporary':
        return trigger_type_list[3]
    elif trigger_type_key == 5 or trigger_type_key == 'Task Monitor':
        return trigger_type_list[4]
    elif trigger_type_key == 6 or trigger_type_key == 'Manual':
        return trigger_type_list[5]
    elif trigger_type_key == 8 or trigger_type_key == 'Application Monitor':
        return trigger_type_list[6]
    elif trigger_type_key == 9 or trigger_type_key == 'Composite':
        return trigger_type_list[7]
    elif trigger_type_key == 10 or trigger_type_key == 'Variable Monitor':
        return trigger_type_list[8]
    elif trigger_type_key == 11 or trigger_type_key == 'Email Monitor':
        return trigger_type_list[9]
    elif trigger_type_key == 12 or trigger_type_key == 'Universal Monitor':
        return trigger_type_list[10]
    else:
        return trigger_type_key

def changeTriggerTypeKey(trigger_dict, trigger_type):
    new_dict = {}
    for key, value in trigger_dict.items():
        new_key = compareTriggerType(key, trigger_type)
        new_dict[new_key] = value
    return new_dict



###########################################################################################

def startWithAny(prefix_list, string: str):
    for prefix in prefix_list:
        if string.startswith(prefix):
            return True
    return False

def filterListByDataFrame(list_api, df, col_name, value_name):
    new_list = []
    for value in list_api:
        if startWithAny(df[col_name], value[value_name]):
            new_list.append(value)
    return new_list

def filterDataFrameByList(list_api, df, col_name, value_name):
    new_list = []
    for index, row in df.iterrows():
        if startWithAny(list_api, row[col_name]):
            new_list.append(row)
    return new_list
    


def filterDictListNameByDataFrame(list_api, df, col_name):
    new_dict_api = { key: [] for key in list_api.keys()}
    for key, value in list_api.items():
        type_list = filterListByDataFrame(value, df, col_name, 'name')
        new_type_list = getSelectedList(type_list, 'name')
        new_dict_api[key] = new_type_list
    return new_dict_api

def filterNonIntersectionDictListName(dict, list_api):
    non_intersection_dict = { key: [] for key in dict.keys()}
    
    for key, value_list in dict.items():
        value2_list = list_api[key]
        new_value_list = getSelectedList(value2_list, 'name')
        non_intersection_dict[key] = [value for value in value_list if value not in new_value_list]
                    
    return non_intersection_dict

def getSelectedList(list, key):
    new_list = []
    for item in list:
        new_list.append(item[key])
    return new_list

def getSelectedDataframe(df, key):
    return df[key].tolist()

def getUniqueList(list):
    new_list = []
    for item in list:
        if item not in new_list:
            new_list.append(item)
    return new_list

def countDictList(dict_list):
    count = 0
    for key, value in dict_list.items():
        count += len(value)
    return count

def countEachDictList(dict_list):
    count_dict = {}
    for key, value in dict_list.items():
        count_dict[key] = len(value)
    return count_dict

###########################################################################################

def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = 'http://172.16.86:8080/uc/resources'
    updateURI(domain)
    
    df = getDataExcel()
    print(df)
    
    trigger_list_api = getTriggerListByType(API_TRIGGER_TYPE, BUSSINESS_SERVICES)
    trigger_business_service_list_api = getTriggerListByBussinessServices(API_TRIGGER_TYPE, BUSSINESS_SERVICES)
    trigger_type_list = filterDictListNameByDataFrame(trigger_list_api, df, 'jobName')
    other_type_list = filterNonIntersectionDictListName(trigger_type_list, trigger_business_service_list_api)
    trigger_type_list_name = changeTriggerTypeKey(trigger_type_list, TRIIGER_TYPE)
    other_type_list_name = changeTriggerTypeKey(other_type_list, TRIIGER_TYPE)
    trigger_count = countDictList(trigger_type_list_name)
    trigger_count_each = countEachDictList(trigger_type_list_name)
    other_count = countDictList(other_type_list_name)
    other_count_each = countEachDictList(other_type_list_name)
    print(json.dumps(trigger_type_list_name, indent = 4))
    for key, value in trigger_count_each.items():
        print(f"Number of {key} : {value}")
    print(f"Number of All Type Trigger : {trigger_count}")
    print('---------------------------------')
    print(json.dumps(other_type_list_name, indent = 4))
    for key, value in other_count_each.items():
        print(f"Number of {key} : {value}")
    print(f"Number of All Type Other : {other_count}")
    
    
    
    
if __name__ == '__main__':
    main()