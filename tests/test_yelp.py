import pytest
import json
from green_spaces.reviews.yelp import cached_get_yelp, clean_yelp
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'

@pytest.fixture
def sample_yelp_inputs():
    '''
    Create sample inputs to check cached_get
    '''
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"location": "Chicago", 
               "sort_by": "best_match",
               "categories": "parks"
            }
    return (url, headers)


@pytest.fixture
def oak_park_raw():
    '''
    Example park data to check Yelp clean 
    '''
    path = Path(DATA_DIR / "test_yelp_park.json")
    with open(path, "r") as f:
        park = json.load(f)
        return park 


@pytest.fixture
def oak_park_clean():
    '''
    Expected example cleaned park data to check Yelp clean 
    '''
    return [{'name': 'Oak Park Conservatory',
             'latitude': 41.87143,
             'longitude': -87.78968,
             'rating': 4.7,
             'review_count': 59, 
             'source': 'Yelp'}] 
    
@pytest.fixture
def park_missing_info_raw():
    '''
    Park missing all information except name and source
    '''
    return {"places": [{'name': 'Park Missing Information','source': 'Yelp'}]} 

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
            'source': 'Yelp'}]
    
def test_cached_get_yelp(sample_yelp_inputs):
    '''
    Test that sample get Yelp inputs result in actually pulling data
    '''
    url, headers = sample_yelp_inputs
    raw_data_list = cached_get_yelp(url, headers)["places"]
    assert len(raw_data_list) > 0, "No data pulled from cached get Yelp"
    
    
def test_clean_yelp(oak_park_clean, oak_park_raw):
    '''
    Test that raw Oak Park data lead to expected cleaned data
    '''
    clean_park = clean_yelp(oak_park_raw)
    assert clean_park == oak_park_clean, \
        f"Returned {clean_park} instead of {oak_park_clean}"
        

def test_clean_yelp_park_missing_information(park_missing_info_raw, 
                                             park_missing_info_clean):
    '''
    Test that raw largely missing data lead to expected cleaned data
    '''
    clean_park = clean_yelp(park_missing_info_raw)
    assert clean_park == park_missing_info_clean, \
         f"Returned {clean_park} instead of {park_missing_info_clean}"
    