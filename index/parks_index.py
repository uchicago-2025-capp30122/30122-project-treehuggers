import geopandas as gpd
import json
from shapely.geometry import Point, Polygon
from typing import NamedTuple
from collections import defaultdict


class ParkTuple(NamedTuple):
    park_polygon: Polygon
    name: str
    rating: int
    total_reviews: int
    area: int

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
# Create park tuples
##############################


def match_park_ratings_point(polygon):
    """
    Match yelp and google ratings to parks.

    Args:
        polygon: polygon object of a park

    Returns: park rating if found, None otherwise
    """
    # parks_dict = defaultdict(int)
    
    # for polygon in parks.geometry:
    # single_park_dict = defaultdict(int)
    
    # for row in ratings:
    #     # create rating points
    #     rating_point = Point(row["longitude"], row["latitude"])
        
    #     # check if polygon contains rating point
    #     if polygon.contains(rating_point):
    #         rating = rating["rating"]
    #         review_count = rating["review_count"]
    #         name = rating["name"]
            
    #         # check if that polygon already has a review
    #         if polygon in single_park_dict:
    #             prev_rating = single_park_dict[polygon][1]
    #             prev_review_count = single_park_dict[polygon][2]
                
    #             #re-calculate average rating based on new review found
    #             total_reviews = review_count+prev_review_count
    #             new_rating = ((rating*review_count)+(prev_rating*prev_review_count))/total_reviews
                
    #             # add new rating calculation to dictionary
    #             single_park_dict[polygon] = [name, new_rating, total_reviews]
    #         else:
    #             single_park_dict[polygon] = [name, rating, review_count]

    #     # create park tuple
    #     park_tuple = ParkTuple(park_polygon=polygon, rating=single_park_dict[polygon][1],total_reviews=single_park_dict[polygon][2])
    
    total_reviews = 0
    cumulative_rating = 0
    park_name = None

    for row in ratings:
        rating_point = Point(row["longitude"], row["latitude"])

        if polygon.contains(rating_point):
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
    
    park_tuple = ParkTuple(park_polygon=polygon, name=park_name,\
        rating=avg_rating, total_reviews=total_reviews, area=polygon.area)

    return park_tuple
        
    # consider removing the park from ratings after rating is found to optimize efficiency
    # may need to think about if multiple polygons will match to the same rating



def match_park_ratings_name(polygon):
    # fuzzy match parks without ratings on name
    pass


def create_parks_dict():
    parks_dict = defaultdict(int)
    
    for polygon in parks.geometry:
        park_tuple = match_park_ratings_point(polygon)
        
        # if reviews not found from point, use park name to match
        if park_tuple.total_reviews is None:
            park_tuple = match_park_ratings_name(polygon)
        
        parks_dict[polygon] = park_tuple
    
    return parks_dict



##############################
# Create housing dictionary with index values
##############################


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

