from constants import (
    ARCH_RIN,
    ARCH_SLAB_W,
    ARCH_STILT_H,
    A_SEGS,
    CS_LAMP_POST_H,
    CS_LAMP_POST_XS,
    CS_WALK_W,
    CS_Y1,
    CS_Y2,
    EP_HW,
    EP_PIL_BELL2_H,
    EP_PIL_CAP_H,
    EP_PIL_HW,
    EP_PIL_POST_H,
    EP_PIL_X1,
    EP_PIL_ZB,
    EP_WALL_T,
    EP_Y,
    FLOOR_Z2,
    KH_BR_CORRIDOR_X1,
    KH_BR_HW,
    KH_BR_RD_X1,
    KH_BR_RD_X2,
    KH_BR_Y1,
    KH_BR_Y2,
    KH_BR_ZT_N,
    KH_BR_ZT_S,
    KH_CX,
    KH_ENABLED,
    KH_ENT_X1,
    KH_ENT_X2,
    KH_FLOORS,
    KH_FLOOR_H,
    KH_GROUND_Z,
    KH_ORIG_CX,
    KH_WALKWAY_ENABLED,
    KH_WALL,
    KH_X1,
    KH_X2,
    KH_Y1,
    KH_Y2,
    KH_Z2,
    BRIDGE_ARCH_X,
    BRIDGE_DZ2,
    BRIDGE_PAR_H,
    BRIDGE_PAR_W,
    BRIDGE_PEND_XS,
    BRIDGE_PIL_BASE_H,
    BRIDGE_PIL_BASE_RAMP_H,
    BRIDGE_PIL_CAP_H,
    BRIDGE_PIL_EXTRA,
    BRIDGE_PIL_HW,
    BRIDGE_PIL_PYR_H,
    BRIDGE_X1,
    BRIDGE_X2,
    BRIDGE_Y1,
    BRIDGE_Y2,
    RH_FLOORS,
    RH_NORTH_Y1,
    RH_NORTH_Y2,
    RH_RIDGE_Z,
    RH_SOUTH1_Y1,
    RH_SOUTH1_Y2,
    RH_SOUTH2_Y1,
    RH_SOUTH2_Y2,
    RH_X1,
    RH_X2,
    ROAD_X1,
    ROAD_X2,
    SHOW_SUPPORTS,
    TEX_FLOOR,
    TEX_FLOOR_KH,
    TEX_SKY,
    TEX_TELEPORT,
    WALK_X1,
    WALK_ZT1,
    WALK_ZT2,
    WALL_T,
    WORLD_X1,
    WORLD_X2,
    WORLD_Y2,
    KH_BIY1,
    KH_BIY2,
    EP_WALL_NY,
    EP_CEMENT_LAMP_POSTS,
    EP_CEMENT_X1,
    EP_CEMENT_X2,
    dbot,
    dtop,
    EP_GATE_X1,
    EP_GATE_X2,
    BRIDGE_EAST_SHIFT_END,
    KH_EAST_ROOM_CX,
    CS_LAMP_POST_YS,
    KH_ROOM_SPLITS,
    stx1,
    stx2,
    sty1,
    sty2,
    KH_STAIRS_MID_Y,
    KH_STAIRS_X1,
    KH_STAIRS_X2,
    KH_STAIRS_Y1,
    KH_STAIRS_Y2,
    KH_WEST_ROOM_CX,
)
from geometry import (
    arch_fill,
    arch_fill_y,
    box,
    brush_ent,
    ent,
    make_bush,
    make_giant_tree,
    make_tree,
)


