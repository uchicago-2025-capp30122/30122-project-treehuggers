import pytest
import json
from scripts.import_utils import cache_key
from scripts.yelp import cached_get_yelp, clean_yelp
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'

@pytest.fixture
def sample_yelp_inputs():
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"location": "Chicago", 
               "sort_by": "best_match",
               "categories": "parks"
            }
    return (url, headers)


@pytest.fixture
def oak_park_raw():
    path = Path(DATA_DIR / "test_yelp_park.json")
    with open(path, "r") as f:
        park = json.load(f)
        return park 


@pytest.fixture
def oak_park_clean():
    return [{'name': 'Oak Park Conservatory',
             'latitude': 41.87143,
             'longitude': -87.78968,
             'rating': 4.7,
             'review_count': 59, 
             'source': 'Yelp'}] 
    
    
def test_cached_get_yelp(sample_yelp_inputs):
    url, headers = sample_yelp_inputs
    raw_data_list = cached_get_yelp(url, headers)["places"]
    assert len(raw_data_list) > 0, "No data pulled from cached get Yelp"
    
    
def test_clean_yelp(oak_park_clean, oak_park_raw):
    clean_park = clean_yelp(oak_park_raw)
    assert clean_park == oak_park_clean, \
        "Returned {clean_park} instead of {oak_park_conservatory_yelp}"