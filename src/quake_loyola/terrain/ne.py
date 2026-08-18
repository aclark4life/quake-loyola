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
    ENNIS_NE_DIAG_JOINT_P1,
    ENNIS_NE_DIAG_JOINT_P2,
    ENNIS_NE_DIAG_JOINT_W,
    ENNIS_NE_PAD_TILE_P,
    ENNIS_WALL_T,
    ENNIS_WALL_X_OFFSET,
    ENNIS_WIDEN_N,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    ROAD_X2,
    STREET_SURFACE_T,
    STREET_SW_JOINT_DROP,
    STREET_SW_SLAB_LEN,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y2,
    Textures,
)
from ..geometry import (
    polygon_prism,
    recess_joint_tops,
    split_poly_by_joints,
    tri_ramp_prism,
)
from ._mesh_helpers import append_sampled_grid_mesh

_NE_HEIGHT_SCALE = 0.5


_NE_ROW_TAPER = [0.25, 0.3275, 0.45, 0.7, 1.0, 1.0, 1.0]


def _clamp0(zs):
    """Scale a sampled row and clamp any below-grade values to flat grade."""
    return [
        max(0, z * _NE_HEIGHT_SCALE * taper)
        for z, taper in zip(zs, _NE_ROW_TAPER, strict=False)
    ]


def _build_ne_terrain_cell(wx1, wx2, y1, y2, z1a, z1b, z2a, z2b, texture):
    """Return the two prisms that mesh one northeast terrain quad."""

    return [
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
            texture,
        ),
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
            texture,
        ),
    ]


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

# X where the NE entrance wall sits — the strip between the corner's ramped
# sidewalk tiles and the wall is paved (cement) rather than grass.
_NE_WALL_X = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET + ENNIS_WALL_T

_ne_y = [
    ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
    ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W + STREET_SW_SLAB_LEN,
    1546,
    ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W + 2 * STREET_SW_SLAB_LEN,
    1696,
    2200,
    2800,
    3450,
    WORLD_Y2 - WALL_T,
]

# The corner-adjacent strip (x = _ne_x[0]) now tracks the sidewalk's own
# grade: the flat low corner and the first Charles-side tile's east edge
# both sit flat at street-surface grade here, then the ground slopes up to
# full sidewalk height across the relocated ramp tile (the second tile
# north), matching CHARLES_WALK_H beyond that.
_NE_CORNER_STRIP_H = [
    FLOOR_Z2 + STREET_SURFACE_T,
    FLOOR_Z2 + STREET_SURFACE_T,
    FLOOR_Z2 + 4.325,
    FLOOR_Z2 + CHARLES_WALK_H,
    FLOOR_Z2 + CHARLES_WALK_H,
    FLOOR_Z2 + CHARLES_WALK_H,
    FLOOR_Z2 + CHARLES_WALK_H,
    FLOOR_Z2 + CHARLES_WALK_H,
    FLOOR_Z2 + CHARLES_WALK_H,
]

_ne_cols = [
    [z - FLOOR_Z2 for z in _NE_CORNER_STRIP_H],
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([123, 118.1, 108, 55, -17, -80, -90]),
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([173, 165.16, 149, 105, 36, -20, -51]),
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([210, 199.22, 177, 127, 47, -8, -56]),
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([209, 206.39, 201, 119, 37, -15, -53]),
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([200, 199.67, 199, 189, 74, -9, -33]),
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([369, 320.0, 219, 192, 148, 19, -16]),
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([310, 302.49, 287, 233, 201, 142, 39]),
    [CHARLES_WALK_H, CHARLES_WALK_H] + _clamp0([370, 365.43, 356, 311, 221, 198, 110]),
]


_PAD_TILE_X, _PAD_TILE_Y = ENNIS_NE_PAD_TILE_P

# Joints scored across the cement pad, in the order they are cut. Each one
# only cuts the pieces the ones before it left, so a joint that should stop
# partway across (a tee rather than a crossing) does so on its own.
_PAD_JOINTS = (
    # The diagonal coming up off the Charles/Ennis corner, across the whole pad.
    (ENNIS_NE_DIAG_JOINT_P1, ENNIS_NE_DIAG_JOINT_P2, ENNIS_NE_DIAG_JOINT_W, None),
    # East-west through the tile point, cutting only the paving east of the
    # diagonal, so its west end lands on the diagonal instead of crossing it.
    (
        (_PAD_TILE_X - 1, _PAD_TILE_Y),
        (_PAD_TILE_X + 1, _PAD_TILE_Y),
        ENNIS_NE_DIAG_JOINT_W,
        ENNIS_NE_PAD_TILE_P,
    ),
    # South from the tile point to the pad's south edge, cutting only the
    # paving south of the east-west joint.
    (
        (_PAD_TILE_X, _PAD_TILE_Y - 1),
        (_PAD_TILE_X, _PAD_TILE_Y + 1),
        ENNIS_NE_DIAG_JOINT_W,
        (_PAD_TILE_X, (_PAD_TILE_Y + _ne_y[0]) / 2),
    ),
)


def build():
    """Build the northeast terrain brushes."""
    BRUSHES = []
    ENTITIES = []

    # Cement pad over the corner and its first (still-flat) sidewalk tile.
    # It is flat, so it is poured as a single slab rather than a meshed
    # quad, which lets it be scored into tiles: the diagonal joint coming up
    # off the Charles/Ennis corner, and the cross east of it.
    pad_z = FLOOR_Z2 + _ne_cols[0][0]
    BRUSHES.extend(
        polygon_prism(
            piece,
            FLOOR_Z1,
            pad_z,
            Textures.SIDEWALK_JOINT if is_joint else Textures.CEMENT,
        )
        for piece, is_joint in split_poly_by_joints(
            [
                (_ne_x[0], _ne_y[0]),
                (_NE_WALL_X, _ne_y[0]),
                (_NE_WALL_X, _ne_y[1]),
                (_ne_x[0], _ne_y[1]),
            ],
            _PAD_JOINTS,
        )
    )

    # Ground strip alongside the relocated ramp tile: slopes up from the
    # flat corner grade to full sidewalk height across the same Y-span as
    # the ramp, so the ground doesn't leave a ledge next to the sidewalk.
    append_sampled_grid_mesh(
        BRUSHES,
        [_ne_x[0], _NE_WALL_X],
        _ne_y[1:4],
        [_ne_cols[0][1:4], _ne_cols[0][1:4]],
        texture=Textures.GROUND,
        build_cell_brushes=_build_ne_terrain_cell,
    )

    # Remainder of the corner-to-wall strip (rows north of the ramp), flat
    # at full sidewalk height.
    append_sampled_grid_mesh(
        BRUSHES,
        [_ne_x[0], _NE_WALL_X],
        _ne_y[3:],
        [_ne_cols[0][3:], _ne_cols[0][3:]],
        texture=Textures.GROUND,
        build_cell_brushes=_build_ne_terrain_cell,
    )

    append_sampled_grid_mesh(
        BRUSHES,
        [_NE_WALL_X] + _ne_x[1:],
        _ne_y,
        [_ne_cols[0]] + _ne_cols[1:],
        texture=Textures.GROUND,
        build_cell_brushes=_build_ne_terrain_cell,
    )

    recess_joint_tops(BRUSHES, STREET_SW_JOINT_DROP, Textures.SIDEWALK_JOINT)

    return BRUSHES, ENTITIES
