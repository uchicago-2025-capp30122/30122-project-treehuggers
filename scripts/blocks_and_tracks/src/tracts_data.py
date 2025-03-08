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

def get_index_to_census_tract(index_points_file, tracts_file):
    """
    Aggregate index values from points to census tract level.
    
    Args:
        index_points_file: Path to GeoJSON with grid points and index values
        tracts_file: Path to shapefile with census tracts
    
    Returns:
        DataFrame with tract IDs and mean index values
    """
    # Read the grid points with index values
    points_gdf = gpd.read_file(index_points_file)
    
    # Read the census tracts
    tracts_gdf = gpd.read_file(tracts_file)
    
    # Make sure CRS match
    if points_gdf.crs != tracts_gdf.crs:
        points_gdf = points_gdf.to_crs(tracts_gdf.crs)
    
    # Spatial join to associate each point with a tract
    joined = gpd.sjoin(points_gdf, tracts_gdf, how="inner", predicate="within")
    
    # Calculate mean index per tract
    # Assuming your index column is named 'index_value' - adjust as needed
    tract_means = joined.groupby("TRACTCE")["index_value"].mean().reset_index()
    
    return tract_means

def main(): 
    path_shape_tracts = pathlib.Path(__file__).parent.parent / "data/raw/census_tracts/il_tracts.shp"
    path_census_data = pathlib.Path(__file__).parent.parent / "data/processed/census/census_data.csv"
    path_index_geojson = pathlib.Path(__file__).parent.parent / "data/processed/index.geojson"
    
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