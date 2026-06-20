from .constants import (
    BRIDGE_DZ2,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM_FLOOR_H,
    DORM_FLOORS,
    DORM_H,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_PIER_X,
    DORM_ROOF_H,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    DORM_WALL_S_Y2,
    DORM_WIN_MARGIN,
    DORM_X1,
    DORM_X2,
    FLOOR_Z1,
    FLOOR_Z2,
    Textures,
)
from .geometry import (
    box,
    brush_ent,
    entrance_arch_xwall,
    entrance_arch_ywall,
    gable_slats,
    layered_wall,
    layered_wall_y,
    ramp_slab,
    win_frame_xwall,
    win_frame_ywall,
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
    DORM_INNER_DOOR_HW = 40  # half-width of doorway between adjacent buildings
    DORM_INNER_DOOR_H = 128  # height of doorway between adjacent buildings

    DORM_CX = (DORM_X1 + DORM_X2) // 2  # building X center
    DORM_NORTH_CY = (
        DORM_NORTH_Y1 + DORM_NORTH_Y2
    ) // 2  # building Y center (gable ridge line)

    # Interior doorway opening (X-normal walls) shared by adjacent buildings
    dorm_door_open = (
        DORM_CX - DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        DORM_CX + DORM_INNER_DOOR_HW,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
    )

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
        DORM_FLOOR_H - DORM_WIN_HH * 2
    ) // 2  # window sill offset within a floor
    dorm_wz_hi = dorm_wz_lo + DORM_WIN_HH * 2  # window head offset within a floor

    def nb_wins_xz(wx_list):
        """Window openings (all floors) for X-facing wall (south/north)."""
        return [
            (
                wx - DORM_WIN_HW,
                FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
                wx + DORM_WIN_HW,
                FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
            )
            for fl in range(DORM_FLOORS)
            for wx in wx_list
        ]

    def nb_wins_yz(wy_list):
        """Window openings (all floors) for Y-facing wall (east/west)."""
        return [
            (
                wy - DORM_WIN_HW,
                FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
                wy + DORM_WIN_HW,
                FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
            )
            for fl in range(DORM_FLOORS)
            for wy in wy_list
        ]

    # South wall (faces bridge) — windows only, no entrance on this face
    dorm_s_openings = nb_wins_xz(dorm_wx) + [
        (
            DORM_CX - DORM_WIN_HW,
            FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
            DORM_CX + DORM_WIN_HW,
            FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
        )
        for fl in range(DORM_FLOORS)
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
            dorm_s_openings + [dorm_door_open],  # ground-floor center is a doorway
            "city2_1",
        )
    )
    # North wall — windows only (including center windows on 2nd and 3rd floor)
    north_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH_Y2 - DORM_WALL,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH_Y2,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz(dorm_wx)
            + [
                (
                    DORM_CX - DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
                    DORM_CX + DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
                )
                for fl in range(1, DORM_FLOORS)
            ],
            "city2_1",
        )
    )
    # East wall — windows only (no entrance)
    dorm_e_openings = nb_wins_yz(dorm_wy) + [
        (
            DORM_NORTH_CY - DORM_WIN_HW,
            FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
            DORM_NORTH_CY + DORM_WIN_HW,
            FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
        )
        for fl in range(DORM_FLOORS)
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

    # ── Decorative wood trim (window frames only — no entrance arches) ───────────────

    # Window frames — south face (all windows including center, all floors)
    for xl, zb, xr, zt in nb_wins_xz(dorm_wx):
        north_bldg_detail += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            DORM_NORTH_Y1,
            +1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    for fl in range(1, DORM_FLOORS):  # ground-floor center is now a doorway to bldg 2
        zb = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo
        zt = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi
        north_bldg_detail += win_frame_xwall(
            DORM_CX - DORM_WIN_HW,
            DORM_CX + DORM_WIN_HW,
            zb,
            zt,
            DORM_NORTH_Y1,
            +1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Door frame — ground-floor center doorway to building 2 (south face)
    north_bldg_detail += win_frame_xwall(
        DORM_CX - DORM_INNER_DOOR_HW,
        DORM_CX + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
        DORM_NORTH_Y1,
        +1,
        Textures.GABLE,
        fw=8,  # thick frame bars
        fd=DORM_WALL,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )
    # Window frames — north face
    for xl, zb, xr, zt in nb_wins_xz(dorm_wx):
        north_bldg_detail += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            DORM_NORTH_Y2,
            -1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Center window frames — north face, 2nd and 3rd floor
    for fl in range(1, DORM_FLOORS):
        zb = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo
        zt = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi
        north_bldg_detail += win_frame_xwall(
            DORM_CX - DORM_WIN_HW,
            DORM_CX + DORM_WIN_HW,
            zb,
            zt,
            DORM_NORTH_Y2,
            -1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
            crossbar=fl != 1,  # 2nd-floor center: one open (undivided) window
        )
    # Window frames — east face (all windows; no entrance to skip)
    for yl, zb, yr, zt in nb_wins_yz(dorm_wy):
        north_bldg_detail += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM_X2,
            -1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Center window frames — east face, all floors
    for fl in range(DORM_FLOORS):
        zb = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo
        zt = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi
        north_bldg_detail += win_frame_ywall(
            DORM_NORTH_CY - DORM_WIN_HW,
            DORM_NORTH_CY + DORM_WIN_HW,
            zb,
            zt,
            DORM_X2,
            -1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Window frames — west face
    for yl, zb, yr, zt in nb_wins_yz(dorm_wy):
        north_bldg_detail += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM_X1,
            +1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )

    DORM_EAVE_Z = FLOOR_Z2 + DORM_H + DORM_WALL  # top of ceiling slab = eave level
    DORM_RIDGE_Z = DORM_EAVE_Z + DORM_ROOF_H  # ridge apex
    DORM_SLAB_T = 16  # roof slab thickness at eave
    # Recess the roof-slab gable ends inward so the slats fill the gap with their
    # outer face flush with the wall below; grooves between planks reveal the
    # recessed slab behind them (relief) without protruding past the wall.
    DORM_GABLE_DEPTH = 6
    DORM_NB_SY1 = DORM_NORTH_Y1  # south end abuts building 2 — full slab, no recess
    DORM_NB_SY2 = DORM_NORTH_Y2 - DORM_GABLE_DEPTH
    # West slope: flat bottom at eave_z, top slopes up to ridge at nb_cx
    north_bldg_detail.append(
        ramp_slab(
            DORM_X1,
            DORM_CX,
            DORM_NB_SY1,
            DORM_NB_SY2,
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
            DORM_NB_SY1,
            DORM_NB_SY2,
            DORM_EAVE_Z,
            DORM_EAVE_Z,
            DORM_RIDGE_Z,
            DORM_EAVE_Z + DORM_SLAB_T,
            Textures.ROOF,
            ts=Textures.GABLE,
        )
    )
    # Horizontal wood slats over the exposed north gable end only (the south end
    # abuts north building 2, so no gable there).
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
        n=8,
        gap=4,
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

    # ── North building 2 — adjacent south of building 1, no doors ───────────────────
    DORM_NORTH2_Y2 = DORM_NORTH_Y1  # north face touches south face of bldg 1
    DORM_NORTH2_Y1 = DORM_NORTH2_Y2 - (DORM_NORTH_Y2 - DORM_NORTH_Y1)  # same depth
    DORM_NORTH2_CY = (DORM_NORTH2_Y1 + DORM_NORTH2_Y2) // 2
    dorm_wy2 = [
        DORM_NORTH2_Y1 + (DORM_NORTH2_Y2 - DORM_NORTH2_Y1) * k // 4 for k in [1, 2, 3]
    ]
    # Center openings (all floors) for X-facing walls of building 2
    nb2_cx_opens = [
        (
            DORM_CX - DORM_WIN_HW,
            FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
            DORM_CX + DORM_WIN_HW,
            FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
        )
        for fl in range(DORM_FLOORS)
    ]
    north2_bldg_detail = []
    # South wall — windows only (no entrance)
    north2_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH2_Y1,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH2_Y1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz(dorm_wx) + nb2_cx_opens,
            "city2_1",
        )
    )
    # North wall — windows only (faces south face of building 1)
    north2_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH2_Y2 - DORM_WALL,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH2_Y2,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz(dorm_wx)
            + [
                (
                    DORM_CX - DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
                    DORM_CX + DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
                )
                for fl in range(1, DORM_FLOORS)
            ]
            + [dorm_door_open],  # ground-floor center is a doorway to bldg 2
            "city2_1",
        )
    )
    # East wall — windows only (no entrance, no arch)
    north2_bldg_detail.extend(
        layered_wall_y(
            DORM_NORTH2_Y1 + DORM_WALL,
            DORM_X2 - DORM_WALL,
            FLOOR_Z2,
            DORM_NORTH2_Y2 - DORM_WALL,
            DORM_X2,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz(dorm_wy2),
            "city2_1",
        )
    )
    # West wall — windows only
    north2_bldg_detail.extend(
        layered_wall_y(
            DORM_NORTH2_Y1 + DORM_WALL,
            DORM_X1,
            FLOOR_Z2,
            DORM_NORTH2_Y2 - DORM_WALL,
            DORM_X1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz(dorm_wy2),
            "city2_1",
        )
    )
    # Ceiling slab
    north2_bldg_detail.append(
        box(
            DORM_X1,
            DORM_NORTH2_Y1,
            FLOOR_Z2 + DORM_H,
            DORM_X2,
            DORM_NORTH2_Y2,
            FLOOR_Z2 + DORM_H + DORM_WALL,
            "city2_1",
        )
    )
    # Window frames — south face (all windows + center, all floors)
    for xl, zb, xr, zt in nb_wins_xz(dorm_wx):
        north2_bldg_detail += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            DORM_NORTH2_Y1,
            +1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    for fl in range(DORM_FLOORS):
        zb = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo
        zt = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi
        north2_bldg_detail += win_frame_xwall(
            DORM_CX - DORM_WIN_HW,
            DORM_CX + DORM_WIN_HW,
            zb,
            zt,
            DORM_NORTH2_Y1,
            +1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Window frames — north face
    for xl, zb, xr, zt in nb_wins_xz(dorm_wx):
        north2_bldg_detail += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            DORM_NORTH2_Y2,
            -1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    for fl in range(1, DORM_FLOORS):
        zb = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo
        zt = FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi
        north2_bldg_detail += win_frame_xwall(
            DORM_CX - DORM_WIN_HW,
            DORM_CX + DORM_WIN_HW,
            zb,
            zt,
            DORM_NORTH2_Y2,
            -1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Door frame — ground-floor center doorway to building 1 (north face)
    north2_bldg_detail += win_frame_xwall(
        DORM_CX - DORM_INNER_DOOR_HW,
        DORM_CX + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
        DORM_NORTH2_Y2,
        -1,
        Textures.GABLE,
        fw=8,  # thick frame bars
        fd=DORM_WALL,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )
    # Window frames — east face (no entrance; all windows get frames)
    for yl, zb, yr, zt in nb_wins_yz(dorm_wy2):
        north2_bldg_detail += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM_X2,
            -1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Window frames — west face
    for yl, zb, yr, zt in nb_wins_yz(dorm_wy2):
        north2_bldg_detail += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM_X1,
            +1,
            Textures.GABLE,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
        )
    # Roof — same gable profile as building 1
    NB2_EAVE_Z = FLOOR_Z2 + DORM_H + DORM_WALL
    NB2_RIDGE_Z = NB2_EAVE_Z + DORM_ROOF_H
    NB2_SLAB_T = 16
    NB2_GABLE_DEPTH = 6
    NB2_SY1 = DORM_NORTH2_Y1 + NB2_GABLE_DEPTH
    NB2_SY2 = DORM_NORTH2_Y2  # north end abuts building 1 — full slab, no recess
    north2_bldg_detail.append(
        ramp_slab(
            DORM_X1,
            DORM_CX,
            NB2_SY1,
            NB2_SY2,
            NB2_EAVE_Z,
            NB2_EAVE_Z,
            NB2_EAVE_Z + NB2_SLAB_T,
            NB2_RIDGE_Z,
            Textures.ROOF,
            ts=Textures.GABLE,
        )
    )
    north2_bldg_detail.append(
        ramp_slab(
            DORM_CX,
            DORM_X2,
            NB2_SY1,
            NB2_SY2,
            NB2_EAVE_Z,
            NB2_EAVE_Z,
            NB2_RIDGE_Z,
            NB2_EAVE_Z + NB2_SLAB_T,
            Textures.ROOF,
            ts=Textures.GABLE,
        )
    )
    # Slats on the exposed south gable end only (the north end abuts building 1).
    north2_bldg_detail += gable_slats(
        DORM_X1,
        DORM_X2,
        DORM_CX,
        NB2_EAVE_Z,
        NB2_RIDGE_Z,
        NB2_SLAB_T,
        DORM_NORTH2_Y1,
        NB2_GABLE_DEPTH,
        Textures.GABLE,
        n=8,
        gap=4,
    )
    ENTITIES.append(brush_ent("func_detail", north2_bldg_detail))
    # Interior floor
    BRUSHES.append(
        box(
            DORM_X1 + DORM_WALL,
            DORM_NORTH2_Y1 + DORM_WALL,
            FLOOR_Z1,
            DORM_X2 - DORM_WALL,
            DORM_NORTH2_Y2 - DORM_WALL,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.ROAD,
        )
    )

    # ── Two south buildings — exact copies of north building, stacked N-S ──────────
    # Same X footprint (DORM_X1..DORM_X2), entrance on east face (faces Charles Street).
    # Moved to func_detail to reduce portal complexity in the open campus area.

    def make_south_bldg(
        by1,
        by2,
        slat_lo=False,
        slat_hi=False,
        entrance=True,
        chimney=False,
        door_lo=False,
        door_hi=False,
    ):
        """Build the south abutment building geometry (walls, roof, windows, entrance)
        between Y positions by1 (south) and by2 (north).
        slat_lo/slat_hi add gable wood slats on the by1/-Y and by2/+Y ends.
        entrance adds the east-face entrance arch/door (windows only when False).
        chimney cuts a passable shaft through the east roof slope and ceiling and adds
        a hollow brick stack above the roof (the player can drop into the interior).
        door_lo/door_hi add a ground-floor center doorway on the by1/-Y or by2/+Y wall."""
        bx1, bx2 = DORM_X1, DORM_X2
        cx = (bx1 + bx2) // 2
        ent_hw, ent_h = 48, 120
        wx_list = [bx1 + (cx - ent_hw - bx1) * k // 3 for k in [1, 2]] + [
            (cx + ent_hw) + (bx2 - cx - ent_hw) * k // 3 for k in [1, 2]
        ]
        wy_list = [by1 + (by2 - by1) * k // 4 for k in [1, 2, 3]]

        def wxz():
            return [
                (
                    wx - DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
                    wx + DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
                )
                for fl in range(DORM_FLOORS)
                for wx in wx_list
            ]

        def wyz():
            return [
                (
                    wy - DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
                    wy + DORM_WIN_HW,
                    FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
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
        # Center window openings on 2nd and 3rd floor (no entrance on these faces)
        mid_wxz = [
            (
                cx - DORM_WIN_HW,
                FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_lo,
                cx + DORM_WIN_HW,
                FLOOR_Z2 + fl * DORM_FLOOR_H + dorm_wz_hi,
            )
            for fl in range(1, DORM_FLOORS)
        ]
        brushes.extend(
            layered_wall(
                bx1,
                by1,
                FLOOR_Z2,
                bx2,
                by1 + DORM_WALL,
                FLOOR_Z2 + DORM_H,
                wxz() + mid_wxz + ([dorm_door_open] if door_lo else []),
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
                wxz() + mid_wxz + ([dorm_door_open] if door_hi else []),
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
        east_openings = wyz()
        if entrance:
            # Solid wall above the door — drop the center-column windows, keep entrance only
            east_openings = [
                o for o in east_openings if o[2] <= cy - ent_hw or o[0] >= cy + ent_hw
            ] + [(cy - ent_hw, FLOOR_Z2, cy + ent_hw, FLOOR_Z2 + ent_h)]
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
        # Chimney shaft footprint straddling the roof ridge (only when chimney=True)
        chim_x1 = chim_x2 = chim_y1 = chim_y2 = None
        if chimney:
            chw = 32  # half-width of the 64-unit square shaft (player hull fits)
            ccy = cy + 64  # a little north of the building centre
            chim_x1, chim_x2 = cx - chw, cx + chw
            chim_y1, chim_y2 = ccy - chw, ccy + chw
        # Ceiling slab — split around the shaft when a chimney is present
        if chimney:
            _cz1, _cz2 = FLOOR_Z2 + DORM_H, FLOOR_Z2 + DORM_H + DORM_WALL
            brushes += [
                box(bx1, by1, _cz1, chim_x1, by2, _cz2, "city2_1"),
                box(chim_x2, by1, _cz1, bx2, by2, _cz2, "city2_1"),
                box(chim_x1, by1, _cz1, chim_x2, chim_y1, _cz2, "city2_1"),
                box(chim_x1, chim_y2, _cz1, chim_x2, by2, _cz2, "city2_1"),
            ]
        else:
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
            FLOOR_Z2 + DORM_H + DORM_WALL + DORM_ROOF_H,
            16,
        )
        depth = 6  # slat recess depth; outer face flush with wall
        # Recess the slab gable end only where slats are added (abutting ends stay full)
        sy1 = by1 + depth if slat_lo else by1
        sy2 = by2 - depth if slat_hi else by2
        if chimney:
            # Both slopes split around the shaft so it passes through the ridge
            def _wtop(x):
                return int(
                    eave_z
                    + slab_t
                    + (x - bx1) * (ridge_z - eave_z - slab_t) // (cx - bx1)
                )

            def _etop(x):
                return int(
                    ridge_z + (x - cx) * (eave_z + slab_t - ridge_z) // (bx2 - cx)
                )

            brushes += [
                ramp_slab(  # west slope, south of shaft
                    bx1,
                    cx,
                    sy1,
                    chim_y1,
                    eave_z,
                    eave_z,
                    eave_z + slab_t,
                    ridge_z,
                    Textures.ROOF,
                    ts=Textures.GABLE,
                ),
                ramp_slab(  # west slope, north of shaft
                    bx1,
                    cx,
                    chim_y2,
                    sy2,
                    eave_z,
                    eave_z,
                    eave_z + slab_t,
                    ridge_z,
                    Textures.ROOF,
                    ts=Textures.GABLE,
                ),
                ramp_slab(  # west slope, eave-side fill beside shaft
                    bx1,
                    chim_x1,
                    chim_y1,
                    chim_y2,
                    eave_z,
                    eave_z,
                    eave_z + slab_t,
                    _wtop(chim_x1),
                    Textures.ROOF,
                    ts=Textures.GABLE,
                ),
                ramp_slab(  # east slope, south of shaft
                    cx,
                    bx2,
                    sy1,
                    chim_y1,
                    eave_z,
                    eave_z,
                    ridge_z,
                    eave_z + slab_t,
                    Textures.ROOF,
                    ts=Textures.GABLE,
                ),
                ramp_slab(  # east slope, north of shaft
                    cx,
                    bx2,
                    chim_y2,
                    sy2,
                    eave_z,
                    eave_z,
                    ridge_z,
                    eave_z + slab_t,
                    Textures.ROOF,
                    ts=Textures.GABLE,
                ),
                ramp_slab(  # east slope, eave-side fill beside shaft
                    chim_x2,
                    bx2,
                    chim_y1,
                    chim_y2,
                    eave_z,
                    eave_z,
                    _etop(chim_x2),
                    eave_z + slab_t,
                    Textures.ROOF,
                    ts=Textures.GABLE,
                ),
            ]
            # Hollow brick stack rising above the ridge, open at the top
            # Keep height ≤ 36 so a player on the ridge can jump over the walls
            chim_wall, chim_top = 12, ridge_z + 32
            brushes += [
                box(
                    chim_x1 - chim_wall,
                    chim_y1 - chim_wall,
                    eave_z,
                    chim_x2 + chim_wall,
                    chim_y1,
                    chim_top,
                    "city2_1",
                ),  # south
                box(
                    chim_x1 - chim_wall,
                    chim_y2,
                    eave_z,
                    chim_x2 + chim_wall,
                    chim_y2 + chim_wall,
                    chim_top,
                    "city2_1",
                ),  # north
                box(
                    chim_x1 - chim_wall,
                    chim_y1,
                    eave_z,
                    chim_x1,
                    chim_y2,
                    chim_top,
                    "city2_1",
                ),  # west
                box(
                    chim_x2,
                    chim_y1,
                    eave_z,
                    chim_x2 + chim_wall,
                    chim_y2,
                    chim_top,
                    "city2_1",
                ),  # east
            ]
        else:
            brushes.append(
                ramp_slab(
                    bx1,
                    cx,
                    sy1,
                    sy2,
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
                    sy1,
                    sy2,
                    eave_z,
                    eave_z,
                    ridge_z,
                    eave_z + slab_t,
                    Textures.ROOF,
                    ts=Textures.GABLE,
                )
            )
        if slat_lo:
            brushes += gable_slats(
                bx1,
                bx2,
                cx,
                eave_z,
                ridge_z,
                slab_t,
                by1,
                depth,
                Textures.GABLE,
                n=8,
                gap=4,
            )
        if slat_hi:
            brushes += gable_slats(
                bx1,
                bx2,
                cx,
                eave_z,
                ridge_z,
                slab_t,
                by2,
                -depth,
                Textures.GABLE,
                n=8,
                gap=4,
            )

        # ── Decorative wood trim (entrance arch + window frames) ─────────────────────

        # East-face entrance arch (faces Charles Street)
        if entrance:
            brushes += entrance_arch_ywall(
                cy,
                FLOOR_Z2,
                ent_hw,
                ent_h,
                bx2,
                +1,
                Textures.GABLE,
                pillar_w=14,
                pillar_d=12,
                lintel_h=16,
                arch_h=60,
            )
            # Transom over the door: top + bottom crossbeams plus 4 mullions forming square panes
            grille_d, beam_h, mull_w, trans_h = 8, 6, 6, 26
            # Centre the grille within the pillar depth (bx2 .. bx2+pillar_d)
            _pillar_d = 12
            gx1 = bx2 + _pillar_d // 2 - grille_d // 2
            gx2 = bx2 + _pillar_d // 2 + grille_d // 2
            trans_t = FLOOR_Z2 + ent_h  # top of the door opening
            trans_b = trans_t - trans_h  # crossbeam line below the transom
            brushes.append(
                box(
                    gx1,
                    cy - ent_hw,
                    trans_b - beam_h,
                    gx2,
                    cy + ent_hw,
                    trans_b,
                    Textures.GABLE,
                )
            )  # bottom crossbeam dividing door from transom panes
            brushes.append(
                box(
                    gx1,
                    cy - ent_hw,
                    trans_t - beam_h,
                    gx2,
                    cy + ent_hw,
                    trans_t,
                    Textures.GABLE,
                )
            )  # top crossbeam at the top of the transom panes
            for k in range(5):
                mx = cy - ent_hw + (2 * ent_hw) * k // 4
                brushes.append(
                    box(
                        gx1,
                        mx - mull_w // 2,
                        trans_b,
                        gx2,
                        mx + mull_w // 2,
                        trans_t,
                        Textures.GABLE,
                    )
                )  # transom mullion
            # Frame recessed into the door opening (jambs + head lining the reveal,
            # like the window frames) using the same gable wood as the arch/pillars.
            brushes += win_frame_ywall(
                cy - ent_hw,
                cy + ent_hw,
                FLOOR_Z2,
                FLOOR_Z2 + ent_h,
                bx2,
                -1,
                Textures.GABLE,
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
                crossbar=False,
                bottom=False,
            )
        # Window frames — south face (inward, flush outer→inner)
        for xl, zb, xr, zt in wxz():
            brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by1,
                +1,
                Textures.GABLE,
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
            )
        # Center window frames — south face, 2nd and 3rd floor
        for xl, zb, xr, zt in mid_wxz:
            brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by1,
                +1,
                Textures.GABLE,
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
            )
        # Window frames — north face
        for xl, zb, xr, zt in wxz():
            brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by2,
                -1,
                Textures.GABLE,
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
            )
        # Center window frames — north face, 2nd and 3rd floor
        for xl, zb, xr, zt in mid_wxz:
            brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by2,
                -1,
                Textures.GABLE,
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
            )
        # Window frames — west face
        for yl, zb, yr, zt in wyz():
            brushes += win_frame_ywall(
                yl,
                yr,
                zb,
                zt,
                bx1,
                +1,
                Textures.GABLE,
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
            )
        # Window frames — east face (skip ground-floor window overlapping the entrance
        # opening when an entrance is present)
        for yl, zb, yr, zt in wyz():
            if entrance and not (yr <= cy - ent_hw or yl >= cy + ent_hw):
                continue
            brushes += win_frame_ywall(
                yl,
                yr,
                zb,
                zt,
                bx2,
                -1,
                Textures.GABLE,
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
            )
        # Door frames — ground-floor center doorways to adjacent south buildings
        if door_hi:
            brushes += win_frame_xwall(
                cx - DORM_INNER_DOOR_HW,
                cx + DORM_INNER_DOOR_HW,
                FLOOR_Z2,
                FLOOR_Z2 + DORM_INNER_DOOR_H,
                by2,
                -1,
                Textures.GABLE,
                fw=8,  # thick frame bars
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
                crossbar=False,
                bottom=False,
            )
        if door_lo:
            brushes += win_frame_xwall(
                cx - DORM_INNER_DOOR_HW,
                cx + DORM_INNER_DOOR_HW,
                FLOOR_Z2,
                FLOOR_Z2 + DORM_INNER_DOOR_H,
                by1,
                +1,
                Textures.GABLE,
                fw=8,  # thick frame bars
                fd=DORM_WALL,
                margin=DORM_WIN_MARGIN,
                crossbar=False,
                bottom=False,
            )
        return brushes

    ENTITIES.append(
        brush_ent(
            "func_detail",
            make_south_bldg(
                DORM_SOUTH1_Y1,
                DORM_SOUTH1_Y2,
                slat_lo=True,
                chimney=True,
                door_hi=True,
            ),
        )
    )
    ENTITIES.append(
        brush_ent(
            "func_detail",
            make_south_bldg(
                DORM_SOUTH2_Y1,
                DORM_SOUTH2_Y2,
                slat_hi=True,
                entrance=False,
                door_lo=True,
            ),
        )
    )

    # ── Threshold floors across the inter-building doorways (fill the wall seam) ──
    for seam_y in (DORM_NORTH_Y1, DORM_SOUTH1_Y2):
        BRUSHES.append(
            box(
                DORM_CX - DORM_INNER_DOOR_HW,
                seam_y - DORM_WALL,
                FLOOR_Z1,
                DORM_CX + DORM_INNER_DOOR_HW,
                seam_y + DORM_WALL,
                FLOOR_Z2,
                Textures.GROUND,
                tt=Textures.ROAD,
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
