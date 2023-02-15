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
