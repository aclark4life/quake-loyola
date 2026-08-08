"""Gameplay entities, lights, teleports, and movers.

Each submodule groups one concern (spawns, pickups, monsters, lights,
vegetation, and the Charles St platform loop) and exposes
``_build_x(ENTITIES)`` helpers that append to a shared, mutable ``ENTITIES``
list. :func:`build` runs them in the same order as the original monolithic
module to keep entity ordering (and therefore the generated ``.map`` output)
unchanged.
"""

from . import lights as _lights
from . import monsters as _monsters
from . import pickups as _pickups
from . import platform as _platform
from . import spawns as _spawns
from . import vegetation as _vegetation


def build():
    """Build gameplay entities, lights, teleports, and movers."""
    BRUSHES = []
    ENTITIES = []

    _spawns._build_teleports(ENTITIES)
    _spawns._build_player_start(ENTITIES)
    _spawns._build_dm_spawns(ENTITIES)
    _pickups._build_weapons(ENTITIES)
    _monsters._build_monsters(ENTITIES)
    _pickups._build_ammo(ENTITIES)
    _pickups._build_health(ENTITIES)
    _lights._build_lights(ENTITIES)
    _vegetation._build_vegetation(ENTITIES)
    _platform._build_platform(ENTITIES)
    _monsters._build_monsters2(ENTITIES)

    return BRUSHES, ENTITIES
