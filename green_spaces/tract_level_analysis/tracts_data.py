import pathlib
import geopandas as gpd
import pandas as pd
from .grid_chicago import get_boundaries_polygon

def filter_tracts_by_chicago_boundary(tracts_gdf):
    """
    Filter census tracts to only those within Chicago's boundaries.
    """
    # Chicago approximate boundaries
    north, south, east, west = 42.0230374, 41.6328758, -87.5240812, -87.8824214
    
    # Filter tracts within Chicago boundaries
    chicago_tracts = tracts_gdf.cx[west:east, south:north]
    
    # Exclude Lake Michigan (tract ID 990000)
    chicago_tracts = chicago_tracts[chicago_tracts['TRACTCE'] != '990000']
    return chicago_tracts


def merge_tract_values(shape_path, data):
    """
    Merge the shape data with a dataframe we choose
    """
    shape_gdf = gpd.read_file(shape_path)
    
    # Filter for Chicago tracts
    shape_gdf = filter_tracts_by_chicago_boundary(shape_gdf)
    
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
    
    # CRS have to match
    if points_gdf.crs != tracts_gdf.crs:
        points_gdf = points_gdf.to_crs(tracts_gdf.crs)
    
    # Spatial join to associate each point with a tract
    joined = gpd.sjoin(points_gdf, tracts_gdf, how="inner", predicate="within")
    
    # Calculate mean index per tract
    tract_means = joined.groupby("TRACTCE")["rating_index"].mean().reset_index()
    
    return tract_means

def get_housing_units_per_tract(housing_geojson_path, tracts_gdf):
    """
    Count the number of affordable housing units in each census tract.
    
    Args:
        housing_geojson_path: Path to GeoJSON with affordable housing data
        tracts_gdf: GeoDataFrame with census tracts
    
    Returns:
        DataFrame with tract IDs and total housing units
    """
    # Read the housing data
    housing_gdf = gpd.read_file(housing_geojson_path)
    
    # Make sure CRS matches
    if housing_gdf.crs != tracts_gdf.crs:
        housing_gdf = housing_gdf.to_crs(tracts_gdf.crs)
    
    # Spatial join to associate each housing point with a tract
    joined = gpd.sjoin(housing_gdf, tracts_gdf, how="right", predicate="within")
    
    # Sum the units per tract
    # Handle null values in the 'Units' column
    joined['Units'] = joined['Units'].fillna(0)
    
    # Calculate sum of units per tract
    tract_housing = joined.groupby("TRACTCE")["Units"].sum().reset_index()
    tract_housing.rename(columns={"Units": "Affordable_Housing_Units"}, inplace=True)
    
    return tract_housing

def main(): 
    main_data_path = pathlib.Path(__file__).parent.parent.parent
    path_shape_tracts = main_data_path / "data/grid_and_tracts/raw/census_tracts/il_tracts.shp"
    path_census_data = main_data_path / "data/grid_and_tracts/processed/census/census_data.csv"
    path_index_geojson = main_data_path / "data/grid_and_tracts/processed/grid/index.geojson"
    path_housing_geojson = main_data_path / "data/housing.geojson"  
    output_dir = main_data_path / "data/grid_and_tracts/processed/merged"
    
    # Read census data
    census_data = pd.read_csv(path_census_data, dtype={'Tract': str})
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    merged_gdf = merge_tract_values(path_shape_tracts, census_data)
    
    # Get mean index per tract
    tract_index = get_index_to_census_tract(path_index_geojson, path_shape_tracts)
    housing_units = get_housing_units_per_tract(path_housing_geojson, merged_gdf)
    # Add index data to the merged data
    final_gdf = merged_gdf.merge(
        tract_index,
        on="TRACTCE",
        how="left"
    )
    final_gdf = final_gdf.merge(
        housing_units,
        on="TRACTCE",
        how="left"
    )
    
    final_gdf['Affordable_Housing_Units'] = final_gdf['Affordable_Housing_Units'].fillna(0)
    #Only necessary columns
    columns_to_keep = ["TRACTCE", "Median Household Income", "Black Population Percentage",
                       "rating_index", "Affordable_Housing_Units", "geometry"]
    final_gdf = final_gdf[columns_to_keep]
    
    # Save merged data as GeoJSON
    output_path = output_dir / "merged_tract_data.geojson"
    final_gdf.to_file(output_path, driver='GeoJSON')
    print(f"Merged data saved to {output_path}")
    
    
if __name__ == "__main__":
    main()