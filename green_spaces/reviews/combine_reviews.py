import json
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point
from .reviews_utils import save_reviews, Place

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "review_data"


def combine_reviews(directory) -> list[dict]:
    """
    Combine Yelp and Google files in specified folder, save as merged json

    Inputs:
        Path of directory to check for files

    Outputs:
        list of dictionaries with merged, unique Yelp and Google reviews
    """

    # Put review information in set to remove duplicates
    unique_entries = set()

    for source in ["google", "yelp"]:
        # Load in each .json file beginning with "google" or "yelp"
        paths = list(directory.glob(f"{source}_*.json"))

        for path in paths:
            with open(path, "r") as f:
                places = json.load(f)

                # Grab characteristics for place, save as named tuple in set
                for place in places:
                    unique_entries.add(
                        Place(
                            name=place["name"],
                            latitude=place["latitude"],
                            longitude=place["longitude"],
                            rating=place["rating"],
                            review_count=place["review_count"],
                            source=place["source"],
                        )
                    )

    # Convert set of tuples to list of dictionaries
    lst_data_dicts = []
    for row in unique_entries:
        lst_data_dicts.append(row._asdict())

    return lst_data_dicts


def buffer_places(places: list[dict], buffer_distance: int):
    """
    Buffers places coordinates by specified distance, saving in "data" folder
    and returning as a GeoJSON dataframe

    Inputs:
        places: list of dictionaries of places with latitudes and longitudes
        buffer_distance: int

    Returns:
        GeoJSON dataframe with each place buffered by the specified distance
    """
    # Convert the list of dictionaries into a list of geometries and properties
    geo = [
        Point(float(place["longitude"]), float(place["latitude"])) for place in places
    ]

    # Create a GeoDataFrame
    places_gdf = gpd.GeoDataFrame(places, geometry=geo, crs=3857)

    # Apply buffer to all points in places data
    places_gdf["geometry"] = places_gdf.geometry.buffer(buffer_distance)

    # Convert to EPSG: 4326 in order to compare to polygons
    places_gdf = places_gdf.to_crs(epsg=4326)

    # Save and return
    path = DATA_DIR / str(
        "combined_reviews_buffered_" + str(buffer_distance) + ".geojson"
    )
    places_gdf.to_file(path, driver="GeoJSON")
    return places_gdf


def main():
    # Create GeoJSON dataframe of places buffered by 250 meters
    places = combine_reviews(DATA_DIR)
    save_reviews(places, "combined_reviews_clean")
    buffer_places(places, 250)
    
    print("Reviews Deduplicated and Buffered")

if __name__ == "__main__":
    main()
