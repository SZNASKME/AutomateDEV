import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel


def checkComponentColumn(df):
    # Create a set from the job names for faster lookup
    box_name_list = df['box_name'].unique().tolist()
    
    # Use a list comprehension to find box names not in the job name set
    job_not_exist = [box_name for box_name in box_name_list if box_name not in df['jobName'].tolist()]
    
    return job_not_exist
        
    
def main():
    
    df = getDataExcel()
    job_not_exist = checkComponentColumn(df)
    df_not_exist = pd.DataFrame(job_not_exist, columns=['box_name'])
    createExcel('job_not_exist.xlsx', (df_not_exist, 'job_not_exist'))
    
if __name__ == "__main__":
    main()
    