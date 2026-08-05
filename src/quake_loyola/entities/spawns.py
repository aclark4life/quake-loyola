from ..constants import (
    A_SEGS,
    ARCH_RIN,
    ARCH_SLAB_W,
    ARCH_STILT_H,
    BRIDGE_DZ2,
    BRIDGE_EAST_SHIFT_END,
    CHARLES_ARCH_RIN,
    CHARLES_ARCH_ROUT,
    CHARLES_ARCH_STILT,
    CHARLES_ARCH_TRIG_INSET,
    CHARLES_ARCH_W,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM,
    DORM_CX,
    DORM_NORTH_CY,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_RIDGE_Z,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    ENNIS_HW,
    ENNIS_WIDEN_N,
    ENNIS_Y,
    ENTITIES_ENABLED_DM_SPAWNS,
    ENTITIES_ENABLED_TELEPORTS,
    FLOOR_Z2,
    KH_ROOFTOP_ORIGIN,
    KH_ROOFTOP_ORIGIN_ENNIS_EAST,
    KH_ROOFTOP_ORIGIN_KH_DRIVE_SOUTH,
    KNOTT,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_ENABLED,
    SDORM_LIFT,
    WALL_T,
    WEST_CAMPUS_ENABLED_DORMS,
    WORLD_X1,
    WORLD_X2_EXT,
    Textures,
    deck_top_z,
)
from ..geometry import (
    arch_fill,
    arch_fill_y,
    arch_wall,
    arch_wall_y,
    box,
    brush_ent,
    ent,
)
from ._common import DORM_SOUTH1_CY, DORM_SOUTH2_CY, ROAD_Z, _cs_offset


