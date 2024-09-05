import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.readExcel import getDataExcel

OUTPUT_FILE = 'JIL.txt'

def create_JIL(df):
    with open(OUTPUT_FILE, 'w') as f:
        for index, row in df.iterrows():
            jil_job = "\n\n"
            jil_job += f"/* ----------------- {row['jobName']} ----------------- */ \n\n"
            jil_job += f"insert_job: {row['jobName']}   job_type: {row['jobType']}\n"
            for col in df.columns:
                if col not in ['jobName', 'jobType'] and not pd.isnull(row[col]):
                    if isinstance(row[col], (int, float)):
                        jil_job += f"{col}: {int(row[col])}\n"
                    elif col == 'description':
                        jil_job += f"{col}: \"{row[col]}\"\n"
                    else:
                        jil_job += f"{col}: {row[col]}\n"
            #if index < len(df) - 1:
            #    jil_job += "\n"
            f.write(jil_job)
    return None
    
def main():
    
    df_selected = getDataExcel()
    
    create_JIL(df_selected)
    
    
    
if __name__ == "__main__":
    main()