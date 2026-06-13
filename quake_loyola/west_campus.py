from .constants import (
    BRIDGE_ARCH_X,
    BRIDGE_DZ1,
    BRIDGE_DZ2,
    BRIDGE_SEG_SPAN_W,
    BRIDGE_SEG_W,
    BRIDGE_X1,
    BRIDGE_X2,
    BRIDGE_Y1,
    BRIDGE_Y2,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM_FLOORS,
    DORM_H,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    DORM_X1,
    DORM_X2,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT_FLOOR_H,
    WALL_T,
    WORLD_X2,
    Textures,
    deck_bot_z,
    deck_top_z,
)
from .geometry import (
    box,
    east_y_shift,
    layered_wall,
    layered_wall_y,
    ramp_slab,
    shear_box_y,
)


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
    BRUSHES.extend(
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
    BRUSHES.extend(
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
    BRUSHES.extend(
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
    BRUSHES.extend(
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
    BRUSHES.append(
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
    BRUSHES.append(
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
        )
    )
    # East slope: top at ridge at nb_cx, slopes down to eave at AB_X2
    BRUSHES.append(
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
        )
    )
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

    def make_south_bldg(by1, by2):
        """Build the south abutment building geometry (walls, roof, windows, entrance)
        between Y positions by1 (south) and by2 (north)."""
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
            )
        )
        return brushes

    BRUSHES.extend(make_south_bldg(DORM_SOUTH1_Y1, DORM_SOUTH1_Y2))
    BRUSHES.extend(make_south_bldg(DORM_SOUTH2_Y1, DORM_SOUTH2_Y2))

    # ── Iron fence along east face of west buildings ──────────────────────────
    FENCE_X1 = DORM_X2 + 96  # well clear of building face
    FENCE_X2 = FENCE_X1 + 2  # picket/rail thickness
    FENCE_H = 96  # fence height
    FENCE_SPACING = 16  # picket center-to-center
    FENCE_TEX = "metal4_4"

    for fence_y1, fence_y2 in [(CHARLES_Y1, CHARLES_Y2)]:
        # Top rail — thin, dropped so pickets extend above it
        BRUSHES.append(
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
            BRUSHES.append(
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

    # ════════════════════════════════════════════════════════════════════════════════
    # West flat approach removed — arch now starts at world edge
    # East flat stub from arch terminus to building entrance — angled southward
    BRIDGE_EAST_SHIFT_START = 0.0  # no shift at the pier (pivot)
    BRIDGE_EAST_SHIFT_END = east_y_shift(
        WORLD_X2 - WALL_T
    )  # full southward shift at east world wall
    BRIDGE_EAST_PIVOT_X = BRIDGE_ARCH_X[4]  # easternmost pier — where the angle begins
    # Straight section: arch terminus → easternmost pier
    BRUSHES.append(
        box(
            BRIDGE_X2,
            BRIDGE_Y1,
            BRIDGE_DZ1,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y2,
            BRIDGE_DZ2,
            Textures.STONE,
            tt=Textures.FLOOR,
            tb=Textures.FLOOR,
        )
    )
    # Angled section: easternmost pier → east world wall
    BRUSHES.append(
        shear_box_y(
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y1,
            BRIDGE_DZ1,
            WORLD_X2 - WALL_T,
            BRIDGE_Y2,
            BRIDGE_DZ2,
            BRIDGE_EAST_SHIFT_START,
            BRIDGE_EAST_SHIFT_END,
            Textures.STONE,
            tt=Textures.FLOOR,
            tb=Textures.FLOOR,
        )
    )

    for i in range(BRIDGE_SEG_SPAN_W):
        sx1 = BRIDGE_X1 + i * BRIDGE_SEG_W
        sx2 = sx1 + BRIDGE_SEG_W
        BRUSHES.append(
            ramp_slab(
                sx1,
                sx2,
                BRIDGE_Y1,
                BRIDGE_Y2,
                deck_bot_z(sx1),
                deck_bot_z(sx2),
                deck_top_z(sx1),
                deck_top_z(sx2),
                Textures.STONE,
                tt=Textures.FLOOR,
                tb=Textures.FLOOR,
            )
        )
    return BRUSHES, ENTITIES
