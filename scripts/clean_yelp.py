import json
from pathlib import Path

data_dir = Path(__file__).parent.parent / 'data'
input_path = data_dir / "yelp_reviews_raw.json"


with open(input_path, "r") as f:
    data = json.load(f)

parks = []

for park in data["businesses"]:
    parks.append(
        {
        "name": park["name"],
        "latitude": park["coordinates"]["latitude"],
        "longitude": park["coordinates"]["longitude"],
        "rating": park["rating"],
        "review_count": park["review_count"],      
        "source": "Yelp"
        }
    )

output_path = data_dir / "yelp_reviews_clean.json"
with open(output_path, "w") as f:
    json.dump(parks, f, indent=1)
    
    