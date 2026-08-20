"""Constants and worldspawn fields derived from other constant modules."""

import math

from ..wads import WAD_FILES as _WAD_FILES
from .bridge import (
    BRIDGE_ARCH_PIER_RISE,
    BRIDGE_ARCH_RISE,
    BRIDGE_CENTER_PIER_SPAN,
    BRIDGE_CENTER_SPAN_OFFSET,
    BRIDGE_DZ1,
    BRIDGE_DZ2,
    BRIDGE_EAST_SPAN2_LEN,
    BRIDGE_OUTER_PIER_SPAN,
    BRIDGE_PAR_H,
    BRIDGE_PILLAR_OVERHANG,
    BRIDGE_SEG_SPAN_W,
    BRIDGE_WALK_WALL,
    BRIDGE_WEST_OUTER_PIER_SPAN,
    BRIDGE_Y1,
    BRIDGE_Y2,
    PIER6_ROTATION_DEG,
    BridgeSpec,
)
from .dorm import (
    DORM_BRICK_WALL_HW,
    DORM_DEPTH,
    DORM_DOOR_OFF,
    DORM_DOOR_W,
    DORM_FENCE_OFFSET,
    DORM_FRONT_WALKWAY_FENCE_OFFSET,
    DORM_FRONT_WALKWAY_W,
)
from .ennis import (
    ENNIS_CURB_W,
    ENNIS_GATE_PILLAR_LEG_T,
    ENNIS_GATE_PILLAR_OPENING_W,
    ENNIS_HW,
    ENNIS_PILLAR_HW,
    ENNIS_WIDEN_N,
)
from .knott import (
    KNOTT_BUILDING_W,
    KNOTT_DRIVEWAY_HW,
    KNOTT_FLOOR_H,
    KNOTT_FLOORS,
    KNOTT_WALL_T,
    KNOTT_WEST_TO_ORIG_CX,
    KNOTT_WEST_TO_PIER_X,
    KNOTT_Y1,
    KNOTT_Y2,
    KnottSpec,
)
from .lighting import FOG_DENSITY, LIGHTING, make_fog
from .streets import (
    CHARLES_CRN_SEGS,
    CHARLES_LAMP_POST_EAST_SETBACK,
    CHARLES_WALK_W,
    ROAD_X1,
    ROAD_X2,
    STREET_DIV_HW,
)
from .textures import SKYBOX_WORLDSPAWN
from .world import ARCH_SLAB_W, ENNIS_PULL_S, FLOOR_Z2, SCALE, WORLD_EAST_BUFFER

# Derived constants.
KNOTT_ENT_HALF_W = 64
KNOTT_EAST_PIER_FACE_OFFSET = 32
# Bridge north edge to the Ennis south curb.
ENNIS_BRIDGE_TO_SOUTH_EDGE = 640 - ENNIS_PULL_S
# Additional northward shift for the Ennis centerline.
ENNIS_CENTERLINE_SHIFT_N = 183
ENNIS_NORTH_OFFSET = ENNIS_BRIDGE_TO_SOUTH_EDGE + ENNIS_HW + ENNIS_CENTERLINE_SHIFT_N
CHARLES_LAMP_POST_SETBACK = 104  # Offset south of the Ennis curb.
ROAD_VERGE_BUFFER = -56  # Additional padding for the Ennis south grass verge.
DORM_PIER_FACE_OFFSET = 32
BRIDGE_LAMP_POST_CLEARANCE = 32

