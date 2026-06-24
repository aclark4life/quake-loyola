from . import constants
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
    BRIDGE_DECK_Z = (
        constants.deck_top_z(0) + 8
    )  # centre of arch deck + a bit (spawn/item height)
    ROAD_Z = constants.FLOOR_Z2 + 8

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
    for floor_index in range(constants.KNOTT.floors):
        fz1 = constants.KNOTT_GROUND_Z + floor_index * constants.KNOTT.floor_h
        item_z = fz1 + constants.KNOTT.wall_t + 24
        light_z = fz1 + constants.KNOTT.floor_h - 24  # near ceiling
        split = constants.KNOTT_ROOM_SPLITS[floor_index]
        sr_yc = (constants.KNOTT_BIY1 + split) // 2
        nr_yc = (split + constants.KNOTT.wall_t + constants.KNOTT_BIY2) // 2
        for side_xc in [constants.KNOTT_WEST_ROOM_CX, constants.KNOTT_EAST_ROOM_CX]:
            for ryc in [sr_yc, nr_yc]:
                # If west room north items land within 64 units of stairwell south wall, push south
                safe_ryc = ryc
                if (
                    side_xc == constants.KNOTT_WEST_ROOM_CX
                    and ryc == nr_yc
                    and nr_yc > constants.KNOTT_STAIRS_Y1 - 64
                ):
                    safe_ryc = constants.KNOTT_STAIRS_Y1 - 80
                ENTITIES.append(
                    ent("light", origin=f"{side_xc} {safe_ryc} {light_z}", light="250")
                )
                # Extra fill light at lower mid-height to reduce dark corners
                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{side_xc} {safe_ryc} {fz1 + constants.KNOTT.floor_h // 2}",
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
    west_stair_center_x = (
        constants.KNOTT_STAIRS_X1 + constants.KNOTT_STAIRS_X2
    ) // 2  # X centre of shaft
    west_stair_north_y = (
        constants.KNOTT_STAIRS_MID_Y + constants.KNOTT_STAIRS_Y2
    ) // 2  # Y centre of north lane
    west_stair_south_y = (
        constants.KNOTT_STAIRS_Y1 + constants.KNOTT_STAIRS_MID_Y
    ) // 2  # Y centre of south lane
    for floor_index in range(constants.KNOTT.floors):
        west_stair_light_z = (
            constants.KNOTT_GROUND_Z
            + floor_index * constants.KNOTT.floor_h
            + constants.KNOTT.floor_h
            - 24
        )  # near ceiling
        west_stair_mid_z = (
            constants.KNOTT_GROUND_Z
            + floor_index * constants.KNOTT.floor_h
            + constants.KNOTT.floor_h // 2
        )  # mid-flight
        west_stair_low_z = (
            constants.KNOTT_GROUND_Z
            + floor_index * constants.KNOTT.floor_h
            + constants.KNOTT.floor_h // 4
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
    hall_center_x = (
        constants.KNOTT_ENT_X1 + constants.KNOTT_ENT_X2
    ) // 2  # hallway centre X
    hall_light_ys = [
        constants.KNOTT_BIY1 + (constants.KNOTT_BIY2 - constants.KNOTT_BIY1) * i // 4
        for i in range(1, 4)  # quarters: 25%, 50%, 75%
    ] + [
        constants.KNOTT_BIY1
        + (constants.KNOTT_BIY2 - constants.KNOTT_BIY1) // 8,  # 12.5% (near south end)
        constants.KNOTT_BIY1
        + (constants.KNOTT_BIY2 - constants.KNOTT_BIY1)
        * 7
        // 8,  # 87.5% (near north end)
    ]
    for floor_index in range(constants.KNOTT.floors):
        hall_light_z = (
            constants.KNOTT_GROUND_Z
            + floor_index * constants.KNOTT.floor_h
            + constants.KNOTT.floor_h
            - 24
        )
        for hall_y in hall_light_ys:
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{hall_center_x} {hall_y} {hall_light_z}",
                    light="200",
                )
            )

    # ── Entrance corridor lights — one per floor in each doorway ─────────────────
    entry_corridor_y = constants.KNOTT.y2 - 48  # just inside north face
    for floor_index in range(constants.KNOTT.floors):
        entry_corridor_light_z = (
            constants.KNOTT_GROUND_Z
            + floor_index * constants.KNOTT.floor_h
            + constants.KNOTT.floor_h
            - 24
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

    for floor_index in range(constants.KNOTT.floors):
        fz1 = constants.KNOTT_GROUND_Z + floor_index * constants.KNOTT.floor_h
        fz_surf = fz1 + constants.KNOTT.wall_t
        split = constants.KNOTT_ROOM_SPLITS[floor_index]
        shelf_x_offset = shelf_offsets[floor_index]

        for shelf_center_x in [
            constants.KNOTT_WEST_ROOM_CX,
            constants.KNOTT_EAST_ROOM_CX,
        ]:
            # South room: shelf against south wall — front faces south (-Y)
            shelf_x = shelf_center_x + shelf_x_offset
            ENTITIES.append(
                brush_ent(
                    "func_detail",
                    [
                        box(
                            shelf_x - KNOTT_SHELF_W // 2,
                            constants.KNOTT_BIY1,
                            fz_surf,
                            shelf_x + KNOTT_SHELF_W // 2,
                            constants.KNOTT_BIY1 + KNOTT_SHELF_D,
                            fz_surf + KNOTT_SHELF_H,
                            "shelf_1",
                        )
                    ],
                )
            )
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{shelf_x} {constants.KNOTT_BIY1 + 32} {fz_surf + KNOTT_SHELF_H + 24}",
                    light="180",
                )
            )

    if not constants.KNOTT_ENABLED:
        del ENTITIES[knott_entity_start:]

    # Teleport destinations — west arch ↔ east arch
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_east",
            origin=f"{(constants.DORM.x1 + constants.DORM.x2) // 2} {(constants.DORM_NORTH_Y1 + constants.DORM_NORTH_Y2) // 2} {int(constants.DORM_RIDGE_Z + 40)}",
            angle="270",  # facing south toward the bridge
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_west",
            origin="2149 -264 904",
            angle="180",  # facing west, on KH rooftop
        )
    )

    # West arch trigger → east destination
    west_brushes = arch_fill(
        constants.WORLD_X1 + constants.WALL_T,
        constants.WORLD_X1 + constants.WALL_T + constants.ARCH_SLAB_W,
        0.0,
        constants.BRIDGE_DZ2,
        constants.ARCH_RIN,
        constants.A_SEGS,
        constants.Textures.TELEPORT,
        stilt_h=constants.ARCH_STILT_H,
    )
    ENTITIES.append(brush_ent("trigger_teleport", west_brushes, target="dest_east"))
    ENTITIES.append(brush_ent("func_illusionary", west_brushes))

    # West lower trigger (ground floor — simple box between posts)
    wlx1 = constants.WORLD_X1 + constants.WALL_T
    wlx2 = wlx1 + constants.ARCH_SLAB_W
    west_lower = [
        box(
            wlx1,
            -constants.ARCH_RIN,
            constants.FLOOR_Z2,
            wlx2,
            constants.ARCH_RIN,
            constants.BRIDGE_DZ2,
            constants.Textures.TELEPORT,
        )
    ]
    ENTITIES.append(brush_ent("trigger_teleport", west_lower, target="dest_east"))
    ENTITIES.append(brush_ent("func_illusionary", west_lower))

    # East arch trigger → west destination (shifted south to match angled span)
    east_brushes = arch_fill(
        constants.WORLD_X2 - constants.WALL_T - constants.ARCH_SLAB_W,
        constants.WORLD_X2 - constants.WALL_T,
        constants.BRIDGE_EAST_SHIFT_END,
        constants.BRIDGE_DZ2,
        constants.ARCH_RIN,
        constants.A_SEGS,
        constants.Textures.TELEPORT,
        stilt_h=constants.ARCH_STILT_H,
    )
    ENTITIES.append(brush_ent("trigger_teleport", east_brushes, target="dest_west"))
    ENTITIES.append(brush_ent("func_illusionary", east_brushes))

    # East lower trigger (ground floor — teleports up to bridge deck above)
    elx1 = constants.WORLD_X2 - constants.WALL_T - constants.ARCH_SLAB_W
    elx2 = constants.WORLD_X2 - constants.WALL_T
    east_lower_deck_x = elx1 - 64  # west of the arch, on the flat deck approach
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_east_deck",
            origin=f"{east_lower_deck_x} {int(constants.BRIDGE_EAST_SHIFT_END)} {int(constants.BRIDGE_DZ2 + 40)}",
            angle="180",  # facing west, on bridge deck east end
        )
    )
    east_lower = [
        box(
            elx1,
            constants.BRIDGE_EAST_SHIFT_END - constants.ARCH_RIN,
            constants.FLOOR_Z2,
            elx2,
            constants.BRIDGE_EAST_SHIFT_END + constants.ARCH_RIN,
            constants.BRIDGE_DZ2,
            constants.Textures.TELEPORT,
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
            origin=f"{(constants.DORM.x1 + constants.DORM.x2) // 2} {(constants.DORM_SOUTH1_Y1 + constants.DORM_SOUTH1_Y2) // 2} {int(constants.DORM_RIDGE_Z + constants.SDORM_LIFT + 40)}",
            angle="90",  # facing north, at top of A-frame ridge
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_dorm_roof",
            origin=f"{(constants.DORM.x1 + constants.DORM.x2) // 2} {(constants.DORM_NORTH_Y1 + constants.DORM_NORTH_Y2) // 2} {int(constants.DORM_RIDGE_Z + 40)}",
            angle="270",  # facing south, at top of A-frame ridge
        )
    )

    CHARLES_ARCH_TRIG_INSET = 8  # push trigger away from world walls and road surface

    for arch_y1, arch_y2, trigger_y1, trigger_y2, arch_target in [
        (
            constants.CHARLES_Y1,
            constants.CHARLES_Y1 + CHARLES_ARCH_W,
            constants.CHARLES_Y1 + CHARLES_ARCH_TRIG_INSET,
            constants.CHARLES_Y1 + CHARLES_ARCH_W,
            "dest_south_dorm_roof",
        ),  # south arch → south dorm rooftop
        (
            constants.CHARLES_Y2 - CHARLES_ARCH_W,
            constants.CHARLES_Y2,
            constants.CHARLES_Y2 - CHARLES_ARCH_W,
            constants.CHARLES_Y2 - CHARLES_ARCH_TRIG_INSET,
            "dest_dorm_roof",
        ),  # north arch → dorm rooftop
    ]:
        # Box trigger — covers only the walkable passage (below the arch crown)
        # so players can stand on the stone arch ring without being teleported.
        north_south_trigger_brushes = [
            box(
                -CHARLES_ARCH_RIN + CHARLES_ARCH_TRIG_INSET,
                trigger_y1,
                constants.FLOOR_Z2,
                CHARLES_ARCH_RIN - CHARLES_ARCH_TRIG_INSET,
                trigger_y2,
                constants.FLOOR_Z2 + CHARLES_ARCH_STILT + 128,
                constants.Textures.TELEPORT,
            )
        ]
        ENTITIES.append(
            brush_ent(
                "trigger_teleport", north_south_trigger_brushes, target=arch_target
            )
        )
        # Arch-shaped illusionary fill so the teleport glow looks like an arch
        north_south_glow_brushes = arch_fill_y(
            arch_y1,
            arch_y2,
            0.0,
            constants.FLOOR_Z2 + 4,
            CHARLES_ARCH_RIN,
            constants.A_SEGS,
            constants.Textures.TELEPORT,
            stilt_h=CHARLES_ARCH_STILT,
        )
        ENTITIES.append(brush_ent("func_illusionary", north_south_glow_brushes))

    # Stone arch surrounds for north & south Charles Street arches
    CHARLES_ARCH_ROUT = 312  # outer radius
    CHARLES_ARCH_SEGS = 24  # smoother than the global A_SEGS = 16
    charles_arch_top_z = constants.FLOOR_Z2 + CHARLES_ARCH_STILT + CHARLES_ARCH_RIN
    for arch_y1, arch_y2 in [
        (constants.CHARLES_Y1, constants.CHARLES_Y1 + CHARLES_ARCH_W),
        (constants.CHARLES_Y2 - CHARLES_ARCH_W, constants.CHARLES_Y2),
    ]:
        ENTITIES.append(
            brush_ent(
                "func_detail",
                arch_wall_y(
                    arch_y1,
                    arch_y2,
                    constants.WORLD_X1 + constants.WALL_T,
                    constants.WORLD_X2 - constants.WALL_T,
                    constants.FLOOR_Z2,
                    charles_arch_top_z,
                    CHARLES_ARCH_RIN,
                    CHARLES_ARCH_ROUT,
                    CHARLES_ARCH_SEGS,
                    constants.Textures.PILLAR,
                    stilt_h=CHARLES_ARCH_STILT,
                ),
            )
        )

    # Both arches → top of Knott Hall rooftop.
    # Each arch spans the road opening and glows with teleport texture.
    ENNIS_ARCH_STILT = 64
    KH_DRIVE_ARCH_STILT = 64
    ARCH_TRIG_INSET = 8  # keep triggers off the walls/floor

    kh_drive_cx = (constants.KNOTT_DRIVEWAY_RD_X1 + constants.KNOTT_DRIVEWAY_RD_X2) // 2

    # Destinations — both land on KH rooftop, facing west
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_ennis_east",
            origin="2149 -264 904",
            angle="180",  # facing west
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_kh_drive_south",
            origin="2149 -264 904",
            angle="180",  # facing west
        )
    )

    # Ennis east arch (X-aligned, at the east world wall)
    ennis_arch_x1 = constants.WORLD_X2_EXT - constants.WALL_T - constants.ARCH_SLAB_W
    ennis_arch_x2 = constants.WORLD_X2_EXT - constants.WALL_T
    ennis_arch_top_z = constants.FLOOR_Z2 + ENNIS_ARCH_STILT + constants.ENNIS_HW
    ennis_east_trigger = [
        box(
            ennis_arch_x1,
            constants.ENNIS_Y - constants.ENNIS_HW + ARCH_TRIG_INSET,
            constants.FLOOR_Z2 + 4,
            ennis_arch_x2,
            constants.ENNIS_Y + constants.ENNIS_HW - ARCH_TRIG_INSET,
            ennis_arch_top_z,
            constants.Textures.TELEPORT,
        )
    ]
    ENTITIES.append(
        brush_ent("trigger_teleport", ennis_east_trigger, target="dest_kh_drive_south")
    )
    ennis_east_glow = arch_fill(
        ennis_arch_x1,
        ennis_arch_x2,
        float(constants.ENNIS_Y),
        constants.FLOOR_Z2,
        constants.ENNIS_HW,
        constants.A_SEGS,
        constants.Textures.TELEPORT,
        stilt_h=ENNIS_ARCH_STILT,
    )
    ENTITIES.append(brush_ent("func_illusionary", ennis_east_glow))

    # Stone arch surround — X-aligned, freestanding at the east Ennis wall
    ENNIS_ARCH_ROUT = constants.ENNIS_HW + 56
    ennis_stone_arch = arch_wall(
        ennis_arch_x1,
        ennis_arch_x2,
        constants.ENNIS_Y - ENNIS_ARCH_ROUT,
        constants.ENNIS_Y + ENNIS_ARCH_ROUT,
        constants.FLOOR_Z2,
        ennis_arch_top_z,
        constants.ENNIS_HW,
        ENNIS_ARCH_ROUT,
        constants.A_SEGS,
        constants.Textures.PILLAR,
        stilt_h=ENNIS_ARCH_STILT,
        yc=float(constants.ENNIS_Y),
        freestanding=True,
    )
    ENTITIES.append(brush_ent("func_detail", ennis_stone_arch))

    # KH driveway south arch (Y-aligned, flush with the south world wall)
    kh_arch_y1 = constants.CHARLES_Y1
    kh_arch_y2 = constants.CHARLES_Y1 + constants.ARCH_SLAB_W
    kh_arch_top_z = (
        constants.KNOTT_DRIVEWAY_ZT_S
        + KH_DRIVE_ARCH_STILT
        + constants.KNOTT.driveway_hw
    )
    kh_drive_trigger = [
        box(
            kh_drive_cx - constants.KNOTT.driveway_hw + ARCH_TRIG_INSET,
            kh_arch_y1,
            constants.KNOTT_DRIVEWAY_ZT_S + 4,
            kh_drive_cx + constants.KNOTT.driveway_hw - ARCH_TRIG_INSET,
            kh_arch_y2,
            kh_arch_top_z,
            constants.Textures.TELEPORT,
        )
    ]
    ENTITIES.append(
        brush_ent("trigger_teleport", kh_drive_trigger, target="dest_ennis_east")
    )
    kh_drive_glow = arch_fill_y(
        kh_arch_y1,
        kh_arch_y2,
        float(kh_drive_cx),
        constants.KNOTT_DRIVEWAY_ZT_S,
        constants.KNOTT.driveway_hw,
        constants.A_SEGS,
        constants.Textures.TELEPORT,
        stilt_h=KH_DRIVE_ARCH_STILT,
    )
    ENTITIES.append(brush_ent("func_illusionary", kh_drive_glow))

    # Stone arch surround — Y-aligned, freestanding at the KH driveway south end
    KH_ARCH_ROUT = constants.KNOTT.driveway_hw + 56
    kh_stone_arch = arch_wall_y(
        kh_arch_y1,
        kh_arch_y2,
        kh_drive_cx - KH_ARCH_ROUT,
        kh_drive_cx + KH_ARCH_ROUT,
        constants.KNOTT_DRIVEWAY_ZT_S,
        kh_arch_top_z,
        constants.KNOTT.driveway_hw,
        KH_ARCH_ROUT,
        constants.A_SEGS,
        constants.Textures.PILLAR,
        stilt_h=KH_DRIVE_ARCH_STILT,
        xc=float(kh_drive_cx),
    )
    ENTITIES.append(brush_ent("func_detail", kh_stone_arch))

    ENTITIES.append(
        ent(
            "info_player_start",
            origin=f"{constants.KNOTT_CX} {constants.BRIDGE.y1 + constants.BRIDGE_PAR_W + 32} {int(constants.BRIDGE_DZ2 + 24)}",
            angle="180",
        )
    )

    knott_cy = (
        constants.KNOTT.y1 + constants.KNOTT.y2
    ) // 2  # Knott Hall center Y = -528
    DORM_NORTH_CY = (
        constants.DORM_NORTH_Y1 + constants.DORM_NORTH_Y2
    ) // 2  # north building center Y
    DORM_CX = (constants.DORM.x1 + constants.DORM.x2) // 2  # west buildings center X
    DORM_SOUTH1_CY = (
        constants.DORM_SOUTH1_Y1 + constants.DORM_SOUTH1_Y2
    ) // 2  # south building 1 center Y
    DORM_SOUTH2_CY = (
        constants.DORM_SOUTH2_Y1 + constants.DORM_SOUTH2_Y2
    ) // 2  # south building 2 center Y

    # ── Deathmatch spawns — spread across all areas ──────────────────────────
    for pos, angle in [
        # Bridge deck
        ((0, 0, int(constants.deck_top_z(0) + 32)), 180),
        ((-200, 0, int(constants.deck_top_z(-200) + 32)), 90),
        ((200, 0, int(constants.deck_top_z(200) + 32)), 270),
        ((-400, 0, int(constants.deck_top_z(-400) + 32)), 90),
        ((400, 0, int(constants.deck_top_z(400) + 32)), 270),
        # Walkway
        *(
            [
                (
                    (
                        constants.KNOTT_CX,
                        (constants.BRIDGE.y1 + constants.KNOTT.y2) // 2,
                        int(constants.WALK_ZT1 + 32),
                    ),
                    180,
                )
            ]
            if constants.KNOTT_ENABLED
            else []
        ),
        # Knott Hall — ground, mid, upper floors
        *(
            [
                (
                    (
                        (constants.KNOTT_ENT_X1 + constants.KNOTT_ENT_X2) // 2,
                        constants.KNOTT.y2 - 80,
                        constants.KNOTT_GROUND_Z + 40,
                    ),
                    180,
                ),  # entrance hallway, north
                (
                    (
                        constants.KNOTT_CX - 100,
                        knott_cy,
                        constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h + 40,
                    ),
                    270,
                ),
                (
                    (
                        constants.KNOTT_CX + 100,
                        knott_cy,
                        constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 2 + 40,
                    ),
                    90,
                ),
                (
                    (
                        constants.KNOTT_CX,
                        constants.KNOTT.y1 + 100,
                        constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 3 + 40,
                    ),
                    0,
                ),
                (
                    (
                        constants.KNOTT_CX,
                        knott_cy,
                        constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 4 + 40,
                    ),
                    180,
                ),
                # Knott Hall rooftop
                ((constants.KNOTT_CX, knott_cy, constants.KNOTT_Z2 + 40), 180),
            ]
            if constants.KNOTT_ENABLED
            else []
        ),
        # Charles Street
        ((0, 300, ROAD_Z + 24), 180),
        ((0, -400, ROAD_Z + 24), 0),
        ((0, DORM_SOUTH1_CY, ROAD_Z + 24), 270),
        # North building interior
        ((DORM_CX, DORM_NORTH_CY, constants.FLOOR_Z2 + 40), 90),
        (
            (DORM_CX, DORM_NORTH_CY, constants.FLOOR_Z2 + constants.DORM.floor_h + 40),
            90,
        ),
        # North building roof ridge
        ((DORM_CX, DORM_NORTH_CY, int(constants.DORM_RIDGE_Z + 40)), 90),
        # South buildings interiors
        ((DORM_CX, DORM_SOUTH1_CY, constants.FLOOR_Z2 + constants.SDORM_LIFT + 40), 90),
        ((DORM_CX, DORM_SOUTH2_CY, constants.FLOOR_Z2 + constants.SDORM_LIFT + 40), 90),
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
    if constants.KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_rocketlauncher",
                origin=f"{constants.KNOTT_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 3 + 40}",
            )
        )
    # Rocket launcher — west arch, north side
    ENTITIES.append(
        ent(
            "weapon_rocketlauncher",
            origin=f"{constants.BRIDGE_ARCH_X[1]} {constants.BRIDGE.y1 - 48} {BRIDGE_DECK_Z}",
        )
    )
    # Remaining rocket launchers
    for rl_origin in [
        f"{constants.ROAD_X2 + 40} {constants.ENNIS_Y - constants.ENNIS_HW - 200} {ROAD_Z + 24}",  # east sidewalk, south of Ennis
        f"{constants.BRIDGE_ARCH_X[2]} 0 {ROAD_Z + 24}",  # under bridge, mid span
        f"{int(constants.ENNIS_GATE_X1 + (constants.ENNIS_GATE_X2 - constants.ENNIS_GATE_X1) // 2)} {constants.ENNIS_WALL_NY - 80} {constants.FLOOR_Z2 + 24}",  # Ennis fence midpoint
        f"{int(constants.ENNIS_CEMENT_X1 + (constants.ENNIS_CEMENT_X2 - constants.ENNIS_CEMENT_X1) // 2)} {constants.ENNIS_WALL_NY - 80} {constants.FLOOR_Z2 + 24}",  # Ennis wall midpoint
        # Bridge deck — one per span
        f"{(constants.BRIDGE.x1 + constants.BRIDGE_ARCH_X[0]) // 2} 0 {BRIDGE_DECK_Z}",  # span 1
        f"{(constants.BRIDGE_ARCH_X[0] + constants.BRIDGE_ARCH_X[1]) // 2} {constants.BRIDGE.y2 - 24} {BRIDGE_DECK_Z}",  # span 2 south edge
        f"{(constants.BRIDGE_ARCH_X[2] + constants.BRIDGE.x2) // 2} 0 {BRIDGE_DECK_Z}",  # span 4
        f"{(constants.BRIDGE.x2 + constants.BRIDGE_ARCH_X[4]) // 2} 0 {BRIDGE_DECK_Z}",  # span 5 (east angled)
    ]:
        ENTITIES.append(ent("weapon_rocketlauncher", origin=rl_origin))

    # Super shotgun — spread around mid-tier locations
    if constants.KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_supershotgun",
                origin=f"{constants.KNOTT_EAST_ROOM_CX} {constants.KNOTT.y2 - 80} {constants.KNOTT_GROUND_Z + 40}",
            )
        )
    ENTITIES.append(
        ent("weapon_supershotgun", origin=f"300 300 {ROAD_Z + 24}")
    )  # east sidewalk
    ENTITIES.append(
        ent(
            "weapon_supershotgun",
            origin=f"{DORM_CX} {DORM_SOUTH1_CY} {constants.FLOOR_Z2 + constants.SDORM_LIFT + 40}",
        )
    )

    # Grenade launcher — Knott Hall floor 2, south building 2
    if constants.KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_grenadelauncher",
                origin=f"{constants.KNOTT_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 2 + 40}",
            )
        )
    ENTITIES.append(
        ent(
            "weapon_grenadelauncher",
            origin=f"{DORM_CX} {DORM_SOUTH2_CY} {constants.FLOOR_Z2 + constants.SDORM_LIFT + 40}",
        )
    )

    # Nailgun — bridge approaches, Charles Street
    ENTITIES.append(ent("weapon_nailgun", origin=f"-600 0 {ROAD_Z + 24}"))
    ENTITIES.append(ent("weapon_nailgun", origin=f"600 0 {ROAD_Z + 24}"))
    if constants.KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_nailgun",
                origin=f"{constants.KNOTT_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h + 40}",
            )
        )

    # Lightning gun — high-value, contested spots
    ENTITIES.append(
        ent("weapon_lightning", origin=f"200 0 {BRIDGE_DECK_Z}")
    )  # bridge centre
    ENTITIES.append(
        ent(
            "weapon_lightning",
            origin=f"{DORM_CX} {DORM_NORTH_CY} {int(constants.DORM_RIDGE_Z + 40)}",
        )
    )  # north dorm roof
    if constants.KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_lightning",
                origin=f"{constants.KNOTT_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 4 + 40}",
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
            origin=f"{DORM_CX} {DORM_SOUTH1_CY} {constants.FLOOR_Z2 + constants.SDORM_LIFT + 40}",
            angle="90",
        )
    )
    # Knott Hall floors
    if constants.KNOTT_ENABLED:
        ENTITIES.append(
            ent(
                "monster_ogre",
                origin=f"{constants.KNOTT_WEST_ROOM_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 2 + 40}",
                angle="90",
            )
        )
        ENTITIES.append(
            ent(
                "monster_ogre",
                origin=f"{constants.KNOTT_EAST_ROOM_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 3 + 40}",
                angle="270",
            )
        )
        # KH rooftop
        ENTITIES.append(
            ent(
                "monster_ogre",
                origin=f"{constants.KNOTT_CX} {knott_cy} {constants.KNOTT_Z2 + 40}",
                angle="180",
            )
        )

    # ── Ammo ──────────────────────────────────────────────────────────────────
    for ax in constants.BRIDGE_ARCH_X:
        ENTITIES.append(
            ent("item_rockets", origin=f"{ax} 0 {int(constants.deck_top_z(ax) + 8)}")
        )
    for rx in [400, 800]:
        ENTITIES.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z + 24}"))
        ENTITIES.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z + 24}"))
    for kf in range(1, constants.KNOTT.floors):
        ENTITIES.append(
            ent(
                "item_rockets",
                origin=f"{constants.KNOTT_CX + 80} {knott_cy} {constants.KNOTT_GROUND_Z + kf * constants.KNOTT.floor_h + 40}",
            )
        )
    ENTITIES.append(
        ent("item_shells", origin=f"-300 -300 {ROAD_Z + 24}")
    )  # west sidewalk
    ENTITIES.append(
        ent(
            "item_shells", origin=f"{DORM_CX} {DORM_NORTH_CY} {constants.FLOOR_Z2 + 40}"
        )
    )
    ENTITIES.append(ent("item_spikes", origin=f"-400 200 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_spikes", origin=f"400 -200 {ROAD_Z + 24}"))

    # ── Health & Armor ────────────────────────────────────────────────────────
    # Health — scattered throughout
    ENTITIES.append(ent("item_health", origin=f"0 0 {BRIDGE_DECK_Z}"))
    ENTITIES.append(
        ent(
            "item_health",
            origin=f"{constants.KNOTT_EAST_ROOM_CX} {constants.KNOTT.y2 - 64} {constants.KNOTT_GROUND_Z + 40}",
        )
    )
    ENTITIES.append(
        ent(
            "item_health",
            origin=f"{constants.KNOTT_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 2 + 40}",
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
            origin=f"{DORM_CX} {DORM_SOUTH2_CY} {constants.FLOOR_Z2 + constants.SDORM_LIFT + 40}",
        )
    )
    # Armor — contested locations
    ENTITIES.append(
        ent("item_armor1", origin=f"-200 0 {BRIDGE_DECK_Z}")
    )  # yellow armor on bridge
    ENTITIES.append(
        ent(
            "item_armor2",
            origin=f"{constants.KNOTT_CX} {knott_cy} {constants.KNOTT_GROUND_Z + constants.KNOTT.floor_h * 4 + 40}",
        )
    )  # red armor top floor
    ENTITIES.append(
        ent(
            "item_armorInv",
            origin=f"{DORM_CX} {DORM_NORTH_CY} {int(constants.DORM_RIDGE_Z + 40)}",
        )
    )  # mega armor on roof ridge (teleport reward)

    # Torch lights on pillar caps
    if constants.SHOW_SUPPORTS:
        for px in constants.BRIDGE_ARCH_X:
            if (
                constants.SHOW_SUPPORTS is not True
                and px not in constants.SHOW_SUPPORTS
            ):
                continue
            pbase = constants.deck_top_z(px)
            pcap = (
                pbase
                + constants.BRIDGE.parapet_h
                + constants.BRIDGE_PIL_EXTRA
                + constants.BRIDGE_PIL_CAP_H
                + constants.BRIDGE_PIL_PYR_H
            )  # top of pyramid
            cy_n = (
                constants.BRIDGE.y2 - constants.BRIDGE_PAR_W // 2
            )  # centred on north pillar cap
            cy_s = (
                constants.BRIDGE.y1 + constants.BRIDGE_PAR_W // 2
            )  # centred on south pillar cap
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
                    constants.Textures.SKY,
                )
                ENTITIES.append(brush_ent("trigger_hurt", [fhb], dmg="10"))

    # Pillar base uplights — ground-level spots wash light up the pier faces
    if constants.SHOW_SUPPORTS:
        for px in constants.BRIDGE_ARCH_X:
            if (
                constants.SHOW_SUPPORTS is not True
                and px not in constants.SHOW_SUPPORTS
            ):
                continue
            for underbridge_light_y in [
                constants.BRIDGE.y2 + 30,
                constants.BRIDGE.y1 - 30,
            ]:
                # Skip abutment-pier positions buried in solid building geometry
                if px == constants.BRIDGE_ARCH_X[0]:
                    continue
                if (
                    px == constants.BRIDGE_ARCH_X[-1]
                    and underbridge_light_y == constants.BRIDGE.y1 - 30
                ):
                    continue
                ENTITIES.append(
                    ent("light", origin=f"{px} {underbridge_light_y} 16", light="200")
                )

    # Campus lamp post lights — flame above brick cup, matching bridge pillar torches
    for lamp_x in constants.CHARLES_LAMP_POST_XS:
        for lamp_y in constants.CHARLES_LAMP_POST_YS:
            pole_top_z = constants.FLOOR_Z2 + constants.CHARLES_LAMP_POST_H
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
    for lamp_x, lamp_y, lamp_z in constants.ENNIS_CEMENT_LAMP_POSTS:
        ENTITIES.append(ent("light", origin=f"{lamp_x} {lamp_y} {lamp_z}", light="300"))
        ENTITIES.append(
            ent("light_flame_large_yellow", origin=f"{lamp_x} {lamp_y} {lamp_z + 4}")
        )

    # Ennis entrance pillar torches — flame above brick cup on each stone pillar
    ennis_pil_flame_z = (
        constants.ENNIS_PIL_ZB
        + constants.ENNIS_PIL_POST_H
        + constants.ENNIS_PIL_CAP_H
        + constants.ENNIS_PIL_BELL2_H
        + 20
    )
    ennis_pil_cx = constants.ENNIS_PIL_X1 + constants.ENNIS_PIL_HW
    for pillar_y in (
        constants.ENNIS_Y - constants.ENNIS_HW - constants.ENNIS_PIL_HW,
        constants.ENNIS_Y + constants.ENNIS_HW + constants.ENNIS_PIL_HW,
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
    for pier_x in constants.BRIDGE_PEND_XS:
        ENTITIES.append(
            ent(
                "light",
                origin=f"{pier_x} 0 {int(constants.deck_bot_z(pier_x)) - 20}",
                light="350",
                style="1",
            )
        )

    # Pier base lights — illuminate plinths and arch openings from just inside each pier
    for pier_x in constants.BRIDGE_ARCH_X:
        # West abutment pier is embedded in solid building geometry — skip buried lights
        if pier_x == constants.BRIDGE_ARCH_X[0]:
            continue
        pier_light_z = (
            constants.FLOOR_Z2 + constants.BRIDGE_PIL_BASE_RAMP_H + 60
        )  # just above the plinth top, low in the arch
        ENTITIES.append(
            ent(
                "light",
                origin=f"{pier_x} {constants.BRIDGE.y2 // 2} {pier_light_z}",
                light="250",
            )
        )
        ENTITIES.append(
            ent(
                "light",
                origin=f"{pier_x} {constants.BRIDGE.y1 // 2} {pier_light_z}",
                light="250",
            )
        )

    # Cement arch on east face of abutment pier (-1246) — three lights for good coverage
    abutment_pier_x = min(constants.BRIDGE_ARCH_X)  # = -1246
    abutment_arch_z = (
        constants.FLOOR_Z2 + constants.BRIDGE_PIL_BASE_H + 60
    )  # mid-height of arch opening
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + constants.BRIDGE_PIL_HW + 32} 0 {abutment_arch_z}",
            light="700",
        )
    )
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + constants.BRIDGE_PIL_HW + 32} {constants.BRIDGE.y2 // 2} {abutment_arch_z}",
            light="500",
        )
    )
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + constants.BRIDGE_PIL_HW + 32} {constants.BRIDGE.y1 // 2} {abutment_arch_z}",
            light="500",
        )
    )

    # Light on underside of walkway slab illuminating the ramp below
    if constants.KNOTT_WALKWAY_ENABLED:
        walk_mid_y = (constants.BRIDGE.y1 + constants.KNOTT.y2) // 2
        walk_frac = (constants.BRIDGE.y1 - walk_mid_y) / float(
            constants.BRIDGE.y1 - constants.KNOTT.y2
        )
        wk_zb1 = constants.WALK_ZT1 - constants.KNOTT.wall_t
        wk_zb2 = constants.WALK_ZT2 - constants.KNOTT.wall_t
        walk_bot_mid = int(wk_zb1 + walk_frac * (wk_zb2 - wk_zb1))
        ENTITIES.append(
            ent(
                "light",
                origin=f"{constants.KNOTT_CX} {walk_mid_y} {walk_bot_mid - 8}",
                light="300",
            )
        )

    # Lift (func_plat) — rides from ground floor up through roof opening to rooftop
    if constants.KNOTT_ENABLED:
        lift_travel = constants.KNOTT_Z2 - (
            constants.KNOTT_GROUND_Z + constants.KNOTT.wall_t
        )
        lift_brush = [
            box(
                constants.KNOTT_SHAFT_X1 + 2,
                constants.KNOTT_SHAFT_Y1 + 2,
                constants.KNOTT_Z2 - 8,
                constants.KNOTT_SHAFT_X2 - 2,
                constants.KNOTT_SHAFT_Y2 - 2,
                constants.KNOTT_Z2,
                constants.Textures.FLOOR_KH,
            )
        ]
        ENTITIES.append(
            brush_ent("func_plat", lift_brush, height=str(lift_travel), speed="200")
        )

    # Interior lights for all campus dorm buildings (north1, north2, 2 south)
    _dorm_north2_y2 = constants.DORM_NORTH_Y1
    _dorm_north2_y1 = _dorm_north2_y2 - (
        constants.DORM_NORTH_Y2 - constants.DORM_NORTH_Y1
    )
    bldg_light_xs = [
        constants.DORM.x1 + (constants.DORM.x2 - constants.DORM.x1) * i // 4
        for i in [1, 2, 3]
    ]
    for building_y1, building_y2, building_lift in [
        (constants.DORM_NORTH_Y1, constants.DORM_NORTH_Y2, 0),
        (_dorm_north2_y1, _dorm_north2_y2, 0),
        (constants.DORM_SOUTH1_Y1, constants.DORM_SOUTH1_Y2, constants.SDORM_LIFT),
        (constants.DORM_SOUTH2_Y1, constants.DORM_SOUTH2_Y2, constants.SDORM_LIFT),
    ]:
        building_y = (building_y1 + building_y2) // 2
        for building_floor_index in range(constants.DORM.floors):
            building_light_z = (
                constants.FLOOR_Z2
                + building_lift
                + building_floor_index * constants.DORM.floor_h
                + constants.DORM.floor_h // 2
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
    if constants.KNOTT_ENABLED:
        for knott_floor_index in range(constants.KNOTT.floors):
            knott_light_z = (
                constants.KNOTT_GROUND_Z
                + knott_floor_index * constants.KNOTT.floor_h
                + constants.KNOTT.floor_h // 2
            )
            for knott_x_index in [1, 2, 3]:
                knott_light_x = (
                    constants.KNOTT.x1
                    + (constants.KNOTT.x2 - constants.KNOTT.x1) * knott_x_index // 4
                )
                for knott_y_index in [1, 2, 3, 4]:
                    knott_light_y = (
                        constants.KNOTT.y1
                        + (constants.KNOTT.y2 - constants.KNOTT.y1) * knott_y_index // 5
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
        (constants.ROAD_X1 - 200, constants.ENNIS_WALL_NY - 100),
        (constants.ROAD_X1 - 400, constants.ENNIS_WALL_NY - 80),
        (constants.ROAD_X1 - 600, constants.ENNIS_WALL_NY - 120),
    ]
    all_tree_brushes = []
    for tree_x, tree_y in tree_positions:
        all_tree_brushes += make_tree(tree_x, tree_y, constants.FLOOR_Z2)
    ENTITIES.append(brush_ent("func_detail", all_tree_brushes))

    # ── Giant trees along Charles Street — in front of Knott Hall only ───────────
    # 5 trees in 2 rows: row of 2 closer to street, row of 3 closer to KH.
    # Tree height matches Knott Hall (KNOTT_Z2).
    charles_tree_height = constants.KNOTT_Z2
    knott_tree_span = constants.KNOTT.y2 - constants.KNOTT.y1
    charles_tree_row_near_x = (
        constants.ROAD_X2 + constants.CHARLES_WALK_W + 300
    )  # closer to Charles St
    charles_tree_row_far_x = (
        constants.ROAD_X2 + constants.CHARLES_WALK_W + 560
    )  # closer to KH
    # Row of 2 — near row, 2 trees at 25% and 75% of KH Y span
    charles_tree_row2_ys = [
        int(constants.KNOTT.y1 + knott_tree_span * f) for f in (0.25, 0.75)
    ]
    # Row of 3 — far row, 3 trees at 15%, 50%, 85%
    charles_tree_row3_ys = [
        int(constants.KNOTT.y1 + knott_tree_span * f) for f in (0.15, 0.5, 0.85)
    ]
    charles_giant_tree_brushes = []
    for tree_y in charles_tree_row2_ys:
        charles_giant_tree_brushes += make_giant_tree(
            charles_tree_row_near_x, tree_y, constants.FLOOR_Z2, charles_tree_height
        )
    for tree_y in charles_tree_row3_ys:
        charles_giant_tree_brushes += make_giant_tree(
            charles_tree_row_far_x, tree_y, constants.FLOOR_Z2, charles_tree_height
        )
    ENTITIES.append(brush_ent("func_detail", charles_giant_tree_brushes))

    # ── Giant trees along KH driveway east side — from the bridge south ──────────
    # Big trees just outside the east sidewalk (KNOTT_DRIVEWAY_ES_X2), running south
    # to the KH south face (KNOTT_DRIVEWAY_Y1).  First tree is set one spacing-step
    # south of the bridge so its canopy clears the bridge deck.  Per-tree jitter in
    # X/Y/height (fixed seed) keeps the row natural rather than perfectly regular.
    # Z tracks the road slope in the KH section; flat at FLOOR_Z2 north of KH.
    import random as kh_tree_rng

    kh_tree_rng.seed(7)  # fixed seed for reproducible jittered layout
    kh_drive_tree_x = (
        constants.KNOTT_DRIVEWAY_ES_X2 + 80
    )  # centre clear of east sidewalk
    kh_drive_tree_spacing = 300
    kh_drive_tree_height = constants.KNOTT_Z2 + 40  # a touch taller than Knott Hall
    kh_drive_tree_brushes = []
    kh_grid_y = constants.BRIDGE.y1 - kh_drive_tree_spacing
    while kh_grid_y >= constants.KNOTT_DRIVEWAY_Y1:
        tree_x = kh_drive_tree_x + kh_tree_rng.randint(-40, 40)
        tree_y = kh_grid_y + kh_tree_rng.randint(-80, 80)
        tree_h = kh_drive_tree_height + kh_tree_rng.randint(-60, 60)
        if tree_y >= constants.KNOTT_DRIVEWAY_Y2:  # flat extension (north of KH)
            tree_z = constants.FLOOR_Z2
        else:  # sloped back-road section alongside KH
            kh_t = (constants.KNOTT_DRIVEWAY_Y2 - tree_y) / (
                constants.KNOTT_DRIVEWAY_Y2 - constants.KNOTT_DRIVEWAY_Y1
            )
            tree_z = int(
                constants.KNOTT_DRIVEWAY_ZT_N
                + kh_t * (constants.KNOTT_DRIVEWAY_ZT_S - constants.KNOTT_DRIVEWAY_ZT_N)
            )
        kh_drive_tree_brushes += make_giant_tree(tree_x, tree_y, tree_z, tree_h)
        kh_grid_y -= kh_drive_tree_spacing
    ENTITIES.append(brush_ent("func_detail", kh_drive_tree_brushes))

    # ── Medium trees in front of the south dorm, set back from Charles Street ─────
    # Two trees, bigger and spread wider: positioned at outer thirds of the full
    # south-dorm Y span and pulled further back (west) from the road.
    sdorm_front_tree_height = 520
    sdorm_front_tree_x = constants.ROAD_X1 - 400  # further back toward the dorm
    sdorm_front_tree_y1 = constants.DORM_SOUTH1_Y1 + 150  # near south end of dorm span
    sdorm_front_tree_y2 = constants.DORM_SOUTH2_Y2 - 150  # near north end of dorm span
    sdorm_front_tree_brushes = []
    for tree_y in (sdorm_front_tree_y1, sdorm_front_tree_y2):
        sdorm_front_tree_brushes += make_giant_tree(
            sdorm_front_tree_x, tree_y, constants.FLOOR_Z2, sdorm_front_tree_height
        )
    ENTITIES.append(brush_ent("func_detail", sdorm_front_tree_brushes))

    # ── Giant trees covering the entire east ground (east of Charles St sidewalk) ──
    # Scattered grid: base spacing ~350 units with per-tree random jitter up to
    # ±120 units in X and Y so the forest looks natural, not uniform.
    east_ground_tree_height = constants.KNOTT_Z2
    east_ground_spacing = 350
    east_ground_jitter = 120
    east_ground_buffer = 120  # clearance buffer from world edges / wall
    east_ground_x1 = constants.ROAD_X2 + constants.CHARLES_WALK_W + east_ground_buffer
    east_ground_x2 = constants.WORLD_X2_EXT - constants.WALL_T - east_ground_buffer
    east_ground_y1 = (
        constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 200
    )  # centered in north space (fence=1148, world=1696, mid≈1422)
    east_ground_y2 = constants.WORLD_Y2 - constants.WALL_T - east_ground_buffer

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
                tree_x, tree_y, constants.FLOOR_Z2, east_ground_tree_height
            )
            grid_y += east_ground_spacing
        grid_x += east_ground_spacing
    ENTITIES.append(brush_ent("func_detail", east_ground_giant_brushes))

    # ── Giant trees east of the teleport — randomised scatter, wider coverage ────
    # Randomly scattered across the full extended-east strip (WORLD_X2 → WORLD_X2_EXT),
    # south of Ennis drive down to the south world wall.
    # Rejection sampling enforces a minimum separation so trees don't overlap.
    east_side_tree_height = constants.KNOTT_Z2
    east_side_foliage_hw = 160  # widest foliage half-width (make_giant_tree)
    _world_x2_ext = constants.WORLD_X2 + 512  # WORLD_X2_EXT
    _ennis_south = constants.ENNIS_Y - constants.ENNIS_HW  # Ennis road south edge
    _ennis_sw_edge = (
        _ennis_south - 3 * constants.CHARLES_WALK_W - 32
    )  # Ennis south sidewalk edge
    east_tele_brushes = []
    et_x1 = (
        constants.WORLD_X2 + constants.WALL_T + east_side_foliage_hw + 20
    )  # foliage clears the world wall / teleport
    et_x2 = _world_x2_ext - constants.WALL_T - 80
    et_y1 = constants.WORLD_Y1 + constants.WALL_T + 120
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
                cx, cy, constants.FLOOR_Z2, east_side_tree_height
            )
    ENTITIES.append(brush_ent("func_detail", east_tele_brushes))

    bush_positions = [
        # Along north face of Ennis brick wall (campus grass side, not sidewalk)
        (
            (constants.ROAD_X2 + constants.CHARLES_WALK_W + 48) + 60,
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            (constants.ROAD_X2 + constants.CHARLES_WALK_W + 48) + 160,
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            (constants.ROAD_X2 + constants.CHARLES_WALK_W + 48) + 260,
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            (constants.ROAD_X2 + constants.CHARLES_WALK_W + 48) + 360,
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        # Along north face of iron fence
        (
            int(constants.ENNIS_GATE_X1 + 120),
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            int(constants.ENNIS_GATE_X1 + 300),
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            int(constants.ENNIS_GATE_X1 + 500),
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            int(constants.ENNIS_GATE_X1 + 700),
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        # Along north face of cement parapet wall
        (
            int(constants.ENNIS_CEMENT_X1 + 120),
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            int(constants.ENNIS_CEMENT_X1 + 320),
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        (
            int(constants.ENNIS_CEMENT_X1 + 560),
            constants.ENNIS_WALL_NY + constants.ENNIS_WALL_T + 40,
        ),
        # Along Knott Hall west face (outside building)
        (constants.KNOTT.x1 - 48, (constants.KNOTT.y1 + constants.KNOTT.y2) // 2 - 200),
        (constants.KNOTT.x1 - 48, (constants.KNOTT.y1 + constants.KNOTT.y2) // 2),
        (constants.KNOTT.x1 - 48, (constants.KNOTT.y1 + constants.KNOTT.y2) // 2 + 200),
        # Along west building east face (outside building)
        (constants.DORM.x2 + 48, -200),
        (constants.DORM.x2 + 48, 200),
        (constants.DORM.x2 + 48, 500),
    ]
    all_bush_brushes = []
    for bush_x, bush_y in bush_positions:
        all_bush_brushes += make_bush(bush_x, bush_y, constants.FLOOR_Z2)

    # ── Bushes along verge in front of KH north face (south of Ennis sidewalk) ───
    # Line of bushes just south of ENNIS_SW_EDGE, spanning the raised/sloped ground
    # between the NW indent and the back-road corridor, skipping the entrance.
    knott_verge_y = (
        constants.ENNIS_Y - constants.ENNIS_HW - 100
    )  # north side of Ennis south sidewalk
    knott_bush_spacing = 120
    knott_bush_buffer = 60
    knott_bush_size = 40
    knott_bush_jitter_x = 40
    knott_bush_jitter_y = 30
    knott_verge_brushes = []
    for verge_x1, verge_x2 in [
        (
            constants.ROAD_X2 + constants.CHARLES_WALK_W + knott_bush_buffer,
            constants.KNOTT_ORIG_CX - 64 - knott_bush_buffer,
        ),
        (
            constants.KNOTT_ORIG_CX + 64 + knott_bush_buffer,
            constants.KNOTT_DRIVEWAY_CORRIDOR_X1 - knott_bush_buffer,
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
                jittered_x, jittered_y, constants.FLOOR_Z2, size=knott_bush_size
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

    CHARLES_PLT_X_OUT = constants.ROAD_X2 // 4  # outbound Charles lane  (east,   X=+64)
    CHARLES_PLT_X_RET = -(
        constants.ROAD_X2 * 3 // 4
    )  # return  Charles lane   (west,   X=-192)
    CHARLES_PLT_Y_S = constants.CHARLES_Y1 + CHARLES_PLT_W // 2 + 48  # south turnaround
    CHARLES_PLT_Y_OUT = (
        constants.ENNIS_Y - constants.ENNIS_HW + 16
    )  # outbound Ennis lane (south Y≈792)
    CHARLES_PLT_Y_RET = (
        constants.ENNIS_Y + constants.ENNIS_HW // 8
    )  # return  Ennis lane  (north Y≈956)
    CHARLES_PLT_BR_X = (
        constants.KNOTT_DRIVEWAY_RD_X1 + constants.KNOTT.driveway_hw // 2
    )  # right lane on back road (X≈2382)

    # Z origin at each road surface (platform bottom + half thickness)
    platform_z_charles = ROAD_Z + CHARLES_PLT_H // 2  # Charles St   (= 14)
    platform_z_flat = (
        constants.FLOOR_Z2 + 2 + CHARLES_PLT_H // 2
    )  # Ennis / back road flat (= 8)
    platform_z_backroad_south = (
        constants.KNOTT_DRIVEWAY_ZT_S + 2 + CHARLES_PLT_H // 2
    )  # back road south / hill top (= 72)

    # Platform brush — placed at pc1 (south end of outbound Charles lane)
    cs_platform_brush = box(
        CHARLES_PLT_X_OUT - CHARLES_PLT_W // 2,
        CHARLES_PLT_Y_S - CHARLES_PLT_W // 2,
        ROAD_Z,
        CHARLES_PLT_X_OUT + CHARLES_PLT_W // 2,
        CHARLES_PLT_Y_S + CHARLES_PLT_W // 2,
        ROAD_Z + CHARLES_PLT_H,
        constants.Textures.FLOOR,
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
        (
            "cs_pc4",
            CHARLES_PLT_BR_X,
            constants.KNOTT_DRIVEWAY_Y2,
            platform_z_flat,
            "cs_pc5",
        ),
        (
            "cs_pc5",
            CHARLES_PLT_BR_X,
            constants.KNOTT_DRIVEWAY_Y1,
            platform_z_backroad_south,
            "cs_pc6",
        ),
        (
            "cs_pc6",
            CHARLES_PLT_BR_X,
            constants.KNOTT_DRIVEWAY_Y2,
            platform_z_flat,
            "cs_pc7",
        ),
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

    # Quad damage in the middle of the tunnel
    ENTITIES.append(
        ent(
            "item_artifact_super_damage",
            origin=f"{(constants.BRIDGE.x1 + constants.DORM.x1) // 2} {(constants.CHARLES_Y1 + constants.CHARLES_Y2) // 2} {constants.FLOOR_Z2 + 32}",
        )
    )

    # ── Rocket launchers along the platform route ─────────────────────────────────
    rocket_hover_height = (
        CHARLES_PLT_H + 56
    )  # hover height above road — clear of platform top + item bbox
    backroad_mid_y = (
        constants.KNOTT_DRIVEWAY_Y1 + constants.KNOTT_DRIVEWAY_Y2
    ) // 2  # Y=-1072
    backroad_mid_z = (
        constants.FLOOR_Z2
        + 2
        + (constants.KNOTT_DRIVEWAY_ZT_S - constants.KNOTT_DRIVEWAY_ZT_N)
        * (backroad_mid_y - constants.KNOTT_DRIVEWAY_Y2)
        // (constants.KNOTT_DRIVEWAY_Y1 - constants.KNOTT_DRIVEWAY_Y2)
    )
    for rocket_x, rocket_y, rocket_z in [
        # Charles outbound (south third, north third) — east sidewalk
        (
            constants.ROAD_X2 + 40,
            constants.CHARLES_Y1 + (constants.CHARLES_Y2 - constants.CHARLES_Y1) // 6,
            ROAD_Z + rocket_hover_height,
        ),
        (
            constants.ROAD_X2 + 40,
            constants.CHARLES_Y1
            + (constants.CHARLES_Y2 - constants.CHARLES_Y1) * 2 // 6,
            ROAD_Z + rocket_hover_height,
        ),
        # Ennis outbound (quarter, three-quarter) — south verge
        (
            (CHARLES_PLT_X_OUT + CHARLES_PLT_BR_X) // 3,
            constants.ENNIS_Y - constants.ENNIS_HW - 40,
            constants.FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        (
            (CHARLES_PLT_X_OUT + CHARLES_PLT_BR_X) * 2 // 3,
            constants.ENNIS_Y - constants.ENNIS_HW - 40,
            constants.FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        # Back road going south (midpoint)
        (CHARLES_PLT_BR_X, backroad_mid_y, backroad_mid_z + rocket_hover_height),
        # Ennis return (midpoint) — north verge
        (
            (CHARLES_PLT_X_RET + CHARLES_PLT_BR_X) // 2,
            constants.ENNIS_Y + constants.ENNIS_HW + 40,
            constants.FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        # Charles return (south third, north third) — west sidewalk
        (
            constants.ROAD_X1 - 40,
            constants.CHARLES_Y1 + (constants.CHARLES_Y2 - constants.CHARLES_Y1) // 6,
            ROAD_Z + rocket_hover_height,
        ),
        (
            constants.ROAD_X1 - 40,
            constants.CHARLES_Y1
            + (constants.CHARLES_Y2 - constants.CHARLES_Y1) * 2 // 6,
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
        (constants.ROAD_X1 + 64, -1200, 90),  # south Charles, west side heading north
        (constants.ROAD_X2 - 64, -800, 270),  # south Charles, east side heading south
        (constants.ROAD_X1 + 64, -300, 90),  # mid Charles, west side
        (constants.ROAD_X2 - 64, 200, 270),  # mid Charles, east side
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
        (500, constants.ENNIS_Y - constants.ENNIS_HW + 40, 0),  # Ennis east, south lane
        (
            1200,
            constants.ENNIS_Y + constants.ENNIS_HW - 40,
            180,
        ),  # Ennis east, north lane
        (1800, constants.ENNIS_Y - constants.ENNIS_HW + 40, 0),  # Ennis further east
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    # Ogres on the back road hill — like guards on the slope
    backroad_center_x = (
        constants.KNOTT_DRIVEWAY_RD_X1 + constants.KNOTT_DRIVEWAY_RD_X2
    ) // 2
    for ogre_y, ogre_z in [
        (
            -600,
            constants.FLOOR_Z2
            + 2
            + (
                64
                * ((-600) - constants.KNOTT_DRIVEWAY_Y2)
                // (constants.KNOTT_DRIVEWAY_Y1 - constants.KNOTT_DRIVEWAY_Y2)
            )
            + 24,
        ),
        (
            -1200,
            constants.FLOOR_Z2
            + 2
            + (
                64
                * ((-1200) - constants.KNOTT_DRIVEWAY_Y2)
                // (constants.KNOTT_DRIVEWAY_Y1 - constants.KNOTT_DRIVEWAY_Y2)
            )
            + 24,
        ),
        (
            constants.KNOTT_DRIVEWAY_Y1 + 64,
            constants.KNOTT_GROUND_Z + 2 + 24,
        ),  # top of hill near quad
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{backroad_center_x} {ogre_y} {ogre_z}",
                angle="90",
            )
        )

    # Knights inside KH rooms — one per floor in each room
    for fl in range(constants.KNOTT.floors):
        fz = (
            constants.KNOTT_GROUND_Z
            + fl * constants.KNOTT.floor_h
            + constants.KNOTT.wall_t
            + 24
        )
        split = constants.KNOTT_ROOM_SPLITS[fl]
        sr_yc = (constants.KNOTT_BIY1 + split) // 2
        nr_yc = (split + constants.KNOTT.wall_t + constants.KNOTT_BIY2) // 2
        for rxc in [constants.KNOTT_WEST_ROOM_CX, constants.KNOTT_EAST_ROOM_CX]:
            for ryc in [sr_yc, nr_yc]:
                ENTITIES.append(
                    ent("monster_knight", origin=f"{rxc} {ryc} {fz}", angle="270")
                )

    # Enforcers in the hallway — one per floor
    hall_center_x = (constants.KNOTT_ENT_X1 + constants.KNOTT_ENT_X2) // 2
    for fl in range(constants.KNOTT.floors):
        fz = (
            constants.KNOTT_GROUND_Z
            + fl * constants.KNOTT.floor_h
            + constants.KNOTT.wall_t
            + 24
        )
        hall_yc = (constants.KNOTT_BIY1 + constants.KNOTT_BIY2) // 2
        ENTITIES.append(
            ent("monster_knight", origin=f"{hall_center_x} {hall_yc} {fz}", angle="180")
        )

    # Enforcers on rooftop
    for roof_enemy_x, roof_enemy_y in [
        (constants.KNOTT_WEST_ROOM_CX, constants.KNOTT.y2 - 80),
        (constants.KNOTT_EAST_ROOM_CX, constants.KNOTT.y2 - 80),
        (constants.KNOTT_CX, constants.KNOTT.y1 + 80),
        (constants.KNOTT_WEST_ROOM_CX, constants.KNOTT.y1 + 80),
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{roof_enemy_x} {roof_enemy_y} {constants.KNOTT_Z2 + 24}",
                angle="180",
            )
        )

    # ── Demon knights (monster_hell_knight) ───────────────────────────────────────
    # Two on the bridge arch span — guard the crown and Pier 3 approach
    deck_center_z = int(constants.deck_top_z(0)) + 24  # standing height at arch crown
    deck_p3_z = int(constants.deck_top_z(525)) + 24  # standing height near Pier 3
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
    walkway_mid_x = (
        constants.BRIDGE.x2 + constants.WALK_X1
    ) // 2  # midpoint of walkway span
    ENTITIES.append(
        ent(
            "monster_hell_knight",
            origin=f"{walkway_mid_x} 0 {constants.WALK_ZT1 + 24}",
            angle="180",
        )
    )

    # Two on the accessible walkway alongside Pier 5
    accessible_walk_z = (
        constants.KNOTT_GROUND_Z + 24
    )  # walkway surface + standing height
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
    dorm_exit_xc = (constants.DORM.x1 + constants.DORM.x2) // 2
    _north2_y2 = constants.DORM_NORTH_Y1  # north face of dorm 2 = south face of dorm 1
    _north2_y1 = _north2_y2 - (constants.DORM_NORTH_Y2 - constants.DORM_NORTH_Y1)
    dorm_exit_yc = (_north2_y1 + _north2_y2) // 2
    dorm_exit_hw = 64
    dorm_exit_z0 = constants.FLOOR_Z2
    dorm_exit_brush = box(
        dorm_exit_xc - dorm_exit_hw,
        dorm_exit_yc - dorm_exit_hw,
        dorm_exit_z0,
        dorm_exit_xc + dorm_exit_hw,
        dorm_exit_yc + dorm_exit_hw,
        dorm_exit_z0 + 112,
        constants.Textures.TELEPORT,
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
                    "func_detail",
                    box(bx1, fy1, bz1, bx2, fy2, bz2, constants.Textures.CEMENT),
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
            tex=constants.Textures.LAVA,
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
                    constants.Textures.CEMENT,
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
            tex=constants.Textures.LAVA,
            mirror=do_mirror,
        )
        if lb:
            ENTITIES.append(brush_ent("func_detail", lb))

    ENTITIES.append(
        ent(
            "info_intermission",
            origin="-361 -500 350",  # south of bridge center, slightly elevated
            mangle="-10 75 0",  # pitch=-10 (nearly level), yaw=75 (mostly north, nudged east)
        )
    )

    return BRUSHES, ENTITIES
