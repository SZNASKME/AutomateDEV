import requests
import urllib.parse
import json
from requests.auth import HTTPBasicAuth
import http
from collections import OrderedDict

TASK_URI = "http://172.16.1.86:8080/uc/resources/task"


TASK_NAME = "MRM_MTHLY_B"

auth = HTTPBasicAuth('ops.admin','p@ssw0rd')


task_configs_temp = {
    'taskname': None,
}

############################################################################################################

def createURI(uri, configs):
    uri += "?"
    for key, value in configs.items():
        uri += f"{key}={value}"
        if key != list(configs.keys())[-1]:
            uri += "&"
    uri = urllib.parse.quote(uri, safe=':/&?=*')
    return uri



def getTaskAPI(task_configs):
    uri = createURI(TASK_URI, task_configs)
    response = requests.get(url = uri, auth = auth, headers={'Accept': 'application/json'})
    return response


############################################################################################################

def findChildren(task_name, next_node = []):
    children = {"Children": OrderedDict(), "Next Node": None}
    task_configs = task_configs_temp.copy()
    task_configs['taskname'] = task_name
    response = getTaskAPI(task_configs)
    status = http.HTTPStatus(response.status_code)
    if response.status_code == 200:
        task_data = json.loads(response.text)
        if task_data['type'] == "taskWorkflow":
            for child in task_data['workflowVertices']:
                child_name = child['task']['value']
                child_next_node = findNextNode(child_name, task_data['workflowEdges'])
                children["Children"][child_name] = findChildren(child_name, child_next_node)
        if len(next_node) > 0:
            children["Next Node"] = next_node
        else:
            children["Next Node"] = []
    
    #print(f"{response.status_code} - {status.phrase}: {status.description}")

    return children

def findNextNode(task_name, workflowEdges):
    next_node = []
    for edge in workflowEdges:
        if edge['sourceId']['taskName'] == task_name:
            next_node.append(edge['targetId']['taskName'])
    return next_node


############################################       tree         ############################################

import tkinter as tk
from tkinter import ttk

def insert_items(parent, children, tree):
    for key, value in children.items():
        item_id = tree.insert(parent, 'end', text=key)
        insert_items(item_id, value['Children'])
        for next_node in value.get('Next Node', []):
            tree.insert(item_id, 'end', text=next_node)

def createTreeView(data):
    root = tk.Tk()
    root.title("GUI Tree Workflow")

    # Create the Treeview widget
    tree = ttk.Treeview(root)
    tree.heading("#0", text="Workflow", anchor='w')

    # Insert the root item
    root_item = tree.insert('', 'end', text='ROOT')
    insert_items(root_item, data['Children'], tree)

    # Pack the Treeview widget
    tree.pack(fill='both', expand=True)

    # Run the application
    root.mainloop()

############################################      graph         ############################################


import networkx as nx
import matplotlib.pyplot as plt


def add_nodes_and_edges(graph, parent, data):
    for node, info in data['Children'].items():
        graph.add_node(node)
        graph.add_edge(parent, node)
        add_nodes_and_edges(graph, node, info)
        for next_node in info.get("Next Node", []):
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
    print("Finding all children of a task in the workflow")
    children = findChildren(TASK_NAME)
    print("Showing the children of the task in a tree view")
    print(json.dumps(children, indent=10))
    
    #visualizeWorkflow(children)
    createTreeView(children)

if __name__ == "__main__":
    main()