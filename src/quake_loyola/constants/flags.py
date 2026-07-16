"""Master module-enable switches and other on/off feature flags.

Every value below is now sourced from :mod:`quake_loyola.config` (defaults
hardcoded there, optionally overridden by ``ql.toml`` at the repo root — see
that module's docstring, or run ``./ql conf show``). The comments here
describe what each flag does; the *value* itself lives in
``config.DEFAULTS`` and is only overridden when the user sets it via
``ql conf set <NAME> <value>``.
"""

from ..config import get as _flag

# ════════════════════════════════════════════════════════════════════════════════
# MASTER MODULE SWITCHES — flip a flag to True (via `ql conf set NAME true`,
# or by editing ql.toml) to re-enable that module's geometry. All default to
# False so only the world-shell rectangle (streets.py, which is never gated —
# it seals the level) is generated. Use this while re-deriving every area's
# dimensions from the top-down references in ref/.
# ════════════════════════════════════════════════════════════════════════════════
BRIDGE_ENABLED = _flag(
    "BRIDGE_ENABLED"
)  # convenience master: if True, forces every BRIDGE_ENABLED_<section> flag below on, overriding their individual settings. Leave False and flip the per-section flags to review one span at a time.
BRIDGE_ENABLED_WEST_APPROACH = _flag(
    "BRIDGE_ENABLED_WEST_APPROACH"
)  # bridge.py span: Pier 1 (west abutment) .. Pier 2
BRIDGE_ENABLED_CENTER_SPAN = _flag(
    "BRIDGE_ENABLED_CENTER_SPAN"
)  # bridge.py span: Pier 2 .. Pier 3 (curved arch span over Charles St)
BRIDGE_ENABLED_EAST_APPROACH = _flag(
    "BRIDGE_ENABLED_EAST_APPROACH"
)  # bridge.py span: Pier 3 .. Pier 4 (west KH pier)
BRIDGE_ENABLED_KH_SPAN = _flag(
    "BRIDGE_ENABLED_KH_SPAN"
)  # bridge.py span: Pier 4 .. Pier 5 (east KH pier / NE pier)
BRIDGE_ENABLED_EAST_EXT = _flag(
    "BRIDGE_ENABLED_EAST_EXT"
)  # bridge.py span: Pier 5 .. Pier 6 (extended east section to Ennis Rd)
STREETS_DETAILS_ENABLED = _flag(
    "STREETS_DETAILS_ENABLED"
)  # streets.py content other than the world-shell rectangle (roads, sidewalks, curbs, lamps, trees, driveways, Ennis entrance features)
WEST_CAMPUS_ENABLED = _flag(
    "WEST_CAMPUS_ENABLED"
)  # west_campus.py — dorm buildings and grounds
WEST_CAMPUS_FENCE_ENABLED = _flag(
    "WEST_CAMPUS_FENCE_ENABLED"
)  # west_campus.py — iron fence along the east
# face of the (currently disabled) west-campus buildings. Kept independent of
# WEST_CAMPUS_ENABLED so the fence can be shown along Charles St even while
# the dorm buildings themselves stay off.
WEST_CAMPUS_TERRAIN_ENABLED = _flag(
    "WEST_CAMPUS_TERRAIN_ENABLED"
)  # west_campus_terrain.py — real-elevation
# ground fill under/around the dorm buildings + bridge west approach. Kept
# independent of WEST_CAMPUS_ENABLED (same reasoning as KNOTT_TERRAIN_ENABLED
# vs KNOTT_HALL_ENABLED) so the terrain can be reviewed on its own even while
# the buildings themselves stay off.
NE_TERRAIN_ENABLED = _flag(
    "NE_TERRAIN_ENABLED"
)  # ne_terrain.py — real-elevation ground fill for the
# NE quadrant (north of Ennis Road, east of Charles St), replacing the flat
# placeholder box streets.py used to build there. See ne_terrain.py's module
# docstring for the real-elevation-derived design and the two flush ties
# (Charles St east sidewalk to the west, Ennis Road north curb to the south).
KNOTT_TERRAIN_ENABLED = _flag(
    "KNOTT_TERRAIN_ENABLED"
)  # knott_terrain.py — KH surrounding terrain/embankment/driveway
KNOTT_HALL_ENABLED = _flag(
    "KNOTT_HALL_ENABLED"
)  # knott_hall.py — KH building shell (walls, windows, roof, sign)
ENTITIES_ENABLED = _flag(
    "ENTITIES_ENABLED"
)  # entities.py — items, monsters, decorative lights, extra spawns (a single info_player_start is always kept so the map stays loadable)
LIGHTS_ENABLED = _flag(
    "LIGHTS_ENABLED"
)  # master switch for every "light"-classname entity across all modules (streets, entities, west_campus, bridge, etc.); see generate_map.py filter
TORCH_LIGHTS_ENABLED = _flag(
    "TORCH_LIGHTS_ENABLED"
)  # light "group" flag: torch/flame fixtures only
BASEMENT_ENABLED_LIGHTS = _flag(
    "BASEMENT_ENABLED_LIGHTS"
)  # light "group" flag: basement.py fixtures only —
# on by default (unlike TORCH_LIGHTS_ENABLED's pattern above, kept True since
# the basement is otherwise a fully unlit sky-textured void with no ambient
# light source, and would render as solid black without at least a few
# lights placed inside it).
# (bridge pillar tops, Ennis entrance pillars, Ennis cement-wall lamppost,
# campus lamp posts) — same convenience-master pattern as BRIDGE_ENABLED:
# LIGHTS_ENABLED=True forces every light group on (including this one),
# overriding the individual setting; leave LIGHTS_ENABLED False and flip
# this (or future per-group flags) to review one light group at a time.
# See generate_map.py filter — torch entities carry an internal
# "_light_group" field so they can be told apart from other "light"-
# classname entities (pendant lights, pillar uplights, etc.) that aren't
# part of any group yet and stay off until LIGHTS_ENABLED is True.
MARYLAND_HALL_ENABLED = _flag(
    "MARYLAND_HALL_ENABLED"
)  # maryland_hall.py — placeholder Maryland Hall massing block, east of Ennis Parallel
MARYLAND_TERRAIN_ENABLED = _flag(
    "MARYLAND_TERRAIN_ENABLED"
)  # maryland_terrain.py — ground mound under/around the Maryland Hall stub
# Kept independent of KNOTT_TERRAIN_ENABLED so each hill/mound can be flipped
# on and off separately while both are still placeholder/provisional models.

DRAW_BRIDGE_FASCIA_TEXT = _flag("DRAW_BRIDGE_FASCIA_TEXT")

SHOW_SUPPORTS = _flag("SHOW_SUPPORTS")
