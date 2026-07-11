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
    -550,
    -420,
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
# rows), one column per _wct_x entry (except the last, flat sidewalk-tie
# column), values in the same order as wct_y. The baseline (0) already
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
]
# The real -700 column rises to ~90-115 near the south end, but the
# sidewalk-tie column (below) is forced flat at the curb height for the
# *entire* Y range (streets.py already owns that ground). Blending
# straight from real -> flat in one 64-unit hop (the old lone "-400"
# column) created a near-vertical cliff right next to the sidewalk,
# worst in the south where the real/flat gap is largest — reported as an
# unnatural steep drop-off close to Charles St. Taper across two more
# steps (-550, -420) instead, each moving partway from the real -700
# column toward the flat curb height, so the same total drop is spread
# over ~364 units rather than 64.
_wct_real_700 = _wct_cols[-1]
_wct_flat_walk = [CHARLES_WALK_H] * len(wct_y)


def _wct_taper(frac):
    return [round(r + (CHARLES_WALK_H - r) * frac) for r in _wct_real_700]


_wct_cols += [
    _wct_taper(0.4),  # -550
    _wct_taper(0.75),  # -420
    # Sidewalk-tie column: flat at the curb/raised-ground height
    # streets.py already builds along this whole edge, for every Y row.
    _wct_flat_walk,
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
    if not WEST_CAMPUS_TERRAIN_ENABLED:
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
