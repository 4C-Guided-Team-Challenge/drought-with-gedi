''' Module that contains our entire data pipeline. '''
from drought.data.ee_climate import get_monthly_climate_data
from drought.data.ee_converter import gdf_to_ee_polygon
import ee
import geopandas as gpd

POLYGONS_DIR = '../../data/polygons/Amazonia_drought_gradient_polygons.shp'

# Initial date of interest (inclusive).
START_DATE = '2019-01-01'

# Final date of interest (exclusive).
END_DATE = '2023-01-01'


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

    # Get monthly climate data.
    climate_monthly = get_monthly_climate_data(start_date, end_date, ee_geoms)

    return climate_monthly
