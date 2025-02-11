import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getTaskAPI
from utils.readFile import loadJson
from utils.createFile import createExcel, createJson

from collections import OrderedDict


workflow_list = [
    'DWH_P_MF_INV3000_D_B',
    'DWH_P_MF_INV3000_M_B'
]


# Non HP & HP Loan Class
# workflow_list = [
#     'DWH_REGULATORY_B',
#     'DWH_LCS_TRIGGER_B',
#     'DI_DWH_LON_CLASS_B',
#     'DWH_XREF_BOT_SOFTLOAN_M_B',
#     'DWH_LON_WRITEOFF_MTHLY_B',
#     'DWH_LON_CLASS_B_NOTI_FIN_B',
#     'DWH_FI_LOAN_CLASS',
#     'DWH_BOT_REL_MTHLY_B',
#     'DWH_SBO_ACCT_B',
#     'DWH_LON_CLASS_NOTIFY_FIN_B',
#     'DWH_LCR.D.02.LCR_CUST_RELATION_B',
#     'DWH_EX_ROS_DWH_EDD_M_B',
#     'DWH_SC_CUST_PROFILE_M_B',
#     'DWH_RPT_LCS_B',
#     'DWH_OFSAA_CL_M.M.UPD_AVG_C',
#     'DWH_AR_TCG_ADJ_B',
#     'DWH_CHK_LCS.TRIG_C'
# ]

# Non HP & HP Stage Migration
# workflow_list = [
#     'DWH_MNL_STAGE_MIG_HP_M_B',
#     'DWH_STAGE_MIGRT_M_HP_B',
#     'DWH_STAGE_MIGRT_ONREQUEST_B',
#     'DWH_MNL_STAGE_MIG_M_B'
# ]

# Non HP & HP Outbound
# workflow_list = [
#     'DWH_CRI_INB_M_B',
#     'DWH_IFRS9_REG_M_B',
#     'DWH_IFRS9_HP_TRIGGER_M_B',
#     'DWH_P_B_SCORE_M_B',
#     'DWH_IFRS9_MONTHLY_B',
#     'DWH_STAGE_MIGRT_M_HP_B.INACT_C',
#     'DWH_IFRS9_MONTHLY.INACT_C',
#     'DWH_IFRS9_BACKUP_M_B',
#     'DWH_IFRS9_MONTHLY_B.SUCCESS_C',
#     'DWH_IFRS9_DAILY_MAIL_B',
#     'DWH_LON_PAMCO_I9_M_B',
#     'DWH_IFRS9_B_SCORE_M.INACT_C'
# ]

# Non HP & HP Inbound
# workflow_list = [
#     'DWH_IFRS9_TRIG_NON_HP_B',
#     'DWH_IFRS9_INBOUND_M_B',
#     'DWH_IFRS9_INBOUND_M_B.SUCCESS_C',
#     'DWH_FEE_TXN_MTHLY_ADJ_B',
#     'DWH_IAS_ADJ_INT_MTH_B',
#     'DWH_PBI_FINANCE_RERUN_B',
#     'DWH_IFRS9_TRIGGER.OSX_SUCCESS_SPOOL_C',
#     'DWH_IFRS9_TRIGGER.OSX_SUCCESS_FTP_C',
#     'DWH_TFRS9_MONTHLY_PL_BY_ACCOUNT_B',
#     'DWH_P_TX_RE_APPRISAL_M_B',
#     'DWH_IFRS9_CONSOLIDATE_B.ON_HOLD_C',
#     'DWH_IFRS9_INBOUND_M_B.ON_HOLD_C',
#     'DWH_IFRS9_HP_INBOUND_M_B.ON_HOLD_C',
#     'DWH_IFRS9_TRIG_NON_HP_ADJ_B',
#     'DWH_IFRS9_INBOUND_D7_B',
#     'DWH_IFRS9_INBOUND_D7_B.FINISH_MAIL_C',
#     'DWH_OFS_OUT_02_MTHLY_B',
#     'DWH_IFRS9_INBOUND_D7_B_SUCCESS_ST_C',
#     'DWH_IFRS9_TRIG_HP_B',
#     'DWH_IFRS9_HP_INBOUND_M_B',
#     'DWH_MNL_OTH_AST_B',
#     'DWH_IFRS9_UPD_ZACC_B',
#     'DWH_IFRS9_CONSOLIDATE_B',
#     'DWH_REG_ZACCHIST_B',
#     'DWH_P_TX_AL_RPT_M_B'
# ]

