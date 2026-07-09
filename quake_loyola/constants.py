"""Shared numeric constants, the ``Textures`` table, and bridge-deck helpers.

Naming conventions
==================

Identifiers are built from an **area prefix** + **feature** + **dimension/axis
suffix**. Once the vocabulary below is known, most names are self-describing
(e.g. ``BRIDGE_PILLAR_CAP_OVH`` = bridge pillar cap overhang).

Area prefixes
    ``BRIDGE_``, ``KNOTT_``, ``ENNIS_``, ``DORM_``, ``CHARLES_``, ``STREET_``,
    ``ROAD_``, ``WORLD_``, ``ARCH_`` — which part of the map the value belongs to.

Axis & position suffixes
    - ``X1``/``X2``, ``Y1``/``Y2``, ``Z1``/``Z2`` — min/max extent of a box along
      that axis (``1`` = lower coordinate, ``2`` = higher).
    - ``DZ1``/``DZ2`` — bridge deck Z bottom / top.
    - ``ZB``/``ZT`` — Z bottom / Z top of a feature.
    - ``CX``/``CY`` — centre X / centre Y of a feature.
    - ``XS``/``YS`` — a *list* (plural) of X or Y positions.
    - ``N``/``S``/``E`` — compass direction (Quake: +Y = north, −Y = south,
      +X = east); combined forms like ``NY`` mean "north-edge Y".

Dimension suffixes
    - ``H`` height, ``HH`` half-height.
    - ``W`` width, ``HW`` half-width.
    - ``T`` thickness, ``R`` radius, ``D`` depth.
    - ``OVH`` overhang, ``EXTRA`` extra length/padding, ``PROUD`` how far a
      feature protrudes from its face.

Feature abbreviations
    - ``PILLAR`` pillar, ``BLK`` block, ``SQ`` square, ``PYR`` pyramid.
    - ``ENT`` entrance, ``WIN`` window, ``DIV`` road divider, ``PLT`` platform,
      ``BR`` back road.
    - ``DRIVEWAY_WS``/``_RD``/``_ES`` — west-side / road / east-side sections of
      the Knott driveway (ordered west→east).
    - ``BIY`` Knott building-interior Y (inner wall face).
    - ``ORIG`` original (pre-extension) reference, e.g. ``KNOTT_ORIG_CX``.
    - ``KH`` Knott Hall (e.g. the ``FLOOR_KH`` texture).
"""

import math
from dataclasses import dataclass

# ════════════════════════════════════════════════════════════════════════════════
# MASTER MODULE SWITCHES — flip a flag to True to re-enable that module's geometry.
# All default to False so only the world-shell rectangle (streets.py, which is
# never gated — it seals the level) is generated. Use this while re-deriving
# every area's dimensions from the top-down references in ref/.
# ════════════════════════════════════════════════════════════════════════════════
BRIDGE_ENABLED = False  # convenience master: if True, forces every BRIDGE_ENABLED_<section> flag below on, overriding their individual settings. Leave False and flip the per-section flags to review one span at a time.
BRIDGE_ENABLED_WEST_APPROACH = False  # bridge.py span: Pier 1 (west abutment) .. Pier 2
BRIDGE_ENABLED_CENTER_SPAN = (
    True  # bridge.py span: Pier 2 .. Pier 3 (curved arch span over Charles St)
)
BRIDGE_ENABLED_EAST_APPROACH = False  # bridge.py span: Pier 3 .. Pier 4 (west KH pier)
BRIDGE_ENABLED_KH_SPAN = (
    False  # bridge.py span: Pier 4 .. Pier 5 (east KH pier / NE pier)
)
BRIDGE_ENABLED_EAST_EXT = (
    False  # bridge.py span: Pier 5 .. Pier 6 (extended east section to Ennis Rd)
)
STREETS_DETAILS_ENABLED = True  # streets.py content other than the world-shell rectangle (roads, sidewalks, curbs, lamps, trees, driveways, Ennis entrance features)
WEST_CAMPUS_ENABLED = False  # west_campus.py — dorm buildings and grounds
WEST_CAMPUS_TERRAIN_ENABLED = True  # west_campus_terrain.py — real-elevation
# ground fill under/around the dorm buildings + bridge west approach. Kept
# independent of WEST_CAMPUS_ENABLED (same reasoning as KNOTT_TERRAIN_ENABLED
# vs KNOTT_HALL_ENABLED) so the terrain can be reviewed on its own even while
# the buildings themselves stay off.
NE_TERRAIN_ENABLED = True  # ne_terrain.py — real-elevation ground fill for the
# NE quadrant (north of Ennis Road, east of Charles St), replacing the flat
# placeholder box streets.py used to build there. See ne_terrain.py's module
# docstring for the real-elevation-derived design and the two flush ties
# (Charles St east sidewalk to the west, Ennis Road north curb to the south).
KNOTT_TERRAIN_ENABLED = (
    True  # knott_terrain.py — KH surrounding terrain/embankment/driveway
)
KNOTT_HALL_ENABLED = (
    False  # knott_hall.py — KH building shell (walls, windows, roof, sign)
)
ENTITIES_ENABLED = False  # entities.py — items, monsters, decorative lights, extra spawns (a single info_player_start is always kept so the map stays loadable)
LIGHTS_ENABLED = False  # master switch for every "light"-classname entity across all modules (streets, entities, west_campus, bridge, etc.); see generate_map.py filter
TORCH_LIGHTS_ENABLED = True  # light "group" flag: torch/flame fixtures only
# (bridge pillar tops, Ennis entrance pillars, Ennis cement-wall lamppost,
# campus lamp posts) — same convenience-master pattern as BRIDGE_ENABLED:
# LIGHTS_ENABLED=True forces every light group on (including this one),
# overriding the individual setting; leave LIGHTS_ENABLED False and flip
# this (or future per-group flags) to review one light group at a time.
# See generate_map.py filter — torch entities carry an internal
# "_light_group" field so they can be told apart from other "light"-
# classname entities (pendant lights, pillar uplights, etc.) that aren't
# part of any group yet and stay off until LIGHTS_ENABLED is True.
MARYLAND_HALL_ENABLED = False  # maryland_hall.py — placeholder Maryland Hall massing block, east of Ennis Parallel
MARYLAND_TERRAIN_ENABLED = (
    False  # maryland_terrain.py — ground mound under/around the Maryland Hall stub
)
# Kept independent of KNOTT_TERRAIN_ENABLED so each hill/mound can be flipped
# on and off separately while both are still placeholder/provisional models.

ARCH_RIN = 96
ARCH_ROUT = 136
ARCH_SLAB_W = 32
ARCH_STILT_H = 96

A_SEGS = 16

