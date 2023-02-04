'''
Methods for converting Earth Engine data structures to other formats (Pandas,
GeoPandas, shapely, etc.) and back.
'''
import ee
import numpy as np
import shapely


def gdf_to_ee_polygon(gdf_polygon: shapely.Polygon):
    ''' Helper to convert GeoPandas geometry to Earth Engine geometry. '''
    x, y = gdf_polygon.exterior.coords.xy
    coords = np.dstack((x, y)).tolist()
    return ee.Geometry.Polygon(coords)
