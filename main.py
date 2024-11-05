import os.path

from mapviz.map import osm_get_map
from mapviz.svg import generate_svg

street_types = [
    'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link', 
    'secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'residential', 'service',
    'unclassified', 'living_street'
]

street_widths = {
    "motorway": 5,
    "motorway_link": 5,
    "trunk": 5,
    "trunk_link": 5,
    "primary": 4.5,
    "primary_link": 4.5,
    "secondary": 4,
    "secondary_link": 4,
    "tertiary": 3.5,
    "tertiary_link": 3.5,
    "residential": 3,
    "service": 2,
    "unclassified": 1,
    "living_street": 1,
}

rail_types = ["rail", "light_rail", "subway", "funicular", "monorail", "narrow_gauge", "tram"]

layers = {
    "street": {
        "custom_filter": f'["highway"~"{"|".join(street_types)}"]',
        "retain_all": True, 
        "truncate_by_edge": True,
        "is_graph": True,
    },
    "railway": {
        "custom_filter": f'["railway"~"{"|".join(rail_types)}"]',
        "retain_all": True, 
        "simplify": False, 
        "truncate_by_edge": True, 
        "is_graph": True,
    },
    "building": {
        "tags": {    
            "building": True,
            "landuse": "construction",
            # TODO move that and temples to a special category
            "historic": "monument",
        },
    },
    "water": {
        "tags": {    
            "natural": [
                "water",
                "bay"
            ]
        }
    },
    "forest": {
        "tags": {    
            "landuse": "forest"
        }
    },
    "green": {
        "tags": {    
            "landuse": [
                "grass",
                "orchard",
            ],
            "natural": [
                "island",
                "scrub",
                "wood",
            ],
            "leisure": [
                "park",
                "pitch",
            ],
            "amenity": "grave_yard",
        }
    },
    "beach": {
        "tags": {    
            "natural": "beach"
        }
    },
    "walk": {
        "tags": {    
            "amenity": "parking",
            "highway": "pedestrian",
            "man_made": "pier",
            "place": "square",
        }
    }
}

styles = {
    'perimeter': {'fc': '#091833', 'ec': '#dadbc1', 'zorder': -1},
    'walk': {'fc': '#ea00d9', 'ec': '#2F3737', 'lw': 0.1, 'zorder': 1},
    'green': {'fc': '#089a00', 'ec': '#2F3737', 'lw': 1, 'zorder': 0},
    'forest': {'fc': '#089a00', 'ec': '#2F3737', 'lw': 1, 'zorder': 0},
    'water': {'fc': '#00b9ff', 'ec': '#711c91', 'lw': 1, 'zorder': 2},
    'street': {'fc': '#8bf4f7', 'ec': '#0fcdf6', 'lw': 0, 'zorder': 3, "width": street_widths},
    'railway': {'fc': '#f7f132', 'ec': '#f7f132', 'lw': 0, 'zorder': 2.5, "width": 2},
    'building': {'palette': ['#2900c1', '#FF5E5B'], 'ec': '#2F3737', 'lw': .1, 'zorder': 4},
}


# get the place boundaries
places = {
    "Tokyo": (35.67694, 139.76384),
    "Sendai": (38.266224, 140.871838),
    "Napoli": (40.848923, 14.250147),
    "Berlin": (52.51702, 13.40178),
}


MAP_DIR="./maps/"
SIZE=2048

def generate(placename, dist):
    coordinates = places[placename]
    map = osm_get_map(layers, coordinates, dist)
    generate_svg(map, os.path.join(MAP_DIR, f"{placename}-{dist}.svg"), SIZE, styles)

if __name__ == "__main__":
    import sys
    dist = int(sys.argv[1])
    placenames = sys.argv[2].split(",")

    for placename in placenames:
        print(f"Generate {placename}@{dist}")
        generate(placename, dist)