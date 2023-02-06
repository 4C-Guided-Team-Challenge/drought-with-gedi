'''Module that filters GEDI shots based on MAPBIOMAS land use raster file'''

import geopandas as gpd
import rasterio as rio
from shapely import wkt
import pandas as pd
import numpy as np
import os
import sys

LAND_USE_DIR = '../../data/land_use/brasil_coverage_2020.tif'

GEDI_DATA_DIR = '../../data/gedi/gedi_queried_shots_original.csv'

SAVE_NEW_FILE_DIR = ('/maps/drought-with-gedi/gedi_data/gedi_land_filtered.csv')# noqa: E501,E261,W292

if os.path.isfile(SAVE_NEW_FILE_DIR) is True:
    sys.exit("File with that name already in the directory")

'''Open raster as array file and evaluate if is in right projection
                compared with GEDI data (ESPG:4326)'''


def read_raster(directory: str):
    raster = rio.open(directory)
    crs = str(raster.crs)
    if crs == 'EPSG:4326':
        raster_array = raster.read(1)
        return raster, raster_array
    else:
        sys.exit("Your raster file is not in crs 'EPSG:4326'")


'''Transform csv file into geopands dataframe'''


def transform_csv_to_gpd(directory: str):
    pd_df = pd.read_csv(directory)
    pd_df['geometry'] = pd_df['geometry'].apply(wkt.loads)
    gpd_df = gpd.GeoDataFrame(pd_df, geometry='geometry')
    return gpd_df


'''   Filter land cover based on a 3x3 window, with the
  recorded GEDI geolocation in the middle,and create a quality flag
     column based on the MAPBIOMAS land cover map (2020).
     If quality flag = 1, all pixels are Forest or Savanna
     If quality flag = 0, at least one pixel is NOT Forest or Savanna.  '''


def filter_land_cover(directoty_csv: str):
    raster_data, raster_array = read_raster(LAND_USE_DIR)
    gdf_gedi = transform_csv_to_gpd(directoty_csv)
    land_quality_flag = []
    for index, row in gdf_gedi.iterrows():
        latitude = row['geometry'].y
        longitude = row['geometry'].x
        row_index, col_index = raster_data.index(longitude, latitude)
        mask = np.array([[1, 1, 1],
                         [1, 1, 1],
                         [1, 1, 1]]).astype(bool)
        window = raster_array[row_index - 1: row_index + 2,
                              col_index - 1: col_index + 2][mask]
        print(index)
        if np.array_equal(window,
                          np.array([3, 3, 3, 3, 3, 3, 3, 3, 3])) is True \
            or np.array_equal(window,
                              np.array([4, 4, 4, 4, 4, 4, 4, 4, 4])) is True:
            land_quality_flag.append(1)
        else:
            land_quality_flag.append(0)

    gdf_gedi['land_quality_flag'] = land_quality_flag
    filtered_gdf_gedi = gdf_gedi[gdf_gedi['land_quality_flag'] == 1]
    return filtered_gdf_gedi


gedi_data_gtc = filter_land_cover(GEDI_DATA_DIR)

gedi_data_gtc.to_csv(SAVE_NEW_FILE_DIR)
