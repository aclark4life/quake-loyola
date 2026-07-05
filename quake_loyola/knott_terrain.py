"""
knott_terrain — hill terrain surrounding Knott Hall.

Geometry that physically grounds the Knott Hall building:
  • Back-road driveway east of Knott Hall (road/sidewalks/curbed junction
    corners connecting to Ennis Drive) — flat, not tied to hill height.
  • Hill fill/ramp/entrance-staircase model — REMOVED pending re-derivation
    against real-world topology (see docs/reference.rst, "Topology check").
    The old model assumed a single flat plateau at KNOTT_GROUND_Z; the real
    terrain climbs continuously toward Ennis Parallel. See the TODO near the
    bottom of build() for what needs to be rebuilt.

Kept separate from bridge.py (bridge/walkway structure) and
knott_hall.py (building walls, floors, interior) so each module has
a single clear responsibility.
"""

import math

from .constants import (
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_CURB_W,
    ENNIS_HW,
    ENNIS_SW_EDGE,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
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
    KNOTT_TERRAIN_ENABLED,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
)
from .geometry import box, brush_ent, curb_seg, ramp_slab_y, tri_prism


def build():
    if not KNOTT_TERRAIN_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []
    DETAIL_BRUSHES = []

    def road_section(brushes, x1, x2, top_z_s, top_z_n, surface_tex):
        # Thin surface overlay riding on top of the GROUND fill: its bottom sits
        # at the fill top (KNOTT_DRIVEWAY_ZT_*) so the visible sloped sides show
        # GROUND below and the surface texture only on the thin top layer.
        brushes.append(
            ramp_slab_y(
                x1,
                x2,
                KNOTT_DRIVEWAY_Y1,
                KNOTT_DRIVEWAY_Y2,
                KNOTT_DRIVEWAY_ZT_S,
                KNOTT_DRIVEWAY_ZT_N,
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
    # West sidewalk — cement from back road up to the E/W Ennis approach sidewalk
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_WS_X1,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_WS_X2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # West sidewalk — ground from E/W Ennis approach sidewalk to NW junction corner
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
    # Cement curb strip along road edge of the ground section
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
    # East sidewalk — cement from back road down to E/W Ennis approach sidewalk
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_ES_X2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # East sidewalk — mulch from E/W sidewalk to south junction corner
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
    # Cement curb strip on road-facing (west) edge of the mulch section
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
    # Terrain east of east sidewalk — raised flush with sidewalk height so the
    # decorative detail surfaces (cement walk / mulch / Ennis verge) laid on top
    # sit level with this ground instead of dropping CHARLES_WALK_H below it
    # (the Ennis verge decorative strip only extends to ENNIS_X2, leaving the
    # remainder of this ground exposed at sidewalk edge — it must match).
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
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
    _r_outer = KNOTT_DRIVEWAY_CURB_CRN_R
    _r_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
    _seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
    # GROUND fill — pie slices from centre to INNER radius only
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
    # CEMENT curb ring — inner to outer radius, wedge segments with tangent-plane faces
    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        a0 = corner_index * _seg_deg
        a1 = (corner_index + 1) * _seg_deg
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

    # East junction corner: center at SE corner of east sidewalk, arc sweeps 90°→180°
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
    _er_outer = KNOTT_DRIVEWAY_CURB_CRN_R
    _er_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
    _e_seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        ea0 = 90 + corner_index * _e_seg_deg
        ea1 = 90 + (corner_index + 1) * _e_seg_deg
        t0, t1 = math.radians(ea0), math.radians(ea1)
        # MULCH fill — pie slices from centre to inner radius
        BRUSHES.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_E,
                KNOTT_DRIVEWAY_EXT_Y2,
                KNOTT_DRIVEWAY_JCX_E + _er_inner * math.cos(t0),
                KNOTT_DRIVEWAY_EXT_Y2 + _er_inner * math.sin(t0),
                KNOTT_DRIVEWAY_JCX_E + _er_inner * math.cos(t1),
                KNOTT_DRIVEWAY_EXT_Y2 + _er_inner * math.sin(t1),
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.MULCH,
            )
        )
        # CEMENT curb ring — inner to outer radius
        BRUSHES.append(
            curb_seg(
                KNOTT_DRIVEWAY_JCX_E,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                _er_inner,
                _er_outer,
                ea0,
                ea1,
                Textures.CEMENT,
            )
        )

    # ── Hill terrain under Knott Hall — REMOVED, pending re-derivation ──────────
    # The previous hill-fill/ramp/entrance-staircase model assumed a single flat
    # plateau at KNOTT_GROUND_Z. The 2024 topology check (docs/reference.rst,
    # "Topology check" section) shows the real east side climbs continuously from
    # Knott Hall (~+7.2 ft) to Ennis Parallel (~+21.7 ft, ~360 ft further east) —
    # not a flat shelf. This section needs to be rebuilt against a sloped
    # elevation model before KNOTT_TERRAIN_ENABLED can be turned back on.
    #
    # TODO: rebuild hill fill + west ramp + north-face slope + entrance
    # staircase/platform using real elevation-derived Z values instead of a
    # single flat KNOTT_GROUND_Z constant.

    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
