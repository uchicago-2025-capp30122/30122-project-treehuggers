import json
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent / 'data'
input_path = data_dir / "yelp/yelp.json"


with open(input_path, "r") as f:
    data = json.load(f)

parks = []

for park in data["businesses"]:
    parks.append(
        {
        "yelp_name": park["name"],
        "yelp_rating": park["rating"],
        "yelp_review_count": park["review_count"],
        "latitude": park["coordinates"]["latitude"],
        "longitude": park["coordinates"]["longitude"]
        }
    )

output_path = data_dir / "yelp/yelp_cleaned.json"
with open(output_path, "w") as f:
    json.dump(parks, f, indent=1)
    
    