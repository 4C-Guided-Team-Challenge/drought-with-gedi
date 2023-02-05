import argparse
import os
import geopandas as gpd
from shapely.geometry import Polygon
from drought.src.data.gedi_database import GediDatabase

def test_linting():
    pass

def parse_args():
    # random change to test linting.
    parser = argparse.ArgumentParser()
    parser.add_argument("--shape_path", default="../../data/Amazonia_drought_gradient_polygons.shp", type=str, help="path of shapefile")
    parser.add_argument("--product_level", default="level_2b", type=str, help="level of GEDI product to query")
    parser.add_argument("--fields", nargs='+', type = str, help="fields to query for corresponding level of product")
    parser.add_argument("--rh_percentiles", nargs='+', type=int, help="range of percentiles to query for RH the tree height")
    parser.add_argument("--save_path", default="../../data/interim/", type=str, help="path to save the query result as a csv file")
    return parser.parse_args()

def gedi_query_psql(
      shape_path:str=None,
      product_level:str=None,
      fields:list=None,
      rh_percentiles:list=None,
      save_path:str=None,
):
    """
    The function can be used to query the GEDI shots at given level, fields and polygons.
    """
    assert product_level in ["level_4a", "level_2b"]
    shape = gpd.read_file(shape_path)
    database = GediDatabase()

    # Load specified data columns for all GEDI shots within shape for 2019
    columns = fields+["shot_number", "lon_lowestmode", "lat_lowestmode"]
    # iterate over time
    processed_data = None
    count = 0
    for year in range(2020, 2023):
        for month in range(1, 13):
            # iterate over each polygon
            for i in range(len(shape)):
                feature = shape.loc[i]
                gedi_shots_gdf = database.query(
                    table_name=product_level,
                    columns=columns,
                    geometry=gpd.GeoDataFrame(geometry=[feature.geometry]).geometry,
                    crs=shape.crs,
                    start_time=f"{year}-{month}-01",
                    end_time=f"{year}-{month+1}-01" if month!=12 else f"{year+1}-01-01",
                    # Get a GeoDataFrame instead of pandas DataFrame
                    use_geopandas=True,
                    # use_geopandas = False,
                )
                print("timestamp", f"{year}-{month}-01", "polygon", feature.id)
                # gedi_shots_gdf = gedi_shots_gdf.loc[gedi_shots_gdf.l2b_quality_flag==1]
                gedi_shots_gdf = gedi_shots_gdf.loc[gedi_shots_gdf[f"l{product_level.split('_')[1]}_quality_flag"]==1]
                if gedi_shots_gdf.shape[0]==0:
                    continue
                gedi_shots_gdf["year"] = year
                gedi_shots_gdf["month"] = month
                gedi_shots_gdf["polygon_id"] = feature.id
                gedi_shots_gdf["polygon_spei"] = feature.SPEI
                processed_data = gedi_shots_gdf if count == 0 else processed_data.append(gedi_shots_gdf)
                count += 1

    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)
    # processed_data.to_csv(os.path.join(save_path, f"gedi_shots_{product_level}.csv"))

if __name__=="__main__":
    args = parse_args()
    print(args)
    gedi_query_psql(
        shape_path=args.shape_path,
        product_level=args.product_level,
        fields=args.fields,
        rh_percentiles=args.rh_percentiles,
        csv_path=args.save_path,
    )


            

