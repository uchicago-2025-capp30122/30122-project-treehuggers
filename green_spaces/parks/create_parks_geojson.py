import osmnx as ox
import json
from pathlib import Path

# Define the data directory relative to the script's location
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def fetch_and_save_park_data(
    place_name="Chicago, Illinois, USA",
    output_filename="uncleaned_park_polygons.geojson",
):
    """
    Fetch park features from OpenStreetMap for a given place and save them to a GeoJSON file.

    Args:
        place_name (str): The name of the place to fetch park data for.
        output_filename (str): The name of the output GeoJSON file.
    """
    polygons_filepath = DATA_DIR / output_filename

    # Define the OSM tags for parks and recreational areas
    tags = {
        "leisure": ["park", "nature_reserve", "playground", "dog_park"],
        "landuse": "recreation_ground",
    }

    # Retrieve park features from OSM
    parks = ox.features_from_place(place_name, tags=tags)

    # Select only relevant columns, adding safeguards for missing ones
    required_columns = ["geometry", "ele", "leisure", "name"]

    # Separate points and polygons
    parks_polygons = parks[parks.geometry.geom_type == "Polygon"]

    # Save to GeoJSON file
    parks_polygons[required_columns].to_file(polygons_filepath, driver="GeoJSON")

    # Pretty-print the GeoJSON file
    with polygons_filepath.open("r") as f:
        data = json.load(f)

    with polygons_filepath.open("w") as f:
        json.dump(data, f, indent=4)

    print(f"Created {output_filename} file")


if __name__ == "__main__":
    fetch_and_save_park_data()
