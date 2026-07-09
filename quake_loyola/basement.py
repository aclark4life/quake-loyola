"""Sub-basement level — doubles the total world height.

Adds a walled void below the existing ground-floor slab, symmetric about
Z=0 (see BASEMENT_Z1 in constants.py), plus a pair of trigger_teleport pads
that let a player travel between ground level and the basement without any
existing floor slab (streets.py, west_campus_terrain.py, etc.) needing to be
cut open.
"""

from .constants import (
    BASEMENT_ENABLED,
    BASEMENT_FLOOR_Z1,
    BASEMENT_SLAB_T,
    BASEMENT_TELEPORT_CX,
    BASEMENT_TELEPORT_CY,
    BASEMENT_TELEPORT_HW,
    BASEMENT_Z1,
    FLOOR_Z1,
    FLOOR_Z2,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    Textures,
)
from .geometry import box, brush_ent, ent


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
            Textures.GROUND,
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
            Textures.STONE,
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
            Textures.STONE,
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
            Textures.STONE,
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
            Textures.STONE,
        )
    )  # N wall

    # ── Teleport pads — ground level ↔ basement ──────────────────────────────
    cx, cy = BASEMENT_TELEPORT_CX, BASEMENT_TELEPORT_CY
    hw = BASEMENT_TELEPORT_HW

    ground_pad_brush = box(
        cx - hw,
        cy - hw,
        FLOOR_Z2,
        cx + hw,
        cy + hw,
        FLOOR_Z2 + 32,
        Textures.TELEPORT,
    )
    ENTITIES.append(
        brush_ent("trigger_teleport", [ground_pad_brush], target="dest_basement")
    )
    ENTITIES.append(brush_ent("func_illusionary", [ground_pad_brush]))

    basement_pad_brush = box(
        cx - hw,
        cy - hw,
        BASEMENT_Z1,
        cx + hw,
        cy + hw,
        BASEMENT_Z1 + 32,
        Textures.TELEPORT,
    )
    ENTITIES.append(
        brush_ent("trigger_teleport", [basement_pad_brush], target="dest_ground")
    )
    ENTITIES.append(brush_ent("func_illusionary", [basement_pad_brush]))

    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_basement",
            origin=f"{cx} {cy} {BASEMENT_Z1 + 40}",
            angle="0",
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_ground",
            origin=f"{cx} {cy} {FLOOR_Z2 + 40}",
            angle="0",
        )
    )

    ENTITIES.append(
        ent(
            "light",
            origin=f"{cx} {cy} {BASEMENT_Z1 + 128}",
            light="300",
        )
    )

    return BRUSHES, ENTITIES
