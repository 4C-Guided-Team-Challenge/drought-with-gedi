# %%
import xarray as xr
import numpy as np
import rasterio
import pandas as pd
import os
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import mapping
import ee
from drought.data.ee_converter import gdf_to_ee_polygon

ee.Initialize()


# %%

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

# %%

polygons = gpd.read_file('/home/fnb25/drought-with-gedi/data/polygons/Amazonia_drought_gradient_polygons.shp') # noqa

ee_polygons = gdf_to_ee_polygon(polygons.geometry[1])


def mabiomas_mask(image):
    mapbiomas = ee.Image('projects/mapbiomas-workspace/public/collection7/mapbiomas_collection70_integration_v2') # noqa
    mapbiomas_2021 = mapbiomas.select('classification_2021')
    forest_mask = mapbiomas_2021.eq(3)
    return image.updateMask(forest_mask)


potapov = ee.ImageCollection('users/potapovpeter/GEDI_V27')

output_proj = ee.Projection('EPSG:4326').scale(0.5, 0.5)

outputScale = 5000

reprojectedImage = potapov.reproject({
  'crs': output_proj,
  'scale': outputScale
})

outputImage = reprojectedImage.reduceResolution({
  'reducer': ee.Reducer.median()
})

mapbiomas = ee.Image('projects/mapbiomas-workspace/public/collection7/mapbiomas_collection70_integration_v2') # noqa

vis = {'min':0, 'max':100, 'palette':['#fff7ec','#fee8c8','#fdd49e','#fdbb84','#fc8d59','#ef6548','#d7301f','#b30000','#7f0000']} # noqa


# %%
from rasterio.enums import Resampling # noqa

downscale_factor = 1/2000

with rasterio.open('/maps/drought-with-gedi/Felipe/Forest_height_2019_SAM.tif', 'r') as dst: # noqa
    transform = dst.transform

    data = dst.read(
        out_shape=(dst.count,
                   int(dst.height * downscale_factor),
                   int(dst.width * downscale_factor)),
        resampling=Resampling.average)

    new_transform = dst.transform * dst.transform.scale(
                int(dst.width / data.shape[-1]),
                int(dst.height / data.shape[-2]))

with rasterio.open('/home/fnb25/Testes/resampled.tif', 'w', driver='GTiff',
                   width=108, height=138, count=1,
                   dtype=np.float64, crs='EPSG:4326',
                   transform=new_transform) as dataset:

    dataset.write(data.reshape(138, 108), 1)


# %%
potapov = ee.Image('projects/ee-fnincao/assets/resampled_potapov')

table = ee.FeatureCollection('projects/ee-fnincao/assets/brazilian_legal_amazon') # noqa

mapbiomas = ee.Image('projects/mapbiomas-workspace/public/collection7/mapbiomas_collection70_integration_v2') # noqa

mapbiomas_2021 = mapbiomas.select('classification_2021')

forest_mask = mapbiomas_2021.eq(3)

resampledImage = forest_mask.resample('bilinear').reproject(
   crs=potapov.projection().getInfo()['crs'],
   scale=potapov.projection().nominalScale().getInfo())

masked_potapov = potapov.updateMask(resampledImage)

spei = ee.Image('users/fnincao/spei_reduced3').select('b1').updateMask(resampledImage)

roi = table.first().geometry()

vis = {'min': 0, 'max': 30,
       'palette': ['#edf8e9', '#c7e9c0', '#a1d99b',
                   '#74c476', '#41ab5d', '#238b45', '#005a32']}

vis_spei = {'min': 0, 'max': 30, 'palette': ['#fee5d9', '#fcae91',
                                             '#fb6a4a', '#cb181d']}


# %%

import geemap # noqa

Map = geemap.Map()

Map.addLayer(spei, vis_spei, 'potapov')

Map

# %%


pixelValues_height = masked_potapov.reduceRegion(
  reducer=ee.Reducer.toList(),
  geometry=roi).get('b1').getInfo()

pixelValues_spei = spei.reduceRegion(
  reducer=ee.Reducer.toList(),
  geometry=roi).get('b1').getInfo()

# %%

from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

model = LinearRegression().fit(np.array(pixelValues_height).reshape(-1, 1),
                               np.array(pixelValues_spei))

print("Slope: %f   Intercept: %f" % (model.coef_[0], model.intercept_))

plt.scatter(pixelValues_spei, pixelValues_height)
# %%
