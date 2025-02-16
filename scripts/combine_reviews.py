import json
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent / 'data'

data = []
for source in ["google", "yelp"]:
    input_path = data_dir / f"{source}_reviews_clean.json"
    with open(input_path, "r") as f:
        source_data = json.load(f)
    data.extend(source_data)

output_path = data_dir / "combined_reviews_clean.json"
with open(output_path, "w") as f:
    json.dump(data, f, indent=1)