# Non HP & HP Manual File
# workflow_list = [
#     'DWH_LEASING_MTHLY_B',
#     'DWH_P_KYC_PROD_HLD_MTHLY_B',
#     'DWH_AL_ADJ_AMT_MTHLY_B',
#     'DWH_RM_CSM_MTHLY_B',
#     'DWH_LON_HAIR_CUT_B',
#     'DWH_MNL_BOT_SKIP_PAY_B',
#     'DWH_POST_RLF_M_B',
#     'DWH_POST_RLF_CMCL_CV99_M_B',
#     'DWH_POST_RLF_CMCL_CV99_M_B.INACTIVE_C',
#     'DWH_OMS_LOAD_LO_TDR_B'
# ]

# DWH-RDT
# workflow_list = [
#     'DWH_RDT_DAILY_B',
#     'DWH_RDT_ACS_PREP_M_B',
#     'DWH_RDT_G1_MTHLY_B',
#     'DWH_RDT_G2_MTHLY_B',
#     'DWH_RDT_MONTHLY_CLR_C',
#     'DWH_RDT_ONETIME_M_B',
#     'DWH_RDT_BU_MATRIX_Q_B',
#     'DWH_RDT_INBOUND_M_B',
#     'DWH_RDT_INBOUND_D_B'
# ]

# RDT-DQ
# workflow_list = [
#     'DWH_RDT_DQ_PRG_MANUAL_B',
#     'DWH_RDT_DQ_DAILY_D_B',
#     'DWH_RDT_DQ_MTHLY_G1_M_B',
#     'DWH_RDT_DQ_MTHLY_G2_M_B'
# ]

# DWH-interval
# workflow_list = [
#     'DWH_ATM_TX_B',
#     'DWH_AML_THLIST_CUST_B',
#     'DWH_AML_THLIST_CUST_VT_SRC_B',
#     'DWH_AML_THLIST_CUST_FLG_B',
#     'DWH_CC_OASLOG.5M_B',
#     'DWH_P_MONITOR_B',
#     'DWH_EXIM_IBO_TIMING_B',
#     'CPIC_CPL_DAILY_B',
#     'CPIC_DAILY_B',
#     'CPIC_FRAUD_DAILY_B',
#     'DWH_OMS_DS_DEP_AVG_DAILY_B',
#     'DWH_OMS_PA_POPULATE_DETAIL_LEAVES_D_B',
#     'MQM_CIDM_DAILY_B',
#     'CPIC_FRAUD.1_B',
#     'CPIC_FRAUD.2_B',
#     'CPIC_FRAUD.3_B',
#     'CPIC_FRAUD.4_B',
#     'CPIC_FRAUD_EXP.DELTA_B',
#     'DWH_CPIC_FRAUD_B',
#     'DWH_OMS_LOAD_FX_OTHTXN_MAN_B',
#     'DWH_OMS_LOAD_FX_TXN_FCD_V2_B',
#     'DWH_OMS_LOAD_NR_TRANS_B',
#     'DWH_OMS_UPD_LOAN_BUS_TXT_LOAD_B',
#     'DWH_TPFM_PROC_BRN_LST_B',
#     'DWH_RMI_BLS.D_B',
#     'DWH_OMS_DS_LTV_B',
# ]

# DWH-interval 2
# workflow_list = [
#     'CPIC_CPL_DAILY_B',
#     'CPIC_DAILY_B',
#     'CPIC_FRAUD.1_B',
#     'CPIC_FRAUD.2_B',
#     'CPIC_FRAUD.3_B',
#     'CPIC_FRAUD.4_B',
#     'CPIC_FRAUD_DAILY_B',
#     'CPIC_FRAUD_EXP.DELTA_B',
#     'DWH_AML_THLIST_CUST_B',
#     'DWH_AML_THLIST_CUST_FLG_B',
#     'DWH_AML_THLIST_CUST_VT_SRC_B',
#     'DWH_ATM_TX_B',
#     'DWH_CC_OASLOG.5M_B',
#     'DWH_CPIC_FRAUD_B',
#     'DWH_EXIM_IBO_TIMING_B',
#     'DWH_OMS_DS_DEP_AVG_DAILY_B',
#     'DWH_OMS_DS_LTV_B',
#     'DWH_OMS_LOAD_FX_OTHTXN_MAN_B',
#     'DWH_OMS_LOAD_FX_TXN_FCD_V2_B',
#     'DWH_OMS_LOAD_NR_TRANS_B',
#     'DWH_OMS_PA_POPULATE_DETAIL_LEAVES_D_B',
#     'DWH_OMS_UPD_LOAN_BUS_TXT_LOAD_B',
#     'DWH_OMS_WSHEET_UPD_RPT_BOT_CONSUMER_B',
#     'DWH_P_MONITOR_B',
#     'DWH_RMI_BLS.D_B',
#     'DWH_TPFM_PROC_BRN_LST_B',
#     'MQM_CIDM_DAILY_B',
# ]

