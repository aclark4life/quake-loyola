"""
maryland_hall — placeholder massing block for Maryland Hall.

Maryland Hall is a real Loyola University Maryland academic building east of
Ennis Parallel, near the Sellinger School of Business. This module currently
provides only a rough rectangular massing block (footprint + flat roof) at
its approximate real-world location and size — no facade detail, windows, or
interior have been derived yet.

The footprint anchor (``MARYLAND_X1``/``X2``/``Y1``/``Y2`` in constants.py)
is a PROVISIONAL placeholder derived from OSM GPS footprint data rather than
the project's usual pixel/satellite-screenshot measurement — see the comment
above those constants for the validation method and known caveats (the
Y-axis in particular is not independently cross-checked). Re-derive against
``ref/`` imagery before doing detailed facade work, the same way
``KNOTT_GROUND_Z`` was re-derived from a rough placeholder to a measured
value.

Kept separate from knott_hall.py/knott_terrain.py/west_campus.py so each
area module has a single clear responsibility.
"""

from .constants import (
    MARYLAND_GROUND_Z,
    MARYLAND_H,
    MARYLAND_HALL_ENABLED,
    MARYLAND_X1,
    MARYLAND_X2,
    MARYLAND_Y1,
    MARYLAND_Y2,
    Textures,
)
from .geometry import box


def build():
    if not MARYLAND_HALL_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # Rough massing block only — footprint flush with the eastward hill climb
    # (MARYLAND_GROUND_Z), flat roof at MARYLAND_H above that. No walls/
    # windows/roof detail yet.
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
