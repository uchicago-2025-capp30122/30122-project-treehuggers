import httpx
import os
import json
<<<<<<< HEAD
import time 
=======
import time
import re
>>>>>>> grace
from pathlib import Path
from .import_utils import cache_key, FetchException

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_DIR = DATA_DIR / "_cache"

<<<<<<< HEAD
try:
    YELP_API_KEY = f"Bearer {os.environ["YELP_API_KEY"]}" 
=======

class FetchException(Exception):
    """
    Turn a httpx.Response into an exception.
    """

    def __init__(self, response: httpx.Response):
        super().__init__(
            f"{response.status_code} retrieving {response.url}: {response.text}"
        )


try:
    API_KEY = f"Bearer {os.environ['API_KEY']}"
>>>>>>> grace
except KeyError:
    raise Exception("Please enter API Key for Yelp")


<<<<<<< HEAD
def cached_get_yelp(url, kwargs: dict) -> dict:
    '''
=======
def cache_key(url: str, kwargs: dict) -> str:
    """
    Inputs:
        url: string of URL for api call
        kwards: dict
    Returns:
        cache_key string
    """
    replace_pattern = re.compile(r'https?://|[^a-zA-Z0-9%+,^=._"]')
    cache_key = re.sub(replace_pattern.pattern, "", url.lower())
    for key, value in kwargs.items():
        cache_key += (
            "_"
            + re.sub(replace_pattern, "", key)
            + "_"
            + re.sub(replace_pattern, "", value)
            + ".json"
        )
    return cache_key


def cached_yelp_get(url, kwargs: dict) -> dict:
    """
>>>>>>> grace
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
<<<<<<< HEAD
        "Authorization": YELP_API_KEY,    
=======
        "Authorization": API_KEY,
>>>>>>> grace
    }
    for offset in range(0, 250, 50):  # Yelp limits to 50 per call, 240 total
        kwargs["offset"] = str(offset)
        response = httpx.get(url, params=kwargs, headers=headers)

        if response.status_code == 200:
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

<<<<<<< HEAD
def clean_yelp(data: dict) -> list[dict]:
    '''
    Creates list of cleaned Yelp data dictionaries with following keys:
=======

def clean_yelp(data: dict, output_name: str):
    """
    Saves cleaned version of raw Yelp data to data directory with following:
>>>>>>> grace
    name, latitude, longitude, rating, review_count, source

    Inputs:
        data: dictionary of raw data
<<<<<<< HEAD
        
    Returns:
        list of cleaned data dictionaries as specified above
    '''
=======
        output_name: string name used for saving cleaned data in data directory
    """
>>>>>>> grace
    places = []
    for place in data["places"]:
        places.append(
            {
<<<<<<< HEAD
            "name": place.get("name"),
            "latitude": place.get("coordinates",{}).get("latitude"),
            "longitude": place.get("coordinates",{}).get("longitude"),
            "rating": place.get("rating", 0),
            "review_count": place.get("review_count", 0),      
            "source": "Yelp"
=======
                "name": place["name"],
                "latitude": place["coordinates"]["latitude"],
                "longitude": place["coordinates"]["longitude"],
                "rating": place["rating"],
                "review_count": place["review_count"],
                "source": "Yelp",
>>>>>>> grace
            }
        )
    return places
    

<<<<<<< HEAD
def save_yelp(places: list[dict], output_name: str):
    '''
    Saves data to directory
    '''
    path = DATA_DIR / (output_name + '.json')
=======
    path = DATA_DIR / (output_name + ".json")
>>>>>>> grace
    with open(path, "w") as f:
        json.dump(places, f, indent=1)


if __name__ == "__main__":
    url = "https://api.yelp.com/v3/businesses/search"
<<<<<<< HEAD
    for search_category in ["parks", 
                            "playgrounds", 
                            "dog_parks", 
                            "communitygardens"]:
        
        headers = {"location": "Chicago", "sort_by": "best_match"}
        headers["categories"] = search_category
        yelp_raw_data = cached_get_yelp(url, headers)
        places = clean_yelp(yelp_raw_data)
        save_yelp(places, "yelp_"+search_category)
=======
    for search_category in ["parks", "playgrounds", "dog_parks", "communitygardens"]:
        headers = {"location": "Chicago", "sort_by": "best_match"}
        headers["categories"] = search_category
        yelp_raw_data = cached_yelp_get(url, headers)
        clean_yelp(yelp_raw_data, "yelp_" + search_category)
>>>>>>> grace
