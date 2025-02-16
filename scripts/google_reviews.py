import os 
import googlemaps
import json
import time
from pathlib import Path
from typing import NamedTuple

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
        "Please enter API Key for Yelp"
    )
    
data_dir = Path(__file__).resolve().parent.parent / 'data'
raw_path = data_dir / "google_reviews_raw.json"
clean_path = data_dir / "google_reviews_clean.json"


def get_parks():
    gmaps = googlemaps.Client(key=API_KEY)
    places = []
    next_page_token = None
    
    # Divide Chicago into 15 roughly equidistant points 
    search_locations = [ 
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
    
    for x, loc in enumerate(search_locations):
        next_page_token = None
        for i in range(3):
            
            response = gmaps.places(
                type="park",
                location=loc,
                radius=3590, 
                page_token = next_page_token
                )
            
            next_page_token = response.get("next_page_token", None)
            places.extend(response.get("results", []))
            time.sleep(10.2)
            
            if not next_page_token: 
                continue 
   
    with open(raw_path, "w") as f:
        json.dump(places, f, indent=1)

def clean_parks():
    with open(raw_path, "r") as f:
        parks = json.load(f)
        
    parks_set = set()
    for park in parks: 
        name = park.get("name", "N/A")
        lat = park.get("geometry", {}).get("location", {}).get("lat", None)
        lng = park.get("geometry", {}).get("location", {}).get("lng", None)
        rating = park.get("rating", "N/A")
        review_count = park.get("user_ratings_total")
        source = "Google"
        
        # Add parks to set for de-duplication 
        parks_set.add(Park(name, lat, lng, rating, review_count, source))
        
    # Convert park set back to list of dictionaries
    parks_dicts = []
    for park in parks_set: 
        parks_dicts.append(park._asdict())
        
    with open(clean_path, "w") as f:
        json.dump(parks_dicts, f, indent=1)

clean_parks()