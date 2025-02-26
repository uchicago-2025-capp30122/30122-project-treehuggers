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
    park_count: int # consider also scaling this by park size or adding another index
    rating_index: float



### Create BASE_DIR for the filepaths below (use pathlib)

##############################
# Load Data -- might want to make these into functions 
##############################
# load parks data
parks = gpd.read_file("data/park_polygons.geojson")

# housing data
housing = gpd.read_file("data/housing.geojson")

# # yelp and google ratings
with open("data/yelp/yelp_cleaned.json", "r") as f:
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
    avg_rating = 0
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
        total_reviews = None  # No ratings found
    else:
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
        
        if polygon.intersects(review_point):
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
            # print("SIM SCORE ABOVE THRESHOLD:", row["name"], park_name)
            matching_rows.append(row)
    
    park_tuple = calculate_park_rating(matching_rows, polygon)
        
    return park_tuple


def create_parks_dict(parks):
    """_summary_

    Returns:
        _type_: _description_
    """
    parks_dict = defaultdict(int)
    
    # buffer the polygon to test match rate
    # to check current CRS: print(parks.crs) # (should be EPSG: 4326)
    # convert to a matric CRS (EPSG to meters)
    # parks = parks.to_crs(epsg=3857)
    # # apply buffer in meters
    # parks["buffered_polygon"] = parks.geometry.buffer(200)
    # # convert back to lat/long
    # parks = parks.to_crs(epsg=4236)
    
    parks_without_names = 0 # FOR DEBUGGING; DELETE LATER

    for _, park in parks.iterrows():
        polygon = park.geometry
        park_name = park["name"]
        
        ##### FOR DEBUGGING PURPOSES##############################
        if park_name is None:
            parks_without_names += 1
        ############################################################
        
        park_tuple = match_park_ratings_point(polygon)
        
        # if reviews not found from point, use park name to match
        if park_tuple.total_reviews is None and park_name is not None:
            park_tuple = match_park_ratings_name(park_name, polygon)
        
        parks_dict[park["id"]] = park_tuple
        
    #######################################################
    ##### FOR DEBUGGING PURPOSES
    none_count = 0
    populated_count = 0
    
    for key, value in parks_dict.items():
        if value.total_reviews is None:
            none_count += 1
        else:
            populated_count += 1
                  
    print("parks with ratings:", populated_count)
    print("parks withOUT ratings:", none_count)
    
    print("total nameless parks:", parks_without_names)
    #######################################################
    
    return parks_dict


######## Self note:
### write a test to see if any polygons are not in the final parks dictionary
### another test idea is to confirm the data type is converted to meters then 
# back to lat/long when creating the buffer around housing units
### test to see how many parks a review is matched to 

##############################
# Create housing dictionary with index values
##############################
def create_buffer(housing, distance):
    # convert to a metric CRS for buffering in meters
    housing_project = housing.to_crs(epsg=3857)
    
    # apply buffer to all points in housing data
    housing_project["geometry"] = housing_project.geometry.buffer(distance)
    
    # convert back to EPSG: 4326 in order to compare to polygon object
    housing_project = housing_project.to_crs(epsg=4326)
    # print("housing CRS after buffer created:", housing.crs)
    
    return housing_project
    

def park_walking_distance(buffered_point, parks_data):
    # set buffer around housing unit
    # buffer_800m = house_point.buffer(distance) 
    polygon_id_list = []
    park_count = 0
    
    # parks = parks.to_crs(epsg=3857)
    # buffered_point = gpd.GeoSeries([buffered_point], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
    # print("parks CRS:", parks.crs) # its in EPSG: 4326
    
    # think about ways to optimize so that you don't check every park in chicago
    for _, park in parks_data.iterrows():
        polygon = park.geometry 
        polygon_id = park["id"]
        # print("walking distance function:", polygon)
        # we can also loop through parks dictionary instead to only consider parks with reviews?
        if buffered_point.intersects(polygon):
            park_count += 1
            polygon_id_list.append(polygon_id)

    return (park_count, polygon_id_list)


def calculate_index(polygon_list, parks_dict):
    size_rating_index = 0
    
    for poly_id in polygon_list:
        park_tuple = parks_dict[poly_id]
        size_rating_index = park_tuple.rating
        size_rating_index += (park_tuple.area * park_tuple.rating)
        
    return size_rating_index


def create_house_tuple(buffered_point, parks_dict, parks_data):
    """_summary_

    Args:
        housing (geopandas dataframe): affordable housing data
        parks (geopandas dataframe): parks data
    """
    parks_buffer_count, polygon_id_list = park_walking_distance(buffered_point, parks_data) 
    # for distance (meters): 800 meters roughly 10 min walking distance

    # check that polygon_list is not empty before proceeding
    if len(polygon_id_list) == 0:
        house_tuple = HousingTuple(park_count=0, rating_index=0) 
    else:
        # gather park tuples that fall within radius
        index = calculate_index(polygon_id_list, parks_dict)
        house_tuple = HousingTuple(park_count=parks_buffer_count, rating_index=index)

    return house_tuple



##############################
# Create index values dictionary
##############################

def create_housing_dict(housing, parks_dict, distance, parks_data):
    ## Currently calling this function would create separate dictionaries for each distance/radius
    ## should we change function to create one dictionary where the values are a list of house tuples?
    housing_dict = {}
    
    # apply buffer to entire GeoDataFrame
    housing_project = create_buffer(housing, distance)
    # print("buffered point", housing["buffered_point"])
    # print("housing point:", housing.geometry)
    
    house_id = 1
    for buffered_point in housing_project["geometry"]:
        house_tuple = create_house_tuple(buffered_point, parks_dict, parks_data)
        
        # convert house coordinates to tuple to use as key in dictionary
        # house_id = str(housing_project["X Coordinate"])+str(housing_project["X Coordinate"])
        housing_dict[house_id] = house_tuple 
        house_id += 1
        
    return housing_dict

            