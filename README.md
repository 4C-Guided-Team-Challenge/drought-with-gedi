# Assessing the Impact of Droughts on Tropical Forests using GEDI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Requirements
- Python 3.9+

## Project Summary

Tropical forests are critical elements of the biosphere, but face unprecedented threats in the face of deforestation and climate change. These potential threats include wavering trends in precipitation and water availability, the effects of which are yet to be clearly established. Recent advances in remote sensing technology, particularly the launch of the Global Ecosystem Dynamics Instrument (GEDI), allow us to evaluate the relationship between forest structure and drought conditions, including the GEDI-derived Plant and a range of climate variables such as precipitation, radiation, and temperature. We compare the response of PAI to precipitation across regions, run seasonality analyses, and study the impacts of anomalous drought. We hope that our study will provide valuable insights into the resilience of tropical forests facing drought, aiding conservation efforts to mitigate the impact of climate change on these vital ecosystems. 

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
| TerraClimate: Monthly Climate and Climatic Water Balance for Global Terrestrial Surfaces, University of Idaho | [Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE)                       | Space-borne multispectral imagery | Palmer Drought Index    | 2001-2023  | -                       |


**Note on data access**: In general, the data used in this project can be divided into three categories:
* Aggregated data (for example monthly means for climate and GEDI) - stored on Github in `data/interim` folder.
* Earth Engine non-aggregated climate data - requires [Earth Engine authentication and initialization](https://developers.google.com/earth-engine/guides/auth). The code should be able to download the necessary data upon execution.
* GEDI footprints - we worked with more than 16 million raw GEDI footprints, and that data is too large to be saved here on GitHub. To obtain the data, we recommend following the instructions specified in this repo: https://github.com/ameliaholcomb/biomass-recovery/blob/main/README.md#data-download-and-setup or just working with NASA download directly.


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

## General Project Guide

The project report containing all the background information and the summary of the analysis performed can be found at `reports/gtc2023_forest_dynamics.pdf`.

### Navigating the code

We outline a brief guide on how to navigate the codebase, focusing on the notebooks:

* Data fetching, filtering and aggregating:
  * Climate data - `notebooks/exploratory/ClimateData.ipynb`
  * GEDI data - `notebooks/exploratory/GEDIDataAnalytics.ipynb`
* Water availability and drought analyses:
  * Seasonality  - `notebooks/exploratory/SeasonalAnalysis.ipynb`
  * SPEI Calculation for each region - `notebooks/exploratory/CalculateSPEI.ipynb`
  * Vegetation and climate variations across all regions - `notebooks/exploratory/AcrossPrecipitationGradient.ipynb`
  * Polygon 2 drought analysis, including vertical PAI variations - `notebooks/exploratory/Polygon2Analysis.ipynb`
  * Palmer Drought indeces and regression analysis - `notebooks/exploratory/EcosystemClustering.ipynb`


