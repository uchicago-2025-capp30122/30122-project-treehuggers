# Tree Huggers

## Abstract
Our group is interested in investigating the availability of high-quality public
parks and other green public spaces near affordable housing in Chicago. The city’s Department of Housing maintains a list of affordable housing rental units, available online and updated regularly. OpenStreetMap and Google’s API contain information on locations of green spaces, and Yelp and Google’s APIs contain data on the ratings of these green spaces.

We will reconcile the city’s Department of Housing data with spatial and user review data on green spaces. For the data analysis component of this project, we will be developing an index that quantifies the accessibility to high-quality green spaces for the various public housing developments. This index will be based upon the proximity of green spaces to public housing developments as well as the quality of these green spaces, determined by ratings/reviews that we scrape
from Google and Yelp.


### Data Reconciliation Plan
All the data will be merged at the spatial unit level, using spatial relationships between the layers of information we have available. Specifically, from the points with georeferenced data, we have coordinates that can be used to spatial join them to other spatial units (counts or average distance), depending on the transformation needed. We aim to construct an index of proximity to parks to the smallest spatial unit available, depending on the data resolution. 

We will try two approaches to join the data: first, for the parks locations, we can create a map with a kernel density surface (grid cells), then we can aggregate the kernel cells over the smallest spatial units we find in the data for analysis: census blocks or neighborhood polygons, resulting in an index that maps the index for all the spatial units over the city at the block/zone level. 

Another approach is to create 500 meters - 1000 meters grids over the city to append the specific data needed by geolocation, we then will be abailable to use those grids to count points, divide them by % of area that belongs to a park, and perform spatial joins to those grids from the socioeconomic data we have to define neighborhoods composition. Any of these approach leaves us with an spatial unit of analysis that can be used to perform statistical analysis and to visualizations either for help building affordable housing around areas with public spaces - good life quality, or to prioritize locations for building infrastructure that helps communities grow stronger. 


## Data Sources

### Data Source #1: OpenStreetMap
The data is coming from an API
Rows: 870
Columns: 77
We will rely solely on this data source to identify parks in Chicago. The main hurdle of this dataset will be figuring out how we merge the nodes, ways, and relations to create our list of parks. We also have to make some decisions about our query terms in order to decide what counts as a public park. 
We will join this dataset based on latitude and longitude. 

### Data Source #2: Yelp Reviews
The data is coming from an API.
Rows: 240
Columns: 14
Things we can get from this data:
Park (business) name
Latitude and longitude 
Address
Average reviews
Number of reviews

### Data Source #3: Google Places API
The data is coming from an API.
Rows: 800
Columns: 6
We need to figure out how we will calculate walking distance to parks using this data. We will also extract park reviews and combine it with the Yelp reviews to create our index. 

### Data Source #4: Affordable Rental Housing Developments
The data is coming from a webpage. We can export the data as a CSV.
Rows: 598
Columns: 14
We do not foresee any challenges with this data.
The data includes latitudes and longitudes of all public housing in Chicago. It also includes the housing type (e.g., multifamily) and the number of units. We will link this data to all our other data sources based on latitudes and longitudes. 



## Project Plan
To be completed by the end of the assigned weeks:

Week 5: Get all data into usable formats

Grace & Andres:
Finish fetching OpenStreetMap (GK) & Google API data and cleaning (AFC). 
Define spatial unit and merge these datasets accordingly
Begin figuring out how we are going to create index items from these datasets (distance to parks, area of parks, etc.)


Evan & Begum:
Start building out the two indexes: (1) distance to park and (2) quality of park
Decide what aspects of the index we still need data for
Decide at which level we are calculating the index (e.g., block level, radius, etc.)
Index thoughts:
Decide how many reviews count in order for us to incorporate into our  model (e.g., if there is only one review maybe we should not include it)
Load Housing Data with pandas & perform any necessary cleaning (BA).


Week 6: Finish Building Index & Begin Building Prototype

Grace & Andres:
Decide on prototype tools and begin designing the prototype 
Decide on unit-size of our visualization/data analysis

Evan & Begum: 
Finalize index and start overlaying/merging data as needed to calculate index scores


Week 7: Put it all together

All of us together:
Code the index and any remaining overlays onto the prototype
Begin fleshing out our story/analysis of our data



## Questions

1. To get the OpenStreetMap data, we initially scraped the data using the OverPass API. However, we recently found access to the osmx library in Python (https://osmnx.readthedocs.io/en/stable/). Is it okay if we utilize this library, or does this invalidate the scraping requirement of the project. 
2. If we have end up having data from census tracks, but with lower spatial resolution (bigger zones) how could we split them to ‘predict’ those variables over smaller grids/zones? 
