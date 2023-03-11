import xarray as xr
import numpy as np
import rasterio
import pandas as pd
import os
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import mapping


PATH_FILE = '/maps-priv/maps/drought-with-gedi/spei_data/spei'

SAVE_DIRECTORY = '/maps-priv/maps/drought-with-gedi/spei_data/'


def create_spei_geotiff(spei_window: int,
                        open_dir: str = PATH_FILE,
                        save_dir: str = SAVE_DIRECTORY,
                        start_date: str = '01-01-2000',
                        end_date: str = '01-01-2021'):
    """
    Opens the SPEI nc file and create a series of aggregated metrics
    for a time period. Save the results into a geotiff file, where
    each band is an agraggegated.
    """
    if open_dir == PATH_FILE:
        SPEI_PATH = open_dir + str(spei_window) + '.nc'
    ds_spei = xr.open_dataset(SPEI_PATH)
    spei = ds_spei.sel(time=slice(start_date, end_date))
    spei_array = spei['spei'].values

    extreme_drought = np.count_nonzero((-2 >= spei_array), axis=0)

    severe_drought = np.count_nonzero((-1.5 >= spei_array) &
                                      (spei_array > -2), axis=0)

    moderate_drought = np.count_nonzero((-1 >= spei_array) &
                                        (spei_array > -1.5), axis=0)

    near_normal = np.count_nonzero((1 > spei_array) &
                                   (spei_array > -1), axis=0)

    moderate_wet = np.count_nonzero((1.5 > spei_array) &
                                    (spei_array >= 1), axis=0)

    severe_wet = np.count_nonzero((2 > spei_array) &
                                  (spei_array >= 1.5), axis=0)

    extreme_wet = np.count_nonzero((2 <= spei_array), axis=0)

    height, width = 360, 720
    xmin, ymin, xmax, ymax = -180, -90, 180, 90
    transform = rasterio.transform.from_bounds(xmin, ymin,
                                               xmax, ymax,
                                               width, height)
    dtype = np.float64
    crs = 'EPSG:4326'
    count = 7

    GEOTIFF_NAME = save_dir + 'spei_reduced' + str(spei_window) + '.tif'

    with rasterio.open(GEOTIFF_NAME, 'w', driver='GTiff',
                       width=width, height=height, count=count,
                       dtype=dtype, crs=crs, transform=transform) as dst:

        dst.write(np.flipud(extreme_drought), 1)
        dst.write(np.flipud(severe_drought), 2)
        dst.write(np.flipud(moderate_drought), 3)
        dst.write(np.flipud(near_normal), 4)
        dst.write(np.flipud(moderate_wet), 5)
        dst.write(np.flipud(severe_wet), 6)
        dst.write(np.flipud(extreme_wet), 7)


def extract_spei_pixels(spei_month: str) -> pd.DataFrame:

    spei_string = PATH_FILE + '_reduced' + spei_month + '.tif'

    if os.path.exists(spei_string) is False:
        create_spei_geotiff(spei_month)

    polygons = gpd.read_file('/home/fnb25/drought-with-gedi/data/polygons/Amazonia_drought_gradient_polygons.shp') # noqa

    full_df = pd.DataFrame(columns=['extreme_drought', 'severe_drought',
                                    'moderate_drought', 'near_normal',
                                    'moderate_wet', 'severe_wet',
                                    'extreme_wet', 'polygon'])

    for polygon in range(polygons.geometry.shape[0]):
        geojson = [mapping(polygons.geometry[polygon])]
        with rasterio.open(spei_string, 'r') as dst:
            clipped, affine = mask(dataset=dst,
                                   shapes=geojson,
                                   all_touched=True,
                                   crop=True)
            values = clipped.reshape(7, (clipped.shape[1] *
                                         clipped.shape[2])).transpose()
            polygon_array = np.full((values.shape[0], 1),
                                    polygon + 1)
            complete_array = np.hstack((values, polygon_array))
            polygon_df = pd.DataFrame(data=complete_array,
                                      columns=full_df.columns)
            full_df = pd.concat([full_df, polygon_df], ignore_index=True)

    return full_df