def build():
    BRUSHES = []
    ENTITIES = []
    BRIDGE_DECK_Z = dtop(0) + 8  # centre of arch deck + a bit (spawn/item height)
    ROAD_Z = FLOOR_Z2 + 8

    # ── Knott Hall room goodies — 2 items per room, varied per floor ──────────────
    kh_entity_start = len(ENTITIES)  # checkpoint — trimmed below if KH_ENABLED is False
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
    for floor_index in range(KH_FLOORS):
        fz1 = KH_GROUND_Z + floor_index * KH_FLOOR_H
        item_z = fz1 + KH_WALL + 24
        light_z = fz1 + KH_FLOOR_H - 24  # near ceiling
        split = KH_ROOM_SPLITS[floor_index]
        sr_yc = (KH_BIY1 + split) // 2
        nr_yc = (split + KH_WALL + KH_BIY2) // 2
        for side_xc in [KH_WEST_ROOM_CX, KH_EAST_ROOM_CX]:
            for ryc in [sr_yc, nr_yc]:
                # If west room north items land within 64 units of stairwell south wall, push south
                safe_ryc = ryc
                if (
                    side_xc == KH_WEST_ROOM_CX
                    and ryc == nr_yc
                    and nr_yc > KH_STAIRS_Y1 - 64
                ):
                    safe_ryc = KH_STAIRS_Y1 - 80
                ENTITIES.append(
                    ent("light", origin=f"{side_xc} {safe_ryc} {light_z}", light="250")
                )
                # Extra fill light at lower mid-height to reduce dark corners
                ENTITIES.append(
                    ent(
                        "light",
                        origin=f"{side_xc} {safe_ryc} {fz1 + KH_FLOOR_H // 2}",
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
    west_stair_center_x = (KH_STAIRS_X1 + KH_STAIRS_X2) // 2  # X centre of shaft
    west_stair_north_y = (KH_STAIRS_MID_Y + KH_STAIRS_Y2) // 2  # Y centre of north lane
    west_stair_south_y = (KH_STAIRS_Y1 + KH_STAIRS_MID_Y) // 2  # Y centre of south lane
    for floor_index in range(KH_FLOORS):
        west_stair_light_z = (
            KH_GROUND_Z + floor_index * KH_FLOOR_H + KH_FLOOR_H - 24
        )  # near ceiling
        west_stair_mid_z = (
            KH_GROUND_Z + floor_index * KH_FLOOR_H + KH_FLOOR_H // 2
        )  # mid-flight
        west_stair_low_z = (
            KH_GROUND_Z + floor_index * KH_FLOOR_H + KH_FLOOR_H // 4
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
    hall_center_x = (KH_ENT_X1 + KH_ENT_X2) // 2  # hallway centre X
    hall_light_ys = [
        KH_BIY1 + (KH_BIY2 - KH_BIY1) * i // 4
        for i in range(1, 4)  # quarters: 25%, 50%, 75%
    ] + [
        KH_BIY1 + (KH_BIY2 - KH_BIY1) // 8,  # 12.5% (near south end)
        KH_BIY1 + (KH_BIY2 - KH_BIY1) * 7 // 8,  # 87.5% (near north end)
    ]
    for floor_index in range(KH_FLOORS):
        hall_light_z = KH_GROUND_Z + floor_index * KH_FLOOR_H + KH_FLOOR_H - 24
        for hall_y in hall_light_ys:
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{hall_center_x} {hall_y} {hall_light_z}",
                    light="200",
                )
            )

    # ── Entrance corridor lights — one per floor in each doorway ─────────────────
    entry_corridor_y = KH_Y2 - 48  # just inside north face
    for floor_index in range(KH_FLOORS):
        entry_corridor_light_z = (
            KH_GROUND_Z + floor_index * KH_FLOOR_H + KH_FLOOR_H - 24
        )
        ENTITIES.append(
            ent(
                "light",
                origin=f"{hall_center_x} {entry_corridor_y} {entry_corridor_light_z}",
                light="220",
            )
        )

    # ── Knott Hall bookshelves — scattered through rooms ─────────────────────────
    KH_SHELF_H = 64  # height of shelf stack
    KH_SHELF_D = 16  # depth (one wall-thickness)
    KH_SHELF_W = 64  # width

    shelf_offsets = [0, 0, 0, 0, 0]

    for floor_index in range(KH_FLOORS):
        fz1 = KH_GROUND_Z + floor_index * KH_FLOOR_H
        fz_surf = fz1 + KH_WALL
        split = KH_ROOM_SPLITS[floor_index]
        shelf_x_offset = shelf_offsets[floor_index]

        for shelf_center_x in [KH_WEST_ROOM_CX, KH_EAST_ROOM_CX]:
            # South room: shelf against south wall — front faces south (-Y)
            shelf_x = shelf_center_x + shelf_x_offset
            ENTITIES.append(
                brush_ent(
                    "func_wall",
                    [
                        box(
                            shelf_x - KH_SHELF_W // 2,
                            KH_BIY1,
                            fz_surf,
                            shelf_x + KH_SHELF_W // 2,
                            KH_BIY1 + KH_SHELF_D,
                            fz_surf + KH_SHELF_H,
                            "shelf_1",
                        )
                    ],
                )
            )
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{shelf_x} {KH_BIY1 + 32} {fz_surf + KH_SHELF_H + 24}",
                    light="180",
                )
            )

    if not KH_ENABLED:
        del ENTITIES[kh_entity_start:]

    # Teleport destinations — west arch ↔ east arch
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_east",
            origin=f"{(RH_X1 + RH_X2) // 2} {(RH_NORTH_Y1 + RH_NORTH_Y2) // 2} {int(RH_RIDGE_Z + 40)}",
            angle="270",  # facing south toward the bridge
        )
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_west",
            origin=f"{KH_CX} {(KH_Y1 + KH_Y2) // 2} {int(KH_Z2 + 40)}",
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
        TEX_TELEPORT,
        stilt_h=ARCH_STILT_H,
    )
    ENTITIES.append(brush_ent("trigger_teleport", west_brushes, target="dest_east"))
    ENTITIES.append(brush_ent("func_illusionary", west_brushes))

    # West lower trigger (ground floor — simple box between posts)
    wlx1 = WORLD_X1 + WALL_T
    wlx2 = wlx1 + ARCH_SLAB_W
    west_lower = [
        box(wlx1, -ARCH_RIN, FLOOR_Z2, wlx2, ARCH_RIN, BRIDGE_DZ2, TEX_TELEPORT)
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
        TEX_TELEPORT,
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
            TEX_TELEPORT,
        )
    ]
    ENTITIES.append(brush_ent("trigger_teleport", east_lower, target="dest_east_deck"))
    ENTITIES.append(brush_ent("func_illusionary", east_lower))

    # ── North & South Charles Street arch teleports → bridge deck centre ─────────
    CS_ARCH_RIN = 256  # inner radius = road half-width
    CS_ARCH_STILT = 96  # straight post height before arch springs
    CS_ARCH_W = 48  # arch thickness in Y (thicker = more stone-like)

    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_bridge_mid",
            origin=f"0 0 {int(dtop(0) + 56)}",
            angle="0",
        )
    )

    CS_ARCH_TRIG_INSET = 8  # push trigger away from world walls and road surface

    for arch_y1, arch_y2, trigger_y1, trigger_y2 in [
        (
            CS_Y1,
            CS_Y1 + CS_ARCH_W,
            CS_Y1 + CS_ARCH_TRIG_INSET,
            CS_Y1 + CS_ARCH_W,
        ),  # south arch — trigger inset from south wall
        (
            CS_Y2 - CS_ARCH_W,
            CS_Y2,
            CS_Y2 - CS_ARCH_W,
            CS_Y2 - CS_ARCH_TRIG_INSET,
        ),  # north arch — trigger inset from north wall
    ]:
        arch_top_z = FLOOR_Z2 + CS_ARCH_STILT + CS_ARCH_RIN
        # Box trigger — reliable activation, inset from walls
        north_south_trigger_brush = [
            box(
                ROAD_X1 + CS_ARCH_TRIG_INSET,
                trigger_y1,
                FLOOR_Z2 + 4,
                ROAD_X2 - CS_ARCH_TRIG_INSET,
                trigger_y2,
                arch_top_z,
                TEX_TELEPORT,
            )
        ]
        ENTITIES.append(
            brush_ent(
                "trigger_teleport", north_south_trigger_brush, target="dest_bridge_mid"
            )
        )
        # Arch-shaped illusionary fill so the teleport glow looks like an arch
        north_south_glow_brushes = arch_fill_y(
            arch_y1,
            arch_y2,
            0.0,
            FLOOR_Z2 + 4,
            CS_ARCH_RIN,
            A_SEGS,
            TEX_TELEPORT,
            stilt_h=CS_ARCH_STILT,
        )
        ENTITIES.append(brush_ent("func_illusionary", north_south_glow_brushes))

    ENTITIES.append(
        ent(
            "info_player_start",
            origin=f"{KH_CX} {BRIDGE_Y1 + BRIDGE_PAR_W + 32} {int(BRIDGE_DZ2 + 24)}",
            angle="180",
        )
    )

    kh_cy = (KH_Y1 + KH_Y2) // 2  # Knott Hall center Y = -528
    RH_NORTH_CY = (RH_NORTH_Y1 + RH_NORTH_Y2) // 2  # north building center Y
    RH_CX = (RH_X1 + RH_X2) // 2  # west buildings center X
    RH_SOUTH1_CY = (RH_SOUTH1_Y1 + RH_SOUTH1_Y2) // 2  # south building 1 center Y
    RH_SOUTH2_CY = (RH_SOUTH2_Y1 + RH_SOUTH2_Y2) // 2  # south building 2 center Y

    # ── Deathmatch spawns — spread across all areas ──────────────────────────
    for pos, angle in [
        # Bridge deck
        ((0, 0, int(dtop(0) + 32)), 180),
        ((-200, 0, int(dtop(-200) + 32)), 90),
        ((200, 0, int(dtop(200) + 32)), 270),
        ((-400, 0, int(dtop(-400) + 32)), 90),
        ((400, 0, int(dtop(400) + 32)), 270),
        # Walkway
        *(
            [((KH_CX, (BRIDGE_Y1 + KH_Y2) // 2, int(WALK_ZT1 + 32)), 180)]
            if KH_ENABLED
            else []
        ),
        # Knott Hall — ground, mid, upper floors
        *(
            [
                (
                    ((KH_ENT_X1 + KH_ENT_X2) // 2, KH_Y2 - 80, KH_GROUND_Z + 40),
                    180,
                ),  # entrance hallway, north
                ((KH_CX - 100, kh_cy, KH_GROUND_Z + KH_FLOOR_H + 40), 270),
                ((KH_CX + 100, kh_cy, KH_GROUND_Z + KH_FLOOR_H * 2 + 40), 90),
                ((KH_CX, KH_Y1 + 100, KH_GROUND_Z + KH_FLOOR_H * 3 + 40), 0),
                ((KH_CX, kh_cy, KH_GROUND_Z + KH_FLOOR_H * 4 + 40), 180),
                # Knott Hall rooftop
                ((KH_CX, kh_cy, KH_Z2 + 40), 180),
            ]
            if KH_ENABLED
            else []
        ),
        # Charles Street
        ((0, 300, ROAD_Z + 24), 180),
        ((0, -400, ROAD_Z + 24), 0),
        ((0, RH_SOUTH1_CY, ROAD_Z + 24), 270),
        # North building interior
        ((RH_CX, RH_NORTH_CY, FLOOR_Z2 + 40), 90),
        ((RH_CX, RH_NORTH_CY, FLOOR_Z2 + KH_FLOOR_H + 40), 90),
        # North building roof ridge
        ((RH_CX, RH_NORTH_CY, int(RH_RIDGE_Z + 40)), 90),
        # South buildings interiors
        ((RH_CX, RH_SOUTH1_CY, FLOOR_Z2 + 40), 90),
        ((RH_CX, RH_SOUTH2_CY, FLOOR_Z2 + 40), 90),
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
    if KH_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_rocketlauncher",
                origin=f"{KH_CX} {kh_cy} {KH_GROUND_Z + KH_FLOOR_H * 3 + 40}",
            )
        )
    # Rocket launcher — west arch, north side
    ENTITIES.append(
        ent(
            "weapon_rocketlauncher",
            origin=f"{BRIDGE_ARCH_X[1]} {BRIDGE_Y1 - 48} {BRIDGE_DECK_Z}",
        )
    )
    # Remaining rocket launchers
    for rl_origin in [
        f"{ROAD_X2 + 40} {EP_Y - EP_HW - 200} {ROAD_Z + 24}",  # east sidewalk, south of Ennis
        f"{BRIDGE_ARCH_X[2]} 0 {ROAD_Z + 24}",  # under bridge, mid span
        f"{int(EP_GATE_X1 + (EP_GATE_X2 - EP_GATE_X1) // 2)} {EP_WALL_NY - 80} {FLOOR_Z2 + 24}",  # Ennis fence midpoint
        f"{int(EP_CEMENT_X1 + (EP_CEMENT_X2 - EP_CEMENT_X1) // 2)} {EP_WALL_NY - 80} {FLOOR_Z2 + 24}",  # Ennis wall midpoint
        # Bridge deck — one per span
        f"{(BRIDGE_X1 + BRIDGE_ARCH_X[0]) // 2} 0 {BRIDGE_DECK_Z}",  # span 1
        f"{(BRIDGE_ARCH_X[0] + BRIDGE_ARCH_X[1]) // 2} {BRIDGE_Y2 - 24} {BRIDGE_DECK_Z}",  # span 2 south edge
        f"{(BRIDGE_ARCH_X[1] + BRIDGE_ARCH_X[2]) // 2} {BRIDGE_Y1 + 24} {BRIDGE_DECK_Z}",  # span 3 north edge
        f"{(BRIDGE_ARCH_X[2] + BRIDGE_X2) // 2} 0 {BRIDGE_DECK_Z}",  # span 4
        f"{(BRIDGE_X2 + BRIDGE_ARCH_X[4]) // 2} 0 {BRIDGE_DECK_Z}",  # span 5 (east angled)
    ]:
        ENTITIES.append(ent("weapon_rocketlauncher", origin=rl_origin))

    # Super shotgun — spread around mid-tier locations
    if KH_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_supershotgun",
                origin=f"{KH_EAST_ROOM_CX} {KH_Y2 - 80} {KH_GROUND_Z + 40}",
            )
        )
    ENTITIES.append(
        ent("weapon_supershotgun", origin=f"300 300 {ROAD_Z + 24}")
    )  # east sidewalk
    ENTITIES.append(
        ent("weapon_supershotgun", origin=f"{RH_CX} {RH_SOUTH1_CY} {FLOOR_Z2 + 40}")
    )

    # Grenade launcher — Knott Hall floor 2, south building 2
    if KH_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_grenadelauncher",
                origin=f"{KH_CX} {kh_cy} {KH_GROUND_Z + KH_FLOOR_H * 2 + 40}",
            )
        )
    ENTITIES.append(
        ent("weapon_grenadelauncher", origin=f"{RH_CX} {RH_SOUTH2_CY} {FLOOR_Z2 + 40}")
    )

    # Nailgun — bridge approaches, Charles Street
    ENTITIES.append(ent("weapon_nailgun", origin=f"-600 0 {ROAD_Z + 24}"))
    ENTITIES.append(ent("weapon_nailgun", origin=f"600 0 {ROAD_Z + 24}"))
    if KH_ENABLED:
        ENTITIES.append(
            ent(
                "weapon_nailgun",
                origin=f"{KH_CX} {kh_cy} {KH_GROUND_Z + KH_FLOOR_H + 40}",
            )
        )

    # ── Ammo ──────────────────────────────────────────────────────────────────
    for ax in BRIDGE_ARCH_X:
        ENTITIES.append(ent("item_rockets", origin=f"{ax} 0 {int(dtop(ax) + 8)}"))
    for rx in [400, 800]:
        ENTITIES.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z + 24}"))
        ENTITIES.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z + 24}"))
    for kf in range(1, KH_FLOORS):
        ENTITIES.append(
            ent(
                "item_rockets",
                origin=f"{KH_CX + 80} {kh_cy} {KH_GROUND_Z + kf * KH_FLOOR_H + 40}",
            )
        )
    ENTITIES.append(
        ent("item_shells", origin=f"-300 -300 {ROAD_Z + 24}")
    )  # west sidewalk
    ENTITIES.append(ent("item_shells", origin=f"{RH_CX} {RH_NORTH_CY} {FLOOR_Z2 + 40}"))
    ENTITIES.append(ent("item_spikes", origin=f"-400 200 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_spikes", origin=f"400 -200 {ROAD_Z + 24}"))

    # ── Health & Armor ────────────────────────────────────────────────────────
    # Health — scattered throughout
    ENTITIES.append(ent("item_health", origin=f"0 0 {BRIDGE_DECK_Z}"))
    ENTITIES.append(
        ent("item_health", origin=f"{KH_EAST_ROOM_CX} {KH_Y2 - 64} {KH_GROUND_Z + 40}")
    )
    ENTITIES.append(
        ent(
            "item_health", origin=f"{KH_CX} {kh_cy} {KH_GROUND_Z + KH_FLOOR_H * 2 + 40}"
        )
    )
    ENTITIES.append(
        ent("item_health", origin=f"-300 400 {ROAD_Z + 24}")
    )  # west sidewalk
    ENTITIES.append(
        ent("item_health", origin=f"300 -600 {ROAD_Z + 24}")
    )  # east sidewalk
    ENTITIES.append(
        ent("item_health", origin=f"{RH_CX} {RH_SOUTH2_CY} {FLOOR_Z2 + 40}")
    )
    # Armor — contested locations
    ENTITIES.append(
        ent("item_armor1", origin=f"-200 0 {BRIDGE_DECK_Z}")
    )  # yellow armor on bridge
    ENTITIES.append(
        ent(
            "item_armor2", origin=f"{KH_CX} {kh_cy} {KH_GROUND_Z + KH_FLOOR_H * 4 + 40}"
        )
    )  # red armor top floor
    ENTITIES.append(
        ent("item_armorInv", origin=f"{RH_CX} {RH_NORTH_CY} {int(RH_RIDGE_Z + 40)}")
    )  # mega armor on roof ridge (teleport reward)

    # Torch lights on pillar caps
    if SHOW_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
                continue
            pbase = dtop(px)
            pcap = (
                pbase
                + BRIDGE_PAR_H
                + BRIDGE_PIL_EXTRA
                + BRIDGE_PIL_CAP_H
                + BRIDGE_PIL_PYR_H
            )  # top of pyramid
            cy_n = BRIDGE_Y2 - BRIDGE_PAR_W // 2  # centred on north pillar cap
            cy_s = BRIDGE_Y1 + BRIDGE_PAR_W // 2  # centred on south pillar cap
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
                    TEX_SKY,
                )
                ENTITIES.append(brush_ent("trigger_hurt", [fhb], dmg="10"))

    # Pillar base uplights — ground-level spots wash light up the pier faces
    if SHOW_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
                continue
            for underbridge_light_y in [BRIDGE_Y2 + 30, BRIDGE_Y1 - 30]:
                # Skip abutment-pier positions buried in solid building geometry
                if px == BRIDGE_ARCH_X[0]:
                    continue
                if px == BRIDGE_ARCH_X[-1] and underbridge_light_y == BRIDGE_Y1 - 30:
                    continue
                ENTITIES.append(
                    ent("light", origin=f"{px} {underbridge_light_y} 16", light="200")
                )

    # Campus lamp post lights — flame above brick cup, matching bridge pillar torches
    for lamp_x in CS_LAMP_POST_XS:
        for lamp_y in CS_LAMP_POST_YS:
            pole_top_z = FLOOR_Z2 + CS_LAMP_POST_H
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
    for lamp_x, lamp_y, lamp_z in EP_CEMENT_LAMP_POSTS:
        # The east-wall post (EP_CEMENT_X2) sits flush against the world wall, so its
        # point light is buried in solid — emit it only for the open (west) post.
        if lamp_x != EP_CEMENT_X2:
            ENTITIES.append(
                ent("light", origin=f"{lamp_x} {lamp_y} {lamp_z}", light="300")
            )
        ENTITIES.append(
            ent("light_flame_large_yellow", origin=f"{lamp_x} {lamp_y} {lamp_z + 4}")
        )

    # Ennis entrance pillar torches — flame above brick cup on each stone pillar
    ennis_pil_flame_z = EP_PIL_ZB + EP_PIL_POST_H + EP_PIL_CAP_H + EP_PIL_BELL2_H + 20
    ennis_pil_cx = EP_PIL_X1 + EP_PIL_HW
    for pillar_y in (EP_Y - EP_HW - EP_PIL_HW, EP_Y + EP_HW + EP_PIL_HW):
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
                origin=f"{pier_x} 0 {int(dbot(pier_x)) - 20}",
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
                "light", origin=f"{pier_x} {BRIDGE_Y2 // 2} {pier_light_z}", light="250"
            )
        )
        ENTITIES.append(
            ent(
                "light", origin=f"{pier_x} {BRIDGE_Y1 // 2} {pier_light_z}", light="250"
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
            origin=f"{abutment_pier_x + BRIDGE_PIL_HW + 32} {BRIDGE_Y2 // 2} {abutment_arch_z}",
            light="500",
        )
    )
    ENTITIES.append(
        ent(
            "light",
            origin=f"{abutment_pier_x + BRIDGE_PIL_HW + 32} {BRIDGE_Y1 // 2} {abutment_arch_z}",
            light="500",
        )
    )

    # Light on underside of walkway slab illuminating the ramp below
    if KH_WALKWAY_ENABLED:
        walk_mid_y = (BRIDGE_Y1 + KH_Y2) // 2
        walk_frac = (BRIDGE_Y1 - walk_mid_y) / float(BRIDGE_Y1 - KH_Y2)
        wk_zb1 = WALK_ZT1 - KH_WALL
        wk_zb2 = WALK_ZT2 - KH_WALL
        walk_bot_mid = int(wk_zb1 + walk_frac * (wk_zb2 - wk_zb1))
        ENTITIES.append(
            ent("light", origin=f"{KH_CX} {walk_mid_y} {walk_bot_mid - 8}", light="300")
        )

    # Lift (func_plat) — rides from ground floor up through roof opening to rooftop
    if KH_ENABLED:
        lift_travel = KH_Z2 - (KH_GROUND_Z + KH_WALL)
        lift_brush = [
            box(
                stx1 + 2,
                sty1 + 2,
                KH_Z2 - 8,
                stx2 - 2,
                sty2 - 2,
                KH_Z2,
                TEX_FLOOR_KH,
            )
        ]
        ENTITIES.append(
            brush_ent("func_plat", lift_brush, height=str(lift_travel), speed="200")
        )

    # Interior lights for the three campus buildings (north + 2 south)
    bldg_light_x = (RH_X1 + RH_X2) // 2
    for building_y1, building_y2 in [
        (RH_NORTH_Y1, RH_NORTH_Y2),
        (RH_SOUTH1_Y1, RH_SOUTH1_Y2),
        (RH_SOUTH2_Y1, RH_SOUTH2_Y2),
    ]:
        building_y = (building_y1 + building_y2) // 2
        for building_floor_index in range(RH_FLOORS):
            building_light_z = (
                FLOOR_Z2 + building_floor_index * KH_FLOOR_H + KH_FLOOR_H // 2
            )
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{bldg_light_x} {building_y} {building_light_z}",
                    light="200",
                )
            )

    # Interior lights for Knott Hall — 3×4 grid per floor
    if KH_ENABLED:
        for kh_floor_index in range(KH_FLOORS):
            kh_light_z = KH_GROUND_Z + kh_floor_index * KH_FLOOR_H + KH_FLOOR_H // 2
            for kh_x_index in [1, 2, 3]:
                kh_light_x = KH_X1 + (KH_X2 - KH_X1) * kh_x_index // 4
                for kh_y_index in [1, 2, 3, 4]:
                    kh_light_y = KH_Y1 + (KH_Y2 - KH_Y1) * kh_y_index // 5
                    ENTITIES.append(
                        ent(
                            "light",
                            origin=f"{kh_light_x} {kh_light_y} {kh_light_z}",
                            light="150",
                        )
                    )

    # ── Cartoon trees as func_detail ─────────────────────────────────────────────
    # Positions based on ref photos:
    # - Dense forest behind cement/iron wall north of Ennis (bridge13, bridge02)
    # - Large trees flanking Knott Hall on west side (bridge01, bridge10)
    # - Trees along Ennis Parallel campus road (bridge02)
    tree_positions = [
        # Trees flanking Knott Hall (west side — bridge01, bridge10)
        (RH_X1 - 80, -600),
        (RH_X1 - 200, -300),
        (RH_X1 - 80, 200),
        (RH_X1 - 200, 500),
        # Along Ennis Parallel (campus side, west of Charles St — bridge02)
        (ROAD_X1 - 200, EP_WALL_NY - 100),
        (ROAD_X1 - 400, EP_WALL_NY - 80),
        (ROAD_X1 - 600, EP_WALL_NY - 120),
    ]
    all_tree_brushes = []
    for tree_x, tree_y in tree_positions:
        all_tree_brushes += make_tree(tree_x, tree_y, FLOOR_Z2)
    ENTITIES.append(brush_ent("func_detail", all_tree_brushes))

    # ── Giant trees along Charles Street — in front of Knott Hall only ───────────
    # 5 trees in 2 rows: row of 2 closer to street, row of 3 closer to KH.
    # Tree height matches Knott Hall (KH_Z2).
    charles_tree_height = KH_Z2
    kh_tree_span = KH_Y2 - KH_Y1
    charles_tree_row_near_x = ROAD_X2 + CS_WALK_W + 300  # closer to Charles St
    charles_tree_row_far_x = ROAD_X2 + CS_WALK_W + 560  # closer to KH
    # Row of 2 — near row, 2 trees at 25% and 75% of KH Y span
    charles_tree_row2_ys = [int(KH_Y1 + kh_tree_span * f) for f in (0.25, 0.75)]
    # Row of 3 — far row, 3 trees at 15%, 50%, 85%
    charles_tree_row3_ys = [int(KH_Y1 + kh_tree_span * f) for f in (0.15, 0.5, 0.85)]
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
    east_ground_tree_height = KH_Z2
    east_ground_spacing = 350
    east_ground_jitter = 120
    east_ground_buffer = 120  # clearance buffer from world edges / wall
    east_ground_x1 = ROAD_X2 + CS_WALK_W + east_ground_buffer
    east_ground_x2 = WORLD_X2 - WALL_T - east_ground_buffer
    east_ground_y1 = (
        EP_WALL_NY + EP_WALL_T + 200
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

    bush_positions = [
        # Along north face of Ennis brick wall (campus grass side, not sidewalk)
        ((ROAD_X2 + CS_WALK_W + 48) + 60, EP_WALL_NY + EP_WALL_T + 40),
        ((ROAD_X2 + CS_WALK_W + 48) + 160, EP_WALL_NY + EP_WALL_T + 40),
        ((ROAD_X2 + CS_WALK_W + 48) + 260, EP_WALL_NY + EP_WALL_T + 40),
        ((ROAD_X2 + CS_WALK_W + 48) + 360, EP_WALL_NY + EP_WALL_T + 40),
        # Along north face of iron fence
        (int(EP_GATE_X1 + 120), EP_WALL_NY + EP_WALL_T + 40),
        (int(EP_GATE_X1 + 300), EP_WALL_NY + EP_WALL_T + 40),
        (int(EP_GATE_X1 + 500), EP_WALL_NY + EP_WALL_T + 40),
        (int(EP_GATE_X1 + 700), EP_WALL_NY + EP_WALL_T + 40),
        # Along north face of cement parapet wall
        (int(EP_CEMENT_X1 + 120), EP_WALL_NY + EP_WALL_T + 40),
        (int(EP_CEMENT_X1 + 320), EP_WALL_NY + EP_WALL_T + 40),
        (int(EP_CEMENT_X1 + 560), EP_WALL_NY + EP_WALL_T + 40),
        # Along Knott Hall west face (outside building)
        (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2 - 200),
        (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2),
        (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2 + 200),
        # Along west building east face (outside building)
        (RH_X2 + 48, -200),
        (RH_X2 + 48, 200),
        (RH_X2 + 48, 500),
    ]
    all_bush_brushes = []
    for bush_x, bush_y in bush_positions:
        all_bush_brushes += make_bush(bush_x, bush_y, FLOOR_Z2)

    # ── Bushes along verge in front of KH north face (south of Ennis sidewalk) ───
    # Line of bushes just south of EP_SW_EDGE, spanning the raised/sloped ground
    # between the NW indent and the back-road corridor, skipping the entrance.
    kh_verge_y = EP_Y - EP_HW - 100  # north side of Ennis south sidewalk
    kh_bush_spacing = 120
    kh_bush_buffer = 60
    kh_bush_size = 40
    kh_bush_jitter_x = 40
    kh_bush_jitter_y = 30
    kh_verge_brushes = []
    for verge_x1, verge_x2 in [
        (ROAD_X2 + CS_WALK_W + kh_bush_buffer, KH_ORIG_CX - 64 - kh_bush_buffer),
        (KH_ORIG_CX + 64 + kh_bush_buffer, KH_BR_CORRIDOR_X1 - kh_bush_buffer),
    ]:
        bush_x = verge_x1
        while bush_x <= verge_x2:
            jittered_x = bush_x + tree_rng.randint(-kh_bush_jitter_x, kh_bush_jitter_x)
            jittered_y = kh_verge_y + tree_rng.randint(
                -kh_bush_jitter_y, kh_bush_jitter_y
            )
            kh_verge_brushes += make_bush(
                jittered_x, jittered_y, FLOOR_Z2, size=kh_bush_size
            )
            bush_x += kh_bush_spacing
    all_bush_brushes += kh_verge_brushes

    ENTITIES.append(brush_ent("func_detail", all_bush_brushes))

    # ── Charles Street scrolling platform — proper two-lane loop with quad damage ──
    # Outbound: east lane north on Charles → south lane east on Ennis → east end
    # Return:   west lane south on Charles ← north lane west on Ennis ← east end
    # ── Charles Street platform — via back road, no Ennis lane switch ─────────────
    # Route: Charles outbound (north) → right on Ennis → right onto back road →
    #        south down hill → back up north → left on Ennis → Charles return (south)
    CS_PLT_W = 128  # platform width and depth
    CS_PLT_H = 12  # platform slab thickness
    CS_PLT_SPEED = 180  # units per second

    CS_PLT_X_OUT = ROAD_X2 // 4  # outbound Charles lane  (east,   X=+64)
    CS_PLT_X_RET = -(ROAD_X2 * 3 // 4)  # return  Charles lane   (west,   X=-192)
    CS_PLT_Y_S = CS_Y1 + CS_PLT_W // 2 + 48  # south turnaround
    CS_PLT_Y_OUT = EP_Y - EP_HW + 16  # outbound Ennis lane (south Y≈792)
    CS_PLT_Y_RET = EP_Y + EP_HW // 8  # return  Ennis lane  (north Y≈956)
    CS_PLT_BR_X = KH_BR_RD_X1 + KH_BR_HW // 2  # right lane on back road (X≈2382)

    # Z origin at each road surface (platform bottom + half thickness)
    platform_z_charles = ROAD_Z + CS_PLT_H // 2  # Charles St   (= 14)
    platform_z_flat = FLOOR_Z2 + 2 + CS_PLT_H // 2  # Ennis / back road flat (= 8)
    platform_z_backroad_south = (
        KH_BR_ZT_S + 2 + CS_PLT_H // 2
    )  # back road south / hill top (= 72)

    # Platform brush — placed at pc1 (south end of outbound Charles lane)
    cs_platform_brush = box(
        CS_PLT_X_OUT - CS_PLT_W // 2,
        CS_PLT_Y_S - CS_PLT_W // 2,
        ROAD_Z,
        CS_PLT_X_OUT + CS_PLT_W // 2,
        CS_PLT_Y_S + CS_PLT_W // 2,
        ROAD_Z + CS_PLT_H,
        TEX_FLOOR,
    )
    ENTITIES.append(
        brush_ent(
            "func_train",
            [cs_platform_brush],
            target="cs_pc1",
            speed=str(CS_PLT_SPEED),
            minlight="255",
        )
    )

    # 9-corner loop:
    # pc1 Charles south (out) → pc2 Ennis junction → pc3 back-road junction
    # → pc4 top of slope → pc5 hill bottom (turn) → pc6 top of slope (return)
    # → pc7 Ennis junction return → pc8 Charles/Ennis return → pc9 Charles south (ret) → pc1
    for path_corner_name, path_x, path_y, path_z, next_target in [
        ("cs_pc1", CS_PLT_X_OUT, CS_PLT_Y_S, platform_z_charles, "cs_pc2"),
        ("cs_pc2", CS_PLT_X_OUT, CS_PLT_Y_OUT, platform_z_flat, "cs_pc3"),
        ("cs_pc3", CS_PLT_BR_X, CS_PLT_Y_OUT, platform_z_flat, "cs_pc4"),
        ("cs_pc4", CS_PLT_BR_X, KH_BR_Y2, platform_z_flat, "cs_pc5"),
        ("cs_pc5", CS_PLT_BR_X, KH_BR_Y1, platform_z_backroad_south, "cs_pc6"),
        ("cs_pc6", CS_PLT_BR_X, KH_BR_Y2, platform_z_flat, "cs_pc7"),
        ("cs_pc7", CS_PLT_BR_X, CS_PLT_Y_RET, platform_z_flat, "cs_pc8"),
        ("cs_pc8", CS_PLT_X_RET, CS_PLT_Y_RET, platform_z_flat, "cs_pc9"),
        ("cs_pc9", CS_PLT_X_RET, CS_PLT_Y_S, platform_z_charles, "cs_pc1"),
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
            origin=f"{CS_PLT_BR_X} {KH_BR_Y1} {platform_z_backroad_south + CS_PLT_H + 18}",
        )
    )

    # ── Rocket launchers along the platform route ─────────────────────────────────
    rocket_hover_height = (
        CS_PLT_H + 56
    )  # hover height above road — clear of platform top + item bbox
    backroad_mid_y = (KH_BR_Y1 + KH_BR_Y2) // 2  # Y=-1072
    backroad_mid_z = (
        FLOOR_Z2
        + 2
        + (KH_BR_ZT_S - KH_BR_ZT_N)
        * (backroad_mid_y - KH_BR_Y2)
        // (KH_BR_Y1 - KH_BR_Y2)
    )
    for rocket_x, rocket_y, rocket_z in [
        # Charles outbound (south third, north third) — east sidewalk
        (ROAD_X2 + 40, CS_Y1 + (CS_Y2 - CS_Y1) // 6, ROAD_Z + rocket_hover_height),
        (ROAD_X2 + 40, CS_Y1 + (CS_Y2 - CS_Y1) * 2 // 6, ROAD_Z + rocket_hover_height),
        # Ennis outbound (quarter, three-quarter) — south verge
        (
            (CS_PLT_X_OUT + CS_PLT_BR_X) // 3,
            EP_Y - EP_HW - 40,
            FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        (
            (CS_PLT_X_OUT + CS_PLT_BR_X) * 2 // 3,
            EP_Y - EP_HW - 40,
            FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        # Back road going south (midpoint)
        (CS_PLT_BR_X, backroad_mid_y, backroad_mid_z + rocket_hover_height),
        # Ennis return (midpoint) — north verge
        (
            (CS_PLT_X_RET + CS_PLT_BR_X) // 2,
            EP_Y + EP_HW + 40,
            FLOOR_Z2 + 2 + rocket_hover_height,
        ),
        # Charles return (south third, north third) — west sidewalk
        (ROAD_X1 - 40, CS_Y1 + (CS_Y2 - CS_Y1) // 6, ROAD_Z + rocket_hover_height),
        (ROAD_X1 - 40, CS_Y1 + (CS_Y2 - CS_Y1) * 2 // 6, ROAD_Z + rocket_hover_height),
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
        (500, EP_Y - EP_HW + 40, 0),  # Ennis east, south lane
        (1200, EP_Y + EP_HW - 40, 180),  # Ennis east, north lane
        (1800, EP_Y - EP_HW + 40, 0),  # Ennis further east
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    # Ogres on the back road hill — like guards on the slope
    backroad_center_x = (KH_BR_RD_X1 + KH_BR_RD_X2) // 2
    for ogre_y, ogre_z in [
        (-600, FLOOR_Z2 + 2 + (64 * ((-600) - KH_BR_Y2) // (KH_BR_Y1 - KH_BR_Y2)) + 24),
        (
            -1200,
            FLOOR_Z2 + 2 + (64 * ((-1200) - KH_BR_Y2) // (KH_BR_Y1 - KH_BR_Y2)) + 24,
        ),
        (KH_BR_Y1 + 64, KH_GROUND_Z + 2 + 24),  # top of hill near quad
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{backroad_center_x} {ogre_y} {ogre_z}",
                angle="90",
            )
        )

    # Knights inside KH rooms — one per floor in each room
    for fl in range(KH_FLOORS):
        fz = KH_GROUND_Z + fl * KH_FLOOR_H + KH_WALL + 24
        split = KH_ROOM_SPLITS[fl]
        sr_yc = (KH_BIY1 + split) // 2
        nr_yc = (split + KH_WALL + KH_BIY2) // 2
        for rxc in [KH_WEST_ROOM_CX, KH_EAST_ROOM_CX]:
            for ryc in [sr_yc, nr_yc]:
                ENTITIES.append(
                    ent("monster_knight", origin=f"{rxc} {ryc} {fz}", angle="270")
                )

    # Enforcers in the hallway — one per floor
    hall_center_x = (KH_ENT_X1 + KH_ENT_X2) // 2
    for fl in range(KH_FLOORS):
        fz = KH_GROUND_Z + fl * KH_FLOOR_H + KH_WALL + 24
        hall_yc = (KH_BIY1 + KH_BIY2) // 2
        ENTITIES.append(
            ent("monster_knight", origin=f"{hall_center_x} {hall_yc} {fz}", angle="180")
        )

    # Enforcers on rooftop
    for roof_enemy_x, roof_enemy_y in [
        (KH_WEST_ROOM_CX, KH_Y2 - 80),
        (KH_EAST_ROOM_CX, KH_Y2 - 80),
        (KH_CX, KH_Y1 + 80),
        (KH_WEST_ROOM_CX, KH_Y1 + 80),
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{roof_enemy_x} {roof_enemy_y} {KH_Z2 + 24}",
                angle="180",
            )
        )

    # ── Demon knights (monster_hell_knight) ───────────────────────────────────────
    # Two on the bridge arch span — guard the crown and Pier 3 approach
    deck_center_z = int(dtop(0)) + 24  # standing height at arch crown
    deck_p3_z = int(dtop(525)) + 24  # standing height near Pier 3
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
    walkway_mid_x = (BRIDGE_X2 + WALK_X1) // 2  # midpoint of walkway span
    ENTITIES.append(
        ent(
            "monster_hell_knight",
            origin=f"{walkway_mid_x} 0 {WALK_ZT1 + 24}",
            angle="180",
        )
    )

    # Two on the accessible walkway alongside Pier 5
    accessible_walk_z = KH_GROUND_Z + 24  # walkway surface + standing height
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

    return BRUSHES, ENTITIES
