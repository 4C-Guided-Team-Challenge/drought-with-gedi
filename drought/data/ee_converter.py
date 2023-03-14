'''
Methods for converting Earth Engine data structures to other formats (Pandas,
GeoPandas, shapely, etc.) and back.
'''
import ee
import numpy as np
import pandas as pd
import shapely


def gdf_to_ee_polygon(gdf_polygon: shapely.Polygon):
    ''' Helper to convert GeoPandas geometry to Earth Engine geometry. '''
    x, y = gdf_polygon.exterior.coords.xy
    coords = np.dstack((x, y)).tolist()
    return ee.Geometry.Polygon(coords)


def get_polygons_as_df(ic: ee.ImageCollection, start_date: ee.Date,
                       end_date: ee.Date, geoms: list[ee.Geometry], scale: int,
                       bands: list[str]) \
        -> pd.DataFrame:
    '''
    Gets Earth Engine data for all polygons, given a resolution, and
    transforms it to pandas.DataFrame.
    '''

    # Convert the data to pandas DataFrame.
    all_polygons_pdfs = []
    for i in range(len(geoms)):
        pdf = get_region_as_df(ic, geoms[i], scale, bands)
        pdf["polygon_id"] = i + 1
        all_polygons_pdfs.append(pdf)

    return pd.concat(all_polygons_pdfs)


def get_region_as_df(ic: ee.ImageCollection, region: ee.Geometry, scale: int,
                     bands: list[str]):
    '''
    Gets Earth Engine data for a specific region and resolution, and
    transforms it to pandas.DataFrame.
    '''
    ee_region_data = ic.select(bands).getRegion(region, scale=scale).getInfo()
    return ee_array_to_df(ee_region_data, bands)


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
    df = df[['time', 'datetime', 'month', 'year', 'longitude', 'latitude',
             *list_of_bands]].sort_values(by='datetime')

    return df
