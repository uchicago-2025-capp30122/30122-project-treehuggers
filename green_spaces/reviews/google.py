import os
import httpx
import json
import time
from pathlib import Path
from .reviews_utils import (
    cache_key,
    FetchException,
    CHICAGO_LOCATIONS,
    get_unnamed_park_locations,
    save_reviews,
)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "review_data"
CACHE_DIR = Path(__file__).parent.parent.parent / "cache"

# Set Google API Key (not needed if using cached files)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


def cached_get_google(url, kwargs: dict, locations: list[tuple]) -> dict:
    """
    Fetches API data from Google based on inputted URL and arguments

    Inputs:
        url: Yelp API URL
        kwargs: arguments dictionary

    Outputs:
        dictionary of raw data returned
    """
    key = cache_key(url, kwargs)

    # If response already in cache, return it
    CACHE_DIR.mkdir(exist_ok=True, parents=True)
    path = CACHE_DIR / key
    if path.exists():
        with open(path, "r") as f:
            all_data_dict = json.load(f)
        return all_data_dict

    # Else get from Google
    kwargs["key"] = GOOGLE_API_KEY
    all_places = []

    # Loop through list of 15 locations distributed throughout Chicago
    for loc in locations:
        next_page_token = None
        for i in range(3):  # Limit of 60 results per search, 20 per page
            # Set location argument equal to lat/lon coordinates in loop
            kwargs["location"] = f"{loc[0]},{loc[1]}"

            # Set page token either to None or from previous httpx response
            kwargs["page_token"] = next_page_token

            response = httpx.get(url, params=kwargs)
            if response.status_code == 200:
                # Extend data list with fetched results, set page token
                data = response.json()
                all_places.extend(data.get("results", []))
                print("Getting results", i, "for", loc)
                next_page_token = data.get("next_page_token", None)
                if not next_page_token:
                    # No more results
                    break
                else:
                    time.sleep(1)
            else:
                # Error fetching
                raise FetchException(response)

    # Save in cache
    all_data_dict = {"places": all_places}
    with open(path, "w") as f:
        json.dump(all_data_dict, f, indent=1)
    return all_data_dict


def clean_google(data: dict) -> list[dict]:
    """
    Saves cleaned version of raw Google data to data directory with following:
    name, latitude, longitude, rating, review_count, source

    Inputs:
        data: dictionary of raw data
        output_name: string name used for saving cleaned data in data directory

    Outputs:
        list of dictionaries containing key information for each place
    """
    places = []
    for place in data["places"]:
        # Select relevant fields on park location/quality
        places.append(
            {
                "name": place.get("name", "N/A"),
                "latitude": place.get("geometry", {})
                .get("location", {})
                .get("lat", None),
                "longitude": place.get("geometry", {})
                .get("location", {})
                .get("lng", None),
                "rating": place.get("rating", 0),
                "review_count": place.get("user_ratings_total", 0),
                "source": "Google",
            }
        )
    return places

def main():

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    # Run various searches to be saved separately
    for search_category in ["park", "field", "stadium"]:
        parameters = {"radius": "3590"}  # Roughly dividing Chicago in 15 areas

        # Utilize more specific "type" parameter when searching for a park,
        # otherwise search using keyword if not a park search
        if search_category == "park":
            parameters["type"] = search_category
        else:
            parameters["keyword"] = search_category

        google_raw_data = cached_get_google(url, parameters, CHICAGO_LOCATIONS)
        google_clean_data = clean_google(google_raw_data)
        save_reviews(google_clean_data, "google_" + search_category)

    # Search for unnamed parks not merged on reviews,
    # searching by location with a small radius
    path = DATA_DIR / "parks_without_reviews.json"
    unnamed_park_locations = get_unnamed_park_locations(path)

    parameters = {"radius": "250", "keyword": "park"}
    google_raw_data = cached_get_google(url, parameters, unnamed_park_locations)
    google_clean_data = clean_google(google_raw_data)
    save_reviews(google_clean_data, "google_additional_parks")
    
    print("Google Reviews Fetched")
 
if __name__ == "__main__":
   main()