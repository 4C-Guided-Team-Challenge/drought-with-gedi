''' Module where we place all aggregation functions. '''
import ee
import pandas as pd
from typing import Callable


def make_monthly_composite(ic: ee.ImageCollection, aggregator: Callable,
                           start_date: ee.Date, end_date: ee.Date):
    '''
    Aggregates images for each month using the aggregator function.

    Common aggregators can be mean, sum, max, etc.
    '''
    n_months = end_date.difference(start_date, 'month').round().subtract(1)
    months = ee.List.sequence(0, n_months) \
                    .map(lambda n: start_date.advance(n, 'month'))

    def aggregate(monthly_date):
        date = ee.Date(monthly_date)
        return (aggregator(ic.filterDate(date, date.advance(1, 'month')))
                # IMPORTANT: Add a date property to all images.
                # We depend on this elsewhere for stacking images.
                .set("date", date.format("YYYY-MM"))
                .set("month", date.get("month"))
                .set("year", date.get("year"))
                .set("system:time_start", date.millis()))

    return ee.ImageCollection(months.map(aggregate))


def from_daily_to_cummulative_monthly(ic: ee.ImageCollection,
                                      start_date: ee.Date,
                                      end_date: ee.Date) -> ee.ImageCollection:
    '''
    Aggregates images for each month by calculating cummulative monthly value
    from daily values.

    Daily values may be missing, so we don't use a sum - instead we calculate
    a daily mean value, and then multiply it with the number of days in a
    month.
    '''
    n_months = end_date.difference(start_date, 'month').round().subtract(1)
    months = ee.List.sequence(0, n_months) \
                    .map(lambda n: start_date.advance(n, 'month'))

    def aggregate(monthly_date):
        start_month = ee.Date(monthly_date)
        end_month = start_month.advance(1, 'month')
        num_of_days = end_month.difference(start_month, 'days')
        return (ic.filterDate(start_month, end_month)
                .mean().multiply(num_of_days)
                .set("date", start_month.format("YYYY-MM"))
                .set("month", start_month.get("month"))
                .set("year", start_month.get("year"))
                .set("system:time_start", start_month.millis()))

    return ee.ImageCollection(months.map(aggregate))


def from_cummulative_8_days_to_daily(ic: ee.ImageCollection,
                                     start_date: ee.Date,
                                     end_date: ee.Date) -> ee.ImageCollection:
    '''
    Takes in image collection that has 8-day cumulative composites, and
    upsamples it into a daily for each day between the start and end date.

    Assumes 8 days is the sum of all eight days within the composite period.
    '''
    # Assert that the start date is divisible by 8 - which means there is a
    # corresponding 8-day composite for each day, starting on the first one.
    assert start_date.getRelative("day", "year").getInfo() % 8 == 0, \
        "The first day of the time range must include the date of the first 8-day composite."  # noqa: E501

    # Upsample data to daily by dividing the 8-day amount equally
    # amongst the days it represents. That is 8 days - unless it's the end of
    # the year, in which case it's shorter.
    n_days = end_date.difference(start_date, 'day').subtract(1)
    days = ee.List.sequence(0, n_days).map(
        lambda n: start_date.advance(n, 'day'))

    def aggregate(date):
        date = ee.Date(date)
        # For each day, find the corresponding 8-day composite.
        # However, sometimes (I've only seen it once), a composite may be
        # missing. If that's the case, we take the values from the one before
        # it. This is why we take a look at all composites in the last 16 days,
        # and pick the most recent one.
        img = ic.filterDate(date.advance(-15, 'day'), date.advance(1, 'day')) \
                .limit(1, "system:time_start", opt_ascending=False).first()

        # Find how many days this composite represents (usually 8, but less at
        # the end of the year).
        next_year = img.date().update(day=1, month=1).advance(1, 'year')
        divide_by = next_year.difference(img.date(), 'day').min(ee.Number(8))

        # Divide each image band by the number of days.
        return img.divide(divide_by) \
                  .set("system:time_start", date.millis()) \
                  .set("system:index", date.format("YYYY-MM-dd"))

    return ee.ImageCollection(days.map(aggregate))


def aggregate_monthly_per_polygon(df: pd.DataFrame, aggregator: Callable,
                                  columns: list[str]) -> pd.DataFrame:
    ''' Calculate monthly aggregation for each year-month for each polygon. '''
    return aggregator(df.groupby(['month', 'year', 'polygon_id'])) \
        .reset_index()[['month', 'year', 'polygon_id',  *columns]]


def aggregate_monthly_per_polygon_across_years(df: pd.DataFrame,
                                               aggregator: Callable,
                                               columns: list[str]) \
        -> pd.DataFrame:
    ''' Calculate monthly aggregation for each polygon across all years. '''
    return aggregator(df.groupby(['month', 'polygon_id'])) \
        .reset_index() \
        .drop(columns=['year'])[['month', 'polygon_id',  *columns]]


def aggregate_number_of_shots(df: pd.DataFrame) -> pd.DataFrame:
    ''' Gets number of shots by month and polygon. '''
    return df.groupby(['year', 'month', 'polygon_id']) \
        .count().reset_index() \
        .rename(columns={'pai': 'number'})[['year', 'month', 'polygon_id', 'number']]  # noqa: E501
