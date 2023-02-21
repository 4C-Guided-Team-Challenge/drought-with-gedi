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
GEDI_L2B_CSV = os.path.join(
    BASE_DIR, "data/interim/gedi_shots_level_2b.csv"
)
gedi_csv = pd.read_csv(GEDI_L2B_CSV)

# %%
monthly_means = aggregate_monthly_per_polygon(
    gedi_csv, lambda x: x.mean(numeric_only=True), ['pai'],
    groupby=['polygon_id', 'year', 'month'])

# TODO test the median values later and add other fields to test
# monthly_medians = aggregate_monthly_per_polygon(
#     gedi_csv, lambda x: x.median(numeric_only=True), ['pai']
# )

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
    res = seasonal_decompose(time_series['pai'], period=6)
    res.plot()
    plt.savefig(os.path.join(SAVE_DIR, f"polygon{i}_monthly_means_pai.png"))

# %%
plt.plot(time_stamp, time_series['pai'])

# %%
res = seasonal_decompose(time_series['pai'], period=6)
res.plot()

#
# filter out the no data month

# seasonality analysis with two different functions

# plot and adapt the parameters

# %%
