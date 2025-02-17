import osmnx as ox
import matplotlib.pyplot as plt
import json
import os

#MAKE FUNCTION OR MODULE
#Default be parks tags, parameter for rest
# We will want to take a look at if things are intersecting


#PULL OSM DATA

# Define the place and the OSM tag for parks
place_name = "Chicago, Illinois, USA"
tags = {"leisure": "park", "landuse":"recreation_ground", "leisure":"nature_reserve",  "leisure":"playground", "leisure":"dog_park"}

# Retrieve park features from OSM using the correct function name
parks = ox.features_from_place(place_name, tags=tags)
 
# Select only relevant columns, adding safeguards for missing ones
required_columns = ["geometry", "ele", "leisure", "name"]

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