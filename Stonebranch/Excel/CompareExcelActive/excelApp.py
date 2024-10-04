import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel
from processExcel import compareDataStatus



def main():
    df_all = getDataExcel()
    df_sep = getDataExcel()
    df_status = compareDataStatus(df_all, df_sep)
    createExcel('output.xlsx'(df_status['main'], 'main'), (df_status['compare'], 'compare'))
    
    
if __name__ == '__main__':
    main()