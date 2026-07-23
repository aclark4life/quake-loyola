import random

from .constants import (
    A_SEGS,
    ARCH_RIN,
    ARCH_SLAB_W,
    ARCH_STILT_H,
    BRIDGE,
    BRIDGE_ARCH_X,
    BRIDGE_CENTER_SPAN_OFFSET,
    BRIDGE_DZ2,
    BRIDGE_EAST_SHIFT_END,
    BRIDGE_ENABLED_PIER_BASE_LIGHTS,
    BRIDGE_ENABLED_SUPPORTS,
    BRIDGE_PEND_XS,
    BRIDGE_PILLAR_BASE_H,
    BRIDGE_PILLAR_BASE_RAMP_H,
    BRIDGE_PILLAR_HW,
    CHARLES_ARCH_RIN,
    CHARLES_ARCH_ROUT,
    CHARLES_ARCH_STILT,
    CHARLES_ARCH_W,
    CHARLES_WALK_W,
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
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    ENNIS_CEMENT_X1,
    ENNIS_CEMENT_X2,
    ENNIS_GATE_X1,
    ENNIS_HW,
    ENNIS_WALL_NY,
    ENNIS_WALL_T,
    ENNIS_WIDEN_N,
    ENNIS_Y,
    ENTITIES_ENABLED_AMMO,
    ENTITIES_ENABLED_DM_SPAWNS,
    ENTITIES_ENABLED_EXIT,
    ENTITIES_ENABLED_HEALTH,
    ENTITIES_ENABLED_MONSTERS,
    ENTITIES_ENABLED_PLATFORM,
    ENTITIES_ENABLED_TELEPORTS,
    ENTITIES_ENABLED_VEGETATION,
    ENTITIES_ENABLED_WEAPONS,
    FLOOR_Z2,
    INDENT,
    KH_ROOFTOP_ORIGIN,
    KH_ROOFTOP_ORIGIN_ENNIS_EAST,
    KH_ROOFTOP_ORIGIN_KH_DRIVE_SOUTH,
    KNOTT,
    KNOTT_BIY1,
    KNOTT_BIY2,
    KNOTT_CX,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_EAST_ROOM_CX,
    KNOTT_ENABLED_INTERIOR,
    KNOTT_ENABLED_MONSTERS,
    KNOTT_ENABLED_WALKWAY,
    KNOTT_ENT_X1,
    KNOTT_ENT_X2,
    KNOTT_GROUND_Z,
    KNOTT_ORIG_CX,
    KNOTT_ROOM_SPLITS,
    KNOTT_SHAFT_X1,
    KNOTT_SHAFT_X2,
    KNOTT_SHAFT_Y1,
    KNOTT_SHAFT_Y2,
    KNOTT_SHELF_D,
    KNOTT_SHELF_H,
    KNOTT_SHELF_W,
    KNOTT_STAIRS_MID_Y,
    KNOTT_STAIRS_X1,
    KNOTT_STAIRS_X2,
    KNOTT_STAIRS_Y1,
    KNOTT_STAIRS_Y2,
    KNOTT_WEST_ROOM_CX,
    KNOTT_Z2,
    ROAD_X1,
    ROAD_X2,
    SDORM_LIFT,
    STREET_DIV_HW,
    WALK_X1,
    WALK_X2,
    WALK_ZT1,
    WALK_ZT2,
    WALL_T,
    WORLD_X1,
    WORLD_X2,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    Textures,
    deck_bot_z,
    deck_top_z,
)
from .geometry import (
    arch_fill,
    arch_fill_y,
    arch_wall,
    arch_wall_y,
    box,
    brush_ent,
    ent,
    make_bush,
    make_giant_tree,
    make_pixel_tree,
    render_text_flat,
    render_text_flat_x,
)


