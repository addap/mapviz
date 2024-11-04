
import sys
from typing import Union, List, Dict
import shapely
from shapely.geometry.base import BaseGeometry
from shapely.geometry import (
    Point,
    LineString,
    Polygon,
)
import svg
from random import randint

from .map import Map
from .geometry import shapely_of_gdf, classify_shapes

def get_color(**kwargs):
    if fc := kwargs.get("fc", None):
        assert(type(fc) == str)
        return fc
    if palette := kwargs.get("palette", None):
        assert(type(palette) == list)
        rand_idx = randint(0, len(palette)-1)
        return palette[rand_idx]
    else:
        return "black"


def svg_of_poly(
        poly: Polygon,
        **kwargs
    ) -> List[svg.Element]:
    """
    Create an SVG polygon from a shapely polygon.
    For a polygon without interior rings (i.e. holes) we can directly use the svg polygon constructor.
    If there are holes we define svg paths from the linear rings. The "evenodd" fill rule ensures that 
    the inside of a hole is not filled in since there are two paths between the hole and the outside
    area of the polygon.
    """
    if len(poly.interiors) > 0:
        # start with a "moveto" and then "lineto" for all further coordinates.
        def path_of_coords(r):
            return [svg.M(*r[0])] + [svg.L(*c) for c in r[1:]]

        ds = path_of_coords(poly.exterior.coords)
        for interior in poly.interiors:
            ds += path_of_coords(interior.coords)

        return [
            svg.Path(
                d=ds,
                fill_rule="evenodd",
                fill=get_color(**kwargs),
                stroke=kwargs.get("ec", "black"),
                stroke_width=kwargs.get("lw", 1),
            )
        ]
    else:
        return [
            svg.Polygon(
                points=[*poly.boundary.coords],
                fill=get_color(**kwargs),
                stroke=kwargs.get("ec", "black"),
                stroke_width=kwargs.get("lw", 1),
            )
        ]

def svg_of_shapely(
    geometry: BaseGeometry,
    **kwargs,
) -> List[svg.Element]:
    """
    Translate shapely geometries into their equivalent SVG element and add styling.
    """
    shapes = classify_shapes(geometry) 
    elements = []
    for poly in shapes[Polygon]:
        elements += svg_of_poly(poly, **kwargs)
    for line in shapes[LineString]:
        print("WARN: LineString remains in output geometry which should have been dilated into a Polygon", file=sys.stderr)
        elements.append(
            svg.Polyline(
                points=[*line.coords],
                stroke=kwargs.get("ec", "black"),
                stroke_width=kwargs.get("lw", 1),
            )
        )
    for point in shapes[Point]:
        elements.append(
            svg.Circle(
                cx=point.x, 
                cy=point.y,
                r=1,
                fill=get_color(**kwargs),
                stroke=kwargs.get("ec", "black"),
                stroke_width=kwargs.get("lw", 1),
            )
        )

    return elements
    
def svg_of_gdf(
    layer: str,
    map: Map,
    size: int,
    width: Union[Union[dict, float], float] = 1,
    **kwargs,
) -> List[svg.Element]:
    """
    Create SVG elements from the GeoDataFrame of a single Map layer.
    First extract the shapely geometries from the gdf and then map them 
    to the closest equivalent in SVG.
    """
    geometry = shapely_of_gdf(map.gdfs[layer], map.bbox_proj, width=width, size=size)
    # SVG y axis grows downwards so mirror y axis at center.
    geometry = shapely.ops.transform(lambda x, y: (x, size - y), geometry)

    elements = svg_of_shapely(geometry, **kwargs)
    return elements

def generate_svg(
        map: Map,
        filepath: str,
        size: int,
        styles: Dict[str, dict],
        css_prefix = "mapviz"
    ):
    """
    Generate an SVG image from a `map` object and save it to the given `filepath`.
    The internal coordinate system will go from 0 to `size`.
    Each layer is styled according to `styles[layer]`.
    All SVG elements will be tagged with a CSS class with prefix `css_prefix`.
    """
    elements = []
    # Go through the layers by zorder since later elements in an SVG are drawn on top of earlier elements.
    for layer in sorted(styles, key=lambda style: styles[style].get("zorder", 0)):
        if layer in map.gdfs:
            layer_elements = svg_of_gdf(layer, map, size=size, **styles[layer])

            # We tag all elements in a layer with a CSS class to identify them later.
            for e in layer_elements:
                e.class_ = f"{css_prefix}-{layer}"
            elements += layer_elements

    img = svg.SVG(
            # completely fill the parent HTML element
            width="100%",
            height="100%",
            # defining the internal viewport as `size` so that the whole image is scaled to fit into the SVG element's viewport.
            viewBox=f"0 0 {size} {size}",
            class_=f"{css_prefix}-map",
            elements=elements)

    with open(filepath, "w") as f:
        f.write(str(img))