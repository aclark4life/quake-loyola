"""Constants and worldspawn fields derived from other area modules."""

import math

from .bridge import (
    BRIDGE_ARCH_PIER_RISE,
    BRIDGE_ARCH_RISE,
    BRIDGE_BLK_HW,
    BRIDGE_CENTER_PIER_SPAN,
    BRIDGE_DZ1,
    BRIDGE_DZ2,
    BRIDGE_EAST_SPAN_ANGLE,
    BRIDGE_OUTER_PIER_SPAN,
    BRIDGE_PAR_H,
    BRIDGE_PILLAR_OVERHANG,
    BRIDGE_SEG_SPAN_W,
    BRIDGE_WALK_WALL,
    BRIDGE_Y1,
    BRIDGE_Y2,
    BridgeSpec,
)
from .dorm import (
    DORM_BRICK_WALL_HALF_W,
    DORM_DEPTH,
    DORM_DOOR_OFF,
    DORM_DOOR_W,
    DORM_FENCE_OFFSET,
    DORM_FLOORS,
    DORM_FRONT_WALKWAY_FENCE_OFFSET,
    DORM_FRONT_WALKWAY_W,
    DORM_WALL,
    DormSpec,
)
from .ennis import (
    ENNIS_CURB_W,
    ENNIS_GATE_PILLAR_LEG_T,
    ENNIS_GATE_PILLAR_OPENING_W,
    ENNIS_HW,
    ENNIS_PILLAR_HW,
    ENNIS_WALL_T,
)
from .knott import (
    KNOTT_BUILDING_W,
    KNOTT_DRIVEWAY_HW,
    KNOTT_FLOOR_H,
    KNOTT_FLOORS,
    KNOTT_WALL,
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
    CHARLES_PLT_W,
    CHARLES_WALK_W,
    ROAD_X1,
    ROAD_X2,
)
from .textures import Textures
from .world import ARCH_SLAB_W, FLOOR_Z2, INDENT, SCALE, WORLD_EAST_BUFFER

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
CHARLES_LAMP_POST_SETBACK = 104  # was 160 — the Ennis-area lamp post sits at
# this offset south of the Ennis curb, which streets.py also uses as the south
# edge of the grass verge (see ROAD_VERGE_BUFFER below); shrunk in lockstep
# with the second verge reduction so the lamp still lands right at the
# verge/sidewalk boundary instead of inside the sidewalk.
CHARLES_PLATFORM_ROAD_OFFSET = 16
ROAD_VERGE_BUFFER = -56  # extra padding for the Ennis south grass verge
# (streets.py); was 32, then 0 (first shrink — the widest safe value with a
# 160-unit CHARLES_LAMP_POST_SETBACK), now negative for a second shrink per
# feedback that it was still a bit wide. CHARLES_LAMP_POST_SETBACK was moved
# down to 104 in lockstep so the lamp still sits at the new (narrower) verge's
# south edge rather than inside the sidewalk (south edge = ENNIS curb −
# 2*CHARLES_WALK_W − this buffer = ENNIS curb − 96, matching the new setback).
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
ENNIS_PILLAR_EAST_SHIFT = 40  # nudges the Ennis entrance pillars east, staying
# clear of the gate (80-unit gap to ENNIS_GATE_X1)
ENNIS_PILLAR_X1 = BRIDGE_ARCH_X[2] - ENNIS_PILLAR_HW + ENNIS_PILLAR_EAST_SHIFT
ENNIS_PILLAR_X2 = BRIDGE_ARCH_X[2] + ENNIS_PILLAR_HW + ENNIS_PILLAR_EAST_SHIFT
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
ENNIS_SHORT_WALL_GAP = 8  # gap north of the sidewalk squares
ENNIS_SHORT_WALL_NY = (
    ENNIS_Y + ENNIS_HW + CHARLES_WALK_W + ENNIS_SHORT_WALL_GAP
)  # short brick wall segment near the north pillar, moved north clear of the
# sidewalk squares (which run up to ENNIS_Y + ENNIS_HW + CHARLES_WALK_W)
# North sidewalk squares span ENNIS_Y + ENNIS_HW + 10 (curb cap + gap) to
# ENNIS_Y + ENNIS_HW + CHARLES_WALK_W, per the sw_slabs_x() call in
# streets.py; the pillar sits at the midpoint of that band.
ENNIS_PILLAR_NORTH_Y = (
    ENNIS_Y + ENNIS_HW + 10 + ENNIS_Y + ENNIS_HW + CHARLES_WALK_W
) // 2
# South pillar — centred in the south grass verge (between the Ennis curb and
# the south sidewalk), rather than flush against the curb, so it reads as a
# planted gate pillar instead of a curbside post.
ENNIS_PILLAR_SOUTH_Y = (
    (ENNIS_Y - ENNIS_HW - ENNIS_CURB_W) + (ENNIS_SW_EDGE + CHARLES_WALK_W)
) // 2

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
    # PIER2 (now -425, tightened toward the curb from -525 — see
    # BRIDGE_CENTER_PIER_SPAN): west terrain min under the new footprint ≈17 —
    # use FLOOR_Z2 (0), still safely below.
    # PIER3 (+525): KH hill profile min under full footprint ≈30 (re-sampled;
    # the old "~57" figure predates later hill-profile edits and left this
    # pier's base — previously 48 — floating above ground near its west/edge
    # corners). Use 20 for a safe margin below the resampled minimum.
    PIER2_X: 0,  # west campus terrain min under bridge span ≈17 (was ≈15 at -525) -
    # use 0 (FLOOR_Z2)
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
    # bumped from 7708 to make room for Maryland Hall (MARYLAND_X2 = 4315 after
    # the /2.5 east-campus compression, see constants/maryland.py — NOT the
    # 8979 pre-compression OSM figure), leaving a ~4785-unit (~317ft)
    # clearance margin before the sealing wall.
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

