import ee
import pandas as pd


def ee_array_to_df(arr, list_of_bands):
    '''Transforms client-side ee.Image.getRegion array to pandas.DataFrame.'''
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['longitude', 'latitude', 'time', *list_of_bands]].dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    # Convert the time field into a datetime, month and year.
    df['datetime'] = pd.to_datetime(df['time'], unit='ms')
    df['year'] = pd.DatetimeIndex(df['datetime']).year
    df['month'] = pd.DatetimeIndex(df['datetime']).month

    # Keep the columns of interest.
    df = df[['time', 'datetime', 'month', 'year',  *list_of_bands]] \
        .sort_values(by='datetime')

    return df


def get_region_as_df(ic: ee.ImageCollection, region: ee.Geometry, scale: int,
                     bands: list[str]):
    '''
    Gets Earth Engine data for a specific region and resolution, and
    transforms it to pandas.DataFrame.
    '''
    ee_region_data = ic.getRegion(region, scale=5000).getInfo()
    return ee_array_to_df(ee_region_data, bands)
