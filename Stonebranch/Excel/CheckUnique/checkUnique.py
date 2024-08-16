from readExcel import getDataExcel, selectSheet





def main():
    df = getDataExcel()
    print(df)
    unique_df = df['jobName'].unique()
    print('Unique Job Name')
    #print(unique_df)
    #duplicated_values_A = df[df['jobName'].duplicated()]['jobName']
    non_unique_values_B = df['jobName'].value_counts()[df['jobName'].value_counts() > 1]



    print(len(df),len(unique_df))
    #print("Duplicated values in column A:", duplicated_values_A.tolist())
    print("Non-unique values in column with counts:\n", non_unique_values_B)
    
    
    
    
if __name__ == '__main__':
    main()