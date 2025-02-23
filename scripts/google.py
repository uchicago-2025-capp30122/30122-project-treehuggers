import os 
import httpx
import json
import time
from pathlib import Path
from typing import NamedTuple
from yelp import cache_key, FetchException

DATA_DIR = Path(__file__).parent.parent / 'data'
CACHE_DIR = DATA_DIR / "_cache"

class Park(NamedTuple):
    name: str
    latitude: float
    longitude: float
    rating: float
    review_count: int
    source: str
    
try:
    API_KEY = os.environ["API_KEY"] 
except KeyError:
    raise Exception(
        "Please enter API Key for Google"
    )
    
CHICAGO_LOCATIONS = [ 
       (41.7033, -87.8980),
       (41.7033, -87.8140),
       (41.7033, -87.7300),
       (41.7033, -87.6460),
       (41.7033, -87.5620),
       (41.8300, -87.8980),
       (41.8300, -87.8140),
       (41.8300, -87.7300),
       (41.8300, -87.6460),
       (41.8300, -87.5620),
       (41.9567, -87.8980),
       (41.9567, -87.8140),
       (41.9567, -87.7300),
       (41.9567, -87.6460),
       (41.9567, -87.5620),
    ]
    
def cached_google_get(url, kwargs: dict) -> dict:
    '''
    Fetches API data from Google based on inputted URL and arguments
    
    Inputs:
        url: Yelp API URL
        kwargs: arguments dictionary
        
    Outputs:
        dictionary of raw data returned
    '''
    key = cache_key(url, kwargs)
    
    # If response already in cache, return it
    CACHE_DIR.mkdir(exist_ok=True, parents=True)
    path = CACHE_DIR / key
    if path.exists():
        with open(path, "r") as f:
            all_data_dict = json.load(f)
        return all_data_dict
    
    # Else get from Google
    all_places = []
    
    for loc in CHICAGO_LOCATIONS:
        next_page_token = None
        for i in range(3): # Limit of 60 results per search
            
            kwargs["location"] = f"{loc[0]},{loc[1]}"
            kwargs["key"] = API_KEY
            kwargs["page_token"] = next_page_token
            
            response = httpx.get(url, params=kwargs)
            if response.status_code == 200:
                data = response.json()
                all_places.extend(data.get("results", [])) 
                print("Getting results", i, "for", loc)
                next_page_token = data.get("next_page_token", None)
                if not next_page_token: 
                    break
                else:
                    time.sleep(10)
            else:
                raise FetchException(response)
            
    # Save in cache 
    all_data_dict = {"places": all_places}
    with open(path, "w") as f:
        json.dump(all_data_dict, f, indent=1)
    return all_data_dict

def clean_google(data: dict, output_name: str):
    '''
    Saves cleaned version of raw Google data to data directory with following:
    name, latitude, longitude, rating, review_count, source
    
    Inputs:
        data: dictionary of raw data
        output_name: string name used for saving cleaned data in data directory
    '''
    places = []
    for place in data["places"]:
        places.append(
            {
            "name": place.get("name", "N/A"),
            "latitude": place.get("geometry", {}).get("location", {}).get("lat", None),
            "longitude": place.get("geometry", {}).get("location", {}).get("lng", None),
            "rating": place.get("rating", ""),
            "review_count": place.get("user_ratings_total", ""),      
            "source": "Google"
            }
        )
     
    path = DATA_DIR / (output_name + '.json')
    with open(path, "w") as f:
        json.dump(places, f, indent=1)
    
  
search_category = "field"
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
parameters = {"radius": "3590"}
parameters["keyword"] = search_category   
    
google_raw_data = cached_google_get(url, parameters)
clean_google(google_raw_data, "google_"+search_category)
