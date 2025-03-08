## Project Tree Huggers
### Team Members: Evan Fantozzi, Grace Kluender, Andres Felipe Camacho, Begum Akkas

### I. Data Documentation

#### Affordable Housing Data
- Downloaded CSV from: https://data.cityofchicago.org/Community-Economic-Development/Affordable-Rental-Housing-Developments-Map/k3g7-7kgc
- This data did not require any cleaning. The only minor inconvenience was that there was not a unique ID field, which we created. 

#### Yelp Review Data
- Reviews of parks and other green spaces were obtained from Yelp using the Business Search API. 
- We searched for the highest rated 240 parks (API limit) in the city of Chicago. We also searched for the top 240 dog parks, playgrounds, and community gardens in Chicago. Each of these categories were derived from the official Yelp business category list.
- For each place (“business”) returned, we extracted the name, average rating, number of reviews, and coordinates.  

#### Google Review Data
- Reviews of parks and other green spaces were obtained from Google using the Nearby Search API.
- Relative to Yelp, many more parks and green spaces are reviewed on Google. 
- Google only returns 60 places per search query. We searched for the top 60 parks, fields, and stadiums closest to each of the 15 locations roughly spread across the city of Chicago. These search terms were determined via several iterations of query testing and reviewing the types of places returned.

#### OpenStreetMap Chicago Parks Data
- To extract the Chicago parks data, we utilized the OSMnx library, which is a Python package that allows you to easily download geospatial features from OpenStreetMap (OSM).
- The main challenge with this data was that many of the parks lacked names. We handled this by assigning parks without names a default name: “Unnamed Park.”
- We had to de-duplicate and clean the OSM parks data, which included reviewing parks that intersected to see if they were true duplicates. There were also 6 parks that were not marked by the cleaning process due to small coordinate discrepancies. We remove these 6 parks manually within the cleaning script.

#### U.S. Census Bureau American Community Survey Data


### II. Project Structure


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
- Using Yelp and Google APIs, obtained average ratings for parks and other green spaces across Chicago. First performed a general search across Chicago; for Yelp this was done by using the city name in the location query. For Google, this was performed using a set of 15 coordinates spread across the city. Next, conducted a second, targeted search for each of roughly 1000 unnamed parks OpenStreetMaps data, querying their exact coordinates with a small radius. This was done exclusively in Google due to limitations with the Yelp API. Finally, removed duplicate review information for each of Google and Yelp, and created GeoJSON files with the final, combined list of review information, with each coordinate buffered by a fixed number of meters.
- To assist with these searches, developed an import_utils.py script that provides the global CHICAGO_LOCATIONS consisting of 15 coordinates roughly spread across the city of Chicago.
- The combine_reviews function loads in each of the files saved in the previous step, and removes duplicates by iterating through each place in the file and adding it to a set.
- The buffer_places function loads in the list of unique places from the previous step and creates a GeoJSON file, buffering the point in each place by the specified number of meters. 
- The responses are cached in the "cache" folder. 


### Andres’s responsibilities



### IV. Final Thoughts

The goal of our project was to evaluate the accessibility of high-quality public parks and green spaces near affordable housing units in Chicago. 

We accomplished what we set out to do. We successfully reconciled affordable housing data from the city’s Department of Housing with spatial data from OpenStreetMap and the U.S. Census Bureau and user review data from Yelp and Google. This allowed us to assess both the availability and quality of green spaces near affordable housing developments and across all of Chicago. The accessibility index we created provides a meaningful way to compare different developments and identify potential disparities in access to high-quality public spaces.

By integrating multiple data sources, we provided a structured approach to evaluating green space accessibility, which can be useful for future urban planning and decision-making for those seeking to redeem affordable housing vouchers within Chicago.



