from .constants import (
    BRIDGE_DZ2,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM_FLOORS,
    DORM_H,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_PIER_X,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    DORM_WALL_S_Y2,
    DORM_X1,
    DORM_X2,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT_FLOOR_H,
    Textures,
)
from .geometry import (
    box,
    brush_ent,
    gable_slats,
    layered_wall,
    layered_wall_y,
    ramp_slab,
)
from .utils import iron_fence


def build():
    BRUSHES = []
    ENTITIES = []
    # ── North building — hollow shell with windows, entrance, and gable roof ───────
    DORM_WALL = 16  # wall thickness
    DORM_WIN_HW = 36  # window half-width
    DORM_WIN_HH = 44  # window half-height
    DORM_ENT_HW = 48  # entrance half-width (96-unit wide doorway)
    DORM_ENT_H = 100  # entrance height

    DORM_CX = (DORM_X1 + DORM_X2) // 2  # building X center
    DORM_NORTH_CY = (
        DORM_NORTH_Y1 + DORM_NORTH_Y2
    ) // 2  # building Y center (gable ridge line)

    # Window X centers on south/north face: 2 left + 2 right of the entrance gap
    dorm_wx = [DORM_X1 + (DORM_CX - DORM_ENT_HW - DORM_X1) * k // 3 for k in [1, 2]] + [
        (DORM_CX + DORM_ENT_HW) + (DORM_X2 - DORM_CX - DORM_ENT_HW) * k // 3
        for k in [1, 2]
    ]
    # Window Y centers on east/west face: 3 evenly spaced
    dorm_wy = [
        DORM_NORTH_Y1 + (DORM_NORTH_Y2 - DORM_NORTH_Y1) * k // 4 for k in [1, 2, 3]
    ]

    dorm_wz_lo = (
        KNOTT_FLOOR_H - DORM_WIN_HH * 2
    ) // 2  # window sill offset within a floor
    dorm_wz_hi = dorm_wz_lo + DORM_WIN_HH * 2  # window head offset within a floor

    def nb_wins_xz(wx_list):
        """Window openings (all floors) for X-facing wall (south/north)."""
        return [
            (
                wx - DORM_WIN_HW,
                FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_lo,
                wx + DORM_WIN_HW,
                FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_hi,
            )
            for fl in range(DORM_FLOORS)
            for wx in wx_list
        ]

    def nb_wins_yz(wy_list):
        """Window openings (all floors) for Y-facing wall (east/west)."""
        return [
            (
                wy - DORM_WIN_HW,
                FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_lo,
                wy + DORM_WIN_HW,
                FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_hi,
            )
            for fl in range(DORM_FLOORS)
            for wy in wy_list
        ]

    # South wall (faces bridge) — windows + ground-level entrance
    dorm_s_openings = nb_wins_xz(dorm_wx) + [
        (DORM_CX - DORM_ENT_HW, FLOOR_Z2, DORM_CX + DORM_ENT_HW, FLOOR_Z2 + DORM_ENT_H)
    ]
    north_bldg_detail = []
    north_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH_Y1,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH_Y1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            dorm_s_openings,
            "city2_1",
        )
    )
    # North wall — windows only
    north_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH_Y2 - DORM_WALL,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH_Y2,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz(dorm_wx),
            "city2_1",
        )
    )
    # East wall — windows + ground-level entrance (matches south buildings)
    dorm_e_openings = nb_wins_yz(dorm_wy) + [
        (
            DORM_NORTH_CY - DORM_ENT_HW,
            FLOOR_Z2,
            DORM_NORTH_CY + DORM_ENT_HW,
            FLOOR_Z2 + DORM_ENT_H,
        )
    ]
    north_bldg_detail.extend(
        layered_wall_y(
            DORM_NORTH_Y1 + DORM_WALL,
            DORM_X2 - DORM_WALL,
            FLOOR_Z2,
            DORM_NORTH_Y2 - DORM_WALL,
            DORM_X2,
            FLOOR_Z2 + DORM_H,
            dorm_e_openings,
            "city2_1",
        )
    )
    # West wall — windows
    north_bldg_detail.extend(
        layered_wall_y(
            DORM_NORTH_Y1 + DORM_WALL,
            DORM_X1,
            FLOOR_Z2,
            DORM_NORTH_Y2 - DORM_WALL,
            DORM_X1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz(dorm_wy),
            "city2_1",
        )
    )
    # Ceiling slab
    north_bldg_detail.append(
        box(
            DORM_X1,
            DORM_NORTH_Y1,
            FLOOR_Z2 + DORM_H,
            DORM_X2,
            DORM_NORTH_Y2,
            FLOOR_Z2 + DORM_H + DORM_WALL,
            "city2_1",
        )
    )

    # Gable (A-frame) roof — ridge runs N-S at building X center, KNOTT_FLOOR_H above ceiling
    DORM_EAVE_Z = FLOOR_Z2 + DORM_H + DORM_WALL  # top of ceiling slab = eave level
    DORM_RIDGE_Z = DORM_EAVE_Z + KNOTT_FLOOR_H  # ridge apex
    DORM_SLAB_T = 16  # roof slab thickness at eave
    # West slope: flat bottom at eave_z, top slopes up to ridge at nb_cx
    north_bldg_detail.append(
        ramp_slab(
            DORM_X1,
            DORM_CX,
            DORM_NORTH_Y1,
            DORM_NORTH_Y2,
            DORM_EAVE_Z,
            DORM_EAVE_Z,
            DORM_EAVE_Z + DORM_SLAB_T,
            DORM_RIDGE_Z,
            Textures.ROOF,
            ts=Textures.GABLE,
        )
    )
    # East slope: top at ridge at nb_cx, slopes down to eave at AB_X2
    north_bldg_detail.append(
        ramp_slab(
            DORM_CX,
            DORM_X2,
            DORM_NORTH_Y1,
            DORM_NORTH_Y2,
            DORM_EAVE_Z,
            DORM_EAVE_Z,
            DORM_RIDGE_Z,
            DORM_EAVE_Z + DORM_SLAB_T,
            Textures.ROOF,
            ts=Textures.GABLE,
        )
    )
    # Horizontal wood slats over both exposed gable ends
    DORM_GABLE_DEPTH = 6  # slats extend inward; outer face flush with wall
    north_bldg_detail += gable_slats(
        DORM_X1,
        DORM_X2,
        DORM_CX,
        DORM_EAVE_Z,
        DORM_RIDGE_Z,
        DORM_SLAB_T,
        DORM_NORTH_Y1,
        DORM_GABLE_DEPTH,  # +Y → into building
        Textures.GABLE,
    )
    north_bldg_detail += gable_slats(
        DORM_X1,
        DORM_X2,
        DORM_CX,
        DORM_EAVE_Z,
        DORM_RIDGE_Z,
        DORM_SLAB_T,
        DORM_NORTH_Y2,
        -DORM_GABLE_DEPTH,  # -Y → into building
        Textures.GABLE,
    )
    ENTITIES.append(brush_ent("func_detail", north_bldg_detail))

    # Interior floor — flat ground surface inside the building (covers the hill void)
    BRUSHES.append(
        box(
            DORM_X1 + DORM_WALL,
            DORM_NORTH_Y1 + DORM_WALL,
            FLOOR_Z1,
            DORM_X2 - DORM_WALL,
            DORM_NORTH_Y2 - DORM_WALL,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.ROAD,
        )
    )

    # ── Two south buildings — exact copies of north building, stacked N-S ──────────
    # Same X footprint (DORM_X1..DORM_X2), entrance on east face (faces Charles Street).
    # Moved to func_detail to reduce portal complexity in the open campus area.

    def make_south_bldg(by1, by2, slat_lo=False, slat_hi=False):
        """Build the south abutment building geometry (walls, roof, windows, entrance)
        between Y positions by1 (south) and by2 (north).
        slat_lo/slat_hi add gable wood slats on the by1/-Y and by2/+Y ends."""
        bx1, bx2 = DORM_X1, DORM_X2
        cx = (bx1 + bx2) // 2
        ent_hw, ent_h = 48, 100
        wx_list = [bx1 + (cx - ent_hw - bx1) * k // 3 for k in [1, 2]] + [
            (cx + ent_hw) + (bx2 - cx - ent_hw) * k // 3 for k in [1, 2]
        ]
        wy_list = [by1 + (by2 - by1) * k // 4 for k in [1, 2, 3]]

        def wxz():
            return [
                (
                    wx - DORM_WIN_HW,
                    FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_lo,
                    wx + DORM_WIN_HW,
                    FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_hi,
                )
                for fl in range(DORM_FLOORS)
                for wx in wx_list
            ]

        def wyz():
            return [
                (
                    wy - DORM_WIN_HW,
                    FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_lo,
                    wy + DORM_WIN_HW,
                    FLOOR_Z2 + fl * KNOTT_FLOOR_H + dorm_wz_hi,
                )
                for fl in range(DORM_FLOORS)
                for wy in wy_list
            ]

        brushes = []
        # Interior floor
        brushes.append(
            box(
                bx1 + DORM_WALL,
                by1 + DORM_WALL,
                FLOOR_Z1,
                bx2 - DORM_WALL,
                by2 - DORM_WALL,
                FLOOR_Z2,
                Textures.GROUND,
                tt=Textures.ROAD,
            )
        )
        brushes.extend(
            layered_wall(
                bx1,
                by1,
                FLOOR_Z2,
                bx2,
                by1 + DORM_WALL,
                FLOOR_Z2 + DORM_H,
                wxz(),
                "city2_1",
            )
        )
        brushes.extend(
            layered_wall(
                bx1,
                by2 - DORM_WALL,
                FLOOR_Z2,
                bx2,
                by2,
                FLOOR_Z2 + DORM_H,
                wxz(),
                "city2_1",
            )
        )
        brushes.extend(
            layered_wall_y(
                by1 + DORM_WALL,
                bx1,
                FLOOR_Z2,
                by2 - DORM_WALL,
                bx1 + DORM_WALL,
                FLOOR_Z2 + DORM_H,
                wyz(),
                "city2_1",
            )
        )
        cy = (by1 + by2) // 2
        east_openings = wyz() + [(cy - ent_hw, FLOOR_Z2, cy + ent_hw, FLOOR_Z2 + ent_h)]
        brushes.extend(
            layered_wall_y(
                by1 + DORM_WALL,
                bx2 - DORM_WALL,
                FLOOR_Z2,
                by2 - DORM_WALL,
                bx2,
                FLOOR_Z2 + DORM_H,
                east_openings,
                "city2_1",
            )
        )
        brushes.append(
            box(
                bx1,
                by1,
                FLOOR_Z2 + DORM_H,
                bx2,
                by2,
                FLOOR_Z2 + DORM_H + DORM_WALL,
                "city2_1",
            )
        )
        eave_z, ridge_z, slab_t = (
            FLOOR_Z2 + DORM_H + DORM_WALL,
            FLOOR_Z2 + DORM_H + DORM_WALL + KNOTT_FLOOR_H,
            16,
        )
        brushes.append(
            ramp_slab(
                bx1,
                cx,
                by1,
                by2,
                eave_z,
                eave_z,
                eave_z + slab_t,
                ridge_z,
                Textures.ROOF,
                ts=Textures.GABLE,
            )
        )
        brushes.append(
            ramp_slab(
                cx,
                bx2,
                by1,
                by2,
                eave_z,
                eave_z,
                ridge_z,
                eave_z + slab_t,
                Textures.ROOF,
                ts=Textures.GABLE,
            )
        )
        depth = 6  # slats extend inward; outer face flush with wall
        if slat_lo:
            brushes += gable_slats(
                bx1, bx2, cx, eave_z, ridge_z, slab_t, by1, depth, Textures.GABLE
            )
        if slat_hi:
            brushes += gable_slats(
                bx1, bx2, cx, eave_z, ridge_z, slab_t, by2, -depth, Textures.GABLE
            )
        return brushes

    ENTITIES.append(
        brush_ent(
            "func_detail",
            make_south_bldg(DORM_SOUTH1_Y1, DORM_SOUTH1_Y2, slat_lo=True),
        )
    )
    ENTITIES.append(
        brush_ent(
            "func_detail",
            make_south_bldg(DORM_SOUTH2_Y1, DORM_SOUTH2_Y2, slat_hi=True),
        )
    )

    # ── Iron fence along east face of west buildings ──────────────────────────
    FENCE_X1 = DORM_X2 + 96  # well clear of building face
    FENCE_X2 = FENCE_X1 + 2  # picket/rail thickness
    FENCE_H = 96  # fence height
    FENCE_SPACING = 16  # picket center-to-center
    FENCE_TEX = "metal4_4"
    fence_brushes = []
    for fence_y1, fence_y2 in [(CHARLES_Y1, CHARLES_Y2)]:
        # Top rail — thin, dropped so pickets extend above it
        fence_brushes.append(
            box(
                FENCE_X1,
                fence_y1,
                FLOOR_Z2 + FENCE_H - 28,
                FENCE_X2,
                fence_y2,
                FLOOR_Z2 + FENCE_H - 26,
                FENCE_TEX,
            )
        )
        # Pickets — thin (2 wide) with thick posts (8 wide) every 10th
        picket_y = fence_y1
        picket_index = 0
        while picket_y + 2 <= fence_y2:
            picket_width = 8 if picket_index % 10 == 0 else 2
            fence_brushes.append(
                box(
                    FENCE_X1,
                    picket_y,
                    FLOOR_Z2,
                    FENCE_X2,
                    picket_y + picket_width,
                    FLOOR_Z2 + FENCE_H,
                    FENCE_TEX,
                )
            )
            picket_y += FENCE_SPACING
            picket_index += 1
    if fence_brushes:
        ENTITIES.append(brush_ent("func_detail", fence_brushes))

    # ── West brick wall — runs from dorm 2 north face to bridge pier, with door ──
    # Door is centered 160 units north of dorm 2; pillars and iron fence are detail.
    wall_hw = 12  # half-thickness (thinner than pier)
    DORM_DOOR_W = 80  # door opening width
    DORM_DOOR_OFF = 160  # distance from dorm 2 north face to door centre
    DORM_DOOR_H = 128  # door opening height
    wall_start_y = DORM_SOUTH2_Y2  # wall stops at north face of dorm 2
    s_door_y = DORM_SOUTH2_Y2 + DORM_DOOR_OFF
    # Brick wall body (worldspawn — seals the level)
    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            wall_start_y,
            FLOOR_Z2,
            DORM_PIER_X + wall_hw,
            s_door_y - DORM_DOOR_W // 2,
            BRIDGE_DZ2,
            "city2_1",
        )
    )
    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            s_door_y + DORM_DOOR_W // 2,
            FLOOR_Z2,
            DORM_PIER_X + wall_hw,
            DORM_WALL_S_Y2,
            BRIDGE_DZ2,
            "city2_1",
        )
    )
    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            s_door_y - DORM_DOOR_W // 2,
            FLOOR_Z2 + DORM_DOOR_H,
            DORM_PIER_X + wall_hw,
            s_door_y + DORM_DOOR_W // 2,
            BRIDGE_DZ2,
            "city2_1",
        )
    )
    # Brick pillars + iron fence (func_detail — non-sealing)
    wall_detail = []
    pillar_w = 56
    pillar_proud = 6
    pillar_h = BRIDGE_DZ2 + 80
    px1 = DORM_PIER_X - wall_hw - pillar_proud
    px2 = DORM_PIER_X + wall_hw + pillar_proud
    cap_h = 10
    cap_overhang = 1
    door_north = s_door_y + DORM_DOOR_W // 2
    for py1, py2 in [
        (door_north + 96, door_north + 96 + pillar_w),
        (door_north + 96 + pillar_w + 380, door_north + 96 + pillar_w + 380 + pillar_w),
    ]:
        wall_detail.append(box(px1, py1, FLOOR_Z2, px2, py2, pillar_h, "city2_1"))
        wall_detail.append(
            box(
                px1 - cap_overhang,
                py1 - cap_overhang,
                pillar_h,
                px2 + cap_overhang,
                py2 + cap_overhang,
                pillar_h + cap_h,
                "city2_1",
            )
        )
    wall_detail.extend(
        iron_fence(
            [
                (wall_start_y, s_door_y - DORM_DOOR_W // 2),  # south of door
                (
                    s_door_y - DORM_DOOR_W // 2,
                    s_door_y + DORM_DOOR_W // 2,
                ),  # over lintel
                (s_door_y + DORM_DOOR_W // 2, DORM_WALL_S_Y2),  # north of door to pier
            ],
            DORM_PIER_X - 1,
            DORM_PIER_X + 1,
            "metal4_4",
            BRIDGE_DZ2,
        )
    )
    ENTITIES.append(brush_ent("func_detail", wall_detail))

    return BRUSHES, ENTITIES
