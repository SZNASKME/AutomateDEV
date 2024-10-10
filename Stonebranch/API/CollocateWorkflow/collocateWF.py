import asyncio
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import getListTaskAdvancedAPI, updateURI, updateAuth
from utils.readFile import loadJson

task_adv_configs_temp = {
    'taskname': '*',
    'type': 1,
    'businessServices': 'A0076 - Data Warehouse ETL',
}
    


async def listTask():
    
    response = await getListTaskAdvancedAPI(task_adv_configs_temp)
    if response.status_code == 200:
        return response.json()
    else:
        return None



def prepareCollocateWorkflow(workflow_list):
    workflow_data_dict = {}
    for workflow_data in workflow_list:
        if workflow_data['workflowVertices']:
            vertex_list = []
            for vertex in workflow_data['workflowVertices']:
                vertex_list.append(vertex['vertexName'])



def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['1.86']
    updateURI(domain)
    task_list = asyncio.run(listTask())
    print(json.dumps(task_list, indent=4))
    
if __name__ == '__main__':
    main()