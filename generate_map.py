#!/usr/bin/env python3
from quake_loyola import (
    bridge,
    entities,
    knott_hall,
    knott_terrain,
    maryland_hall,
    maryland_terrain,
    ne_terrain,
    sewer,
    streets,
    west_campus,
    west_campus_terrain,
)
from quake_loyola.constants import (
    LIGHTS_ENABLED,
    TORCH_LIGHTS_ENABLED,
    WORLDSPAWN_FIELDS,
)
from quake_loyola.mapdata import MapBuilder

MODULES = [
    streets,
    west_campus,
    west_campus_terrain,
    bridge,
    knott_terrain,
    knott_hall,
    maryland_terrain,
    maryland_hall,
    ne_terrain,
    sewer,
    entities,
]

# Per-group overrides, keyed by the "_light_group" field torch_flame()/light
# calls tag themselves with (see geometry.py). LIGHTS_ENABLED=True is a
# convenience master that forces every group on, same pattern as
# BRIDGE_ENABLED vs its per-section flags — see constants.py.
LIGHT_GROUP_FLAGS = {
    "torch": TORCH_LIGHTS_ENABLED,
}


def build_map():
    """Build the full map by collecting every module's geometry into a MapBuilder."""
    mb = MapBuilder()
    for mod in MODULES:
        brushes, ents = mod.build()
        kept = []
        for e in ents:
            group = e.fields.pop("_light_group", None)
            if not e.classname.startswith("light"):
                kept.append(e)
            elif LIGHTS_ENABLED or LIGHT_GROUP_FLAGS.get(group):
                # Master on, or this entity's group has its own flag on —
                # keep it (ungrouped "light" entities have no flag yet, so
                # they only pass through when the master itself is on).
                kept.append(e)
        mb.add_brushes(brushes)
        mb.add_entities(kept)
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
