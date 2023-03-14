import os
import sys
import argparse
from statsmodels.tsa.seasonal import STL
from drought.data.aggregator import aggregate_monthly_per_polygon
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = "/maps-priv/maps/ys611/drought-with-gedi/"  # noqa: E501
sys.path.append(BASE_DIR)  # noqa: E501


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timescale", default="weekly",
                        type=str, help="granularity of seasonal component in ['monthly', 'weekly']")  # noqa: E501
    parser.add_argument("--period", default=12,
                        type=int, help="period of STL function for seasonality analysis")  # noqa: E501
    parser.add_argument("--save_path", defult="reports/figures/",
                        type=str, help="path to save plots")
    return parser.parse_args()


def seasonality(
        time_scale: str,
        period: int,
        save_path: str,
):
    assert time_scale in ["monthly", "weekly"], "Timescale not supported"
    if time_scale == "monthly":
        DATA_PATH = "data/interim/gedi_queried_shots_original.csv"
    else:
        DATA_PATH = "data/interim/gedi_shots_level_2b_7d_pai.csv"

    GEDI_L2B_CSV = os.path.join(BASE_DIR, DATA_PATH)
    gedi_csv = pd.read_csv(GEDI_L2B_CSV)

    if time_scale == "monthly":
        monthly_means = aggregate_monthly_per_polygon(
            gedi_csv, lambda x: x.mean(numeric_only=True), ['pai'],
            groupby=['polygon_id', 'year', 'month'])
    else:
        monthly_means = aggregate_monthly_per_polygon(
            gedi_csv, lambda x: x.mean(numeric_only=True), ['pai'],
            groupby=['polygon_id', 'timestamp'])

    SAVE_DIR = os.path.join(BASE_DIR, save_path, f"seasonality_{time_scale}")
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    for i in range(1, 9):
        polygon_filter = monthly_means['polygon_id'] == i
        # skip the polygons with if number of available months is less than 38
        if time_scale == "monthly" and sum(polygon_filter) < 38:
            continue
        print(f'polygon used for time series anaylysis: {i}')
        res = STL(monthly_means[polygon_filter]['pai'], period=period).fit()
        res.plot()
        plt.savefig(os.path.join(BASE_DIR, SAVE_DIR,
                                 f"polygon{i}_{time_scale}_means_pai.png"))


if __name__ == "__main__":
    args = parse_args()
    print(args)
    seasonality(
        time_scale=args.time_scale,
        period=args.time_period,
        save_path=args.save_path,
    )
