import math
from constants import (
    FLOOR_Z1,
    FLOOR_Z2,
    KH_X2,
    BRIDGE_ARCH_X,
    BRIDGE_DZ2,
    BRIDGE_PIL_HW,
    BRIDGE_PIL_OVERHANG,
    BRIDGE_X1,
    BRIDGE_Y1,
    BRIDGE_Y2,
    ROAD_X1,
    ROAD_X2,
    TEX_BRICK,
    TEX_CEMENT,
    TEX_GROUND,
    TEX_PILLAR,
    TEX_ROAD,
    TEX_SKY,
    TEX_WHITE_STONE,
    WALL_T,
    WORLD_X1,
    WORLD_X2,
    WORLD_Y1,
    WORLD_Y2,
    WORLD_Z2,
)
from geometry import (
    box,
    brush_ent,
    pyramid,
    ramp_slab,
    ramp_slab_y,
    tri_prism,
)


def build():
    BRUSHES = []
    ENTITIES = []
    # ════════════════════════════════════════════════════════════════════════════════
    # RECTANGULAR WORLD SHELL — floor, 4 outer walls, sky ceiling
    # ════════════════════════════════════════════════════════════════════════════════
    BRUSHES.append(
        box(WORLD_X1, WORLD_Y1, FLOOR_Z1, WORLD_X2, WORLD_Y2, FLOOR_Z2, TEX_GROUND)
    )  # floor
    BRUSHES.append(
        box(
            WORLD_X1, WORLD_Y1, FLOOR_Z1, WORLD_X1 + WALL_T, WORLD_Y2, WORLD_Z2, TEX_SKY
        )
    )  # W wall
    BRUSHES.append(
        box(
            WORLD_X2 - WALL_T, WORLD_Y1, FLOOR_Z1, WORLD_X2, WORLD_Y2, WORLD_Z2, TEX_SKY
        )
    )  # E wall
    BRUSHES.append(
        box(
            WORLD_X1, WORLD_Y2 - WALL_T, FLOOR_Z1, WORLD_X2, WORLD_Y2, WORLD_Z2, TEX_SKY
        )
    )  # N wall
    BRUSHES.append(
        box(
            WORLD_X1, WORLD_Y1, FLOOR_Z1, WORLD_X2, WORLD_Y1 + WALL_T, WORLD_Z2, TEX_SKY
        )
    )  # S wall
    BRUSHES.append(
        box(
            WORLD_X1, WORLD_Y1, WORLD_Z2 - WALL_T, WORLD_X2, WORLD_Y2, WORLD_Z2, TEX_SKY
        )
    )  # sky

    # ════════════════════════════════════════════════════════════════════════════════
    # CHARLES STREET — road surface, sidewalks, centre stripe
    # Road runs N-S (full Y); road channel E-W = ROAD_X1..ROAD_X2
    # ════════════════════════════════════════════════════════════════════════════════
    CS_Y1 = WORLD_Y1 + WALL_T
    CS_Y2 = WORLD_Y2 - WALL_T
    CS_WALK_W = 80  # sidewalk width (E-W)
    CS_WALK_H = 8  # sidewalk + curb height above road

    # ── Ennis Road (E-W, parallel to bridge, north side) ──
    # Runs from Charles Street west edge (ROAD_X1) east to the world wall, dead-ending there.
    # Half as wide as Charles Street (512/2=256 total → HW=128), north of bridge.
    EP_Y = BRIDGE_Y2 + 800  # 936: centred 800 units north of bridge north edge
    EP_HW = 160  # road half-width → 320-unit carriageway (~21 ft, matches reference)
    EP_X1 = ROAD_X1  # start at west edge of Charles St to form T-junction
    EP_X2 = WORLD_X2 - WALL_T  # dead-end at east world wall
    EP_SW_EDGE = EP_Y - EP_HW - 3 * CS_WALK_W - 32  # Ennis south sidewalk outer edge
    # Back road corridor X extents — defined here for road/curb brush splits below
    KH_BR_CORRIDOR_X1 = KH_X2  # west edge of corridor gap
    KH_BR_CORRIDOR_X2 = KH_X2 + CS_WALK_W + 2 * 128 + CS_WALK_W  # east edge
    EP_CURB_W = 8  # south Ennis curb strip width (N-S)

    # Road surface — split either side of centre divider slot (div_hw wide)
    div_hw = 4  # half-width of Charles St divider slot
    div_ep_hw = 16  # half-width of Ennis divider slot (wider for rune1_lig2 white)
    BRUSHES.append(
        box(ROAD_X1, CS_Y1, FLOOR_Z2, -div_hw, CS_Y2, FLOOR_Z2 + 2, TEX_ROAD)
    )
    BRUSHES.append(box(div_hw, CS_Y1, FLOOR_Z2, ROAD_X2, CS_Y2, FLOOR_Z2 + 2, TEX_ROAD))
    CS_SWALK_START = BRIDGE_Y2 + 200  # sidewalk starts north of bridge
    # West sidewalk — north of bridge
    BRUSHES.append(
        box(
            ROAD_X1 - CS_WALK_W,
            CS_SWALK_START,
            FLOOR_Z2,
            ROAD_X1,
            CS_Y2,
            FLOOR_Z2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )
    # West curb — south section up to sidewalk start
    BRUSHES.append(
        box(
            ROAD_X1 - 8,
            CS_Y1,
            FLOOR_Z2,
            ROAD_X1,
            CS_SWALK_START,
            FLOOR_Z2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )
    # Raised ground west of curb — rock/ground texture, flush with sidewalk
    BRUSHES.append(
        box(
            ROAD_X1 - CS_WALK_W,
            CS_Y1,
            FLOOR_Z2,
            ROAD_X1 - 8,
            CS_SWALK_START,
            FLOOR_Z2 + CS_WALK_H,
            TEX_GROUND,
        )
    )
    # East sidewalk — split into two segments, trimmed CS_WALK_W short of each corner
    BRUSHES.append(
        box(
            ROAD_X2,
            CS_Y1,
            FLOOR_Z2,
            ROAD_X2 + CS_WALK_W,
            EP_Y - EP_HW - CS_WALK_W,
            FLOOR_Z2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )
    BRUSHES.append(
        box(
            ROAD_X2,
            EP_Y + EP_HW + CS_WALK_W,
            FLOOR_Z2,
            ROAD_X2 + CS_WALK_W,
            CS_Y2,
            FLOOR_Z2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )

    # ── Ennis Road brushes ──
    # Road surface — split around centre divider slot and south curb strip (Y=776–784)
    # West section (near Charles St, no curb strip here)
    BRUSHES.append(
        box(
            EP_X1,
            EP_Y - EP_HW,
            FLOOR_Z2,
            ROAD_X2 + CS_WALK_W,
            EP_Y - div_ep_hw,
            FLOOR_Z2 + 2,
            TEX_ROAD,
        )
    )
    # Main east sections — full south extent to road edge
    for road_x1, road_x2 in [
        (ROAD_X2 + CS_WALK_W, KH_BR_CORRIDOR_X1),
        (KH_BR_CORRIDOR_X2, EP_X2),
    ]:
        BRUSHES.append(
            box(
                road_x1,
                EP_Y - EP_HW,
                FLOOR_Z2,
                road_x2,
                EP_Y - div_ep_hw,
                FLOOR_Z2 + 2,
                TEX_ROAD,
            )
        )
    # Corridor gap section (back road entrance, no curb strip)
    BRUSHES.append(
        box(
            KH_BR_CORRIDOR_X1,
            EP_Y - EP_HW,
            FLOOR_Z2,
            KH_BR_CORRIDOR_X2,
            EP_Y - div_ep_hw,
            FLOOR_Z2 + 2,
            TEX_ROAD,
        )
    )
    BRUSHES.append(
        box(EP_X1, EP_Y, FLOOR_Z2, EP_X2, EP_Y + EP_HW, FLOOR_Z2 + 2, TEX_ROAD)
    )
    # North curb — offset east by CS_WALK_W to cut corner square
    BRUSHES.append(
        box(
            ROAD_X2 + CS_WALK_W,
            EP_Y + EP_HW,
            FLOOR_Z2,
            EP_X2,
            EP_Y + EP_HW + CS_WALK_W,
            FLOOR_Z2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )
    # South curb — split into two segments with a gap for the back road entrance
    # West segment: Charles St east sidewalk to back road west sidewalk
    BRUSHES.append(
        box(
            ROAD_X2 + CS_WALK_W,
            EP_SW_EDGE,
            FLOOR_Z2,
            KH_X2,
            EP_SW_EDGE + CS_WALK_W,
            FLOOR_Z2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )
    # East segment: back road east sidewalk east to world wall
    # KH_BR_ES_X2 = KH_X2 + CS_WALK_W + 2*128 + CS_WALK_W (computed inline to avoid forward-ref)
    BRUSHES.append(
        box(
            KH_X2 + CS_WALK_W + 2 * 128 + CS_WALK_W,
            EP_SW_EDGE,
            FLOOR_Z2,
            EP_X2,
            EP_SW_EDGE + CS_WALK_W,
            FLOOR_Z2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )

    # ── Lane dividers — dashed sfloor3_2 flush inserts in carved road slots ───────
    TEX_DIVIDER = "sfloor3_2"
    ROAD_DASH_LEN = 64  # dash length
    ROAD_GAP_LEN = 64  # gap length (filled with road tex)
    # Charles Street — dashed N-S, two sections either side of bridge
    for section_y1, section_y2 in [(CS_Y1, BRIDGE_Y1), (BRIDGE_Y2, CS_Y2)]:
        divider_y = section_y1
        dash_on = True
        while divider_y < section_y2:
            next_divider_y = min(
                divider_y + (ROAD_DASH_LEN if dash_on else ROAD_GAP_LEN), section_y2
            )
            divider_tex = TEX_DIVIDER if dash_on else TEX_ROAD
            BRUSHES.append(
                box(
                    -div_hw,
                    divider_y,
                    FLOOR_Z2,
                    div_hw,
                    next_divider_y,
                    FLOOR_Z2 + 2,
                    divider_tex,
                )
            )
            divider_y = next_divider_y
            dash_on = not dash_on
    # Ennis Road — dashed E-W from Charles St east to world wall
    divider_x = ROAD_X2
    dash_on = True
    while divider_x < EP_X2:
        next_divider_x = min(
            divider_x + (ROAD_DASH_LEN if dash_on else ROAD_GAP_LEN), EP_X2
        )
        divider_tex = TEX_DIVIDER if dash_on else TEX_ROAD
        BRUSHES.append(
            box(
                divider_x,
                EP_Y - div_ep_hw,
                FLOOR_Z2,
                next_divider_x,
                EP_Y,
                FLOOR_Z2 + 2,
                divider_tex,
            )
        )
        divider_x = next_divider_x
        dash_on = not dash_on

    # ── Rounded intersection corners (Charles & Ennis) ───────────────────────────
    # Arc center at the OUTER (far) corner so the curve faces outward toward the road.
    # Each corner: road box fills the cut square, cement arc fans sit on top.
    CS_CRN_R = CS_WALK_W  # corner radius = sidewalk width
    CS_CRN_SEGS = 12  # segments per arc (12 × 7.5° = 90°)

    # SE corner: far corner is at SE of cut square
    cx_se = ROAD_X2 + CS_CRN_R
    cy_se = EP_Y - EP_HW - CS_CRN_R
    BRUSHES.append(
        box(ROAD_X2, cy_se, FLOOR_Z2, cx_se, EP_Y - EP_HW, FLOOR_Z2 + 2, TEX_ROAD)
    )
    # Arc sweeps CCW from 90° (north) to 180° (west)
    for corner_index in range(CS_CRN_SEGS):
        angle_start = math.radians(90 + corner_index * 90 / CS_CRN_SEGS)
        angle_end = math.radians(90 + (corner_index + 1) * 90 / CS_CRN_SEGS)
        arc_x0, arc_y0 = (
            cx_se + CS_CRN_R * math.cos(angle_start),
            cy_se + CS_CRN_R * math.sin(angle_start),
        )
        arc_x1, arc_y1 = (
            cx_se + CS_CRN_R * math.cos(angle_end),
            cy_se + CS_CRN_R * math.sin(angle_end),
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
                FLOOR_Z2 + CS_WALK_H,
                TEX_CEMENT,
            )
        )

    # NE corner: far corner is at NE of cut square
    cx_ne = ROAD_X2 + CS_CRN_R
    cy_ne = EP_Y + EP_HW + CS_CRN_R
    BRUSHES.append(
        box(ROAD_X2, EP_Y + EP_HW, FLOOR_Z2, cx_ne, cy_ne, FLOOR_Z2 + 2, TEX_ROAD)
    )
    # Arc sweeps CCW from 180° (west) to 270° (south)
    for corner_index in range(CS_CRN_SEGS):
        angle_start = math.radians(180 + corner_index * 90 / CS_CRN_SEGS)
        angle_end = math.radians(180 + (corner_index + 1) * 90 / CS_CRN_SEGS)
        arc_x0, arc_y0 = (
            cx_ne + CS_CRN_R * math.cos(angle_start),
            cy_ne + CS_CRN_R * math.sin(angle_start),
        )
        arc_x1, arc_y1 = (
            cx_ne + CS_CRN_R * math.cos(angle_end),
            cy_ne + CS_CRN_R * math.sin(angle_end),
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
                FLOOR_Z2 + CS_WALK_H,
                TEX_CEMENT,
            )
        )

    # ── Sidewalk ramps — smooth ground-to-sidewalk transitions ───────────────────
    CS_RAMP_W = 64  # ramp width in units

    # West ramp — slopes from ground up to west sidewalk edge (full N-S extent)
    BRUSHES.append(
        ramp_slab(
            ROAD_X1 - CS_WALK_W - CS_RAMP_W,
            ROAD_X1 - CS_WALK_W,
            CS_Y1,
            CS_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2,
            FLOOR_Z2 + CS_WALK_H,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # East ramp — south of Ennis Road
    BRUSHES.append(
        ramp_slab(
            ROAD_X2 + CS_WALK_W,
            ROAD_X2 + CS_WALK_W + CS_RAMP_W,
            CS_Y1,
            EP_SW_EDGE,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CS_WALK_H,
            FLOOR_Z2,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # East ramp — north of Ennis Road
    BRUSHES.append(
        ramp_slab(
            ROAD_X2 + CS_WALK_W,
            ROAD_X2 + CS_WALK_W + CS_RAMP_W,
            EP_Y + EP_HW + CS_WALK_W,
            CS_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CS_WALK_H,
            FLOOR_Z2,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # Ennis north ramp — slopes from north curb edge down going north
    BRUSHES.append(
        ramp_slab_y(
            ROAD_X2 + CS_WALK_W,
            EP_X2,
            EP_Y + EP_HW + CS_WALK_W,
            EP_Y + EP_HW + CS_WALK_W + CS_RAMP_W,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CS_WALK_H,
            FLOOR_Z2,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # (Ramp zone south of Ennis sidewalk covered by world floor — no fill needed)

    # Verge fill — ground between road south edge and sidewalk inner edge, flush with sidewalk
    # Split around back road corridor gap (KH_BR_CORRIDOR_X1..KH_BR_CORRIDOR_X2)
    # SE corner (east of back road) uses gravel3c (mulch bed)
    for vx1, vx2, vtex in [
        (ROAD_X2 + CS_WALK_W, KH_BR_CORRIDOR_X1, TEX_GROUND),
        (KH_BR_CORRIDOR_X2, EP_X2, "grave13c"),
    ]:
        BRUSHES.append(
            box(
                vx1,
                EP_SW_EDGE + CS_WALK_W,
                FLOOR_Z1,
                vx2,
                EP_Y - EP_HW - EP_CURB_W,
                FLOOR_Z2 + CS_WALK_H,
                vtex,
            )
        )

    # Cement curb strip — last 8 units of verge at road edge, flush with verge surface
    for vx1, vx2 in [
        (ROAD_X2 + CS_WALK_W, KH_BR_CORRIDOR_X1),
        (KH_BR_CORRIDOR_X2, EP_X2),
    ]:
        BRUSHES.append(
            box(
                vx1,
                EP_Y - EP_HW - EP_CURB_W,
                FLOOR_Z1,
                vx2,
                EP_Y - EP_HW,
                FLOOR_Z2 + CS_WALK_H,
                TEX_CEMENT,
            )
        )

    # ── Ennis Drive entrance pillars (white stone columns flanking Charles St entrance) ──
    EP_PIL_HW = 22  # pillar half-width (was 30, ×0.75)
    EP_PIL_X1 = (
        BRIDGE_ARCH_X[2] - EP_PIL_HW
    )  # align pillar centre with closest bridge pier (X=525)
    EP_PIL_X2 = BRIDGE_ARCH_X[2] + EP_PIL_HW
    EP_PIL_ZB = FLOOR_Z2
    EP_PIL_POST_H = 81  # post height (was 108, ×0.75)
    EP_PIL_CAP_OVH = 1
    EP_PIL_CAP_H = 3

    # Bell shape — cap divider + single tapered step (no flare, no tip):
    #      |  |      step 2: hw=16, h=27
    #  ====+==+====  cap:    hw=23, h=1
    #      |  |      post:   hw=22, h=81
    EP_PIL_BELL2_HW = (
        19  # tapered top section half-width (wider than before, less than post)
    )
    EP_PIL_BELL2_H = 27  # tapered top section height (was 36, ×0.75)

    for pillar_y in (EP_Y - EP_HW - EP_PIL_HW, EP_Y + EP_HW + EP_PIL_HW):
        ennis_pil_cx = EP_PIL_X1 + EP_PIL_HW  # pillar centre X
        cap_half_width = EP_PIL_HW + EP_PIL_CAP_OVH

        # Post
        base_height = EP_PIL_POST_H // 3  # bottom base = lower third of post
        # Bottom base — same width as cap, gives plinth effect
        BRUSHES.append(
            box(
                ennis_pil_cx - cap_half_width,
                pillar_y - cap_half_width,
                EP_PIL_ZB,
                ennis_pil_cx + cap_half_width,
                pillar_y + cap_half_width,
                EP_PIL_ZB + base_height,
                TEX_WHITE_STONE,
            )
        )
        # Upper post — narrower, sits on bottom base
        BRUSHES.append(
            box(
                EP_PIL_X1,
                pillar_y - EP_PIL_HW,
                EP_PIL_ZB + base_height,
                EP_PIL_X2,
                pillar_y + EP_PIL_HW,
                EP_PIL_ZB + EP_PIL_POST_H,
                TEX_WHITE_STONE,
            )
        )
        # Thin cap divider — overhangs post on all sides
        cap_z = EP_PIL_ZB + EP_PIL_POST_H
        BRUSHES.append(
            box(
                ennis_pil_cx - cap_half_width,
                pillar_y - cap_half_width,
                cap_z,
                ennis_pil_cx + cap_half_width,
                pillar_y + cap_half_width,
                cap_z + EP_PIL_CAP_H,
                TEX_WHITE_STONE,
            )
        )
        # Bell step 2 — tapered top, narrower than post
        bell2_z = cap_z + EP_PIL_CAP_H
        BRUSHES.append(
            box(
                ennis_pil_cx - EP_PIL_BELL2_HW,
                pillar_y - EP_PIL_BELL2_HW,
                bell2_z,
                ennis_pil_cx + EP_PIL_BELL2_HW,
                pillar_y + EP_PIL_BELL2_HW,
                bell2_z + EP_PIL_BELL2_H,
                TEX_WHITE_STONE,
            )
        )
        # Torch base above pyramid apex — narrow post + brick cup (matches bridge pillars)
        ennis_pillar_apex_z = bell2_z + EP_PIL_BELL2_H
        ennis_pil_cx = EP_PIL_X1 + EP_PIL_HW
        BRUSHES.append(
            box(
                ennis_pil_cx - 3,
                pillar_y - 3,
                ennis_pillar_apex_z,
                ennis_pil_cx + 3,
                pillar_y + 3,
                ennis_pillar_apex_z + 16,
                TEX_CEMENT,
            )
        )
        BRUSHES.append(
            box(
                ennis_pil_cx - 5,
                pillar_y - 5,
                ennis_pillar_apex_z + 16,
                ennis_pil_cx + 5,
                pillar_y + 5,
                ennis_pillar_apex_z + 20,
                TEX_BRICK,
            )
        )

    # ── Ennis Drive L-shaped campus boundary wall (north side of entrance) ────────
    # city2_1 brick wall from near Charles St sidewalk east to pillar, then turns north.
    # Starts with a small grass gap east of the sidewalk.
    EP_WALL_T = 8  # wall thickness
    EP_WALL_H = 96  # wall height — matches iron fence
    EP_WALL_NY = EP_Y + EP_HW + EP_PIL_HW * 2  # south face Y (flush with north pillar)
    EP_WALL_X1 = ROAD_X2 + CS_WALK_W + 48  # ~48u east of sidewalk (more grass)
    bwex2 = BRIDGE_ARCH_X[2] + EP_PIL_HW + 80  # E-W wall extends past stone pillar
    # East-running segment (south base of L)
    BRUSHES.append(
        box(
            EP_WALL_X1,
            EP_WALL_NY,
            FLOOR_Z2,
            bwex2,
            EP_WALL_NY + EP_WALL_T,
            FLOOR_Z2 + EP_WALL_H,
            "city2_1",
        )
    )
    # North-turning segment — south half brick, north half iron fence
    bw_mid_y = (EP_WALL_NY + WORLD_Y2 - WALL_T) // 2  # midpoint of north segment
    BRUSHES.append(
        box(
            EP_WALL_X1,
            EP_WALL_NY,
            FLOOR_Z2,
            EP_WALL_X1 + EP_WALL_T,
            bw_mid_y,
            FLOOR_Z2 + EP_WALL_H,
            "city2_1",
        )
    )
    # North half — iron fence matching west-side style (FENCE_* constants defined later)
    gate_fence_x1 = (
        EP_WALL_X1 + EP_WALL_T // 2 - 1
    )  # centre the pickets on the wall line
    gate_fence_x2 = gate_fence_x1 + 2
    gate_fence_height = 96
    gate_fence_spacing = 16
    gate_fence_tex = "metal4_4"
    # Top rail
    BRUSHES.append(
        box(
            gate_fence_x1,
            bw_mid_y,
            FLOOR_Z2 + gate_fence_height - 28,
            gate_fence_x2,
            WORLD_Y2 - WALL_T,
            FLOOR_Z2 + gate_fence_height - 26,
            gate_fence_tex,
        )
    )
    # Pickets
    gate_picket_y = bw_mid_y
    gate_picket_index = 0
    while gate_picket_y + 2 <= WORLD_Y2 - WALL_T:
        gate_picket_width = 8 if gate_picket_index % 10 == 0 else 2
        BRUSHES.append(
            box(
                gate_fence_x1,
                gate_picket_y,
                FLOOR_Z2,
                gate_fence_x2,
                gate_picket_y + gate_picket_width,
                FLOOR_Z2 + gate_fence_height,
                gate_fence_tex,
            )
        )
        gate_picket_y += gate_fence_spacing
        gate_picket_index += 1

    # ── Decorative iron panels on west face of brick wall, sitting ON TOP of wall ──
    # Panels protrude above wall top; rectangles are horizontal (wider than tall).
    panel_x1 = EP_WALL_X1 - 2  # protrude 2 units from west face
    panel_x2 = EP_WALL_X1
    panel_bar_thickness = 2  # bar thickness
    panel_outer_width = 48  # outer frame Y width (wide = horizontal)
    panel_outer_height = 28  # outer frame Z height (shorter than wide)
    panel_inner_width = 28  # inner frame Y width
    panel_inner_height = 12  # inner frame Z height
    panel_z1 = FLOOR_Z2 + EP_WALL_H  # panels start at wall top
    panel_z_center = panel_z1 + panel_outer_height // 2  # Z centre above wall top
    panel_spacing = panel_outer_width + 16  # centre-to-centre spacing

    # Snap bw_mid_y to the north edge of the last full panel that fits in the original half-space
    panel_available_span = bw_mid_y - EP_WALL_NY
    panel_count = max(
        1, (panel_available_span + panel_outer_width) // (panel_outer_width + 8)
    )  # at least 8-unit gap between panels
    panel_spacing = (
        panel_available_span // panel_count
    )  # evenly distribute N panels across the brick space

    # Start first panel so its south edge aligns exactly with EP_WALL_NY (no overhang)
    panel_center_y = EP_WALL_NY + panel_spacing // 2
    panels_drawn = 0
    while panels_drawn < panel_count:
        panel_width = panel_outer_width
        panel_inner_frame_width = panel_inner_width

        y1_o = panel_center_y - panel_width // 2
        y2_o = panel_center_y + panel_width // 2
        z1_o = panel_z_center - panel_outer_height // 2
        z2_o = panel_z_center + panel_outer_height // 2
        y1_i = panel_center_y - panel_inner_frame_width // 2
        y2_i = panel_center_y + panel_inner_frame_width // 2
        z1_i = panel_z_center - panel_inner_height // 2
        z2_i = panel_z_center + panel_inner_height // 2

        # Outer rectangle
        BRUSHES.append(
            box(
                panel_x1,
                y1_o,
                z1_o,
                panel_x2,
                y2_o,
                z1_o + panel_bar_thickness,
                gate_fence_tex,
            )
        )  # bottom
        BRUSHES.append(
            box(
                panel_x1,
                y1_o,
                z2_o - panel_bar_thickness,
                panel_x2,
                y2_o,
                z2_o,
                gate_fence_tex,
            )
        )  # top
        BRUSHES.append(
            box(
                panel_x1,
                y1_o,
                z1_o,
                panel_x2,
                y1_o + panel_bar_thickness,
                z2_o,
                gate_fence_tex,
            )
        )  # left
        BRUSHES.append(
            box(
                panel_x1,
                y2_o - panel_bar_thickness,
                z1_o,
                panel_x2,
                y2_o,
                z2_o,
                gate_fence_tex,
            )
        )  # right
        # Inner rectangle
        BRUSHES.append(
            box(
                panel_x1,
                y1_i,
                z1_i,
                panel_x2,
                y2_i,
                z1_i + panel_bar_thickness,
                gate_fence_tex,
            )
        )  # bottom
        BRUSHES.append(
            box(
                panel_x1,
                y1_i,
                z2_i - panel_bar_thickness,
                panel_x2,
                y2_i,
                z2_i,
                gate_fence_tex,
            )
        )  # top
        BRUSHES.append(
            box(
                panel_x1,
                y1_i,
                z1_i,
                panel_x2,
                y1_i + panel_bar_thickness,
                z2_i,
                gate_fence_tex,
            )
        )  # left
        BRUSHES.append(
            box(
                panel_x1,
                y2_i - panel_bar_thickness,
                z1_i,
                panel_x2,
                y2_i,
                z2_i,
                gate_fence_tex,
            )
        )  # right
        # Diagonal corner connectors: each inner corner → corresponding outer corner
        BRUSHES.append(
            ramp_slab_y(
                panel_x1,
                panel_x2,
                y1_o,
                y1_i,
                z1_o,
                z1_i,
                z1_o + panel_bar_thickness,
                z1_i + panel_bar_thickness,
                gate_fence_tex,
            )
        )  # bottom-left
        BRUSHES.append(
            ramp_slab_y(
                panel_x1,
                panel_x2,
                y2_i,
                y2_o,
                z1_i,
                z1_o,
                z1_i + panel_bar_thickness,
                z1_o + panel_bar_thickness,
                gate_fence_tex,
            )
        )  # bottom-right
        BRUSHES.append(
            ramp_slab_y(
                panel_x1,
                panel_x2,
                y1_o,
                y1_i,
                z2_o - panel_bar_thickness,
                z2_i - panel_bar_thickness,
                z2_o,
                z2_i,
                gate_fence_tex,
            )
        )  # top-left
        BRUSHES.append(
            ramp_slab_y(
                panel_x1,
                panel_x2,
                y2_i,
                y2_o,
                z2_i - panel_bar_thickness,
                z2_o - panel_bar_thickness,
                z2_i,
                z2_o,
                gate_fence_tex,
            )
        )  # top-right
        # Connector to next panel at mid-Z
        conn_y2_p = panel_center_y + panel_spacing - panel_outer_width // 2
        if panels_drawn + 1 < panel_count:
            BRUSHES.append(
                box(
                    panel_x1,
                    y2_o,
                    panel_z_center - panel_bar_thickness // 2,
                    panel_x2,
                    conn_y2_p,
                    panel_z_center + panel_bar_thickness // 2,
                    gate_fence_tex,
                )
            )
        panel_center_y += panel_spacing
        panels_drawn += 1
    # Corner pillar — square brick post at the L junction, wider than wall
    EP_WALL_PIL_HW = 14  # pillar half-width (28 units square)
    EP_WALL_PIL_H = 120  # pillar height — taller than wall
    bw_cx = EP_WALL_X1 + EP_WALL_T // 2  # pillar centre X (wall centre)
    bw_cy = EP_WALL_NY + EP_WALL_T // 2  # pillar centre Y (wall centre)
    BRUSHES.append(
        box(
            bw_cx - EP_WALL_PIL_HW,
            bw_cy - EP_WALL_PIL_HW,
            FLOOR_Z2,
            bw_cx + EP_WALL_PIL_HW,
            bw_cy + EP_WALL_PIL_HW,
            FLOOR_Z2 + EP_WALL_PIL_H,
            "city2_1",
        )
    )
    # Cement collar — same width as pillar, sits between brick post and cap slab
    BRUSHES.append(
        box(
            bw_cx - EP_WALL_PIL_HW,
            bw_cy - EP_WALL_PIL_HW,
            FLOOR_Z2 + EP_WALL_PIL_H,
            bw_cx + EP_WALL_PIL_HW,
            bw_cy + EP_WALL_PIL_HW,
            FLOOR_Z2 + EP_WALL_PIL_H + 6,
            TEX_CEMENT,
        )
    )
    # Square cap slab, then shallow pyramid on top
    BRUSHES.append(
        box(
            bw_cx - EP_WALL_PIL_HW - 1,
            bw_cy - EP_WALL_PIL_HW - 1,
            FLOOR_Z2 + EP_WALL_PIL_H + 6,
            bw_cx + EP_WALL_PIL_HW + 1,
            bw_cy + EP_WALL_PIL_HW + 1,
            FLOOR_Z2 + EP_WALL_PIL_H + 10,
            TEX_CEMENT,
        )
    )
    BRUSHES.append(
        pyramid(
            bw_cx - EP_WALL_PIL_HW - 1,
            bw_cy - EP_WALL_PIL_HW - 1,
            FLOOR_Z2 + EP_WALL_PIL_H + 10,
            bw_cx + EP_WALL_PIL_HW + 1,
            bw_cy + EP_WALL_PIL_HW + 1,
            FLOOR_Z2 + EP_WALL_PIL_H + 16,
            TEX_CEMENT,
        )
    )

    # ── East-running iron gate along Ennis Drive (from brick wall end to ~halfway east) ──
    # Built as func_detail to avoid BSP portal overflow from pickets in open space.
    EP_GATE_X1 = bwex2  # starts at east end of brick wall
    EP_GATE_X2 = (bwex2 + WORLD_X2 - WALL_T) // 2  # ends halfway to east world wall
    east_gate_y1 = EP_WALL_NY + EP_WALL_T // 2 - 1  # Y centre of fence line
    east_gate_y2 = east_gate_y1 + 2
    east_gate_brushes = []
    # Top rail
    east_gate_brushes.append(
        box(
            EP_GATE_X1,
            east_gate_y1,
            FLOOR_Z2 + gate_fence_height - 28,
            EP_GATE_X2,
            east_gate_y2,
            FLOOR_Z2 + gate_fence_height - 26,
            gate_fence_tex,
        )
    )
    # Pickets — 2-wide every 16, 8-wide posts every 10th
    east_gate_picket_x = EP_GATE_X1
    east_gate_picket_index = 0
    while east_gate_picket_x + 2 <= EP_GATE_X2:
        east_gate_picket_width = 8 if east_gate_picket_index % 10 == 0 else 2
        east_gate_brushes.append(
            box(
                east_gate_picket_x,
                east_gate_y1,
                FLOOR_Z2,
                east_gate_picket_x + east_gate_picket_width,
                east_gate_y2,
                FLOOR_Z2 + gate_fence_height,
                gate_fence_tex,
            )
        )
        east_gate_picket_x += gate_fence_spacing
        east_gate_picket_index += 1

    # ── Cement parapet wall — east half of Ennis Drive (iron fence end to east world wall) ──
    EP_CEMENT_X1 = EP_GATE_X2  # starts where iron fence ends
    EP_CEMENT_X2 = WORLD_X2 - WALL_T  # east world wall inner face
    cement_wall_y1 = EP_WALL_NY  # south face
    cement_wall_y2 = EP_WALL_NY + EP_WALL_T  # north face
    cement_wall_height = 32  # parapet height — low enough to jump over
    cement_wall_pillar_half_width = 14  # pillar half-width
    cement_wall_pillar_height = (
        cement_wall_height + 16
    )  # pillar slightly taller than wall
    # Wall body
    BRUSHES.append(
        box(
            EP_CEMENT_X1,
            cement_wall_y1,
            FLOOR_Z2,
            EP_CEMENT_X2,
            cement_wall_y2,
            FLOOR_Z2 + cement_wall_height,
            TEX_CEMENT,
        )
    )
    # Cap slab (slightly proud on all sides)
    BRUSHES.append(
        box(
            EP_CEMENT_X1,
            cement_wall_y1 - 2,
            FLOOR_Z2 + cement_wall_height,
            EP_CEMENT_X2,
            cement_wall_y2 + 2,
            FLOOR_Z2 + cement_wall_height + 6,
            TEX_CEMENT,
        )
    )
    # Pillars at each end
    EP_CEMENT_LAMP_POSTS = []
    for pillar_x in (EP_CEMENT_X1, EP_CEMENT_X2):
        pillar_center_y = (cement_wall_y1 + cement_wall_y2) // 2
        BRUSHES.append(
            box(
                pillar_x - cement_wall_pillar_half_width,
                pillar_center_y - cement_wall_pillar_half_width,
                FLOOR_Z2,
                pillar_x + cement_wall_pillar_half_width,
                pillar_center_y + cement_wall_pillar_half_width,
                FLOOR_Z2 + cement_wall_pillar_height,
                TEX_CEMENT,
            )
        )
        # Cap slab on pillar
        BRUSHES.append(
            box(
                pillar_x - cement_wall_pillar_half_width - 2,
                pillar_center_y - cement_wall_pillar_half_width - 2,
                FLOOR_Z2 + cement_wall_pillar_height,
                pillar_x + cement_wall_pillar_half_width + 2,
                pillar_center_y + cement_wall_pillar_half_width + 2,
                FLOOR_Z2 + cement_wall_pillar_height + 6,
                TEX_CEMENT,
            )
        )
        # Lamppost pole
        lamppost_base_z = FLOOR_Z2 + cement_wall_pillar_height + 6
        BRUSHES.append(
            box(
                pillar_x - 3,
                pillar_center_y - 3,
                lamppost_base_z,
                pillar_x + 3,
                pillar_center_y + 3,
                lamppost_base_z + 160,
                TEX_PILLAR,
            )
        )
        # Lantern head — narrow shaft + wider cap
        BRUSHES.append(
            box(
                pillar_x - 4,
                pillar_center_y - 4,
                lamppost_base_z + 160,
                pillar_x + 4,
                pillar_center_y + 4,
                lamppost_base_z + 176,
                TEX_CEMENT,
            )
        )
        BRUSHES.append(
            box(
                pillar_x - 7,
                pillar_center_y - 7,
                lamppost_base_z + 176,
                pillar_x + 7,
                pillar_center_y + 7,
                lamppost_base_z + 180,
                TEX_CEMENT,
            )
        )
        EP_CEMENT_LAMP_POSTS.append((pillar_x, pillar_center_y, lamppost_base_z + 180))

    RH_DEPTH = 600  # building N-S depth (doubled)
    RH_PIER_X = min(BRIDGE_ARCH_X)  # = -1100
    RH_X2 = RH_PIER_X + BRIDGE_PIL_HW + 32  # east face of building  = -1031
    RH_X1 = RH_X2 - 576  # west face of building (doubled width)
    RH_NORTH_Y2 = WORLD_Y2 - WALL_T - 150  # north building north face (shifted south)
    RH_NORTH_Y1 = RH_NORTH_Y2 - RH_DEPTH  # north building south face
    RH_SOUTH1_Y1 = WORLD_Y1 + WALL_T  # south building 1 south face = -2032
    RH_SOUTH1_Y2 = RH_SOUTH1_Y1 + RH_DEPTH  # south building 1 north face = -1432
    RH_SOUTH2_Y1 = RH_SOUTH1_Y2  # south building 2 south face = -1432
    RH_SOUTH2_Y2 = RH_SOUTH2_Y1 + RH_DEPTH  # south building 2 north face = -832

    # Starts at X=-560 (clear of the -525 pier base) so arch stone is not buried there.
    RH_EMB_X2 = -1146  # starts just east of abutment pier, keeping stone base visible
    # Interpolate ramp top-Z at the building's west face so the slope is continuous
    emb_zt_at_ab_x1 = int(
        BRIDGE_DZ2
        + (FLOOR_Z2 - BRIDGE_DZ2) * (RH_X1 - BRIDGE_X1) / (RH_EMB_X2 - BRIDGE_X1)
    )
    # South segment — west of south buildings (through buildings' Y range)
    BRUSHES.append(
        ramp_slab(
            BRIDGE_X1,
            RH_X1,
            CS_Y1,
            RH_SOUTH2_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2,
            emb_zt_at_ab_x1,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # South segment — full width between south buildings and north building
    BRUSHES.append(
        ramp_slab(
            BRIDGE_X1,
            RH_EMB_X2,
            RH_SOUTH2_Y2,
            RH_NORTH_Y1,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2,
            FLOOR_Z2,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # Middle segment — only west of north building
    BRUSHES.append(
        ramp_slab(
            BRIDGE_X1,
            RH_X1,
            RH_NORTH_Y1,
            RH_NORTH_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2,
            emb_zt_at_ab_x1,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # North of north building — restore original ramp
    BRUSHES.append(
        ramp_slab(
            BRIDGE_X1,
            RH_EMB_X2,
            RH_NORTH_Y2,
            CS_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2,
            FLOOR_Z2,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )

    # Wall extending north from the abutment pier, deck height, city2_1 texture
    # Door opening ~160 units north of the pier (visible in bridge10)
    RH_WALL_S_Y2 = -(BRIDGE_Y2 + BRIDGE_PIL_OVERHANG)  # south face of pier = -152
    RH_DOOR_W = 80  # door opening width (~5 ft)
    RH_DOOR_OFF = 160  # distance from pier face to door centre
    RH_DOOR_H = (
        128  # door opening height — embankment rises ~56 units at wall, need clearance
    )
    # (Building dimensions already defined above)
    # South brick wall — from bridge pier south face to nearest south building, with door gap
    # Door centered 160 units north of the building (closer to buildings)
    s_door_y = RH_SOUTH2_Y2 + RH_DOOR_OFF  # door centre Y
    BRUSHES.append(
        box(
            RH_PIER_X - BRIDGE_PIL_HW,
            RH_SOUTH2_Y2,
            FLOOR_Z2,
            RH_PIER_X + BRIDGE_PIL_HW,
            s_door_y - RH_DOOR_W // 2,
            BRIDGE_DZ2,
            "city2_1",
        )
    )
    BRUSHES.append(
        box(
            RH_PIER_X - BRIDGE_PIL_HW,
            s_door_y + RH_DOOR_W // 2,
            FLOOR_Z2,
            RH_PIER_X + BRIDGE_PIL_HW,
            RH_WALL_S_Y2,
            BRIDGE_DZ2,
            "city2_1",
        )
    )
    BRUSHES.append(
        box(
            RH_PIER_X - BRIDGE_PIL_HW,
            s_door_y - RH_DOOR_W // 2,
            FLOOR_Z2 + RH_DOOR_H,
            RH_PIER_X + BRIDGE_PIL_HW,
            s_door_y + RH_DOOR_W // 2,
            BRIDGE_DZ2,
            "city2_1",
        )
    )
    if east_gate_brushes:
        ENTITIES.append(brush_ent("func_detail", east_gate_brushes))
    return BRUSHES, ENTITIES
