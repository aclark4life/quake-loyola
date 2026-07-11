"""Sub-basement level — doubles the total world height.

Adds a walled void below the existing ground-floor slab, symmetric about
Z=0 (see BASEMENT_Z1 in constants.py). The only way down is the manhole
opening (MANHOLE_X/Y/R in constants.py), which punches straight through
both this module's ceiling slab and streets.py's world floor slab. A full
stone arch teleport at the north end of the basement — same shape as the
Charles St north arch teleport (entities.py), stonework included — sends
the player back to the map's spawn point.
"""

from .constants import (
    A_SEGS,
    BASEMENT_ENABLED,
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
            Textures.GROUND,
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
            Textures.GROUND,
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
            Textures.GROUND,
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
            Textures.GROUND,
        )
    )  # N wall

    # ── Ceiling — thin slab directly under the existing ground-floor slab,
    # textured ground on both faces, so the basement's ceiling reads clearly
    # as ground when looking up from inside the void. Punched with the
    # matching manhole opening so the hole in streets.py's floor slab above
    # actually connects all the way down into the basement void.
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

    # ── Teleport back to spawn — a full stone arch teleport at the true
    # north end of the world (against the basement's north wall), same
    # shape as the Charles St north arch teleport (entities.py): stone
    # arch surround (func_detail) + teleport glow fill (func_illusionary) +
    # box trigger (trigger_teleport). Targets "dest_start", the
    # info_teleport_destination co-located with the map's spawn point.
    charles_arch_trig_inset = 8  # matches CHARLES_ARCH_TRIG_INSET in entities.py
    charles_arch_segs = 24  # matches CHARLES_ARCH_SEGS in entities.py
    basement_arch_y2 = WORLD_Y2 - WALL_T  # flush against the north wall
    basement_arch_y1 = basement_arch_y2 - CHARLES_ARCH_W
    basement_arch_top_z = BASEMENT_Z1 + CHARLES_ARCH_STILT + CHARLES_ARCH_RIN

    basement_arch_glow = arch_fill_y(
        basement_arch_y1,
        basement_arch_y2,
        0.0,
        BASEMENT_Z1 + 4,
        CHARLES_ARCH_RIN,
        A_SEGS,
        Textures.TELEPORT,
        stilt_h=CHARLES_ARCH_STILT,
    )
    ENTITIES.append(brush_ent("func_illusionary", basement_arch_glow))

    basement_arch_stone = arch_wall_y(
        basement_arch_y1,
        basement_arch_y2,
        WORLD_X1 + WALL_T,
        WORLD_X2_EXT - WALL_T,
        BASEMENT_Z1,
        basement_arch_top_z,
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
            Textures.TELEPORT,
        )
    ]
    ENTITIES.append(
        brush_ent("trigger_teleport", basement_arch_trigger, target="dest_start")
    )

    return BRUSHES, ENTITIES
