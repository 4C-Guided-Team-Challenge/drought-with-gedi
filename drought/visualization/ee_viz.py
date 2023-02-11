import ee
import geemap
import geemap.colormaps as cm
from drought.data.ee_converter import gdf_to_ee_polygon
from drought.data.pipeline import get_gpd_polygons, get_ee_polygons


def viz_all_polygons(img: ee.Image, bands: list[str],
                     palette: cm.Box = cm.palettes.inferno_r,
                     scale: int = 5000, map: geemap.Map = None) -> geemap.Map:
    '''
    Plots image on a map across all 8 polygons.

    Each band is added as a separate layer on the map.

    '''
    polygons = get_gpd_polygons().geometry
    ee_polygons = get_ee_polygons()

    if map is None:
        map = geemap.Map(center=(polygons.centroid.y.median(),
                                 polygons.centroid.x.median()),
                         zoom=5)

    # Clip image to include all of the polygons.
    clipped = ee.Image(ee.ImageCollection(
        [img.clip(geometry) for geometry in ee_polygons]).mosaic())
    # Get image stats for each region.
    img_stats = [geemap.image_stats(img.clip(region), scale=scale).getInfo()
                 for region in ee_polygons]

    for band in bands:
        # Calculate min and max across all polygons.
        band_min = min(stat['min'][band] for stat in img_stats)
        band_max = max(stat['max'][band] for stat in img_stats)
        band_vis = {'bands': band, 'palette': palette,
                    'min': band_min, 'max': band_max}
        map.addLayer(clipped, band_vis, band)
        map.add_colorbar(band_vis, label=band, layer_name=band)

    return map


def viz_single_polygon(img: ee.Image, polygon_index: int,  bands: list[str],
                       palette: cm.Box = cm.palettes.inferno_r,
                       scale: int = 5000,
                       map: geemap.Map = None) -> geemap.Map:
    '''
    Plots image on a map clipped to a specified polygon.

    Each band is added as a separate layer on the map.

    '''
    polygon = get_gpd_polygons().geometry[polygon_index]
    region = gdf_to_ee_polygon(polygon)
    img_stats = geemap.image_stats(img.clip(region), scale=5000).getInfo()

    if map is None:
        map = geemap.Map(center=(polygon.centroid.y, polygon.centroid.x),
                         zoom=9)

    for band in bands:
        band_min = img_stats['min'][band]
        band_max = img_stats['max'][band]
        band_vis = {'bands': band, 'palette': palette,
                    'min': band_min, 'max': band_max}
        map.addLayer(img.clip(region), band_vis, band)
        map.add_colorbar(band_vis, label=band, layer_name=band)

    return map
