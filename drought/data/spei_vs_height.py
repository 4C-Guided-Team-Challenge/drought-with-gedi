import numpy as np
import rasterio
from rasterio.enums import Resampling
import geemap
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import ee

ee.Initialize()

# %%

# ########## Resampling potapov height map ############## #

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

spei = ee.Image('users/fnincao/spei_reduced3') \
                .select('b1').updateMask(resampledImage)

roi = table.first().geometry()

vis = {'min': 0, 'max': 30,
       'palette': ['#edf8e9', '#c7e9c0', '#a1d99b',
                   '#74c476', '#41ab5d', '#238b45', '#005a32']}

vis_spei = {'min': 0, 'max': 30, 'palette': ['#fee5d9', '#fcae91',
                                             '#fb6a4a', '#cb181d']}


# %%

Map = geemap.Map()

Map.addLayer(spei, vis_spei, 'spei')

Map.addLayer(masked_potapov, vis, 'potapov')

Map

# %%


pixelValues_height = masked_potapov.reduceRegion(
  reducer=ee.Reducer.toList(),
  geometry=roi).get('b1').getInfo()

pixelValues_spei = spei.reduceRegion(
  reducer=ee.Reducer.toList(),
  geometry=roi).get('b1').getInfo()

# %%

model = LinearRegression().fit(np.array(pixelValues_height).reshape(-1, 1),
                               np.array(pixelValues_spei))

print("Slope: %f   Intercept: %f" % (model.coef_[0], model.intercept_))

plt.scatter(pixelValues_spei, pixelValues_height)
# %%
