import http
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTaskAdvancedAPI, updateURI, updateAuth
from utils.readFile import loadJson
from utils.createExcel import createExcel

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


def getData():
    
    response = getListTaskAdvancedAPI()
        
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
        
        
def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    
    APIdata = getData()
    df = createDataFrame(APIdata)
    df = df[new_order]
    #createExcel(OUTPUT_FILE,(df, 'Sheet'))
    print(df)
    
if __name__ == "__main__":
    main()