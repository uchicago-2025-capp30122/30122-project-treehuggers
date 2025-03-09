import cenpy as cp
import pandas as pd
from pathlib import Path
from typing import List

def get_census_data(year, variables: List[str], geo_level='tract'):
    """
    Retrieve census data for Chicago at the specified geographic level.

    Args:
        year (str): Census year (e.g., '2019')
        variables (list): List of census variable codes to retrieve
        geo_level (str): Geographic level ('tract' or 'block group')

    Returns:
        DataFrame: Census data for the specified variables and geography
    """
    try:
        # Connect to the ACS 5-year dataset
        dataset = f'ACSDT5Y{year}'
        conn = cp.remote.APIConnection(dataset)

        # Define Cook County, Illinois (FIPS code 17031) to encompass Chicago
        state_fips = '17'  # Illinois
        county_fips = '031'  # Cook County

        # Query the specified variables at the geographic level
        data = conn.query(
            variables,
            geo_unit=geo_level,
            geo_filter={'state': state_fips, 'county': county_fips}
        )
        print("Columns in the DataFrame:", data.columns)
        return data

    except Exception as e:
        print(f"Error retrieving census data: {e}")
        return None
    
def main():
    
    year = '2022'
    variables = ['B19013_001E', 'B02001_001E', 'B02001_003E']
    geo_level = 'tract'

    # Fetch the data
    output_dir = Path(__file__).parent.parent.parent / "data" / "grid_and_tracts" / "processed" / "census"
    output_dir.mkdir(parents=True, exist_ok=True)
    census_data = get_census_data(year, variables, geo_level)

    if census_data is not None:
        # Calculate the percentage of the Black population
        census_data['Black_Percentage'] = (
            census_data['B02001_003E'].astype(float) / census_data['B02001_001E'].astype(float)
        ) * 100

        # Select relevant columns and change the columns
        census_data = census_data[['state', 'county', 'tract', 'B19013_001E', 'Black_Percentage']]
        census_data.columns = ['State', 'County', 'Tract', 'Median Household Income', 'Black Population Percentage']
        
        census_data['Tract'] = census_data['Tract'].astype(str)
        output_path = output_dir / "census_data.csv"
        census_data.to_csv(output_path, index=False)
        print(census_data.head())
    else:
        print("No data retrieved.")
        
if __name__ == "__main__":
    main()