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

from .constants import (
    BRIDGE,
    BRIDGE_PIL_OVERHANG,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_SW_EDGE,
    FLOOR_Z1,
    FLOOR_Z2,
    INDENT,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    KNOTT_GROUND_Z,
    KNOTT_ORIG_CX,
    ROAD_X2,
    WALL_T,
    WORLD_X2,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
)
from .geometry import box, ramp_slab, ramp_slab_y


def build():
    BRUSHES = []
    ENTITIES = []

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
        east_walk_ext_y1_val = BRIDGE.y2 + BRIDGE_PIL_OVERHANG + 96 + 80 - 64  # 264
        east_walk_ext_y2_val = BRIDGE.y2 + BRIDGE_PIL_OVERHANG + 96 + 80  # 328

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
        # North section (Y=328..504): sloped terrain continues
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
                Textures.GROUND,
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
        # North of E-W extension (restore ground fully)
        BRUSHES.append(
            box(
                east_ramp_x2,
                east_walk_ext_y2_val,
                FLOOR_Z1,
                KNOTT_DRIVEWAY_CORRIDOR_X1,
                ENNIS_SW_EDGE,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
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
        # East of entrance: flat platform flush with interior ground floor + steps going east down to ground
        platform_top_z = (
            KNOTT_GROUND_Z + KNOTT.wall_t
        )  # flush with interior ground-floor surface (= 80)
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

    return BRUSHES, ENTITIES
