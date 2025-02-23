# We need to see if we have intersecting polygons/duplicates
# as a result of using multiple tags per park.

import json
from shapely.geometry import shape
from shapely.ops import unary_union
import networkx as nx

def load_geojson(filepath):
    """
    Loads GeoJSON data from a file and returns the list of parks
    """
    with open(filepath, "r") as f:
        data = json.load(f)
        features = data["features"]
    return features


def standardize_unnamed_parks(features):
    """
    If a park is missing a name, this function sets the park's name to 
    "Unnamed Park(ID: {id})"
    """
    for feature in features:
        if not feature["properties"].get("name"):
            id = feature["properties"].get("id", "Unknown ID")
            feature["properties"]["name"] = ("Unnamed Park", id)

    return features


def get_feature_info(feature):
    """
    Extract the ID, name, and geometry from a feature.
    """
    id = feature["properties"].get("id")
    name = feature["properties"].get("name")
    geom = shape(feature["geometry"])
    return id, name, geom


def handle_unnamed_parks(features):
    """
    This function handles unnamed parks that intersect with at least one other
    park. This function handles three situations:
    
    1) If an unnamed park intersects with another unnamed park, these parks 
    are to be merged. In order to prepare for that merging, this function builds
    a graph where the nodes are unnamed parks and the edges represent intersections
    between them. This graph will eventually be used to  merge clusters of
    intersecting unnamed parks. Because intersections of unnamed parks are not
    always one-to-one, this avoids merging issues that may arise when an unnamed
    park intersects with more than one other unnamed park. 

    2) If an unnamed park intersects with a named park, the unnamed park should
    be removed from the dataset. This function returns a list of unnamed park
    ids that should be removed from the data.

    3) If two named parks intersect, we will need to check if one of the park
    polygons is fully contained within the other. In that case, we will remove
    the fully contained polygon from out data. To prepare for this operation,
    this function returns a list of tuples, where each tuple contains a pair of
    intersecting features to check containment for.
    """
    # initialize empty undirected graph
    G = nx.Graph()
    unnameds_to_remove = []
    check_containment_parks = []

    # for each pair of parks, check if their geometries intersect (but aren't identical)
    for i, feature1 in enumerate(features):
        id1, name1, geom1 = get_feature_info(feature1)
        
        for feature2 in features[i + 1:]: # to avoid duplicate checks
            id2, name2, geom2 = get_feature_info(feature2)

            if geom1.intersects(geom2) and not geom1.equals(geom2):
                if name1[0] == "Unnamed Park" and name2[0] == "Unnamed Park":
                    # if we have two unnamed parks, add edge.
                    G.add_edge(name1, name2)
                elif name1[0] == "Unnamed Park" and name2[0] != "Unnamed Park":
                    unnameds_to_remove.append(id1)
                elif name1[0] != "Unnamed Park" and name2[0] == "Unnamed Park":
                    unnameds_to_remove.append(id2)
                elif name1[0] != "Unnamed Park" and name2[0] != "Unnamed Park":
                    check_containment_parks.append((feature1, feature2))
    
    return G, unnameds_to_remove, check_containment_parks

def create_merged_feature(geometry):
    """Creates a new GeoJSON feature for the merged unnamed parks."""

    return {
        "type": "Feature",
        "properties": {
            "element": "way",
            "id": "merged",
            "ele": None,
            "leisure": "park",
            "name": "Unnamed Merged Park"
        },
        "geometry": json.loads(json.dumps(geometry.__geo_interface__))
    } #geometry.__geo_interface__ is a Shapely attribute that returns a dictionary
     # representation of the geometry in GeoJSON format. 

def check_park_containment(check_containment_parks):
    """

    """
    named_parks_to_remove = []

    for feature1, feature2 in check_containment_parks:
        id1, name1, geom1 = get_feature_info(feature1)
        id2, name2, geom2 = get_feature_info(feature2)

        # if park2 is fully contained with the parent, add to remove list
        if geom2.within(geom1):
            named_parks_to_remove.append(id2)
        elif geom1.within(geom2):
            named_parks_to_remove.append(id1)

    return named_parks_to_remove


