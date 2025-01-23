import sys
import os
import json
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.createFile import createJson
from utils.readExcel import getDataExcel
from utils.readFile import loadJson


VERTEX_PATH = "Stonebranch\\JSON\\genarateDepend\\SRC_Vertex.json"
WORKFLOW_VERTEX = "workflowVertices"

JSON_FILENAME = "depen.json"
SOURCE_COLUMN = "Source"
TARGET_COLUMN = "Target"

depen_configs_temp = {
    "condition": {
        "value": None
    },
    "sourceId": {
        "taskName": None,
        "value": None
    },
    "targetId": {
        "taskName": None,
        "value": None
    },
    "straightEdge": True,
}

def restructureVetex(vertex_json):
    vertex_info = {}
    #print(json.dumps(vertex_json, indent=4))
    vertex_list = vertex_json[WORKFLOW_VERTEX]
    
    for vertex in vertex_list:
        vertex_info[vertex['task']['value']] = vertex['vertexId']
    #print(json.dumps(vertex_info, indent=4))
    return vertex_info

def findVertexId(vertex_info, vertex_name):
    return vertex_info[vertex_name]


def genDepenList(df_depen_configs, vertex_info, depen_configs_temp):
    depen_list = []
    for index, row in df_depen_configs.iterrows():
        depen_configs = copy.deepcopy(depen_configs_temp)
        depen_configs['condition']['value'] = 'Success'
        depen_configs['sourceId']['taskName'] = row[SOURCE_COLUMN]
        depen_configs['sourceId']['value'] = findVertexId(vertex_info, row[SOURCE_COLUMN])
        depen_configs['targetId']['taskName'] = row[TARGET_COLUMN]
        depen_configs['targetId']['value'] = findVertexId(vertex_info, row[TARGET_COLUMN])
        depen_list.append(depen_configs)
    
    return depen_list




def main():
    
    df_custom = getDataExcel()
    vertex_json = loadJson(VERTEX_PATH)
    vertex_info = restructureVetex(vertex_json)
    depen_list = genDepenList(df_custom, vertex_info ,depen_configs_temp)
    
    createJson(JSON_FILENAME, depen_list)



if __name__ == "__main__":
    main()