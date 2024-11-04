import osmnx as ox
import geopandas as gp
from typing import Union, Tuple, List, Dict
from shapely.geometry import (
    Point,
    Polygon,
    box,
)
from dataclasses import dataclass

@dataclass
class Map:
    """
    A collection of GeoDataFrames with a bounding box.
    In the end we intersect all geometry with the bounding box in order to fit into a square picture.
    """
    gdfs: dict[str, gp.GeoDataFrame]
    bbox_proj: Polygon

def compute_perimeter(
        coordinates: Tuple[float, float],
        dist: float, 
        crs: str = "EPSG:4326"
    ):
    """
    Create two bounding boxes of side length `dist` around `coordinates`.
    The coordiantes are assumed to be in EPSG:4326 format by default.

    The first bbox has projected linear coordinates and can be used later when processing the geometry.
    The second bbox has coordinates according to `crs` and is used to query the OSM api.
    The perimeter is just the second bounding box as a GeoDataFrame to process it together with other geometry.
    """
    # The EPSG projections use long/lat pairs instead of the traditional lat/long.
    lat = coordinates[0]
    long = coordinates[1]

    # Convert the lat/long coordinates to linear coordinates by projecting according to EPSG:4326
    origin = ox.projection.project_gdf(gp.GeoDataFrame(geometry=[Point(long, lat)], crs=crs))

    x = origin.geometry[0].x
    y = origin.geometry[0].y
    # Define a bounding box on linear coodinates and unproject it again to get a bounding box in lat/long coordinates.
    dist2 = dist/2
    bbox_proj = box(x - dist2, y - dist2, x + dist2, y + dist2)
    perimeter = gp.GeoDataFrame(geometry=[bbox_proj], crs=origin.crs).to_crs(crs)
    bbox = box(*perimeter.geometry[0].bounds)
    return bbox_proj, bbox, perimeter

def osm_get_gdf(
        bbox: Polygon,
        layer: str,
        **kwargs
    ) -> Union[gp.GeoDataFrame, None] :
    """
    Get all features/graphs inside an area defined by the bounding box `bbox`.
    Any query parameters for osmnx are directly passed through in `**kwargs`.
    """
    print(f"Get gdf for layer {layer}")

    try:
        if kwargs.pop("is_graph", False):
            G = ox.graph_from_polygon(bbox, **kwargs)
            return ox.graph_to_gdfs(G, nodes=False, edges=True)
        else:
            return ox.features_from_polygon(bbox, **kwargs)
    # Exception thrown on an empty OSM response, e.g. if no feature with this tag exists at that location.
    except:
        return None
    
def osm_get_map(
        layers: Dict[str, dict],
        coordinates: Tuple[float, float],
        dist: float
    ) -> Map:
    """
    Create a Map containing a GeoDataFrame with feature/graph geometry for each layer in `layers`.
    The geometry for each layer will be centered on `coordinates` and fall within a bounding box of side length `dist`.
    """
    bbox_proj, bbox, perimeter = compute_perimeter(coordinates, dist)

    gdfs = {}
    for k, v in layers.items():
        gdf = osm_get_gdf(bbox, k, **v)
        if gdf is not None:
            gdfs[k] = gdf
    gdfs["perimeter"] = perimeter

    return Map(gdfs, bbox_proj)