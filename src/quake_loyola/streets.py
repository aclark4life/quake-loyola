import math

from .constants import (
    BASEMENT_FLOOR_Z1,
    BRIDGE,
    BRIDGE_DZ2,
    CHARLES_CRN_R,
    CHARLES_CRN_SEGS,
    CHARLES_LAMP_POST_H,
    CHARLES_LAMP_POST_XS,
    CHARLES_LAMP_POST_YS,
    CHARLES_RAMP_W,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    CROSSWALK_GAP_W,
    CROSSWALK_LEN,
    CROSSWALK_STRIPE_W,
    DORM,
    ENNIS_CEMENT_WALL_CAP_H,
    ENNIS_CEMENT_WALL_CAP_OVH,
    ENNIS_CEMENT_WALL_H,
    ENNIS_CEMENT_WALL_LAMP_POST_H,
    ENNIS_CEMENT_WALL_PILLAR_EXTRA_H,
    ENNIS_CEMENT_WALL_PILLAR_HW,
    ENNIS_CEMENT_WALL_PILLAR_SPACING,
    ENNIS_CEMENT_X1,
    ENNIS_CEMENT_X2,
    ENNIS_CURB_BULGE_LEN,
    ENNIS_CURB_W,
    ENNIS_DIVIDER_EXTRA_N,
    ENNIS_GATE_FENCE_BAR_T,
    ENNIS_GATE_FENCE_HEIGHT,
    ENNIS_GATE_FENCE_POST_W,
    ENNIS_GATE_FENCE_SPACING,
    ENNIS_GATE_FENCE_TOP_RAIL_DROP,
    ENNIS_GATE_FENCE_TOP_RAIL_T,
    ENNIS_GATE_FENCE_WEST_SHIFT,
    ENNIS_GATE_PANEL_COUNT,
    ENNIS_GATE_PILLAR_CROSS_T,
    ENNIS_GATE_PILLAR_EXTRA_H,
    ENNIS_GATE_PILLAR_GAP,
    ENNIS_GATE_PILLAR_LEG_T,
    ENNIS_GATE_PILLAR_OPENING_W,
    ENNIS_GATE_PILLAR_W,
    ENNIS_GATE_X1,
    ENNIS_GATE_X2,
    ENNIS_HW,
    ENNIS_PANEL_GAP,
    ENNIS_PANEL_INNER_H,
    ENNIS_PANEL_INNER_W,
    ENNIS_PANEL_MOUNT_FOOT_DROP,
    ENNIS_PANEL_MOUNT_FOOT_INSET,
    ENNIS_PANEL_OUTER_H,
    ENNIS_PANEL_OUTER_W,
    ENNIS_PILLAR_BELL2_H,
    ENNIS_PILLAR_BELL2_HW,
    ENNIS_PILLAR_CAP_H,
    ENNIS_PILLAR_CAP_OVH,
    ENNIS_PILLAR_HW,
    ENNIS_PILLAR_NORTH_Y,
    ENNIS_PILLAR_POST_H,
    ENNIS_PILLAR_SOUTH_Y,
    ENNIS_PILLAR_X1,
    ENNIS_SHORT_WALL_NY,
    ENNIS_SW_EDGE,
    ENNIS_WALL_H,
    ENNIS_WALL_NY,
    ENNIS_WALL_PILLAR_H,
    ENNIS_WALL_PILLAR_HW,
    ENNIS_WALL_T,
    ENNIS_WALL_X_OFFSET,
    ENNIS_WIDEN_N,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    KNOTT_DRIVEWAY_CURB_CRN_R,
    KNOTT_DRIVEWAY_CURB_CRN_SEGS,
    KNOTT_DRIVEWAY_ES_X1,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_EXT_Y2,
    KNOTT_DRIVEWAY_JCX_E,
    KNOTT_DRIVEWAY_JCX_X1,
    KNOTT_DRIVEWAY_JCY,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_WS_X1,
    KNOTT_DRIVEWAY_WS_X2,
    KNOTT_ENABLED_TERRAIN,
    MANHOLE_R,
    MANHOLE_X,
    MANHOLE_Y,
    NE_ENABLED_TERRAIN,
    ROAD_X1,
    ROAD_X2,
    SDORM_LIFT,
    STREET_CHARLES_CURB_W,
    STREET_DIV_HW,
    STREET_DIV_LINE_HW,
    STREET_ENNIS_DIV_HW,
    STREET_SURFACE_T,
    STREETS_ENABLED_DETAILS,
    WALL_T,
    WEST_CAMPUS_ENABLED_TERRAIN,
    WORLD_X1,
    WORLD_X2,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    WORLD_Z2,
    Textures,
)
from .geometry import (
    arch_seg,
    arch_seg_y,
    box,
    box_with_round_hole,
    brush_ent,
    curb_seg,
    pyramid,
    ramp_slab,
    ramp_slab_y,
    shear_box_y,
    shear_box_z,
    torch_flame,
    tri_prism,
)
from .utils import swap_xy, swap_xz


