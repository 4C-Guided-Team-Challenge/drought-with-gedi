#%%
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


def return_index_col(coords: tuple) -> np.ndarray:
    """
    Return the row and column from a raster based on a lat and long
    of a point stored in a tuple.
    """
    row_index, column_index = raster_data.index(coords[0], coords[1])
    row_col_array = np.array([row_index, column_index])
    return row_col_array


def retrieve_window_array(idx: np.ndarray,
                          raster: np.ndarray,
                          window_size: int) -> np.ndarray:
    """
    Retrieves a window from a raster centered on the row and column idx.
    """
    window = raster[idx[0] - (window_size//2): idx[0] + (window_size//2 + 1),
                    idx[1] - (window_size//2): idx[1] + (window_size//2 + 1)]
    return window.flatten()


def land_use_check(window: np.ndarray) -> bool:
    """
    Check the values from the extracted window to assure that the GEDI shot and
    all the neighbors are Forest, Savanna or are in Polygon 1. The
    values are based on the land and use map provided by MAPBIOMAS(2021)
    Polygon 1 is outside Brazil. Therefore, all windows will have the value 0
    """
    poly1_check = np.all(window == 0)
    forest_check = np.all(window == 3)
    savanna_check = np.all(window == 4)
    land_flag = poly1_check or forest_check or savanna_check
    return land_flag








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
    Since Polygon 1 is outside Brazil, all shots landing inside it
    receives the quality flag = 1, but the land use was not checked
    '''
    raster_data, raster_array = read_raster(LAND_USE_DIR)
    gdf_gedi = transform_csv_to_gpd(dir_csv)
    land_quality_flag = []
    for index, row in gdf_gedi.iterrows():
        if row['polygon_id'] == 1:
            land_quality_flag.append(1)
        else:
            latitude = row['geometry'].y
            longitude = row['geometry'].x
            row_index, col_index = raster_data.index(longitude, latitude)
            MASK = np.array([[1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1]]).astype(bool)
            window = raster_array[row_index - 1: row_index + 2,
                                  col_index - 1: col_index + 2][MASK]
            # MAPBIOMAS set the class 3 for forest and class 4 for savanna
            # Therefore, to be considered valid, the pixel where GEDI landed
            # and all neighbors must be assigned to the same class (3 or 4)
            if np.array_equal(window,  # check if all pixels are forest (3) # noqa: E501
                              np.array([3, 3, 3, 3, 3, 3, 3, 3, 3])) \
                or np.array_equal(window,  # check if all pixels are savanna class (4) # noqa: E501
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
#%%

df = pd.read_feather('/home/fnb25/gedi.feather').set_index('index')
raster_data, raster_array = read_raster(LAND_USE_DIR)

coords = pd.Series(list(zip(df['lon_lowestmode'],
                            df['lat_lowestmode'])))

def return_index_col(coord):
    row_index, column_index = raster_data.index(coord[0],coord[1])
    ziped = np.array([row_index,column_index])
    return ziped

indexes = coords.apply(lambda row: return_index_col(row))

def retrieve_array(idx, raster, window):    
    window = raster[idx[0] - (window//2) : idx[0] + (window//2 + 1),
                    idx[1] - (window//2) : idx[1] + (window//2 + 1)]
    return window.flatten()

values = indexes.apply(lambda row: retrieve_array(row, raster_array, 3))


def land_use_check(row):
     poly1_check = np.all(row == 0)
     forest_check = np.all(row == 3)
     savanna_check = np.all(row == 4)
     result = poly1_check or forest_check or savanna_check
     return result

land_quality = values.apply(lambda row: land_use_check(row))

filtered_df = df[land_quality.values]

#%%
