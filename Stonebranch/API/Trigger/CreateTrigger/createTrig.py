import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import *
from utils.readFile import loadJson
from utils.createFile import createJson, createExcel
from utils.readExcel import getDataExcel


trigger_configs_temp = {
    "type" : "triggerTm",
    "action" : "Do Not Trigger",
    "calendar" : "Default conversion calendar",
    "customField1" : {
        "label" : None,
        "value" : None
    },
    "customField2" : {
        "label" : None,
        "value" : None
    },
    "description" : None,
    "disabledTime" : "",
    "enabled" : False,
    "enabledEnd" : "00:00",
    "enabledStart" : "00:00",
    "enabledTime" : "",
    "enforceVariables" : False,
    "exportReleaseLevel" : "7.6.0.2",
    "exportTable" : "ops_trigger_tm",
    "lockVariables" : False,
    "name" : None,
    "nextScheduledTime" : "",
    "notes" : [ ],
    "opswiseGroups" : [ ], ##
    "rdExcludeBackup" : False,
    "restrictedTimes" : False,
    "restriction" : False,
    "restrictionAdjective" : "Every",
    "restrictionComplex" : False,
    "restrictionMode" : "Or",
    "restrictionNoun" : {
        "value" : "Day"
    },
    "restrictionNouns" : [ {
        "value" : "Day"
    } ],
    "restrictionNthAmount" : 5,
    "restrictionQualifier" : {
        "value" : "Year"
    },
    "restrictionQualifiers" : [ {
        "value" : "Year"
    } ],
    "restrictionSimple" : False,
    "retainSysIds" : True,
    "retentionDuration" : 1,
    "retentionDurationPurge" : False,
    "retentionDurationUnit" : "Days",
    "situation" : "Holiday",
    "skipActive" : True,
    "skipAfterDate" : None,
    "skipAfterTime" : None,
    "skipBeforeDate" : None,
    "skipBeforeTime" : None,
    "skipCondition" : "Active",
    "skipCount" : 0,
    "skipDateList" : [ ],
    "skipRestriction" : "None",
    "taskMonitor" : None, ##
    "tasks" : [ ], ##
    "timeZone" : None,
    "variables" : [ ],
    "version" : 1
}



TASKNAME_COLUMN = "task"
TASKMONITOR_COLUMN = "taskmonitor"
TRIGGER_COLUMN = "taskmonitortrigger"

OUTPUT_EXCEL_NAME = "CreateTriggerLog.xlsx"
OUTPUT_EXCEL_SHEET = "TriggerLog"

BUSINESS_SERVICES = [
    'A0076 - Data Warehouse ETL'
]

def createTaskMonitorTrigger(trigger_name, task_list, task_monitor):
    trigger_configs = trigger_configs_temp.copy()
    trigger_configs['name'] = trigger_name
    trigger_configs['taskMonitor'] = task_monitor
    trigger_configs['tasks'] = task_list
    trigger_configs['opswiseGroups'] = BUSINESS_SERVICES
    #print(json.dumps(trigger_configs, indent=4))
    response = createTriggerAPI(trigger_configs)
    if response.status_code == 200:
        log = {
            "triggername": trigger_name,
            "taskmonitor": task_monitor,
            "tasklist": task_list,
            "message": "Trigger created successfully"
        }
        return log
    elif response.status_code == 400:
        log = {
            "triggername": trigger_name,
            "taskmonitor": task_monitor,
            "tasklist": task_list,
            "message": "Trigger already exists"
        }
        return log
    else:
        log = {
            "triggername": trigger_name,
            "taskmonitor": task_monitor,
            "tasklist": task_list,
            "message": f"Error creating trigger: {response.status_code}"
        }
        return log
    
    
    
def runCreateTriggers(df):
    logs = []

    for index, row in df.iterrows():
        trigger_name = row[TRIGGER_COLUMN]
        task_list = [row[TASKNAME_COLUMN]]
        task_monitor = row[TASKMONITOR_COLUMN]
        log = createTaskMonitorTrigger(trigger_name, task_list, task_monitor)
        logs.append(log)
    
    df_logs = pd.DataFrame(logs)
    return df_logs



def main():
    auth = loadJson('Auth.json')
    #userpass = auth['TTB']
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['1.86']
    updateURI(domain)
    
    df = getDataExcel()
    
    logs = runCreateTriggers(df)
    createExcel(OUTPUT_EXCEL_NAME, (OUTPUT_EXCEL_SHEET, logs))
    
    
    
if __name__ == '__main__':
    main()