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


def _build_ennis_entrance_pillars(brushes, entities):
    """Build the paired freestanding gate pillars with their flame entities."""
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


def _build_ennis_gate_run(
    brushes,
    *,
    panel_outer_w,
    panel_inner_w,
    brick_top_z,
    panel_z_center,
    make_box,
    make_lower_ramp,
    make_upper_ramp,
    build_arch_legs,
    append_arch_segments,
    build_cross_braces,
    build_layout,
):
    """Build one ornamental Ennis fence run from the provided layout callbacks."""
    panel_z2_o = panel_z_center + ENNIS_PANEL_OUTER_H // 2

    def add_panel(center):
        outer_1 = center - panel_outer_w // 2
        outer_2 = center + panel_outer_w // 2
        z1_o = panel_z_center - ENNIS_PANEL_OUTER_H // 2
        z2_o = panel_z_center + ENNIS_PANEL_OUTER_H // 2
        inner_1 = center - panel_inner_w // 2
        inner_2 = center + panel_inner_w // 2
        z1_i = panel_z_center - ENNIS_PANEL_INNER_H // 2
        z2_i = panel_z_center + ENNIS_PANEL_INNER_H // 2
        brushes.extend(
            [
                make_box(outer_1, z1_o, outer_2, z1_o + ENNIS_GATE_FENCE_BAR_T),
                make_box(outer_1, z2_o - ENNIS_GATE_FENCE_BAR_T, outer_2, z2_o),
                make_box(outer_1, z1_o, outer_1 + ENNIS_GATE_FENCE_BAR_T, z2_o),
                make_box(outer_2 - ENNIS_GATE_FENCE_BAR_T, z1_o, outer_2, z2_o),
                make_box(inner_1, z1_i, inner_2, z1_i + ENNIS_GATE_FENCE_BAR_T),
                make_box(inner_1, z2_i - ENNIS_GATE_FENCE_BAR_T, inner_2, z2_i),
                make_box(inner_1, z1_i, inner_1 + ENNIS_GATE_FENCE_BAR_T, z2_i),
                make_box(inner_2 - ENNIS_GATE_FENCE_BAR_T, z1_i, inner_2, z2_i),
                make_lower_ramp(
                    outer_1,
                    inner_1,
                    z1_o,
                    z1_i,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                ),
                make_upper_ramp(
                    inner_2,
                    outer_2,
                    z1_i,
                    z1_o,
                    z1_i + ENNIS_GATE_FENCE_BAR_T,
                    z1_o + ENNIS_GATE_FENCE_BAR_T,
                ),
                make_lower_ramp(
                    outer_1,
                    inner_1,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    z2_o,
                    z2_i,
                ),
                make_upper_ramp(
                    inner_2,
                    outer_2,
                    z2_i - ENNIS_GATE_FENCE_BAR_T,
                    z2_o - ENNIS_GATE_FENCE_BAR_T,
                    z2_i,
                    z2_o,
                ),
            ]
        )
        foot_half_width = ENNIS_GATE_FENCE_BAR_T // 2
        foot_1 = outer_1 + ENNIS_PANEL_MOUNT_FOOT_INSET
        foot_2 = outer_2 - ENNIS_PANEL_MOUNT_FOOT_INSET
        brushes.extend(
            [
                make_box(
                    foot_1 - foot_half_width,
                    z1_o - ENNIS_PANEL_MOUNT_FOOT_DROP,
                    foot_1 + foot_half_width,
                    z1_o,
                ),
                make_box(
                    foot_2 - foot_half_width,
                    z1_o - ENNIS_PANEL_MOUNT_FOOT_DROP,
                    foot_2 + foot_half_width,
                    z1_o,
                ),
            ]
        )

    def add_connector(start, end):
        if end <= start:
            return
        bar_t = ENNIS_GATE_FENCE_BAR_T
        quarter_h = ENNIS_PANEL_OUTER_H // 4
        upper_z1 = panel_z_center + quarter_h - bar_t // 2
        lower_z1 = panel_z_center - quarter_h - bar_t // 2
        brushes.extend(
            [
                make_box(start, upper_z1, end, upper_z1 + bar_t),
                make_box(start, lower_z1, end, lower_z1 + bar_t),
            ]
        )

    def add_arch_post(center):
        leg_t = ENNIS_GATE_PILLAR_LEG_T
        arch_rin = ENNIS_GATE_PILLAR_OPENING_W // 2
        arch_rout = arch_rin + leg_t
        post_top_z = panel_z2_o + ENNIS_GATE_PILLAR_EXTRA_H
        legs_top_z = post_top_z - arch_rout
        brushes.extend(build_arch_legs(center, arch_rout, leg_t, legs_top_z))
        append_arch_segments(center, legs_top_z, arch_rin, arch_rout)
        cross_hw = ENNIS_GATE_PILLAR_CROSS_T // 2
        brushes.extend(
            build_cross_braces(center, arch_rin, brick_top_z, legs_top_z, cross_hw)
        )

    build_layout(add_panel, add_connector, add_arch_post)


