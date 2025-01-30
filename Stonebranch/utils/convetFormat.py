import json





def convertDictToList(nested_dict, key_field = 'name'):
    converted_list_of_dict = []
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            value[key_field] = key
            converted_list_of_dict.append(value)
        elif isinstance(value, list):
            for item in value:
                item[key_field] = key
                converted_list_of_dict.append(item)
                
    return converted_list_of_dict
                
                
def convertListToDict(list_of_dict, key_field = 'name'):
    converted_nested_dict = {}
    for item in list_of_dict:
        key = item[key_field]
        item.pop(key_field)
        converted_nested_dict[key] = item
        
    return converted_nested_dict