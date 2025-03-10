import json
from shapely.geometry import shape
from shapely.ops import unary_union
import networkx as nx
from pathlib import Path
import random

random.seed(2024)

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def load_geojson(filepath):
    """
    Loads GeoJSON data from a file and returns the list of park features.

    Args:
        filepath (str): Path to the GeoJSON file

    Returns:
        list: A list of GeoJSON features.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
        features = data["features"]

    return features


def standardize_unnamed_parks(features):
    """
    Standardizes names for unnamed parks in the feature list. If a park is
    missing a name, this function sets the park's name to "Unnamed Park."

    Args:
        features (list): List of GeoJSON features

    Returns:
        list: Updated list of features with standardized names
    """
    for feature in features:
        if not feature["properties"].get("name"):
            feature["properties"]["name"] = "Unnamed Park"

    return features


def get_feature_info(feature):
    """
    Extract the ID, name, and geometry from a feature.

    Args:
        feature (dict): A GeoJSON feature

    Returns:
        tuple: Feature ID, name, and geometry object
    """
    id = feature["properties"].get("id")
    name = feature["properties"].get("name")
    geom = shape(feature["geometry"])
    return id, name, geom


def handle_intersecting_parks(features):
    """
    The function manages intersecting parks in three ways:

    - If an unnamed park intersects with another unnamed park, these parks
    are added as related nodes to an undirected intersection graph, which will
    later be used to merge these parks.
    - If an unnamed park intersects with a named park, the unnamed park is added
    to the unnameds_to_remove return list to be used for later removal.
    - If two named parks intersect, these parks will be added as a tuple to the
    check_containment_parks list, which will later be used to check if one of
    these parks are fully contained within the other.

    Args:
        features (list): List of GeoJSON features

    Returns:
        NetworkX Graph: Graph of unnamed park intersections
        list: list of unnamed park IDs to remove
        list: list of intersecting named park pairs for containment checks.
    """
    # initialize empty undirected graph
    G = nx.Graph()
    unnameds_to_remove = []
    check_containment_parks = []

    # for each pair of parks, check if their geometries intersect (but aren't identical)
    for i, feature1 in enumerate(features):
        id1, name1, geom1 = get_feature_info(feature1)

        for feature2 in features[i + 1 :]:  # to avoid duplicate checks
            id2, name2, geom2 = get_feature_info(feature2)

            if geom1.intersects(geom2) and not geom1.equals(geom2):
                # if we have two unnamed intersecting parks, add edge
                if name1 == "Unnamed Park" and name2 == "Unnamed Park":
                    G.add_edge(id1, id2)
                # if unnamed park intersects with named park, remove unnamed park
                elif name1 == "Unnamed Park" and name2 != "Unnamed Park":
                    unnameds_to_remove.append(id1)
                # if unnamed park intersects with named park, remove unnamed park
                elif name1 != "Unnamed Park" and name2 == "Unnamed Park":
                    unnameds_to_remove.append(id2)
                # if two named parks intersect, add to list to check for containment
                elif name1 != "Unnamed Park" and name2 != "Unnamed Park":
                    check_containment_parks.append((feature1, feature2))

    return G, unnameds_to_remove, check_containment_parks


def create_merged_feature(geometry, merged_id):
    """
    Creates a new GeoJSON feature for merged unnamed parks.

    Args:
        geometry (shapely.geometry): Merged geometry object.
        int: randomly assigned id for new merged feature

    Returns:
        dict: A new GeoJSON feature representing the merged park.
    """

    return {
        "type": "Feature",
        "properties": {
            "element": "way",
            "id": merged_id,
            "ele": None,
            "leisure": "park",
            "name": "Unnamed Merged Park",
        },
        "geometry": json.loads(json.dumps(geometry.__geo_interface__)),
    }
    # geometry.__geo_interface__ is a Shapely attribute that returns a dictionary
    # representation of the geometry in GeoJSON format.


def check_park_containment(check_containment_parks):
    """
    This function checks all intersecting named parks to see if either geometry
    is fully contained within the other. If one is, it is added to a list of
    parks to remove from the cleaned data.

    The list of named_parks_to_remove is initialized with a set of park ids that
    should be removed but wouldn't be captured by this cleaning function due to
    miniscule differences in their boundary coordinates. This function handles
    the removal of those parks manually.

    Args:
        check_containment_parks (list): List of intersecting named park feature pairs

    Returns:
        list: IDs of named parks to remove
    """
    # initialized with hand-selected park IDs to remove
    # these are park IDs that are missed in the cleaning due to small coordinate differences
    named_parks_to_remove = [
        "242304191",
        "747168477",
        "747168489",
        "747184016",
        "747184053",
        "860267019",
    ]

    for feature1, feature2 in check_containment_parks:
        id1, _, geom1 = get_feature_info(feature1)
        id2, _, geom2 = get_feature_info(feature2)

        # if park2 is fully contained within park1, add to remove list
        if geom2.within(geom1):
            named_parks_to_remove.append(id2)
        # if park1 is fully contained within park2, add to remove list
        elif geom1.within(geom2):
            named_parks_to_remove.append(id1)

    return named_parks_to_remove


def get_final_features(features, graph, unnameds_to_remove, named_parks_to_remove):
    """
    This function merges intersecting unnamed parks into single features.
    By using the intersection graph, where nodes are park IDs and edges represent
    intersections, the function groups connected parks, merges their geometries,
    creates and adds their merged feature to the cleaned data, and removes the
    original features of the merged parks.

    The return list of features excludes the given list of unnamed and named parks
    to remove from the data.

    Args:
        features (list): List of GeoJSON features.
        graph (networkx.Graph): Intersection graph of unnamed parks.
        unnameds_to_remove (list): IDs of unnamed parks to remove.
        named_parks_to_remove (list): IDs of named parks to remove.

    Returns:
        list: Updated list of park features, including merged unnamed parks.
    """
    # initialize list to track new merged park features
    merged_features = []
    # initialize set to track park ids that have been merged and should be removed
    merged_ids = set()

    # nx.connected_components(graph) finds all groups of interconnected parks
    # clusters is a list of sets, where each set contains the IDs of intersecting parks
    clusters = [comp for comp in nx.connected_components(graph)]
    # for each cluster of intersecting parks, initialize an empty list to collect the geometries
    for cluster in clusters:
        cluster_geometries = []

        for park_id in cluster:
            for feature in features:
                # for each park ID in the cluster, find the corresponding feature in the original features list
                if feature["properties"].get("id") == park_id:
                    # if match found, add geometry to cluster_geometries
                    cluster_geometries.append(shape(feature["geometry"]))
                    # add park id to merged_ids for removal from features list
                    merged_ids.add(park_id)
                    # assign new random park_id to merged feature
                    new_id = new_id = str(random.randint(1, 100000))
                    # break to ensure we only remove first matching feature
                    break

        # unary_union merges multiple geometries into a single geometry, handling overlaps & adjacent areas
        merged_geometry = unary_union(cluster_geometries)
        # create a new merged feature and append it to the merged_features return list
        merged_features.append(create_merged_feature(merged_geometry, new_id))

    # remaining features are park ids not within merged_ids, unnameds_to_remove, or named_parks_to_remove lists
    remaining_features = [
        feature
        for feature in features
        if feature["properties"].get("id") not in merged_ids
        and feature["properties"].get("id") not in unnameds_to_remove
        and feature["properties"].get("id") not in named_parks_to_remove
    ]

    # add the new merged features to the remaining features list
    remaining_features.extend(merged_features)

    return remaining_features


def save_geojson(features, output_file_path):
    """
    Save the cleaned park features to a JeoJSON file.

    Args:
        features (list): List of cleaned GeoJSON features.
        output_file_path (str): Path to save the output file.
    """
    with open(output_file_path, "w") as f:
        # convert the features list into a GeoJSON FeatureCollection
        json.dump({"type": "FeatureCollection", "features": features}, f, indent=4)

    print("After cleaning, we have", len(features), "parks")


def main():
    """
    Execute the complete park cleaning and merging process.
    """

    file_path = DATA_DIR / "uncleaned_park_polygons.geojson"
    output_path = DATA_DIR / "cleaned_park_polygons.geojson"

    features = load_geojson(file_path)

    # standardize unnamed park names in GeoJSON
    standardized_features = standardize_unnamed_parks(features)

    # retrieve intersection graph, list of unnamed parks to remove, list of intersecting named parks to review
    intersection_graph, unnameds_to_remove, check_containment_parks = (
        handle_intersecting_parks(standardized_features)
    )

    # extract list of named parks to remove
    named_parks_to_remove = check_park_containment(check_containment_parks)

    # merge unnamed park clusters & update features list accordingly
    updated_features = get_final_features(
        features, intersection_graph, unnameds_to_remove, named_parks_to_remove
    )

    # create cleaned parks GeoJSON file
    save_geojson(updated_features, output_path)
    print(f"Chicago Park Data cleaned and saved")


if __name__ == "__main__":
    main()
