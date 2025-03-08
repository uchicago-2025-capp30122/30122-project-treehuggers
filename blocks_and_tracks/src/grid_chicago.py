import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from pathlib import Path
import numpy as np

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
    grid_gdf = gpd.GeoDataFrame(geometry=points)
    return grid_gdf

def save_data(grid_gdf, output_dir):
    """Save the GeoDataFrame to a file."""
    try:
        # We create output directory if it doesn't exist
        grid_path = output_dir / "grid"
        grid_path.mkdir(parents=True, exist_ok=True)
        
        grid_gdf.to_file(grid_path / "chicago_grid.geojson", driver='GeoJSON')
        
        print(f"Data saved successfully to {grid_path}")
    
    except Exception as e:
        print(f"Error saving data: {e}")

def main():
    # We use Chicago boundaries
    north, south, east, west = 42.023131, 41.644286, -87.523661, -87.940101
    spacing = 0.001 
    
    # Set output directory
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    
    # Create grid
    print("Creating grid of points over Chicago...")
    grid_gdf = create_grid(north, south, east, west, spacing)
    
    if grid_gdf is not None:
        print(f"Created grid with {len(grid_gdf)} points")
        save_data(grid_gdf, output_dir)

if __name__ == "__main__":
    main()