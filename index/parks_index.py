import geopandas as gpd
import json
import re
from shapely.geometry import Point, Polygon
from typing import NamedTuple
from collections import defaultdict
from pathlib import Path
from jellyfish import jaro_winkler_similarity


class ParkTuple(NamedTuple):
    park_polygon: Polygon
    name: str
    rating: float
    total_reviews: int
    area: float

class HousingTuple(NamedTuple):
    park_count: int 
    size_index: float
    rating_index: float


REMOVE_WORDS = ["Park", "park"]
MAX_SIZE = 0.06979516506749803
MAX_RATING = 0.3166132156375893

DATA_DIR = Path(__file__).parent.parent / 'data'

##############################
# Load Data 
##############################
# load parks data
parks = gpd.read_file(DATA_DIR/"cleaned_park_polygons.geojson")

# housing data
housing = gpd.read_file(DATA_DIR/"housing.geojson")

# yelp and google ratings
with open(DATA_DIR/"combined_reviews_buffered_50.geojson", "r") as f:
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

        if review_count != "": ## get rid of this if this issue is fixed in reviews file
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
        review_point = Point(row["longitude"], row["latitude"]) # update to take buffered point

    # update matching logic to find nearest point
        if polygon.intersects(review_point): # update once having buffered point
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
        # remove the word "park" from names
        for word in REMOVE_WORDS:
            park_name = park_name.replace(word, "")
            row["name"] = row["name"].replace(word, "")
        
        # calculate similarity score
        sim_score = jaro_winkler_similarity(row["name"], park_name)
        
        # for park names such as "No. 593", require a perfect match
        if re.match(r'^No\.\s\d{3}$', park_name.strip()):
            if sim_score > 0.97:
                # print(#"SIM SCORE ABOVE THRESHOLD:", '\n',
                #   "park name from rating:", row["name"],'\n',
                #   "park name from OSM:", park_name)
                matching_rows.append(row)
                
        # for all other parks, only require match threshold of 0.9
        elif sim_score > 0.9:
            # print(#"SIM SCORE ABOVE THRESHOLD:", '\n',
            #     "park name from rating:", row["name"],'\n',
            #     "park name from OSM:", park_name)
            matching_rows.append(row)
    
    park_tuple = calculate_park_rating(matching_rows, polygon)
        
    return park_tuple


def create_parks_dict(parks):
    """_summary_

    Returns:
        _type_: _description_
    """
    parks_dict = defaultdict(int)
    
    # parks_without_names = 0 # FOR DEBUGGING; DELETE LATER

    for _, park in parks.iterrows():
        polygon = park.geometry
        park_name = park["name"]
        
        ##### FOR DEBUGGING PURPOSES##############################
        # if park_name is None:
        #     parks_without_names += 1
        # ############################################################
        
        park_tuple = match_park_ratings_point(polygon)
        
        ### update this to check all parks on name even if review found from point
        # if reviews not found from point, use park name to match
        if park_tuple.total_reviews is None and park_name is not None:
            park_tuple = match_park_ratings_name(park_name, polygon)

        
        parks_dict[park["id"]] = park_tuple
        
    #######################################################
    ##### FOR DEBUGGING PURPOSES
    # none_count = 0
    # populated_count = 0
    
    # for key, value in parks_dict.items():
    #     if value.total_reviews is None:
    #         none_count += 1
    #     else:
    #         populated_count += 1
             
    # print("parks with ratings:", populated_count)
    # print("parks withOUT ratings:", none_count)
    
    # print("total nameless parks:", parks_without_names)
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
    polygon_id_list = []
    park_count = 0
    
    # think about ways to optimize so that you don't check every park in chicago
    for _, park in parks_data.iterrows():
        polygon = park.geometry 
        polygon_id = park["id"]
        # we can also loop through parks dictionary instead to only consider parks with reviews?
        if buffered_point.intersects(polygon):
            park_count += 1
            polygon_id_list.append(polygon_id)

    return (park_count, polygon_id_list)


def calculate_index(polygon_list, parks_dict):
    rating_index = 0
    size_index = 0

    for poly_id in polygon_list:
        park_tuple = parks_dict[poly_id]
        # calculate index only using park size
        size_index += park_tuple.area * 100
        ### DECIDE WHAT VALUE TO SCALE AREA BY (IF ANY VALUE)
        
        # calculate index using park reviews and size
        rating_index += (park_tuple.area * 100 * park_tuple.rating)
        
        
        ##### FOR DEBUGGING #####
        # if park_tuple.name is not None and park_tuple.rating == 0:
        #     named_parks_no_ratings.add(poly_id)
        ##############################

    return (size_index, rating_index)


