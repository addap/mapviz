import sys
import osmnx as ox
import geopandas as gp
from typing import Union, List, Dict, Type
import shapely
from shapely.geometry.base import BaseGeometry
from shapely.geometry import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    GeometryCollection,
    box,
)

def dilate_graph(
        gdf: gp.GeoDataFrame,
        width: Union[Dict[str, float], float]
    ) -> gp.GeoDataFrame:
    """
    Given a GeoDataFrame containing a graph (street/railway network),
    turn all LineStrings representing streets/railways into polygon strips by dilating by 'width'.
    """

    # Annotate GeoDataFrame with the width for each graph type
    def get_width(v):
        if isinstance(v, list):
            for x in v:
                if w := width.get(x):
                    return w
            return 1
        else:
            return width.get(v, 1)
                
    # Only the streets layer supports different widths.
    # TODO We also query the railway layer by different values (tram/subway/etc.) but these values are not preserved in the geodataframe.
    if isinstance(width, dict) and hasattr(gdf, "highway"):
        gdf["width"] = gdf.highway.map(get_width)
    else:
        gdf["width"] = width

    def dilate(row):
        if type(row.geometry) [LineString, MultiLineString, Point, MultiPoint]:
            return row.geometry.buffer(row.width, cap_style="flat")
        else:
            return row.geometry
    gdf.geometry = gdf.apply(dilate, axis=1)

    return gdf

def scale_geometry(
        geometry: BaseGeometry,
        bbox_src: Polygon,
        bbox_dst: Polygon,
    ) -> BaseGeometry:
    """
    Project a geometry from one frame of reference defined by a bounding box `bbox_src` to another defined by `bbox_dst`.
    """
    minx1, miny1, maxx1, maxy1 = bbox_src.bounds
    minx2, miny2, maxx2, maxy2 = bbox_dst.bounds
    
    # 1. Move everything to the origin.
    # 2. Scale from the size of `bbox_src` to the size of `bbox_dst`.
    # 3. Move everything into `bbox_dst`.
    g = shapely.affinity.translate(geometry, -minx1, -miny1)
    g = shapely.affinity.scale(g, (maxx2 - minx2) / (maxx1 - minx1), (maxy2 - miny2) / (maxy1 - miny1), origin=(0, 0))
    g = shapely.affinity.translate(g, minx2, miny2)
    return g

def classify_shapes(
        geometry: BaseGeometry
    ) -> Dict[Type, List[Union[Polygon, LineString, Point]]]:
    """
    Flatten a hierarchy of geometries (i.e. GeometryCollection, MultiPolygon, MultiLineString)
    into a dictionary of simple shapes (Polygon, LineString, Point).
    
    TODO: since we dilate all points and linestrings into polygons we should actually have only polygons left. 
    But I'm not sure if the geometry operations afterwards could result in new lines/points being created so leave it in for now.
    """
    # Stack of geometries that we still need to process.
    stack: List[BaseGeometry] = [geometry]
    shapes = {
        Polygon: [],
        LineString: [],
        Point: []
    }

    while len(stack) > 0:
        shape = stack.pop()
        # case for nested geometries like GeometryCollection, MultiPolygon, MultiLineString etc.
        if hasattr(shape, 'geoms'):
            stack.extend(shape.geoms)
        elif type(shape) in shapes:
            shapes[type(shape)].append(shape)
        else:
            print(f"Unknown shape: {shape}", file=sys.stderr)
    return shapes

def shapely_of_gdf(
    gdf: gp.GeoDataFrame,
    bbox_src: Polygon,
    size: int,
    width: Union[Dict[str, float], float],
    overdraw: bool = False,
) -> BaseGeometry:
    """
    Convert a single GeoDataFrame `gdf` to a shapely geometry and scale it to fit into a bounding box of side length `size` and anchored at the origin.
    Any line & point geometries will be dilated into polygon stripes by using `width`. 
    By default, the geometry will be intersected with the destination bounding box to only keep geometry that is inside.
    """

    gdf = ox.projection.project_gdf(gdf)
    gdf = dilate_graph(gdf, width=width)
    
    bbox_dst = box(0, 0, size, size)

    geometry = GeometryCollection(geoms=gdf.geometry.tolist())
    geometry = shapely.ops.unary_union(geometry)
    geometry = scale_geometry(geometry, bbox_src, bbox_dst)
    geometry = shapely.ops.unary_union(geometry)

    if not overdraw:
        geometry = bbox_dst.intersection(geometry)

    return geometry