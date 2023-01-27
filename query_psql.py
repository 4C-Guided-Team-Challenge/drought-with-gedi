import geopandas as gpd
from src.data.gedi_database import GediDatabase
from shapely.geometry import Polygon

shape = gpd.read_file("Amazonia_drought_gradient_polygons/Amazonia_drought_gradient_polygons.shp")

database = GediDatabase()

# TODO how to get the timestamp for each fetched shot?
# TODO do we need to further filter the quality flags?
# Load specified data columns for all GEDI shots within shape for 2019
columns = ["pai", "l2b_quality_flag", "shot_number", "lon_lowestmode", "lat_lowestmode"]
# iterate over time
processed_data = None
count = 0
for year in range(2019, 2023):
    for month in range(1, 13):
        # iterate over each polygon
        for i in range(len(shape)):
            feature = shape.loc[i]
            geometry =feature.geometry
            gedi_shots_gdf = database.query(
                table_name="level_2b",
                columns=columns,
                geometry = gpd.GeoDataFrame(geometry=[feature.geometry]).geometry,
                crs=shape.crs,
                start_time=f"{year}-{month}-01",
                end_time=f"{year}-{month+1}-01" if month!=12 else f"{year+1}-01-01",
                # Get a GeoDataFrame instead of pandas DataFrame
                # use_geopandas=True,
                use_geopandas = False,
            )
            print("timestamp", f"{year}-{month}-01", "polygon", feature.id)
            gedi_shots_gdf = gedi_shots_gdf.loc[gedi_shots_gdf.l2b_quality_flag==1]
            if gedi_shots_gdf.shape[0]==0:
                continue
            gedi_shots_gdf["year"] = year
            gedi_shots_gdf["month"] = month
            gedi_shots_gdf["polygon_id"] = feature.id
            gedi_shots_gdf["polygon_spei"] = feature.SPEI
            processed_data = gedi_shots_gdf if count == 0 else processed_data.append(gedi_shots_gdf)
            count += 1

processed_data.to_csv("processed_data.csv")
            

