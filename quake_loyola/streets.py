import math

from .constants import (
    BRIDGE,
    BRIDGE_DZ2,
    CHARLES_CRN_R,
    CHARLES_CRN_SEGS,
    CHARLES_LAMP_POST_H,
    CHARLES_LAMP_POST_XS,
    CHARLES_LAMP_POST_YS,
    CHARLES_PARKING_LANE_W,
    CHARLES_RAMP_W,
    CHARLES_SWALK_START,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    DORM,
    ENNIS_CEMENT_WALL_CAP_H,
    ENNIS_CEMENT_WALL_CAP_OVH,
    ENNIS_CEMENT_WALL_H,
    ENNIS_CEMENT_WALL_LAMP_POST_H,
    ENNIS_CEMENT_WALL_PILLAR_EXTRA_H,
    ENNIS_CEMENT_WALL_PILLAR_HW,
    ENNIS_CEMENT_X1,
    ENNIS_CEMENT_X2,
    ENNIS_CURB_W,
    ENNIS_GATE_FENCE_BAR_T,
    ENNIS_GATE_FENCE_HEIGHT,
    ENNIS_GATE_FENCE_POST_W,
    ENNIS_GATE_FENCE_SPACING,
    ENNIS_GATE_FENCE_TOP_RAIL_DROP,
    ENNIS_GATE_FENCE_TOP_RAIL_T,
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
    ENNIS_PILLAR_POST_H,
    ENNIS_PILLAR_X1,
    ENNIS_SW_EDGE,
    ENNIS_WALL_H,
    ENNIS_WALL_NY,
    ENNIS_WALL_PILLAR_H,
    ENNIS_WALL_PILLAR_HW,
    ENNIS_WALL_T,
    ENNIS_WALL_X_OFFSET,
    ENNIS_Y,
    FENCE_TEX,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    KNOTT_DRIVEWAY_ES_X2,
    ROAD_DASH_LEN,
    ROAD_GAP_LEN,
    ROAD_X1,
    ROAD_X2,
    SDORM_LIFT,
    STREET_CHARLES_CURB_W,
    STREET_DIV_HW,
    STREET_DIV_LINE_HW,
    STREET_ENNIS_DIV_HW,
    STREET_SURFACE_T,
    STREETS_DETAILS_ENABLED,
    WALL_T,
    WEST_CAMPUS_ENABLED,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    WORLD_Z2,
    Textures,
)
from .geometry import (
    arch_seg,
    box,
    brush_ent,
    ent,
    pyramid,
    ramp_slab,
    ramp_slab_y,
    shear_box_z,
    tri_prism,
)


