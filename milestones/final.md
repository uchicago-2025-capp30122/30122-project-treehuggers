## Affordable Housing & Green Space Equity in Chicago
### Team Members: Evan Fantozzi, Grace Kluender, Andres Felipe Camacho, Begum Akkas

### I. Data Documentation

#### Affordable Housing Data
- Downloaded CSV from: https://data.cityofchicago.org/Community-Economic-Development/Affordable-Rental-Housing-Developments-Map/k3g7-7kgc
- This data did not require any cleaning. The only minor inconvenience was that there was not a unique ID field, which we created. 

#### Yelp Review Data
- Reviews of parks and other green spaces were obtained from Yelp using the Business Search API. 
- For each place (“business”) returned, we extracted the name, average rating, number of reviews, and coordinates.  

#### Google Review Data
- Reviews of parks and other green spaces were obtained from Google using the Nearby Search API.
- Relative to Yelp, many more parks and green spaces are reviewed on Google. 
- Google only returns 60 places per search query. We searched for the top 60 parks, fields, and stadiums closest to each of the 15 locations roughly spread across the city of Chicago. 

#### OpenStreetMap Chicago Parks Data
- To extract the Chicago parks data, we utilized the OSMnx library, which is a Python package that allows you to easily download geospatial features from OpenStreetMap (OSM).
- The main challenge with this data was that many of the parks lacked names. We handled this by assigning parks without names a default name: “Unnamed Park.”
- We had to de-duplicate and clean the OSM parks data, which included reviewing parks that intersected to see if they were true duplicates. There were also 6 parks that were not marked by the cleaning process due to small coordinate discrepancies. We remove these 6 parks manually within the cleaning script.

#### U.S. Census Bureau American Community Survey Data
- We used the cenpy Python library to access U.S. Census Bureau data on median household income, race, and total population by tract
- We stored the response in a .csv and then merged it with the census tracts shapefiles

### II. Project Structure
Below is the general structure of the project.
```
.
├── README.md
├── data
│   ├── Affordable_Rental_Housing_Developments_20250201.csv
│   ├── cleaned_park_polygons.geojson
│   ├── grid_and_tracts
│   ├── housing.geojson
│   ├── housing_data_index.geojson
│   ├── review_data
│   └── uncleaned_park_polygons.geojson
├── green_spaces
│   ├── __init__.py
│   ├── __main__.py
│   ├── census_data
│   ├── housing
│   ├── index
│   ├── parks
│   ├── reviews
│   ├── tract_level_analysis
│   └── viz
├── milestones
│   ├── final.md
│   ├── milestone1.md
│   ├── milestone2.md
│   └── milestone3.md
├── notebooks
│   ├── CensusTracks.ipynb
│   ├── OSM.ipynb
│   ├── chicago_parks_kepler.html
│   ├── demo.ipynb
│   ├── kepler_config.json
│   └── kepler_config_explore.ipynb
├── pyproject.toml
├── tests
│   ├── data
│   ├── test_clean_park_polygons.py
│   ├── test_combine_reviews.py
│   ├── test_google.py
│   ├── test_index.py
│   ├── test_reviews_utils.py
│   └── test_yelp.py
└── uv.lock
```

Modules:
1. The "data" module contains all the raw and cleaned data. The raw data files can be seen in the diagram above.
2. The "green_spaces" module contains all of the files used for analysis. This includes data cleaning, processing, analysis, and visualization. Only this module needs to be run to create the dashboard.  
3. The "milestones" module contains documentation about the process of the project, which is also where this file ("final.md") is located.
4. The "notebooks" module contains files, primarily Jupyter notebook, that were used to quickly view the data. This module is for understanding only is not a part of the module that runs the project. 
5. The "tests" module contains all of the tests written for the analysis done in the "green_spaces" module. This includes testing the data cleaning process, the index creation, and combining the reviews from Google and Yelp. 

### III. Team Responsibilities

#### Begum’s responsibilities
- Loaded affordable housing data and converted to GeoJSON.
- Built index.py. This file reconciles three datasets: (1) Yelp and Google reviews, (2) OSM parks data, and (3) affordable housing data. 
    - The index finds parks that fall within walking distance (about 10-12 minutes) of each housing unit. The two indexes are:
        - “size_index”: scales each park by its area.
        - “rating_index”: scales each park by its area and average rating.
    - The indexes are normalized by the maximum value and scaled between 0 and 100. The output is a GeoJSON file of housing units with their respective indexes (“housing_data_index.geojson”).

### Grace’s responsibilities
- Extracted Chicago Parks data from OpenStreetMap utilizing the OSMnx library (https://osmnx.readthedocs.io/en/stable/), and created a GeoJSON FeatureCollection file containing uncleaned polygonal data for Chicago parks. The script that extracts and writes the GeoJSON file is titled create_parks_geojson.py. The file that this script writes is titled uncleaned_park_polygons.geojson.
- Wrote the clean_park_polygons.py script, which cleans and merges the park polygons from the uncleaned_park_polygons.geojson file and writes the cleaned data to the cleaned_park_polygons.geojson file. The script ensures that park geometries are standardized and merged when appropriate.

### Evan’s responsibilities
- Using Yelp and Google APIs, obtained average ratings for parks and other green spaces across Chicago. First performed a general search across Chicago; for Yelp this was done by using the city name in the location query. For Google, this was performed using a set of 15 coordinates spread across the city. 
- Next, conducted a second, targeted search for each of roughly 1000 unnamed parks in OpenStreetMaps data, querying their exact coordinates with a small radius. This was done exclusively in Google due to limitations with the Yelp API. 
- Finally, removed duplicate review information for each of Google and Yelp, and created GeoJSON files with the final, combined list of review information, with each coordinate buffered by a fixed number of meters.

### Andres’s responsibilities
- Extracted the census data from the cenpy API at tract level, then combined with the tracts shapefiles to merge the data and to extract socio-economic variables
- Created grid points with spacing of 200 meters all over Chicago to reconstruct the index for all the city, then collapsed those index points to an average by census tract and merged the data with the U.S. Census Bureau data.
- Created a keplergl object that maps all the data we have into a fast reactive interaction
- Created the dashboard with the landing page and the 4 specific tabs to show the data and the analysis


### IV. Final Thoughts

The goal of our project was to evaluate the accessibility of high-quality public parks and green spaces near affordable housing units in Chicago. 

We accomplished what we set out to do. We successfully reconciled affordable housing data from the city’s Department of Housing with spatial data from OpenStreetMap and the U.S. Census Bureau and user review data from Yelp and Google. This allowed us to assess both the availability and quality of green spaces near affordable housing developments and across all of Chicago. The accessibility index we created provides a meaningful way to compare different developments and identify potential disparities in access to high-quality public spaces.

By integrating multiple data sources, we provided a structured approach to evaluating green space accessibility, which can be useful for future urban planning and decision-making for those seeking to redeem affordable housing vouchers within Chicago.



