# We need to see if we have intersecting polygons/duplicates
# as a result of using multiple tags per park.

from shapely.geometry import shape
import json

# Load GeoJSON data
with open("/Users/gracekluender/CAPP-122/30122-project-treehuggers/data/parks_polygons.geojson") as f:
    data = json.load(f)

features = data["features"]
seen = []  # Track unique geometries
duplicates = set()  # Store duplicate polygon names

# Step 1: Identify and print duplicate polygons (but NOT removing them)
print("Identified duplicate polygons (not removed):")
for feature in features:
    geom = shape(feature["geometry"])
    name = feature["properties"].get("name") or f"Unnamed Park (ID: {feature['properties'].get('id', 'Unknown')})"

    if any(geom.equals(seen_geom) for seen_geom in seen):
        print(f"  - {name}")
        duplicates.add(name)
    else:
        seen.append(geom)

# Step 2: Identify and print intersecting polygons (excluding duplicates)
seen_intersections = set()

print("\nIdentified intersecting polygons (excluding flagged duplicates):")
for i, feature1 in enumerate(features):
    name1 = feature1["properties"].get("name") or f"Unnamed Park (ID: {feature1['properties'].get('id', 'Unknown')})"

    if name1 in duplicates:  # Skip flagged duplicates
        continue

    geom1 = shape(feature1["geometry"])

    for j, feature2 in enumerate(features):
        if i == j:  # Skip self-comparison
            continue

        name2 = feature2["properties"].get("name") or f"Unnamed Park (ID: {feature2['properties'].get('id', 'Unknown')})"

        if name2 in duplicates:  # Skip flagged duplicates
            continue

        geom2 = shape(feature2["geometry"])

        if geom1.intersects(geom2) and not geom1.equals(geom2):
            pair = frozenset([name1, name2])  # Unique unordered pair

            if pair not in seen_intersections:
                print(f"  - {name1} and {name2}")
                seen_intersections.add(pair)  # Store the intersection
print(len(seen_intersections))