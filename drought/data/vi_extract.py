import ee
import pandas as pd
from drought.data.aggregator import make_monthly_composite
from drought.data.ee_converter import get_region_as_df


ee.Initialize()

VI_COLUMNS = ['ndvi', 'evi']


def get_monthly_vi_data_as_pdf(start_date: ee.Date, end_date: ee.Date,
                               geoms: list[ee.Geometry], scale: int) \
        -> pd.DataFrame:
    ''' Returns Pandas DataFrame that combines all Vegetation indexes data. '''
    # Get monthly vi data as ee.ImageCollection.
    vi_monthly = get_monthly_vi_data(start_date, end_date)

    # Convert the data to pandas DataFrame.
    all_polygons_pdfs = []
    for i in range(len(geoms)):
        pdf = get_region_as_df(
            vi_monthly, geoms[i], scale, VI_COLUMNS)
        pdf["polygon_id"] = i + 1
        all_polygons_pdfs.append(pdf)

    return pd.concat(all_polygons_pdfs)


def get_monthly_vi_data(start_date: ee.Date, end_date: ee.Date):
    ''' Calculate Vegetatio indexes (NDVI and EVI) based on
    the BRDF Nadir-ajusted daily reflectance
    product (MODIS MCD43A4.061). Data is masked based on land use
    by NASA (MCD12Q1.061) for the year of 2021
    '''

    def calculate_ndvi(img: ee.Image) -> ee.Image:
        ndvi = img.normalizedDifference(['Nadir_Reflectance_Band2',
                                         'Nadir_Reflectance_Band1'])

        return img.addBands(ndvi.rename('ndvi'))

    def calculate_evi(img: ee.Image) -> ee.Image:
        evi = img.expression(
                             '2.5 * ((nir - red) / \
                             (nir + 6 * red - 7.5 * blue + 1))',
                             {'red': img.select('Nadir_Reflectance_Band1'),
                              'nir': img.select('Nadir_Reflectance_Band2'),
                              'blue': img.select('Nadir_Reflectance_Band3')})
        return img.addBands(evi.rename('evi'))

    def mask_bands(img: ee.Image) -> ee.Image:
        ''' Filters the reflectance product (MODIS MCD43A4.061) based on
        the land-use classification produced by NASA.
        For more information refer to https://developers.google.com/earth-
        engine/datasets/catalog/MODIS_061_MCD12Q1#bands
        '''
        land_use = ee.ImageCollection('MODIS/061/MCD12Q1') \
                     .filterDate('2021-01-01', '2021-02-01') \
                     .first() \
                     .select('LC_Type1')

        land_mask = land_use.eq(2)  # Pixels classified as forest

        return img.updateMask(land_mask)

    veg_idx = ee.ImageCollection('MODIS/061/MCD43A4') \
                .select('Nadir_Reflectance_Band1',
                        'Nadir_Reflectance_Band2',
                        'Nadir_Reflectance_Band3') \
                .filterDate(start_date, end_date) \
                .map(calculate_ndvi) \
                .map(calculate_evi)

    # Since the dataset gives us the best pixel from a 16 days composite,
    # we need to average values per month to obtain monthly VI's.
    return make_monthly_composite(veg_idx.select(['ndvi', 'evi']),
                                  lambda x: x.median(),
                                  start_date, end_date)
