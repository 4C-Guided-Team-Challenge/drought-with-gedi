''' Simple methods for fetching regions of interests relevant for GTC. '''
import geopandas as gpd
import numpy as np
import ee


def get_ee_polygons():
    ''' Returns a list of GTC Regions of Interest, as ee geometries. '''
    gdf = get_gpd_polygons()
    return [_gdf_to_ee_polygon(polygon) for polygon in gdf.geometry]


def get_gpd_polygons():
    ''' Returns a list of GTC Regions of Interest, as geopandas geometries. '''
    return gpd.read_file(
        "../data/polygons/Amazonia_drought_gradient_polygons.shp")


def _gdf_to_ee_polygon(gdf_polygon):
    ''' Helper to convert Geopandas geometry to Earth Engine geometry. '''
    x, y = gdf_polygon.exterior.coords.xy
    coords = np.dstack((x, y)).tolist()
    return ee.Geometry.Polygon(coords)
