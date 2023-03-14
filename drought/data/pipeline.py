''' Module that contains our entire data pipeline. '''
from drought.data.aggregator import aggregate_monthly_per_polygon
from drought.data.aggregator import aggregate_monthly_per_polygon_across_years
from drought.data.ee_climate import get_monthly_climate_data_as_pdf, \
    CLIMATE_COLUMNS
from drought.data.ee_converter import gdf_to_ee_polygon
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
GEDI_MONTHLY_MEANS_CSV = "../../data/interim/gedi_PAI_monthly_mean_per_polygon_4-2019_to_6-2022.csv"  # noqa: E501
GEDI_MONTHLY_MEDIANS_CSV = "../../data/interim/gedi_PAI_monthly_median_per_polygon_4-2019_to_6-2022.csv"  # noqa: E501
GEDI_MONTHLY_AGG_MEANS_CSV = "../../data/interim/gedi_PAI_monthly_mean_per_polygon_across_years_4-2019_to_6-2022.csv"  # noqa: E501
GEDI_MONTHLY_AGG_MEDIANS_CSV = "../../data/interim/gedi_PAI_monthly_median_per_polygon_across_years_4-2019_to_6-2022.csv"  # noqa: E501
CLIMATE_MONTHLY_MEANS_CSV = "../../data/interim/climate_r_p_t_monthly_mean_per_polygon_1-2019_to_12-2022.csv"  # noqa: E501
CLIMATE_MONTHLY_AGG_MEANS_CSV = "../../data/interim/climate_r_p_t_aggregate_monthly_mean_per_polygon_1-2019_to_12-2022.csv"  # noqa: E501
GEDI_FOOTPRINTS = "/maps-priv/maps/drought-with-gedi/gedi_data/gedi_shots_level_2b.csv"  # noqa: E501
GEDI_FILTERED_FOOTPRINTS = "/maps/drought-with-gedi/gedi_data/gedi_shots_level_2b_land_filtered.csv"  # noqa: E501
GEDI_EXTENDED_FOOTPRINTS = "/maps-priv/maps/drought-with-gedi/gedi_data/gedi_shots_lebel_2b_extended.csv"  # noqa: E501


def get_gpd_polygons():
    ''' Returns a list of GTC Regions of Interest, as geopandas geometries. '''
    return gpd.read_file(POLYGONS_DIR)


def get_gedi_footprints():
    ''' Returns dataframe containing all footprints within polygons. '''
    gedi_csv = pd.read_csv(GEDI_FOOTPRINTS, index_col=0)

    return gedi_csv


def get_extended_gedi_footprints():
    ''' Returns dataframe containing all footprints within polygons. '''
    gedi_csv = pd.read_csv(GEDI_EXTENDED_FOOTPRINTS, index_col=0)

    return gedi_csv


def get_ee_polygons():
    ''' Returns a list of GTC Regions of Interest, as ee geometries. '''
    gdf = get_gpd_polygons()
    return [gdf_to_ee_polygon(polygon) for polygon in gdf.geometry]


def generate_GEDI_monthly_data():
    ''' Generates monthly GEDI data and saves it to a CSV file.'''
    # Read GEDI data from Sherwood.
    gedi_csv = pd.read_csv(GEDI_FOOTPRINTS)

    # Calculate monthly means for each polygon.
    monthly_means = aggregate_monthly_per_polygon(
        gedi_csv, lambda x: x.mean(numeric_only=True), ['pai'])

    # Save to csv file.
    monthly_means.to_csv(GEDI_MONTHLY_MEANS_CSV)

    # Calculate monthly means for each polygon.
    monthly_median = aggregate_monthly_per_polygon(
        gedi_csv, lambda x: x.median(numeric_only=True), ['pai'])

    # Save to csv file.
    monthly_median.to_csv(GEDI_MONTHLY_MEDIANS_CSV)

    # Calculate aggregate monthly means across all the years.
    total_monthly_mean = aggregate_monthly_per_polygon_across_years(
        gedi_csv, lambda x: x.mean(numeric_only=True), ['pai'])

    # Save to csv file.
    total_monthly_mean.to_csv(GEDI_MONTHLY_AGG_MEANS_CSV)

    # Calculate aggregate monthly means across all the years.
    total_monthly_median = aggregate_monthly_per_polygon_across_years(
        gedi_csv, lambda x: x.median(numeric_only=True), ['pai'])

    # Save to csv file.
    total_monthly_median.to_csv(GEDI_MONTHLY_AGG_MEDIANS_CSV)


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
    monthly_mean = aggregate_monthly_per_polygon(
        climate_pdf, lambda x: x.median(numeric_only=True), CLIMATE_COLUMNS)

    # Save monthly means to a csv file.
    monthly_mean.to_csv(CLIMATE_MONTHLY_MEANS_CSV)

    # Calculate aggregate monthly means for across all the years.
    total_monthly_mean = aggregate_monthly_per_polygon_across_years(
        climate_pdf, lambda x: x.median(numeric_only=True), CLIMATE_COLUMNS)

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


def get_filtered_gedi_footprints():
    return pd.read_csv(GEDI_FILTERED_FOOTPRINTS, index_col=0)


def execute():
    ''' Executes our entire data pipeline. '''
    ee.Initialize()

    generate_climate_monthly_data()
    generate_GEDI_monthly_data()
    return get_monthly_means_per_polygon()
