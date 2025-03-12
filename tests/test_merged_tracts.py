import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import pathlib
import numpy as np
from green_spaces.tract_level_analysis.tracts_data import (
    filter_tracts_by_chicago_boundary,
    merge_tract_values,
    get_index_to_census_tract,
    get_housing_units_per_tract
)

# Fixtures for test data
def create_sample_tracts():
    """Create a sample GeoDataFrame with census tracts"""
    # Inside Chicago boundaries
    inside1 = Polygon([
        (-87.7, 41.8),
        (-87.7, 41.9),
        (-87.6, 41.9),
        (-87.6, 41.8),
        (-87.7, 41.8)
    ])
    inside2 = Polygon([
        (-87.7, 41.7),
        (-87.7, 41.75),
        (-87.6, 41.75),
        (-87.6, 41.7),
        (-87.7, 41.7)
    ])
    
    # Outside Chicago boundaries
    outside = Polygon([
        (-88.0, 42.1),
        (-88.0, 42.2),
        (-87.9, 42.2),
        (-87.9, 42.1),
        (-88.0, 42.1)
    ])
    
    # Lake Michigan tract (should be excluded)
    lake = Polygon([
        (-87.5, 41.8),
        (-87.5, 41.9),
        (-87.4, 41.9),
        (-87.4, 41.8),
        (-87.5, 41.8)
    ])
    
    return gpd.GeoDataFrame(
        {
            'TRACTCE': ['001100', '002200', '003300', '990000'],
            'NAME': ['Tract 1', 'Tract 2', 'Tract 3', 'Lake Michigan'],
            'geometry': [inside1, inside2, outside, lake]
        },
        crs="EPSG:4326"
    )

def create_sample_index_points():
    points = [
        Point(-87.65, 41.85),  # In tract 001100
        Point(-87.65, 41.86),  # Also in tract 001100
        Point(-87.65, 41.72),  # In tract 002200
        Point(-87.95, 42.15),  # Outside any test tract
    ]
    
    return gpd.GeoDataFrame(
        {
            'id': [1, 2, 3, 4],
            'rating_index': [0.8, 0.7, 0.6, 0.5],
            'geometry': points
        },
        crs="EPSG:4326"
    )

def create_sample_housing_points():
    points = [
        Point(-87.65, 41.85),  # In tract 001100
        Point(-87.66, 41.86),  # Also in tract 001100
        Point(-87.65, 41.72),  # In tract 002200
    ]
    
    return gpd.GeoDataFrame(
        {
            'id': [1, 2, 3],
            'Units': [50, 30, 100],
            'geometry': points
        },
        crs="EPSG:4326"
    )

# Update your fixtures to use these functions
@pytest.fixture
def sample_tracts_gdf():
    return create_sample_tracts()

@pytest.fixture
def sample_index_points():
    return create_sample_index_points()

@pytest.fixture
def sample_housing_points():
    return create_sample_housing_points()

@pytest.fixture
def data_files():
    """Create and return paths to test data files"""
    # Get the path to the tests directory
    tests_dir = pathlib.Path(__file__).parent
    data_dir = tests_dir / "data"
    
    # Define paths to the test data files
    tracts_path = data_dir / "test_tracts.geojson"
    index_path = data_dir / "test_index.geojson"
    housing_path = data_dir / "test_housing.geojson"
    
    # Create the test data files
    _create_test_data_files(data_dir, tracts_path, index_path, housing_path)
    
    # Return dictionary with paths
    return {
        'tracts_path': str(tracts_path),
        'index_path': str(index_path),
        'housing_path': str(housing_path)
    }

@pytest.fixture
def sample_census_data():
    """Create sample census data for testing"""
    return pd.DataFrame({
        'Tract': ['001100', '002200', '003300'],
        'Median Household Income': [50000, 60000, 70000],
        'Black Population Percentage': [20.5, 35.1, 15.7]
    })


# Update your _create_test_data_files function
def _create_test_data_files(data_dir, tracts_path, index_path, housing_path):
    """Create test data files if they don't exist"""
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    
    # Use the helper functions
    create_sample_tracts().to_file(tracts_path, driver="GeoJSON")
    create_sample_index_points().to_file(index_path, driver="GeoJSON")
    create_sample_housing_points().to_file(housing_path, driver="GeoJSON")

# Basic functionality tests
def test_filter_tracts_by_chicago_boundary(sample_tracts_gdf):
    """Test that Chicago tracts are properly filtered"""
    filtered = filter_tracts_by_chicago_boundary(sample_tracts_gdf)
    
    assert len(filtered) == 2
    assert all(tid in filtered['TRACTCE'].values for tid in ['001100', '002200'])
    assert '990000' not in filtered['TRACTCE'].values  # Lake Michigan excluded
    assert '003300' not in filtered['TRACTCE'].values  # Outside boundary excluded

def test_merge_tract_values(data_files, sample_census_data):
    """Test that tract shapes are correctly merged with census data"""
    merged = merge_tract_values(data_files['tracts_path'], sample_census_data)
    
    assert isinstance(merged, gpd.GeoDataFrame)
    assert 'Tract' in merged.columns
    assert 'Median Household Income' in merged.columns
    assert 'Black Population Percentage' in merged.columns
    assert 'geometry' in merged.columns
    
    # Only Chicago tracts should be included
    assert len(merged) == 2
    assert all(tid in merged['TRACTCE'].values for tid in ['001100', '002200'])
    
    # Check if data was merged correctly
    tract1 = merged[merged['TRACTCE'] == '001100'].iloc[0]
    assert tract1['Median Household Income'] == 50000
    assert tract1['Black Population Percentage'] == 20.5

def test_get_index_to_census_tract(data_files):
    """Test that green space indices are correctly aggregated to census tracts"""
    tract_index = get_index_to_census_tract(
        data_files['index_path'], 
        data_files['tracts_path']
    )
    
    assert isinstance(tract_index, pd.DataFrame)
    assert 'TRACTCE' in tract_index.columns
    assert 'rating_index' in tract_index.columns
    
    tract1_index = tract_index[tract_index['TRACTCE'] == '001100']['rating_index'].values[0]
    tract2_index = tract_index[tract_index['TRACTCE'] == '002200']['rating_index'].values[0]
    
    # Verify aggregated values
    assert np.isclose(tract1_index, 0.75)  # (0.8 + 0.7) / 2
    assert np.isclose(tract2_index, 0.6)

def test_get_housing_units_per_tract(data_files, sample_tracts_gdf):
    """Test that affordable housing units are correctly counted per tract"""
    tract_housing = get_housing_units_per_tract(
        data_files['housing_path'],
        sample_tracts_gdf
    )
    
    assert isinstance(tract_housing, pd.DataFrame)
    assert 'TRACTCE' in tract_housing.columns
    assert 'Affordable_Housing_Units' in tract_housing.columns
    
    # Verify housing unit counts
    tract1_units = tract_housing[tract_housing['TRACTCE'] == '001100']['Affordable_Housing_Units'].values[0]
    tract2_units = tract_housing[tract_housing['TRACTCE'] == '002200']['Affordable_Housing_Units'].values[0]
    
    assert tract1_units == 80  # 50 + 30 units
    assert tract2_units == 100
    
    # Test that tracts with no housing units have 0
    assert len(tract_housing) == 4  # Should include all tracts
    assert tract_housing[tract_housing['TRACTCE'] == '003300']['Affordable_Housing_Units'].values[0] == 0
    assert tract_housing[tract_housing['TRACTCE'] == '990000']['Affordable_Housing_Units'].values[0] == 0