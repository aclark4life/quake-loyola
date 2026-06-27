"""
knott_terrain — hill terrain surrounding Knott Hall.

Geometry that physically grounds the Knott Hall building:
  • Solid hill fill that raises the building footprint to KNOTT_GROUND_Z
  • West hill ramp connecting Charles Street sidewalk up to building level
  • North-face sloped terrain between the KH entrance and Ennis sidewalk
  • East-side cement entrance platform + descending steps
  • Small cement connector to the back-road west sidewalk

Kept separate from bridge.py (bridge/walkway structure) and
knott_hall.py (building walls, floors, interior) so each module has
a single clear responsibility.
"""

import math

from .constants import (
    BRIDGE,
    BRIDGE_PILLAR_OVERHANG,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_CURB_W,
    ENNIS_HW,
    ENNIS_SW_EDGE,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
    INDENT,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
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
    KNOTT_ENT_X1,
    KNOTT_ENT_X2,
    KNOTT_GROUND_Z,
    KNOTT_ORIG_CX,
    KNOTT_RAIL_H,
    KNOTT_RAIL_TEX,
    KNOTT_STAIR_CAP_RAISE,
    KNOTT_STAIR_CAP_W,
    KNOTT_STAIR_OFFSET,
    KNOTT_STAIR_RAIL_EXTENSION,
    KNOTT_STAIR_RAIL_POST_D,
    KNOTT_STAIR_RAIL_POST_W,
    KNOTT_STEP_DEPTH,
    KNOTT_STEP_N,
    ROAD_X2,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
)
from .geometry import (
    box,
    brush_ent,
    curb_seg,
    make_tree,
    ramp_slab,
    ramp_slab_y,
    tri_prism,
)


