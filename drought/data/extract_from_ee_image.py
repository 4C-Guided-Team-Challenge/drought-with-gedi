#%%
import ee
import numpy as np
import pandas as pd
from drought.data.ee_converter import ee_points_converter
ee.Initialize()


df = pd.read_feather('/home/fnb25/reduced_gedi.feather').set_index('index')


#%%

def create_ee_points_series(df: pd.DataFrame):
    """
    Creates a series with ee_points using lat and long 
    values from pandas.DataFrame.
    For running 16M rows the code takes ~9 minutes.
    """

    coords_series = pd.Series(list(zip(df['lon_lowestmode'],
                                       df['lat_lowestmode'])))
    ee_points = coords_series.apply(lambda row: ee_points_converter(row))
    return ee_points

#%%

ee_list_coords = ee.List(list(zip(df['lon_lowestmode'].iloc[0:10],
                                  df['lat_lowestmode'].iloc[0:10])))

ee_point = ee_list_coords.map(lambda row: ee.Feature(ee.Geometry.Point(row)))

fc = ee.FeatureCollection(ee_point)


collection = ee.ImageCollection('MODIS/061/MOD15A2H') \
                  .filterDate('2019-01-01', '2019-10-01') \
                  .mean()

sample_pure = collection.sampleRegions(fc)

n = 3

weights = [[1] * n] * n

window = kernel = ee.Kernel.fixed(n, n, weights)

reduced_neighborhood_array = collection.reduceNeighborhood(reducer = ee.Reducer.sum(), kernel = window)

neighborhood_array = collection.neighborhoodToArray(window)

teste = reduced_neighborhood_array.sampleRegions(fc)

sample_pure = collection.sampleRegions(fc)

values = teste.aggregate_array('Fpar_500m_sum')

values2 = sample_pure.aggregate_array('Fpar_500m')

def extract_value(list):
    value = ee.Number(list)
    return value

#%%
point = ee_point_list.get(0)

neighborhood_dict = neighborhood_array.sample(point, scale=collection.projection().nominalScale()).first().getInfo()

#%%

teste = np.array(neighborhood_dict['properties']['FparStdDev_500m']).flatten()

bands_modis = collection.bandNames().getInfo()

#%%


def extract_value_from_eeImage(df: pd.DataFrame,
                               ee_points: pd.Series,
                               image: ee.Image, bands: list[str] = None,
                               scale: int = None,
                               window_size: int = 0,
                               reducer: str = 'mean'):
    '''
    Extract points from an ee.Image
    '''
    reducer_dict = {
                'mean': ee.Reducer.mean(),
                'median': ee.Reducer.median(),
                'min': ee.Reducer.min(),
                'max': ee.Reducer.max()
                }

    if scale is None:
        scale = image.projection().nominalScale()

    if bands is None:
        bands = image.bandNames().getInfo()

    reducer = reducer_dic[reducer]

    data_array = np.zeros((df.shape[0], len(bands)))
    window = ee.Kernel.square(radius=window_size / 2, units='pixels')
    neighborhood_array = collection.neighborhoodToArray(window)

    for index, point in enumerate(ee_points):
        values = []
        dict_results = neighborhood_array.sample(point, scale=scale).first().getInfo()
        for band in bands:
            array = np.array(dict_results['properties'][band]).flatten()
            band_value = aggregate_func(array)
            values.append(band_value)
        data_array[index, :] = values

    gpd_df_copy = gpd_df.copy()
    for index, band in enumerate(bands):
        print(index, band)
        gpd_df_copy[band] = data_array[:, index]

    return gpd_df_copy



#%%
import multiprocessing as mp

def extract_value_from_eeImage(gpd_df: gpd.GeoDataFrame, 
                               image: ee.Image, bands: list[str] = None,
                               scale: int = None,
                               window_size: int = 0, 
                               agregator: str = 'mean',
                               chunk_size: int = None,
                               num_processes: int = None):
    '''
    Extract points from an ee.Image
    '''
    if scale is None:
        scale = image.projection().nominalScale()

    if bands is None:
        bands = image.bandNames().getInfo()
    aggregate_func = getattr(np, agregator)
    ee_points_list = gdf_to_ee_points(gpd_df)
    
    if chunk_size is None:
        chunk_size = len(ee_points_list)
        
    if num_processes is None:
        num_processes = mp.cpu_count()
        
    pool = mp.Pool(processes=num_processes)
    
    results = []
    for i in range(0, len(ee_points_list), chunk_size):
        print(i)
        chunk = ee_points_list[i:i+chunk_size]
        results.append(pool.apply_async(process_chunk, (chunk, image, bands, scale, window_size, aggregate_func)))
    
    pool.close()
    pool.join()
    
    data_array = np.vstack([result.get() for result in results])
    
    for index, band in enumerate(bands):
        gpd_df[band] = data_array[:, index]
        print(index)

    return gpd_df

def process_chunk(ee_points_list, image, bands, scale, window_size, aggregate_func):
    data_array = np.zeros((len(ee_points_list), len(bands)))
    window = ee.Kernel.square(radius=window_size / 2, units='pixels')
    neighborhood_array = collection.neighborhoodToArray(window)

    for index, point in enumerate(ee_points_list):
        values = []
        dict_results = neighborhood_array.sample(point, scale=scale).first().getInfo()
        for band in bands:
            array = np.array(dict_results['properties'][band]).flatten()
            band_value = aggregate_func(array)
            values.append(band_value)
        data_array[index, :] = values
        
    return data_array








#%%
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
    aggregate_func = getattr(np, agregator)
    gpd_df['ee_point'] = gpd_df['geometry'].apply(lambda row: ee.Geometry.Point([row.x, row.y]))
    print('passou')
    data_array = np.zeros((gpd_df.shape[0], len(bands)))
    window = ee.Kernel.square(radius=window_size / 2, units='pixels')
    neighborhood_array = collection.neighborhoodToArray(window)

    for index, point in enumerate(ee_points_list):
        values = []
        dict_results = neighborhood_array.sample(point, scale=scale).first().getInfo()
        for band in bands:
            array = np.array(dict_results['properties'][band]).flatten()
            band_value = aggregate_func(array)
            values.append(band_value)
        data_array[index, :] = values

    gpd_df_copy = gpd_df.copy()
    for index, band in enumerate(bands):
        print(index, band)
        gpd_df_copy[band] = data_array[:, index]

    return gpd_df_copy

#%%
teste_2 = extract_value_from_eeImage(gpd_df=df, image=collection, bands=['Fpar_500m','Lai_500m'], window_size=3, agregator='median')

# %%

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
    batched_points = [ee_points_list[i:i+batch_size] for i in range(0, len(ee_points_list), batch_size)]

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
