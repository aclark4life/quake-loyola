import math

from .constants import (
    A_SEGS,
    BRIDGE_DZ2,
    BRIDGE_PAR_H,
    BRIDGE_Y1,
    BRIDGE_Y2,
    CHARLES_CRN_SEGS,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    CHARLES_Y1,
    CHARLES_Y2,
    ENNIS_HW,
    ENNIS_SW_EDGE,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
    INDENT,
    KH_ENABLED,
    KH_FLOOR_H,
    KH_FLOORS,
    KH_GROUND_Z,
    KH_ORIG_CX,
    KH_SHAFT_X1,
    KH_SHAFT_X2,
    KH_SHAFT_Y1,
    KH_SHAFT_Y2,
    KH_STAIRS_MID_Y,
    KH_STAIRS_X1,
    KH_STAIRS_X2,
    KH_STAIRS_Y1,
    KH_STAIRS_Y2,
    KH_WALL,
    KH_X1,
    KH_X2,
    KH_Y1,
    KH_Y2,
    KH_Z2,
    WALK_ZT2,
    WALL_T,
    WORLD_X1,
    WORLD_X2,
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
    tri_prism,
)


def build():
    BRUSHES = []
    ENTITIES = []
    kh_brush_start = len(BRUSHES)  # checkpoint — trimmed below if KH_ENABLED is False

    # ══════════════════════════════════════════════════════════════════════════════
    # BACK ROAD — east of Knott Hall, slopes south to meet the back of the building
    # Sidewalks with rounded north entrance corners (like Ennis Drive)
    # Road slopes from Z=0 at the north entrance to KH_GROUND_Z at the back.
    # ══════════════════════════════════════════════════════════════════════════════
    KH_BR_HW = 128  # back road half-width (256-unit carriageway, like Ennis)
    KH_BRCS_WALK_W = (
        CHARLES_WALK_W  # sidewalk width = 80 units (matches Charles St sidewalks)
    )
    KH_BRCS_CRN_R = CHARLES_WALK_W  # corner radius = sidewalk width
    KH_BRCS_CRN_SEGS = CHARLES_CRN_SEGS  # 12 arc segments = 90°

    # ── X extents (road runs N-S, east of building east wall) ──
    KH_BR_WS_X1 = KH_X2  # west sidewalk west = building east wall = 1906
    KH_BR_WS_X2 = KH_X2 + KH_BRCS_WALK_W  # west sidewalk east = road west edge = 1986
    KH_BR_RD_X1 = KH_BR_WS_X2  # road west edge = 1986
    KH_BR_RD_X2 = KH_BR_RD_X1 + 2 * KH_BR_HW  # road east edge = 2242
    KH_BR_ES_X1 = KH_BR_RD_X2  # east sidewalk west = 2242
    KH_BR_ES_X2 = KH_BR_RD_X2 + KH_BRCS_WALK_W  # east sidewalk east = 2322

    # ── Y extents (north entrance → south back-wall) ──
    KH_BR_Y1 = KH_Y1  # south end: back of building = -1888
    KH_BR_Y2 = KH_Y2  # north end: north face of building = -256

    # ── Elevation: road surface rises gradually from north (Z=0) to south (Z=hill top) ──
    KH_BR_ZT_N = FLOOR_Z2  # road top at north entrance = 0
    KH_BR_ZT_S = KH_GROUND_Z  # road top at south/back     = 80

    # Road surface — 2-unit textured overlay riding on sloped fill
    BRUSHES.append(
        ramp_slab_y(
            KH_BR_RD_X1,
            KH_BR_RD_X2,
            KH_BR_Y1,
            KH_BR_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KH_BR_ZT_S + 2,
            KH_BR_ZT_N + 2,
            Textures.ROAD,
            tt=Textures.ROAD,
        )
    )
    # Road fill — solid ground under road surface
    BRUSHES.append(
        ramp_slab_y(
            KH_BR_RD_X1,
            KH_BR_RD_X2,
            KH_BR_Y1,
            KH_BR_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KH_BR_ZT_S,
            KH_BR_ZT_N,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    # West sidewalk (strip between building east wall and road) — slopes with road
    BRUSHES.append(
        ramp_slab_y(
            KH_BR_WS_X1,
            KH_BR_WS_X2,
            KH_BR_Y1,
            KH_BR_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KH_BR_ZT_S + CHARLES_WALK_H,
            KH_BR_ZT_N + CHARLES_WALK_H,
            Textures.CEMENT,
            tt=Textures.CEMENT,
        )
    )
    # West sidewalk fill
    BRUSHES.append(
        ramp_slab_y(
            KH_BR_WS_X1,
            KH_BR_WS_X2,
            KH_BR_Y1,
            KH_BR_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KH_BR_ZT_S,
            KH_BR_ZT_N,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    # East sidewalk — slopes with road
    BRUSHES.append(
        ramp_slab_y(
            KH_BR_ES_X1,
            KH_BR_ES_X2,
            KH_BR_Y1,
            KH_BR_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KH_BR_ZT_S + CHARLES_WALK_H,
            KH_BR_ZT_N + CHARLES_WALK_H,
            Textures.CEMENT,
            tt=Textures.CEMENT,
        )
    )
    # East sidewalk fill
    BRUSHES.append(
        ramp_slab_y(
            KH_BR_ES_X1,
            KH_BR_ES_X2,
            KH_BR_Y1,
            KH_BR_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KH_BR_ZT_S,
            KH_BR_ZT_N,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    # Terrain east of east sidewalk — south flat + sloped main section matching sidewalk
    # South extension: flat at hill level
    BRUSHES.append(
        box(
            KH_BR_ES_X2,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            WORLD_X2 - WALL_T,
            KH_BR_Y1,
            KH_BR_ZT_S + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    # Main back road section: slopes with the sidewalk (88 at south → 8 at north)
    BRUSHES.append(
        ramp_slab_y(
            KH_BR_ES_X2,
            WORLD_X2 - WALL_T,
            KH_BR_Y1,
            KH_BR_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KH_BR_ZT_S + CHARLES_WALK_H,
            KH_BR_ZT_N + CHARLES_WALK_H,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    # ── South extension — road + east sidewalk behind Knott Hall to world edge ──
    BRUSHES.append(
        box(
            KH_X1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            KH_BR_ES_X1,
            KH_BR_Y1,
            KH_BR_ZT_S + 2,
            Textures.ROAD,
        )
    )
    BRUSHES.append(
        box(
            KH_BR_ES_X1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            KH_BR_ES_X2,
            KH_BR_Y1,
            KH_BR_ZT_S + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Flat extension north from Knott Hall to Ennis south sidewalk ──────────────
    KH_BR_EXT_Y1 = KH_BR_Y2  # = -256 (north face of building)
    KH_BR_EXT_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_WALK_W

    # Flat road surface
    BRUSHES.append(
        box(
            KH_BR_RD_X1,
            KH_BR_EXT_Y1,
            FLOOR_Z2,
            KH_BR_RD_X2,
            KH_BR_EXT_Y2,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )
    # West sidewalk
    BRUSHES.append(
        box(
            KH_BR_WS_X1,
            KH_BR_EXT_Y1,
            FLOOR_Z2,
            KH_BR_WS_X2,
            KH_BR_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # East sidewalk
    BRUSHES.append(
        box(
            KH_BR_ES_X1,
            KH_BR_EXT_Y1,
            FLOOR_Z2,
            KH_BR_ES_X2,
            KH_BR_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # Terrain east of east sidewalk — flush with sidewalk top
    BRUSHES.append(
        box(
            KH_BR_ES_X2,
            KH_BR_EXT_Y1,
            FLOOR_Z1,
            WORLD_X2 - WALL_T,
            KH_BR_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )

    # Road patch filling the gap between back road end (Y=328) and Ennis road (Y=408)
    # (This was previously the Ennis south sidewalk; now it's part of the road junction)
    BRUSHES.append(
        box(
            KH_BR_RD_X1,
            KH_BR_EXT_Y2,
            FLOOR_Z2,
            KH_BR_RD_X2,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )

    # ── Rounded corners where back road meets Ennis south (inside the junction) ───
    # Centers at the back-road-facing (south) corners so the curved face points toward
    # the back road — matching the Charles/Ennis corner style.
    # West junction corner: center at SW corner (1906, 328), arc sweeps 0°→90°
    KH_BR_JCX_W = KH_BR_WS_X1
    KH_BR_JCY = ENNIS_Y - ENNIS_HW
    BRUSHES.append(
        box(
            KH_BR_WS_X1,
            KH_BR_EXT_Y2,
            FLOOR_Z2,
            KH_BR_RD_X1,
            KH_BR_JCY,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )
    for corner_index in range(KH_BRCS_CRN_SEGS):
        angle_start = math.radians(0 + corner_index * 90 / KH_BRCS_CRN_SEGS)
        angle_end = math.radians(0 + (corner_index + 1) * 90 / KH_BRCS_CRN_SEGS)
        arc_x0 = KH_BR_JCX_W + KH_BRCS_CRN_R * math.cos(angle_start)
        arc_y0 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(angle_start)
        arc_x1 = KH_BR_JCX_W + KH_BRCS_CRN_R * math.cos(angle_end)
        arc_y1 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(angle_end)
        BRUSHES.append(
            tri_prism(
                KH_BR_JCX_W,
                KH_BR_EXT_Y2,
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
    KH_BR_JCX_E = KH_BR_ES_X2
    BRUSHES.append(
        box(
            KH_BR_ES_X1,
            KH_BR_EXT_Y2,
            FLOOR_Z2,
            KH_BR_ES_X2,
            KH_BR_JCY,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )
    for corner_index in range(KH_BRCS_CRN_SEGS):
        angle_start = math.radians(90 + corner_index * 90 / KH_BRCS_CRN_SEGS)
        angle_end = math.radians(90 + (corner_index + 1) * 90 / KH_BRCS_CRN_SEGS)
        arc_x0 = KH_BR_JCX_E + KH_BRCS_CRN_R * math.cos(angle_start)
        arc_y0 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(angle_start)
        arc_x1 = KH_BR_JCX_E + KH_BRCS_CRN_R * math.cos(angle_end)
        arc_y1 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(angle_end)
        BRUSHES.append(
            tri_prism(
                KH_BR_JCX_E,
                KH_BR_EXT_Y2,
                arc_x0,
                arc_y0,
                arc_x1,
                arc_y1,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )

    bix1 = KH_X1 + KH_WALL  # interior west
    bix2 = KH_X2 - KH_WALL  # interior east
    KH_BIY1 = KH_Y1 + KH_WALL  # interior south = -784
    KH_BIY2 = KH_Y2 - KH_WALL  # interior north = -272

    # Entrance doorway — pinned to original building centre, not current KH_CX
    KH_ENT_X1, KH_ENT_X2 = KH_ORIG_CX - 64, KH_ORIG_CX + 64

    # ── Entrance staircase ────────────────────────────────────────────────────────
    KH_STEP_N = 5
    KH_STEP_DEPTH = 24  # tread depth
    KH_STAIR_OFFSET = 384  # distance from north wall to stair base
    stair_base_z = FLOOR_Z2 + CHARLES_WALK_H  # steps start at apron surface height (8)

    # Flat cement platform between building and stairs
    BRUSHES.append(
        box(
            KH_ENT_X1,
            KH_Y2,
            FLOOR_Z2,
            KH_ENT_X2,
            KH_Y2 + KH_STAIR_OFFSET,
            KH_GROUND_Z,
            Textures.CEMENT,
        )
    )

    stair_y0 = KH_Y2 + KH_STAIR_OFFSET  # south edge of staircase
    stair_y_end = (
        stair_y0 + KH_STEP_N * KH_STEP_DEPTH
    )  # north end of stairs (ground level)
    for stair_index in range(KH_STEP_N):
        step_top_z = (
            stair_base_z + (KH_GROUND_Z - stair_base_z) * (stair_index + 1) // KH_STEP_N
        )
        step_north_y = stair_y0 + (KH_STEP_N - stair_index) * KH_STEP_DEPTH
        BRUSHES.append(
            box(
                KH_ENT_X1,
                stair_y0,
                stair_base_z,
                KH_ENT_X2,
                step_north_y,
                step_top_z,
                Textures.CEMENT,
                tt=Textures.CEMENT,
            )
        )

    # Cement sidewalk from stair base to Ennis south sidewalk — flush with ground fill
    BRUSHES.append(
        box(
            KH_ENT_X1,
            stair_y_end,
            FLOOR_Z1,
            KH_ENT_X2,
            ENNIS_SW_EDGE,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Stair side caps (cement cheek walls) ─────────────────────────────────────
    # Solid sloped cement walls on each side of the staircase, top follows stair slope.
    cap_width = 24  # cheek wall thickness (X)
    cap_raise = 16  # extra height above stair slope
    for cap_x1, cap_x2 in [
        (KH_ENT_X1 - cap_width, KH_ENT_X1),  # west cheek
        (KH_ENT_X2, KH_ENT_X2 + cap_width),  # east cheek
    ]:
        BRUSHES.append(
            ramp_slab_y(
                cap_x1,
                cap_x2,
                stair_y0,
                stair_y_end,
                FLOOR_Z1,
                FLOOR_Z1,
                KH_GROUND_Z + cap_raise,
                stair_base_z + cap_raise,
                Textures.CEMENT,
            )
        )

    # ── Stair railings ────────────────────────────────────────────────────────────
    KH_RAIL_H = 72  # stair handrail height
    KH_RAIL_TEX = "metal4_4"
    post_width = 8  # post face width (X) — wide flat-facing
    post_depth = 2  # post depth (Y)
    level_extension = 20  # length of level rail extension at top and bottom
    for rail_x_base, is_west_side in [(KH_ENT_X1, True), (KH_ENT_X2, False)]:
        rail_top_z_at_platform = KH_GROUND_Z + KH_RAIL_H - 28
        rail_top_z_at_apron = stair_base_z + KH_RAIL_H - 28
        rail_x1 = rail_x_base - post_width if is_west_side else rail_x_base
        rail_x2 = rail_x_base if is_west_side else rail_x_base + post_width

        # Sloped cross rail
        BRUSHES.append(
            ramp_slab_y(
                rail_x1,
                rail_x2,
                stair_y0,
                stair_y_end,
                rail_top_z_at_platform,
                rail_top_z_at_apron,
                rail_top_z_at_platform + 2,
                rail_top_z_at_apron + 2,
                KH_RAIL_TEX,
            )
        )

        # Horizontal extension at top (level with platform floor)
        BRUSHES.append(
            box(
                rail_x1,
                stair_y0 - level_extension,
                rail_top_z_at_platform,
                rail_x2,
                stair_y0,
                rail_top_z_at_platform + 2,
                KH_RAIL_TEX,
            )
        )
        # Horizontal extension at bottom (level with apron floor)
        BRUSHES.append(
            box(
                rail_x1,
                stair_y_end,
                rail_top_z_at_apron,
                rail_x2,
                stair_y_end + level_extension,
                rail_top_z_at_apron + 2,
                KH_RAIL_TEX,
            )
        )

        # Posts — wide flat-facing
        for post_y, post_z in [
            (stair_y0, KH_GROUND_Z),
            (stair_y_end, stair_base_z),
        ]:
            BRUSHES.append(
                box(
                    rail_x1,
                    post_y,
                    post_z,
                    rail_x2,
                    post_y + post_depth,
                    post_z + KH_RAIL_H - 26,
                    KH_RAIL_TEX,
                )
            )

    # West stairwell extents defined after INDENT below

    # ── Outer walls ──────────────────────────────────────────────────────────────
    WIN_HALF = 24  # half-width of recessed corner windows
    KH_MULLION_W = 12  # mullion width
    KH_MULLION_PRO = 12  # mullion protrusion depth

    # South wall — mirrors north wall: indented SW/SE corners with recessed windows
    # Main south face — hallway openings cut through at each floor level
    s_wall_openings = [
        (
            KH_ENT_X1,
            KH_GROUND_Z + fl * KH_FLOOR_H + KH_WALL,
            KH_ENT_X2,
            KH_GROUND_Z + (fl + 1) * KH_FLOOR_H,
        )
        for fl in range(KH_FLOORS)
    ]
    BRUSHES.extend(
        layered_wall(
            KH_X1 + INDENT,
            KH_Y1,
            KH_GROUND_Z,
            KH_X2 - INDENT,
            KH_Y1 + KH_WALL,
            KH_Z2,
            s_wall_openings,
            Textures.WALL,
        )
    )
    # SW Indentation inner walls — recessed back wall with centered 48-unit window
    sw_win_cx = KH_X1 + INDENT // 2
    BRUSHES.extend(
        layered_wall(
            KH_X1,
            KH_Y1 + INDENT - KH_WALL,
            FLOOR_Z1,
            KH_X1 + INDENT,
            KH_Y1 + INDENT,
            KH_Z2,
            [
                (
                    sw_win_cx - WIN_HALF,
                    KH_GROUND_Z + KH_FLOOR_H,
                    sw_win_cx + WIN_HALF,
                    KH_Z2,
                )
            ],
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KH_X1 + INDENT - KH_WALL,
            KH_Y1,
            FLOOR_Z1,
            KH_X1 + INDENT,
            KH_Y1 + INDENT,
            KH_Z2,
            Textures.WALL,
        )
    )
    # SE Indentation inner walls — recessed back wall with centered 48-unit window
    se_win_cx = KH_X2 - INDENT // 2
    BRUSHES.extend(
        layered_wall(
            KH_X2 - INDENT,
            KH_Y1 + INDENT - KH_WALL,
            FLOOR_Z1,
            KH_X2,
            KH_Y1 + INDENT,
            KH_Z2,
            [
                (
                    se_win_cx - WIN_HALF,
                    KH_GROUND_Z + KH_FLOOR_H,
                    se_win_cx + WIN_HALF,
                    KH_Z2,
                )
            ],
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KH_X2 - INDENT,
            KH_Y1,
            FLOOR_Z1,
            KH_X2 - INDENT + KH_WALL,
            KH_Y1 + INDENT,
            KH_Z2,
            Textures.WALL,
        )
    )
    # South mullions — protrude outward (south, -Y)
    for mx in [sw_win_cx - WIN_HALF - KH_MULLION_W, sw_win_cx + WIN_HALF]:
        BRUSHES.append(
            box(
                mx,
                KH_Y1 + INDENT - KH_WALL,
                KH_GROUND_Z + KH_FLOOR_H,
                mx + KH_MULLION_W,
                KH_Y1 + INDENT + KH_MULLION_PRO,
                KH_Z2,
                Textures.CEMENT,
            )
        )
    for mx in [se_win_cx - WIN_HALF - KH_MULLION_W, se_win_cx + WIN_HALF]:
        BRUSHES.append(
            box(
                mx,
                KH_Y1 + INDENT - KH_WALL,
                KH_GROUND_Z + KH_FLOOR_H,
                mx + KH_MULLION_W,
                KH_Y1 + INDENT + KH_MULLION_PRO,
                KH_Z2,
                Textures.CEMENT,
            )
        )
    # Horizontal mullions — SW and SE south-face indentation windows, matching east/west walls
    for wx in [sw_win_cx, se_win_cx]:
        for fl in range(1, KH_FLOORS):
            mz = KH_GROUND_Z + fl * KH_FLOOR_H + KH_FLOOR_H // 2
            BRUSHES.append(
                box(
                    wx - WIN_HALF,
                    KH_Y1 + INDENT - KH_WALL,
                    mz,
                    wx + WIN_HALF,
                    KH_Y1 + INDENT + KH_MULLION_PRO,
                    mz + 4,
                    Textures.RAIL,
                )
            )
    # Floor-level mullions — SW and SE south-face windows
    for wx in [sw_win_cx, se_win_cx]:
        for fl in range(1, KH_FLOORS + 1):
            fz = KH_GROUND_Z + fl * KH_FLOOR_H
            BRUSHES.append(
                box(
                    wx - WIN_HALF,
                    KH_Y1 + INDENT - KH_WALL,
                    fz - 4 if fl > 0 else KH_GROUND_Z,
                    wx + WIN_HALF,
                    KH_Y1 + INDENT + KH_MULLION_PRO,
                    (fz if fl > 0 else KH_GROUND_Z + 4),
                    Textures.RAIL,
                )
            )
    # North-West Indentation (Corner Notch)
    # North wall — faces bridge; ground entrance + 2nd-floor walkway opening
    door_ground = [
        (KH_ENT_X1, KH_GROUND_Z, KH_ENT_X2, KH_GROUND_Z + KH_FLOOR_H)
    ]  # ground entrance
    door_upper = [
        (KH_ENT_X1, WALK_ZT2, KH_ENT_X2, KH_GROUND_Z + KH_FLOOR_H * 2)
    ]  # walkway entrance
    win_n = [
        (KH_ORIG_CX - 48, KH_GROUND_Z + KH_FLOOR_H * 2, KH_ORIG_CX - 6, KH_Z2),
        (KH_ORIG_CX + 6, KH_GROUND_Z + KH_FLOOR_H * 2, KH_ORIG_CX + 48, KH_Z2),
    ]  # two window slots centered over entrance doorway, split by center mullion
    BRUSHES.extend(
        layered_wall(
            KH_X1 + 2 * INDENT,
            KH_Y2 - KH_WALL,
            KH_GROUND_Z,
            KH_X2 - INDENT,
            KH_Y2,
            KH_Z2,
            door_ground + door_upper + win_n,
            Textures.WALL,
        )
    )

    # NW Indentation — 2×INDENT wide (extends west to KH_X1), two windows side by side
    nw_win_cx1 = KH_X1 + INDENT // 2  # west window = 1246 (pier-aligned)
    nw_win_cx2 = KH_X1 + INDENT + INDENT // 2  # east window = 1326
    BRUSHES.extend(
        layered_wall(
            KH_X1,
            KH_Y2 - INDENT,
            FLOOR_Z1,
            KH_X1 + 2 * INDENT,
            KH_Y2 - INDENT + KH_WALL,
            KH_Z2,
            [
                (
                    nw_win_cx1 - WIN_HALF,
                    KH_GROUND_Z + KH_FLOOR_H,
                    nw_win_cx1 + WIN_HALF,
                    KH_Z2,
                ),
                (
                    nw_win_cx2 - WIN_HALF,
                    KH_GROUND_Z + KH_FLOOR_H,
                    nw_win_cx2 + WIN_HALF,
                    KH_Z2,
                ),
            ],
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KH_X1 + 2 * INDENT - KH_WALL,
            KH_Y2 - INDENT,
            FLOOR_Z1,
            KH_X1 + 2 * INDENT,
            KH_Y2,
            KH_Z2,
            Textures.WALL,
        )
    )

    # NE Indentation inner walls (mirror of NW) — recessed back wall has a centered 48-unit window
    ne_win_cx = KH_X2 - INDENT // 2
    BRUSHES.extend(
        layered_wall(
            KH_X2 - INDENT,
            KH_Y2 - INDENT,
            FLOOR_Z1,
            KH_X2,
            KH_Y2 - INDENT + KH_WALL,
            KH_Z2,
            [
                (
                    ne_win_cx - WIN_HALF,
                    KH_GROUND_Z + KH_FLOOR_H,
                    ne_win_cx + WIN_HALF,
                    KH_Z2,
                )
            ],
            Textures.WALL,
        )
    )
    BRUSHES.append(
        box(
            KH_X2 - INDENT,
            KH_Y2 - INDENT,
            FLOOR_Z1,
            KH_X2 - INDENT + KH_WALL,
            KH_Y2,
            KH_Z2,
            Textures.WALL,
        )
    )

    # Front mullions — protruding sfloor3_2 posts on each side of the recessed windows
    # and the narrow vertical window on the main north face. All protrude 12 units outward.
    # NW recessed windows: mullions for both (west and east window in the wide NW indentation)
    for mx in [
        nw_win_cx1 - WIN_HALF - KH_MULLION_W,
        nw_win_cx1 + WIN_HALF,
        nw_win_cx2 - WIN_HALF - KH_MULLION_W,
        nw_win_cx2 + WIN_HALF,
    ]:
        BRUSHES.append(
            box(
                mx,
                KH_Y2 - INDENT - KH_MULLION_PRO,
                KH_GROUND_Z + KH_FLOOR_H,
                mx + KH_MULLION_W,
                KH_Y2 - INDENT + KH_WALL,
                KH_Z2,
                Textures.CEMENT,
            )
        )
    # NE recessed window: mullions just outside the opening so player can fit through
    for mx in [ne_win_cx - WIN_HALF - KH_MULLION_W, ne_win_cx + WIN_HALF]:
        BRUSHES.append(
            box(
                mx,
                KH_Y2 - INDENT - KH_MULLION_PRO,
                KH_GROUND_Z + KH_FLOOR_H,
                mx + KH_MULLION_W,
                KH_Y2 - INDENT + KH_WALL,
                KH_Z2,
                Textures.CEMENT,
            )
        )
    # Main front wall window win_n: mullions on each side and center post
    win_n_x1, win_n_x2 = KH_ORIG_CX - 48, KH_ORIG_CX + 48
    win_n_mid = KH_ORIG_CX - 6  # left edge of center mullion
    for mx in [win_n_x1 - KH_MULLION_W, win_n_mid, win_n_x2]:
        BRUSHES.append(
            box(
                mx,
                KH_Y2 - KH_WALL,
                KH_GROUND_Z + KH_FLOOR_H * 2,
                mx + KH_MULLION_W,
                KH_Y2 + KH_MULLION_PRO,
                KH_Z2,
                Textures.CEMENT,
            )
        )

    # ── "Marion Burk Knott Hall" sign plaque — north face, 2nd floor level ───────
    # Protruding cement slab, sized to fit pixel-font lettering
    sign_text = "MARION BURK KNOTT HALL"
    sign_pixel_width, sign_pixel_height = 2, 4
    sign_char_width = (4 + 1) * sign_pixel_width
    sign_total_width = len(sign_text) * sign_char_width - sign_pixel_width
    sign_half_width = sign_total_width // 2 + 4  # 4 unit padding each side = 222
    sign_center_x = KH_X2 - INDENT - sign_half_width  # east edge flush with wall end
    sign_z1 = KH_GROUND_Z + KH_FLOOR_H * 2 + 20  # just above 2nd floor line
    sign_z2 = sign_z1 + 48  # 48 units tall
    BRUSHES.append(
        box(
            sign_center_x - sign_half_width,
            KH_Y2,
            sign_z1,
            sign_center_x + sign_half_width,
            KH_Y2 + 6,
            sign_z2,
            Textures.CEMENT,
        )
    )
    # Letter brushes deferred — render_text_flat defined below

    # ── Brutalist Fins (All Exposed Facades) — currently disabled ─────────────────

    # East wall — three 120-unit wide floor-to-ceiling windows, matching west side
    # Shared window layout variables (used for both east and west walls)
    ww_half = 120
    ww_wall_y1, ww_wall_y2 = KH_Y1, KH_Y2 - INDENT
    ww_quarter = (ww_wall_y2 - ww_wall_y1) // 4
    ww_c1 = ww_wall_y1 + ww_quarter
    ww_c2 = ww_wall_y1 + 2 * ww_quarter
    ww_c3 = ww_wall_y1 + 3 * ww_quarter
    ww_div_w = 12
    ww_protrude = 12
    BRUSHES.extend(
        layered_wall_y(
            ww_wall_y1,
            KH_X2 - KH_WALL,
            KH_GROUND_Z,
            ww_wall_y2,
            KH_X2,
            KH_Z2,
            [
                (ww_c1 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c1 + ww_half, KH_Z2),
                (ww_c2 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c2 + ww_half, KH_Z2),
                (ww_c3 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c3 + ww_half, KH_Z2),
            ],
            Textures.WALL,
        )
    )
    # Vertical mullions — protrude 12 units east of wall face
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for mullion_y in [
            window_center_y - ww_half,  # left edge
            window_center_y - 48,  # interior left
            window_center_y + 36,  # interior right
            window_center_y + ww_half - ww_div_w,  # right edge
        ]:
            BRUSHES.append(
                box(
                    KH_X2 - KH_WALL,
                    mullion_y,
                    KH_GROUND_Z + KH_FLOOR_H,
                    KH_X2 + ww_protrude,
                    mullion_y + ww_div_w,
                    KH_Z2,
                    Textures.CEMENT,
                )
            )

    # Horizontal mullions — centered in each floor span for contrast, players still fit through
    # Mid-floor Z leaves ~85 units clearance each side (player height = 56)
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for fl in range(1, KH_FLOORS):
            mz = KH_GROUND_Z + fl * KH_FLOOR_H + KH_FLOOR_H // 2
            BRUSHES.append(
                box(
                    KH_X2 - KH_WALL,
                    window_center_y - ww_half,
                    mz,
                    KH_X2 + ww_protrude,
                    window_center_y + ww_half,
                    mz + 4,
                    Textures.RAIL,
                )
            )
    # Floor-level mullions — sill at base of each floor (floors 1+), lintel at top of each floor
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for fl in range(1, KH_FLOORS + 1):
            fz = KH_GROUND_Z + fl * KH_FLOOR_H
            BRUSHES.append(
                box(
                    KH_X2 - KH_WALL,
                    window_center_y - ww_half,
                    fz - 4 if fl > 0 else KH_GROUND_Z,
                    KH_X2 + ww_protrude,
                    window_center_y + ww_half,
                    (fz if fl > 0 else KH_GROUND_Z + 4),
                    Textures.RAIL,
                )
            )

    # West wall — three 120-unit wide floor-to-ceiling windows, evenly spread
    BRUSHES.extend(
        layered_wall_y(
            ww_wall_y1,
            KH_X1,
            KH_GROUND_Z,
            ww_wall_y2,
            KH_X1 + KH_WALL,
            KH_Z2,
            [
                (ww_c1 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c1 + ww_half, KH_Z2),
                (ww_c2 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c2 + ww_half, KH_Z2),
                (ww_c3 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c3 + ww_half, KH_Z2),
            ],
            Textures.WALL,
        )
    )
    # Vertical mullions — protrude 12 units west of wall face
    # 2 interior + 2 side mullions per window (4 total each)
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for mullion_y in [
            window_center_y - ww_half,  # left edge
            window_center_y - 48,  # interior left
            window_center_y + 36,  # interior right
            window_center_y + ww_half - ww_div_w,  # right edge
        ]:
            BRUSHES.append(
                box(
                    KH_X1 - ww_protrude,
                    mullion_y,
                    KH_GROUND_Z + KH_FLOOR_H,
                    KH_X1 + KH_WALL,
                    mullion_y + ww_div_w,
                    KH_Z2,
                    Textures.CEMENT,
                )
            )

    # Horizontal mullions — west wall, matching east
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for fl in range(1, KH_FLOORS):
            mz = KH_GROUND_Z + fl * KH_FLOOR_H + KH_FLOOR_H // 2
            BRUSHES.append(
                box(
                    KH_X1 - ww_protrude,
                    window_center_y - ww_half,
                    mz,
                    KH_X1 + KH_WALL,
                    window_center_y + ww_half,
                    mz + 4,
                    Textures.RAIL,
                )
            )
    # Floor-level mullions — west wall
    for window_center_y in [ww_c1, ww_c2, ww_c3]:
        for fl in range(1, KH_FLOORS + 1):
            fz = KH_GROUND_Z + fl * KH_FLOOR_H
            BRUSHES.append(
                box(
                    KH_X1 - ww_protrude,
                    window_center_y - ww_half,
                    fz - 4 if fl > 0 else KH_GROUND_Z,
                    KH_X1 + KH_WALL,
                    window_center_y + ww_half,
                    (fz if fl > 0 else KH_GROUND_Z + 4),
                    Textures.RAIL,
                )
            )

    # Horizontal mullions — win_n narrow slot window on main north face (floors 2–3)
    for fl in range(2, KH_FLOORS):
        mz = KH_GROUND_Z + fl * KH_FLOOR_H + KH_FLOOR_H // 2
        BRUSHES.append(
            box(
                win_n_x1,
                KH_Y2 - KH_WALL,
                mz,
                win_n_x2,
                KH_Y2 + KH_MULLION_PRO,
                mz + 4,
                Textures.RAIL,
            )
        )
    # Floor-level mullions — win_n
    for fl in range(2, KH_FLOORS + 1):
        fz = KH_GROUND_Z + fl * KH_FLOOR_H
        if fz <= KH_Z2:
            BRUSHES.append(
                box(
                    win_n_x1,
                    KH_Y2 - KH_WALL,
                    fz - 4 if fl > 0 else KH_GROUND_Z,
                    win_n_x2,
                    KH_Y2 + KH_MULLION_PRO,
                    (fz if fl > 0 else KH_GROUND_Z + 4),
                    Textures.RAIL,
                )
            )
    for window_center_x, window_half_width in [
        (nw_win_cx1, WIN_HALF),
        (nw_win_cx2, WIN_HALF),
        (ne_win_cx, WIN_HALF),
    ]:
        for fl in range(1, KH_FLOORS):
            mz = KH_GROUND_Z + fl * KH_FLOOR_H + KH_FLOOR_H // 2
            BRUSHES.append(
                box(
                    window_center_x - window_half_width,
                    KH_Y2 - INDENT - KH_MULLION_PRO,
                    mz,
                    window_center_x + window_half_width,
                    KH_Y2 - INDENT + KH_WALL,
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
        for fl in range(1, KH_FLOORS + 1):
            fz = KH_GROUND_Z + fl * KH_FLOOR_H
            BRUSHES.append(
                box(
                    window_center_x - window_half_width,
                    KH_Y2 - INDENT - KH_MULLION_PRO,
                    fz - 4 if fl > 0 else KH_GROUND_Z,
                    window_center_x + window_half_width,
                    KH_Y2 - INDENT + KH_WALL,
                    (fz if fl > 0 else KH_GROUND_Z + 4),
                    Textures.RAIL,
                )
            )

    # Roof — open above lift shaft, clipped for NW indentation
    BRUSHES.append(
        box(
            KH_X1,
            KH_Y1,
            KH_Z2,
            KH_STAIRS_X1,
            KH_Y2 - INDENT,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # far-west bulk
    BRUSHES.append(
        box(
            KH_X1 + 2 * INDENT,
            KH_Y2 - INDENT,
            KH_Z2,
            KH_STAIRS_X1,
            KH_Y2,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # far-west north-strip
    BRUSHES.append(
        box(
            KH_STAIRS_X1,
            KH_Y1,
            KH_Z2,
            KH_STAIRS_X2,
            KH_STAIRS_Y1,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # south of west stairwell
    BRUSHES.append(
        box(
            KH_STAIRS_X1,
            KH_STAIRS_Y2,
            KH_Z2,
            KH_STAIRS_X2,
            KH_Y2,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # north of west stairwell
    BRUSHES.append(
        box(
            KH_STAIRS_X2,
            KH_Y1,
            KH_Z2,
            KH_SHAFT_X1,
            KH_Y2,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # between shafts (no indent — interior)
    BRUSHES.append(
        box(
            KH_SHAFT_X2,
            KH_Y1,
            KH_Z2,
            KH_X2,
            KH_Y2 - INDENT,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # east bulk
    BRUSHES.append(
        box(
            KH_SHAFT_X2,
            KH_Y2 - INDENT,
            KH_Z2,
            KH_X2 - INDENT,
            KH_Y2,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # east north-strip (NE cutout)
    BRUSHES.append(
        box(
            KH_SHAFT_X1,
            KH_Y1,
            KH_Z2,
            KH_SHAFT_X2,
            KH_SHAFT_Y1,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # south of shaft
    BRUSHES.append(
        box(
            KH_SHAFT_X1,
            KH_SHAFT_Y2,
            KH_Z2,
            KH_SHAFT_X2,
            KH_Y2,
            KH_Z2 + KH_WALL,
            Textures.FLOOR_KH,
        )
    )  # north of shaft (closes roof over north wall above shaft)

    # ── Interior floor slabs (floors 0-3, lift shaft opening in center-north) ────
    # Floor 0 (ground): full slab with no shaft opening, clipped for NW indentation
    sz0 = KH_GROUND_Z
    st0 = sz0 + KH_WALL
    BRUSHES.append(
        box(KH_X1, KH_Y1, sz0, KH_X2, KH_Y2 - INDENT, st0, Textures.FLOOR_KH)
    )
    BRUSHES.append(
        box(
            KH_X1 + 2 * INDENT,
            KH_Y2 - INDENT,
            sz0,
            KH_X2 - INDENT,
            KH_Y2,
            st0,
            Textures.FLOOR_KH,
        )
    )

    for floor_index in range(1, KH_FLOORS):
        floor_z1 = KH_GROUND_Z + floor_index * KH_FLOOR_H
        floor_z2 = floor_z1 + KH_WALL
        # South bulk — full width up to stairwell's south wall
        BRUSHES.append(
            box(
                bix1, KH_BIY1, floor_z1, bix2, KH_STAIRS_Y1, floor_z2, Textures.FLOOR_KH
            )
        )
        # Stairwell south extension (KH_STAIRS_Y1..KH_SHAFT_Y1): floor on either side, stairwell open
        BRUSHES.append(
            box(
                bix1,
                KH_STAIRS_Y1,
                floor_z1,
                KH_STAIRS_X1,
                KH_SHAFT_Y1,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )
        BRUSHES.append(
            box(
                KH_STAIRS_X2,
                KH_STAIRS_Y1,
                floor_z1,
                bix2,
                KH_SHAFT_Y1,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )
        # North zone (KH_SHAFT_Y1..KH_BIY2): west of stairwell, clipped for NW indentation
        BRUSHES.append(
            box(
                bix1,
                KH_SHAFT_Y1,
                floor_z1,
                KH_STAIRS_X1,
                KH_Y2 - INDENT,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )
        # Between west stairwell and east shaft
        BRUSHES.append(
            box(
                KH_STAIRS_X2,
                KH_SHAFT_Y1,
                floor_z1,
                KH_SHAFT_X1,
                KH_BIY2,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )
        # East of shaft, clipped for NE indentation
        BRUSHES.append(
            box(
                KH_SHAFT_X2,
                KH_SHAFT_Y1,
                floor_z1,
                bix2,
                KH_Y2 - INDENT,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )
        BRUSHES.append(
            box(
                KH_SHAFT_X2,
                KH_Y2 - INDENT,
                floor_z1,
                bix2 - INDENT,
                KH_BIY2,
                floor_z2,
                Textures.FLOOR_KH,
            )
        )

    # ── Elevator Shaft Enclosure ──────────────────────────────────────────────
    # Walls around the lift shaft (KH_SHAFT_X1..KH_SHAFT_X2, KH_SHAFT_Y1..KH_SHAFT_Y2)
    shaft_wall = 8
    # Door opening dimensions per floor (used for both wall openings and func_door entities)
    shaft_door_h = KH_FLOOR_H  # door height matches floor-to-floor height
    shaft_door_openings = [
        (
            KH_SHAFT_Y1 + 16,
            KH_GROUND_Z + floor_index * KH_FLOOR_H,
            KH_SHAFT_Y2 - 16,
            KH_GROUND_Z + floor_index * KH_FLOOR_H + shaft_door_h,
        )
        for floor_index in range(KH_FLOORS)
    ]

    # Shaft North wall (internal, solid)
    BRUSHES.append(
        box(
            KH_SHAFT_X1,
            KH_SHAFT_Y2,
            KH_GROUND_Z,
            KH_SHAFT_X2,
            KH_SHAFT_Y2 + shaft_wall,
            KH_Z2,
            Textures.WALL,
        )
    )
    # Shaft South wall (internal, solid)
    BRUSHES.append(
        box(
            KH_SHAFT_X1,
            KH_SHAFT_Y1 - shaft_wall,
            KH_GROUND_Z,
            KH_SHAFT_X2,
            KH_SHAFT_Y1,
            KH_Z2,
            Textures.WALL,
        )
    )
    # Shaft West wall (internal, openings for each floor's door — flush with hallway east wall and shaft interior)
    BRUSHES.extend(
        layered_wall_y(
            KH_SHAFT_Y1,
            KH_ENT_X2,
            KH_GROUND_Z,
            KH_SHAFT_Y2,
            KH_SHAFT_X1,
            KH_Z2,
            shaft_door_openings,
            Textures.WALL,
        )
    )
    # Shaft East wall (internal)
    BRUSHES.append(
        box(
            KH_SHAFT_X2,
            KH_SHAFT_Y1,
            KH_GROUND_Z,
            KH_SHAFT_X2 + shaft_wall,
            KH_SHAFT_Y2,
            KH_Z2,
            Textures.WALL,
        )
    )

    # ── West Stairwell Enclosure ──────────────────────────────────────────────────
    # Walls around the west stairwell (KH_STAIRS_X1..KH_STAIRS_X2, KH_STAIRS_Y1..KH_STAIRS_Y2)
    west_shaft_door_openings = [
        (
            KH_SHAFT_Y1 + 16,  # same Y extents as east shaft doorway
            KH_GROUND_Z + floor_index * KH_FLOOR_H,
            KH_SHAFT_Y2 - 16,
            KH_GROUND_Z + floor_index * KH_FLOOR_H + shaft_door_h,
        )
        for floor_index in range(KH_FLOORS)
    ]

    # West stairwell North wall (internal, solid)
    BRUSHES.append(
        box(
            KH_STAIRS_X1,
            KH_STAIRS_Y2,
            KH_GROUND_Z,
            KH_STAIRS_X2,
            KH_STAIRS_Y2 + shaft_wall,
            KH_Z2,
            Textures.WALL,
        )
    )
    # West stairwell South wall (internal, solid)
    BRUSHES.append(
        box(
            KH_STAIRS_X1,
            KH_STAIRS_Y1 - shaft_wall,
            KH_GROUND_Z,
            KH_STAIRS_X2,
            KH_STAIRS_Y1,
            KH_Z2,
            Textures.WALL,
        )
    )
    # West stairwell East wall (internal, openings for each floor's door — flush both sides)
    BRUSHES.extend(
        layered_wall_y(
            KH_STAIRS_Y1,
            KH_STAIRS_X2,
            KH_GROUND_Z,
            KH_STAIRS_Y2,
            KH_ENT_X1,
            KH_Z2,
            west_shaft_door_openings,
            Textures.WALL,
        )
    )
    # West stairwell West wall (internal, solid)
    BRUSHES.append(
        box(
            KH_STAIRS_X1 - shaft_wall,
            KH_STAIRS_Y1,
            KH_GROUND_Z,
            KH_STAIRS_X1,
            KH_STAIRS_Y2,
            KH_Z2,
            Textures.WALL,
        )
    )

    # ── West Stairwell — Switchback Staircase ─────────────────────────────────────
    # Stairs compressed to the shaft centre (192 u wide), leaving 88-unit flanks for
    # half-floor platforms on the east and west sides.
    #
    # North lane (KH_STAIRS_MID_Y..KH_STAIRS_Y2): enter east door, walk WEST, rise z0 → z_mid.
    # West platform at z_mid (full shaft Y, 88 u wide) — turn-around landing.
    # South lane (KH_STAIRS_Y1..KH_STAIRS_MID_Y): walk EAST, rise z_mid → z_top.
    #
    # Step 0 of north lane and step 7 of south lane extend east to KH_STAIRS_X2 so the
    # door at each floor connects directly to the staircase.
    # Loop runs KH_FLOORS times (fl 0→4) — top flight exits onto building roof.
    KH_STAIRS_HALF_N = 8
    KH_STAIRS_STEP_R = 10  # rise per step (≤ 18-unit Quake limit)
    KH_STAIRS_TREAD_X = 24  # compressed tread depth: 8 × 24 = 192
    PLAT_H = 8  # platform slab thickness
    stair_cx = (KH_STAIRS_X1 + KH_STAIRS_X2) // 2  # shaft X centre
    stair_x1 = (
        stair_cx - KH_STAIRS_HALF_N * KH_STAIRS_TREAD_X // 2
    )  # west edge of stairs
    stair_x2 = stair_x1 + KH_STAIRS_HALF_N * KH_STAIRS_TREAD_X  # east edge of stairs
    for floor_index in range(KH_FLOORS):
        floor_z0 = KH_GROUND_Z + floor_index * KH_FLOOR_H + KH_WALL  # floor surface Z
        half_flight_z = (
            floor_z0 + KH_STAIRS_HALF_N * KH_STAIRS_STEP_R
        )  # half-floor Z (floor_z0 + 80)
        top_flight_z = floor_z0 + KH_FLOOR_H  # next floor surface Z (= exit level)

        # Entrance landing — flush with hallway floor, east of stair band (north lane).
        BRUSHES.append(
            box(
                stair_x2,
                KH_STAIRS_MID_Y,
                floor_z0 - PLAT_H,
                KH_STAIRS_X2,
                KH_STAIRS_Y2,
                floor_z0,
                Textures.FLOOR_KH,
            )
        )
        # Exit landing — flush with next floor, east of stair band (south lane).
        BRUSHES.append(
            box(
                stair_x2,
                KH_STAIRS_Y1,
                top_flight_z - PLAT_H,
                KH_STAIRS_X2,
                KH_STAIRS_MID_Y,
                top_flight_z,
                Textures.FLOOR_KH,
            )
        )

        # North lane: individual treads ascending westward (stair_x2 → stair_x1).
        for tread_index in range(KH_STAIRS_HALF_N):
            step_x_east = stair_x2 - tread_index * KH_STAIRS_TREAD_X
            step_x_west = stair_x2 - (tread_index + 1) * KH_STAIRS_TREAD_X
            step_z1 = floor_z0 + tread_index * KH_STAIRS_STEP_R
            BRUSHES.append(
                box(
                    step_x_west,
                    KH_STAIRS_MID_Y,
                    step_z1,
                    step_x_east,
                    KH_STAIRS_Y2,
                    step_z1 + KH_STAIRS_STEP_R,
                    Textures.WALL,
                    tt=Textures.FLOOR_KH,
                )
            )

        # Half-floor west platform: turn-around landing, full shaft Y depth.
        BRUSHES.append(
            box(
                KH_STAIRS_X1,
                KH_STAIRS_Y1,
                half_flight_z - PLAT_H,
                stair_x1,
                KH_STAIRS_Y2,
                half_flight_z,
                Textures.FLOOR_KH,
            )
        )

        # South lane: individual treads ascending eastward (stair_x1 → stair_x2).
        for tread_index in range(KH_STAIRS_HALF_N):
            step_x_west = stair_x1 + tread_index * KH_STAIRS_TREAD_X
            step_x_east = step_x_west + KH_STAIRS_TREAD_X
            step_z1 = half_flight_z + tread_index * KH_STAIRS_STEP_R
            BRUSHES.append(
                box(
                    step_x_west,
                    KH_STAIRS_Y1,
                    step_z1,
                    step_x_east,
                    KH_STAIRS_MID_Y,
                    step_z1 + KH_STAIRS_STEP_R,
                    Textures.WALL,
                    tt=Textures.FLOOR_KH,
                )
            )

    # ── West Stairwell — Iron Railings ────────────────────────────────────────────
    # 2 end posts + 1 sloped cross rail per half-flight, central divider (KH_STAIRS_MID_Y).
    # Posts sit OUTSIDE the stair band (on the entrance area and west platform) so
    # they never land on a tread.  Cross rail spans the full stair band between them.
    KH_STAIRS_RAIL_H = 72  # handrail height above landing surface (bottom of rail = 68u, clears 56u player)
    KH_STAIRS_POST_W = 4  # square post cross-section
    KH_STAIRS_RAIL_T = 4  # cross-rail bar thickness

    for floor_index in range(KH_FLOORS):
        floor_z0 = KH_GROUND_Z + floor_index * KH_FLOOR_H + KH_WALL
        half_flight_z = floor_z0 + KH_STAIRS_HALF_N * KH_STAIRS_STEP_R
        top_flight_z = half_flight_z + KH_STAIRS_HALF_N * KH_STAIRS_STEP_R

        # ── North lane — south face (KH_STAIRS_MID_Y) ────────────────────────────────
        # Lower post: east of stair band, in the entrance area
        BRUSHES.append(
            box(
                stair_x2,
                KH_STAIRS_MID_Y,
                floor_z0,
                stair_x2 + KH_STAIRS_POST_W,
                KH_STAIRS_MID_Y + KH_STAIRS_POST_W,
                floor_z0 + KH_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )
        # Upper post: west of stair band, on the west platform
        BRUSHES.append(
            box(
                stair_x1 - KH_STAIRS_POST_W,
                KH_STAIRS_MID_Y,
                half_flight_z,
                stair_x1,
                KH_STAIRS_MID_Y + KH_STAIRS_POST_W,
                half_flight_z + KH_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )
        # Sloped cross rail along center divider (high at west, low at east)
        BRUSHES.append(
            ramp_slab(
                stair_x1,
                stair_x2,
                KH_STAIRS_MID_Y,
                KH_STAIRS_MID_Y + KH_STAIRS_RAIL_T,
                half_flight_z + KH_STAIRS_RAIL_H - KH_STAIRS_RAIL_T,
                floor_z0 + KH_STAIRS_RAIL_H - KH_STAIRS_RAIL_T,
                half_flight_z + KH_STAIRS_RAIL_H,
                floor_z0 + KH_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

        # ── South lane — north face (KH_STAIRS_MID_Y) ────────────────────────────────
        # Lower post: west of stair band, on the west platform
        BRUSHES.append(
            box(
                stair_x1 - KH_STAIRS_POST_W,
                KH_STAIRS_MID_Y - KH_STAIRS_POST_W,
                half_flight_z,
                stair_x1,
                KH_STAIRS_MID_Y,
                half_flight_z + KH_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )
        # Upper post: east of stair band, in the entrance area
        BRUSHES.append(
            box(
                stair_x2,
                KH_STAIRS_MID_Y - KH_STAIRS_POST_W,
                top_flight_z,
                stair_x2 + KH_STAIRS_POST_W,
                KH_STAIRS_MID_Y,
                top_flight_z + KH_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )
        # Sloped cross rail along center divider (low at west, high at east)
        BRUSHES.append(
            ramp_slab(
                stair_x1,
                stair_x2,
                KH_STAIRS_MID_Y - KH_STAIRS_RAIL_T,
                KH_STAIRS_MID_Y,
                half_flight_z + KH_STAIRS_RAIL_H - KH_STAIRS_RAIL_T,
                top_flight_z + KH_STAIRS_RAIL_H - KH_STAIRS_RAIL_T,
                half_flight_z + KH_STAIRS_RAIL_H,
                top_flight_z + KH_STAIRS_RAIL_H,
                Textures.RAIL,
            )
        )

    # Partition Y splits vary per floor so each floor has different room proportions.
    KH_ROOM_SPLITS = [-1072, -950, -1200, -850, -1300]  # partition Y per floor

    wx1, wx2 = bix1, KH_ENT_X1 - KH_WALL  # west room X extents (1282..1506)
    ex1, ex2 = KH_ENT_X2 + KH_WALL, bix2  # east room X extents (1666..1890)
    KH_WEST_ROOM_CX = (wx1 + wx2) // 2  # west room X center = 1394
    KH_EAST_ROOM_CX = (ex1 + ex2) // 2  # east room X center = 1778

    # Collect door openings in hallway walls across all floors
    w_hall_openings = [
        (KH_SHAFT_Y1, KH_GROUND_Z, KH_SHAFT_Y2, KH_Z2)
    ]  # west stairwell gap — doorway size
    e_hall_openings = [
        (KH_SHAFT_Y1, KH_GROUND_Z, KH_SHAFT_Y2, KH_Z2)
    ]  # shaft gap always open

    for floor_index in range(KH_FLOORS):
        fz1 = KH_GROUND_Z + floor_index * KH_FLOOR_H
        fz_surf = fz1 + KH_WALL  # top of floor slab
        split = KH_ROOM_SPLITS[floor_index]
        sr_yc = (KH_BIY1 + split) // 2  # south room Y center
        nr_yc = (split + KH_WALL + KH_BIY2) // 2  # north room Y center
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
            KH_BIY1,
            KH_ENT_X1 - KH_WALL,
            KH_GROUND_Z,
            KH_BIY2,
            KH_ENT_X1,
            KH_Z2,
            w_hall_openings,
            Textures.WALL,
        )
    )
    # East hallway wall with room door openings + shaft opening
    BRUSHES.extend(
        layered_wall_y(
            KH_BIY1,
            KH_ENT_X2,
            KH_GROUND_Z,
            KH_BIY2,
            KH_ENT_X2 + KH_WALL,
            KH_Z2,
            e_hall_openings,
            Textures.WALL,
        )
    )

    # Partition walls per floor (divide each side into 2 rooms, with connecting door)
    for fl in range(KH_FLOORS):
        fz1 = KH_GROUND_Z + fl * KH_FLOOR_H
        fz2 = fz1 + KH_FLOOR_H
        fz_surf = fz1 + KH_WALL
        split = KH_ROOM_SPLITS[fl]
        sp_y2 = split + KH_WALL
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
                [(KH_WEST_ROOM_CX - 32, fz_surf, KH_WEST_ROOM_CX + 32, pdz2)],
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
                [(KH_EAST_ROOM_CX - 32, fz_surf, KH_EAST_ROOM_CX + 32, pdz2)],
                Textures.WALL,
            )
        )

    if not KH_ENABLED:
        del BRUSHES[kh_brush_start:]

    DRAW_KH_FASCIA_TEXT = True  # Set True to re-enable (slow to compile)

    # ── "LOYOLA UNIVERSITY MARYLAND" fascia lettering ────────────────────────────
    # Fascia panel follows the arch: one box per character hanging from deck_bot_z(x)
    KH_FASCIA_PX_W, KH_FASCIA_PX_H = 4, 4
    KH_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
    char_w = (4 + 1) * KH_FASCIA_PX_W  # 4 cols + 1 gap
    total_w = len(KH_FASCIA_TEXT) * char_w - KH_FASCIA_PX_W
    text_x0 = 0 - total_w // 2

    # No separate background fascia boxes — parapet wall face is the backdrop

    KH_FASCIA_FONT = {
        "A": [0b0110, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
        "B": [0b1110, 0b1001, 0b1110, 0b1001, 0b1110, 0b0000],
        "C": [0b0111, 0b1000, 0b1000, 0b1000, 0b0111, 0b0000],
        "D": [0b1110, 0b1001, 0b1001, 0b1001, 0b1110, 0b0000],
        "E": [0b1111, 0b1000, 0b1110, 0b1000, 0b1111, 0b0000],
        "F": [0b1111, 0b1000, 0b1110, 0b1000, 0b1000, 0b0000],
        "G": [0b0111, 0b1000, 0b1011, 0b1001, 0b0111, 0b0000],
        "H": [0b1001, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
        "I": [0b1110, 0b0100, 0b0100, 0b0100, 0b1110, 0b0000],
        "J": [0b0011, 0b0001, 0b0001, 0b1001, 0b0110, 0b0000],
        "K": [0b1001, 0b1010, 0b1100, 0b1010, 0b1001, 0b0000],
        "L": [0b1000, 0b1000, 0b1000, 0b1000, 0b1111, 0b0000],
        "M": [0b1001, 0b1111, 0b1111, 0b1001, 0b1001, 0b0000],
        "N": [0b1001, 0b1101, 0b1011, 0b1001, 0b1001, 0b0000],
        "O": [0b0110, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
        "P": [0b1110, 0b1001, 0b1110, 0b1000, 0b1000, 0b0000],
        "R": [0b1110, 0b1001, 0b1110, 0b1010, 0b1001, 0b0000],
        "S": [0b0111, 0b1000, 0b0110, 0b0001, 0b1110, 0b0000],
        "T": [0b1111, 0b0100, 0b0100, 0b0100, 0b0100, 0b0000],
        "U": [0b1001, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
        "V": [0b1001, 0b1001, 0b1001, 0b0110, 0b0110, 0b0000],
        "W": [0b1001, 0b1001, 0b1111, 0b1111, 0b1001, 0b0000],
        "Y": [0b1001, 0b0110, 0b0100, 0b0100, 0b0100, 0b0000],
        " ": [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000],
    }

    def render_text_fascia(text, x0, y_face, px_w, px_h, depth, tex, mirror=False):
        """Render text as pixel-font raised boxes on a fascia face.
        Each character's Z is computed from deck_top_z(x) so letters follow the arch curve.
        mirror=True flips each glyph horizontally (needed for north-facing surface)."""
        cols = 4
        char_w = (cols + 1) * px_w  # 4 cols + 1 gap

        brushes = []
        for ci, ch in enumerate(text):
            bitmap = KH_FASCIA_FONT.get(ch, KH_FASCIA_FONT[" "])
            cx = x0 + ci * char_w
            x_mid = cx + (cols * px_w) / 2
            z_top = (
                int(deck_top_z(x_mid)) + BRIDGE_PAR_H - 14
            )  # centred in parapet height
            for row_i, row_bits in enumerate(bitmap):
                z = z_top - row_i * px_h
                for col_i in range(cols):
                    src_col = (cols - 1 - col_i) if mirror else col_i
                    if row_bits & (1 << (cols - 1 - src_col)):
                        px = cx + col_i * px_w
                        brushes.append(
                            box(px, y_face - depth, z - px_h, px + px_w, y_face, z, tex)
                        )
        return brushes

    def render_text_flat(
        text, x0, y_face, z_base, px_w, px_h, depth, tex, mirror=False
    ):
        """Render text as pixel-font raised boxes on a flat north-facing wall surface."""
        cols = 4
        rows = 6
        char_w_f = (cols + 1) * px_w
        brushes = []
        for ci, ch in enumerate(text):
            bitmap = KH_FASCIA_FONT.get(ch, KH_FASCIA_FONT[" "])
            cx = x0 + ci * char_w_f
            for row_i, row_bits in enumerate(bitmap):
                z = z_base + (rows - 1 - row_i) * px_h
                for col_i in range(cols):
                    src_col = (cols - 1 - col_i) if mirror else col_i
                    if row_bits & (1 << (cols - 1 - src_col)):
                        px = cx + col_i * px_w
                        brushes.append(
                            box(px, y_face, z, px + px_w, y_face + depth, z + px_h, tex)
                        )
        return brushes

    # Raised pixel-font letters on the Knott Hall sign plaque
    # Text reversed + mirrored so it reads correctly when viewed from north (facing south)
    BRUSHES.extend(
        render_text_flat(
            sign_text[::-1],
            x0=sign_center_x - sign_total_width // 2,
            y_face=KH_Y2 + 6,
            z_base=sign_z1 + 14,  # centered: (48-20)//2 = 14
            px_w=sign_pixel_width,
            px_h=sign_pixel_height,
            depth=2,
            tex=Textures.RAIL,
            mirror=True,
        )
    )

    letter_brushes = (
        (
            render_text_fascia(
                KH_FASCIA_TEXT,
                x0=text_x0,
                y_face=BRIDGE_Y1,
                px_w=KH_FASCIA_PX_W,
                px_h=KH_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
            )
            + render_text_fascia(
                KH_FASCIA_TEXT[::-1],
                x0=text_x0,
                y_face=BRIDGE_Y2 + 1,
                px_w=KH_FASCIA_PX_W,
                px_h=KH_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
                mirror=True,
            )
        )
        if DRAW_KH_FASCIA_TEXT
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
            BRUSHES.append(
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
            BRUSHES.append(
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
            BRUSHES.append(
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
        BRUSHES.extend(
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
                Textures.STONE,
                stilt_h=CHARLES_ARCH_STILT_PRE,
            )
        )
    if letter_brushes:
        ENTITIES.append(brush_ent("func_detail", letter_brushes))
    return BRUSHES, ENTITIES
