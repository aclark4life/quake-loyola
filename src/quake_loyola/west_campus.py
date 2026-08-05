from .constants import FLOOR_Z1, WORLD_Y2
from .constants.bridge import BRIDGE_CENTER_SPAN_OFFSET
from .constants.derived import (
    BRIDGE_DZ2,
    CHARLES_Y1,
    DORM,
    DORM_FRONT_WALKWAY_SPUR_X1,
    DORM_FRONT_WALKWAY_SPUR_Y2,
    DORM_FRONT_WALKWAY_X1,
    DORM_FRONT_WALKWAY_X2,
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
    FENCE_X1,
    FENCE_X2,
    FLOOR_Z2,
    SDORM_LIFT,
    SDORM_STAIR_N,
    SDORM_STAIR_RISE,
    SDORM_STAIR_RUN,
    SDORM_STAIR_X1,
    SDORM_STAIR_X2,
    SDORM_STAIR_Y1,
    SDORM_STAIR_Y2,
    WALL_T,
)
from .constants.dorm import (
    DORM_BRICK_GATE_H,
    DORM_BRICK_PILLAR_CAP_H,
    DORM_BRICK_PILLAR_CAP_OVH,
    DORM_BRICK_PILLAR_GAP,
    DORM_BRICK_PILLAR_H_OFFSET,
    DORM_BRICK_PILLAR_PROUD,
    DORM_BRICK_PILLAR_SEPARATION,
    DORM_BRICK_PILLAR_W,
    DORM_BRICK_WALL_HW,
    DORM_DOOR_OFF,
    DORM_DOOR_W,
    DORM_ENT_H,
    DORM_ENT_HW,
    DORM_GABLE_DEPTH,
    DORM_INNER_DOOR_H,
    DORM_INNER_DOOR_HW,
    DORM_SLAB_T,
    DORM_WIN_HH,
    DORM_WIN_HW,
    DORM_WIN_MARGIN,
)
from .constants.flags import (
    BRIDGE_ENABLED_SPAN_CENTER,
    WEST_CAMPUS_ENABLED_DORMS,
    WEST_CAMPUS_ENABLED_FENCE,
    WEST_CAMPUS_ENABLED_SIDEWALK,
    WEST_CAMPUS_ENABLED_TERRAIN,
    WEST_CAMPUS_ENABLED_WALL,
)
from .constants.textures import Textures
from .constants.world import FENCE_H, FENCE_SPACING
from .geometry import (
    box,
    brush_ent,
    entrance_arch_ywall,
    gable_slats,
    iron_fence,
    layered_wall,
    layered_wall_y,
    ramp_slab,
    ramp_slab_y,
    win_frame_xwall,
    win_frame_ywall,
)
from .terrain.west_campus import terrain_z, wct_y


def _build_iron_fence(ENTITIES):
    """Build the east-side iron fence for the west-campus frontage."""
    fence_brushes = []

    fence_y2 = WORLD_Y2 - WALL_T

    def fence_base_at(y):
        """Return the fence base height from the hillside terrain."""
        return terrain_z(FENCE_X1, y)

    rail_lo, rail_hi = FENCE_H - 28, FENCE_H - 26
    rail_ys = sorted(
        {CHARLES_Y1, fence_y2} | {y for y in wct_y if CHARLES_Y1 < y < fence_y2}
    )
    for ny1, ny2 in zip(rail_ys, rail_ys[1:], strict=False):
        b1, b2 = fence_base_at(ny1), fence_base_at(ny2)
        fence_brushes.append(
            ramp_slab_y(
                FENCE_X1,
                FENCE_X2,
                ny1,
                ny2,
                b1 + rail_lo,
                b2 + rail_lo,
                b1 + rail_hi,
                b2 + rail_hi,
                Textures.FENCE,
            )
        )

    picket_y = CHARLES_Y1
    picket_index = 0
    while True:
        picket_width = 8 if picket_index % 10 == 0 else 2
        if picket_y + picket_width > fence_y2:
            break
        fence_base = fence_base_at(picket_y)
        fence_brushes.append(
            box(
                FENCE_X1,
                picket_y,
                fence_base,
                FENCE_X2,
                picket_y + picket_width,
                fence_base + FENCE_H,
                Textures.FENCE,
            )
        )
        picket_y += FENCE_SPACING
        picket_index += 1

    pillar_hw = 24
    pillar_cx = (FENCE_X1 + FENCE_X2) // 2
    pillar_y1 = CHARLES_Y1 - pillar_hw
    pillar_y2 = CHARLES_Y1 + pillar_hw
    pillar_base = fence_base_at(CHARLES_Y1)
    cap_h = 10
    cap_ovh = 4
    pillar_top = pillar_base + FENCE_H + 12
    fence_brushes.append(
        box(
            pillar_cx - pillar_hw,
            pillar_y1,
            pillar_base,
            pillar_cx + pillar_hw,
            pillar_y2,
            pillar_top,
            Textures.BUILDING,
        )
    )
    fence_brushes.append(
        box(
            pillar_cx - pillar_hw - cap_ovh,
            pillar_y1 - cap_ovh,
            pillar_top,
            pillar_cx + pillar_hw + cap_ovh,
            pillar_y2 + cap_ovh,
            pillar_top + cap_h,
            Textures.BUILDING,
        )
    )

    if fence_brushes:
        ENTITIES.append(brush_ent("func_detail", fence_brushes))


