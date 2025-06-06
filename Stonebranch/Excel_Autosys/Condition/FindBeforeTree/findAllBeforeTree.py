import sys
import os
import json
import pandas as pd
import re
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

JOBNAME_COLUMN = 'jobName'
CONDITION_COLUMN = 'condition'
BOXNAME_COLUMN = 'box_name'

sys.setrecursionlimit(10000)


OUTPUT_EXCEL_FILE = 'FindBeforeAfter.xlsx'

CONDITION_PATTERN = re.compile(r"[a-z]\([A-Za-z0-9_\.]+\)")
PARENTHESES_PATTERN = re.compile(r"\(([^()]+)\)")

SELECTED_COLUMN = 'jobName'
FILTER_COLUMN = 'rootBox'


# def getAllInnermostSubstrings(string, start_char, end_char):
#     pattern = re.escape(start_char) + r'([^' + re.escape(start_char) + re.escape(end_char) + r']+)' + re.escape(end_char)
#     # Find all substrings that match the pattern
#     matches = re.findall(pattern, string)
#     return matches

# def getNamefromCondition(condition):
#     name_list = getAllInnermostSubstrings(condition, '(', ')')
#     return name_list

def getNamefromCondition(condition):
    return PARENTHESES_PATTERN.findall(condition)


def getSpecificColumn(df, column_name, filter_column_name = None, filter_value_list = None):
    column_list_dict = {}
    for filter_value in filter_value_list:
        df_filtered = df.copy()
        if filter_column_name is not None:
            df_filtered = df_filtered[df_filtered[filter_column_name].isin([filter_value])]

        #column_list_dict[filter_value] = []
        column_list_dict[filter_value] = df[df[column_name] == filter_value][column_name].tolist()
        if filter_column_name is not None:
            for index, row in df_filtered.iterrows():
                if row[column_name] not in column_list_dict[filter_value]:
                    column_list_dict[filter_value].append(row[column_name])
        
    return column_list_dict    

########################################################################################


def findRootNodes(node_data):
    all_keys = node_data.keys()
    all_having_condition = set()
    all_in_box = set()
    for key, value in node_data.items():
        if value['condition_list']:
            all_having_condition.add(key)
        if value['box_name']:
            all_in_box.add(key)
            
    root_nodes = all_keys - all_having_condition - all_in_box
    return root_nodes

def createConditionPairs(node_data):
    condition_pair_list = []
    for name, value in node_data.items():
        if value['condition_list'] and value['box_name']:
            for condition in value['condition_list']:
                condition_pair_list.append({
                    "target": name, 
                    "source": condition,
                    "pair_type": "condition"
                    })
        elif value['condition_list'] and not value['box_name']:
            for condition in value['condition_list']:
                condition_pair_list.append({
                    "target": name, 
                    "source": condition,
                    "pair_type": "root_condition"
                    })
        elif value['box_name'] and not value['condition_list']:
            condition_pair_list.append({
                "target": name, 
                "source": value['box_name'],
                "pair_type": "start_in_box"
                })
                
    return condition_pair_list

def createConditionPairsDict(node_data):
    condition_pair_dict = {}
    for name, value in node_data.items():
        if value['condition_list'] and value['box_name']:
            for condition in value['condition_list']:
                if condition in condition_pair_dict:
                    condition_pair_dict[condition].append({
                        "target": name,
                        "pair_type": "condition"
                    })
                else:
                    condition_pair_dict[condition] = [{
                        "target": name,
                        "pair_type": "condition"
                    }]
        elif value['condition_list'] and not value['box_name']:
            for condition in value['condition_list']:
                if condition in condition_pair_dict:
                    condition_pair_dict[condition].append({
                        "target": name,
                        "pair_type": "root_condition"
                    })
                else:
                    condition_pair_dict[condition] = [{
                        "target": name,
                        "pair_type": "root_condition"
                    }]
        elif value['box_name'] and not value['condition_list']:
            if value['box_name'] in condition_pair_dict:
                condition_pair_dict[value['box_name']].append({
                    "target": name,
                    "pair_type": "start_in_box"
                })
            else:
                condition_pair_dict[value['box_name']] = [{
                    "target": name,
                    "pair_type": "start_in_box"
                }]
    return condition_pair_dict

def buildHierarchyTreeFromDict(root_node, condition_pair_dict, cache, visited_nodes = None):
    
    if visited_nodes is None:
        visited_nodes = set()
        
    if root_node in visited_nodes:
        return {}
    
    if root_node not in condition_pair_dict:
        cache[root_node] = {}
        return {}
    
    visited_nodes.add(root_node)
    children = condition_pair_dict[root_node]
    tree = {}
    
    #print("Current Node: ", root_node, "Children: ", len(children), "Cache: ", len(cache))
    for child in children:
        child_node = child['target']
        pair_type = child['pair_type']
        if pair_type == 'condition':
            tree[child_node] = buildHierarchyTreeFromDict(child_node, condition_pair_dict, cache, visited_nodes)
        elif pair_type == 'root_condition':
            tree[child_node] = buildHierarchyTreeFromDict(child_node, condition_pair_dict, cache, visited_nodes)
        elif pair_type == 'start_in_box':
            tree[child_node] = buildHierarchyTreeFromDict(child_node, condition_pair_dict, cache, visited_nodes)
        else:
            tree[child_node] = {}
            
    
    cache[root_node] = tree
    return tree

