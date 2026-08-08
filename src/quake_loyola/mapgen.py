"""Assemble area modules into the final ``loyola.map`` document."""

from pathlib import Path

from . import (
    basement,
    bridge,
    config,
    entities,
    knott_hall,
    streets,
    terrain,
    west_campus,
)
from .constants import WORLDSPAWN_FIELDS
from .mapdata import MapBuilder

MODULES = [
    streets,
    west_campus,
    terrain.west_campus,
    bridge,
    terrain.knott_hall,
    knott_hall,
    terrain.ne,
    basement,
    entities,
]


def build_map():
    """Collect every module's geometry into a ``MapBuilder``."""
    mb = MapBuilder()
    for mod in MODULES:
        brushes, ents = mod.build()
        mb.add_brushes(brushes)
        mb.add_entities(ents)
    return mb


def build_map_text():
    """Return the serialized .map document text."""
    return build_map().to_map(WORLDSPAWN_FIELDS)


def main(path=None):
    """Write ``loyola.map`` to ``path`` (default: the repository root)."""
    overrides = config.non_default_overrides()
    if overrides:
        print(
            f"quake_loyola: {len(overrides)} non-default build setting(s) "
            f"active from {config.CONFIG_PATH}:"
        )
        for name in sorted(overrides):
            print(f"  {name} = {overrides[name]!r}")

    mb = build_map()
    map_text = mb.to_map(WORLDSPAWN_FIELDS)

    map_path = Path(path) if path is not None else config.REPO_ROOT / "loyola.map"
    with open(map_path, "w") as f:
        f.write(map_text)
    print(
        f"{map_path} written — {len(mb.brushes)} worldspawn brushes, {len(mb.entities)} entities"
    )


if __name__ == "__main__":
    main()
