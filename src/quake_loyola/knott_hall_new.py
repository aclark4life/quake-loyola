"""Prototype Knott Hall shell: four walls and a roof, no floors.

This is a from-scratch replacement for the old ``knott_hall`` module (see
``knott_hall.py``), sized and placed against the real terrain modeled in
``terrain/knott_hall.py`` rather than the old flat ``KNOTT_GROUND_Z`` anchor.
The interior is left as one big open volume so the footprint and height can
be iterated on before any floors, windows, or interior detail are added.
Once this shape is settled, the old module and its constants can be triaged
and removed.
"""

from .constants import (
    KNOTT_ENABLED_NEW,
    KNOTT_X1,
    KNOTT_X2,
    KNOTT_Y1,
    KNOTT_Y2,
    Textures,
)
from .geometry import box
from .terrain.knott_hall import kh_hill_ground_z

WALL_T = 16
ROOF_T = 16
BUILDING_H = 960  # Matches the old 5-floor massing (5 * 192) as a starting guess.

# The real terrain hillside is flat under the whole footprint (see
# terrain/knott_hall.py's kh_hill_ground_z), so any corner gives the ground Z.
GROUND_Z = kh_hill_ground_z(KNOTT_X1, KNOTT_Y1)


def build():
    if not KNOTT_ENABLED_NEW:
        return [], []

    z1 = GROUND_Z
    z2 = z1 + BUILDING_H
    roof_z1 = z2
    roof_z2 = roof_z1 + ROOF_T

    brushes = [
        # West wall
        box(KNOTT_X1, KNOTT_Y1, z1, KNOTT_X1 + WALL_T, KNOTT_Y2, z2, Textures.BRICK_KH),
        # East wall
        box(KNOTT_X2 - WALL_T, KNOTT_Y1, z1, KNOTT_X2, KNOTT_Y2, z2, Textures.BRICK_KH),
        # South wall (between the two side walls)
        box(
            KNOTT_X1 + WALL_T,
            KNOTT_Y1,
            z1,
            KNOTT_X2 - WALL_T,
            KNOTT_Y1 + WALL_T,
            z2,
            Textures.BRICK_KH,
        ),
        # North wall (between the two side walls)
        box(
            KNOTT_X1 + WALL_T,
            KNOTT_Y2 - WALL_T,
            z1,
            KNOTT_X2 - WALL_T,
            KNOTT_Y2,
            z2,
            Textures.BRICK_KH,
        ),
        # Roof, spanning the full footprint
        box(KNOTT_X1, KNOTT_Y1, roof_z1, KNOTT_X2, KNOTT_Y2, roof_z2, Textures.CEMENT),
    ]
    return brushes, []