def _build_brick_wall(BRUSHES, ENTITIES):
    """Build the west brick wall, gate, pillars, and pier-side fence run."""

    wall_hw = DORM_BRICK_WALL_HW

    if BRIDGE_ENABLED_SPAN_CENTER:
        wall_shift_y = BRIDGE_CENTER_SPAN_OFFSET[1]
        wall_shift_z = BRIDGE_CENTER_SPAN_OFFSET[2]
    else:
        wall_shift_y = 0
        wall_shift_z = 0
    bridge_top_z = BRIDGE_DZ2 + wall_shift_z
    wall_start_y = DORM_SOUTH2_Y2 + wall_shift_y
    s_door_y = DORM_SOUTH2_Y2 + DORM_DOOR_OFF + wall_shift_y
    wall_end_y = DORM_WALL_S_Y2 + wall_shift_y

    gate_base = FLOOR_Z2 + SDORM_LIFT
    gate_top = gate_base + DORM_BRICK_GATE_H

    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            wall_start_y,
            FLOOR_Z2,
            DORM_PIER_X + wall_hw,
            s_door_y - DORM_DOOR_W // 2,
            bridge_top_z,
            Textures.BUILDING,
        )
    )
    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            s_door_y + DORM_DOOR_W // 2,
            FLOOR_Z2,
            DORM_PIER_X + wall_hw,
            wall_end_y,
            bridge_top_z,
            Textures.BUILDING,
        )
    )
    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            s_door_y - DORM_DOOR_W // 2,
            gate_top,
            DORM_PIER_X + wall_hw,
            s_door_y + DORM_DOOR_W // 2,
            bridge_top_z,
            Textures.BUILDING,
        )
    )

    pillar_w = DORM_BRICK_PILLAR_W
    pillar_proud = DORM_BRICK_PILLAR_PROUD
    pillar_h = bridge_top_z + DORM_BRICK_PILLAR_H_OFFSET
    px1 = DORM_PIER_X - wall_hw - pillar_proud
    px2 = DORM_PIER_X + wall_hw + pillar_proud
    cap_h = DORM_BRICK_PILLAR_CAP_H
    cap_overhang = DORM_BRICK_PILLAR_CAP_OVH
    door_north = s_door_y + DORM_DOOR_W // 2
    for py1, py2 in [
        (
            door_north + DORM_BRICK_PILLAR_GAP,
            door_north + DORM_BRICK_PILLAR_GAP + pillar_w,
        ),
        (
            door_north
            + DORM_BRICK_PILLAR_GAP
            + pillar_w
            + DORM_BRICK_PILLAR_SEPARATION,
            door_north
            + DORM_BRICK_PILLAR_GAP
            + pillar_w
            + DORM_BRICK_PILLAR_SEPARATION
            + pillar_w,
        ),
    ]:
        pillar_brushes = [
            box(px1, py1, FLOOR_Z2, px2, py2, pillar_h, Textures.BUILDING),
            box(
                px1 - cap_overhang,
                py1 - cap_overhang,
                pillar_h,
                px2 + cap_overhang,
                py2 + cap_overhang,
                pillar_h + cap_h,
                Textures.BUILDING,
            ),
        ]
        ENTITIES.append(brush_ent("func_detail", pillar_brushes))
    fence_brushes = iron_fence(
        [
            (wall_start_y, s_door_y - DORM_DOOR_W // 2),
            (
                s_door_y - DORM_DOOR_W // 2,
                s_door_y + DORM_DOOR_W // 2,
            ),
            (s_door_y + DORM_DOOR_W // 2, wall_end_y),
        ],
        DORM_PIER_X - 1,
        DORM_PIER_X + 1,
        Textures.FENCE,
        bridge_top_z,
    )
    if fence_brushes:
        ENTITIES.append(brush_ent("func_detail", fence_brushes))


def _build_sidewalk(BRUSHES):
    """Build the dorm-front terrace walk and its north spur.

    The walkway is tiled into square panels, extends south to CHARLES_Y1,
    and uses a terrain-following curb along its east edge.
    """
    walk_lift = SDORM_LIFT - 10
    _SW_SLAB_LEN = 80
    _SW_GAP = 2
    _CURB_W = 8
    _CURB_GAP = 2

    def slabs_y(x1, x2, y1, y2):
        """Tile a flat north-south run into square panels."""
        brushes = []
        step = _SW_SLAB_LEN + _SW_GAP
        y = y1
        while y > y2:
            sy2 = max(y - _SW_SLAB_LEN, y2)
            brushes.append(
                box(x1, sy2, FLOOR_Z2, x2, y, FLOOR_Z2 + walk_lift, Textures.STONE)
            )
            y -= step
        return brushes

    def curb_y(x1, x2, y1, y2):
        """Build a terrain-following curb along a north-south run."""
        brushes = []
        curb_cx = (x1 + x2) / 2
        ys = sorted({y1, y2} | {y for y in wct_y if y2 < y < y1}, reverse=True)
        for ny1, ny2 in zip(ys, ys[1:], strict=False):
            b1, b2 = terrain_z(curb_cx, ny1), terrain_z(curb_cx, ny2)
            brushes.append(
                ramp_slab_y(
                    x1,
                    x2,
                    ny1,
                    ny2,
                    b1,
                    b2,
                    FLOOR_Z2 + walk_lift,
                    FLOOR_Z2 + walk_lift,
                    Textures.STONE,
                )
            )
        return brushes

    walk = []

    walk.extend(
        slabs_y(
            DORM_FRONT_WALKWAY_X1, DORM_FRONT_WALKWAY_X2, DORM_SOUTH2_Y2, CHARLES_Y1
        )
    )

    walk.extend(
        slabs_y(
            DORM_FRONT_WALKWAY_SPUR_X1,
            DORM_FRONT_WALKWAY_X2,
            DORM_FRONT_WALKWAY_SPUR_Y2,
            DORM_SOUTH2_Y2,
        )
    )

    curb_x1 = DORM_FRONT_WALKWAY_X2 + _CURB_GAP
    curb_x2 = curb_x1 + _CURB_W
    walk.extend(curb_y(curb_x1, curb_x2, DORM_FRONT_WALKWAY_SPUR_Y2, CHARLES_Y1))
    BRUSHES.extend(walk)


def _make_dorm_context():
    """Return shared dorm geometry values and window-opening helpers."""

    dorm_cx = (DORM.x1 + DORM.x2) // 2
    dorm_north_cy = (DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2
    dorm_door_open = (
        dorm_cx - DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        dorm_cx + DORM_INNER_DOOR_HW,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
    )
    dorm_wx = [DORM.x1 + (dorm_cx - DORM_ENT_HW - DORM.x1) * k // 3 for k in [1, 2]] + [
        (dorm_cx + DORM_ENT_HW) + (DORM.x2 - dorm_cx - DORM_ENT_HW) * k // 3
        for k in [1, 2]
    ]
    dorm_wy = [
        DORM_NORTH_Y1 + (DORM_NORTH_Y2 - DORM_NORTH_Y1) * k // 4 for k in [1, 2, 3]
    ]

    dorm_wz_lo = (DORM.floor_h - DORM_WIN_HH * 2) // 2
    dorm_wz_hi = dorm_wz_lo + DORM_WIN_HH * 2

    def dorm_window_z(fl):
        base_z = FLOOR_Z2 + fl * DORM.floor_h
        return base_z + dorm_wz_lo, base_z + dorm_wz_hi

    def dorm_window_levels(start_floor=0):
        for fl in range(start_floor, DORM.floors):
            yield fl, *dorm_window_z(fl)

    def dorm_window_openings(
        centers, *, start_floor=0, double=False, include_window=None
    ):
        openings = []
        for fl, zb, zt in dorm_window_levels(start_floor):
            for center in centers:
                if include_window and not include_window(center, fl):
                    continue
                if double:
                    openings.append((center - DORM_WIN_HW * 2, zb, center, zt))
                    openings.append((center, zb, center + DORM_WIN_HW * 2, zt))
                else:
                    openings.append(
                        (center - DORM_WIN_HW, zb, center + DORM_WIN_HW, zt)
                    )
        return openings

    def nb_wins_yz(wy_list):
        """Return single-window openings for a Y-facing wall."""
        return dorm_window_openings(wy_list)

    def nb_wins_yz_west(wy_list):
        """Return west-face openings for the exposed upper floors."""
        return dorm_window_openings(wy_list, start_floor=2)

    def nb_wins_yz_double(wy_list):
        """Return paired window openings for a Y-facing wall."""
        return dorm_window_openings(wy_list, double=True)

    def nb_wins_xz_upper(wx_list, x_clear=None):
        """Return north/south wall openings from floor 1 up.

        Openings west of x_clear start at floor 2 instead.
        """
        return dorm_window_openings(
            wx_list,
            start_floor=1,
            include_window=lambda wx, fl: x_clear is None or wx >= x_clear or fl >= 2,
        )

    return {
        "dorm_cx": dorm_cx,
        "dorm_north_cy": dorm_north_cy,
        "dorm_door_open": dorm_door_open,
        "dorm_wx": dorm_wx,
        "dorm_wy": dorm_wy,
        "tunn_h": DORM_INNER_DOOR_H,
        "dorm_window_levels": dorm_window_levels,
        "dorm_window_openings": dorm_window_openings,
        "nb_wins_xz_upper": nb_wins_xz_upper,
        "nb_wins_yz": nb_wins_yz,
        "nb_wins_yz_double": nb_wins_yz_double,
        "nb_wins_yz_west": nb_wins_yz_west,
    }


def _north_dorm_center_window_openings(dorm_ctx):
    """Return the centered upper-floor openings on the north dorm back wall."""

    dorm_cx = dorm_ctx["dorm_cx"]
    dorm_window_levels = dorm_ctx["dorm_window_levels"]
    return [
        (
            dorm_cx - DORM_WIN_HW,
            zb,
            dorm_cx + DORM_WIN_HW,
            zt,
        )
        for _, zb, zt in dorm_window_levels(1)
    ]


def _north_dorm_east_window_openings(dorm_ctx):
    """Return the east-wall window openings for the north dorm."""

    nb_wins_yz = dorm_ctx["nb_wins_yz"]
    nb_wins_yz_double = dorm_ctx["nb_wins_yz_double"]
    nb1_e_double_wy = DORM_NORTH_Y1 + 157
    nb1_e_single_wy = DORM_NORTH_Y1 + 334
    return nb_wins_yz_double([nb1_e_double_wy]) + nb_wins_yz([nb1_e_single_wy])


def _build_north_dorm_floor_brush():
    """Return the north dorm interior floor slab."""

    return box(
        DORM.x1 + DORM.wall_t,
        DORM_NORTH_Y1 + DORM.wall_t,
        FLOOR_Z1,
        DORM.x2 - DORM.wall_t,
        DORM_NORTH_Y2 - DORM.wall_t,
        FLOOR_Z2,
        Textures.GROUND,
        tt=Textures.ROAD,
    )


def _build_north_dorm_wall_brushes(dorm_ctx, center_window_openings, dorm_e_openings):
    """Return the north dorm wall runs and top cap slab."""

    dorm_north_cy = dorm_ctx["dorm_north_cy"]
    dorm_door_open = dorm_ctx["dorm_door_open"]
    dorm_wx = dorm_ctx["dorm_wx"]
    dorm_wy = dorm_ctx["dorm_wy"]
    nb_wins_xz_upper = dorm_ctx["nb_wins_xz_upper"]
    nb_wins_yz_west = dorm_ctx["nb_wins_yz_west"]
    tunn_h = dorm_ctx["tunn_h"]

    wall_brushes = []
    wall_brushes.extend(
        layered_wall(
            DORM.x1,
            DORM_NORTH_Y1,
            FLOOR_Z2,
            DORM.x2,
            DORM_NORTH_Y1 + DORM.wall_t,
            FLOOR_Z2 + DORM_H,
            [dorm_door_open],
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall(
            DORM.x1,
            DORM_NORTH_Y2 - DORM.wall_t,
            FLOOR_Z2,
            DORM.x2,
            DORM_NORTH_Y2,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz_upper(dorm_wx, x_clear=-1652) + center_window_openings,
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall_y(
            DORM_NORTH_Y1 + DORM.wall_t,
            DORM.x2 - DORM.wall_t,
            FLOOR_Z2,
            DORM_NORTH_Y2 - DORM.wall_t,
            DORM.x2,
            FLOOR_Z2 + DORM_H,
            dorm_e_openings,
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall_y(
            DORM_NORTH_Y1 + DORM.wall_t,
            DORM.x1,
            FLOOR_Z2,
            DORM_NORTH_Y2 - DORM.wall_t,
            DORM.x1 + DORM.wall_t,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz_west(dorm_wy)
            + [
                (
                    dorm_north_cy - DORM_INNER_DOOR_HW,
                    FLOOR_Z2,
                    dorm_north_cy + DORM_INNER_DOOR_HW,
                    FLOOR_Z2 + tunn_h,
                )
            ],
            Textures.BUILDING,
        )
    )
    wall_brushes.append(
        box(
            DORM.x1,
            DORM_NORTH_Y1,
            FLOOR_Z2 + DORM_H,
            DORM.x2,
            DORM_NORTH_Y2,
            FLOOR_Z2 + DORM_H + DORM.wall_t,
            Textures.BUILDING,
        )
    )
    return wall_brushes


def _build_north_dorm_window_frame_brushes(
    dorm_ctx, center_window_openings, dorm_e_openings
):
    """Return the north dorm window and door trim brushes."""

    dorm_cx = dorm_ctx["dorm_cx"]
    dorm_north_cy = dorm_ctx["dorm_north_cy"]
    dorm_wx = dorm_ctx["dorm_wx"]
    dorm_wy = dorm_ctx["dorm_wy"]
    nb_wins_xz_upper = dorm_ctx["nb_wins_xz_upper"]
    nb_wins_yz_west = dorm_ctx["nb_wins_yz_west"]
    tunn_h = dorm_ctx["tunn_h"]

    frame_brushes = []
    for xl, zb, xr, zt in nb_wins_xz_upper(dorm_wx, x_clear=-1652):
        frame_brushes += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            DORM_NORTH_Y2,
            -1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )

    for xl, zb, xr, zt in center_window_openings:
        frame_brushes += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            DORM_NORTH_Y2,
            -1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
            crossbar=True,
        )

    frame_brushes += win_frame_xwall(
        dorm_cx - DORM_INNER_DOOR_HW,
        dorm_cx + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
        DORM_NORTH_Y1,
        +1,
        Textures.GABLE,
        fw=8,
        fd=DORM.wall_t,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )

    for yl, zb, yr, zt in dorm_e_openings:
        frame_brushes += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM.x2,
            -1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )

    for yl, zb, yr, zt in nb_wins_yz_west(dorm_wy):
        frame_brushes += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM.x1,
            +1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )

    frame_brushes += win_frame_ywall(
        dorm_north_cy - DORM_INNER_DOOR_HW,
        dorm_north_cy + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + tunn_h,
        DORM.x1,
        +1,
        Textures.GABLE,
        fw=8,
        fd=DORM.wall_t,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )
    return frame_brushes


def _build_north_dorm_roof_brushes(dorm_ctx):
    """Return the north dorm roof slabs and gable slats."""

    dorm_cx = dorm_ctx["dorm_cx"]
    dorm_eave_z = FLOOR_Z2 + DORM_H + DORM.wall_t
    dorm_ridge_z = dorm_eave_z + DORM_ROOF_H
    dorm_nb_sy1 = DORM_NORTH_Y1
    dorm_nb_sy2 = DORM_NORTH_Y2 - DORM_GABLE_DEPTH
    return [
        ramp_slab(
            DORM.x1,
            dorm_cx,
            dorm_nb_sy1,
            dorm_nb_sy2,
            dorm_eave_z,
            dorm_eave_z,
            dorm_eave_z + DORM_SLAB_T,
            dorm_ridge_z,
            Textures.ROOF,
            ts=Textures.GABLE,
        ),
        ramp_slab(
            dorm_cx,
            DORM.x2,
            dorm_nb_sy1,
            dorm_nb_sy2,
            dorm_eave_z,
            dorm_eave_z,
            dorm_ridge_z,
            dorm_eave_z + DORM_SLAB_T,
            Textures.ROOF,
            ts=Textures.GABLE,
        ),
        *gable_slats(
            DORM.x1,
            DORM.x2,
            dorm_cx,
            dorm_eave_z,
            dorm_ridge_z,
            DORM_SLAB_T,
            DORM_NORTH_Y2,
            -DORM_GABLE_DEPTH,
            Textures.GABLE,
            n=8,
            gap=4,
        ),
    ]


def _build_north_dorm(dorm_ctx):
    """Build the northern dorm shell, roof, and interior floor slab."""

    center_window_openings = _north_dorm_center_window_openings(dorm_ctx)
    dorm_e_openings = _north_dorm_east_window_openings(dorm_ctx)

    north_bldg_detail = []
    north_bldg_detail.extend(
        _build_north_dorm_wall_brushes(
            dorm_ctx,
            center_window_openings,
            dorm_e_openings,
        )
    )
    north_bldg_detail.extend(
        _build_north_dorm_window_frame_brushes(
            dorm_ctx,
            center_window_openings,
            dorm_e_openings,
        )
    )
    north_bldg_detail.extend(_build_north_dorm_roof_brushes(dorm_ctx))

    return (
        _build_north_dorm_floor_brush(),
        brush_ent("func_detail", north_bldg_detail),
    )


def _make_second_north_dorm_context(dorm_ctx):
    """Return shared bounds and openings for the second north dorm."""

    dorm_cx = dorm_ctx["dorm_cx"]
    dorm_window_levels = dorm_ctx["dorm_window_levels"]
    nb_wins_yz = dorm_ctx["nb_wins_yz"]
    nb_wins_yz_double = dorm_ctx["nb_wins_yz_double"]

    dorm_north2_y2 = DORM_NORTH_Y1
    dorm_north2_y1 = dorm_north2_y2 - (DORM_NORTH_Y2 - DORM_NORTH_Y1)
    dorm_wy2 = [
        dorm_north2_y1 + (dorm_north2_y2 - dorm_north2_y1) * k // 4 for k in [1, 2, 3]
    ]
    nb2_e_wy_s1 = dorm_north2_y1 + 82
    nb2_e_wy_s2 = dorm_north2_y1 + 184
    nb2_e_double_wy = dorm_north2_y1 + 326
    return {
        "dorm_north2_y1": dorm_north2_y1,
        "dorm_north2_y2": dorm_north2_y2,
        "dorm_wy2": dorm_wy2,
        "nb2_cx_opens": [
            (
                dorm_cx - DORM_WIN_HW,
                zb,
                dorm_cx + DORM_WIN_HW,
                zt,
            )
            for _, zb, zt in dorm_window_levels(1)
        ],
        "nb2_e_openings": nb_wins_yz([nb2_e_wy_s1, nb2_e_wy_s2])
        + nb_wins_yz_double([nb2_e_double_wy]),
    }


def _build_second_north_dorm_floor_brush(second_ctx):
    """Return the second north dorm interior floor slab."""

    dorm_north2_y1 = second_ctx["dorm_north2_y1"]
    dorm_north2_y2 = second_ctx["dorm_north2_y2"]
    return box(
        DORM.x1 + DORM.wall_t,
        dorm_north2_y1 + DORM.wall_t,
        FLOOR_Z1,
        DORM.x2 - DORM.wall_t,
        dorm_north2_y2 - DORM.wall_t,
        FLOOR_Z2,
        Textures.GROUND,
        tt=Textures.ROAD,
    )


def _build_second_north_dorm_wall_brushes(dorm_ctx, second_ctx):
    """Return the second north dorm wall runs and top cap slab."""

    dorm_door_open = dorm_ctx["dorm_door_open"]
    dorm_wx = dorm_ctx["dorm_wx"]
    nb_wins_xz_upper = dorm_ctx["nb_wins_xz_upper"]
    nb_wins_yz_west = dorm_ctx["nb_wins_yz_west"]
    dorm_north2_y1 = second_ctx["dorm_north2_y1"]
    dorm_north2_y2 = second_ctx["dorm_north2_y2"]
    dorm_wy2 = second_ctx["dorm_wy2"]
    nb2_cx_opens = second_ctx["nb2_cx_opens"]
    nb2_e_openings = second_ctx["nb2_e_openings"]

    wall_brushes = []
    wall_brushes.extend(
        layered_wall(
            DORM.x1,
            dorm_north2_y1,
            FLOOR_Z2,
            DORM.x2,
            dorm_north2_y1 + DORM.wall_t,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz_upper(dorm_wx, x_clear=-1652) + nb2_cx_opens,
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall(
            DORM.x1,
            dorm_north2_y2 - DORM.wall_t,
            FLOOR_Z2,
            DORM.x2,
            dorm_north2_y2,
            FLOOR_Z2 + DORM_H,
            [dorm_door_open],
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall_y(
            dorm_north2_y1 + DORM.wall_t,
            DORM.x2 - DORM.wall_t,
            FLOOR_Z2,
            dorm_north2_y2 - DORM.wall_t,
            DORM.x2,
            FLOOR_Z2 + DORM_H,
            nb2_e_openings,
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall_y(
            dorm_north2_y1 + DORM.wall_t,
            DORM.x1,
            FLOOR_Z2,
            dorm_north2_y2 - DORM.wall_t,
            DORM.x1 + DORM.wall_t,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz_west(dorm_wy2),
            Textures.BUILDING,
        )
    )
    wall_brushes.append(
        box(
            DORM.x1,
            dorm_north2_y1,
            FLOOR_Z2 + DORM_H,
            DORM.x2,
            dorm_north2_y2,
            FLOOR_Z2 + DORM_H + DORM.wall_t,
            Textures.BUILDING,
        )
    )
    return wall_brushes


def _build_second_north_dorm_window_frame_brushes(dorm_ctx, second_ctx):
    """Return the second north dorm window and door trim brushes."""

    dorm_cx = dorm_ctx["dorm_cx"]
    dorm_wx = dorm_ctx["dorm_wx"]
    nb_wins_xz_upper = dorm_ctx["nb_wins_xz_upper"]
    nb_wins_yz_west = dorm_ctx["nb_wins_yz_west"]
    dorm_north2_y1 = second_ctx["dorm_north2_y1"]
    dorm_north2_y2 = second_ctx["dorm_north2_y2"]
    dorm_wy2 = second_ctx["dorm_wy2"]
    nb2_cx_opens = second_ctx["nb2_cx_opens"]
    nb2_e_openings = second_ctx["nb2_e_openings"]

    frame_brushes = []
    for xl, zb, xr, zt in nb_wins_xz_upper(dorm_wx, x_clear=-1652):
        frame_brushes += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            dorm_north2_y1,
            +1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )
    for xl, zb, xr, zt in nb2_cx_opens:
        frame_brushes += win_frame_xwall(
            xl,
            xr,
            zb,
            zt,
            dorm_north2_y1,
            +1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )

    for yl, zb, yr, zt in nb2_e_openings:
        frame_brushes += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM.x2,
            -1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )

    frame_brushes += win_frame_xwall(
        dorm_cx - DORM_INNER_DOOR_HW,
        dorm_cx + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
        dorm_north2_y2,
        -1,
        Textures.GABLE,
        fw=8,
        fd=DORM.wall_t,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )

    for yl, zb, yr, zt in nb_wins_yz_west(dorm_wy2):
        frame_brushes += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            DORM.x1,
            +1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )
    return frame_brushes


def _build_second_north_dorm_roof_brushes(dorm_ctx, second_ctx):
    """Return the second north dorm roof slabs and gable slats."""

    dorm_cx = dorm_ctx["dorm_cx"]
    dorm_north2_y1 = second_ctx["dorm_north2_y1"]
    dorm_north2_y2 = second_ctx["dorm_north2_y2"]
    nb2_eave_z = FLOOR_Z2 + DORM_H + DORM.wall_t
    nb2_ridge_z = nb2_eave_z + DORM_ROOF_H
    nb2_slab_t = DORM_SLAB_T
    nb2_gable_depth = DORM_GABLE_DEPTH
    nb2_sy1 = dorm_north2_y1 + nb2_gable_depth
    nb2_sy2 = dorm_north2_y2
    return [
        ramp_slab(
            DORM.x1,
            dorm_cx,
            nb2_sy1,
            nb2_sy2,
            nb2_eave_z,
            nb2_eave_z,
            nb2_eave_z + nb2_slab_t,
            nb2_ridge_z,
            Textures.ROOF,
            ts=Textures.GABLE,
        ),
        ramp_slab(
            dorm_cx,
            DORM.x2,
            nb2_sy1,
            nb2_sy2,
            nb2_eave_z,
            nb2_eave_z,
            nb2_ridge_z,
            nb2_eave_z + nb2_slab_t,
            Textures.ROOF,
            ts=Textures.GABLE,
        ),
        *gable_slats(
            DORM.x1,
            DORM.x2,
            dorm_cx,
            nb2_eave_z,
            nb2_ridge_z,
            nb2_slab_t,
            dorm_north2_y1,
            nb2_gable_depth,
            Textures.GABLE,
            n=8,
            gap=4,
        ),
    ]


def _build_second_north_dorm(dorm_ctx):
    """Build the second north dorm shell, roof, and interior floor slab."""

    second_ctx = _make_second_north_dorm_context(dorm_ctx)

    north2_bldg_detail = []
    north2_bldg_detail.extend(
        _build_second_north_dorm_wall_brushes(dorm_ctx, second_ctx)
    )
    north2_bldg_detail.extend(
        _build_second_north_dorm_window_frame_brushes(dorm_ctx, second_ctx)
    )
    north2_bldg_detail.extend(
        _build_second_north_dorm_roof_brushes(dorm_ctx, second_ctx)
    )

    return (
        _build_second_north_dorm_floor_brush(second_ctx),
        brush_ent("func_detail", north2_bldg_detail),
    )


def _make_south_dorm_context(
    dorm_ctx,
    by1,
    by2,
    slat_lo=False,
    slat_hi=False,
    entrance=True,
    chimney=False,
    door_lo=False,
    door_hi=False,
    north_pier_x=None,
    north_pier_hw=0,
    north_min_floor=0,
    west_door=True,
    stairwell=False,
):
    """Return shared geometry and option state for one south dorm shell."""

    dorm_door_open = dorm_ctx["dorm_door_open"]
    dorm_window_openings = dorm_ctx["dorm_window_openings"]

    bx1, bx2 = DORM.x1, DORM.x2
    cx = (bx1 + bx2) // 2
    ent_hw, ent_h = 48, DORM_ENT_H
    wx_list = [bx1 + (cx - ent_hw - bx1) * k // 3 for k in [1, 2]] + [
        (cx + ent_hw) + (bx2 - cx - ent_hw) * k // 3 for k in [1, 2]
    ]
    wy_list = [by1 + (by2 - by1) * k // 4 for k in [1, 2, 3]]

    def wxz():
        return dorm_window_openings(wx_list)

    def wyz():
        return dorm_window_openings(wy_list)

    def wyz_west():
        """Return west-face openings above the hillside."""
        return dorm_window_openings(wy_list, start_floor=1)

    def wxz_north():
        """Return north-face openings filtered by floor and pier overlap."""
        wins = dorm_window_openings(wx_list, start_floor=north_min_floor)
        if north_pier_x is not None:
            wins = [
                (xl, zb, xr, zt)
                for xl, zb, xr, zt in wins
                if xr <= north_pier_x - north_pier_hw
                or xl >= north_pier_x + north_pier_hw
            ]
        return wins

    return {
        "by1": by1,
        "by2": by2,
        "bx1": bx1,
        "bx2": bx2,
        "cx": cx,
        "chimney": chimney,
        "door_hi": door_hi,
        "door_lo": door_lo,
        "dorm_door_open": dorm_door_open,
        "ent_h": ent_h,
        "ent_hw": ent_hw,
        "entrance": entrance,
        "north_pier_hw": north_pier_hw,
        "north_pier_x": north_pier_x,
        "north_min_floor": north_min_floor,
        "slat_hi": slat_hi,
        "slat_lo": slat_lo,
        "stairwell": stairwell,
        "west_door": west_door,
        "wxz": wxz,
        "wxz_north": wxz_north,
        "wyz": wyz,
        "wyz_west": wyz_west,
    }


def _build_south_dorm_floor_brushes(south_ctx):
    """Return the ground slab and optional stairwell brushes."""

    by1 = south_ctx["by1"]
    by2 = south_ctx["by2"]
    bx1 = south_ctx["bx1"]
    bx2 = south_ctx["bx2"]
    stairwell = south_ctx["stairwell"]

    floor_brushes = []
    if stairwell:
        floor_brushes += [
            box(
                bx1 + DORM.wall_t,
                by1 + DORM.wall_t,
                FLOOR_Z1,
                bx2 - DORM.wall_t,
                SDORM_STAIR_Y1,
                FLOOR_Z2,
                Textures.GROUND,
                tt=Textures.ROAD,
            ),
            box(
                bx1 + DORM.wall_t,
                SDORM_STAIR_Y2,
                FLOOR_Z1,
                bx2 - DORM.wall_t,
                by2 - DORM.wall_t,
                FLOOR_Z2,
                Textures.GROUND,
                tt=Textures.ROAD,
            ),
            box(
                SDORM_STAIR_X2,
                SDORM_STAIR_Y1,
                FLOOR_Z1,
                bx2 - DORM.wall_t,
                SDORM_STAIR_Y2,
                FLOOR_Z2,
                Textures.GROUND,
                tt=Textures.ROAD,
            ),
        ]

        for i in range(SDORM_STAIR_N):
            floor_brushes.append(
                box(
                    SDORM_STAIR_X1 + i * SDORM_STAIR_RUN,
                    SDORM_STAIR_Y1,
                    FLOOR_Z2 - SDORM_LIFT,
                    SDORM_STAIR_X1 + (i + 1) * SDORM_STAIR_RUN,
                    SDORM_STAIR_Y2,
                    (i + 1) * SDORM_STAIR_RISE - SDORM_LIFT,
                    Textures.GROUND,
                )
            )
    else:
        floor_brushes.append(
            box(
                bx1 + DORM.wall_t,
                by1 + DORM.wall_t,
                FLOOR_Z1,
                bx2 - DORM.wall_t,
                by2 - DORM.wall_t,
                FLOOR_Z2,
                Textures.GROUND,
                tt=Textures.ROAD,
            )
        )
    return floor_brushes


def _south_dorm_mid_front_window_openings(dorm_ctx, south_ctx):
    """Return the centered front/back window openings."""

    cx = south_ctx["cx"]
    dorm_window_levels = dorm_ctx["dorm_window_levels"]
    return [
        (
            cx - DORM_WIN_HW,
            zb,
            cx + DORM_WIN_HW,
            zt,
        )
        for _, zb, zt in dorm_window_levels(1)
    ]


def _build_south_dorm_wall_brushes(south_ctx, mid_wxz, cy):
    """Return the four wall runs with their openings."""

    by1 = south_ctx["by1"]
    by2 = south_ctx["by2"]
    bx1 = south_ctx["bx1"]
    bx2 = south_ctx["bx2"]
    door_hi = south_ctx["door_hi"]
    door_lo = south_ctx["door_lo"]
    dorm_door_open = south_ctx["dorm_door_open"]
    ent_h = south_ctx["ent_h"]
    ent_hw = south_ctx["ent_hw"]
    entrance = south_ctx["entrance"]
    west_door = south_ctx["west_door"]
    wxz = south_ctx["wxz"]
    wxz_north = south_ctx["wxz_north"]
    wyz = south_ctx["wyz"]
    wyz_west = south_ctx["wyz_west"]

    wall_brushes = []
    wall_brushes.extend(
        layered_wall(
            bx1,
            by1,
            FLOOR_Z2,
            bx2,
            by1 + DORM.wall_t,
            FLOOR_Z2 + DORM_H,
            ([] if door_lo else wxz() + mid_wxz)
            + ([dorm_door_open] if door_lo else []),
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall(
            bx1,
            by2 - DORM.wall_t,
            FLOOR_Z2,
            bx2,
            by2,
            FLOOR_Z2 + DORM_H,
            ([] if door_hi else wxz_north() + mid_wxz)
            + ([dorm_door_open] if door_hi else []),
            Textures.BUILDING,
        )
    )
    wall_brushes.extend(
        layered_wall_y(
            by1 + DORM.wall_t,
            bx1,
            FLOOR_Z2,
            by2 - DORM.wall_t,
            bx1 + DORM.wall_t,
            FLOOR_Z2 + DORM_H,
            wyz_west()
            + (
                [
                    (
                        cy - DORM_INNER_DOOR_HW,
                        FLOOR_Z2 - SDORM_LIFT,
                        cy + DORM_INNER_DOOR_HW,
                        FLOOR_Z2,
                    )
                ]
                if west_door
                else []
            ),
            Textures.BUILDING,
        )
    )
    east_openings = wyz()
    if entrance:
        east_openings = [
            o for o in east_openings if o[2] <= cy - ent_hw or o[0] >= cy + ent_hw
        ] + [(cy - ent_hw, FLOOR_Z2, cy + ent_hw, FLOOR_Z2 + ent_h)]
    wall_brushes.extend(
        layered_wall_y(
            by1 + DORM.wall_t,
            bx2 - DORM.wall_t,
            FLOOR_Z2,
            by2 - DORM.wall_t,
            bx2,
            FLOOR_Z2 + DORM_H,
            east_openings,
            Textures.BUILDING,
        )
    )
    return wall_brushes


def _south_dorm_chimney_bounds(south_ctx, cy):
    """Return the chimney footprint, or Nones when omitted."""

    chimney = south_ctx["chimney"]
    cx = south_ctx["cx"]
    chim_x1 = chim_x2 = chim_y1 = chim_y2 = None
    if chimney:
        chw = 32
        ccy = cy + 64
        chim_x1, chim_x2 = (
            cx + 80,
            cx + 80 + chw * 2,
        )
        chim_y1, chim_y2 = ccy - chw, ccy + chw
    return chim_x1, chim_x2, chim_y1, chim_y2


def _build_south_dorm_top_cap_brushes(south_ctx, chim_x1, chim_x2, chim_y1, chim_y2):
    """Return the south dorm top slab brushes beneath the roof."""

    by1 = south_ctx["by1"]
    by2 = south_ctx["by2"]
    bx1 = south_ctx["bx1"]
    bx2 = south_ctx["bx2"]
    chimney = south_ctx["chimney"]

    if chimney:
        _cz1, _cz2 = FLOOR_Z2 + DORM_H, FLOOR_Z2 + DORM_H + DORM.wall_t
        return [
            box(bx1, by1, _cz1, chim_x1, by2, _cz2, Textures.BUILDING),
            box(chim_x2, by1, _cz1, bx2, by2, _cz2, Textures.BUILDING),
            box(chim_x1, by1, _cz1, chim_x2, chim_y1, _cz2, Textures.BUILDING),
            box(chim_x1, chim_y2, _cz1, chim_x2, by2, _cz2, Textures.BUILDING),
        ]
    return [
        box(
            bx1,
            by1,
            FLOOR_Z2 + DORM_H,
            bx2,
            by2,
            FLOOR_Z2 + DORM_H + DORM.wall_t,
            Textures.BUILDING,
        )
    ]


def _south_dorm_roof_bounds(south_ctx):
    """Return shared roof elevations and gable depth for a south dorm."""

    by1 = south_ctx["by1"]
    by2 = south_ctx["by2"]
    slat_hi = south_ctx["slat_hi"]
    slat_lo = south_ctx["slat_lo"]
    eave_z = FLOOR_Z2 + DORM_H + DORM.wall_t
    ridge_z = FLOOR_Z2 + DORM_H + DORM.wall_t + DORM_ROOF_H
    slab_t = DORM_SLAB_T
    depth = 6
    sy1 = by1 + depth if slat_lo else by1
    sy2 = by2 - depth if slat_hi else by2
    return eave_z, ridge_z, slab_t, depth, sy1, sy2


def _build_south_dorm_roof_brushes(
    south_ctx,
    chim_x1,
    chim_x2,
    chim_y1,
    chim_y2,
    eave_z,
    ridge_z,
    slab_t,
    sy1,
    sy2,
):
    """Return the main south dorm roof slabs."""

    bx1 = south_ctx["bx1"]
    bx2 = south_ctx["bx2"]
    chimney = south_ctx["chimney"]
    cx = south_ctx["cx"]

    if chimney:

        def _etop(x):
            return int(ridge_z + (x - cx) * (eave_z + slab_t - ridge_z) // (bx2 - cx))

        return [
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
            ),
            ramp_slab(
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
            ramp_slab(
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
            ramp_slab(
                cx,
                chim_x1,
                chim_y1,
                chim_y2,
                eave_z,
                eave_z,
                ridge_z,
                _etop(chim_x1),
                Textures.ROOF,
                ts=Textures.GABLE,
            ),
            ramp_slab(
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
    return [
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
        ),
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
        ),
    ]


def _build_south_dorm_chimney_stack_brushes(
    south_ctx, chim_x1, chim_x2, chim_y1, chim_y2, eave_z, ridge_z
):
    """Return the chimney stack walls above the south dorm roof."""

    chimney = south_ctx["chimney"]
    if not chimney:
        return []

    chim_wall, chim_top = 12, ridge_z + 32
    return [
        box(
            chim_x1 - chim_wall,
            chim_y1 - chim_wall,
            eave_z,
            chim_x2 + chim_wall,
            chim_y1,
            chim_top,
            Textures.BUILDING,
        ),
        box(
            chim_x1 - chim_wall,
            chim_y2,
            eave_z,
            chim_x2 + chim_wall,
            chim_y2 + chim_wall,
            chim_top,
            Textures.BUILDING,
        ),
        box(
            chim_x1 - chim_wall,
            chim_y1,
            eave_z,
            chim_x1,
            chim_y2,
            chim_top,
            Textures.BUILDING,
        ),
        box(
            chim_x2,
            chim_y1,
            eave_z,
            chim_x2 + chim_wall,
            chim_y2,
            chim_top,
            Textures.BUILDING,
        ),
    ]


def _build_south_dorm_gable_slat_brushes(south_ctx, eave_z, ridge_z, slab_t, depth):
    """Return the optional south dorm gable slats."""

    by1 = south_ctx["by1"]
    by2 = south_ctx["by2"]
    bx1 = south_ctx["bx1"]
    bx2 = south_ctx["bx2"]
    cx = south_ctx["cx"]
    slat_hi = south_ctx["slat_hi"]
    slat_lo = south_ctx["slat_lo"]

    slat_brushes = []
    if slat_lo:
        slat_brushes += gable_slats(
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
        slat_brushes += gable_slats(
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
    return slat_brushes


def _build_south_dorm_top_and_roof_brushes(
    south_ctx, chim_x1, chim_x2, chim_y1, chim_y2
):
    """Return the top slab, roof, chimney stack, and gable slats."""

    eave_z, ridge_z, slab_t, depth, sy1, sy2 = _south_dorm_roof_bounds(south_ctx)

    top_brushes = []
    top_brushes.extend(
        _build_south_dorm_top_cap_brushes(
            south_ctx,
            chim_x1,
            chim_x2,
            chim_y1,
            chim_y2,
        )
    )
    top_brushes.extend(
        _build_south_dorm_roof_brushes(
            south_ctx,
            chim_x1,
            chim_x2,
            chim_y1,
            chim_y2,
            eave_z,
            ridge_z,
            slab_t,
            sy1,
            sy2,
        )
    )
    top_brushes.extend(
        _build_south_dorm_chimney_stack_brushes(
            south_ctx,
            chim_x1,
            chim_x2,
            chim_y1,
            chim_y2,
            eave_z,
            ridge_z,
        )
    )
    top_brushes.extend(
        _build_south_dorm_gable_slat_brushes(
            south_ctx,
            eave_z,
            ridge_z,
            slab_t,
            depth,
        )
    )
    return top_brushes


def _build_south_dorm_entrance_brushes(south_ctx, cy):
    """Return the east entrance arch, grille, and door frame."""

    bx2 = south_ctx["bx2"]
    ent_h = south_ctx["ent_h"]
    ent_hw = south_ctx["ent_hw"]
    entrance = south_ctx["entrance"]

    entrance_brushes = []
    if entrance:
        entrance_brushes += entrance_arch_ywall(
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

        grille_d, beam_h, mull_w, trans_h = 8, 6, 6, 26

        _pillar_d = 12
        gx1 = bx2 + _pillar_d // 2 - grille_d // 2
        gx2 = bx2 + _pillar_d // 2 + grille_d // 2
        trans_t = FLOOR_Z2 + ent_h
        trans_b = trans_t - trans_h
        entrance_brushes.append(
            box(
                gx1,
                cy - ent_hw,
                trans_b - beam_h,
                gx2,
                cy + ent_hw,
                trans_b,
                Textures.GABLE,
            )
        )
        entrance_brushes.append(
            box(
                gx1,
                cy - ent_hw,
                trans_t - beam_h,
                gx2,
                cy + ent_hw,
                trans_t,
                Textures.GABLE,
            )
        )
        for k in range(5):
            mx = cy - ent_hw + (2 * ent_hw) * k // 4
            entrance_brushes.append(
                box(
                    gx1,
                    mx - mull_w // 2,
                    trans_b,
                    gx2,
                    mx + mull_w // 2,
                    trans_t,
                    Textures.GABLE,
                )
            )

        entrance_brushes += win_frame_ywall(
            cy - ent_hw,
            cy + ent_hw,
            FLOOR_Z2,
            FLOOR_Z2 + ent_h,
            bx2,
            -1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
            crossbar=False,
            bottom=False,
        )
    return entrance_brushes


def _build_south_dorm_window_frame_brushes(south_ctx, mid_wxz, cy):
    """Return the non-door window trim for all faces."""

    by1 = south_ctx["by1"]
    by2 = south_ctx["by2"]
    bx1 = south_ctx["bx1"]
    bx2 = south_ctx["bx2"]
    door_hi = south_ctx["door_hi"]
    door_lo = south_ctx["door_lo"]
    ent_hw = south_ctx["ent_hw"]
    entrance = south_ctx["entrance"]
    wxz = south_ctx["wxz"]
    wxz_north = south_ctx["wxz_north"]
    wyz = south_ctx["wyz"]
    wyz_west = south_ctx["wyz_west"]

    frame_brushes = []
    if not door_lo:
        for xl, zb, xr, zt in wxz():
            frame_brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by1,
                +1,
                Textures.GABLE,
                fd=DORM.wall_t,
                margin=DORM_WIN_MARGIN,
            )
        for xl, zb, xr, zt in mid_wxz:
            frame_brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by1,
                +1,
                Textures.GABLE,
                fd=DORM.wall_t,
                margin=DORM_WIN_MARGIN,
            )

    if not door_hi:
        for xl, zb, xr, zt in wxz_north():
            frame_brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by2,
                -1,
                Textures.GABLE,
                fd=DORM.wall_t,
                margin=DORM_WIN_MARGIN,
            )
        for xl, zb, xr, zt in mid_wxz:
            frame_brushes += win_frame_xwall(
                xl,
                xr,
                zb,
                zt,
                by2,
                -1,
                Textures.GABLE,
                fd=DORM.wall_t,
                margin=DORM_WIN_MARGIN,
            )

    for yl, zb, yr, zt in wyz_west():
        frame_brushes += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            bx1,
            +1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )

    for yl, zb, yr, zt in wyz():
        if entrance and not (yr <= cy - ent_hw or yl >= cy + ent_hw):
            continue
        frame_brushes += win_frame_ywall(
            yl,
            yr,
            zb,
            zt,
            bx2,
            -1,
            Textures.GABLE,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
        )
    return frame_brushes


def _build_south_dorm_door_frame_brushes(south_ctx):
    """Return trim for the optional end doors."""

    by1 = south_ctx["by1"]
    by2 = south_ctx["by2"]
    cx = south_ctx["cx"]
    door_hi = south_ctx["door_hi"]
    door_lo = south_ctx["door_lo"]

    door_brushes = []
    if door_hi:
        door_brushes += win_frame_xwall(
            cx - DORM_INNER_DOOR_HW,
            cx + DORM_INNER_DOOR_HW,
            FLOOR_Z2,
            FLOOR_Z2 + DORM_INNER_DOOR_H,
            by2,
            -1,
            Textures.GABLE,
            fw=8,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
            crossbar=False,
            bottom=False,
        )
    if door_lo:
        door_brushes += win_frame_xwall(
            cx - DORM_INNER_DOOR_HW,
            cx + DORM_INNER_DOOR_HW,
            FLOOR_Z2,
            FLOOR_Z2 + DORM_INNER_DOOR_H,
            by1,
            +1,
            Textures.GABLE,
            fw=8,
            fd=DORM.wall_t,
            margin=DORM_WIN_MARGIN,
            crossbar=False,
            bottom=False,
        )
    return door_brushes


def _make_south_dorm(
    dorm_ctx,
    by1,
    by2,
    slat_lo=False,
    slat_hi=False,
    entrance=True,
    chimney=False,
    door_lo=False,
    door_hi=False,
    north_pier_x=None,
    north_pier_hw=0,
    north_min_floor=0,
    west_door=True,
    stairwell=False,
):
    """Build one south dorm shell between by1 and by2."""

    south_ctx = _make_south_dorm_context(
        dorm_ctx,
        by1,
        by2,
        slat_lo=slat_lo,
        slat_hi=slat_hi,
        entrance=entrance,
        chimney=chimney,
        door_lo=door_lo,
        door_hi=door_hi,
        north_pier_x=north_pier_x,
        north_pier_hw=north_pier_hw,
        north_min_floor=north_min_floor,
        west_door=west_door,
        stairwell=stairwell,
    )

    brushes = []
    brushes.extend(_build_south_dorm_floor_brushes(south_ctx))
    mid_wxz = _south_dorm_mid_front_window_openings(dorm_ctx, south_ctx)
    cy = (by1 + by2) // 2
    brushes.extend(_build_south_dorm_wall_brushes(south_ctx, mid_wxz, cy))
    chim_x1, chim_x2, chim_y1, chim_y2 = _south_dorm_chimney_bounds(south_ctx, cy)
    brushes.extend(
        _build_south_dorm_top_and_roof_brushes(
            south_ctx,
            chim_x1,
            chim_x2,
            chim_y1,
            chim_y2,
        )
    )
    brushes.extend(_build_south_dorm_entrance_brushes(south_ctx, cy))
    brushes.extend(_build_south_dorm_window_frame_brushes(south_ctx, mid_wxz, cy))
    brushes.extend(_build_south_dorm_door_frame_brushes(south_ctx))
    return brushes


def _build_south_dorm_entities(dorm_ctx):
    """Build the two south dorm func_detail entities."""

    return [
        brush_ent(
            "func_detail",
            [
                b.translated(0, 0, SDORM_LIFT)
                for b in _make_south_dorm(
                    dorm_ctx,
                    DORM_SOUTH1_Y1,
                    DORM_SOUTH1_Y2,
                    slat_lo=True,
                    chimney=True,
                    door_hi=True,
                    stairwell=True,
                )
            ],
        ),
        brush_ent(
            "func_detail",
            [
                b.translated(0, 0, SDORM_LIFT)
                for b in _make_south_dorm(
                    dorm_ctx,
                    DORM_SOUTH2_Y1,
                    DORM_SOUTH2_Y2,
                    slat_hi=True,
                    entrance=False,
                    door_lo=True,
                    north_pier_x=DORM_PIER_X,
                    north_pier_hw=12,
                    north_min_floor=1,
                    west_door=False,
                )
            ],
        ),
    ]


def _build_dorm_seam_brushes(dorm_ctx):
    """Build the tunnel seam floor brushes between the dorm blocks."""

    dorm_cx = dorm_ctx["dorm_cx"]
    return [
        box(
            dorm_cx - DORM_INNER_DOOR_HW,
            seam_y - DORM.wall_t,
            FLOOR_Z1 + seam_lift,
            dorm_cx + DORM_INNER_DOOR_HW,
            seam_y + DORM.wall_t,
            FLOOR_Z2 + seam_lift,
            Textures.GROUND,
            tt=Textures.ROAD,
        )
        for seam_y, seam_lift in ((DORM_NORTH_Y1, 0), (DORM_SOUTH1_Y2, SDORM_LIFT))
    ]


def _build_dorms():
    """Build the west-campus dorm shells and their detail entities."""

    brushes = []
    entities = []
    dorm_ctx = _make_dorm_context()

    north_floor_brush, north_entity = _build_north_dorm(dorm_ctx)
    entities.append(north_entity)
    brushes.append(north_floor_brush)

    north2_floor_brush, north2_entity = _build_second_north_dorm(dorm_ctx)
    entities.append(north2_entity)
    brushes.append(north2_floor_brush)

    entities.extend(_build_south_dorm_entities(dorm_ctx))
    brushes.extend(_build_dorm_seam_brushes(dorm_ctx))

    return brushes, entities


def build():
    """Build west-campus buildings and terrain.

    Returns:
        tuple[list, list]: ``(brushes, entities)`` for the west-campus area,
        gated by the relevant ``WEST_CAMPUS_ENABLED_*`` config flags.
    """
    BRUSHES = []
    ENTITIES = []

    if (
        WEST_CAMPUS_ENABLED_FENCE
        or WEST_CAMPUS_ENABLED_WALL
        or WEST_CAMPUS_ENABLED_SIDEWALK
    ) and not WEST_CAMPUS_ENABLED_TERRAIN:
        raise ValueError(
            "west_campus.build(): WEST_CAMPUS_ENABLED_FENCE/WALL/SIDEWALK "
            "follow the real hillside terrain and require "
            "WEST_CAMPUS_ENABLED_TERRAIN to also be on — enable it (or "
            "disable the fence/wall/sidewalk) via `ql conf set`."
        )

    if WEST_CAMPUS_ENABLED_FENCE:
        _build_iron_fence(ENTITIES)

    if WEST_CAMPUS_ENABLED_WALL:
        _build_brick_wall(BRUSHES, ENTITIES)

    if WEST_CAMPUS_ENABLED_SIDEWALK:
        _build_sidewalk(BRUSHES)

    if not WEST_CAMPUS_ENABLED_DORMS:
        return BRUSHES, ENTITIES

    dorm_brushes, dorm_entities = _build_dorms()
    BRUSHES.extend(dorm_brushes)
    ENTITIES.extend(dorm_entities)
    return BRUSHES, ENTITIES
