import stbAPI as API
import json

task_configs_temp = {
    'name': '*',
}


TASK_TYPE = ['Workflow','Timer','Windows','Linux/Unix','z/OS','Agent File Monitor','Manual','Email','File Transfer','SQL','Remote File Monitor','Task Monitor','Stored Procedure','Universal Command','System Monitor','Application Control','SAP','Variable Monitor','Web Service','Email Monitor','PeopleSoft','Recurring','Universal Monitor','Universal']
API_TASK_TYPE = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,99]

ORIGINAL_BUSSINESS_SERVICES = ['A0329 - Data Warehouse ETL (ODS)']
DESTINATION_BUSSINESS_SERVICES = ['A0329 - Data Warehouse ETL (ODS)']


###########################################################################################

def getTaskListByType(api_task_type, bussiness_service_list):
    task_list_type_dict = { type: [] for type in api_task_type}
    for type in api_task_type:
        for bussiness_service in bussiness_service_list:
            task_configs = task_configs_temp.copy()
            task_configs['businessServices'] = bussiness_service
            task_configs['type'] = type
            response_task_list = API.getListTaskAPI(task_configs)
            if response_task_list.status_code == 200:
                for task in response_task_list.json():
                    if task['name'] not in task_list_type_dict[type]:
                        task_list_type_dict[type].append(task)
        print(len(task_list_type_dict[type]),type)
    return task_list_type_dict


# http://172.16.1.86:8080/u/resources
# https://ttbdevstb.stonebranch.cloud/resources

def main():
    original_DOMAIN = API.DOMAIN
    try:
        origin_domain = 'http://172.16.1.86:8080/u/resources'
        API.updateURI(origin_domain)
        print(API.LIST_TASK_URI)
        task_type_dict = getTaskListByType(API_TASK_TYPE, ORIGINAL_BUSSINESS_SERVICES)
        #print(json.dumps(task_type_dict, indent=4))

        
        destination_domain = 'https://ttbdevstb.stonebranch.cloud/resources'
        API.updateURI(destination_domain)
        print(API.LIST_TASK_URI)
        task_type_dict = getTaskListByType(API_TASK_TYPE, DESTINATION_BUSSINESS_SERVICES)
        #print(json.dumps(task_type_dict, indent=4))
    finally:
        API.DOMAIN = original_DOMAIN
    
    
    
    
    
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()