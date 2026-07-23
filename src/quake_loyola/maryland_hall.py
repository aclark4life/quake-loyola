"""Placeholder massing block for Maryland Hall."""

from .constants import (
    MARYLAND_ENABLED,
    MARYLAND_GROUND_Z,
    MARYLAND_H,
    MARYLAND_X1,
    MARYLAND_X2,
    MARYLAND_Y1,
    MARYLAND_Y2,
    Textures,
)
from .geometry import box


def build():
    """Build the Maryland Hall massing block when enabled."""
    if not MARYLAND_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    BRUSHES.append(
        box(
            MARYLAND_X1,
            MARYLAND_Y1,
            MARYLAND_GROUND_Z,
            MARYLAND_X2,
            MARYLAND_Y2,
            MARYLAND_GROUND_Z + MARYLAND_H,
            Textures.BUILDING,
            tt=Textures.ROOF,
        )
    )

    return BRUSHES, ENTITIES
