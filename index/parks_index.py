import geopandas as gpd
import json
from shapely.geometry import Point
from collections import namedtuple


##############################
# Load Data
##############################
# parks data
parks = gpd.read_file("test_park_data.geojson")
## import osm parks geojson file
## currently using test data for parks

# housing data
housing = gpd.read_file("../data/housing.geojson")

# yelp ratings
with open("../data/yelp/yelp_cleaned.json", "r") as f:
    yelp_ratings = json.load(f)



##############################
# Create housing dictionary with index values
##############################

def match_park_ratings_point(polygon):
    """
    Match yelp ratings to parks.

    Args:
        polygon: polygon object of a park

    Returns: park rating if found, None otherwise
    """
    for park in yelp_ratings:
        rating_point = Point(park["longitude"], park["latitude"])
        
        if polygon.contains(rating_point):
            rating = park["rating"]
        else:
            rating = None 
            
    # consider removing the park from yelp_ratings after rating is found to optimize efficiency
    # may need to think about if multiple polygons will match to the same rating
    
    return rating
        

def match_park_ratings_name(polygon):
    # fuzzy match parks without ratings on name
    pass



def create_index_values(housing, parks):
    """_summary_

    Args:
        housing (geopandas dataframe): affordable housing data
        parks (geopandas dataframe): parks data
    """
    housing_dict = {}
    # maybe we should've done this within a class? 
    housing_tuple = namedtuple('housing_values', ['park_count_800', 'park_rating'])
    
    for point in housing.geometry: # geometry accesses Point object
        buffer_800m = point.buffer(800) # 800 meters roughly 10 min walking distance
        # we can move the buffer to a helper if needed 
        # will add 1-2 more buffers
        
        park_count = 0
        # think about ways to optimize so that you don't check every park in chicago
        for polygon in parks.geometry:
            if buffer_800m.intersects(polygon):
                park_count += 1
               
            rating = match_park_ratings_point(polygon)
            if rating is None:
                # call function to fuzzy match on park name & update rating value
                rating = match_park_ratings_name(polygon) # update rating with fuzzy matched park name

        house_values = housing_tuple(park_count_800=park_count, park_rating=rating)
        housing_dict[point] = house_values # should we give each unit an ID other than the point?

    return housing_dict

            
 
 
##############################
# Calculate indexes for each unit
##############################
    

