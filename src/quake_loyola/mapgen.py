"""Assemble area modules into the final ``loyola.map`` document."""

from dataclasses import replace

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
    """Collect enabled module geometry into a ``MapBuilder``."""
    mb = MapBuilder()
    for mod in MODULES:
        brushes, ents = mod.build()
        kept = []
        for e in ents:
            # Read (without mutating) so repeated build_map() calls on the
            # same entity objects stay idempotent; strip the internal key
            # only from the copy we actually keep.
            group = e.fields.get("_light_group")
            if not e.classname.startswith("light"):
                kept.append(e)
                continue
            if group is not None and group not in LIGHT_GROUP_FLAGS:
                raise ValueError(
                    f"Unknown _light_group {group!r} (from {mod.__name__}) — "
                    f"not one of {sorted(LIGHT_GROUP_FLAGS)}. Add it to "
                    "LIGHT_GROUP_FLAGS in mapgen.py or fix the typo, rather "
                    "than letting the fixture silently disappear."
                )
            if group is None or LIGHT_GROUP_FLAGS.get(group):
                if "_light_group" in e.fields:
                    e = replace(
                        e,
                        fields={
                            k: v for k, v in e.fields.items() if k != "_light_group"
                        },
                    )
                kept.append(e)
        mb.add_brushes(brushes)
        mb.add_entities(kept)
    return mb


def build_map_text():
    """Return the serialized .map document text."""
    return build_map().to_map(WORLDSPAWN_FIELDS)


def main():
    """Write ``loyola.map`` to the repository root."""
    mb = build_map()
    map_text = mb.to_map(WORLDSPAWN_FIELDS)

    map_path = config.REPO_ROOT / "loyola.map"
    with open(map_path, "w") as f:
        f.write(map_text)
    print(
        f"{map_path} written — {len(mb.brushes)} worldspawn brushes, {len(mb.entities)} entities"
    )


if __name__ == "__main__":
    main()
