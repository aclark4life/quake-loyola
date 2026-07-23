"""Placeholder terrain support for the Maryland Hall massing block.

The module builds a flat pad and simple south/east slopes around Maryland
Hall. When both Maryland Hall and its terrain are disabled, it emits only
HINT brushes around the footprint.
"""

from ..constants import (
    FLOOR_Z1,
    FLOOR_Z2,
    MARYLAND_ENABLED,
    MARYLAND_ENABLED_TERRAIN,
    MARYLAND_GROUND_Z,
    MARYLAND_TERRAIN_MARGIN,
    MARYLAND_TERRAIN_RAMP_W,
    MARYLAND_X1,
    MARYLAND_X2,
    MARYLAND_Y1,
    MARYLAND_Y2,
    WORLD_Z2,
    Textures,
)
from ..geometry import box, corner_ramp, ramp_slab, ramp_slab_y


def build():
    """Build the Maryland Hall terrain brushes."""
    if not MARYLAND_ENABLED_TERRAIN and not MARYLAND_ENABLED:
        pad_x1 = MARYLAND_X1
        pad_x2 = MARYLAND_X2 + MARYLAND_TERRAIN_MARGIN
        pad_y1 = MARYLAND_Y1 - MARYLAND_TERRAIN_MARGIN
        pad_y2 = MARYLAND_Y2
        hint_t = 4
        return (
            [
                box(
                    pad_x1 - hint_t,
                    pad_y1,
                    FLOOR_Z1,
                    pad_x1,
                    pad_y2,
                    WORLD_Z2,
                    Textures.HINT,
                ),
                box(
                    pad_x2,
                    pad_y1,
                    FLOOR_Z1,
                    pad_x2 + hint_t,
                    pad_y2,
                    WORLD_Z2,
                    Textures.HINT,
                ),
                box(
                    pad_x1,
                    pad_y1 - hint_t,
                    FLOOR_Z1,
                    pad_x2,
                    pad_y1,
                    WORLD_Z2,
                    Textures.HINT,
                ),
                box(
                    pad_x1,
                    pad_y2,
                    FLOOR_Z1,
                    pad_x2,
                    pad_y2 + hint_t,
                    WORLD_Z2,
                    Textures.HINT,
                ),
            ],
            [],
        )
    BRUSHES = []
    ENTITIES = []

    pad_x1 = MARYLAND_X1
    pad_x2 = MARYLAND_X2 + MARYLAND_TERRAIN_MARGIN
    pad_y1 = MARYLAND_Y1 - MARYLAND_TERRAIN_MARGIN
    pad_y2 = MARYLAND_Y2
    BRUSHES.append(
        box(
            pad_x1,
            pad_y1,
            FLOOR_Z1,
            pad_x2,
            pad_y2,
            MARYLAND_GROUND_Z,
            Textures.GROUND,
            tt=Textures.MULCH,
        )
    )

    rw = MARYLAND_TERRAIN_RAMP_W

    BRUSHES.append(
        ramp_slab(
            pad_x2,
            pad_x2 + rw,
            pad_y1,
            pad_y2,
            FLOOR_Z1,
            FLOOR_Z1,
            MARYLAND_GROUND_Z,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    BRUSHES.append(
        ramp_slab_y(
            pad_x1,
            pad_x2,
            pad_y1 - rw,
            pad_y1,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2,
            MARYLAND_GROUND_Z,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    BRUSHES.append(
        corner_ramp(
            pad_x2,
            pad_y1,
            pad_x2 + rw,
            pad_y1 - rw,
            FLOOR_Z2,
            MARYLAND_GROUND_Z,
            Textures.GROUND,
        )
    )

    return BRUSHES, ENTITIES
