import requests
import urllib.parse
import json
from requests.auth import HTTPBasicAuth
import http
from collections import OrderedDict

TASK_URI = "http://172.16.1.85:8080/uc/resources/task"


TASK_NAME = "IFRS_MONTHLY_B"

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
        #print(json.dumps(task_data, indent=5))
        if task_data['type'] == "taskWorkflow":
            for child in task_data['workflowVertices']:
                child_name = child['task']['value']
                next_node_list = findNextNode(child_name, task_data['workflowEdges'])
                children["Children"][child_name] = findChildren(child_name, next_node_list)
        #else:
        if len(next_node) > 0:
            children["Next Node"] = next_node
        else:
            children["Next Node"] = "End of workflow"
    
    print(f"{response.status_code} - {status.phrase}: {status.description}")

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

def populate_tree(tree, parent, dictionary):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            node = tree.insert(parent, 'end', text=key)
            populate_tree(tree, node, value)
        else:
            tree.insert(parent, 'end', text=key, values=(value,))

def create_tree_view(data):
    root = tk.Tk()
    root.title("Multi-level Dictionary Tree View")
    
    tree = ttk.Treeview(root)
    
    # Define columns
    tree['columns'] = ('Value')
    tree.column('#0', width=150, minwidth=150, stretch=tk.NO)
    tree.column('Value', width=100, minwidth=100, stretch=tk.NO)
    
    # Define headings
    tree.heading('#0', text='Key', anchor=tk.W)
    tree.heading('Value', text='Value', anchor=tk.W)
    
    # Populate tree
    populate_tree(tree, '', data)
    
    tree.pack(expand=True, fill=tk.BOTH)
    
    root.mainloop()

############################################      graph         ############################################


import networkx as nx
import matplotlib.pyplot as plt


def add_nodes_edges(graph, workflow_dict, parent=None):
    if isinstance(workflow_dict, dict):
        for key, value in workflow_dict.items():
            if key == 'Children':
                for child_key, child_value in value.items():
                    graph.add_node(child_key)
                    if parent:
                        graph.add_edge(parent, child_key)
                    add_nodes_edges(graph, child_value, child_key)
            elif key == 'Next Node':
                if isinstance(value, list):
                    for next_node in value:
                        graph.add_edge(parent, next_node)
                        if next_node not in graph:
                            graph.add_node(next_node)
                else:
                    graph.add_edge(parent, value)
                    if value not in graph:
                        graph.add_node(value)

# Function to create and visualize the workflow graph
def visualize_workflow(workflow_dict):
    graph = nx.DiGraph()  # Create a directed graph
    add_nodes_edges(graph, workflow_dict)

    pos = nx.spring_layout(graph)  # Layout for nodes
    plt.figure(figsize=(15, 10))  # Size of the plot
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrowsize=20)
    plt.show()


############################################################################################################


def main():
    children = findChildren(TASK_NAME)
    print(json.dumps(children, indent=10))
    
    visualize_workflow(children)

if __name__ == "__main__":
    main()