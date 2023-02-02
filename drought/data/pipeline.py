''' Module that contains our entire data pipeline. '''
from drought.data.ee_climate import get_monthly_climate_data_as_pdf
from drought.data.ee_converter import gdf_to_ee_polygon, get_region_as_df
import ee
import geopandas as gpd
import pandas as pd

POLYGONS_DIR = '../../data/polygons/Amazonia_drought_gradient_polygons.shp'

# Initial date of interest (inclusive).
START_DATE = '2019-01-01'

# Final date of interest (exclusive).
END_DATE = '2023-01-01'

# Raster resolution.
SCALE = 5000


def get_gpd_polygons():
    ''' Returns a list of GTC Regions of Interest, as geopandas geometries. '''
    return gpd.read_file(POLYGONS_DIR)


def get_ee_polygons():
    ''' Returns a list of GTC Regions of Interest, as ee geometries. '''
    gdf = get_gpd_polygons()
    return [gdf_to_ee_polygon(polygon) for polygon in gdf.geometry]


def execute():
    ''' Executes our entire data pipeline. '''
    ee.Initialize()

    # Dates of interest.
    start_date = ee.Date(START_DATE)
    end_date = ee.Date(END_DATE)

    # Get regions of interest.
    ee_geoms = get_ee_polygons()

    # Get monthly climate data as Pandas DataFrame.
    climate_pdf = get_monthly_climate_data_as_pdf(
        start_date, end_date, ee_geoms, SCALE)

    # Calculate monthly mean per polygon.
    monthly_mean = climate_pdf.groupby(['month', 'year', 'polygon_id']) \
        .mean(numeric_only=True).reset_index()

    # Save monthly means to a csv file.
    monthly_mean.to_csv(
        "../../data/interim/climate_r_p_t_monthly_mean_per_polygon_1-2019_to_12-2022.csv")

    # Calculate aggregate monthly means for across all the years.
    total_monthly_mean = climate_pdf.groupby(['month', 'polygon_id']) \
        .mean(numeric_only=True).reset_index() \
        .drop(columns=['year'])

    # Save aggregate monthly means to a csv file.
    total_monthly_mean.to_csv(
        "../../data/interim/climate_r_p_t_aggregate_monthly_mean_per_polygon_1-2019_to_12-2022.csv")
