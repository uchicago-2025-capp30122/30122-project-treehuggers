import pytest
import json
from green_spaces.reviews.reviews_utils import CHICAGO_LOCATIONS
from green_spaces.reviews.google import cached_get_google, clean_google
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'


@pytest.fixture
def sample_google_inputs():
    '''
    Create sample inputs to check cached_get
    '''
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    headers = {"radius": "250", "keyword": "park"}
    return (url, headers)

@pytest.fixture
def morrill_meadow_raw():
    '''
    Example park data to check Google clean 
    '''
    path = Path(DATA_DIR / "test_google_park.json")
    with open(path, "r") as f:
        park = json.load(f)
        return park 

@pytest.fixture
def morrill_meadow_clean():
    '''
    Expected example cleaned park data to check Google clean 
    '''
    return [
        {
        "name": "Morrill Meadow",
        "latitude": 41.6955632,
        "longitude": -87.85792339999999,
        "rating": 4.6,
        "review_count": 108,
        "source": "Google"
        }
        ] 
    
@pytest.fixture
def park_missing_info_raw():
    '''
    Park missing all information except name and source
    '''
    return {"places": [{'name': 'Park Missing Information','source': 'Google'}]} 

@pytest.fixture
def park_missing_info_clean():
    '''
    Expected values for cleaned park missing most information
    '''
    return [{'name': 'Park Missing Information',
                 'latitude': None,
                 'longitude': None,
                 'rating': 0,
                 'review_count': 0, 
                 'source': 'Google'}]
    
def test_cached_get_google(sample_google_inputs):
    '''
    Test that sample get Google inputs result in actually pulling data
    '''
    url, headers = sample_google_inputs
    raw_data_list = cached_get_google(url, headers, CHICAGO_LOCATIONS)["places"]
    assert len(raw_data_list) > 0, "No data pulled from cached get Google"
    
  
def test_clean_google(morrill_meadow_raw, morrill_meadow_clean):
    '''
    Test that raw Morrill Meadow data lead to expected cleaned data
    '''
    clean_park = clean_google(morrill_meadow_raw)
    assert clean_park == morrill_meadow_clean, \
        f"Returned {clean_park} instead of {morrill_meadow_clean}"
        

def test_clean_yelp_park_missing_information(park_missing_info_raw, 
                                             park_missing_info_clean):
    '''
    Test that raw largely missing data lead to expected cleaned data
    '''
    clean_park = clean_google(park_missing_info_raw)
    assert clean_park == park_missing_info_clean, \
         f"Returned {clean_park} instead of {park_missing_info_clean}"
  