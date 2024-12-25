import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getTaskAPI
from utils.readFile import loadJson
from utils.createFile import createExcel, createJson

from collections import OrderedDict

workflow_list = [
    #'DI_DWH_LCS_S.MN_B'
]

CHILDREN_FIELD = "Children"
CHILD_TYPE = "Task Type"
CHILD_LEVEL = "Task Level"
NEXT_NODE = "Next Node"
PREVIOUS_NODE = "Previous Node"


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
#     return children_list

def flattenChildrenHierarchy(children_json, parent_path=None):
    if parent_path is None:
        parent_path = []

    rows = []
    for child_name, child_data in children_json["Children"].items():
        current_path = parent_path + [child_name]
        child_level = child_data["Task Level"]
        child_type = child_data["Task Type"]
        next_node = ", ".join(child_data["Next Node"]) if child_data["Next Node"] else None
        previous_node = ", ".join(child_data["Previous Node"]) if child_data["Previous Node"] else None
        rows.append({
            "Path": current_path,
            "Taskname": child_name,
            #"Parent": parent_path[-1] if parent_path else None,
            "Task Level": child_level,
            "Task Type": child_type,
            "Previous Node": previous_node,
            "Next Node": next_node
        })
        if child_data["Children"]:
            rows.extend(flattenChildrenHierarchy(child_data, current_path))
    return rows

def listChildrenHierarchyToDataFrame(children_dict):
    workflow_children_dict = {}
    df_children_list = []
    max_depth = 0
    for workflow_name, workflow_children in children_dict.items():
        flattened_rows = flattenChildrenHierarchy(workflow_children)
        workflow_children_dict[workflow_name] = flattened_rows
        max_depth = max(max_depth, max(len(row["Path"]) for row in flattened_rows))
        
    columns = ["Taskname", "Task Type", "Task Level", "Main Workflow"] + [f"Sub Level {i+1}" for i in range(max_depth)] + ["Previous Task", "Next Task"]
    
    for workflow_name, workflow_rows in workflow_children_dict.items():
        for row in workflow_rows:
            padded_path = row["Path"] + [""] * (max_depth - len(row["Path"]))
            df_children_list.append([row["Taskname"], row["Task Type"], row["Task Level"], workflow_name] + padded_path + [row["Previous Node"], row["Next Node"]])
            #print(json.dumps(data, indent=10))
    df_children_list = pd.DataFrame(df_children_list, columns=columns)

    return df_children_list

############################################################################################################


def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    #userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.86']
    updateURI(domain)
    
    print("Finding all children of the workflow")
    all_children_dict = searchAllChildrenInWorkflow(workflow_list)
    #print(json.dumps(all_children_dict, indent=10))
    createJson("Deep\\All Children.json", all_children_dict, False)
    print("Preparing the children list")
    df_workflow_children_list = listChildrenHierarchyToDataFrame(all_children_dict)
    #print(df_workflow_children_list)
    createExcel("ChildrenExcel\\All Children In Workflow.xlsx", ("All Children",df_workflow_children_list))
    

if __name__ == "__main__":
    main()