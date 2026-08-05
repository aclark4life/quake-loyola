"""Real-elevation terrain for the northeast quadrant.

This module fills the area north of Ennis Road and east of Charles Street
with a sampled height grid. The west and south edges tie flush to the
existing sidewalk and curb geometry, and the sampled relief is scaled and
tapered to keep the terrain walkable.
"""

from ..constants import (
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
from ..geometry import extend_terrain_row_overlap, tri_ramp_prism

_NE_HEIGHT_SCALE = 0.5


_NE_ROW_TAPER = [0.25, 0.45, 0.7, 1.0, 1.0, 1.0]


def _clamp0(zs):
    """Scale a sampled row and clamp any below-grade values to flat grade."""
    return [
        max(0, z * _NE_HEIGHT_SCALE * taper)
        for z, taper in zip(zs, _NE_ROW_TAPER, strict=False)
    ]


def build():
    """Build the northeast terrain brushes."""
    if not NE_ENABLED_TERRAIN:
        return [], []
    BRUSHES = []
    ENTITIES = []

    _ne_x = [
        ROAD_X2 + CHARLES_WALK_W,
        900,
        1700,
        KNOTT_DRIVEWAY_CORRIDOR_X1,
        KNOTT_DRIVEWAY_CORRIDOR_X2,
        3472,
        5000,
        7300,
        WORLD_X2_EXT - WALL_T,
    ]

    _ne_y = [
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
        1546,
        1696,
        2200,
        2800,
        3450,
        WORLD_Y2 - WALL_T,
    ]

    _ne_cols = [
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
                y2, z1b, z2b = extend_terrain_row_overlap(
                    y1, y2, z1a, z1b, z2a, z2b, _NE_OVR
                )

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
