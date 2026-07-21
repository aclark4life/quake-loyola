"""
ne_terrain — real-elevation ground fill for the NE quadrant: north of Ennis
Road, east of Charles St. This is the last remaining unmodeled quadrant of
the map — streets.py previously filled this whole rectangle with a single
flat placeholder box (flush with the Charles St sidewalk height), the same
"placeholder until the real terrain module exists" pattern west_campus.py's
verge used before west_campus_terrain.py replaced it (see that module for
the precedent this one follows).

USGS EPQS elevation samples (docs/elevation_samples.csv, the ne_quad_*
rows) show real ground here climbing well above grade close to Charles
St/Ennis Road (150-240 z-units), rising further into a local hill around
X=5000 (up to 414 z-units), then easing off toward the world's NE corner —
and dipping below grade in the northernmost rows (clamped to 0 — see
_clamp0 below), similar to west_campus_terrain.py's north rows. The raw
deltas between adjacent grid points produced near-vertical cliffs in-game,
so _clamp0 applies _NE_HEIGHT_SCALE (0.5) to gentle the relief — actual
in-map heights are half the raw USGS figures quoted above.

Two edges of this quadrant border existing flush (CHARLES_WALK_H) built
infrastructure and need a flat tie, same technique used for
west_campus_terrain.py's Charles St sidewalk tie:
  - West edge (X = ROAD_X2 + CHARLES_WALK_W): the Charles St east sidewalk's
    north segment runs this whole Y range at CHARLES_WALK_H — real terrain
    ties flush there instead of using real data, to avoid overlapping the
    sidewalk.
  - South edge (Y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W):
    Ennis Road's north curb (streets.py) runs the full X range of this
    quadrant at the same CHARLES_WALK_H — real terrain ties flush there
    too, for the same reason.
Real elevation data starts one grid step in from each of those two edges,
same "flat tie column/row, real data begins next column/row over" approach
as west_campus_terrain.py used at its Charles St edge.

Built as a single 9-column x 7-row real-data grid, using the same
overlap-safe multi-column tri_ramp_prism technique proven in
knott_terrain.py's south-extension / west-ramp sections and
west_campus_terrain.py (see _NE_OVR below).

Kept independent as its own NE_ENABLED_TERRAIN flag so this terrain can be
reviewed/compiled on its own — mirrors WEST_CAMPUS_ENABLED_TERRAIN.
"""

from .constants import (
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_HW,
    ENNIS_WIDEN_N,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    NE_ENABLED_TERRAIN,
    ROAD_X2,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y2,
    Textures,
)
from .geometry import tri_ramp_prism

# Real USGS relief here produced near-vertical drops between adjacent grid
# points (visible in-game as cliffs). Scale the real-elevation deltas down
# to a gentler hill while keeping the flat sidewalk/curb tie (CHARLES_WALK_H)
# untouched — the tie values never pass through _clamp0.
_NE_HEIGHT_SCALE = 0.5

# The row closest to Ennis Road (_ne_y[1], right after the flat curb tie)
# still rose steeply over a short Y run, reading as a small cliff right at
# the road edge. Ease the climb in over the first few rows — index 0 here
# is _ne_y[1] (nearest Ennis), ramping up to full scale by index 3.
_NE_ROW_TAPER = [0.25, 0.45, 0.7, 1.0, 1.0, 1.0]


def _clamp0(zs):
    """Real elevation dips below the FLOOR_Z2 baseline in the northernmost
    rows — using those negative values directly would push a brush's top
    below its FLOOR_Z1 bottom cap (a degenerate/inverted brush). Clamp to
    flat grade instead, matching west_campus_terrain.py's convention."""
    return [
        max(0, z * _NE_HEIGHT_SCALE * taper)
        for z, taper in zip(zs, _NE_ROW_TAPER, strict=False)
    ]


