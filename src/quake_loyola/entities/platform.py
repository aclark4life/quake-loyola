from ..constants import (
    BRIDGE,
    CHARLES_PLT_BR_X,
    CHARLES_PLT_H,
    CHARLES_PLT_SPEED,
    CHARLES_PLT_W,
    CHARLES_PLT_X_OUT,
    CHARLES_PLT_X_RET,
    CHARLES_PLT_Y_OUT,
    CHARLES_PLT_Y_RET,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM,
    ENTITIES_ENABLED_PLATFORM,
    FLOOR_Z2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    ROAD_X1,
    ROAD_X2,
    Textures,
)
from ..geometry import (
    box,
    brush_ent,
    ent,
    path_loop,
)
from ._common import ROAD_Z


def _build_platform(ENTITIES):
    platform_start = len(ENTITIES)

    CHARLES_PLT_Y_S = CHARLES_Y1 + CHARLES_PLT_W // 2 + 48

    platform_z_charles = ROAD_Z + CHARLES_PLT_H // 2
    platform_z_flat = FLOOR_Z2 + 2 + CHARLES_PLT_H // 2
    platform_z_backroad_south = KNOTT_DRIVEWAY_ZT_S + 2 + CHARLES_PLT_H // 2

    cs_platform_brush = box(
        CHARLES_PLT_X_OUT - CHARLES_PLT_W // 2,
        CHARLES_PLT_Y_S - CHARLES_PLT_W // 2,
        ROAD_Z,
        CHARLES_PLT_X_OUT + CHARLES_PLT_W // 2,
        CHARLES_PLT_Y_S + CHARLES_PLT_W // 2,
        ROAD_Z + CHARLES_PLT_H,
        Textures.FLOOR,
    )
    ENTITIES.append(
        brush_ent(
            "func_train",
            [cs_platform_brush],
            target="cs_pc1",
            speed=str(CHARLES_PLT_SPEED),
            _minlight="255",
        )
    )

    ENTITIES.extend(
        path_loop(
            "cs_pc",
            [
                (CHARLES_PLT_X_OUT, CHARLES_PLT_Y_S, platform_z_charles),
                (CHARLES_PLT_X_OUT, CHARLES_PLT_Y_OUT, platform_z_flat),
                (CHARLES_PLT_BR_X, CHARLES_PLT_Y_OUT, platform_z_flat),
                (CHARLES_PLT_BR_X, KNOTT_DRIVEWAY_Y2, platform_z_flat),
                (CHARLES_PLT_BR_X, KNOTT_DRIVEWAY_Y1, platform_z_backroad_south),
                (CHARLES_PLT_BR_X, KNOTT_DRIVEWAY_Y2, platform_z_flat),
                (CHARLES_PLT_BR_X, CHARLES_PLT_Y_RET, platform_z_flat),
                (CHARLES_PLT_X_RET, CHARLES_PLT_Y_RET, platform_z_flat),
                (CHARLES_PLT_X_RET, CHARLES_PLT_Y_S, platform_z_charles),
            ],
        )
    )

    ENTITIES.append(
        ent(
            "item_artifact_super_damage",
            origin=f"{(BRIDGE.x1 + DORM.x1) // 2} {(CHARLES_Y1 + CHARLES_Y2) // 2} {FLOOR_Z2 + 32}",
        )
    )

    rocket_hover_height = CHARLES_PLT_H + 56
    backroad_mid_y = (KNOTT_DRIVEWAY_Y1 + KNOTT_DRIVEWAY_Y2) // 2
    backroad_mid_z = (
        FLOOR_Z2
        + 2
        + (KNOTT_DRIVEWAY_ZT_S - KNOTT_DRIVEWAY_ZT_N)
        * (backroad_mid_y - KNOTT_DRIVEWAY_Y2)
        // (KNOTT_DRIVEWAY_Y1 - KNOTT_DRIVEWAY_Y2)
    )
    for rocket_x, rocket_y, rocket_z in [
        (
            ROAD_X2 + 40,
            CHARLES_Y1 + (CHARLES_Y2 - CHARLES_Y1) // 6,
            ROAD_Z + rocket_hover_height,
        ),
        (
            ROAD_X2 + 40,
            CHARLES_Y1 + (CHARLES_Y2 - CHARLES_Y1) * 2 // 6,
            ROAD_Z + rocket_hover_height,
        ),
        (CHARLES_PLT_BR_X, backroad_mid_y, backroad_mid_z + rocket_hover_height),
        (
            ROAD_X1 - 40,
            CHARLES_Y1 + (CHARLES_Y2 - CHARLES_Y1) // 6,
            ROAD_Z + rocket_hover_height,
        ),
        (
            ROAD_X1 - 40,
            CHARLES_Y1 + (CHARLES_Y2 - CHARLES_Y1) * 2 // 6,
            ROAD_Z + rocket_hover_height,
        ),
    ]:
        ENTITIES.append(
            ent("weapon_rocketlauncher", origin=f"{rocket_x} {rocket_y} {rocket_z}")
        )

    if not ENTITIES_ENABLED_PLATFORM:
        del ENTITIES[platform_start:]
