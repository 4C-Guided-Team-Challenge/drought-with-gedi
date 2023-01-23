import geopandas as gpd
from src.data.gedi_database import GediDatabase

shape = gpd.read_file("~/Amazonia_drought_gradient")

database = GediDatabase()

# Load specified data columns for all GEDI shots within shape for 2019
gedi_shots_gdf = database.query(
    table_name="level_2b",
    columns=[
    "shot_number",
    # and other columns to fetch
    ],
    geometry=shape.crs,
    start_time=f"2019-01-01",
    end_time=f"2020_01_01",
    # Get a GeoDataFrame instead of pandas DataFrame
    # TODO verify whether this step is necessary
    use_geopandas=True,
)
