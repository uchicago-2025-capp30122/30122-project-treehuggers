import geopandas as gpd
import json
import re
from shapely.geometry import Polygon
from typing import NamedTuple
from collections import defaultdict
from pathlib import Path
from jellyfish import jaro_winkler_similarity
from rtree import index as rtree_index

DATA_DIR = Path(__file__).parent.parent.parent / "data" 
REVIEW_DIR = DATA_DIR / "review_data"

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

REMOVE_WORDS = ["Park", "park", "Garden", "Field", "Playground"]

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

    if total_reviews != 0:
        # Compute average rating
        avg_rating = cumulative_rating / total_reviews

    return ParkTuple(
        park_polygon=polygon,
        name=park_name,
        rating=avg_rating,
        total_reviews=total_reviews,
        area=polygon.area,
    )


def match_park_ratings_point(polygon, ratings):
    """
    Match Yelp and Google ratings to parks based on location.

    Args:
        polygon: Polygon object of a park.

    Returns: ParkTuple with ratings.
    """
    matching_rows = []

    for _, row in ratings.iterrows():
        buffered_review = row["geometry"]

        if buffered_review.intersects(polygon):
            matching_rows.append(row)

    park_tuple = calculate_park_rating(matching_rows, polygon)

    return park_tuple


def match_park_ratings_name(park_name, polygon, ratings):
    """
    Match Yelp and Google ratings to parks based on name similarity.

    Args:
        park_name (str): Name of the park.
        polygon: Polygon object of the park.

    Returns: ParkTuple with ratings.
    """
    matching_rows = []
    
    # Process park_name once outside the loop
    cleaned_park_name = park_name
    for word in REMOVE_WORDS:
        cleaned_park_name = cleaned_park_name.replace(word, "")
        
    is_numbered_park = re.match(r"^No\.\s\d{3}$", cleaned_park_name.strip())
    
    for _, row in ratings.iterrows():
        # remove words such as "park" and "field" from park name
        cleaned_row_name = row["name"]
        for word in REMOVE_WORDS:
            cleaned_row_name = cleaned_row_name.replace(word, "")

        # calculate similarity score of park names
        sim_score = jaro_winkler_similarity(cleaned_row_name, park_name)

        # for park names such as "No. 593", require close to a perfect match
        if is_numbered_park and sim_score > 0.97:
            matching_rows.append(row)

        # for all other parks, only require match threshold of 0.85
        elif not is_numbered_park and sim_score > 0.85:
            matching_rows.append(row)

    park_tuple = calculate_park_rating(matching_rows, polygon)

    return park_tuple


def create_parks_dict(parks_data, ratings):
    """
    Create a dictionary of parks with average ratings.

    Args:
        parks_data (geopandas dataframe): parks data

    Returns: dictionary of parks with NamedTuples as values.
    """
    parks_dict = defaultdict(int)

    for _, park in parks_data.iterrows():
        polygon = park.geometry
        park_name = park["name"]

        park_tuple = match_park_ratings_point(polygon, ratings)

        # Still check all park matches on name even if a review was matched to
        # a park based on spatial proximity & override previous match accordingly
        if park_name is not None:
            park_tuple = match_park_ratings_name(park_name, polygon, ratings)

        parks_dict[park["id"]] = park_tuple

    return parks_dict


##############################
# Find parks within walking distance to housing units
##############################
def create_buffer(housing, distance):
    """
    Create buffers around each housing unit based on distance.

    Args:
        housing (geopandas dataframe): affordable housing data
        distance (int): specifies buffer distnace (meters) from housing unit

    Returns: updated geopandas dataframe with buffer geometries.
    """
    # convert to a metric CRS for buffering in meters
    housing_project = housing.to_crs(epsg=3857)

    # apply buffer to all points in housing data
    housing_project["geometry"] = housing_project.geometry.buffer(distance)

    # convert back to EPSG: 4326 in order to compare to polygon object
    housing_project = housing_project.to_crs(epsg=4326)

    return housing_project


def park_walking_distance(buffered_point, parks_data):
    """
    Find parks within walking distance of housing unit.

    Args:
        buffered_point (Polygon): buffered radius around housing unit
        parks_data (geopandas dataframe): parks data

    Returns: tuple containing count of parks within walking distance to unit and
    list of those park ids.
    """
    polygon_id_list = []
    park_count = 0
    # Create spatial index
    idx = rtree_index.Index()
    for i, park in parks_data.iterrows():
        idx.insert(i, park.geometry.bounds)
    
    # Use spatial index to filter candidates
    for i in list(idx.intersection(buffered_point.bounds)):
        park = parks_data.iloc[i]
        polygon = park.geometry
        polygon_id = park["id"]
        
        if buffered_point.intersects(polygon):
            park_count += 1
            polygon_id_list.append(polygon_id)

    return (park_count, polygon_id_list)


