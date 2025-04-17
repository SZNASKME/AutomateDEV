import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateAuth, updateAPIAuth, updateURI, getTaskAPI, runReportAPI

from utils.readFile import loadJson
from utils.createFile import createExcel, createJson
from utils.readExcel import getDataExcel

from io import StringIO


workflow_list = [
    # 'DWH_AFTER_DAILY_B',
    'DWH_MIS_ALL_DAY_B',
    'DWH_MIS_D01_B',
    'DWH_MIS_D02_B',
    'DWH_MIS_D03_B',
    'DWH_MIS_D04_B',
    'DWH_MIS_D05_B',
    'DWH_MIS_D06_B',
    'DWH_MIS_D07_B',
    'DWH_MIS_D08_B',
    'DWH_MIS_D09_B',
    'DWH_MIS_D10_B',
    'DWH_MIS_D11_B',
    'DWH_MIS_D12_B',
    'DWH_MIS_D13_B',
    'DWH_MIS_D14_B',
    'DWH_MIS_D15_B',
    'DWH_MIS_D16_B',
    'DWH_MIS_D17_B',
    'DWH_MIS_D18_B',
    'DWH_MIS_D19_B',
    'DWH_MIS_D20_B',
    'DWH_MIS_D22_B',
    'DWH_MIS_D24_B',
    'DWH_MIS_D25_B',
    'DWH_MIS_D26_B',
    'DWH_MIS_D28_B',
    'DWH_MONTH_END_B',
    # 'DWH_AMLO_MAIN_DAILY_B'

]


REPORT_TITLE = "AskMe - Task Report"


TOPIC_COLUMN = "jobName"





MAIN_WORKFLOW = "Main Workflow"
VERTEX_NAME = "Taskname"
TASK_NAME = "Name"


SECOND_SPECIAL_CASE_SUFFIX = "-TM"

EXCEL_OUTPUT_NAME = "Special case Children In XXXXX.xlsx"


task_configs_temp = {
    'taskname': None,
}

report_configs_temp = {
    'reporttitle': None,
}


###############################################################################################################



def getReport(title_name):
    
    report_configs = report_configs_temp.copy()
    report_configs['reporttitle'] = title_name
    response_csv = runReportAPI(report_configs=report_configs, format_str='csv')
    if response_csv.status_code == 200:
        csv_data = StringIO(response_csv.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        print("Error generating report")
        return None




#########################################     find children    ################################################


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


def findSecondSpecialCase(sub_workflow_vertex, sub_workflow_edges):
    found_special_case_list = []
    for vertex in sub_workflow_vertex:
        vertex_name = vertex['task']['value']
        vertex_next_node = findNextNode(vertex_name, sub_workflow_edges)
        vertex_previous_node = findPreviousNode(vertex_name, sub_workflow_edges)

        if not vertex_previous_node and vertex_name.endswith(SECOND_SPECIAL_CASE_SUFFIX):
            found_special_case_list.append({
                'Taskname': vertex_name,
                'Previous Node': vertex_previous_node,
                'Next Node': vertex_next_node,
            })
    return found_special_case_list



def findSpecialCaseChildren(workflow_list, checking_task_list):
    first_special_case_children_list = []
    second_special_case_children_list = []
    
    
    for workflow_name in workflow_list:
        task_configs = task_configs_temp.copy()
        task_configs['taskname'] = workflow_name
        response_task = getTaskAPI(task_configs)
        if response_task.status_code != 200:
            continue
        task_data = response_task.json()
        if task_data['type'] != "taskWorkflow":
            print(f"Task {workflow_name} is not a workflow task")
            continue
        workflow_vertex = task_data['workflowVertices']
        workflow_edges = task_data['workflowEdges']
        
        for vertex in workflow_vertex:
            vertex_name = vertex['task']['value']
            vertex_next_node = findNextNode(vertex_name, workflow_edges)
            vertex_previous_node = findPreviousNode(vertex_name, workflow_edges)

            if not vertex_previous_node:
                vertex_configs = task_configs.copy()
                vertex_configs['taskname'] = vertex_name
                response_vertex = getTaskAPI(vertex_configs)
                if response_vertex.status_code != 200:
                    continue
                vertex_data = response_vertex.json()
                if vertex_data['type'] == "taskWorkflow":
                    ##
                    first_special_case_children_list.append({
                        'Main Workflow': workflow_name,
                        'Taskname': vertex_name,
                        'Task Go-live': 'Yes' if vertex_name in checking_task_list else 'No',
                        'Previous Node': ' // '.join(vertex_previous_node),
                        'Next Node': ' // '.join(vertex_next_node),
                    })
                    ##
                    sub_workflow_vertex = vertex_data['workflowVertices']
                    sub_workflow_edges = vertex_data['workflowEdges']
                    second_special_case_list = findSecondSpecialCase(sub_workflow_vertex, sub_workflow_edges)
                    if second_special_case_list:
                        for special_case in second_special_case_list:
                            second_special_case_children_list.append({
                                'Main Workflow': workflow_name,
                                'Taskname': vertex_name,
                                'Task Go-live': 'Yes' if vertex_name in checking_task_list else 'No',
                                'Found Taskname': special_case['Taskname'],
                                'Previous Node': ' // '.join(special_case['Previous Node']),
                                'Next Node': ' // '.join(special_case['Next Node']),
                            })
                            
                            
    df_first_special_case_children_list = pd.DataFrame(first_special_case_children_list)
    df_second_special_case_children_list = pd.DataFrame(second_special_case_children_list)
    
    return df_first_special_case_children_list, df_second_special_case_children_list
            
            
            
            

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


############################################################################################################


def main():
    
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.174']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    updateURI(domain)
    
    df_task = getReport(REPORT_TITLE)
    
    checking_task_list = df_task[TASK_NAME].tolist()
    
    
    
    #userpass = auth['TTB_PROD']
    userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    #updateAPIAuth(userpass["API_KEY"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_PROD']
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.86']
    updateURI(domain)
    
    df_job_list = getDataExcel("Get Excel Job List")
    workflow_list = df_job_list[TOPIC_COLUMN].tolist()
    print(f"Total workflows: {len(workflow_list)}")
    print("Finding all children of the workflow")
    df_first, df_second = findSpecialCaseChildren(workflow_list, checking_task_list)
    #print(json.dumps(all_children_dict, indent=10))
    #createJson("Deep\\All Children.json", all_children_dict, False)
    print("Preparing the children list")

    #print(df_workflow_children_list)
    createExcel(EXCEL_OUTPUT_NAME, ("CASE 1", df_first), ("CASE 2", df_second))


if __name__ == "__main__":
    main()