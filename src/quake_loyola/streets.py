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
    KNOTT_DRIVEWAY_JCX_W,
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
    WEST_CAMPUS_ENABLED,
    WEST_CAMPUS_ENABLED_DORMS,
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
    """Punch the manhole opening (MANHOLE_X/Y/R) through any thin surface
    layer detail brush (road, lane stripes, sidewalk panels, etc.) whose
    footprint overlaps it. Several independent constructs — Charles St's
    lane fills, Ennis Road's lanes (which physically overlap Charles St at
    this intersection), and the dashed parking-lane stripe fills — can each
    place a separate solid slab over the same spot, so cutting one
    construct's brush isn't enough; sweeping every DETAIL_BRUSHES entry once
    here catches all of them without needing a manual edit at each call
    site. Only plain axis-aligned box slabs sitting in the thin road-surface
    Z-band are touched; anything taller (curbs, walls, ramps) is left alone.

    Two cases, based on how a brush's footprint relates to the circle:
      - Entirely inside the circle (all 4 corners within radius) -> drop the
        brush outright, nothing of it survives the hole.
      - Any other overlap with the circle's bounding square -> run the
        square-cut + circular-fan-fill routine (box_with_round_hole). The
        fan-fill clamps each circle vertex into the brush's own bounds, so
        it stays well-defined even when the brush is narrower than the
        circle's diameter (e.g. a ~94-unit road lane against a 128-unit
        hole) or doesn't fully contain the circle's centre.
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
    """Return the Ennis entrance/wall details that belong with west-campus geometry."""
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
        # Flame + light above the brick cup, matching the Charles St lamp posts
        pillar_flame_z = pillar_apex_z + 20
        entities.extend(torch_flame(ennis_pil_cx, pillar_y, pillar_flame_z))

    ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    bwex2 = ENNIS_GATE_X1
    # Short brick wall moved north, clear of the sidewalk squares it used to
    # run through.
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
    # Iron fence on top of the short brick wall — same decorative rectangular
    # "iron square" panel motif (outer + inner frame, mounting feet dropping
    # onto the brick top) as the adjacent iron gate run connected at this
    # wall's east end, just laid out along X instead of Y since this wall
    # segment runs east/west instead of north/south.
    sw_tex = Textures.FENCE
    sw_brick_top_z = FLOOR_Z2 + ENNIS_WALL_H
    sw_panel_y1 = ENNIS_SHORT_WALL_NY - ENNIS_GATE_FENCE_BAR_T
    sw_panel_y2 = ENNIS_SHORT_WALL_NY
    sw_panel_z1 = sw_brick_top_z + ENNIS_PANEL_MOUNT_FOOT_DROP
    sw_panel_z_center = sw_panel_z1 + ENNIS_PANEL_OUTER_H // 2
    # This wall segment is shorter than the main gate run, so its panels are
    # narrower to fit three (instead of the main gate's width) in the
    # available space, keeping the same frame thickness on each side.
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
        # Mounting feet dropping onto the brick top, same as the adjacent gate.
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
        # Two small decorative horizontal iron bars bridging the gap between
        # adjacent panels, matching the adjacent gate's connector treatment.
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
        # Diagonal iron cross-brace bar, sheared along X as a function of Z
        # (height), flat through the panel's Y depth — same shape as the
        # adjacent gate's arch post cross-braces, just built along the other axis.
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
        # U-shaped arched iron fence post bookending the panel run, matching
        # the adjacent gate's separator posts.
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
        # Decorative X cross-brace filling the opening between the legs,
        # below the arch spring line.
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

    # Leading arch post right next to the wall's own corner cap post
    # (bw_cx/bw_cy, built further below), same offset the main gate run uses
    # from its own corner post, then a connector into the first panel.
    sw_panel_z2_o = sw_panel_z_center + ENNIS_PANEL_OUTER_H // 2
    sw_arch_post_lead_x = (
        ennis_wall_x1 + ENNIS_WALL_T // 2 + ENNIS_WALL_PILLAR_HW + ENNIS_GATE_PILLAR_GAP
    )
    sw_add_arch_post(sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W // 2)
    sw_cursor_x = sw_arch_post_lead_x + ENNIS_GATE_PILLAR_W
    sw_gap_x1 = sw_cursor_x
    sw_cursor_x += ENNIS_GATE_PILLAR_GAP
    sw_add_connector(sw_gap_x1, sw_cursor_x)

    # Three narrower panels in the remaining run (east of the leading arch
    # post) to match the adjacent gate's three-square rhythm, with a
    # connector filling every inter-panel gap. The run starts immediately
    # after the leading post's connector (no leading margin) so the panel
    # fence connects directly to it instead of leaving an unfenced gap; any
    # leftover space falls at the east end instead.
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
    # Trailing bookend arch post closing out the east end of the run,
    # matching the leading post at the west end (and the main gate run's own
    # trailing bookend), with a connector tying it to the last panel.
    sw_trailing_gap_x1 = sw_run_x1 + sw_run_w
    sw_trailing_gap_x2 = sw_trailing_gap_x1 + ENNIS_GATE_PILLAR_GAP
    sw_add_connector(sw_trailing_gap_x1, sw_trailing_gap_x2)
    sw_add_arch_post(sw_trailing_gap_x2 + ENNIS_GATE_PILLAR_W // 2)
    # Small section of iron fence bridging the short wall's east end down to
    # the main east iron gate's baseline (east_gate_y1/y2 below), where the
    # small brick return wall used to be. Same treatment as the connector
    # that rejoins the shifted picket run to the brick wall further north:
    # thick end posts at the wall and gate sides, a thin picket post
    # centered in between, and a top rail spanning the whole gap.
    fence_bridge_x1 = bwex2 - ENNIS_WALL_T
    fence_bridge_x2 = bwex2
    # Matches east_gate_y1/y2's formula below (not yet computed at this point
    # in the function).
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
    # Fixed dozen-panel decorative iron gate: 12 rectangular panels grouped
    # into 6 pairs. A U-shaped iron arch post bookends the run (one at the
    # very south start, one at the very north end) and separates every pair
    # in between. The run starts clear of the existing brick/cement corner
    # cap pillar at the Ennis Rd corner (bw_cx/bw_cy below) so the two don't
    # overlap. The brick wall's north end (bw_mid_y) is sized to exactly fit
    # this run, after which the plain picket fence continues to the world edge.
    # The wall/run is anchored to ENNIS_SHORT_WALL_NY (not the older
    # ENNIS_WALL_NY) so it stays extended north, flush with the corner post.
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

    # Plain picket run sits ENNIS_GATE_FENCE_WEST_SHIFT west of where it used to
    # butt directly against the brick wall, so a short post + cross-rail
    # connector below rejoins the two at the south end of the run.
    gate_fence_x1 = ennis_wall_x1 + ENNIS_WALL_T // 2 - 1 - ENNIS_GATE_FENCE_WEST_SHIFT
    gate_fence_x2 = gate_fence_x1 + ENNIS_GATE_FENCE_BAR_T
    gate_fence_tex = Textures.FENCE
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

    # Reconnect the shifted picket run to the brick wall at its south end:
    # thick end posts at the fence and wall sides, a thin picket post
    # centered in between, and a top rail spanning the whole gap — same
    # treatment as a regular short fence section.
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

    def add_arch_post(center_y):
        # Arched iron fence post: two vertical legs topped with a rounded
        # arch (rin/rout ring), slightly taller overall than the panels it
        # separates, in place of a flat crossbar.
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
        # between adjacent panels/arch posts, matching the real fence's look.
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
    # Leading bookend arch post, then a gap into the first panel.
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
        # An arch post follows every pair — the interior separators, and (on
        # the last pair) the trailing bookend post that closes out the run.
        gap_y1 = cursor_y
        cursor_y += ENNIS_GATE_PILLAR_GAP
        add_connector(gap_y1, cursor_y)
        add_arch_post(cursor_y + ENNIS_GATE_PILLAR_W // 2)
        cursor_y += ENNIS_GATE_PILLAR_W
        gap_y1 = cursor_y
        cursor_y += ENNIS_GATE_PILLAR_GAP
        # Skip the connector tie after the trailing (north) bookend post —
        # it would otherwise reach toward the plain picket fence, which
        # doesn't share the same decorative style.
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
    # Straight span connects to the east face of the west pillar and the
    # west face of the middle pillar, rather than skewering through their
    # centres.
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
    # Wall extension east of the original end pillar, curving in a shallow
    # semi-circular bulge — echoes the north curb's bump-out below it (same
    # overall length, and the same depth-to-length ratio: half as deep as
    # long) so the wall visually rhymes with the curve instead of running
    # straight past it. Built the same way as the curb bulge: a chord-based
    # polygon approximation, where each segment's boundary points sit
    # exactly on the true elliptical curve and connect seamlessly to their
    # neighbours. Depth is zero exactly at the drawn span's own two ends —
    # the east face of the middle pillar and the west face of the new end
    # pillar + cap + lamp post at ENNIS_CEMENT_X2_EXT — so the curve
    # connects flush to both pillar faces instead of leaving a gap.
    ENNIS_CEMENT_X2_EXT = ENNIS_CEMENT_X2 + ENNIS_CURB_BULGE_LEN
    _wall_cap_z1 = FLOOR_Z2 + cement_wall_height
    _wall_cap_z2 = _wall_cap_z1 + ENNIS_CEMENT_WALL_CAP_H
    _wall_bulge_draw_x1 = ENNIS_CEMENT_X2 + cement_wall_pillar_half_width
    _wall_bulge_draw_x2 = ENNIS_CEMENT_X2_EXT - cement_wall_pillar_half_width
    _wall_bulge_cx = (_wall_bulge_draw_x1 + _wall_bulge_draw_x2) / 2
    _wall_bulge_half_len = (_wall_bulge_draw_x2 - _wall_bulge_draw_x1) / 2
    _wall_bulge_depth = _wall_bulge_half_len / 2  # half as deep as long, like the curb

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
        # Wall band quad (south1, south2, north2, north1), split into 2
        # triangles like the curb — no stair-stepping between segments.
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
        # Cap quad — same curve, overhanging both edges as usual.
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
            # Flame + light above the lamp post, matching the Charles St lamp posts
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

    # Straight-run extension east of the curved bulge, continuing all the way
    # to the world's east sealing wall. This corridor (immediately north of
    # Ennis Road's curb, south of where ne_terrain.py's real elevation data
    # begins) is deliberately kept flat/flush the whole way — see that
    # module's docstring: the row bordering the curb is tied to a constant
    # height, with the rising hill only starting further north — so a flat
    # wall at cement_wall_height needs no terrain-following logic here.
    # Pillars repeat at roughly ENNIS_CEMENT_WALL_PILLAR_SPACING, alternating
    # every other capstone with a lamp post; the pillar at ENNIS_CEMENT_X2_EXT
    # already has one, so the alternation continues from there (no lamp,
    # lamp, no lamp, ...).
    _ext_run_x1 = ENNIS_CEMENT_X2_EXT
    _ext_run_x2 = WORLD_X2 - WALL_T
    _ext_run_len = _ext_run_x2 - _ext_run_x1
    _ext_pillar_count = round(_ext_run_len / ENNIS_CEMENT_WALL_PILLAR_SPACING)
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
    # ════════════════════════════════════════════════════════════════════════════════
    # RECTANGULAR WORLD SHELL — floor, 4 outer walls, sky ceiling
    # ════════════════════════════════════════════════════════════════════════════════
    # Tunnel-portal wall faces (below) show ground only when the west-campus
    # hillside/embankment geometry that they're shaped around is actually
    # present (built by west_campus.py); with WEST_CAMPUS_ENABLED_DORMS off,
    # those inner faces should read as sky, regardless of
    # STREETS_ENABLED_DETAILS.
    _tunnel_wall_tex = (
        Textures.GROUND
        if (WEST_CAMPUS_ENABLED or WEST_CAMPUS_ENABLED_DORMS)
        else Textures.SKY
    )
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
    )  # floor — punched with the manhole opening down to the basement (see
    # basement.py, which cuts the matching hole through its own ceiling slab
    # immediately below)
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
    if not STREETS_ENABLED_DETAILS:
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

    def ranges_excluding(v1, v2, ex1, ex2):
        """Split [v1, v2) into the pieces remaining after excluding [ex1, ex2)."""
        ranges = []
        if ex1 > v1:
            ranges.append((v1, min(ex1, v2)))
        if ex2 < v2:
            ranges.append((max(ex2, v1), v2))
        return ranges

    # ── Charles St pedestrian crossing band — on the SE corner of the
    # Charles/Ennis intersection, the corner closest to the pedestrian bridge.
    # Carved out of the road surface and lane-marking brushes below (see
    # ranges_excluding() calls) so the crosswalk stripes sit flush with the
    # road, matching the centerline/parking-lane stripes.
    CHARLES_CROSSING_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
    CHARLES_CROSSING_Y1 = CHARLES_CROSSING_Y2 - CROSSWALK_LEN
    # Midpoint of the crossing — the west sidewalk north of the bridge gives
    # way to curb-and-ground up to this point (see "West sidewalk" below).
    CHARLES_CROSSING_MID = (CHARLES_CROSSING_Y1 + CHARLES_CROSSING_Y2) / 2

    # ── Ennis Road (E-W, parallel to bridge, north side) ──
    # Runs from Charles Street west edge (ROAD_X1) east to the world wall, dead-ending there.
    # Half as wide as Charles Street (512/2=256 total → HW=128), north of bridge.
    ENNIS_X1 = ROAD_X1  # start at west edge of Charles St to form T-junction
    ENNIS_X2 = WORLD_X2_EXT - WALL_T  # dead-end at east world wall
    # Back road corridor X extents — defined here for road/curb brush splits below

    # ── Ennis Road pedestrian crossing band — at the entrance from the
    # Charles St east sidewalk, lined up with the sidewalk's own width
    # (ROAD_X2..ROAD_X2+CHARLES_WALK_W). Carved out of the road/curb/centerline
    # brushes below so the crosswalk stripes sit flush with the road.
    ENNIS_CROSSING_X1 = ROAD_X2
    ENNIS_CROSSING_X2 = ROAD_X2 + CHARLES_WALK_W

    # Charles St curb-to-curb models 2 travel lanes (one each direction),
    # divided by a centre double-yellow (no-passing) line and a single solid
    # white line on each side marking the outer edge of each travel lane —
    # see docs/reference.rst "Charles St width validation". Road surface
    # split into 4 equal-width slabs, leaving narrow slots for the centre
    # divider and the two lane-line stripes, so all lanes come out an equal
    # width, evenly spaced across the road rather than a fixed lane width.
    # ROAD_CX is the midpoint of the curb-to-curb width (not a fixed X=0) so
    # the centre divider/lanes stay correctly centred automatically even when
    # ROAD_X1/ROAD_X2 aren't mirror images of each other (e.g. after widening
    # Charles St to only one side).
    ROAD_CX = (ROAD_X1 + ROAD_X2) / 2
    WEST_LANE_LINE_X = (ROAD_X1 + ROAD_CX - STREET_DIV_HW) / 2
    EAST_LANE_LINE_X = (ROAD_CX + STREET_DIV_HW + ROAD_X2) / 2
    for lane_x1, lane_x2 in (
        (ROAD_X1, WEST_LANE_LINE_X - STREET_DIV_LINE_HW),  # west outer lane
        (
            WEST_LANE_LINE_X + STREET_DIV_LINE_HW,
            ROAD_CX - STREET_DIV_HW,
        ),  # west inner lane
        (
            ROAD_CX + STREET_DIV_HW,
            EAST_LANE_LINE_X - STREET_DIV_LINE_HW,
        ),  # east inner lane
        (EAST_LANE_LINE_X + STREET_DIV_LINE_HW, ROAD_X2),  # east outer lane
    ):
        for lane_y1, lane_y2 in ranges_excluding(
            CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
        ):
            # The manhole opening (MANHOLE_X/Y/R) falls in the east outer
            # lane — the hole through this slab (and any other overlapping
            # decorative layer at this intersection) is punched generically
            # further down (see punch_manhole_detail sweep over
            # DETAIL_BRUSHES), so just build the plain slab here.
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

    # ── Sidewalk slab helpers — tile sidewalks into concrete panels with
    # expansion-joint gaps (same technique as knott_terrain.py's sloped slabs).
    _SW_SLAB_LEN = 80  # matches CHARLES_WALK_W so panels are square (80×80)
    _SW_GAP = 2  # expansion-joint width

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
        """Tile a flat N-S sidewalk strip (y1..y2) as individual panels.

        `tile_overrides`, if given, is a list of (y_start, tex) pairs — any
        panel whose starting Y matches one gets that texture instead of the
        default `tex`, for one-off accent squares without disturbing the
        rest of the strip's tiling.

        Consecutive stn_f14_wht1 (Textures.WHITE_STONE), mulch
        (Textures.MULCH), or ground (Textures.GROUND) panels are merged
        into a single continuous slab, closing the expansion-joint gaps
        between them — those materials are meant to read as one seamless
        surface, unlike the jointed cement squares.
        """
        _seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
        step = _SW_SLAB_LEN + _SW_GAP
        segments = []  # [seg_y1, seg_y2, tex] — merged run bounds
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
        """Tile a flat E-W sidewalk strip (x1..x2) as individual panels.

        `tex_from_x`, if given, is an (x_threshold, tex) pair — any panel
        starting at or east of `x_threshold` uses that texture instead of
        the default `tex`.

        `tex_ranges`, if given, is a list of (range_x1, range_x2, tex) or
        (range_x1, range_x2, tex, tt_params) entries — any panel overlapping
        [range_x1, range_x2) uses that texture (and tt_params, if given, in
        place of the call's default) for the overlapping portion (splitting
        the panel at the range boundary if it only partially overlaps),
        instead of the default `tex`/`tt_params`. Takes priority over
        `tex_from_x`. A 5th element, `y_north_inset`, shaves that many units
        off the north (y2) edge of the range and fills the sliver with the
        call's default `tex`/`tt_params` instead — useful for pulling a
        patch's north edge back a bit without affecting its x extent.

        Consecutive stn_f14_wht1 (Textures.WHITE_STONE), mulch
        (Textures.MULCH), or ground (Textures.GROUND) panels are merged
        into a single continuous slab, closing the expansion-joint gaps
        between them — those materials are meant to read as one seamless
        surface, unlike the jointed cement squares.
        """
        _seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
        step = _SW_SLAB_LEN + _SW_GAP
        segments = []  # [seg_x1, seg_x2, tex, tt_params, y_north_inset]
        x = x1
        while x < x2:
            sx2 = min(x + _SW_SLAB_LEN, x2)
            panel_tex = tex
            if tex_from_x is not None and x >= tex_from_x[0]:
                panel_tex = tex_from_x[1]
            # Sub-panels for this grid slab, split at any tex_ranges boundary
            # that falls strictly inside it.
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
                brushes.append(  # north filler sliver — default sidewalk
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

    # West sidewalk — resumes north of the crossing midpoint (curb-and-ground
    # takes over from the bridge's north side up to that point, below).
    # The first two panels (a curb-cut) sit flush with the street surface
    # height instead of the full curb height, so pedestrians stepping off
    # the crosswalk aren't met with a curb lip. The next panel is a ramp,
    # sloping the top face from the flush height back up to the full curb
    # height, so the transition back to the normal sidewalk is gradual
    # rather than an abrupt step.
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
    # West curb wall (north of the ramp) — like the Ennis Road curbs, this
    # stretch of sidewalk relies solely on the height difference against the
    # adjacent road slab, which doesn't reliably render as a visible step.
    # Add an explicit standing curb wall along the road-facing (east) edge,
    # separated from the sidewalk squares by a low flush gap so the curb
    # reads as its own distinct piece rather than the sidewalk's own edge.
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
    BRUSHES.append(  # flush gap between the sidewalk squares and the curb
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
    # South east-west curb cap — the south edge of the curb-cut (where it
    # meets the full-height curb south of the crossing, at
    # CHARLES_CROSSING_MID) needs its own explicit wall face. The two
    # brushes touch there but don't reliably render a step on their own, so
    # add a dedicated curb slab spanning the full sidewalk width, standing
    # from the flush height up to the full curb height.
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
    # West retaining wall — along the outer (west) edge of the curb-cut and
    # ramp above, since that whole strip dips below the usual curb height.
    # Without this, the drop-off there would be an open-sided ledge instead
    # of a proper curb. Constant-height wall alongside the flush curb-cut,
    # then tapers down (following the ramp's rising top face) to a small
    # residual reveal by the time the ramp meets full curb height, matching
    # the sidewalk's own texture/style.
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
    # West curb — from Charles St south edge up to the crossing midpoint
    # (covers the south section below the bridge and, per the same
    # curb-and-ground treatment, the stretch from the bridge's north side
    # up to the middle of the pedestrian crossing)
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
    # Raised ground west of curb — rock/ground texture, flush with sidewalk,
    # same south-edge-to-crossing-midpoint extent as the curb above
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
    # East sidewalk — split into two segments, trimmed CHARLES_WALK_W short of each corner.
    # Curb wall sits along the road-facing (west) edge, separated from the
    # sidewalk squares by a low flush gap (same treatment as the west
    # sidewalk and Ennis Road curbs above).
    for _seg_y1, _seg_y2, _seg_overrides in (
        (
            CHARLES_Y1,
            ENNIS_Y - ENNIS_HW - CHARLES_WALK_W,
            [(508, Textures.WHITE_STONE)],  # accent square next to the Ennis
            # south-curb white-stone/cement pair built above
        ),
        (ENNIS_Y + ENNIS_HW + CHARLES_WALK_W, CHARLES_Y2, None),
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
        BRUSHES.append(  # flush gap between the sidewalk squares and the curb
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

    # ── Ennis Road brushes ──
    # Road surface — split around centre divider slot and south curb strip (Y=776–784)
    # Ennis runs E-W (perpendicular to Charles), so its road texture is
    # rotated 90° from Charles St's orientation to keep the tech-panel grain
    # running the right way.
    ENNIS_ROAD_TT_PARAMS = "0 0 90 1 1"
    # West section (near Charles St, no curb strip here)
    for wx1, wx2 in ranges_excluding(
        ENNIS_X1, ROAD_X2 + CHARLES_WALK_W, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
    ):
        BRUSHES.append(
            box(
                wx1,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2,
                wx2,
                ENNIS_Y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
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
                tt_params=ENNIS_ROAD_TT_PARAMS,
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
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    for nx1, nx2 in ranges_excluding(
        ENNIS_X1, ENNIS_X2, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
    ):
        BRUSHES.append(
            box(
                nx1,
                ENNIS_Y + STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                nx2,
                ENNIS_Y + ENNIS_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
    # North curb — offset east by CHARLES_WALK_W to cut corner square.
    # Curb wall sits along the road-facing (south) edge, separated from the
    # sidewalk squares by a low flush gap (matches Charles St's treatment).
    _ENNIS_CURB_CAP_D = 8  # depth of the curb wall itself
    _ENNIS_CURB_GAP = 2  # width of the flush gap between curb and sidewalk
    # Corner brick/cement wall pillar (bw_cx/bw_cy in build_ennis_entrance_
    # features()) sits at the west end of this sidewalk run — recompute its
    # X center here so the white-stone patch below can extend a bit past
    # its west face, leaving plain cement sidewalk only further west.
    _ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    _bw_cx = _ennis_wall_x1 + ENNIS_WALL_T // 2
    sw_slabs_x(
        BRUSHES,
        ROAD_X2 + CHARLES_WALK_W,
        ENNIS_X2,
        ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP,
        ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK,
        tt_params=ENNIS_ROAD_TT_PARAMS,
        # White stone (stn_f14_wht1) from just west of the corner brick/
        # cement wall pillar's west face (bw_cx, at the NW corner of the
        # Charles/Ennis intersection) east to the north Ennis entrance
        # pillar, matching the white-stone accent squares on the south
        # side of Ennis. West of that, plain cement sidewalk remains. East
        # of the north pillar, mulch runs to where the main iron gate
        # ends, fronting the fence/gate; beyond that, the remaining cement
        # sidewalk becomes grass (Textures.GROUND) the rest of the way to
        # ENNIS_X2.
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
    # North curb bulge extents (defined here so the flush-gap strip below
    # can be skipped across the bulge — its cement wouldn't make sense
    # cutting across the grass island).
    _CURB_BULGE_X1 = ENNIS_CEMENT_X2
    _CURB_BULGE_LEN = ENNIS_CURB_BULGE_LEN
    _CURB_BULGE_X2 = _CURB_BULGE_X1 + _CURB_BULGE_LEN
    BRUSHES.append(  # flush gap between the sidewalk squares and the curb
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D,
            FLOOR_Z2,
            _CURB_BULGE_X1,
            ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    BRUSHES.append(  # flush gap resumes east of the bulge
        box(
            _CURB_BULGE_X2,
            ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    # North curb bulge — a rounded bump-out starting at the east-most
    # cement-wall lamp post (ENNIS_CEMENT_X2) and running east about two
    # car-lengths, then tapering back to the regular straight curb. Built
    # like the Charles/Ennis driveway-corner curb (curb_seg/tri_prism): a
    # chord-based polygon approximation, where each segment's boundary
    # points sit exactly on the true elliptical curve (half as deep into
    # the road as it is long) and connect directly to their neighbours —
    # not axis-aligned stepped boxes, which look chunky/stair-stepped by
    # comparison. The curb itself stays a constant _ENNIS_CURB_CAP_D thick
    # (like the rest of the curb) rather than becoming a solid mass — the
    # island enclosed by the curve, north of the curb wall (including the
    # flush-gap strip, since that's grass too here, not sidewalk) is filled
    # with ground/grass instead of cement.
    _CURB_BULGE_HALF_LEN = _CURB_BULGE_LEN / 2
    _CURB_BULGE_DEPTH = _CURB_BULGE_HALF_LEN / 2  # half as deep as it is long
    _CURB_BULGE_CX = (_CURB_BULGE_X1 + _CURB_BULGE_X2) / 2
    _CURB_BULGE_SEGMENTS = 24
    _CURB_BULGE_FAR_Y = ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP
    BRUSHES.append(  # north curb — straight run west of the bulge
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            _CURB_BULGE_X1,
            ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D,
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
        _outer1_y = ENNIS_Y + ENNIS_HW - _bd1
        _outer2_y = ENNIS_Y + ENNIS_HW - _bd2
        _inner1_y = _outer1_y + _ENNIS_CURB_CAP_D
        _inner2_y = _outer2_y + _ENNIS_CURB_CAP_D
        _z1, _z2 = FLOOR_Z2 + STREET_SURFACE_T, FLOOR_Z2 + CHARLES_WALK_H
        # Curb quad (outer1, outer2, inner2, inner1), split into 2 triangles
        # — chord endpoints sit exactly on the arc, so adjacent segments
        # connect seamlessly with no stair-step.
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
            # Grass island quad (inner1, inner2, far2, far1), same 2-triangle
            # split, filling from the curb's inner edge back to the flush
            # line north of it.
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
    BRUSHES.append(  # north curb — straight run east of the bulge
        box(
            _CURB_BULGE_X2,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + _ENNIS_CURB_CAP_D,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    # South curb — split into two segments with a gap for the back road entrance.
    # Curb wall sits along the road-facing (north) edge of each segment,
    # with the same flush gap treatment as the north curb above.
    # West segment's sidewalk depth is doubled (ref/gmaps-charles-ennis-satellite.png
    # shows a noticeably wider paved apron here, at the SE corner of the
    # Charles/Ennis intersection nearest the pedestrian bridge/Parkhurst
    # Dining) — only its south (far-from-road) edge moves; the north edge
    # stays flush against the existing curb/gap geometry below.
    # West segment's first (westmost) panel is split into two accent pieces
    # instead of the plain sidewalk tiling below: a white-stone strip on its
    # south side, and a square cement panel on the north side (flush against
    # the curb gap).
    _west_curb_x1 = ROAD_X2 + CHARLES_WALK_W
    _west_sw_d = CHARLES_WALK_W * 2 + 56
    _west_y1 = ENNIS_SW_EDGE + CHARLES_WALK_W - _west_sw_d
    _west_y2 = ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D - _ENNIS_CURB_GAP
    _west_north_y1 = _west_y2 - _SW_SLAB_LEN
    BRUSHES.append(  # south piece — white-stone accent slab
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
    BRUSHES.append(  # north piece — square cement sidewalk panel
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
            KNOTT.x2,
            CHARLES_WALK_W * 2 + 56,
            _west_curb_x1 + _SW_SLAB_LEN + _SW_GAP,
            (_west_curb_x1 + _SW_SLAB_LEN + _SW_GAP, Textures.WHITE_STONE),
        ),  # west segment — remaining panels (first panel built above); curb
        # wall/gap still span the full curb_x1..curb_x2 width; panels from
        # x=418 (the tile containing 470,631) and east are white-stone
        (
            KNOTT_DRIVEWAY_ES_X2,
            ENNIS_X2,
            CHARLES_WALK_W,
            KNOTT_DRIVEWAY_ES_X2,
            None,
        ),  # east segment
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
        BRUSHES.append(  # flush gap between the sidewalk squares and the curb
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
        BRUSHES.append(  # sidewalk is south of the road
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

    # ── Lane markings — dashed sfloor3_2 flush inserts in carved road slots ──────
    dash_brushes = []
    # Charles Street centre line — solid double-yellow (two stripes with a gap),
    # not dashed: real N Charles St has a no-passing double-yellow stripe here
    # (see docs/reference.rst "Charles St width validation"). Textures.CENTERLINE
    # is a placeholder stand-in until a dedicated yellow line texture is sourced.
    # The bridge deck overhead is an overpass with piers landing well outside
    # the road, so nothing in the road is ever obstructed — stripe the whole
    # length regardless of BRIDGE_ENABLED. Centred on ROAD_CX (the midpoint of
    # ROAD_X1/ROAD_X2) rather than a fixed X=0, so the stripe stays centred in
    # the roadway even when ROAD_X1/ROAD_X2 aren't mirror images of each other.
    _centerline_gap_hw = 2  # half-width of the gap between the two lines
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
    # Charles Street lane-divider stripes — single solid white line on each
    # side, at the midpoint of each half-section (from the centre divider's
    # edge to the curb), so the two travel lanes on each side of the centre
    # come out equal width, evenly spaced across the road.
    for lane_line_x in (WEST_LANE_LINE_X, EAST_LANE_LINE_X):
        # Quake tiles top-face textures by absolute world X (u = X + offset_x).
        # The two stripes sit at different world X (not necessarily mirror
        # images of each other), so without a compensating offset they'd
        # sample different parts of the texture. Shift each stripe's offset so
        # it always samples as if it were at WEST_LANE_LINE_X's position.
        tex_offset_x = WEST_LANE_LINE_X - lane_line_x
        divider_tt_params = f"{tex_offset_x} 0 0 1 1"
        # Skip/clip the portion (if any) inside the Charles St crossing
        # band — the crosswalk stripes below take over that stretch.
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
    # Charles St pedestrian crossing — thick white zebra stripes filling the
    # CHARLES_CROSSING_Y1..Y2 band carved out of the road/lane markings above;
    # gaps between stripes are filled with plain road so no void is left.
    # On the SE corner of the Charles/Ennis intersection, adjacent to (nearest)
    # the pedestrian bridge.
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
    # Ennis Road — solid single yellow centerline (replaces the old dashed
    # divider strip). The line starts at the Ennis entrance pillars (it
    # previously ran all the way to Charles St, which put it too far out
    # into the intersection); west of the pillars the carved slot is filled
    # with plain Textures.ROAD instead.
    _ennis_line_hw = STREET_DIV_LINE_HW
    _ennis_line_x1 = ENNIS_PILLAR_X1 + ENNIS_PILLAR_HW  # pillar centerline
    for gx1, gx2 in ranges_excluding(
        ROAD_X2, _ennis_line_x1, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
    ):
        dash_brushes.append(
            box(
                gx1,
                ENNIS_Y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                gx2,
                ENNIS_Y + STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
    dash_brushes.append(
        box(
            _ennis_line_x1,
            ENNIS_Y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y - _ennis_line_hw,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    dash_brushes.append(
        box(
            _ennis_line_x1,
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
            _ennis_line_x1,
            ENNIS_Y + _ennis_line_hw,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=ENNIS_ROAD_TT_PARAMS,
        )
    )
    # Ennis Road pedestrian crossing — thick white zebra stripes filling the
    # ENNIS_CROSSING_X1..X2 band carved out of the road/curb/centerline
    # brushes above; gaps between stripes are filled with plain road (rotated
    # to match Ennis's grain) so no void is left. At the Ennis entrance,
    # lined up with the Charles St east sidewalk.
    _ey = ENNIS_Y - ENNIS_HW
    _ennis_crossing_y2 = ENNIS_Y + ENNIS_HW
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
                Textures.SIDEWALK,
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
                Textures.SIDEWALK,
            )
        )

    # ── Sidewalk verges — flat ground raised flush with sidewalk height ─────────
    # (previously sloped ramps down to ground level, then a flat raised strip only
    # CHARLES_RAMP_W wide; with west campus/knott terrain still disabled, that
    # left a hard 8-unit cliff a short distance beyond the sidewalk where the
    # base world floor (FLOOR_Z2) took over.)
    #
    # The verge is a *placeholder* fill: it only needs to reach all the way out
    # to the world walls while the module that owns the real terrain on that
    # side is disabled. Once that module is re-enabled it will build its own
    # ground flush with the sidewalk, so the verge here should shrink back to
    # its original narrow strip (CHARLES_RAMP_W) to leave room for it and avoid
    # overlapping brushes.
    #   west side  -> owned by west_campus_terrain.py (WEST_CAMPUS_ENABLED_TERRAIN)
    #   east side  -> owned by knott_terrain.py (KNOTT_ENABLED_TERRAIN)
    _west_verge_x1 = (
        ROAD_X1 - CHARLES_WALK_W - CHARLES_RAMP_W
        if (WEST_CAMPUS_ENABLED or WEST_CAMPUS_ENABLED_TERRAIN)
        else WORLD_X1 + WALL_T
    )
    _east_verge_x2 = WORLD_X2_EXT - WALL_T
    # West verge — full N-S extent along west sidewalk edge
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
    # East verge — south of Ennis Road.
    # When KH terrain is enabled, knott_terrain.py owns the driveway corridor
    # (KNOTT_DRIVEWAY_CORRIDOR_X1..X2); split the verge around it so it doesn't
    # bury the road/sidewalk brushes built there.
    # The west segment's north edge is pulled back an extra CHARLES_WALK_W to
    # match the doubled-depth sidewalk built above it (SE Charles/Ennis corner).
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
    # NE quadrant verge — placeholder flat ground filling the whole area
    # north of Ennis and east of Charles St, flush with the sidewalk, for
    # while ne_terrain.py's real-elevation fill is disabled. Once
    # NE_ENABLED_TERRAIN, ne_terrain.py builds its own ground there instead
    # — skip this box entirely to avoid overlapping brushes (same
    # placeholder-shrinks-to-nothing pattern as the west/east verges above).
    if not NE_ENABLED_TERRAIN:  # Always provide a baseline ground to prevent leaks
        BRUSHES.append(
            box(
                ROAD_X2 + CHARLES_WALK_W,
                ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
                FLOOR_Z2,
                ENNIS_X2,
                CHARLES_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
    # (Ramp zone south of Ennis sidewalk covered by world floor — no fill needed)

    # Verge fill — ground between road south edge and sidewalk inner edge, flush with sidewalk
    # Split around back road corridor gap (KNOTT_DRIVEWAY_CORRIDOR_X1..KNOTT_DRIVEWAY_CORRIDOR_X2)
    # SE corner (east of back road) uses gravel3c (mulch bed)
    # A single cement patch is cut into the SW corner of the ground verge
    # (west segment only), roughly centred on (377, 724) in X and spanning
    # the full verge depth in Y (no leftover ground sliver to the north),
    # replacing the ground there.
    _VERGE_CEMENT_X1 = ROAD_X2 + CHARLES_WALK_W
    _VERGE_CEMENT_X2 = _VERGE_CEMENT_X1 + _SW_SLAB_LEN
    for vx1, vx2, vtex in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, Textures.GROUND),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2, Textures.MULCH),
    ]:
        vy1 = ENNIS_SW_EDGE + CHARLES_WALK_W
        vy2 = ENNIS_Y - ENNIS_HW - ENNIS_CURB_W
        if vtex is Textures.GROUND:
            BRUSHES.append(  # cement patch carved out of the SW corner
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
            BRUSHES.append(  # remainder east of the patch, full verge height
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

    # Ennis driveway head — with KH terrain disabled, knott_terrain.py's
    # driveway-mouth geometry occupying the corridor gap
    # (KNOTT_DRIVEWAY_CORRIDOR_X1..X2) doesn't exist, so the verge/curb strip
    # built above stops short on both sides of the gap. This is a direct port
    # of knott_terrain.py's own driveway-head sections (west/east sidewalks,
    # road patch, and rounded junction corners) — the same geometry that
    # appears there when KH terrain is enabled — restricted to the Y range
    # north of the curb line (KNOTT_DRIVEWAY_EXT_Y2) so it doesn't overlap the
    # verge/ground fills above, which already cover everything south of it.
    if not KNOTT_ENABLED_TERRAIN:
        # Sidewalk-band gap — the unconditional Ennis south-curb SIDEWALK strip
        # above (built regardless of KNOTT_ENABLED_TERRAIN) leaves a corridor
        # gap between KNOTT.x2 and KNOTT_DRIVEWAY_ES_X2 for knott_terrain.py to
        # fill; with it disabled, that band (Y: ENNIS_SW_EDGE to
        # ENNIS_SW_EDGE+CHARLES_WALK_W) was left empty. Fill it the same way
        # knott_terrain.py does: CEMENT sidewalk on each side, ROAD lane down
        # the middle.
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
        # West sidewalk — ground from the curb line up to the NW junction corner
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
        # Cement curb strip along the road edge of the ground section
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
        # East sidewalk — mulch from the curb line up to the south junction corner
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
        # Cement curb strip on the road-facing (west) edge of the mulch section
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
        # Road patch filling the driveway lane from the sidewalks' start (curb
        # line at Ennis's south sidewalk) up to Ennis road — flush with the
        # road (not raised). Previously only covered the curb-line-to-road
        # segment (KNOTT_DRIVEWAY_EXT_Y2 north), leaving the lane unpaved
        # between the two sidewalks for the stretch south of that.
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
        # ── Rounded corners where the driveway meets Ennis south (inside the
        # junction) — centers at the back-road-facing (south) corners so the
        # curved face points toward the driveway, matching the Charles/Ennis
        # corner style.
        # West junction corner: arc sweeps 0°→90°
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
                    KNOTT_DRIVEWAY_JCX_W,
                    KNOTT_DRIVEWAY_EXT_Y2,
                    KNOTT_DRIVEWAY_JCX_W + _r_inner * math.cos(t0),
                    KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t0),
                    KNOTT_DRIVEWAY_JCX_W + _r_inner * math.cos(t1),
                    KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t1),
                    FLOOR_Z2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                curb_seg(
                    KNOTT_DRIVEWAY_JCX_W,
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
        # East junction corner: arc sweeps 90°→180°
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
            ENTITIES.extend(torch_flame(lamp_x, lamp_y, flame_z))

    if DETAIL_BRUSHES:
        DETAIL_BRUSHES = punch_manhole_detail(DETAIL_BRUSHES)
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    # ── Final safety seal — giant hollow box around the entire map coordinate space ──
    # This ensures the map is sealed even if internal terrain or building geometry
    # has tiny gaps or degenerate portals that confuse qbsp.
    # seal_z1 is pinned below BASEMENT_FLOOR_Z1 (rather than FLOOR_Z1) so this
    # seal's floor sits below basement.py's sub-basement level instead of
    # floating as a stray sky slab inside its open void.
    seal_x1, seal_x2 = WORLD_X1 - 256, WORLD_X2_EXT + 256
    seal_y1, seal_y2 = WORLD_Y1 - 256, WORLD_Y2 + 256
    seal_z1, seal_z2 = BASEMENT_FLOOR_Z1 - 256, WORLD_Z2 + 512
    ST = 64  # seal thickness
    BRUSHES.extend(
        [
            box(
                seal_x1, seal_y1, seal_z1, seal_x2, seal_y2, seal_z1 + ST, Textures.SKY
            ),  # floor
            box(
                seal_x1, seal_y1, seal_z2 - ST, seal_x2, seal_y2, seal_z2, Textures.SKY
            ),  # ceiling
            box(
                seal_x1, seal_y1, seal_z1, seal_x1 + ST, seal_y2, seal_z2, Textures.SKY
            ),  # west wall
            box(
                seal_x2 - ST, seal_y1, seal_z1, seal_x2, seal_y2, seal_z2, Textures.SKY
            ),  # east wall
            box(
                seal_x1, seal_y1, seal_z1, seal_x2, seal_y1 + ST, seal_z2, Textures.SKY
            ),  # south wall
            box(
                seal_x1, seal_y2 - ST, seal_z1, seal_x2, seal_y2, seal_z2, Textures.SKY
            ),  # north wall
        ]
    )

    return BRUSHES, ENTITIES
