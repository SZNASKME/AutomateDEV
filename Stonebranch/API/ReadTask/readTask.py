import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTaskAdvancedAPI, updateURI, updateAuth
from utils.readFile import loadJson
from utils.readExcel import getDataExcel



import multiprocessing

task_adv_configs_temp = {
    'taskname': None,
    #'type': 'taskWorkflow',
    #'businessServices': 'A0417 - AML Management System',
}



def readingAllTask(df, num_process = 4):
    task_list_api = []
    task_list = getListExcel(df)
    task_configs_list = addDataToConfigs(task_list, task_adv_configs_temp, col_name = 'taskname')
    count = multiprocessing.Value('i', 0)
    with multiprocessing.Pool(num_process) as pool_task:
        result_task = pool_task.map(getListTaskAdvancedAPI, task_configs_list)
        #result_task = async_result_task.get()
        print("Waiting for all subprocesses done...")
    pool_task.close()
    pool_task.join()

    for result in result_task:
        if result.status_code == 200:
            for task in result.json():
                task_list_api.append(task)

###########################################################################################

def getListExcel(df, col_name = 'jobName'):
    del_list = []
    for index, row in df.iterrows():
        del_list.append(row[col_name])
    return del_list

def addDataToConfigs(data_list, configs, col_name = 'name'):
    new_list = []
    for data in data_list:
        new_configs = configs.copy()
        new_configs[col_name] = data
        new_list.append(new_configs)
    return new_list

###########################################################################################

def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    
    df = getDataExcel()
    exist_reading_task = readingAllTask(df)
    