BRIDGE_ARCH_RISE = 100
BRIDGE_ARCH_PIER_RISE = 82  # deck rise at the centre-span piers (PIER2/PIER3, ±525):
# the centre span arches from here up to BRIDGE_ARCH_RISE over Charles St (X=0); the
# two approach spans descend straight from here to 0 at the outer piers (ref/bridge08)
BRIDGE_ACCESS_WALK_CENTER_X = 2120
BRIDGE_ACCESS_WALK_HALF_W = 32
BRIDGE_ACCESS_WALK_NORTH_OFFSET = 80
BRIDGE_ACCESS_WALK_PIER_CLEARANCE = 96
BRIDGE_BLK_H = 36
BRIDGE_BLK_HW = 24
BRIDGE_BLK_OVH = 0
BRIDGE_BLK_PIER_CLEARANCE = 4
BRIDGE_DECK_EAST_RECESS = 1
BRIDGE_DZ1, BRIDGE_DZ2 = (
    256,
    272,
)  # raised 32 units (was 224/240) so the flat deck at KNOTT_ORIG_CX (WALK_ZT1) is
# level with the KH 2nd-floor walkway landing (WALK_ZT2); see KNOTT_GROUND_Z below,
# now a fixed hill-height anchor independent of this deck elevation.
BRIDGE_EAST_SHIFT_START = 0.0
BRIDGE_EAST_SPAN_ANGLE = 12.0
BRIDGE_FASCIA_PX_W, BRIDGE_FASCIA_PX_H = 4, 4
BRIDGE_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
BRIDGE_PAR_H = 40
BRIDGE_PILLAR_BASE_CAP_H = 6
BRIDGE_PILLAR_BASE_CAP_OVH = 5
BRIDGE_PILLAR_BASE_H = 64  # solid plinth height before the arch opening starts (was 24 originally — raised so more stone shows at the pier base before the archway begins)
BRIDGE_PILLAR_BASE_RAMP_H = 80  # ramped-side plinth height (was 40 originally — kept the same 16-unit rise over BASE_H)
BRIDGE_PILLAR_CAP_H = 12
BRIDGE_PILLAR_CAP_IN_OVH = 4
BRIDGE_PILLAR_CAP_OUT_OVH = 20
BRIDGE_PILLAR_EXTRA = 64
BRIDGE_PIER_BASE_LIGHTS_ENABLED = False  # temporarily disabled — pier-base lights (some sit buried in the east-span fill)
BRIDGE_PIER_FILL_OFFSET = 16
BRIDGE_PILLAR_INNER_R = (160, 84)
BRIDGE_PILLAR_OUTER_R = (140, 72)
BRIDGE_PILLAR_OVERHANG = 16
# Decorative square cement plates on the interior (facing the opposite pillar
# across the opening) and exterior (facing outward) walls of each arch/square
# pier. See bridge.py "Pillar posts" — plates protrude slightly from the flat
# pillar wall for a panelled look.
BRIDGE_PIER_PLATE_SIZE = 34
BRIDGE_PIER_PLATE_GAP = 3
BRIDGE_PIER_PLATE_D = (
    1  # plate protrusion depth from the pillar wall (slight, flush-ish)
)
# Cement lining covering the inside surfaces (stilt/side walls + curved
# intrados or lintel underside) of each pier's arch/square opening — leaves
# a stone border at each opening end (margin) before the lining begins.
BRIDGE_PIER_LINING_MARGIN = 6
BRIDGE_PIER_LINING_THICK = 3
BRIDGE_PILLAR_PYR_H = 20
BRIDGE_SEG_SPAN_W = 32
BRIDGE_SQ_D = 1
BRIDGE_SQ_HH = 6
BRIDGE_SQ_HW = 8
BRIDGE_SUPPORT_BEAM_H = 20
BRIDGE_SUPPORT_HALF_W = 16
BRIDGE_SUPPORT_PIER_HALF_W = 20
BRIDGE_TELEPORT_ARCH_CLEARANCE = 8
BRIDGE_TELEPORT_ARCH_X1_OFFSET = 2
BRIDGE_TELEPORT_ARCH_X2_OFFSET = 18
BRIDGE_TELEPORT_DEST_Z = 40
BRIDGE_TORCH_CUP_H = 4
BRIDGE_TORCH_CUP_HW = 5
BRIDGE_TORCH_POST_H = 16
BRIDGE_TORCH_POST_HW = 3
BRIDGE_TUBE_GAP = 12
BRIDGE_TUBE_HW = 2
BRIDGE_TUBE_RISE = 10
BRIDGE_WALK_WALL = 32
BRIDGE_Y1, BRIDGE_Y2 = -148, 148  # 296-unit (~19.6 ft) deck; after the two 38-unit
# parapets, interior walking width = 220 units = ft_to_units(14,6) ≈ 14.5 ft

CHARLES_ARCH_RIN = 256
CHARLES_ARCH_RIN_PRE = 256
CHARLES_ARCH_ROUT = 312
CHARLES_ARCH_ROUT_PRE = 312
CHARLES_ARCH_STILT = 96
CHARLES_ARCH_STILT_PRE = 96
CHARLES_ARCH_TRIG_INSET = 8
CHARLES_ARCH_W = 48
CHARLES_ARCH_W_PRE = 48
CHARLES_CRN_SEGS = 12
CHARLES_LAMP_POST_EAST_SETBACK = 48
CHARLES_PLT_H = 12
CHARLES_PLT_SPEED = 180
CHARLES_PLT_W = 128
CHARLES_RAMP_W = 64
CHARLES_WALK_H = 8
CHARLES_WALK_W = 80

DORM_DEPTH = 450
DORM_FENCE_OFFSET = 216
DORM_FRONT_WALKWAY_FENCE_OFFSET = 40
DORM_FRONT_WALKWAY_W = 96
DORM_GABLE_DEPTH = 6
DORM_INNER_DOOR_H = 128
DORM_INNER_DOOR_HW = 56
DORM_BRICK_PILLAR_CAP_H = 10
DORM_BRICK_PILLAR_CAP_OVH = 1
DORM_BRICK_PILLAR_GAP = 96
DORM_BRICK_PILLAR_H_OFFSET = 80
DORM_BRICK_PILLAR_PROUD = 6
DORM_BRICK_PILLAR_SEPARATION = 380
DORM_BRICK_PILLAR_W = 56
DORM_BRICK_WALL_HALF_W = 12
DORM_BRICK_GATE_H = 96
DORM_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)
DORM_DOOR_OFF = 160
DORM_DOOR_W = 80
DORM_EMB_X2 = -1146
DORM_ENT_H = 100
DORM_ENT_HW = 48
DORM_FLOORS = 3
DORM_SLAB_T = 16
DORM_WALL = 16
DORM_WIN_HH = 44
DORM_WIN_HW = 36
DORM_WIN_MARGIN = 0  # gap between window frame bar and opening edge (0 = flush)
DORM_WIN_W, DORM_WIN_H, DORM_WIN_T = 20, 28, 3

DRAW_BRIDGE_FASCIA_TEXT = True

ENNIS_CURB_W = 8
ENNIS_CEMENT_WALL_CAP_H = 6
ENNIS_CEMENT_WALL_CAP_OVH = 2
ENNIS_CEMENT_WALL_H = 32
ENNIS_CEMENT_WALL_LAMP_POST_H = 160
ENNIS_CEMENT_WALL_PILLAR_EXTRA_H = 16
ENNIS_CEMENT_WALL_PILLAR_HW = 14
ENNIS_GATE_FENCE_BAR_T = 2
ENNIS_GATE_FENCE_HEIGHT = 96
ENNIS_GATE_FENCE_POST_W = 8
ENNIS_GATE_FENCE_SPACING = 16
ENNIS_GATE_FENCE_TOP_RAIL_DROP = 28
ENNIS_GATE_FENCE_TOP_RAIL_T = 2
ENNIS_GATE_FENCE_WEST_SHIFT = 24  # plain picket run sits this far west of the brick
# wall it used to butt against, so a short connector (post + cross rail) is needed
# to rejoin them at the south end of the picket run.
ENNIS_GATE_PANEL_COUNT = 12  # dozen decorative rectangular iron panels on the brick
ENNIS_GATE_PILLAR_LEG_T = 4  # leg thickness of the inverted-U (∩) separator pillars
ENNIS_GATE_PILLAR_OPENING_W = 12  # gap between the two legs of each ∩ pillar
ENNIS_GATE_PILLAR_GAP = 8  # clearance either side of a pillar, between it and a panel
ENNIS_GATE_PILLAR_EXTRA_H = 12  # how much taller the pillar is than a panel
ENNIS_GATE_PILLAR_CROSS_T = 2  # thickness of the decorative X cross-brace bars
ENNIS_PANEL_GAP = 8
ENNIS_PANEL_INNER_H = 12
ENNIS_PANEL_INNER_W = 28
ENNIS_PANEL_OUTER_H = 28
ENNIS_PANEL_OUTER_W = 48
ENNIS_PANEL_MOUNT_FOOT_DROP = 6  # how far the bracket drops onto the brick top
ENNIS_PANEL_MOUNT_FOOT_INSET = 6  # shift feet in from the corners toward center
ENNIS_HW = 160
ENNIS_PILLAR_BELL2_H = 27
ENNIS_PILLAR_BELL2_HW = (
    19  # tapered top section half-width (wider than before, less than post)
)
ENNIS_PILLAR_CAP_H = 3
ENNIS_PILLAR_CAP_OVH = 1
ENNIS_PILLAR_HW = 22
ENNIS_PILLAR_POST_H = 81
ENNIS_WALL_H = 96
ENNIS_WALL_PILLAR_H = (
    126  # 120 base + ENNIS_PANEL_MOUNT_FOOT_DROP, to stay taller than the raised gate
)
ENNIS_WALL_PILLAR_HW = 14
ENNIS_WALL_T = 8
ENNIS_WALL_X_OFFSET = 96

