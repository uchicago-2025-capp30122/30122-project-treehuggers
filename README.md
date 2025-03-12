# Affordable Housing and Green Space Equity in Chicago
Grace Kluender, Evan Fantozzi, Begum Akkas, Andrés Felipe Camacho

## Abstract
Public parks and green spaces bring communities together, offering places for recreation, social interaction, and personal well-being. Policymakers and urban planners have a critical responsibility to ensure equitable access to high-quality green spaces for residents of affordable housing. This project evaluates the accessibility of high-quality public parks and green spaces near affordable housing units in Chicago, relative to other areas within the city.

By integrating housing data and census tract data with spatial and ratings data on Chicago green spaces, we develop an Accessibility Index that quantifies access to high-quality green spaces. This index considers key factors such as park ratings, size, and proximity to affordable housing developments and census tracts, highlighting disparities in green space accessibility across the city. To make these insights more accessible, we create an interactive dashboard that visualizes the index, allowing users to explore the data and identify areas with limited green space access.

This project offers policymakers and urban planners with a data-driven tool to identify areas where access to high-quality green spaces is limited, particularly for residents of affordable housing.

## Visualization

[▶️ Click here to watch the project video](https://www.youtube.com/watch?v=jTMRUfCFJLQ)

<img src= "./green_spaces/viz/Project_Viz.png" alt="Chicago Parks Visualization" width="500"/>


## Instructions for Running Project

To properly run this project, please follow these steps: 

1) Clone the repository

``` 
git clone https://github.com/uchicago-2025-capp30122/30122-project-treehuggers.git
```

2) Syncronize the libraries needed using ```uv```. This will install all the dependencies needed to run the code in the proyect

```
uv sync
```

3) (Optional) if there is a problem installing the dependency kepler, try this code that runs the project on a previuos version of python: 

```
deactivate #in case the virtual environment is active
rm -rf .venv
uv venv --python=python3.12
source .venv/bin/activate
uv sync
```

4) (Optional) To recreate the files used in the dashboard, you can run: 
```
uv run python green_spaces 
```

5) After reviewing the data is complete, you can run the following to visualize the data. 
   Open the link that is generated, and that will take you to the interactive dashboard.

```
uv run green_spaces/viz/dash_housing_capp.py
```

6) To run all tests associated with the analysis, you can run:

```
uv run pytest tests/
```


# Data Source Citations

Below are the data sources used for the project. We focus heavily on spatial
data to achieve a visualization of the affordable housing index.

1) OpenStreetMap Chicago Parks Data: The first set of data comes from OpenStreetMap, which is a free, open map
database: https://www.openstreetmap.org/#map=5/38.01/-95.84

    To extract coordinate data on Chicago green spaces and parks, we utilized the 
    OSMnx API for Python (https://wiki.openstreetmap.org/wiki/OSMnx). 

2) Affordable Rental Housing Developments Data: downloaded CSV from city of Chicago's data portal: https://data.cityofchicago.org/Community-Economic-Development/Affordable-Rental-Housing-Developments-Map/k3g7-7kgc 

3) Yelp API Review Data: Used Yelps's Business Search API: https://docs.developer.yelp.com/reference/v3_business_search 

4) Google Places API Review Data: Used Google's Nearby Search API: https://developers.google.com/maps/documentation/places/web-service/search-nearby 

5) U.S. Census Bureau American Community Survey Data: used ACS API to pull census tracts: https://www.census.gov/data/developers/data-sets.html 



