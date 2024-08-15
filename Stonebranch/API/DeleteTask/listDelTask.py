from readExcel import getDataExcel
from stbAPI import getListTaskAPI, getListTriggerAPI, getListTaskAdvancedAPI, getListTriggerAdvancedAPI
from delProcess import deleteProcess
import pandas as pd
import multiprocessing
import json



BUSINESS_SERVICES = "A0417 - AML Management System"

TASK_TYPE = ['taskWorkflow','taskUniversal','taskSleep','taskMonitor','taskFileMonitor']

API_TASK_TYPE = [1,99,2,12,6]

BUSSINESS_SERVICE_LIST = [
    "A0127 - Market and Liquidity Risk Management  -  Ambit Focus",
    "A0341 - Core GL System",
    "A0357 - IFRS9 system",
    "A0357-1 - IFRS9 (HP) system",
    "A0455 - Core Hire Purchase"
]

task_adv_configs_temp = {
    'taskname': '*',
    #'type': None,
    'businessServices': None,
}

task_configs_temp = {
    'name': '*',
    #'type': None,
    #'businessServices': None,
    'updatedTime': 'd',
}

trigger_configs_temp = {
    'name': None,
}

trigger_adv_configs_temp = {
    'triggername': '*',
}




###########################################################################################

def getDeleteTaskTrigger(del_list, prefix_list = []):
    del_task_count = 0
    del_trigger_count = 0
    max_del = len(del_list)
    del_task_list_api = []
    del_trigger_list_api = []
    del_list = addWildCardSuffix(del_list)
    
    for del_name in del_list:
        task_configs = task_configs_temp.copy()
        task_configs['name'] = del_name
        trigger_configs = trigger_configs_temp.copy()
        trigger_configs['name'] = del_name
        response_task_list = getListTaskAPI(task_configs)
        response_trigger_list = getListTriggerAPI(trigger_configs)
        #task_status = http.HTTPStatus(response_task_list.status_code)
        #trigger_status = http.HTTPStatus(response_trigger_list.status_code)
        if response_task_list.status_code == 200:
            del_task_count += 1
            for task in response_task_list.json():
                if task['name'] not in del_task_list_api and startWithAny(prefix_list, task['name']):
                    del_task_list_api.append(task)
        if response_trigger_list.status_code == 200:
            del_trigger_count += 1
            for trigger in response_trigger_list.json():
                if trigger['name'] not in del_trigger_list_api and startWithAny(prefix_list, trigger['name']):
                    del_trigger_list_api.append(trigger)
        print(f"{del_task_count},{del_trigger_count}/{max_del} {response_task_list.status_code} - {response_trigger_list.status_code} {del_name}")
        
    return del_task_list_api, del_trigger_list_api
    

def getDeleteTaskTriggerMultiProcessing(del_list, prefix_list = [], num_process=4):
    task_list_api = []
    trigger_list_api = []
    del_list_wildcard = addWildCardSuffix(del_list)
    task_configs_list = addDataToConfigs(del_list_wildcard, task_adv_configs_temp, col_name = 'taskname')
    count = multiprocessing.Value('i', 0)
    with multiprocessing.Pool(num_process, initializer, (count,)) as pool_task:
        result_task = pool_task.map(getListTaskAdvancedAPI, task_configs_list)
        #result_task = async_result_task.get()
        print("Waiting for all subprocesses done...")
    pool_task.close()
    pool_task.join()
    trigger_configs = trigger_configs_temp.copy()
    trigger_configs['name'] = '*'
    result_trigger = getListTriggerAPI(trigger_configs)

    print("All subprocesses done.")
    for result in result_task:
        if result.status_code == 200:
            for task in result.json():
                if task['name'] not in task_list_api and startWithAny(prefix_list, task['name']):
                    task_list_api.append(task)
                    
    if result_trigger.status_code == 200:
        for trigger in result_trigger.json():
            if trigger['name'] not in trigger_list_api and startWithAny(prefix_list, trigger['name']):
                trigger_list_api.append(trigger)
    print(count)
    return task_list_api, trigger_list_api


def getDeleteTaskTriggerbyBusinessService(api_task_type, bussiness_service_list = []):
    task_list_api_type_dict = { type: [] for type in api_task_type }
    trigger_list_api = []
    
    for business_service in bussiness_service_list:
        for api_type in api_task_type:
            task_configs = task_configs_temp.copy()
            task_configs['type'] = api_type
            task_configs['businessServices'] = business_service
            response_task_list = getListTaskAPI(task_configs)
            if response_task_list.status_code == 200:
                for task in response_task_list.json():
                    if task['name'] not in task_list_api_type_dict[api_type]:
                        task_list_api_type_dict[api_type].append(task)
                        
        trigger_configs = trigger_adv_configs_temp.copy()
        trigger_configs['businessServices'] = business_service
        response_trigger_list = getListTriggerAdvancedAPI(trigger_configs)
        if response_trigger_list.status_code == 200:
            for trigger in response_trigger_list.json():
                if trigger['name'] not in trigger_list_api:
                    trigger_list_api.append(trigger)
                    
    return task_list_api_type_dict, trigger_list_api


def separateTaskType(task_list, task_type_list):
    task_type_dict = {}
    for task_type in task_type_list:
        task_type_dict[task_type] = []
    
    for task in task_list:
        if task['type'] in task_type_list:
            task_type_dict[task['type']].append(task)
    
    return task_type_dict