CHARLES_CRN_R = CHARLES_WALK_W
KNOTT_DRIVEWAY_CURB_CRN_R = CHARLES_WALK_W
KNOTT_DRIVEWAY_CURB_CRN_SEGS = CHARLES_CRN_SEGS
KNOTT_DRIVEWAY_CURB_WALK_W = CHARLES_WALK_W
# North curb and sidewalk bulge on the Ennis-driveway west ground section.
KNOTT_DRIVEWAY_CURB_BULGE_D = 128
KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W = 128
KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W = 320
KNOTT_DRIVEWAY_ZT_N = FLOOR_Z2
# Treat the Knott west face as the root X anchor.
KNOTT_X1 = 1206
KNOTT_PIER_X = KNOTT_X1 + KNOTT_WEST_TO_PIER_X
KNOTT_ORIG_CX = KNOTT_X1 + KNOTT_WEST_TO_ORIG_CX
KNOTT_X2 = KNOTT_X1 + KNOTT_BUILDING_W
KNOTT_NE_PIER_X = KNOTT_X2 - KNOTT_EAST_PIER_FACE_OFFSET
# Shifts the driveway and eastern bridge piers east of the building wall.
KNOTT_DRIVEWAY_X_SHIFT = 300
KNOTT_DRIVEWAY_CORRIDOR_X1 = KNOTT_X2 + KNOTT_DRIVEWAY_X_SHIFT
KNOTT_DRIVEWAY_CORRIDOR_X2 = (
    KNOTT_X2
    + KNOTT_DRIVEWAY_X_SHIFT
    + CHARLES_WALK_W
    + 2 * KNOTT_DRIVEWAY_HW
    + CHARLES_WALK_W
)
KNOTT_DRIVEWAY_WS_X1 = KNOTT_X2 + KNOTT_DRIVEWAY_X_SHIFT
KNOTT_DRIVEWAY_JCX_X1 = KNOTT_DRIVEWAY_WS_X1
KNOTT_DRIVEWAY_WS_X2 = KNOTT_X2 + KNOTT_DRIVEWAY_X_SHIFT + KNOTT_DRIVEWAY_CURB_WALK_W
KNOTT_DRIVEWAY_RD_X1 = KNOTT_DRIVEWAY_WS_X2
KNOTT_DRIVEWAY_RD_X2 = KNOTT_DRIVEWAY_RD_X1 + 2 * KNOTT_DRIVEWAY_HW
KNOTT_DRIVEWAY_ES_X1 = KNOTT_DRIVEWAY_RD_X2
KNOTT_DRIVEWAY_ES_X2 = KNOTT_DRIVEWAY_RD_X2 + KNOTT_DRIVEWAY_CURB_WALK_W
KNOTT_DRIVEWAY_JCX_E = KNOTT_DRIVEWAY_ES_X2
KNOTT_DRIVEWAY_Y1 = KNOTT_Y1
KNOTT_DRIVEWAY_Y2 = KNOTT_Y2
KNOTT_DRIVEWAY_EXT_Y1 = KNOTT_DRIVEWAY_Y2
# Bridge pier X positions, west to east.
BRIDGE_ARCH_X = [
    KNOTT_PIER_X
    - BRIDGE_OUTER_PIER_SPAN
    - BRIDGE_CENTER_PIER_SPAN
    - BRIDGE_WEST_OUTER_PIER_SPAN,  # Pier 1
    KNOTT_PIER_X - BRIDGE_OUTER_PIER_SPAN - BRIDGE_CENTER_PIER_SPAN,  # Pier 2
    KNOTT_PIER_X - BRIDGE_OUTER_PIER_SPAN,  # Pier 3
    KNOTT_PIER_X - BRIDGE_OUTER_PIER_SPAN + BRIDGE_EAST_SPAN2_LEN,  # Pier 4
    2400 + KNOTT_DRIVEWAY_X_SHIFT,  # Pier 5
    3050 + KNOTT_DRIVEWAY_X_SHIFT,  # Pier 6
]
CHARLES_LAMP_POST_XS = [
    KNOTT_NE_PIER_X - CHARLES_LAMP_POST_EAST_SETBACK,
    KNOTT_PIER_X,
]
ENNIS_PILLAR_EAST_SHIFT = 100  # Shared eastward shift for the Ennis pillars and gate.
ENNIS_GATE_X1 = BRIDGE_ARCH_X[2] + ENNIS_PILLAR_HW + ENNIS_PILLAR_EAST_SHIFT + 20
# The short brick wall segment now extends past the old gate-aligned pillar
# position to meet the ornamental fence run's true east end (see
# _build_ennis_short_wall_section) — shift the pillars further east so they
# line up with that new wall end instead of the original gate position.
ENNIS_PILLAR_WALL_END_SHIFT = 66
ENNIS_PILLAR_X1 = (
    BRIDGE_ARCH_X[2]
    - ENNIS_PILLAR_HW
    + ENNIS_PILLAR_EAST_SHIFT
    + ENNIS_PILLAR_WALL_END_SHIFT
)
CHARLES_LAMP_POST_H = BRIDGE_DZ2 - BRIDGE_LAMP_POST_CLEARANCE
KNOTT_GROUND_Z = 221  # Terrain height anchor for the Knott side.
KNOTT_DRIVEWAY_ZT_S = KNOTT_GROUND_Z
KNOTT_Z2 = KNOTT_GROUND_Z + KNOTT_FLOORS * KNOTT_FLOOR_H
BRIDGE_X2 = BRIDGE_ARCH_X[3]  # Pier 4 / span-2 terminus.
ENNIS_Y = BRIDGE_Y2 + ENNIS_NORTH_OFFSET
CHARLES_LAMP_POST_YS = [ENNIS_Y - ENNIS_HW - CHARLES_LAMP_POST_SETBACK]
ENNIS_SW_EDGE = ENNIS_Y - ENNIS_HW - 3 * CHARLES_WALK_W - ROAD_VERGE_BUFFER
ENNIS_WALL_NY = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ENNIS_PILLAR_HW * 2
ENNIS_SHORT_WALL_GAP = 8  # gap north of the sidewalk squares
ENNIS_SHORT_WALL_NY = (
    ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W + ENNIS_SHORT_WALL_GAP
)  # Short north-side brick wall segment.
ENNIS_PILLAR_NORTH_Y = (
    ENNIS_Y
    + ENNIS_HW
    + ENNIS_WIDEN_N
    + 10
    + ENNIS_Y
    + ENNIS_HW
    + ENNIS_WIDEN_N
    + CHARLES_WALK_W
) // 2
# South pillar centered in the grass verge.
ENNIS_PILLAR_SOUTH_Y = (
    (ENNIS_Y - ENNIS_HW - ENNIS_CURB_W) + (ENNIS_SW_EDGE + CHARLES_WALK_W)
) // 2

