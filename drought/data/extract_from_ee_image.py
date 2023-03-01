# %%
import ee
import pandas as pd
from drought.data.ee_converter import ee_points_converter
import geopandas as gpd
import geemap

ee.Initialize()


df = pd.read_feather('/maps/drought-with-gedi/Felipe/reduced_gedi.feather').set_index('index') # noqa

polygons = gpd.read_file('/home/fnb25/drought-with-gedi/data/polygons/Amazonia_drought_gradient_polygons.shp') # noqa

xmin, ymin, xmax, ymax = polygons.total_bounds

ee_geometry = ee.Geometry.BBox(xmin, ymin, xmax, ymax)

Map = geemap.Map()

# %%


def create_ee_points_series(df: pd.DataFrame) -> pd.Series:
    """
    Creates a series with ee_points using lat and long
    values from pandas.DataFrame.
    For running 16M rows the code takes ~9 minutes.
    """

    coords_series = pd.Series(list(zip(df['lon_lowestmode'],
                                       df['lat_lowestmode'])))
    ee_points = coords_series.apply(lambda row: ee_points_converter(row))
    return ee_points

# %%


landsat = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2").median()

# %%

ee_list_coords = ee.List(list(zip(df['lon_lowestmode'].iloc[0:100],
                                  df['lat_lowestmode'].iloc[0:100])))

ee_point = ee_list_coords.map(lambda row: ee.Feature(ee.Geometry.Point(row)))

fc = ee.FeatureCollection(ee_point)

collection = ee.ImageCollection('MODIS/061/MOD15A2H') \
                  .filterDate('2019-01-01', '2019-10-01') \
                  .mean()

n = 1

weights = [[1] * n] * n

window = ee.Kernel.fixed(n, n, weights)

scale = collection.projection().nominalScale()

reduced_array = collection.reduceNeighborhood(reducer=ee.Reducer.median(),
                                              kernel=window)

sample = reduced_array.sampleRegions(fc, scale=scale)

sample_pure = collection.sampleRegions(fc, scale=scale)

values = sample.aggregate_array('Fpar_500m_median')

values2 = sample_pure.aggregate_array('Fpar_500m')

tete = values.getInfo()


# %%


def extract_value_from_eeImage(df: pd.DataFrame,
                               ee_points: pd.Series,
                               image: ee.Image, bands: list[str] = None,
                               scale: int = None,
                               window_size: int = 1,
                               reducer: str = 'mean'):
    '''
    Extract points from an ee.Image
    '''
    reducer_dict = {
                'mean': ee.Reducer.mean(),
                'median': ee.Reducer.median(),
                'min': ee.Reducer.min(),
                'max': ee.Reducer.max(),
                'sum': ee.Reducer.sum()
                }

    if scale is None:
        scale = image.projection().nominalScale()

    if bands is None:
        bands = image.bandNames().getInfo()

    reducer_func = reducer_dict[reducer]
    weights = [[1] * window_size] * window_size
    kernel = ee.Kernel.fixed(window_size, window_size, weights)
    neigh_array = image.reduceNeighborhood(reducer=reducer_func,
                                           kernel=kernel)
    renamed_bands = [(name + '_' + reducer) for name in bands]
    sample_points = ee_points.apply(lambda point:
                                    neigh_array.sample(point, scale=scale))
    bands_df = pd.DataFrame()
    for band in renamed_bands:
        band_value = sample_points.apply(lambda point:
                                         point.aggregate_array(band).getInfo())
        bands_df[band] = band_value.values
    columns_name = list(df.columns) + bands
    result = pd.concat([df, bands_df], axis=1, ignore_index=True)
    result.columns = columns_name
    return result


# %%

"""
def extract_value_from_eeImage(gpd_df: gpd.GeoDataFrame, 
                               image: ee.Image, bands: list[str] = None,
                               scale: int = None,
                               window_size: int = 0, 
                               agregator: str = 'mean'):
    '''
    Extract points from an ee.Image
    '''
    if scale is None:
        scale = image.projection().nominalScale()

    if bands is None:
        bands = image.bandNames().getInfo()
    reducer = getattr(ee.Reducer, agregator)()

    ee_points_list = gdf_to_ee_points(gpd_df)
    data_array = np.zeros((gpd_df.shape[0], len(bands)))
    batch_size = 100
    batched_points = [ee_points_list[i:i+batch_size] for i in range(0, len(ee_points_list), batch_size)] # noqa

    for batch in batched_points:
        fc = ee.FeatureCollection(batch)
        neighborhood = image.reduceNeighborhood(reducer, ee.Kernel.square(radius=window_size / 2, units='pixels'))
        dict_results = neighborhood.reduceRegions(collection=fc, scale=scale).getInfo()['features']
        for i, f in enumerate(dict_results):
            values = []
            for band in bands:
                band_value = f['properties'][band]
                values.append(band_value)
            data_array[batch_size * len(batched_points) + i, :] = values

    gpd_df_copy = gpd_df.copy()
    for index, band in enumerate(bands):
        gpd_df_copy[band] = data_array[:, index]

    return gpd_df_copy
"""
