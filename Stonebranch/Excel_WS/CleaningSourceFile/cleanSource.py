import sys
import os
import json
from unittest import result
import pandas as pd
import math
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readFile import loadJson
from utils.createFile import createJson, createExcel
from utils.readExcel import getDataExcel

TRIGGER_TYPE_LIST = ["Daily", "Weekly", "Monthly", "One Time"]

TRIGGER_TYPE_PREFIXES = "TriggerType_"
TRIGGER_TIME_PREFIXES = "StartBoundary_"
DESCRIPTION_PREFIXES = "Detail_"


def cleanTriggerType(df):
    
    for index, row in df.iterrows():
        trigger_type_list = []
        for col in df.columns:
            if col.startswith(TRIGGER_TYPE_PREFIXES):
                if pd.notna(row[col]) and row[col] in TRIGGER_TYPE_LIST:
                    trigger_type_list.append(row[col])
        trigger_type_set = set(trigger_type_list)
        
        if len(trigger_type_set) == 1:
            df.at[index, 'TriggerType'] = trigger_type_set.pop()
        elif len(trigger_type_set) > 1:
            if "Daily" in trigger_type_set and len(trigger_type_set) == trigger_type_list.count("Daily"):
                df.at[index, 'TriggerType'] = "Daily"
            elif "Weekly" in trigger_type_set and len(trigger_type_set) == trigger_type_list.count("Weekly"):
                df.at[index, 'TriggerType'] = "Weekly"
            elif "Monthly" in trigger_type_set and len(trigger_type_set) == trigger_type_list.count("Monthly"):
                df.at[index, 'TriggerType'] = "Monthly"
            elif "One Time" in trigger_type_set and len(trigger_type_set) == trigger_type_list.count("One Time"):
                df.at[index, 'TriggerType'] = "One Time"
            else:
                trigger_type_counts = {t: trigger_type_list.count(t) for t in trigger_type_set}
                trigger_type_str = ' || '.join([f"{k}: {v}" for k, v in trigger_type_counts.items()])
                df.at[index, 'TriggerType'] = trigger_type_str
        else:
            df.at[index, 'TriggerType'] = "None"

    return df

def cleanStartBoundary(df):
    
    def cleaningTimeFormat(time_str):
        # Format DD/MM/YYYY HH:MM:SS to HH:MM:SS
        time_pattern = r'(\d{2}):(\d{2}):(\d{2})'
        match = re.search(time_pattern, str(time_str))
        if match:
            return f"{match.group(1)}:{match.group(2)}:{match.group(3)}"
    
    
    for index, row in df.iterrows():
        time_list = []
        for col in df.columns:
            if col.startswith(TRIGGER_TIME_PREFIXES):
                if pd.notna(row[col]):
                    restrutctured_time = cleaningTimeFormat(row[col])
                    print(restrutctured_time)
                    if restrutctured_time:
                        time_list.append(restrutctured_time)
        df.at[index, 'StartBoundary'] = ' || '.join(time_list) if time_list else ""
    return df
        
    

def cleanDescription(df):
    for index, row in df.iterrows():
        description_list = []
        for col in df.columns:
            if col.startswith(DESCRIPTION_PREFIXES):
                if pd.notna(row[col]):
                    description_list.append(row[col])
        df.at[index, 'Description'] = ' || '.join(description_list) if description_list else ""
    return df

def cleanDataProcess(df):
    df_deduped = df.drop_duplicates()
    df_new = df_deduped.copy()
    df_new = cleanTriggerType(df_new)
    df_new = cleanStartBoundary(df_new)
    
    return df_new, df_deduped
    
    
    
    
        
    











def main():
    df = getDataExcel()
    
    df_cleaned = cleanDataProcess(df)
    
    createExcel('Cleaned_Source_File.xlsx', ('CleanedData', df_cleaned))
    
    
    
if __name__ == "__main__":
    main()
