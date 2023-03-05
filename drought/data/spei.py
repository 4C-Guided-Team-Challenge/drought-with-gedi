# %%
import xarray as xr
import rioxarray as rio # noqa
import matplotlib.pyplot as plt
import numpy as np
import rasterio

PATH_FILE = '/maps-priv/maps/drought-with-gedi/spei_data/spei'

SAVE_DIRECTORY = '/maps-priv/maps/drought-with-gedi/spei_data/'


def create_spei_geotiff(spei_window: int,
                        open_dir: str = PATH_FILE,
                        save_dir: str = SAVE_DIRECTORY,
                        start_date: str = '01-01-2000',
                        end_date: str = '01-01-2021'):
    """
    Opens the SPEI nc file and create a series of aggregated metrics
    for a time period. Save the results into a geotiff file.
    """
    if open_dir == PATH_FILE:
        SPEI_PATH = open_dir + str(spei_window) + '.nc'
    ds_spei = xr.open_dataset(SPEI_PATH)
    spei = ds_spei.sel(time=slice(start_date, end_date))
    spei_array = spei['spei'].values

    extreme_drought = np.count_nonzero((-2 >= spei_array), axis=0)

    severe_drought = np.count_nonzero((-1.5 >= spei_array) &
                                      (spei_array > -2), axis=0)

    moderate_drought = np.count_nonzero((-1 >= spei_array) &
                                        (spei_array > -1.5), axis=0)

    near_normal = np.count_nonzero((1 > spei_array) &
                                   (spei_array > -1), axis=0)

    moderate_wet = np.count_nonzero((1.5 > spei_array) &
                                    (spei_array >= 1), axis=0)

    severe_wet = np.count_nonzero((2 > spei_array) &
                                  (spei_array >= 1.5), axis=0)

    extreme_wet = np.count_nonzero((2 <= spei_array), axis=0)

    height = 360
    width = 720
    x_resolution = 0.5
    y_resolution = 0.5
    left, top = -179.75, 89.75
    transform = rasterio.transform.from_bounds(left, top,
                                               x_resolution, y_resolution,
                                               width=width, height=height)
    dtype = np.float64
    crs = 'EPSG:4326'
    count = 7

    GEOTIFF_NAME = save_dir + 'reduced_spei' + str(spei_window) + '.tif'

    with rasterio.open(GEOTIFF_NAME, 'w', driver='GTiff',
                       width=width, height=height, count=count,
                       dtype=dtype, crs=crs, transform=transform) as dst:

        dst.write(extreme_drought, 1)
        dst.write(severe_drought, 2)
        dst.write(moderate_drought, 3)
        dst.write(near_normal, 4)
        dst.write(moderate_wet, 5)
        dst.write(severe_wet, 6)
        dst.write(extreme_wet, 7)

# %%


ds = xr.open_dataset(PATH_FILE)

'''for dim in ds.dims.values():
    print(dim)

for var in ds.variables.values():
    print(var)'''

lat = ds['lat']
lon = ds.variables['lon'][:]
time = ds.variables['time'][:]
spei = ds.sel(time=slice('01-01-2000', '01-01-2021'))

spei_array = spei['spei'].values

mean_spei = np.mean(spei_array, axis=0)

median_spei = np.median(spei_array, axis=0)

sum_spei = np.sum(spei_array, axis=0)

std_spei = np.std(spei_array, axis=0)

count_negative_spei = np.count_nonzero((1 < spei_array) &
                                       (spei_array <= 2), axis=0)

extreme_drought = np.count_nonzero((-2 >= spei_array), axis=0)

severe_drought = np.count_nonzero((-1.5 >= spei_array) &
                                  (spei_array > -2), axis=0)

moderate_drought = np.count_nonzero((-1 >= spei_array) &
                                    (spei_array > -1.5), axis=0)

near_normal = np.count_nonzero((1 > spei_array) &
                               (spei_array > -1), axis=0)

moderate_wet = np.count_nonzero((1.5 > spei_array) &
                                (spei_array >= 1), axis=0)

severe_wet = np.count_nonzero((2 > spei_array) &
                              (spei_array >= 1.5), axis=0)

extreme_wet = np.count_nonzero((2 <= spei_array), axis=0)

arr_with_nans = np.where(count_negative_spei == 0, np.nan, count_negative_spei)

lons, lats = np.meshgrid(lon, lat)
# %%
height = 360
width = 720
x_resolution = 0.5  # Example pixel size in x direction: 1 degree
y_resolution = 0.5  # Example pixel size in y direction: 1 degree
left, top = -179.75, 89.75  # Example coordinates of upper-left corner
transform = rio.transform.from_bounds(left, top,
                                      x_resolution, y_resolution,
                                      width=width, height=height)
dtype = np.float64
crs = 'EPSG:4326'
count = 5
data = np.random.randint(0, 255, size=(height, width), dtype=np.int64)


with rasterio.open('/home/fnb25/Testes/teste.tif', 'w', driver='GTiff',
                   width=width, height=height, count=count,
                   dtype=dtype, crs=crs, transform=transform) as dst:
    dst.write(data, 4)


# %%
raster = spei.rio.set_spatial_dims(x_dim='lon', y_dim='lat')


print(spei.rio.crs)

spei.rio.write_crs("epsg:4326", inplace=True)

print(spei.rio.crs)

# spei.rio.to_raster(r"/home/fnb25/Testes/test.tiff")


# %%
plt.contourf(lons, lats, near_normal, cmap='viridis')
plt.colorbar()
plt.show()

# %%
