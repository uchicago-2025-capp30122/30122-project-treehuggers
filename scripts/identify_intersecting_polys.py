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


def build_intersection_graph(features):
    """
    This function builds a graph where edges represent intersecting unnamed park
    polygons. This graph will merge clusters of intersecting unnamed parks. Because
    intersections of unnamed parks are not always one-to-one, this avoids merging
    issues that may arise when an unnamed park intersects with more than one other
    unnamed park
    """
    # initialize empty undirected graph
    G = nx.Graph()

    # for each pair of parks, check if their geometries intersect (but aren't identical)
    for i, feature1 in enumerate(features):
        id1, name1, geom1 = get_feature_info(feature1)
        
        for feature2 in features[i + 1:]: # to avoid duplicate checks
            id2, name2, geom2 = get_feature_info(feature2)

            if geom1.intersects(geom2) and not geom1.equals(geom2):
                if name1[0] == "Unnamed Park" and name2[0] == "Unnamed Park":
                    # if we have two unnamed parks, add edge.
                    G.add_edge(name1, name2)

    return G

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


def merge_unnamed_park_clusters(features, graph):
    """
    This function merges intersecting unnamed parks into single features.
    By using the intersection graph, where nodes are park IDs and edges represent
    intersections, the function groups connected parks and merges their geometries.

    The function removes the individual intersecting unnamed parks from the 
    original data and replaces them with the merged features in place.

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

    # keep only features that weren't merged
    remaining_features = [feature for feature in features if feature["properties"].get("id") not in merged_ids]
   
    # add the new merged features to the remaining features list
    remaining_features.extend(merged_features)

    return remaining_features

def save_geojson(features, output_file_path):
    """
    Save new features list to a cleaned parks_polygons.geojson file.
    """
    file_path = "/Users/gracekluender/CAPP-122/30122-project-treehuggers/data/merged_park_polygons.geojson"
    with open(file_path, "w") as f:
        # convert the features list into a GeoJSON FeatureCollection
        json.dump({"type": "FeatureCollection", "features": features}, f, indent=4)
    
    print(len(features))

def main():
    """Run the full workflow for cleaning and merging unnamed park polygons."""

    file_path = "/Users/gracekluender/CAPP-122/30122-project-treehuggers/data/parks_polygons.geojson"
    output_path = "/Users/gracekluender/CAPP-122/30122-project-treehuggers/data/merged_parks.geojson" 

    features = load_geojson(file_path)

    # standardize unnamed park names in GeoJSON
    standardized_features = standardize_unnamed_parks(features)

    # create clusters of unnnamed parks to merge
    intersection_graph = build_intersection_graph(standardized_features)

    # merge unnamed park clusters & update features list accordingly
    updated_features = merge_unnamed_park_clusters(features, intersection_graph)

    # create cleaned parks GeoJSON file
    save_geojson(updated_features, output_path)
    print(f"Unnamed park clusters merged and saved to {output_path}!")

if __name__ == "__main__":
    main()