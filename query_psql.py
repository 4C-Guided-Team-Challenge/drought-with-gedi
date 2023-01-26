#%%
import geopandas as gpd
from src.data.gedi_database import GediDatabase

shape = gpd.read_file("Amazonia_drought_gradient_polygons/Amazonia_drought_gradient_polygons.shp")

database = GediDatabase()

#%%
# TODO how to get the timestamp for each fetched shot?
# TODO do we need to further filter the quality flags?
# Load specified data columns for all GEDI shots within shape for 2019
columns = ["pai", "l2b_quality_flag", "shot_number", "lon_lowestmode", "lat_lowestmode"]
# iterate over each polygon
for i in range(len(shape)):
    feature = shape.loc[i]
    gedi_shots_gdf = database.query(
        table_name="level_2b",
        columns=columns,
        # geometry=shape.geometry,
        # TODO fix the error: AttributeError: 'Polygon' object has no attribute 'to_wkt'
        geometry = feature.geometry,
        crs=shape.crs,
        start_time=f"2019-01-01",
        end_time=f"2020_01_01",
        # Get a GeoDataFrame instead of pandas DataFrame
        # TODO verify whether this step is necessary
        use_geopandas=True,
    )
#%%
gedi_shots_gdf
