import pytest
import geopandas as gpd
from scripts.parks_index import create_buffer, create_parks_dict
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'


@pytest.fixture
def housing_data():
    housing_data = gpd.read_file(DATA_DIR/"housing.geojson")
    return housing_data


def test_houses_without_reviews(housing_data):
    # Ensure every rating_index value is not equal to 0
    assert (housing_data["rating_index"] != 0).all()
    
    
def test_geodataframe_crs(housing_data, distance=1000):
    """Check if the housing GeoDataFrame was converted back to EPSG:4326."""
    housing = create_buffer(housing_data, distance)
    assert housing.crs == "EPSG:4326", f"Expected EPSG:4326 but got {housing.crs}"
    

    
# write a test that compares length of cleaned polygons to length of create_parks_dict()
    
    