KNOTT_DRIVEWAY_EXT_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_WALK_W
KNOTT_DRIVEWAY_JCY = ENNIS_Y - ENNIS_HW
PIER1_X, PIER2_X, PIER3_X, PIER4_X, PIER5_X, PIER6_X = BRIDGE_ARCH_X
# Center-span piers use terrain-height bases instead of FLOOR_Z2.
BRIDGE_PIER_GROUND_Z = {
    PIER2_X: 0,  # West-side center pier.
    PIER3_X: 20,  # Knott-side center pier.
}
DORM_PIER_X = min(BRIDGE_ARCH_X)
DORM_WALL_S_Y2 = -(BRIDGE_Y2 + BRIDGE_PILLAR_OVERHANG)
# Lane-centered outbound/return platform X positions (matches the east/west
# lane-line midpoints used elsewhere for Charles St. lane geometry).
_ROAD_CX = (ROAD_X1 + ROAD_X2) / 2
_WEST_LANE_LINE_X = (ROAD_X1 + _ROAD_CX - STREET_DIV_HW) / 2
_EAST_LANE_LINE_X = (_ROAD_CX + STREET_DIV_HW + ROAD_X2) / 2
# Ennis Rd begins at the east kerb line of Charles St: it tees into Charles
# rather than crossing it, so it has no carriageway west of here. Paving it
# from ROAD_X1 instead used to lay a second, 90-degree-rotated road surface
# over the whole Charles junction, coplanar with the Charles lanes already
# there, and the Ennis one won -- Charles appeared to change texture direction
# for the length of the junction.
ENNIS_X1 = ROAD_X2

