import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.loadFile import loadJson
from utils.readExcel import getDataExcel
from utils.stbAPI import updateURI, updateAuth, deleteTaskInWorkflowAPI

delete_task_configs_temp = {
    'taskname': '',
    'workflowname': '',
}



def deleteTaskInWorkflow(task_name, workflow_name):
    delete_task_configs = delete_task_configs_temp.copy()
    delete_task_configs['taskname'] = task_name
    delete_task_configs['workflowname'] = workflow_name
    response = deleteTaskInWorkflowAPI(delete_task_configs)
    if response.status_code == 200:
        print("Task deleted successfully")
        return True
    else:
        print("Task deletion failed")
        return False

def deleteTaskInWorkflowProcess(df_delete):
    del_count = 0
    for index, row in df_delete.iterrows():
        task_name = row['jobName']
        workflow_name = row['box_name']
        status = deleteTaskInWorkflow(task_name, workflow_name)
        if status:
            del_count += 1
            
    print("Total tasks deleted: ", del_count)
    


def main():
    auth = loadJson('Auth.json')
    #userpass = auth['TTB']
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    #domain = "https://ttbdevstb.stonebranch.cloud/resources"
    domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    df_delete = getDataExcel()
    deleteTaskInWorkflowProcess(df_delete)
    print("Task deletion process completed")

if __name__ == "__main__":
    main()