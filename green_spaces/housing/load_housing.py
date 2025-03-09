import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Load affordable housing data
housing_data = pd.read_csv(
    DATA_DIR / "Affordable_Rental_Housing_Developments_20250201.csv"
)

# Convert Latitude & Longitude into a Geometry Column
housing_data["geometry"] = housing_data.apply(
    lambda row: Point(row["Longitude"], row["Latitude"]), axis=1
)

# Convert Pandas DataFrame to GeoDataFrame
# WGS 84 Coordinate System
housing_geo = gpd.GeoDataFrame(housing_data, geometry="geometry", crs="EPSG:4326")

# Save as a GeoJSON file
housing_geo.to_file(DATA_DIR / "housing.geojson", driver="GeoJSON")
