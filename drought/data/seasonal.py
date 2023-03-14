import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa import seasonal


def get_ts_seasonal_component(df: pd.DataFrame, polygon_id: int,
                              start_date: str, end_date: str,
                              columns: list[str], method='STL'
                              ) -> dict[str, pd.Series]:
    polygon_ts = df.loc[df.polygon_id == polygon_id]
    polygon_ts = polygon_ts.sort_values('datetime')
    polygon_ts.index = pd.date_range(
        start=start_date, end=end_date, freq=pd.offsets.MonthBegin(1))

    seasonal_df = polygon_ts[['polygon_id', 'date', 'month', 'year']]
    for column in columns:
        if method == 'STL':
            seasonal_df[column] = STL(polygon_ts[[column]], seasonal=13) \
                .fit().seasonal + polygon_ts[column].mean()
        else:
            seasonal_df[column] = \
                seasonal.seasonal_decompose(polygon_ts[[column]],
                                            model='additive') \
                .seasonal + polygon_ts[column].mean()
    return seasonal_df


def get_ts_seasonal_decomposition(df: pd.DataFrame, polygon_id: int,
                                  start_date: str, end_date: str,
                                  columns: list[str], method='STL'
                                  ) -> dict[str, pd.Series]:
    polygon_ts = df.loc[df.polygon_id == polygon_id]
    polygon_ts = polygon_ts.sort_values('datetime')
    polygon_ts.index = pd.date_range(
        start=start_date, end=end_date, freq=pd.offsets.MonthBegin(1))

    seasonal = {}
    for column in columns:
        if method == 'STL':
            seasonal[column] = STL(polygon_ts[[column]], seasonal=17).fit()
    return seasonal


def get_ts_seasonal_component_per_polygon(df: pd.DataFrame, start_date: str,
                                          end_date: str, columns: list[str],
                                          method='STL'
                                          ) -> dict[str, pd.Series]:
    all_polygon_dfs = []
    for polygon_id in range(1, 9):
        all_polygon_dfs.append(
            get_ts_seasonal_component(df, polygon_id, start_date, end_date,
                                      columns, method))
    seasonals_df = pd.concat(all_polygon_dfs)
    return seasonals_df.reset_index() \
        .rename(columns={'index': 'datetime'})


def calculate_nrmse(original, seasonal, polygon_id, column):
    original_polygon = original[original.polygon_id == polygon_id].set_index(
        'datetime').sort_index()[column]
    seasonal_polygon = seasonal[seasonal.polygon_id == polygon_id].set_index(
        'datetime').sort_index()[column]

    rmse = ((original_polygon - seasonal_polygon) ** 2).mean() ** .5
    nrmse = rmse / original_polygon.mean()
    # nrmse = rmse / (original_polygon.quantile(0.75) -
    #                original_polygon.quantile(0.25))
    return nrmse


def get_seasonal_amplitude(original, seasonal, polygon_id, column):
    # original_polygon = original[original.polygon_id == polygon_id].set_index(
    #    'datetime').sort_index()[column]
    seasonal_polygon = seasonal[seasonal.polygon_id == polygon_id].set_index(
        'datetime').sort_index()[column]

    absolute_amplitude = seasonal_polygon.max() - seasonal_polygon.min()
    # relative_amplitude = absolute_amplitude / (original_polygon.quantile(0.75) - original_polygon.quantile(0.25))  # noqa: E501
    relative_amplitude = absolute_amplitude / seasonal_polygon.mean()
    return absolute_amplitude, relative_amplitude
