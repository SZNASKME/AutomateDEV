import sys
import os
import json
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createFile import createJson
from utils.readExcel import getDataExcel

JSON_FILENAME = "vertex.json"
TASK = "Task"

vertex_configs_temp = {
    "alias": None,
    "task":{
        "value": None
    },
    "vertexId" : None
    #"vertexX": None,
    #"vertexY": None,
}



def genVertexList(df_vertex, initial_vertex_id, vertex_configs_temp):
    vertex_list = []
    current_vertex_id = int(initial_vertex_id)
    for index, row in df_vertex.iterrows():
        vertex_configs = copy.deepcopy(vertex_configs_temp)
        vertex_configs['alias'] = None
        vertex_configs['task']['value'] = row[TASK]
        vertex_configs['vertexId'] = str(current_vertex_id)
        vertex_list.append(vertex_configs)
        vertex_configs = {}
        
        current_vertex_id += 1
    
    return vertex_list




def main():
    
    df_vertex = getDataExcel()
    
    initial_vertex_id = input("Enter the initial vertex id: ")
    vertex_list = genVertexList(df_vertex, initial_vertex_id , vertex_configs_temp)
    print(json.dumps(vertex_list, indent=4))
    createJson(JSON_FILENAME, vertex_list)



if __name__ == "__main__":
    main()