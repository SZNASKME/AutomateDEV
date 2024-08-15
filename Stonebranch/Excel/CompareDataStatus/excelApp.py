from readExcel import getDataExcel
from processExcel import compareDataStatus, createExcel



def main():
    df_all = getDataExcel()
    df_sep = getDataExcel()
    df_status = compareDataStatus(df_all, df_sep)
    createExcel(df_status, 'output.xlsx')
    
    
if __name__ == '__main__':
    main()