def _build_teleports(ENTITIES):
    teleports_start = len(ENTITIES)

    if WEST_CAMPUS_ENABLED_DORMS:
        ENTITIES.append(
            ent(
                "info_teleport_destination",
                targetname="dest_east",
                origin=f"{(DORM.x1 + DORM.x2) // 2} {(DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2} {int(DORM_RIDGE_Z + 40)}",
                angle="270",
            )
        )

        west_brushes = arch_fill(
            WORLD_X1 + WALL_T,
            WORLD_X1 + WALL_T + ARCH_SLAB_W,
            0.0,
            BRIDGE_DZ2,
            ARCH_RIN,
            A_SEGS,
            Textures.TELEPORT,
            stilt_h=ARCH_STILT_H,
        )
        ENTITIES.append(brush_ent("trigger_teleport", west_brushes, target="dest_east"))
        ENTITIES.append(brush_ent("func_illusionary", west_brushes))

        wlx1 = WORLD_X1 + WALL_T
        wlx2 = wlx1 + ARCH_SLAB_W
        west_lower = [
            box(
                wlx1, -ARCH_RIN, FLOOR_Z2, wlx2, ARCH_RIN, BRIDGE_DZ2, Textures.TELEPORT
            )
        ]
        ENTITIES.append(brush_ent("trigger_teleport", west_lower, target="dest_east"))
        ENTITIES.append(brush_ent("func_illusionary", west_lower))

    if KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "info_teleport_destination",
                targetname="dest_west",
                origin=KH_ROOFTOP_ORIGIN,
                angle="180",
            )
        )

        east_brushes = arch_fill(
            WORLD_X2_EXT - WALL_T - ARCH_SLAB_W,
            WORLD_X2_EXT - WALL_T,
            BRIDGE_EAST_SHIFT_END,
            BRIDGE_DZ2,
            ARCH_RIN,
            A_SEGS,
            Textures.TELEPORT,
            stilt_h=ARCH_STILT_H,
        )
        ENTITIES.append(brush_ent("trigger_teleport", east_brushes, target="dest_west"))
        ENTITIES.append(brush_ent("func_illusionary", east_brushes))

    elx1 = WORLD_X2_EXT - WALL_T - ARCH_SLAB_W
    elx2 = WORLD_X2_EXT - WALL_T
    east_lower_deck_x = elx1 - 64
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_east_deck",
            origin=f"{east_lower_deck_x} {int(BRIDGE_EAST_SHIFT_END)} {int(BRIDGE_DZ2 + 40)}",
            angle="180",
        )
    )
    east_lower = [
        box(
            elx1,
            BRIDGE_EAST_SHIFT_END - ARCH_RIN,
            FLOOR_Z2,
            elx2,
            BRIDGE_EAST_SHIFT_END + ARCH_RIN,
            BRIDGE_DZ2,
            Textures.TELEPORT,
        )
    ]
    ENTITIES.append(brush_ent("trigger_teleport", east_lower, target="dest_east_deck"))
    ENTITIES.append(brush_ent("func_illusionary", east_lower))

    if WEST_CAMPUS_ENABLED_DORMS:
        ENTITIES.append(
            ent(
                "info_teleport_destination",
                targetname="dest_south_dorm_roof",
                origin=f"{(DORM.x1 + DORM.x2) // 2} {(DORM_SOUTH1_Y1 + DORM_SOUTH1_Y2) // 2} {int(DORM_RIDGE_Z + SDORM_LIFT + 40)}",
                angle="90",
            )
        )
        ENTITIES.append(
            ent(
                "info_teleport_destination",
                targetname="dest_dorm_roof",
                origin=f"{(DORM.x1 + DORM.x2) // 2} {(DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2 - 100} {int(DORM_RIDGE_Z + 40)}",
                angle="270",
            )
        )

    if WEST_CAMPUS_ENABLED_DORMS:
        # Both trigger targets above land on the dorm roof, so build them
        # together with their destinations rather than leaving a
        # trigger_teleport with a dangling target.
        for arch_y1, arch_y2, trigger_y1, trigger_y2, arch_target in [
            (
                CHARLES_Y1,
                CHARLES_Y1 + CHARLES_ARCH_W,
                CHARLES_Y1 + CHARLES_ARCH_TRIG_INSET,
                CHARLES_Y1 + CHARLES_ARCH_W,
                "dest_south_dorm_roof",
            ),
            (
                CHARLES_Y2 - CHARLES_ARCH_W,
                CHARLES_Y2,
                CHARLES_Y2 - CHARLES_ARCH_W,
                CHARLES_Y2 - CHARLES_ARCH_TRIG_INSET,
                "dest_dorm_roof",
            ),
        ]:
            north_south_trigger_brushes = [
                box(
                    -CHARLES_ARCH_RIN + CHARLES_ARCH_TRIG_INSET,
                    trigger_y1,
                    FLOOR_Z2,
                    CHARLES_ARCH_RIN - CHARLES_ARCH_TRIG_INSET,
                    trigger_y2,
                    FLOOR_Z2 + CHARLES_ARCH_STILT + 128,
                    Textures.TELEPORT,
                )
            ]
            ENTITIES.append(
                brush_ent(
                    "trigger_teleport", north_south_trigger_brushes, target=arch_target
                )
            )

            north_south_glow_brushes = arch_fill_y(
                arch_y1,
                arch_y2,
                0.0,
                FLOOR_Z2 + 4,
                CHARLES_ARCH_RIN,
                A_SEGS,
                Textures.TELEPORT,
                stilt_h=CHARLES_ARCH_STILT,
            )
            ENTITIES.append(brush_ent("func_illusionary", north_south_glow_brushes))

    CHARLES_ARCH_SEGS = 24
    for arch_y1, arch_y2 in [
        (CHARLES_Y1, CHARLES_Y1 + CHARLES_ARCH_W),
        (CHARLES_Y2 - CHARLES_ARCH_W, CHARLES_Y2),
    ]:
        ENTITIES.append(
            brush_ent(
                "func_detail",
                arch_wall_y(
                    arch_y1,
                    arch_y2,
                    FLOOR_Z2,
                    CHARLES_ARCH_RIN,
                    CHARLES_ARCH_ROUT,
                    CHARLES_ARCH_SEGS,
                    Textures.PILLAR,
                    stilt_h=CHARLES_ARCH_STILT,
                ),
            )
        )

    ENNIS_ARCH_STILT = 64
    KH_DRIVE_ARCH_STILT = 64
    ARCH_TRIG_INSET = 8

    kh_drive_cx = (KNOTT_DRIVEWAY_RD_X1 + KNOTT_DRIVEWAY_RD_X2) // 2

    if KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "info_teleport_destination",
                targetname="dest_ennis_east",
                origin=KH_ROOFTOP_ORIGIN_ENNIS_EAST,
                angle="180",
            )
        )
        ENTITIES.append(
            ent(
                "info_teleport_destination",
                targetname="dest_kh_drive_south",
                origin=KH_ROOFTOP_ORIGIN_KH_DRIVE_SOUTH,
                angle="180",
            )
        )

    ennis_arch_x1 = WORLD_X2_EXT - WALL_T - ARCH_SLAB_W
    ennis_arch_x2 = WORLD_X2_EXT - WALL_T
    ennis_arch_top_z = FLOOR_Z2 + ENNIS_ARCH_STILT + ENNIS_HW
    if KNOTT_ENABLED:
        ennis_east_trigger = [
            box(
                ennis_arch_x1,
                ENNIS_Y - ENNIS_HW + ARCH_TRIG_INSET,
                FLOOR_Z2 + 4,
                ennis_arch_x2,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - ARCH_TRIG_INSET,
                ennis_arch_top_z,
                Textures.TELEPORT,
            )
        ]
        ENTITIES.append(
            brush_ent(
                "trigger_teleport", ennis_east_trigger, target="dest_kh_drive_south"
            )
        )
        ennis_east_glow = arch_fill(
            ennis_arch_x1,
            ennis_arch_x2,
            float(ENNIS_Y),
            FLOOR_Z2,
            ENNIS_HW,
            A_SEGS,
            Textures.TELEPORT,
            stilt_h=ENNIS_ARCH_STILT,
        )
        ENTITIES.append(brush_ent("func_illusionary", ennis_east_glow))

    ENNIS_ARCH_ROUT = ENNIS_HW + 56
    ennis_stone_arch = arch_wall(
        ennis_arch_x1,
        ennis_arch_x2,
        ENNIS_Y - ENNIS_ARCH_ROUT,
        ENNIS_Y + ENNIS_ARCH_ROUT,
        FLOOR_Z2,
        ennis_arch_top_z,
        ENNIS_HW,
        ENNIS_ARCH_ROUT,
        A_SEGS,
        Textures.PILLAR,
        stilt_h=ENNIS_ARCH_STILT,
        yc=float(ENNIS_Y),
        freestanding=True,
    )
    ENTITIES.append(brush_ent("func_detail", ennis_stone_arch))

    kh_arch_y1 = CHARLES_Y1
    kh_arch_y2 = CHARLES_Y1 + ARCH_SLAB_W
    kh_arch_top_z = KNOTT_DRIVEWAY_ZT_S + KH_DRIVE_ARCH_STILT + KNOTT.driveway_hw
    if KNOTT_ENABLED:
        kh_drive_trigger = [
            box(
                kh_drive_cx - KNOTT.driveway_hw + ARCH_TRIG_INSET,
                kh_arch_y1,
                KNOTT_DRIVEWAY_ZT_S + 4,
                kh_drive_cx + KNOTT.driveway_hw - ARCH_TRIG_INSET,
                kh_arch_y2,
                kh_arch_top_z,
                Textures.TELEPORT,
            )
        ]
        ENTITIES.append(
            brush_ent("trigger_teleport", kh_drive_trigger, target="dest_ennis_east")
        )
        kh_drive_glow = arch_fill_y(
            kh_arch_y1,
            kh_arch_y2,
            float(kh_drive_cx),
            KNOTT_DRIVEWAY_ZT_S,
            KNOTT.driveway_hw,
            A_SEGS,
            Textures.TELEPORT,
            stilt_h=KH_DRIVE_ARCH_STILT,
        )
        ENTITIES.append(brush_ent("func_illusionary", kh_drive_glow))

    KH_ARCH_ROUT = KNOTT.driveway_hw + 56
    kh_stone_arch = arch_wall_y(
        kh_arch_y1,
        kh_arch_y2,
        KNOTT_DRIVEWAY_ZT_S,
        KNOTT.driveway_hw,
        KH_ARCH_ROUT,
        A_SEGS,
        Textures.PILLAR,
        stilt_h=KH_DRIVE_ARCH_STILT,
        xc=float(kh_drive_cx),
    )
    ENTITIES.append(brush_ent("func_detail", kh_stone_arch))

    if not ENTITIES_ENABLED_TELEPORTS:
        del ENTITIES[teleports_start:]


