'''Module that filters GEDI shots based on MAPBIOMAS land use raster file'''

import rasterio as rio
import pandas as pd
import numpy as np


LAND_USE_DIR = '../../data/land_use/brasil_coverage_2020.tif'


def land_use_filter(df: pd.DataFrame, window_size: int) -> pd.DataFrame:
    """
    Applies the filter based on the land use map provided by MAPBIOMAS(2021).
    The land quality flag is based o a NxN window, centered on the pixel where
    the GEDI shot landed. All values inside the window must be the same and
    equal 0 (polygon 1), 3 (forest) or 4 (savanna). More details about the
    MAPBIOMAS mapping can be found at https://mapbiomas.org/en
    """
    raster_obj, raster_array = read_raster(LAND_USE_DIR)
    coords = pd.Series(list(zip(df['lon_lowestmode'],
                                df['lat_lowestmode'])))
    indexes = coords.apply(lambda row: return_index_col(row, raster_obj))
    windows = indexes.apply(lambda row: retrieve_window_array(row,
                                                              raster_array,
                                                              window_size))
    land_quality = windows.apply(lambda row: land_use_check(row))
    filtered_df = df[land_quality.values]
    return filtered_df


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


def return_index_col(coords: tuple, raster_obj: rio.DatasetReader) \
        -> np.ndarray:
    """
    Return the row and column from a raster based on a lat and long
    of a point stored in a tuple.
    """
    row_index, column_index = raster_obj.index(coords[0], coords[1])
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
    values are based on the land use map provided by MAPBIOMAS(2021)
    Polygon 1 is outside Brazil. Therefore, all windows will have the value 0
    """
    poly1_check = np.all(window == 0)  # checks if all pixels are in poly1
    forest_check = np.all(window == 3)  # checks if all pixels are forest
    savanna_check = np.all(window == 4)  # checks if all pixels are savanna
    land_flag = poly1_check or forest_check or savanna_check
    return land_flag