def prepareTaskType(task_type_dict, task_type_list = TASK_TYPE):
    new_task_type_dict = {}
    for key, value in task_type_dict.items():
        compared_task_type = compareTaskType(key, task_type_list)
        new_task_type_dict[compared_task_type] = value
    return new_task_type_dict
        
def compareTaskType(task_type_key, task_type_list):
    if task_type_key == 1 or task_type_key == 'Workflow':
        return task_type_list[0]
    elif task_type_key == 99 or task_type_key == 'Universal':
        return task_type_list[1]
    elif task_type_key == 2 or task_type_key == 'Timer':
        return task_type_list[2]
    elif task_type_key == 12 or task_type_key == 'Task Monitor':
        return task_type_list[3]
    elif task_type_key == 6 or task_type_key == 'Agent File Monitor':
        return task_type_list[4]
    else:
        return task_type_key


#################################    utils      ###########################################

def initializer(cnt):
    global count
    count = cnt

def startWithAny(prefix_list, string: str):
    for prefix in prefix_list:
        if string.startswith(prefix):
            return True
    return False

def getFristPrefixList(data_list):
    prefix_list = []
    for data in data_list:
        prefix_list.append(data.split('_')[0])
    return prefix_list

def addWildCardSuffix(data_list):
    new_list = []
    for i in range(len(data_list)):
        new_list.append(data_list[i] + '*')
    return new_list

def getListExcel(df, col_name = 'jobName'):
    del_list = []
    for index, row in df.iterrows():
        del_list.append(row[col_name])
    return del_list

def groupingName(task_list):
    grouping_list = []
    for row in task_list:
        prefix_row = row.split('.')[0]
        if prefix_row not in grouping_list:
            grouping_list.append(prefix_row)
    return grouping_list

def compareStartWith(list_excel, list_api):
    compared_list = []
    for task in list_api:
        if startWithAny(list_excel, task['name']) or task['name'] in list_excel:
            if task not in compared_list:
                compared_list.append(task)
    
    return compared_list

def getUniqueList(list):
    new_list = []
    for item in list:
        if item not in new_list:
            new_list.append(item)
    return new_list

def createExcel(outputfile, *data):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            for df, sheetname in data:
                df.to_excel(writer, sheet_name=sheetname, index=False)
        print("Delete file created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")

def addDataToConfigs(data_list, configs, col_name = 'name'):
    new_list = []
    for data in data_list:
        new_configs = configs.copy()
        new_configs[col_name] = data
        new_list.append(new_configs)
    return new_list

###########################################################################################
def main():
    #df = getDataExcel()
    
    #del_list_excel = getListExcel(df)
    #print(len(del_list_excel))
    #group_task_list = groupingName(del_list_excel)
    #print(len(group_task_list))
    
    #del_task_list_api, del_trigger_list_api = getDeleteTaskTriggerMultiProcessing(del_list_excel, del_list_excel, num_process=4)
    #del_task_list_api, del_trigger_list_api = getDeleteTaskTriggerMultiProcessing(group_task_list, del_list_excel, num_process=4)
    del_task_list_api_type_dict, del_trigger_list_api = getDeleteTaskTriggerbyBusinessService(API_TASK_TYPE, BUSSINESS_SERVICE_LIST)
    #del_task_list_clean = getUniqueList(del_task_list_api)
    #del_trigger_list_clean = getUniqueList(del_trigger_list_api)
    #print(len(del_task_list_clean), len(del_trigger_list_clean))
    #del_task_type_dict = separateTaskType(del_task_list_api, TASK_TYPE)
    del_task_type_dict = prepareTaskType(del_task_list_api_type_dict)
    #print(json.dumps(compared_del_task_list, indent=4))
    
    dfworkflow = pd.DataFrame(del_task_type_dict['taskWorkflow'])
    dfuniversal = pd.DataFrame(del_task_type_dict['taskUniversal'])
    dfsleep = pd.DataFrame(del_task_type_dict['taskSleep'])
    dfmonitor = pd.DataFrame(del_task_type_dict['taskMonitor'])
    dffilemonitor = pd.DataFrame(del_task_type_dict['taskFileMonitor'])
    #dftask = pd.DataFrame(del_task_list_api)
    dftrigger = pd.DataFrame(del_trigger_list_api)
    
    createExcel('delete_task_trigger.xlsx', (dfworkflow, 'Workflow'), (dfuniversal, 'Universal'), (dfsleep, 'Timer'), (dfmonitor, 'TaskMonitor'), (dffilemonitor, 'AgentFileMonitor'), (dftrigger, 'Trigger'))
    dftask_dict = {
        'taskWorkflow': dfworkflow,
        'taskUniversal': dfuniversal,
        'taskSleep': dfsleep,
        'taskMonitor': dfmonitor,
        'taskFileMonitor': dffilemonitor,
    }
    for key, value in dftask_dict.items():
        print(key, len(value))
    print("Do you want to delete these tasks and triggers? (y/n)")
    choice = input().lower()
    if choice == 'y':
        confirm = input("confirm to continue delete? (confirm/...)").lower()
        if confirm == 'confirm':
            deleteProcess(dftask_dict, dftrigger)
    
if __name__ == "__main__":
    main()