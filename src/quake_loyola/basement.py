"""Sub-basement shell, lighting, and return teleport."""

from .constants import (
    BASEMENT_FLOOR_Z1,
    BASEMENT_Z1,
    CHARLES_ARCH_RIN,
    CHARLES_ARCH_ROUT,
    CHARLES_ARCH_STILT,
    CHARLES_ARCH_W,
    FLOOR_Z1,
    MANHOLE_R,
    MANHOLE_X,
    MANHOLE_Y,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    Textures,
)
from .geometry import (
    arch_fill_y,
    arch_wall_y,
    box,
    box_with_round_hole,
    brush_ent,
    ent,
)

LIGHT_GRID_Z_OFFSET = 300  # Height above the basement floor for grid lights.
LIGHT_GRID_STEP = 2500  # Spacing between lights in both X and Y.
LIGHT_GRID_MARGIN = 300  # Inset from the basement walls before the first light.
LIGHT_GRID_BRIGHTNESS = "500"


def build():
    """Build the basement brushes and entities."""
    BRUSHES = []
    ENTITIES = []

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

    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BASEMENT_Z1,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            FLOOR_Z1,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X2_EXT - WALL_T,
            WORLD_Y1,
            BASEMENT_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z1,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BASEMENT_Z1,
            WORLD_X2_EXT,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y2 - WALL_T,
            BASEMENT_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z1,
            Textures.GROUND,
        )
    )

    BRUSHES.extend(
        box_with_round_hole(
            WORLD_X1 + WALL_T,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1 - WALL_T,
            WORLD_X2_EXT - WALL_T,
            WORLD_Y2 - WALL_T,
            FLOOR_Z1,
            MANHOLE_X,
            MANHOLE_Y,
            MANHOLE_R,
            Textures.GROUND,
        )
    )

    light_z = BASEMENT_Z1 + LIGHT_GRID_Z_OFFSET
    step = LIGHT_GRID_STEP
    margin = LIGHT_GRID_MARGIN
    x = WORLD_X1 + margin
    while x < WORLD_X2_EXT - margin:
        y = WORLD_Y1 + margin
        while y < WORLD_Y2 - margin:
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{x} {y} {light_z}",
                    light=LIGHT_GRID_BRIGHTNESS,
                )
            )
            y += step
        x += step

    charles_arch_trig_inset = 8
    charles_arch_segs = 24
    basement_arch_y2 = WORLD_Y2 - WALL_T
    basement_arch_y1 = basement_arch_y2 - CHARLES_ARCH_W
    basement_arch_glow = arch_fill_y(
        basement_arch_y1,
        basement_arch_y2,
        0.0,
        BASEMENT_Z1 + 4,
        CHARLES_ARCH_RIN,
        charles_arch_segs,
        Textures.TELEPORT,
        stilt_h=CHARLES_ARCH_STILT,
    )
    ENTITIES.append(brush_ent("func_illusionary", basement_arch_glow))

    basement_arch_stone = arch_wall_y(
        basement_arch_y1,
        basement_arch_y2,
        BASEMENT_Z1,
        CHARLES_ARCH_RIN,
        CHARLES_ARCH_ROUT,
        charles_arch_segs,
        Textures.PILLAR,
        stilt_h=CHARLES_ARCH_STILT,
    )
    ENTITIES.append(brush_ent("func_detail", basement_arch_stone))

    basement_arch_trigger = [
        box(
            -CHARLES_ARCH_RIN + charles_arch_trig_inset,
            basement_arch_y1 + charles_arch_trig_inset,
            BASEMENT_Z1,
            CHARLES_ARCH_RIN - charles_arch_trig_inset,
            basement_arch_y2,
            BASEMENT_Z1 + CHARLES_ARCH_STILT + 128,
            # The trigger volume is invisible, so it takes Textures.TRIGGER and
            # not the *teleport it sits inside: a '*' name is a liquid content
            # type to qbsp, which has no business being applied to a brush
            # entity whose only job is to be walked through. The visible glow
            # above keeps *teleport.
            Textures.TRIGGER,
        )
    ]
    ENTITIES.append(
        brush_ent("trigger_teleport", basement_arch_trigger, target="dest_start")
    )

    return BRUSHES, ENTITIES