KNOTT_ENT_WALK_X1 = KNOTT_ORIG_CX - KNOTT_ENT_HALF_W
# Knott second-floor walkway landing height.
WALL_T = 16
WORLD_X1 = -5135  # West world bound.
BRIDGE_X1 = -1967  # West bridge bound.
BRIDGE_SEG_W = (BRIDGE_X2 - BRIDGE_X1) / BRIDGE_SEG_SPAN_W
WORLD_X2 = 9100  # East world bound.
WORLD_X2_EXT = WORLD_X2 + WORLD_EAST_BUFFER  # East world wall position.
_EAST_FEATURES_X2 = 2976  # East anchor for Ennis and nearby features.
_EAST_FEATURES_X2_EXT = _EAST_FEATURES_X2 + WORLD_EAST_BUFFER
ENNIS_CEMENT_EAST_SHIFT = 160  # Eastward shift for the cement-wall pillar and lamp.
ENNIS_CEMENT_X2 = (
    _EAST_FEATURES_X2 - WALL_T - ARCH_SLAB_W // 2 + ENNIS_CEMENT_EAST_SHIFT
)  # Aligned with the east teleport center.
ENNIS_GATE_X2 = (ENNIS_GATE_X1 + _EAST_FEATURES_X2_EXT - WALL_T) // 2
ENNIS_CEMENT_X1 = ENNIS_GATE_X2
WORLD_Y1, WORLD_Y2 = (
    -6642,  # South world bound.
    4085,
)
CHARLES_Y1 = -2768  # South Charles St bound.
CHARLES_Y2 = 1696  # North Charles St bound.
DORM_NORTH_Y2 = 1846  # North dorm bound. Shifted +300 north of the bridge
# to leave room for another building in the gap between the bridge and the
# dorm pair.
DORM_NORTH_Y1 = DORM_NORTH_Y2 - DORM_DEPTH
DORM_SOUTH1_Y1 = -1968  # South dorm anchor.
SDORM1_EXTRA_DEPTH = 150  # Extra depth on the south1 footprint; south2
# shifts north by the same amount to stay flush against it.
DORM_SOUTH1_Y2 = DORM_SOUTH1_Y1 + DORM_DEPTH + SDORM1_EXTRA_DEPTH
DORM_SOUTH2_Y1 = DORM_SOUTH1_Y2
DORM_SOUTH2_Y2 = DORM_SOUTH2_Y1 + DORM_DEPTH
WORLD_Z2 = max(640, KNOTT_Z2 + 768)  # Bumped headroom (was +512, then +640)
# so players can stand/jump on top of KH without hitting the sky ceiling.

# Sub-basement shell.
BASEMENT_SLAB_T = 16  # Matches FLOOR_Z1..FLOOR_Z2 thickness.
BASEMENT_Z1 = -WORLD_Z2  # Basement floor top.
BASEMENT_FLOOR_Z1 = BASEMENT_Z1 - BASEMENT_SLAB_T  # Basement floor slab bottom.

# Round manhole opening through the world floor and basement ceiling. It sits
# out in the Charles/Ennis intersection, midway between Ennis Road's two curbs.
MANHOLE_X, MANHOLE_Y = 170, ENNIS_Y + ENNIS_WIDEN_N // 2
# 32x32 player hull needs at least 16*sqrt(2); 28 leaves margin.
MANHOLE_R = 28
BRIDGE_EAST_PIVOT_X = BRIDGE_ARCH_X[5]  # Pier 6 anchors the east-span bend.


# Function-derived constants.
def arch_z_at(x):
    """Z offset above flat datum for the deck profile at x.

    Piecewise, matching the real Loyola bridge (ref/bridge08): the centre span
    between PIER2_X and PIER3_X is a shallow parabolic arch cresting at
    BRIDGE_ARCH_RISE over the midpoint of those two piers; the two approach
    spans (PIER1_X..PIER2_X west, PIER3_X..PIER4_X east) descend as straight
    rakes from BRIDGE_ARCH_PIER_RISE at the centre piers down to 0 at the
    outer piers. Beyond PIER1_X/PIER4_X the deck is flat (approach to world
    wall / KH walkway).

    Uses the actual pier X-positions rather than a fixed radius around X=0,
    so the crest and rakes stay correctly anchored to PIER1_X..PIER4_X
    automatically whenever BRIDGE_CENTER_PIER_SPAN (or any other pier-spacing
    constant) changes — PIER3_X/PIER4_X are fixed while PIER1_X/PIER2_X shift
    west, so a fixed ±X radius around 0 would leave the crest off-centre and
    misalign the west rake with the actual west pier.
    """
    center_mid = (PIER2_X + PIER3_X) / 2.0
    center_half = (PIER3_X - PIER2_X) / 2.0  # half the actual centre-pier span
    dx = x - center_mid
    adx = abs(dx)
    if adx <= center_half:
        return (
            BRIDGE_ARCH_RISE
            - (BRIDGE_ARCH_RISE - BRIDGE_ARCH_PIER_RISE) * (adx / center_half) ** 2
        )
    if dx < 0:
        # West approach span: rakes down from PIER2_X to PIER1_X.
        if x <= PIER1_X:
            return 0.0
        return BRIDGE_ARCH_PIER_RISE * (x - PIER1_X) / float(PIER2_X - PIER1_X)
    # East approach span: rakes down from PIER3_X to PIER4_X.
    if x >= PIER4_X:
        return 0.0
    return BRIDGE_ARCH_PIER_RISE * (PIER4_X - x) / float(PIER4_X - PIER3_X)


def deck_bot_z(x):
    """Z coordinate of the deck underside at a given X position."""
    return BRIDGE_DZ1 + arch_z_at(x)


