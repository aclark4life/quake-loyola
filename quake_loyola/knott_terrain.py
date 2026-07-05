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
    CHARLES_RAMP_W,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_CURB_W,
    ENNIS_HW,
    ENNIS_SW_EDGE,
    ENNIS_X2,
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
    KNOTT_GROUND_Z,
    KNOTT_TERRAIN_ENABLED,
    ROAD_X2,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
)
from .geometry import (
    box,
    brush_ent,
    corner_ramp,
    curb_seg,
    ramp_slab,
    ramp_slab_y,
    tri_prism,
)


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

    # ── West ramp — blend the hill terrain back down to Charles St grade ───────
    # KNOTT_GROUND_Z (re-derived from real elevation data) sits well above the
    # Charles St sidewalk verge (streets.py, flush at FLOOR_Z2+CHARLES_WALK_H),
    # and nothing currently fills the gap between the verge's east edge and
    # KNOTT.x1 — without this, that gap is a sheer, unwalkable cliff.
    #
    # Two pieces close it:
    #  1. A flat-cross-section ramp for the south extension's Y range (where the
    #     hill sits at a constant KNOTT_GROUND_Z), sloping X from the verge edge
    #     up to KNOTT.x1.
    #  2. A tetrahedral corner ramp for the back-road's Y range, where the hill
    #     height itself already tapers from KNOTT_GROUND_Z (south) down to
    #     FLOOR_Z2 (north, at Ennis) — the wedge's apex sits at the hill's tall
    #     south corner and falls to grade on both the west (Charles) and north
    #     (Ennis) edges simultaneously, matching that taper instead of leaving a
    #     second cliff where a flat ramp would meet the sloped driveway.
    _charles_verge_x2 = ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W
    BRUSHES.append(
        ramp_slab(
            _charles_verge_x2,
            KNOTT.x1,
            WORLD_Y1 + WALL_T,
            KNOTT_DRIVEWAY_Y1,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2,
            KNOTT_GROUND_Z,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    BRUSHES.append(
        corner_ramp(
            KNOTT.x1,
            KNOTT_DRIVEWAY_Y1,
            _charles_verge_x2,
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z2,
            KNOTT_GROUND_Z,
            Textures.GROUND,
        )
    )

    # ── Terrain west of west sidewalk — mirrors "Terrain east of east sidewalk" ──
    # Fills the building-footprint strip between Knott Hall's west edge and the
    # driveway's west sidewalk (previously empty/flat at world-floor grade,
    # leaving a cliff right where the west corner ramp above tops out). Slopes
    # with the sidewalk, same as the east-side main section.
    BRUSHES.append(
        ramp_slab_y(
            KNOTT.x1,
            KNOTT_DRIVEWAY_WS_X1,
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
    # Terrain east of east sidewalk — climbs from sidewalk-flush height toward
    # Ennis Parallel, matching the re-measured eastward rise (scripts/
    # sample_elevation.py, docs/elevation_samples.csv "knott_climb_2".."_4":
    # +17.3 ft -> +19.3 ft, a ~29-unit rise) instead of a single flat plateau.
    # Past ENNIS_X2 (Ennis Parallel) is unmodeled real estate pending further
    # re-derivation (docs/reference.rst "Topology check"), so it stays flat at
    # the top of the ramp rather than extrapolating the slope further east.
    _EAST_TERRAIN_RISE = 29  # units; ft_to_units(19.25 - 17.32)
    BRUSHES.append(
        ramp_slab(
            KNOTT_DRIVEWAY_ES_X2,
            ENNIS_X2,
            KNOTT_DRIVEWAY_EXT_Y1,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2 + CHARLES_WALK_H + _EAST_TERRAIN_RISE,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    BRUSHES.append(
        box(
            ENNIS_X2,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H + _EAST_TERRAIN_RISE,
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
