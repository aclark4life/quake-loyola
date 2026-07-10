"""Sub-basement level — doubles the total world height.

Adds a walled void below the existing ground-floor slab, symmetric about
Z=0 (see BASEMENT_Z1 in constants.py). No access point (teleporter/hatch)
yet — this module only builds the sealed basement shell itself; a way down
will be added separately once the basement has actual content.
"""

from .constants import (
    BASEMENT_ENABLED,
    BASEMENT_FLOOR_Z1,
    BASEMENT_Z1,
    FLOOR_Z1,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    Textures,
)
from .geometry import box, ent


def build():
    if not BASEMENT_ENABLED:
        return [], []

    BRUSHES = []
    ENTITIES = []

    # ── Basement floor slab ──────────────────────────────────────────────────
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BASEMENT_FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            BASEMENT_Z1,
            Textures.SKY,
        )
    )

    # ── Perimeter walls — continue the world-shell footprint straight down
    # from the underside of the existing ground slab (FLOOR_Z1) to the new
    # basement floor (BASEMENT_Z1), so there's no gap/lip at the seam.
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BASEMENT_Z1,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            FLOOR_Z1,
            Textures.SKY,
        )
    )  # W wall
    BRUSHES.append(
        box(
            WORLD_X2_EXT - WALL_T,
            WORLD_Y1,
            BASEMENT_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z1,
            Textures.SKY,
        )
    )  # E wall
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BASEMENT_Z1,
            WORLD_X2_EXT,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            Textures.SKY,
        )
    )  # S wall
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y2 - WALL_T,
            BASEMENT_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z1,
            Textures.SKY,
        )
    )  # N wall

    # ── Lighting — the basement is otherwise a fully unlit sky-textured void
    # (no ambient/sunlight reaches this enclosed space), so a grid of lights
    # is placed at a mid-height plane to make the room actually visible.
    # Tagged with the "basement" light group (see generate_map.py) so these
    # stay on regardless of the global LIGHTS_ENABLED master switch.
    light_z = BASEMENT_Z1 + 300
    step = 2500
    margin = 300
    x = WORLD_X1 + margin
    while x < WORLD_X2_EXT - margin:
        y = WORLD_Y1 + margin
        while y < WORLD_Y2 - margin:
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{x} {y} {light_z}",
                    light="500",
                    _light_group="basement",
                )
            )
            y += step
        x += step

    return BRUSHES, ENTITIES
