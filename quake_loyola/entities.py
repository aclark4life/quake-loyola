from .constants import (
    A_SEGS,
    ARCH_RIN,
    ARCH_SLAB_W,
    ARCH_STILT_H,
    BRIDGE,
    BRIDGE_ARCH_X,
    BRIDGE_DZ2,
    BRIDGE_EAST_SHIFT_END,
    BRIDGE_PAR_W,
    BRIDGE_PEND_XS,
    BRIDGE_PIL_BASE_H,
    BRIDGE_PIL_BASE_RAMP_H,
    BRIDGE_PIL_CAP_H,
    BRIDGE_PIL_EXTRA,
    BRIDGE_PIL_HW,
    BRIDGE_PIL_PYR_H,
    CHARLES_LAMP_POST_H,
    CHARLES_LAMP_POST_XS,
    CHARLES_LAMP_POST_YS,
    CHARLES_WALK_W,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_RIDGE_Z,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    ENNIS_CEMENT_LAMP_POSTS,
    ENNIS_CEMENT_X1,
    ENNIS_CEMENT_X2,
    ENNIS_GATE_X1,
    ENNIS_GATE_X2,
    ENNIS_HW,
    ENNIS_PIL_BELL2_H,
    ENNIS_PIL_CAP_H,
    ENNIS_PIL_HW,
    ENNIS_PIL_POST_H,
    ENNIS_PIL_X1,
    ENNIS_PIL_ZB,
    ENNIS_WALL_NY,
    ENNIS_WALL_T,
    ENNIS_Y,
    FLOOR_Z2,
    KNOTT,
    KNOTT_BIY1,
    KNOTT_BIY2,
    KNOTT_CX,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_EAST_ROOM_CX,
    KNOTT_ENABLED,
    KNOTT_ENT_X1,
    KNOTT_ENT_X2,
    KNOTT_GROUND_Z,
    KNOTT_ORIG_CX,
    KNOTT_ROOM_SPLITS,
    KNOTT_SHAFT_X1,
    KNOTT_SHAFT_X2,
    KNOTT_SHAFT_Y1,
    KNOTT_SHAFT_Y2,
    KNOTT_STAIRS_MID_Y,
    KNOTT_STAIRS_X1,
    KNOTT_STAIRS_X2,
    KNOTT_STAIRS_Y1,
    KNOTT_STAIRS_Y2,
    KNOTT_WALKWAY_ENABLED,
    KNOTT_WEST_ROOM_CX,
    KNOTT_Z2,
    ROAD_X1,
    ROAD_X2,
    SDORM_LIFT,
    SHOW_SUPPORTS,
    WALK_X1,
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
    make_tree,
    render_text_flat,
    render_text_flat_x,
)


