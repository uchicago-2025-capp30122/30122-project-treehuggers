import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from pathlib import Path
import numpy as np
from green_spaces.index.index import create_housing_file

def create_grid(north, south, east, west, spacing):
    """
    Create a grid of points over the specified bounding box.
    
    Args:
        north (float): Northern boundary
        south (float): Southern boundary
        east (float): Eastern boundary
        west (float): Western boundary
        spacing (float): Spacing between points in degrees
    
    Returns:
        GeoDataFrame: Grid of points
    """
    x_coords = np.arange(west, east, spacing)
    y_coords = np.arange(south, north, spacing)
    points = [Point(x, y) for x in x_coords for y in y_coords]
    grid_gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
    grid_gdf["Longitude"] = grid_gdf.geometry.x
    grid_gdf["Latitude"] = grid_gdf.geometry.y
    return grid_gdf

def get_boundaries_polygon(parks_gdf):
    """
    Extract bounding box coordinates from parks GeoDataFrame.
    
    Args:
        parks_gdf: GeoDataFrame containing park polygons
    
    Returns:
        tuple: (north, south, east, west) coordinates
    """
    # Get the total bounds of all park geometries
    minx, miny, maxx, maxy = parks_gdf.total_bounds
    
    # Return as north, south, east, west
    return maxy, miny, maxx, minx

def main():
    #Set paths for this module
    main_data_path = Path(__file__).parent.parent.parent
    output_file = main_data_path / "data/grid_and_tracts/processed/grid/index.geojson"
    
    print("Loading parks data...")
    parks = gpd.read_file(main_data_path / "data/cleaned_park_polygons.geojson" )
    ratings = gpd.read_file(main_data_path / "data/review_data/combined_reviews_buffered_250.geojson")
    
    #Create the grid file 
    north, south, east, west = get_boundaries_polygon(parks)
    print(f"Parks data boundaries: North={north},South={south}, East={east}, West={west}")
    # We use Chicago boundaries
    spacing = 0.002 #Aprox 200 meters
    #Index for all points
    distance = 1000
    print("Creating grid of points over Chicago...")
    grid_gdf = create_grid(north, south, east, west, spacing)
    
    #Not running the file again if already exists, time consuming
    if not output_file.exists():
        create_housing_file(grid_gdf, distance, parks, ratings, output_file)
    else:
        print(f"   File already exists at {output_file}")
    print(f"   Created grid with {len(grid_gdf)} points")

if __name__ == "__main__":
    main()