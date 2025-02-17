import geopandas as gpd
import json
from shapely.geometry import Point
# from collections import namedtuple
from typing import NamedTuple

class ParkTuple(NamedTuple):
    point: Point

class HousingTuple(NamedTuple):
    park_count_800: int
    park_count_1500: int
    park_rating: int
    total_reviews: int

### Create BASE_DIR for the filepaths below (use pathlib)

##############################
# Load Data
##############################
# parks data
parks = gpd.read_file("test_park_data.geojson")
## import osm parks geojson file
## currently using test data for parks
## official data:
parks = gpd.read_file("../data/parks_polygons.geojson")

# housing data
housing = gpd.read_file("../data/housing.geojson")

# yelp ratings
with open("../data/yelp/yelp_cleaned.json", "r") as f:
    ratings = json.load(f)



##############################
# Create housing dictionary with index values
##############################

def match_park_ratings_point():
    """
    Match yelp and google ratings to parks.

    Args:
        polygon: polygon object of a park

    Returns: park rating if found, None otherwise
    """
    for polygon in parks.geometry:
        for park in ratings:
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


def park_walking_distance(distance_m, house_point):
    # set buffer around housing unit
    buffer_800m = house_point.buffer(distance_m) 

    park_count = 0
    # think about ways to optimize so that you don't check every park in chicago
    for polygon in parks.geometry:
        if buffer_800m.intersects(polygon):
            park_count += 1

    return park_count


def create_index_values(housing, parks):
    """_summary_

    Args:
        housing (geopandas dataframe): affordable housing data
        parks (geopandas dataframe): parks data
    """
    housing_dict = {}

    for point in housing.geometry: # geometry accesses Point object
        count_800 = park_walking_distance(point, 800) # 800 meters roughly 10 min walking distance
        count_1500 = park_walking_distance(point, 1500)

        rating = match_park_ratings_point()
        if rating is None:
            # call function to fuzzy match on park name & update rating value
            rating = match_park_ratings_name() # update rating with fuzzy matched park name

        house_tuple = HousingTuple(park_count_800=count_800, park_rating=rating)
        housing_dict[point] = house_tuple # should we give each unit an ID other than the point?

    return housing_dict

            
 
 
##############################
# Calculate indexes for each unit
##############################
    
# loop through dictionary and create new dictionary with index values (maybe another namedtuple?)

