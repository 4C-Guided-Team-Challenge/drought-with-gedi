'''
This module contains methods for importing all the relevant climatic data
from Google Earth Engine.

Before calling any of the methods, make sure to authenticate with earth
engine. See: https://developers.google.com/earth-engine/guides/python_install#authentication # noqa
for more details.
'''
from drought.data.ee_converter import get_region_as_df
from drought.data.aggregator import make_monthly_composite
import ee
import pandas as pd

# All climate data columns.
CLIMATE_COLUMNS = ['precipitation', 'temperature', 'radiation', 'fpar']


def get_monthly_climate_data_as_pdf(start_date: ee.Date, end_date: ee.Date,
                                    geoms: list[ee.Geometry], scale: int) \
        -> pd.DataFrame:
    ''' Returns Pandas DataFrame that combines all climate data. '''
    # Get monthly climate data as ee.ImageCollection.
    climate_monthly = get_monthly_climate_data(start_date, end_date, geoms)

    # Convert the data to pandas DataFrame.
    all_polygons_pdfs = []
    for i in range(len(geoms)):
        pdf = get_region_as_df(
            climate_monthly, geoms[i], scale, CLIMATE_COLUMNS)
        pdf["polygon_id"] = i + 1
        all_polygons_pdfs.append(pdf)

    return pd.concat(all_polygons_pdfs)


def get_monthly_climate_data(start_date: ee.Date, end_date: ee.Date,
                             geometries: list[ee.Geometry]) \
        -> ee.ImageCollection:
    '''
    Returns ImageCollection that combines all climate data.

    Each climate variable is stored as a separate Band. Images are clipped
    to contain only regions of interest.
    '''

    p_monthly = get_monthly_precipitation_data(start_date, end_date)
    r_monthly = get_monthly_radiation_data(start_date, end_date)
    t_monthly = get_monthly_temperature_data(start_date, end_date)
    fpar_monthly = get_monthly_fpar_data(start_date, end_date)

    # Stack images together.
    climate_stack = _stack_monthly_composites(_stack_monthly_composites(
        _stack_monthly_composites(p_monthly, r_monthly), t_monthly
    ), fpar_monthly)

    # Clip image to include only regions of interest specified in geometries.
    clipped = climate_stack.map(lambda img: ee.ImageCollection(
        [img.clip(geometry) for geometry in geometries]).mosaic()
        .copyProperties(img, ['year', 'month', 'date', 'system:time_start']))
    return clipped


def get_monthly_precipitation_data(start_date: ee.Date, end_date: ee.Date):
    ''' Get cummulative monthly precipitation from CHIRPS dataset. '''

    precipitation_daily = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                            .select('precipitation') \
                            .filterDate(start_date, end_date)

    # Since CHIRPS gives us daily precipitation, we need to sum daily values
    # per month to obtain monthly precipitation.
    return make_monthly_composite(precipitation_daily, lambda x: x.sum(),
                                  start_date, end_date)


def get_monthly_radiation_data(start_date: ee.Date, end_date: ee.Date):
    '''
    Get aggregated montly downward radiation from ERA5 dataset.

    Using ERA monthly now for simplicity, since it's already aggregated.
    TODO: Consider using MCD18C2.061 if we need PAR instead of downward
    radiation and if we need 5km resolution, instead of 11km.
    '''
    radiation_monthly = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY") \
        .select(['surface_net_solar_radiation'], ['radiation']) \
        .filterDate(start_date, end_date)

    radiation_monthly = make_monthly_composite(radiation_monthly,
                                               lambda x: x.mean(),
                                               start_date, end_date)

    # Since ERA5 is missing December 2022, we will calculate that one
    # averaging previous Decembers.
    def interpolate_december_2022(img):
        prev_december_filter = ee.Filter.Or(
            ee.Filter.eq("date", "2021-12"),
            ee.Filter.eq("date", "2020-12"),
            ee.Filter.eq("date", "2019-12"))
        return ee.Algorithms.If(
            ee.String(img.get("date")).equals("2022-12"),
            ee.ImageCollection(
                radiation_monthly.filter(prev_december_filter)).mean(),
            img)

    return radiation_monthly.map(interpolate_december_2022)


def get_monthly_temperature_data(start_date: ee.Date, end_date: ee.Date):
    '''
    Get mean monthly temperature from MODIS.

    It's possible once we select image resolution, we won't have data
    for some months if they were cloudy.
    TODO: Decide what to do in these cases.
    '''

    def scaleAndMaskTemp(img):
        '''
        Filters images based on the quality flag QC_Day value (0 is valid),
        and scales data with 0.02 scale. Converts to Celsius.
        '''

        return (img.select(["LST_Day_1km"], ["temperature"])
                .multiply(0.02)
                .subtract(273.15)  # Convert to Celsius.
                .updateMask(img.select("QC_Day").eq(0))
                .copyProperties(img, ["system:time_start"]))

    temperature_daily = ee.ImageCollection('MODIS/061/MOD11A1') \
                          .map(scaleAndMaskTemp) \
                          .filterDate(start_date, end_date)

    return make_monthly_composite(temperature_daily, lambda x: x.mean(),
                                  start_date, end_date)


def get_monthly_fpar_data(start_date: ee.Date, end_date: ee.Date):
    ''' Get average monthly fraction of the absorved photossynthic
    active radiation from MODIS dataset in percentege (0-100%). '''

    fpar_8days = ee.ImageCollection('MODIS/061/MOD15A2H') \
                   .select(['Fpar_500m'], ['fpar']) \
                   .filterDate(start_date, end_date)

    # Since the dataset gives us the best pixel from a 8 days composite,
    # we need to average values per month to obtain monthly fpar.
    return make_monthly_composite(fpar_8days, lambda x: x.mean(),
                                  start_date, end_date)


def _stack_monthly_composites(ic1: ee.ImageCollection,
                              ic2: ee.ImageCollection):
    '''
    Stacks image collections together, doing the inner join on 'date'
    property.
    '''

    filter_month = ee.Filter.equals(leftField='date', rightField='date')
    stack = ee.Join.inner().apply(ic1, ic2, filter_month).map(
        lambda img: ee.Image.cat(img.get('primary'), img.get('secondary')))

    return ee.ImageCollection(stack)
