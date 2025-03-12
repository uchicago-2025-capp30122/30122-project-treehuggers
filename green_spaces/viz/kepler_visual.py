import geopandas as gpd
import pandas as pd
from keplergl import KeplerGl
from pathlib import Path
import json
from shapely.geometry import Point
import traceback
import re


def create_visualization( housing_data, parks_data, tracts_data, output_file, configure):
    """Create and save Kepler visualization."""
    try:
        CHICAGO_CENTER = {
            "latitude": 41.8781,
            "longitude": -87.6298,
            "zoom": 10,
            "pitch": 0,
            "bearing": 0
        }
        
        # First create map without config to let Kepler auto-configure
        kepler_map = KeplerGl(height=1024,
                              data={
                                  'Housing': housing_data, 
                                  'Parks': parks_data, 
                                  'Tracts': tracts_data
                          })
        
        # Apply config after data is loaded
        kepler_map.config = configure
        
        kepler_map.save_to_html(file_name=output_file, read_only=False)
        print(f"Visualization saved to {output_file}")
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
        traceback.print_exc()

def main():
    """Main function to run the visualization process."""
    # Set up file paths
    data_parent = Path(__file__).parent.parent.parent
    path_parks = data_parent / "data/cleaned_park_polygons.geojson"
    path_housing = data_parent / "data/housing_data_index.geojson"
    path_tracts = data_parent / "data/grid_and_tracts/processed/merged/merged_tract_data.geojson"
    output_file = data_parent / "green_spaces/viz/chicago_parks_kepler.html"

    # Load data
    with open(path_parks) as f:
        parks_data = json.load(f)
    with open(path_housing) as f:
        housing_data = json.load(f)
    with open(path_tracts) as f:
        tracts_data = json.load(f)
    
    #path to config
    kepler_config_path = data_parent / "green_spaces/viz/kepler_config2.json"
    with open(kepler_config_path, "r") as f:
        config = json.load(f)
        print("config loaded")

    # Create visualization
    create_visualization(housing_data, parks_data, tracts_data, output_file,
                         config)


if __name__ == "__main__":
    main()