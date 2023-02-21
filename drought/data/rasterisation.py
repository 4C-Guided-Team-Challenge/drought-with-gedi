from drought.data.pipeline import *
from sklearn.cluster import KMeans
from math import floor
from shapely import Polygon
from typing import Callable
import pickle


def rasterise_polygon(r: int, df: pd.DataFrame, shape: gpd.GeoDataFrame,
                      polygon: int):
    ''' 
    Generates a r x r grid (as a 2D list) and then 
    assigns every footprint to the appropriate cell.

    df should contain GEDI footprints, shape the polygons of interest, 
    and polygon the desired polygon_id. 

    Returns both the grid AND a list of polygons representing
    each grid cell.
    '''
    df = df[df["polygon_id"] == polygon]
    geometry = shape.geometry[polygon - 1]

    grid = [[pd.DataFrame()]*r for i in range(r)]

    minx, miny, maxx, maxy = geometry.bounds
    stepx = (maxx - minx) / r
    stepy = (maxy - miny) / r

    for i in range(len(df)):
        footprint = df.iloc[[i]]
        lon = footprint["lon_lowestmode"]
        lat = footprint["lat_lowestmode"]
        x = floor((lon - minx) / stepx)
        y = floor((maxy - lat) / stepy)
        grid[y][x] = pd.concat([grid[y][x], footprint])
        if (i % 100000 == 0):
            print(i)

    cells = grid_cells(r, shape, polygon)

    return grid, cells


def grid_cells(r: int, shape: gpd.GeoDataFrame, polygon: int):
    ''' Encodes geospatial information for convenient plotting.'''
    geometry = shape.geometry[polygon - 1]

    minx, miny, maxx, maxy = geometry.bounds
    stepx = (maxx - minx) / r
    stepy = (maxy - miny) / r

    curx = minx
    cury = maxy

    cells = []

    for y in range(r):
        for x in range(r):
            cell = Polygon([(curx, cury), (curx + stepx, cury),
                            (curx + stepx, cury - stepy), (curx, cury - stepy)])  # noqa: E501
            cells.append(cell)
            curx += stepx
        cury -= stepy
        curx = minx

    cells = gpd.GeoDataFrame(cells, columns=["geometry"])

    return cells


def plot_raster(r: int, grid: list, cells: list, var: str, method: Callable):
    ''' 
    Generates plot of quantity var when passed grid and cells, 
    the outputs of rasterise_polygon. 

    Make sure to provide the full method, for example, pd.DataFrame.mean. 
    '''
    means = []

    for y in range(r):
        for x in range(r):
            means.append(method(grid[y][x][var]))

    cells[var] = means

    cells.plot(column=var, cmap="Greens")
