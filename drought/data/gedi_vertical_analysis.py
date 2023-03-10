import json
import pandas as pd
import numpy as np
GEDI_DATA_DIR = \
    "/maps/ys611/drought-with-gedi/data/interim/gedi_shots_level_2b.csv"
SAVE_PATH = \
    "/maps/ys611/drought-with-gedi/data/interim/gedi_shots_level_2b_vertical.csv"  # noqa: E501


def vertical_stats(x, stat: str):
    assert stat in ['mean', 'median', 'max', 'min', 'sum']
    x = np.array(json.loads(x))
    if stat == 'mean':
        return x[x != 0].mean() if sum(x != 0) != 0 else 0
    # TODO bug to fix, the following line only returns 0
    if stat == 'median':
        num = np.median(x)
        return np.median(x)
    if stat == 'max':
        return x.max()
    if stat == 'min':
        return x[x != 0].min() if sum(x != 0) != 0 else 0
    if stat == 'sum':
        return x.sum()


data = pd.read_csv(GEDI_DATA_DIR)

data[f"pai_z_sum"] = data['pai_z'].map(
    lambda x: vertical_stats(x, stat='sum'))
# stats = ['mean', 'median', 'max', 'min']
stats = ['median']
for field in ['pai_z', 'pavd_z']:
    for stat in stats:
        print(field, stat)
        data[f"{field}_{stat}"] = data[field].map(
            lambda x: vertical_stats(x, stat=stat))
    data.drop(columns=[field], axis=1, inplace=True)

# data.to_csv(SAVE_PATH)
