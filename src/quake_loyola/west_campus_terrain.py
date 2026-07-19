"""
west_campus_terrain — real-elevation ground fill for the west campus dorm
buildings (west_campus.py), the bridge's west approach, and the full span
west of Charles St, from the road's actual west sidewalk/curb out to the
world's west wall and along Charles St's *full* modeled length (the true
world Y range, not just the documented "CHARLES_Y1/CHARLES_Y2" survey
corridor — see the wct_y note below for why those two differ).

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

Kept independent of WEST_CAMPUS_ENABLED_DORMS (own WEST_CAMPUS_ENABLED_TERRAIN
flag) so the terrain can be reviewed/compiled on its own even while the
dorm buildings themselves stay disabled — same reasoning as
KNOTT_ENABLED_TERRAIN vs KNOTT_ENABLED.
"""

from .constants import (
    BRIDGE_X1,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    DORM_X1,
    DORM_X2,
    FENCE_X1,
    FLOOR_Z1,
    FLOOR_Z2,
    ROAD_X1,
    WALL_T,
    WEST_CAMPUS_ENABLED,
    WEST_CAMPUS_ENABLED_TERRAIN,
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


# X grid: world west wall -> bridge west approach -> dorm buildings ->
# Charles St west sidewalk edge. West-to-east ascending order. The last
# column ties to the sidewalk's own west edge (ROAD_X1 - CHARLES_WALK_W)
# rather than ROAD_X1 itself — streets.py's west sidewalk/curb/raised-
# ground brushes already occupy X in [ROAD_X1-CHARLES_WALK_W, ROAD_X1]
# for the *entire* world Y range; tying real terrain all the way to
# ROAD_X1 overlapped and effectively overrode that curb geometry.
#
# The DORM_X1/DORM_CX/DORM_X2/FENCE_X1 columns used to be hardcoded literal
# copies of those constants' original values. Once Charles St/the bridge's
# centre span started being widened west (moving DORM_PIER_X, and
# everything derived from it including these, further west each time), the
# stale literals no longer matched the live building positions and drifted
# past the (also-shifting) sidewalk-tie column, breaking this grid's
# required strict west-to-east ordering — producing degenerate/inverted
# terrain brushes right at the west sidewalk seam. Reference the live
# constants directly instead, so this grid re-derives automatically
# whenever the dorm/fence positions move (e.g. from further Charles St
# widening) with no manual re-tuning needed.
_wct_dorm_cx = (DORM_X1 + DORM_X2) // 2
_wct_sidewalk_x = ROAD_X1 - CHARLES_WALK_W
# wcampus_ext_x-700_*: a real USGS-sampled elevation column at a fixed
# real-world GPS location (docs/elevation_samples.csv), staying high
# (~150 z-units) right up to that X. As Charles St/the bridge's centre
# span kept widening west (moving ROAD_X1, and therefore
# _wct_sidewalk_x, further west each time), the gap between this real
# x=-700 sample and the sidewalk shrank from several hundred units down
# to under 20 — squeezing the whole ~150-unit real->flat drop into a
# near-vertical cliff right next to the sidewalk (reported as an
# unnatural steep drop-off) no matter how many extra steps subdivide
# that now-tiny gap; spreading a fixed drop over ~14 units can never
# look gradual. The taper below now starts from the FENCE_X1 real
# column instead (~700 units of room, vs. the ~14 left after x=-700) and
# spans the *entire* FENCE_X1 -> sidewalk distance, so the same drop
# happens over a genuinely walkable slope. This supersedes the
# intervening real x=-700 sample's own literal column with the smooth
# taper curve's value at that X — the same "deliberate deviation from
# as-surveyed data for gameplay" tradeoff already used for ROAD_X1/
# BRIDGE_CENTER_PIER_SPAN above.
_WCT_TAPER_FRACS = (0.2, 0.4, 0.6, 0.8)
assert FENCE_X1 < _wct_sidewalk_x, (
    "west_campus_terrain X grid must stay in strict west-to-east order; "
    "FENCE_X1 has drifted past the sidewalk tie — re-derive the terrain "
    "grid before widening further."
)


def _wct_taper_x(frac):
    return round(FENCE_X1 + (_wct_sidewalk_x - FENCE_X1) * frac)


# Raw (X, real-elevation-column) pairs for the surveyed portion of the grid
# (world wall through the real FENCE_X1 sample — the x=-700 sample used to
# anchor this list too, but is now superseded by the taper below, see the
# _wct_sidewalk_x comment above). DORM_X1/_wct_dorm_cx/DORM_X2/FENCE_X1
# track the *live* building/fence positions rather than the original
# literal survey X's (-1753/-1465/-1177/-961) they replaced, so the
# terrain stays aligned with the buildings even as Charles St/the bridge's
# centre span keep widening west — at the cost of these particular columns'
# real elevation data no longer being tied to their exact original GPS X
# (same "deliberate deviation for gameplay" tradeoff as ROAD_X1/
# BRIDGE_CENTER_PIER_SPAN — see docs/reference.rst "Charles St width
# validation"). WORLD_X1/-4500/-3500/-2500/BRIDGE_X1 stay literal: they're
# real, fixed-GPS audit-grid samples that don't track any building.
#
# Sorted by X (rather than assumed pre-ordered) so this grid self-corrects
# if further widening ever pushes a building column past a fixed real-sample
# column (e.g. DORM_X1 now sits west of BRIDGE_X1) — each column keeps its
# own real elevation data; only the column *order* is re-derived.
_wct_raw = list(
    zip(
        [WORLD_X1 + WALL_T, -4500, -3500, -2500, BRIDGE_X1],
        [
            [-79, 9, 83, 90, 129, 134, 172, 163, 92, 51, -74, 124, 167],
            [-66, -6, 74, 83, 106, 132, 145, 133, 89, 52, -42, 182, 215],
            [-36, 10, 123, 115, 98, 111, 122, 104, 100, 67, 2, 226, 245],
            [-119, 85, 124, 125, 142, 143, 145, 143, 165, 149, 40, 232, 223],
            [-78, 13, 142, 147, 155, 141, 146, 150, 142, 147, 58, 233, 221],
        ],
    )
) + list(
    zip(
        [DORM_X1, _wct_dorm_cx, DORM_X2, FENCE_X1],
        [
            [-78, -8, 143, 146, 151, 129, 135, 152, 149, 144, 64, 233, 216],
            [-103, -19, 101, 102, 107, 114, 110, 124, 141, 134, 74, 227, 209],
            [-117, -23, 88, 92, 101, 106, 105, 108, 109, 122, 86, 206, 198],
            # FENCE_X1 column: the real y=-1068 (index 7) sample is a 139
            # spike — inconsistent with its neighbors (104 at y=0, 113 at
            # y=-1968, and the DORM_X2 column's own y=-1068 sample of 108)
            # and well above the flat FLOOR_Z2 + SDORM_LIFT (128)
            # walkway/spur that build_sidewalk() inlays right next to this
            # column, poking up through/burying the walkway. Trimmed to
            # 108 (matching DORM_X2's same row) to smooth the local spike
            # and clear the walkway.
            [-116, -36, 62, 74, 88, 101, 104, 108, 113, 108, 93, 161, 186],
        ],
    )
)
_wct_raw.sort(key=lambda pair: pair[0])
_wct_raw_x = [x for x, _ in _wct_raw]
assert len(_wct_raw_x) == len(set(_wct_raw_x)) and _wct_raw_x == sorted(_wct_raw_x), (
    "west_campus_terrain surveyed X columns collided or failed to sort "
    "strictly ascending — two grid columns landed on the same X (or the "
    "sort itself is broken); re-derive the terrain grid before widening "
    "further."
)
_wct_x = _wct_raw_x + [_wct_taper_x(f) for f in _WCT_TAPER_FRACS] + [_wct_sidewalk_x]

# Y grid: full world Y range, north to south. streets.py's Charles St
# sidewalk/curb geometry runs the *actual* world Y extent
# (WORLD_Y1+WALL_T .. WORLD_Y2-WALL_T) — noticeably further both north
# and south than the constants.py CHARLES_Y1/CHARLES_Y2 anchors, which
# only mark the documented real-elevation *survey* corridor's ends, not
# the modeled road's actual extent. Stopping this grid at those anchors
# left real cliffs at both seams; these rows extend it to the true
# world edges.
wct_y = [
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
# rows), one column per surveyed _wct_x entry, in the same order as wct_y
# (paired with X above via _wct_raw, then clamped and re-ordered to match
# the sorted _wct_x). The baseline (0) already corresponds to FLOOR_Z2
# (bridge-crossing grade), so no extra curb-style offset is needed for
# these, unlike the flat taper/sidewalk-tie columns below.
_wct_cols = [_clamp0(col) for _, col in _wct_raw]
# The real FENCE_X1 column rises to ~90-186, but the sidewalk-tie column
# (below) is forced flat at the curb height for the *entire* Y range
# (streets.py already owns that ground). See the _wct_sidewalk_x comment
# above for why this taper now starts from FENCE_X1 (~700 units of room)
# rather than the x=-700 sample it used to start from (only ~14 units of
# room left after Charles St's widening, which produced a near-vertical
# cliff right next to the sidewalk no matter how that tiny gap was
# subdivided). Taper across _WCT_TAPER_FRACS steps instead, each moving
# partway from the real FENCE_X1 column toward the flat curb height, so
# the same total drop is spread over the full FENCE_X1 -> sidewalk span.
_wct_fence_col = _wct_cols[-1]
_wct_flat_walk = [CHARLES_WALK_H] * len(wct_y)


def _wct_taper(frac):
    return [round(r + (CHARLES_WALK_H - r) * frac) for r in _wct_fence_col]


_wct_cols += [_wct_taper(f) for f in _WCT_TAPER_FRACS] + [
    # Sidewalk-tie column: flat at the curb/raised-ground height
    # streets.py already builds along this whole edge, for every Y row.
    _wct_flat_walk
]


def terrain_z(x, y):
    """Real-elevation ground height (world Z, i.e. FLOOR_Z2 + sample) at an
    arbitrary (x, y) point, bilinearly interpolated across the _wct_x/wct_y
    grid this module builds its terrain from. Lets other modules (e.g. the
    west_campus.py iron fence, which used to assume a flat FLOOR_Z2 grade
    north of the bridge) stay flush with the real hillside instead of
    getting buried under it or floating above it. x/y are clamped to the
    grid's own bounds rather than extrapolated."""
    x = min(max(x, _wct_x[0]), _wct_x[-1])
    y = max(min(y, wct_y[0]), wct_y[-1])
    xi = 0
    while xi < len(_wct_x) - 2 and _wct_x[xi + 1] < x:
        xi += 1
    yi = 0
    while yi < len(wct_y) - 2 and wct_y[yi + 1] > y:
        yi += 1
    x1, x2 = _wct_x[xi], _wct_x[xi + 1]
    y1, y2 = wct_y[yi], wct_y[yi + 1]  # y1 >= y2 (north to south)
    tx = (x - x1) / (x2 - x1) if x2 != x1 else 0
    ty = (y1 - y) / (y1 - y2) if y1 != y2 else 0
    col1, col2 = _wct_cols[xi], _wct_cols[xi + 1]
    z11, z12 = col1[yi], col1[yi + 1]
    z21, z22 = col2[yi], col2[yi + 1]
    z1 = z11 + (z12 - z11) * ty
    z2 = z21 + (z22 - z21) * ty
    return FLOOR_Z2 + z1 + (z2 - z1) * tx


def build():
    # WEST_CAMPUS_ENABLED_TERRAIN is not a strict, independent on/off switch:
    # this terrain also builds whenever the WEST_CAMPUS_ENABLED master is
    # True, even if WEST_CAMPUS_ENABLED_TERRAIN itself is False — the west
    # campus buildings/fence/wall rely on this terrain fill to avoid floating
    # over a bare cliff, so the master intentionally forces it on. To
    # preview the terrain with west campus otherwise disabled, set
    # WEST_CAMPUS_ENABLED_TERRAIN true and leave WEST_CAMPUS_ENABLED false.
    if not (WEST_CAMPUS_ENABLED or WEST_CAMPUS_ENABLED_TERRAIN):
        return [], []
    BRUSHES = []
    ENTITIES = []

    # A chain of 3+ Y-segments sharing an exact coincident boundary plane
    # (this grid has 12) trips a qbsp portal-building bug that produces a
    # real leak — see the matching _WRAMP_OVR note in knott_terrain.py for
    # the bisection that found this. Overlap each non-final segment's south
    # edge by a hair so segments no longer share an exact coincident plane.
    #
    # The south edge's height must stay exactly at the real sampled value
    # for the nominal boundary (y2), NOT extrapolated further along this
    # quad's own slope past that boundary — the next segment's north edge
    # uses that same real sampled value for ITS corners, so extrapolating
    # here instead made the two segments disagree on the surface height
    # across the overlap sliver (by several units in places), which is
    # exactly the kind of seam a player's collision hull can sink/fall
    # through. Keeping the height flat across the sliver instead means
    # both segments agree on the boundary height, at the cost of a few
    # units of slope getting flattened right at the seam (imperceptible).
    #
    # 4 units was not always enough: at the row spanning y=-1968..-2768
    # (steeper real-elevation drop than most rows), qbsp's hull1 (player
    # clip hull) CSG still silently dropped the whole row's collision
    # surface even though hull0/visual geometry and the source .map
    # brushes looked correct — confirmed by a direct BSP clipnode probe at
    # (-571, -2162): the compiled player hull reported the base floor slab
    # (z~30) instead of the terrain surface (z~100+), a real fall-through
    # with no leak or qbsp warning to flag it. Raising the overlap to 20
    # units resolved it (verified via the same clipnode probe). Keep this
    # generous rather than re-tuning per row.
    _WCT_OVR = 20

    for (wx1, wcol1), (wx2, wcol2) in zip(
        zip(_wct_x, _wct_cols), zip(_wct_x[1:], _wct_cols[1:])
    ):
        for i in range(len(wct_y) - 1):
            y1, y2 = wct_y[i], wct_y[i + 1]
            z_nw, z_sw = wcol1[i], wcol1[i + 1]
            z_ne, z_se = wcol2[i], wcol2[i + 1]
            if i < len(wct_y) - 2:
                y2 = y2 - _WCT_OVR

            # A single diagonal split (the old two-triangle approach) can't
            # represent a "saddle" quad — one where opposite corners' Z sum
            # differs from the other pair's (e.g. NW+SE != NE+SW) — without
            # introducing a sharp, unavoidable slope crease along whichever
            # diagonal gets chosen. That crease is a real (if shallow-Z)
            # concave fold in the walkable surface, which can snag the
            # player's bounding box and make them sink/stick partway into
            # the ground when crossing it (observed at (-923, 626, 56), in
            # the FENCE_X1/-700 x=8/9 column pair). Fan all four corners
            # around a centre point (the corners' Z average) instead —
            # four shallower creases radiating from the centre, none of
            # them as sharp as the single-diagonal fold could get.
            mx, my = (wx1 + wx2) / 2, (y1 + y2) / 2
            mz = (z_nw + z_ne + z_sw + z_se) / 4
            zbot = FLOOR_Z1
            # wx1 < wx2 and y1 > y2 (north-to-south) always hold for this
            # grid, so (corner, centre, next-corner) is CCW for every one
            # of the four fan triangles below — verified against
            # tri_ramp_prism's required CCW-from-above winding.
            BRUSHES.append(  # north
                tri_ramp_prism(
                    wx1,
                    y1,
                    mx,
                    my,
                    wx2,
                    y1,
                    zbot,
                    FLOOR_Z2 + z_nw,
                    FLOOR_Z2 + mz,
                    FLOOR_Z2 + z_ne,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(  # east
                tri_ramp_prism(
                    wx2,
                    y1,
                    mx,
                    my,
                    wx2,
                    y2,
                    zbot,
                    FLOOR_Z2 + z_ne,
                    FLOOR_Z2 + mz,
                    FLOOR_Z2 + z_se,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(  # south
                tri_ramp_prism(
                    wx2,
                    y2,
                    mx,
                    my,
                    wx1,
                    y2,
                    zbot,
                    FLOOR_Z2 + z_se,
                    FLOOR_Z2 + mz,
                    FLOOR_Z2 + z_sw,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(  # west
                tri_ramp_prism(
                    wx1,
                    y2,
                    mx,
                    my,
                    wx1,
                    y1,
                    zbot,
                    FLOOR_Z2 + z_sw,
                    FLOOR_Z2 + mz,
                    FLOOR_Z2 + z_nw,
                    Textures.GROUND,
                )
            )

    return BRUSHES, ENTITIES
