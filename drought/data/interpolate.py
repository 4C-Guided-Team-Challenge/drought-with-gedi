import pandas as pd


def interpolate_using_weighted_average(df_all_polygons: pd.DataFrame,
                                       weight: str, value: str
                                       ) -> pd.DataFrame:
    '''
    Interpolates values on the value column based on the weighted average of a
    3 month sliding window.

    Corresponding weights are sampled from the weight column.

    Outputs interpolated value on the 'value_interpolated' column of the output
    DataFrame.

    Example: 
      value = 'pai', weight = 'number' (number of GEDI shots per month).

      In this case, we want to interpolate pai value for each month, based on 
      the PAI values in the previous, current and next month.

      Each month PAI is weighted according to the number of GEDI shots 
      available for that month. More GEDI shots => more significant PAI value.
    '''
    all_polygons = []
    for polygon_id in range(1, 9):
        df = df_all_polygons[df_all_polygons.polygon_id == polygon_id]

        # Sort based on dates, in this case just year and month. This is
        # important because we want to interpolate values for the current
        # month based on the previous and the next month.

        # TODO: If we wanted to interpolate on a less than month granularity,
        # we'd need to update this.
        df = df.sort_values(by=['year', 'month'])

        # Step 1: Calculate weighted value for each date = value * weight.
        weighted_values = df[value] * df[weight]

        # Step 2: Calculate the total weights for the 3 month window.
        sum_of_weighted_values = weighted_values.rolling(
            window=3, center=True).sum()

        # Step 3. Weighted sum for rolling 3 month window.
        sum_of_weights = df[weight].rolling(window=3, center=True).sum()

        # Interpolated value = (sum of weighted values) / (sum of the weights)
        interpolated_value = sum_of_weighted_values / sum_of_weights

        df[f'{value}_interpolated'] = interpolated_value
        all_polygons.append(df)
    return pd.concat(all_polygons)


def fill_timeseries_missing_data(df: pd.DataFrame, start_date: str,
                                 end_date: str, values_to_fill: dict[str, str]
                                 ) -> pd.DataFrame:
    '''
    If DataFrame df is missing data for any months between start_date and 
    end_date, this method will create new rows for the missing months and fill
    missing data with values_to_fill.

    values_to_fill is a dictionary of the form: column_name -> value_to_fill.
    '''
    df_copy = df.copy()
    for polygon in range(1, 9):
        for date in pd.date_range(start=start_date, end=end_date, freq='M'):
            if not ((df['year'] == date.year)
                    & (df['month'] == date.month)
                    & (df['polygon_id'] == polygon)).any():

                new_row = pd.DataFrame({'year': date.year,
                                        'month': date.month,
                                        'polygon_id': polygon}
                                       | values_to_fill,
                                       index=[0])
                df_copy = pd.concat([df_copy, new_row], ignore_index=True)
    return df_copy
