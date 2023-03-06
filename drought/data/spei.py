# %%
import xarray as xr
import numpy as np
import rasterio
import pandas as pd
import os
import geopandas as gpd

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

# %%


def extract_spei_pixels() -> pd.DataFrame:

    spei_months = ['1', '3', '6', '9', '12']

    spei_strings = [(PATH_FILE + '_reduced' + i + '.tif') for i in spei_months]

    for string, spei_month in zip(spei_strings, spei_months):
        if os.path.exists(string) is False:
            create_spei_geotiff(spei_month)

    polygons = gpd.read_file('/home/fnb25/drought-with-gedi/data/polygons/Amazonia_drought_gradient_polygons.shp') # noqa


# %%
