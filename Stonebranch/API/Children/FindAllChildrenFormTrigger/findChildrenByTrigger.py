import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getTaskAPI, getTriggerAPI
from utils.readFile import loadJson
from utils.createFile import createExcel, createJson

from collections import OrderedDict


trigger_list = [
    'DWH_PROMPTPAY_INFO_D_B-ND-TRTM001',
    'DWH_DEP.M.CURR.LDR_C-ND-TRTM001',
    'DWH_P_SK_SKPY_CMCRSC_01_D_C-ND-TRTM001',
    'DWH_P_RM_D_B-ND-TRTM001',
    'DWH_LON_D_PRE_ALS_B-ND-TRTM001',
    'DWH_P_HCM_D_B-ND-TRTM001',
    'DWH_CUS_RMCUST_M_B-ND-TRTM001',
    'DWH_DEP.D.CURR.LDR_C-ND-TRTM001',
    'DWH_TMB_CC_CARD_HOLDER_D_B-ND-TRTM001',
    'DWH_CUS_RMCUST_D_B-ND-TRTM001',
    'DWH_ACN_D.NAMEST_B-ND-TRTM001',
    'DWH_DAILY_B-TR001',
    'ODS_DAILY_B-TR001',
    'DWH_P_MF_D_B-TR001',
    'DWH_MIB_IMPORT_MTHLY_B-TR001',
    'DWH_DEP_D.STMT_ODS_B-TR001',
    'DWH_TDR_RELIEF_DAILY_B-TR001',
    'DWH_EMAIL_STATUS_LOG_B-TR001',
    'DWH_HPBD_DAILY_B.CHECK_DT_C-TR001',
    'DWH_SCS_DISPUTE_TRANSACTION_D_TRIGGER_B-TR001',
    'DWH_P_RM_RMCONSENT_D_B-TR001',
    'DWH_AUTO_LOAN_DAILY_B-TR001',
    'DWH_P_ESTAMP_DUTY_D_B-TR001',
    'DWH_CMS_API_D_B-TR001',
    'DWH_PROMPTPAY_INFO_D_B-TR001',
    'DWH_SCV.D.UPD_AR_LN_C.TRIG_C-WF-TR001',
    'DWH_P_HCM_D_B-TR001',
    'DWH_P_MIB_D_B-TR001',
    'DWH_CUS.D.UPD_RMCUS_MAP.NEW_C.TRIG_C-WF-TR001',
    'DWH_CHQ_CHEQUE_IN_RETURN_D_B-TR001',
    'DWH_MIB_IMPORT_DAILY_B-TR001',
    'DWH_SCS_INTEREST_AND_CHARGES_D_TRIGGER_B-TR001',
    'DWH_ALS_PAST_DUE_DAILY_B-TR001',
    'DWH_P_EC_ENTERPRISE_CUSTOMER_D_B-TR001',
    'DWH_P_CTUNI_D_B-TR001',
    'DWH_P_IM_MTTXN_D_B-TR001',
    'DWH_P_CTUNI_MIB_B-TR001',
    'DWH_P_SCS_MODEL_D_B-TR001',
    'DWH_P_ST_MTTXN_D_B-TR001',
    'DWH_P_ALSPAMC_D_B-TR001',
    'DWH_P_ALSBILL_D_B-TR001'
]
   

CHILDREN_FIELD = "Children"
CHILD_TYPE = "Task Type"
CHILD_LEVEL = "Task Level"
NEXT_NODE = "Next Node"
PREVIOUS_NODE = "Previous Node"
BUSNESS_SERVICE = "Business Service"

EXCEL_OUTPUT_NAME = "ChildrenExcel\\All Children In XXXX.xlsx"


task_configs_temp = {
    'taskname': None,
}

trigger_configs_temp = {
    'triggername': None,
}



#######################################

def findWorkflowByTrigger(trigger_list):
    trigger_workflow_dict = {}
    workflow_list = []
    for trigger_name in trigger_list:
        trigger_configs = trigger_configs_temp.copy()
        trigger_configs['triggername'] = trigger_name
        response = getTriggerAPI(trigger_configs)
        if response.status_code == 200:
            trigger_data = response.json()
            task_by_trigger = trigger_data['tasks']
            for task_name in task_by_trigger:
                if task_name not in trigger_workflow_dict:
                    trigger_workflow_dict[task_name] = []
                trigger_workflow_dict[task_name].append(trigger_name)
                if task_name not in workflow_list:
                    workflow_list.append(task_name)
    
    return trigger_workflow_dict, workflow_list




