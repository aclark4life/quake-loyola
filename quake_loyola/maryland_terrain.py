"""
maryland_terrain — ground mound under/around the Maryland Hall stub.

Maryland Hall (maryland_hall.py) sits on a flat pad at MARYLAND_GROUND_Z,
matching the eastward hill climb documented in docs/reference.rst ("Topology
check"). Without terrain to carry that pad down to the surrounding FLOOR_Z2
plaza, the stub floats above a bare vertical cliff. This module fills that
gap with a flat apron plus a sloped skirt down to grade on two sides
(east/south) — a rough placeholder, not a real-world-derived terrain model
(see the MARYLAND_* constants for what's provisional here). The north (Ennis
Road) and west (KH driveway) sides are left as cuts instead of ramps — see
the in-function comments for why.

Kept separate from knott_terrain.py so each hill/mound (Knott Hall's vs.
Maryland Hall's) can be enabled/disabled independently — both are
provisional models pending re-derivation, and neither should force the
other on or off.
"""

from .constants import (
    FLOOR_Z1,
    FLOOR_Z2,
    MARYLAND_GROUND_Z,
    MARYLAND_TERRAIN_ENABLED,
    MARYLAND_TERRAIN_MARGIN,
    MARYLAND_TERRAIN_RAMP_W,
    MARYLAND_X1,
    MARYLAND_X2,
    MARYLAND_Y1,
    MARYLAND_Y2,
    Textures,
)
from .geometry import box, corner_ramp, ramp_slab, ramp_slab_y


def build():
    if not MARYLAND_TERRAIN_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # Flat apron. East/south get a margin to carry a walkable ramp down to
    # grade. North (Ennis Road) and west (KH driveway) are cut flush with
    # the building footprint itself (no margin) — those roads sit too close
    # to allow any ramp run, so the apron simply stops at the building wall
    # and drops straight down, like a road cut through a hill.
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

    # East skirt — slopes in X from the apron edge (MARYLAND_GROUND_Z) down
    # to grade (FLOOR_Z2) over a run of RAMP_W. No west skirt: the KH
    # driveway's east sidewalk edge (KNOTT_DRIVEWAY_ES_X2 = 2902) sits only
    # ~376 units from the building's west wall (MARYLAND_X1 = 3278) — too
    # close for a full walkable ramp, and ramping across would carry the
    # mound right over the driveway pavement. Cut off flush at the building
    # wall instead (same treatment as the north/Ennis Road side below).
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

    # South skirt — slopes in Y down to grade. No north skirt: Ennis Road's
    # south edge (ENNIS_Y - ENNIS_HW = 753) sits only ~244 units past the
    # building's north wall (MARYLAND_Y2 = 509), too close for a full
    # walkable ramp — and ramping across would carry the mound right over
    # the road. Instead the mound is cut off flush at the building wall
    # there, like a road cut through a hill (matching the "road cut"
    # treatment used elsewhere in this project's topology notes); the
    # apron's own north face (built by box() above) serves as that cut.
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

    # Corner skirt — tetrahedral fill for the diagonal gap the south/east
    # skirts above leave uncovered (apex at the SE apron corner, falling to
    # grade along both outer edges simultaneously). The SW corner is skipped
    # along with the west skirt (see comment above) — that corner is just
    # the plain cut, no ramp blend needed.
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
