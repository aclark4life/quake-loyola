"""Real-elevation terrain for the west campus hillside.

This module builds the sampled ground west of Charles Street, including the
dorm area and the bridge's west approach. The terrain grid spans the full
modeled Charles Street Y range and tapers back to the sidewalk height at the
street edge.
"""

from ..constants import (
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
    WEST_CAMPUS_ENABLED_TERRAIN,
    WORLD_X1,
    WORLD_Y1,
    WORLD_Y2,
    Textures,
)
from ..geometry import tri_ramp_prism
from ._mesh_helpers import append_sampled_grid_mesh


def _clamp0(zs):
    """Clamp below-grade sampled heights to flat grade."""
    return [max(0, z) for z in zs]


_wct_dorm_cx = (DORM_X1 + DORM_X2) // 2
_wct_sidewalk_x = ROAD_X1 - CHARLES_WALK_W


_WCT_TAPER_FRACS = (0.2, 0.4, 0.6, 0.8)
if not FENCE_X1 < _wct_sidewalk_x:
    raise ValueError(
        "west_campus_terrain X grid must stay in strict west-to-east order; "
        "FENCE_X1 has drifted past the sidewalk tie — re-derive the terrain "
        "grid before widening further."
    )


def _wct_taper_x(frac):
    return round(FENCE_X1 + (_wct_sidewalk_x - FENCE_X1) * frac)


_wct_raw = list(
    zip(
        [WORLD_X1 + WALL_T, -4500, -3500, -2500, BRIDGE_X1],
        [
            [-79, 9, 83, 90, 129, 134, 172, 163, 92, 51, -74, 124, 167],
            [-66, -6, 74, 83, 106, 132, 145, 133, 89, 52, -42, 182, 215],
            [-36, 10, 123, 115, 98, 111, 122, 104, 100, 67, 2, 226, 245],
            [-119, 11, 124, 125, 142, 143, 145, 143, 165, 149, 40, 232, 223],
            [-78, 13, 142, 147, 155, 141, 146, 150, 142, 147, 58, 233, 221],
        ],
        strict=True,
    )
) + list(
    zip(
        [DORM_X1, _wct_dorm_cx, DORM_X2, FENCE_X1],
        [
            [-78, -8, 143, 146, 151, 129, 135, 152, 149, 144, 64, 233, 216],
            [-103, -19, 101, 102, 107, 114, 110, 124, 141, 134, 74, 227, 209],
            [-117, -23, 88, 92, 101, 106, 105, 108, 109, 122, 86, 206, 198],
            [-116, -36, 62, 74, 88, 101, 104, 108, 113, 108, 93, 161, 186],
        ],
        strict=True,
    )
)
_wct_raw.sort(key=lambda pair: pair[0])
_wct_raw_x = [x for x, _ in _wct_raw]
if not (len(_wct_raw_x) == len(set(_wct_raw_x)) and _wct_raw_x == sorted(_wct_raw_x)):
    raise ValueError(
        "west_campus_terrain surveyed X columns collided or failed to sort "
        "strictly ascending — two grid columns landed on the same X (or the "
        "sort itself is broken); re-derive the terrain grid before widening "
        "further."
    )
_wct_x = _wct_raw_x + [_wct_taper_x(f) for f in _WCT_TAPER_FRACS] + [_wct_sidewalk_x]


wct_y = [
    WORLD_Y2 - WALL_T,
    2800,
    1846,
    1696,
    1396,
    500,
    0,
    -1068,
    -1968,
    -2768,
    -3800,
    -5200,
    WORLD_Y1 + WALL_T,
]


_wct_cols = [_clamp0(col) for _, col in _wct_raw]


_wct_fence_col = _wct_cols[-1]
_wct_flat_walk = [CHARLES_WALK_H] * len(wct_y)


def _wct_taper(frac):
    return [round(r + (CHARLES_WALK_H - r) * frac) for r in _wct_fence_col]