def buildHierarchyTreeFromList(root_node, condition_pair_list, cache, visited_nodes = None):
    
    if visited_nodes is None:
        visited_nodes = set()
        
    if root_node in visited_nodes:
        return {}
    
    children = [child for child in condition_pair_list if child['source'] == root_node]
    if not children:
        cache[root_node] = {}
        return {}
    
    visited_nodes.add(root_node)
    tree = {}
    
    #print("Current Node: ", root_node, "Children: ", len(children), "Cache: ", len(cache))
    for child in children:
        child_node = child['target']
        pair_type = child['pair_type']
        if pair_type == 'condition':
            tree[child_node] = buildHierarchyTreeFromList(child_node, condition_pair_list, cache, visited_nodes)
        elif pair_type == 'root_condition':
            tree[child_node] = buildHierarchyTreeFromList(child_node, condition_pair_list, cache, visited_nodes)
        elif pair_type == 'start_in_box':
            tree[child_node] = buildHierarchyTreeFromList(child_node, condition_pair_list, cache, visited_nodes)
        else:
            tree[child_node] = {}
            
    
    cache[root_node] = tree
    return tree
    
def searchBeforeJobTree(df_job):
    try:
        df_job_processed = df_job.copy()
        #df_dict = df_job_processed.set_index(JOBNAME_COLUMN).to_dict(orient='index')
        job_dependency_tree = defaultdict(dict)
        node_data = {}
        print("Processing . . .")
        print("Total Rows: ", len(df_job_processed))
        #print(df_job_processed.columns)
        for row in df_job_processed.itertuples(index=False):
            job_name = getattr(row, JOBNAME_COLUMN)
            condition = getattr(row, CONDITION_COLUMN)
            box_name = getattr(row, BOXNAME_COLUMN)
            
            if pd.notna(condition) and pd.notna(box_name):
                condition_name_list = getNamefromCondition(condition)
                node_data[job_name] = {
                    'condition_list': condition_name_list,
                    'box_name': box_name
                }
            elif pd.notna(condition) and not pd.notna(box_name):
                node_data[job_name] = {
                    'condition_list': getNamefromCondition(condition),
                    'box_name': None
                }
            elif not pd.notna(condition) and pd.notna(box_name):
                node_data[job_name] = {
                    'condition_list': [],
                    'box_name': box_name
                }
            else:
                node_data[job_name] = {
                    'condition_list': [],
                    'box_name': None
                }
        
        #t = createConditionPairs(node_data)
        #print(len(condition_pair_list))
        root_node_list = findRootNodes(node_data)
        root_node_list = sorted(list(root_node_list))
        print(len(root_node_list))
        # condition_pair_list = createConditionPairs(node_data)
        # print(len(condition_pair_list))
        condition_pair_dict = createConditionPairsDict(node_data)
        print(len(condition_pair_dict))

        node_data.clear()
        
        #children_dict = preprocessDependencies(condition_pair_list)
        for root_node in root_node_list:
            cache = {}
            print("Root Node: ", root_node)
            #job_dependency_tree[root_node] = buildHierarchyTreeFromList(root_node, condition_pair_list, cache)
            job_dependency_tree[root_node] = buildHierarchyTreeFromDict(root_node, condition_pair_dict, cache)
            print("completed")
        
        #return job_dependency_tree, condition_pair_list
        return job_dependency_tree, condition_pair_dict

    except Exception as e:
        print("Error: ", e)

      

########################################################################################

def main():
    
    df_job = getDataExcel('get Excel path with main job file')
    # root_list_option = input("Do you want to use the root or list? (r/l): ")
    # if root_list_option == 'r':
    #     df_root = getDataExcel("Enter the path of the excel file with the root jobs")
    # df_list_job = getDataExcel("Enter the path of the excel file with the list of jobs")
    # list_job_name = df_list_job[JOBNAME_COLUMN].tolist()
    # if root_list_option == 'r':
    #     list_dict = getSpecificColumn(df_root, SELECTED_COLUMN, FILTER_COLUMN, list_job_name)
    # else:
    #     list_dict = getSpecificColumn(df_job, SELECTED_COLUMN, None, list_job_name)
    # print("---------------------------------")
    # #for key, value in list_dict.items():
    # #    print(key, len(value))
    # print("---------------------------------")
    # print("Processing Previous job dependencies . . .")
    # #print(list_dict)
    # merged_list = [name for sublist in list_dict.values() for name in sublist]
    # df_job_merge = df_job[df_job[JOBNAME_COLUMN].isin(merged_list)]
    df_job_merge = df_job.copy()
    job_dependency_tree, condition_pair = searchBeforeJobTree(df_job_merge)
    createJson('condition_pair_all.json', condition_pair)
    createJson('stored_conditions_tree_all.json', job_dependency_tree)
        
    # job_dependency_tree, condition_pair = searchBeforeJobTree()
    # createJson('condition_pair.json', condition_pair)
    # createJson('stored_conditions_tree.json', job_dependency_tree)
    #job_dependency = searchBeforeJob(df_job)
    #createJson('stored_conditions.json', job_dependency)
    #createExcel(OUTPUT_EXCEL_FILE, ("Before", df_job_before))
    
    
    
    
if __name__ == '__main__':
    main()