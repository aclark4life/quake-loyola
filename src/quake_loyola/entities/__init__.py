"""Gameplay entities.

Currently just the single-player spawn point. Lights are emitted by the area
module that owns the geometry they light (e.g. :mod:`quake_loyola.basement`),
not from here.
"""

from ..geometry import ent

# Hand-placed spawn location (west of the bridge, on Charles St); not derived
# from a terrain/road constant, so it stays a private constant here rather
# than in constants/ to avoid implying it tracks map scale.
_SPAWN_X = -180
_SPAWN_Y = 1992
_SPAWN_Z = 26


def build():
    """Build gameplay entities."""
    return [], [
        ent(
            "info_player_start",
            origin=f"{_SPAWN_X} {_SPAWN_Y} {_SPAWN_Z}",
            angle="270",
        ),
        ent(
            "info_teleport_destination",
            targetname="dest_start",
            origin=f"{_SPAWN_X} {_SPAWN_Y + 24} {_SPAWN_Z}",
            angle="270",
        ),
    ]
