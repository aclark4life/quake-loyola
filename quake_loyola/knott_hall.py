import math

from .constants import (
    A_SEGS,
    BRIDGE,
    BRIDGE_DZ2,
    BRIDGE_FASCIA_PX_H,
    BRIDGE_FASCIA_PX_W,
    BRIDGE_FASCIA_TEXT,
    CHARLES_CRN_SEGS,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    CHARLES_Y1,
    CHARLES_Y2,
    DRAW_BRIDGE_FASCIA_TEXT,
    ENNIS_HW,
    ENNIS_SW_EDGE,
    ENNIS_Y,
    FASCIA_FONT,
    FLOOR_Z1,
    FLOOR_Z2,
    INDENT,
    KNOTT,
    KNOTT_DRIVEWAY_CURB_CRN_R,
    KNOTT_DRIVEWAY_CURB_CRN_SEGS,
    KNOTT_DRIVEWAY_ES_X1,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_EXT_Y1,
    KNOTT_DRIVEWAY_EXT_Y2,
    KNOTT_DRIVEWAY_JCX_E,
    KNOTT_DRIVEWAY_JCX_W,
    KNOTT_DRIVEWAY_JCY,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_WS_X1,
    KNOTT_DRIVEWAY_WS_X2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_ENABLED,
    KNOTT_ENT_HALF_W,
    KNOTT_FRONT_WINDOW_HALF_W,
    KNOTT_FRONT_WINDOW_MULLION_HALF_GAP,
    KNOTT_GROUND_Z,
    KNOTT_MULLION_PRO,
    KNOTT_MULLION_W,
    KNOTT_ORIG_CX,
    KNOTT_RAIL_H,
    KNOTT_RAIL_TEX,
    KNOTT_SHAFT_WALL,
    KNOTT_SHAFT_X1,
    KNOTT_SHAFT_X2,
    KNOTT_SHAFT_Y1,
    KNOTT_SHAFT_Y2,
    KNOTT_SIDE_WINDOW_DIV_W,
    KNOTT_SIDE_WINDOW_HALF_W,
    KNOTT_SIDE_WINDOW_INNER_LEFT,
    KNOTT_SIDE_WINDOW_INNER_RIGHT,
    KNOTT_SIDE_WINDOW_PROTRUSION,
    KNOTT_SIGN_H,
    KNOTT_SIGN_PADDING,
    KNOTT_SIGN_PX_H,
    KNOTT_SIGN_PX_W,
    KNOTT_SIGN_TEXT,
    KNOTT_SIGN_Z_OFFSET,
    KNOTT_STAIR_CAP_RAISE,
    KNOTT_STAIR_CAP_W,
    KNOTT_STAIR_OFFSET,
    KNOTT_STAIR_RAIL_EXTENSION,
    KNOTT_STAIR_RAIL_POST_D,
    KNOTT_STAIR_RAIL_POST_W,
    KNOTT_STAIRS_HALF_N,
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
    KNOTT_STEP_DEPTH,
    KNOTT_STEP_N,
    KNOTT_Z2,
    WALK_ZT2,
    WALL_T,
    WIN_HALF,
    WORLD_X1,
    WORLD_X2,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
    deck_top_z,
)
from .geometry import (
    arch_wall_y,
    box,
    brush_ent,
    layered_wall,
    layered_wall_y,
    ramp_slab,
    ramp_slab_y,
    render_text_flat,
    tri_prism,
)


