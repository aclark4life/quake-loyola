"""Assembles every area module's geometry into the final .map document.

This is the actual implementation behind the repo-root ``generate_map.py``
script (kept as a thin wrapper for backwards compatibility with
``python generate_map.py``) and the ``ql generate`` CLI command. Living
inside the package (rather than only as a root-level script) means it's
importable once quake-loyola is pip-installed too.
"""

from . import (
    basement,
    bridge,
    entities,
    knott_hall,
    knott_terrain,
    maryland_hall,
    maryland_terrain,
    ne_terrain,
    streets,
    west_campus,
    west_campus_terrain,
)
from .constants import (
    BASEMENT_ENABLED_LIGHTS,
    LIGHTS_ENABLED,
    LIGHTS_ENABLED_TORCHES,
    WORLDSPAWN_FIELDS,
)
from .mapdata import MapBuilder

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
    basement,
    entities,
]

# Per-group overrides, keyed by the "_light_group" field torch_flame()/light
# calls tag themselves with (see geometry.py). LIGHTS_ENABLED=True is a
# convenience master that forces every group on, same pattern as
# BRIDGE_ENABLED vs its per-section flags — see constants.py.
LIGHT_GROUP_FLAGS = {
    "torch": LIGHTS_ENABLED_TORCHES,
    "basement": BASEMENT_ENABLED_LIGHTS,
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
