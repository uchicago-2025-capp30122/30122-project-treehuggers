import pytest
import geojson
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union

from green_spaces.parks.clean_park_polygons import (
    standardize_unnamed_parks,
    handle_intersecting_parks,
    create_merged_feature,
    check_park_containment
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
    """
# Define the test parks as polygons with sample coordinates
    # Unnamed park 1
    unnamed_park_1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)]) 
    
    # Unnamed park 2 (intersects unnamed_park_1)
    unnamed_park_2 = Polygon([(1, 1), (1, 3), (3, 3), (3, 1)])  
    
    # Unnamed park 3 (intersects named_park_1)
    unnamed_park_3 = Polygon([(3.5, 1), (3.5, 2.5), (4.5, 2.5), (4.5, 1)]) 
    
    # Named park 1
    named_park_1 = Polygon([(4, 0), (4, 2), (6, 2), (6, 0)])    
    
    # Named park 2 (intersects named_park_1, but not contained)
    named_park_2 = Polygon([(5, 1), (5, 3), (7, 3), (7, 1)])
    
    # Named park 3 (contained in named_park_1)    
    named_park_3 = Polygon([(4.5, 0.5), (4.5, 1.5), (5.5, 1.5), (5.5, 0.5)])  

    # Create GeoJSON structure with park properties
    test_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": mapping(unnamed_park_1), 
             "properties": {"id": '1', "name": None}},
            {"type": "Feature", "geometry": mapping(unnamed_park_2), 
             "properties": {"id": '2', "name": None}},
            {"type": "Feature", "geometry": mapping(unnamed_park_3), 
             "properties": {"id": '6', "name": None}},
            {"type": "Feature", "geometry": mapping(named_park_1), 
             "properties": {"id": '3', "name": "Park 1"}},
            {"type": "Feature", "geometry": mapping(named_park_2), 
             "properties": {"id": '4', "name": "Park 2"}},
            {"type": "Feature", "geometry": mapping(named_park_3), 
             "properties": {"id": '5', "name": "Park 3"}},
        ]
    }

    return test_data


def test_standardize_unnamed_parks(test_data):
    """
    This test checks if all park features in the GeoJSON data have a non-None
    'name' property after running the `standardize_unnamed_parks` function. 

    Args:
        test_data (dict): A GeoJSON dictionary containing park features, 
                          with some parks initially missing names.

    Assertion:
        Every feature's 'name' property is not None after standardization.
    """
    features = test_data["features"]
    standardized_features = standardize_unnamed_parks(features)
    
    # After running standardize_unnamed_parks, all parks should have a name now
    for feature in standardized_features:
        assert feature['properties']['name'] is not None


def test_handle_intersecting_parks(test_data):
    """
    This test checks that the handle_intersecting_parks function is working
    properly. Below is the functionality this test checks for:

    - If an unnamed park intersects with another unnamed park, these parks 
    are added as related nodes to an undirected intersection graph.
    - If an unnamed park intersects with a named park, the unnamed park is added
    to the unnameds_to_remove return list to be used for later removal.
    - If two named parks intersect, these parks will be added as a tuple to the 
    check_containment_parks list, which will later be used to check if one of
    these parks are fully contained within the other. 
    """
    features = test_data["features"]

    standardized_features = standardize_unnamed_parks(features)

    intersection_graph, unnameds_to_remove, check_containment_parks = handle_intersecting_parks(standardized_features)

    # Unnamed Park 3 (id = 6) intersects with Named Park 1, so the id, '6'. should
    # be in the unnameds_to_remove return list
    assert '6' in unnameds_to_remove

    # Unnamed Park 1 (id = 1) and Unnamed Park 2 (id = 2) intersect and should be
    # added as related nodes in the NetworkX intersection_graph
    assert intersection_graph.has_edge('1', '2')

    # Named parks 1, 2, and 3 (id = 3, id = 4, id =5) intersect each other, so
    # they should be in the check_containment_parks list for further review
    assert (features[3], features[4]) in check_containment_parks
    assert (features[3], features[5]) in check_containment_parks

def test_check_park_containment(test_data):
    """ 
    Tests the removal of named parks that are fully contained within another named park.
    
    This function verifies that when a named park is entirely enclosed within 
    another named park, it is correctly identified and removed. It follows these steps:
    
    1. Extracts the park features from the test data.
    2. Standardizes unnamed parks to ensure consistent processing.
    3. Builds an intersection graph to identify overlapping parks.
    4. Checks which named parks are fully contained within others.
    5. Asserts that Named Park 3 (id = 5), which is fully contained within 
       Named Park 1 (id = 3), is included in the removal list.

    Args:
        test_data (dict): A GeoJSON-like dictionary containing park features.

    Raises:
        AssertionError: If Named Park 3 (id = 5) is not detected for removal.
    """
    features = test_data["features"]

    standardized_features = standardize_unnamed_parks(features)

    _, _, check_containment_parks = handle_intersecting_parks(standardized_features)

    named_parks_to_remove = check_park_containment(check_containment_parks)

    # Named Park 3 (id = 5) is fully contained within Named Park 1 (id = 3) so
    # it should be in the named_parks_to_remove list
    assert '5' in named_parks_to_remove


def test_create_merged_feature():
    """
    This function tests the creation of a GeoJSON feature for a merged unnamed
    park.
    
    This test checks that:
    1. The function returns a valid GeoJSON feature.
    2. The feature has the correct properties, including 'id', 'name', and 'leisure'.
    3. The geometry is correctly formatted as a GeoJSON-compliant dictionary.
    """

    # Define test geometry (a simple merged polygon)
    test_merged_geometry = Polygon([(0, 0), (0, 3), (3, 3), (3, 0)])  
    merged_id = '1234567'

    merged_feature = create_merged_feature(test_merged_geometry, merged_id)

    # check that id updated properly
    assert merged_feature["properties"]["id"] == merged_id, "Feature ID should match the merged_id."

    # check that the name updated properly
    assert merged_feature["properties"]["name"] == "Unnamed Merged Park", "Name should be 'Unnamed Merged Park'."

    # Validate that the merged_feature is a proper GeoJSON Feature
    assert geojson.Feature(**merged_feature), "Invalid GeoJSON Feature!"
