import pytest
import geopandas as gpd
from green_spaces.index.index import create_buffer, create_parks_dict
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'

@pytest.fixture
def housing_data():
    housing_data = gpd.read_file(DATA_DIR/"test_housing_data_index.geojson")
    return housing_data

@pytest.fixture
def parks_data():
    parks_data = gpd.read_file(DATA_DIR/"test_cleaned_park_polygons.geojson")
    return parks_data

@pytest.fixture
def ratings_data():
    ratings_data = gpd.read_file(DATA_DIR/"test_buffered_ratings.geojson")
    return ratings_data


def test_houses_without_reviews(housing_data):
    """Ensure rating index is never equal to 0"""
    assert (housing_data["rating_index"] != 0).all()
    
    
def test_geodataframe_crs(housing_data, distance=1000):
    """Check if the housing GeoDataFrame was converted back to EPSG:4326."""
    housing = create_buffer(housing_data, distance)
    assert housing.crs == "EPSG:4326", f"Expected EPSG:4326 but got {housing.crs}"
    

def test_parks_dict(parks_data, ratings_data):
    """Confirm all parks from raw data exist in parks dictionary"""
    parks_dict = create_parks_dict(parks_data, ratings_data)
    assert len(parks_dict) == len(parks_data), f"Expected length \
        {len(parks_data)} but got length {len(parks_dict)}"
    
    