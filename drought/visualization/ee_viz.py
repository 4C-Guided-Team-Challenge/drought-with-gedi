import branca
import ee
import folium
import geemap
from drought.data.ee_converter import gdf_to_ee_polygon
from drought.data.pipeline import get_gpd_polygons


def viz_all_polygons(img: ee.Image,  band: str) -> folium.Map:
    ''' Plots image pixels on a map across all 8 polygons. '''
    polygons = get_gpd_polygons().geometry
    lon, lat = polygons.centroid.x.median(), polygons.centroid.y.median()
    my_map = folium.Map(location=[lat, lon], zoom_start=5, control_scale=True)

    for polygon in polygons:
        region = gdf_to_ee_polygon(polygon)
        img_stats = geemap.image_stats(img.clip(region), scale=5000).getInfo()

        band_min = img_stats['min'][band]
        band_max = img_stats['max'][band]
        if band_min == band_max:
            band_max = band_min + 1
        colors = ['#ffff00', '#800026']

        my_map.add_ee_layer(img.select(band).clip(region),
                            {'min': band_min, 'max': band_max,
                             'palette': colors}, name=band)

    return my_map


def viz_single_polygon(img: ee.Image, polygon_index: int,  band: str) \
        -> folium.Map:
    ''' Plots image pixels on a map clipped to a specified polygon. '''
    polygon = get_gpd_polygons().geometry[polygon_index]
    region = gdf_to_ee_polygon(polygon)
    img_stats = geemap.image_stats(img.clip(region), scale=5000).getInfo()

    band_min = img_stats['min'][band]
    band_max = img_stats['max'][band]
    if band_min == band_max:
        band_max = band_min + 1
    colors = ['#ffff00', '#800026']

    lon, lat = polygon.centroid.x, polygon.centroid.y
    my_map = folium.Map(location=[lat, lon], zoom_start=9, control_scale=True)
    my_map.add_ee_layer(img.select(band).clip(region),
                        {'min': band_min, 'max': band_max,
                         'palette': colors}, name=band)

    # Add legend
    colormap = branca.colormap.LinearColormap(
        colors=['yellow', 'red']).scale(band_min, band_max)
    colormap.add_to(my_map)
    return my_map


def add_ee_layer(self, ee_image_object, vis_params, name):
    '''Adds a method for displaying Earth Engine image tiles to folium map.'''
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',  # noqa: E501
        name=name,
        overlay=True,
        control=True
    ).add_to(self)


# Add Earth Engine drawing method to folium.
folium.Map.add_ee_layer = add_ee_layer
