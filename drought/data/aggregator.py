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


def from_8_days_to_monthly(ic: ee.ImageCollection, aggregator: Callable,
                           start_date: ee.Date, end_date: ee.Date):
    '''
    Takes in image collection that has 8-day composites, and aggregates it to
    monthly.

    It firsts upsamples data to daily, assuming that 8-day is a cumulative
    composite of those 8 days, then aggregates daily data for each month using
    the provided aggregator function.
    '''
    # Assert that the start date is divisible by 8 - which means there is a
    # corresponding 8-day composite for each day, starting on the first one.
    assert start_date.getRelative("day", "year").getInfo() % 8 == 0, \
        "The first day of the time range must include the date of the first 8-day composite."  # noqa: E501

    # Step 1 - Upsample data to daily by dividing the 8-day amount equally
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
                  .copyProperties(img, ["system:time_start", "system:index"])

    daily_ic = ee.ImageCollection(days.map(aggregate))

    # Step 2 - Aggregate daily data to monthly.
    return make_monthly_composite(daily_ic, aggregator, start_date, end_date)


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
