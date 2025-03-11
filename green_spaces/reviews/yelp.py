import httpx
import os
import json
import time
from pathlib import Path
from .reviews_utils import cache_key, FetchException, save_reviews

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "review_data"
CACHE_DIR = Path(__file__).parent.parent.parent / "cache"

# Set Yelp API Key (not needed if using cached files)
YELP_API_KEY = f"Bearer {os.environ.get('YELP_API_KEY')}"


def cached_get_yelp(url, kwargs: dict) -> dict:
    """
    Fetches API data from Yelp based on inputted URL and headers

    Inputs:
        url: Yelp API URL
        kwargs: headers dictionary

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

    # Else get from Yelp
    all_places = []
    headers = {
        "accept": "application/json",
        "Authorization": YELP_API_KEY,
    }
    for offset in range(0, 250, 50):  # Yelp limits to 50 per call, 240 total
        kwargs["offset"] = str(offset)
        response = httpx.get(url, params=kwargs, headers=headers)

        if response.status_code == 200:
            # Successful get, add all fetched results to list
            data = response.json()
            all_places.extend(data["businesses"])
        else:
            raise FetchException(response)

        time.sleep(1)

    # Save in cache
    all_data_dict = {"places": all_places}
    with open(path, "w") as f:
        json.dump(all_data_dict, f, indent=1)
    return all_data_dict


def clean_yelp(data: dict) -> list[dict]:
    """
    Creates list of cleaned Yelp data dictionaries with following keys:
    name, latitude, longitude, rating, review_count, source

    Inputs:
        data: dictionary of raw data

    Returns:
        list of cleaned data dictionaries as specified above
    """
    places = []
    for place in data["places"]:
        places.append(
            {
                "name": place.get("name"),
                "latitude": place.get("coordinates", {}).get("latitude"),
                "longitude": place.get("coordinates", {}).get("longitude"),
                "rating": place.get("rating", 0),
                "review_count": place.get("review_count", 0),
                "source": "Yelp",
            }
        )
    return places

def main():
    url = "https://api.yelp.com/v3/businesses/search"

    # Search in multiple Yelp categories
    for search_category in ["parks", "playgrounds", "dog_parks", "communitygardens"]:
        # Always search in Chicago, by "best match" with search category
        headers = {"location": "Chicago", "sort_by": "best_match"}
        headers["categories"] = search_category

        # For each query, get raw data, clean, and save
        yelp_raw_data = cached_get_yelp(url, headers)
        places = clean_yelp(yelp_raw_data)
        save_reviews(places, "yelp_" + search_category)
        
    print("Yelp Reviews Fetched")

if __name__ == "__main__":
    main()
    
    