# ── Sub-basement level (basement.py) ────────────────────────────────────────
# Doubles total world height by extending a walled void below the existing
# ground-floor slab (FLOOR_Z1..FLOOR_Z2). BASEMENT_Z1 is the negative mirror
# of WORLD_Z2, so the full vertical span runs BASEMENT_Z1..WORLD_Z2 and the
# ground plane (Z=0) sits exactly halfway between the new basement floor and
# the existing ceiling. No access point (teleporter/hatch) exists yet — this
# is just the sealed shell, to be connected once the basement has content.
BASEMENT_ENABLED = True
BASEMENT_SLAB_T = 16  # basement floor slab thickness, matches FLOOR_Z1..FLOOR_Z2
BASEMENT_Z1 = -WORLD_Z2  # basement floor top (walkable surface)
BASEMENT_FLOOR_Z1 = BASEMENT_Z1 - BASEMENT_SLAB_T  # basement floor slab bottom

# Manhole opening — a true round hole (n-gon approximation of a circle; see
# box_with_round_hole/radial_fan_fills in geometry.py) punched straight down
# through both the world floor slab (FLOOR_Z1..FLOOR_Z2, streets.py) and the
# basement ceiling slab (FLOOR_Z1-WALL_T..FLOOR_Z1, basement.py) at this X/Y,
# connecting ground level directly to the basement void below. Just the
# opening for now — no cover, ladder, or tube.
MANHOLE_X, MANHOLE_Y = 170, 986
# Player hull is a 32x32 (half-extent 16) axis-aligned box; the tightest a
# circular hole can be and still pass it every orientation is the box's
# half-diagonal, 16*sqrt(2) =~ 22.6. 28 gives a small (~5 unit) safety
# margin above that so the player doesn't snag on the hole's n-gon edges.
MANHOLE_R = 28
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
# Ennis east / KH driveway south teleports both land on the KH rooftop but are
# spread apart along Y (perpendicular to the shared west-facing direction) so
# the two destinations don't stack exactly on top of one another.
KH_ROOFTOP_ORIGIN_ENNIS_EAST = "2149 -216 904"
KH_ROOFTOP_ORIGIN_KH_DRIVE_SOUTH = "2149 -312 904"

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


WORLDSPAWN_FIELDS = {
    "wad": "quake101.wad;ad.wad;makkon_building.wad;ikwhite.wad;makkon_stone.wad",
    "message": "Loyola University Maryland - Charles Street Pedestrian Bridge",
    "sky": Textures.SKY,
    "dmflags": "128",
    **{**LIGHTING.to_worldspawn(), "_fog": _fog},
}
