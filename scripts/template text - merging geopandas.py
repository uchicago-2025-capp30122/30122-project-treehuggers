import json
from pathlib import Path
import jellyfish as jf 
import geopandas as gpd 
from shapely.geometry import Point, MultiPoint

data_dir = Path(__file__).resolve().parent.parent / 'data'
yelp_path = data_dir / "yelp" / "yelp_cleaned.json"
google_path = data_dir / "google_reviews.json"

# Import 
with open(yelp_path, "r") as f:
        yelp_parks = json.load(f)

with open(google_path, "r") as f:
        google_parks = json.load(f)

# Remove me 
google_lower = [
    {k.lower(): v for k, v in d.items()} for d in google_parks
]
google_parks = google_lower

# Create Yelp geopandas df 
yelp_index = []
for i, yelp_park in enumerate(yelp_parks):
    yelp_index.append(i)
    yelp_park["point"] = Point(yelp_park["longitude"], yelp_park["latitude"])
yelp_df = gpd.GeoDataFrame(yelp_parks, geometry="point", index=yelp_index)
yelp_df.set_crs('EPSG:4326', inplace=True)

# Create Google geopandas df 
for i, google_park in enumerate(google_parks):
     p = Point(google_park["longitude"], google_park["latitude"])
     google_park["point"] = p
     google_park["buffer"] = p.buffer(.01)

google_df = gpd.GeoDataFrame(google_parks, geometry="buffer")
google_df.set_crs('EPSG:4326', inplace=True)

    
result = gpd.sjoin(google_df, yelp_df, how='left', predicate='intersects')
print(result)
output_path = data_dir / "merged_reviews.csv"
result.to_csv(output_path, index=False)