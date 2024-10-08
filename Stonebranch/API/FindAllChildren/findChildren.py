import requests
import urllib.parse
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateAuth, updateURI, getTaskAPI
from utils.readFile import loadJson

from collections import OrderedDict

TASK_NAME = "DWH_ONICE_ONHOLD_B"

CHILDREN_FIELD = "Children"
CHILD_TYPE = "Child Type"
CHILD_LEVEL = "Child Level"
NEXT_NODE = "Next Node"


task_configs_temp = {
    'taskname': None,
}

#########################################     find children    ################################################

def findChildren(task_name, next_node = [], level = 0):
    children = {CHILD_TYPE: None, CHILD_LEVEL: level, CHILDREN_FIELD: OrderedDict(), NEXT_NODE: None}
    task_configs = task_configs_temp.copy()
    task_configs['taskname'] = task_name
    response = getTaskAPI(task_configs)
    if response.status_code == 200:
        task_data = json.loads(response.text)
        children[CHILD_TYPE] = task_data['type']
        if task_data['type'] == "taskWorkflow":
            for child in task_data['workflowVertices']:
                child_name = child['task']['value']
                child_next_node = findNextNode(child_name, task_data['workflowEdges'])
                children["Children"][child_name] = findChildren(child_name, child_next_node, level + 1)
        if len(next_node) > 0:
            children[NEXT_NODE] = next_node
        else:
            children[NEXT_NODE] = []
        
    #print(f"{response.status_code} - {status.phrase}: {status.description}")

    return children

def findNextNode(task_name, workflowEdges):
    next_node = []
    for edge in workflowEdges:
        if edge['sourceId']['taskName'] == task_name:
            next_node.append(f"{edge['targetId']['taskName']} | {edge['condition']['value']}")
    return next_node

def countChildren(children_dict):
    count = 0
    for child_name, child_data in children_dict["Children"].items():
        count += 1  # Count this child
        count += countChildren(child_data)  # Recursively count the child's children
    return count

############################################       tree         ############################################

import tkinter as tk
from tkinter import ttk

def insert_items(parent, children, tree):
    for key, value in children.items():
        item_id = tree.insert(parent, 'end', text=key)
        insert_items(item_id, value[CHILDREN_FIELD], tree)
        for next_node in value.get(NEXT_NODE, []):
            tree.insert(item_id, 'end', text=next_node)

def createTreeView(data):
    root = tk.Tk()
    root.title("GUI Tree Workflow")

    # Create the Treeview widget
    tree = ttk.Treeview(root)
    tree.heading("#0", text="Workflow", anchor='w')

    # Insert the root item
    root_item = tree.insert('', 'end', text='ROOT')
    insert_items(root_item, data[CHILDREN_FIELD], tree)

    # Pack the Treeview widget
    tree.pack(fill='both', expand=True)

    # Run the application
    root.mainloop()

############################################      graph         ############################################


import networkx as nx
import matplotlib.pyplot as plt


def add_nodes_and_edges(graph, parent, data):
    for node, info in data[CHILDREN_FIELD].items():
        graph.add_node(node)
        graph.add_edge(parent, node)
        add_nodes_and_edges(graph, node, info)
        for next_node in info.get(NEXT_NODE, []):
            graph.add_node(next_node)
            graph.add_edge(node, next_node)

# Function to create and visualize the workflow graph
def visualizeWorkflow(workflow_dict):
    G = nx.DiGraph()
    root = "ROOT"
    G.add_node(root)

    # Build the graph
    add_nodes_and_edges(G, root, workflow_dict)

    # Draw the graph
    plt.figure(figsize=(20, 15))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
    plt.title("Visual Graph GUI Workflow")
    plt.show()


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
    
    print("Finding all children of a task in the workflow")
    children = findChildren(TASK_NAME)
    print("Showing the children of the task in a tree view")
    print(json.dumps(children, indent=10))
    total_children = countChildren(children)
    print(f"Total children: {total_children}")
    #visualizeWorkflow(children)
    #createTreeView(children)
    save_choice = input("Do you want to save the children to a file? (y/n): ")
    if save_choice.lower() == "y":
        with open(f"./DWF/{TASK_NAME}_children.json", "w") as file:
            json.dump(children, file, indent=4)
        print(f"Children saved to '{TASK_NAME}_children.json'")

if __name__ == "__main__":
    main()