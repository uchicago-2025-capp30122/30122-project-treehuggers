# Green Space Accessibility for Affordable Housing Buildings in Chicago
Authors: Begum Akkas, Andrés Camacho, Evan Fantozzi, Grace Kluender

## Abstract
Public parks and green spaces are vital to community well-being, providing spaces for recreation, social connection, and mental health. Ensuring equitable access to high-quality green spaces is a key responsibility for urban planners and policymakers—especially for residents of affordable housing.

This project analyzes disparities in access to high-quality public parks near affordable housing buildings in Chicago. By combining housing and census tract data with spatial and ratings data on city green spaces, we develop an Accessibility Index that quantifies access based on park ratings, size, and proximity. The index reveals patterns of inequity in green space access across neighborhoods.

To make these insights actionable, we’ve built an interactive dashboard that visualizes the Accessibility Index, enabling users to explore the data and pinpoint areas with limited access to quality parks. This tool empowers planners and decision-makers with a data-driven approach to promoting more equitable urban green space planning.

## Visualization

<img src="./green_spaces/viz/assets/ProjectDemo.gif" alt="Demo" width="98%" />

[▶️ Click here to watch the whole project video](https://www.youtube.com/watch?v=jTMRUfCFJLQ)


## Instructions for Running the Project

To execute this project, please follow these steps: 

1) Clone the repository.

``` 
git clone https://github.com/uchicago-2025-capp30122/30122-project-treehuggers.git
```

2) Synchronize the libraries needed using ```uv```. This will install all the dependencies needed to run the code in the project.

```
uv sync
```

3) (Optional) If there is a problem installing the dependency Kepler, try this code that runs the project on a previous version of Python (3.12): 

```
deactivate #in case the virtual environment is active
rm -rf .venv
uv venv --python=python3.12
source .venv/bin/activate
uv sync
```

4) (Optional) To recreate the files used in the dashboard, run the code below. The review and parks data were cached on February 2025.

```
uv run python green_spaces 
```

5) After reviewing the data for completeness, you can run the following to visualize the data. Copy the url that is generated in the terminal and paste into a browser. This will take you to the interactive dashboard.

```
uv run green_spaces/viz/dash_housing_capp.py
```

6) To run all tests associated with the analysis, run:

```
uv run pytest tests/
```


## Data Source Citations

Below are the data sources used for the project. We focus heavily on spatial
data to achieve a visualization of the affordable housing index.

1) OpenStreetMap Chicago Parks Data: The first set of data comes from OpenStreetMap, which is a free, open map
database: https://www.openstreetmap.org/#map=5/38.01/-95.84

    To extract coordinate data on Chicago green spaces and parks, we utilized the 
    OSMnx API for Python: (https://wiki.openstreetmap.org/wiki/OSMnx). 

2) Affordable Rental Housing Developments Data: downloaded CSV from city of Chicago's data portal: https://data.cityofchicago.org/Community-Economic-Development/Affordable-Rental-Housing-Developments-Map/k3g7-7kgc 

3) Yelp API Review Data: Used Yelp's Business Search API: https://docs.developer.yelp.com/reference/v3_business_search 

4) Google Places API Review Data: Used Google's Nearby Search API: https://developers.google.com/maps/documentation/places/web-service/search-nearby 

5) U.S. Census Bureau American Community Survey Data: used ACS API to pull census tracts: https://www.census.gov/data/developers/data-sets.html 