def punch_manhole_detail(brushes):
    """Cut the manhole opening through overlapping thin detail slabs.

    Brushes fully inside the hole are dropped; overlapping box slabs are
    rebuilt with box_with_round_hole().
    """
    out = []
    for b in brushes:
        pts = [p for f in b.faces for p in (f.p1, f.p2, f.p3)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        z1, z2 = min(zs), max(zs)
        is_thin_surface_layer = z1 >= FLOOR_Z2 - 1 and z2 <= FLOOR_Z2 + 20
        if not is_thin_surface_layer:
            out.append(b)
            continue

        def _dist(px, py):
            return math.hypot(px - MANHOLE_X, py - MANHOLE_Y)

        corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
        entirely_inside_circle = all(_dist(px, py) <= MANHOLE_R for px, py in corners)
        overlaps_circle_bbox = (
            x1 <= MANHOLE_X + MANHOLE_R
            and x2 >= MANHOLE_X - MANHOLE_R
            and y1 <= MANHOLE_Y + MANHOLE_R
            and y2 >= MANHOLE_Y - MANHOLE_R
        )
        if entirely_inside_circle:
            continue
        elif overlaps_circle_bbox and len(b.faces) == 6:
            tex = b.faces[0].tex
            tt_params = b.faces[-1].params
            out.extend(
                box_with_round_hole(
                    x1,
                    y1,
                    z1,
                    x2,
                    y2,
                    z2,
                    MANHOLE_X,
                    MANHOLE_Y,
                    MANHOLE_R,
                    tex,
                    tt_params=tt_params,
                )
            )
        else:
            out.append(b)
    return out


def build_ennis_entrance_features():
    """Return the Ennis entrance pillars, walls, gates, and lamps owned by west-campus geometry."""
    brushes = []
    entities = []

    for pillar_y in (
        ENNIS_PILLAR_SOUTH_Y,
        ENNIS_PILLAR_NORTH_Y,
    ):
        ennis_pil_cx = ENNIS_PILLAR_X1 + ENNIS_PILLAR_HW
        cap_half_width = ENNIS_PILLAR_HW + ENNIS_PILLAR_CAP_OVH
        base_height = ENNIS_PILLAR_POST_H // 3
        brushes.append(
            box(
                ennis_pil_cx - cap_half_width,
                pillar_y - cap_half_width,
                FLOOR_Z2,
                ennis_pil_cx + cap_half_width,
                pillar_y + cap_half_width,
                FLOOR_Z2 + base_height,
                Textures.ENNIS_PILLAR,
            )
        )
        brushes.append(
            box(
                ENNIS_PILLAR_X1,
                pillar_y - ENNIS_PILLAR_HW,
                FLOOR_Z2 + base_height,
                ENNIS_PILLAR_X1 + 2 * ENNIS_PILLAR_HW,
                pillar_y + ENNIS_PILLAR_HW,
                FLOOR_Z2 + ENNIS_PILLAR_POST_H,
                Textures.ENNIS_PILLAR,
            )
        )
        cap_z = FLOOR_Z2 + ENNIS_PILLAR_POST_H
        brushes.append(
            box(
                ennis_pil_cx - cap_half_width,
                pillar_y - cap_half_width,
                cap_z,
                ennis_pil_cx + cap_half_width,
                pillar_y + cap_half_width,
                cap_z + ENNIS_PILLAR_CAP_H,
                Textures.ENNIS_PILLAR,
            )
        )
        bell2_z = cap_z + ENNIS_PILLAR_CAP_H
        brushes.append(
            box(
                ennis_pil_cx - ENNIS_PILLAR_BELL2_HW,
                pillar_y - ENNIS_PILLAR_BELL2_HW,
                bell2_z,
                ennis_pil_cx + ENNIS_PILLAR_BELL2_HW,
                pillar_y + ENNIS_PILLAR_BELL2_HW,
                bell2_z + ENNIS_PILLAR_BELL2_H,
                Textures.ENNIS_PILLAR,
            )
        )
        pillar_apex_z = bell2_z + ENNIS_PILLAR_BELL2_H
        brushes.append(
            box(
                ennis_pil_cx - 3,
                pillar_y - 3,
                pillar_apex_z,
                ennis_pil_cx + 3,
                pillar_y + 3,
                pillar_apex_z + 16,
                Textures.CEMENT,
            )
        )
        brushes.append(
            box(
                ennis_pil_cx - 5,
                pillar_y - 5,
                pillar_apex_z + 16,
                ennis_pil_cx + 5,
                pillar_y + 5,
                pillar_apex_z + 20,
                Textures.BRICK,
            )
        )
        pillar_flame_z = pillar_apex_z + 20
        entities.extend(torch_flame(ennis_pil_cx, pillar_y, pillar_flame_z))

    ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    bwex2 = ENNIS_GATE_X1
    brushes.append(
        box(
            ennis_wall_x1,
            ENNIS_SHORT_WALL_NY,
            FLOOR_Z2,
            bwex2,
            ENNIS_SHORT_WALL_NY + ENNIS_WALL_T,
            FLOOR_Z2 + ENNIS_WALL_H,
            Textures.BUILDING,
        )
    )
    sw_tex = Textures.FENCE
    sw_brick_top_z = FLOOR_Z2 + ENNIS_WALL_H
    sw_panel_y1 = ENNIS_SHORT_WALL_NY - ENNIS_GATE_FENCE_BAR_T
    sw_panel_y2 = ENNIS_SHORT_WALL_NY
    sw_panel_z1 = sw_brick_top_z + ENNIS_PANEL_MOUNT_FOOT_DROP
    sw_panel_z_center = sw_panel_z1 + ENNIS_PANEL_OUTER_H // 2
    _sw_frame_t = (ENNIS_PANEL_OUTER_W - ENNIS_PANEL_INNER_W) // 2
    sw_panel_outer_w = 41
    sw_panel_inner_w = sw_panel_outer_w - 2 * _sw_frame_t

    def sw_add_panel(center_x):
        x1_o = center_x - sw_panel_outer_w // 2
        x2_o = center_x + sw_panel_outer_w // 2
        z1_o = sw_panel_z_center - ENNIS_PANEL_OUTER_H // 2
        z2_o = sw_panel_z_center + ENNIS_PANEL_OUTER_H // 2
        x1_i = center_x - sw_panel_inner_w // 2
        x2_i = center_x + sw_panel_inner_w // 2
        z1_i = sw_panel_z_center - ENNIS_PANEL_INNER_H // 2
        z2_i = sw_panel_z_center + ENNIS_PANEL_INNER_H // 2
        brushes.extend(
            [
                box(
                    x1_o,
                    sw_panel_y1,
                    z1_o,
                    x2_o,
                    sw_panel_y2,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                    sw_tex,
                ),
                box(
                    x1_o,
                    sw_panel_y1,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    x2_o,
                    sw_panel_y2,
                    z2_o,
                    sw_tex,
                ),
                box(
                    x1_o,
                    sw_panel_y1,
                    z1_o,
                    x1_o + ENNIS_GATE_FENCE_BAR_T,
                    sw_panel_y2,
                    z2_o,
                    sw_tex,
                ),
                box(
                    x2_o - ENNIS_GATE_FENCE_BAR_T,
                    sw_panel_y1,
                    z1_o,
                    x2_o,
                    sw_panel_y2,
                    z2_o,
                    sw_tex,
                ),
                box(
                    x1_i,
                    sw_panel_y1,
                    z1_i,
                    x2_i,
                    sw_panel_y2,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                    sw_tex,
                ),
                box(
                    x1_i,
                    sw_panel_y1,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    x2_i,
                    sw_panel_y2,
                    z2_i,
                    sw_tex,
                ),
                box(
                    x1_i,
                    sw_panel_y1,
                    z1_i,
                    x1_i + ENNIS_GATE_FENCE_BAR_T,
                    sw_panel_y2,
                    z2_i,
                    sw_tex,
                ),
                box(
                    x2_i - ENNIS_GATE_FENCE_BAR_T,
                    sw_panel_y1,
                    z1_i,
                    x2_i,
                    sw_panel_y2,
                    z2_i,
                    sw_tex,
                ),
                ramp_slab(
                    x1_o,
                    x1_i,
                    sw_panel_y1,
                    sw_panel_y2,
                    z1_o,
                    z1_i,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                    sw_tex,
                ),
                ramp_slab(
                    x2_i,
                    x2_o,
                    sw_panel_y1,
                    sw_panel_y2,
                    z1_i,
                    z1_o,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                    sw_tex,
                ),
                ramp_slab(
                    x1_o,
                    x1_i,
                    sw_panel_y1,
                    sw_panel_y2,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    z2_o,
                    z2_i,
                    sw_tex,
                ),
                ramp_slab(
                    x2_i,
                    x2_o,
                    sw_panel_y1,
                    sw_panel_y2,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    z2_i,
                    z2_o,
                    sw_tex,
                ),
            ]
        )
        foot_hw = ENNIS_GATE_FENCE_BAR_T // 2
        foot_x1 = x1_o + ENNIS_PANEL_MOUNT_FOOT_INSET
        foot_x2 = x2_o - ENNIS_PANEL_MOUNT_FOOT_INSET
        brushes.extend(
            [
                box(
                    foot_x1 - foot_hw,
                    sw_panel_y1,
                    z1_o - ENNIS_PANEL_MOUNT_FOOT_DROP,
                    foot_x1 + foot_hw,
                    sw_panel_y2,
                    z1_o,
                    sw_tex,
                ),
                box(
                    foot_x2 - foot_hw,
                    sw_panel_y1,
                    z1_o - ENNIS_PANEL_MOUNT_FOOT_DROP,
                    foot_x2 + foot_hw,
                    sw_panel_y2,
                    z1_o,
                    sw_tex,
                ),
            ]
        )

    def sw_add_connector(x1, x2):
        if x2 <= x1:
            return
        bar_t = ENNIS_GATE_FENCE_BAR_T
        quarter_h = ENNIS_PANEL_OUTER_H // 4
        upper_z1 = sw_panel_z_center + quarter_h - bar_t // 2
        lower_z1 = sw_panel_z_center - quarter_h - bar_t // 2
        brushes.extend(
            [
                box(
                    x1, sw_panel_y1, upper_z1, x2, sw_panel_y2, upper_z1 + bar_t, sw_tex
                ),
                box(
                    x1, sw_panel_y1, lower_z1, x2, sw_panel_y2, lower_z1 + bar_t, sw_tex
                ),
            ]
        )

    def sw_shear_x_brace(z1, z2, cross_hw, opening_x1, opening_x2):
        b = shear_box_y(
            z1,
            -cross_hw,
            sw_panel_y1,
            z2,
            cross_hw,
            sw_panel_y2,
            opening_x1,
            opening_x2,
            sw_tex,
        )
        return swap_xy(swap_xz(b))

    def sw_add_arch_post(center_x):
        leg_t = ENNIS_GATE_PILLAR_LEG_T
        arch_rin = ENNIS_GATE_PILLAR_OPENING_W // 2
        arch_rout = arch_rin + leg_t
        post_top_z = sw_panel_z2_o + ENNIS_GATE_PILLAR_EXTRA_H
        legs_top_z = post_top_z - arch_rout
        leg_x1 = center_x - arch_rout
        leg_x2 = center_x + arch_rout
        brushes.extend(
            [
                box(
                    leg_x1,
                    sw_panel_y1,
                    sw_brick_top_z,
                    leg_x1 + leg_t,
                    sw_panel_y2,
                    legs_top_z,
                    sw_tex,
                ),
                box(
                    leg_x2 - leg_t,
                    sw_panel_y1,
                    sw_brick_top_z,
                    leg_x2,
                    sw_panel_y2,
                    legs_top_z,
                    sw_tex,
                ),
            ]
        )
        arch_segs = 8
        arch_step = 180.0 / arch_segs
        for seg_i in range(arch_segs):
            brushes.append(
                arch_seg_y(
                    sw_panel_y1,
                    sw_panel_y2,
                    center_x,
                    legs_top_z,
                    arch_rin,
                    arch_rout,
                    seg_i * arch_step,
                    (seg_i + 1) * arch_step,
                    sw_tex,
                )
            )
        cross_hw = ENNIS_GATE_PILLAR_CROSS_T // 2
        opening_x1 = center_x - arch_rin
        opening_x2 = center_x + arch_rin
        brushes.extend(
            [
                sw_shear_x_brace(
                    sw_brick_top_z, legs_top_z, cross_hw, opening_x1, opening_x2
                ),
                sw_shear_x_brace(
                    sw_brick_top_z, legs_top_z, cross_hw, opening_x2, opening_x1
                ),
            ]
        )

    sw_panel_z2_o = sw_panel_z_center + ENNIS_PANEL_OUTER_H // 2
    sw_arch_post_lead_x = (
        ennis_wall_x1 + ENNIS_WALL_T // 2 + ENNIS_WALL_PILLAR_HW + ENNIS_GATE_PILLAR_GAP
    )
    sw_add_arch_post(sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W // 2)
    sw_cursor_x = sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W
    sw_gap_x1 = sw_cursor_x
    sw_cursor_x += ENNIS_GATE_PILLAR_GAP
    sw_add_connector(sw_gap_x1, sw_cursor_x)

    sw_panel_count = 3
    sw_run_w = (
        sw_panel_count * sw_panel_outer_w + (sw_panel_count - 1) * ENNIS_PANEL_GAP
    )
    sw_run_x1 = sw_cursor_x
    for i in range(sw_panel_count):
        panel_center_x = (
            sw_run_x1 + i * (sw_panel_outer_w + ENNIS_PANEL_GAP) + sw_panel_outer_w // 2
        )
        sw_add_panel(panel_center_x)
        if i > 0:
            sw_add_connector(
                panel_center_x - sw_panel_outer_w // 2 - ENNIS_PANEL_GAP,
                panel_center_x - sw_panel_outer_w // 2,
            )
    sw_trailing_gap_x1 = sw_run_x1 + sw_run_w
    sw_trailing_gap_x2 = sw_trailing_gap_x1 + ENNIS_GATE_PILLAR_GAP
    sw_add_connector(sw_trailing_gap_x1, sw_trailing_gap_x2)
    sw_add_arch_post(sw_trailing_gap_x2 + ENNIS_GATE_PILLAR_W // 2)
    fence_bridge_x1 = bwex2 - ENNIS_WALL_T
    fence_bridge_x2 = bwex2
    fence_bridge_south_y2 = ENNIS_WALL_NY + ENNIS_WALL_T // 2 - 1 + 2
    fence_bridge_north_y1 = ENNIS_SHORT_WALL_NY
    fence_bridge_mid_y = (
        fence_bridge_south_y2
        + ENNIS_GATE_FENCE_POST_W
        + fence_bridge_north_y1
        - ENNIS_GATE_FENCE_POST_W
    ) // 2
    brushes.extend(
        [
            box(
                fence_bridge_x1,
                fence_bridge_south_y2,
                FLOOR_Z2,
                fence_bridge_x2,
                fence_bridge_south_y2 + ENNIS_GATE_FENCE_POST_W,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                Textures.FENCE,
            ),
            box(
                fence_bridge_x1,
                fence_bridge_north_y1 - ENNIS_GATE_FENCE_POST_W,
                FLOOR_Z2,
                fence_bridge_x2,
                fence_bridge_north_y1,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                Textures.FENCE,
            ),
            box(
                fence_bridge_x1,
                fence_bridge_mid_y - ENNIS_GATE_FENCE_BAR_T // 2,
                FLOOR_Z2,
                fence_bridge_x2,
                fence_bridge_mid_y + ENNIS_GATE_FENCE_BAR_T // 2,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                Textures.FENCE,
            ),
            box(
                fence_bridge_x1,
                fence_bridge_south_y2,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT - ENNIS_GATE_FENCE_TOP_RAIL_DROP,
                fence_bridge_x2,
                fence_bridge_north_y1,
                FLOOR_Z2
                + ENNIS_GATE_FENCE_HEIGHT
                - ENNIS_GATE_FENCE_TOP_RAIL_DROP
                + ENNIS_GATE_FENCE_TOP_RAIL_T,
                Textures.FENCE,
            ),
        ]
    )
    gate_run_start_y = (
        ENNIS_SHORT_WALL_NY
        + ENNIS_WALL_T // 2
        + ENNIS_WALL_PILLAR_HW
        + ENNIS_GATE_PILLAR_GAP
    )
    _pair_w = 2 * ENNIS_PANEL_OUTER_W + ENNIS_PANEL_GAP
    _arch_post_unit_lead = ENNIS_GATE_PILLAR_W + ENNIS_GATE_PILLAR_GAP
    _arch_post_unit_trail = 2 * ENNIS_GATE_PILLAR_GAP + ENNIS_GATE_PILLAR_W
    _pair_count = ENNIS_GATE_PANEL_COUNT // 2
    total_gate_w = _arch_post_unit_lead + _pair_count * (
        _pair_w + _arch_post_unit_trail
    )
    bw_mid_y = gate_run_start_y + total_gate_w
    brushes.append(
        box(
            ennis_wall_x1,
            ENNIS_SHORT_WALL_NY,
            FLOOR_Z2,
            ennis_wall_x1 + ENNIS_WALL_T,
            bw_mid_y,
            FLOOR_Z2 + ENNIS_WALL_H,
            Textures.BUILDING,
        )
    )

    gate_fence_x1 = ennis_wall_x1 + ENNIS_WALL_T // 2 - 1 - ENNIS_GATE_FENCE_WEST_SHIFT
    gate_fence_x2 = gate_fence_x1 + ENNIS_GATE_FENCE_BAR_T
    gate_fence_tex = Textures.FENCE
    fence_end_y = WORLD_Y2 - WALL_T
    brushes.append(
        box(
            gate_fence_x1,
            bw_mid_y,
            FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT - ENNIS_GATE_FENCE_TOP_RAIL_DROP,
            gate_fence_x2,
            fence_end_y,
            FLOOR_Z2
            + ENNIS_GATE_FENCE_HEIGHT
            - ENNIS_GATE_FENCE_TOP_RAIL_DROP
            + ENNIS_GATE_FENCE_TOP_RAIL_T,
            gate_fence_tex,
        )
    )
    gate_picket_y = bw_mid_y
    gate_picket_index = 0
    while gate_picket_y + 2 <= fence_end_y:
        gate_picket_width = (
            ENNIS_GATE_FENCE_POST_W
            if gate_picket_index % 10 == 0
            else ENNIS_GATE_FENCE_BAR_T
        )
        brushes.append(
            box(
                gate_fence_x1,
                gate_picket_y,
                FLOOR_Z2,
                gate_fence_x2,
                gate_picket_y + gate_picket_width,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                gate_fence_tex,
            )
        )
        gate_picket_y += ENNIS_GATE_FENCE_SPACING
        gate_picket_index += 1

    connector_y1 = bw_mid_y
    connector_y2 = bw_mid_y + ENNIS_GATE_FENCE_POST_W
    connector_wall_x2 = ennis_wall_x1 + ENNIS_WALL_T // 2 - 1 + ENNIS_GATE_FENCE_BAR_T
    connector_x1 = gate_fence_x2
    connector_x2 = connector_wall_x2
    connector_mid_x = (
        connector_x1 + ENNIS_GATE_FENCE_POST_W + connector_x2 - ENNIS_GATE_FENCE_POST_W
    ) // 2
    brushes.extend(
        [
            box(
                connector_x1,
                connector_y1,
                FLOOR_Z2,
                connector_x1 + ENNIS_GATE_FENCE_POST_W,
                connector_y2,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                gate_fence_tex,
            ),
            box(
                connector_x2 - ENNIS_GATE_FENCE_POST_W,
                connector_y1,
                FLOOR_Z2,
                connector_x2,
                connector_y2,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                gate_fence_tex,
            ),
            box(
                connector_mid_x - ENNIS_GATE_FENCE_BAR_T // 2,
                connector_y1,
                FLOOR_Z2,
                connector_mid_x + ENNIS_GATE_FENCE_BAR_T // 2,
                connector_y2,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                gate_fence_tex,
            ),
            box(
                connector_x1,
                connector_y1,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT - ENNIS_GATE_FENCE_TOP_RAIL_DROP,
                connector_x2,
                connector_y2,
                FLOOR_Z2
                + ENNIS_GATE_FENCE_HEIGHT
                - ENNIS_GATE_FENCE_TOP_RAIL_DROP
                + ENNIS_GATE_FENCE_TOP_RAIL_T,
                gate_fence_tex,
            ),
        ]
    )

    panel_x1 = ennis_wall_x1 - ENNIS_GATE_FENCE_BAR_T
    panel_x2 = ennis_wall_x1
    brick_top_z = FLOOR_Z2 + ENNIS_WALL_H
    panel_z1 = brick_top_z + ENNIS_PANEL_MOUNT_FOOT_DROP
    panel_z_center = panel_z1 + ENNIS_PANEL_OUTER_H // 2
    panel_z2_o = panel_z_center + ENNIS_PANEL_OUTER_H // 2

    def add_panel(center_y):
        y1_o = center_y - ENNIS_PANEL_OUTER_W // 2
        y2_o = center_y + ENNIS_PANEL_OUTER_W // 2
        z1_o = panel_z_center - ENNIS_PANEL_OUTER_H // 2
        z2_o = panel_z_center + ENNIS_PANEL_OUTER_H // 2
        y1_i = center_y - ENNIS_PANEL_INNER_W // 2
        y2_i = center_y + ENNIS_PANEL_INNER_W // 2
        z1_i = panel_z_center - ENNIS_PANEL_INNER_H // 2
        z2_i = panel_z_center + ENNIS_PANEL_INNER_H // 2
        brushes.extend(
            [
                box(
                    panel_x1,
                    y1_o,
                    z1_o,
                    panel_x2,
                    y2_o,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y1_o,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    panel_x2,
                    y2_o,
                    z2_o,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y1_o,
                    z1_o,
                    panel_x2,
                    y1_o + ENNIS_GATE_FENCE_BAR_T,
                    z2_o,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y2_o - ENNIS_GATE_FENCE_BAR_T,
                    z1_o,
                    panel_x2,
                    y2_o,
                    z2_o,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y1_i,
                    z1_i,
                    panel_x2,
                    y2_i,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y1_i,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    panel_x2,
                    y2_i,
                    z2_i,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y1_i,
                    z1_i,
                    panel_x2,
                    y1_i + ENNIS_GATE_FENCE_BAR_T,
                    z2_i,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y2_i - ENNIS_GATE_FENCE_BAR_T,
                    z1_i,
                    panel_x2,
                    y2_i,
                    z2_i,
                    gate_fence_tex,
                ),
                ramp_slab_y(
                    panel_x1,
                    panel_x2,
                    y1_o,
                    y1_i,
                    z1_o,
                    z1_i,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                    gate_fence_tex,
                ),
                ramp_slab_y(
                    panel_x1,
                    panel_x2,
                    y2_i,
                    y2_o,
                    z1_i,
                    z1_o,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                    gate_fence_tex,
                ),
                ramp_slab_y(
                    panel_x1,
                    panel_x2,
                    y1_o,
                    y1_i,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    z2_o,
                    z2_i,
                    gate_fence_tex,
                ),
                ramp_slab_y(
                    panel_x1,
                    panel_x2,
                    y2_i,
                    y2_o,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    z2_i,
                    z2_o,
                    gate_fence_tex,
                ),
            ]
        )
        foot_hw = ENNIS_GATE_FENCE_BAR_T // 2
        foot_y1 = y1_o + ENNIS_PANEL_MOUNT_FOOT_INSET
        foot_y2 = y2_o - ENNIS_PANEL_MOUNT_FOOT_INSET
        brushes.extend(
            [
                box(
                    panel_x1,
                    foot_y1 - foot_hw,
                    z1_o - ENNIS_PANEL_MOUNT_FOOT_DROP,
                    panel_x2,
                    foot_y1 + foot_hw,
                    z1_o,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    foot_y2 - foot_hw,
                    z1_o - ENNIS_PANEL_MOUNT_FOOT_DROP,
                    panel_x2,
                    foot_y2 + foot_hw,
                    z1_o,
                    gate_fence_tex,
                ),
            ]
        )

    def add_arch_post(center_y):
        leg_t = ENNIS_GATE_PILLAR_LEG_T
        arch_rin = ENNIS_GATE_PILLAR_OPENING_W // 2
        arch_rout = arch_rin + leg_t
        post_top_z = panel_z2_o + ENNIS_GATE_PILLAR_EXTRA_H
        legs_top_z = post_top_z - arch_rout
        leg_y1 = center_y - arch_rout
        leg_y2 = center_y + arch_rout
        brushes.extend(
            [
                box(
                    panel_x1,
                    leg_y1,
                    brick_top_z,
                    panel_x2,
                    leg_y1 + leg_t,
                    legs_top_z,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    leg_y2 - leg_t,
                    brick_top_z,
                    panel_x2,
                    leg_y2,
                    legs_top_z,
                    gate_fence_tex,
                ),
            ]
        )
        arch_segs = 8
        arch_step = 180.0 / arch_segs
        for seg_i in range(arch_segs):
            brushes.append(
                arch_seg(
                    panel_x1,
                    panel_x2,
                    center_y,
                    legs_top_z,
                    arch_rin,
                    arch_rout,
                    seg_i * arch_step,
                    (seg_i + 1) * arch_step,
                    gate_fence_tex,
                )
            )
        cross_hw = ENNIS_GATE_PILLAR_CROSS_T // 2
        opening_y1 = center_y - arch_rin
        opening_y2 = center_y + arch_rin
        brushes.extend(
            [
                shear_box_z(
                    panel_x1,
                    -cross_hw,
                    brick_top_z,
                    panel_x2,
                    cross_hw,
                    legs_top_z,
                    opening_y1,
                    opening_y2,
                    gate_fence_tex,
                ),
                shear_box_z(
                    panel_x1,
                    -cross_hw,
                    brick_top_z,
                    panel_x2,
                    cross_hw,
                    legs_top_z,
                    opening_y2,
                    opening_y1,
                    gate_fence_tex,
                ),
            ]
        )

    def add_connector(y1, y2):
        if y2 <= y1:
            return
        bar_t = ENNIS_GATE_FENCE_BAR_T
        quarter_h = ENNIS_PANEL_OUTER_H // 4
        upper_z1 = panel_z_center + quarter_h - bar_t // 2
        lower_z1 = panel_z_center - quarter_h - bar_t // 2
        brushes.extend(
            [
                box(
                    panel_x1,
                    y1,
                    upper_z1,
                    panel_x2,
                    y2,
                    upper_z1 + bar_t,
                    gate_fence_tex,
                ),
                box(
                    panel_x1,
                    y1,
                    lower_z1,
                    panel_x2,
                    y2,
                    lower_z1 + bar_t,
                    gate_fence_tex,
                ),
            ]
        )

    cursor_y = gate_run_start_y
    add_arch_post(cursor_y + ENNIS_GATE_PILLAR_W // 2)
    cursor_y += ENNIS_GATE_PILLAR_W
    gap_y1 = cursor_y
    cursor_y += ENNIS_GATE_PILLAR_GAP
    add_connector(gap_y1, cursor_y)
    for pair_i in range(_pair_count):
        add_panel(cursor_y + ENNIS_PANEL_OUTER_W // 2)
        cursor_y += ENNIS_PANEL_OUTER_W
        gap_y1 = cursor_y
        cursor_y += ENNIS_PANEL_GAP
        add_connector(gap_y1, cursor_y)
        add_panel(cursor_y + ENNIS_PANEL_OUTER_W // 2)
        cursor_y += ENNIS_PANEL_OUTER_W
        gap_y1 = cursor_y
        cursor_y += ENNIS_GATE_PILLAR_GAP
        add_connector(gap_y1, cursor_y)
        add_arch_post(cursor_y + ENNIS_GATE_PILLAR_W // 2)
        cursor_y += ENNIS_GATE_PILLAR_W
        gap_y1 = cursor_y
        cursor_y += ENNIS_GATE_PILLAR_GAP
        if pair_i < _pair_count - 1:
            add_connector(gap_y1, cursor_y)
    assert cursor_y == bw_mid_y, (cursor_y, bw_mid_y)

    bw_cx = ennis_wall_x1 + ENNIS_WALL_T // 2
    bw_cy = ENNIS_SHORT_WALL_NY + ENNIS_WALL_T // 2
    brushes.append(
        box(
            bw_cx - ENNIS_WALL_PILLAR_HW,
            bw_cy - ENNIS_WALL_PILLAR_HW,
            FLOOR_Z2,
            bw_cx + ENNIS_WALL_PILLAR_HW,
            bw_cy + ENNIS_WALL_PILLAR_HW,
            FLOOR_Z2 + ENNIS_WALL_PILLAR_H,
            Textures.BUILDING,
        )
    )
    brushes.append(
        box(
            bw_cx - ENNIS_WALL_PILLAR_HW,
            bw_cy - ENNIS_WALL_PILLAR_HW,
            FLOOR_Z2 + ENNIS_WALL_PILLAR_H,
            bw_cx + ENNIS_WALL_PILLAR_HW,
            bw_cy + ENNIS_WALL_PILLAR_HW,
            FLOOR_Z2 + ENNIS_WALL_PILLAR_H + 6,
            Textures.CEMENT,
        )
    )
    brushes.append(
        box(
            bw_cx - ENNIS_WALL_PILLAR_HW - 1,
            bw_cy - ENNIS_WALL_PILLAR_HW - 1,
            FLOOR_Z2 + ENNIS_WALL_PILLAR_H + 6,
            bw_cx + ENNIS_WALL_PILLAR_HW + 1,
            bw_cy + ENNIS_WALL_PILLAR_HW + 1,
            FLOOR_Z2 + ENNIS_WALL_PILLAR_H + 10,
            Textures.CEMENT,
        )
    )
    brushes.append(
        pyramid(
            bw_cx - ENNIS_WALL_PILLAR_HW - 1,
            bw_cy - ENNIS_WALL_PILLAR_HW - 1,
            FLOOR_Z2 + ENNIS_WALL_PILLAR_H + 10,
            bw_cx + ENNIS_WALL_PILLAR_HW + 1,
            bw_cy + ENNIS_WALL_PILLAR_HW + 1,
            FLOOR_Z2 + ENNIS_WALL_PILLAR_H + 16,
            Textures.CEMENT,
        )
    )

    east_gate_y1 = ENNIS_WALL_NY + ENNIS_WALL_T // 2 - 1
    east_gate_y2 = east_gate_y1 + 2
    east_gate_brushes = [
        box(
            ENNIS_GATE_X1,
            east_gate_y1,
            FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT - ENNIS_GATE_FENCE_TOP_RAIL_DROP,
            ENNIS_GATE_X2,
            east_gate_y2,
            FLOOR_Z2
            + ENNIS_GATE_FENCE_HEIGHT
            - ENNIS_GATE_FENCE_TOP_RAIL_DROP
            + ENNIS_GATE_FENCE_TOP_RAIL_T,
            gate_fence_tex,
        )
    ]
    east_gate_picket_x = ENNIS_GATE_X1
    east_gate_picket_index = 0
    while east_gate_picket_x + 2 <= ENNIS_GATE_X2:
        east_gate_picket_width = (
            ENNIS_GATE_FENCE_POST_W
            if east_gate_picket_index % 10 == 0
            else ENNIS_GATE_FENCE_BAR_T
        )
        east_gate_brushes.append(
            box(
                east_gate_picket_x,
                east_gate_y1,
                FLOOR_Z2,
                east_gate_picket_x + east_gate_picket_width,
                east_gate_y2,
                FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT,
                gate_fence_tex,
            )
        )
        east_gate_picket_x += ENNIS_GATE_FENCE_SPACING
        east_gate_picket_index += 1

    cement_wall_y1 = ENNIS_WALL_NY
    cement_wall_y2 = ENNIS_WALL_NY + ENNIS_WALL_T
    cement_wall_height = ENNIS_CEMENT_WALL_H
    cement_wall_pillar_half_width = ENNIS_CEMENT_WALL_PILLAR_HW
    cement_wall_pillar_height = cement_wall_height + ENNIS_CEMENT_WALL_PILLAR_EXTRA_H
    brushes.append(
        box(
            ENNIS_CEMENT_X1 + cement_wall_pillar_half_width,
            cement_wall_y1,
            FLOOR_Z2,
            ENNIS_CEMENT_X2 - cement_wall_pillar_half_width,
            cement_wall_y2,
            FLOOR_Z2 + cement_wall_height,
            Textures.CEMENT,
        )
    )
    brushes.append(
        box(
            ENNIS_CEMENT_X1 + cement_wall_pillar_half_width,
            cement_wall_y1 - ENNIS_CEMENT_WALL_CAP_OVH,
            FLOOR_Z2 + cement_wall_height,
            ENNIS_CEMENT_X2 - cement_wall_pillar_half_width,
            cement_wall_y2 + ENNIS_CEMENT_WALL_CAP_OVH,
            FLOOR_Z2 + cement_wall_height + ENNIS_CEMENT_WALL_CAP_H,
            Textures.CEMENT,
        )
    )
    ENNIS_CEMENT_X2_EXT = ENNIS_CEMENT_X2 + ENNIS_CURB_BULGE_LEN
    _wall_cap_z1 = FLOOR_Z2 + cement_wall_height
    _wall_cap_z2 = _wall_cap_z1 + ENNIS_CEMENT_WALL_CAP_H
    _wall_bulge_draw_x1 = ENNIS_CEMENT_X2 + cement_wall_pillar_half_width
    _wall_bulge_draw_x2 = ENNIS_CEMENT_X2_EXT - cement_wall_pillar_half_width
    _wall_bulge_cx = (_wall_bulge_draw_x1 + _wall_bulge_draw_x2) / 2
    _wall_bulge_half_len = (_wall_bulge_draw_x2 - _wall_bulge_draw_x1) / 2
    _wall_bulge_depth = _wall_bulge_half_len / 2

    def _wall_bulge_depth_at(bx):
        bdx = bx - _wall_bulge_cx
        _t = max(1 - (bdx / _wall_bulge_half_len) ** 2, 0)
        return _wall_bulge_depth * math.sqrt(_t)

    _wall_bulge_segments = 24
    _wall_bulge_step = (
        _wall_bulge_draw_x2 - _wall_bulge_draw_x1
    ) / _wall_bulge_segments
    for _wi in range(_wall_bulge_segments):
        _wx1 = _wall_bulge_draw_x1 + _wi * _wall_bulge_step
        _wx2 = _wx1 + _wall_bulge_step
        _wd1 = _wall_bulge_depth_at(_wx1)
        _wd2 = _wall_bulge_depth_at(_wx2)
        _w_south1 = cement_wall_y1 - _wd1
        _w_south2 = cement_wall_y1 - _wd2
        _w_north1 = cement_wall_y2 - _wd1
        _w_north2 = cement_wall_y2 - _wd2
        brushes.append(
            tri_prism(
                _wx1,
                _w_south1,
                _wx2,
                _w_south2,
                _wx2,
                _w_north2,
                FLOOR_Z2,
                FLOOR_Z2 + cement_wall_height,
                Textures.CEMENT,
            )
        )
        brushes.append(
            tri_prism(
                _wx1,
                _w_south1,
                _wx2,
                _w_north2,
                _wx1,
                _w_north1,
                FLOOR_Z2,
                FLOOR_Z2 + cement_wall_height,
                Textures.CEMENT,
            )
        )
        _c_south1 = _w_south1 - ENNIS_CEMENT_WALL_CAP_OVH
        _c_south2 = _w_south2 - ENNIS_CEMENT_WALL_CAP_OVH
        _c_north1 = _w_north1 + ENNIS_CEMENT_WALL_CAP_OVH
        _c_north2 = _w_north2 + ENNIS_CEMENT_WALL_CAP_OVH
        brushes.append(
            tri_prism(
                _wx1,
                _c_south1,
                _wx2,
                _c_south2,
                _wx2,
                _c_north2,
                _wall_cap_z1,
                _wall_cap_z2,
                Textures.CEMENT,
            )
        )
        brushes.append(
            tri_prism(
                _wx1,
                _c_south1,
                _wx2,
                _c_north2,
                _wx1,
                _c_north1,
                _wall_cap_z1,
                _wall_cap_z2,
                Textures.CEMENT,
            )
        )

    def _build_wall_pillar(pillar_x, with_lamp):
        pillar_center_y = (cement_wall_y1 + cement_wall_y2) // 2
        brushes.append(
            box(
                pillar_x - cement_wall_pillar_half_width,
                pillar_center_y - cement_wall_pillar_half_width,
                FLOOR_Z2,
                pillar_x + cement_wall_pillar_half_width,
                pillar_center_y + cement_wall_pillar_half_width,
                FLOOR_Z2 + cement_wall_pillar_height,
                Textures.CEMENT,
            )
        )
        brushes.append(
            box(
                pillar_x - cement_wall_pillar_half_width - ENNIS_CEMENT_WALL_CAP_OVH,
                pillar_center_y
                - cement_wall_pillar_half_width
                - ENNIS_CEMENT_WALL_CAP_OVH,
                FLOOR_Z2 + cement_wall_pillar_height,
                pillar_x + cement_wall_pillar_half_width + ENNIS_CEMENT_WALL_CAP_OVH,
                pillar_center_y
                + cement_wall_pillar_half_width
                + ENNIS_CEMENT_WALL_CAP_OVH,
                FLOOR_Z2 + cement_wall_pillar_height + ENNIS_CEMENT_WALL_CAP_H,
                Textures.CEMENT,
            )
        )
        if with_lamp:
            lamppost_base_z = (
                FLOOR_Z2 + cement_wall_pillar_height + ENNIS_CEMENT_WALL_CAP_H
            )
            brushes.append(
                box(
                    pillar_x - 3,
                    pillar_center_y - 3,
                    lamppost_base_z,
                    pillar_x + 3,
                    pillar_center_y + 3,
                    lamppost_base_z + ENNIS_CEMENT_WALL_LAMP_POST_H,
                    Textures.PILLAR,
                )
            )
            cement_wall_flame_z = lamppost_base_z + ENNIS_CEMENT_WALL_LAMP_POST_H + 20
            entities.extend(torch_flame(pillar_x, pillar_center_y, cement_wall_flame_z))
            brushes.append(
                box(
                    pillar_x - 4,
                    pillar_center_y - 4,
                    lamppost_base_z + ENNIS_CEMENT_WALL_LAMP_POST_H,
                    pillar_x + 4,
                    pillar_center_y + 4,
                    lamppost_base_z
                    + ENNIS_CEMENT_WALL_LAMP_POST_H
                    + ENNIS_CEMENT_WALL_PILLAR_EXTRA_H,
                    Textures.CEMENT,
                )
            )
            brushes.append(
                box(
                    pillar_x - 7,
                    pillar_center_y - 7,
                    lamppost_base_z
                    + ENNIS_CEMENT_WALL_LAMP_POST_H
                    + ENNIS_CEMENT_WALL_PILLAR_EXTRA_H,
                    pillar_x + 7,
                    pillar_center_y + 7,
                    lamppost_base_z
                    + ENNIS_CEMENT_WALL_LAMP_POST_H
                    + ENNIS_CEMENT_WALL_PILLAR_EXTRA_H
                    + ENNIS_GATE_FENCE_TOP_RAIL_T * 2,
                    Textures.CEMENT,
                )
            )

    for pillar_x in (ENNIS_CEMENT_X1, ENNIS_CEMENT_X2, ENNIS_CEMENT_X2_EXT):
        _build_wall_pillar(pillar_x, with_lamp=True)

    _ext_run_x1 = ENNIS_CEMENT_X2_EXT
    _ext_run_x2 = WORLD_X2 - WALL_T
    _ext_run_len = _ext_run_x2 - _ext_run_x1
    _ext_pillar_count = max(1, round(_ext_run_len / ENNIS_CEMENT_WALL_PILLAR_SPACING))
    _ext_pillar_spacing = _ext_run_len / _ext_pillar_count
    _ext_pillar_xs = [
        _ext_run_x1 + round(i * _ext_pillar_spacing)
        for i in range(1, _ext_pillar_count + 1)
    ]
    _prev_pillar_x = _ext_run_x1
    for _ext_i, _pillar_x in enumerate(_ext_pillar_xs):
        brushes.append(
            box(
                _prev_pillar_x + cement_wall_pillar_half_width,
                cement_wall_y1,
                FLOOR_Z2,
                _pillar_x - cement_wall_pillar_half_width,
                cement_wall_y2,
                FLOOR_Z2 + cement_wall_height,
                Textures.CEMENT,
            )
        )
        brushes.append(
            box(
                _prev_pillar_x + cement_wall_pillar_half_width,
                cement_wall_y1 - ENNIS_CEMENT_WALL_CAP_OVH,
                FLOOR_Z2 + cement_wall_height,
                _pillar_x - cement_wall_pillar_half_width,
                cement_wall_y2 + ENNIS_CEMENT_WALL_CAP_OVH,
                FLOOR_Z2 + cement_wall_height + ENNIS_CEMENT_WALL_CAP_H,
                Textures.CEMENT,
            )
        )
        _build_wall_pillar(_pillar_x, with_lamp=(_ext_i % 2 == 1))
        _prev_pillar_x = _pillar_x

    if east_gate_brushes:
        entities.append(brush_ent("func_detail", east_gate_brushes))
    return brushes, entities


def build():
    BRUSHES = []
    ENTITIES = []
    DETAIL_BRUSHES = []
    _tunnel_wall_tex_n = Textures.SKY
    _tunnel_wall_tex = Textures.GROUND if WEST_CAMPUS_ENABLED_TERRAIN else Textures.SKY
    BRUSHES.extend(
        box_with_round_hole(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z2,
            MANHOLE_X,
            MANHOLE_Y,
            MANHOLE_R,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            BRIDGE_DZ2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BRIDGE_DZ2,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X2_EXT - WALL_T,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y2 - WALL_T,
            FLOOR_Z1,
            BRIDGE.x1,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            BRIDGE.x1,
            WORLD_Y1 + WALL_T,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y2 - WALL_T,
            WORLD_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            Textures.SKY,
            tt=_tunnel_wall_tex_n,
            te=_tunnel_wall_tex_n,
            ts=_tunnel_wall_tex_n,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y2 - WALL_T,
            WORLD_Y2,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            WORLD_Z2,
            WORLD_Z2,
            Textures.SKY,
            tb=_tunnel_wall_tex_n,
        )
    )
    BRUSHES.append(
        box(
            DORM.x1,
            WORLD_Y2 - WALL_T,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            Textures.SKY,
            tt=_tunnel_wall_tex,
            ts=_tunnel_wall_tex,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE.x1,
            DORM.x1 + WALL_T,
            WORLD_Y1,
            WORLD_Y1 + WALL_T,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            WORLD_Z2,
            WORLD_Z2,
            Textures.SKY,
            tb=_tunnel_wall_tex,
        )
    )
    BRUSHES.append(
        box(
            DORM.x1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y1 + WALL_T,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            WORLD_Z2 - WALL_T,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )
    if not STREETS_ENABLED_DETAILS:
        return BRUSHES, ENTITIES
    _world_brushes = BRUSHES
    BRUSHES = DETAIL_BRUSHES

    CHARLES_Y1 = WORLD_Y1 + WALL_T
    CHARLES_Y2 = WORLD_Y2 - WALL_T

    def ranges_excluding(v1, v2, ex1, ex2):
        """Return the subranges of [v1, v2) that lie outside [ex1, ex2)."""
        ranges = []
        if ex1 > v1:
            ranges.append((v1, min(ex1, v2)))
        if ex2 < v2:
            ranges.append((max(ex2, v1), v2))
        return ranges

    CHARLES_CROSSING_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
    CHARLES_CROSSING_Y1 = CHARLES_CROSSING_Y2 - CROSSWALK_LEN
    CHARLES_CROSSING_MID = (CHARLES_CROSSING_Y1 + CHARLES_CROSSING_Y2) / 2

    ENNIS_X1 = ROAD_X1
    ENNIS_X2 = WORLD_X2_EXT - WALL_T

    ENNIS_CROSSING_X1 = ROAD_X2
    ENNIS_CROSSING_X2 = ROAD_X2 + CHARLES_WALK_W

    ROAD_CX = (ROAD_X1 + ROAD_X2) / 2
    WEST_LANE_LINE_X = (ROAD_X1 + ROAD_CX - STREET_DIV_HW) / 2
    EAST_LANE_LINE_X = (ROAD_CX + STREET_DIV_HW + ROAD_X2) / 2
    for lane_x1, lane_x2 in (
        (ROAD_X1, WEST_LANE_LINE_X - STREET_DIV_LINE_HW),
        (
            WEST_LANE_LINE_X + STREET_DIV_LINE_HW,
            ROAD_CX - STREET_DIV_HW,
        ),
        (
            ROAD_CX + STREET_DIV_HW,
            EAST_LANE_LINE_X - STREET_DIV_LINE_HW,
        ),
        (EAST_LANE_LINE_X + STREET_DIV_LINE_HW, ROAD_X2),
    ):
        for lane_y1, lane_y2 in ranges_excluding(
            CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
        ):
            BRUSHES.append(
                box(
                    lane_x1,
                    lane_y1,
                    FLOOR_Z2,
                    lane_x2,
                    lane_y2,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.ROAD,
                )
            )

    _SW_SLAB_LEN = 80
    _SW_GAP = 2

    def sw_slabs_y(
        brushes,
        x1,
        x2,
        y1,
        y2,
        z_base,
        z_top,
        tex,
        tt_params="0 0 0 1 1",
        tile_overrides=None,
    ):
        """Tile a north-south sidewalk strip into panels.

        `tile_overrides` swaps textures for specific panel starts, and seamless
        textures are merged into continuous runs.
        """
        _seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
        step = _SW_SLAB_LEN + _SW_GAP
        segments = []
        y = y1
        while y < y2:
            sy2 = min(y + _SW_SLAB_LEN, y2)
            panel_tex = tex
            if tile_overrides:
                for oy, otex in tile_overrides:
                    if abs(oy - y) < 1:
                        panel_tex = otex
                        break
            if segments and segments[-1][2] == panel_tex and panel_tex in _seamless_tex:
                segments[-1][1] = sy2
            else:
                segments.append([y, sy2, panel_tex])
            y += step
        for seg_y1, seg_y2, panel_tex in segments:
            brushes.append(
                box(
                    x1,
                    seg_y1,
                    z_base,
                    x2,
                    seg_y2,
                    z_top,
                    panel_tex,
                    tt_params=tt_params,
                )
            )

    def sw_slabs_x(
        brushes,
        x1,
        x2,
        y1,
        y2,
        z_base,
        z_top,
        tex,
        tt_params="0 0 0 1 1",
        tex_from_x=None,
        tex_ranges=None,
    ):
        """Tile an east-west sidewalk strip into panels.

        `tex_from_x` and `tex_ranges` override textures by position, and
        seamless textures are merged into continuous runs.
        """
        _seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
        step = _SW_SLAB_LEN + _SW_GAP
        segments = []
        x = x1
        while x < x2:
            sx2 = min(x + _SW_SLAB_LEN, x2)
            panel_tex = tex
            if tex_from_x is not None and x >= tex_from_x[0]:
                panel_tex = tex_from_x[1]
            pieces = [[x, sx2, panel_tex, tt_params, None]]
            if tex_ranges:
                for rspec in tex_ranges:
                    rx1, rx2, rtex = rspec[0], rspec[1], rspec[2]
                    rparams = rspec[3] if len(rspec) > 3 else tt_params
                    r_inset = rspec[4] if len(rspec) > 4 else None
                    new_pieces = []
                    for px1, px2, ptex, pparams, pinset in pieces:
                        ox1, ox2 = max(px1, rx1), min(px2, rx2)
                        if ox1 >= ox2:
                            new_pieces.append([px1, px2, ptex, pparams, pinset])
                            continue
                        if px1 < ox1:
                            new_pieces.append([px1, ox1, ptex, pparams, pinset])
                        new_pieces.append([ox1, ox2, rtex, rparams, r_inset])
                        if ox2 < px2:
                            new_pieces.append([ox2, px2, ptex, pparams, pinset])
                    pieces = new_pieces
            for px1, px2, ptex, pparams, pinset in pieces:
                if (
                    segments
                    and segments[-1][2] == ptex
                    and segments[-1][3] == pparams
                    and segments[-1][4] == pinset
                    and ptex in _seamless_tex
                ):
                    segments[-1][1] = px2
                else:
                    segments.append([px1, px2, ptex, pparams, pinset])
            x += step
        for seg_x1, seg_x2, panel_tex, panel_params, y_north_inset in segments:
            seg_y2 = y2 - y_north_inset if y_north_inset else y2
            brushes.append(
                box(
                    seg_x1,
                    y1,
                    z_base,
                    seg_x2,
                    seg_y2,
                    z_top,
                    panel_tex,
                    tt_params=panel_params,
                )
            )
            if y_north_inset:
                brushes.append(
                    box(
                        seg_x1,
                        seg_y2,
                        z_base,
                        seg_x2,
                        y2,
                        z_top,
                        tex,
                        tt_params=tt_params,
                    )
                )

    CHARLES_CURB_CUT_LEN = 2 * (_SW_SLAB_LEN + _SW_GAP)
    CHARLES_CURB_CUT_Y2 = CHARLES_CROSSING_MID + CHARLES_CURB_CUT_LEN
    CHARLES_CURB_RAMP_Y2 = CHARLES_CURB_CUT_Y2 + _SW_SLAB_LEN
    sw_slabs_y(
        BRUSHES,
        ROAD_X1 - CHARLES_WALK_W,
        ROAD_X1,
        CHARLES_CROSSING_MID,
        CHARLES_CURB_CUT_Y2,
        FLOOR_Z2,
        FLOOR_Z2 + STREET_SURFACE_T,
        Textures.SIDEWALK,
    )
    BRUSHES.append(
        ramp_slab_y(
            ROAD_X1 - CHARLES_WALK_W,
            ROAD_X1,
            CHARLES_CURB_CUT_Y2,
            CHARLES_CURB_RAMP_Y2,
            FLOOR_Z2,
            FLOOR_Z2,
            FLOOR_Z2 + STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    _CHARLES_CURB_CAP_D = 8
    _CHARLES_CURB_GAP = 2
    sw_slabs_y(
        BRUSHES,
        ROAD_X1 - CHARLES_WALK_W,
        ROAD_X1 - _CHARLES_CURB_CAP_D - _CHARLES_CURB_GAP,
        CHARLES_CURB_RAMP_Y2 + _SW_GAP,
        CHARLES_Y2,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK,
    )
    BRUSHES.append(
        box(
            ROAD_X1 - _CHARLES_CURB_CAP_D - _CHARLES_CURB_GAP,
            CHARLES_CURB_RAMP_Y2 + _SW_GAP,
            FLOOR_Z2,
            ROAD_X1 - _CHARLES_CURB_CAP_D,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.SIDEWALK,
        )
    )
    BRUSHES.append(
        box(
            ROAD_X1 - _CHARLES_CURB_CAP_D,
            CHARLES_CURB_RAMP_Y2 + _SW_GAP,
            FLOOR_Z2 + STREET_SURFACE_T,
            ROAD_X1,
            CHARLES_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    BRUSHES.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_CROSSING_MID,
            FLOOR_Z2 + STREET_SURFACE_T,
            ROAD_X1,
            CHARLES_CROSSING_MID + 4,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    _RW_X2 = ROAD_X1 - CHARLES_WALK_W
    _RW_X1 = _RW_X2 - STREET_CHARLES_CURB_W
    BRUSHES.append(
        box(
            _RW_X1,
            CHARLES_CROSSING_MID,
            FLOOR_Z2 + STREET_SURFACE_T,
            _RW_X2,
            CHARLES_CURB_CUT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    BRUSHES.append(
        ramp_slab_y(
            _RW_X1,
            _RW_X2,
            CHARLES_CURB_CUT_Y2,
            CHARLES_CURB_RAMP_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H - STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    BRUSHES.append(
        box(
            ROAD_X1 - STREET_CHARLES_CURB_W,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X1,
            CHARLES_CROSSING_MID,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    BRUSHES.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X1 - STREET_CHARLES_CURB_W,
            CHARLES_CROSSING_MID,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    for _seg_y1, _seg_y2, _seg_overrides in (
        (
            CHARLES_Y1,
            ENNIS_Y - ENNIS_HW - CHARLES_WALK_W,
            [(508, Textures.WHITE_STONE)],
        ),
        (ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W, CHARLES_Y2, None),
    ):
        sw_slabs_y(
            BRUSHES,
            ROAD_X2 + _CHARLES_CURB_CAP_D + _CHARLES_CURB_GAP,
            ROAD_X2 + CHARLES_WALK_W,
            _seg_y1,
            _seg_y2,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tile_overrides=_seg_overrides,
        )
        BRUSHES.append(
            box(
                ROAD_X2 + _CHARLES_CURB_CAP_D,
                _seg_y1,
                FLOOR_Z2,
                ROAD_X2 + _CHARLES_CURB_CAP_D + _CHARLES_CURB_GAP,
                _seg_y2,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.SIDEWALK,
            )
        )
        BRUSHES.append(
            box(
                ROAD_X2,
                _seg_y1,
                FLOOR_Z2 + STREET_SURFACE_T,
                ROAD_X2 + _CHARLES_CURB_CAP_D,
                _seg_y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )

    ENNIS_ROAD_TT_PARAMS = "0 0 90 1 1"
    _ennis_center_y = ENNIS_Y + ENNIS_WIDEN_N / 2 + ENNIS_DIVIDER_EXTRA_N
    for wx1, wx2 in ranges_excluding(
        ENNIS_X1, ROAD_X2 + CHARLES_WALK_W, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
    ):
        BRUSHES.append(
            box(
                wx1,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2,
                wx2,
                _ennis_center_y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
    for road_x1, road_x2 in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2),
    ]:
        BRUSHES.append(
            box(
                road_x1,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2,
                road_x2,
                _ennis_center_y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_CORRIDOR_X1,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_CORRIDOR_X2,
            _ennis_center_y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    for nx1, nx2 in ranges_excluding(
        ENNIS_X1, ENNIS_X2, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
    ):
        BRUSHES.append(
            box(
                nx1,
                _ennis_center_y + STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                nx2,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
    _ENNIS_CURB_CAP_D = 8
    _ENNIS_CURB_GAP = 2
    _ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    _bw_cx = _ennis_wall_x1 + ENNIS_WALL_T // 2
    sw_slabs_x(
        BRUSHES,
        ROAD_X2 + CHARLES_WALK_W,
        ENNIS_X2,
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP,
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK,
        tt_params=ENNIS_ROAD_TT_PARAMS,
        tex_ranges=[
            (
                _bw_cx - ENNIS_WALL_PILLAR_HW + 4,
                ENNIS_PILLAR_X1,
                Textures.WHITE_STONE,
                ENNIS_ROAD_TT_PARAMS,
            ),
            (ENNIS_PILLAR_X1, ENNIS_GATE_X2, Textures.MULCH),
            (ENNIS_GATE_X2, ENNIS_X2, Textures.GROUND),
        ],
    )
    _CURB_BULGE_X1 = ENNIS_CEMENT_X2
    _CURB_BULGE_LEN = ENNIS_CURB_BULGE_LEN
    _CURB_BULGE_X2 = _CURB_BULGE_X1 + _CURB_BULGE_LEN
    BRUSHES.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
            FLOOR_Z2,
            _CURB_BULGE_X1,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    BRUSHES.append(
        box(
            _CURB_BULGE_X2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    _CURB_BULGE_HALF_LEN = _CURB_BULGE_LEN / 2
    _CURB_BULGE_DEPTH = _CURB_BULGE_HALF_LEN / 2
    _CURB_BULGE_CX = (_CURB_BULGE_X1 + _CURB_BULGE_X2) / 2
    _CURB_BULGE_SEGMENTS = 24
    _CURB_BULGE_FAR_Y = (
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP
    )
    BRUSHES.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
            FLOOR_Z2 + STREET_SURFACE_T,
            _CURB_BULGE_X1,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    _bulge_step = _CURB_BULGE_LEN / _CURB_BULGE_SEGMENTS

    def _bulge_depth_at(bx):
        bdx = bx - _CURB_BULGE_CX
        _t = max(1 - (bdx / _CURB_BULGE_HALF_LEN) ** 2, 0)
        return _CURB_BULGE_DEPTH * math.sqrt(_t)

    for _bi in range(_CURB_BULGE_SEGMENTS):
        _bx1 = _CURB_BULGE_X1 + _bi * _bulge_step
        _bx2 = _bx1 + _bulge_step
        _bd1 = _bulge_depth_at(_bx1)
        _bd2 = _bulge_depth_at(_bx2)
        _outer1_y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - _bd1
        _outer2_y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - _bd2
        _inner1_y = _outer1_y + _ENNIS_CURB_CAP_D
        _inner2_y = _outer2_y + _ENNIS_CURB_CAP_D
        _z1, _z2 = FLOOR_Z2 + STREET_SURFACE_T, FLOOR_Z2 + CHARLES_WALK_H
        BRUSHES.append(
            tri_prism(
                _bx1,
                _outer1_y,
                _bx2,
                _outer2_y,
                _bx2,
                _inner2_y,
                _z1,
                _z2,
                Textures.SIDEWALK,
            )
        )
        BRUSHES.append(
            tri_prism(
                _bx1,
                _outer1_y,
                _bx2,
                _inner2_y,
                _bx1,
                _inner1_y,
                _z1,
                _z2,
                Textures.SIDEWALK,
            )
        )
        if _bd1 > 0 or _bd2 > 0:
            BRUSHES.append(
                tri_prism(
                    _bx1,
                    _inner1_y,
                    _bx2,
                    _inner2_y,
                    _bx2,
                    _CURB_BULGE_FAR_Y,
                    FLOOR_Z2,
                    _z2,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_prism(
                    _bx1,
                    _inner1_y,
                    _bx2,
                    _CURB_BULGE_FAR_Y,
                    _bx1,
                    _CURB_BULGE_FAR_Y,
                    FLOOR_Z2,
                    _z2,
                    Textures.GROUND,
                )
            )
    BRUSHES.append(
        box(
            _CURB_BULGE_X2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
            FLOOR_Z2 + STREET_SURFACE_T,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    _west_curb_x1 = ROAD_X2 + CHARLES_WALK_W
    _west_sw_d = CHARLES_WALK_W * 2 + 56
    _west_y1 = ENNIS_SW_EDGE + CHARLES_WALK_W - _west_sw_d
    _west_y2 = ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D - _ENNIS_CURB_GAP
    _west_north_y1 = _west_y2 - _SW_SLAB_LEN
    BRUSHES.append(
        box(
            _west_curb_x1,
            _west_y1,
            FLOOR_Z2,
            _west_curb_x1 + _SW_SLAB_LEN,
            _west_north_y1,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.WHITE_STONE,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    BRUSHES.append(
        box(
            _west_curb_x1,
            _west_north_y1,
            FLOOR_Z2,
            _west_curb_x1 + _SW_SLAB_LEN,
            _west_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    for curb_x1, curb_x2, _sw_d, _tile_x1, _tex_from_x in (
        (
            _west_curb_x1,
            KNOTT_DRIVEWAY_WS_X1,
            CHARLES_WALK_W * 2 + 56,
            _west_curb_x1 + _SW_SLAB_LEN + _SW_GAP,
            (_west_curb_x1 + _SW_SLAB_LEN + _SW_GAP, Textures.WHITE_STONE),
        ),
        (
            KNOTT_DRIVEWAY_ES_X2,
            ENNIS_X2,
            CHARLES_WALK_W,
            KNOTT_DRIVEWAY_ES_X2,
            None,
        ),
    ):
        sw_slabs_x(
            BRUSHES,
            _tile_x1,
            curb_x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W - _sw_d,
            ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D - _ENNIS_CURB_GAP,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
            tex_from_x=_tex_from_x,
        )
        BRUSHES.append(
            box(
                curb_x1,
                ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D - _ENNIS_CURB_GAP,
                FLOOR_Z2,
                curb_x2,
                ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.SIDEWALK,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        BRUSHES.append(
            box(
                curb_x1,
                ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D,
                FLOOR_Z2 + STREET_SURFACE_T,
                curb_x2,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )

    dash_brushes = []
    _centerline_gap_hw = 2
    for line_x1, line_x2 in (
        (ROAD_CX - STREET_DIV_HW, ROAD_CX - _centerline_gap_hw),
        (ROAD_CX + _centerline_gap_hw, ROAD_CX + STREET_DIV_HW),
    ):
        for line_y1, line_y2 in ranges_excluding(
            CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
        ):
            dash_brushes.append(
                box(
                    line_x1,
                    line_y1,
                    FLOOR_Z2,
                    line_x2,
                    line_y2,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.CENTERLINE,
                )
            )
    for gap_y1, gap_y2 in ranges_excluding(
        CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
    ):
        dash_brushes.append(
            box(
                ROAD_CX - _centerline_gap_hw,
                gap_y1,
                FLOOR_Z2,
                ROAD_CX + _centerline_gap_hw,
                gap_y2,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
            )
        )
    for lane_line_x in (WEST_LANE_LINE_X, EAST_LANE_LINE_X):
        tex_offset_x = WEST_LANE_LINE_X - lane_line_x
        divider_tt_params = f"{tex_offset_x} 0 0 1 1"
        for seg_y1, seg_y2 in ranges_excluding(
            CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
        ):
            dash_brushes.append(
                box(
                    lane_line_x - STREET_DIV_LINE_HW,
                    seg_y1,
                    FLOOR_Z2,
                    lane_line_x + STREET_DIV_LINE_HW,
                    seg_y2,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.PARKING_STRIPE,
                    tt_params=divider_tt_params,
                )
            )
    _cx = ROAD_X1
    _stripe_on = True
    while _cx < ROAD_X2:
        next_cx = min(
            _cx + (CROSSWALK_STRIPE_W if _stripe_on else CROSSWALK_GAP_W), ROAD_X2
        )
        dash_brushes.append(
            box(
                _cx,
                CHARLES_CROSSING_Y1,
                FLOOR_Z2,
                next_cx,
                CHARLES_CROSSING_Y2,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.PARKING_STRIPE if _stripe_on else Textures.ROAD,
            )
        )
        _cx = next_cx
        _stripe_on = not _stripe_on
    _ennis_line_hw = STREET_DIV_LINE_HW
    _ennis_line_x1 = ENNIS_PILLAR_X1 + ENNIS_PILLAR_HW
    for gx1, gx2 in ranges_excluding(
        ROAD_X2, _ennis_line_x1, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
    ):
        dash_brushes.append(
            box(
                gx1,
                _ennis_center_y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                gx2,
                _ennis_center_y + STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
    dash_brushes.append(
        box(
            _ennis_line_x1,
            _ennis_center_y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2,
            ENNIS_X2,
            _ennis_center_y - _ennis_line_hw,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    dash_brushes.append(
        box(
            _ennis_line_x1,
            _ennis_center_y - _ennis_line_hw,
            FLOOR_Z2,
            ENNIS_X2,
            _ennis_center_y + _ennis_line_hw,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.CENTERLINE,
        )
    )
    dash_brushes.append(
        box(
            _ennis_line_x1,
            _ennis_center_y + _ennis_line_hw,
            FLOOR_Z2,
            ENNIS_X2,
            _ennis_center_y + STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    _ey = ENNIS_Y - ENNIS_HW
    _ennis_crossing_y2 = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N
    _stripe_on = True
    while _ey < _ennis_crossing_y2:
        next_ey = min(
            _ey + (CROSSWALK_STRIPE_W if _stripe_on else CROSSWALK_GAP_W),
            _ennis_crossing_y2,
        )
        dash_brushes.append(
            box(
                ENNIS_CROSSING_X1,
                _ey,
                FLOOR_Z2,
                ENNIS_CROSSING_X2,
                next_ey,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.PARKING_STRIPE if _stripe_on else Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS if not _stripe_on else "0 0 0 1 1",
            )
        )
        _ey = next_ey
        _stripe_on = not _stripe_on
    if dash_brushes:
        ENTITIES.append(brush_ent("func_detail", punch_manhole_detail(dash_brushes)))

    cx_se = ROAD_X2 + CHARLES_CRN_R
    cy_se = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
    BRUSHES.append(
        box(
            ROAD_X2,
            cy_se,
            FLOOR_Z2,
            cx_se,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    for corner_index in range(CHARLES_CRN_SEGS):
        angle_start = math.radians(90 + corner_index * 90 / CHARLES_CRN_SEGS)
        angle_end = math.radians(90 + (corner_index + 1) * 90 / CHARLES_CRN_SEGS)
        arc_x0, arc_y0 = (
            cx_se + CHARLES_CRN_R * math.cos(angle_start),
            cy_se + CHARLES_CRN_R * math.sin(angle_start),
        )
        arc_x1, arc_y1 = (
            cx_se + CHARLES_CRN_R * math.cos(angle_end),
            cy_se + CHARLES_CRN_R * math.sin(angle_end),
        )
        BRUSHES.append(
            tri_prism(
                cx_se,
                cy_se,
                arc_x0,
                arc_y0,
                arc_x1,
                arc_y1,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )

    cx_ne = ROAD_X2 + CHARLES_CRN_R
    cy_ne = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_CRN_R
    BRUSHES.append(
        box(
            ROAD_X2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
            FLOOR_Z2,
            cx_ne,
            cy_ne,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    for corner_index in range(CHARLES_CRN_SEGS):
        angle_start = math.radians(180 + corner_index * 90 / CHARLES_CRN_SEGS)
        angle_end = math.radians(180 + (corner_index + 1) * 90 / CHARLES_CRN_SEGS)
        arc_x0, arc_y0 = (
            cx_ne + CHARLES_CRN_R * math.cos(angle_start),
            cy_ne + CHARLES_CRN_R * math.sin(angle_start),
        )
        arc_x1, arc_y1 = (
            cx_ne + CHARLES_CRN_R * math.cos(angle_end),
            cy_ne + CHARLES_CRN_R * math.sin(angle_end),
        )
        BRUSHES.append(
            tri_prism(
                cx_ne,
                cy_ne,
                arc_x0,
                arc_y0,
                arc_x1,
                arc_y1,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )

    _west_verge_x1 = (
        ROAD_X1 - CHARLES_WALK_W - CHARLES_RAMP_W
        if WEST_CAMPUS_ENABLED_TERRAIN
        else WORLD_X1 + WALL_T
    )
    _east_verge_x2 = WORLD_X2_EXT - WALL_T
    BRUSHES.append(
        box(
            _west_verge_x1,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    _west_verge_y2 = ENNIS_SW_EDGE - CHARLES_WALK_W
    _east_verge_segs = (
        [
            (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, _west_verge_y2),
            (KNOTT_DRIVEWAY_CORRIDOR_X2, _east_verge_x2, ENNIS_SW_EDGE),
        ]
        if KNOTT_ENABLED_TERRAIN
        else [
            (ROAD_X2 + CHARLES_WALK_W, KNOTT.x2, _west_verge_y2),
            (KNOTT.x2, _east_verge_x2, ENNIS_SW_EDGE),
        ]
    )
    for _evx1, _evx2, _evy2 in _east_verge_segs:
        BRUSHES.append(
            box(
                _evx1,
                CHARLES_Y1,
                FLOOR_Z2,
                _evx2,
                _evy2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
    if not NE_ENABLED_TERRAIN:
        BRUSHES.append(
            box(
                ROAD_X2 + CHARLES_WALK_W,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
                FLOOR_Z2,
                ENNIS_X2,
                CHARLES_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )

    _VERGE_CEMENT_X1 = ROAD_X2 + CHARLES_WALK_W
    _VERGE_CEMENT_X2 = _VERGE_CEMENT_X1 + _SW_SLAB_LEN
    for vx1, vx2, vtex in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, Textures.GROUND),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2, Textures.MULCH),
    ]:
        vy1 = ENNIS_SW_EDGE + CHARLES_WALK_W
        vy2 = ENNIS_Y - ENNIS_HW - ENNIS_CURB_W
        if vtex is Textures.GROUND:
            BRUSHES.append(
                box(
                    _VERGE_CEMENT_X1,
                    vy1,
                    FLOOR_Z1,
                    _VERGE_CEMENT_X2,
                    vy2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )
            BRUSHES.append(
                box(
                    _VERGE_CEMENT_X2,
                    vy1,
                    FLOOR_Z1,
                    vx2,
                    vy2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    vtex,
                )
            )
        else:
            BRUSHES.append(
                box(
                    vx1,
                    vy1,
                    FLOOR_Z1,
                    vx2,
                    vy2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    vtex,
                )
            )

    for vx1, vx2 in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2),
    ]:
        BRUSHES.append(
            box(
                vx1,
                ENNIS_Y - ENNIS_HW - ENNIS_CURB_W,
                FLOOR_Z1,
                vx2,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )

    if not KNOTT_ENABLED_TERRAIN:
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_WS_X1,
                ENNIS_SW_EDGE,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_WS_X2,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_RD_X1,
                ENNIS_SW_EDGE,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_RD_X2,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2 + 2,
                Textures.ROAD,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_ES_X1,
                ENNIS_SW_EDGE,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_ES_X2,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_WS_X1,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_WS_X2,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_ES_X2,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.MULCH,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_ES_X1,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_RD_X1,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_RD_X2,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2 + 2,
                Textures.ROAD,
            )
        )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_WS_X1,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_RD_X1,
                KNOTT_DRIVEWAY_JCY,
                FLOOR_Z2 + 2,
                Textures.ROAD,
            )
        )
        _r_outer = KNOTT_DRIVEWAY_CURB_CRN_R
        _r_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
        _seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
        for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
            a0 = corner_index * _seg_deg
            a1 = (corner_index + 1) * _seg_deg
            t0, t1 = math.radians(a0), math.radians(a1)
            BRUSHES.append(
                tri_prism(
                    KNOTT_DRIVEWAY_JCX_X1,
                    KNOTT_DRIVEWAY_EXT_Y2,
                    KNOTT_DRIVEWAY_JCX_X1 + _r_inner * math.cos(t0),
                    KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t0),
                    KNOTT_DRIVEWAY_JCX_X1 + _r_inner * math.cos(t1),
                    KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t1),
                    FLOOR_Z2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                curb_seg(
                    KNOTT_DRIVEWAY_JCX_X1,
                    KNOTT_DRIVEWAY_EXT_Y2,
                    FLOOR_Z2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    _r_inner,
                    _r_outer,
                    a0,
                    a1,
                    Textures.CEMENT,
                )
            )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_ES_X1,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_ES_X2,
                KNOTT_DRIVEWAY_JCY,
                FLOOR_Z2 + 2,
                Textures.ROAD,
            )
        )
        for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
            ea0 = 90 + corner_index * _seg_deg
            ea1 = 90 + (corner_index + 1) * _seg_deg
            t0, t1 = math.radians(ea0), math.radians(ea1)
            BRUSHES.append(
                tri_prism(
                    KNOTT_DRIVEWAY_JCX_E,
                    KNOTT_DRIVEWAY_EXT_Y2,
                    KNOTT_DRIVEWAY_JCX_E + _r_inner * math.cos(t0),
                    KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t0),
                    KNOTT_DRIVEWAY_JCX_E + _r_inner * math.cos(t1),
                    KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t1),
                    FLOOR_Z2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.MULCH,
                )
            )
            BRUSHES.append(
                curb_seg(
                    KNOTT_DRIVEWAY_JCX_E,
                    KNOTT_DRIVEWAY_EXT_Y2,
                    FLOOR_Z2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    _r_inner,
                    _r_outer,
                    ea0,
                    ea1,
                    Textures.CEMENT,
                )
            )

    ennis_brushes, ennis_entities = build_ennis_entrance_features()
    BRUSHES.extend(ennis_brushes)
    ENTITIES.extend(ennis_entities)

    BRUSHES = _world_brushes

    for lamp_x in CHARLES_LAMP_POST_XS:
        for lamp_y in CHARLES_LAMP_POST_YS:
            pole_top_z = FLOOR_Z2 + CHARLES_LAMP_POST_H
            DETAIL_BRUSHES.append(
                box(
                    lamp_x - 2,
                    lamp_y - 2,
                    FLOOR_Z2,
                    lamp_x + 2,
                    lamp_y + 2,
                    pole_top_z,
                    Textures.PILLAR,
                )
            )
            DETAIL_BRUSHES.append(
                box(
                    lamp_x - 3,
                    lamp_y - 3,
                    pole_top_z,
                    lamp_x + 3,
                    lamp_y + 3,
                    pole_top_z + 16,
                    Textures.CEMENT,
                )
            )
            DETAIL_BRUSHES.append(
                box(
                    lamp_x - 5,
                    lamp_y - 5,
                    pole_top_z + 16,
                    lamp_x + 5,
                    lamp_y + 5,
                    pole_top_z + 20,
                    Textures.BRICK,
                )
            )
            flame_z = pole_top_z + 20
            ENTITIES.extend(torch_flame(lamp_x, lamp_y, flame_z))

    if DETAIL_BRUSHES:
        DETAIL_BRUSHES = punch_manhole_detail(DETAIL_BRUSHES)
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    seal_x1, seal_x2 = WORLD_X1 - 256, WORLD_X2_EXT + 256
    seal_y1, seal_y2 = WORLD_Y1 - 256, WORLD_Y2 + 256
    seal_z1, seal_z2 = BASEMENT_FLOOR_Z1 - 256, WORLD_Z2 + 512
    ST = 64
    BRUSHES.extend(
        [
            box(
                seal_x1, seal_y1, seal_z1, seal_x2, seal_y2, seal_z1 + ST, Textures.SKY
            ),
            box(
                seal_x1, seal_y1, seal_z2 - ST, seal_x2, seal_y2, seal_z2, Textures.SKY
            ),
            box(
                seal_x1, seal_y1, seal_z1, seal_x1 + ST, seal_y2, seal_z2, Textures.SKY
            ),
            box(
                seal_x2 - ST, seal_y1, seal_z1, seal_x2, seal_y2, seal_z2, Textures.SKY
            ),
            box(
                seal_x1, seal_y1, seal_z1, seal_x2, seal_y1 + ST, seal_z2, Textures.SKY
            ),
            box(
                seal_x1, seal_y2 - ST, seal_z1, seal_x2, seal_y2, seal_z2, Textures.SKY
            ),
        ]
    )

    return BRUSHES, ENTITIES