def build():
    if not NE_ENABLED_TERRAIN:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # X grid: Charles St east sidewalk edge -> world east wall. The first
    # column ties flush to the sidewalk (see module docstring); real data
    # begins at the second column.
    _ne_x = [
        ROAD_X2 + CHARLES_WALK_W,
        900,
        1700,
        KNOTT_DRIVEWAY_CORRIDOR_X1,  # 2486
        KNOTT_DRIVEWAY_CORRIDOR_X2,  # 2902
        3472,  # _EAST_FEATURES_X2_EXT - WALL_T (old ENNIS_X2 anchor / gate area)
        5000,
        7300,
        WORLD_X2_EXT - WALL_T,
    ]
    # Y grid: Ennis Road's north curb -> world north wall. The first row
    # ties flush to the curb (see module docstring); real data begins at
    # the second row.
    _ne_y = [
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
        1546,
        1696,
        2200,
        2800,
        3450,
        WORLD_Y2 - WALL_T,
    ]
    # Real USGS z-units-above-baseline samples (docs/elevation_samples.csv,
    # ne_quad_x{X}_y{Y} rows), one column per _ne_x entry after the tie
    # column, values in the same order as _ne_y after the tie row (row 0
    # forced flush to the sidewalk/curb height instead of its real value —
    # same convention as the tie column).
    _ne_cols = [
        # Sidewalk-tie column: flat at the curb/sidewalk height streets.py
        # already builds along this whole edge, for every Y row.
        [CHARLES_WALK_H] * len(_ne_y),
        [CHARLES_WALK_H] + _clamp0([123, 108, 55, -17, -80, -90]),
        [CHARLES_WALK_H] + _clamp0([173, 149, 105, 36, -20, -51]),
        [CHARLES_WALK_H] + _clamp0([210, 177, 127, 47, -8, -56]),
        [CHARLES_WALK_H] + _clamp0([209, 201, 119, 37, -15, -53]),
        [CHARLES_WALK_H] + _clamp0([200, 199, 189, 74, -9, -33]),
        [CHARLES_WALK_H] + _clamp0([369, 219, 192, 148, 19, -16]),
        [CHARLES_WALK_H] + _clamp0([310, 287, 233, 201, 142, 39]),
        [CHARLES_WALK_H] + _clamp0([370, 356, 311, 221, 198, 110]),
    ]

    # A chain of 3+ Y-segments sharing an exact coincident boundary plane
    # trips a qbsp portal-building bug that produces a real leak — see the
    # matching _WRAMP_OVR/_WCT_OVR notes in knott_terrain.py /
    # west_campus_terrain.py for the bisection that found this. Overlap
    # each non-final segment's north edge by a hair, linearly extrapolating
    # that column's own slope.
    _NE_OVR = 8

    for (wx1, wcol1), (wx2, wcol2) in zip(
        zip(_ne_x, _ne_cols, strict=False),
        zip(_ne_x[1:], _ne_cols[1:], strict=False),
        strict=False,
    ):
        for i in range(len(_ne_y) - 1):
            y1, y2 = _ne_y[i], _ne_y[i + 1]
            z1a, z1b = wcol1[i], wcol1[i + 1]
            z2a, z2b = wcol2[i], wcol2[i + 1]
            if i < len(_ne_y) - 2:
                # Grid ascends northward (y2 > y1), so the overlap extends
                # the segment's north edge further north (unlike
                # west_campus_terrain.py's descending grid, which extends
                # south) — same OVR technique, opposite sign.
                y2_ext = y2 + _NE_OVR
                z1b = z1a + (z1b - z1a) * (y2_ext - y1) / (y2 - y1)
                z2b = z2a + (z2b - z2a) * (y2_ext - y1) / (y2 - y1)
                y2 = y2_ext
            # y2 > y1 (northward), wx2 > wx1 (eastward) — split the quad
            # SW/SE/NE/NW into 2 CCW triangles: (SW,SE,NE) and (SW,NE,NW).
            BRUSHES.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx2,
                    y1,
                    wx2,
                    y2,
                    FLOOR_Z1,
                    FLOOR_Z2 + z1a,
                    FLOOR_Z2 + z2a,
                    FLOOR_Z2 + z2b,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx2,
                    y2,
                    wx1,
                    y2,
                    FLOOR_Z1,
                    FLOOR_Z2 + z1a,
                    FLOOR_Z2 + z2b,
                    FLOOR_Z2 + z1b,
                    Textures.GROUND,
                )
            )

    return BRUSHES, ENTITIES
