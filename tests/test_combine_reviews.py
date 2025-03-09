import pytest
from green_spaces.reviews.combine_reviews import combine_reviews
from pathlib import Path

def test_combine_reviews():
    '''
    Test that duplicates are dropped when combining review files
    '''
    directory = Path(__file__).parent / 'data/test_directory_with_duplicate_files'
    combined_reviews = combine_reviews(directory)
    reduced_num_reviews = len(combined_reviews)
    assert reduced_num_reviews == 6, f"Contained {reduced_num_reviews} instead of 6"
    
