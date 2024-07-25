import requests
import http
import pandas as pd

LIST_TASK_URI = "http://172.16.1.85:8080/uc/resources/task/list"
LIST_TASK_ADV_URI = "http://172.16.1.85:8080/uc/resources/task/listadv"

OUTPUT_FILE = 'Excel_API.xlsx'

task_configs = {
    'name': '*',
    'type':  'Task Monitor',
}

task_adv_configs = {
    'taskname': '*',
    'type': 'Task Monitor',
    'updatedTime': '-10d',
}

auth = ('ops.admin','p@ssw0rd')

new_order = ['name', 'type', 'description','sysId','version']

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    return uri


def getListTask():
    response = requests.post(url=LIST_TASK_URI, json=task_configs, auth=auth, headers={'Accept': 'application/json'})
    return response

def getListTaskAdvanced():
    uri = createURI(LIST_TASK_ADV_URI, task_adv_configs)
    print(uri)
    response = requests.get(url=uri, auth=auth, headers={'Accept': 'application/json'})
    return response

def getDataAPI(mode = 0):
    
    if mode == 0:
        response = getListTask()
    else:
        response = getListTaskAdvanced()
        
    status = http.HTTPStatus(response.status_code)
    print(f"{response.status_code} - {status.phrase}: {status.description}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def createDataFrame(API_data):
    if API_data:
        columns = list(API_data[0].keys())
        try:
            return pd.DataFrame(API_data, columns=columns)
        except Exception as e:
            print(f"Error converting JSON to DataFrame: {e}")
            return None
    else:
        return None 
    
def createExcel(API_data, outputfile):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            API_data.to_excel(writer, sheet_name='Sheet', index=False)

        print("File created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")
        
        
def main():
    APIdata = getDataAPI()
    df = createDataFrame(APIdata)
    df = df[new_order]
    #createExcel(df, OUTPUT_FILE)
    print(df)
    
if __name__ == "__main__":
    main()