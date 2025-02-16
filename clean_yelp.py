import json 
import geopandas as gpd

# we should probably update this path so that it is relative to the directory
data_path = "/home/evanfantozzi/capp30122/Project/30122-project-treehuggers/yelp.json"

with open("data/yelp/yelp.json", "r") as f:
    data = json.load(f)

parks = []

for park in data["businesses"]:
    parks.append(
        {
        "name": park["name"],
        "rating": park["rating"],
        "review_count": park["review_count"],
        "latitude": park["coordinates"]["latitude"],
        "longitude": park["coordinates"]["longitude"],
        "location": park["location"]
        }
    )

with open("data/yelp/yelp_cleaned.json", "w") as f:
    json.dump(parks, f, indent=2)
    



    
    