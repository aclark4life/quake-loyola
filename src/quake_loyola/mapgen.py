"""Assembles every area module's geometry into the final .map document.

This is the actual implementation behind the repo-root ``generate_map.py``
script (kept as a thin wrapper for backwards compatibility with
``python generate_map.py``) and the ``ql gen`` CLI command. Living
inside the package (rather than only as a root-level script) means it's
importable once quake-loyola is pip-installed too.
"""

from . import (
    basement,
    bridge,
    config,
    entities,
    knott_hall,
    maryland_hall,
    streets,
    terrain,
    west_campus,
)
from .constants import (
    BASEMENT_ENABLED_LIGHTS,
    LIGHTS_ENABLED_ABUTMENT_ARCH,
    LIGHTS_ENABLED_DECK_WALL,
    LIGHTS_ENABLED_DORM_INTERIOR,
    LIGHTS_ENABLED_PENDANTS,
    LIGHTS_ENABLED_PIER_UPLIGHTS,
    LIGHTS_ENABLED_TORCHES,
    WORLDSPAWN_FIELDS,
)
from .mapdata import MapBuilder

MODULES = [
    streets,
    west_campus,
    terrain.west_campus,
    bridge,
    terrain.knott_hall,
    knott_hall,
    terrain.maryland,
    maryland_hall,
    terrain.ne,
    basement,
    entities,
]

# Per-group overrides, keyed by the "_light_group" field torch_flame()/light
# calls tag themselves with (see geometry.py). Each fixture type is toggled
# independently — there is no overall "LIGHTS_ENABLED" master.
LIGHT_GROUP_FLAGS = {
    "torch": LIGHTS_ENABLED_TORCHES,
    "basement": BASEMENT_ENABLED_LIGHTS,
    "deck_wall": LIGHTS_ENABLED_DECK_WALL,
    "pendant": LIGHTS_ENABLED_PENDANTS,
    "pier_uplight": LIGHTS_ENABLED_PIER_UPLIGHTS,
    "abutment_arch": LIGHTS_ENABLED_ABUTMENT_ARCH,
    "dorm_interior": LIGHTS_ENABLED_DORM_INTERIOR,
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
            elif group is None or LIGHT_GROUP_FLAGS.get(group):
                # Ungrouped "light" entities have no flag of their own, so
                # they pass through unfiltered, relying entirely on whatever
                # section-level flag (if any) already wraps them in their
                # source module. Grouped entities are kept only when their
                # own group flag is on.
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
    # Write next to ql.toml (config.REPO_ROOT) rather than the raw cwd, so
    # `ql gen`/`ql build` produce loyola.map in the same directory that
    # `ql build`'s qbsp/vis/light subprocess calls (cwd=REPO_ROOT) expect it
    # in, even when invoked from a subdirectory of the repo.
    map_path = config.REPO_ROOT / "loyola.map"
    with open(map_path, "w") as f:
        f.write(map_text)
    print(
        f"{map_path} written — {len(mb.brushes)} worldspawn brushes, {len(mb.entities)} entities"
    )


if __name__ == "__main__":
    main()
