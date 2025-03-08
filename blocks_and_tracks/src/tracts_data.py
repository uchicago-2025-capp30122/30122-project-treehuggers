import pathlib
import geopandas as gpd
import pandas as pd


def merge_tract_values(shape_path, data):
    """
    Merge the shape data with matches
    """
    shape_gdf = gpd.read_file(shape_path)
    
    merged_df = shape_gdf.merge(
        data, 
        left_on = 'TRACTCE',
        right_on = 'Tract', 
        how = 'inner' #Keep only matches
    )
    
    return  merged_df

def get_index_to_census_tract(points_path):
    """
    Create an housing_parks index for all the city of Chicaago
    """
    
    #First, we call the function to calculate an index for each point 
    


def main(): 
    path_shape_tracts = pathlib.Path(__file__).parent.parent / "data/raw/census_tracts/il_tracts.shp"
    path_census_data = pathlib.Path(__file__).parent.parent / "data/processed/census/census_data.csv"
    output_dir = pathlib.Path(__file__).parent.parent / "data/processed/merged"
    
    # Read census data
    census_data = pd.read_csv(path_census_data, dtype={'Tract': str})
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Merge data
    merged_gdf = merge_tract_values(path_shape_tracts, census_data)
    
    # Save merged data as GeoJSON
    output_path = output_dir / "merged_tract_data.geojson"
    merged_gdf.to_file(output_path, driver='GeoJSON')
    print(f"Merged data saved to {output_path}")
    
    
if __name__ == "__main__":
    main()