# %%
import os
import sys
BASE_DIR = "/maps-priv/maps/ys611/drought-with-gedi/"  # noqa: E501
sys.path.append(BASE_DIR)  # noqa: E501
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from drought.data.aggregator import aggregate_monthly_per_polygon
from drought.data.aggregator import aggregate_monthly_per_polygon_across_years
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%
DATA_PATH = "data/interim/gedi_shots_level_2b_7d_pai.csv"
GEDI_L2B_CSV = os.path.join(
    BASE_DIR, DATA_PATH
)
gedi_csv = pd.read_csv(GEDI_L2B_CSV)

# %%
# monthly_means = aggregate_monthly_per_polygon(
#     gedi_csv, lambda x: x.mean(numeric_only=True), ['pai'],
#     groupby=['polygon_id', 'year', 'month'])
monthly_means = aggregate_monthly_per_polygon(
    gedi_csv, lambda x: x.mean(numeric_only=True), ['pai'],
    groupby=['polygon_id', 'timestamp'])

# TODO test different statistics, mean, median, variance etc.
# TODO test other fields, relative height, density etc.
# TODO refine the granularity of the queried data
# monthly_medians = aggregate_monthly_per_polygon(
#     gedi_csv, lambda x: x.median(numeric_only=True), ['pai']
# )
# %%
for i in range(1, 9):
    polygon_filter = monthly_means['polygon_id'] == i
    print(f'polygon used for time series anaylysis: {i}')
    # res = STL(monthly_means[polygon_filter][['timestamp', 'pai']]).fit()
    res = STL(monthly_means[polygon_filter]['pai'], period=52).fit()
    res.plot()

# %%
SAVE_DIR = os.path.join(BASE_DIR, "reports/figures/seasonality")
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
for i in range(1, 9):
    polygon_filter = monthly_means['polygon_id'] == i
    if sum(polygon_filter) < 38:
        continue
    print(f'polygon used for time series anaylysis: {i}')
    time_series = {}
    for k in ['year', 'month', 'pai']:
        time_series[k] = np.array(monthly_means[k][polygon_filter])
    time_stamp = np.array([
        f"{y}-{m}" for y, m in zip(time_series['year'], time_series['month'])
    ])
    # res = seasonal_decompose(time_series['pai'], period=6)
    # TODO run STL analysis without specifying period (using pd index)
    res = STL(time_series['pai'], period=3).fit()
    res.plot()
    # plt.savefig(os.path.join(SAVE_DIR, f"polygon{i}_monthly_means_pai.png"))
