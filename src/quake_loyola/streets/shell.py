from ..constants.bridge import (
    BRIDGE_DZ2,
)
from ..constants.derived import (
    BRIDGE,
    DORM,
    MANHOLE_R,
    MANHOLE_X,
    MANHOLE_Y,
    SDORM_LIFT,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    WORLD_Z2,
)
from ..constants.flags import (
    WEST_CAMPUS_ENABLED_TERRAIN,
)
from ..constants.textures import (
    Textures,
)
from ..constants.world import (
    FLOOR_Z1,
    FLOOR_Z2,
)
from ..geometry import (
    box,
    box_with_round_hole,
    ramp_slab,
)


def _build_street_world_shell():
    """Build the base Charles Street tunnel shell and manhole cutout."""

    BRUSHES = []
    ENTITIES = []
    _tunnel_wall_tex_n = Textures.SKY
    _tunnel_wall_tex = Textures.GROUND if WEST_CAMPUS_ENABLED_TERRAIN else Textures.SKY
    BRUSHES.extend(
        box_with_round_hole(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z2,
            MANHOLE_X,
            MANHOLE_Y,
            MANHOLE_R,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            BRIDGE_DZ2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BRIDGE_DZ2,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X2_EXT - WALL_T,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y2 - WALL_T,
            FLOOR_Z1,
            BRIDGE.x1,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            BRIDGE.x1,
            WORLD_Y1 + WALL_T,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y2 - WALL_T,
            WORLD_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            Textures.SKY,
            tt=_tunnel_wall_tex_n,
            te=_tunnel_wall_tex_n,
            ts=_tunnel_wall_tex_n,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y2 - WALL_T,
            WORLD_Y2,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            WORLD_Z2,
            WORLD_Z2,
            Textures.SKY,
            tb=_tunnel_wall_tex_n,
        )
    )
    BRUSHES.append(
        box(
            DORM.x1,
            WORLD_Y2 - WALL_T,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            Textures.SKY,
            tt=_tunnel_wall_tex,
            ts=_tunnel_wall_tex,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y1,
            WORLD_Y1 + WALL_T,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            WORLD_Z2,
            WORLD_Z2,
            Textures.SKY,
            tb=_tunnel_wall_tex,
        )
    )
    BRUSHES.append(
        box(
            DORM.x1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y1 + WALL_T,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            WORLD_Z2 - WALL_T,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    return BRUSHES, ENTITIES
