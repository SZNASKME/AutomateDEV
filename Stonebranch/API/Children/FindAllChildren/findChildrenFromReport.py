import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from io import StringIO
from utils.stbAPI import updateAuth, updateAPIAuth, updateURI, runReportAPI
from utils.readFile import loadJson
from utils.createFile import createExcel, createJson
from utils.readExcel import getDataExcel

from collections import OrderedDict


workflow_list = [
    #'DWH_P_FLPN_D_B',
    #'DWH_P_FLPN_M_B'
    # 'DWH_AFTER_DAILY_B',
    'DWH_MIS_ALL_DAY_B',
    # 'DWH_MIS_D01_B',
    # 'DWH_MIS_D02_B',
    # 'DWH_MIS_D03_B',
    # 'DWH_MIS_D04_B',
    # 'DWH_MIS_D05_B',
    # 'DWH_MIS_D06_B',
    # 'DWH_MIS_D07_B',
    # 'DWH_MIS_D08_B',
    # 'DWH_MIS_D09_B',
    # 'DWH_MIS_D10_B',
    # 'DWH_MIS_D11_B',
    # 'DWH_MIS_D12_B',
    # 'DWH_MIS_D13_B',
    # 'DWH_MIS_D14_B',
    # 'DWH_MIS_D15_B',
    # 'DWH_MIS_D16_B',
    # 'DWH_MIS_D17_B',
    # 'DWH_MIS_D18_B',
    # 'DWH_MIS_D20_B',
    # 'DWH_MIS_D22_B',
    # 'DWH_MIS_D24_B',
    # 'DWH_MIS_D25_B',
    # 'DWH_MIS_D26_B',
    # 'DWH_MIS_D28_B',
    # 'DWH_MONTH_END_B',
    # 'DWH_AMLO_MAIN_DAILY_B'

]

TOPIC_COLUMN = "jobName"

MAIN_WORKFLOW = "Main Workflow"
VERTEX_REPORT_TITLE = 'AskMe - Workflow Vertices'#'UAC - Workflow List Of Tasks By Workflow'


EXCEL_OUTPUT_NAME = "ChildrenExcel\\All Children In XXXXX.xlsx"


task_configs_temp = {
    'taskname': None,
}

report_configs_temp = {
    #'reporttitle': 'UAC - Task List Credential By Task',
    'reporttitle': None,
}

#########################################     find children    ################################################

def findChildren(workflow_name, df_workflow_vertex, visited=None):
    if visited is None:
        visited = set()
    if workflow_name in visited:
        return {"Workflow": workflow_name, "Children": OrderedDict()}  # Prevent infinite loops

    visited.add(workflow_name)
    children_dict = {"Workflow": workflow_name, "Children": OrderedDict()}

    # Filter the DataFrame for the specific workflow
    df_filtered = df_workflow_vertex[df_workflow_vertex['Workflow'] == workflow_name]

    for index, row in df_filtered.iterrows():
        child_name = row['Task']

        # Check if this child is also a workflow (i.e., appears in the Workflow column)
        if child_name in df_workflow_vertex['Workflow'].values:
            # Recursively find children for this workflow
            child_data = findChildren(child_name, df_workflow_vertex, visited)
        else:
            # Not a workflow, just add as a leaf
            child_data = {
                "Name": child_name,
                "Children": OrderedDict()
            }

        children_dict["Children"][child_name] = child_data

    return children_dict




def countChildren(children_dict):
    count = 0
    for child_name, child_data in children_dict["Children"].items():
        count += 1  # Count this child
        count += countChildren(child_data)  # Recursively count the child's children
    return count


############################################################################################################

def searchAllChildrenInWorkflow(workflow_list, df_workflow_vertex=None):
    all_children_dict = {}
    
    for workflow_name in workflow_list:
        print(f"Searching children of {workflow_name}")
        all_children_dict[workflow_name] = findChildren(workflow_name, df_workflow_vertex)
        total_children = countChildren(all_children_dict[workflow_name])
        print(f"Total children: {total_children}")
    return all_children_dict


############################################################################################################

def listChildrenHierarchyToDataFrameAllInOne(all_children_dict):
    rows = []

    def traverse(node, path):
        # If this is a leaf node (no children), add the path
        if not node["Children"]:
            rows.append(path)
        else:
            for child_name, child_data in node["Children"].items():
                if "Workflow" in child_data:
                    traverse(child_data, path + [child_data["Workflow"]])
                elif "Name" in child_data:
                    traverse(child_data, path + [child_data["Name"]])
                else:
                    traverse(child_data, path + [child_name])

    for root_workflow, tree in all_children_dict.items():
        traverse(tree, [root_workflow])

    # Find the maximum depth for columns
    max_depth = max(len(row) for row in rows)
    columns = [f"Level_{i+1}" for i in range(max_depth)]

    # Pad rows to max_depth
    padded_rows = [row + [""] * (max_depth - len(row)) for row in rows]

    df = pd.DataFrame(padded_rows, columns=columns)
    return df

#############################################################################################################

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


############################################################################################################


def main():
    auth = loadJson('auth.json')
    #userpass = auth['ASKME_STB']
    #userpass = auth['TTB_PROD']
    userpass = auth['TTB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    #updateAPIAuth(userpass["API_KEY"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_PROD']
    domain = domain_url['TTB_UAT']
    #domain = domain_url['1.173']
    updateURI(domain)
    
    
    
    df_job_list = getDataExcel("Get Excel Job List")
    workflow_list = df_job_list[TOPIC_COLUMN].tolist()
    print(f"Total workflows: {len(workflow_list)}")
    print("Finding all children of the workflow")
    df_workflow_vertex = getReport(VERTEX_REPORT_TITLE)
    all_children_dict = searchAllChildrenInWorkflow(workflow_list, df_workflow_vertex)
    #print(json.dumps(all_children_dict, indent=10))
    createJson("Deep\\All Children.json", all_children_dict, False)
    print("Preparing the children list")
    
    df_workflow_children_list = listChildrenHierarchyToDataFrameAllInOne(all_children_dict)
    #print(df_workflow_children_list)
    createExcel(EXCEL_OUTPUT_NAME, ("All Children",df_workflow_children_list))
    

if __name__ == "__main__":
    main()