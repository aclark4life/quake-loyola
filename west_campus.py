from constants import (
    CS_Y1,
    CS_Y2,
    FLOOR_Z1,
    FLOOR_Z2,
    KH_FLOOR_H,
    BRIDGE_ARCH_X,
    BRIDGE_DZ1,
    BRIDGE_DZ2,
    BRIDGE_X1,
    BRIDGE_X2,
    BRIDGE_Y1,
    BRIDGE_Y2,
    RH_FLOORS,
    RH_H,
    RH_NORTH_Y1,
    RH_NORTH_Y2,
    RH_SOUTH1_Y1,
    RH_SOUTH1_Y2,
    RH_SOUTH2_Y1,
    RH_SOUTH2_Y2,
    RH_X1,
    RH_X2,
    BRIDGE_SEG_SPAN_W,
    BRIDGE_SEG_W,
    TEX_FLOOR,
    TEX_GROUND,
    TEX_ROAD,
    TEX_ROOF,
    TEX_STONE,
    WALL_T,
    WORLD_X2,
    dbot,
    dtop,
)
from geometry import (
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
    RH_WALL = 16  # wall thickness
    RH_WIN_HW = 36  # window half-width
    RH_WIN_HH = 44  # window half-height
    RH_ENT_HW = 48  # entrance half-width (96-unit wide doorway)
    RH_ENT_H = 100  # entrance height

    RH_CX = (RH_X1 + RH_X2) // 2  # building X center
    RH_NORTH_CY = (
        RH_NORTH_Y1 + RH_NORTH_Y2
    ) // 2  # building Y center (gable ridge line)

    # Window X centers on south/north face: 2 left + 2 right of the entrance gap
    rh_wx = [RH_X1 + (RH_CX - RH_ENT_HW - RH_X1) * k // 3 for k in [1, 2]] + [
        (RH_CX + RH_ENT_HW) + (RH_X2 - RH_CX - RH_ENT_HW) * k // 3 for k in [1, 2]
    ]
    # Window Y centers on east/west face: 3 evenly spaced
    rh_wy = [RH_NORTH_Y1 + (RH_NORTH_Y2 - RH_NORTH_Y1) * k // 4 for k in [1, 2, 3]]

    rh_wz_lo = (KH_FLOOR_H - RH_WIN_HH * 2) // 2  # window sill offset within a floor
    rh_wz_hi = rh_wz_lo + RH_WIN_HH * 2  # window head offset within a floor

    def nb_wins_xz(wx_list):
        """Window openings (all floors) for X-facing wall (south/north)."""
        return [
            (
                wx - RH_WIN_HW,
                FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_lo,
                wx + RH_WIN_HW,
                FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_hi,
            )
            for fl in range(RH_FLOORS)
            for wx in wx_list
        ]

    def nb_wins_yz(wy_list):
        """Window openings (all floors) for Y-facing wall (east/west)."""
        return [
            (
                wy - RH_WIN_HW,
                FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_lo,
                wy + RH_WIN_HW,
                FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_hi,
            )
            for fl in range(RH_FLOORS)
            for wy in wy_list
        ]

    # South wall (faces bridge) — windows + ground-level entrance
    rh_s_openings = nb_wins_xz(rh_wx) + [
        (RH_CX - RH_ENT_HW, FLOOR_Z2, RH_CX + RH_ENT_HW, FLOOR_Z2 + RH_ENT_H)
    ]
    BRUSHES.extend(
        layered_wall(
            RH_X1,
            RH_NORTH_Y1,
            FLOOR_Z2,
            RH_X2,
            RH_NORTH_Y1 + RH_WALL,
            FLOOR_Z2 + RH_H,
            rh_s_openings,
            "city2_1",
        )
    )
    # North wall — windows only
    BRUSHES.extend(
        layered_wall(
            RH_X1,
            RH_NORTH_Y2 - RH_WALL,
            FLOOR_Z2,
            RH_X2,
            RH_NORTH_Y2,
            FLOOR_Z2 + RH_H,
            nb_wins_xz(rh_wx),
            "city2_1",
        )
    )
    # East wall — windows + ground-level entrance (matches south buildings)
    rh_e_openings = nb_wins_yz(rh_wy) + [
        (
            RH_NORTH_CY - RH_ENT_HW,
            FLOOR_Z2,
            RH_NORTH_CY + RH_ENT_HW,
            FLOOR_Z2 + RH_ENT_H,
        )
    ]
    BRUSHES.extend(
        layered_wall_y(
            RH_NORTH_Y1 + RH_WALL,
            RH_X2 - RH_WALL,
            FLOOR_Z2,
            RH_NORTH_Y2 - RH_WALL,
            RH_X2,
            FLOOR_Z2 + RH_H,
            rh_e_openings,
            "city2_1",
        )
    )
    # West wall — windows
    BRUSHES.extend(
        layered_wall_y(
            RH_NORTH_Y1 + RH_WALL,
            RH_X1,
            FLOOR_Z2,
            RH_NORTH_Y2 - RH_WALL,
            RH_X1 + RH_WALL,
            FLOOR_Z2 + RH_H,
            nb_wins_yz(rh_wy),
            "city2_1",
        )
    )
    # Ceiling slab
    BRUSHES.append(
        box(
            RH_X1,
            RH_NORTH_Y1,
            FLOOR_Z2 + RH_H,
            RH_X2,
            RH_NORTH_Y2,
            FLOOR_Z2 + RH_H + RH_WALL,
            "city2_1",
        )
    )

    # Gable (A-frame) roof — ridge runs N-S at building X center, KH_FLOOR_H above ceiling
    RH_EAVE_Z = FLOOR_Z2 + RH_H + RH_WALL  # top of ceiling slab = eave level
    RH_RIDGE_Z = RH_EAVE_Z + KH_FLOOR_H  # ridge apex
    RH_SLAB_T = 16  # roof slab thickness at eave
    # West slope: flat bottom at eave_z, top slopes up to ridge at nb_cx
    BRUSHES.append(
        ramp_slab(
            RH_X1,
            RH_CX,
            RH_NORTH_Y1,
            RH_NORTH_Y2,
            RH_EAVE_Z,
            RH_EAVE_Z,
            RH_EAVE_Z + RH_SLAB_T,
            RH_RIDGE_Z,
            TEX_ROOF,
        )
    )
    # East slope: top at ridge at nb_cx, slopes down to eave at AB_X2
    BRUSHES.append(
        ramp_slab(
            RH_CX,
            RH_X2,
            RH_NORTH_Y1,
            RH_NORTH_Y2,
            RH_EAVE_Z,
            RH_EAVE_Z,
            RH_RIDGE_Z,
            RH_EAVE_Z + RH_SLAB_T,
            TEX_ROOF,
        )
    )
    # Interior floor — flat ground surface inside the building (covers the hill void)
    BRUSHES.append(
        box(
            RH_X1 + RH_WALL,
            RH_NORTH_Y1 + RH_WALL,
            FLOOR_Z1,
            RH_X2 - RH_WALL,
            RH_NORTH_Y2 - RH_WALL,
            FLOOR_Z2,
            TEX_GROUND,
            tt=TEX_ROAD,
        )
    )

    # ── Two south buildings — exact copies of north building, stacked N-S ──────────
    # Same X footprint (RH_X1..RH_X2), entrance on east face (faces Charles Street).

    def make_south_bldg(by1, by2):
        """Build the south abutment building geometry (walls, roof, windows, entrance)
        between Y positions by1 (south) and by2 (north)."""
        bx1, bx2 = RH_X1, RH_X2
        cx = (bx1 + bx2) // 2
        ent_hw, ent_h = 48, 100
        wx_list = [bx1 + (cx - ent_hw - bx1) * k // 3 for k in [1, 2]] + [
            (cx + ent_hw) + (bx2 - cx - ent_hw) * k // 3 for k in [1, 2]
        ]
        wy_list = [by1 + (by2 - by1) * k // 4 for k in [1, 2, 3]]

        def wxz():
            return [
                (
                    wx - RH_WIN_HW,
                    FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_lo,
                    wx + RH_WIN_HW,
                    FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_hi,
                )
                for fl in range(RH_FLOORS)
                for wx in wx_list
            ]

        def wyz():
            return [
                (
                    wy - RH_WIN_HW,
                    FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_lo,
                    wy + RH_WIN_HW,
                    FLOOR_Z2 + fl * KH_FLOOR_H + rh_wz_hi,
                )
                for fl in range(RH_FLOORS)
                for wy in wy_list
            ]

        brushes = []
        # Interior floor
        brushes.append(
            box(
                bx1 + RH_WALL,
                by1 + RH_WALL,
                FLOOR_Z1,
                bx2 - RH_WALL,
                by2 - RH_WALL,
                FLOOR_Z2,
                TEX_GROUND,
                tt=TEX_ROAD,
            )
        )
        brushes.extend(
            layered_wall(
                bx1,
                by1,
                FLOOR_Z2,
                bx2,
                by1 + RH_WALL,
                FLOOR_Z2 + RH_H,
                wxz(),
                "city2_1",
            )
        )
        brushes.extend(
            layered_wall(
                bx1,
                by2 - RH_WALL,
                FLOOR_Z2,
                bx2,
                by2,
                FLOOR_Z2 + RH_H,
                wxz(),
                "city2_1",
            )
        )
        brushes.extend(
            layered_wall_y(
                by1 + RH_WALL,
                bx1,
                FLOOR_Z2,
                by2 - RH_WALL,
                bx1 + RH_WALL,
                FLOOR_Z2 + RH_H,
                wyz(),
                "city2_1",
            )
        )
        cy = (by1 + by2) // 2
        east_openings = wyz() + [(cy - ent_hw, FLOOR_Z2, cy + ent_hw, FLOOR_Z2 + ent_h)]
        brushes.extend(
            layered_wall_y(
                by1 + RH_WALL,
                bx2 - RH_WALL,
                FLOOR_Z2,
                by2 - RH_WALL,
                bx2,
                FLOOR_Z2 + RH_H,
                east_openings,
                "city2_1",
            )
        )
        brushes.append(
            box(
                bx1,
                by1,
                FLOOR_Z2 + RH_H,
                bx2,
                by2,
                FLOOR_Z2 + RH_H + RH_WALL,
                "city2_1",
            )
        )
        eave_z, ridge_z, slab_t = (
            FLOOR_Z2 + RH_H + RH_WALL,
            FLOOR_Z2 + RH_H + RH_WALL + KH_FLOOR_H,
            16,
        )
        brushes.append(
            ramp_slab(
                bx1, cx, by1, by2, eave_z, eave_z, eave_z + slab_t, ridge_z, TEX_ROOF
            )
        )
        brushes.append(
            ramp_slab(
                cx, bx2, by1, by2, eave_z, eave_z, ridge_z, eave_z + slab_t, TEX_ROOF
            )
        )
        return brushes

    BRUSHES.extend(make_south_bldg(RH_SOUTH1_Y1, RH_SOUTH1_Y2))
    BRUSHES.extend(make_south_bldg(RH_SOUTH2_Y1, RH_SOUTH2_Y2))

    # ── Iron fence along east face of west buildings ──────────────────────────
    FENCE_X1 = RH_X2 + 96  # well clear of building face
    FENCE_X2 = FENCE_X1 + 2  # picket/rail thickness
    FENCE_H = 96  # fence height
    FENCE_SPACING = 16  # picket center-to-center
    FENCE_TEX = "metal4_4"

    for fence_y1, fence_y2 in [(CS_Y1, CS_Y2)]:
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
            TEX_STONE,
            tt=TEX_FLOOR,
            tb=TEX_FLOOR,
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
            TEX_STONE,
            tt=TEX_FLOOR,
            tb=TEX_FLOOR,
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
                dbot(sx1),
                dbot(sx2),
                dtop(sx1),
                dtop(sx2),
                TEX_STONE,
                tt=TEX_FLOOR,
                tb=TEX_FLOOR,
            )
        )
    return BRUSHES, ENTITIES
