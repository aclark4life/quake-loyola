from ..constants import (
    BRIDGE,
    BRIDGE_ARCH_X,
    DORM_CX,
    DORM_NORTH_CY,
    DORM_RIDGE_Z,
    ENNIS_CEMENT_X1,
    ENNIS_CEMENT_X2,
    ENNIS_HW,
    ENNIS_WALL_NY,
    ENNIS_Y,
    ENTITIES_ENABLED_AMMO,
    ENTITIES_ENABLED_HEALTH,
    ENTITIES_ENABLED_WEAPONS,
    FLOOR_Z2,
    ROAD_X2,
    SDORM_LIFT,
    WEST_CAMPUS_ENABLED_DORMS,
    WEST_CAMPUS_ENABLED_DORMS_SOUTH,
    deck_top_z,
)
from ..geometry import (
    ent,
)
from ._common import DORM_SOUTH1_CY, DORM_SOUTH2_CY, ROAD_Z, _cs_offset


def _build_weapons(ENTITIES):
    weapons_start = len(ENTITIES)

    _rl_y, _rl_z = _cs_offset(0, 0, int(deck_top_z(0) + 8))
    ENTITIES.append(ent("weapon_rocketlauncher", origin=f"0 {_rl_y} {_rl_z}"))

    span1_x = (BRIDGE.x1 + BRIDGE_ARCH_X[0]) // 2
    span4_x = (BRIDGE_ARCH_X[2] + BRIDGE.x2) // 2
    span5_x = (BRIDGE.x2 + BRIDGE_ARCH_X[4]) // 2
    for rl_origin in [
        f"{ROAD_X2 + 40} {ENNIS_Y - ENNIS_HW - 200} {ROAD_Z + 24}",
        f"{BRIDGE_ARCH_X[2]} 0 {ROAD_Z + 24}",
        f"{int(ENNIS_CEMENT_X1 + (ENNIS_CEMENT_X2 - ENNIS_CEMENT_X1) // 2)} {ENNIS_WALL_NY - 80} {FLOOR_Z2 + 24}",
        f"{span1_x} 0 {int(deck_top_z(span1_x) + 8)}",
        f"{span4_x} 0 {int(deck_top_z(span4_x) + 8)}",
        f"{span5_x} 0 {int(deck_top_z(span5_x) + 8)}",
    ]:
        ENTITIES.append(ent("weapon_rocketlauncher", origin=rl_origin))

    ENTITIES.append(ent("weapon_supershotgun", origin=f"300 300 {ROAD_Z + 24}"))
    if WEST_CAMPUS_ENABLED_DORMS_SOUTH:
        ENTITIES.append(
            ent(
                "weapon_supershotgun",
                origin=f"{DORM_CX} {DORM_SOUTH1_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
            )
        )

        ENTITIES.append(
            ent(
                "weapon_grenadelauncher",
                origin=f"{DORM_CX} {DORM_SOUTH2_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
            )
        )

    ENTITIES.append(ent("weapon_nailgun", origin=f"-600 0 {ROAD_Z + 24}"))
    ENTITIES.append(ent("weapon_nailgun", origin=f"600 0 {ROAD_Z + 24}"))

    _lg_y, _lg_z = _cs_offset(200, 0, int(deck_top_z(200) + 8))
    ENTITIES.append(ent("weapon_lightning", origin=f"200 {_lg_y} {_lg_z}"))
    ENTITIES.append(ent("weapon_lightning", origin=f"0 -500 {ROAD_Z + 24}"))

    if not ENTITIES_ENABLED_WEAPONS:
        del ENTITIES[weapons_start:]


def _build_ammo(ENTITIES):
    ammo_start = len(ENTITIES)
    for ax in BRIDGE_ARCH_X:
        _ir_y, _ir_z = _cs_offset(ax, 0, int(deck_top_z(ax) + 8))
        ENTITIES.append(ent("item_rockets", origin=f"{ax} {_ir_y} {_ir_z}"))
    for rx in [400, 800]:
        ENTITIES.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z + 24}"))
        ENTITIES.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_shells", origin=f"-300 -300 {ROAD_Z + 24}"))
    if WEST_CAMPUS_ENABLED_DORMS:
        ENTITIES.append(
            ent("item_shells", origin=f"{DORM_CX} {DORM_NORTH_CY} {FLOOR_Z2 + 40}")
        )
    ENTITIES.append(ent("item_spikes", origin=f"-400 200 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_spikes", origin=f"400 -200 {ROAD_Z + 24}"))

    if not ENTITIES_ENABLED_AMMO:
        del ENTITIES[ammo_start:]


def _build_health(ENTITIES):
    health_start = len(ENTITIES)

    _hp_y, _hp_z = _cs_offset(-100, 0, int(deck_top_z(-100) + 8))
    ENTITIES.append(ent("item_health", origin=f"-100 {_hp_y} {_hp_z}"))
    ENTITIES.append(ent("item_health", origin=f"-300 400 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_health", origin=f"300 -600 {ROAD_Z + 24}"))
    if WEST_CAMPUS_ENABLED_DORMS_SOUTH:
        ENTITIES.append(
            ent(
                "item_health",
                origin=f"{DORM_CX} {DORM_SOUTH2_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
            )
        )

    _arm_y, _arm_z = _cs_offset(-200, 0, int(deck_top_z(-200) + 8))
    ENTITIES.append(ent("item_armor1", origin=f"-200 {_arm_y} {_arm_z}"))
    if WEST_CAMPUS_ENABLED_DORMS:
        ENTITIES.append(
            ent(
                "item_armorInv",
                origin=f"{DORM_CX} {DORM_NORTH_CY} {int(DORM_RIDGE_Z + 40)}",
            )
        )

    if not ENTITIES_ENABLED_HEALTH:
        del ENTITIES[health_start:]
