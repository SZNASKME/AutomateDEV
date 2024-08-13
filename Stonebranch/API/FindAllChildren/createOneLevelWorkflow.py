import json

def flatten_workflow(node, flat_list, json_data, parent=None):
    # Add the current node to the flat list
    current_node = {
        "Node": node,
        "Next Node": []
    }
    if parent:
        flat_list[parent]["Next Node"].append(node)
    
    flat_list[node] = current_node

    # Recurse into children
    if "Children" in json_data[node]:
        for child in json_data[node]["Children"]:
            flatten_workflow(child, flat_list, json_data, node)

    # Add "Next Node" connections
    if "Next Node" in json_data[node]:
        current_node["Next Node"].extend([n.split(" | ")[0] for n in json_data[node]["Next Node"]])

# Load your JSON file
with open('./WF/DWH_DAILY_B_children.json') as f:
    json_data = json.load(f)
flat_list = {}
for root_node in json_data["Children"]:
    flatten_workflow(root_node, flat_list, json_data)

# Convert flat_list to a list for easier processing/visualization
flat_workflow = list(flat_list.values())

# Optionally, save to a new JSON file
with open('./OLWF/DWH_DAILY_B.json', 'w') as f:
    json.dump(flat_workflow, f, indent=4)
