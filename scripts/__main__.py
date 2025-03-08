import geopandas as gpd
from pathlib import Path
from reviews.reviews_utils import (
    save_reviews,
    CHICAGO_LOCATIONS,
    get_unnamed_park_locations,
)
from reviews.yelp import cached_get_yelp, clean_yelp
from reviews.google import cached_get_google, clean_google
from reviews.combine_reviews import combine_reviews, buffer_places
from parks.create_parks_geojson import fetch_and_save_park_data
from parks.clean_park_polygons import (
    load_geojson,
    standardize_unnamed_parks,
    handle_intersecting_parks,
    check_park_containment,
    get_final_features,
    save_geojson,
)
from index.index import create_housing_file

DATA_DIR = Path(__file__).parent.parent / "data"
REVIEW_DIR = DATA_DIR / "review_data"
CACHE_DIR = Path(__file__).parent.parent / "cache"

def run_create_park_geojson():
    """
    Run create_park_geojson.py
    """
    fetch_and_save_park_data(
        place_name="Chicago, Illinois, USA",
        output_filename="uncleaned_park_polygons.geojson",
    )

def run_clean_park_polygons():
    """
    Run clean_park_polygons.py
    """
    file_path = DATA_DIR / "uncleaned_park_polygons.geojson"
    output_path = DATA_DIR / "cleaned_park_polygons.geojson"

    features = load_geojson(file_path)

    # standardize unnamed park names in GeoJSON
    standardized_features = standardize_unnamed_parks(features)

    # retrieve intersection graph, list of unnamed parks to remove,
    # list of intersecting named parks to review
    intersection_graph, unnameds_to_remove, check_containment_parks = (
        handle_intersecting_parks(standardized_features)
    )

    # extract list of named parks to remove
    named_parks_to_remove = check_park_containment(check_containment_parks)

    # merge unnamed park clusters & update features list accordingly
    updated_features = get_final_features(
        features, intersection_graph, unnameds_to_remove, named_parks_to_remove
    )

    # create cleaned parks GeoJSON file
    save_geojson(updated_features, output_path)

def run_yelp():
    """
    Run yelp.py
    """

    yelp_api_url = "https://api.yelp.com/v3/businesses/search"

    # Iterate through multiple Yelp queries
    headers = {"location": "Chicago", "sort_by": "best_match"}
    for search_category in ["parks", "playgrounds", "dog_parks", "communitygardens"]:
        headers["categories"] = search_category

        # For each query, get raw data, clean, and save
        yelp_raw_data = cached_get_yelp(yelp_api_url, headers)
        yelp_clean_data = clean_yelp(yelp_raw_data)
        save_reviews(yelp_clean_data, "yelp_" + search_category)
    print("Finished searching for parks on Yelp")


def run_google():
    """
    Run Google.py
    """
    google_api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    # Run various searches to be concatenated
    for search_category in ["park", "field", "stadium"]:
        parameters = {"radius": "3590"}  # Roughly dividing Chicago in 15 areas

        # Either search using keyword (if park) or "type" (not park)
        if search_category == "park":
            parameters["type"] = search_category
        else:
            parameters["keyword"] = search_category

        google_raw_data = cached_get_google(
            google_api_url, parameters, CHICAGO_LOCATIONS
        )

        # Clean and save
        places = clean_google(google_raw_data)
        save_reviews(places, "google_" + search_category)
    print("Finished searching for parks on Google")

    # Search for additional unmerged, unnamed parks specifically by location
    path = REVIEW_DIR / "parks_without_reviews.json"
    unnamed_park_locations = get_unnamed_park_locations(path)

    parameters = {"radius": "250", "keyword": "park"}
    google_raw_data = cached_get_google(
        google_api_url, parameters, unnamed_park_locations
    )

    # Clean and save
    google_clean_data = clean_google(google_raw_data)
    print(
        f"Found {len(google_clean_data)} reviews searching for previously "
        + "unmerged parks on Google"
    )
    save_reviews(google_clean_data, "google_additional_parks")


def run_combine_reviews():
    """
    Run combine_reviews.py
    """
    places = combine_reviews(REVIEW_DIR)
    print(f"After removing duplicates, we have {len(places)} unique reviews")
    save_reviews(places, "combined_reviews_clean")
    buffer_places(places, 250)

def run_index():
    """
    Run index.py
    """
    # Import data
    parks = gpd.read_file(DATA_DIR / "cleaned_park_polygons.geojson")
    housing = gpd.read_file(DATA_DIR / "housing.geojson")
    ratings = gpd.read_file(REVIEW_DIR / "combined_reviews_buffered_250.geojson")

    # Create housing file
    path = DATA_DIR / "housing_data_index.geojson"
    create_housing_file(housing, 1000, parks, ratings, path)


def main():
   
    # Parks
    run_create_park_geojson()
    run_clean_park_polygons()
    
    # Reviews
    run_yelp()
    run_google()
    run_combine_reviews()

    # Index
    run_index()


if __name__ == "__main__":
    main()
