import pandas as pd


def add_date_column(df: pd.DataFrame):
    '''
    Adds 'date' column to the DataFrame df.

    DataFrame must have columns 'year' and 'month' already.
    '''
    if 'datetime' in df.columns:
        df['date'] = df.datetime.dt.strftime('%m-%y')
    else:
        df = df.sort_values(by=['year', 'month'])

        df['date'] = pd.to_datetime(df['year'].astype(str) +
                                    df['month'] .astype(str),
                                    format='%Y%m').dt.strftime('%m-%y')
    return df


def add_datetime_column(df: pd.DataFrame):
    '''
    Adds 'datetime' column to the DataFrame df.

    DataFrame must have columns 'year' and 'month' already.
    '''
    df_copy = df.copy()
    df_copy['day'] = 1
    df['datetime'] = pd.to_datetime(df_copy[['month', 'day', 'year']])
    return df
