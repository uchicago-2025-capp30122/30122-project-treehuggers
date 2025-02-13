import httpx
import json

# Define the Overpass API endpoint
overpass_url = "https://overpass-api.de/api/interpreter"

overpass_query = """
[out:json][timeout:120];
// Define Chicago boundary
area[name="Chicago"]->.searchArea;

// Search for ways and nodes for the same tags
(
  way["leisure"="park"](area.searchArea);
  way["landuse"="recreation_ground"](area.searchArea);
  way["leisure"="nature_reserve"](area.searchArea);
  way["leisure"="dog_park"](area.searchArea);
);

// Output results
out body;
>;
out skel qt;
"""

# Make the POST request to Overpass API
response = httpx.post(overpass_url, data={'data': overpass_query}, timeout=120)

# Check if the request was successful
try:
    response = httpx.post(overpass_url, data={'data': overpass_query}, timeout=120)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        with open("OSM_park_ways.json", "w") as f:
            json.dump(data, f, indent=1)
        #print(data)  # Print or process the data
    else:
        print(f"Error: {response.status_code} - {response.text}")
except httpx.RequestError as e:
    print(f"An error occurred: {e}")
except httpx.TimeoutException:
    print("The request timed out.")



"""
[out:json][timeout:120];
// Define Chicago boundary
area[name="Chicago"]->.searchArea;

// Search for ways and nodes for the same tags
(
  way["leisure"="park"](area.searchArea);
  way["landuse"="recreation_ground"](area.searchArea);
  way["leisure"="nature_reserve"](area.searchArea);
  way["leisure"="dog_park"](area.searchArea);
);

// Output results
out body;
>;
out skel qt;
"""

"""
[out:json][timeout:120];
// Define Chicago boundary
area[name="Chicago"]->.searchArea;

// Search for various types of parks and recreational areas, excluding national parks
(
  relation["leisure"="park"](area.searchArea);
  relation["landuse"="recreation_ground"](area.searchArea);
  relation["leisure"="nature_reserve"](area.searchArea);
  relation["leisure"="dog_park"](area.searchArea);
);

// Search for ways and nodes for the same tags
(
  way["leisure"="park"](area.searchArea);
  way["landuse"="recreation_ground"](area.searchArea);
  way["leisure"="nature_reserve"](area.searchArea);
  way["leisure"="dog_park"](area.searchArea);
);

// Output results
out body;
>;
out skel qt;
"""