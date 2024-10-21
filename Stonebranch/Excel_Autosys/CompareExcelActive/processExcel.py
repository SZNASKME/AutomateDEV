import pandas as pd


COMAPRE_COLUMN = 'jobName'
CHECKING_COLUMN = 'Status'
#(Active/Inactive/Terminated/On Hold/On Ice/On Request)'


def checkExistRow(df, column, value):
    return df.loc[df[column] == value]

def compareDataStatus(dfm, dfc):
    
    # check value in main dataframe
    main_not_in_df = dfm[~dfm[COMAPRE_COLUMN].isin(dfc[COMAPRE_COLUMN])]
    compare_not_in_df = dfc[~dfc[COMAPRE_COLUMN].isin(dfm[COMAPRE_COLUMN])]
    main_same_df = dfm[dfm[COMAPRE_COLUMN].isin(dfc[COMAPRE_COLUMN])]
    compare_same_df = dfc[dfc[COMAPRE_COLUMN].isin(dfm[COMAPRE_COLUMN])]
    df_merge = pd.merge(dfm, dfc, on=COMAPRE_COLUMN, suffixes=('_main', '_compare'))
    #print(df_merge)
    df_intrsct = df_merge[df_merge[f'{CHECKING_COLUMN}_main'].startwith('Active')]
    
    
    return {
        'main_inverse': main_not_in_df,
        'compare_inverse': compare_not_in_df,
        'main_same': main_same_df,
        'compare_same': compare_same_df,
        'map': df_merge,
        'intersection_active': df_intrsct,
    }
            