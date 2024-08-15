import pandas as pd


COMAPRE_COLUMN = 'jobName'
CHECKING_COLUMN = 'Status'
#(Active/Inactive/Terminated/On Hold/On Ice/On Request)'


def checkExistRow(df, column, value):
    return df.loc[df[column] == value]

def compareDataStatus(dfm, dfc):
    
    # check value in main dataframe
    #main_not_in_df = dfm[~dfm[COMAPRE_COLUMN].isin(dfc[COMAPRE_COLUMN])]
    #compare_not_in_df = dfc[~dfc[COMAPRE_COLUMN].isin(dfm[COMAPRE_COLUMN])]
    main_same_df = dfm[dfm[COMAPRE_COLUMN].isin(dfc[COMAPRE_COLUMN])]
    compare_same_df = dfc[dfc[COMAPRE_COLUMN].isin(dfm[COMAPRE_COLUMN])]
    #df_merge = pd.merge(dfm, dfc, on=COMAPRE_COLUMN, suffixes=('_main', '_compare'))
    #print(df_merge)
    #df_intrsct = df_merge[df_merge[f'{CHECKING_COLUMN}_main'].startwith('Active')]
    
    
    return {'main': main_same_df,
            'compare': compare_same_df
            }
            



def createExcel(data, outputfile):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            data['main'].to_excel(writer, sheet_name='main', index=False)
            data['compare'].to_excel(writer, sheet_name='compare', index=False)
        print("Difference file created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")