def build_ennis_entrance_features():
    """Return the Ennis entrance/wall details that belong with west-campus geometry."""
    brushes = []
    entities = []

    for pillar_y in (
        ENNIS_Y - ENNIS_HW - ENNIS_PILLAR_HW,
        ENNIS_Y + ENNIS_HW + ENNIS_PILLAR_HW,
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
                Textures.WHITE_STONE,
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
                Textures.WHITE_STONE,
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
                Textures.WHITE_STONE,
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
                Textures.WHITE_STONE,
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
        # Flame + light above the brick cup, matching the Charles St lamp posts
        pillar_flame_z = pillar_apex_z + 20
        entities.append(
            ent(
                "light",
                origin=f"{ennis_pil_cx} {pillar_y} {pillar_flame_z}",
                light="300",
            )
        )
        entities.append(
            ent(
                "light_flame_large_yellow",
                origin=f"{ennis_pil_cx} {pillar_y} {pillar_flame_z + 4}",
            )
        )

    ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    bwex2 = ENNIS_GATE_X1
    brushes.append(
        box(
            ennis_wall_x1,
            ENNIS_WALL_NY,
            FLOOR_Z2,
            bwex2,
            ENNIS_WALL_NY + ENNIS_WALL_T,
            FLOOR_Z2 + ENNIS_WALL_H,
            Textures.BUILDING,
        )
    )
    # Fixed dozen-panel decorative iron gate: 12 rectangular panels grouped
    # into 6 pairs. A U-shaped iron pillar bookends the run (one at the very
    # south start, one at the very north end) and separates every pair in
    # between. The run starts clear of the existing brick/cement corner cap
    # pillar at the Ennis Rd corner (bw_cx/bw_cy below) so the two don't
    # overlap. The brick wall's north end (bw_mid_y) is sized to exactly fit
    # this run, after which the plain picket fence continues to the world edge.
    gate_run_start_y = (
        ENNIS_WALL_NY + ENNIS_WALL_T // 2 + ENNIS_WALL_PILLAR_HW + ENNIS_GATE_PILLAR_GAP
    )
    _pair_w = 2 * ENNIS_PANEL_OUTER_W + ENNIS_PANEL_GAP
    _pillar_unit_lead = ENNIS_GATE_PILLAR_W + ENNIS_GATE_PILLAR_GAP
    _pillar_unit_trail = 2 * ENNIS_GATE_PILLAR_GAP + ENNIS_GATE_PILLAR_W
    _pair_count = ENNIS_GATE_PANEL_COUNT // 2
    total_gate_w = _pillar_unit_lead + _pair_count * (_pair_w + _pillar_unit_trail)
    bw_mid_y = gate_run_start_y + total_gate_w
    brushes.append(
        box(
            ennis_wall_x1,
            ENNIS_WALL_NY,
            FLOOR_Z2,
            ennis_wall_x1 + ENNIS_WALL_T,
            bw_mid_y,
            FLOOR_Z2 + ENNIS_WALL_H,
            Textures.BUILDING,
        )
    )

    gate_fence_x1 = ennis_wall_x1 + ENNIS_WALL_T // 2 - 1
    gate_fence_x2 = gate_fence_x1 + ENNIS_GATE_FENCE_BAR_T
    gate_fence_tex = FENCE_TEX
    # Iron gate fence — extended to the true north world edge (WORLD_Y2, re-derived
    # from real-world measurement) rather than stopping at the old CHARLES_Y2
    # anchor, so Charles St stays fenced all the way to the world boundary.
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

    panel_x1 = ennis_wall_x1 - ENNIS_GATE_FENCE_BAR_T
    panel_x2 = ennis_wall_x1
    brick_top_z = FLOOR_Z2 + ENNIS_WALL_H
    # Panels sit a little proud of the brick top, connected down to it by the
    # mounting feet (see add_panel), matching how a real iron fence is
    # bracketed onto a wall rather than sitting flush with it.
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
        # Mounting feet — small iron brackets at each bottom corner, dropping
        # from the bottom rail down onto/into the brick top so the panel
        # reads as mounted on the wall rather than floating flush with it.
        # Same thin bar thickness as the connector ties for a consistent look.
        # Inset in from the corners a little so they sit under the rail
        # rather than right at the outer edge.
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

    def add_pillar(center_y):
        # Arched iron pillar: two vertical legs topped with a rounded arch
        # (rin/rout ring), slightly taller overall than the panels it
        # separates, in place of a flat crossbar.
        leg_t = ENNIS_GATE_PILLAR_LEG_T
        arch_rin = ENNIS_GATE_PILLAR_OPENING_W // 2
        arch_rout = arch_rin + leg_t
        pillar_top_z = panel_z2_o + ENNIS_GATE_PILLAR_EXTRA_H
        legs_top_z = pillar_top_z - arch_rout
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
        # Decorative X cross-brace filling the opening between the legs,
        # below the arch spring line.
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
        # Two small decorative horizontal iron bars bridging the narrow gap
        # between adjacent panels/pillars, matching the real fence's look.
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
    # Leading bookend pillar, then a gap into the first panel.
    add_pillar(cursor_y + ENNIS_GATE_PILLAR_W // 2)
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
        # A pillar follows every pair — the interior separators, and (on the
        # last pair) the trailing bookend pillar that closes out the run.
        gap_y1 = cursor_y
        cursor_y += ENNIS_GATE_PILLAR_GAP
        add_connector(gap_y1, cursor_y)
        add_pillar(cursor_y + ENNIS_GATE_PILLAR_W // 2)
        cursor_y += ENNIS_GATE_PILLAR_W
        gap_y1 = cursor_y
        cursor_y += ENNIS_GATE_PILLAR_GAP
        # Skip the connector tie after the trailing (north) bookend pillar —
        # it would otherwise reach toward the plain picket fence, which
        # doesn't share the same decorative style.
        if pair_i < _pair_count - 1:
            add_connector(gap_y1, cursor_y)
    assert cursor_y == bw_mid_y, (cursor_y, bw_mid_y)

    bw_cx = ennis_wall_x1 + ENNIS_WALL_T // 2
    bw_cy = ENNIS_WALL_NY + ENNIS_WALL_T // 2
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
            ENNIS_CEMENT_X1,
            cement_wall_y1,
            FLOOR_Z2,
            ENNIS_CEMENT_X2,
            cement_wall_y2,
            FLOOR_Z2 + cement_wall_height,
            Textures.CEMENT,
        )
    )
    brushes.append(
        box(
            ENNIS_CEMENT_X1,
            cement_wall_y1 - ENNIS_CEMENT_WALL_CAP_OVH,
            FLOOR_Z2 + cement_wall_height,
            ENNIS_CEMENT_X2,
            cement_wall_y2 + ENNIS_CEMENT_WALL_CAP_OVH,
            FLOOR_Z2 + cement_wall_height + ENNIS_CEMENT_WALL_CAP_H,
            Textures.CEMENT,
        )
    )
    for pillar_x in (ENNIS_CEMENT_X1, ENNIS_CEMENT_X2):
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
        # Flame + light above the lamp post, matching the Charles St lamp posts
        cement_wall_flame_z = lamppost_base_z + ENNIS_CEMENT_WALL_LAMP_POST_H + 20
        entities.append(
            ent(
                "light",
                origin=f"{pillar_x} {pillar_center_y} {cement_wall_flame_z}",
                light="300",
            )
        )
        entities.append(
            ent(
                "light_flame_large_yellow",
                origin=f"{pillar_x} {pillar_center_y} {cement_wall_flame_z + 4}",
            )
        )
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

    if east_gate_brushes:
        entities.append(brush_ent("func_detail", east_gate_brushes))
    return brushes, entities


def build():
    BRUSHES = []
    ENTITIES = []
    DETAIL_BRUSHES = []
    # ════════════════════════════════════════════════════════════════════════════════
    # RECTANGULAR WORLD SHELL — floor, 4 outer walls, sky ceiling
    # ════════════════════════════════════════════════════════════════════════════════
    # Tunnel-portal wall faces (below) show ground only when the west-campus
    # hillside/embankment geometry that they're shaped around is actually
    # present (built by west_campus.py); with WEST_CAMPUS_ENABLED off, those
    # inner faces should read as sky, regardless of STREETS_DETAILS_ENABLED.
    _tunnel_wall_tex = Textures.GROUND if WEST_CAMPUS_ENABLED else Textures.SKY
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z2,
            Textures.GROUND,
        )
    )  # floor
    # W wall — split by Z so only the tunnel-height portion shows ground on its inner face.
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            BRIDGE_DZ2,
            Textures.SKY,
            te=_tunnel_wall_tex,  # inner east face at tunnel height → ground
        )
    )  # W wall lower (tunnel height)
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
    )  # W wall upper (above tunnel)
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
    )  # E wall
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
    )  # N wall west of BRIDGE.x1 — plain seal over unmodeled real estate now that
    # BRIDGE.x1 no longer sits at the world wall (see constants.py § BRIDGE_X1).
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
    )  # S wall west of BRIDGE.x1 — plain seal, see N-wall comment above.
    # N wall — split at DORM.x1 (tunnel east boundary).  The inner (south) face is
    # split ALONG the tunnel ceiling-underside line, which slopes from
    # BRIDGE_DZ2-WALL_T at the world wall down to SDORM_LIFT at DORM.x1: ground on
    # the visible tunnel end-wall below that line, sky above it (the band above is
    # buried in the hillside slab / open sky), so no ground triangle pokes above
    # the hill.  This line is always below the hill roofline, so it stays hidden.
    # Shifted one wall-thickness east (WORLD_X1 → BRIDGE.x1) to align with the tunnel
    # west edge and seal the sky leak, matching the south-wall fix.
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
            tt=_tunnel_wall_tex,  # sloped top visible at tunnel exit → ground
            te=_tunnel_wall_tex,  # east end-cap at tunnel opening → ground
            ts=_tunnel_wall_tex,  # inner south face = tunnel end-wall → ground
        )
    )  # N wall tunnel portal (ground up to the ceiling-underside line)
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
            tb=_tunnel_wall_tex,  # sloped bottom face visible from tunnel → ground
        )
    )  # N wall above the tunnel end-wall
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
    )  # N wall east of tunnel
    # S wall — lower ramp mirrors the north-wall tunnel-portal pair: ground from
    # FLOOR_Z1 up to the sloped hillside underside (BRIDGE_DZ2-WALL_T west,
    # SDORM_LIFT east), sealing the tunnel mouth and showing the hillside slope face.
    # Shifted one wall-thickness east of the world wall (WORLD_X1 → BRIDGE.x1) so the
    # slope's high end (BRIDGE_DZ2-WALL_T) lands at the tunnel's west edge (BRIDGE.x1)
    # instead of behind the wall — otherwise the slope sat below the ceiling at the
    # tunnel mouth and left a sliver of sky visible inside the tunnel.
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
            tt=_tunnel_wall_tex,  # sloped top face — hillside slope visible at tunnel mouth
            ts=_tunnel_wall_tex,  # ±Y gable ends — tunnel end-wall ground texture
        )
    )  # S wall tunnel portal lower (sloped ground up to hillside underside)
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
            tb=_tunnel_wall_tex,  # sloped bottom face visible from tunnel → ground
        )
    )  # S wall above the tunnel end-wall (sky, up to the world ceiling)
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
    )  # S wall east of tunnel
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
    )  # sky
    if not STREETS_DETAILS_ENABLED:
        return BRUSHES, ENTITIES
    # ── Non-sealing street furniture, markings, and decorative ground geometry ──
    # These are moved to DETAIL_BRUSHES to speed up vis and reduce portal fragmentation.
    _world_brushes = BRUSHES
    BRUSHES = DETAIL_BRUSHES

    # ════════════════════════════════════════════════════════════════════════════════
    # CHARLES STREET — road surface, sidewalks, centre stripe
    # Road runs N-S (full Y); road channel E-W = ROAD_X1..ROAD_X2
    # ════════════════════════════════════════════════════════════════════════════════
    CHARLES_Y1 = WORLD_Y1 + WALL_T
    CHARLES_Y2 = WORLD_Y2 - WALL_T

    # ── Ennis Road (E-W, parallel to bridge, north side) ──
    # Runs from Charles Street west edge (ROAD_X1) east to the world wall, dead-ending there.
    # Half as wide as Charles Street (512/2=256 total → HW=128), north of bridge.
    ENNIS_X1 = ROAD_X1  # start at west edge of Charles St to form T-junction
    ENNIS_X2 = WORLD_X2_EXT - WALL_T  # dead-end at east world wall
    # Back road corridor X extents — defined here for road/curb brush splits below

    # Charles St curb-to-curb models 1 travel lane + 1 parking lane each side
    # (see docs/reference.rst "Charles St width validation"). Parking lane sits
    # nearest each curb; travel lane sits between it and the centre divider.
    # Road surface split into 4 slabs, leaving narrow slots for the centre
    # double-yellow divider and the two parking-lane stripes.
    CHARLES_PARKING_LINE_X = ROAD_X2 - CHARLES_PARKING_LANE_W  # = 160
    BRUSHES.append(
        box(
            ROAD_X1,
            CHARLES_Y1,
            FLOOR_Z2,
            -CHARLES_PARKING_LINE_X - STREET_DIV_LINE_HW,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )  # west parking lane
    BRUSHES.append(
        box(
            -CHARLES_PARKING_LINE_X + STREET_DIV_LINE_HW,
            CHARLES_Y1,
            FLOOR_Z2,
            -STREET_DIV_HW,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )  # west travel lane
    BRUSHES.append(
        box(
            STREET_DIV_HW,
            CHARLES_Y1,
            FLOOR_Z2,
            CHARLES_PARKING_LINE_X - STREET_DIV_LINE_HW,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )  # east travel lane
    BRUSHES.append(
        box(
            CHARLES_PARKING_LINE_X + STREET_DIV_LINE_HW,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X2,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )  # east parking lane
    # West sidewalk — north of bridge
    BRUSHES.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_SWALK_START,
            FLOOR_Z2,
            ROAD_X1,
            CHARLES_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # West curb — south section up to sidewalk start
    BRUSHES.append(
        box(
            ROAD_X1 - STREET_CHARLES_CURB_W,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X1,
            CHARLES_SWALK_START,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # Raised ground west of curb — rock/ground texture, flush with sidewalk
    BRUSHES.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X1 - STREET_CHARLES_CURB_W,
            CHARLES_SWALK_START,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    # East sidewalk — split into two segments, trimmed CHARLES_WALK_W short of each corner
    BRUSHES.append(
        box(
            ROAD_X2,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y - ENNIS_HW - CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        box(
            ROAD_X2,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            FLOOR_Z2,
            ROAD_X2 + CHARLES_WALK_W,
            CHARLES_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Ennis Road brushes ──
    # Road surface — split around centre divider slot and south curb strip (Y=776–784)
    # West section (near Charles St, no curb strip here)
    BRUSHES.append(
        box(
            ENNIS_X1,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2,
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # Main east sections — full south extent to road edge
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
                ENNIS_Y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
            )
        )
    # Corridor gap section (back road entrance, no curb strip)
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_CORRIDOR_X1,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_CORRIDOR_X2,
            ENNIS_Y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    BRUSHES.append(
        box(
            ENNIS_X1,
            ENNIS_Y + STREET_ENNIS_DIV_HW,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # North curb — offset east by CHARLES_WALK_W to cut corner square
    BRUSHES.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # South curb — split into two segments with a gap for the back road entrance
    # West segment: Charles St east sidewalk to back road west sidewalk
    BRUSHES.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_SW_EDGE,
            FLOOR_Z2,
            KNOTT.x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # East segment: back road east sidewalk east to world wall
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X2,
            ENNIS_SW_EDGE,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Lane markings — dashed sfloor3_2 flush inserts in carved road slots ──────
    dash_brushes = []
    # Charles Street centre line — solid double-yellow (two stripes with a gap),
    # not dashed: real N Charles St has a no-passing double-yellow stripe here
    # (see docs/reference.rst "Charles St width validation"). Textures.CENTERLINE
    # is a placeholder stand-in until a dedicated yellow line texture is sourced.
    # The bridge deck overhead is an overpass with piers landing well outside
    # the road (nearest piers at X=-1246/525, road is only X=-256..256), so
    # nothing in the road is ever obstructed — stripe the whole length
    # regardless of BRIDGE_ENABLED.
    _centerline_gap_hw = 2  # half-width of the gap between the two lines
    for line_x1, line_x2 in (
        (-STREET_DIV_HW, -_centerline_gap_hw),
        (_centerline_gap_hw, STREET_DIV_HW),
    ):
        dash_brushes.append(
            box(
                line_x1,
                CHARLES_Y1,
                FLOOR_Z2,
                line_x2,
                CHARLES_Y2,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.CENTERLINE,
            )
        )
    dash_brushes.append(
        box(
            -_centerline_gap_hw,
            CHARLES_Y1,
            FLOOR_Z2,
            _centerline_gap_hw,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # Charles Street parking-lane stripes — dashed, delineating the travel lane
    # from the curbside parking lane on each side.
    for parking_x in (-CHARLES_PARKING_LINE_X, CHARLES_PARKING_LINE_X):
        # Quake tiles top-face textures by absolute world X (u = X + offset_x).
        # The east stripe sits at +CHARLES_PARKING_LINE_X vs the west stripe's
        # -CHARLES_PARKING_LINE_X, so without a compensating offset it samples
        # a different part of the texture. Shift east's offset by the mirror
        # distance so both stripes read the same texture region.
        tex_offset_x = -(parking_x + CHARLES_PARKING_LINE_X)
        divider_tt_params = f"{tex_offset_x} 0 0 1 1"
        divider_y = CHARLES_Y1
        dash_on = True
        while divider_y < CHARLES_Y2:
            next_divider_y = min(
                divider_y + (ROAD_DASH_LEN if dash_on else ROAD_GAP_LEN), CHARLES_Y2
            )
            divider_tex = Textures.PARKING_STRIPE if dash_on else Textures.ROAD
            dash_brushes.append(
                box(
                    parking_x - STREET_DIV_LINE_HW,
                    divider_y,
                    FLOOR_Z2,
                    parking_x + STREET_DIV_LINE_HW,
                    next_divider_y,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    divider_tex,
                    tt_params=divider_tt_params,
                )
            )
            divider_y = next_divider_y
            dash_on = not dash_on
    # Ennis Road — solid single yellow centerline (replaces the old dashed
    # divider strip; carved slot width is unchanged, only a thin line is
    # painted in the middle with Textures.ROAD filling the rest).
    _ennis_line_hw = STREET_DIV_LINE_HW
    dash_brushes.append(
        box(
            ROAD_X2,
            ENNIS_Y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y - _ennis_line_hw,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    dash_brushes.append(
        box(
            ROAD_X2,
            ENNIS_Y - _ennis_line_hw,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + _ennis_line_hw,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.CENTERLINE,
        )
    )
    dash_brushes.append(
        box(
            ROAD_X2,
            ENNIS_Y + _ennis_line_hw,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    if dash_brushes:
        ENTITIES.append(brush_ent("func_detail", dash_brushes))

    # ── Rounded intersection corners (Charles & Ennis) ───────────────────────────
    # Arc center at the OUTER (far) corner so the curve faces outward toward the road.
    # Each corner: road box fills the cut square, cement arc fans sit on top.
    # SE corner: far corner is at SE of cut square
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
    # Arc sweeps CCW from 90° (north) to 180° (west)
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
                Textures.CEMENT,
            )
        )

    # NE corner: far corner is at NE of cut square
    cx_ne = ROAD_X2 + CHARLES_CRN_R
    cy_ne = ENNIS_Y + ENNIS_HW + CHARLES_CRN_R
    BRUSHES.append(
        box(
            ROAD_X2,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2,
            cx_ne,
            cy_ne,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # Arc sweeps CCW from 180° (west) to 270° (south)
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
                Textures.CEMENT,
            )
        )

    # ── Sidewalk ramps — smooth ground-to-sidewalk transitions ───────────────────
    # West ramp — slopes from ground up to west sidewalk edge (full N-S extent)
    BRUSHES.append(
        ramp_slab(
            ROAD_X1 - CHARLES_WALK_W - CHARLES_RAMP_W,
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_Y1,
            CHARLES_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # East ramp — south of Ennis Road
    BRUSHES.append(
        ramp_slab(
            ROAD_X2 + CHARLES_WALK_W,
            ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W,
            CHARLES_Y1,
            ENNIS_SW_EDGE,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # East ramp — north of Ennis Road
    BRUSHES.append(
        ramp_slab(
            ROAD_X2 + CHARLES_WALK_W,
            ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            CHARLES_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # Ennis north ramp — slopes from north curb edge down going north
    BRUSHES.append(
        ramp_slab_y(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W + CHARLES_RAMP_W,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # (Ramp zone south of Ennis sidewalk covered by world floor — no fill needed)

    # Verge fill — ground between road south edge and sidewalk inner edge, flush with sidewalk
    # Split around back road corridor gap (KNOTT_DRIVEWAY_CORRIDOR_X1..KNOTT_DRIVEWAY_CORRIDOR_X2)
    # SE corner (east of back road) uses gravel3c (mulch bed)
    for vx1, vx2, vtex in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, Textures.GROUND),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2, Textures.MULCH),
    ]:
        BRUSHES.append(
            box(
                vx1,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z1,
                vx2,
                ENNIS_Y - ENNIS_HW - ENNIS_CURB_W,
                FLOOR_Z2 + CHARLES_WALK_H,
                vtex,
            )
        )

    # Cement curb strip — last 8 units of verge at road edge, flush with verge surface
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

    ennis_brushes, ennis_entities = build_ennis_entrance_features()
    BRUSHES.extend(ennis_brushes)
    ENTITIES.extend(ennis_entities)

    # ── West-side hill/terrace terrain — REMOVED, pending re-derivation ─────────
    # Previously built a sloped embankment under the (currently disabled) dorm
    # buildings plus a raised south-dorm terrace/frontage hill down to Charles St.
    # Both were flat-plateau/simple-ramp models not yet validated against the
    # real-world topology check (docs/reference.rst, "Topology check" section).
    # The base world floor (built above, unconditionally) is already flat at
    # FLOOR_Z2, so removing this section leaves flat ground here with no leak.
    #
    # TODO: rebuild this terrain in real-world-derived sections/quadrants rather
    # than one continuous hill model, once the new elevation data is ready.
    BRUSHES = _world_brushes

    # ── Campus lamp posts (brush geometry) — along Charles Street (N-S) ──────────
    # X/Y/H imported from constants.py — must match entities.py's flame placement
    # (previously duplicated here with stale hardcoded X values that had drifted
    # out of sync with the flame positions, leaving flames floating with no pole).
    for lamp_x in CHARLES_LAMP_POST_XS:
        for lamp_y in CHARLES_LAMP_POST_YS:
            pole_top_z = FLOOR_Z2 + CHARLES_LAMP_POST_H
            # Narrow shaft
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
            # Torch top — narrow post + brick cup (matches bridge pillar torches)
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
            # Flame + light above the brick cup, matching bridge pillar torches
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

    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
