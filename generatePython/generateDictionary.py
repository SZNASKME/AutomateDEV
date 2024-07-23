import os
import importlib.util
import ast
import json


TARGET_FILE_PATH = ".\Target\mappingField.py"
SOURCE_FILE_PATH = ".\source\mappingField.py"

# Load dictionary from file

def load_dict_from_file(file_path, dict_name):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return getattr(module, dict_name)


def get_dict_names_from_file(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    dict_names = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Dict):
                    dict_names.append(target.id)

    return dict_names


# Process dictionary

def find_intersection(dict_data):
    intersection = {}
    dicts = dict_data.copy()
    all_keys = set().union(*dicts.values())
    
    
    for key in all_keys:
        values = [dict_value[key] for dict_value in dict_data.values() if key in dict_value]
        if len(values) == len(dict_data):
            intersection[key] = values[0]
            
    print("I\n",intersection)
    return intersection


def find_union(dict_data):
    union = {}
    dicts = dict_data.copy()
    all_keys = set().union(*dicts.values())
    
    for key in all_keys:
        for dict_name, dict_value in dict_data.items():
            if key in dict_value:
                union[key] = dict_value[key]
                break
            
    print("U\n",union)
    return union


# Generate dictionary

def generate_intersection_dictionary(target_file_path, dict_data, dict_name = "dictionary"):
    
    code_format = f"""
    {dict_name} = "{{"
    """

    


    code_format += f"""}}"""


    with open(target_file_path, 'w') as file:
        file.write(code_format)
    

def main():
    dict_names = get_dict_names_from_file(SOURCE_FILE_PATH)
    print(dict_names)
    
    dict_data = {}
    for dict_name in dict_names:
        dict_data[dict_name]= load_dict_from_file(SOURCE_FILE_PATH, dict_name)
    
    print(json.dumps(dict_data, indent=4))
    #generate_mapping_field(MAPPING_FIELD_FILE_PATH, TARGET_FILE_PATH)
    
    intersection = find_intersection(dict_data)
    union = find_union(dict_data)

    #print("\n\n\n",json.dumps(intersection, indent=4))
    #print("\n\n\n",json.dumps(union, indent=4))
    
    print(len(intersection))
    print(len(union))



if __name__ == '__main__':
    main()
    