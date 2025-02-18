import geopandas as gpd
import json
from shapely.geometry import Point, Polygon
from typing import NamedTuple
from collections import defaultdict
from jellyfish import jaro_winkler_similarity


class ParkTuple(NamedTuple):
    park_polygon: Polygon
    name: str
    rating: float
    total_reviews: int
    area: float

class HousingTuple(NamedTuple):
    park_count: int
    park_index: float


### Create BASE_DIR for the filepaths below (use pathlib)

##############################
# Load Data -- might want to make these into functions 
##############################
# parks data
# parks = gpd.read_file("test_park_data.geojson")

## import osm parks geojson file
## currently using test data for parks
## official data:
parks = gpd.read_file("../data/parks_polygons.geojson")

# housing data
housing = gpd.read_file("../data/housing.geojson")

# yelp and google ratings
with open("../data/yelp/yelp_cleaned.json", "r") as f:
    ratings = json.load(f)


##############################
# Create park tuples
##############################

def calculate_park_rating(matching_rows, polygon):
    """
    Calculate park rating and return a ParkTuple. Aggregate ratings if more than 1.

    Args:
        matching_rows (list of dicts): List of rating rows that match the park.
        polygon: Polygon object of the park.

    Returns:
        ParkTuple with calculated rating, or None if no ratings are found.
    """
    total_reviews = 0
    cumulative_rating = 0
    park_name = None

    for row in matching_rows:
        rating = row["rating"]
        review_count = row["review_count"]
        name = row["name"]

        # Accumulate ratings and reviews
        total_reviews += review_count
        cumulative_rating += rating * review_count
        park_name = name  # Last matched name (assuming one park per polygon)

    if total_reviews == 0:
        return None  # No ratings found

    # Compute average rating
    avg_rating = cumulative_rating / total_reviews

    return ParkTuple(park_polygon=polygon, name=park_name, 
                     rating=avg_rating, total_reviews=total_reviews, area=polygon.area)


def match_park_ratings_point(polygon):
    """
    Match Yelp and Google ratings to parks based on location.

    Args:
        polygon: Polygon object of a park.

    Returns:
        ParkTuple if found, None otherwise.
    """
    matching_rows = []
    
    for row in ratings:
        review_point = Point(row["longitude"], row["latitude"])
        
        if polygon.contains(review_point):
            matching_rows.append(row)
    
    park_tuple = calculate_park_rating(matching_rows, polygon)
        
    return park_tuple


def match_park_ratings_name(park_name, polygon):
    """
    Match Yelp and Google ratings to parks based on name similarity.

    Args:
        park_name (str): Name of the park.
        polygon: Polygon object of the park.

    Returns:
        ParkTuple if found, None otherwise.
    """
    matching_rows = []
    
    for row in ratings:
        sim_score = jaro_winkler_similarity(row["name"], park_name)
        
        if sim_score > 0.9:
            matching_rows.append(row)
    
    park_tuple = calculate_park_rating(matching_rows, polygon)
        
    return park_tuple



def create_parks_dict():
    """_summary_

    Returns:
        _type_: _description_
    """
    parks_dict = defaultdict(int)
    
    for _, park in parks:
        polygon = park.geometry
        park_name = park["name"]
        park_tuple = match_park_ratings_point(polygon)
        
        # if reviews not found from point, use park name to match
        if park_tuple.total_reviews is None:
            park_tuple = match_park_ratings_name(park_name, polygon)
        
        parks_dict[polygon] = park_tuple
    
    return parks_dict


######## Self note:
### write a test to see if any polygons are not in the final parks dictionary


##############################
# Create housing dictionary with index values
##############################


def park_walking_distance(house_point, distance):
    # set buffer around housing unit
    buffer_800m = house_point.buffer(distance) 
    polygon_list = []
    park_count = 0
    
    # think about ways to optimize so that you don't check every park in chicago
    for polygon in parks.geometry:
        # we can also loop through parks dictionary instead to only consider parks with reviews?
        if buffer_800m.intersects(polygon):
            park_count += 1
            polygon_list.append(polygon)

    return (park_count, polygon_list)


def calculate_index(polygon_list, parks_dict):
    size_rating_index = 0
    
    for polygon in polygon_list:
        park_tuple = parks_dict[polygon]
        size_rating_index += (park_tuple.area * park_tuple.rating)
        
    return size_rating_index


def create_house_tuple(point, parks_dict, distance):
    """_summary_

    Args:
        housing (geopandas dataframe): affordable housing data
        parks (geopandas dataframe): parks data
    """
    parks_buffer_count, polygon_list = park_walking_distance(point, distance) 
    # for distance (meters): 800 meters roughly 10 min walking distance

    # gather park tuples that fall within radius
    index = calculate_index(polygon_list, parks_dict)
    
    house_tuple = HousingTuple(park_count=parks_buffer_count, park_index=index)
    # housing_dict[point] = house_tuple 

    return house_tuple



##############################
# Create index values dictionary
##############################

def create_index_values(housing, parks_dict, distance):
    ## Currently calling this function would create separate dictionaries for each distance/radius
    ## should we change function to create one dictionary where the values are a list of house tuples?
    housing_dict = {}
    
    for point in housing.geometry: # geometry accesses Point object
        house_tuple = create_house_tuple(point, parks_dict, distance)
        
        housing_dict[point] = house_tuple 
        
    return housing_dict

            