#########################################     find children    ################################################

def findChildren(task_name, next_node=None, previous_node=None, level=0):
    if next_node is None:
        next_node = []
    if previous_node is None:
        previous_node = []
    children = {CHILD_TYPE: None, BUSNESS_SERVICE: None, CHILD_LEVEL: level, CHILDREN_FIELD: OrderedDict(), NEXT_NODE: None, PREVIOUS_NODE: None}
    task_configs = task_configs_temp.copy()
    task_configs['taskname'] = task_name
    response = getTaskAPI(task_configs)
    if response.status_code == 200:
        task_data = response.json()
        children[CHILD_TYPE] = task_data['type']
        children[BUSNESS_SERVICE] = ", ".join(task_data["opswiseGroups"])
        if task_data['type'] == "taskWorkflow":
            for child in task_data['workflowVertices']:
                child_name = child['task']['value']
                child_next_node = findNextNode(child_name, task_data['workflowEdges'])
                child_previous_node = findPreviousNode(child_name, task_data['workflowEdges'])
                children["Children"][child_name] = findChildren(child_name, child_next_node, child_previous_node, level + 1)
                
        if len(next_node) > 0:
            children[NEXT_NODE] = next_node
        else:
            children[NEXT_NODE] = []
            
        if len(previous_node) > 0:
            children[PREVIOUS_NODE] = previous_node
        else:
            children[PREVIOUS_NODE] = []
    
    return children

def findNextNode(task_name, workflowEdges):
    next_node = []
    for edge in workflowEdges:
        if edge['sourceId']['taskName'] == task_name:
            next_node.append(f"{edge['targetId']['taskName']} ({edge['condition']['value']})")
    return next_node

def findPreviousNode(task_name, workflowEdges):
    previous_node = []
    for edge in workflowEdges:
        if edge['targetId']['taskName'] == task_name:
            previous_node.append(f"{edge['sourceId']['taskName']} ({edge['condition']['value']})")
    return previous_node

def countChildren(children_dict):
    count = 0
    for child_name, child_data in children_dict["Children"].items():
        count += 1  # Count this child
        count += countChildren(child_data)  # Recursively count the child's children
    return count

############################################################################################################

def searchAllChildrenInWorkflow(workflow_list):
    all_children_dict = {}
    for workflow_name in workflow_list:
        print(f"Searching children of {workflow_name}")
        all_children_dict[workflow_name] = findChildren(workflow_name)
        total_children = countChildren(all_children_dict[workflow_name])
        print(f"Total children: {total_children}")
    return all_children_dict


############################################################################################################

# def prepareChildrenList(children_json, parent_name, children_list):
#     if children_json["Children"]:
#         for childname, child_data in children_json["Children"].items():
#             child_level = child_data["Child Level"]
#             child_type = child_data["Child Type"]
#             next_node = child_data["Next Node"]
#             if next_node == []:
#                 next_node = None
#             children_list.append({
#                 'Taskname': childname,
#                 'workflow': parent_name,
#                 'Child Level': child_level,
#                 'Child Type': child_type,
#                 'Next Node': next_node
#             })
#             if child_data["Children"]:
#                 children_list = prepareChildrenList(child_data, childname, children_list)
#     return children_list


# def prepareChildrenListAllLevel(children_dict):
#     df_all_children_list = {}
#     for workflow_name, children_dict in children_dict.items():
#         children_list = prepareChildrenList(children_dict, workflow_name, children_list)
        
#         df_children_list = pd.DataFrame(children_list)
#         df_all_children_list[workflow_name] = df_children_list
#     return df_all_children_list

def flattenChildrenHierarchy(children_json, parent_path=None):
    if parent_path is None:
        parent_path = []

    rows = []
    if children_json["Task Level"] == 0:
        rows.append({
            "Path": parent_path,
            "Business Service": children_json[BUSNESS_SERVICE],
            "Taskname": None,
            "Task Level": children_json[CHILD_LEVEL],
            "Task Type": children_json[CHILD_TYPE],
            "Previous Node": None,
            "Next Node": None
        })
    for child_name, child_data in children_json["Children"].items():
        current_path = parent_path + [child_name]
        child_business_service = child_data[BUSNESS_SERVICE]
        child_level = child_data[CHILD_LEVEL]
        child_type = child_data["Task Type"]
        next_node = ", ".join(child_data["Next Node"]) if child_data["Next Node"] else None
        previous_node = ", ".join(child_data["Previous Node"]) if child_data["Previous Node"] else None
        rows.append({
            "Path": current_path,
            "Taskname": child_name,
            BUSNESS_SERVICE: child_business_service,
            CHILD_LEVEL: child_level,
            CHILD_TYPE: child_type,
            PREVIOUS_NODE: previous_node,
            NEXT_NODE: next_node
        })
        if child_data["Children"]:
            rows.extend(flattenChildrenHierarchy(child_data, current_path))
    return rows