def build():
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
    _r_outer = KNOTT_DRIVEWAY_CURB_CRN_R
    _r_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
    _seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
    # MULCH fill — pie slices from centre to INNER radius only
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
                Textures.MULCH,
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

    # ── Island trees — one on each planted corner ─────────────────────────────
    # Trees centred on the island quarter-circle pivot points, offset slightly
    # into the mulch area so they clear the curb ring.
    _island_tree_offset = _r_inner // 2
    for tree_cx, tree_cy in [
        (
            KNOTT_DRIVEWAY_JCX_W + _island_tree_offset,
            KNOTT_DRIVEWAY_EXT_Y2 + _island_tree_offset,
        ),
        (
            KNOTT_DRIVEWAY_JCX_E - _island_tree_offset,
            KNOTT_DRIVEWAY_EXT_Y2 + _island_tree_offset,
        ),
    ]:
        DETAIL_BRUSHES.extend(make_tree(tree_cx, tree_cy, FLOOR_Z2 + CHARLES_WALK_H))

    # ── Hill terrain under Knott Hall ─────────────────────────────────────────────
    # Bridge deck is raised; building sits on a hill so its 2nd floor meets the walkway.
    if KNOTT_GROUND_Z > FLOOR_Z2:
        west_ramp_x1 = ROAD_X2 + CHARLES_WALK_W  # east edge of east sidewalk = 336
        west_ramp_x2 = KNOTT.x1  # ramp rises all the way to building west face
        # Solid hill fill under the entire building footprint — split to exclude indent pockets
        # so indents are recessed at all heights down to ground level
        for fill_x1, fill_y1, fill_x2, fill_y2 in [
            (
                KNOTT.x1 + INDENT,
                KNOTT.y1,
                KNOTT.x2 - INDENT,
                KNOTT.y1 + INDENT,
            ),  # south strip
            (KNOTT.x1, KNOTT.y1 + INDENT, KNOTT.x2, KNOTT.y2 - INDENT),  # middle strip
            (
                KNOTT.x1 + 2 * INDENT,
                KNOTT.y2 - INDENT,
                KNOTT.x2 - INDENT,
                KNOTT.y2,
            ),  # north strip
        ]:
            BRUSHES.append(
                box(
                    fill_x1,
                    fill_y1,
                    FLOOR_Z2,
                    fill_x2,
                    fill_y2,
                    KNOTT_GROUND_Z,
                    Textures.WALL,
                )
            )
        # NW indent floor — flush with exterior ground
        BRUSHES.append(
            box(
                KNOTT.x1,
                KNOTT.y2 - INDENT,
                FLOOR_Z1,
                KNOTT.x1 + 2 * INDENT,
                KNOTT.y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # (No flat east fill — the back road section provides its own sloped fill there)
        # West hill — ramp from sidewalk height at Charles St up to building ground level
        west_ramp_north_y = KNOTT.y2 - INDENT * 3 // 4
        BRUSHES.append(
            ramp_slab(
                west_ramp_x1,
                west_ramp_x2,
                WORLD_Y1 + WALL_T,
                west_ramp_north_y,
                FLOOR_Z1,
                FLOOR_Z1,
                FLOOR_Z2 + CHARLES_WALK_H,
                KNOTT_GROUND_Z,
                Textures.GROUND,
            )
        )
        # Flat ground from ramp north edge to building face (west of KNOTT.x1)
        BRUSHES.append(
            box(
                west_ramp_x1,
                west_ramp_north_y,
                FLOOR_Z1,
                west_ramp_x2,
                KNOTT.y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # South terrain fill — flat ground at building level behind south wall to east world edge
        BRUSHES.append(
            box(
                KNOTT.x1,
                WORLD_Y1 + WALL_T,
                FLOOR_Z1,
                WORLD_X2_EXT - WALL_T,
                KNOTT.y1,
                KNOTT_GROUND_Z,
                Textures.WALL,
            )
        )
        # Flat ground in front of KH (north face to Ennis sidewalk edge), flush with sidewalk
        # Split around KH entrance strip (KNOTT_ENT_X1..KNOTT_ENT_X2) to let cement apron show.
        # Between Pier 4 (PIER4_X) and Pier 5 (PIER5_X): gradual slope from KNOTT_GROUND_Z
        # at the north KH face (KNOTT.y2) down to sidewalk height at the Ennis sidewalk (ENNIS_SW_EDGE).
        knott_entry_x1 = KNOTT_ORIG_CX - 64
        knott_entry_x2 = KNOTT_ORIG_CX + 64
        east_ramp_x1 = knott_entry_x2  # east of entrance opening
        east_ramp_x2 = KNOTT.x2 - INDENT  # west edge of NE indent
        east_platform_depth = (
            96  # N-S depth of side-step platform — slope must not cover this
        )
        # West section of seg1 — stays at sidewalk height (up to NW indent of KH)
        segment1_split_x = (
            KNOTT.x1 + 2 * INDENT
        )  # = NW indent X, aligns raised ground with NW corner
        BRUSHES.append(
            box(
                west_ramp_x1,
                KNOTT.y2,
                FLOOR_Z1,
                segment1_split_x,
                ENNIS_SW_EDGE,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # East section of seg1 (NW indent → entrance) — slopes from KNOTT_GROUND_Z at KH face to
        # sidewalk height at Ennis sidewalk
        BRUSHES.append(
            ramp_slab_y(
                segment1_split_x,
                knott_entry_x1,
                KNOTT.y2,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                FLOOR_Z1,
                KNOTT_GROUND_Z,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # Seg2 (east of entrance to NE indent)
        # east_walk_ext_y1_val / east_walk_ext_y2_val bracket the E-W ramp (Y=264..328)
        east_walk_ext_y1_val = BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG + 96 + 80 - 64  # 264
        east_walk_ext_y2_val = BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG + 96 + 80  # 328

        # Terrain Z at the ramp Y-midpoint — this is the west-end height of the ramp
        def terrain_z_at(y):
            return int(
                KNOTT_GROUND_Z
                + (FLOOR_Z2 + CHARLES_WALK_H - KNOTT_GROUND_Z)
                * (y - (KNOTT.y2 + 96))
                / (ENNIS_SW_EDGE - (KNOTT.y2 + 96))
            )

        extension_terrain_z_west = (
            terrain_z_at(east_walk_ext_y1_val) + terrain_z_at(east_walk_ext_y2_val)
        ) // 2
        # Full sloped terrain Y=-160..264 (path zone starts at ramp south edge)
        BRUSHES.append(
            ramp_slab_y(
                knott_entry_x2,
                east_ramp_x2,
                KNOTT.y2 + east_platform_depth,
                east_walk_ext_y1_val,
                FLOOR_Z1,
                FLOOR_Z1,
                KNOTT_GROUND_Z,
                terrain_z_at(east_walk_ext_y1_val),
                Textures.GROUND,
            )
        )
        # Accessible entrance ramp — rises gently from sidewalk level (Z=8) on the west
        # up to accessible-path level (Z=25) on the east.  Starts at the path's west edge
        # (X=knott_entry_x2) and extends 128 units east, clearing the entrance staircase zone.
        accessible_ramp_x1 = knott_entry_x2  # 1894 — west/low end
        accessible_ramp_x2 = knott_entry_x2 + 128  # 2022 — east/high end
        BRUSHES.append(
            ramp_slab(
                accessible_ramp_x1,
                accessible_ramp_x2,
                east_walk_ext_y1_val,
                east_walk_ext_y2_val,
                FLOOR_Z1,
                FLOOR_Z1,
                FLOOR_Z2 + CHARLES_WALK_H,
                extension_terrain_z_west,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )
        # Accessible path pad — flat cement at path level (Y=264..328, Z=extension_terrain_z_west),
        # spanning from the ramp's east end to the east ramp's high/west end (X=2152) so the
        # pad meets the east ramp flush without overshooting.
        east_walk_x2 = (
            2120 + 32
        )  # west edge of E-W back-road ramp (KNOTT_WALKWAY block)
        BRUSHES.append(
            box(
                accessible_ramp_x2,
                east_walk_ext_y1_val,
                FLOOR_Z1,
                east_walk_x2,
                east_walk_ext_y2_val,
                extension_terrain_z_west,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )
        # North section (Y=328..504): sloped mulch terrain
        BRUSHES.append(
            ramp_slab_y(
                knott_entry_x2,
                east_ramp_x2,
                east_walk_ext_y2_val,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                FLOOR_Z1,
                terrain_z_at(east_walk_ext_y2_val),
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.MULCH,
            )
        )
        # NE indent ground — south of ramp (Y=-160..264): full ground, no cement needed
        BRUSHES.append(
            box(
                east_ramp_x2,
                KNOTT.y2 + east_platform_depth,
                FLOOR_Z1,
                KNOTT_DRIVEWAY_CORRIDOR_X1,
                east_walk_ext_y1_val,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # North of E-W extension (Y=328..504): flat mulch pad matching the slope above
        BRUSHES.append(
            box(
                east_ramp_x2,
                east_walk_ext_y2_val,
                FLOOR_Z1,
                KNOTT_DRIVEWAY_CORRIDOR_X1,
                ENNIS_SW_EDGE,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.MULCH,
            )
        )
        # Seg3 (east of back-road corridor to east world wall) — beyond Pier 5; sealing ground
        # flush with the sidewalk. Extends to the full extended east boundary (WORLD_X2_EXT)
        # so the ground stays level all the way to the Ennis east dead-end.
        # Stops at ENNIS_SW_EDGE (south Ennis sidewalk outer edge) where curb/verge detail
        # begins, so it has no detail laid on top and can sit at sidewalk height without
        # z-fighting (the detail/verge to the north sits over the recessed knott_hall ground).
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_CORRIDOR_X2,
                KNOTT.y2,
                FLOOR_Z1,
                WORLD_X2_EXT - WALL_T,
                ENNIS_SW_EDGE,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # ── Entrance staircase (north face, centred on building) ─────────────────
        stair_base_z = FLOOR_Z2 + CHARLES_WALK_H
        platform_top_z = (
            KNOTT_GROUND_Z + KNOTT.wall_t
        )  # flush with interior floor (= 80)

        # Flat cement platform between building and stairs
        BRUSHES.append(
            box(
                KNOTT_ENT_X1,
                KNOTT.y2,
                FLOOR_Z2,
                KNOTT_ENT_X2,
                KNOTT.y2 + KNOTT_STAIR_OFFSET,
                platform_top_z,
                Textures.CEMENT,
            )
        )

        stair_y0 = KNOTT.y2 + KNOTT_STAIR_OFFSET  # south edge of staircase
        stair_y_end = stair_y0 + KNOTT_STEP_N * KNOTT_STEP_DEPTH  # north end
        for stair_index in range(KNOTT_STEP_N):
            step_top_z = (
                stair_base_z
                + (platform_top_z - stair_base_z) * (stair_index + 1) // KNOTT_STEP_N
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

        # Cement sidewalk from stair base to Ennis south sidewalk
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

        # Stair side caps (cement cheek walls)
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
                    platform_top_z + KNOTT_STAIR_CAP_RAISE,
                    stair_base_z + KNOTT_STAIR_CAP_RAISE,
                    Textures.CEMENT,
                )
            )

        # Stair railings
        for rail_x_base, is_west_side in [(KNOTT_ENT_X1, True), (KNOTT_ENT_X2, False)]:
            rail_top_z_at_platform = platform_top_z + KNOTT_RAIL_H - 28
            rail_top_z_at_apron = stair_base_z + KNOTT_RAIL_H - 28
            rail_x1 = (
                rail_x_base - KNOTT_STAIR_RAIL_POST_W if is_west_side else rail_x_base
            )
            rail_x2 = (
                rail_x_base if is_west_side else rail_x_base + KNOTT_STAIR_RAIL_POST_W
            )

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
                (stair_y0, platform_top_z),
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

        # East of entrance: flat platform flush with interior ground floor + steps going east
        east_platform_x1 = east_ramp_x1  # KNOTT_ENT_X2
        east_platform_x2 = KNOTT.x2
        east_step_count = 4
        east_step_rise = (
            platform_top_z - (FLOOR_Z2 + CHARLES_WALK_H)
        ) // east_step_count
        east_step_depth = 24
        east_steps_width = east_step_count * east_step_depth
        east_steps_x1 = (
            east_platform_x2 - east_steps_width
        )  # steps recessed, end flush with east wall
        # Flat platform at platform_top_z (west of steps) — flush with entrance plaza and interior floor
        BRUSHES.append(
            box(
                east_platform_x1,
                KNOTT.y2,
                FLOOR_Z1,
                east_steps_x1,
                KNOTT.y2 + east_platform_depth,
                platform_top_z,
                Textures.CEMENT,
            )
        )
        # Steps going east (downhill in X), flush with KH east wall
        for step_index in range(east_step_count):
            step_z = platform_top_z - (step_index + 1) * east_step_rise
            step_x1 = east_steps_x1 + step_index * east_step_depth
            step_x2 = step_x1 + east_step_depth
            BRUSHES.append(
                box(
                    step_x1,
                    KNOTT.y2,
                    FLOOR_Z1,
                    step_x2,
                    KNOTT.y2 + east_platform_depth,
                    step_z,
                    Textures.CEMENT,
                )
            )
        # Small cement connector — bridges step bottom to back road west sidewalk (32 units wide)
        BRUSHES.append(
            box(
                KNOTT.x2,
                KNOTT.y2,
                FLOOR_Z1,
                KNOTT.x2 + CHARLES_WALK_W,
                KNOTT.y2 + east_platform_depth,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
            )
        )

    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
