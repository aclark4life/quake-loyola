from .constants import (
    BRIDGE_DZ2,
    BRIDGE_X1,
    CHARLES_WALK_W,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM,
    DORM_BRICK_GATE_H,
    DORM_BRICK_PILLAR_CAP_H,
    DORM_BRICK_PILLAR_CAP_OVH,
    DORM_BRICK_PILLAR_GAP,
    DORM_BRICK_PILLAR_H_OFFSET,
    DORM_BRICK_PILLAR_PROUD,
    DORM_BRICK_PILLAR_SEPARATION,
    DORM_BRICK_PILLAR_W,
    DORM_BRICK_WALL_HALF_W,
    DORM_DOOR_H,
    DORM_DOOR_OFF,
    DORM_DOOR_W,
    DORM_EMB_X2,
    DORM_ENT_H,
    DORM_ENT_HW,
    DORM_FLOOR_H,
    DORM_FLOORS,
    DORM_FRONT_WALKWAY_FENCE_OFFSET,
    DORM_FRONT_WALKWAY_H,
    DORM_FRONT_WALKWAY_W,
    DORM_GABLE_DEPTH,
    DORM_H,
    DORM_INNER_DOOR_H,
    DORM_INNER_DOOR_HW,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_PIER_X,
    DORM_ROOF_H,
    DORM_SLAB_T,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    DORM_WALL,
    DORM_WALL_S_Y2,
    DORM_WIN_HH,
    DORM_WIN_HW,
    DORM_WIN_MARGIN,
    DORM_X1,
    DORM_X2,
    ENNIS_CEMENT_WALL_CAP_H,
    ENNIS_CEMENT_WALL_CAP_OVH,
    ENNIS_CEMENT_WALL_H,
    ENNIS_CEMENT_WALL_LAMP_POST_H,
    ENNIS_CEMENT_WALL_PILLAR_EXTRA_H,
    ENNIS_CEMENT_WALL_PILLAR_HW,
    ENNIS_CEMENT_X1,
    ENNIS_CEMENT_X2,
    ENNIS_GATE_FENCE_BAR_T,
    ENNIS_GATE_FENCE_HEIGHT,
    ENNIS_GATE_FENCE_POST_W,
    ENNIS_GATE_FENCE_SPACING,
    ENNIS_GATE_FENCE_TOP_RAIL_DROP,
    ENNIS_GATE_FENCE_TOP_RAIL_T,
    ENNIS_GATE_X1,
    ENNIS_GATE_X2,
    ENNIS_HW,
    ENNIS_PANEL_GAP,
    ENNIS_PANEL_INNER_H,
    ENNIS_PANEL_INNER_W,
    ENNIS_PANEL_OUTER_H,
    ENNIS_PANEL_OUTER_W,
    ENNIS_PIL_BELL2_H,
    ENNIS_PIL_BELL2_HW,
    ENNIS_PIL_CAP_H,
    ENNIS_PIL_CAP_OVH,
    ENNIS_PIL_HW,
    ENNIS_PIL_POST_H,
    ENNIS_PIL_X1,
    ENNIS_WALL_H,
    ENNIS_WALL_NY,
    ENNIS_WALL_PIL_H,
    ENNIS_WALL_PIL_HW,
    ENNIS_WALL_T,
    ENNIS_WALL_X_OFFSET,
    ENNIS_Y,
    FENCE_H,
    FENCE_SPACING,
    FENCE_TEX,
    FENCE_X1,
    FENCE_X2,
    FLOOR_Z1,
    FLOOR_Z2,
    ROAD_X2,
    SDORM_LIFT,
    SDORM_SLOPE_Y_N,
    SDORM_SLOPE_Y_S,
    SDORM_STAIR_N,
    SDORM_STAIR_RISE,
    SDORM_STAIR_RUN,
    SDORM_STAIR_X1,
    SDORM_STAIR_X2,
    SDORM_STAIR_Y1,
    SDORM_STAIR_Y2,
    Textures,
)
from .geometry import (
    box,
    brush_ent,
    ent,
    entrance_arch_xwall,
    entrance_arch_ywall,
    gable_slats,
    layered_wall,
    layered_wall_y,
    pyramid,
    ramp_slab,
    ramp_slab_y,
    win_frame_xwall,
    win_frame_ywall,
)
from .utils import iron_fence


