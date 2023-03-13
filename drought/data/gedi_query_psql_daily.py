import argparse
import os
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import date, timedelta
from utils.gedi_database import GediDatabase


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shape_path",
                        default="data/polygons/Amazonia_drought_gradient_polygons.shp",  # noqa: E501
                        type=str, help="path of shapefile")
    parser.add_argument("--start_time", type=str, default="2019-1-1",
                        help="start date of query in the format yyyy-m-d")
    parser.add_argument("--end_time", type=str, default="2022-12-31",
                        help="end date of query in the format yyyy-m-d")
    parser.add_argument("--time_delta", type=int, default=7,
                        help="time interval to specify the query dates")
    parser.add_argument("--product_level", type=str, default="level_2b",
                        help="level of GEDI product to query")
    parser.add_argument("--fields", nargs='+', type=str, default=[],
                        help="fields to query for corresponding level of product")  # noqa: E501
    parser.add_argument("--save_path", default="data/interim/",
                        type=str, help="path to save the query result as a csv file")  # noqa: E501
    return parser.parse_args()

def gedi_query_psql(
    shape_path: str,
    start_time: str,
    end_time: str,
    time_delta: int,
    product_level: str,
    save_path: str,
    fields: list = [],
):
    """
    The function can be used to query the GEDI shots at given level,
    fields and polygons.
    """
    assert product_level in ["level_4a", "level_2b"]
    shape = gpd.read_file(shape_path)
    database = GediDatabase()

    # Load data columns for all GEDI shots of given polygons.
    QUALITY_FLAG = f"l{product_level.split('_')[1]}_quality_flag"
    columns = fields+["shot_number", "lon_lowestmode",
                      "lat_lowestmode", QUALITY_FLAG]

    # iterate over time
    processed_data = gpd.GeoDataFrame(geometry=[])
    # year_range = range(year_range[0], year_range[1])
    # month_range = range(1, 13)
    start_time = [int(i) for i in start_time.split('-')]
    end_time = [int(i) for i in end_time.split('-')]
    start_time = date(start_time[0], start_time[1], start_time[2])
    end_time = date(end_time[0], end_time[1], end_time[2])
    time_delta = timedelta(days=time_delta)

    # iterate over each polygon
    for i in range(len(shape)):
        start_time_query = start_time
        while start_time_query < end_time:
            feature = shape.loc[i]
            gedi_shots_gdf = database.query(
                table_name=product_level,
                columns=columns,
                geometry=gpd.GeoDataFrame(
                    geometry=[feature.geometry]).geometry,
                crs=shape.crs,
                start_time=start_time_query.strftime("%Y-%m-%d"),
                end_time=(start_time_query+time_delta).strftime("%Y-%m-%d"),
                # Get a GeoDataFrame instead of pandas DataFrame
                use_geopandas=True,
            )
            print("timestamp", start_time_query.strftime(
                "%Y-%m-%d"), "polygon", feature.id)
            start_time_query += time_delta

            # Check the quality flag of the data product. If PAI is
            # queried, also make sure it is greater than 0.
            if "pai" in columns:
                qa_check_ok = np.logical_and(
                    gedi_shots_gdf[QUALITY_FLAG] == 1,
                    gedi_shots_gdf["pai"] > 0,
                )
            else:
                gedi_shots_gdf[QUALITY_FLAG] == 1

            gedi_shots_gdf = gedi_shots_gdf.loc[qa_check_ok]
            if gedi_shots_gdf.shape[0] == 0:
                continue

            gedi_shots_gdf["timestamp"] = pd.Timestamp(
                start_time_query-time_delta)
            gedi_shots_gdf["polygon_id"] = feature.id
            gedi_shots_gdf["polygon_spei"] = feature.SPEI
            processed_data = processed_data.append(gedi_shots_gdf)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    processed_data.to_csv(
        os.path.join(save_path, f"gedi_shots_{product_level}_7d_pai.csv")
    )


if __name__ == "__main__":
    args = parse_args()
    print(args)
    gedi_query_psql(
        shape_path=args.shape_path,
        start_time=args.start_time,
        end_time=args.end_time,
        time_delta=args.time_delta,
        product_level=args.product_level,
        save_path=args.save_path,
        fields=args.fields,
    )