def listChildrenHierarchyToDataFrameAllInOne(children_dict, trigger_workflow_dict):
    workflow_children_dict = {}
    df_children_list = []
    max_depth = 0
    for workflow_name, workflow_children in children_dict.items():
        flattened_rows = flattenChildrenHierarchy(workflow_children)
        workflow_children_dict[workflow_name] = flattened_rows
        if flattened_rows:
            max_depth = max(max_depth, max(len(row["Path"]) for row in flattened_rows))
    
    columns = ["Business Service", "Trigger(s)", "Taskname", "Task Type", "Task Level", "Main Workflow"] + [f"Sub Level {i+1}" for i in range(max_depth)] + ["Previous Task", "Next Task"]
    trigger_list = trigger_workflow_dict.get(workflow_name, [])
    
    for workflow_name, workflow_rows in workflow_children_dict.items():
        trigger_list = trigger_workflow_dict.get(workflow_name, [])
        for row in workflow_rows:
            padded_path = row["Path"] + [""] * (max_depth - len(row["Path"]))
            if row[CHILD_LEVEL] == 0:
                df_children_list.append([row[BUSNESS_SERVICE], ", ".join(trigger_list) , workflow_name, row[CHILD_TYPE], row[CHILD_LEVEL], workflow_name] + padded_path + [row[PREVIOUS_NODE], row[NEXT_NODE]])
            else:
                df_children_list.append([row[BUSNESS_SERVICE], ", ".join(trigger_list), row["Taskname"], row[CHILD_TYPE], row[CHILD_LEVEL], workflow_name] + padded_path + [row[PREVIOUS_NODE], row[NEXT_NODE]])
            #print(json.dumps(data, indent=10))
    df_children_list = pd.DataFrame(df_children_list, columns=columns)

    return df_children_list

# def listChildrenHierarchyToDataFrameSeparate(children_dict):
#     workflow_children_dict = {}
#     df_children_list = []
#     max_depth = 0
#     for workflow_name, workflow_children in children_dict.items():
#         flattened_rows = flattenChildrenHierarchy(workflow_children)
#         workflow_children_dict[workflow_name] = flattened_rows
#         max_depth = max(max_depth, max(len(row["Path"]) for row in flattened_rows))
        
#     columns = ["Taskname", "Task Type", "Task Level", "Main Workflow"] + [f"Sub Level {i+1}" for i in range(max_depth)] + ["Previous Task", "Next Task"]
    
#     for workflow_name, workflow_rows in workflow_children_dict.items():
#         for row in workflow_rows:
#             padded_path = row["Path"] + [""] * (max_depth - len(row["Path"]))
#             df_children_list.append([row["Taskname"], row["Task Type"], row["Task Level"], workflow_name] + padded_path + [row["Previous Node"], row["Next Node"]])
#             #print(json.dumps(data, indent=10))
#     df_children_list = pd.DataFrame(df_children_list, columns=columns)

#     return df_children_list


############################################################################################################


def main():
    auth = loadJson('auth.json')
    #userpass = auth['ASKME_STB']
    userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.86']
    updateURI(domain)
    
    print("Finding all workflows")
    trigger_workflow_dict, workflow_list = findWorkflowByTrigger(trigger_list)
    print("Finding all children of the workflow")
    all_children_dict = searchAllChildrenInWorkflow(workflow_list)
    #print(json.dumps(all_children_dict, indent=10))
    createJson("Deep\\All Children.json", all_children_dict, False)
    print("Preparing the children list")
    
    df_workflow_children_list = listChildrenHierarchyToDataFrameAllInOne(all_children_dict, trigger_workflow_dict)
    #print(df_workflow_children_list)
    createExcel(EXCEL_OUTPUT_NAME, ("All Children",df_workflow_children_list))
    

if __name__ == "__main__":
    main()