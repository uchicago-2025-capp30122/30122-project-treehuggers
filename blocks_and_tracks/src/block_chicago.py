import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd
from pathlib import Path

def get_chicago_buildings():
    """
    Retrieve building footprints for Chicago using OSMNX.
    Returns both the building polygons and their centroids.
    """
    # Chicago boundaries
    north, south, east, west = 42.023131, 41.644286, -87.523661, -87.940101

    try:
        # Get building footprints
        buildings_gdf = ox.features_from_bbox(
            bbox=(north, south, east, west),
            tags={'building': True}
        )
        
        # Convert to GeoDataFrame
        #buildings_gdf = gpd.GeoDataFrame(buildings)
        
        # Create centroids
        centroids_gdf = buildings_gdf.copy()
        centroids_gdf['geometry'] = buildings_gdf.centroid
        
        return buildings_gdf, centroids_gdf
    
    except Exception as e:
        print(f"Error retrieving building data: {e}")
        return None, None

def save_data(buildings_gdf, centroids_gdf, output_dir):
    """Save the GeoDataFrames to files."""
    try:
        # Create output directory
        buildings_path = output_dir / "buildings"
        buildings_path.mkdir(parents=True, exist_ok=True)
        
        # Save the files
        buildings_gdf.to_file(buildings_path / "chicago_buildings.geojson", driver='GeoJSON')
        centroids_gdf.to_file(buildings_path / "chicago_building_centroids.geojson", driver='GeoJSON')
        
        print(f"Data saved successfully to {buildings_path}")
    
    except Exception as e:
        print(f"Error saving data: {e}")

def main():
    # Set output directory
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    
    # Get building data
    print("Retrieving Chicago building data...")
    buildings_gdf, centroids_gdf = get_chicago_buildings()
    
    if buildings_gdf is not None and centroids_gdf is not None:
        print(f"Retrieved {len(buildings_gdf)} buildings")
        save_data(buildings_gdf, centroids_gdf, output_dir)

if __name__ == "__main__":
    main()