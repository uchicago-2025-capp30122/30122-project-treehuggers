import pytest
from scripts.yelp import cache_key, cached_yelp_get, clean_yelp
from scripts.google import cached_google_get, clean_google


@pytest.fixture
def sample_yelp_inputs():
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"location": "Chicago", 
               "sort_by": "best_match",
               "categories": "parks"
            }
    return (url, headers)

def test_cache_key(sample_yelp_inputs):
    url, headers = sample_yelp_inputs
    key = cache_key(url, headers)
    correct_key = "api.yelp.comv3businessessearch_location_Chicago.json" + \
                  "_sort_by_best_match.json_categories_parks.json"
    assert key == correct_key, \
        "Cache key incorrect, is {key} instead of {correct_key}"
    
def test_cached_yelp_get(sample_yelp_inputs):
    