def build_ennis_entrance_features():
    """Return the Ennis entrance/wall details that belong with west-campus geometry."""
    brushes = []
    entities = []

    for pillar_y in (
        ENNIS_Y - ENNIS_HW - ENNIS_PIL_HW,
        ENNIS_Y + ENNIS_HW + ENNIS_PIL_HW,
    ):
        ennis_pil_cx = ENNIS_PIL_X1 + ENNIS_PIL_HW
        cap_half_width = ENNIS_PIL_HW + ENNIS_PIL_CAP_OVH
        base_height = ENNIS_PIL_POST_H // 3
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
                ENNIS_PIL_X1,
                pillar_y - ENNIS_PIL_HW,
                FLOOR_Z2 + base_height,
                ENNIS_PIL_X1 + 2 * ENNIS_PIL_HW,
                pillar_y + ENNIS_PIL_HW,
                FLOOR_Z2 + ENNIS_PIL_POST_H,
                Textures.WHITE_STONE,
            )
        )
        cap_z = FLOOR_Z2 + ENNIS_PIL_POST_H
        brushes.append(
            box(
                ennis_pil_cx - cap_half_width,
                pillar_y - cap_half_width,
                cap_z,
                ennis_pil_cx + cap_half_width,
                pillar_y + cap_half_width,
                cap_z + ENNIS_PIL_CAP_H,
                Textures.WHITE_STONE,
            )
        )
        bell2_z = cap_z + ENNIS_PIL_CAP_H
        brushes.append(
            box(
                ennis_pil_cx - ENNIS_PIL_BELL2_HW,
                pillar_y - ENNIS_PIL_BELL2_HW,
                bell2_z,
                ennis_pil_cx + ENNIS_PIL_BELL2_HW,
                pillar_y + ENNIS_PIL_BELL2_HW,
                bell2_z + ENNIS_PIL_BELL2_H,
                Textures.WHITE_STONE,
            )
        )
        pillar_apex_z = bell2_z + ENNIS_PIL_BELL2_H
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
            "city2_1",
        )
    )
    bw_mid_y = (ENNIS_WALL_NY + CHARLES_Y2) // 2
    brushes.append(
        box(
            ennis_wall_x1,
            ENNIS_WALL_NY,
            FLOOR_Z2,
            ennis_wall_x1 + ENNIS_WALL_T,
            bw_mid_y,
            FLOOR_Z2 + ENNIS_WALL_H,
            "city2_1",
        )
    )

    gate_fence_x1 = ennis_wall_x1 + ENNIS_WALL_T // 2 - 1
    gate_fence_x2 = gate_fence_x1 + ENNIS_GATE_FENCE_BAR_T
    gate_fence_tex = "metal4_4"
    brushes.append(
        box(
            gate_fence_x1,
            bw_mid_y,
            FLOOR_Z2 + ENNIS_GATE_FENCE_HEIGHT - ENNIS_GATE_FENCE_TOP_RAIL_DROP,
            gate_fence_x2,
            CHARLES_Y2,
            FLOOR_Z2
            + ENNIS_GATE_FENCE_HEIGHT
            - ENNIS_GATE_FENCE_TOP_RAIL_DROP
            + ENNIS_GATE_FENCE_TOP_RAIL_T,
            gate_fence_tex,
        )
    )
    gate_picket_y = bw_mid_y
    gate_picket_index = 0
    while gate_picket_y + 2 <= CHARLES_Y2:
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
    panel_z1 = FLOOR_Z2 + ENNIS_WALL_H
    panel_z_center = panel_z1 + ENNIS_PANEL_OUTER_H // 2
    panel_available_span = bw_mid_y - ENNIS_WALL_NY
    panel_count = max(
        1,
        (panel_available_span + ENNIS_PANEL_OUTER_W)
        // (ENNIS_PANEL_OUTER_W + ENNIS_PANEL_GAP),
    )
    panel_spacing = panel_available_span // panel_count
    panel_center_y = ENNIS_WALL_NY + panel_spacing // 2
    panels_drawn = 0
    while panels_drawn < panel_count:
        y1_o = panel_center_y - ENNIS_PANEL_OUTER_W // 2
        y2_o = panel_center_y + ENNIS_PANEL_OUTER_W // 2
        z1_o = panel_z_center - ENNIS_PANEL_OUTER_H // 2
        z2_o = panel_z_center + ENNIS_PANEL_OUTER_H // 2
        y1_i = panel_center_y - ENNIS_PANEL_INNER_W // 2
        y2_i = panel_center_y + ENNIS_PANEL_INNER_W // 2
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
        conn_y2_p = panel_center_y + panel_spacing - ENNIS_PANEL_OUTER_W // 2
        if panels_drawn + 1 < panel_count:
            brushes.append(
                box(
                    panel_x1,
                    y2_o,
                    panel_z_center - ENNIS_GATE_FENCE_BAR_T // 2,
                    panel_x2,
                    conn_y2_p,
                    panel_z_center + ENNIS_GATE_FENCE_BAR_T // 2,
                    gate_fence_tex,
                )
            )
        panel_center_y += panel_spacing
        panels_drawn += 1

    bw_cx = ennis_wall_x1 + ENNIS_WALL_T // 2
    bw_cy = ENNIS_WALL_NY + ENNIS_WALL_T // 2
    brushes.append(
        box(
            bw_cx - ENNIS_WALL_PIL_HW,
            bw_cy - ENNIS_WALL_PIL_HW,
            FLOOR_Z2,
            bw_cx + ENNIS_WALL_PIL_HW,
            bw_cy + ENNIS_WALL_PIL_HW,
            FLOOR_Z2 + ENNIS_WALL_PIL_H,
            "city2_1",
        )
    )
    brushes.append(
        box(
            bw_cx - ENNIS_WALL_PIL_HW,
            bw_cy - ENNIS_WALL_PIL_HW,
            FLOOR_Z2 + ENNIS_WALL_PIL_H,
            bw_cx + ENNIS_WALL_PIL_HW,
            bw_cy + ENNIS_WALL_PIL_HW,
            FLOOR_Z2 + ENNIS_WALL_PIL_H + 6,
            Textures.CEMENT,
        )
    )
    brushes.append(
        box(
            bw_cx - ENNIS_WALL_PIL_HW - 1,
            bw_cy - ENNIS_WALL_PIL_HW - 1,
            FLOOR_Z2 + ENNIS_WALL_PIL_H + 6,
            bw_cx + ENNIS_WALL_PIL_HW + 1,
            bw_cy + ENNIS_WALL_PIL_HW + 1,
            FLOOR_Z2 + ENNIS_WALL_PIL_H + 10,
            Textures.CEMENT,
        )
    )
    brushes.append(
        pyramid(
            bw_cx - ENNIS_WALL_PIL_HW - 1,
            bw_cy - ENNIS_WALL_PIL_HW - 1,
            FLOOR_Z2 + ENNIS_WALL_PIL_H + 10,
            bw_cx + ENNIS_WALL_PIL_HW + 1,
            bw_cy + ENNIS_WALL_PIL_HW + 1,
            FLOOR_Z2 + ENNIS_WALL_PIL_H + 16,
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
    # ── North building — hollow shell with windows, entrance, and gable roof ───────
    # Underground tunnel — dimensions and embankment interpolation
    TUNN_T = DORM.wall_t  # wall/ceiling/floor thickness (= 16)
    TUNN_H = DORM_INNER_DOOR_H  # interior height (= 128), matches door opening
    TUNN_X2 = DORM_X1  # east face of tunnel = west face of buildings

    # Embankment surface Z at the building's west face (east end of the backfill ramp).
    _emb_denom = DORM_EMB_X2 - BRIDGE_X1
    emb_zt_tunn_e = int(
        BRIDGE_DZ2 + (FLOOR_Z2 - BRIDGE_DZ2) * (TUNN_X2 - BRIDGE_X1) / _emb_denom
    )

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
        DORM.floor_h - DORM_WIN_HH * 2
    ) // 2  # window sill offset within a floor
    dorm_wz_hi = dorm_wz_lo + DORM_WIN_HH * 2  # window head offset within a floor

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

    def nb_wins_xz(wx_list):
        """Window openings (all floors) for X-facing wall (south/north)."""
        return dorm_window_openings(wx_list)

    def nb_wins_yz(wy_list):
        """Window openings (all floors) for Y-facing wall (east/west)."""
        return dorm_window_openings(wy_list)

    def nb_wins_yz_west(wy_list):
        """West-face window openings — floors 0 and 1 are buried by the hillside
        (terrain reaches z=177 at the building west face), so only floor 2+ is shown."""
        return dorm_window_openings(wy_list, start_floor=2)

    def nb_wins_yz_double(wy_list):
        """Double window openings for Y-facing wall — two full-single-sized panes per floor."""
        return dorm_window_openings(wy_list, double=True)

    def nb_wins_xz_upper(wx_list, x_clear=None):
        """X-facing wall windows from floor 1 up — floor 0 is buried by the
        gap embankment on the NB2 south face and NB1 north face.
        x_clear: windows with wx < x_clear also skip floor 1 (terrain still
        overlaps the floor-1 sill at the far-west window position)."""
        return dorm_window_openings(
            wx_list,
            start_floor=1,
            include_window=lambda wx, fl: x_clear is None or wx >= x_clear or fl >= 2,
        )

    # South wall (faces NB2) — door only, no windows on interior walls
    north_bldg_detail = []
    north_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH_Y1,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH_Y1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            [dorm_door_open],
            "city2_1",
        )
    )
    # North wall — windows (floors 0 and wx<-1652 floor 1 buried by gap embankment; center floor 1+)
    north_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH_Y2 - DORM_WALL,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH_Y2,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz_upper(dorm_wx, x_clear=-1652)
            + [
                (
                    DORM_CX - DORM_WIN_HW,
                    zb,
                    DORM_CX + DORM_WIN_HW,
                    zt,
                )
                for _, zb, zt in dorm_window_levels(1)
            ],
            "city2_1",
        )
    )
    # East wall — windows only (no entrance)
    # Explicit even-spaced positions within NB1 (G≈65): sets 4(D), 5(S).
    nb1_e_double_wy = DORM_NORTH_Y1 + 157  # set 4 double
    nb1_e_single_wy = DORM_NORTH_Y1 + 334  # set 5 single
    dorm_e_openings = nb_wins_yz_double([nb1_e_double_wy]) + nb_wins_yz(
        [nb1_e_single_wy]
    )
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
    # West wall — windows (floor 2 only; floors 0–1 are buried by the hillside)
    # + ground-floor tunnel door opening
    north_bldg_detail.extend(
        layered_wall_y(
            DORM_NORTH_Y1 + DORM_WALL,
            DORM_X1,
            FLOOR_Z2,
            DORM_NORTH_Y2 - DORM_WALL,
            DORM_X1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz_west(dorm_wy)
            + [
                (
                    DORM_NORTH_CY - DORM_INNER_DOOR_HW,
                    FLOOR_Z2,
                    DORM_NORTH_CY + DORM_INNER_DOOR_HW,
                    FLOOR_Z2 + TUNN_H,
                )
            ],
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

    # Door frame removed — south wall between NB1 and NB2 is gone.
    # Window frames — north face (floors 0 and wx<-1652 floor 1 buried by gap embankment)
    for xl, zb, xr, zt in nb_wins_xz_upper(dorm_wx, x_clear=-1652):
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
    for _, zb, zt in dorm_window_levels(1):
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
            crossbar=True,
        )
    # Door frame — ground-floor center doorway to building 2 (south face, interior wall)
    north_bldg_detail += win_frame_xwall(
        DORM_CX - DORM_INNER_DOOR_HW,
        DORM_CX + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
        DORM_NORTH_Y1,
        +1,
        Textures.GABLE,
        fw=8,
        fd=DORM_WALL,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )
    # Window frames — east face (set4 double, set5 single) — evenly spaced
    for yl, zb, yr, zt in nb_wins_yz_double([nb1_e_double_wy]):
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
    for yl, zb, yr, zt in nb_wins_yz([nb1_e_single_wy]):
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
    # Window frames — west face (floor 2 only; floors 0–1 buried by hillside)
    for yl, zb, yr, zt in nb_wins_yz_west(dorm_wy):
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
    # Door frame — west face tunnel entrance
    north_bldg_detail += win_frame_ywall(
        DORM_NORTH_CY - DORM_INNER_DOOR_HW,
        DORM_NORTH_CY + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + TUNN_H,
        DORM_X1,
        +1,
        Textures.GABLE,
        fw=8,
        fd=DORM_WALL,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )

    DORM_EAVE_Z = FLOOR_Z2 + DORM_H + DORM_WALL  # top of ceiling slab = eave level
    DORM_RIDGE_Z = DORM_EAVE_Z + DORM_ROOF_H  # ridge apex
    DORM_SLAB_T = 16  # roof slab thickness at eave
    # Recess the roof-slab gable ends inward so the slats fill the gap with their
    # outer face flush with the wall below; grooves between planks reveal the
    # recessed slab behind them (relief) without protruding past the wall.
    DORM_NB_SY1 = DORM_NORTH_Y1  # south end abuts building 2 — full slab, no recess
    DORM_NB_SY2 = DORM_NORTH_Y2 - DORM_GABLE_DEPTH
    # West slope: flat bottom at eave_z, top slopes up to ridge
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
    # East slope: top at ridge, slopes down to eave at DORM_X2
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
    # Center openings (floor 1+ only) for X-facing walls of building 2
    nb2_cx_opens = [
        (
            DORM_CX - DORM_WIN_HW,
            zb,
            DORM_CX + DORM_WIN_HW,
            zt,
        )
        for _, zb, zt in dorm_window_levels(1)
    ]
    north2_bldg_detail = []
    # South wall — floors 0 and wx<-1652 floor 1 buried by gap embankment
    north2_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH2_Y1,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH2_Y1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            nb_wins_xz_upper(dorm_wx, x_clear=-1652) + nb2_cx_opens,
            "city2_1",
        )
    )
    # North wall (faces NB1) — door only, no windows on interior walls
    north2_bldg_detail.extend(
        layered_wall(
            DORM_X1,
            DORM_NORTH2_Y2 - DORM_WALL,
            FLOOR_Z2,
            DORM_X2,
            DORM_NORTH2_Y2,
            FLOOR_Z2 + DORM_H,
            [dorm_door_open],
            "city2_1",
        )
    )
    # East wall — windows only (no entrance, no arch)
    # Explicit even-spaced positions within NB2 (G≈30): sets 1(S), 2(S), 3(D).
    nb2_e_wy_s1 = DORM_NORTH2_Y1 + 82  # set 1 single
    nb2_e_wy_s2 = DORM_NORTH2_Y1 + 184  # set 2 single
    nb2_e_double_wy = DORM_NORTH2_Y1 + 326  # set 3 double
    north2_bldg_detail.extend(
        layered_wall_y(
            DORM_NORTH2_Y1 + DORM_WALL,
            DORM_X2 - DORM_WALL,
            FLOOR_Z2,
            DORM_NORTH2_Y2 - DORM_WALL,
            DORM_X2,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz([nb2_e_wy_s1, nb2_e_wy_s2])
            + nb_wins_yz_double([nb2_e_double_wy]),
            "city2_1",
        )
    )
    # West wall — windows only (floor 2 only; floors 0–1 buried by hillside)
    north2_bldg_detail.extend(
        layered_wall_y(
            DORM_NORTH2_Y1 + DORM_WALL,
            DORM_X1,
            FLOOR_Z2,
            DORM_NORTH2_Y2 - DORM_WALL,
            DORM_X1 + DORM_WALL,
            FLOOR_Z2 + DORM_H,
            nb_wins_yz_west(dorm_wy2),
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
    # Window frames — south face (floors 0 and wx<-1652 floor 1 buried by gap embankment)
    for xl, zb, xr, zt in nb_wins_xz_upper(dorm_wx, x_clear=-1652):
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
    for _, zb, zt in dorm_window_levels(1):
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
    # Window frames — east face (set1+2 single; set3 double) — evenly spaced
    for yl, zb, yr, zt in nb_wins_yz([nb2_e_wy_s1, nb2_e_wy_s2]):
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
    for yl, zb, yr, zt in nb_wins_yz_double([nb2_e_double_wy]):
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
    # Door frame — ground-floor center doorway to building 1 (north face, interior wall)
    north2_bldg_detail += win_frame_xwall(
        DORM_CX - DORM_INNER_DOOR_HW,
        DORM_CX + DORM_INNER_DOOR_HW,
        FLOOR_Z2,
        FLOOR_Z2 + DORM_INNER_DOOR_H,
        DORM_NORTH2_Y2,
        -1,
        Textures.GABLE,
        fw=8,
        fd=DORM_WALL,
        margin=DORM_WIN_MARGIN,
        crossbar=False,
        bottom=False,
    )
    # Window frames — west face (floor 2 only; floors 0–1 buried by hillside)
    for yl, zb, yr, zt in nb_wins_yz_west(dorm_wy2):
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
        north_pier_x=None,
        north_pier_hw=0,
        north_min_floor=0,
        west_door=True,
        stairwell=False,
    ):
        """Build the south abutment building geometry (walls, roof, windows, entrance)
        between Y positions by1 (south) and by2 (north).
        slat_lo/slat_hi add gable wood slats on the by1/-Y and by2/+Y ends.
        entrance adds the east-face entrance arch/door (windows only when False).
        chimney cuts a passable shaft through the east roof slope and ceiling and adds
        a hollow brick stack above the roof (the player can drop into the interior).
        door_lo/door_hi add a ground-floor center doorway on the by1/-Y or by2/+Y wall.
        north_pier_x/north_pier_hw: X position and half-width of an external wall that
        blocks windows on the north face (by2); overlapping openings are omitted.
        north_min_floor: lowest floor shown on the north (by2) face; floors below this
        are omitted (used when the embankment in the gap partially buries floor 0)."""
        bx1, bx2 = DORM_X1, DORM_X2
        cx = (bx1 + bx2) // 2
        ent_hw, ent_h = 48, 120
        wx_list = [bx1 + (cx - ent_hw - bx1) * k // 3 for k in [1, 2]] + [
            (cx + ent_hw) + (bx2 - cx - ent_hw) * k // 3 for k in [1, 2]
        ]
        wy_list = [by1 + (by2 - by1) * k // 4 for k in [1, 2, 3]]

        def wxz():
            return dorm_window_openings(wx_list)

        def wyz():
            return dorm_window_openings(wy_list)

        def wyz_west():
            """West-face windows: floor 0 is buried by the hillside after terrace lift."""
            return dorm_window_openings(wy_list, start_floor=1)

        def wxz_north():
            """North-face (by2) windows: floors below north_min_floor are omitted,
            and any opening that overlaps north_pier_x ± north_pier_hw is filtered."""
            wins = dorm_window_openings(wx_list, start_floor=north_min_floor)
            if north_pier_x is not None:
                wins = [
                    (xl, zb, xr, zt)
                    for xl, zb, xr, zt in wins
                    if xr <= north_pier_x - north_pier_hw
                    or xl >= north_pier_x + north_pier_hw
                ]
            return wins

        brushes = []
        # Interior floor — carved around the stairwell void when stairwell=True
        if stairwell:
            # Floor frame: south strip, north strip, and an east strip; the void
            # itself (west edge to SDORM_STAIR_X2, SDORM_STAIR_Y1..Y2) is left open.
            brushes += [
                box(
                    bx1 + DORM_WALL,
                    by1 + DORM_WALL,
                    FLOOR_Z1,
                    bx2 - DORM_WALL,
                    SDORM_STAIR_Y1,
                    FLOOR_Z2,
                    Textures.GROUND,
                    tt=Textures.ROAD,
                ),
                box(
                    bx1 + DORM_WALL,
                    SDORM_STAIR_Y2,
                    FLOOR_Z1,
                    bx2 - DORM_WALL,
                    by2 - DORM_WALL,
                    FLOOR_Z2,
                    Textures.GROUND,
                    tt=Textures.ROAD,
                ),
                box(
                    SDORM_STAIR_X2,
                    SDORM_STAIR_Y1,
                    FLOOR_Z1,
                    bx2 - DORM_WALL,
                    SDORM_STAIR_Y2,
                    FLOOR_Z2,
                    Textures.GROUND,
                    tt=Textures.ROAD,
                ),
            ]
            # Descending steps: lowest at the west (door) end at the tunnel floor
            # (FLOOR_Z2 - SDORM_LIFT in local coords), rising to the dorm floor.
            for i in range(SDORM_STAIR_N):
                brushes.append(
                    box(
                        SDORM_STAIR_X1 + i * SDORM_STAIR_RUN,
                        SDORM_STAIR_Y1,
                        FLOOR_Z2 - SDORM_LIFT,
                        SDORM_STAIR_X1 + (i + 1) * SDORM_STAIR_RUN,
                        SDORM_STAIR_Y2,
                        (i + 1) * SDORM_STAIR_RISE - SDORM_LIFT,
                        Textures.GROUND,
                        tt=Textures.ROAD,
                    )
                )
        else:
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
                zb,
                cx + DORM_WIN_HW,
                zt,
            )
            for _, zb, zt in dorm_window_levels(1)
        ]
        brushes.extend(
            layered_wall(
                bx1,
                by1,
                FLOOR_Z2,
                bx2,
                by1 + DORM_WALL,
                FLOOR_Z2 + DORM_H,
                ([] if door_lo else wxz() + mid_wxz)
                + ([dorm_door_open] if door_lo else []),
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
                ([] if door_hi else wxz_north() + mid_wxz)
                + ([dorm_door_open] if door_hi else []),
                "city2_1",
            )
        )
        cy = (by1 + by2) // 2
        brushes.extend(
            layered_wall_y(
                by1 + DORM_WALL,
                bx1,
                FLOOR_Z2,
                by2 - DORM_WALL,
                bx1 + DORM_WALL,
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
                "city2_1",
            )
        )
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
            chim_x1, chim_x2 = (
                cx + 80,
                cx + 80 + chw * 2,
            )  # well east of ridge to avoid BSP slope issues
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

            # No deck — chimney is well east of the ridge so slopes meet cleanly.
            brushes += [
                ramp_slab(  # west slope — full span, chimney is east of ridge
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
                ramp_slab(  # east slope, south of chimney bay
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
                ramp_slab(  # east slope, north of chimney bay
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
                ramp_slab(  # east slope, chimney bay, west of shaft
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
                ramp_slab(  # east slope, chimney bay, east of shaft
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
        # Window frames — south face (door wall has no windows)
        if not door_lo:
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
        # Window frames — north face (door wall has no windows)
        if not door_hi:
            for xl, zb, xr, zt in wxz_north():
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
        # Window frames — west face (floor 0 buried by hillside after terrace lift)
        for yl, zb, yr, zt in wyz_west():
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
        # Door frame — west face tunnel entrance
        brushes += win_frame_ywall(
            cy - DORM_INNER_DOOR_HW,
            cy + DORM_INNER_DOOR_HW,
            FLOOR_Z2 - SDORM_LIFT,
            FLOOR_Z2,
            bx1,
            +1,
            Textures.GABLE,
            fw=8,
            fd=DORM_WALL,
            margin=DORM_WIN_MARGIN,
            crossbar=False,
            bottom=False,
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
            [
                b.translated(0, 0, SDORM_LIFT)
                for b in make_south_bldg(
                    DORM_SOUTH1_Y1,
                    DORM_SOUTH1_Y2,
                    slat_lo=True,
                    chimney=True,
                    door_hi=True,
                    stairwell=True,
                )
            ],
        )
    )
    ENTITIES.append(
        brush_ent(
            "func_detail",
            [
                b.translated(0, 0, SDORM_LIFT)
                for b in make_south_bldg(
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
        )
    )

    # ── Threshold floors across the inter-building doorways (fill the wall seam) ──
    for seam_y, seam_lift in ((DORM_NORTH_Y1, 0), (DORM_SOUTH1_Y2, SDORM_LIFT)):
        BRUSHES.append(
            box(
                DORM_CX - DORM_INNER_DOOR_HW,
                seam_y - DORM_WALL,
                FLOOR_Z1 + seam_lift,
                DORM_CX + DORM_INNER_DOOR_HW,
                seam_y + DORM_WALL,
                FLOOR_Z2 + seam_lift,
                Textures.GROUND,
                tt=Textures.ROAD,
            )
        )

    # ── Underground tunnel — full west strip from world west wall to buildings ──
    # Extends from BRIDGE_X1 (inner face of the west sky-wall) to DORM_X1 (building
    # west face) across the full N-S span of both dorm clusters and the gap between
    # them.  Floor is at FLOOR_Z2, ceiling at SDORM_LIFT / SDORM_LIFT+TUNN_T.
    # Above the ceiling a sloped backfill slab (at BRIDGE_DZ2 on the west side,
    # grading down to emb_zt_tunn_e at DORM_X1) fills the hillside; streets.py no
    # longer places any embankment in the BRIDGE_X1-to-DORM_X1 X-range for these
    # Y segments since the tunnel now owns the whole strip.
    DORM_NORTH2_Y1_tunn = DORM_NORTH_Y1 - (DORM_NORTH_Y2 - DORM_NORTH_Y1)
    gap_y1, gap_y2 = DORM_SOUTH2_Y2, DORM_NORTH2_Y1_tunn

    for seg_y1, seg_y2, tunn_brushes in [
        # South flat section — fully underground under the south dorm pair
        (
            DORM_SOUTH1_Y1,
            DORM_SOUTH2_Y2,
            [
                # Floor — extends to world west wall
                box(
                    BRIDGE_X1,
                    DORM_SOUTH1_Y1,
                    FLOOR_Z1,
                    TUNN_X2,
                    DORM_SOUTH2_Y2,
                    FLOOR_Z2,
                    Textures.GROUND,
                ),
                # Wedge ceiling — underside slopes from BRIDGE_DZ2-TUNN_T (west) to
                # SDORM_LIFT (east). Top slopes from BRIDGE_DZ2 (west wall) down to
                # SDORM_LIFT (east), tapering to a knife edge flush with the south
                # terrace so the hill reads as a clean slope with no wedge poking
                # above the terrace; the dorm interior/terrace are untouched.
                ramp_slab(
                    BRIDGE_X1,
                    TUNN_X2,
                    DORM_SOUTH1_Y1,
                    DORM_SOUTH2_Y2,
                    BRIDGE_DZ2 - TUNN_T,
                    SDORM_LIFT,
                    BRIDGE_DZ2,
                    SDORM_LIFT,
                    Textures.GROUND,
                ),
            ],
        ),
        # North flat section — fully underground under the north dorm pair
        (
            DORM_NORTH2_Y1_tunn,
            DORM_NORTH_Y2,
            [
                # Floor — extends to world west wall
                box(
                    BRIDGE_X1,
                    DORM_NORTH2_Y1_tunn,
                    FLOOR_Z1,
                    TUNN_X2,
                    DORM_NORTH_Y2,
                    FLOOR_Z2,
                    Textures.GROUND,
                ),
                # Wedge ceiling — same profile as the south section.
                ramp_slab(
                    BRIDGE_X1,
                    TUNN_X2,
                    DORM_NORTH2_Y1_tunn,
                    DORM_NORTH_Y2,
                    BRIDGE_DZ2 - TUNN_T,
                    SDORM_LIFT,
                    BRIDGE_DZ2,
                    emb_zt_tunn_e,
                    Textures.GROUND,
                ),
            ],
        ),
    ]:
        BRUSHES.extend(tunn_brushes)

    # Gap section — open tunnel running from world west wall through the gap between clusters
    BRUSHES.append(
        box(BRIDGE_X1, gap_y1, FLOOR_Z1, TUNN_X2, gap_y2, FLOOR_Z2, Textures.GROUND)
    )
    # Wedge ceiling for the gap section — same profile as south/north.
    # ts=SKY: the south gable end at gap_y1 is partially exposed above the
    # south section's knife edge (128 vs 177); sky texture keeps it invisible.
    BRUSHES.append(
        ramp_slab(
            BRIDGE_X1,
            TUNN_X2,
            gap_y1,
            gap_y2,
            BRIDGE_DZ2 - TUNN_T,
            SDORM_LIFT,
            BRIDGE_DZ2,
            emb_zt_tunn_e,
            Textures.GROUND,
            ts=Textures.SKY,
        )
    )

    # North extension — from north building's north face to the world north wall.
    # Same wedge-ceiling profile as the other sections; no buildings above, just ramp.
    BRUSHES.append(
        box(
            BRIDGE_X1,
            DORM_NORTH_Y2,
            FLOOR_Z1,
            TUNN_X2,
            CHARLES_Y2,
            FLOOR_Z2,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        ramp_slab(
            BRIDGE_X1,
            TUNN_X2,
            DORM_NORTH_Y2,
            CHARLES_Y2,
            BRIDGE_DZ2 - TUNN_T,
            SDORM_LIFT,
            BRIDGE_DZ2,
            emb_zt_tunn_e,
            Textures.GROUND,
        )
    )

    # ── Lights for the west-side underground tunnel space ────────────────────
    # Evenly-spaced along the full N-S extent of the tunnel (DORM_SOUTH1_Y1 to
    # CHARLES_Y2), centred in the X width of the tunnel, at mid-height.
    _tunn_light_x = (BRIDGE_X1 + DORM_X1) // 2  # centre of full tunnel width
    _tunn_light_z = SDORM_LIFT // 2  # mid-height between floor (0) and ceiling (128)
    _tunn_y_start = DORM_SOUTH1_Y1 + 200  # 200 units from south end
    _tunn_y_end = CHARLES_Y2 - 200  # 200 units from north end
    _tunn_light_count = 7
    for _i in range(_tunn_light_count):
        _ly = _tunn_y_start + (_tunn_y_end - _tunn_y_start) * _i // (
            _tunn_light_count - 1
        )
        ENTITIES.append(
            ent("light", origin=f"{_tunn_light_x} {_ly} {_tunn_light_z}", light="220")
        )

    # Iron fence along east face of west buildings ──────────────────────────
    fence_brushes = []

    def fence_base_at(y):
        """Iron-fence base Z: on the raised terrace south of the brick wall's
        south pillar, declining to grade between the pillar and the north side of
        the bridge so the fence stays connected, then flat at grade to the north."""
        if y <= SDORM_SLOPE_Y_S:
            return FLOOR_Z2 + SDORM_LIFT
        if y >= SDORM_SLOPE_Y_N:
            return FLOOR_Z2
        frac = (SDORM_SLOPE_Y_N - y) / (SDORM_SLOPE_Y_N - SDORM_SLOPE_Y_S)
        return FLOOR_Z2 + round(SDORM_LIFT * frac)

    # Top rail — flat over the two level runs, sloped through the decline band.
    rail_lo, rail_hi = FENCE_H - 28, FENCE_H - 26
    for ry1, ry2 in [(CHARLES_Y1, SDORM_SLOPE_Y_S), (SDORM_SLOPE_Y_N, CHARLES_Y2)]:
        b = fence_base_at((ry1 + ry2) // 2)
        fence_brushes.append(
            box(FENCE_X1, ry1, b + rail_lo, FENCE_X2, ry2, b + rail_hi, FENCE_TEX)
        )
    bs, bn = fence_base_at(SDORM_SLOPE_Y_S), fence_base_at(SDORM_SLOPE_Y_N)
    fence_brushes.append(
        ramp_slab_y(
            FENCE_X1,
            FENCE_X2,
            SDORM_SLOPE_Y_S,
            SDORM_SLOPE_Y_N,
            bs + rail_lo,
            bn + rail_lo,
            bs + rail_hi,
            bn + rail_hi,
            FENCE_TEX,
        )
    )
    # Pickets — thin (2 wide) with thick posts (8 wide) every 10th; base follows
    # the terrace/decline so each picket meets the ground.
    picket_y = CHARLES_Y1
    picket_index = 0
    while picket_y + 2 <= CHARLES_Y2:
        picket_width = 8 if picket_index % 10 == 0 else 2
        fence_base = fence_base_at(picket_y)
        fence_brushes.append(
            box(
                FENCE_X1,
                picket_y,
                fence_base,
                FENCE_X2,
                picket_y + picket_width,
                fence_base + FENCE_H,
                FENCE_TEX,
            )
        )
        picket_y += FENCE_SPACING
        picket_index += 1
    if fence_brushes:
        ENTITIES.append(brush_ent("func_detail", fence_brushes))

    # ── West brick wall — runs from dorm 2 north face to bridge pier, with door ──
    # Door is centered 160 units north of dorm 2; pillars and iron fence are detail.
    wall_hw = DORM_BRICK_WALL_HALF_W  # half-thickness (thinner than pier)
    wall_start_y = DORM_SOUTH2_Y2  # wall stops at north face of dorm 2
    s_door_y = DORM_SOUTH2_Y2 + DORM_DOOR_OFF
    # Gate opening now sits on the raised terrace (its sill is buried in the pad);
    # the wall top stays at the bridge deck so the wall just reads as shorter.
    gate_base = FLOOR_Z2 + SDORM_LIFT
    gate_top = gate_base + DORM_BRICK_GATE_H
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
            gate_top,
            DORM_PIER_X + wall_hw,
            s_door_y + DORM_DOOR_W // 2,
            BRIDGE_DZ2,
            "city2_1",
        )
    )
    # Brick pillars + iron fence (func_detail — non-sealing)
    wall_detail = []
    pillar_w = DORM_BRICK_PILLAR_W
    pillar_proud = DORM_BRICK_PILLAR_PROUD
    pillar_h = BRIDGE_DZ2 + DORM_BRICK_PILLAR_H_OFFSET
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
        # Base extends to grade so the pillar still meets the ground where the
        # wall→fence strip declines north of the south pillar.
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

    # ── Raised stone walkway: narrow strip set off the dorm face (sits just
    #    inside the fence), with a spur running north to the brick-wall door ────
    WALK_X2 = (
        FENCE_X1 - DORM_FRONT_WALKWAY_FENCE_OFFSET
    )  # outer edge, a little inside the fence line
    WALK_X1 = (
        WALK_X2 - DORM_FRONT_WALKWAY_W
    )  # narrow strip, leaving a gap to the dorm face
    walk = [
        # Frontage parallel to the dorm east face
        box(
            WALK_X1,
            DORM_SOUTH1_Y1,
            FLOOR_Z2 + SDORM_LIFT,
            WALK_X2,
            DORM_SOUTH2_Y2,
            FLOOR_Z2 + SDORM_LIFT + DORM_FRONT_WALKWAY_H,
            Textures.STONE,
        ),
        # Spur north from the dorm corner to the brick-wall door (east side of wall)
        box(
            DORM_PIER_X + wall_hw,
            DORM_SOUTH2_Y2,
            FLOOR_Z2 + SDORM_LIFT,
            WALK_X2,
            door_north,
            FLOOR_Z2 + SDORM_LIFT + DORM_FRONT_WALKWAY_H,
            Textures.STONE,
        ),
    ]
    ENTITIES.append(brush_ent("func_detail", walk))

    return BRUSHES, ENTITIES