def build():
    BRUSHES = []
    ENTITIES = []
    BRIDGE_DECK_Z = deck_top_z(0) + 8  # centre of arch deck + a bit (spawn/item height)
    ROAD_Z = FLOOR_Z2 + 8

    # ── Knott Hall room goodies — 2 items per room, varied per floor ──────────────
    knott_entity_start = len(
        ENTITIES
    )  # checkpoint — trimmed below if KNOTT_ENABLED is False
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
        light_z = fz1 + KNOTT.floor_h - 24  # near ceiling
        split = KNOTT_ROOM_SPLITS[floor_index]
        sr_yc = (KNOTT_BIY1 + split) // 2
        nr_yc = (split + KNOTT.wall_t + KNOTT_BIY2) // 2
        for side_xc in [KNOTT_WEST_ROOM_CX, KNOTT_EAST_ROOM_CX]:
            for ryc in [sr_yc, nr_yc]:
                # If west room north items land within 64 units of stairwell south wall, push south
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
                # Extra fill light at lower mid-height to reduce dark corners
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

    # ── West stairwell lights — ceiling + mid-flight + low fill per lane per floor ──────────
    west_stair_center_x = (KNOTT_STAIRS_X1 + KNOTT_STAIRS_X2) // 2  # X centre of shaft
    west_stair_north_y = (
        KNOTT_STAIRS_MID_Y + KNOTT_STAIRS_Y2
    ) // 2  # Y centre of north lane
    west_stair_south_y = (
        KNOTT_STAIRS_Y1 + KNOTT_STAIRS_MID_Y
    ) // 2  # Y centre of south lane
    for floor_index in range(KNOTT.floors):
        west_stair_light_z = (
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h - 24
        )  # near ceiling
        west_stair_mid_z = (
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h // 2
        )  # mid-flight
        west_stair_low_z = (
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + KNOTT.floor_h // 4
        )  # low fill
        for lz in [west_stair_light_z, west_stair_mid_z, west_stair_low_z]:
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{west_stair_center_x} {west_stair_north_y} {lz}",
                    light="220",
                )
            )
            # South-lane near-ceiling lights sit inside the floor slab above — skip (buried in solid)
            if lz != west_stair_light_z:
                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{west_stair_center_x} {west_stair_south_y} {lz}",
                        light="220",
                    )
                )

    # ── Central hallway lights — 5 per floor along N-S corridor ─────────────────
    hall_center_x = (KNOTT_ENT_X1 + KNOTT_ENT_X2) // 2  # hallway centre X
    hall_light_ys = [
        KNOTT_BIY1 + (KNOTT_BIY2 - KNOTT_BIY1) * i // 4
        for i in range(1, 4)  # quarters: 25%, 50%, 75%
    ] + [
        KNOTT_BIY1 + (KNOTT_BIY2 - KNOTT_BIY1) // 8,  # 12.5% (near south end)
        KNOTT_BIY1 + (KNOTT_BIY2 - KNOTT_BIY1) * 7 // 8,  # 87.5% (near north end)
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

    # ── Entrance corridor lights — one per floor in each doorway ─────────────────
    entry_corridor_y = KNOTT.y2 - 48  # just inside north face
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

    # ── Knott Hall bookshelves — scattered through rooms ─────────────────────────
    KNOTT_SHELF_H = 64  # height of shelf stack
    KNOTT_SHELF_D = 16  # depth (one wall-thickness)
    KNOTT_SHELF_W = 64  # width

    shelf_offsets = [0, 0, 0, 0, 0]

    for floor_index in range(KNOTT.floors):
        fz1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
        fz_surf = fz1 + KNOTT.wall_t
        split = KNOTT_ROOM_SPLITS[floor_index]
        shelf_x_offset = shelf_offsets[floor_index]

        for shelf_center_x in [KNOTT_WEST_ROOM_CX, KNOTT_EAST_ROOM_CX]:
            # South room: shelf against south wall — front faces south (-Y)
            shelf_x = shelf_center_x + shelf_x_offset
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
                            "shelf_1",
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

    if not KNOTT_ENABLED:
        del ENTITIES[knott_entity_start:]

    # Teleport destinations — west arch ↔ east arch
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_east",
            origin=f"{(DORM.x1 + DORM.x2) // 2} {(DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2} {int(DORM_RIDGE_Z + 40)}",
            angle="270",  # facing south toward the bridge
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_west",
            origin=f"{KNOTT_CX} {(KNOTT.y1 + KNOTT.y2) // 2} {int(KNOTT_Z2 + 40)}",
            angle="180",  # facing south, on Knott Hall rooftop
        )
    )

    # West arch trigger → east destination
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

    # West lower trigger (ground floor — simple box between posts)
    wlx1 = WORLD_X1 + WALL_T
    wlx2 = wlx1 + ARCH_SLAB_W
    west_lower = [
        box(wlx1, -ARCH_RIN, FLOOR_Z2, wlx2, ARCH_RIN, BRIDGE_DZ2, Textures.TELEPORT)
    ]
    ENTITIES.append(brush_ent("trigger_teleport", west_lower, target="dest_east"))
    ENTITIES.append(brush_ent("func_illusionary", west_lower))

    # East arch trigger → west destination (shifted south to match angled span)
    east_brushes = arch_fill(
        WORLD_X2 - WALL_T - ARCH_SLAB_W,
        WORLD_X2 - WALL_T,
        BRIDGE_EAST_SHIFT_END,
        BRIDGE_DZ2,
        ARCH_RIN,
        A_SEGS,
        Textures.TELEPORT,
        stilt_h=ARCH_STILT_H,
    )
    ENTITIES.append(brush_ent("trigger_teleport", east_brushes, target="dest_west"))
    ENTITIES.append(brush_ent("func_illusionary", east_brushes))

    # East lower trigger (ground floor — teleports up to bridge deck above)
    elx1 = WORLD_X2 - WALL_T - ARCH_SLAB_W
    elx2 = WORLD_X2 - WALL_T
    east_lower_deck_x = elx1 - 64  # west of the arch, on the flat deck approach
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

    # ── North & South Charles Street arch teleports ────────────────────────────────
    # South arch → south dorm rooftop; North arch → north dorm rooftop
    CHARLES_ARCH_RIN = 256  # inner radius = road half-width
    CHARLES_ARCH_STILT = 96  # straight post height before arch springs
    CHARLES_ARCH_W = 48  # arch thickness in Y (thicker = more stone-like)

    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_south_dorm_roof",
            origin=f"{(DORM.x1 + DORM.x2) // 2} {(DORM_SOUTH1_Y1 + DORM_SOUTH1_Y2) // 2} {int(DORM_RIDGE_Z + SDORM_LIFT + 40)}",
            angle="90",  # facing north, at top of A-frame ridge
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_dorm_roof",
            origin=f"{(DORM.x1 + DORM.x2) // 2} {(DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2} {int(DORM_RIDGE_Z + 40)}",
            angle="0",  # facing east, atop roof ridge center
        )
    )

    CHARLES_ARCH_TRIG_INSET = 8  # push trigger away from world walls and road surface

    for arch_y1, arch_y2, trigger_y1, trigger_y2, arch_target in [
        (
            CHARLES_Y1,
            CHARLES_Y1 + CHARLES_ARCH_W,
            CHARLES_Y1 + CHARLES_ARCH_TRIG_INSET,
            CHARLES_Y1 + CHARLES_ARCH_W,
            "dest_south_dorm_roof",
        ),  # south arch → south dorm rooftop
        (
            CHARLES_Y2 - CHARLES_ARCH_W,
            CHARLES_Y2,
            CHARLES_Y2 - CHARLES_ARCH_W,
            CHARLES_Y2 - CHARLES_ARCH_TRIG_INSET,
            "dest_dorm_roof",
        ),  # north arch → dorm rooftop
    ]:
        arch_top_z = FLOOR_Z2 + CHARLES_ARCH_STILT + CHARLES_ARCH_RIN
        # Box trigger — reliable activation, inset from walls
        north_south_trigger_brush = [
            box(
                ROAD_X1 + CHARLES_ARCH_TRIG_INSET,
                trigger_y1,
                FLOOR_Z2 + 4,
                ROAD_X2 - CHARLES_ARCH_TRIG_INSET,
                trigger_y2,
                arch_top_z,
                Textures.TELEPORT,
            )
        ]
        ENTITIES.append(
            brush_ent("trigger_teleport", north_south_trigger_brush, target=arch_target)
        )
        # Arch-shaped illusionary fill so the teleport glow looks like an arch
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

    # ── Ennis east-end & KH driveway south-end arch teleports ─────────────────
    # Both arches → top of Knott Hall rooftop.
    # Each arch spans the road opening and glows with teleport texture.
    ENNIS_ARCH_STILT = 64
    KH_DRIVE_ARCH_STILT = 64
    ARCH_TRIG_INSET = 8  # keep triggers off the walls/floor

    kh_drive_cx = (KNOTT_DRIVEWAY_RD_X1 + KNOTT_DRIVEWAY_RD_X2) // 2
    kh_roof_origin = f"{(KNOTT_STAIRS_X2 + KNOTT_SHAFT_X1) // 2} {(KNOTT_STAIRS_Y1 + KNOTT_SHAFT_Y2) // 2} {int(KNOTT_Z2 + 40)}"

    # Destinations — both land on KH rooftop, facing south
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_ennis_east",
            origin=kh_roof_origin,
            angle="90",  # facing north on KH rooftop
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_kh_drive_south",
            origin=kh_roof_origin,
            angle="90",  # facing north on KH rooftop
        )
    )

    # Ennis east arch (X-aligned, at the east world wall)
    ennis_arch_x1 = WORLD_X2_EXT - WALL_T - ARCH_SLAB_W
    ennis_arch_x2 = WORLD_X2_EXT - WALL_T
    ennis_arch_top_z = FLOOR_Z2 + ENNIS_ARCH_STILT + ENNIS_HW
    ennis_east_trigger = [
        box(
            ennis_arch_x1,
            ENNIS_Y - ENNIS_HW + ARCH_TRIG_INSET,
            FLOOR_Z2 + 4,
            ennis_arch_x2,
            ENNIS_Y + ENNIS_HW - ARCH_TRIG_INSET,
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

    # Stone arch surround — X-aligned, freestanding at the east Ennis wall
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
        Textures.STONE,
        stilt_h=ENNIS_ARCH_STILT,
        yc=float(ENNIS_Y),
        freestanding=True,
    )
    ENTITIES.append(brush_ent("func_detail", ennis_stone_arch))

    # KH driveway south arch (Y-aligned, flush with the south world wall)
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

    # Stone arch surround — Y-aligned, freestanding at the KH driveway south end
    KH_ARCH_ROUT = KNOTT.driveway_hw + 56
    kh_stone_arch = arch_wall_y(
        kh_arch_y1,
        kh_arch_y2,
        kh_drive_cx - KH_ARCH_ROUT,
        kh_drive_cx + KH_ARCH_ROUT,
        KNOTT_DRIVEWAY_ZT_S,
        kh_arch_top_z,
        KNOTT.driveway_hw,
        KH_ARCH_ROUT,
        A_SEGS,
        Textures.STONE,
        stilt_h=KH_DRIVE_ARCH_STILT,
        xc=float(kh_drive_cx),
    )
    ENTITIES.append(brush_ent("func_detail", kh_stone_arch))

    ENTITIES.append(
        ent(
            "info_player_start",
            origin=f"{KNOTT_CX} {BRIDGE.y1 + BRIDGE_PAR_W + 32} {int(BRIDGE_DZ2 + 24)}",
            angle="180",
        )
    )

    knott_cy = (KNOTT.y1 + KNOTT.y2) // 2  # Knott Hall center Y = -528
    DORM_NORTH_CY = (DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2  # north building center Y
    DORM_CX = (DORM.x1 + DORM.x2) // 2  # west buildings center X
    DORM_SOUTH1_CY = (DORM_SOUTH1_Y1 + DORM_SOUTH1_Y2) // 2  # south building 1 center Y
    DORM_SOUTH2_CY = (DORM_SOUTH2_Y1 + DORM_SOUTH2_Y2) // 2  # south building 2 center Y

    # ── Deathmatch spawns — spread across all areas ──────────────────────────
    for pos, angle in [
        # Bridge deck
        ((0, 0, int(deck_top_z(0) + 32)), 180),
        ((-200, 0, int(deck_top_z(-200) + 32)), 90),
        ((200, 0, int(deck_top_z(200) + 32)), 270),
        ((-400, 0, int(deck_top_z(-400) + 32)), 90),
        ((400, 0, int(deck_top_z(400) + 32)), 270),
        # Walkway
        *(
            [((KNOTT_CX, (BRIDGE.y1 + KNOTT.y2) // 2, int(WALK_ZT1 + 32)), 180)]
            if KNOTT_ENABLED
            else []
        ),
        # Knott Hall — ground, mid, upper floors
        *(
            [
                (
                    (
                        (KNOTT_ENT_X1 + KNOTT_ENT_X2) // 2,
                        KNOTT.y2 - 80,
                        KNOTT_GROUND_Z + 40,
                    ),
                    180,
                ),  # entrance hallway, north
                ((KNOTT_CX - 100, knott_cy, KNOTT_GROUND_Z + KNOTT.floor_h + 40), 270),
                (
                    (KNOTT_CX + 100, knott_cy, KNOTT_GROUND_Z + KNOTT.floor_h * 2 + 40),
                    90,
                ),
                (
                    (KNOTT_CX, KNOTT.y1 + 100, KNOTT_GROUND_Z + KNOTT.floor_h * 3 + 40),
                    0,
                ),
                ((KNOTT_CX, knott_cy, KNOTT_GROUND_Z + KNOTT.floor_h * 4 + 40), 180),
                # Knott Hall rooftop
                ((KNOTT_CX, knott_cy, KNOTT_Z2 + 40), 180),
            ]
            if KNOTT_ENABLED
            else []
        ),
        # Charles Street
        ((0, 300, ROAD_Z + 24), 180),
        ((0, -400, ROAD_Z + 24), 0),
        ((0, DORM_SOUTH1_CY, ROAD_Z + 24), 270),
        # North building interior
        ((DORM_CX, DORM_NORTH_CY, FLOOR_Z2 + 40), 90),
        ((DORM_CX, DORM_NORTH_CY, FLOOR_Z2 + DORM.floor_h + 40), 90),
        # North building roof ridge
        ((DORM_CX, DORM_NORTH_CY, int(DORM_RIDGE_Z + 40)), 90),
        # South buildings interiors
        ((DORM_CX, DORM_SOUTH1_CY, FLOOR_Z2 + SDORM_LIFT + 40), 90),
        ((DORM_CX, DORM_SOUTH2_CY, FLOOR_Z2 + SDORM_LIFT + 40), 90),
        # Ground east/west of bridge
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

    # ── Weapons ───────────────────────────────────────────────────────────────
    # Rocket launcher — bridge centre (high value, exposed position)
    ENTITIES.append(ent("weapon_rocketlauncher", origin=f"0 0 {BRIDGE_DECK_Z}"))
    # Rocket launcher — Knott Hall floor 3 (reward for climbing)
    if KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_rocketlauncher",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 3 + 40}",
            )
        )
    # Rocket launcher — west arch, north side
    ENTITIES.append(
        ent(
            "weapon_rocketlauncher",
            origin=f"{BRIDGE_ARCH_X[1]} {BRIDGE.y1 - 48} {BRIDGE_DECK_Z}",
        )
    )
    # Remaining rocket launchers
    for rl_origin in [
        f"{ROAD_X2 + 40} {ENNIS_Y - ENNIS_HW - 200} {ROAD_Z + 24}",  # east sidewalk, south of Ennis
        f"{BRIDGE_ARCH_X[2]} 0 {ROAD_Z + 24}",  # under bridge, mid span
        f"{int(ENNIS_GATE_X1 + (ENNIS_GATE_X2 - ENNIS_GATE_X1) // 2)} {ENNIS_WALL_NY - 80} {FLOOR_Z2 + 24}",  # Ennis fence midpoint
        f"{int(ENNIS_CEMENT_X1 + (ENNIS_CEMENT_X2 - ENNIS_CEMENT_X1) // 2)} {ENNIS_WALL_NY - 80} {FLOOR_Z2 + 24}",  # Ennis wall midpoint
        # Bridge deck — one per span
        f"{(BRIDGE.x1 + BRIDGE_ARCH_X[0]) // 2} 0 {BRIDGE_DECK_Z}",  # span 1
        f"{(BRIDGE_ARCH_X[0] + BRIDGE_ARCH_X[1]) // 2} {BRIDGE.y2 - 24} {BRIDGE_DECK_Z}",  # span 2 south edge
        f"{(BRIDGE_ARCH_X[1] + BRIDGE_ARCH_X[2]) // 2} {BRIDGE.y1 + 24} {BRIDGE_DECK_Z}",  # span 3 north edge
        f"{(BRIDGE_ARCH_X[2] + BRIDGE.x2) // 2} 0 {BRIDGE_DECK_Z}",  # span 4
        f"{(BRIDGE.x2 + BRIDGE_ARCH_X[4]) // 2} 0 {BRIDGE_DECK_Z}",  # span 5 (east angled)
    ]:
        ENTITIES.append(ent("weapon_rocketlauncher", origin=rl_origin))

    # Super shotgun — spread around mid-tier locations
    if KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_supershotgun",
                origin=f"{KNOTT_EAST_ROOM_CX} {KNOTT.y2 - 80} {KNOTT_GROUND_Z + 40}",
            )
        )
    ENTITIES.append(
        ent("weapon_supershotgun", origin=f"300 300 {ROAD_Z + 24}")
    )  # east sidewalk
    ENTITIES.append(
        ent(
            "weapon_supershotgun",
            origin=f"{DORM_CX} {DORM_SOUTH1_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
        )
    )

    # Grenade launcher — Knott Hall floor 2, south building 2
    if KNOTT_ENABLED:
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

    # Nailgun — bridge approaches, Charles Street
    ENTITIES.append(ent("weapon_nailgun", origin=f"-600 0 {ROAD_Z + 24}"))
    ENTITIES.append(ent("weapon_nailgun", origin=f"600 0 {ROAD_Z + 24}"))
    if KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_nailgun",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h + 40}",
            )
        )

    # Lightning gun — high-value, contested spots
    ENTITIES.append(
        ent("weapon_lightning", origin=f"200 0 {BRIDGE_DECK_Z}")
    )  # bridge centre
    ENTITIES.append(
        ent(
            "weapon_lightning",
            origin=f"{DORM_CX} {DORM_NORTH_CY} {int(DORM_RIDGE_Z + 40)}",
        )
    )  # north dorm roof
    if KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_lightning",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 4 + 40}",
            )
        )  # KH top floor
    ENTITIES.append(
        ent("weapon_lightning", origin=f"0 -500 {ROAD_Z + 24}")
    )  # south Charles St

    # ── Ogres — spread across open areas and upper floors ─────────────────────
    # Bridge deck
    ENTITIES.append(ent("monster_ogre", origin=f"-300 0 {BRIDGE_DECK_Z}", angle="90"))
    ENTITIES.append(ent("monster_ogre", origin=f"300 0 {BRIDGE_DECK_Z}", angle="270"))
    # Charles Street
    ENTITIES.append(ent("monster_ogre", origin=f"0 200 {ROAD_Z + 24}", angle="180"))
    ENTITIES.append(ent("monster_ogre", origin=f"0 -600 {ROAD_Z + 24}", angle="0"))
    # East sidewalk
    ENTITIES.append(ent("monster_ogre", origin=f"700 0 {ROAD_Z + 24}", angle="270"))
    # West sidewalk
    ENTITIES.append(ent("monster_ogre", origin=f"-700 0 {ROAD_Z + 24}", angle="90"))
    # Dorm rooftop
    ENTITIES.append(
        ent(
            "monster_ogre",
            origin=f"{DORM_CX} {DORM_SOUTH1_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
            angle="90",
        )
    )
    # Knott Hall floors
    if KNOTT_ENABLED:
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
        # KH rooftop
        ENTITIES.append(
            ent(
                "monster_ogre",
                origin=f"{KNOTT_CX} {knott_cy} {KNOTT_Z2 + 40}",
                angle="180",
            )
        )

    # ── Ammo ──────────────────────────────────────────────────────────────────
    for ax in BRIDGE_ARCH_X:
        ENTITIES.append(ent("item_rockets", origin=f"{ax} 0 {int(deck_top_z(ax) + 8)}"))
    for rx in [400, 800]:
        ENTITIES.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z + 24}"))
        ENTITIES.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z + 24}"))
    for kf in range(1, KNOTT.floors):
        ENTITIES.append(
            ent(
                "item_rockets",
                origin=f"{KNOTT_CX + 80} {knott_cy} {KNOTT_GROUND_Z + kf * KNOTT.floor_h + 40}",
            )
        )
    ENTITIES.append(
        ent("item_shells", origin=f"-300 -300 {ROAD_Z + 24}")
    )  # west sidewalk
    ENTITIES.append(
        ent("item_shells", origin=f"{DORM_CX} {DORM_NORTH_CY} {FLOOR_Z2 + 40}")
    )
    ENTITIES.append(ent("item_spikes", origin=f"-400 200 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_spikes", origin=f"400 -200 {ROAD_Z + 24}"))

    # ── Health & Armor ────────────────────────────────────────────────────────
    # Health — scattered throughout
    ENTITIES.append(ent("item_health", origin=f"0 0 {BRIDGE_DECK_Z}"))
    ENTITIES.append(
        ent(
            "item_health",
            origin=f"{KNOTT_EAST_ROOM_CX} {KNOTT.y2 - 64} {KNOTT_GROUND_Z + 40}",
        )
    )
    ENTITIES.append(
        ent(
            "item_health",
            origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 2 + 40}",
        )
    )
    ENTITIES.append(
        ent("item_health", origin=f"-300 400 {ROAD_Z + 24}")
    )  # west sidewalk
    ENTITIES.append(
        ent("item_health", origin=f"300 -600 {ROAD_Z + 24}")
    )  # east sidewalk
    ENTITIES.append(
        ent(
            "item_health",
            origin=f"{DORM_CX} {DORM_SOUTH2_CY} {FLOOR_Z2 + SDORM_LIFT + 40}",
        )
    )
    # Armor — contested locations
    ENTITIES.append(
        ent("item_armor1", origin=f"-200 0 {BRIDGE_DECK_Z}")
    )  # yellow armor on bridge
    ENTITIES.append(
        ent(
            "item_armor2",
            origin=f"{KNOTT_CX} {knott_cy} {KNOTT_GROUND_Z + KNOTT.floor_h * 4 + 40}",
        )
    )  # red armor top floor
    ENTITIES.append(
        ent(
            "item_armorInv",
            origin=f"{DORM_CX} {DORM_NORTH_CY} {int(DORM_RIDGE_Z + 40)}",
        )
    )  # mega armor on roof ridge (teleport reward)

    # Torch lights on pillar caps
    if SHOW_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
                continue
            pbase = deck_top_z(px)
            pcap = (
                pbase
                + BRIDGE.parapet_h
                + BRIDGE_PIL_EXTRA
                + BRIDGE_PIL_CAP_H
                + BRIDGE_PIL_PYR_H
            )  # top of pyramid
            cy_n = BRIDGE.y2 - BRIDGE_PAR_W // 2  # centred on north pillar cap
            cy_s = BRIDGE.y1 + BRIDGE_PAR_W // 2  # centred on south pillar cap
            # Flames on pillar tops — raised above pyramid apex so they visually sit on top
            ENTITIES.append(
                ent("light_flame_large_yellow", origin=f"{px} {cy_n} {int(pcap + 24)}")
            )
            ENTITIES.append(
                ent("light_flame_large_yellow", origin=f"{px} {cy_s} {int(pcap + 24)}")
            )
            # Damaging trigger at each flame — hurts players who walk into the fire
            for cy in [cy_n, cy_s]:
                fhb = box(
                    px - 16,
                    cy - 16,
                    int(pcap + 24),
                    px + 16,
                    cy + 16,
                    int(pcap) + 64,
                    Textures.SKY,
                )
                ENTITIES.append(brush_ent("trigger_hurt", [fhb], dmg="10"))

    # Pillar base uplights — ground-level spots wash light up the pier faces
    if SHOW_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
                continue
            for underbridge_light_y in [BRIDGE.y2 + 30, BRIDGE.y1 - 30]:
                # Skip abutment-pier positions buried in solid building geometry
                if px == BRIDGE_ARCH_X[0]:
                    continue
                if px == BRIDGE_ARCH_X[-1] and underbridge_light_y == BRIDGE.y1 - 30:
                    continue
                ENTITIES.append(
                    ent("light", origin=f"{px} {underbridge_light_y} 16", light="200")
                )

    # Campus lamp post lights — flame above brick cup, matching bridge pillar torches
    for lamp_x in CHARLES_LAMP_POST_XS:
        for lamp_y in CHARLES_LAMP_POST_YS:
            pole_top_z = FLOOR_Z2 + CHARLES_LAMP_POST_H
            flame_z = pole_top_z + 20
            ENTITIES.append(
                ent("light", origin=f"{lamp_x} {lamp_y} {flame_z}", light="300")
            )
            ENTITIES.append(
                ent(
                    "light_flame_large_yellow",
                    origin=f"{lamp_x} {lamp_y} {flame_z + 4}",
                )
            )

    # Ennis cement wall lamppost lights
    for lamp_x, lamp_y, lamp_z in ENNIS_CEMENT_LAMP_POSTS:
        ENTITIES.append(ent("light", origin=f"{lamp_x} {lamp_y} {lamp_z}", light="300"))
        ENTITIES.append(
            ent("light_flame_large_yellow", origin=f"{lamp_x} {lamp_y} {lamp_z + 4}")
        )

    # Ennis entrance pillar torches — flame above brick cup on each stone pillar
    ennis_pil_flame_z = (
        ENNIS_PIL_ZB + ENNIS_PIL_POST_H + ENNIS_PIL_CAP_H + ENNIS_PIL_BELL2_H + 20
    )
    ennis_pil_cx = ENNIS_PIL_X1 + ENNIS_PIL_HW
    for pillar_y in (
        ENNIS_Y - ENNIS_HW - ENNIS_PIL_HW,
        ENNIS_Y + ENNIS_HW + ENNIS_PIL_HW,
    ):
        ENTITIES.append(
            ent(
                "light",
                origin=f"{ennis_pil_cx} {pillar_y} {ennis_pil_flame_z}",
                light="300",
            )
        )
        ENTITIES.append(
            ent(
                "light_flame_large_yellow",
                origin=f"{ennis_pil_cx} {pillar_y} {ennis_pil_flame_z + 4}",
            )
        )

    # Under-bridge amber pendant lights — flicker style, hang below deck
    for pier_x in BRIDGE_PEND_XS:
        ENTITIES.append(
            ent(
                "light",
                origin=f"{pier_x} 0 {int(deck_bot_z(pier_x)) - 20}",
                light="350",
                style="1",
            )
        )

    # Pier base lights — illuminate plinths and arch openings from just inside each pier
    for pier_x in BRIDGE_ARCH_X:
        # West abutment pier is embedded in solid building geometry — skip buried lights
        if pier_x == BRIDGE_ARCH_X[0]:
            continue
        pier_light_z = (
            FLOOR_Z2 + BRIDGE_PIL_BASE_RAMP_H + 60
        )  # just above the plinth top, low in the arch
        ENTITIES.append(
            ent(
                "light", origin=f"{pier_x} {BRIDGE.y2 // 2} {pier_light_z}", light="250"
            )
        )
        ENTITIES.append(
            ent(
                "light", origin=f"{pier_x} {BRIDGE.y1 // 2} {pier_light_z}", light="250"
            )
        )

    # Cement arch on east face of abutment pier (-1246) — three lights for good coverage
    abutment_pier_x = min(BRIDGE_ARCH_X)  # = -1246
    abutment_arch_z = FLOOR_Z2 + BRIDGE_PIL_BASE_H + 60  # mid-height of arch opening
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + BRIDGE_PIL_HW + 32} 0 {abutment_arch_z}",
            light="700",
        )
    )
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + BRIDGE_PIL_HW + 32} {BRIDGE.y2 // 2} {abutment_arch_z}",
            light="500",
        )
    )
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + BRIDGE_PIL_HW + 32} {BRIDGE.y1 // 2} {abutment_arch_z}",
            light="500",
        )
    )

    # Light on underside of walkway slab illuminating the ramp below
    if KNOTT_WALKWAY_ENABLED:
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

    # Lift (func_plat) — rides from ground floor up through roof opening to rooftop
    if KNOTT_ENABLED:
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

    # Interior lights for all campus dorm buildings (north1, north2, 2 south)
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
                    )
                )

    # Interior lights for Knott Hall — 3×4 grid per floor
    if KNOTT_ENABLED:
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

    # ── Cartoon trees as func_detail ─────────────────────────────────────────────
    # Positions based on ref photos:
    # - Dense forest behind cement/iron wall north of Ennis (bridge13, bridge02)
    # - Large trees flanking Knott Hall on west side (bridge01, bridge10)
    # - Trees along Ennis Parallel campus road (bridge02)
    tree_positions = [
        # Along Ennis Parallel (campus side, west of Charles St — bridge02)
        (ROAD_X1 - 200, ENNIS_WALL_NY - 100),
        (ROAD_X1 - 400, ENNIS_WALL_NY - 80),
        (ROAD_X1 - 600, ENNIS_WALL_NY - 120),
    ]
    all_tree_brushes = []
    for tree_x, tree_y in tree_positions:
        all_tree_brushes += make_tree(tree_x, tree_y, FLOOR_Z2)
    ENTITIES.append(brush_ent("func_detail", all_tree_brushes))

    # ── Giant trees along Charles Street — in front of Knott Hall only ───────────
    # 5 trees in 2 rows: row of 2 closer to street, row of 3 closer to KH.
    # Tree height matches Knott Hall (KNOTT_Z2).
    charles_tree_height = KNOTT_Z2
    knott_tree_span = KNOTT.y2 - KNOTT.y1
    charles_tree_row_near_x = ROAD_X2 + CHARLES_WALK_W + 300  # closer to Charles St
    charles_tree_row_far_x = ROAD_X2 + CHARLES_WALK_W + 560  # closer to KH
    # Row of 2 — near row, 2 trees at 25% and 75% of KH Y span
    charles_tree_row2_ys = [int(KNOTT.y1 + knott_tree_span * f) for f in (0.25, 0.75)]
    # Row of 3 — far row, 3 trees at 15%, 50%, 85%
    charles_tree_row3_ys = [
        int(KNOTT.y1 + knott_tree_span * f) for f in (0.15, 0.5, 0.85)
    ]
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

    # ── Giant trees covering the entire east ground (east of Charles St sidewalk) ──
    # Scattered grid: base spacing ~350 units with per-tree random jitter up to
    # ±120 units in X and Y so the forest looks natural, not uniform.
    east_ground_tree_height = KNOTT_Z2
    east_ground_spacing = 350
    east_ground_jitter = 120
    east_ground_buffer = 120  # clearance buffer from world edges / wall
    east_ground_x1 = ROAD_X2 + CHARLES_WALK_W + east_ground_buffer
    east_ground_x2 = WORLD_X2_EXT - WALL_T - east_ground_buffer
    east_ground_y1 = (
        ENNIS_WALL_NY + ENNIS_WALL_T + 200
    )  # centered in north space (fence=1148, world=1696, mid≈1422)
    east_ground_y2 = WORLD_Y2 - WALL_T - east_ground_buffer

    import random as tree_rng

    tree_rng.seed(42)  # fixed seed for reproducible layout

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

    # ── Giant trees east of the teleport — randomised scatter, wider coverage ────
    # Randomly scattered across the full extended-east strip (WORLD_X2 → WORLD_X2_EXT),
    # south of Ennis drive down to the south world wall.
    # Rejection sampling enforces a minimum separation so trees don't overlap.
    east_side_tree_height = KNOTT_Z2
    east_side_foliage_hw = 160  # widest foliage half-width (make_giant_tree)
    _world_x2_ext = WORLD_X2 + 512  # WORLD_X2_EXT
    _ennis_south = ENNIS_Y - ENNIS_HW  # Ennis road south edge
    _ennis_sw_edge = _ennis_south - 3 * CHARLES_WALK_W - 32  # Ennis south sidewalk edge
    east_tele_brushes = []
    et_x1 = (
        WORLD_X2 + WALL_T + east_side_foliage_hw + 20
    )  # foliage clears the world wall / teleport
    et_x2 = _world_x2_ext - WALL_T - 80
    et_y1 = WORLD_Y1 + WALL_T + 120
    et_y2 = _ennis_sw_edge - east_side_foliage_hw  # keep foliage clear of the sidewalk
    et_min_dist = 280  # minimum centre-to-centre spacing
    et_placed = []
    for _ in range(300):  # attempt budget — stops when area is full
        cx = tree_rng.randint(et_x1, et_x2)
        cy = tree_rng.randint(et_y1, et_y2)
        if all(
            (cx - px) ** 2 + (cy - py) ** 2 >= et_min_dist**2 for px, py in et_placed
        ):
            et_placed.append((cx, cy))
            east_tele_brushes += make_giant_tree(
                cx, cy, FLOOR_Z2, east_side_tree_height
            )
    ENTITIES.append(brush_ent("func_detail", east_tele_brushes))

    bush_positions = [
        # Along north face of Ennis brick wall (campus grass side, not sidewalk)
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 60, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 160, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 260, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 360, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        # Along north face of iron fence
        (int(ENNIS_GATE_X1 + 120), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 300), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 500), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 700), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        # Along north face of cement parapet wall
        (int(ENNIS_CEMENT_X1 + 120), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 320), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 560), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        # Along Knott Hall west face (outside building)
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2 - 200),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2 + 200),
        # Along west building east face (outside building)
        (DORM.x2 + 48, -200),
        (DORM.x2 + 48, 200),
        (DORM.x2 + 48, 500),
    ]
    all_bush_brushes = []
    for bush_x, bush_y in bush_positions:
        all_bush_brushes += make_bush(bush_x, bush_y, FLOOR_Z2)

    # ── Bushes along verge in front of KH north face (south of Ennis sidewalk) ───
    # Line of bushes just south of ENNIS_SW_EDGE, spanning the raised/sloped ground
    # between the NW indent and the back-road corridor, skipping the entrance.
    knott_verge_y = ENNIS_Y - ENNIS_HW - 100  # north side of Ennis south sidewalk
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

    # ── Charles Street scrolling platform — proper two-lane loop with quad damage ──
    # Outbound: east lane north on Charles → south lane east on Ennis → east end
    # Return:   west lane south on Charles ← north lane west on Ennis ← east end
    # ── Charles Street platform — via back road, no Ennis lane switch ─────────────
    # Route: Charles outbound (north) → right on Ennis → right onto back road →
    #        south down hill → back up north → left on Ennis → Charles return (south)
    CHARLES_PLT_W = 128  # platform width and depth
    CHARLES_PLT_H = 12  # platform slab thickness
    CHARLES_PLT_SPEED = 180  # units per second

    CHARLES_PLT_X_OUT = ROAD_X2 // 4  # outbound Charles lane  (east,   X=+64)
    CHARLES_PLT_X_RET = -(ROAD_X2 * 3 // 4)  # return  Charles lane   (west,   X=-192)
    CHARLES_PLT_Y_S = CHARLES_Y1 + CHARLES_PLT_W // 2 + 48  # south turnaround
    CHARLES_PLT_Y_OUT = ENNIS_Y - ENNIS_HW + 16  # outbound Ennis lane (south Y≈792)
    CHARLES_PLT_Y_RET = ENNIS_Y + ENNIS_HW // 8  # return  Ennis lane  (north Y≈956)
    CHARLES_PLT_BR_X = (
        KNOTT_DRIVEWAY_RD_X1 + KNOTT.driveway_hw // 2
    )  # right lane on back road (X≈2382)

    # Z origin at each road surface (platform bottom + half thickness)
    platform_z_charles = ROAD_Z + CHARLES_PLT_H // 2  # Charles St   (= 14)
    platform_z_flat = FLOOR_Z2 + 2 + CHARLES_PLT_H // 2  # Ennis / back road flat (= 8)
    platform_z_backroad_south = (
        KNOTT_DRIVEWAY_ZT_S + 2 + CHARLES_PLT_H // 2
    )  # back road south / hill top (= 72)

    # Platform brush — placed at pc1 (south end of outbound Charles lane)
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

    # 9-corner loop:
    # pc1 Charles south (out) → pc2 Ennis junction → pc3 back-road junction
    # → pc4 top of slope → pc5 hill bottom (turn) → pc6 top of slope (return)
    # → pc7 Ennis junction return → pc8 Charles/Ennis return → pc9 Charles south (ret) → pc1
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

    # Quad damage at the hill top (south end of back road) — reward for the full loop
    ENTITIES.append(
        ent(
            "item_artifact_super_damage",
            origin=f"{CHARLES_PLT_BR_X} {KNOTT_DRIVEWAY_Y1} {platform_z_backroad_south + CHARLES_PLT_H + 18}",
        )
    )

    # ── Rocket launchers along the platform route ─────────────────────────────────
    rocket_hover_height = (
        CHARLES_PLT_H + 56
    )  # hover height above road — clear of platform top + item bbox
    backroad_mid_y = (KNOTT_DRIVEWAY_Y1 + KNOTT_DRIVEWAY_Y2) // 2  # Y=-1072
    backroad_mid_z = (
        FLOOR_Z2
        + 2
        + (KNOTT_DRIVEWAY_ZT_S - KNOTT_DRIVEWAY_ZT_N)
        * (backroad_mid_y - KNOTT_DRIVEWAY_Y2)
        // (KNOTT_DRIVEWAY_Y1 - KNOTT_DRIVEWAY_Y2)
    )
    for rocket_x, rocket_y, rocket_z in [
        # Charles outbound (south third, north third) — east sidewalk
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
        # Ennis outbound (quarter, three-quarter) — south verge
        (
            (CHARLES_PLT_X_OUT + CHARLES_PLT_BR_X) // 3,
            ENNIS_Y - ENNIS_HW - 40,
            FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        (
            (CHARLES_PLT_X_OUT + CHARLES_PLT_BR_X) * 2 // 3,
            ENNIS_Y - ENNIS_HW - 40,
            FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        # Back road going south (midpoint)
        (CHARLES_PLT_BR_X, backroad_mid_y, backroad_mid_z + rocket_hover_height),
        # Ennis return (midpoint) — north verge
        (
            (CHARLES_PLT_X_RET + CHARLES_PLT_BR_X) // 2,
            ENNIS_Y + ENNIS_HW + 40,
            FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        # Charles return (south third, north third) — west sidewalk
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

    # ── Monsters ──────────────────────────────────────────────────────────────────
    # Grunts patrol Charles Street and Ennis
    monster_stand_z = ROAD_Z + 24
    for monster_x, monster_y, monster_angle in [
        (ROAD_X1 + 64, -1200, 90),  # south Charles, west side heading north
        (ROAD_X2 - 64, -800, 270),  # south Charles, east side heading south
        (ROAD_X1 + 64, -300, 90),  # mid Charles, west side
        (ROAD_X2 - 64, 200, 270),  # mid Charles, east side
        (0, -1600, 90),  # far south Charles, centre
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    # Grunts on Ennis
    for monster_x, monster_y, monster_angle in [
        (500, ENNIS_Y - ENNIS_HW + 40, 0),  # Ennis east, south lane
        (1200, ENNIS_Y + ENNIS_HW - 40, 180),  # Ennis east, north lane
        (1800, ENNIS_Y - ENNIS_HW + 40, 0),  # Ennis further east
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    # Ogres on the back road hill — like guards on the slope
    backroad_center_x = (KNOTT_DRIVEWAY_RD_X1 + KNOTT_DRIVEWAY_RD_X2) // 2
    for ogre_y, ogre_z in [
        (
            -600,
            FLOOR_Z2
            + 2
            + (
                64
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
                64
                * ((-1200) - KNOTT_DRIVEWAY_Y2)
                // (KNOTT_DRIVEWAY_Y1 - KNOTT_DRIVEWAY_Y2)
            )
            + 24,
        ),
        (KNOTT_DRIVEWAY_Y1 + 64, KNOTT_GROUND_Z + 2 + 24),  # top of hill near quad
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{backroad_center_x} {ogre_y} {ogre_z}",
                angle="90",
            )
        )

    # Knights inside KH rooms — one per floor in each room
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

    # Enforcers in the hallway — one per floor
    hall_center_x = (KNOTT_ENT_X1 + KNOTT_ENT_X2) // 2
    for fl in range(KNOTT.floors):
        fz = KNOTT_GROUND_Z + fl * KNOTT.floor_h + KNOTT.wall_t + 24
        hall_yc = (KNOTT_BIY1 + KNOTT_BIY2) // 2
        ENTITIES.append(
            ent("monster_knight", origin=f"{hall_center_x} {hall_yc} {fz}", angle="180")
        )

    # Enforcers on rooftop
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

    # ── Demon knights (monster_hell_knight) ───────────────────────────────────────
    # Two on the bridge arch span — guard the crown and Pier 3 approach
    deck_center_z = int(deck_top_z(0)) + 24  # standing height at arch crown
    deck_p3_z = int(deck_top_z(525)) + 24  # standing height near Pier 3
    for monster_x, monster_y, monster_z, monster_angle in [
        (0, 0, deck_center_z, 180),  # arch crown, facing west
        (525, 0, deck_p3_z, 0),  # Pier 3 approach, facing east
    ]:
        ENTITIES.append(
            ent(
                "monster_hell_knight",
                origin=f"{monster_x} {monster_y} {monster_z}",
                angle=str(monster_angle),
            )
        )

    # One on the elevated walkway — guards the bridge → KH 2nd floor approach
    walkway_mid_x = (BRIDGE.x2 + WALK_X1) // 2  # midpoint of walkway span
    ENTITIES.append(
        ent(
            "monster_hell_knight",
            origin=f"{walkway_mid_x} 0 {WALK_ZT1 + 24}",
            angle="180",
        )
    )

    # Two on the accessible walkway alongside Pier 5
    accessible_walk_z = KNOTT_GROUND_Z + 24  # walkway surface + standing height
    for accessible_walk_y, accessible_walk_angle in [
        (-128, 90),  # mid-path, facing north toward bridge
        (180, 270),  # north end near bridge south edge, facing south
    ]:
        ENTITIES.append(
            ent(
                "monster_hell_knight",
                origin=f"2120 {accessible_walk_y} {accessible_walk_z}",
                angle=str(accessible_walk_angle),
            )
        )

    # ── Single-player exit — inside north dorm 2 (southern north dorm) ──────────
    # Loops back to this map. Portal stands inside north dorm 2.
    dorm_exit_xc = (DORM.x1 + DORM.x2) // 2
    _north2_y2 = DORM_NORTH_Y1  # north face of dorm 2 = south face of dorm 1
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
    # Cement frame — two posts + lintel on each face of the portal (4 posts total)
    frame_t = 16  # post/lintel thickness
    frame_d = 12  # depth of frame slab (centred on each portal face)
    ex1 = dorm_exit_xc - dorm_exit_hw
    ex2 = dorm_exit_xc + dorm_exit_hw
    portal_top = dorm_exit_z0 + 112
    # px_w=4 px_h=2 → "EXIT" is 76 units wide × 12 tall; centred on 160-wide lintel
    exit_px_w, exit_px_h, exit_depth = 4, 2, 2
    # Embed each letter 1 unit into its backing surface so the letter's back face is
    # never coplanar with the beam/lintel face (coplanar faces z-fight in qbsp, which
    # garbles the corner letters). exit_total = visible standoff (exit_depth) + embed.
    exit_embed = 1
    exit_total = exit_depth + exit_embed
    exit_text_w = (
        4 * 5 - 1
    ) * exit_px_w  # 76 units (4 chars × 5-col cell − trailing gap)
    exit_x0 = dorm_exit_xc - exit_text_w // 2
    exit_z_base = (
        portal_top + (frame_t - 6 * exit_px_h) // 2
    )  # vertically centred in lintel
    for face_yc, out_sign in [
        (dorm_exit_yc - dorm_exit_hw, -1),  # south face — letters protrude south
        (dorm_exit_yc + dorm_exit_hw, +1),  # north face — letters protrude north
    ]:
        fy1 = face_yc - frame_d // 2
        fy2 = face_yc + frame_d // 2
        for bx1, bx2, bz1, bz2 in [
            (ex1 - frame_t, ex1, dorm_exit_z0, portal_top + frame_t),  # left post
            (ex2, ex2 + frame_t, dorm_exit_z0, portal_top + frame_t),  # right post
            (ex1 - frame_t, ex2 + frame_t, portal_top, portal_top + frame_t),  # lintel
        ]:
            ENTITIES.append(
                brush_ent(
                    "func_detail", box(bx1, fy1, bz1, bx2, fy2, bz2, Textures.CEMENT)
                )
            )
        # Pixel-font "EXIT" letters raised on the outward lintel face.
        # Same handedness rule as the Knott Hall sign / bridge fascia:
        #   south-facing (protrudes -Y) → normal text, mirror=False
        #   north-facing (protrudes +Y) → reversed text, mirror=True
        # Back face is recessed into the lintel slab (exit_embed) to avoid z-fighting.
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
    # Cross beams — run in Y across the top, left and right, connecting both face frames
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
    # "EXIT" letters on the west and east cross-beam faces (text advances in +Y).
    # West face is read facing east (viewer-left = +Y) → reversed text, mirror=True.
    # East face is read facing west (viewer-left = -Y) → normal text, mirror=False.
    # Back face is recessed into the cross-beam (exit_embed) to avoid z-fighting.
    # These faces use the glowing lava texture: the metal letter texture rendered
    # dark/garbled on the dense "E" glyph here, while the fullbright lava reads
    # cleanly and suits the teleport-portal theme.
    exit_y0 = dorm_exit_yc - exit_text_w // 2
    for x_face, letter_text, do_mirror in [
        (ex1 - frame_t - exit_depth, "EXIT"[::-1], True),  # west face
        (ex2 + frame_t - exit_embed, "EXIT", False),  # east face
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

    ENTITIES.append(
        ent(
            "info_intermission",
            origin=f"-361 -500 350",  # south of bridge center, slightly elevated
            mangle="-10 75 0",  # pitch=-10 (nearly level), yaw=75 (mostly north, nudged east)
        )
    )

    return BRUSHES, ENTITIES