_wct_cols += [_wct_taper(f) for f in _WCT_TAPER_FRACS] + [_wct_flat_walk]


def terrain_z(x, y):
    """Return the interpolated terrain height at ``(x, y)`` within this grid."""
    x = min(max(x, _wct_x[0]), _wct_x[-1])
    y = max(min(y, wct_y[0]), wct_y[-1])
    xi = 0
    while xi < len(_wct_x) - 2 and _wct_x[xi + 1] < x:
        xi += 1
    yi = 0
    while yi < len(wct_y) - 2 and wct_y[yi + 1] > y:
        yi += 1
    x1, x2 = _wct_x[xi], _wct_x[xi + 1]
    y1, y2 = wct_y[yi], wct_y[yi + 1]
    tx = (x - x1) / (x2 - x1) if x2 != x1 else 0
    ty = (y1 - y) / (y1 - y2) if y1 != y2 else 0
    col1, col2 = _wct_cols[xi], _wct_cols[xi + 1]
    z11, z12 = col1[yi], col1[yi + 1]
    z21, z22 = col2[yi], col2[yi + 1]
    z1 = z11 + (z12 - z11) * ty
    z2 = z21 + (z22 - z21) * ty
    return FLOOR_Z2 + z1 + (z2 - z1) * tx


_WCT_OVR = 32  # Overlap extension for adjacent terrain rows; see build().
# 32 is chosen empirically: the terrain grid's DORM_X1/DORM_X2 columns and its
# y=1396/1846 rows fall exactly on the dorm walls, so an overlap that lands
# near the wall thickness makes qbsp clip the wall faces against the
# overlapping terrain prisms and leaves uncovered strips at grade inside the
# dorms. Sweeping 0..40 against a hole scan of the dorm block gave 73/426/1446
# /42/59/131/1/16 uncovered samples for 0/4/8/12/16/24/32/40. Re-run that sweep
# if the terrain grid or the dorm footprint moves.


def _build_west_campus_terrain_cell(wx1, wx2, y1, y2, z_nw, z_sw, z_ne, z_se, texture):
    """Return the four prisms that mesh one west-campus terrain quad."""

    mx, my = (wx1 + wx2) / 2, (y1 + y2) / 2
    mz = (z_nw + z_ne + z_sw + z_se) / 4
    return [
        tri_ramp_prism(
            wx1,
            y1,
            mx,
            my,
            wx2,
            y1,
            FLOOR_Z1,
            FLOOR_Z2 + z_nw,
            FLOOR_Z2 + mz,
            FLOOR_Z2 + z_ne,
            texture,
        ),
        tri_ramp_prism(
            wx2,
            y1,
            mx,
            my,
            wx2,
            y2,
            FLOOR_Z1,
            FLOOR_Z2 + z_ne,
            FLOOR_Z2 + mz,
            FLOOR_Z2 + z_se,
            texture,
        ),
        tri_ramp_prism(
            wx2,
            y2,
            mx,
            my,
            wx1,
            y2,
            FLOOR_Z1,
            FLOOR_Z2 + z_se,
            FLOOR_Z2 + mz,
            FLOOR_Z2 + z_sw,
            texture,
        ),
        tri_ramp_prism(
            wx1,
            y2,
            mx,
            my,
            wx1,
            y1,
            FLOOR_Z1,
            FLOOR_Z2 + z_sw,
            FLOOR_Z2 + mz,
            FLOOR_Z2 + z_nw,
            texture,
        ),
    ]


def build():
    """Build the west campus terrain brushes."""

    if not WEST_CAMPUS_ENABLED_TERRAIN:
        return [], []
    BRUSHES = []
    ENTITIES = []

    append_sampled_grid_mesh(
        BRUSHES,
        _wct_x,
        wct_y,
        _wct_cols,
        overlap=-_WCT_OVR,
        texture=Textures.GROUND,
        build_cell_brushes=_build_west_campus_terrain_cell,
    )

    return BRUSHES, ENTITIES
