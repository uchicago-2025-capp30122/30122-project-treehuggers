import pytest
from green_spaces.reviews.reviews_utils import cache_key

@pytest.fixture
def sample_yelp_inputs():
    '''
    Yelp API URL and headers to use in data pull
    '''
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"location": "Chicago", 
               "sort_by": "best_match",
               "categories": "parks"
            }
    return (url, headers)

@pytest.fixture
def sample_google_inputs():
    '''
    Google API URL and headers to use in data pull
    '''
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    headers = {"radius": "3590", 
               "keyword": "stadium",
            }
    return (url, headers)

def test_cache_key_yelp(sample_yelp_inputs):
    '''
    Test that the cache key is correctly generated for Yelp inputs
    '''
    url, headers = sample_yelp_inputs
    key = cache_key(url, headers)
    correct_key = "api.yelp.comv3businessessearch_location_Chicago.json" + \
                  "_sort_by_best_match.json_categories_parks.json"
    assert key == correct_key, \
        "Cache key incorrect, is {key} instead of {correct_key}"
        
        
def test_cache_key_google(sample_google_inputs):
    '''
    Test that the cache key is correctly generated for Google inputs
    '''
    url, headers = sample_google_inputs
    key = cache_key(url, headers)
    correct_key = "maps.googleapis.commapsapiplacenearbysearchjson" + \
                  "_radius_3590.json_keyword_stadium.json"
    assert key == correct_key, \
        "Cache key incorrect, is {key} instead of {correct_key}"