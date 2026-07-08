"""
west_campus_terrain — real-elevation ground fill for the west campus dorm
buildings (west_campus.py), the bridge's west approach, and the full span
west of Charles St, from the road's actual west sidewalk/curb out to the
world's west wall and along Charles St's *full* modeled length (the true
world Y range, not just the documented "CHARLES_Y1/CHARLES_Y2" survey
corridor — see the _wct_y note below for why those two differ).

USGS EPQS elevation samples (docs/elevation_samples.csv, the wcampus_audit_*
/ wcampus_ext_* / wcampus_far_* rows) show the ground climbing gently west
from Charles St up to the dorm buildings' footprint (~60-155 z-units) and
staying broadly hill-like (~50-245 z-units, no clean taper back to 0) out to
the world's west wall — much gentler overall than Knott Hall's hill (125-330
z-units) near Charles St, but rising further south, and dipping below grade
in a few spots north of the dorm buildings (clamped to 0 — see below).

Built as a single 12-column x 13-row real-data grid, using the same
overlap-safe multi-column tri_ramp_prism technique proven in
knott_terrain.py's south-extension / west-ramp sections (see _WCT_OVR
below).

Kept independent of WEST_CAMPUS_ENABLED (own WEST_CAMPUS_TERRAIN_ENABLED
flag) so the terrain can be reviewed/compiled on its own even while the
dorm buildings themselves stay disabled — same reasoning as
KNOTT_TERRAIN_ENABLED vs KNOTT_HALL_ENABLED.
"""

from .constants import (
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    FLOOR_Z1,
    FLOOR_Z2,
    ROAD_X1,
    WALL_T,
    WEST_CAMPUS_TERRAIN_ENABLED,
    WORLD_X1,
    WORLD_Y1,
    WORLD_Y2,
    Textures,
)
from .geometry import tri_ramp_prism


def _clamp0(zs):
    """Real elevation dips below the FLOOR_Z2 baseline in a few spots (north
    of the dorm buildings, and right next to Charles St) — using those
    negative values directly would both duplicate ground already covered by
    the flat road/floor and, worse, could push a brush's top below its
    FLOOR_Z1 bottom cap (a degenerate/inverted brush). Clamp to flat grade
    instead, matching the "already engineered/flat, no contrary evidence"
    convention used for other paved surfaces throughout this project."""
    return [max(0, z) for z in zs]


