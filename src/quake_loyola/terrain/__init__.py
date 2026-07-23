"""Terrain builders for the map's quadrant-specific ground geometry.

Each submodule exposes ``build() -> (brushes, entities)`` and can be toggled
with its own ``*_ENABLED_TERRAIN`` flag.
"""

from . import knott_hall, maryland, ne, west_campus

__all__ = ["knott_hall", "maryland", "ne", "west_campus"]