def build():
    BRUSHES = []
    ENTITIES = []
    DETAIL_BRUSHES = []
    knott_brush_start = len(
        BRUSHES
    )  # checkpoint — trimmed below if KNOTT_ENABLED is False

    def road_section(brushes, x1, x2, top_z_s, top_z_n, surface_tex):
        brushes.append(
            ramp_slab_y(
                x1,
                x2,
                KNOTT_DRIVEWAY_Y1,
                KNOTT_DRIVEWAY_Y2,
                FLOOR_Z1,
                FLOOR_Z1,
                top_z_s,
                top_z_n,
                surface_tex,
                tt=surface_tex,
            )
        )
        brushes.append(
            ramp_slab_y(
                x1,
                x2,
                KNOTT_DRIVEWAY_Y1,
                KNOTT_DRIVEWAY_Y2,
                FLOOR_Z1,
                FLOOR_Z1,
                KNOTT_DRIVEWAY_ZT_S,
                KNOTT_DRIVEWAY_ZT_N,
                Textures.GROUND,
                tt=Textures.GROUND,
            )
        )

    def floor_levels():
        for floor_index in range(KNOTT.floors):
            fz1 = KNOTT_GROUND_Z + floor_index * KNOTT.floor_h
            fz2 = fz1 + KNOTT.floor_h
            fz_surf = fz1 + KNOTT.wall_t
            fz_mid = fz1 + KNOTT.floor_h // 2
            yield floor_index, fz1, fz2, fz_surf, fz_mid

    # ══════════════════════════════════════════════════════════════════════════════
    # BACK ROAD — east of Knott Hall, slopes south to meet the back of the building
    # Sidewalks with rounded north entrance corners (like Ennis Drive)
    # Road surface — 2-unit textured overlay riding on sloped fill
    road_section(
        BRUSHES,
        KNOTT_DRIVEWAY_RD_X1,
        KNOTT_DRIVEWAY_RD_X2,
        KNOTT_DRIVEWAY_ZT_S + 2,
        KNOTT_DRIVEWAY_ZT_N + 2,
        Textures.ROAD,
    )

    # West sidewalk (strip between building east wall and road) — slopes with road
    road_section(
        BRUSHES,
        KNOTT_DRIVEWAY_WS_X1,
        KNOTT_DRIVEWAY_WS_X2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.CEMENT,
    )

    # East sidewalk — slopes with road
    road_section(
        BRUSHES,
        KNOTT_DRIVEWAY_ES_X1,
        KNOTT_DRIVEWAY_ES_X2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.CEMENT,
    )

    # Terrain east of east sidewalk — south flat + sloped main section matching sidewalk
    # South extension: flat at hill level
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X2,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    # Main back road section: slopes with the sidewalk (88 at south → 8 at north)
    BRUSHES.append(
        ramp_slab_y(
            KNOTT_DRIVEWAY_ES_X2,
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
            KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    # ── South extension — road + east sidewalk behind Knott Hall to world edge ──
    BRUSHES.append(
        box(
            KNOTT.x1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            KNOTT_DRIVEWAY_ES_X1,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_ZT_S + 2,
            Textures.ROAD,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Flat extension north from Knott Hall to Ennis south sidewalk ──────────────
    # Flat road surface
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_RD_X1,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_RD_X2,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )
    # West sidewalk
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_WS_X1,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_WS_X2,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # East sidewalk
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # Terrain east of east sidewalk — sealing ground recessed to floor level so the
    # decorative detail surfaces (cement walk / mulch / Ennis verge) laid on top at
    # sidewalk height (FLOOR_Z2 + CHARLES_WALK_H) are the visible surface, not this ground.
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2,
            Textures.GROUND,
        )
    )

    # Road patch filling the gap between back road end (Y=328) and Ennis road (Y=408)
    # (This was previously the Ennis south sidewalk; now it's part of the road junction)
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_RD_X1,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_RD_X2,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )

    # ── Rounded corners where back road meets Ennis south (inside the junction) ───
    # Centers at the back-road-facing (south) corners so the curved face points toward
    # the back road — matching the Charles/Ennis corner style.
    # West junction corner: center at SW corner (1906, 328), arc sweeps 0°→90°
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
    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        angle_start = math.radians(0 + corner_index * 90 / KNOTT_DRIVEWAY_CURB_CRN_SEGS)
        angle_end = math.radians(
            0 + (corner_index + 1) * 90 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
        )
        arc_x0 = KNOTT_DRIVEWAY_JCX_W + KNOTT_DRIVEWAY_CURB_CRN_R * math.cos(
            angle_start
        )
        arc_y0 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_CRN_R * math.sin(
            angle_start
        )
        arc_x1 = KNOTT_DRIVEWAY_JCX_W + KNOTT_DRIVEWAY_CURB_CRN_R * math.cos(angle_end)
        arc_y1 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_CRN_R * math.sin(angle_end)
        BRUSHES.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_W,
                KNOTT_DRIVEWAY_EXT_Y2,
                arc_x0,
                arc_y0,
                arc_x1,
                arc_y1,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )

    # East junction corner: center at SE corner (2322, 328), arc sweeps 90°→180°
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
        angle_start = math.radians(
            90 + corner_index * 90 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
        )
        angle_end = math.radians(
            90 + (corner_index + 1) * 90 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
        )
        arc_x0 = KNOTT_DRIVEWAY_JCX_E + KNOTT_DRIVEWAY_CURB_CRN_R * math.cos(
            angle_start
        )
        arc_y0 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_CRN_R * math.sin(
            angle_start
        )
        arc_x1 = KNOTT_DRIVEWAY_JCX_E + KNOTT_DRIVEWAY_CURB_CRN_R * math.cos(angle_end)
        arc_y1 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_CRN_R * math.sin(angle_end)
        BRUSHES.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_E,
                KNOTT_DRIVEWAY_EXT_Y2,
                arc_x0,
                arc_y0,
                arc_x1,
                arc_y1,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )

    bix1 = KNOTT.x1 + KNOTT.wall_t  # interior west
    bix2 = KNOTT.x2 - KNOTT.wall_t  # interior east
    KNOTT_BIY1 = KNOTT.y1 + KNOTT.wall_t  # interior south = -784
    KNOTT_BIY2 = KNOTT.y2 - KNOTT.wall_t  # interior north = -272

    # Entrance doorway — pinned to original building centre, not current KNOTT_CX
    KNOTT_ENT_X1, KNOTT_ENT_X2 = (
        KNOTT_ORIG_CX - KNOTT_ENT_HALF_W,
        KNOTT_ORIG_CX + KNOTT_ENT_HALF_W,
    )

    # ── Entrance staircase ────────────────────────────────────────────────────────
    stair_base_z = FLOOR_Z2 + CHARLES_WALK_H  # steps start at apron surface height (8)

    # Flat cement platform between building and stairs
    BRUSHES.append(
        box(
            KNOTT_ENT_X1,
            KNOTT.y2,
            FLOOR_Z2,
            KNOTT_ENT_X2,
            KNOTT.y2 + KNOTT_STAIR_OFFSET,
            KNOTT_GROUND_Z,
            Textures.CEMENT,
        )
    )

    stair_y0 = KNOTT.y2 + KNOTT_STAIR_OFFSET  # south edge of staircase
    stair_y_end = (
        stair_y0 + KNOTT_STEP_N * KNOTT_STEP_DEPTH
    )  # north end of stairs (ground level)
    for stair_index in range(KNOTT_STEP_N):
        step_top_z = (
            stair_base_z
            + (KNOTT_GROUND_Z - stair_base_z) * (stair_index + 1) // KNOTT_STEP_N
        )
        step_north_y = stair_y0 + (KNOTT_STEP_N - stair_index) * KNOTT_STEP_DEPTH
        BRUSHES.append(
            box(
                KNOTT_ENT_X1,
                stair_y0,
                stair_base_z,
                KNOTT_ENT_X2,
                step_north_y,
                step_top_z,
                Textures.CEMENT,
                tt=Textures.CEMENT,
            )
        )

    # Cement sidewalk from stair base to Ennis south sidewalk — flush with ground fill
    BRUSHES.append(
        box(
            KNOTT_ENT_X1,
            stair_y_end,
            FLOOR_Z1,
            KNOTT_ENT_X2,
            ENNIS_SW_EDGE,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Stair side caps (cement cheek walls) ─────────────────────────────────────
    # Solid sloped cement walls on each side of the staircase, top follows stair slope.
    for cap_x1, cap_x2 in [
        (KNOTT_ENT_X1 - KNOTT_STAIR_CAP_W, KNOTT_ENT_X1),  # west cheek
        (KNOTT_ENT_X2, KNOTT_ENT_X2 + KNOTT_STAIR_CAP_W),  # east cheek
    ]:
        BRUSHES.append(
            ramp_slab_y(
                cap_x1,
                cap_x2,
                stair_y0,
                stair_y_end,
                FLOOR_Z1,
                FLOOR_Z1,
                KNOTT_GROUND_Z + KNOTT_STAIR_CAP_RAISE,
                stair_base_z + KNOTT_STAIR_CAP_RAISE,
                Textures.CEMENT,
            )
        )

    # ── Stair railings ────────────────────────────────────────────────────────────
    for rail_x_base, is_west_side in [(KNOTT_ENT_X1, True), (KNOTT_ENT_X2, False)]:
        rail_top_z_at_platform = KNOTT_GROUND_Z + KNOTT_RAIL_H - 28
        rail_top_z_at_apron = stair_base_z + KNOTT_RAIL_H - 28
        rail_x1 = rail_x_base - KNOTT_STAIR_RAIL_POST_W if is_west_side else rail_x_base
        rail_x2 = rail_x_base if is_west_side else rail_x_base + KNOTT_STAIR_RAIL_POST_W

        # Sloped cross rail
        DETAIL_BRUSHES.append(
            ramp_slab_y(
                rail_x1,
                rail_x2,
                stair_y0,
                stair_y_end,
                rail_top_z_at_platform,
                rail_top_z_at_apron,
                rail_top_z_at_platform + 2,
                rail_top_z_at_apron + 2,
                KNOTT_RAIL_TEX,
            )
        )

        # Horizontal extension at top (level with platform floor)
        DETAIL_BRUSHES.append(
            box(
                rail_x1,
                stair_y0 - KNOTT_STAIR_RAIL_EXTENSION,
                rail_top_z_at_platform,
                rail_x2,
                stair_y0,
                rail_top_z_at_platform + 2,
                KNOTT_RAIL_TEX,
            )
        )
        # Horizontal extension at bottom (level with apron floor)
        DETAIL_BRUSHES.append(
            box(
                rail_x1,
                stair_y_end,
                rail_top_z_at_apron,
                rail_x2,
                stair_y_end + KNOTT_STAIR_RAIL_EXTENSION,
                rail_top_z_at_apron + 2,
                KNOTT_RAIL_TEX,
            )
        )

        # Posts — wide flat-facing
        for post_y, post_z in [
            (stair_y0, KNOTT_GROUND_Z),
            (stair_y_end, stair_base_z),
        ]:
            DETAIL_BRUSHES.append(
                box(
                    rail_x1,
                    post_y,
                    post_z,
                    rail_x2,
                    post_y + KNOTT_STAIR_RAIL_POST_D,
                    post_z + KNOTT_RAIL_H - 26,
                    KNOTT_RAIL_TEX,
                )
            )

    # West stairwell extents defined after INDENT below

    # ── Outer walls ──────────────────────────────────────────────────────────────
    # South wall — mirrors north wall: indented SW/SE corners with recessed windows
    # Main south face — hallway openings cut through at each floor level
    s_wall_openings = [
        (
            KNOTT_ENT_X1,
            KNOTT_GROUND_Z + fl * KNOTT.floor_h + KNOTT.wall_t,
            KNOTT_ENT_X2,
            KNOTT_GROUND_Z + (fl + 1) * KNOTT.floor_h,
        )
        for fl in range(KNOTT.floors)
    ]
    BRUSHES.extend(
        layered_wall(
            KNOTT.x1 + INDENT,
            KNOTT.y1,
            KNOTT_GROUND_Z,
            KNOTT.x2 - INDENT,
            KNOTT.y1 + KNOTT.wall_t,
            KNOTT_Z2,
            s_wall_openings,
            Textures.WALL,
        )
    )
    # SW Indentation inner walls — recessed back wall with centered 48-unit window
    sw_win_cx = KNOTT.x1 + INDENT // 2
    BRUSHES.extend(
        layered_wall(
            KNOTT.x1,
            KNOTT.y1 + INDENT - KNOTT.wall_t,
            FLOOR_Z1,
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
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1 + INDENT - KNOTT.wall_t,
            KNOTT.y1,
            FLOOR_Z1,
            KNOTT.x1 + INDENT,
            KNOTT.y1 + INDENT,
            KNOTT_Z2,
            Textures.WALL,
        )
    )
    # SE Indentation inner walls — recessed back wall with centered 48-unit window
    se_win_cx = KNOTT.x2 - INDENT // 2
    BRUSHES.extend(
        layered_wall(
            KNOTT.x2 - INDENT,
            KNOTT.y1 + INDENT - KNOTT.wall_t,
            FLOOR_Z1,
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
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y1,
            FLOOR_Z1,
            KNOTT.x2 - INDENT + KNOTT.wall_t,
            KNOTT.y1 + INDENT,
            KNOTT_Z2,
            Textures.WALL,
        )
    )
    # South mullions — protrude outward (south, -Y)
    for mx in [sw_win_cx - WIN_HALF - KNOTT_MULLION_W, sw_win_cx + WIN_HALF]:
        DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y1 + INDENT - KNOTT.wall_t,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y1 + INDENT + KNOTT_MULLION_PRO,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )
    for mx in [se_win_cx - WIN_HALF - KNOTT_MULLION_W, se_win_cx + WIN_HALF]:
        DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y1 + INDENT - KNOTT.wall_t,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y1 + INDENT + KNOTT_MULLION_PRO,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )
    # Horizontal mullions — SW and SE south-face indentation windows, matching east/west walls
    for wx in [sw_win_cx, se_win_cx]:
        for floor_index, _, _, _, mz in floor_levels():
            if floor_index == 0:
                continue
            DETAIL_BRUSHES.append(
                box(
                    wx - WIN_HALF,
                    KNOTT.y1 + INDENT - KNOTT.wall_t,
                    mz,
                    wx + WIN_HALF,
                    KNOTT.y1 + INDENT + KNOTT_MULLION_PRO,
                    mz + 4,
                    Textures.RAIL,
                )
            )
    # Floor-level mullions — SW and SE south-face windows
    for wx in [sw_win_cx, se_win_cx]:
        for _, _, fz, _, _ in floor_levels():
            DETAIL_BRUSHES.append(
                box(
                    wx - WIN_HALF,
                    KNOTT.y1 + INDENT - KNOTT.wall_t,
                    fz - 4,
                    wx + WIN_HALF,
                    KNOTT.y1 + INDENT + KNOTT_MULLION_PRO,
                    fz,
                    Textures.RAIL,
                )
            )
    # North-West Indentation (Corner Notch)
    # North wall — faces bridge; ground entrance + 2nd-floor walkway opening
    door_ground = [
        (KNOTT_ENT_X1, KNOTT_GROUND_Z, KNOTT_ENT_X2, KNOTT_GROUND_Z + KNOTT.floor_h)
    ]  # ground entrance
    door_upper = [
        (KNOTT_ENT_X1, WALK_ZT2, KNOTT_ENT_X2, KNOTT_GROUND_Z + KNOTT.floor_h * 2)
    ]  # walkway entrance
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
    ]  # two window slots centered over entrance doorway, split by center mullion
    BRUSHES.extend(
        layered_wall(
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2 - KNOTT.wall_t,
            KNOTT_GROUND_Z,
            KNOTT.x2 - INDENT,
            KNOTT.y2,
            KNOTT_Z2,
            door_ground + door_upper + win_n,
            Textures.WALL,
        )
    )

    # NW Indentation — 2×INDENT wide (extends west to KNOTT.x1), two windows side by side
    nw_win_cx1 = KNOTT.x1 + INDENT // 2  # west window = 1246 (pier-aligned)
    nw_win_cx2 = KNOTT.x1 + INDENT + INDENT // 2  # east window = 1326
    BRUSHES.extend(
        layered_wall(
            KNOTT.x1,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
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
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x1 + 2 * INDENT - KNOTT.wall_t,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
            KNOTT.x1 + 2 * INDENT,
            KNOTT.y2,
            KNOTT_Z2,
            Textures.WALL,
        )
    )

    # NE Indentation inner walls (mirror of NW) — recessed back wall has a centered 48-unit window
    ne_win_cx = KNOTT.x2 - INDENT // 2
    BRUSHES.extend(
        layered_wall(
            KNOTT.x2 - INDENT,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
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
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KNOTT.x2 - INDENT,
            KNOTT.y2 - INDENT,
            FLOOR_Z1,
            KNOTT.x2 - INDENT + KNOTT.wall_t,
            KNOTT.y2,
            KNOTT_Z2,
            Textures.WALL,
        )
    )

    # Front mullions — protruding sfloor3_2 posts on each side of the recessed windows
    # and the narrow vertical window on the main north face. All protrude 12 units outward.
    # NW recessed windows: mullions for both (west and east window in the wide NW indentation)
    for mx in [
        nw_win_cx1 - WIN_HALF - KNOTT_MULLION_W,
        nw_win_cx1 + WIN_HALF,
        nw_win_cx2 - WIN_HALF - KNOTT_MULLION_W,
        nw_win_cx2 + WIN_HALF,
    ]:
        DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y2 - INDENT - KNOTT_MULLION_PRO,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y2 - INDENT + KNOTT.wall_t,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )
    # NE recessed window: mullions just outside the opening so player can fit through
    for mx in [ne_win_cx - WIN_HALF - KNOTT_MULLION_W, ne_win_cx + WIN_HALF]:
        DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y2 - INDENT - KNOTT_MULLION_PRO,
                KNOTT_GROUND_Z + KNOTT.floor_h,
                mx + KNOTT_MULLION_W,
                KNOTT.y2 - INDENT + KNOTT.wall_t,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )
    # Main front wall window win_n: mullions on each side and center post
    win_n_x1, win_n_x2 = (
        KNOTT_ORIG_CX - KNOTT_FRONT_WINDOW_HALF_W,
        KNOTT_ORIG_CX + KNOTT_FRONT_WINDOW_HALF_W,
    )
    win_n_mid = KNOTT_ORIG_CX - KNOTT_FRONT_WINDOW_MULLION_HALF_GAP
    for mx in [win_n_x1 - KNOTT_MULLION_W, win_n_mid, win_n_x2]:
        DETAIL_BRUSHES.append(
            box(
                mx,
                KNOTT.y2 - KNOTT.wall_t,
                KNOTT_GROUND_Z + KNOTT.floor_h * 2,
                mx + KNOTT_MULLION_W,
                KNOTT.y2 + KNOTT_MULLION_PRO,
                KNOTT_Z2,
                Textures.CEMENT,
            )
        )

    # ── "Marion Burk Knott Hall" sign plaque — north face, 2nd floor level ───────
    # Protruding cement slab, sized to fit pixel-font lettering
    knott_sign_char_w = (4 + 1) * KNOTT_SIGN_PX_W
    knott_sign_total_w = len(KNOTT_SIGN_TEXT) * knott_sign_char_w - KNOTT_SIGN_PX_W
    knott_sign_half_w = (
        knott_sign_total_w // 2 + KNOTT_SIGN_PADDING
    )  # padding each side = 222
    knott_sign_cx = (
        KNOTT.x2 - INDENT - knott_sign_half_w
    )  # east edge flush with wall end
    knott_sign_z1 = (
        KNOTT_GROUND_Z + KNOTT.floor_h * 2 + KNOTT_SIGN_Z_OFFSET
    )  # just above 2nd floor line
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
    # Letter brushes deferred — render_text_flat defined below

    # ── Brutalist Fins (All Exposed Facades) — currently disabled ─────────────────

    # East wall — three 120-unit wide floor-to-ceiling windows, matching west side
    # Shared window layout variables (used for both east and west walls)
    ww_half = KNOTT_SIDE_WINDOW_HALF_W
    ww_wall_y1, ww_wall_y2 = KNOTT.y1, KNOTT.y2 - INDENT
    ww_quarter = (ww_wall_y2 - ww_wall_y1) // 4
    ww_c1 = ww_wall_y1 + ww_quarter
    ww_c2 = ww_wall_y1 + 2 * ww_quarter
    ww_c3 = ww_wall_y1 + 3 * ww_quarter
    ww_div_w = KNOTT_SIDE_WINDOW_DIV_W
    ww_protrude = KNOTT_SIDE_WINDOW_PROTRUSION
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
            Textures.WALL,
        )
    )
    # Vertical mullions — protrude 12 units east of wall face
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for mullion_y in [
            window_center_y - ww_half,  # left edge
            window_center_y - KNOTT_SIDE_WINDOW_INNER_LEFT,  # interior left
            window_center_y + KNOTT_SIDE_WINDOW_INNER_RIGHT,  # interior right
            window_center_y + ww_half - ww_div_w,  # right edge
        ]:
            DETAIL_BRUSHES.append(
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

    # Horizontal mullions — centered in each floor span for contrast, players still fit through
    # Mid-floor Z leaves ~85 units clearance each side (player height = 56)
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for floor_index, _, _, _, mz in floor_levels():
            if floor_index == 0:
                continue
            DETAIL_BRUSHES.append(
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
    # Floor-level mullions — sill at base of each floor (floors 1+), lintel at top of each floor
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for _, _, fz, _, _ in floor_levels():
            DETAIL_BRUSHES.append(
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

    # West wall — three 120-unit wide floor-to-ceiling windows, evenly spread
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
            Textures.WALL,
        )
    )
    # Vertical mullions — protrude 12 units west of wall face
    # 2 interior + 2 side mullions per window (4 total each)
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for mullion_y in [
            window_center_y - ww_half,  # left edge
            window_center_y - KNOTT_SIDE_WINDOW_INNER_LEFT,  # interior left
            window_center_y + KNOTT_SIDE_WINDOW_INNER_RIGHT,  # interior right
            window_center_y + ww_half - ww_div_w,  # right edge
        ]:
            DETAIL_BRUSHES.append(
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

    # Horizontal mullions — west wall, matching east
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for floor_index, _, _, _, mz in floor_levels():
            if floor_index == 0:
                continue
            DETAIL_BRUSHES.append(
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
    # Floor-level mullions — west wall
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for _, _, fz, _, _ in floor_levels():
            DETAIL_BRUSHES.append(
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

    # Horizontal mullions — win_n narrow slot window on main north face (floors 2–3)
    for floor_index, _, _, _, mz in floor_levels():
        if floor_index < 2:
            continue
        DETAIL_BRUSHES.append(
            box(
                win_n_x1,
                KNOTT.y2 - KNOTT.wall_t,
                mz,
                win_n_x2,
                KNOTT.y2 + KNOTT_MULLION_PRO,
                mz + 4,
                Textures.RAIL,
            )
        )
    # Floor-level mullions — win_n
    for floor_index, _, fz, _, _ in floor_levels():
        if floor_index < 1:
            continue
        if fz <= KNOTT_Z2:
            DETAIL_BRUSHES.append(
                box(
                    win_n_x1,
                    KNOTT.y2 - KNOTT.wall_t,
                    fz - 4,
                    win_n_x2,
                    KNOTT.y2 + KNOTT_MULLION_PRO,
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
            DETAIL_BRUSHES.append(
                box(
                    window_center_x - window_half_width,
                    KNOTT.y2 - INDENT - KNOTT_MULLION_PRO,
                    mz,
                    window_center_x + window_half_width,
                    KNOTT.y2 - INDENT + KNOTT.wall_t,
                    mz + 4,
                    Textures.RAIL,
                )
            )
    # Floor-level mullions — NW/NE recessed north-face windows
    for window_center_x, window_half_width in [
        (nw_win_cx1, WIN_HALF),
        (nw_win_cx2, WIN_HALF),
        (ne_win_cx, WIN_HALF),
    ]:
        for _, _, fz, _, _ in floor_levels():
            DETAIL_BRUSHES.append(
                box(
                    window_center_x - window_half_width,
                    KNOTT.y2 - INDENT - KNOTT_MULLION_PRO,
                    fz - 4,
                    window_center_x + window_half_width,
                    KNOTT.y2 - INDENT + KNOTT.wall_t,
                    fz,
                    Textures.RAIL,
                )
            )

    # Roof — open above lift shaft, clipped for NW indentation
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
    )  # far-west bulk
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
    )  # far-west north-strip
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
    )  # south of west stairwell
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
    )  # north of west stairwell
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
    )  # between shafts (no indent — interior)
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
    )  # east bulk
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
    )  # east north-strip (NE cutout)
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
    )  # south of shaft
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
    )  # north of shaft (closes roof over north wall above shaft)

    # ── Interior floor slabs (floors 0-3, lift shaft opening in center-north) ────
    # Floor 0 (ground): full slab with no shaft opening, clipped for NW indentation
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
        # South bulk — full width up to stairwell's south wall
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
        # Stairwell south extension (KNOTT_STAIRS_Y1..KNOTT_SHAFT_Y1): floor on either side, stairwell open
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
        # North zone (KNOTT_SHAFT_Y1..KNOTT_BIY2): west of stairwell, clipped for NW indentation
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
        # Between west stairwell and east shaft
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
        # East of shaft, clipped for NE indentation
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

    # ── Elevator Shaft Enclosure ──────────────────────────────────────────────
    # Walls around the lift shaft (KNOTT_SHAFT_X1..KNOTT_SHAFT_X2, KNOTT_SHAFT_Y1..KNOTT_SHAFT_Y2)
    shaft_wall = KNOTT_SHAFT_WALL
    # Door opening dimensions per floor (used for both wall openings and func_door entities)
    shaft_door_h = KNOTT.floor_h  # door height matches floor-to-floor height
    shaft_door_openings = [
        (
            KNOTT_SHAFT_Y1 + 16,
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h,
            KNOTT_SHAFT_Y2 - 16,
            KNOTT_GROUND_Z + floor_index * KNOTT.floor_h + shaft_door_h,
        )
        for floor_index in range(KNOTT.floors)
    ]

    # Shaft North wall (internal, solid)
    DETAIL_BRUSHES.append(
        box(
            KNOTT_SHAFT_X1,
            KNOTT_SHAFT_Y2,
            KNOTT_GROUND_Z,
            KNOTT_SHAFT_X2,
            KNOTT_SHAFT_Y2 + shaft_wall,
            KNOTT_Z2,
            Textures.WALL,
        )
    )
    # Shaft South wall (internal, solid)
    DETAIL_BRUSHES.append(
        box(
            KNOTT_SHAFT_X1,
            KNOTT_SHAFT_Y1 - shaft_wall,
            KNOTT_GROUND_Z,
            KNOTT_SHAFT_X2,
            KNOTT_SHAFT_Y1,
            KNOTT_Z2,
            Textures.WALL,
        )
    )
    # Shaft West wall (internal, openings for each floor's door — flush with hallway east wall and shaft interior)
    DETAIL_BRUSHES.extend(
        layered_wall_y(
            KNOTT_SHAFT_Y1,
            KNOTT_ENT_X2,
            KNOTT_GROUND_Z,
            KNOTT_SHAFT_Y2,
            KNOTT_SHAFT_X1,
            KNOTT_Z2,
            shaft_door_openings,
            Textures.WALL,
        )
    )
    # Shaft East wall (internal)
    DETAIL_BRUSHES.append(
        box(
            KNOTT_SHAFT_X2,
            KNOTT_SHAFT_Y1,
            KNOTT_GROUND_Z,
            KNOTT_SHAFT_X2 + shaft_wall,
            KNOTT_SHAFT_Y2,
            KNOTT_Z2,
            Textures.WALL,
        )
    )

    # ── West Stairwell Enclosure ──────────────────────────────────────────────────
    # Walls around the west stairwell (KNOTT_STAIRS_X1..KNOTT_STAIRS_X2, KNOTT_STAIRS_Y1..KNOTT_STAIRS_Y2)
    west_shaft_door_openings = [
        (
            KNOTT_SHAFT_Y1 + 16,  # same Y extents as east shaft doorway
            fz1,
            KNOTT_SHAFT_Y2 - 16,
            fz1 + shaft_door_h,
        )
        for _, fz1, _, _, _ in floor_levels()
    ]

    # West stairwell North wall (internal, solid)
    DETAIL_BRUSHES.append(
        box(
            KNOTT_STAIRS_X1,
            KNOTT_STAIRS_Y2,
            KNOTT_GROUND_Z,
            KNOTT_STAIRS_X2,
            KNOTT_STAIRS_Y2 + shaft_wall,
            KNOTT_Z2,
            Textures.WALL,
        )
    )
    # West stairwell South wall (internal, solid)
    DETAIL_BRUSHES.append(
        box(
            KNOTT_STAIRS_X1,
            KNOTT_STAIRS_Y1 - shaft_wall,
            KNOTT_GROUND_Z,
            KNOTT_STAIRS_X2,
            KNOTT_STAIRS_Y1,
            KNOTT_Z2,
            Textures.WALL,
        )
    )
    # West stairwell East wall (internal, openings for each floor's door — flush both sides)
    DETAIL_BRUSHES.extend(
        layered_wall_y(
            KNOTT_STAIRS_Y1,
            KNOTT_STAIRS_X2,
            KNOTT_GROUND_Z,
            KNOTT_STAIRS_Y2,
            KNOTT_ENT_X1,
            KNOTT_Z2,
            west_shaft_door_openings,
            Textures.WALL,
        )
    )
    # West stairwell West wall (internal, solid)
    DETAIL_BRUSHES.append(
        box(
            KNOTT_STAIRS_X1 - shaft_wall,
            KNOTT_STAIRS_Y1,
            KNOTT_GROUND_Z,
            KNOTT_STAIRS_X1,
            KNOTT_STAIRS_Y2,
            KNOTT_Z2,
            Textures.WALL,
        )
    )

    # ── West Stairwell — Switchback Staircase ─────────────────────────────────────
    # Stairs compressed to the shaft centre (192 u wide), leaving 88-unit flanks for
    # half-floor platforms on the east and west sides.
    #
    # North lane (KNOTT_STAIRS_MID_Y..KNOTT_STAIRS_Y2): enter east door, walk WEST, rise z0 → z_mid.
    # West platform at z_mid (full shaft Y, 88 u wide) — turn-around landing.
    # South lane (KNOTT_STAIRS_Y1..KNOTT_STAIRS_MID_Y): walk EAST, rise z_mid → z_top.
    #
    # Step 0 of north lane and step 7 of south lane extend east to KNOTT_STAIRS_X2 so the
    # door at each floor connects directly to the staircase.
    # Loop runs KNOTT.floors times (fl 0→4) — top flight exits onto building roof.
    KNOTT_STAIRS_HALF_N = 8
    KNOTT_STAIRS_STEP_R = KNOTT.floor_h // (
        2 * KNOTT_STAIRS_HALF_N
    )  # rise per step, derived from floor height (≤ 18-unit Quake limit)
    KNOTT_STAIRS_TREAD_X = 24  # compressed tread depth: 8 × 24 = 192
    PLAT_H = 8  # platform slab thickness
    stair_cx = (KNOTT_STAIRS_X1 + KNOTT_STAIRS_X2) // 2  # shaft X centre
    stair_x1 = (
        stair_cx - KNOTT_STAIRS_HALF_N * KNOTT_STAIRS_TREAD_X // 2
    )  # west edge of stairs
    stair_x2 = (
        stair_x1 + KNOTT_STAIRS_HALF_N * KNOTT_STAIRS_TREAD_X
    )  # east edge of stairs
    for _, _, _, floor_z0, _ in floor_levels():
        half_flight_z = (
            floor_z0 + KNOTT_STAIRS_HALF_N * KNOTT_STAIRS_STEP_R
        )  # half-floor Z (floor_z0 + 80)
        top_flight_z = floor_z0 + KNOTT.floor_h  # next floor surface Z (= exit level)

        # Entrance landing — flush with hallway floor, east of stair band (north lane).
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
        # Exit landing — flush with next floor, east of stair band (south lane).
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

        # North lane: individual treads ascending westward (stair_x2 → stair_x1).
        for tread_index in range(KNOTT_STAIRS_HALF_N):
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
                    Textures.WALL,
                    tt=Textures.FLOOR_KH,
                )
            )

        # Half-floor west platform: turn-around landing, full shaft Y depth.
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

        # South lane: individual treads ascending eastward (stair_x1 → stair_x2).
        for tread_index in range(KNOTT_STAIRS_HALF_N):
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
                    Textures.WALL,
                    tt=Textures.FLOOR_KH,
                )
            )

    # ── West Stairwell — Iron Railings ────────────────────────────────────────────
    # 2 end posts + 1 sloped cross rail per half-flight, central divider (KNOTT_STAIRS_MID_Y).
    # Posts sit OUTSIDE the stair band (on the entrance area and west platform) so
    # they never land on a tread.  Cross rail spans the full stair band between them.
    KNOTT_STAIRS_RAIL_H = 72  # handrail height above landing surface (bottom of rail = 68u, clears 56u player)
    KNOTT_STAIRS_POST_W = 4  # square post cross-section
    KNOTT_STAIRS_RAIL_T = 4  # cross-rail bar thickness

    for _, _, _, floor_z0, _ in floor_levels():
        half_flight_z = floor_z0 + KNOTT_STAIRS_HALF_N * KNOTT_STAIRS_STEP_R
        top_flight_z = half_flight_z + KNOTT_STAIRS_HALF_N * KNOTT_STAIRS_STEP_R

        # ── North lane — south face (KNOTT_STAIRS_MID_Y) ────────────────────────────────
        # Lower post: east of stair band, in the entrance area
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
        # Upper post: west of stair band, on the west platform
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
        # Sloped cross rail along center divider (high at west, low at east)
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

        # ── South lane — north face (KNOTT_STAIRS_MID_Y) ────────────────────────────────
        # Lower post: west of stair band, on the west platform
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
        # Upper post: east of stair band, in the entrance area
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
        # Sloped cross rail along center divider (low at west, high at east)
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

    # Partition Y splits vary per floor so each floor has different room proportions.
    KNOTT_ROOM_SPLITS = [-1072, -950, -1200, -850, -1300]  # partition Y per floor

    wx1, wx2 = bix1, KNOTT_ENT_X1 - KNOTT.wall_t  # west room X extents (1282..1506)
    ex1, ex2 = KNOTT_ENT_X2 + KNOTT.wall_t, bix2  # east room X extents (1666..1890)
    KNOTT_WEST_ROOM_CX = (wx1 + wx2) // 2  # west room X center = 1394
    KNOTT_EAST_ROOM_CX = (ex1 + ex2) // 2  # east room X center = 1778

    # Collect door openings in hallway walls across all floors
    w_hall_openings = [
        (KNOTT_SHAFT_Y1, KNOTT_GROUND_Z, KNOTT_SHAFT_Y2, KNOTT_Z2)
    ]  # west stairwell gap — doorway size
    e_hall_openings = [
        (KNOTT_SHAFT_Y1, KNOTT_GROUND_Z, KNOTT_SHAFT_Y2, KNOTT_Z2)
    ]  # shaft gap always open

    for floor_index, fz1, _, fz_surf, _ in floor_levels():
        split = KNOTT_ROOM_SPLITS[floor_index]
        sr_yc = (KNOTT_BIY1 + split) // 2  # south room Y center
        nr_yc = (split + KNOTT.wall_t + KNOTT_BIY2) // 2  # north room Y center
        dz2 = fz_surf + 96  # door top
        w_hall_openings += [
            (sr_yc - 32, fz_surf, sr_yc + 32, dz2),
            (nr_yc - 32, fz_surf, nr_yc + 32, dz2),
        ]
        e_hall_openings += [
            (sr_yc - 32, fz_surf, sr_yc + 32, dz2),
            (nr_yc - 32, fz_surf, nr_yc + 32, dz2),
        ]

    # West hallway wall with room door openings
    BRUSHES.extend(
        layered_wall_y(
            KNOTT_BIY1,
            KNOTT_ENT_X1 - KNOTT.wall_t,
            KNOTT_GROUND_Z,
            KNOTT_BIY2,
            KNOTT_ENT_X1,
            KNOTT_Z2,
            w_hall_openings,
            Textures.WALL,
        )
    )
    # East hallway wall with room door openings + shaft opening
    BRUSHES.extend(
        layered_wall_y(
            KNOTT_BIY1,
            KNOTT_ENT_X2,
            KNOTT_GROUND_Z,
            KNOTT_BIY2,
            KNOTT_ENT_X2 + KNOTT.wall_t,
            KNOTT_Z2,
            e_hall_openings,
            Textures.WALL,
        )
    )

    # Partition walls per floor (divide each side into 2 rooms, with connecting door)
    for floor_index, fz1, fz2, fz_surf, _ in floor_levels():
        split = KNOTT_ROOM_SPLITS[floor_index]
        sp_y2 = split + KNOTT.wall_t
        pdz2 = fz_surf + 96
        # West side partition wall with connecting door
        BRUSHES.extend(
            layered_wall(
                wx1,
                split,
                fz1,
                wx2,
                sp_y2,
                fz2,
                [(KNOTT_WEST_ROOM_CX - 32, fz_surf, KNOTT_WEST_ROOM_CX + 32, pdz2)],
                Textures.WALL,
            )
        )
        # East side partition wall with connecting door
        BRUSHES.extend(
            layered_wall(
                ex1,
                split,
                fz1,
                ex2,
                sp_y2,
                fz2,
                [(KNOTT_EAST_ROOM_CX - 32, fz_surf, KNOTT_EAST_ROOM_CX + 32, pdz2)],
                Textures.WALL,
            )
        )

    if not KNOTT_ENABLED:
        del BRUSHES[knott_brush_start:]

    # ── "LOYOLA UNIVERSITY MARYLAND" bridge fascia lettering ─────────────────────
    # Fascia panel follows the arch: one box per character hanging from deck_bot_z(x)
    # First letter of each word (L, U, M) stays at full pixel size; the rest shrink slightly.
    _cols = 4
    _small_px = BRIDGE_FASCIA_PX_W - 1  # one unit smaller than full size
    _n = len(BRIDGE_FASCIA_TEXT)
    # Word-initial positions in the forward text (L=0, U=7, M=18)
    _capital_pos = {
        i
        for i, ch in enumerate(BRIDGE_FASCIA_TEXT)
        if ch != " " and (i == 0 or BRIDGE_FASCIA_TEXT[i - 1] == " ")
    }
    # Mirror positions for the reversed text used on the north face
    _capital_pos_rev = {_n - 1 - i for i in _capital_pos}

    def _char_pw(i):
        return BRIDGE_FASCIA_PX_W if i in _capital_pos else _small_px

    total_w = sum((_cols + 1) * _char_pw(i) for i in range(_n)) - _char_pw(_n - 1)
    text_x0 = 0 - total_w // 2

    # No separate background fascia boxes — parapet wall face is the backdrop

    def render_text_fascia(
        text, x0, y_face, px_w, px_h, depth, tex, mirror=False, cap_pos=None
    ):
        """Render text as pixel-font raised boxes on a fascia face.
        Each character's Z is computed from deck_top_z(x) so letters follow the arch curve.
        cap_pos: set of character indices that render at full px size (others shrink by 1).
        mirror=True flips each glyph horizontally (needed for north-facing surface)."""
        cols = 4
        rows = 6
        small_pw = px_w - 1
        small_ph = px_h - 1
        if cap_pos is None:
            cap_pos = _capital_pos

        brushes = []
        cx = x0
        for ci, ch in enumerate(text):
            cpw = px_w if ci in cap_pos else small_pw
            cph = px_h if ci in cap_pos else small_ph
            char_w = (cols + 1) * cpw

            bitmap = FASCIA_FONT.get(ch, FASCIA_FONT[" "])
            x_mid = cx + (cols * cpw) / 2
            z_top_cap = int(deck_top_z(x_mid)) + BRIDGE.parapet_h - 14
            # Bottom-align smaller glyphs with capitals
            z_top = z_top_cap - rows * (px_h - cph)

            for row_i, row_bits in enumerate(bitmap):
                z = z_top - row_i * cph
                for col_i in range(cols):
                    src_col = (cols - 1 - col_i) if mirror else col_i
                    if row_bits & (1 << (cols - 1 - src_col)):
                        px = cx + col_i * cpw
                        brushes.append(
                            box(px, y_face - depth, z - cph, px + cpw, y_face, z, tex)
                        )
            cx += char_w
        return brushes

    # Raised pixel-font letters on the Knott Hall sign plaque
    # Text reversed + mirrored so it reads correctly when viewed from north (facing south)
    BRUSHES.extend(
        render_text_flat(
            KNOTT_SIGN_TEXT[::-1],
            x0=knott_sign_cx - knott_sign_total_w // 2,
            y_face=KNOTT.y2 + 6,
            z_base=knott_sign_z1 + 14,  # centered: (48-20)//2 = 14
            px_w=KNOTT_SIGN_PX_W,
            px_h=KNOTT_SIGN_PX_H,
            depth=2,
            tex=Textures.RAIL,
            mirror=True,
        )
    )

    letter_brushes = (
        (
            render_text_fascia(
                BRIDGE_FASCIA_TEXT,
                x0=text_x0,
                y_face=BRIDGE.y1,
                px_w=BRIDGE_FASCIA_PX_W,
                px_h=BRIDGE_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
            )
            + render_text_fascia(
                BRIDGE_FASCIA_TEXT[::-1],
                x0=text_x0,
                y_face=BRIDGE.y2 + 1,
                px_w=BRIDGE_FASCIA_PX_W,
                px_h=BRIDGE_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
                mirror=True,
                cap_pos=_capital_pos_rev,
            )
        )
        if DRAW_BRIDGE_FASCIA_TEXT
        else []
    )

    # ── Campus lamp posts (brush geometry) — along Charles Street (N-S) ──────────
    CHARLES_LAMP_POST_H = BRIDGE_DZ2 - 32  # pole height (~12 ft)
    # Single lamp post — east sidewalk, at the SE corner of the Ennis Road intersection
    CHARLES_LAMP_POST_XS = [
        2158,
        1246,
    ]  # east sidewalk near Ennis (= NE pier − 48), and next pier west
    CHARLES_LAMP_POST_YS = [ENNIS_Y - ENNIS_HW - 160]
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

    # ── Under-bridge pendant lights — one per span, no brush geometry ─────────────
    # ── N/S arch stone wall panels (must be added to B before worldspawn assembly) ──
    CHARLES_ARCH_RIN_PRE = 256  # inner radius = road half-width
    CHARLES_ARCH_ROUT_PRE = 312  # outer radius
    CHARLES_ARCH_STILT_PRE = 96  # stilt height
    CHARLES_ARCH_W_PRE = 48  # arch thickness in Y
    cs_arch_top_pre = FLOOR_Z2 + CHARLES_ARCH_STILT_PRE + CHARLES_ARCH_RIN_PRE

    for pre_syb, pre_syf in [
        (CHARLES_Y1, CHARLES_Y1 + CHARLES_ARCH_W_PRE),
        (CHARLES_Y2 - CHARLES_ARCH_W_PRE, CHARLES_Y2),
    ]:
        # Stone arch posts + ring
        DETAIL_BRUSHES.extend(
            arch_wall_y(
                pre_syb,
                pre_syf,
                WORLD_X1 + WALL_T,
                WORLD_X2 - WALL_T,
                FLOOR_Z2,
                cs_arch_top_pre,
                CHARLES_ARCH_RIN_PRE,
                CHARLES_ARCH_ROUT_PRE,
                A_SEGS,
                Textures.PILLAR,
                stilt_h=CHARLES_ARCH_STILT_PRE,
            )
        )
    if letter_brushes:
        ENTITIES.append(brush_ent("func_detail", letter_brushes))
    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
