from shapely.geometry import Point, Polygon
from typing import NamedTuple
import geopandas as gpd
import pathlib
import shapefile


class Tract(NamedTuple):
    id: str
    name: str
    polygon: Polygon


def load_shapefiles(path: pathlib.Path) -> Tract:
    """
    Extract and parse polygons from Census shapefiles.
    """
    tracts = []
    with shapefile.Reader(path) as sf:
        # This iterates over all shapes with their associated data.
        for shape_rec in sf.shapeRecords():
            # the shape_rec object here has two properties of interest
            #    shape_rec.record - dict containing the data attributes
            #                       associated with the shape
            #    shape_rec.shape.points - list of WKT points, used to construct
            #                             a shapely.Polygon
            tracts.append(
                Tract(
                    id=shape_rec.record["TRACTCE"],
                    name=shape_rec.record["NAMELSAD"],
                    polygon=Polygon(shape_rec.shape.points),
                )
            )
    return tracts


def shapes_to_geojson(tracts, path):
    """
    Convert list of Tract namedtuples to GeoJSON and save to file.

    Args:
        tracts: List of Tract namedtuples
        path: Path where the GeoJSON file will be saved
    """
    # Create lists in a single pass through the data
    data = {"id": [], "name": [], "geometry": []}

    for tract in tracts:
        data["id"].append(tract.id)
        data["name"].append(tract.name)
        data["geometry"].append(tract.polygon)

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(data)

    # Save to GeoJSON
    gdf.to_file(path, driver="GeoJSON")