def create_house_tuple(buffered_point, parks_dict, parks_data):
    """_summary_

    Args:
        housing (geopandas dataframe): affordable housing data
        parks (geopandas dataframe): parks data
    """
    parks_buffer_count, polygon_id_list = park_walking_distance(buffered_point, parks_data) 
    # for distance (meters): 800 meters roughly 10 min walking distance
    
    #### FOR DEBUGGING: DELETE
    # named_parks_no_ratings = set()
    
    # check that polygon_list is not empty before proceeding
    if len(polygon_id_list) == 0:
        house_tuple = HousingTuple(park_count=0, size_index=0, rating_index=0) 
    else:
        # gather park tuples that fall within radius
        ###### delete parameter: parks_without_ratings (for debugging)
        size_ix, rating_ix = calculate_index(polygon_id_list, parks_dict)
        house_tuple = HousingTuple(park_count=parks_buffer_count, \
            size_index=size_ix,rating_index=rating_ix)

    return house_tuple


##############################
# Create housing file with index columns
##############################

def create_housing_file(housing, parks_dict, distance, parks_data):
    # apply buffer to entire GeoDataFrame
    housing_project = create_buffer(housing, distance)
    parks_dict = create_parks_dict(parks_data)
    
    # Create geoJSON dictionary
    geojson_dict = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # named_parks_no_ratings_AGG = set() # FOR DEBUGGING
    
    house_id = 1
    for _, row in housing_project.iterrows():
        buffered_point = row["geometry"]
        house_tuple = create_house_tuple(buffered_point, parks_dict, parks_data)
        #### FOR DEBUGGING: DELETE: named_parks_no_ratings ############
        # # print(named_parks_no_ratings)
        # if len(named_parks_no_ratings) > 0:
        #     named_parks_no_ratings_AGG.update(named_parks_no_ratings)
        # ########################################
        

        feature = {
            "type": "Feature",
            "geometry":
                {
                "type": "Point",
                "coordinates": [row["Longitude"], row["Latitude"]] 
                },
            "properties": {
                "id": house_id,
                "park_count": house_tuple.park_count,
                # Divide by max size and max rating to normalize index values
                "size_index": house_tuple.size_index/MAX_SIZE,
                "rating_index": house_tuple.rating_index/MAX_RATING,
                "latitude": row["Latitude"],
                "longitude": row["Longitude"]
            }
        }
        geojson_dict["features"].append(feature)

        house_id += 1
        
    # Save to a GeoJSON file
    with open(DATA_DIR / "housing_data_index.geojson", "w") as f:
        json.dump(geojson_dict, f, indent=4)
        
    # return named_parks_no_ratings_AGG
 
    #######################################################
    ##### FOR DEBUGGING PURPOSES: see how many houses have ratings
    # for key, value in housing_dict.items():
    #     if value.rating_index > 0.0:
    #         print(key,value)
    
    #######################################################
        
    ## next tasks:
        ## normalize index: subtract mean from index and divide by SD to normalize
        ## look into houses with no reviews & very small rating index values


def find_norm_constant():
    housing_index = gpd.read_file("data/housing_data_index.geojson")
    
    MAX_SIZE = housing_index["size_index"].max()
    MAX_RATING = housing_index["rating_index"].max()
    
    return (float(MAX_SIZE), float(MAX_RATING))


###########################
###### For Debugging
###########################
housing_index = gpd.read_file("data/housing_data_index.geojson")

def houses_without_reviews(housing_index):
    zero_ratings = 0
    non_zero_ratings = 0
    avg_rating = 0
    
    for _, row in housing_index.iterrows():
        if row["rating_index"] == 0:
            zero_ratings += 1
        elif row["rating_index"] != 0:
            non_zero_ratings += 1
            avg_rating += row["rating_index"]
            
    print("houses with ratings:", non_zero_ratings)     
    print("houses without ratings:", zero_ratings)   
    print("average rating, excluding 0s:", avg_rating/len(housing_index))


def parks_without_reviews():
    parks_dict = create_parks_dict(parks)
    
    no_reviews = 0
    no_name = 0
    for key, value in parks_dict.items():
        if value.total_reviews is None:
            no_reviews += 1
        if value.name is None:
            no_name += 1
            
    print("parks without reviews:", no_reviews)
    print("parks without names:", no_name)
    print("total parks:", len(parks_dict))

    

################# FOR PULLING MORE REVIEWS:
## OUTPUT FILE OF PARKS WITHOUT REVIEWS
## paste into ipython3
# parks_dict = create_parks_dict(parks)

# parks_lst = []
# with open("index/parks_without_reviews.json", "w") as f:
#     for key, value in parks_dict.items():
#         if value.rating == 0:
#             parks_lst.append({
#                 "id": key,
#                 "name": value.name,
#                 "centroid": {"type": "Point", "coordinates": \
#                     [value.park_polygon.centroid.x, value.park_polygon.centroid.y]}
#             })
#         else:
#             continue
    
#     json.dump(parks_lst, f, indent=4)
    
    
# count = 0
# for key, value in parks_dict.items():
#     if value.rating == 0:
#         count += 1
            