def build():
    if not WEST_CAMPUS_TERRAIN_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # X grid: world west wall -> bridge west approach -> dorm buildings ->
    # Charles St west sidewalk edge. West-to-east ascending order. The last
    # column ties to the sidewalk's own west edge (ROAD_X1 - CHARLES_WALK_W)
    # rather than ROAD_X1 itself — streets.py's west sidewalk/curb/raised-
    # ground brushes already occupy X in [ROAD_X1-CHARLES_WALK_W, ROAD_X1]
    # for the *entire* world Y range; tying real terrain all the way to
    # ROAD_X1 overlapped and effectively overrode that curb geometry.
    _wct_sidewalk_x = ROAD_X1 - CHARLES_WALK_W
    _wct_x = [
        WORLD_X1 + WALL_T,
        -4500,
        -3500,
        -2500,
        -1967,  # BRIDGE_X1 — bridge west abutment
        -1753,  # DORM_X1
        -1465,  # DORM_CX
        -1177,  # DORM_X2
        -961,  # FENCE_X1
        -700,
        -400,
        _wct_sidewalk_x,
    ]
    # Y grid: full world Y range, north to south. streets.py's Charles St
    # sidewalk/curb geometry runs the *actual* world Y extent
    # (WORLD_Y1+WALL_T .. WORLD_Y2-WALL_T) — noticeably further both north
    # and south than the constants.py CHARLES_Y1/CHARLES_Y2 anchors, which
    # only mark the documented real-elevation *survey* corridor's ends, not
    # the modeled road's actual extent. Stopping this grid at those anchors
    # left real cliffs at both seams; these rows extend it to the true
    # world edges.
    _wct_y = [
        WORLD_Y2 - WALL_T,
        2800,
        1696,
        1546,
        1096,
        500,
        0,
        -1068,
        -1968,
        -2768,
        -3800,
        -5200,
        WORLD_Y1 + WALL_T,
    ]
    # Real USGS z-units-above-baseline samples (docs/elevation_samples.csv,
    # wcampus_audit_x{X}_y{Y} / wcampus_ext_x{X}_y{Y} / wcampus_far_x{X}_y{Y}
    # rows), one column per _wct_x entry (except the last, flat sidewalk-tie
    # column), values in the same order as _wct_y. The baseline (0) already
    # corresponds to FLOOR_Z2 (bridge-crossing grade), so no extra
    # curb-style offset is needed for these, unlike the last column.
    _wct_cols = [
        _clamp0([-79, 9, 83, 90, 129, 134, 172, 163, 92, 51, -74, 124, 167]),
        _clamp0([-66, -6, 74, 83, 106, 132, 145, 133, 89, 52, -42, 182, 215]),
        _clamp0([-36, 10, 123, 115, 98, 111, 122, 104, 100, 67, 2, 226, 245]),
        _clamp0([-119, 85, 124, 125, 142, 143, 145, 143, 165, 149, 40, 232, 223]),
        _clamp0([-78, 13, 142, 147, 155, 141, 146, 150, 142, 147, 58, 233, 221]),
        _clamp0([-78, -8, 143, 146, 151, 129, 135, 152, 149, 144, 64, 233, 216]),
        _clamp0([-103, -19, 101, 102, 107, 114, 110, 124, 141, 134, 74, 227, 209]),
        _clamp0([-117, -23, 88, 92, 101, 106, 105, 108, 109, 122, 86, 206, 198]),
        _clamp0([-116, -36, 62, 74, 88, 101, 104, 139, 113, 108, 93, 161, 186]),
        _clamp0([-137, -82, -28, -16, 12, 50, 67, 104, 105, 100, 105, 136, 154]),
        _clamp0([-131, -89, -52, -48, -33, -13, 5, 38, 68, 90, 115, 114, 114]),
        # Sidewalk-tie column: flat at the curb/raised-ground height
        # streets.py already builds along this whole edge, for every Y row.
        [CHARLES_WALK_H] * len(_wct_y),
    ]

    # A chain of 3+ Y-segments sharing an exact coincident boundary plane
    # (this grid has 12) trips a qbsp portal-building bug that produces a
    # real leak — see the matching _WRAMP_OVR note in knott_terrain.py for
    # the bisection that found this. Overlap each non-final segment's south
    # edge by a hair, linearly extrapolating that column's own slope.
    _WCT_OVR = 4

    for (wx1, wcol1), (wx2, wcol2) in zip(
        zip(_wct_x, _wct_cols), zip(_wct_x[1:], _wct_cols[1:])
    ):
        for i in range(len(_wct_y) - 1):
            y1, y2 = _wct_y[i], _wct_y[i + 1]
            z1a, z1b = wcol1[i], wcol1[i + 1]
            z2a, z2b = wcol2[i], wcol2[i + 1]
            if i < len(_wct_y) - 2:
                y2_ext = y2 - _WCT_OVR
                z1b = z1a + (z1b - z1a) * (y2_ext - y1) / (y2 - y1)
                z2b = z2a + (z2b - z2a) * (y2_ext - y1) / (y2 - y1)
                y2 = y2_ext
            # y2 < y1 (southward) — swap B/C corners (and their z values)
            # from the "northward" convention to keep tri_ramp_prism's
            # required CCW winding, same as knott_terrain.py's south loops.
            BRUSHES.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx2,
                    y2,
                    wx2,
                    y1,
                    FLOOR_Z1,
                    FLOOR_Z2 + z1a,
                    FLOOR_Z2 + z2b,
                    FLOOR_Z2 + z2a,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx1,
                    y2,
                    wx2,
                    y2,
                    FLOOR_Z1,
                    FLOOR_Z2 + z1a,
                    FLOOR_Z2 + z1b,
                    FLOOR_Z2 + z2b,
                    Textures.GROUND,
                )
            )

    return BRUSHES, ENTITIES
