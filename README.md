# Assessing the Impact of Droughts on Tropical Forests using GEDI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Requirements
- Python 3.9+

## Data availability
This project uses the following data sources:

| Data source                                           | Availability                                                                  | Sensors                                     | Data                | Date range      | No. observations (used) |
|-------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------|---------------------|-----------------|-------------------------|
| GEDI Level 2B (v002)                                  | [public](https://lpdaac.usgs.gov/products/gedi02_bv002/)                      | Space-borne LiDAR                           | Full-waveform LiDAR | 2019-2020       | 16 Mio.                |
| CHIRPS Daily: Climate Hazards Group InfraRed Precipitation With Station Data | [Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY)                       | Space-borne multispectral imagery & weather stations | Precipitation    | 2001-2023 | -                       |  
| MODIS MOD11A1.061 Terra Land Surface Temperature and Emissivity Daily Global 1km | [Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A1)                       | Space-borne multispectral imagery | Temperature    | 2001-2023  | -                       |
| MODIS MOD15A2H.061: Terra Leaf Area Index/FPAR 8-Day Global 500m | [Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD15A2H)                       | Space-borne multispectral imagery |  Photosynthetically Active Radiation (FPAR)    | 2001-2023  | -                       |
| MODIS MOD16A2.006: Terra Net Evapotranspiration 8-Day Global 500m | [Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD16A2)                       | Space-borne multispectral imagery | Evapotranspiration (ET) and Potential Evapotranspiration (PET)   | 2001-2023  | -                       |
| ERA5-Land Monthly Averaged by Hour of Day - ECMWF Climate Reanalysis | [Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY_BY_HOUR)                       | Space-borne multispectral imagery | Surface Net Solar Radiation    | 2001-2023  | -                       |

## Project Organization
```
├── LICENSE
├── Makefile           <- Makefile with commands like `make init` or `make test_environment`
├── README.md          <- The top-level README for developers using this project.
|
├── notebooks          <- Jupyter notebooks.
│   ├── exploratory    <- Notebooks for initial exploration. This is where all of our notebooks currently reside.
│
│
├── requirements.txt   <- File containing all the required python packages. Use pip install -r requirements.txt to install them.
│
├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
├── data               <- Directory that contains all of our intermediate data. Does not contain large data like GEDI. Mostly has monthly data aggregates.
├── reports/figures    <- Directory that contains our results as figures.
└── drought            <- Source code for use in this project.
   ├── __init__.py    <- Makes drought a Python module
   │
   ├── data           <- Functions to download, process and analyze data.
   │
   └── visualization  <- Functions to plot and visualize data.
```


<b> Overview </b>

The sustained functioning of forest ecosystems is critical to achieving global climate and biodiversity goals but the resilience of forests to the intensifying threat of climate change is poorly understood. In particular, severe droughts such as those experienced across Amazonia in 2005, 2010 & 2016 may well have killed millions of trees, with drought increasing the risk of mortality for tree species adapted to wet conditions. Forests that experience periods of low rainfall, such as seasonally dry tropical forests, are well adapted to these conditions with a greater occurrence of deciduousness and shorter canopy, however similar adaptions are debated in moist tropical forests. 
Traditional optical remote sensing techniques detect changes in canopy greenness via Leaf Area Index (LAI) and Normalized Difference Vegetation Indices (NDVI), but these may be affected by optical artifacts and do not pick up reliable signals of canopy height and structure. GEDI, a space-borne lidar instrument, fills that gap with billions of forest structure measurements taken from the International Space Station. 

<b> Goals </b>

In this project, we will first use GEDI data to examine forest structural differences across longstanding climatic and seasonal water gradients in the Amazon basin. We will build on these results to evaluate the resilience of differently adapted forests to anomalous drought conditions. If there is time, we will have the opportunity to investigate other factors that mediate forest resilience, including proximity to roads and rivers and other environmental conditions. 

<b> Directory Structure </b>

All the core code for the project resides in the drought folder, with any data that is accessed being stored in the data folder. Important figures and results can be found in the reports folder. 
