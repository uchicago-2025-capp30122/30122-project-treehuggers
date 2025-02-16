import osmnx as ox
import matplotlib.pyplot as plt
import json
import os

# WRITE A TEST ?
# YOU SAID TO HAVE THE TAG AS A PARAMETER, BUT I AM NOT SURE WE SHOULD GIVE THAT MUCH FREEDOM TO USER? 
# WOULDN'T ALLOWING TAGS MEAN THEY COULD PULL ANYTHING IN? THEN DATA MAY BE DIFF?
# IS GEOJSON OKAY WITH HAVE POLYGON COORDINATES LIKE THAT ??

# Define the place and the OSM tag for parks
place_name = "Chicago, Illinois, USA"
tags = {"leisure": "park"}

# Retrieve park features from OSM using the correct function name
parks = ox.features_from_place(place_name, tags=tags)
 
# Select only relevant columns, adding safeguards for missing ones
required_columns = ["geometry", "ele", "gnis:feature_id", "leisure", "name"]

# Separate points and polygons
parks_points = parks[parks.geometry.geom_type == "Point"]
parks_polygons = parks[parks.geometry.geom_type == "Polygon"]

# Create file paths to save geojsons: 

# Move up one level to project root
project_root = os.path.dirname(os.getcwd())
# Define data folder path
data_folder = os.path.join(project_root, "data")
# Define points filepath
points_filepath = os.path.join(data_folder, "parks_points.geojson")
# Define polygons filepath
polygons_filepath = os.path.join(data_folder, "parks_polygons.geojson")

# Save to GeoJSON files
parks_points[required_columns].to_file(points_filepath, driver="GeoJSON")
parks_polygons[required_columns].to_file(polygons_filepath, driver="GeoJSON")

# Pretty-print the GeoJSON files
for filename in [points_filepath, polygons_filepath]:
    with open(filename, "r") as f:
        data = json.load(f)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)