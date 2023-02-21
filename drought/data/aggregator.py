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
                                  columns: list[str],
                                  groupby: list[str] =
                                  ['month', 'year', 'polygon_id'],
                                  ) -> pd.DataFrame:
    ''' Calculate monthly aggregation for each year-month for each polygon. '''
    return aggregator(df.groupby(groupby)) \
        .reset_index()[[*groupby,  *columns]]


def aggregate_monthly_per_polygon_across_years(df: pd.DataFrame,
                                               aggregator: Callable,
                                               columns: list[str],
                                               groupby: list[str] =
                                               ['month', 'polygon_id'],
                                               ) -> pd.DataFrame:
    ''' Calculate monthly aggregation for each polygon across all years. '''
    return aggregator(df.groupby(groupby)) \
        .reset_index() \
        .drop(columns=['year'])[[*groupby,  *columns]]
