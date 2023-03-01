import json
import pandas as pd
import numpy as np
GEDI_DATA_DIR = \
    "/maps/ys611/drought-with-gedi/data/interim/gedi_shots_level_2b.csv"


def vertical_stats(x: str):
    x = np.array(json.load(x))
    return x[x != 0].mean(), x.max(), x.sum()


data = pd.read_csv(GEDI_DATA_DIR)

data.columns
ls = json.loads(data['pai_z'][0])
data["pai_z_mean"], data["pai_z_max"], data["pai_z_sum"] = data['pai_z'].map(
    lambda x: vertical_stats(x))