CHILDREN_FIELD = "Children"
CHILD_TYPE = "Task Type"
CHILD_LEVEL = "Task Level"
NEXT_NODE = "Next Node"
PREVIOUS_NODE = "Previous Node"

EXCEL_OUTPUT_NAME = "ChildrenExcel\\All Children In INV_3000.xlsx"


task_configs_temp = {
    'taskname': None,
}

#########################################     find children    ################################################

def findChildren(task_name, next_node = [], previous_node = [], level = 0):
    children = {CHILD_TYPE: None, CHILD_LEVEL: level, CHILDREN_FIELD: OrderedDict(), NEXT_NODE: None, PREVIOUS_NODE: None}
    task_configs = task_configs_temp.copy()
    task_configs['taskname'] = task_name
    response = getTaskAPI(task_configs)
    if response.status_code == 200:
        task_data = response.json()
        children[CHILD_TYPE] = task_data['type']
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
            "Taskname": None,
            "Task Level": children_json[CHILD_LEVEL],
            "Task Type": children_json[CHILD_TYPE],
            "Previous Node": None,
            "Next Node": None
        })
    for child_name, child_data in children_json["Children"].items():
        current_path = parent_path + [child_name]
        child_level = child_data[CHILD_LEVEL]
        child_type = child_data["Task Type"]
        next_node = ", ".join(child_data["Next Node"]) if child_data["Next Node"] else None
        previous_node = ", ".join(child_data["Previous Node"]) if child_data["Previous Node"] else None
        rows.append({
            "Path": current_path,
            "Taskname": child_name,
            #"Parent": parent_path[-1] if parent_path else None,
            CHILD_LEVEL: child_level,
            CHILD_TYPE: child_type,
            PREVIOUS_NODE: previous_node,
            NEXT_NODE: next_node
        })
        if child_data["Children"]:
            rows.extend(flattenChildrenHierarchy(child_data, current_path))
    return rows

def listChildrenHierarchyToDataFrameAllInOne(children_dict):
    workflow_children_dict = {}
    df_children_list = []
    max_depth = 0
    for workflow_name, workflow_children in children_dict.items():
        flattened_rows = flattenChildrenHierarchy(workflow_children)
        workflow_children_dict[workflow_name] = flattened_rows
        if flattened_rows:
            max_depth = max(max_depth, max(len(row["Path"]) for row in flattened_rows))
        
    columns = ["Taskname", "Task Type", "Task Level", "Main Workflow"] + [f"Sub Level {i+1}" for i in range(max_depth)] + ["Previous Task", "Next Task"]
    
    for workflow_name, workflow_rows in workflow_children_dict.items():
        for row in workflow_rows:
            padded_path = row["Path"] + [""] * (max_depth - len(row["Path"]))
            if row[CHILD_LEVEL] == 0:
                df_children_list.append([workflow_name, row[CHILD_TYPE], row[CHILD_LEVEL], workflow_name] + padded_path + [row[PREVIOUS_NODE], row[NEXT_NODE]])
            else:
                df_children_list.append([row["Taskname"], row[CHILD_TYPE], row[CHILD_LEVEL], workflow_name] + padded_path + [row[PREVIOUS_NODE], row[NEXT_NODE]])
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
    userpass = auth['ASKME_STB']
    #userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['1.86']
    updateURI(domain)
    
    print("Finding all children of the workflow")
    all_children_dict = searchAllChildrenInWorkflow(workflow_list)
    #print(json.dumps(all_children_dict, indent=10))
    createJson("Deep\\All Children.json", all_children_dict, False)
    print("Preparing the children list")
    
    df_workflow_children_list = listChildrenHierarchyToDataFrameAllInOne(all_children_dict)
    #print(df_workflow_children_list)
    createExcel(EXCEL_OUTPUT_NAME, ("All Children",df_workflow_children_list))
    

if __name__ == "__main__":
    main()