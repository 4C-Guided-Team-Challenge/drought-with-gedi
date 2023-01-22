'''
    This module contains methods for importing all the relevant climatic data
    from Google Earth Engine.

    Before calling any of the methods, make sure to authenticate with earth
    engine. See: https://developers.google.com/earth-engine/guides/python_install#authentication # noqa
    for more details.
'''
import ee
from typing import Callable


def get_monthly_climate_data(start_date: ee.Date, end_date: ee.Date,
                             geometries: list[ee.Geometry]):
    '''
        Returns ImageCollection that combines all climate data.

        Each climate variable is stored as a separate Band. Images are clipped
        to contain only regions of interest.
    '''

    p_monthly = get_monthly_precipitation_data(start_date, end_date)
    r_monthly = get_monthly_radiation_data(start_date, end_date)
    t_monthly = get_monthly_temperature_data(start_date, end_date)

    # Stack images together.
    climate_stack = stack_monthly_composites(
        stack_monthly_composites(p_monthly, r_monthly), t_monthly
    )

    # Clip image to include only regions of interest specified in geometries.
    clipped = climate_stack.map(lambda img: ee.ImageCollection(
        [img.clip(geometry) for geometry in geometries]).mosaic())
    return clipped


def make_monthly_composite(ic: ee.ImageCollection, aggregator: Callable,
                           start_date: ee.Date, end_date: ee.Date):
    '''
      Aggregates images for each month using the aggregator function.

      Common aggregators can be mean, sum, max, etc.
    '''
    n_months = end_date.difference(start_date, 'month').subtract(1)
    months = ee.List.sequence(0, n_months) \
                    .map(lambda n: start_date.advance(n, 'month'))

    def aggregate(monthly_date):
        date = ee.Date(monthly_date)
        return (aggregator(ic.filterDate(date, date.advance(1, 'month')))
                # IMPORTANT: Add a date property to all images.
                # We depend on this elsewhere for stacking images.
                .set("date", date.format("YYYY-MM"))
                .set("month", date.format("MM"))
                .set("year", date.format("YYYY"))
                .set("system:time_start", date.millis()))

    return ee.ImageCollection(months.map(aggregate))


def stack_monthly_composites(ic1: ee.ImageCollection, ic2: ee.ImageCollection):
    '''
        Stacks image collections together, doing the inner join on 'date'
        property.
    '''

    filter_month = ee.Filter.equals(leftField='date', rightField='date')
    stack = ee.Join.inner().apply(ic1, ic2, filter_month).map(
        lambda img: ee.Image.cat(img.get('primary'), img.get('secondary')))

    return ee.ImageCollection(stack)


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
    radiation_monthly = \
        ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY") \
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
            and scales data with 0.02 scale.
        '''

        return (img.select(["LST_Day_1km"], ["temperature"])
                .multiply(0.02)
                .updateMask(img.select("QC_Day").eq(0))
                .copyProperties(img, ["system:time_start"]))

    temperature_daily = ee.ImageCollection('MODIS/061/MOD11A1') \
                          .map(scaleAndMaskTemp) \
                          .filterDate(start_date, end_date)

    return make_monthly_composite(temperature_daily, lambda x: x.mean(),
                                  start_date, end_date)
