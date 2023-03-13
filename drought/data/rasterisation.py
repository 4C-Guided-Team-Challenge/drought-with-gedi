import numpy as np
from shapely import Polygon
import pandas as pd
import geopandas as gpd
from drought.data.ee_converter import gdf_to_ee_polygon


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


def raster_climate(df: pd.DataFrame, dataset: str, feature: str,
                   start: str, end: str):
    '''
    Given a DataFrame consisting of a geometry column, returns requested
    climatic variable (as defined by dataset and feature) for each geometry
    over the timeframe specified by start and end.  
    '''
    climate = []

    collection = ee.ImageCollection(dataset)

    dSUTC = ee.Date(start, 'GMT')
    dEUTC = ee.Date(end, 'GMT')
    filtered = collection.filterDate(dSUTC, dEUTC.advance(1, 'day')) \
        .select(feature)

    image = filtered.mean()

    for polygon in df['geometry']:
        ee_polygon = gdf_to_ee_polygon(polygon)
        series = image.reduceRegions(collection=ee_polygon,
                                     reducer=ee.Reducer.mean(),
                                     scale=500)

        value = series.getInfo()['features'][0]['properties']['mean']

        climate.append(value)

    df[feature] = climate

    return df


def raster_climate_all_polygons(r: int, df: pd.DataFrame,
                                shape: gpd.GeoDataFrame, gedi_var: str,
                                climate_dataset: str, climate_var: str,
                                climate_start: str, climate_end: str):
    '''
    Standalone function which will generate a rasterised DataFrame containing
    requested gedi_var and climate_var for each cell.

    Note that climate_var will be the mean of the variable over the timeframe
    from climate_start to climate_end. 
    '''
    master_climate = pd.DataFrame()

    for pol in range(1, 9):
        grid = rasterise_polygon(r, df, shape, pol) \
            .groupby(['x', 'y']).mean()[gedi_var].reset_index()
        geo_grid = calculate_grid_geometry(grid, r, shape, pol, [gedi_var])

        climate_grid = raster_climate(geo_grid, climate_dataset, climate_var,
                                      climate_start, climate_end)
        climate_grid['polygon_id'] = pol

        master_climate = pd.concat([master_climate, climate_grid])

    return master_climate
