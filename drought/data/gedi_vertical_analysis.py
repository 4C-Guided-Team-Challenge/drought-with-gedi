import argparse
import json
import pandas as pd
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path",
                        default="/maps/ys611/drought-with-gedi/data/interim/gedi_shots_level_2b.csv",  # noqa: E501
                        type=str, help="path of GEDI data")
    parser.add_argument("--save_path",
                        default="/maps/ys611/drought-with-gedi/data/interim/gedi_shots_level_2b_vertical.csv",  # noqa: E501
                        help=str, help="path to save the results csv")
    return parser.parse_args()


def vertical_stats(x, stat: str):
    assert stat in ['mean', 'max', 'min', 'sum']
    x = np.array(json.loads(x))
    if stat == 'mean':
        return x[x != 0].mean() if sum(x != 0) != 0 else 0
    if stat == 'max':
        return x.max()
    if stat == 'min':
        return x[x != 0].min() if sum(x != 0) != 0 else 0
    if stat == 'sum':
        return x.sum()


def vertical(
    data_path: str,
    save_path: str,
):
    GEDI_DATA_DIR = data_path
    SAVE_PATH = save_path
    data = pd.read_csv(GEDI_DATA_DIR)

    data['pai_z_sum'] = data['pai_z'].map(
        lambda x: vertical_stats(x, stat='sum'))

    stats = ['mean', 'max', 'min']
    for field in ['pai_z', 'pavd_z']:
        for stat in stats:
            print(field, stat)
            data[f"{field}_{stat}"] = data[field].map(
                lambda x: vertical_stats(x, stat=stat))
        data.drop(columns=[field], axis=1, inplace=True)

    data.to_csv(SAVE_PATH)


if __name__ == "__main__":
    args = parse_args()
    print(args)
    vertical(
        data_path=args.data_path,
        save_path=args.save_path,
    )