def calculate_index(polygon_list, parks_dict):
    """
    Calculate size and rating indexes for each housing unit.

    Args:
        polygon_list (lst): list of polygon ids.
        parks_dict (dict): dictionary containing park values (NamedTuples)

    Returns: tuple containing index values.
    """
    rating_index = 0
    size_index = 0

    for poly_id in polygon_list:
        park_tuple = parks_dict[poly_id]
        # calculate index only using park size
        size_index += park_tuple.area

        # calculate index using park reviews and size
        rating_index += park_tuple.area * park_tuple.rating

    return (size_index, rating_index)


def create_house_tuple(buffered_point, parks_dict, parks_data):
    """
    Create NamedTuple for each housing unit.

    Args:
        buffered_point (Polygon): buffered radius around housing unit
        housing (geopandas dataframe): affordable housing data
        parks_data (geopandas dataframe): parks data

    Returns: NamedTuple of housing unit with index values.
    """
    parks_buffer_count, polygon_id_list = park_walking_distance(
        buffered_point, parks_data
    )

    # check that polygon_list is not empty before proceeding
    if len(polygon_id_list) == 0:
        house_tuple = HousingTuple(park_count=0, size_index=0, rating_index=0)
    else:
        # gather park tuples that fall within radius
        size_ix, rating_ix = calculate_index(polygon_id_list, parks_dict)
        house_tuple = HousingTuple(
            park_count=parks_buffer_count, size_index=size_ix, rating_index=rating_ix
        )

    return house_tuple


##############################
# Create housing dataframe with indexes
##############################


def create_housing_df(housing, parks_dict, distance, parks_data, ratings):
    """
    Create updated housing dataframe with index columns.

    Args:
        housing (geopandas dataframe): affordable housing data
        parks_dict (dict): dictionary containing park values (NamedTuples)
        distance (int): specifies buffer distnace (meters) from housing unit
        parks_data (geopandas dataframe): parks data

    Returns: geopandas dataframe of housing data with indexes.
    """
    # apply buffer to entire GeoDataFrame
    housing_with_index = create_buffer(housing, distance)

    for idx, row in housing_with_index.iterrows():
        buffered_point = row["geometry"]
        house_tuple = create_house_tuple(buffered_point, parks_dict, parks_data)

        housing_with_index.at[idx, "id"] = idx + 1  # Assign unique ID
        housing_with_index.at[idx, "park_count"] = house_tuple.park_count
        housing_with_index.at[idx, "size_index"] = house_tuple.size_index
        housing_with_index.at[idx, "rating_index"] = house_tuple.rating_index

    return housing_with_index


def calc_norm_values(housing):
    """
    Calculate values to normalize indexes.

    Args:
        housing (geopandas dataframe): affordable housing data

    Returns: tuple containing values to normalize index.
    """

    max_size = housing["size_index"].max()
    max_rating = housing["rating_index"].max()
    avg_rating = housing["rating_index"].mean()

    return (float(max_size), float(max_rating), float(avg_rating))


##############################
# Output housing file with indexes
##############################


def create_housing_file(housing, distance, parks_data, ratings, file_name):
    """
    Create housing GeoJSON file with indexes.

    Args:
        housing (geopandas dataframe): affordable housing data
        distance (int): specifies buffer distnace (meters) from housing unit
        parks_data (geopandas dataframe): parks data

    Returns: outputs GeoJSON file to "data" folder.
    """
    # Create parks dictionary & updated housing dataframe
    parks_dict = create_parks_dict(parks_data, ratings)
    housing_with_index = create_housing_df(
        housing, parks_dict, distance, parks_data, ratings
    )

    # retrieve values to normalize indexes
    max_size, max_rating, avg_rating = calc_norm_values(housing_with_index)

    # update rows where rating index = 0 with average index
    housing_with_index.loc[housing_with_index["rating_index"] == 0, "rating_index"] = (
        avg_rating
    )

    # Create geoJSON dictionary
    geojson_dict = {"type": "FeatureCollection", "features": []}

    # Convert housing dataframe to geoJSON format
    for _, row in housing_with_index.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["Longitude"], row["Latitude"]],
            },
            "properties": {
                "id": row["id"],
                "park_count": row["park_count"],
                # Normalize index values on a scale of 1 to 100
                "size_index": 100 * (row["size_index"] / max_size),
                "rating_index": 100 * (row["rating_index"] / max_rating),
                "latitude": row["Latitude"],
                "longitude": row["Longitude"],
            },
        }
        geojson_dict["features"].append(feature)

    # Save to a GeoJSON file
    with open(file_name, "w") as f:
        json.dump(geojson_dict, f, indent=4)


def main(): 
    # Import data
    parks = gpd.read_file(DATA_DIR / "cleaned_park_polygons.geojson")
    housing = gpd.read_file(DATA_DIR / "housing.geojson")
    ratings = gpd.read_file(REVIEW_DIR / "combined_reviews_buffered_250.geojson")

    # Create housing file
    path = DATA_DIR / "housing_data_index.geojson"
    create_housing_file(housing, 1000, parks, ratings, path)
    
if __name__ == "__main__":
    main()