def build():
    """Build gameplay entities, lights, teleports, and movers."""
    BRUSHES = []
    ENTITIES = []
    ROAD_Z = FLOOR_Z2 + 8

    # Bridge-deck entities follow the shared center-span Y/Z offset.
    BRIDGE_X_MIN, BRIDGE_X_MAX = min(BRIDGE_ARCH_X), max(BRIDGE_ARCH_X)
    CS_X1, CS_X2 = BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]
    CS_DY, CS_DZ = BRIDGE_CENTER_SPAN_OFFSET[1], BRIDGE_CENTER_SPAN_OFFSET[2]

    def _cs_offset(x, y, z):
        if BRIDGE_X_MIN <= x <= BRIDGE_X_MAX:
            return y + CS_DY, z + CS_DZ
        return y, z

    knott_entity_start = len(ENTITIES)
    room_goodies = [
        "item_health",
        "weapon_supershotgun",
        "item_shells",
        "item_rockets",
        "weapon_nailgun",
        "item_spikes",
        "weapon_grenadelauncher",
        "item_health",
        "item_shells",
        "item_rockets",
        "item_health",
        "weapon_supershotgun",
        "item_spikes",
        "item_shells",
        "weapon_nailgun",
        "item_rockets",
        "item_health",
        "weapon_grenadelauncher",
        "item_shells",
        "item_spikes",
    ]
    gi = 0
    for floor_index in range(KNOTT.floors):
        fz1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
        item_z = fz1 + KNOTT.wall_t + 24
        light_z = fz1 + KNOTT.floor_h - 24
        split = KNOTT_ROOM_SPLITS[floor_index]
        sr_yc = (KNOTT_BIY1 + split) // 2
        nr_yc = (split + KNOTT.wall_t + KNOTT_BIY2) // 2
        for side_xc in [KNOTT_WEST_ROOM_CX, KNOTT_EAST_ROOM_CX]:
            for ryc in [sr_yc, nr_yc]:
                safe_ryc = ryc
                if (
                    side_xc == KNOTT_WEST_ROOM_CX
                    and ryc == nr_yc
                    and nr_yc > KNOTT_STAIRS_Y1 - 64
                ):
                    safe_ryc = KNOTT_STAIRS_Y1 - 80
                ENTITIES.append(
                    ent("light", origin=f"{side_xc} {safe_ryc} {light_z}", light="250")
                )

                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{side_xc} {safe_ryc} {fz1 + KNOTT.floor_h // 2}",
                        light="150",
                    )
                )
                ENTITIES.append(
                    ent(
                        room_goodies[gi % len(room_goodies)],
                        origin=f"{side_xc - 40} {safe_ryc} {item_z}",
                    )
                )
                gi += 1
                ENTITIES.append(
                    ent(
                        room_goodies[gi % len(room_goodies)],
                        origin=f"{side_xc + 40} {safe_ryc} {item_z}",
                    )
                )
                gi += 1

    west_stair_center_x = (KNOTT_STAIRS_X1 + KNOTT_STAIRS_X2) // 2
    west_stair_north_y = (KNOTT_STAIRS_MID_Y + KNOTT_STAIRS_Y2) // 2
    west_stair_south_y = (KNOTT_STAIRS_Y1 + KNOTT_STAIRS_MID_Y) // 2
    for floor_index in range(KNOTT.floors):
        west_stair_light_z = (
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h - 24
        )
        west_stair_mid_z = (
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h // 2
        )
        west_stair_low_z = (
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h // 4
        )
        for lz in [west_stair_light_z, west_stair_mid_z, west_stair_low_z]:
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{west_stair_center_x} {west_stair_north_y} {lz}",
                    light="220",
                )
            )

            if lz != west_stair_light_z:
                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{west_stair_center_x} {west_stair_south_y} {lz}",
                        light="220",
                    )
                )

    hall_center_x = (KNOTT_ENT_X1 + KNOTT_ENT_X2) // 2
    hall_light_ys = [
        KNOTT_BIY1 + (KNOTT_BIY2 - KNOTT_BIY1) * i // 4 for i in range(1, 4)
    ] + [
        KNOTT_BIY1 + (KNOTT_BIY2 - KNOTT_BIY1) // 8,
        KNOTT_BIY1 + (KNOTT_BIY2 - KNOTT_BIY1) * 7 // 8,
    ]
    for floor_index in range(KNOTT.floors):
        hall_light_z = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h - 24
        for hall_y in hall_light_ys:
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{hall_center_x} {hall_y} {hall_light_z}",
                    light="200",
                )
            )

    entry_corridor_y = KNOTT.y2 - 48
    for floor_index in range(KNOTT.floors):
        entry_corridor_light_z = (
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h - 24
        )
        ENTITIES.append(
            ent(
                "light",
                origin=f"{hall_center_x} {entry_corridor_y} {entry_corridor_light_z}",
                light="220",
            )
        )

    nw_cut_cx = KNOTT.x1 + INDENT
    nw_cut_cy = (KNOTT.y2 - INDENT + KNOTT.y2) // 2
    ne_cut_cx = (KNOTT.x2 - INDENT + KNOTT.x2) // 2
    sw_cut_cx = (KNOTT.x1 + KNOTT.x1 + INDENT) // 2
    sw_cut_cy = (KNOTT.y1 + KNOTT.y1 + INDENT) // 2
    se_cut_cx = (KNOTT.x2 - INDENT + KNOTT.x2) // 2
    for floor_index in range(KNOTT.floors):
        cut_z = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h - 24
        for cx, cy in [
            (nw_cut_cx, nw_cut_cy),
            (ne_cut_cx, nw_cut_cy),
            (sw_cut_cx, sw_cut_cy),
            (se_cut_cx, sw_cut_cy),
        ]:
            ENTITIES.append(ent("light", origin=f"{cx} {cy} {cut_z}", light="200"))

    east_fill_x = (KNOTT_SHAFT_X2 + KNOTT.x2 - KNOTT.wall_t) // 2
    for floor_index in range(KNOTT.floors):
        fz1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
        east_fill_z = fz1 + KNOTT.floor_h - 24
        split = KNOTT_ROOM_SPLITS[floor_index]
        for ryc in [
            (KNOTT_BIY1 + split) // 2,
            (split + KNOTT.wall_t + KNOTT_BIY2) // 2,
        ]:
            ENTITIES.append(
                ent("light", origin=f"{east_fill_x} {ryc} {east_fill_z}", light="200")
            )

    south_fill_y = KNOTT_BIY1 + 64
    for floor_index in range(KNOTT.floors):
        fz1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
        south_fill_z = fz1 + KNOTT.floor_h - 24
        for xc in [KNOTT_WEST_ROOM_CX, hall_center_x, KNOTT_EAST_ROOM_CX]:
            ENTITIES.append(
                ent("light", origin=f"{xc} {south_fill_y} {south_fill_z}", light="180")
            )

    for floor_index in range(KNOTT.floors):
        fz1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
        fz_surf = fz1 + KNOTT.wall_t
        split = KNOTT_ROOM_SPLITS[floor_index]

        for shelf_center_x in [KNOTT_WEST_ROOM_CX, KNOTT_EAST_ROOM_CX]:
            shelf_x = shelf_center_x
            ENTITIES.append(
                brush_ent(
                    "func_detail",
                    [
                        box(
                            shelf_x - KNOTT_SHELF_W // 2,
                            KNOTT_BIY1,
                            fz_surf,
                            shelf_x + KNOTT_SHELF_W // 2,
                            KNOTT_BIY1 + KNOTT_SHELF_D,
                            fz_surf + KNOTT_SHELF_H,
                            Textures.SHELF,
                        )
                    ],
                )
            )
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{shelf_x} {KNOTT_BIY1 + 32} {fz_surf + KNOTT_SHELF_H + 24}",
                    light="180",
                )
            )

    if not KNOTT_ENABLED_INTERIOR:
        del ENTITIES[knott_entity_start:]

    teleports_start = len(ENTITIES)

    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_east",
            origin=f"{(DORM.x1 + DORM.x2) // 2} {(DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2} {int(DORM_RIDGE_Z + 40)}",
            angle="270",
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_west",
            origin=KH_ROOFTOP_ORIGIN,
            angle="180",
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
        box(wlx1, -ARCH_RIN, FLOOR_Z2, wlx2, ARCH_RIN, BRIDGE_DZ2, Textures.TELEPORT)
    ]
    ENTITIES.append(brush_ent("trigger_teleport", west_lower, target="dest_east"))
    ENTITIES.append(brush_ent("func_illusionary", west_lower))

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

    CHARLES_ARCH_TRIG_INSET = 8

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
        brush_ent("trigger_teleport", ennis_east_trigger, target="dest_kh_drive_south")
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

    knott_cy = (KNOTT.y1 + KNOTT.y2) // 2
    DORM_SOUTH1_CY = (DORM_SOUTH1_Y1 + DORM_SOUTH1_Y2) // 2
    DORM_SOUTH2_CY = (DORM_SOUTH2_Y1 + DORM_SOUTH2_Y2) // 2

    if ENTITIES_ENABLED_DM_SPAWNS:
        for pos, angle in [
            ((0, *_cs_offset(0, 0, int(deck_top_z(0) + 32))), 180),
            ((-200, *_cs_offset(-200, 0, int(deck_top_z(-200) + 32))), 90),
            ((200, *_cs_offset(200, 0, int(deck_top_z(200) + 32))), 270),
            ((-400, *_cs_offset(-400, 0, int(deck_top_z(-400) + 32))), 90),
            ((400, *_cs_offset(400, 0, int(deck_top_z(400) + 32))), 270),
            *(
                [
                    (
                        (
                            (WALK_X1 + WALK_X2) // 2,
                            (BRIDGE.y1 + KNOTT.y2) // 2,
                            int((WALK_ZT1 + WALK_ZT2) // 2 + 32),
                        ),
                        180,
                    )
                ]
                if KNOTT_ENABLED_INTERIOR
                else []
            ),
            *(
                [
                    (
                        (
                            (KNOTT_ENT_X1 + KNOTT_ENT_X2) // 2,
                            KNOTT.y2 - 80,
                            KNOTT_GROUND_Z + 40,
                        ),
                        180,
                    ),
                    (
                        (KNOTT_CX - 100, knott_cy, KNOTT_GROUND_Z + KNOTT.floor_h + 40),
                        270,
                    ),
                    (
                        (
                            KNOTT_CX + 100,
                            knott_cy,
                            KNOTT_GROUND_Z + KNOTT.floor_h * 2 + 40,
                        ),
                        90,
                    ),
                    (
                        (
                            KNOTT_CX,
                            KNOTT.y1 + 100,
                            KNOTT_GROUND_Z + KNOTT.floor_h * 3 + 40,
                        ),
                        0,
                    ),
                    (
                        (KNOTT_CX, knott_cy, KNOTT_GROUND_Z + KNOTT.floor_h * 4 + 40),
                        180,
                    ),
                    ((KNOTT_CX, knott_cy, KNOTT_Z2 + 40), 180),
                ]
                if KNOTT_ENABLED_INTERIOR
                else []
            ),
            ((0, 300, ROAD_Z + 24), 180),
            ((0, -400, ROAD_Z + 24), 0),
            ((0, DORM_SOUTH1_CY, ROAD_Z + 24), 270),
            ((DORM_CX, DORM_NORTH_CY, FLOOR_Z2 + 40), 90),
            ((DORM_CX, DORM_NORTH_CY, FLOOR_Z2 + DORM.floor_h + 40), 90),
            ((DORM_CX, DORM_NORTH_CY + 150, int(DORM_RIDGE_Z + 40)), 90),
            ((DORM_CX, DORM_SOUTH1_CY, FLOOR_Z2 + SDORM_LIFT + 40), 90),
            ((DORM_CX, DORM_SOUTH2_CY, FLOOR_Z2 + SDORM_LIFT + 40), 90),
            ((800, 0, ROAD_Z + 24), 270),
            ((-800, 0, ROAD_Z + 24), 90),
        ]:
            ENTITIES.append(
                ent(
                    "info_player_deathmatch",
                    origin=f"{pos[0]} {pos[1]} {pos[2]}",
                    angle=str(angle),
                )
            )

    weapons_start = len(ENTITIES)

    _rl_y, _rl_z = _cs_offset(0, 0, int(deck_top_z(0) + 8))
    ENTITIES.append(ent("weapon_rocketlauncher", origin=f"0 {_rl_y} {_rl_z}"))

    if KNOTT_ENABLED_INTERIOR:
        ENTITIES.append(
            ent(
                "weapon_rocketlauncher",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 3 + 40}",
            )
        )

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

    if KNOTT_ENABLED_INTERIOR:
        ENTITIES.append(
            ent(
                "weapon_supershotgun",
                origin=f"{KNOTT_EAST_ROOM_CX} {KNOTT.y2 - 80} {KNOTT_GROUND_Z + 40}",
            )
        )
    ENTITIES.append(ent("weapon_supershotgun", origin=f"300 300 {ROAD_Z + 24}"))
    ENTITIES.append(
        ent(
            "weapon_supershotgun",
            origin=f"{DORM_CX} {DORM_SOUTH1_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
        )
    )

    if KNOTT_ENABLED_INTERIOR:
        ENTITIES.append(
            ent(
                "weapon_grenadelauncher",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 2 + 40}",
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
    if KNOTT_ENABLED_INTERIOR:
        ENTITIES.append(
            ent(
                "weapon_nailgun",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h + 40}",
            )
        )

    _lg_y, _lg_z = _cs_offset(200, 0, int(deck_top_z(200) + 8))
    ENTITIES.append(ent("weapon_lightning", origin=f"200 {_lg_y} {_lg_z}"))
    if KNOTT_ENABLED_INTERIOR:
        ENTITIES.append(
            ent(
                "weapon_lightning",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 4 + 40}",
            )
        )
    ENTITIES.append(ent("weapon_lightning", origin=f"0 -500 {ROAD_Z + 24}"))

    if not ENTITIES_ENABLED_WEAPONS:
        del ENTITIES[weapons_start:]

    monsters_start = len(ENTITIES)

    _og1_y, _og1_z = _cs_offset(-300, 0, int(deck_top_z(-300) + 8))
    _og2_y, _og2_z = _cs_offset(300, 0, int(deck_top_z(300) + 8))
    ENTITIES.append(ent("monster_ogre", origin=f"-300 {_og1_y} {_og1_z}", angle="90"))
    ENTITIES.append(ent("monster_ogre", origin=f"300 {_og2_y} {_og2_z}", angle="270"))

    ENTITIES.append(ent("monster_ogre", origin=f"0 200 {ROAD_Z + 24}", angle="180"))
    ENTITIES.append(ent("monster_ogre", origin=f"0 -600 {ROAD_Z + 24}", angle="0"))

    ENTITIES.append(ent("monster_ogre", origin=f"700 0 {ROAD_Z + 24}", angle="270"))

    ENTITIES.append(ent("monster_ogre", origin=f"-700 0 {ROAD_Z + 24}", angle="90"))

    ENTITIES.append(
        ent(
            "monster_ogre",
            origin=f"{DORM_CX} {DORM_SOUTH1_CY + 150} {int(DORM_RIDGE_Z + SDORM_LIFT + 40)}",
            angle="90",
        )
    )

    if KNOTT_ENABLED_INTERIOR and KNOTT_ENABLED_MONSTERS:
        ENTITIES.append(
            ent(
                "monster_ogre",
                origin=f"{KNOTT_WEST_ROOM_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 2 + 40}",
                angle="90",
            )
        )
        ENTITIES.append(
            ent(
                "monster_ogre",
                origin=f"{KNOTT_EAST_ROOM_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 3 + 40}",
                angle="270",
            )
        )

        ENTITIES.append(
            ent(
                "monster_ogre",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_Z2 + 40}",
                angle="180",
            )
        )

    if not ENTITIES_ENABLED_MONSTERS:
        del ENTITIES[monsters_start:]
    ammo_start = len(ENTITIES)
    for ax in BRIDGE_ARCH_X:
        ENTITIES.append(ent("item_rockets", origin=f"{ax} 0 {int(deck_top_z(ax) + 8)}"))
    for rx in [400, 800]:
        ENTITIES.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z + 24}"))
        ENTITIES.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z + 24}"))
    if KNOTT_ENABLED_INTERIOR:
        for kf in range(1, KNOTT.floors):
            ENTITIES.append(
                ent(
                    "item_rockets",
                    origin=f"{KNOTT_CX + 80} {knott_cy} {KNOTT_GROUND_Z + kf * KNOTT.floor_h + 40}",
                )
            )
    ENTITIES.append(ent("item_shells", origin=f"-300 -300 {ROAD_Z + 24}"))
    ENTITIES.append(
        ent("item_shells", origin=f"{DORM_CX} {DORM_NORTH_CY} {FLOOR_Z2 + 40}")
    )
    ENTITIES.append(ent("item_spikes", origin=f"-400 200 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_spikes", origin=f"400 -200 {ROAD_Z + 24}"))

    if not ENTITIES_ENABLED_AMMO:
        del ENTITIES[ammo_start:]

    health_start = len(ENTITIES)

    _hp_y, _hp_z = _cs_offset(-100, 0, int(deck_top_z(-100) + 8))
    ENTITIES.append(ent("item_health", origin=f"-100 {_hp_y} {_hp_z}"))
    if KNOTT_ENABLED_INTERIOR:
        ENTITIES.append(
            ent(
                "item_health",
                origin=f"{KNOTT_EAST_ROOM_CX} {KNOTT.y2 - 64} {KNOTT_GROUND_Z + 40}",
            )
        )
        ENTITIES.append(
            ent(
                "item_health",
                origin=f"{KNOTT_CX - 100} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 2 + 40}",
            )
        )
    ENTITIES.append(ent("item_health", origin=f"-300 400 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_health", origin=f"300 -600 {ROAD_Z + 24}"))
    ENTITIES.append(
        ent(
            "item_health",
            origin=f"{DORM_CX} {DORM_SOUTH2_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
        )
    )

    _arm_y, _arm_z = _cs_offset(-200, 0, int(deck_top_z(-200) + 8))
    ENTITIES.append(ent("item_armor1", origin=f"-200 {_arm_y} {_arm_z}"))
    if KNOTT_ENABLED_INTERIOR:
        ENTITIES.append(
            ent(
                "item_armor2",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 4 + 40}",
            )
        )
    ENTITIES.append(
        ent(
            "item_armorInv",
            origin=f"{DORM_CX} {DORM_NORTH_CY} {int(DORM_RIDGE_Z + 40)}",
        )
    )

    if not ENTITIES_ENABLED_HEALTH:
        del ENTITIES[health_start:]

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
                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{px} {underbridge_light_y} 16",
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

    if KNOTT_ENABLED_INTERIOR:
        lift_travel = KNOTT_Z2 - (KNOTT_GROUND_Z + KNOTT.wall_t)
        lift_brush = [
            box(
                KNOTT_SHAFT_X1 + 2,
                KNOTT_SHAFT_Y1 + 2,
                KNOTT_Z2 - 8,
                KNOTT_SHAFT_X2 - 2,
                KNOTT_SHAFT_Y2 - 2,
                KNOTT_Z2,
                Textures.FLOOR_KH,
            )
        ]
        ENTITIES.append(
            brush_ent("func_plat", lift_brush, height=str(lift_travel), speed="200")
        )

    _dorm_north2_y2 = DORM_NORTH_Y1
    _dorm_north2_y1 = _dorm_north2_y2 - (DORM_NORTH_Y2 - DORM_NORTH_Y1)
    bldg_light_xs = [DORM.x1 + (DORM.x2 - DORM.x1) * i // 4 for i in [1, 2, 3]]
    for building_y1, building_y2, building_lift in [
        (DORM_NORTH_Y1, DORM_NORTH_Y2, 0),
        (_dorm_north2_y1, _dorm_north2_y2, 0),
        (DORM_SOUTH1_Y1, DORM_SOUTH1_Y2, SDORM_LIFT),
        (DORM_SOUTH2_Y1, DORM_SOUTH2_Y2, SDORM_LIFT),
    ]:
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

    if KNOTT_ENABLED_INTERIOR:
        for knott_floor_index in range(KNOTT.floors):
            knott_light_z = (
                KNOTT_GROUND_Z + knott_floor_index * KNOTT.floor_h + KNOTT.floor_h // 2
            )
            for knott_x_index in [1, 2, 3]:
                knott_light_x = KNOTT.x1 + (KNOTT.x2 - KNOTT.x1) * knott_x_index // 4
                for knott_y_index in [1, 2, 3, 4]:
                    knott_light_y = (
                        KNOTT.y1 + (KNOTT.y2 - KNOTT.y1) * knott_y_index // 5
                    )
                    ENTITIES.append(
                        ent(
                            "light",
                            origin=f"{knott_light_x} {knott_light_y} {knott_light_z}",
                            light="150",
                        )
                    )

    vegetation_start = len(ENTITIES)

    _tree_cx = KNOTT.x1 - 200
    _tree_cy = (KNOTT.y1 + KNOTT.y2) // 2
    all_tree_brushes = make_pixel_tree(
        _tree_cx,
        _tree_cy,
        FLOOR_Z2,
        profile="large",
        vox_size=8,
        trunk_solid=True,
        ring_segs=12,
    )
    ENTITIES.append(brush_ent("func_detail", all_tree_brushes))

    for _lx, _ly, _lz, _intensity in [
        (_tree_cx, _tree_cy, FLOOR_Z2 + 24, 150),
        (_tree_cx - 96, _tree_cy, FLOOR_Z2 + 180, 200),
        (_tree_cx + 96, _tree_cy, FLOOR_Z2 + 180, 200),
    ]:
        ENTITIES.append(
            ent("light", origin=f"{_lx} {_ly} {_lz}", light=str(_intensity))
        )

    charles_tree_height = int(KNOTT_Z2 * 0.65)
    knott_tree_span = KNOTT.y2 - KNOTT.y1
    charles_tree_row_near_x = ROAD_X2 + CHARLES_WALK_W + 300
    charles_tree_row_far_x = ROAD_X2 + CHARLES_WALK_W + 560

    charles_tree_row2_ys = [int(KNOTT.y1 + knott_tree_span * f) for f in (0.25, 0.75)]

    charles_tree_row3_ys = [int(KNOTT.y1 + knott_tree_span * f) for f in (0.15, 0.85)]
    charles_giant_tree_brushes = []
    for tree_y in charles_tree_row2_ys:
        charles_giant_tree_brushes += make_giant_tree(
            charles_tree_row_near_x, tree_y, FLOOR_Z2, charles_tree_height
        )
    for tree_y in charles_tree_row3_ys:
        charles_giant_tree_brushes += make_giant_tree(
            charles_tree_row_far_x, tree_y, FLOOR_Z2, charles_tree_height
        )
    ENTITIES.append(brush_ent("func_detail", charles_giant_tree_brushes))

    kh_tree_rng = random.Random(7)
    kh_drive_tree_x = KNOTT_DRIVEWAY_ES_X2 + 80
    kh_drive_tree_spacing = 300
    kh_drive_tree_height = int(KNOTT_Z2 * 0.65)
    kh_drive_tree_brushes = []
    kh_grid_y = BRIDGE.y1 - kh_drive_tree_spacing
    while kh_grid_y >= KNOTT_DRIVEWAY_Y1:
        tree_x = kh_drive_tree_x + kh_tree_rng.randint(-40, 40)
        tree_y = kh_grid_y + kh_tree_rng.randint(-80, 80)
        tree_h = kh_drive_tree_height + kh_tree_rng.randint(-60, 60)
        if tree_y >= KNOTT_DRIVEWAY_Y2:
            tree_z = FLOOR_Z2
        else:
            kh_t = (KNOTT_DRIVEWAY_Y2 - tree_y) / (
                KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1
            )
            tree_z = int(
                KNOTT_DRIVEWAY_ZT_N + kh_t * (KNOTT_DRIVEWAY_ZT_S - KNOTT_DRIVEWAY_ZT_N)
            )
        kh_drive_tree_brushes += make_giant_tree(tree_x, tree_y, tree_z, tree_h)
        kh_grid_y -= kh_drive_tree_spacing
    ENTITIES.append(brush_ent("func_detail", kh_drive_tree_brushes))

    sdorm_front_tree_height = 520
    sdorm_front_tree_x = ROAD_X1 - 400
    sdorm_front_tree_y1 = DORM_SOUTH1_Y1 + 150
    sdorm_front_tree_y2 = DORM_SOUTH2_Y2 - 150
    sdorm_front_tree_brushes = []
    for tree_y in (sdorm_front_tree_y1, sdorm_front_tree_y2):
        sdorm_front_tree_brushes += make_giant_tree(
            sdorm_front_tree_x, tree_y, FLOOR_Z2, sdorm_front_tree_height
        )
    ENTITIES.append(brush_ent("func_detail", sdorm_front_tree_brushes))

    east_ground_tree_height = int(KNOTT_Z2 * 0.65)
    east_ground_spacing = 350
    east_ground_jitter = 120
    east_ground_buffer = 120
    east_ground_x1 = ROAD_X2 + CHARLES_WALK_W + east_ground_buffer
    east_ground_x2 = WORLD_X2_EXT - WALL_T - east_ground_buffer
    east_ground_y1 = ENNIS_WALL_NY + ENNIS_WALL_T + 200
    east_ground_y2 = WORLD_Y2 - WALL_T - east_ground_buffer

    tree_rng = random.Random(42)

    east_ground_giant_brushes = []
    grid_x = east_ground_x1
    while grid_x <= east_ground_x2:
        grid_y = east_ground_y1
        while grid_y <= east_ground_y2:
            tree_x = grid_x + tree_rng.randint(-east_ground_jitter, east_ground_jitter)
            tree_y = grid_y + tree_rng.randint(-east_ground_jitter, east_ground_jitter)
            tree_x = max(east_ground_x1, min(east_ground_x2, tree_x))
            tree_y = max(east_ground_y1, min(east_ground_y2, tree_y))
            east_ground_giant_brushes += make_giant_tree(
                tree_x, tree_y, FLOOR_Z2, east_ground_tree_height
            )
            grid_y += east_ground_spacing
        grid_x += east_ground_spacing
    ENTITIES.append(brush_ent("func_detail", east_ground_giant_brushes))

    east_side_tree_height = int(KNOTT_Z2 * 0.65)
    east_side_foliage_hw = 160
    _ennis_south = ENNIS_Y - ENNIS_HW
    _ennis_sw_edge = _ennis_south - 3 * CHARLES_WALK_W - 32
    east_tele_brushes = []
    et_rng = random.Random(43)
    et_x1 = WORLD_X2 + WALL_T + east_side_foliage_hw + 20
    et_x2 = WORLD_X2_EXT - WALL_T - east_side_foliage_hw
    et_y1 = WORLD_Y1 + WALL_T + 120
    et_y2 = _ennis_sw_edge - east_side_foliage_hw
    et_min_dist = 280
    et_placed = []
    for _ in range(300):
        cx = et_rng.randint(et_x1, et_x2)
        cy = et_rng.randint(et_y1, et_y2)
        if all(
            (cx - px) ** 2 + (cy - py) ** 2 >= et_min_dist**2 for px, py in et_placed
        ):
            et_placed.append((cx, cy))

    for target in ((3349, -195), (3215, -461)):
        et_placed.sort(key=lambda p, t=target: (p[0] - t[0]) ** 2 + (p[1] - t[1]) ** 2)
        et_placed = et_placed[1:]
    for cx, cy in et_placed:
        east_tele_brushes += make_giant_tree(cx, cy, FLOOR_Z2, east_side_tree_height)
    ENTITIES.append(brush_ent("func_detail", east_tele_brushes))

    bush_positions = [
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 60, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 160, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 260, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 360, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 120), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 300), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 500), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 700), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 120), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 320), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 560), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2 - 200),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2 + 200),
        (DORM.x2 + 48, -200),
        (DORM.x2 + 48, 200),
        (DORM.x2 + 48, 500),
    ]
    all_bush_brushes = []
    for bush_x, bush_y in bush_positions:
        all_bush_brushes += make_bush(bush_x, bush_y, FLOOR_Z2)

    knott_verge_y = ENNIS_Y - ENNIS_HW - 100
    knott_bush_spacing = 120
    knott_bush_buffer = 60
    knott_bush_size = 40
    knott_bush_jitter_x = 40
    knott_bush_jitter_y = 30
    knott_verge_brushes = []
    for verge_x1, verge_x2 in [
        (
            ROAD_X2 + CHARLES_WALK_W + knott_bush_buffer,
            KNOTT_ORIG_CX - 64 - knott_bush_buffer,
        ),
        (
            KNOTT_ORIG_CX + 64 + knott_bush_buffer,
            KNOTT_DRIVEWAY_CORRIDOR_X1 - knott_bush_buffer,
        ),
    ]:
        bush_x = verge_x1
        while bush_x <= verge_x2:
            jittered_x = bush_x + tree_rng.randint(
                -knott_bush_jitter_x, knott_bush_jitter_x
            )
            jittered_y = knott_verge_y + tree_rng.randint(
                -knott_bush_jitter_y, knott_bush_jitter_y
            )
            knott_verge_brushes += make_bush(
                jittered_x, jittered_y, FLOOR_Z2, size=knott_bush_size
            )
            bush_x += knott_bush_spacing
    all_bush_brushes += knott_verge_brushes

    ENTITIES.append(brush_ent("func_detail", all_bush_brushes))

    if not ENTITIES_ENABLED_VEGETATION:
        del ENTITIES[vegetation_start:]

    platform_start = len(ENTITIES)

    CHARLES_PLT_W = 128
    CHARLES_PLT_H = 12
    CHARLES_PLT_SPEED = 180

    _road_cx = (ROAD_X1 + ROAD_X2) / 2
    _west_lane_line_x = (ROAD_X1 + _road_cx - STREET_DIV_HW) / 2
    _east_lane_line_x = (_road_cx + STREET_DIV_HW + ROAD_X2) / 2
    CHARLES_PLT_X_OUT = int((_east_lane_line_x + ROAD_X2) / 2)
    CHARLES_PLT_X_RET = int((ROAD_X1 + _west_lane_line_x) / 2)
    CHARLES_PLT_Y_S = CHARLES_Y1 + CHARLES_PLT_W // 2 + 48
    CHARLES_PLT_Y_OUT = ENNIS_Y - ENNIS_HW + 16
    CHARLES_PLT_Y_RET = ENNIS_Y + ENNIS_HW // 8
    CHARLES_PLT_BR_X = KNOTT_DRIVEWAY_RD_X1 + KNOTT.driveway_hw // 2

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
            minlight="255",
        )
    )

    for path_corner_name, path_x, path_y, path_z, next_target in [
        ("cs_pc1", CHARLES_PLT_X_OUT, CHARLES_PLT_Y_S, platform_z_charles, "cs_pc2"),
        ("cs_pc2", CHARLES_PLT_X_OUT, CHARLES_PLT_Y_OUT, platform_z_flat, "cs_pc3"),
        ("cs_pc3", CHARLES_PLT_BR_X, CHARLES_PLT_Y_OUT, platform_z_flat, "cs_pc4"),
        ("cs_pc4", CHARLES_PLT_BR_X, KNOTT_DRIVEWAY_Y2, platform_z_flat, "cs_pc5"),
        (
            "cs_pc5",
            CHARLES_PLT_BR_X,
            KNOTT_DRIVEWAY_Y1,
            platform_z_backroad_south,
            "cs_pc6",
        ),
        ("cs_pc6", CHARLES_PLT_BR_X, KNOTT_DRIVEWAY_Y2, platform_z_flat, "cs_pc7"),
        ("cs_pc7", CHARLES_PLT_BR_X, CHARLES_PLT_Y_RET, platform_z_flat, "cs_pc8"),
        ("cs_pc8", CHARLES_PLT_X_RET, CHARLES_PLT_Y_RET, platform_z_flat, "cs_pc9"),
        ("cs_pc9", CHARLES_PLT_X_RET, CHARLES_PLT_Y_S, platform_z_charles, "cs_pc1"),
    ]:
        ENTITIES.append(
            ent(
                "path_corner",
                targetname=path_corner_name,
                target=next_target,
                origin=f"{path_x} {path_y} {path_z}",
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

    monsters2_start = len(ENTITIES)

    monster_stand_z = ROAD_Z + 24
    for monster_x, monster_y, monster_angle in [
        (ROAD_X1 + 64, -1200, 90),
        (ROAD_X2 - 64, -800, 270),
        (ROAD_X1 + 64, -300, 90),
        (ROAD_X2 - 64, 200, 270),
        (0, -1600, 90),
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    for monster_x, monster_y, monster_angle in [
        (500, ENNIS_Y - ENNIS_HW + 40, 0),
        (1200, ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - 40, 180),
        (1800, ENNIS_Y - ENNIS_HW + 40, 0),
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    backroad_center_x = (KNOTT_DRIVEWAY_RD_X1 + KNOTT_DRIVEWAY_RD_X2) // 2
    _backroad_rise = KNOTT_DRIVEWAY_ZT_S - KNOTT_DRIVEWAY_ZT_N

    for ogre_y, ogre_z in [
        (
            -600,
            FLOOR_Z2
            + 2
            + (
                _backroad_rise
                * ((-600) - KNOTT_DRIVEWAY_Y2)
                // (KNOTT_DRIVEWAY_Y1 - KNOTT_DRIVEWAY_Y2)
            )
            + 24,
        ),
        (
            -1200,
            FLOOR_Z2
            + 2
            + (
                _backroad_rise
                * ((-1200) - KNOTT_DRIVEWAY_Y2)
                // (KNOTT_DRIVEWAY_Y1 - KNOTT_DRIVEWAY_Y2)
            )
            + 24,
        ),
        (KNOTT_DRIVEWAY_Y1 + 64, KNOTT_GROUND_Z + 2 + 24),
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{backroad_center_x} {ogre_y} {ogre_z}",
                angle="90",
            )
        )

    if KNOTT_ENABLED_MONSTERS:
        for fl in range(KNOTT.floors):
            fz = KNOTT_GROUND_Z + fl * KNOTT.floor_h + KNOTT.wall_t + 24
            split = KNOTT_ROOM_SPLITS[fl]
            sr_yc = (KNOTT_BIY1 + split) // 2
            nr_yc = (split + KNOTT.wall_t + KNOTT_BIY2) // 2
            for rxc in [KNOTT_WEST_ROOM_CX, KNOTT_EAST_ROOM_CX]:
                for ryc in [sr_yc, nr_yc]:
                    ENTITIES.append(
                        ent("monster_knight", origin=f"{rxc} {ryc} {fz}", angle="270")
                    )

        hall_center_x = (KNOTT_ENT_X1 + KNOTT_ENT_X2) // 2
        for fl in range(KNOTT.floors):
            fz = KNOTT_GROUND_Z + fl * KNOTT.floor_h + KNOTT.wall_t + 24
            hall_yc = (KNOTT_BIY1 + KNOTT_BIY2) // 2
            ENTITIES.append(
                ent(
                    "monster_knight",
                    origin=f"{hall_center_x} {hall_yc} {fz}",
                    angle="180",
                )
            )

        for roof_enemy_x, roof_enemy_y in [
            (KNOTT_WEST_ROOM_CX, KNOTT.y2 - 80),
            (KNOTT_EAST_ROOM_CX, KNOTT.y2 - 80),
            (KNOTT_CX, KNOTT.y1 + 80),
            (KNOTT_WEST_ROOM_CX, KNOTT.y1 + 80),
        ]:
            ENTITIES.append(
                ent(
                    "monster_knight",
                    origin=f"{roof_enemy_x} {roof_enemy_y} {KNOTT_Z2 + 24}",
                    angle="180",
                )
            )

    deck_center_z = int(deck_top_z(0)) + 24
    deck_p3_z = int(deck_top_z(525)) + 24
    for monster_x, monster_y, monster_z, monster_angle in [
        (0, *_cs_offset(0, 0, deck_center_z), 180),
        (525, *_cs_offset(525, 0, deck_p3_z), 0),
    ]:
        ENTITIES.append(
            ent(
                "monster_hell_knight",
                origin=f"{monster_x} {monster_y} {monster_z}",
                angle=str(monster_angle),
            )
        )

    if KNOTT_ENABLED_WALKWAY:
        walkway_mid_x = (WALK_X1 + WALK_X2) // 2
        walkway_mid_y = (BRIDGE.y1 + KNOTT.y2) // 2
        walkway_mid_z = (WALK_ZT1 + WALK_ZT2) // 2
        ENTITIES.append(
            ent(
                "monster_hell_knight",
                origin=f"{walkway_mid_x} {walkway_mid_y} {walkway_mid_z + 24}",
                angle="180",
            )
        )

        accessible_walk_z = KNOTT_GROUND_Z + 24
        for accessible_walk_y, accessible_walk_angle in [
            (-128, 90),
            (180, 270),
        ]:
            ENTITIES.append(
                ent(
                    "monster_hell_knight",
                    origin=f"2120 {accessible_walk_y} {accessible_walk_z}",
                    angle=str(accessible_walk_angle),
                )
            )

    if not ENTITIES_ENABLED_MONSTERS:
        del ENTITIES[monsters2_start:]

    exit_start = len(ENTITIES)

    dorm_exit_xc = (DORM.x1 + DORM.x2) // 2
    _north2_y2 = DORM_NORTH_Y1
    _north2_y1 = _north2_y2 - (DORM_NORTH_Y2 - DORM_NORTH_Y1)
    dorm_exit_yc = (_north2_y1 + _north2_y2) // 2
    dorm_exit_hw = 64
    dorm_exit_z0 = FLOOR_Z2
    dorm_exit_brush = box(
        dorm_exit_xc - dorm_exit_hw,
        dorm_exit_yc - dorm_exit_hw,
        dorm_exit_z0,
        dorm_exit_xc + dorm_exit_hw,
        dorm_exit_yc + dorm_exit_hw,
        dorm_exit_z0 + 112,
        Textures.TELEPORT,
    )
    ENTITIES.append(brush_ent("trigger_changelevel", dorm_exit_brush, map="loyola"))
    ENTITIES.append(brush_ent("func_illusionary", dorm_exit_brush))
    ENTITIES.append(
        ent(
            "light",
            origin=f"{dorm_exit_xc} {dorm_exit_yc} {dorm_exit_z0 + 56}",
            light="200",
            _color="0.4 0.6 1",
        )
    )

    frame_t = 16
    frame_d = 12
    ex1 = dorm_exit_xc - dorm_exit_hw
    ex2 = dorm_exit_xc + dorm_exit_hw
    portal_top = dorm_exit_z0 + 112

    exit_px_w, exit_px_h, exit_depth = 4, 2, 2

    exit_embed = 1
    exit_total = exit_depth + exit_embed
    exit_text_w = (4 * 5 - 1) * exit_px_w
    exit_x0 = dorm_exit_xc - exit_text_w // 2
    exit_z_base = portal_top + (frame_t - 6 * exit_px_h) // 2
    for face_yc, out_sign in [
        (dorm_exit_yc - dorm_exit_hw, -1),
        (dorm_exit_yc + dorm_exit_hw, +1),
    ]:
        fy1 = face_yc - frame_d // 2
        fy2 = face_yc + frame_d // 2
        for bx1, bx2, bz1, bz2 in [
            (ex1 - frame_t, ex1, dorm_exit_z0, portal_top + frame_t),
            (ex2, ex2 + frame_t, dorm_exit_z0, portal_top + frame_t),
            (ex1 - frame_t, ex2 + frame_t, portal_top, portal_top + frame_t),
        ]:
            ENTITIES.append(
                brush_ent(
                    "func_detail", box(bx1, fy1, bz1, bx2, fy2, bz2, Textures.CEMENT)
                )
            )

        if out_sign < 0:
            letter_text, y_face, do_mirror = "EXIT", fy1 - exit_depth, False
        else:
            letter_text, y_face, do_mirror = "EXIT"[::-1], fy2 - exit_embed, True
        letter_brushes = render_text_flat(
            letter_text,
            x0=exit_x0,
            y_face=y_face,
            z_base=exit_z_base,
            px_w=exit_px_w,
            px_h=exit_px_h,
            depth=exit_total,
            tex=Textures.LAVA,
            mirror=do_mirror,
        )
        if letter_brushes:
            ENTITIES.append(brush_ent("func_detail", letter_brushes))

    beam_y1 = dorm_exit_yc - dorm_exit_hw - frame_d // 2
    beam_y2 = dorm_exit_yc + dorm_exit_hw + frame_d // 2
    for bx1, bx2 in [(ex1 - frame_t, ex1), (ex2, ex2 + frame_t)]:
        ENTITIES.append(
            brush_ent(
                "func_detail",
                box(
                    bx1,
                    beam_y1,
                    portal_top,
                    bx2,
                    beam_y2,
                    portal_top + frame_t,
                    Textures.CEMENT,
                ),
            )
        )

    exit_y0 = dorm_exit_yc - exit_text_w // 2
    for x_face, letter_text, do_mirror in [
        (ex1 - frame_t - exit_depth, "EXIT"[::-1], True),
        (ex2 + frame_t - exit_embed, "EXIT", False),
    ]:
        lb = render_text_flat_x(
            letter_text,
            y0=exit_y0,
            x_face=x_face,
            z_base=exit_z_base,
            px_w=exit_px_w,
            px_h=exit_px_h,
            depth=exit_total,
            tex=Textures.LAVA,
            mirror=do_mirror,
        )
        if lb:
            ENTITIES.append(brush_ent("func_detail", lb))

    if not ENTITIES_ENABLED_EXIT:
        del ENTITIES[exit_start:]

    ENTITIES.append(
        ent(
            "info_intermission",
            origin="-361 -500 350",
            mangle="-10 75 0",
        )
    )

    return BRUSHES, ENTITIES