# Pixel-font bitmaps for fascia lettering. Each entry is a list of rows (top→bottom),
# where each row is a 4-bit Python integer: 1 = draw a block, 0 = empty space.
# The geometry modules read these values and emit Quake brush boxes for each set bit.
FASCIA_FONT = {
    "A": [0b0110, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
    "B": [0b1110, 0b1001, 0b1110, 0b1001, 0b1110, 0b0000],
    "C": [0b0111, 0b1000, 0b1000, 0b1000, 0b0111, 0b0000],
    "D": [0b1110, 0b1001, 0b1001, 0b1001, 0b1110, 0b0000],
    "E": [0b1111, 0b1000, 0b1110, 0b1000, 0b1111, 0b0000],
    "F": [0b1111, 0b1000, 0b1110, 0b1000, 0b1000, 0b0000],
    "G": [0b0111, 0b1000, 0b1011, 0b1001, 0b0111, 0b0000],
    "H": [0b1001, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
    "I": [0b1110, 0b0100, 0b0100, 0b0100, 0b1110, 0b0000],
    "J": [0b0011, 0b0001, 0b0001, 0b1001, 0b0110, 0b0000],
    "K": [0b1001, 0b1010, 0b1100, 0b1010, 0b1001, 0b0000],
    "L": [0b1000, 0b1000, 0b1000, 0b1000, 0b1111, 0b0000],
    "M": [0b1001, 0b1111, 0b1111, 0b1001, 0b1001, 0b0000],
    "N": [0b1001, 0b1101, 0b1011, 0b1001, 0b1001, 0b0000],
    "O": [0b0110, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
    "P": [0b1110, 0b1001, 0b1110, 0b1000, 0b1000, 0b0000],
    "R": [0b1110, 0b1001, 0b1110, 0b1010, 0b1001, 0b0000],
    "S": [0b0111, 0b1000, 0b0110, 0b0001, 0b1110, 0b0000],
    "T": [0b1111, 0b0100, 0b0100, 0b0100, 0b0100, 0b0000],
    "U": [0b1001, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
    "V": [0b1001, 0b1001, 0b1001, 0b0110, 0b0110, 0b0000],
    "W": [0b1001, 0b1001, 0b1111, 0b1111, 0b1001, 0b0000],
    "X": [0b1001, 0b0110, 0b0110, 0b0110, 0b1001, 0b0000],
    "Q": [0b0110, 0b1001, 0b1001, 0b1011, 0b0111, 0b0000],
    "Y": [0b1001, 0b0110, 0b0100, 0b0100, 0b0100, 0b0000],
    "Z": [0b1111, 0b0001, 0b0110, 0b1000, 0b1111, 0b0000],
    " ": [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000],
}

FENCE_H = 96
FENCE_SPACING = 16

FLOOR_Z1, FLOOR_Z2 = -16, 0

INDENT = 80

KNOTT_DRIVEWAY_HW = 128
KNOTT_EXTERIOR_ENABLED = True  # KH exterior (walls, windows, roof, sign)
KNOTT_INTERIOR_ENABLED = False  # temporarily disabled — KH interior (floor slabs, stairs, hallway walls, partitions)
KNOTT_MONSTERS_ENABLED = (
    False  # temporarily disabled — KH monsters (ogres + knights inside/on KH)
)
KNOTT_FLOORS = 5
KNOTT_FLOOR_H = 192
KNOTT_MULLION_PRO = 12
KNOTT_MULLION_W = 12
KNOTT_BUILDING_W = 1280
KNOTT_OFFSET = 90
KNOTT_WEST_TO_ORIG_CX = (
    (KNOTT_BUILDING_W + INDENT) // 2 + 64
)  # entrance + center window + bridge landing anchored on the true facade center;
# +64 shifts them east to match the curtain-wall position in the reference photos (ref/bridge01);
# capped so the accessible-entrance ramp still meets the fixed accessible path pad (X=2152)
KNOTT_WEST_TO_PIER_X = 40
KNOTT_RAIL_H = 72
KNOTT_ROOM_SPLITS = [-1072, -950, -1200, -850, -1300]
KNOTT_SHELF_D = 16
KNOTT_SHELF_H = 64
KNOTT_SHELF_W = 64
KNOTT_SIGN_PX_W, KNOTT_SIGN_PX_H = 3, 6
KNOTT_SIGN_TEXT = "MARION BURK KNOTT HALL"
KNOTT_SIGN_H = 72
KNOTT_SIGN_PADDING = 4
KNOTT_SIGN_Z_OFFSET = 20
KNOTT_SIDE_WINDOW_DIV_W = 12
KNOTT_SIDE_WINDOW_HALF_W = 120
KNOTT_SIDE_WINDOW_INNER_LEFT = 48
KNOTT_SIDE_WINDOW_INNER_RIGHT = 36
KNOTT_SIDE_WINDOW_PROTRUSION = 12
KNOTT_SHAFT_WALL = 8
KNOTT_STAIRS_HALF_N = 8
KNOTT_STAIR_CAP_RAISE = 16
KNOTT_STAIR_CAP_W = 24
KNOTT_STAIRS_POST_W = 4
KNOTT_STAIRS_RAIL_H = 72
KNOTT_STAIRS_RAIL_T = 4
KNOTT_STAIRS_STEP_R = KNOTT_FLOOR_H // (2 * KNOTT_STAIRS_HALF_N)
KNOTT_STAIRS_TREAD_X = 24
KNOTT_STAIR_OFFSET = 384
KNOTT_STAIR_RAIL_EXTENSION = 20
KNOTT_STAIR_RAIL_POST_D = 2
KNOTT_STAIR_RAIL_POST_W = 8
KNOTT_STEP_DEPTH = 24
KNOTT_STEP_N = 5
KNOTT_WALKWAY_ENABLED = True
KNOTT_WALL = 16
KNOTT_FRONT_WINDOW_HALF_W = 48
KNOTT_FRONT_WINDOW_MULLION_HALF_GAP = 6
KNOTT_Y1, KNOTT_Y2 = -1888, -233  # KNOTT_Y2 shifts KH 23 units closer to the bridge,
# undoing the incidental walkway-span stretch introduced when BRIDGE_Y1 narrowed the
# deck (-136 -> -113, see commit 87a86f6); restores the walkway gap
# (KNOTT_Y2 - BRIDGE_Y1) to ~120 units, matching the near-flush bridge/KH landing
# seen in ref/gmaps-kh-streetview-east.png.

PLAT_H = 8

BRIDGE_CENTER_PIER_SPAN = 1050
BRIDGE_OUTER_PIER_SPAN = 721
ROAD_DASH_LEN = 64
ROAD_GAP_LEN = 64
STREET_CHARLES_CURB_W = 8
STREET_DIV_HW = (
    6  # carved centerline slot half-width (doubled stripe thickness; see streets.py)
)
STREET_ENNIS_DIV_HW = 16
STREET_SURFACE_T = 2
ROAD_X1, ROAD_X2 = -256, 256
# Charles St curb-to-curb width models 1 travel lane + 1 parking lane each side
# (see docs/reference.rst "Charles St width validation" + satellite re-check):
# parking lane nearest each curb, travel lane between it and the centerline.
CHARLES_PARKING_LANE_W = 96
STREET_DIV_LINE_HW = 2  # half-width of each parking-lane stripe (dashed, white)

# ── Pedestrian crosswalks — thick white zebra stripes, flush with the road
# surface (carved out of the road/lane-marking brushes, same technique as the
# centerline and parking-lane stripes). See streets.py "PEDESTRIAN CROSSWALKS".
CROSSWALK_LEN = 80  # depth of the crossing along the direction of travel
CROSSWALK_STRIPE_W = 32  # width of each white stripe, across the crossing
CROSSWALK_GAP_W = 32  # gap between stripes (shows the road texture below)

SCALE = 15.108

SHOW_SUPPORTS = True
WORLD_EAST_BUFFER = 512


@dataclass
class LightingPreset:
    """All worldspawn lighting and fog fields for a single time-of-day."""

    ambient: str
    sunlight: str
    sunlight_color: str
    sunlight_dir: str  # "pitch yaw" — pitch = elevation above horizon, yaw = azimuth
    sunlight_penumbra: str
    fog: str  # "density r g b"

    def to_worldspawn(self) -> dict:
        return {
            "ambient": self.ambient,
            "_sunlight": self.sunlight,
            "_sunlight_color": self.sunlight_color,
            "_sunlight_dir": self.sunlight_dir,
            "_sunlight_penumbra": self.sunlight_penumbra,
            "_fog": self.fog,
        }


class FogDensity:
    OFF = 0.00
    LOW = 0.03
    MED = 0.06
    HIGH = 0.10


def make_fog(density: float, r: float, g: float, b: float) -> str:
    """Build a _fog worldspawn string from a FogDensity level and RGB color (0.0–1.0)."""
    return f"{density} {r} {g} {b}"


LIGHTING_PRESETS: dict[str, LightingPreset] = {
    "dawn": LightingPreset(
        ambient="30",
        sunlight="120",
        sunlight_color="255 200 140",  # pale orange
        sunlight_dir="8 -90",  # low on the eastern horizon
        sunlight_penumbra="40",
        fog=make_fog(FogDensity.LOW, 0.6, 0.5, 0.4),
    ),
    "midday": LightingPreset(
        ambient="90",
        sunlight="140",
        sunlight_color="255 245 210",  # warm white
        sunlight_dir="60 -60",
        sunlight_penumbra="30",
        fog=make_fog(FogDensity.LOW, 0.5, 0.5, 0.6),
    ),
    "golden_hour": LightingPreset(
        ambient="40",
        sunlight="160",
        sunlight_color="255 180 80",  # deep amber
        sunlight_dir="10 -90",  # low on the western horizon
        sunlight_penumbra="40",
        fog=make_fog(FogDensity.MED, 0.6, 0.4, 0.3),
    ),
    "dusk": LightingPreset(
        ambient="20",
        sunlight="100",
        sunlight_color="200 120 60",  # dusky orange-red
        sunlight_dir="5 -120",  # just below the horizon
        sunlight_penumbra="50",
        fog=make_fog(FogDensity.MED, 0.4, 0.3, 0.4),
    ),
    "overcast": LightingPreset(
        ambient="120",
        sunlight="0",
        sunlight_color="200 210 220",  # cool grey-white
        sunlight_dir="90 0",
        sunlight_penumbra="60",
        fog=make_fog(FogDensity.MED, 0.5, 0.5, 0.55),
    ),
    "night": LightingPreset(
        ambient="5",
        sunlight="20",
        sunlight_color="180 200 255",  # cool moonlight blue
        sunlight_dir="15 120",  # low moon, opposite side from sun
        sunlight_penumbra="10",
        fog=make_fog(FogDensity.HIGH, 0.05, 0.05, 0.15),  # dark blue-black
    ),
    "bright": LightingPreset(
        ambient="120",
        sunlight="255",
        sunlight_color="255 255 240",  # brilliant white with slight warmth
        sunlight_dir="75 -45",  # high sun, near overhead
        sunlight_penumbra="20",
        fog=make_fog(FogDensity.OFF, 0.5, 0.5, 0.6),
    ),
    "afternoon": LightingPreset(
        ambient="75",
        sunlight="160",
        sunlight_color="255 220 170",  # warm afternoon white
        sunlight_dir="35 -180",  # ~35° altitude, sun due south (Baltimore ~39°N)
        sunlight_penumbra="25",
        fog=make_fog(FogDensity.LOW, 0.5, 0.5, 0.6),
    ),
}

LIGHTING = LIGHTING_PRESETS["afternoon"]
FOG_DENSITY: float | None = None  # use preset fog density


class Textures:
    BRICK = "bricka2_1"
    BRICK_KH = "city6_8"
    BUILDING = "city2_1"
    CEMENT = "sfloor3_2"
    EXIT = "z_exit"
    DIVIDER = "sfloor3_2"
    FENCE = "metal4_4"
    CENTERLINE = (
        "win_fbylw_01"  # fullbright yellow, stand-in for a yellow line marking texture
    )
    PARKING_STRIPE = (
        "win_fbblu_01"  # named "blu" but reads more white than blue in-game, so
        # it works fine as a stand-in for the white parking-lane stripe texture
    )
    FLOOR = "sfloor3_2"
    FLOOR_KH = "sfloor3_2"
    GROUND = "ground1_1"
    HINT = "hint"
    MULCH = "grave13c"
    LAVA = "*lava1"
    PILLAR = "city6_8"
    RAIL = "metal5_4"
    ROAD = "thantech10_9"
    GABLE = "woodc1_cwht01"
    ROOF = "roofkell1"
    SHELF = "shelf_1"
    SIDEWALK = "sfloor3_2"
    SKY = "sky1"
    STONE = "sfloor3_2"
    TELEPORT = "*teleport"
    WALL = "city2_7"
    WHITE_STONE = "sfloor3_2"


@dataclass
class KnottSpec:
    floors: int
    floor_h: int
    wall_t: int
    x1: int
    x2: int
    y1: int
    y2: int
    driveway_hw: int


@dataclass
class BridgeSpec:
    x1: int
    x2: int
    y1: int
    y2: int
    arch_rise: int
    parapet_h: int
    walk_wall: int


@dataclass
class DormSpec:
    floor_h: int
    floors: int
    wall_t: int
    depth: int
    x1: int
    x2: int


# ── Derived / Dependent Constants ─────────────────────────────────────────────
KNOTT_ENT_HALF_W = 64
KNOTT_STAIR_LANDING_GAP = 16
KNOTT_EAST_PIER_FACE_OFFSET = 32
KNOTT_SHAFT_X_OFFSET = 16
KNOTT_SHAFT_W = 128
KNOTT_SHAFT_Y_OFFSET = 128
# Bridge north edge → Ennis south curb offset; ENNIS_NORTH_OFFSET then adds half-width.
ENNIS_BRIDGE_TO_SOUTH_EDGE = 640
ENNIS_NORTH_OFFSET = ENNIS_BRIDGE_TO_SOUTH_EDGE + ENNIS_HW
CHARLES_LAMP_POST_SETBACK = 160
CHARLES_PLATFORM_ROAD_OFFSET = 16
ROAD_VERGE_BUFFER = 32
DORM_PIER_FACE_OFFSET = 32
BRIDGE_LAMP_POST_CLEARANCE = 32

CHARLES_CRN_R = CHARLES_WALK_W
ENNIS_PILLAR_ZB = FLOOR_Z2
KNOTT_DRIVEWAY_CURB_CRN_R = CHARLES_WALK_W
KNOTT_DRIVEWAY_CURB_CRN_SEGS = CHARLES_CRN_SEGS
KNOTT_DRIVEWAY_CURB_WALK_W = CHARLES_WALK_W
# North curb/sidewalk extension (bulge) on the Ennis-driveway west ground
# section — the ground, its curb, and the NW junction corner all shift
# KNOTT_DRIVEWAY_CURB_BULGE_D further north (not east/into the road). The
# corner's curvature (unchanged radius) then eases the curb back to its
# base line on its own as it sweeps west toward angle 90. From there, a
# flat curb continues west for KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W before a
# straight closing curb slopes back down to the pre-bulge corner position
# over KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W (kept long/gradual for a subtle
# slope), with ground filling the wedge behind it.
KNOTT_DRIVEWAY_CURB_BULGE_D = 64
KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W = 64
KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W = 320
KNOTT_DRIVEWAY_ZT_N = FLOOR_Z2
# Treat the Knott west face as the root X anchor; nearby anchors derive from it.
KNOTT_X1 = 1206
KNOTT_PIER_X = KNOTT_X1 + KNOTT_WEST_TO_PIER_X
KNOTT_ORIG_CX = KNOTT_X1 + KNOTT_WEST_TO_ORIG_CX
KNOTT_ENT_X1, KNOTT_ENT_X2 = (
    KNOTT_ORIG_CX - KNOTT_ENT_HALF_W,
    KNOTT_ORIG_CX + KNOTT_ENT_HALF_W,
)
KNOTT_STAIRS_X2 = KNOTT_ENT_X1 - KNOTT_STAIR_LANDING_GAP

KNOTT_STAIRS_X1 = KNOTT_X1 + KNOTT_WALL + 2 * INDENT
KNOTT_WEST_ROOM_CX = (KNOTT_X1 + KNOTT_ENT_X1) // 2
KNOTT_X2 = KNOTT_X1 + KNOTT_BUILDING_W
KNOTT_NE_PIER_X = KNOTT_X2 - KNOTT_EAST_PIER_FACE_OFFSET
KNOTT_DRIVEWAY_CORRIDOR_X1 = KNOTT_X2
KNOTT_DRIVEWAY_CORRIDOR_X2 = (
    KNOTT_X2 + CHARLES_WALK_W + 2 * KNOTT_DRIVEWAY_HW + CHARLES_WALK_W
)
KNOTT_DRIVEWAY_WS_X1 = KNOTT_X2
KNOTT_DRIVEWAY_JCX_W = KNOTT_DRIVEWAY_WS_X1
KNOTT_DRIVEWAY_WS_X2 = KNOTT_X2 + KNOTT_DRIVEWAY_CURB_WALK_W
KNOTT_DRIVEWAY_RD_X1 = KNOTT_DRIVEWAY_WS_X2
CHARLES_PLT_BR_X = KNOTT_DRIVEWAY_RD_X1 + KNOTT_DRIVEWAY_HW // 2
KNOTT_DRIVEWAY_RD_X2 = KNOTT_DRIVEWAY_RD_X1 + 2 * KNOTT_DRIVEWAY_HW
KNOTT_DRIVEWAY_ES_X1 = KNOTT_DRIVEWAY_RD_X2
KNOTT_DRIVEWAY_ES_X2 = KNOTT_DRIVEWAY_RD_X2 + KNOTT_DRIVEWAY_CURB_WALK_W
KNOTT_DRIVEWAY_JCX_E = KNOTT_DRIVEWAY_ES_X2
KNOTT_CX = (KNOTT_X1 + KNOTT_X2) // 2
KNOTT_EAST_ROOM_CX = (KNOTT_ENT_X2 + KNOTT_X2) // 2
KNOTT_BIY1 = KNOTT_Y1 + KNOTT_WALL
KNOTT_BIY2 = KNOTT_Y2 - KNOTT_WALL
KNOTT_DRIVEWAY_Y1 = KNOTT_Y1
KNOTT_DRIVEWAY_Y2 = KNOTT_Y2
KNOTT_DRIVEWAY_EXT_Y1 = KNOTT_DRIVEWAY_Y2
KNOTT_STAIRS_Y1 = KNOTT_BIY2 - 256
# West bridge piers step back from the Knott pier using the two reference span widths.
# Piers 1-3 are derived; Pier 4 = KNOTT_PIER_X; Pier 5 = KNOTT_NE_PIER_X.
# Individual names are unpacked immediately after.
BRIDGE_ARCH_X = [
    KNOTT_PIER_X
    - BRIDGE_OUTER_PIER_SPAN
    - BRIDGE_CENTER_PIER_SPAN
    - BRIDGE_OUTER_PIER_SPAN,  # Pier 1 — west abutment pier
    KNOTT_PIER_X - BRIDGE_OUTER_PIER_SPAN - BRIDGE_CENTER_PIER_SPAN,  # Pier 2
    KNOTT_PIER_X
    - BRIDGE_OUTER_PIER_SPAN,  # Pier 3 (anchors Ennis Drive entrance pillars)
    KNOTT_PIER_X,  # Pier 4 — west KH pier (arch span terminus)
    KNOTT_NE_PIER_X,  # Pier 5 — east KH pier / NE pier
    3150,  # Pier 6 — mid-span pier in extended east section (moved east, clear of
    # KH driveway roadway [2566-2822]/sidewalks [2486-2902]; sits in Ennis Rd
    # pavement between the driveway and the Ennis-east teleport arch [3440-3472])
]
CHARLES_LAMP_POST_XS = [
    KNOTT_NE_PIER_X - CHARLES_LAMP_POST_EAST_SETBACK,
    KNOTT_PIER_X,
]
ENNIS_GATE_X1 = BRIDGE_ARCH_X[2] + ENNIS_PILLAR_HW + 80
ENNIS_PILLAR_X1 = BRIDGE_ARCH_X[2] - ENNIS_PILLAR_HW
ENNIS_PILLAR_X2 = BRIDGE_ARCH_X[2] + ENNIS_PILLAR_HW
CHARLES_LAMP_POST_H = BRIDGE_DZ2 - BRIDGE_LAMP_POST_CLEARANCE
_KNOTT_GROUND_FLOOR_H = (
    160  # nominal floor height used to anchor building to bridge/hill;
)
# independent of KNOTT_FLOOR_H (192) so scaling floor height doesn't flatten the hill.
KNOTT_GROUND_Z = 221  # hill-height anchor, re-derived from real-world elevation data.
# Was 64 (4.24 ft), based on an old, unscripted "~+7.2 ft at Knott Hall's west edge"
# estimate. Re-measured via scripts/sample_elevation.py (see docs/elevation_samples.csv,
# label "knott_climb_0": Knott Hall west edge at Ennis Y, +14.6 ft above the bridge-
# crossing baseline) -> round(14.6 * SCALE) == 221. See docs/reference.rst
# "Topology check" for the full re-measurement and its caveats (1 m DEM resolution,
# approximate anchor/bearing). Independent of BRIDGE_DZ2: the bridge deck (not the
# hill) was raised 32 units to make the KH walkway level (WALK_ZT1 == WALK_ZT2)
# without re-flattening the hill.
KNOTT_DRIVEWAY_ZT_S = KNOTT_GROUND_Z
KNOTT_Z2 = KNOTT_GROUND_Z + KNOTT_FLOORS * KNOTT_FLOOR_H
BRIDGE_X2 = KNOTT_PIER_X
ENNIS_Y = BRIDGE_Y2 + ENNIS_NORTH_OFFSET
CHARLES_LAMP_POST_YS = [ENNIS_Y - ENNIS_HW - CHARLES_LAMP_POST_SETBACK]
CHARLES_PLT_Y_OUT = ENNIS_Y - ENNIS_HW + CHARLES_PLATFORM_ROAD_OFFSET
CHARLES_PLT_Y_RET = ENNIS_Y + ENNIS_HW // 8
ENNIS_SW_EDGE = ENNIS_Y - ENNIS_HW - 3 * CHARLES_WALK_W - ROAD_VERGE_BUFFER
ENNIS_WALL_NY = ENNIS_Y + ENNIS_HW + ENNIS_PILLAR_HW * 2
KNOTT_DRIVEWAY_EXT_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_WALK_W
KNOTT_DRIVEWAY_JCY = ENNIS_Y - ENNIS_HW
PIER1_X, PIER2_X, PIER3_X, PIER4_X, PIER5_X, PIER6_X = BRIDGE_ARCH_X
# Center-span piers (2 and 3) cross a real hillside rather than flat grade —
# west_campus_terrain.py / knott_terrain.py's real-elevation data already
# rises well above FLOOR_Z2 at these two piers' footprints (verified via
# point-in-triangle sampling of each module's terrain grid at (X, Y=0)).
# Rather than carving a notch into that hill to meet a fixed FLOOR_Z2 base
# (which fights the real data and re-flattens a hillside that's supposed to
# be there), each pier's own base sits at the hill's real height instead —
# i.e. the pier stands ON TOP of the existing terrain rather than being
# embedded in it. Pier 3 (Knott side) reuses knott_terrain.py's own
# "Pier 3" hill-profile anchor (525, 171) + its flat-grade baseline (8),
# confirming this was the original terrain author's intent all along
# ("...so the whole bridge sits on fully-risen hill"). Pier 2 (west side)
# is interpolated from west_campus_terrain.py's real grid columns at
# X=-700/-400, Y=0. Piers without an entry here keep the default FLOOR_Z2.
BRIDGE_PIER_GROUND_Z = {
    # Base Z for each center-span pier. Must be at or below the lowest terrain
    # point under the pier's full X (px±BRIDGE_PILLAR_HW) and Y (bridge span,
    # including overhang) footprint so the pier doesn't float above the
    # hillside anywhere along its base.
    # PIER2 (-525): west terrain min under full footprint ≈15 — use FLOOR_Z2 (0).
    # PIER3 (+525): KH hill profile min under full footprint ≈30 (re-sampled;
    # the old "~57" figure predates later hill-profile edits and left this
    # pier's base — previously 48 — floating above ground near its west/edge
    # corners). Use 20 for a safe margin below the resampled minimum.
    PIER2_X: 0,  # west campus terrain min under bridge span ≈15; use 0 (FLOOR_Z2)
    PIER3_X: 20,  # KH hill min under full pier footprint ≈30; use 20 to stay buried
}
DORM_FLOOR_H = (
    128  # dorm-specific floor height (shorter than Knott's KNOTT_FLOOR_H=192)
)
DORM_ROOF_H = 192  # roof ridge rise above eave (independent of floor height)
DORM_H = DORM_FLOORS * DORM_FLOOR_H
DORM_PIER_X = min(BRIDGE_ARCH_X)
DORM_EAVE_Z = FLOOR_Z2 + DORM_H + DORM_WALL
DORM_RIDGE_Z = DORM_EAVE_Z + DORM_ROOF_H
DORM_WALL_N_Y1 = BRIDGE_Y2 + BRIDGE_PILLAR_OVERHANG
DORM_WALL_S_Y2 = -(BRIDGE_Y2 + BRIDGE_PILLAR_OVERHANG)
CHARLES_PLT_X_OUT = ROAD_X2 // 4
CHARLES_PLT_X_RET = -(ROAD_X2 * 3 // 4)
ENNIS_X1 = ROAD_X1
ROAD_Z = FLOOR_Z2 + 8

WALK_X1 = KNOTT_ORIG_CX - KNOTT_ENT_HALF_W
WALK_X2 = KNOTT_ORIG_CX + KNOTT_ENT_HALF_W
WALK_ZT2 = KNOTT_GROUND_Z + KNOTT_FLOOR_H + KNOTT_WALL
WALL_T = 16
WIN_HALF = 24
WORLD_X1 = (
    -5135
)  # re-derived from real-world measurement, see docs/reference.rst § World scale
BRIDGE_X1 = (
    -1967
)  # fixed anchor, independent of WORLD_X1 — preserves the bridge/west-campus span
# (~213 ft, already a reasonable real-world estimate) after the world rectangle was
# enlarged to the full real-world footprint; see docs/reference.rst § World scale.
# The gap between WORLD_X1 and BRIDGE_X1 is unmodeled real estate pending further
# re-derivation (west campus terrain/dorms further out).
BRIDGE_SEG_W = (BRIDGE_X2 - BRIDGE_X1) / BRIDGE_SEG_SPAN_W
WORLD_X2 = (
    9100  # re-derived from real-world measurement, see docs/reference.rst § World scale;
    # bumped from 7708 to make room for Maryland Hall (MARYLAND_X2 ~8979, see below),
    # leaving a ~121-unit (~8ft) clearance margin before the sealing wall.
)
WORLD_X2_EXT = (
    WORLD_X2 + WORLD_EAST_BUFFER
)  # extended east boundary — actual world-shell east wall (streets.py); NOT used
# for Ennis/east-campus feature placement below, see _EAST_FEATURES_X2_EXT.
_EAST_FEATURES_X2 = 2976  # fixed anchor, independent of WORLD_X2 — pre-resize
# WORLD_X2. Ennis Drive/east-campus features (teleport arch, gate, cement plaza)
# stay pinned here rather than stretching out to the new, much larger WORLD_X2,
# which now represents unmodeled real estate further east; see docs/reference.rst
# § World scale. NOTE: bridge.py/entities.py/knott_terrain.py still reference the
# live WORLD_X2_EXT internally for these same features — to be repointed at this
# fixed anchor when those modules are re-enabled/re-derived.
_EAST_FEATURES_X2_EXT = _EAST_FEATURES_X2 + WORLD_EAST_BUFFER
ENNIS_CEMENT_EAST_SHIFT = 160  # nudges the east cement-wall pillar/lamp post
# further east (and extends the wall to meet it); see streets.py cement wall build.
ENNIS_CEMENT_X2 = (
    _EAST_FEATURES_X2 - WALL_T - ARCH_SLAB_W // 2 + ENNIS_CEMENT_EAST_SHIFT
)  # aligned with east teleport centre, plus ENNIS_CEMENT_EAST_SHIFT
ENNIS_GATE_X2 = (ENNIS_GATE_X1 + _EAST_FEATURES_X2_EXT - WALL_T) // 2
ENNIS_CEMENT_X1 = ENNIS_GATE_X2
ENNIS_CEMENT_LAMP_POSTS = [
    (ENNIS_CEMENT_X1, ENNIS_WALL_NY + ENNIS_WALL_T // 2, FLOOR_Z2 + 234),
    (ENNIS_CEMENT_X2, ENNIS_WALL_NY + ENNIS_WALL_T // 2, FLOOR_Z2 + 234),
]
ENNIS_X2 = _EAST_FEATURES_X2_EXT - WALL_T
BRIDGE_EAST_SHIFT_END = -(
    (_EAST_FEATURES_X2_EXT - WALL_T) - BRIDGE_ARCH_X[4]
) * math.tan(math.radians(BRIDGE_EAST_SPAN_ANGLE))
BRIDGE_SPAN_CENTRES = [
    (BRIDGE_X1 + BRIDGE_ARCH_X[0]) // 2,
    (BRIDGE_ARCH_X[0] + BRIDGE_ARCH_X[1]) // 2,
    (BRIDGE_ARCH_X[1] + BRIDGE_ARCH_X[2]) // 2,
    (BRIDGE_ARCH_X[2] + BRIDGE_X2) // 2,
    (BRIDGE_X2 + BRIDGE_ARCH_X[4]) // 2,
    (BRIDGE_ARCH_X[4] + BRIDGE_ARCH_X[5]) // 2,
    (BRIDGE_ARCH_X[5] + _EAST_FEATURES_X2_EXT - WALL_T) // 2,
]
BRIDGE_PEND_XS = BRIDGE_SPAN_CENTRES
WORLD_Y1, WORLD_Y2 = (
    -6642,  # re-derived from real-world measurement, see docs/reference.rst § World scale
    4085,
)
CHARLES_Y1 = (
    -2768
)  # fixed anchor, independent of WORLD_Y1 — preserves the modeled Charles St/bridge
# span after the world rectangle was enlarged to the full real-world footprint
# (previously WORLD_Y1 + WALL_T); see docs/reference.rst § World scale. The gap
# between WORLD_Y1 and CHARLES_Y1 is unmodeled real estate pending further
# re-derivation.
CHARLES_PLT_Y_S = CHARLES_Y1 + CHARLES_PLT_W // 2 + 48
CHARLES_Y2 = 1696  # fixed anchor, independent of WORLD_Y2 — see CHARLES_Y1 above.
DORM_NORTH_Y2 = 1546  # fixed anchor, independent of WORLD_Y2 — see CHARLES_Y1 above.
DORM_NORTH_Y1 = DORM_NORTH_Y2 - DORM_DEPTH
DORM_SOUTH1_Y1 = (
    -1968
)  # pinned: south dorms stay at original position despite world extension
DORM_SOUTH1_Y2 = DORM_SOUTH1_Y1 + DORM_DEPTH
DORM_SOUTH1_CY = (DORM_SOUTH1_Y1 + DORM_SOUTH1_Y2) // 2
DORM_SOUTH2_Y1 = DORM_SOUTH1_Y2
DORM_SOUTH2_Y2 = DORM_SOUTH2_Y1 + DORM_DEPTH
DORM_SOUTH2_CY = (DORM_SOUTH2_Y1 + DORM_SOUTH2_Y2) // 2
WORLD_Z2 = max(640, KNOTT_Z2 + 512)
KNOTT_SHAFT_X1 = KNOTT_ENT_X2 + KNOTT_SHAFT_X_OFFSET
KNOTT_SHAFT_X2 = KNOTT_SHAFT_X1 + KNOTT_SHAFT_W
KNOTT_SHAFT_Y1, KNOTT_SHAFT_Y2 = KNOTT_BIY2 - KNOTT_SHAFT_Y_OFFSET, KNOTT_BIY2
KNOTT_STAIRS_Y2 = KNOTT_SHAFT_Y2
KNOTT_STAIRS_MID_Y = (KNOTT_STAIRS_Y1 + KNOTT_STAIRS_Y2) // 2
DORM_NORTH_CY = (DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2
BRIDGE_EAST_PIVOT_X = BRIDGE_ARCH_X[4]


# ── Function-Derived Constants ────────────────────────────────────────────────
# Helper functions below; the constants computed from them follow at the end.
def arch_z_at(x):
    """Z offset above flat datum for the deck profile at x.

    Piecewise, matching the real Loyola bridge (ref/bridge08): the centre span
    over Charles Street (|x| <= half the centre pier span, ±525) is a shallow
    parabolic arch cresting at BRIDGE_ARCH_RISE over X=0; the two approach spans
    (525 <= |x| <= 1246) descend as straight rakes from BRIDGE_ARCH_PIER_RISE at
    the centre piers down to 0 at the outer piers. Beyond ±BRIDGE_X2 the deck is
    flat (approach to world wall / KH walkway).
    """
    ax = abs(x)
    if ax >= BRIDGE_X2:
        return 0.0
    center_half = BRIDGE_CENTER_PIER_SPAN / 2.0  # ±525, PIER2/PIER3
    if ax <= center_half:
        return (
            BRIDGE_ARCH_RISE
            - (BRIDGE_ARCH_RISE - BRIDGE_ARCH_PIER_RISE) * (ax / center_half) ** 2
        )
    return BRIDGE_ARCH_PIER_RISE * (BRIDGE_X2 - ax) / float(BRIDGE_X2 - center_half)


def deck_bot_z(x):
    """Z coordinate of the deck underside at a given X position."""
    return BRIDGE_DZ1 + arch_z_at(x)


def deck_top_z(x):
    """Z coordinate of the deck surface (top face) at a given X position."""
    return BRIDGE_DZ2 + arch_z_at(x)


def ft_to_units(feet, inches=0):
    """Convert real-world feet (+ optional inches) to Quake units."""
    return round((feet + inches / 12) * SCALE)


BRIDGE_DECK_Z = deck_top_z(0) + 8
WALK_ZT1 = int(deck_top_z(KNOTT_ORIG_CX))
BRIDGE_PAR_W = ft_to_units(2, 6)
BRIDGE_PILLAR_HW = ft_to_units(2, 5.5)
BRIDGE_PILLAR_PYR_W = BRIDGE_PILLAR_HW  # cap flush with the pillar post below (was
# a separate, wider constant — 45 vs 37 — which made the cap overhang the post
# on its E/W faces; only the documented N/S overhangs (CAP_IN_OVH/CAP_OUT_OVH)
# should apply)
BRIDGE_BLK_PIR_M = BRIDGE_PILLAR_HW + BRIDGE_BLK_HW + 4
DORM_X2 = DORM_PIER_X + BRIDGE_PILLAR_HW + DORM_PIER_FACE_OFFSET
FENCE_X1 = DORM_X2 + DORM_FENCE_OFFSET
FENCE_X2 = FENCE_X1 + 2
DORM_X1 = DORM_X2 - 576
DORM_CX = (DORM_X1 + DORM_X2) // 2
ENNIS_GATE_PILLAR_W = ENNIS_GATE_PILLAR_OPENING_W + 2 * ENNIS_GATE_PILLAR_LEG_T

# Fixed spawn / destination coordinates used by multiple teleport destinations.
KH_ROOFTOP_ORIGIN = "2149 -264 904"  # top of Knott Hall rooftop, facing-west landing

KNOTT = KnottSpec(
    floors=KNOTT_FLOORS,
    floor_h=KNOTT_FLOOR_H,
    wall_t=KNOTT_WALL,
    x1=KNOTT_X1,
    x2=KNOTT_X2,
    y1=KNOTT_Y1,
    y2=KNOTT_Y2,
    driveway_hw=KNOTT_DRIVEWAY_HW,
)
BRIDGE = BridgeSpec(
    x1=BRIDGE_X1,
    x2=BRIDGE_X2,
    y1=BRIDGE_Y1,
    y2=BRIDGE_Y2,
    arch_rise=BRIDGE_ARCH_RISE,
    parapet_h=BRIDGE_PAR_H,
    walk_wall=BRIDGE_WALK_WALL,
)
DORM = DormSpec(
    floor_h=DORM_FLOOR_H,
    floors=DORM_FLOORS,
    wall_t=DORM_WALL,
    depth=DORM_DEPTH,
    x1=DORM_X1,
    x2=DORM_X2,
)

# ── Maryland Hall — PROVISIONAL placeholder anchor, pending re-derivation ──────
# Real building (OSM way 1019882993, operator "Loyola University Maryland"),
# east of Ennis Parallel near the Sellinger School of Business. Derived from
# OSM footprint GPS coordinates (not a pixel/satellite-screenshot measurement
# like other anchors in this file), converted via the real-world-ft -> Quake-
# unit transform anchored at KNOTT_X1/KNOTT_Y2 (SCALE = 15.108 units/ft) —
# validated to ~4% against the real Knott Hall footprint width, but the
# Y-axis correspondence is NOT independently cross-checked.
#
# That full-scale conversion (6385/8979/412/1622, below in a comment for
# reference) placed the block ~230 ft beyond the KH driveway/Ennis Drive
# corner — because Ennis/east-campus constants (_EAST_FEATURES_X2 etc.) were
# deliberately left at an older, ~2.4-2.6x more compressed scale than the
# rest of the map (ENNIS_Y could not be used to cross-check for the same
# reason). Left uncorrected, Maryland Hall would sit far past where Ennis
# Parallel/the rest of the modeled east campus ends. Rescaled here by /2.5
# (the middle of that ~2.4-2.6x range) relative to the KNOTT_X1/KNOTT_Y2
# anchor so the stub lands just past Ennis Parallel, consistent with the
# compressed geometry around it. Treat these values the way KNOTT_GROUND_Z
# used to be treated before its own re-derivation: a reasonable placeholder,
# not a verified measurement — re-derive against ref/ imagery before doing
# detailed facade work.
_MARYLAND_COMPRESSION = 2.5  # matches Ennis/east-campus's ~2.4-2.6x compression
_MARYLAND_X1_FULL_SCALE = 6385  # pre-compression OSM-derived value
_MARYLAND_X2_FULL_SCALE = 8979
_MARYLAND_Y1_FULL_SCALE = 412
_MARYLAND_Y2_FULL_SCALE = 1622
MARYLAND_X1 = KNOTT_X1 + round(
    (_MARYLAND_X1_FULL_SCALE - KNOTT_X1) / _MARYLAND_COMPRESSION
)
MARYLAND_X2 = KNOTT_X1 + round(
    (_MARYLAND_X2_FULL_SCALE - KNOTT_X1) / _MARYLAND_COMPRESSION
)
MARYLAND_Y1 = KNOTT_Y2 + round(
    (_MARYLAND_Y1_FULL_SCALE - KNOTT_Y2) / _MARYLAND_COMPRESSION
)
MARYLAND_Y2 = KNOTT_Y2 + round(
    (_MARYLAND_Y2_FULL_SCALE - KNOTT_Y2) / _MARYLAND_COMPRESSION
)
MARYLAND_FLOORS = 3  # real Maryland Hall is a 3-story academic building
MARYLAND_FLOOR_H = 128  # matches DORM_FLOOR_H; no facade detail derived yet
MARYLAND_H = MARYLAND_FLOORS * MARYLAND_FLOOR_H
# Ground level under the massing block. The hill keeps climbing east of Knott
# Hall (KNOTT_GROUND_Z=221) toward Ennis Parallel/Maryland Hall — re-measured
# via scripts/sample_elevation.py at +17.3 to +19.3 ft above the bridge-
# crossing baseline ("knott_climb_2".."knott_climb_4", 262 -> 291 units; see
# docs/reference.rst "Topology check"). Without this, the stub sat flush with
# FLOOR_Z2 (0) and appeared sunk far below the surrounding terrain. 291 is
# used as the far (Ennis-side) end of that climb, closest to Maryland Hall's
# real-world location.
MARYLAND_GROUND_Z = 291

# maryland_terrain.py — flat mound under/around the stub, sloping down to the
# surrounding FLOOR_Z2 plaza on all four sides so the building doesn't float
# on a bare cliff edge. MARGIN is the flat apron beyond the footprint before
# the slope starts; RAMP_W is the horizontal run of that slope — sized for a
# ~20.8° grade (291/768) so it's comfortably walkable in Quake, not the
# ~48.7° (291/256) wall the first pass produced. Both are rough placeholder
# values (no real-world grading data yet), sized only to stay clear of the
# Ennis Drive/east-campus features to the west (_EAST_FEATURES_X2=2976) and
# Ennis Road to the north (ENNIS_Y - ENNIS_HW=753) — see maryland_terrain.py
# for the actual geometry.
MARYLAND_TERRAIN_MARGIN = 192
MARYLAND_TERRAIN_RAMP_W = 768


# South-dorm raised terrace + gentler frontage hill out to Charles Street.
# The south-dorm pad sits flat on a terrace at FLOOR_Z2 + SDORM_LIFT; east of the
# pad a gentle ramp descends to grade at SDORM_TOE_X (the "hill out to Charles St").
SDORM_LIFT = 128  # terrace height = new south-dorm floor level
SDORM_TERRACE_X2 = DORM_X2 + 216  # east edge of flat terrace (= south fence line)
SDORM_TOE_X = -400  # frontage ramp reaches grade (z=0) here, near the road
# N-S decline at/east of the front fence: from the brick wall's south pillar down
# to the north side of the bridge, so the iron fence stays connected to grade.
SDORM_SLOPE_Y_S = DORM_SOUTH2_Y2 + DORM_DOOR_OFF + DORM_DOOR_W // 2 + 96  # south pillar
SDORM_SLOPE_Y_N = BRIDGE_Y2  # north side of bridge
SDORM_WALL_X = DORM_PIER_X  # brick-wall centreline: divides the flat dorm pad (west)
# from the strip that declines north between the wall and the fence (east).

# South-dorm stairwell — steps cut into the south-dorm-1 footprint, descending west
# to the existing west-wall tunnel door, bridging the SDORM_LIFT drop down to the
# tunnel floor (z=0). The footprint below is carved out of both the terrace fill
# (streets.py) and the dorm interior floor (west_campus.py); the steps fill it.
SDORM_STAIR_HW = 40  # half-width (matches the west-wall door opening)
SDORM_STAIR_N = SDORM_LIFT // 16  # number of 16-high steps (= 8)
SDORM_STAIR_RISE = SDORM_LIFT // SDORM_STAIR_N  # per-step rise (= 16)
SDORM_STAIR_RUN = 32  # tread depth (E-W) per step
SDORM_STAIR_X1 = (
    DORM_X1 + KNOTT_STAIR_LANDING_GAP
)  # first-step / floor-hole west edge (= interior face)
SDORM_STAIR_X2 = SDORM_STAIR_X1 + SDORM_STAIR_N * SDORM_STAIR_RUN  # east edge of run
SDORM_STAIR_Y1 = DORM_SOUTH1_CY - SDORM_STAIR_HW
SDORM_STAIR_Y2 = DORM_SOUTH1_CY + SDORM_STAIR_HW

# Front stone walkway footprint — a flush paved path inlaid into the dorm terrace
# (top level with the surrounding ground). Shared by the path fill (west_campus.py)
# and the matching terrace carve (streets.py) so the two stay aligned.
DORM_FRONT_WALKWAY_X2 = FENCE_X1 - DORM_FRONT_WALKWAY_FENCE_OFFSET  # outer (east) edge
DORM_FRONT_WALKWAY_X1 = (
    DORM_FRONT_WALKWAY_X2 - DORM_FRONT_WALKWAY_W
)  # inner (west) edge
DORM_FRONT_WALKWAY_SPUR_X1 = (
    DORM_PIER_X + DORM_BRICK_WALL_HALF_W
)  # spur west = wall E face
DORM_FRONT_WALKWAY_SPUR_Y2 = (
    DORM_SOUTH2_Y2 + DORM_DOOR_OFF + DORM_DOOR_W // 2
)  # spur runs north to the brick-wall door's north jamb

_fog = (
    make_fog(FOG_DENSITY, *[float(x) for x in LIGHTING.fog.split()[1:]])
    if FOG_DENSITY is not None
    else LIGHTING.fog
)

# ── Voxel tree profiles ──────────────────────────────────────────────────────
# Each profile is a list of strings rendered top-to-bottom (index 0 = crown tip).
# Characters: 'L' = leaf (GROUND), 'B' = branch (MULCH), 'T' = trunk (MULCH),
#             ' ' = empty.  All strings in a profile must be the same width.
# Rendered by geometry.make_pixel_tree() as two perpendicular crossed fins.
TREE_PROFILES: dict[str, list[str]] = {
    # Narrow columnar tree — Baltimore ginkgo / street tree style
    "street": [
        "  LLL  ",
        " LLLLL ",
        "LLLLLLL",
        " LLLLL ",
        "  LLL  ",
        "  BBB  ",
        "  TTT  ",
        "  TTT  ",
        "  TTT  ",
        "  TTT  ",
    ],
    # Broad-crowned deciduous tree — red maple / oak style
    "deciduous": [
        "   LLL   ",
        "  LLLLL  ",
        " LLLLLLL ",
        "LLLLLLLLL",
        " LLLLLLL ",
        "  LLLLL  ",
        "   LBL   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
    ],
    # Conifer — pine / fir style
    "pine": [
        "    L    ",
        "   LLL   ",
        "  LLLLL  ",
        " LLLLLLL ",
        "  LLLLL  ",
        " LLLLLLL ",
        "LLLLLLLLL",
        "   BBB   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
    ],
    # Large detailed broad-crown tree — fine voxels (vox_size=8), 26 cols × 41 rows.
    # At vox_size=8: 208 units wide crown, 328 units tall.
    # Crown (rows 0-25) drops straight to trunk (rows 26-40), no branch zone.
    "large": [
        "            LL            ",  # row  0 — sparse crown tip
        "          LLLLLL          ",  # row  1
        "        LLLLLLLLLL        ",  # row  2
        "      LLLLLLLLLLLLLL      ",  # row  3
        "    LLLLLLLLLLLLLLLLLL    ",  # row  4
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row  5
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row  6
        " LLLLLLLLLLLLLLLLLLLLLLLL ",  # row  7
        "LLLLLLLLLLLLLLLLLLLLLLLLL ",  # row  8 — slight asymmetry
        "LLLLLLLLLLLLLLLLLLLLLLLLLL",  # row  9 — widest
        "LLLLLLLLLLLLLLLLLLLLLLLLLL",  # row 10
        " LLLLLLLLLLLLLLLLLLLLLLLL ",  # row 11
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row 12
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row 13
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row 14 — second swell
        " LLLLLLLLLLLLLLLLLLLLLLLL ",  # row 15
        "LLLLLLLLLLLLLLLLLLLLLLLLLL",  # row 16
        " LLLLLLLLLLLLLLLLLLLLLLL  ",  # row 17 — asymmetric droop
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row 18
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row 19
        "    LLLLLLLLLLLLLLLLLL    ",  # row 20
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row 21 — natural bulge
        "    LLLLLLLLLLLLLLLLLL    ",  # row 22
        "      LLLLLLLLLLLLLL      ",  # row 23
        "       LLLLLLLLLLLL       ",  # row 24
        "        LLLLLLLLL         ",  # row 25 — lower crown
        "           TTTT           ",  # row 26 — trunk begins (no branch zone)
        "           TTTT           ",  # row 27
        "           TTTT           ",  # row 28
        "           TTTT           ",  # row 29
        "           TTTT           ",  # row 30
        "           TTTT           ",  # row 31
        "           TTTT           ",  # row 32
        "           TTTT           ",  # row 33
        "           TTTT           ",  # row 34
        "           TTTT           ",  # row 35
        "           TTTT           ",  # row 36
        "           TTTT           ",  # row 37
        "           TTTT           ",  # row 38
        "           TTTT           ",  # row 39
        "           TTTT           ",  # row 40 — base
    ],
}


WORLDSPAWN_FIELDS = {
    "wad": "quake101.wad;ad.wad;makkon_building.wad",
    "message": "Loyola University Maryland - Charles Street Pedestrian Bridge",
    "sky": Textures.SKY,
    "dmflags": "128",
    **{**LIGHTING.to_worldspawn(), "_fog": _fog},
}

# ── Sewer tunnel under Charles Street ───────────────────────────────────────
# A giant cylindrical storm-sewer running the full length of Charles St,
# buried well below the road slab (FLOOR_Z1) so it never intersects any
# street/building foundation above. Access is via a manhole cover at street
# level (a trigger_teleport, matching the bridge abutment's teleport-arch
# idiom) rather than a physically carved shaft through the road slab.
SEWER_ENABLED = True
SEWER_WALL_T = 16  # tube wall thickness
SEWER_RIN = 224  # inner (passable) radius — 448-unit diameter, slightly under
# the 512-unit Charles St curb-to-curb width (ROAD_X2 - ROAD_X1) above
SEWER_ROUT = SEWER_RIN + SEWER_WALL_T
SEWER_SEGS = 16  # wedge segments around the full 360° circle
SEWER_ZC = -320  # tube centre depth — top of the outer wall sits at -80,
# comfortably below FLOOR_Z1 (-16), the bottom of every street/building slab
SEWER_Y1, SEWER_Y2 = CHARLES_Y1, CHARLES_Y2  # spans the full modeled street
SEWER_CAP_T = 32  # end-cap thickness sealing off both ends of the tube
SEWER_TEX = Textures.GROUND  # aged concrete/stone stand-in
SEWER_LIGHT_SPACING = 768  # distance between interior point lights

MANHOLE_X, MANHOLE_Y = 185, 946  # user-specified surface location
MANHOLE_R = 48  # cover radius
MANHOLE_COVER_T = 4  # visual cover thickness
MANHOLE_DEST_Z = SEWER_ZC  # teleport destination inside the tube's hollow
# (falls a short, safe distance onto the curved floor below)
MANHOLE_RETURN_Y_OFFSET = 96  # the "climb out" pad sits this far north of the
# landing spot, so arriving players don't immediately re-trigger the return
# teleport underfoot