def merge_unnamed_park_clusters(features, graph, unnameds_to_remove, named_parks_to_remove):
    """
    This function merges intersecting unnamed parks into single features.
    By using the intersection graph, where nodes are park IDs and edges represent
    intersections, the function groups connected parks and merges their geometries.

    The function removes the individual intersecting unnamed parks from the 
    original data and replaces them with the merged features in place.

    The function also removes the given list of unnamed parks extracted from 
    the handle_unnamed_parks() function. The unnamed parks set for removal are
    those that can be accounted for under a named park polygon.

    Returns: 
    An updated list of park features, which includes both the original named parks
    and the newly merged unnamed parks. 
    """
    # initialize list to track all new features of merged parks
    merged_features = []
    # initialize set to track the park ids that have been merged and should not
    # exist in their individual form anymore
    merged_ids = set()

    # nx.connected_components(graph) finds all groups of interconnected parks
    clusters = [comp for comp in nx.connected_components(graph)]
    # clusters is a list of sets, where each set contains the IDs of intersecting parks

    # for each cluster of intersecting parks, initialize an empty list to collect the geometries
    for cluster in clusters:
        cluster_geometries = []

        for name, park_id in cluster:
            for feature in features:
                # for each park ID in the cluster, find the corresponding feature in the original features list
                if feature["properties"].get("id") == park_id:
                    # if match found, add geometry to cluster_geometries
                    geometry = feature["geometry"]
                    cluster_geometries.append(shape(feature["geometry"]))
                    # add park id to merged_ids if merged with other park(s) so
                    # that we can remove them from features list
                    merged_ids.add(park_id)
                    # break to ensure we only remove first matching feature
                    break

        # unary_union merges multiple geometries into a single geometry, handling overlaps & adjacent areas
        merged_geometry = unary_union(cluster_geometries)
        # create a new merged feature and append it to the merged_features return list
        merged_features.append(create_merged_feature(merged_geometry))

    # add features that aren't in the unnameds_to_remove

    # keep only features that weren't merged
    remaining_features = [feature for feature in features
                         if feature["properties"].get("id") not in merged_ids and feature["properties"].get("id") not in unnameds_to_remove and feature["properties"].get("id") not in named_parks_to_remove]
   
    # add the new merged features to the remaining features list
    remaining_features.extend(merged_features)

    return remaining_features

def save_geojson(features, output_file_path):
    """
    Save new features list to a cleaned parks_polygons.geojson file.
    """
    with open(output_file_path, "w") as f:
        # convert the features list into a GeoJSON FeatureCollection
        json.dump({"type": "FeatureCollection", "features": features}, f, indent=4)
    
    print(len(features))

def main():
    """Run altogether to clean and merge unnamed park polygons."""

    file_path = "/Users/gracekluender/CAPP-122/30122-project-treehuggers/data/parks_polygons.geojson"
    output_path = "/Users/gracekluender/CAPP-122/30122-project-treehuggers/data/cleaned_park_polygons.geojson" 

    features = load_geojson(file_path)

    # standardize unnamed park names in GeoJSON
    standardized_features = standardize_unnamed_parks(features)

    # retrieve intersection graph, list of unnamed parks to remove, list of intersecting named parks to review
    intersection_graph, unnameds_to_remove, check_containment_parks = handle_unnamed_parks(standardized_features)
    # merge unnamed park clusters & update features list accordingly

    named_parks_to_remove = check_park_containment(check_containment_parks)

    remaining_intersections = [[(feature1["properties"].get("id"), feature1["properties"].get("name")) ,(feature2["properties"].get("id"), feature2["properties"].get("name"))] for feature1, feature2 in check_containment_parks if feature1["properties"].get("id") not in named_parks_to_remove and feature2["properties"].get("id") not in named_parks_to_remove]

    updated_features = merge_unnamed_park_clusters(features, intersection_graph, unnameds_to_remove, named_parks_to_remove)

    # create cleaned parks GeoJSON file
    save_geojson(updated_features, output_path)
    print(f"Unnamed park clusters merged and saved to {output_path}!")



if __name__ == "__main__":
    main()