def deck_top_z(x):
    """Z coordinate of the deck surface (top face) at a given X position."""
    return BRIDGE_DZ2 + arch_z_at(x)


def ft_to_units(feet, inches=0):
    """Convert real-world feet (+ optional inches) to Quake units."""
    return round((feet + inches / 12) * SCALE)


BRIDGE_PAR_W = ft_to_units(2, 6)
KNOTT_ENT_WALK_ZT1 = int(
    deck_top_z(KNOTT_ORIG_CX)
)  # Bridge deck height at the Knott approach.
BRIDGE_PILLAR_HW = ft_to_units(2, 5.5) + 8  # Pier half-width.

BRIDGE_PILLAR_PYR_W = BRIDGE_PILLAR_HW  # Pyramid cap stays flush with the pillar post.


# Pier 6 is rotated, so its face X positions vary by Y.
_PIER6_ROT_RAD = math.radians(PIER6_ROTATION_DEG)
_PIER6_COS = math.cos(_PIER6_ROT_RAD)
_PIER6_TAN = math.tan(_PIER6_ROT_RAD)


def pier6_west_face_x_at_y(y):
    return PIER6_X - BRIDGE_PILLAR_HW / _PIER6_COS - _PIER6_TAN * y


def pier6_east_face_x_at_y(y):
    """Return the rotated east-face X position for a given Y."""
    return PIER6_X + BRIDGE_PILLAR_HW / _PIER6_COS - _PIER6_TAN * y


DORM_X2 = DORM_PIER_X + BRIDGE_PILLAR_HW + DORM_PIER_FACE_OFFSET
FENCE_X1 = DORM_X2 + DORM_FENCE_OFFSET
FENCE_X2 = FENCE_X1 + 2
DORM_X1 = DORM_X2 - 576
DORM_CX = (DORM_X1 + DORM_X2) // 2
ENNIS_GATE_PILLAR_W = ENNIS_GATE_PILLAR_OPENING_W + 2 * ENNIS_GATE_PILLAR_LEG_T

KNOTT = KnottSpec(
    floors=KNOTT_FLOORS,
    floor_h=KNOTT_FLOOR_H,
    wall_t=KNOTT_WALL_T,
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
# South-dorm terrace.
SDORM_LIFT = 128  # Terrace height.


DORM_FRONT_WALKWAY_X2 = FENCE_X1 - DORM_FRONT_WALKWAY_FENCE_OFFSET  # Outer edge.
DORM_FRONT_WALKWAY_X1 = DORM_FRONT_WALKWAY_X2 - DORM_FRONT_WALKWAY_W  # Inner edge.
DORM_FRONT_WALKWAY_SPUR_X1 = DORM_PIER_X + DORM_BRICK_WALL_HW  # Spur west edge.
DORM_FRONT_WALKWAY_SPUR_Y2 = (
    DORM_SOUTH2_Y2 + DORM_DOOR_OFF + DORM_DOOR_W // 2 + BRIDGE_CENTER_SPAN_OFFSET[1]
)  # Spur north edge; matches the door's center-span shift only when that span is built.

_fog = (
    make_fog(FOG_DENSITY, *[float(x) for x in LIGHTING.fog.split()[1:]])
    if FOG_DENSITY is not None
    else LIGHTING.fog
)


WORLDSPAWN_FIELDS = {
    "wad": ";".join(_WAD_FILES),
    "message": "Loyola University Maryland - Charles Street Pedestrian Bridge",
    "dmflags": "128",
    # Engines (vkQuake, QuakeSpasm, Ironwail) read the worldspawn "sky" key as
    # the name of a six-image skybox under gfx/env -- *not* as a texture name.
    # qbsp ignores the key entirely; it decides which faces are sky purely
    # from the sky* texture prefix, so Textures.SKY does that job on its own.
    # The key is therefore omitted when no skybox is configured: pointing it
    # at a texture name only makes the engine hunt for a gfx/env file that
    # cannot exist and silently fall back. Note the value keeps the skybox's
    # trailing separator, because the engine's path format is "gfx/env/%s%s"
    # with a bare "rt"/"bk"/... suffix -- there is no separator in it.
    **({"sky": SKYBOX_WORLDSPAWN} if SKYBOX_WORLDSPAWN else {}),
    **{**LIGHTING.to_worldspawn(), "_fog": _fog},
}
