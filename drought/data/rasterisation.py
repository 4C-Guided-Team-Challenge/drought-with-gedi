import numpy as np
from shapely import Polygon
import pandas as pd
import geopandas as gpd


def rasterise_polygon(r: int, df: pd.DataFrame, shape: gpd.GeoDataFrame,
                      polygon: int):
    '''
    Generates a r x r grid and then assigns every footprint
    x and y coordinates within that grid.

    df should contain GEDI footprints, shape the polygons of interest,
    and polygon the desired polygon_id.

    Returns df with x and y columns appended indicating grid coordinates.
    '''
    df = df[df["polygon_id"] == polygon]
    geometry = shape.geometry[polygon - 1]

    minx, miny, maxx, maxy = geometry.bounds
    stepx = (maxx - minx) / r
    stepy = (maxy - miny) / r

    df['x'] = ((df['lon_lowestmode'] - minx) / stepx).apply(np.floor)
    df['y'] = ((maxy - df['lat_lowestmode']) / stepy).apply(np.floor)

    return df


def calculate_grid_geometry(df: pd.DataFrame, r: int, shape: gpd.GeoDataFrame,
                            polygon: int, var: str):
    '''
        Given a Pandas.DataFrame with x and y columns, replace those with the
        appropriate geometry column.
    '''
    geometry = shape.geometry[polygon - 1]

    minx, miny, maxx, maxy = geometry.bounds
    stepx = (maxx - minx) / r
    stepy = (maxy - miny) / r

    def calc_geometry(row):
        curx = minx + row['x'] * stepx
        cury = maxy - row['y'] * stepy
        return Polygon([(curx, cury), (curx + stepx, cury),
                        (curx + stepx, cury - stepy), (curx, cury - stepy)])

    df['geometry'] = df.apply(calc_geometry, axis=1)
    df = df.drop(columns=['x', 'y'])

    geo_df = gpd.GeoDataFrame(df, columns=["geometry", *var])
    return geo_df


def plot_raster(df: pd.DataFrame, r: int, shape: gpd.GeoDataFrame,
                polygon: int, var: str):
    '''
    Generates plot of quantity var when passed df,
    the output of rasterise_polygon.
    '''
    df = df.groupby(['x', 'y']).mean()[var].reset_index()
    geo_df = calculate_grid_geometry(df, r, shape, polygon, [var])

    geo_df.plot(column=var, cmap='Greens')
