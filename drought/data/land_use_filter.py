'''Module that filters GEDI shots based on MAPBIOMAS land use raster file'''

import geopandas as gpd
import rasterio as rio
from shapely import wkt
import pandas as pd
import numpy as np
import os


LAND_USE_DIR = '../../data/land_use/brasil_coverage_2020.tif'

GEDI_DATA_DIR = '../../data/gedi/gedi_queried_shots_original.csv'

SAVE_NEW_FILE_DIR = ('/maps/drought-with-gedi/gedi_data/gedi_land_use_filtered.csv')  # noqa: E501


def read_raster(directory: str):
    '''
    Open raster as array file and evaluate if is in right projection
    compared with GEDI data (ESPG:4326).
    '''
    raster = rio.open(directory)
    crs = str(raster.crs)
    if crs == 'EPSG:4326':
        raster_array = raster.read(1)
        return raster, raster_array
    else:
        raise Warning("Your raster file is not in crs 'EPSG:4326'")


def transform_csv_to_gpd(directory: str):
    '''
    Transform csv file into geopandas dataframe
    '''
    pd_df = pd.read_csv(directory)
    pd_df['geometry'] = pd_df['geometry'].apply(wkt.loads)
    gpd_df = gpd.GeoDataFrame(pd_df, geometry='geometry')
    return gpd_df


def filter_land_cover(dir_csv: str, save_csv: bool, overwrite_file: bool):
    '''
    Input GEDI csv file to filter land cover based on a 3x3 window, with the
    recorded GEDI geolocation in the middle,and create a quality flag
    column based on the MAPBIOMAS land cover map (2020).
    If quality flag = 1, all pixels are Forest or Savanna
    If quality flag = 0, at least one pixel is NOT Forest or Savanna.
    Save the csv file in /maps/drought-with-gedi/gedi_data/ if save_csv = True
    Or return the filtered dataset if save_csv = False
    If there is an existing file with the same name, and you want overwrite,
    use overwrite_file = True
    '''
    raster_data, raster_array = read_raster(LAND_USE_DIR)
    gdf_gedi = transform_csv_to_gpd(dir_csv)
    land_quality_flag = []
    for index, row in gdf_gedi.iterrows():
        latitude = row['geometry'].y
        longitude = row['geometry'].x
        row_index, col_index = raster_data.index(longitude, latitude)
        MASK = np.array([[1, 1, 1],
                         [1, 1, 1],
                         [1, 1, 1]]).astype(bool)
        window = raster_array[row_index - 1: row_index + 2,
                              col_index - 1: col_index + 2][MASK]
        # MAPBIOMAS set the class 3 for forest and class 4 for savanna
        # Therefore, to be considered valid, the pixel where GEDI shot landed
        # and all neighbors must be assigned to the same class (3 or 4)
        if np.array_equal(window,
                          np.array([3, 3, 3, 3, 3, 3, 3, 3, 3]))\
            or np.array_equal(window,
                              np.array([4, 4, 4, 4, 4, 4, 4, 4, 4])):
            land_quality_flag.append(1)
        else:
            land_quality_flag.append(0)

    gdf_gedi['land_quality_flag'] = land_quality_flag
    filtered_gdf_gedi = gdf_gedi[gdf_gedi['land_quality_flag'] == 1]

    if save_csv:
        if os.path.isfile(SAVE_NEW_FILE_DIR):
            print("File with that name already exists in the directory")
            if overwrite_file:
                filtered_gdf_gedi.to_csv(SAVE_NEW_FILE_DIR)
                print("New csv file saved")
            else:
                print("File not saved")

        filtered_gdf_gedi.to_csv(SAVE_NEW_FILE_DIR)
    else:
        return filtered_gdf_gedi
