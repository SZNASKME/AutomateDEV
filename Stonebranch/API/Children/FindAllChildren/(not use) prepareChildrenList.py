import sys
import os
import pandas as pd
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readFile import loadJson
from utils.createFile import createExcel

JSON_FILE = "DWH_ONICE_ONHOLD_B_children.json"
TASK_NAME = "DWH_ONICE_ONHOLD_B"

def prepareChildrenList(children_dict, parent_name, children_list):
    if children_dict["Children"]:
        for childname, child_data in children_dict["Children"].items():
            child_level = child_data["Child Level"]
            child_type = child_data["Child Type"]
            next_node = child_data["Next Node"]
            if next_node == []:
                next_node = None
            children_list.append({
                'Taskname': childname,
                'workflow': parent_name,
                'Child Level': child_level,
                'Child Type': child_type,
                'Next Node': next_node
            })
            if child_data["Children"]:
                children_list = prepareChildrenList(child_data, childname, children_list)
    return children_list


def prepareChildrenListAllLevel(children_json, task_name):
    children_list = []
    children_list = prepareChildrenList(children_json, task_name, children_list)
    return children_list


def main():
    children_json = loadJson(JSON_FILE,2,"API\\FindAllChildren\\DWF")
    children_list = prepareChildrenListAllLevel(children_json, TASK_NAME)
    df_children = pd.DataFrame(children_list)
    createExcel("ChildrenExcel\\{0}.xlsx".format(JSON_FILE.split('.')[0]), ("Children List", df_children))
    
    
if __name__ == "__main__":
    main()