def _build_player_start(ENTITIES):
    spawn_x = -180
    spawn_y = 1992
    spawn_z = 26
    ENTITIES.append(
        ent(
            "info_player_start",
            origin=f"{spawn_x} {spawn_y} {spawn_z}",
            angle="270",
        )
    )

    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_start",
            origin=f"{spawn_x} {spawn_y + 24} {spawn_z}",
            angle="270",
        )
    )


def _build_dm_spawns(ENTITIES):
    if ENTITIES_ENABLED_DM_SPAWNS:
        spawn_points = [
            ((0, *_cs_offset(0, 0, int(deck_top_z(0) + 32))), 180),
            ((-200, *_cs_offset(-200, 0, int(deck_top_z(-200) + 32))), 90),
            ((200, *_cs_offset(200, 0, int(deck_top_z(200) + 32))), 270),
            ((-400, *_cs_offset(-400, 0, int(deck_top_z(-400) + 32))), 90),
            ((400, *_cs_offset(400, 0, int(deck_top_z(400) + 32))), 270),
            ((0, 300, ROAD_Z + 24), 180),
            ((0, -400, ROAD_Z + 24), 0),
            ((0, DORM_SOUTH1_CY, ROAD_Z + 24), 270),
            ((800, 0, ROAD_Z + 24), 270),
            ((-800, 0, ROAD_Z + 24), 90),
        ]
        if WEST_CAMPUS_ENABLED_DORMS:
            # These sit inside/on the dorm building, so only add them when
            # that geometry actually exists — otherwise they float in air.
            spawn_points += [
                ((DORM_CX, DORM_NORTH_CY, FLOOR_Z2 + 40), 90),
                ((DORM_CX, DORM_NORTH_CY, FLOOR_Z2 + DORM.floor_h + 40), 90),
                ((DORM_CX, DORM_NORTH_CY + 150, int(DORM_RIDGE_Z + 40)), 90),
                ((DORM_CX, DORM_SOUTH1_CY, FLOOR_Z2 + SDORM_LIFT + 40), 90),
                ((DORM_CX, DORM_SOUTH2_CY, FLOOR_Z2 + SDORM_LIFT + 40), 90),
            ]
        for pos, angle in spawn_points:
            ENTITIES.append(
                ent(
                    "info_player_deathmatch",
                    origin=f"{pos[0]} {pos[1]} {pos[2]}",
                    angle=str(angle),
                )
            )
