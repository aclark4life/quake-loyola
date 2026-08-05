from ..constants import (
    BRIDGE,
    BRIDGE_ARCH_X,
    BRIDGE_ENABLED_PIER_BASE_LIGHTS,
    BRIDGE_ENABLED_SUPPORTS,
    BRIDGE_PEND_XS,
    BRIDGE_PILLAR_BASE_H,
    BRIDGE_PILLAR_BASE_RAMP_H,
    BRIDGE_PILLAR_HW,
    DORM,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    FLOOR_Z2,
    KNOTT,
    KNOTT_CX,
    KNOTT_ENABLED_WALKWAY,
    SDORM_LIFT,
    WALK_ZT1,
    WALK_ZT2,
    WEST_CAMPUS_ENABLED_DORMS,
    deck_bot_z,
)
from ..geometry import (
    ent,
)
from ._common import CS_X1, CS_X2, _cs_offset


def _build_lights(ENTITIES):
    if BRIDGE_ENABLED_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            for underbridge_light_y in [BRIDGE.y2 + 30, BRIDGE.y1 - 30]:
                if px == BRIDGE_ARCH_X[0]:
                    continue

                if (
                    px in (BRIDGE_ARCH_X[4], BRIDGE_ARCH_X[-1])
                    and underbridge_light_y == BRIDGE.y1 - 30
                ):
                    continue
                _ul_y, _ul_z = _cs_offset(px, underbridge_light_y, 16)
                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{px} {_ul_y} {_ul_z}",
                        light="200",
                        _light_group="pier_uplight",
                    )
                )

    for pier_x in BRIDGE_PEND_XS:
        if CS_X1 <= pier_x <= CS_X2:
            continue
        _pend_y, _pend_z = _cs_offset(pier_x, 0, int(deck_bot_z(pier_x)) - 20)
        ENTITIES.append(
            ent(
                "light",
                origin=f"{pier_x} {_pend_y} {_pend_z}",
                light="350",
                style="1",
                _light_group="pendant",
            )
        )
    for _center_pend_x in (
        CS_X1 + (CS_X2 - CS_X1) // 4,
        (CS_X1 + CS_X2) // 2,
        CS_X2 - (CS_X2 - CS_X1) // 4,
    ):
        _pend_y, _pend_z = _cs_offset(
            _center_pend_x, 0, int(deck_bot_z(_center_pend_x)) - 20
        )
        ENTITIES.append(
            ent(
                "light",
                origin=f"{_center_pend_x} {_pend_y} {_pend_z}",
                light="350",
                style="1",
                _light_group="pendant",
            )
        )

    if BRIDGE_ENABLED_PIER_BASE_LIGHTS:
        for pier_x in BRIDGE_ARCH_X:
            if pier_x == BRIDGE_ARCH_X[0]:
                continue
            pier_light_z = FLOOR_Z2 + BRIDGE_PILLAR_BASE_RAMP_H + 60
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{pier_x} {BRIDGE.y2 // 2} {pier_light_z}",
                    light="250",
                )
            )
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{pier_x} {BRIDGE.y1 // 2} {pier_light_z}",
                    light="250",
                )
            )

    abutment_pier_x = min(BRIDGE_ARCH_X)
    abutment_arch_z = FLOOR_Z2 + BRIDGE_PILLAR_BASE_H + 60
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + BRIDGE_PILLAR_HW + 32} 0 {abutment_arch_z}",
            light="700",
            _light_group="abutment_arch",
        )
    )
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + BRIDGE_PILLAR_HW + 32} {BRIDGE.y2 // 2} {abutment_arch_z}",
            light="500",
            _light_group="abutment_arch",
        )
    )
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + BRIDGE_PILLAR_HW + 32} {BRIDGE.y1 // 2} {abutment_arch_z}",
            light="500",
            _light_group="abutment_arch",
        )
    )

    if KNOTT_ENABLED_WALKWAY:
        walk_mid_y = (BRIDGE.y1 + KNOTT.y2) // 2
        walk_frac = (BRIDGE.y1 - walk_mid_y) / float(BRIDGE.y1 - KNOTT.y2)
        wk_zb1 = WALK_ZT1 - KNOTT.wall_t
        wk_zb2 = WALK_ZT2 - KNOTT.wall_t
        walk_bot_mid = int(wk_zb1 + walk_frac * (wk_zb2 - wk_zb1))
        ENTITIES.append(
            ent(
                "light",
                origin=f"{KNOTT_CX} {walk_mid_y} {walk_bot_mid - 8}",
                light="300",
            )
        )

    _dorm_north2_y2 = DORM_NORTH_Y1
    _dorm_north2_y1 = _dorm_north2_y2 - (DORM_NORTH_Y2 - DORM_NORTH_Y1)
    bldg_light_xs = [DORM.x1 + (DORM.x2 - DORM.x1) * i // 4 for i in [1, 2, 3]]
    for building_y1, building_y2, building_lift in (
        [
            (DORM_NORTH_Y1, DORM_NORTH_Y2, 0),
            (_dorm_north2_y1, _dorm_north2_y2, 0),
            (DORM_SOUTH1_Y1, DORM_SOUTH1_Y2, SDORM_LIFT),
            (DORM_SOUTH2_Y1, DORM_SOUTH2_Y2, SDORM_LIFT),
        ]
        if WEST_CAMPUS_ENABLED_DORMS
        else []
    ):
        building_y = (building_y1 + building_y2) // 2
        for building_floor_index in range(DORM.floors):
            building_light_z = (
                FLOOR_Z2
                + building_lift
                + building_floor_index * DORM.floor_h
                + DORM.floor_h // 2
            )
            for bldg_light_x in bldg_light_xs:
                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{bldg_light_x} {building_y} {building_light_z}",
                        light="250",
                        _light_group="dorm_interior",
                    )
                )
