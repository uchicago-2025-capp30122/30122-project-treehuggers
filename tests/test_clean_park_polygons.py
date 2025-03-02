import pytest
import json
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union
import networkx as nx
import sys

from scripts.clean_park_polygons import (
    load_geojson,
    standardize_unnamed_parks,
    get_feature_info,
    handle_unnamed_parks,
    create_merged_feature,
    check_park_containment,
    merge_unnamed_park_clusters,
    save_geojson,
    main
)

@pytest.fixture
def test_data():
    """
    This fixture provides the test dataset as a Python dictionary.
    The data includes named, unnamed, and intersecting parks.

    This fixture creates a sample dataset simulating raw park data in GeoJSON
    format. The test data consists of unnamed parks, named parks, intersecting
    parks, and parks fully contained within another park. This test data is used
    to check that the functions within clean_park_polygons.py are properly 
    identifying and handling unnamed parks, checking for park containment, 
    and merging park clusters.

    The test data covers several edge cases:
    - Parks with no name (unnamed parks) that should be standardized.
    - Parks with names that should remain untouched in the process.
    - Parks with overlaps to test merging and removal logic.
    - Parks fully contained within another park to test removal logic.

    Returns:
        str: The path to the test GeoJSON data file used for testing.

    Explanation of the test data:
Unnamed Park 1 and Unnamed Park 2:

These two unnamed parks intersect with each other. According to your test cases, they should be merged into one park.
Unnamed Park 1 and Named Park 1:

Unnamed parks that intersect with a named park should be removed. In this case, Unnamed Park 1 intersects with Named Park 1, so Unnamed Park 1 should be removed from the dataset.
Named Park 1 and Named Park 2:

These two parks intersect but none is fully contained within the other, so they should remain separate in the dataset.
Named Park 1 and Named Park 3:

Named Park 3 is fully contained within Named Park 1. Therefore, Named Park 3 should be removed from the dataset, as per your specification for named parks intersecting with full containment.
    """
    # Define the test parks as polygons with sample coordinates
    unnamed_park_1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])  # Unnamed park 1
    unnamed_park_2 = Polygon([(1, 1), (1, 3), (3, 3), (3, 1)])  # Unnamed park 2 (intersects unnamed_park_1)
    named_park_1 = Polygon([(4, 0), (4, 2), (6, 2), (6, 0)])    # Named park 1
    named_park_2 = Polygon([(5, 1), (5, 3), (7, 3), (7, 1)])    # Named park 2 (intersects named_park_1, but not contained)
    named_park_3 = Polygon([(4.5, 0.5), (4.5, 1.5), (5.5, 1.5), (5.5, 0.5)])  # Named park 3 (contained in named_park_1)

    # Create GeoJSON structure with park properties
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": geojson.utils.dumps(unnamed_park_1), "properties": {"name": None}},
            {"type": "Feature", "geometry": geojson.utils.dumps(unnamed_park_2), "properties": {"name": None}},
            {"type": "Feature", "geometry": geojson.utils.dumps(named_park_1), "properties": {"name": "Park 1"}},
            {"type": "Feature", "geometry": geojson.utils.dumps(named_park_2), "properties": {"name": "Park 2"}},
            {"type": "Feature", "geometry": geojson.utils.dumps(named_park_3), "properties": {"name": "Park 3"}},
        ]
    }

    return geojson_data


def test_check_park_containment(test_data):
    """
    If two named parks intersect with one another, the cleaning script should
    check if either of these two parks are fully contained within the other. If
    one named park is fully contained within another named park, then that 
    named park should be removed from the data. If the two intersecting named
    parks are not fully contained within one another, both named parks should
    remain in the data.

    This test checks that the above functionality is properly working.
    """
    features = test_data["features"]
    intersection_graph, unnameds_to_remove, check_containment_parks = handle_unnamed_parks(features)
    
    # Check which named parks are fully contained in other parks
    named_parks_to_remove = check_park_containment(check_containment_parks)
    
    # Park 3 should be removed as it is fully contained within Park 1
    assert "Park 3" in named_parks_to_remove
    # Park 2 is not fully contained in Park 1 so should not be marked for removal
    assert "Park 2" not in named_parks_to_remove


def test_handle_unnamed_parks(test_data):
    """
    This test checks if unnamed parks that intersect with each other are merged 
    and unnamed parks that intersect named parks are removed.

    THIS TEST COULD CHECK ALL MERGING FEATURES IN ONE !!!
    LIKE WE DON"T NECESSARILY NEED TO EVEN HAVE A SINGLE OTHER TEST FUNCTION
    IF WE JUST CHECK THAT ALL CASES ARE IN THE FINAL ONE
    """
    features = test_data["features"]

    intersection_graph, unnameds_to_remove, check_containment_parks = handle_unnamed_parks(features)

    # extract list of named parks to remove
    named_parks_to_remove = check_park_containment(check_containment_parks)

    # get final features list
    updated_features = merge_unnamed_park_clusters(features, intersection_graph, unnameds_to_remove, named_parks_to_remove)

    # Unnamed park 1 and 2 intersect, and should be merged into one
    # Therefore Unnamed Park 1 and Unnamed Park 2 shouldn't be in final updated_features list
    

    
    # CREATE ASSERTIONS ACCORDINGLY!!