def _build_ennis_short_wall_gate_layout(
    add_panel,
    add_connector,
    add_arch_post,
    *,
    sw_arch_post_lead_x,
    sw_panel_count,
    sw_run_x1,
    sw_run_w,
    sw_panel_outer_w,
):
    """Lay out the ornamental fence panels that sit atop the short wall."""
    add_arch_post(sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W // 2)
    add_connector(
        sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W,
        sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W + ENNIS_GATE_PILLAR_GAP,
    )
    for i in range(sw_panel_count):
        panel_center_x = (
            sw_run_x1 + i * (sw_panel_outer_w + ENNIS_PANEL_GAP) + sw_panel_outer_w // 2
        )
        add_panel(panel_center_x)
        if i > 0:
            add_connector(
                panel_center_x - sw_panel_outer_w // 2 - ENNIS_PANEL_GAP,
                panel_center_x - sw_panel_outer_w // 2,
            )
    sw_trailing_gap_x1 = sw_run_x1 + sw_run_w
    sw_trailing_gap_x2 = sw_trailing_gap_x1 + ENNIS_GATE_PILLAR_GAP
    add_connector(sw_trailing_gap_x1, sw_trailing_gap_x2)
    add_arch_post(sw_trailing_gap_x2 + ENNIS_GATE_PILLAR_W // 2)


def _build_ennis_short_wall_bridge_fence(brushes, bwex2):
    """Build the short vertical fence bridge linking the wall and east gate."""
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


def _build_ennis_short_wall_section(brushes, ennis_wall_x1, bwex2, sw_tex):
    """Build the short masonry wall and its attached ornamental fence run."""
    sw_arch_post_lead_x = (
        ennis_wall_x1 + ENNIS_WALL_T // 2 + ENNIS_WALL_PILLAR_HW + ENNIS_GATE_PILLAR_GAP
    )
    sw_panel_count = 3
    sw_panel_outer_w = ENNIS_SW_PANEL_OUTER_W
    sw_run_w = (
        sw_panel_count * sw_panel_outer_w + (sw_panel_count - 1) * ENNIS_PANEL_GAP
    )
    sw_run_x1 = sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W + ENNIS_GATE_PILLAR_GAP
    # The trailing arch post (the fence run's true east end) can sit east of
    # bwex2 — extend the brick wall to meet it so the fence isn't left
    # floating over an unbuilt gap with no brick underneath.
    sw_trailing_gap_x2 = sw_run_x1 + sw_run_w + ENNIS_GATE_PILLAR_GAP
    sw_last_post_x2 = (
        sw_trailing_gap_x2 + ENNIS_GATE_PILLAR_W // 2 + ENNIS_GATE_PILLAR_W // 2
    )
    wall_x2 = max(bwex2, sw_last_post_x2)
    brushes.append(
        box(
            ennis_wall_x1,
            ENNIS_SHORT_WALL_NY,
            FLOOR_Z2,
            wall_x2,
            ENNIS_SHORT_WALL_NY + ENNIS_WALL_T,
            FLOOR_Z2 + ENNIS_WALL_H,
            Textures.BUILDING,
        )
    )

    sw_brick_top_z = FLOOR_Z2 + ENNIS_WALL_H
    sw_panel_y1 = ENNIS_SHORT_WALL_NY - ENNIS_GATE_FENCE_BAR_T
    sw_panel_y2 = ENNIS_SHORT_WALL_NY
    sw_panel_z1 = sw_brick_top_z + ENNIS_PANEL_MOUNT_FOOT_DROP
    sw_panel_z_center = sw_panel_z1 + ENNIS_PANEL_OUTER_H // 2
    _sw_frame_t = (ENNIS_PANEL_OUTER_W - ENNIS_PANEL_INNER_W) // 2
    sw_panel_inner_w = sw_panel_outer_w - 2 * _sw_frame_t

    _build_ennis_gate_run(
        brushes,
        panel_outer_w=sw_panel_outer_w,
        panel_inner_w=sw_panel_inner_w,
        brick_top_z=sw_brick_top_z,
        panel_z_center=sw_panel_z_center,
        make_box=lambda x1, z1, x2, z2: box(
            x1, sw_panel_y1, z1, x2, sw_panel_y2, z2, sw_tex
        ),
        make_lower_ramp=lambda x1, x2, z1a, z1b, z2a, z2b: ramp_slab(
            x1, x2, sw_panel_y1, sw_panel_y2, z1a, z1b, z2a, z2b, sw_tex
        ),
        make_upper_ramp=lambda x1, x2, z1a, z1b, z2a, z2b: ramp_slab(
            x1, x2, sw_panel_y1, sw_panel_y2, z1a, z1b, z2a, z2b, sw_tex
        ),
        build_arch_legs=lambda center_x, arch_rout, leg_t, legs_top_z: [
            box(
                center_x - arch_rout,
                sw_panel_y1,
                sw_brick_top_z,
                center_x - arch_rout + leg_t,
                sw_panel_y2,
                legs_top_z,
                sw_tex,
            ),
            box(
                center_x + arch_rout - leg_t,
                sw_panel_y1,
                sw_brick_top_z,
                center_x + arch_rout,
                sw_panel_y2,
                legs_top_z,
                sw_tex,
            ),
        ],
        append_arch_segments=lambda center_x, legs_top_z, arch_rin, arch_rout: (
            brushes.extend(
                [
                    arch_seg_y(
                        sw_panel_y1,
                        sw_panel_y2,
                        center_x,
                        legs_top_z,
                        arch_rin,
                        arch_rout,
                        seg_i * (180.0 / 8),
                        (seg_i + 1) * (180.0 / 8),
                        sw_tex,
                    )
                    for seg_i in range(8)
                ]
            )
        ),
        build_cross_braces=lambda center_x, arch_rin, z1, z2, cross_hw: [
            swap_xy(
                swap_xz(
                    shear_box_y(
                        z1,
                        -cross_hw,
                        sw_panel_y1,
                        z2,
                        cross_hw,
                        sw_panel_y2,
                        center_x - arch_rin,
                        center_x + arch_rin,
                        sw_tex,
                    )
                )
            ),
            swap_xy(
                swap_xz(
                    shear_box_y(
                        z1,
                        -cross_hw,
                        sw_panel_y1,
                        z2,
                        cross_hw,
                        sw_panel_y2,
                        center_x + arch_rin,
                        center_x - arch_rin,
                        sw_tex,
                    )
                )
            ),
        ],
        build_layout=lambda add_panel, add_connector, add_arch_post: (
            _build_ennis_short_wall_gate_layout(
                add_panel,
                add_connector,
                add_arch_post,
                sw_arch_post_lead_x=sw_arch_post_lead_x,
                sw_panel_count=sw_panel_count,
                sw_run_x1=sw_run_x1,
                sw_run_w=sw_run_w,
                sw_panel_outer_w=sw_panel_outer_w,
            )
        ),
    )
    _build_ennis_short_wall_bridge_fence(brushes, wall_x2)


def _build_ennis_main_gate_layout(
    add_panel,
    add_connector,
    add_arch_post,
    *,
    gate_run_start_y,
    pair_count,
    bw_mid_y,
):
    """Lay out the main north-south Ennis gate run without altering brush order."""
    cursor_y = gate_run_start_y
    add_arch_post(cursor_y + ENNIS_GATE_PILLAR_W // 2)
    cursor_y += ENNIS_GATE_PILLAR_W
    gap_y1 = cursor_y
    cursor_y += ENNIS_GATE_PILLAR_GAP
    add_connector(gap_y1, cursor_y)
    for pair_i in range(pair_count):
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
        if pair_i < pair_count - 1:
            add_connector(gap_y1, cursor_y)
    if cursor_y != bw_mid_y:
        raise ValueError(
            f"Ennis gate-run layout drift: cursor_y ({cursor_y}) does not "
            f"land on bw_mid_y ({bw_mid_y}) — panel/pillar/gap constants no "
            "longer sum to the expected gate-run midpoint."
        )


def _build_ennis_main_fence_run(brushes, ennis_wall_x1, bw_mid_y, gate_fence_tex):
    """Build the plain fence run and connector that continue north of the gate."""
    gate_fence_x1 = ennis_wall_x1 + ENNIS_WALL_T // 2 - 1 - ENNIS_GATE_FENCE_WEST_SHIFT
    gate_fence_x2 = gate_fence_x1 + ENNIS_GATE_FENCE_BAR_T
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


def _build_ennis_main_gate_section(brushes, ennis_wall_x1, gate_fence_tex):
    """Build the long masonry wall, plain fence run, and main ornamental gate."""
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

    _build_ennis_main_fence_run(brushes, ennis_wall_x1, bw_mid_y, gate_fence_tex)

    panel_x1 = ennis_wall_x1 - ENNIS_GATE_FENCE_BAR_T
    panel_x2 = ennis_wall_x1
    brick_top_z = FLOOR_Z2 + ENNIS_WALL_H
    panel_z1 = brick_top_z + ENNIS_PANEL_MOUNT_FOOT_DROP
    panel_z_center = panel_z1 + ENNIS_PANEL_OUTER_H // 2

    _build_ennis_gate_run(
        brushes,
        panel_outer_w=ENNIS_PANEL_OUTER_W,
        panel_inner_w=ENNIS_PANEL_INNER_W,
        brick_top_z=brick_top_z,
        panel_z_center=panel_z_center,
        make_box=lambda y1, z1, y2, z2: box(
            panel_x1, y1, z1, panel_x2, y2, z2, gate_fence_tex
        ),
        make_lower_ramp=lambda y1, y2, z1a, z1b, z2a, z2b: ramp_slab_y(
            panel_x1, panel_x2, y1, y2, z1a, z1b, z2a, z2b, gate_fence_tex
        ),
        make_upper_ramp=lambda y1, y2, z1a, z1b, z2a, z2b: ramp_slab_y(
            panel_x1, panel_x2, y1, y2, z1a, z1b, z2a, z2b, gate_fence_tex
        ),
        build_arch_legs=lambda center_y, arch_rout, leg_t, legs_top_z: [
            box(
                panel_x1,
                center_y - arch_rout,
                brick_top_z,
                panel_x2,
                center_y - arch_rout + leg_t,
                legs_top_z,
                gate_fence_tex,
            ),
            box(
                panel_x1,
                center_y + arch_rout - leg_t,
                brick_top_z,
                panel_x2,
                center_y + arch_rout,
                legs_top_z,
                gate_fence_tex,
            ),
        ],
        append_arch_segments=lambda center_y, legs_top_z, arch_rin, arch_rout: (
            brushes.extend(
                [
                    arch_seg(
                        panel_x1,
                        panel_x2,
                        center_y,
                        legs_top_z,
                        arch_rin,
                        arch_rout,
                        seg_i * (180.0 / 8),
                        (seg_i + 1) * (180.0 / 8),
                        gate_fence_tex,
                    )
                    for seg_i in range(8)
                ]
            )
        ),
        build_cross_braces=lambda center_y, arch_rin, z1, z2, cross_hw: [
            shear_box_z(
                panel_x1,
                -cross_hw,
                z1,
                panel_x2,
                cross_hw,
                z2,
                center_y - arch_rin,
                center_y + arch_rin,
                gate_fence_tex,
            ),
            shear_box_z(
                panel_x1,
                -cross_hw,
                z1,
                panel_x2,
                cross_hw,
                z2,
                center_y + arch_rin,
                center_y - arch_rin,
                gate_fence_tex,
            ),
        ],
        build_layout=lambda add_panel, add_connector, add_arch_post: (
            _build_ennis_main_gate_layout(
                add_panel,
                add_connector,
                add_arch_post,
                gate_run_start_y=gate_run_start_y,
                pair_count=_pair_count,
                bw_mid_y=bw_mid_y,
            )
        ),
    )


def _build_ennis_corner_wall_pillar(brushes, ennis_wall_x1):
    """Build the square pillar capping the corner where the wall turns east."""
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


def _build_ennis_east_gate(gate_fence_tex):
    """Build the freestanding east gate brush set for the func_detail entity."""
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
    return east_gate_brushes


def _build_ennis_cement_wall_bulge(
    brushes,
    *,
    cement_wall_y1,
    cement_wall_y2,
    cement_wall_height,
    cement_wall_pillar_half_width,
    ennis_cement_x2_ext,
):
    """Build the curved curb bulge and its matching cap on the cement wall run."""
    _wall_cap_z1 = FLOOR_Z2 + cement_wall_height
    _wall_cap_z2 = _wall_cap_z1 + ENNIS_CEMENT_WALL_CAP_H
    _wall_bulge_draw_x1 = ENNIS_CEMENT_X2 + cement_wall_pillar_half_width
    _wall_bulge_draw_x2 = ennis_cement_x2_ext - cement_wall_pillar_half_width
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


def _build_ennis_cement_wall_pillar(
    brushes,
    entities,
    pillar_x,
    with_lamp,
    *,
    cement_wall_y1,
    cement_wall_y2,
    cement_wall_pillar_half_width,
    cement_wall_pillar_height,
):
    """Build one cement wall pillar, optionally topping it with a lamp post."""
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
            pillar_center_y - cement_wall_pillar_half_width - ENNIS_CEMENT_WALL_CAP_OVH,
            FLOOR_Z2 + cement_wall_pillar_height,
            pillar_x + cement_wall_pillar_half_width + ENNIS_CEMENT_WALL_CAP_OVH,
            pillar_center_y + cement_wall_pillar_half_width + ENNIS_CEMENT_WALL_CAP_OVH,
            FLOOR_Z2 + cement_wall_pillar_height + ENNIS_CEMENT_WALL_CAP_H,
            Textures.CEMENT,
        )
    )
    if with_lamp:
        lamppost_base_z = FLOOR_Z2 + cement_wall_pillar_height + ENNIS_CEMENT_WALL_CAP_H
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


def _build_ennis_cement_wall_extension(
    brushes,
    entities,
    *,
    cement_wall_y1,
    cement_wall_y2,
    cement_wall_height,
    cement_wall_pillar_half_width,
    ennis_cement_x2_ext,
    cement_wall_pillar_height,
):
    """Extend the cement wall eastward with repeated pillars and alternating lamps."""
    _ext_run_x1 = ennis_cement_x2_ext
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
        _build_ennis_cement_wall_pillar(
            brushes,
            entities,
            _pillar_x,
            with_lamp=(_ext_i % 2 == 1),
            cement_wall_y1=cement_wall_y1,
            cement_wall_y2=cement_wall_y2,
            cement_wall_pillar_half_width=cement_wall_pillar_half_width,
            cement_wall_pillar_height=cement_wall_pillar_height,
        )
        _prev_pillar_x = _pillar_x


def _build_ennis_cement_wall(brushes, entities):
    """Build the long cement wall, its bulged curb, pillars, caps, and lamps."""
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
    ennis_cement_x2_ext = ENNIS_CEMENT_X2 + ENNIS_CURB_BULGE_LEN
    _build_ennis_cement_wall_bulge(
        brushes,
        cement_wall_y1=cement_wall_y1,
        cement_wall_y2=cement_wall_y2,
        cement_wall_height=cement_wall_height,
        cement_wall_pillar_half_width=cement_wall_pillar_half_width,
        ennis_cement_x2_ext=ennis_cement_x2_ext,
    )
    for pillar_x in (ENNIS_CEMENT_X1, ENNIS_CEMENT_X2, ennis_cement_x2_ext):
        _build_ennis_cement_wall_pillar(
            brushes,
            entities,
            pillar_x,
            with_lamp=True,
            cement_wall_y1=cement_wall_y1,
            cement_wall_y2=cement_wall_y2,
            cement_wall_pillar_half_width=cement_wall_pillar_half_width,
            cement_wall_pillar_height=cement_wall_pillar_height,
        )
    _build_ennis_cement_wall_extension(
        brushes,
        entities,
        cement_wall_y1=cement_wall_y1,
        cement_wall_y2=cement_wall_y2,
        cement_wall_height=cement_wall_height,
        cement_wall_pillar_half_width=cement_wall_pillar_half_width,
        ennis_cement_x2_ext=ennis_cement_x2_ext,
        cement_wall_pillar_height=cement_wall_pillar_height,
    )


def _build_ennis_entrance_features():
    """Return the Ennis entrance pillars, walls, gates, and lamps owned by west-campus geometry."""
    brushes = []
    entities = []

    ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    bwex2 = ENNIS_GATE_X1
    sw_tex = Textures.FENCE
    gate_fence_tex = Textures.FENCE

    _build_ennis_entrance_pillars(brushes, entities)
    _build_ennis_short_wall_section(brushes, ennis_wall_x1, bwex2, sw_tex)
    _build_ennis_main_gate_section(brushes, ennis_wall_x1, gate_fence_tex)
    _build_ennis_corner_wall_pillar(brushes, ennis_wall_x1)
    east_gate_brushes = _build_ennis_east_gate(gate_fence_tex)
    _build_ennis_cement_wall(brushes, entities)
    if east_gate_brushes:
        entities.append(brush_ent("func_detail", east_gate_brushes))
    return brushes, entities
