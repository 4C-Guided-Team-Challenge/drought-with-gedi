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

# File names for intermediate CSV data.
GEDI_MONTHLY_MEANS_CSV = "../../data/interim/gedi_PAI_monthly_mean_per_polygon_4-2019_to_6-2022.csv"
CLIMATE_MONTHLY_MEANS_CSV = "../../data/interim/climate_r_p_t_monthly_mean_per_polygon_1-2019_to_12-2022.csv"
CLIMATE_MONTHLY_AGG_MEANS_CSV = "../../data/interim/climate_r_p_t_aggregate_monthly_mean_per_polygon_1-2019_to_12-2022.csv"


def get_gpd_polygons():
    ''' Returns a list of GTC Regions of Interest, as geopandas geometries. '''
    return gpd.read_file(POLYGONS_DIR)


def get_ee_polygons():
    ''' Returns a list of GTC Regions of Interest, as ee geometries. '''
    gdf = get_gpd_polygons()
    return [gdf_to_ee_polygon(polygon) for polygon in gdf.geometry]


def generate_GEDI_monthly_data():
    ''' Generates monthly GEDI data and saves it to a CSV file.'''
    # Read GEDI data from Sherwood.
    gedi_csv = pd.read_csv(
        "/maps-priv/maps/ys611/drought-with-gedi/processed_data.csv")

    # Calculate monthly means for each polygon.
    monthly_means = gedi_csv.groupby(['month', 'year', 'polygon_id']) \
        .mean(numeric_only=True) \
        .reset_index()[["pai", "month", "year", "polygon_id"]]

    # Save to csv file.
    monthly_means.to_csv(GEDI_MONTHLY_MEANS_CSV)


def generate_climate_monthly_data():
    ''' Generates monthly climate data and saves it to a CSV file.'''
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
    monthly_mean.to_csv(CLIMATE_MONTHLY_MEANS_CSV)

    # Calculate aggregate monthly means for across all the years.
    total_monthly_mean = climate_pdf.groupby(['month', 'polygon_id']) \
        .mean(numeric_only=True).reset_index() \
        .drop(columns=['year'])

    # Save aggregate monthly means to a csv file.
    total_monthly_mean.to_csv(CLIMATE_MONTHLY_AGG_MEANS_CSV)


def get_monthly_means_per_polygon():
    ''' Combines all monthly data sources into one DataFrame. '''
    climate_monthly = pd.read_csv(CLIMATE_MONTHLY_MEANS_CSV, index_col=0)
    gedi_monthly = pd.read_csv(GEDI_MONTHLY_MEANS_CSV, index_col=0)

    # Join data sets.
    climate_indexed = climate_monthly.set_index(
        ['month', 'year', 'polygon_id'])
    gedi_indexed = gedi_monthly.set_index(['month', 'year', 'polygon_id'])
    monthly_data = gedi_indexed.join(climate_indexed).reset_index()
    return monthly_data


def execute():
    ''' Executes our entire data pipeline. '''
    ee.Initialize()

    generate_climate_monthly_data()
    generate_GEDI_monthly_data()
    return get_monthly_means_per_polygon()
