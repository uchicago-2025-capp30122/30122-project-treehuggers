import os 
import httpx
import json
import time
from pathlib import Path
from import_utils import cache_key, FetchException, CHICAGO_LOCATIONS

DATA_DIR = Path(__file__).parent.parent / 'data'
CACHE_DIR = DATA_DIR / "_cache"

try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"] 
except KeyError:
    raise Exception(
        "Please enter API Key for Google"
    )
    

    
def cached_get_google(url, kwargs: dict) -> dict:
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
            kwargs["key"] = GOOGLE_API_KEY
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

def clean_google(data: dict):
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
    return places
        
def save_google(places: list[dict], output_name: str):
    '''
    Saves data at specified output path 
    '''
    path = DATA_DIR / (output_name + '.json')
    with open(path, "w") as f:
        json.dump(places, f, indent=1)
  
if __name__ == "__main__":
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    for search_category in ["park", "field", "stadium"]:
        parameters = {"radius": "3590"}
    
        # Either search using "type" or using a keyword
        if search_category == "park":
            parameters["type"] = search_category
        else:
            parameters["keyword"] = search_category   
            
        google_raw_data = cached_get_google(url, parameters)
        google_clean_data = clean_google(google_raw_data)
        save_google(google_clean_data, "google_"+search_category)
