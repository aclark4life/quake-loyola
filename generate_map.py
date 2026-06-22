#!/usr/bin/env python3
from quake_loyola import (
    bridge,
    entities,
    knott_hall,
    knott_terrain,
    streets,
    west_campus,
)
from quake_loyola.constants import WORLDSPAWN_FIELDS
from quake_loyola.mapdata import MapBuilder

MODULES = [streets, west_campus, bridge, knott_terrain, knott_hall, entities]


def build_map():
    """Build the full map by collecting every module's geometry into a MapBuilder."""
    mb = MapBuilder()
    for mod in MODULES:
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
