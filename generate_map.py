#!/usr/bin/env python3
from constants import Textures
from mapdata import MapBuilder

import streets
import west_campus
import bridge
import knott_hall
import entities

WORLDSPAWN_FIELDS = {
    "wad": "quake101.wad;ad.wad",
    "message": "Loyola Bridge & Knott Hall",
    "sky": Textures.SKY,
    "ambient": "60",
    "_sunlight": "220",
    "_sunlight_color": "255 245 210",
    "_sunlight_dir": "60 -60",
    "_sunlight_penumbra": "8",
    "dmflags": "128",
    "_fog": "0.03 0.5 0.5 0.6",
}


def build_map():
    """Build the full map by collecting every module's geometry into a MapBuilder."""
    mb = MapBuilder()
    for mod in [streets, west_campus, bridge, knott_hall, entities]:
        brushes, ents = mod.build()
        mb.add_brushes(brushes)
        mb.add_entities(ents)
    return mb


def build_map_text():
    """Return the serialized .map document text."""
    return build_map().to_map(WORLDSPAWN_FIELDS)


def main():
    mb = build_map()
    map_text = mb.to_map(WORLDSPAWN_FIELDS)
    with open("loyola.map", "w") as f:
        f.write(map_text)
    print(
        f"loyola.map written — {len(mb.brushes)} worldspawn brushes, {len(mb.entities)} entities"
    )


if __name__ == "__main__":
    main()
