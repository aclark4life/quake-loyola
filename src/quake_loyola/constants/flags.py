"""Boolean feature flags loaded from :mod:`quake_loyola.config`.

Defaults live in ``config.DEFAULTS`` and can be overridden in ``ql.toml`` or
via ``ql conf``.

Note: not every ``config.DEFAULTS`` flag is re-exported here. A few flags
are defined alongside their area's other constants instead, so related
values stay together:

- ``BASEMENT_ENABLED`` — see ``constants/derived.py``
- ``KNOTT_ENABLED_WALKWAY`` / ``KNOTT_ENABLED_WALKWAY_BENT`` — see
  ``constants/knott.py``
- ``BRIDGE_ENABLED_PIER_BASE_LIGHTS`` — see ``constants/bridge.py``

All of these (plus everything below) are still re-exported from
``constants/__init__.py``, so callers importing from the top-level
``constants`` package don't need to know which submodule a flag lives in.
"""

from ..config import get as _flag

# Module and section flags.
BRIDGE_ENABLED_SPAN_WEST_APPROACH = _flag(
    "BRIDGE_ENABLED_SPAN_WEST_APPROACH"
)  # bridge.py span: Pier 1 to Pier 2
BRIDGE_ENABLED_SPAN_CENTER = _flag(
    "BRIDGE_ENABLED_SPAN_CENTER"
)  # bridge.py span: Pier 2 to Pier 3
BRIDGE_ENABLED_SPAN_EAST_APPROACH = _flag(
    "BRIDGE_ENABLED_SPAN_EAST_APPROACH"
)  # bridge.py span: Pier 3 to Pier 4
BRIDGE_ENABLED_SPAN_KH = _flag(
    "BRIDGE_ENABLED_SPAN_KH"
)  # bridge.py span: Pier 4 to Pier 5
BRIDGE_ENABLED_SPAN_EAST_EXT = _flag(
    "BRIDGE_ENABLED_SPAN_EAST_EXT"
)  # bridge.py span: Pier 5 to Pier 6
STREETS_ENABLED_DETAILS = _flag(
    "STREETS_ENABLED_DETAILS"
)  # Roads, sidewalks, curbs, lamps, trees, driveways, and Ennis entrance features.
WEST_CAMPUS_ENABLED_DORMS = _flag(
    "WEST_CAMPUS_ENABLED_DORMS"
)  # Dorm buildings and grounds.
WEST_CAMPUS_ENABLED_FENCE = _flag("WEST_CAMPUS_ENABLED_FENCE")  # Charles St iron fence.
WEST_CAMPUS_ENABLED_TERRAIN = _flag(
    "WEST_CAMPUS_ENABLED_TERRAIN"
)  # West-campus terrain fill.
WEST_CAMPUS_ENABLED_WALL = _flag(
    "WEST_CAMPUS_ENABLED_WALL"
)  # Brick wall, gate, pillars, and fence south of Pier 1.
WEST_CAMPUS_ENABLED_SIDEWALK = _flag(
    "WEST_CAMPUS_ENABLED_SIDEWALK"
)  # Front walkway and wall-door spur.
NE_ENABLED_TERRAIN = _flag("NE_ENABLED_TERRAIN")  # North-east quadrant terrain fill.
KNOTT_ENABLED_TERRAIN = _flag(
    "KNOTT_ENABLED_TERRAIN"
)  # Knott terrain, embankment, and driveway.
KNOTT_ENABLED = _flag(
    "KNOTT_ENABLED"
)  # Prototype Knott Hall shell (walls + roof, no floors) sized against real terrain.

# Entity groups.
ENTITIES_ENABLED_TELEPORTS = _flag("ENTITIES_ENABLED_TELEPORTS")  # Teleports.
ENTITIES_ENABLED_DM_SPAWNS = _flag("ENTITIES_ENABLED_DM_SPAWNS")  # Deathmatch spawns.
ENTITIES_ENABLED_WEAPONS = _flag("ENTITIES_ENABLED_WEAPONS")  # weapon_* pickups
ENTITIES_ENABLED_AMMO = _flag("ENTITIES_ENABLED_AMMO")  # item_rockets/shells/spikes
ENTITIES_ENABLED_HEALTH = _flag("ENTITIES_ENABLED_HEALTH")  # item_health/armor pickups
ENTITIES_ENABLED_MONSTERS = _flag("ENTITIES_ENABLED_MONSTERS")  # Non-Knott monsters.
ENTITIES_ENABLED_VEGETATION = _flag("ENTITIES_ENABLED_VEGETATION")  # Trees and bushes.
ENTITIES_ENABLED_PLATFORM = _flag(
    "ENTITIES_ENABLED_PLATFORM"
)  # Charles St platform loop and its rocket launchers.
ENTITIES_ENABLED_EXIT = _flag("ENTITIES_ENABLED_EXIT")  # Single-player exit portal.

# Light groups.
LIGHTS_ENABLED_TORCHES = _flag("LIGHTS_ENABLED_TORCHES")  # Torch and flame fixtures.
LIGHTS_ENABLED_DECK_WALL = _flag(
    "LIGHTS_ENABLED_DECK_WALL"
)  # Bridge parapet wall lights.
LIGHTS_ENABLED_PENDANTS = _flag(
    "LIGHTS_ENABLED_PENDANTS"
)  # Under-bridge pendant lights.
LIGHTS_ENABLED_PIER_UPLIGHTS = _flag(
    "LIGHTS_ENABLED_PIER_UPLIGHTS"
)  # Pier base uplights.
LIGHTS_ENABLED_ABUTMENT_ARCH = _flag(
    "LIGHTS_ENABLED_ABUTMENT_ARCH"
)  # West abutment cement-arch lights.
LIGHTS_ENABLED_DORM_INTERIOR = _flag(
    "LIGHTS_ENABLED_DORM_INTERIOR"
)  # Dorm interior lights.
BASEMENT_ENABLED_LIGHTS = _flag("BASEMENT_ENABLED_LIGHTS")  # Basement fixtures.
MARYLAND_ENABLED = _flag("MARYLAND_ENABLED")  # Maryland Hall massing block.
MARYLAND_ENABLED_TERRAIN = _flag(
    "MARYLAND_ENABLED_TERRAIN"
)  # Maryland Hall terrain mound.

BRIDGE_ENABLED_FASCIA_TEXT = _flag("BRIDGE_ENABLED_FASCIA_TEXT")

BRIDGE_ENABLED_SUPPORTS = _flag("BRIDGE_ENABLED_SUPPORTS")
