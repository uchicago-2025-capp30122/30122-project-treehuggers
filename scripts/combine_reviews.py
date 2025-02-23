import json
from pathlib import Path
from typing import NamedTuple

class Place(NamedTuple):
    name: str
    latitude: float
    longitude: float
    rating: float
    review_count: int
    source: str

DATA_DIR = Path(__file__).parent.parent / 'data'

unique_entries_list = []
for source in ["google", "yelp"]:
    source_data = set()
    paths = list(DATA_DIR.glob(f"{source}_*.json"))
    
    for path in paths:
        with open(path, "r") as f:
            places = json.load(f)
            for place in places:
                source_data.add(Place(
                name=place["name"],
                latitude=place["latitude"],
                longitude=place["longitude"],
                rating=place["rating"],
                review_count=place["review_count"],
                source=place["source"],
            ))
    unique_entries_list.extend(source_data)

lst_data_dicts = []
for row in unique_entries_list:
    lst_data_dicts.append(row._asdict())
        
output_path = DATA_DIR / "combined_reviews_clean.json"
with open(output_path, "w") as f:
    json.dump(lst_data_dicts, f, indent=1)