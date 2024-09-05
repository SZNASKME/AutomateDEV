import asyncio
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTaskAdvancedAPI, updateURI

task_adv_configs_temp = {
    'taskname': '*',
    'businessServices': 'A0076 - Data Warehouse ETL',
}
    


async def listTask():
    
    response = await getListTaskAdvancedAPI(task_adv_configs_temp)
    if response.status_code == 200:
        return response.json()
    else:
        return None



def main():
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    task_list = asyncio.run(listTask())
    print(json.dumps(task_list, indent=4))
    
if __name__ == '__main__':
    main()