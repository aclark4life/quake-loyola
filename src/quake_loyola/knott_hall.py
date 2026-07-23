"""Build the Knott Hall shell, interior, and facade details."""

from .constants import (
    FLOOR_Z1,
    INDENT,
    KNOTT,
    KNOTT_ENABLED,
    KNOTT_ENABLED_EXTERIOR,
    KNOTT_ENABLED_INTERIOR,
    KNOTT_ENT_HALF_W,
    KNOTT_FRONT_WINDOW_HALF_W,
    KNOTT_FRONT_WINDOW_MULLION_HALF_GAP,
    KNOTT_GROUND_Z,
    KNOTT_MULLION_PROUD,
    KNOTT_MULLION_W,
    KNOTT_ORIG_CX,
    KNOTT_ROOM_SPLITS,
    KNOTT_SHAFT_WALL,
    KNOTT_SHAFT_X1,
    KNOTT_SHAFT_X2,
    KNOTT_SHAFT_Y1,
    KNOTT_SHAFT_Y2,
    KNOTT_SIDE_WINDOW_DIV_W,
    KNOTT_SIDE_WINDOW_HW,
    KNOTT_SIDE_WINDOW_INNER_LEFT,
    KNOTT_SIDE_WINDOW_INNER_RIGHT,
    KNOTT_SIDE_WINDOW_PROTRUSION,
    KNOTT_SIGN_H,
    KNOTT_SIGN_PADDING,
    KNOTT_SIGN_PX_H,
    KNOTT_SIGN_PX_W,
    KNOTT_SIGN_TEXT,
    KNOTT_SIGN_Z_OFFSET,
    KNOTT_STAIRS_HN,
    KNOTT_STAIRS_MID_Y,
    KNOTT_STAIRS_POST_W,
    KNOTT_STAIRS_RAIL_H,
    KNOTT_STAIRS_RAIL_T,
    KNOTT_STAIRS_STEP_R,
    KNOTT_STAIRS_TREAD_X,
    KNOTT_STAIRS_X1,
    KNOTT_STAIRS_X2,
    KNOTT_STAIRS_Y1,
    KNOTT_STAIRS_Y2,
    KNOTT_Z2,
    WALK_ZT2,
    WIN_HALF,
    Textures,
)
from .geometry import (
    box,
    brush_ent,
    layered_wall,
    layered_wall_y,
    ramp_slab,
    render_text_flat,
)


