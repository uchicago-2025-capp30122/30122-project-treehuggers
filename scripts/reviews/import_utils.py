import re
import httpx
import json

# List of 15 locations spread out throughout Chicago
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

class FetchException(Exception):
    """
    Turn a httpx.Response into an exception.
    """

    def __init__(self, response: httpx.Response):
        super().__init__(
            f"{response.status_code} retrieving {response.url}: {response.text}"
        )

def cache_key(url: str, kwargs: dict) -> str:
    '''
    Inputs:
        url: string of URL for api call 
        kwards: dict
    Returns:
        cache_key string
    '''
    replace_pattern = re.compile(r'https?://|[^a-zA-Z0-9%+,^=._"]')
    cache_key = re.sub(replace_pattern.pattern, '', url.lower())
    for key, value in kwargs.items():
        cache_key += "_" + re.sub(replace_pattern, '', key) \
                  +  "_" + re.sub(replace_pattern, '', value) \
                  + ".json"
    return cache_key

def get_unnamed_park_locations(path) -> list[tuple]:
    '''
    Inputs:
        path: location of json file with unnamed parks
    Outputs:
        list of tuples with latitude, longitude    
    '''
    all_coords = []
    with open(path, "r") as f:
        parks = json.load(f)
        for park in parks:
            coords = park.get("centroid").get("coordinates")
            if coords:
                lat = coords[1]
                lon = coords[0]
                all_coords.append((lat, lon))
    return all_coords
        
    