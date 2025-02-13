import json 

data_path = "/home/evanfantozzi/capp30122/Project/30122-project-treehuggers/yelp.json"

with open("yelp.json", "r") as f:
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

with open("yelp_cleaned.json", "w") as f:
    json.dump(parks, f, indent=1)
    
    