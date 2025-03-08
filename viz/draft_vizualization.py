import geopandas as gpd
import pandas as pd
from keplergl import KeplerGl
from pathlib import Path
import json
from shapely.geometry import Point

def load_geojson_data(file_path):
    """Load GeoJSON files."""
    try:
        gdf = gpd.read_file(file_path)
        for col in gdf.columns:
            # Check if the column contains complex or unsupported types
            if gdf[col].dtype == 'object':
                # Try to convert to string
                gdf[col] = gdf[col].fillna('').astype(str)
        return gdf
    except Exception as e:
        print(f"Error loading GeoJSON file {file_path}: {e}")
        return None

def process_reviews(file_path):
    """Process reviews JSON file and convert to GeoDataFrame."""
    try:
        geometries = []
        data = []
        
        with open(file_path) as f:
            reviews_data = json.load(f)
            for review in reviews_data:
                geometries.append(Point(review['longitude'], review['latitude']))
                data.append(review)
        
        return gpd.GeoDataFrame(data, geometry=geometries)
    except Exception as e:
        print(f"Error processing reviews file {file_path}: {e}")
        return None

def create_visualization(parks_gdf, housing_gdf, reviews_gdf, output_file):
    """Create and save Kepler visualization."""
    try:
        CHICAGO_CENTER = {
            "latitude": 41.8781,
            "longitude": -87.6298,
            "zoom": 10,
            "pitch": 0,
            "bearing": 0
        }
        
        config = {
            "version": "v1",
            "config": {
                "visState": {
                    "filters": []
                },
                "mapState": CHICAGO_CENTER
            }
        }
        
        kepler_map = KeplerGl(height=600, config = config)
        
        if parks_gdf is not None:
            kepler_map.add_data(data=parks_gdf, name="Chicago Parks")
        if housing_gdf is not None:
            kepler_map.add_data(data=housing_gdf, name="Public Housing Chicago")
        if reviews_gdf is not None:
            kepler_map.add_data(data=reviews_gdf, name="Reviews parks")
        
        kepler_map.save_to_html(file_name=output_file)
        print(f"Visualization saved to {output_file}")
    except Exception as e:
        print(f"Error creating visualization: {e}")

def main():
    """Main function to run the visualization process."""
    # Set up file paths
    data_parent = Path(__file__).parent.parent
    print(data_parent)
    path_parks = data_parent / "data/cleaned_park_polygons.geojson"
    path_housing = data_parent / "data/housing.geojson"
    path_reviews = data_parent / "data/combined_reviews_clean.json"
    output_file = data_parent / "viz/chicago_parks_kepler.html"

    # Load data
    parks_gdf = load_geojson_data(path_parks)
    housing_gdf = load_geojson_data(path_housing)
    reviews_gdf = process_reviews(path_reviews)

    # Create visualization
    create_visualization(parks_gdf, housing_gdf, reviews_gdf, output_file)

if __name__ == "__main__":
    main()