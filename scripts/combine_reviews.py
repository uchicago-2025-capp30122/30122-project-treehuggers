import json
import geopandas as gpd
from pathlib import Path
from typing import NamedTuple
from shapely.geometry import Point


DATA_DIR = Path(__file__).parent.parent / 'data'
class Place(NamedTuple):
    name: str
    latitude: float
    longitude: float
    rating: float
    review_count: int
    source: str

def combine_reviews() -> list[dict]:
    '''
    Combine Yelp and Google review files in data folder, save as merged json
    
    Inputs:
        None
    
    Outputs:
        list of dictionaries with merged, unique Yelp and Google reviews
    '''
    
    # Save review information in set to avoid duplicates
    unique_entries = set()
    for source in ["google", "yelp"]:
        
        # Load in each .json file beginning with "google" or "yelp"
        paths = list(DATA_DIR.glob(f"{source}_*.json"))
        
        for path in paths:
            with open(path, "r") as f:
                places = json.load(f)
                
                # Grab characteristics for place, save as named tuple in set
                for place in places:
                    unique_entries.add(Place(
                    name=place["name"],
                    latitude=place["latitude"],
                    longitude=place["longitude"],
                    rating=place["rating"],
                    review_count=place["review_count"],
                    source=place["source"],
                ))

    # Convert set of tuples to list of dictionaries 
    lst_data_dicts = []
    for row in unique_entries:
        lst_data_dicts.append(row._asdict())
            
    # Save as JSON
    output_path = DATA_DIR / "combined_reviews_clean.json"
    with open(output_path, "w") as f:
        json.dump(lst_data_dicts, f, indent=1)
    
    return lst_data_dicts

def buffer_places(places: list[dict], buffer_distance: int):
    '''
    Take a list of dictionaries of places with latitudes and longitudes, 
    buffer each point by inputted buffer distance
    '''
    # Convert the list of dictionaries into a list of geometries and properties
    geo = [Point(float(place['longitude']), float(place['latitude'])) for place in places]

    # Create a GeoDataFrame
    places_gdf = gpd.GeoDataFrame(places, geometry=geo, crs=3857)
    
    # apply buffer to all points in places data
    places_gdf["geometry"] = places_gdf.geometry.buffer(buffer_distance)
    
    # convert to EPSG: 4326 in order to compare to polygons
    places_gdf = places_gdf.to_crs(epsg=4326)
    
    # Save and return 
    path = (
        DATA_DIR / 
        str("combined_reviews_buffered.geojson_" + 
        str(buffer_distance) + 
        ".geojson")
    )
    places_gdf.to_file(path, driver='GeoJSON')
    return places_gdf

# Create buffered files of places 
places = combine_reviews()
for buffer_distance in [50, 100, 250, 500, 750, 1000]:
    buffer_places(places, buffer_distance)
