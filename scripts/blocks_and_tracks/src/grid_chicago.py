import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from pathlib import Path
import numpy as np
from scripts.index.index import create_housing_file

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


def main():
    # We use Chicago boundaries
    north, south, east, west = 42.023131, 41.644286, -87.523661, -87.940101
    spacing = 0.01
    
    # Set output directory
    output_file = Path(__file__).parent.parent / "data/processed/index.geojson"
    
    #Index for all points
    distance = 1000

    main_data_path = Path(__file__).parent.parent.parent.parent

    parks = gpd.read_file(main_data_path / "data/cleaned_park_polygons.geojson" )
    ratings = gpd.read_file(main_data_path / "data/review_data/combined_reviews_buffered_250.geojson")
    
    #Create the grid file 
    print("Creating grid of points over Chicago...")
    grid_gdf = create_grid(north, south, east, west, spacing)
    create_housing_file(grid_gdf, distance, parks, ratings, output_file)

    print(f"Created grid with {len(grid_gdf)} points")

if __name__ == "__main__":
    main()