import math

from ..constants.derived import (
    ENNIS_CEMENT_X1,
    ENNIS_CEMENT_X2,
    ENNIS_GATE_PILLAR_W,
    ENNIS_GATE_X1,
    ENNIS_GATE_X2,
    ENNIS_PILLAR_NORTH_Y,
    ENNIS_PILLAR_SOUTH_Y,
    ENNIS_PILLAR_X1,
    ENNIS_SHORT_WALL_NY,
    ENNIS_WALL_NY,
    WALL_T,
    WORLD_X2,
    WORLD_Y2,
)
from ..constants.ennis import (
    ENNIS_CEMENT_WALL_CAP_H,
    ENNIS_CEMENT_WALL_CAP_OVH,
    ENNIS_CEMENT_WALL_H,
    ENNIS_CEMENT_WALL_LAMP_POST_H,
    ENNIS_CEMENT_WALL_PILLAR_EXTRA_H,
    ENNIS_CEMENT_WALL_PILLAR_HW,
    ENNIS_CEMENT_WALL_PILLAR_SPACING,
    ENNIS_CURB_BULGE_LEN,
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
    ENNIS_PILLAR_POST_H,
    ENNIS_SW_PANEL_OUTER_W,
    ENNIS_WALL_H,
    ENNIS_WALL_PILLAR_H,
    ENNIS_WALL_PILLAR_HW,
    ENNIS_WALL_T,
    ENNIS_WALL_X_OFFSET,
)
from ..constants.streets import (
    CHARLES_WALK_W,
    ROAD_X2,
)
from ..constants.textures import (
    Textures,
)
from ..constants.world import (
    FLOOR_Z2,
)
from ..geometry import (
    arch_seg,
    arch_seg_y,
    box,
    brush_ent,
    pyramid,
    ramp_slab,
    ramp_slab_y,
    shear_box_y,
    shear_box_z,
    torch_flame,
    tri_prism,
)
from ..utils import (
    swap_xy,
    swap_xz,
)


def _build_ennis_entrance_features():
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
    sw_panel_outer_w = ENNIS_SW_PANEL_OUTER_W
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
    while True:
        gate_picket_width = (
            ENNIS_GATE_FENCE_POST_W
            if gate_picket_index % 10 == 0
            else ENNIS_GATE_FENCE_BAR_T
        )
        if gate_picket_y + gate_picket_width > fence_end_y:
            break
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
    if cursor_y != bw_mid_y:
        raise ValueError(
            f"Ennis gate-run layout drift: cursor_y ({cursor_y}) does not "
            f"land on bw_mid_y ({bw_mid_y}) — panel/pillar/gap constants no "
            "longer sum to the expected gate-run midpoint."
        )

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
    while True:
        east_gate_picket_width = (
            ENNIS_GATE_FENCE_POST_W
            if east_gate_picket_index % 10 == 0
            else ENNIS_GATE_FENCE_BAR_T
        )
        if east_gate_picket_x + east_gate_picket_width > ENNIS_GATE_X2:
            break
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