def build():
    """Build Knott Hall brushes and detail entities."""
    if not KNOTT_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # Interior-only detail brushes.
    DETAIL_BRUSHES = []

    # Exterior detail brushes gated separately from the interior.
    EXTERIOR_DETAIL_BRUSHES = []
    knott_brush_start = len(BRUSHES)

    # Fill the footprint up to the ground-floor slab.
    BRUSHES.append(
        box(
            KNOTT.x1,
            KNOTT.y1,
            FLOOR_Z1,
            KNOTT.x2,
            KNOTT.y2,
            KNOTT_GROUND_Z,
            Textures.GROUND,
        )
    )

    def floor_levels():
        for floor_index in range(KNOTT.floors):
            fz1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
            fz2 = fz1 + KNOTT.floor_h
            fz_surf = fz1 + KNOTT.wall_t
            fz_mid = fz1 + KNOTT.floor_h // 2
            yield floor_index, fz1, fz2, fz_surf, fz_mid

    bix1 = KNOTT.x1 + KNOTT.wall_t
    bix2 = KNOTT.x2 - KNOTT.wall_t
    KNOTT_BIY1 = KNOTT.y1 + KNOTT.wall_t
    KNOTT_BIY2 = KNOTT.y2 - KNOTT.wall_t

    # Keep the entrance centered on the original facade alignment.
    KNOTT_ENT_X1, KNOTT_ENT_X2 = (
        KNOTT_ORIG_CX - KNOTT_ENT_HALF_W,
        KNOTT_ORIG_CX + KNOTT_ENT_HALF_W,
    )

    s_wall_openings = [
        (
            KNOTT_ENT_X1,
            KNOTT_GROUND_Z + fl * KNOTT.floor_h + KNOTT.wall_t,
            KNOTT_ENT_X2,
            KNOTT_GROUND_Z + (fl + 1) * KNOTT.floor_h,
        )
        for fl in range(KNOTT.floors)
    ]
    BRUSHES.append(
        box(
            KNOTT.x1 + INDENT,
            KNOTT.y1,
            FLOOR_Z1,
            KNOTT.x2 - INDENT,
            KNOTT.y1 + KNOTT.wall_t,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            ts=Textures.BRICK_KH,
            tn=Textures.FLOOR_KH,
        )
    )
    BRUSHES.extend(
        layered_wall(
            KNOTT.x1 + INDENT,
            KNOTT.y1,
            KNOTT_GROUND_Z,
            KNOTT.x2 - INDENT,
            KNOTT.y1 + KNOTT.wall_t,
            KNOTT_Z2,
            s_wall_openings,
            Textures.BRICK_KH,
            ts=Textures.BRICK_KH,
            tn=Textures.FLOOR_KH,
            tf=Textures.CEMENT,
        )
    )

    sw_win_cx = KNOTT.x1 + INDENT // 2
    BRUSHES.append(
        box(
            KNOTT.x1,
            KNOTT.y1 + INDENT - KNOTT.wall_t,
            FLOOR_Z1,
            KNOTT.x1 + INDENT,
            KNOTT.y1 + INDENT,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            tn=Textures.FLOOR_KH,
        )
    )
    BRUSHES.extend(
        layered_wall(
            KNOTT.x1,
            KNOTT.y1 + INDENT - KNOTT.wall_t,
            KNOTT_GROUND_Z,
            KNOTT.x1 + INDENT,
            KNOTT.y1 + INDENT,
            KNOTT_Z2,
            [
                (
                    sw_win_cx - WIN_HALF,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    sw_win_cx + WIN_HALF,
                    KNOTT_Z2,
                )
            ],
            Textures.BRICK_KH,
            ts=Textures.BRICK_KH,
            tn=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1 + INDENT - KNOTT.wall_t,
            KNOTT.y1,
            FLOOR_Z1,
            KNOTT.x1 + INDENT,
            KNOTT.y1 + INDENT,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            te=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1 + INDENT - KNOTT.wall_t,
            KNOTT.y1,
            KNOTT_GROUND_Z,
            KNOTT.x1 + INDENT,
            KNOTT.y1 + INDENT,
            KNOTT_Z2,
            Textures.BRICK_KH,
            tw=Textures.BRICK_KH,
            te=Textures.FLOOR_KH,
        )
    )

    se_win_cx = KNOTT.x2 - INDENT // 2
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y1 + INDENT - KNOTT.wall_t,
            FLOOR_Z1,
            KNOTT.x2,
            KNOTT.y1 + INDENT,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            tn=Textures.FLOOR_KH,
        )
    )
    BRUSHES.extend(
        layered_wall(
            KNOTT.x2 - INDENT,
            KNOTT.y1 + INDENT - KNOTT.wall_t,
            KNOTT_GROUND_Z,
            KNOTT.x2,
            KNOTT.y1 + INDENT,
            KNOTT_Z2,
            [
                (
                    se_win_cx - WIN_HALF,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    se_win_cx + WIN_HALF,
                    KNOTT_Z2,
                )
            ],
            Textures.BRICK_KH,
            ts=Textures.BRICK_KH,
            tn=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y1,
            FLOOR_Z1,
            KNOTT.x2 - INDENT + KNOTT.wall_t,
            KNOTT.y1 + INDENT,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            tw=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y1,
            KNOTT_GROUND_Z,
            KNOTT.x2 - INDENT + KNOTT.wall_t,
            KNOTT.y1 + INDENT,
            KNOTT_Z2,
            Textures.BRICK_KH,
            tw=Textures.FLOOR_KH,
            te=Textures.BRICK_KH,
        )
    )

    for mx in [sw_win_cx - WIN_HALF - KNOTT_MULLION_W, sw_win_cx + WIN_HALF]:
        EXTERIOR_DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y1 + INDENT - KNOTT.wall_t,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y1 + INDENT + KNOTT_MULLION_PROUD,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )
    for mx in [se_win_cx - WIN_HALF - KNOTT_MULLION_W, se_win_cx + WIN_HALF]:
        EXTERIOR_DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y1 + INDENT - KNOTT.wall_t,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y1 + INDENT + KNOTT_MULLION_PROUD,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )

    for wx in [sw_win_cx, se_win_cx]:
        for floor_index, _, _, _, mz in floor_levels():
            if floor_index == 0:
                continue
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    wx - WIN_HALF,
                    KNOTT.y1 + INDENT - KNOTT.wall_t,
                    mz,
                    wx + WIN_HALF,
                    KNOTT.y1 + INDENT + KNOTT_MULLION_PROUD,
                    mz + 4,
                    Textures.RAIL,
                )
            )

    for wx in [sw_win_cx, se_win_cx]:
        for _, _, fz, _, _ in floor_levels():
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    wx - WIN_HALF,
                    KNOTT.y1 + INDENT - KNOTT.wall_t,
                    fz - 4,
                    wx + WIN_HALF,
                    KNOTT.y1 + INDENT + KNOTT_MULLION_PROUD,
                    fz,
                    Textures.RAIL,
                )
            )

    door_ground = [
        (KNOTT_ENT_X1, KNOTT_GROUND_Z, KNOTT_ENT_X2, KNOTT_GROUND_Z + KNOTT.floor_h)
    ]
    door_upper = [
        (KNOTT_ENT_X1, WALK_ZT2, KNOTT_ENT_X2, KNOTT_GROUND_Z + KNOTT.floor_h * 2)
    ]
    win_n = [
        (
            KNOTT_ORIG_CX - KNOTT_FRONT_WINDOW_HALF_W,
            KNOTT_GROUND_Z + KNOTT.floor_h * 2,
            KNOTT_ORIG_CX - KNOTT_FRONT_WINDOW_MULLION_HALF_GAP,
            KNOTT_Z2,
        ),
        (
            KNOTT_ORIG_CX + KNOTT_FRONT_WINDOW_MULLION_HALF_GAP,
            KNOTT_GROUND_Z + KNOTT.floor_h * 2,
            KNOTT_ORIG_CX + KNOTT_FRONT_WINDOW_HALF_W,
            KNOTT_Z2,
        ),
    ]
    BRUSHES.append(
        box(
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - KNOTT.wall_t,
            FLOOR_Z1,
            KNOTT.x2 - INDENT,
            KNOTT.y2,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
            tn=Textures.BRICK_KH,
        )
    )
    BRUSHES.extend(
        layered_wall(
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - KNOTT.wall_t,
            KNOTT_GROUND_Z,
            KNOTT.x2 - INDENT,
            KNOTT.y2,
            KNOTT_Z2,
            door_ground + door_upper + win_n,
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
            tn=Textures.BRICK_KH,
            tf=Textures.CEMENT,
        )
    )

    nw_win_cx1 = KNOTT.x1 + INDENT // 2
    nw_win_cx2 = KNOTT.x1 + INDENT + INDENT // 2
    BRUSHES.append(
        box(
            KNOTT.x1,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - INDENT + KNOTT.wall_t,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1,
            KNOTT.y2 - INDENT,
            KNOTT_GROUND_Z,
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - INDENT + KNOTT.wall_t,
            KNOTT_GROUND_Z + KNOTT.floor_h,
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
            tn=Textures.BRICK_KH,
        )
    )

    BRUSHES.extend(
        layered_wall(
            KNOTT.x1,
            KNOTT.y2 - INDENT,
            KNOTT_GROUND_Z + KNOTT.floor_h,
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - INDENT + KNOTT.wall_t,
            KNOTT_Z2,
            [
                (
                    nw_win_cx1 - WIN_HALF,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    nw_win_cx1 + WIN_HALF,
                    KNOTT_Z2,
                ),
                (
                    nw_win_cx2 - WIN_HALF,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    nw_win_cx2 + WIN_HALF,
                    KNOTT_Z2,
                ),
            ],
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
            tn=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1 + 2 * INDENT - KNOTT.wall_t,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            te=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1 + 2 * INDENT - KNOTT.wall_t,
            KNOTT.y2 - INDENT,
            KNOTT_GROUND_Z,
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2,
            KNOTT_Z2,
            Textures.BRICK_KH,
            tw=Textures.BRICK_KH,
            te=Textures.FLOOR_KH,
        )
    )

    ne_win_cx = KNOTT.x2 - INDENT // 2
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
            KNOTT.x2,
            KNOTT.y2 - INDENT + KNOTT.wall_t,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
        )
    )

    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y2 - INDENT,
            KNOTT_GROUND_Z,
            KNOTT.x2,
            KNOTT.y2 - INDENT + KNOTT.wall_t,
            KNOTT_GROUND_Z + KNOTT.floor_h,
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
            tn=Textures.BRICK_KH,
        )
    )

    BRUSHES.extend(
        layered_wall(
            KNOTT.x2 - INDENT,
            KNOTT.y2 - INDENT,
            KNOTT_GROUND_Z + KNOTT.floor_h,
            KNOTT.x2,
            KNOTT.y2 - INDENT + KNOTT.wall_t,
            KNOTT_Z2,
            [
                (
                    ne_win_cx - WIN_HALF,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    ne_win_cx + WIN_HALF,
                    KNOTT_Z2,
                )
            ],
            Textures.BRICK_KH,
            ts=Textures.FLOOR_KH,
            tn=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
            KNOTT.x2 - INDENT + KNOTT.wall_t,
            KNOTT.y2,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            tw=Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y2 - INDENT,
            KNOTT_GROUND_Z,
            KNOTT.x2 - INDENT + KNOTT.wall_t,
            KNOTT.y2,
            KNOTT_Z2,
            Textures.BRICK_KH,
            tw=Textures.FLOOR_KH,
            te=Textures.BRICK_KH,
        )
    )

    for mx in [
        nw_win_cx1 - WIN_HALF - KNOTT_MULLION_W,
        nw_win_cx1 + WIN_HALF,
        nw_win_cx2 - WIN_HALF - KNOTT_MULLION_W,
        nw_win_cx2 + WIN_HALF,
    ]:
        EXTERIOR_DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y2 - INDENT - KNOTT_MULLION_PROUD,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y2 - INDENT + KNOTT.wall_t,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )

    for mx in [ne_win_cx - WIN_HALF - KNOTT_MULLION_W, ne_win_cx + WIN_HALF]:
        EXTERIOR_DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y2 - INDENT - KNOTT_MULLION_PROUD,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y2 - INDENT + KNOTT.wall_t,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )

    win_n_x1, win_n_x2 = (
        KNOTT_ORIG_CX - KNOTT_FRONT_WINDOW_HALF_W,
        KNOTT_ORIG_CX + KNOTT_FRONT_WINDOW_HALF_W,
    )
    win_n_mid = KNOTT_ORIG_CX - KNOTT_FRONT_WINDOW_MULLION_HALF_GAP
    for mx in [win_n_x1 - KNOTT_MULLION_W, win_n_mid, win_n_x2]:
        EXTERIOR_DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y2 - KNOTT.wall_t,
                KNOTT_GROUND_Z + KNOTT.floor_h * 2,
                mx + KNOTT_MULLION_W,
                KNOTT.y2 + KNOTT_MULLION_PROUD,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )

    knott_sign_char_w = (4 + 1) * KNOTT_SIGN_PX_W
    knott_sign_total_w = len(KNOTT_SIGN_TEXT) * knott_sign_char_w - KNOTT_SIGN_PX_W
    knott_sign_half_w = knott_sign_total_w // 2 + KNOTT_SIGN_PADDING
    knott_sign_cx = (KNOTT_ORIG_CX + ne_win_cx) // 2
    knott_sign_z1 = KNOTT_GROUND_Z + KNOTT.floor_h * 2 + KNOTT_SIGN_Z_OFFSET
    knott_sign_z2 = knott_sign_z1 + KNOTT_SIGN_H
    BRUSHES.append(
        box(
            knott_sign_cx - knott_sign_half_w,
            KNOTT.y2,
            knott_sign_z1,
            knott_sign_cx + knott_sign_half_w,
            KNOTT.y2 + 6,
            knott_sign_z2,
            Textures.CEMENT,
        )
    )

    ww_half = KNOTT_SIDE_WINDOW_HW
    ww_wall_y1, ww_wall_y2 = KNOTT.y1, KNOTT.y2 - INDENT
    ww_quarter = (ww_wall_y2 - ww_wall_y1) // 4
    ww_c1 = ww_wall_y1 + ww_quarter
    ww_c2 = ww_wall_y1 + 2 * ww_quarter
    ww_c3 = ww_wall_y1 + 3 * ww_quarter
    ww_div_w = KNOTT_SIDE_WINDOW_DIV_W
    ww_protrude = KNOTT_SIDE_WINDOW_PROTRUSION
    BRUSHES.append(
        box(
            KNOTT.x2 - KNOTT.wall_t,
            ww_wall_y1,
            FLOOR_Z1,
            KNOTT.x2,
            ww_wall_y2,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            tw=Textures.FLOOR_KH,
        )
    )
    BRUSHES.extend(
        layered_wall_y(
            ww_wall_y1,
            KNOTT.x2 - KNOTT.wall_t,
            KNOTT_GROUND_Z,
            ww_wall_y2,
            KNOTT.x2,
            KNOTT_Z2,
            [
                (
                    ww_c1 - ww_half,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    ww_c1 + ww_half,
                    KNOTT_Z2,
                ),
                (
                    ww_c2 - ww_half,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    ww_c2 + ww_half,
                    KNOTT_Z2,
                ),
                (
                    ww_c3 - ww_half,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    ww_c3 + ww_half,
                    KNOTT_Z2,
                ),
            ],
            Textures.BRICK_KH,
            tw=Textures.FLOOR_KH,
            te=Textures.BRICK_KH,
        )
    )

    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for mullion_y in [
            window_center_y - ww_half,
            window_center_y - KNOTT_SIDE_WINDOW_INNER_LEFT,
            window_center_y + KNOTT_SIDE_WINDOW_INNER_RIGHT,
            window_center_y + ww_half - ww_div_w,
        ]:
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    KNOTT.x2 - KNOTT.wall_t,
                    mullion_y,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    KNOTT.x2 + ww_protrude,
                    mullion_y + ww_div_w,
                    KNOTT_Z2,
                    Textures.CEMENT,
                )
            )

    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for floor_index, _, _, _, mz in floor_levels():
            if floor_index == 0:
                continue
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    KNOTT.x2 - KNOTT.wall_t,
                    window_center_y - ww_half,
                    mz,
                    KNOTT.x2 + ww_protrude,
                    window_center_y + ww_half,
                    mz + 4,
                    Textures.RAIL,
                )
            )

    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for _, _, fz, _, _ in floor_levels():
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    KNOTT.x2 - KNOTT.wall_t,
                    window_center_y - ww_half,
                    fz - 4,
                    KNOTT.x2 + ww_protrude,
                    window_center_y + ww_half,
                    fz,
                    Textures.RAIL,
                )
            )

    BRUSHES.append(
        box(
            KNOTT.x1,
            ww_wall_y1,
            FLOOR_Z1,
            KNOTT.x1 + KNOTT.wall_t,
            ww_wall_y2,
            KNOTT_GROUND_Z,
            Textures.BRICK_KH,
            te=Textures.FLOOR_KH,
        )
    )
    BRUSHES.extend(
        layered_wall_y(
            ww_wall_y1,
            KNOTT.x1,
            KNOTT_GROUND_Z,
            ww_wall_y2,
            KNOTT.x1 + KNOTT.wall_t,
            KNOTT_Z2,
            [
                (
                    ww_c1 - ww_half,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    ww_c1 + ww_half,
                    KNOTT_Z2,
                ),
                (
                    ww_c2 - ww_half,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    ww_c2 + ww_half,
                    KNOTT_Z2,
                ),
                (
                    ww_c3 - ww_half,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    ww_c3 + ww_half,
                    KNOTT_Z2,
                ),
            ],
            Textures.BRICK_KH,
            tw=Textures.BRICK_KH,
            te=Textures.FLOOR_KH,
        )
    )

    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for mullion_y in [
            window_center_y - ww_half,
            window_center_y - KNOTT_SIDE_WINDOW_INNER_LEFT,
            window_center_y + KNOTT_SIDE_WINDOW_INNER_RIGHT,
            window_center_y + ww_half - ww_div_w,
        ]:
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    KNOTT.x1 - ww_protrude,
                    mullion_y,
                    KNOTT_GROUND_Z + KNOTT.floor_h,
                    KNOTT.x1 + KNOTT.wall_t,
                    mullion_y + ww_div_w,
                    KNOTT_Z2,
                    Textures.CEMENT,
                )
            )

    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for floor_index, _, _, _, mz in floor_levels():
            if floor_index == 0:
                continue
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    KNOTT.x1 - ww_protrude,
                    window_center_y - ww_half,
                    mz,
                    KNOTT.x1 + KNOTT.wall_t,
                    window_center_y + ww_half,
                    mz + 4,
                    Textures.RAIL,
                )
            )

    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for _, _, fz, _, _ in floor_levels():
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    KNOTT.x1 - ww_protrude,
                    window_center_y - ww_half,
                    fz - 4,
                    KNOTT.x1 + KNOTT.wall_t,
                    window_center_y + ww_half,
                    fz,
                    Textures.RAIL,
                )
            )

    for floor_index, _, _, _, mz in floor_levels():
        if floor_index < 2:
            continue
        EXTERIOR_DETAIL_BRUSHES.append(
            box(
                win_n_x1,
                KNOTT.y2 - KNOTT.wall_t,
                mz,
                win_n_x2,
                KNOTT.y2 + KNOTT_MULLION_PROUD,
                mz + 4,
                Textures.RAIL,
            )
        )

    for floor_index, _, fz, _, _ in floor_levels():
        if floor_index < 1:
            continue
        if fz <= KNOTT_Z2:
            hx1 = win_n_x1 - (KNOTT_MULLION_W if floor_index == 1 else 0)
            hx2 = win_n_x2 + (KNOTT_MULLION_W if floor_index == 1 else 0)
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    hx1,
                    KNOTT.y2 - KNOTT.wall_t,
                    fz - 4,
                    hx2,
                    KNOTT.y2 + KNOTT_MULLION_PROUD,
                    fz,
                    Textures.RAIL,
                )
            )
    for window_center_x, window_half_width in [
        (nw_win_cx1, WIN_HALF),
        (nw_win_cx2, WIN_HALF),
        (ne_win_cx, WIN_HALF),
    ]:
        for floor_index, _, _, _, mz in floor_levels():
            if floor_index == 0:
                continue
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    window_center_x - window_half_width,
                    KNOTT.y2 - INDENT - KNOTT_MULLION_PROUD,
                    mz,
                    window_center_x + window_half_width,
                    KNOTT.y2 - INDENT + KNOTT.wall_t,
                    mz + 4,
                    Textures.RAIL,
                )
            )

    for window_center_x, window_half_width in [
        (nw_win_cx1, WIN_HALF),
        (nw_win_cx2, WIN_HALF),
        (ne_win_cx, WIN_HALF),
    ]:
        for _, _, fz, _, _ in floor_levels():
            EXTERIOR_DETAIL_BRUSHES.append(
                box(
                    window_center_x - window_half_width,
                    KNOTT.y2 - INDENT - KNOTT_MULLION_PROUD,
                    fz - 4,
                    window_center_x + window_half_width,
                    KNOTT.y2 - INDENT + KNOTT.wall_t,
                    fz,
                    Textures.RAIL,
                )
            )

    BRUSHES.append(
        box(
            KNOTT.x1,
            KNOTT.y1,
            KNOTT_Z2,
            KNOTT_STAIRS_X1,
            KNOTT.y2 - INDENT,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - INDENT,
            KNOTT_Z2,
            KNOTT_STAIRS_X1,
            KNOTT.y2,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_STAIRS_X1,
            KNOTT.y1,
            KNOTT_Z2,
            KNOTT_STAIRS_X2,
            KNOTT_STAIRS_Y1,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_STAIRS_X1,
            KNOTT_STAIRS_Y2,
            KNOTT_Z2,
            KNOTT_STAIRS_X2,
            KNOTT.y2,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_STAIRS_X2,
            KNOTT.y1,
            KNOTT_Z2,
            KNOTT_SHAFT_X1,
            KNOTT.y2,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_SHAFT_X2,
            KNOTT.y1,
            KNOTT_Z2,
            KNOTT.x2,
            KNOTT.y2 - INDENT,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_SHAFT_X2,
            KNOTT.y2 - INDENT,
            KNOTT_Z2,
            KNOTT.x2 - INDENT,
            KNOTT.y2,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_SHAFT_X1,
            KNOTT.y1,
            KNOTT_Z2,
            KNOTT_SHAFT_X2,
            KNOTT_SHAFT_Y1,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_SHAFT_X1,
            KNOTT_SHAFT_Y2,
            KNOTT_Z2,
            KNOTT_SHAFT_X2,
            KNOTT.y2,
            KNOTT_Z2 + KNOTT.wall_t,
            Textures.FLOOR_KH,
        )
    )

    sz0 = KNOTT_GROUND_Z
    st0 = sz0 + KNOTT.wall_t
    DETAIL_BRUSHES.append(
        box(
            KNOTT.x1, KNOTT.y1, sz0, KNOTT.x2, KNOTT.y2 - INDENT, st0, Textures.FLOOR_KH
        )
    )
    DETAIL_BRUSHES.append(
        box(
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - INDENT,
            sz0,
            KNOTT.x2 - INDENT,
            KNOTT.y2,
            st0,
            Textures.FLOOR_KH,
        )
    )

    for floor_index in range(1, KNOTT.floors):
        floor_z1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
        floor_z2 = floor_z1 + KNOTT.wall_t

        DETAIL_BRUSHES.append(
            box(
                bix1,
                KNOTT_BIY1,
                floor_z1,
                bix2,
                KNOTT_STAIRS_Y1,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                bix1,
                KNOTT_STAIRS_Y1,
                floor_z1,
                KNOTT_STAIRS_X1,
                KNOTT_SHAFT_Y1,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )
        DETAIL_BRUSHES.append(
            box(
                KNOTT_STAIRS_X2,
                KNOTT_STAIRS_Y1,
                floor_z1,
                bix2,
                KNOTT_SHAFT_Y1,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                bix1,
                KNOTT_SHAFT_Y1,
                floor_z1,
                KNOTT_STAIRS_X1,
                KNOTT.y2 - INDENT,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                KNOTT_STAIRS_X2,
                KNOTT_SHAFT_Y1,
                floor_z1,
                KNOTT_SHAFT_X1,
                KNOTT_BIY2,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                KNOTT_SHAFT_X2,
                KNOTT_SHAFT_Y1,
                floor_z1,
                bix2,
                KNOTT.y2 - INDENT,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )
        DETAIL_BRUSHES.append(
            box(
                KNOTT_SHAFT_X2,
                KNOTT.y2 - INDENT,
                floor_z1,
                bix2 - INDENT,
                KNOTT_BIY2,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )

    shaft_wall = KNOTT_SHAFT_WALL

    shaft_door_h = KNOTT.floor_h
    shaft_door_openings = [
        (
            KNOTT_SHAFT_Y1 + 16,
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h,
            KNOTT_SHAFT_Y2 - 16,
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + shaft_door_h,
        )
        for floor_index in range(KNOTT.floors)
    ]

    DETAIL_BRUSHES.append(
        box(
            KNOTT_SHAFT_X1,
            KNOTT_SHAFT_Y1 - shaft_wall,
            KNOTT_GROUND_Z,
            KNOTT_SHAFT_X2,
            KNOTT_SHAFT_Y1,
            KNOTT_Z2,
            Textures.FLOOR_KH,
        )
    )

    DETAIL_BRUSHES.extend(
        layered_wall_y(
            KNOTT_SHAFT_Y1,
            KNOTT_ENT_X2,
            KNOTT_GROUND_Z,
            KNOTT_SHAFT_Y2,
            KNOTT_SHAFT_X1,
            KNOTT_Z2,
            shaft_door_openings,
            Textures.FLOOR_KH,
        )
    )

    DETAIL_BRUSHES.append(
        box(
            KNOTT_SHAFT_X2,
            KNOTT_SHAFT_Y1,
            KNOTT_GROUND_Z,
            KNOTT_SHAFT_X2 + shaft_wall,
            KNOTT_SHAFT_Y2,
            KNOTT_Z2,
            Textures.FLOOR_KH,
        )
    )

    west_shaft_door_openings = [
        (
            KNOTT_SHAFT_Y1 + 16,
            fz1,
            KNOTT_SHAFT_Y2 - 16,
            fz1 + shaft_door_h,
        )
        for _, fz1, _, _, _ in floor_levels()
    ] + [
        (
            KNOTT_STAIRS_Y1 + 16,
            fz1,
            KNOTT_STAIRS_MID_Y - 16,
            fz1 + shaft_door_h,
        )
        for _, fz1, _, _, _ in floor_levels()
    ]

    DETAIL_BRUSHES.append(
        box(
            KNOTT_STAIRS_X1,
            KNOTT_STAIRS_Y1 - shaft_wall,
            KNOTT_GROUND_Z,
            KNOTT_STAIRS_X2,
            KNOTT_STAIRS_Y1,
            KNOTT_Z2,
            Textures.FLOOR_KH,
        )
    )

    DETAIL_BRUSHES.extend(
        layered_wall_y(
            KNOTT_STAIRS_Y1,
            KNOTT_STAIRS_X2,
            KNOTT_GROUND_Z,
            KNOTT_STAIRS_Y2,
            KNOTT_ENT_X1,
            KNOTT_Z2,
            west_shaft_door_openings,
            Textures.FLOOR_KH,
        )
    )

    DETAIL_BRUSHES.append(
        box(
            KNOTT_STAIRS_X1 - shaft_wall,
            KNOTT_STAIRS_Y1,
            KNOTT_GROUND_Z,
            KNOTT_STAIRS_X1,
            KNOTT_STAIRS_Y2,
            KNOTT_Z2,
            Textures.FLOOR_KH,
        )
    )

    PLAT_H = 8
    stair_cx = (KNOTT_STAIRS_X1 + KNOTT_STAIRS_X2) // 2
    stair_x1 = stair_cx - KNOTT_STAIRS_HN * KNOTT_STAIRS_TREAD_X // 2
    stair_x2 = stair_x1 + KNOTT_STAIRS_HN * KNOTT_STAIRS_TREAD_X
    for _, _, _, floor_z0, _ in floor_levels():
        half_flight_z = floor_z0 + KNOTT_STAIRS_HN * KNOTT_STAIRS_STEP_R
        top_flight_z = floor_z0 + KNOTT.floor_h

        DETAIL_BRUSHES.append(
            box(
                stair_x2,
                KNOTT_STAIRS_MID_Y,
                floor_z0 - PLAT_H,
                KNOTT_STAIRS_X2,
                KNOTT_STAIRS_Y2,
                floor_z0,
                Textures.FLOOR_KH,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                stair_x2,
                KNOTT_STAIRS_Y1,
                top_flight_z - PLAT_H,
                KNOTT_STAIRS_X2,
                KNOTT_STAIRS_MID_Y,
                top_flight_z,
                Textures.FLOOR_KH,
            )
        )

        for tread_index in range(KNOTT_STAIRS_HN):
            step_x_east = stair_x2 - tread_index * KNOTT_STAIRS_TREAD_X
            step_x_west = stair_x2 - (tread_index + 1) * KNOTT_STAIRS_TREAD_X
            step_z1 = floor_z0 + tread_index * KNOTT_STAIRS_STEP_R
            DETAIL_BRUSHES.append(
                box(
                    step_x_west,
                    KNOTT_STAIRS_MID_Y,
                    step_z1,
                    step_x_east,
                    KNOTT_STAIRS_Y2,
                    step_z1 + KNOTT_STAIRS_STEP_R,
                    Textures.FLOOR_KH,
                    tt=Textures.FLOOR_KH,
                )
            )

        DETAIL_BRUSHES.append(
            box(
                KNOTT_STAIRS_X1,
                KNOTT_STAIRS_Y1,
                half_flight_z - PLAT_H,
                stair_x1,
                KNOTT_STAIRS_Y2,
                half_flight_z,
                Textures.FLOOR_KH,
            )
        )

        for tread_index in range(KNOTT_STAIRS_HN):
            step_x_west = stair_x1 + tread_index * KNOTT_STAIRS_TREAD_X
            step_x_east = step_x_west + KNOTT_STAIRS_TREAD_X
            step_z1 = half_flight_z + tread_index * KNOTT_STAIRS_STEP_R
            DETAIL_BRUSHES.append(
                box(
                    step_x_west,
                    KNOTT_STAIRS_Y1,
                    step_z1,
                    step_x_east,
                    KNOTT_STAIRS_MID_Y,
                    step_z1 + KNOTT_STAIRS_STEP_R,
                    Textures.FLOOR_KH,
                    tt=Textures.FLOOR_KH,
                )
            )

    for _, _, _, floor_z0, _ in floor_levels():
        half_flight_z = floor_z0 + KNOTT_STAIRS_HN * KNOTT_STAIRS_STEP_R
        top_flight_z = floor_z0 + KNOTT.floor_h

        DETAIL_BRUSHES.append(
            box(
                stair_x2,
                KNOTT_STAIRS_MID_Y,
                floor_z0,
                stair_x2 + KNOTT_STAIRS_POST_W,
                KNOTT_STAIRS_MID_Y + KNOTT_STAIRS_POST_W,
                floor_z0 + KNOTT_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                stair_x1 - KNOTT_STAIRS_POST_W,
                KNOTT_STAIRS_MID_Y,
                half_flight_z,
                stair_x1,
                KNOTT_STAIRS_MID_Y + KNOTT_STAIRS_POST_W,
                half_flight_z + KNOTT_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

        DETAIL_BRUSHES.append(
            ramp_slab(
                stair_x1,
                stair_x2,
                KNOTT_STAIRS_MID_Y,
                KNOTT_STAIRS_MID_Y + KNOTT_STAIRS_RAIL_T,
                half_flight_z + KNOTT_STAIRS_RAIL_H - KNOTT_STAIRS_RAIL_T,
                floor_z0 + KNOTT_STAIRS_RAIL_H - KNOTT_STAIRS_RAIL_T,
                half_flight_z + KNOTT_STAIRS_RAIL_H,
                floor_z0 + KNOTT_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                stair_x1 - KNOTT_STAIRS_POST_W,
                KNOTT_STAIRS_MID_Y - KNOTT_STAIRS_POST_W,
                half_flight_z,
                stair_x1,
                KNOTT_STAIRS_MID_Y,
                half_flight_z + KNOTT_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

        DETAIL_BRUSHES.append(
            box(
                stair_x2,
                KNOTT_STAIRS_MID_Y - KNOTT_STAIRS_POST_W,
                top_flight_z,
                stair_x2 + KNOTT_STAIRS_POST_W,
                KNOTT_STAIRS_MID_Y,
                top_flight_z + KNOTT_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

        DETAIL_BRUSHES.append(
            ramp_slab(
                stair_x1,
                stair_x2,
                KNOTT_STAIRS_MID_Y - KNOTT_STAIRS_RAIL_T,
                KNOTT_STAIRS_MID_Y,
                half_flight_z + KNOTT_STAIRS_RAIL_H - KNOTT_STAIRS_RAIL_T,
                top_flight_z + KNOTT_STAIRS_RAIL_H - KNOTT_STAIRS_RAIL_T,
                half_flight_z + KNOTT_STAIRS_RAIL_H,
                top_flight_z + KNOTT_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

    wx1, wx2 = bix1, KNOTT_ENT_X1 - KNOTT.wall_t
    ex1, ex2 = KNOTT_ENT_X2 + KNOTT.wall_t, bix2
    KNOTT_WEST_ROOM_CX = (wx1 + wx2) // 2
    KNOTT_EAST_ROOM_CX = (ex1 + ex2) // 2

    w_hall_openings = [(KNOTT_SHAFT_Y1, KNOTT_GROUND_Z, KNOTT_SHAFT_Y2, KNOTT_Z2)]
    e_hall_openings = [(KNOTT_SHAFT_Y1, KNOTT_GROUND_Z, KNOTT_SHAFT_Y2, KNOTT_Z2)]

    for floor_index, _fz1, _, fz_surf, _ in floor_levels():
        split = KNOTT_ROOM_SPLITS[floor_index]
        sr_yc = (KNOTT_BIY1 + split) // 2
        nr_yc = (split + KNOTT.wall_t + KNOTT_BIY2) // 2
        dz2 = fz_surf + 96
        w_hall_openings += [
            (sr_yc - 32, fz_surf, sr_yc + 32, dz2),
            (nr_yc - 32, fz_surf, nr_yc + 32, dz2),
        ]
        e_hall_openings += [
            (sr_yc - 32, fz_surf, sr_yc + 32, dz2),
            (nr_yc - 32, fz_surf, nr_yc + 32, dz2),
        ]

    DETAIL_BRUSHES.extend(
        layered_wall_y(
            KNOTT_BIY1,
            KNOTT_ENT_X1 - KNOTT.wall_t,
            KNOTT_GROUND_Z,
            KNOTT_BIY2,
            KNOTT_ENT_X1,
            KNOTT_Z2,
            w_hall_openings,
            Textures.FLOOR_KH,
        )
    )

    DETAIL_BRUSHES.extend(
        layered_wall_y(
            KNOTT_BIY1,
            KNOTT_ENT_X2,
            KNOTT_GROUND_Z,
            KNOTT_BIY2,
            KNOTT_ENT_X2 + KNOTT.wall_t,
            KNOTT_Z2,
            e_hall_openings,
            Textures.FLOOR_KH,
        )
    )

    for floor_index, fz1, fz2, fz_surf, _ in floor_levels():
        split = KNOTT_ROOM_SPLITS[floor_index]
        sp_y2 = split + KNOTT.wall_t
        pdz2 = fz_surf + 96

        DETAIL_BRUSHES.extend(
            layered_wall(
                wx1,
                split,
                fz1,
                wx2,
                sp_y2,
                fz2,
                [(KNOTT_WEST_ROOM_CX - 32, fz_surf, KNOTT_WEST_ROOM_CX + 32, pdz2)],
                Textures.FLOOR_KH,
            )
        )

        DETAIL_BRUSHES.extend(
            layered_wall(
                ex1,
                split,
                fz1,
                ex2,
                sp_y2,
                fz2,
                [(KNOTT_EAST_ROOM_CX - 32, fz_surf, KNOTT_EAST_ROOM_CX + 32, pdz2)],
                Textures.FLOOR_KH,
            )
        )

    if not KNOTT_ENABLED_EXTERIOR:
        del BRUSHES[knott_brush_start:]
        EXTERIOR_DETAIL_BRUSHES.clear()

    if not KNOTT_ENABLED_INTERIOR:
        DETAIL_BRUSHES.clear()

    DETAIL_BRUSHES.extend(EXTERIOR_DETAIL_BRUSHES)

    if KNOTT_ENABLED_EXTERIOR:
        BRUSHES.extend(
            render_text_flat(
                KNOTT_SIGN_TEXT[::-1],
                x0=knott_sign_cx - knott_sign_total_w // 2,
                y_face=KNOTT.y2 + 6,
                z_base=knott_sign_z1 + (KNOTT_SIGN_H - 6 * KNOTT_SIGN_PX_H) // 2,
                px_w=KNOTT_SIGN_PX_W,
                px_h=KNOTT_SIGN_PX_H,
                depth=2,
                tex=Textures.RAIL,
                mirror=True,
            )
        )

    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
