import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel




def main():
    df = getDataExcel()
    print(df)
    unique_df = df['jobName'].unique()
    print('Unique Job Name')
    #print(unique_df)
    #duplicated_values_A = df[df['jobName'].duplicated()]['jobName']
    non_unique_values_B = df['jobName'].value_counts()[df['jobName'].value_counts() > 1]

    df_non_unique = df[df['jobName'].isin(non_unique_values_B.index)]

    print(len(df),len(unique_df))
    #print("Duplicated values in column A:", duplicated_values_A.tolist())
    print("Non-unique values in column with counts:\n", df_non_unique)
    
    createExcel("NonUniqueJob.xlsx", (df_non_unique, 'NonUniqueJob'))
    
    
if __name__ == '__main__':
    main()