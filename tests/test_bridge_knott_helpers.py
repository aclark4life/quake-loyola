"""Focused unit tests for the knott_hall.py/bridge.py sub-builder helpers
extracted from their previously-oversized build() functions. These
complement the broader map-level regression coverage in
test_regression.py/test_build_toggles.py by exercising individual helpers
directly, with assertions on brush counts, bounding boxes, and basic
geometric invariants (rather than only the merged whole-map output).
"""

import unittest
from unittest import mock

from quake_loyola import bridge, knott_hall
from quake_loyola.constants import (
    BRIDGE_ARCH_X,
    BRIDGE_SUPPORT_BEAM_H,
    CHARLES_WALK_H,
    ENNIS_CURB_W,
    ENNIS_SW_EDGE,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT,
    KNOTT_CORE_WALL_JOINT_D,
    KNOTT_CORE_WALL_JOINT_LEN,
    KNOTT_CORE_WALL_JOINT_W,
    KNOTT_DOOR_WALK_CAP_PROUD,
    KNOTT_DOOR_WALK_CAP_W,
    KNOTT_DOOR_WALK_PATH_PROUD,
    KNOTT_DOOR_WALK_PATH_TAIL,
    KNOTT_DOOR_WALK_RAIL_END,
    KNOTT_DOOR_WALK_RAIL_H,
    KNOTT_DOOR_WALK_RAIL_OVH,
    KNOTT_DOOR_WALK_RAIL_T,
    KNOTT_DOOR_WALK_RISE,
    KNOTT_DOOR_WALK_STEPS,
    KNOTT_DOOR_WALK_TREAD,
    KNOTT_DRIVEWAY_WS_X1,
    KNOTT_DRIVEWAY_WS_X2,
    KNOTT_EAST_WALK_RAIL_END,
    KNOTT_EAST_WALK_RAIL_H,
    KNOTT_EAST_WALK_RAIL_OVH,
    KNOTT_EAST_WALK_RAIL_T,
    KNOTT_EAST_WALK_RISERS,
    KNOTT_EAST_WALK_TREAD,
    KNOTT_EAST_WALK_W,
    KNOTT_ENT_WALK_ZT1,
    KNOTT_LIFT_CAR_GAP,
    KNOTT_LIFT_CAR_H,
    KNOTT_LIFT_CAR_T,
    KNOTT_LIFT_CAR_W,
    KNOTT_RAMP_PILLAR_GAP,
    KNOTT_RAMP_RAIL_CORNER_RUN,
    KNOTT_RAMP_RAIL_H,
    KNOTT_RAMP_RAIL_LOOP_H,
    KNOTT_RAMP_RAIL_OVH,
    KNOTT_RAMP_RAIL_POSTS,
    KNOTT_RAMP_RAIL_T,
    KNOTT_RAMP_SOUTH_SHIFT,
    KNOTT_RAMP_W,
    STREET_SURFACE_T,
    STREET_SW_GAP,
    STREET_SW_SLAB_LEN,
)
from quake_loyola.constants.bridge import BRIDGE_CENTER_SPAN_OFFSET
from quake_loyola.constants.textures import Textures
from quake_loyola.terrain import knott_hall as knott_terrain


class KnottHallWallsTest(unittest.TestCase):
    def setUp(self):
        self.z1 = knott_hall.KH_GROUND_Z
        self.z2 = self.z1 + knott_hall.BUILDING_H

    def test_build_walls_returns_brushes_and_two_detail_lists(self):
        wall_brushes, west_detail, east_detail = knott_hall._build_walls(
            self.z1, self.z2
        )
        self.assertTrue(wall_brushes)
        self.assertTrue(west_detail)
        self.assertTrue(east_detail)

    def test_build_walls_brushes_stay_within_footprint(self):
        wall_brushes, west_detail, east_detail = knott_hall._build_walls(
            self.z1, self.z2
        )
        # Mullions/beams intentionally protrude past the wall face
        # (MULLION_PROUD/BEAM_PROUD) so they render distinctly instead of
        # z-fighting with the coplanar window-fill brush — allow for that.
        margin = max(knott_hall.MULLION_PROUD, knott_hall.BEAM_PROUD)
        for brush in [*wall_brushes, *west_detail, *east_detail]:
            (x1, y1, z1), (x2, y2, z2) = brush.get_bbox()
            self.assertGreaterEqual(x1, knott_hall.KH_X1 - margin - 1e-3)
            self.assertLessEqual(x2, knott_hall.KH_X2 + margin + 1e-3)
            self.assertGreaterEqual(y1, knott_hall.KH_Y1 - margin - 1e-3)
            self.assertLessEqual(y2, knott_hall.KH_Y2 + margin + 1e-3)
            self.assertGreaterEqual(z1, self.z1 - 1e-3)
            self.assertLessEqual(z2, self.z2 + 1e-3)


class KnottHallRoofTest(unittest.TestCase):
    def test_build_roof_returns_four_spans(self):
        z2 = knott_hall.KH_GROUND_Z + knott_hall.BUILDING_H
        roof_z1, roof_z2 = z2, z2 + knott_hall.ROOF_T
        roof_brushes = knott_hall._build_roof(roof_z1, roof_z2)
        self.assertEqual(len(roof_brushes), 4)
        for brush in roof_brushes:
            (_, _, bz1), (_, _, bz2) = brush.get_bbox()
            self.assertAlmostEqual(bz1, roof_z1)
            self.assertAlmostEqual(bz2, roof_z2)


class KnottHallParapetTest(unittest.TestCase):
    def test_build_parapet_returns_eight_segments_above_roofline(self):
        z2 = knott_hall.KH_GROUND_Z + knott_hall.BUILDING_H
        parapet_z2 = z2 + knott_hall.PARAPET_H
        parapet_brushes = knott_hall._build_parapet(z2, parapet_z2)
        self.assertEqual(len(parapet_brushes), 8)
        for brush in parapet_brushes:
            (_, _, bz1), (_, _, bz2) = brush.get_bbox()
            self.assertAlmostEqual(bz1, z2)
            self.assertAlmostEqual(bz2, parapet_z2)


class KnottHallSignTest(unittest.TestCase):
    def test_build_sign_returns_nonempty_brushes_on_north_wall(self):
        sign_brushes = knott_hall._build_sign(knott_hall.KH_GROUND_Z)
        self.assertTrue(sign_brushes)
        for brush in sign_brushes:
            (_, y1, _), (_, y2, _) = brush.get_bbox()
            # The sign hangs off the north (knott_hall.KH_Y2) wall.
            self.assertGreaterEqual(y1, knott_hall.KH_Y2 - 1e-3)
            self.assertGreaterEqual(y2, knott_hall.KH_Y2 - 1e-3)


class KnottHallFloorTest(unittest.TestCase):
    def test_each_storey_is_decked_over_the_whole_interior(self):
        spans = knott_hall._interior_spans()
        floors = knott_hall._build_floors()
        ground = [b for b in floors if b.get_bbox()[1][2] == knott_hall.GROUND_FLOOR_Z]
        entry = [b for b in floors if b.get_bbox()[1][2] == knott_hall.ENTRY_FLOOR_Z]
        upper = [
            b
            for z in knott_hall.UPPER_FLOOR_ZS
            for b in floors
            if b.get_bbox()[1][2] == z
        ]
        # The lowest deck is uncut, so one plate per span.
        self.assertEqual(len(ground), len(spans))
        # Every deck above it is split around the two shafts, so each takes
        # more plates than a span alone would.
        self.assertGreater(len(entry), len(spans))
        for z in knott_hall.UPPER_FLOOR_ZS:
            self.assertGreater(
                len([b for b in floors if b.get_bbox()[1][2] == z]), len(spans)
            )
        # All five storeys (ground, entry, and the three above) account for
        # every deck plate built.
        self.assertEqual(len(knott_hall.UPPER_FLOOR_ZS), 3)
        self.assertEqual(len(floors), len(ground) + len(entry) + len(upper))

    def test_the_ground_deck_is_flush_with_the_north_door_threshold(self):
        # The door opens onto a walk that leaves the doorway at grade, so a
        # deck any higher or lower would put a lip in the doorway.
        self.assertEqual(knott_hall.GROUND_FLOOR_Z, knott_hall.GROUND_DOOR_BOTTOM)

    def test_the_ground_deck_is_poured_onto_the_world_floor_slab(self):
        # It must land on the slab streets/shell.py lays at FLOOR_Z1..FLOOR_Z2
        # rather than float above it, or the gap is a sealed dead crawlspace.
        decks = [
            b
            for b in knott_hall._build_floors()
            if b.get_bbox()[1][2] == knott_hall.GROUND_FLOOR_Z
        ]
        self.assertTrue(decks)
        for brush in decks:
            (_, _, z1), (_, _, _z2) = brush.get_bbox()
            self.assertEqual(z1, knott_hall.FLOOR_Z2)

    def test_the_entry_deck_is_level_with_the_bridge_entrance(self):
        # The entrance sill is dropped to the bridge deck's height at Knott
        # so the crossing runs in level (see ENTRANCE_SILL_Z); the floor has
        # to meet it exactly or walking in puts a lip in the doorway.
        self.assertEqual(knott_hall.ENTRY_FLOOR_Z, knott_hall.ENTRANCE_SILL_Z)
        decks = [
            b
            for b in knott_hall._build_floors()
            if b.get_bbox()[1][2] == knott_hall.ENTRY_FLOOR_Z
        ]
        self.assertTrue(decks)
        for brush in decks:
            (_, _, z1), (_, _, z2) = brush.get_bbox()
            self.assertEqual(z2 - z1, knott_hall.FLOOR_T)

    def test_the_window_sills_sit_above_the_entry_deck(self):
        # The facade's opening grid starts a beam segment above the
        # entrance sill, so the glazing gets an upstand rather than the
        # floor cutting through it.
        self.assertGreater(knott_hall.OPENING_BOTTOM_Z, knott_hall.ENTRY_FLOOR_Z)

    def test_the_lowest_deck_is_left_solid_under_the_cores(self):
        # The shafts bottom out on it, so cutting it would open a pit down
        # onto the world ground slab rather than a shaft.
        ground = [
            b
            for b in knott_hall._build_floors()
            if b.get_bbox()[1][2] == knott_hall.GROUND_FLOOR_Z
        ]
        self.assertEqual(len(ground), len(knott_hall._interior_spans()))
        for vx1, vy1, vx2, vy2 in knott_hall._core_voids():
            cx, cy = (vx1 + vx2) / 2, (vy1 + vy2) / 2
            covered = any(
                b.get_bbox()[0][0] <= cx <= b.get_bbox()[1][0]
                and b.get_bbox()[0][1] <= cy <= b.get_bbox()[1][1]
                for b in ground
            )
            self.assertTrue(covered, "the lowest deck should be solid here")

    def test_the_cores_are_cut_out_of_the_upper_deck(self):
        entry = [
            b
            for b in knott_hall._build_floors()
            if b.get_bbox()[1][2] == knott_hall.ENTRY_FLOOR_Z
        ]
        for vx1, vy1, vx2, vy2 in knott_hall._core_voids():
            for brush in entry:
                (bx1, by1, _), (bx2, by2, _) = brush.get_bbox()
                overlaps = bx1 < vx2 and vx1 < bx2 and by1 < vy2 and vy1 < by2
                self.assertFalse(
                    overlaps, f"deck brush {(bx1, by1, bx2, by2)} blocks a shaft"
                )

    def test_the_upper_deck_loses_exactly_the_core_area(self):
        entry = [
            b
            for b in knott_hall._build_floors()
            if b.get_bbox()[1][2] == knott_hall.ENTRY_FLOOR_Z
        ]
        area = 0
        for brush in entry:
            (bx1, by1, _), (bx2, by2, _) = brush.get_bbox()
            area += (bx2 - bx1) * (by2 - by1)
        spans = sum(
            (x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in knott_hall._interior_spans()
        )
        # Clipped to the spans, not nominal: a core may abut a notch-ledge
        # wall, where the plate already stops short of the core's own edge.
        cores = 0
        for sx1, sy1, sx2, sy2 in knott_hall._interior_spans():
            for vx1, vy1, vx2, vy2 in knott_hall._core_voids():
                w = min(sx2, vx2) - max(sx1, vx1)
                d = min(sy2, vy2) - max(sy1, vy1)
                if w > 0 and d > 0:
                    cores += w * d
        self.assertEqual(area, spans - cores)
        self.assertGreater(cores, 0)

    def test_the_cores_flank_the_bridge_entrance(self):
        # As the retired prototype had them: stair to the west of the
        # entrance, lift to the east, so you arrive between the two.
        stair, lift = knott_hall._core_voids()
        self.assertLess(stair[2], knott_hall.ENTRANCE_X1)
        self.assertGreater(lift[0], knott_hall.ENTRANCE_X2)
        self.assertGreaterEqual(
            knott_hall.ENTRANCE_X1 - stair[2], knott_hall.CORE_LANDING_GAP
        )
        self.assertGreaterEqual(
            lift[0] - knott_hall.ENTRANCE_X2, knott_hall.CORE_LANDING_GAP
        )

    def test_the_lift_fills_the_north_east_corner(self):
        # The plan's true NE corner, in the notched north bay — not the
        # east wall of the main block. Flush to both faces, so no unusable
        # slot of floor is stranded beside it.
        _stair, lift = knott_hall._core_voids()
        self.assertEqual(lift[2], knott_hall.KH_NORTH_X2 - knott_hall.WALL_T)
        self.assertEqual(lift[3], knott_hall.KH_Y2 - knott_hall.WALL_T)
        self.assertEqual(lift[2] - lift[0], knott_hall.CORE_LIFT_W)
        self.assertEqual(lift[3] - lift[1], knott_hall.CORE_LIFT_D)

    def test_the_lift_takes_the_full_depth_of_the_notch(self):
        # The bay is shallow; leaving a strip of deck behind the shaft
        # would be unreachable floor.
        self.assertGreaterEqual(knott_hall.CORE_LIFT_D, knott_hall.NOTCH_D)

    def test_the_lift_opens_south_past_the_notch_line(self):
        # Stopping on the notch line would wall the lobby off from the
        # main floor with deck resuming flush against it. The lift now
        # matches the stair's own depth so both shafts' back walls align
        # on one south line (CORE_WALL_Y) instead of staggering.
        _stair, lift = knott_hall._core_voids()
        self.assertLess(lift[1], knott_hall.KH_NOTCH_Y)
        self.assertEqual(knott_hall.CORE_LIFT_D, knott_hall.CORE_STAIR_D)

    def test_the_stair_leaves_a_landing_inside_the_door(self):
        # Not a token gap: you should arrive on floor, not on the lip of
        # the stairwell.
        stair, _lift = knott_hall._core_voids()
        self.assertGreaterEqual(knott_hall.ENTRANCE_X1 - stair[2], 64)

    def test_the_cores_are_set_back_symmetrically_from_the_door(self):
        # The stair's clearance is taken from the lift's, so the two read
        # as a matched pair either side of the entrance.
        stair, lift = knott_hall._core_voids()
        self.assertEqual(
            knott_hall.ENTRANCE_X1 - stair[2], lift[0] - knott_hall.ENTRANCE_X2
        )

    def test_the_stair_fills_the_north_west_corner(self):
        # Mirror of the lift: the NW corner of the notched north bay,
        # flush to the front wall and to the bay's west face.
        stair, _lift = knott_hall._core_voids()
        self.assertEqual(stair[0], knott_hall.KH_NORTH_X1 + knott_hall.WALL_T)
        self.assertEqual(stair[3], knott_hall.KH_Y2 - knott_hall.WALL_T)
        self.assertEqual(stair[3] - stair[1], knott_hall.CORE_STAIR_D)

    def test_the_stair_runs_south_out_of_the_notch(self):
        # A switchback is deeper than the bay, so it cannot be contained
        # by it; the surplus has to come out of the main floor.
        stair, _lift = knott_hall._core_voids()
        self.assertGreater(knott_hall.CORE_STAIR_D, knott_hall.NOTCH_D)
        self.assertLess(stair[1], knott_hall.KH_NOTCH_Y)

    def test_the_cores_open_flush_with_the_front_wall(self):
        # The point of the placement: both read off the facade line, so
        # neither is a recess set back behind the notch.
        front = knott_hall.KH_Y2 - knott_hall.WALL_T
        for _vx1, _vy1, _vx2, vy2 in knott_hall._core_voids():
            self.assertEqual(vy2, front)

    def test_the_cores_stay_inside_the_notch_bay_in_x(self):
        # North of KH_NOTCH_Y only the bay exists; a core reaching wider
        # than it would open onto nothing.
        for vx1, _vy1, vx2, _vy2 in knott_hall._core_voids():
            self.assertGreaterEqual(vx1, knott_hall.KH_NORTH_X1 + knott_hall.WALL_T)
            self.assertLessEqual(vx2, knott_hall.KH_NORTH_X2 - knott_hall.WALL_T)

    def test_the_cores_stay_within_the_interior(self):
        for vx1, vy1, vx2, vy2 in knott_hall._core_voids():
            self.assertGreaterEqual(vx1, knott_hall.KH_X1 + knott_hall.WALL_T)
            self.assertLessEqual(vx2, knott_hall.KH_X2 - knott_hall.WALL_T)
            self.assertGreaterEqual(vy1, knott_hall.KH_Y1 + knott_hall.WALL_T)
            self.assertLess(vx1, vx2)
            self.assertLess(vy1, vy2)

    def test_the_two_cores_do_not_overlap(self):
        (sx1, sy1, sx2, sy2), (lx1, ly1, lx2, ly2) = knott_hall._core_voids()
        self.assertFalse(sx1 < lx2 and lx1 < sx2 and sy1 < ly2 and ly1 < sy2)

    def test_decks_stay_inside_the_shell(self):
        for brush in knott_hall._build_floors():
            (x1, y1, _), (x2, y2, _) = brush.get_bbox()
            self.assertGreaterEqual(x1, knott_hall.KH_X1 + knott_hall.WALL_T)
            self.assertLessEqual(x2, knott_hall.KH_X2 - knott_hall.WALL_T)
            self.assertGreaterEqual(y1, knott_hall.KH_Y1 + knott_hall.WALL_T)
            self.assertLessEqual(y2, knott_hall.KH_Y2 - knott_hall.WALL_T)

    def test_the_roof_covers_the_same_footprint_as_a_floor(self):
        # Both are built from _interior_spans(), which is the point of it:
        # a change to the notch can't move one without moving the other.
        # Compared against the uncut lowest deck, since the deck above is
        # split around the shafts.
        z2 = knott_hall.KH_GROUND_Z + knott_hall.BUILDING_H
        roof = knott_hall._build_roof(z2, z2 + knott_hall.ROOF_T)
        roof_xy = sorted(b.get_bbox()[0][:2] + b.get_bbox()[1][:2] for b in roof)
        floors = [
            b
            for b in knott_hall._build_floors()
            if b.get_bbox()[1][2] == knott_hall.GROUND_FLOOR_Z
        ]
        floor_xy = sorted(b.get_bbox()[0][:2] + b.get_bbox()[1][:2] for b in floors)
        self.assertEqual(roof_xy, floor_xy)


class KnottHallCoreWallTest(unittest.TestCase):
    def test_one_storey_worth_of_brushes_per_floor(self):
        # Three doored walls (center, stair, lift), each two jambs plus a
        # header (9 brushes), plus two solid backs closing the shafts'
        # own far ends (2 more), plus two solid side panels closing off
        # the shafts' remaining exterior-wall-facing sides (2 more) — 13
        # per storey, five storeys, none skipped.
        brushes = knott_hall._build_core_wall_slabs()
        self.assertEqual(len(brushes), 13 * len(knott_hall.FLOOR_ZS))

    def test_wall_uses_the_interior_partition_texture(self):
        for brush in knott_hall._build_core_wall_slabs():
            self.assertEqual(brush.faces[0].tex, Textures.WALL_KH_INTERIOR)

    def test_every_slab_is_scored_into_panels_parted_by_joints(self):
        # Each slab comes back as panels of the wall's full thickness with
        # grooves between them, held back from both faces so the joint
        # reads from either side of the wall.
        slabs = knott_hall._build_core_wall_slabs()
        scored = knott_hall._build_core_wall()
        self.assertGreater(len(scored), len(slabs))
        joints = [b for b in scored if b.faces[0].tex == Textures.SIDEWALK_JOINT_FILL]
        self.assertTrue(joints)
        for brush in joints:
            (x1, y1, _), (x2, y2, _) = brush.get_bbox()
            run, thick = sorted((x2 - x1, y2 - y1))
            self.assertEqual(run, KNOTT_CORE_WALL_JOINT_W)
            self.assertEqual(
                thick, knott_hall.CORE_WALL_T - 2 * KNOTT_CORE_WALL_JOINT_D
            )

    def test_every_corner_is_jointed_on_both_of_its_walls(self):
        # Where a partition dies into another the two are separate pours, so
        # the groove goes just clear of the wall being met -- on both walls,
        # since each meets the other.
        scored = knott_hall._build_core_wall()
        joints = {
            b.get_bbox()[0][:2]
            for b in scored
            if b.faces[0].tex == Textures.SIDEWALK_JOINT_FILL
        }
        half_t = knott_hall.CORE_WALL_T / 2
        # A joint brush is held back KNOTT_CORE_WALL_JOINT_D from both of its
        # wall's faces, so its own low corner sits that far in.
        # The lobby's southwest corner, scored on the center wall, just clear
        # of the stair wall it runs into...
        self.assertIn(
            (
                knott_hall.STAIR_WALL_X + half_t,
                knott_hall.CORE_WALL_Y - half_t + KNOTT_CORE_WALL_JOINT_D,
            ),
            joints,
        )
        # ...and on the stair wall itself, just clear of the center wall.
        self.assertIn(
            (
                knott_hall.STAIR_WALL_X - half_t + KNOTT_CORE_WALL_JOINT_D,
                knott_hall.CORE_WALL_Y + half_t,
            ),
            joints,
        )

    def test_panels_are_no_longer_than_a_single_pour(self):
        for brush in knott_hall._build_core_wall():
            if brush.faces[0].tex != Textures.WALL_KH_INTERIOR:
                continue
            (x1, y1, _), (x2, y2, _) = brush.get_bbox()
            self.assertLessEqual(
                max(x2 - x1, y2 - y1),
                KNOTT_CORE_WALL_JOINT_LEN + KNOTT_CORE_WALL_JOINT_W,
            )

    def test_double_door_opening_is_centered_on_the_bridge_entrance(self):
        # The route in from the bridge should run straight through the
        # opening rather than dogleg around it.
        self.assertEqual(
            (knott_hall.CORE_DOOR_X1 + knott_hall.CORE_DOOR_X2) / 2,
            knott_hall.ENTRANCE_CX,
        )

    def test_center_wall_fills_the_gap_between_the_stair_and_lift_shafts(self):
        # It has to land exactly on the shafts' facing edges, or it either
        # overlaps a shaft void or leaves a gap next to one.
        (stair_x1, _, stair_x2, _), (lift_x1, _, lift_x2, _) = knott_hall._core_voids()
        self.assertEqual(knott_hall.CORE_WALL_X1, stair_x2)
        self.assertEqual(knott_hall.CORE_WALL_X2, lift_x1)

    def test_center_wall_aligns_with_the_back_of_the_stair_shaft(self):
        # The whole notch bay should read as one consistent-depth lobby,
        # not have the center wall floating at an arbitrary depth partway
        # into it.
        self.assertEqual(knott_hall.CORE_WALL_Y, knott_hall.STAIR_WALL_Y1)
        self.assertLess(knott_hall.CORE_WALL_Y, knott_hall.KH_NOTCH_Y)

    def test_stair_and_lift_walls_run_perpendicular_to_the_center_wall(self):
        # The center wall's doorway is split along X (you walk through it
        # north-south); the stair and lift doors have to be split along Y
        # instead (you walk through them east-west) to actually be
        # perpendicular to it.
        self.assertEqual(knott_hall.STAIR_WALL_X, knott_hall.CORE_WALL_X1)
        self.assertEqual(knott_hall.LIFT_WALL_X, knott_hall.CORE_WALL_X2)
        self.assertLess(knott_hall.STAIR_DOOR_Y1, knott_hall.STAIR_DOOR_Y2)
        self.assertLess(knott_hall.LIFT_DOOR_Y1, knott_hall.LIFT_DOOR_Y2)

    def test_stair_and_lift_walls_meet_the_center_wall_at_its_own_depth(self):
        # Both run from the front wall back to CORE_WALL_Y, whatever their
        # own shaft's depth happens to be, so there's no gap between a
        # shallower shaft's own back and the center wall.
        (_, _, _, stair_y2), (_, _, _, lift_y2) = knott_hall._core_voids()
        self.assertEqual(knott_hall.STAIR_WALL_Y1, knott_hall.CORE_WALL_Y)
        self.assertEqual(knott_hall.STAIR_WALL_Y2, stair_y2)
        self.assertEqual(knott_hall.LIFT_WALL_Y1, knott_hall.CORE_WALL_Y)
        self.assertEqual(knott_hall.LIFT_WALL_Y2, lift_y2)

    def test_stair_and_lift_doors_sit_in_the_lobby_short_of_the_center_wall(self):
        # Reachable straight from the bridge entrance without first passing
        # through the center wall's double door.
        self.assertGreater(knott_hall.STAIR_DOOR_Y1, knott_hall.CORE_WALL_Y)
        self.assertLess(knott_hall.STAIR_DOOR_Y2, knott_hall.STAIR_WALL_Y2)
        self.assertGreater(knott_hall.LIFT_DOOR_Y1, knott_hall.CORE_WALL_Y)
        self.assertLess(knott_hall.LIFT_DOOR_Y2, knott_hall.LIFT_WALL_Y2)

    def test_shaft_backs_close_off_each_void_at_its_own_far_end(self):
        # Otherwise the shaft would read as open-ended into the main floor
        # beyond it instead of an enclosed shaft.
        (stair_x1, stair_y1, stair_x2, _), (lift_x1, lift_y1, lift_x2, _) = (
            knott_hall._core_voids()
        )
        self.assertEqual(knott_hall.STAIR_SHAFT_X1, stair_x1)
        self.assertEqual(knott_hall.STAIR_SHAFT_Y1, stair_y1)
        self.assertEqual(knott_hall.STAIR_SHAFT_X2, stair_x2)
        self.assertEqual(knott_hall.LIFT_SHAFT_X1, lift_x1)
        self.assertEqual(knott_hall.LIFT_SHAFT_Y1, lift_y1)
        self.assertEqual(knott_hall.LIFT_SHAFT_X2, lift_x2)

    def test_shaft_side_panels_close_off_the_exterior_wall_facing_side(self):
        # The back-wall panel only closes the shaft's far (south) end;
        # without this the shaft would still be open on its west (stair)
        # or east (lift) side, relying on the building's own exterior
        # wall face rather than having its own interior-textured panel.
        self.assertEqual(knott_hall.STAIR_SHAFT_WEST_X, knott_hall.STAIR_SHAFT_X1)
        self.assertEqual(knott_hall.LIFT_SHAFT_EAST_X, knott_hall.LIFT_SHAFT_X2)

    def test_no_brush_is_taller_than_its_own_storey(self):
        # A jamb or header that overshot its ceiling would poke into the
        # deck above it instead of stopping flush at its underside.
        storeys = zip(knott_hall.FLOOR_ZS, knott_hall.CORE_WALL_CEILINGS, strict=True)
        brushes = iter(knott_hall._build_core_wall_slabs())
        for floor_z, ceiling_z in storeys:
            for _ in range(13):
                (_, _, z1), (_, _, z2) = next(brushes).get_bbox()
                self.assertGreaterEqual(z1, floor_z)
                self.assertLessEqual(z2, ceiling_z)

    def test_door_openings_do_not_exceed_their_own_wall_span(self):
        self.assertGreater(knott_hall.CORE_DOOR_X1, knott_hall.CORE_WALL_X1)
        self.assertLess(knott_hall.CORE_DOOR_X2, knott_hall.CORE_WALL_X2)
        self.assertGreater(knott_hall.STAIR_DOOR_Y1, knott_hall.STAIR_WALL_Y1)
        self.assertLess(knott_hall.STAIR_DOOR_Y2, knott_hall.STAIR_WALL_Y2)
        self.assertGreater(knott_hall.LIFT_DOOR_Y1, knott_hall.LIFT_WALL_Y1)
        self.assertLess(knott_hall.LIFT_DOOR_Y2, knott_hall.LIFT_WALL_Y2)


class KnottHallBuildTest(unittest.TestCase):
    def test_build_matches_sum_of_helper_parts(self):
        brushes, entities = knott_hall.build()
        wall_brushes, west_detail, east_detail = knott_hall._build_walls(
            knott_hall.KH_GROUND_Z, knott_hall.KH_GROUND_Z + knott_hall.BUILDING_H
        )
        z2 = knott_hall.KH_GROUND_Z + knott_hall.BUILDING_H
        roof_brushes = knott_hall._build_roof(z2, z2 + knott_hall.ROOF_T)
        floor_brushes = knott_hall._build_floors()
        core_wall_brushes = knott_hall._build_core_wall()
        sign_brushes = knott_hall._build_sign(knott_hall.KH_GROUND_Z)
        parapet_brushes = knott_hall._build_parapet(z2, z2 + knott_hall.PARAPET_H)

        self.assertEqual(
            len(brushes),
            len(wall_brushes)
            + len(roof_brushes)
            + len(floor_brushes)
            + len(core_wall_brushes)
            + len(sign_brushes),
        )
        self.assertEqual(len(entities), 3)
        self.assertEqual(
            len(entities[0].brushes),
            len(west_detail)
            + len(east_detail)
            + len(parapet_brushes)
            + len(knott_hall._build_lift_sill()),
        )
        self.assertEqual(entities[1].classname, "func_door")
        self.assertEqual(entities[2].classname, "trigger_multiple")


class KnottLiftCarTest(unittest.TestCase):
    def setUp(self):
        self.car, self.call = knott_hall._build_lift_car()
        self.boxes = [b.get_bbox() for b in self.car.brushes]

    def test_car_rides_inside_the_lift_shaft(self):
        lift_x1, lift_y1, lift_x2, lift_y2 = knott_hall._LIFT_VOID
        for (x1, y1, _), (x2, y2, _) in self.boxes:
            self.assertGreaterEqual(x1, lift_x1)
            self.assertLessEqual(x2, lift_x2)
            self.assertGreaterEqual(y1, lift_y1)
            self.assertLessEqual(y2, lift_y2)

    def test_car_stands_a_sill_gap_off_the_shaft_wall_it_serves(self):
        # A real elevator has one; the player hull is far too wide to drop
        # down a gap this narrow.
        west = knott_hall.LIFT_WALL_X + knott_hall.CORE_WALL_T / 2
        self.assertEqual(min(b[0][0] for b in self.boxes), west + KNOTT_LIFT_CAR_GAP)
        self.assertLess(KNOTT_LIFT_CAR_GAP, 32)

    def test_car_door_lines_up_with_the_shaft_door(self):
        # The opening in the car's own lobby-facing wall has to be the one
        # the shaft door is, or the two never line up at a landing.
        west = min(b[0][0] for b in self.boxes)
        wall = [
            b
            for b in self.boxes
            if b[0][0] == west and b[1][0] == west + KNOTT_LIFT_CAR_T
        ]
        floor_top = min(b[0][2] for b in self.boxes) + KNOTT_LIFT_CAR_T
        jambs = sorted(b for b in wall if b[0][2] == floor_top)
        self.assertEqual(len(jambs), 2)
        self.assertEqual(jambs[0][1][1], knott_hall.LIFT_DOOR_Y1)
        self.assertEqual(jambs[1][0][1], knott_hall.LIFT_DOOR_Y2)
        header = [b for b in wall if b[0][2] == floor_top + knott_hall.LIFT_DOOR_H]
        self.assertEqual(len(header), 1)

    def test_car_is_a_box_with_a_floor_and_a_ceiling(self):
        z1 = min(b[0][2] for b in self.boxes)
        z2 = max(b[1][2] for b in self.boxes)
        self.assertEqual(z2 - z1, KNOTT_LIFT_CAR_H)
        decks = [
            b
            for b in self.boxes
            if b[1][0] - b[0][0] == KNOTT_LIFT_CAR_W
            and b[1][2] - b[0][2] == KNOTT_LIFT_CAR_T
        ]
        self.assertEqual(sorted(b[0][2] for b in decks), [z1, z2 - KNOTT_LIFT_CAR_T])

    def test_call_trigger_is_invisible(self):
        for brush in self.call.brushes:
            for face in brush.faces:
                self.assertEqual(face.tex, Textures.TRIGGER)

    def test_car_is_finished_like_the_building_own_decks(self):
        for brush in self.car.brushes:
            for face in brush.faces:
                self.assertEqual(face.tex, Textures.ROOF_KH)

    def test_car_floor_comes_out_level_with_the_ground_storey_deck(self):
        # You walk into the car, you don't step up into it -- so the floor
        # slab is sunk into the deck rather than laid on top of it. The deck
        # it disappears into is the one _build_floors leaves solid, and is
        # thicker than the slab, so no part of the car pokes out underneath.
        base_z = min(b[0][2] for b in self.boxes)
        self.assertEqual(base_z + KNOTT_LIFT_CAR_T, knott_hall.FLOOR_ZS[0])
        self.assertGreaterEqual(knott_hall.GROUND_FLOOR_T, KNOTT_LIFT_CAR_T)

    def test_car_is_called_from_inside_it_and_climbs_to_the_top(self):
        # A plat's own trigger is fitted to the top of its brush, which on a
        # car is the roof, well above anyone standing on the floor inside, and
        # a door's own field reaches out into the lobby -- so the car gets a
        # trigger of its own, filling the space a passenger stands in.
        self.assertEqual(self.car.classname, "func_door")
        self.assertEqual(self.call.classname, "trigger_multiple")
        self.assertEqual(self.call.fields["target"], self.car.fields["targetname"])
        (tx1, ty1, tz1), (tx2, ty2, tz2) = self.call.brushes[0].get_bbox()
        x1 = min(b[0][0] for b in self.boxes)
        z1 = min(b[0][2] for b in self.boxes)
        self.assertEqual((tx1, tz1), (x1 + KNOTT_LIFT_CAR_T, z1 + KNOTT_LIFT_CAR_T))
        self.assertEqual(tz2, z1 + KNOTT_LIFT_CAR_H - KNOTT_LIFT_CAR_T)
        self.assertGreater(tx2, tx1)
        self.assertGreater(ty2, ty1)
        self.assertEqual(self.car.fields["angle"], "-1")
        # A door travels its own height along the move direction less the lip.
        travel = KNOTT_LIFT_CAR_H - float(self.car.fields["lip"])
        floor_top = min(b[0][2] for b in self.boxes) + KNOTT_LIFT_CAR_T
        self.assertEqual(floor_top + travel, knott_hall.FLOOR_ZS[-1])

    def test_car_clears_the_top_storey_ceiling_when_raised(self):
        travel = KNOTT_LIFT_CAR_H - float(self.car.fields["lip"])
        top = max(b[1][2] for b in self.boxes) + travel
        self.assertLessEqual(top, knott_hall.CORE_WALL_CEILINGS[-1])

    def test_car_does_not_crush_whoever_is_riding_it(self):
        self.assertEqual(self.car.fields["dmg"], "0")


class BridgeRailingTubeBoundsTest(unittest.TestCase):
    def test_tube_bounds_are_ordered_and_symmetric_width(self):
        tube_ny1, tube_ny2, tube_sy1, tube_sy2 = bridge._bridge_railing_tube_y_bounds()
        self.assertLess(tube_ny1, tube_ny2)
        self.assertLess(tube_sy1, tube_sy2)
        self.assertAlmostEqual(tube_ny2 - tube_ny1, tube_sy2 - tube_sy1)
        self.assertAlmostEqual(tube_ny2 - tube_ny1, bridge.BRIDGE_TUBE_HW * 2)
        # North tube sits north of the south tube.
        self.assertGreater(tube_ny1, tube_sy2)


class BridgeSouthParapetEndcapTest(unittest.TestCase):
    def test_endcap_brush_sits_above_parapet_at_the_south_wall(self):
        span4_west_mid = bridge.BRIDGE.x2 + 500
        endcap = bridge._bridge_south_parapet_endcap_brush(span4_west_mid)
        (x1, y1, z1), (x2, y2, z2) = endcap.get_bbox()
        self.assertLess(x1, x2)
        self.assertLess(y1, y2)
        self.assertAlmostEqual(z1, bridge.BRIDGE_DZ2 + bridge.BRIDGE.parapet_h)
        self.assertAlmostEqual(
            z2, bridge.BRIDGE_DZ2 + bridge.BRIDGE.parapet_h + bridge.BRIDGE_BLK_H
        )


class BridgeFilterSectionsTest(unittest.TestCase):
    """Correctness checks for _filter_sections()'s per-section X windows.

    _shift_center_span() runs every brush through _filter_sections(), so a
    window that keeps the wrong geometry would silently move (or drop) part
    of the bridge. These tests assert *which* geometry each section's window
    keeps, by bounding box.
    """

    @classmethod
    def setUpClass(cls):
        cls.all_brushes, cls.all_entities = bridge._build_all()
        cls.section_names = list(bridge._section_x_ranges().keys())
        margin = (
            bridge.BRIDGE_PILLAR_HW
            + bridge.BRIDGE_PILLAR_OVERHANG
            + bridge.PIER6_ROTATION_MARGIN
        )
        cls.ranges = bridge._section_accept_ranges(margin)

    def test_extracted_section_brushes_stay_within_its_accept_window(self):
        for name in self.section_names:
            brushes, entities = bridge._filter_sections(
                self.all_brushes, self.all_entities, [name]
            )
            self.assertTrue(
                entities, f"expected at least one entity extracted for {name!r}"
            )
            ax1, ax2 = self.ranges[name]
            for ent in entities:
                for b in ent.brushes:
                    (bx1, _, _), (bx2, _, _) = b.get_bbox()
                    self.assertGreaterEqual(
                        bx1,
                        ax1 - 1e-3,
                        f"{name}: brush x1={bx1} below window start {ax1}",
                    )
                    self.assertLessEqual(
                        bx2,
                        ax2 + 1e-3,
                        f"{name}: brush x2={bx2} beyond window end {ax2}",
                    )


class BridgeShiftCenterSpanTest(unittest.TestCase):
    """_shift_center_span() must translate the assembly by exactly the
    configured offset — not merely change the brush/entity count."""

    def test_shift_translates_every_brush_by_the_exact_offset(self):
        all_brushes, all_entities = bridge._build_all()
        offset = (5.0, 320.0, 96.0)

        unshifted_b, unshifted_e = bridge._filter_sections(all_brushes, all_entities)
        shifted_b, shifted_e = bridge._shift_center_span(
            all_brushes, all_entities, offset
        )
        self.assertEqual(len(unshifted_e), len(shifted_e))
        self.assertEqual(len(unshifted_b), len(shifted_b))

        dx, dy, dz = offset
        checked_any = False
        for e0, e1 in zip(unshifted_e, shifted_e, strict=False):
            self.assertEqual(len(e0.brushes), len(e1.brushes))
            for b0, b1 in zip(e0.brushes, e1.brushes, strict=False):
                (x1, y1, z1), (x2, y2, z2) = b0.get_bbox()
                (X1, Y1, Z1), (X2, Y2, Z2) = b1.get_bbox()
                self.assertAlmostEqual(X1 - x1, dx, places=3)
                self.assertAlmostEqual(Y1 - y1, dy, places=3)
                self.assertAlmostEqual(Z1 - z1, dz, places=3)
                self.assertAlmostEqual(X2 - x2, dx, places=3)
                self.assertAlmostEqual(Y2 - y2, dy, places=3)
                self.assertAlmostEqual(Z2 - z2, dz, places=3)
                checked_any = True
        self.assertTrue(checked_any, "expected at least one brush to check")


class KnottWalkwayBentTest(unittest.TestCase):
    """The bent under the span in front of the Knott entrance."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_walkway_bent(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]

    def test_emits_a_beam_five_pillars_a_joint_each_and_a_tie_beam(self):
        # Beam split into 3 segments with 2 joint seams between them (5) +
        # 5 pillars, each with its own joint slab (10) + a joint where the
        # tie beam picks up from the last pillar (1) + tie beam (1) = 17.
        self.assertEqual(len(self.brushes), 17)

    def test_beam_sits_flush_under_the_span_deck(self):
        deck_underside = (
            KNOTT_ENT_WALK_ZT1 - KNOTT.wall_t + BRIDGE_CENTER_SPAN_OFFSET[2]
        )
        tops = [maxs[2] for _mins, maxs in self.boxes]
        self.assertEqual(max(tops), deck_underside)

    def test_bent_stays_within_the_span_it_carries(self):
        for mins, maxs in self.boxes:
            self.assertGreaterEqual(mins[0], BRIDGE_ARCH_X[3])
            self.assertLessEqual(maxs[0], BRIDGE_ARCH_X[4])

    def test_pillars_reach_the_hillside_below_their_own_joint_slab(self):
        beam_bottom = (
            KNOTT_ENT_WALK_ZT1
            - KNOTT.wall_t
            + BRIDGE_CENTER_SPAN_OFFSET[2]
            - BRIDGE_SUPPORT_BEAM_H
        )
        pillar_top = beam_bottom - knott_terrain.KNOTT_SUPPORT_PILLAR_JOINT_H
        pillars = [b for b in self.boxes if b[1][2] == pillar_top]
        self.assertEqual(len(pillars), 5)
        for mins, maxs in pillars:
            ground = knott_terrain._kh_hill_ground_z((mins[0] + maxs[0]) / 2, maxs[1])
            self.assertLessEqual(mins[2], ground)
            self.assertGreater(mins[2], 0)

    def test_each_pillar_gets_its_own_joint_seam_to_the_beam(self):
        # Same treatment as a sidewalk panel joint: a thin SIDEWALK_JOINT_FILL
        # slab between the pillar top and the beam's underside, so the two
        # read as separately poured elements.
        beam_bottom = (
            KNOTT_ENT_WALK_ZT1
            - KNOTT.wall_t
            + BRIDGE_CENTER_SPAN_OFFSET[2]
            - BRIDGE_SUPPORT_BEAM_H
        )
        joints = [
            b for b in self.brushes if b.faces[0].tex == Textures.SIDEWALK_JOINT_FILL
        ]
        pillar_joints = [j for j in joints if j.get_bbox()[1][2] == beam_bottom]
        self.assertEqual(len(pillar_joints), 5)
        for joint in pillar_joints:
            (_x1, _y1, z1), (_x2, _y2, z2) = joint.get_bbox()
            self.assertEqual(z2, beam_bottom)
            self.assertEqual(z2 - z1, knott_terrain.KNOTT_SUPPORT_PILLAR_JOINT_H)

    def test_beam_is_split_into_three_even_segments(self):
        # The beam is split into three even-length segments with a thin
        # joint groove between them, mirroring sidewalk panels butted end
        # to end, rather than being one long continuous pour.
        beam_top = KNOTT_ENT_WALK_ZT1 - KNOTT.wall_t + BRIDGE_CENTER_SPAN_OFFSET[2]
        joints = [
            b.get_bbox()
            for b in self.brushes
            if b.faces[0].tex == Textures.SIDEWALK_JOINT_FILL
            and b.get_bbox()[1][2] == beam_top
        ]
        self.assertEqual(len(joints), 2)
        for mins, maxs in joints:
            self.assertEqual(
                maxs[0] - mins[0], knott_terrain.KNOTT_SUPPORT_PILLAR_JOINT_H
            )
        cement_boxes = [
            b.get_bbox()
            for b in self.brushes
            if b.faces[0].tex == Textures.CEMENT and b.get_bbox()[1][2] == beam_top
        ]
        # Only the 3 beam segments run the full support_y1..support_y2
        # depth at beam_top; the tie beam sits further downhill and is
        # excluded by requiring the same y-span as the joints.
        joint_y_span = round(joints[0][0][1]), round(joints[0][1][1])
        segments = [
            box
            for box in cement_boxes
            if (round(box[0][1]), round(box[1][1])) == joint_y_span
        ]
        self.assertEqual(len(segments), 3)
        seg_lens = sorted(maxs[0] - mins[0] for mins, maxs in segments)
        # The two end segments lose only one joint's width; the middle
        # segment loses both, so allow up to a full joint width of slack.
        joint_w = knott_terrain.KNOTT_SUPPORT_PILLAR_JOINT_H
        self.assertAlmostEqual(seg_lens[0], seg_lens[1], delta=joint_w)
        self.assertAlmostEqual(seg_lens[1], seg_lens[2], delta=joint_w)

    def test_tie_beam_gets_a_joint_seam_from_the_last_pillar(self):
        # The ground-level tie beam picks up east of the last pillar; a
        # thin joint slab separates the two, same treatment as the beam
        # segment joints, rather than the tie beam butting straight into
        # the pillar.
        _y1, _y2, pier_xs, pier_half_w = knott_terrain._knott_walkway_bent_layout()
        last_pier_x2 = pier_xs[-1] + pier_half_w
        joints = [
            b.get_bbox()
            for b in self.brushes
            if b.faces[0].tex == Textures.SIDEWALK_JOINT_FILL
        ]
        tie_joints = [j for j in joints if round(j[0][0]) == round(last_pier_x2)]
        self.assertEqual(len(tie_joints), 1)
        mins, maxs = tie_joints[0]
        self.assertEqual(maxs[0] - mins[0], knott_terrain.KNOTT_SUPPORT_PILLAR_JOINT_H)


class KnottEntranceWalkTest(unittest.TestCase):
    """The walk, steps, and path outside the Knott ground-level north door."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_entrance_walk(self.brushes)
        self.paved = [b for b in self.brushes if b.faces[0].tex != Textures.CLIP]
        self.boxes = [b.get_bbox() for b in self.paved]
        self.flat_z = FLOOR_Z2 + CHARLES_WALK_H
        self.stair_y1, self.stair_y2, self.stair_z2 = (
            knott_terrain._knott_door_walk_layout()
        )

    def test_the_hillside_falls_away_from_the_building_face(self):
        # The crest used to stop at y = 0, 13 units north of Knott's wall, so
        # the fill's top stayed level with the walks over that strip and the
        # ground z-fought the cement the length of the facade. The crest now
        # ends at the wall and the slope starts there.
        self.assertEqual(knott_terrain.KH_CREST_Y, knott_hall.KH_Y2)
        for x in (2235, 2400, 2600):
            crest = knott_terrain._kh_hill_ground_z(x, knott_hall.KH_Y2)
            self.assertEqual(crest, knott_hall.GROUND_DOOR_BOTTOM)
            self.assertLess(
                knott_terrain._kh_hill_ground_z(x, knott_hall.KH_Y2 + 1), crest
            )

    def test_the_walk_never_runs_below_the_hillside(self):
        # Every paved brush the walk lays down must top out at or above the
        # modeled grade under it, or the ground pokes through the cement.
        for mins, maxs in self.boxes:
            cx = (mins[0] + maxs[0]) / 2
            for y in (mins[1], (mins[1] + maxs[1]) / 2, maxs[1]):
                self.assertGreaterEqual(
                    maxs[2] + 1e-6, knott_terrain._kh_hill_ground_z(cx, y)
                )

    def test_a_clip_wedge_rides_the_nosings_of_the_flight(self):
        clip = [b for b in self.brushes if b.faces[0].tex == Textures.CLIP]
        self.assertEqual(len(clip), 1)
        mins, maxs = clip[0].get_bbox()
        self.assertEqual((mins[1], maxs[1]), (self.stair_y1, self.stair_y2))
        self.assertEqual(maxs[2], knott_hall.GROUND_DOOR_BOTTOM)
        treads = [
            b.get_bbox()
            for b in self.paved
            if self.stair_y1 <= b.get_bbox()[0][1] < self.stair_y2
        ]
        rise = (knott_hall.GROUND_DOOR_BOTTOM - self.stair_z2) / (
            self.stair_y2 - self.stair_y1
        )
        for t_mins, t_maxs in treads:
            nosing = knott_hall.GROUND_DOOR_BOTTOM - rise * (t_mins[1] - self.stair_y1)
            self.assertGreaterEqual(nosing, t_maxs[2])

    def test_walk_is_inset_a_cheek_either_side_of_the_doorway(self):
        # The cheeks flanking the steps take up the rest of the doorway's
        # width, so walk and cheeks together span it.
        for mins, maxs in self.boxes:
            self.assertEqual(mins[0], knott_hall.GROUND_DOOR_X1 + KNOTT_DOOR_WALK_CAP_W)
            self.assertEqual(maxs[0], knott_hall.GROUND_DOOR_X2 - KNOTT_DOOR_WALK_CAP_W)

    def test_walk_leaves_the_doorway_at_grade(self):
        sill = knott_hall.GROUND_DOOR_BOTTOM
        outside = knott_terrain._kh_hill_ground_z(
            knott_hall.GROUND_DOOR_CX, knott_hall.KH_Y2
        )
        self.assertEqual(sill, outside)
        at_door = min(self.boxes, key=lambda b: b[0][1])
        self.assertEqual(at_door[0][1], knott_hall.KH_Y2)
        self.assertEqual(at_door[1][2], sill)

    def test_level_run_carries_the_door_height_to_the_steps(self):
        level = [b for b in self.boxes if b[1][2] == knott_hall.GROUND_DOOR_BOTTOM]
        self.assertEqual(min(b[0][1] for b in level), knott_hall.KH_Y2)
        self.assertEqual(max(b[1][1] for b in level), self.stair_y1)

    def test_there_is_a_single_flight_of_steps(self):
        run = KNOTT_DOOR_WALK_STEPS * KNOTT_DOOR_WALK_TREAD
        self.assertEqual(self.stair_y2 - self.stair_y1, run)
        tops = sorted(
            {
                maxs[2]
                for mins, maxs in self.boxes
                if self.stair_y1 <= mins[1] < self.stair_y2
            },
            reverse=True,
        )
        self.assertEqual(len(tops), KNOTT_DOOR_WALK_STEPS)
        for upper, lower in zip(tops, tops[1:], strict=False):
            self.assertEqual(upper - lower, KNOTT_DOOR_WALK_RISE)
        self.assertEqual(tops[-1], self.stair_z2)

    def test_steps_are_steeper_than_the_hillside_they_cross(self):
        hill_run = ENNIS_SW_EDGE - knott_hall.KH_Y2
        hill_fall = knott_hall.GROUND_DOOR_BOTTOM - self.flat_z
        self.assertGreater(
            KNOTT_DOOR_WALK_RISE / KNOTT_DOOR_WALK_TREAD, hill_fall / hill_run
        )

    def test_path_below_the_steps_lands_flush_on_the_ennis_walk(self):
        # The path starts a joint gap off the bottom step, which is scored
        # where the flight's pour meets the path's own.
        path = next(b for b in self.paved if b.get_bbox()[1][1] == ENNIS_SW_EDGE)
        mins, maxs = path.get_bbox()
        self.assertEqual(mins[1], self.stair_y2 + STREET_SW_GAP)
        self.assertEqual(maxs[2], self.stair_z2)
        ends = [
            v[2]
            for face in path.faces
            for v in (face.p1, face.p2, face.p3)
            if v[1] == ENNIS_SW_EDGE and v[2] > FLOOR_Z1
        ]
        self.assertEqual(max(ends), self.flat_z)

    def test_a_joint_is_scored_at_the_foot_of_the_flight(self):
        joint = next(
            b
            for b in self.brushes
            if b.faces[0].tex == Textures.SIDEWALK_JOINT
            and b.get_bbox()[0][1] == self.stair_y2
        )
        mins, maxs = joint.get_bbox()
        self.assertEqual(
            (mins[1], maxs[1]), (self.stair_y2, self.stair_y2 + STREET_SW_GAP)
        )
        self.assertEqual(maxs[2], self.stair_z2)
        self.assertEqual(
            (mins[0], maxs[0]),
            (
                knott_hall.GROUND_DOOR_X1 + KNOTT_DOOR_WALK_CAP_W,
                knott_hall.GROUND_DOOR_X2 - KNOTT_DOOR_WALK_CAP_W,
            ),
        )

    def test_path_ramps_the_hillside_ledge_away_at_the_bottom(self):
        # The tail starts a joint gap north of the Ennis walk edge: the street
        # module scores the seam there, and the tail would fill the groove.
        tail = max(self.paved, key=lambda b: b.get_bbox()[1][1])
        mins, maxs = tail.get_bbox()
        self.assertEqual(mins[1], ENNIS_SW_EDGE + STREET_SW_GAP)
        self.assertEqual(maxs[1], ENNIS_SW_EDGE + KNOTT_DOOR_WALK_PATH_TAIL)
        self.assertEqual(maxs[2], self.flat_z)
        ends = [
            v[2]
            for face in tail.faces
            for v in (face.p1, face.p2, face.p3)
            if v[1] == maxs[1] and v[2] > FLOOR_Z1
        ]
        self.assertEqual(max(ends), FLOOR_Z2)

    def test_nothing_is_buried_in_the_hillside(self):
        for mins, maxs in self.boxes:
            downhill = knott_terrain._kh_hill_ground_z((mins[0] + maxs[0]) / 2, maxs[1])
            self.assertGreaterEqual(maxs[2], downhill)

    def test_path_starts_at_ground_level(self):
        grade = knott_terrain._kh_hill_ground_z(
            knott_hall.GROUND_DOOR_CX, self.stair_y2
        )
        self.assertGreaterEqual(self.stair_z2 - grade, KNOTT_DOOR_WALK_PATH_PROUD)
        self.assertLess(
            self.stair_z2 - grade,
            KNOTT_DOOR_WALK_PATH_PROUD + KNOTT_DOOR_WALK_RISE,
        )

    def test_path_falls_faster_than_the_hillside_it_crosses(self):
        grade = knott_terrain._kh_hill_ground_z(
            knott_hall.GROUND_DOOR_CX, self.stair_y2
        )
        run = ENNIS_SW_EDGE - self.stair_y2
        self.assertGreater(
            (self.stair_z2 - self.flat_z) / run, (grade - self.flat_z) / run
        )

    def test_a_flight_too_long_to_fit_the_hillside_is_rejected(self):
        with mock.patch.object(knott_terrain, "KNOTT_DOOR_WALK_STEPS", 64):
            with self.assertRaises(ValueError):
                knott_terrain._knott_door_walk_layout()

    def test_a_flight_that_would_start_inside_the_building_is_rejected(self):
        with mock.patch.object(knott_terrain, "KNOTT_DOOR_WALK_TREAD", 512):
            with self.assertRaises(ValueError):
                knott_terrain._knott_door_walk_layout()

    def test_a_flight_that_would_land_past_ennis_is_rejected(self):
        with mock.patch.object(knott_terrain, "KNOTT_DOOR_WALK_RISE", 77):
            with mock.patch.object(knott_terrain, "KNOTT_DOOR_WALK_STEPS", 1):
                with self.assertRaises(ValueError):
                    knott_terrain._knott_door_walk_layout()


class KnottEntranceStepCapsTest(unittest.TestCase):
    """The cement cheeks flanking those steps."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_entrance_walk_step_caps(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.stair_y1, self.stair_y2, self.stair_z2 = (
            knott_terrain._knott_door_walk_layout()
        )

    def test_a_cheek_flanks_each_edge_of_the_steps(self):
        # They stick out past the walk, which is inset from the doorway by
        # exactly their width, so the three together span the doorway.
        west = [b for b in self.boxes if b[0][0] < knott_hall.GROUND_DOOR_CX]
        east = [b for b in self.boxes if b[0][0] > knott_hall.GROUND_DOOR_CX]
        self.assertEqual(len(west), len(east))
        self.assertEqual(len(west) + len(east), len(self.boxes))
        self.assertEqual(min(b[0][0] for b in west), knott_hall.GROUND_DOOR_X1)
        self.assertEqual(
            max(b[1][0] for b in west),
            knott_hall.GROUND_DOOR_X1 + KNOTT_DOOR_WALK_CAP_W,
        )
        self.assertEqual(
            min(b[0][0] for b in east),
            knott_hall.GROUND_DOOR_X2 - KNOTT_DOOR_WALK_CAP_W,
        )
        self.assertEqual(max(b[1][0] for b in east), knott_hall.GROUND_DOOR_X2)

    def test_a_joint_is_scored_where_each_cheek_meets_the_walk(self):
        joints = [
            b.get_bbox()
            for b in self.brushes
            if b.faces[0].tex == Textures.SIDEWALK_JOINT
        ]
        self.assertEqual(len(joints), 6)
        for mins, maxs in joints:
            self.assertEqual(maxs[0] - mins[0], STREET_SW_GAP)
        inner = sorted({round(b[0][0]) for b in joints})
        self.assertEqual(
            inner,
            sorted(
                {
                    round(knott_hall.GROUND_DOOR_X1 + KNOTT_DOOR_WALK_CAP_W)
                    - STREET_SW_GAP,
                    round(knott_hall.GROUND_DOOR_X2 - KNOTT_DOOR_WALK_CAP_W),
                }
            ),
        )

    def test_cheeks_run_level_past_each_end_of_the_flight(self):
        # Each level end carries a post of the rail above; outside the walk
        # there is nothing else under one.
        self.assertEqual(
            min(b[0][1] for b in self.boxes),
            self.stair_y1 - KNOTT_DOOR_WALK_RAIL_END,
        )
        self.assertEqual(
            max(b[1][1] for b in self.boxes),
            self.stair_y2 + KNOTT_DOOR_WALK_RAIL_END,
        )

    def test_the_cap_ends_level_with_the_walk_and_rakes_out_of_it(self):
        # The cap ends level with the walk carrying on above the flight,
        # then rakes shallower than the steps, so the cheek rises out of the
        # walk rather than reading as more of it.
        top = knott_hall.GROUND_DOOR_BOTTOM
        bot = self.stair_z2 + KNOTT_DOOR_WALK_CAP_PROUD
        west = [
            b for b in self.brushes if b.get_bbox()[0][0] == knott_hall.GROUND_DOOR_X1
        ]
        self.assertEqual(len(west), 3)
        above, rake, below = sorted(west, key=lambda b: b.get_bbox()[0][1])
        self.assertEqual(above.get_bbox()[1][2], top)
        self.assertEqual(below.get_bbox()[1][2], bot)
        self.assertEqual(rake.get_bbox()[0][1], self.stair_y1)
        self.assertEqual(rake.get_bbox()[1][1], self.stair_y2)
        ends = [
            v[2]
            for face in rake.faces
            for v in (face.p1, face.p2, face.p3)
            if v[1] == self.stair_y2 and v[2] > FLOOR_Z1
        ]
        self.assertEqual(rake.get_bbox()[1][2], top)
        self.assertEqual(max(ends), bot)

    def test_cheeks_are_poured_from_the_fill_not_off_the_treads(self):
        # The surface under them steps and then falls away downhill, so only
        # the cap is meant to show — a cheek standing on the treads would
        # leave the run's own steps showing through its side.
        for mins, _maxs in self.boxes:
            self.assertEqual(mins[2], FLOOR_Z1)


class KnottEntranceWalkRailsTest(unittest.TestCase):
    """The pipe rails flanking those steps."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_entrance_walk_rails(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.stair_y1, self.stair_y2, self.stair_z2 = (
            knott_terrain._knott_door_walk_layout()
        )

    def test_rails_run_centred_along_each_cheek(self):
        inset = (KNOTT_DOOR_WALK_CAP_W - KNOTT_DOOR_WALK_RAIL_T) / 2
        west = [b for b in self.boxes if b[0][0] == knott_hall.GROUND_DOOR_X1 + inset]
        east = [b for b in self.boxes if b[1][0] == knott_hall.GROUND_DOOR_X2 - inset]
        self.assertTrue(west)
        self.assertEqual(len(west), len(east))
        self.assertEqual(len(west) + len(east), len(self.boxes))

    def test_rails_are_a_thin_pipe_section(self):
        for mins, maxs in self.boxes:
            self.assertEqual(maxs[0] - mins[0], KNOTT_DOOR_WALK_RAIL_T)

    def test_rails_run_level_past_each_end_of_the_flight(self):
        self.assertEqual(
            min(b[0][1] for b in self.boxes),
            self.stair_y1 - KNOTT_DOOR_WALK_RAIL_END,
        )
        self.assertEqual(
            max(b[1][1] for b in self.boxes),
            self.stair_y2 + KNOTT_DOOR_WALK_RAIL_END,
        )

    def test_each_rail_stands_on_two_posts_and_no_more(self):
        inset = (KNOTT_DOOR_WALK_CAP_W - KNOTT_DOOR_WALK_RAIL_T) / 2
        west = [b for b in self.boxes if b[0][0] == knott_hall.GROUND_DOOR_X1 + inset]
        posts = [b for b in west if b[1][1] - b[0][1] == KNOTT_DOOR_WALK_RAIL_T]
        self.assertEqual(len(posts), 2)
        ends = sorted(p[0][1] for p in posts)
        self.assertEqual(
            ends[0],
            self.stair_y1 - KNOTT_DOOR_WALK_RAIL_END + KNOTT_DOOR_WALK_RAIL_OVH,
        )
        self.assertEqual(
            ends[1],
            self.stair_y2
            + KNOTT_DOOR_WALK_RAIL_END
            - KNOTT_DOOR_WALK_RAIL_OVH
            - KNOTT_DOOR_WALK_RAIL_T,
        )

    def test_the_posts_stand_within_the_cheek_below_them(self):
        caps = []
        knott_terrain._append_knott_entrance_walk_step_caps(caps)
        cap_boxes = [b.get_bbox() for b in caps]
        posts = [b for b in self.boxes if b[1][1] - b[0][1] == KNOTT_DOOR_WALK_RAIL_T]
        self.assertEqual(len(posts), 4)
        for mins, maxs in posts:
            self.assertTrue(
                any(
                    c[0][0] <= mins[0]
                    and c[1][0] >= maxs[0]
                    and c[0][1] <= mins[1]
                    and c[1][1] >= maxs[1]
                    and c[1][2] >= mins[2]
                    for c in cap_boxes
                )
            )

    def test_rail_tops_stay_a_handrail_above_the_treads(self):
        walk = []
        knott_terrain._append_knott_entrance_walk(walk)
        treads = [b.get_bbox() for b in walk]
        for mins, maxs in self.boxes:
            underfoot = [
                t[1][2] for t in treads if t[0][1] < maxs[1] and t[1][1] > mins[1]
            ]
            self.assertLessEqual(
                maxs[2],
                max(underfoot) + KNOTT_DOOR_WALK_RAIL_H + KNOTT_DOOR_WALK_RISE,
            )
            self.assertGreater(maxs[2], min(underfoot))


class KnottEastWalkTest(unittest.TestCase):
    """The walk hugging the Knott north face east to the driveway."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_east_walk(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.flat_z = FLOOR_Z2 + CHARLES_WALK_H
        self.stair_x1, self.stair_x2, self.rise = (
            knott_terrain._knott_east_walk_layout()
        )
        self.treads = sorted(b for b in self.boxes if b[0][0] >= self.stair_x1)

    def test_walk_hugs_the_north_face(self):
        for mins, maxs in self.boxes:
            self.assertEqual(mins[1], knott_hall.KH_Y2)
            self.assertEqual(maxs[1], knott_hall.KH_Y2 + KNOTT_EAST_WALK_W)

    def test_walk_leaves_the_north_door_walk_at_its_own_level(self):
        # It starts at the north door walk's east edge, which is inset a
        # cheek's width in from the doorway, so the two pours meet on a line.
        self.assertEqual(
            min(b[0][0] for b in self.boxes),
            knott_hall.GROUND_DOOR_X2 - KNOTT_DOOR_WALK_CAP_W,
        )
        level = [b for b in self.boxes if b[0][0] < self.stair_x1]
        self.assertTrue(level)
        for _mins, maxs in level:
            self.assertEqual(maxs[2], knott_hall.GROUND_DOOR_BOTTOM)

    def test_the_level_walk_runs_unbroken_to_the_head_of_the_steps(self):
        level = sorted(b for b in self.boxes if b[0][0] < self.stair_x1)
        self.assertEqual(level[-1][1][0], self.stair_x1)
        for west, east in zip(level, level[1:], strict=False):
            self.assertEqual(west[1][0], east[0][0])

    def test_flight_drops_in_even_risers(self):
        self.assertEqual(len(self.treads), KNOTT_EAST_WALK_RISERS - 1)
        tops = [maxs[2] for _mins, maxs in self.treads]
        self.assertEqual(tops[0], knott_hall.GROUND_DOOR_BOTTOM - self.rise)
        for above, below in zip(tops, tops[1:], strict=False):
            self.assertEqual(above - below, self.rise)

    def test_treads_are_a_consistent_depth(self):
        for mins, maxs in self.treads:
            self.assertEqual(maxs[0] - mins[0], KNOTT_EAST_WALK_TREAD)

    def test_last_riser_lands_on_the_driveway_walk(self):
        self.assertEqual(self.treads[-1][1][2] - self.rise, self.flat_z)
        self.assertEqual(self.treads[-1][1][0], self.stair_x2 - KNOTT_EAST_WALK_TREAD)
        self.assertGreater(self.stair_x2, KNOTT_DRIVEWAY_WS_X1)

    def test_flight_stops_short_of_the_driveway_curb(self):
        self.assertLessEqual(
            self.stair_x2 + KNOTT_EAST_WALK_RAIL_END,
            KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
        )

    def test_no_tread_cuts_below_the_bank(self):
        for mins, maxs in self.treads:
            self.assertGreaterEqual(
                maxs[2],
                knott_terrain._kh_hill_ground_z(mins[0], knott_hall.KH_Y2),
            )

    def test_flight_hugs_the_bank_rather_than_standing_off_it(self):
        # One tread further west and the top tread would be buried in the crest.
        west = self.stair_x1 - KNOTT_EAST_WALK_TREAD
        self.assertLess(
            knott_hall.GROUND_DOOR_BOTTOM - self.rise,
            knott_terrain._kh_hill_ground_z(west, knott_hall.KH_Y2),
        )

    def test_layout_rejects_a_riser_count_that_does_not_divide_the_drop(self):
        with mock.patch.object(knott_terrain, "KNOTT_EAST_WALK_RISERS", 5):
            with self.assertRaises(ValueError):
                knott_terrain._knott_east_walk_layout()


class KnottEastWalkRailsTest(unittest.TestCase):
    """The pipe rails flanking the east walk's steps."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_east_walk_rails(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.stair_x1, self.stair_x2, self.rise = (
            knott_terrain._knott_east_walk_layout()
        )

    def test_rails_flank_both_edges_of_the_steps(self):
        south = [b for b in self.boxes if b[0][1] == knott_hall.KH_Y2]
        north = [
            b for b in self.boxes if b[1][1] == knott_hall.KH_Y2 + KNOTT_EAST_WALK_W
        ]
        self.assertTrue(south)
        self.assertEqual(len(south), len(north))
        self.assertEqual(len(south) + len(north), len(self.boxes))

    def test_rails_are_a_thin_pipe_section(self):
        for mins, maxs in self.boxes:
            self.assertEqual(maxs[1] - mins[1], KNOTT_EAST_WALK_RAIL_T)

    def test_rails_run_level_past_each_end_of_the_flight(self):
        self.assertEqual(
            min(b[0][0] for b in self.boxes),
            self.stair_x1 - KNOTT_EAST_WALK_RAIL_END,
        )
        self.assertEqual(
            max(b[1][0] for b in self.boxes),
            self.stair_x2 + KNOTT_EAST_WALK_RAIL_END,
        )

    def test_each_rail_stands_on_two_posts_that_its_ends_overhang(self):
        south = [b for b in self.boxes if b[0][1] == knott_hall.KH_Y2]
        posts = [b for b in south if b[1][0] - b[0][0] == KNOTT_EAST_WALK_RAIL_T]
        self.assertEqual(len(posts), 2)
        top_post, bottom_post = sorted(posts)
        self.assertEqual(
            top_post[0][0] - min(b[0][0] for b in south), KNOTT_EAST_WALK_RAIL_OVH
        )
        self.assertEqual(
            max(b[1][0] for b in south) - bottom_post[1][0], KNOTT_EAST_WALK_RAIL_OVH
        )

    def test_rail_tops_stay_a_handrail_above_the_steps(self):
        walk = []
        knott_terrain._append_knott_east_walk(walk)
        treads = [b.get_bbox() for b in walk]
        for mins, maxs in self.boxes:
            underfoot = [
                t[1][2] for t in treads if t[0][0] < maxs[0] and t[1][0] > mins[0]
            ]
            if not underfoot:
                continue
            self.assertLessEqual(
                maxs[2], max(underfoot) + KNOTT_EAST_WALK_RAIL_H + self.rise
            )
            self.assertGreater(maxs[2], min(underfoot))


class KnottAccessibleRampTest(unittest.TestCase):
    """The ramp taking the driveway up to the east walk step-free."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_ramp(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.walk_z = FLOOR_Z2 + CHARLES_WALK_H
        self.foot_z = knott_terrain._knott_ramp_foot_z()
        self.turn_x, self.cy, self.corner_z, self.grade = (
            knott_terrain._knott_ramp_layout()
        )
        self.foot_x = KNOTT_DRIVEWAY_WS_X2
        self.hw = KNOTT_RAMP_W / 2
        self.head_y = knott_hall.KH_Y2 + KNOTT_EAST_WALK_W
        self.west = [b for b in self.boxes if b[0][0] > self.turn_x]
        self.south = [b for b in self.boxes if b[1][1] < self.cy]

    def test_the_ramp_starts_at_the_driveway_and_ends_on_the_east_walk(self):
        self.assertAlmostEqual(
            max(b[1][2] for b in self.boxes), knott_hall.GROUND_DOOR_BOTTOM
        )
        lowest = min(b[1][2] for b in self.boxes)
        self.assertGreater(lowest, self.foot_z)
        self.assertLessEqual(lowest, self.foot_z + STREET_SW_SLAB_LEN * self.grade)
        self.assertAlmostEqual(max(b[1][0] for b in self.boxes), self.foot_x)
        self.assertAlmostEqual(min(b[0][1] for b in self.boxes), self.head_y)

    def test_the_ramp_runs_on_over_the_curb_to_meet_the_roadbed(self):
        # Stopping it on the walk behind the curb would leave a step at the
        # one end of the route that has to be rollable.
        self.assertAlmostEqual(self.foot_z, FLOOR_Z2 + STREET_SURFACE_T)
        self.assertLess(self.foot_z, self.walk_z)
        foot = [b for b in self.boxes if abs(b[1][0] - self.foot_x) < 1e-6]
        self.assertEqual(len(foot), 1)
        west_run = self.foot_x - (self.turn_x + self.hw)
        self.assertAlmostEqual(self.corner_z - west_run * self.grade, self.foot_z)

    def test_the_ramp_lands_on_the_level_run_of_the_east_walk(self):
        stair_x1 = knott_terrain._knott_east_walk_layout()[0]
        self.assertGreaterEqual(self.turn_x - self.hw, knott_hall.GROUND_DOOR_X2)
        self.assertLessEqual(self.turn_x + self.hw, stair_x1)

    def test_the_west_leg_hugs_the_ennis_walk(self):
        # South of it the hillside climbs faster than the ramp does, so a leg
        # set back from that walk would bury itself in the bank. It is
        # pulled south of the walk's own edge to close up the gap to Pier 5.
        self.assertTrue(self.west)
        for mins, maxs in self.west:
            self.assertAlmostEqual(maxs[1], ENNIS_SW_EDGE - KNOTT_RAMP_SOUTH_SHIFT)
            self.assertAlmostEqual(
                mins[1], ENNIS_SW_EDGE - KNOTT_RAMP_SOUTH_SHIFT - KNOTT_RAMP_W
            )

    def test_both_legs_are_the_same_width(self):
        self.assertTrue(self.south)
        for mins, maxs in self.west:
            self.assertAlmostEqual(maxs[1] - mins[1], KNOTT_RAMP_W)
        for mins, maxs in self.south:
            self.assertAlmostEqual(maxs[0] - mins[0], KNOTT_RAMP_W)

    def test_the_grade_is_derived_from_the_run_the_landing_leaves(self):
        rise = knott_hall.GROUND_DOOR_BOTTOM - self.foot_z
        west_run = self.foot_x - (self.turn_x + self.hw)
        south_run = (self.cy - self.hw) - self.head_y
        self.assertAlmostEqual(self.grade, rise / (west_run + south_run))
        self.assertAlmostEqual(self.corner_z, self.foot_z + west_run * self.grade)

    def test_the_landing_is_level_and_square(self):
        landing = [
            b
            for b in self.boxes
            if abs(b[1][0] - b[0][0] - KNOTT_RAMP_W) < 1e-6
            and abs(b[1][1] - b[0][1] - KNOTT_RAMP_W) < 1e-6
            and abs(b[1][2] - self.corner_z) < 1e-6
        ]
        self.assertEqual(len(landing), 1)
        mins, maxs = landing[0]
        self.assertAlmostEqual(maxs[0] - mins[0], KNOTT_RAMP_W)
        self.assertAlmostEqual(maxs[1] - mins[1], KNOTT_RAMP_W)
        self.assertAlmostEqual(maxs[2], self.corner_z)
        self.assertAlmostEqual(mins[2], maxs[2] - (self.corner_z - FLOOR_Z1))

    def test_the_deck_never_runs_below_the_hillside(self):
        for mins, maxs in self.boxes:
            if maxs[2] < self.walk_z:
                continue  # the curb cut, which is meant to sit below grade
            for x in (mins[0], maxs[0]):
                for y in (mins[1], maxs[1]):
                    self.assertGreaterEqual(
                        maxs[2] + 1e-6, knott_terrain._kh_hill_ground_z(x, y)
                    )

    def test_the_south_leg_threads_clear_of_the_bridge_drop_pillars(self):
        _y1, _y2, pillar_xs, half_w = knott_terrain._knott_walkway_bent_layout()
        for pillar_x in pillar_xs:
            gap = max(
                (pillar_x - half_w) - (self.turn_x + self.hw),
                (self.turn_x - self.hw) - (pillar_x + half_w),
            )
            self.assertGreaterEqual(gap, KNOTT_RAMP_PILLAR_GAP)

    def test_the_landing_is_snug_against_the_east_most_pillar(self):
        _y1, _y2, pillar_xs, half_w = knott_terrain._knott_walkway_bent_layout()
        east_pillar_x = max(pillar_xs)
        gap = (east_pillar_x - half_w) - (self.turn_x + self.hw)
        self.assertGreaterEqual(gap, KNOTT_RAMP_PILLAR_GAP)
        self.assertLess(gap, KNOTT_RAMP_PILLAR_GAP + 4)

    def test_the_ramp_leaves_the_driveway_at_its_curb_line(self):
        self.assertAlmostEqual(max(b[1][0] for b in self.boxes), KNOTT_DRIVEWAY_WS_X2)

    def test_the_driveway_walk_gives_way_to_the_ramp_at_the_cut(self):
        # The walk, its joint, and the curb strip are all solid to the walk
        # height, so running them on past the ramp would backfill the cut.
        self.assertAlmostEqual(
            knott_terrain._knott_ramp_curb_cut_y1(), self.cy - self.hw
        )
        cut = [
            b
            for b in (b.get_bbox() for b in knott_terrain.build()[0])
            if b[0][0] > KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - STREET_SW_GAP
            and b[0][1] >= self.cy - self.hw - 1e-6
            and b[1][1] <= self.cy + self.hw + 1e-6
        ]
        self.assertTrue(cut)
        for _mins, maxs in cut:
            self.assertLessEqual(maxs[2], self.walk_z)

    def test_the_deck_is_poured_full_depth_so_it_retains_its_own_edge(self):
        for mins, _maxs in self.boxes:
            self.assertAlmostEqual(mins[2], FLOOR_Z1)

    def test_layout_rejects_a_ramp_too_wide_for_the_hillside(self):
        with mock.patch.object(knott_terrain, "KNOTT_RAMP_W", 4 * ENNIS_SW_EDGE):
            with self.assertRaises(ValueError):
                knott_terrain._knott_ramp_layout()


class KnottAccessibleRampRailsTest(unittest.TestCase):
    """The long-O guardrail along the north side of the ramp's west leg.

    One unbroken rail bent where the deck's own grade breaks: flat over the
    landing (which doesn't slope) and down the rest of the west leg to the
    driveway foot, closed into a round only at its two outer ends.
    """

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_ramp_rails(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.turn_x, self.cy, self.corner_z, self.grade = (
            knott_terrain._knott_ramp_layout()
        )
        self.hw = KNOTT_RAMP_W / 2
        self.foot_z = knott_terrain._knott_ramp_foot_z()
        self.x1, self.x2 = self.turn_x - self.hw, KNOTT_DRIVEWAY_WS_X2
        self.landing_x2 = self.turn_x + self.hw
        # The corner spur (and its own post/round) sits south of the plain
        # rail band, at y < cy + hw - rail_t, so pull those out first and
        # test the straight run's classification against what's left.
        rail_y1 = self.cy + self.hw - KNOTT_RAMP_RAIL_T
        self.corner_boxes = [b for b in self.boxes if b[0][1] < rail_y1 - 1e-6]
        self.boxes = [b for b in self.boxes if b not in self.corner_boxes]
        self.rails = [b for b in self.boxes if b[1][0] - b[0][0] > 20]
        self.posts = [
            b
            for b in self.boxes
            if b not in self.rails and abs(b[1][0] - b[0][0] - KNOTT_RAMP_RAIL_T) < 1e-6
        ]
        self.caps = [
            b for b in self.boxes if b not in self.rails and b not in self.posts
        ]

    def deck_z(self, x):
        if x <= self.landing_x2 + 1e-6:
            return self.corner_z
        return self.corner_z - (x - self.landing_x2) * self.grade

    def test_only_the_west_leg_is_railed(self):
        # The other three edges either retain the hillside or meet the
        # driveway at its own level, so there is nothing to fall off.
        for mins, maxs in self.boxes:
            self.assertGreaterEqual(mins[0] + 1e-6, self.x1)
            self.assertLessEqual(maxs[0] - 1e-6, self.x2)

    def test_the_rail_runs_along_the_north_edge_of_the_deck(self):
        for mins, maxs in self.boxes:
            self.assertAlmostEqual(maxs[1], self.cy + self.hw)
            self.assertAlmostEqual(mins[1], self.cy + self.hw - KNOTT_RAMP_RAIL_T)

    def test_the_o_spans_the_leg_end_to_end(self):
        self.assertAlmostEqual(min(b[0][0] for b in self.boxes), self.x1)
        self.assertAlmostEqual(max(b[1][0] for b in self.boxes), self.x2)

    def test_the_o_rides_a_rail_height_above_the_ramp_deck(self):
        # Each of the top and lower rails is built as two segments meeting
        # at the bend (one flat over the landing, one sloped beyond it), so
        # there are 4 rail brushes in all rather than 2.
        self.assertEqual(len(self.rails), 4)
        top, lower = (
            sorted(self.rails, key=lambda b: b[1][2], reverse=True)[:2],
            sorted(self.rails, key=lambda b: b[1][2], reverse=True)[2:],
        )
        for group, drop in ((top, 0), (lower, KNOTT_RAMP_RAIL_LOOP_H)):
            for rail in group:
                self.assertAlmostEqual(
                    rail[1][2], self.deck_z(rail[0][0]) + KNOTT_RAMP_RAIL_H - drop
                )
                self.assertAlmostEqual(
                    rail[0][2],
                    self.deck_z(rail[1][0])
                    + KNOTT_RAMP_RAIL_H
                    - drop
                    - KNOTT_RAMP_RAIL_T,
                )

    def test_the_o_is_turned_through_a_round_at_only_the_foot_end(self):
        # The foot end still gets a round; the head end instead turns the
        # corner and continues south as a spur, so there's no round there.
        self.assertTrue(self.caps)
        foot = self.caps
        self.assertAlmostEqual(max(b[1][0] for b in foot), self.x2)
        depth = max(b[1][2] for b in foot) - min(b[0][2] for b in foot)
        self.assertAlmostEqual(
            depth, KNOTT_RAMP_RAIL_LOOP_H + KNOTT_RAMP_RAIL_T, places=4
        )

    def test_the_whole_railing_is_steel(self):
        for brush in self.brushes:
            for face in brush.faces:
                self.assertEqual(face.tex, Textures.RAIL_STEEL)

    def test_it_stands_on_the_asked_for_number_of_pillars(self):
        self.assertEqual(len(self.posts), KNOTT_RAMP_RAIL_POSTS)

    def test_the_pillars_run_from_the_deck_up_through_the_top_rail(self):
        for mins, maxs in self.posts:
            self.assertAlmostEqual(maxs[2], self.deck_z(mins[0]) + KNOTT_RAMP_RAIL_H)
            self.assertLess(mins[2], self.deck_z(mins[0]))

    def test_the_o_overhangs_the_pillars_at_both_ends(self):
        rail_x2 = max(b[1][0] for b in self.rails)
        cap_r = (KNOTT_RAMP_RAIL_LOOP_H + KNOTT_RAMP_RAIL_T) / 2
        # At the head end there's no round cap (the rail turns the corner
        # instead), so the first post sits in from the corner's own round
        # by cap_r plus the usual overhang, rather than from the rail's
        # bare end.
        self.assertAlmostEqual(
            min(b[0][0] for b in self.posts), self.x1 + cap_r + KNOTT_RAMP_RAIL_OVH
        )
        self.assertAlmostEqual(
            max(b[1][0] for b in self.posts), rail_x2 - KNOTT_RAMP_RAIL_OVH
        )

    def test_the_rail_turns_the_corner_and_runs_south_a_short_distance(self):
        # The corner spur reuses the x1..x1+rail_t column and runs south
        # from the landing's rail band down to KNOTT_RAMP_RAIL_CORNER_RUN
        # short of it, still at the flat landing height, with its own
        # round at the spur's south end and an extra post along it.
        spur_rails = [b for b in self.corner_boxes if b[1][1] - b[0][1] > 20]
        spur_posts = [
            b
            for b in self.corner_boxes
            if b not in spur_rails and abs(b[1][1] - b[0][1] - KNOTT_RAMP_RAIL_T) < 1e-6
        ]
        spur_caps = [
            b for b in self.corner_boxes if b not in spur_rails and b not in spur_posts
        ]
        self.assertEqual(len(spur_rails), 2)
        self.assertEqual(len(spur_posts), 1)
        self.assertTrue(spur_caps)
        for mins, maxs in spur_rails:
            self.assertAlmostEqual(mins[0], self.x1)
            self.assertAlmostEqual(maxs[0], self.x1 + KNOTT_RAMP_RAIL_T)
            self.assertAlmostEqual(maxs[1], self.cy + self.hw)
            self.assertAlmostEqual(
                mins[1], self.cy + self.hw - KNOTT_RAMP_RAIL_CORNER_RUN
            )
        top, lower = sorted(spur_rails, key=lambda b: b[1][2], reverse=True)
        self.assertAlmostEqual(top[1][2], self.corner_z + KNOTT_RAMP_RAIL_H)
        self.assertAlmostEqual(
            lower[1][2], self.corner_z + KNOTT_RAMP_RAIL_H - KNOTT_RAMP_RAIL_LOOP_H
        )
        for brush in self.corner_boxes:
            self.assertAlmostEqual(brush[0][0], self.x1)
            self.assertLessEqual(brush[1][0] - self.x1, KNOTT_RAMP_RAIL_LOOP_H + 1e-6)


class KnottInteriorFloorTest(unittest.TestCase):
    """The even floor cut into the hillside inside the Knott Hall shell."""

    @classmethod
    def setUpClass(cls):
        cls.brushes = knott_terrain.build()[0]
        cls.boxes = [(b.get_bbox(), b) for b in cls.brushes]

    def surface_z(self, x, y):
        near = [
            b
            for (mn, mx), b in self.boxes
            if mn[0] - 1 <= x <= mx[0] + 1 and mn[1] - 1 <= y <= mx[1] + 1
        ]
        lo, hi = FLOOR_Z1 + 0.1, 4000
        if not any(b.contains((x, y, lo)) for b in near):
            return None
        for _ in range(30):
            mid = (lo + hi) / 2
            if any(b.contains((x, y, mid)) for b in near):
                lo = mid
            else:
                hi = mid
        return lo

    def interior_samples(self):
        for x1, y1, x2, y2 in knott_terrain._knott_interior_rects():
            for x in (x1 + 2, (x1 + x2) / 2, x2 - 2):
                for y in (y1 + 2, (y1 + y2) / 2, y2 - 2):
                    yield x, y

    def test_the_floor_is_even_across_the_whole_interior(self):
        for x, y in self.interior_samples():
            self.assertAlmostEqual(
                self.surface_z(x, y), knott_hall.GROUND_DOOR_BOTTOM, places=3
            )

    def test_the_floor_is_level_with_the_ground_door_sill(self):
        # The door opens straight on to it, so any step here would be one the
        # accessible route spends its whole length avoiding.
        x = (knott_hall.GROUND_DOOR_X1 + knott_hall.GROUND_DOOR_X2) / 2
        self.assertAlmostEqual(
            self.surface_z(x, knott_hall.KH_Y2 - knott_hall.WALL_T - 2),
            knott_hall.GROUND_DOOR_BOTTOM,
            places=3,
        )

    def test_the_interior_is_solid_right_down_to_the_base_fill(self):
        for x, y in self.interior_samples():
            self.assertTrue(
                any(b.contains((x, y, FLOOR_Z1 + 0.1)) for b in self.brushes),
                (x, y),
            )

    def test_the_doorway_reveal_is_floored_too(self):
        # Otherwise the floor stops at the inside face of the north wall and
        # the player crosses raw hillside standing in the doorway.
        *_, door = knott_terrain._knott_interior_rects()
        self.assertEqual(
            (door[0], door[2]),
            (knott_hall.GROUND_DOOR_X1, knott_hall.GROUND_DOOR_X2),
        )
        self.assertEqual(
            (door[1], door[3]), (knott_hall.KH_Y2 - knott_hall.WALL_T, knott_hall.KH_Y2)
        )
        cx = (door[0] + door[2]) / 2
        for y in (door[1] + 1, (door[1] + door[3]) / 2, door[3] - 1):
            self.assertAlmostEqual(
                self.surface_z(cx, y), knott_hall.GROUND_DOOR_BOTTOM, places=3
            )

    def test_walking_out_of_the_door_never_meets_a_step(self):
        # The coarse hillside fills used to cross the wall line a little high,
        # leaving a lip of ground standing through the cement on the sill.
        stair_y1 = knott_terrain._knott_door_walk_layout()[0]
        cx = (knott_hall.GROUND_DOOR_X1 + knott_hall.GROUND_DOOR_X2) / 2
        for y in range(knott_hall.KH_Y2 - knott_hall.WALL_T + 1, stair_y1, 8):
            self.assertAlmostEqual(
                self.surface_z(cx, y), knott_hall.GROUND_DOOR_BOTTOM, places=3, msg=y
            )

    def test_the_hillside_outside_the_walls_is_left_alone(self):
        for x, y in (
            (knott_hall.KH_X1 - 20, -1500),
            (knott_hall.KH_X2 + 20, -1500),
            (2600, knott_hall.KH_Y1 - 20),
        ):
            z = self.surface_z(x, y)
            self.assertIsNotNone(z, (x, y))
            self.assertNotAlmostEqual(z, knott_hall.GROUND_DOOR_BOTTOM, places=1)

    def test_the_two_interior_rectangles_meet_at_the_notch(self):
        lower, upper, _door = knott_terrain._knott_interior_rects()
        self.assertEqual(lower[3], upper[1])
        self.assertEqual(lower[3], knott_hall.KH_NOTCH_Y)
        self.assertGreater(lower[2] - lower[0], upper[2] - upper[0])


class KnottBridgeEntranceTest(unittest.TestCase):
    """The bridge-level entrance's sill against the deck that serves it."""

    @classmethod
    def setUpClass(cls):
        cls.brushes = [b for b in knott_hall.build()[0]]
        cls.cx = (knott_hall.KH_NORTH_X1 + knott_hall.KH_NORTH_X2) / 2 + (
            knott_hall.CENTER_OPENING_OFFSET
        )

    def deck_top(self):
        """The bridge deck's surface where it meets Knott's north face."""
        bridge_brushes = bridge.build()[0]
        for e in bridge.build()[1]:
            bridge_brushes = bridge_brushes + list(getattr(e, "brushes", []) or [])
        tops = [
            b.get_bbox()[1][2]
            for b in bridge_brushes
            if b.contains(
                (self.cx, knott_hall.KH_Y2 + 4, knott_hall.ENTRANCE_SILL_Z - 8)
            )
        ]
        return max(tops)

    def test_the_sill_is_flush_with_the_deck_outside_it(self):
        self.assertAlmostEqual(knott_hall.ENTRANCE_SILL_Z, self.deck_top(), places=3)

    def test_the_wall_under_the_entrance_stops_at_the_sill(self):
        # Above the sill and below the rest of the facade's opening grid the
        # doorway must be clear, or the crossing steps up into the building.
        for z in (knott_hall.ENTRANCE_SILL_Z + 1, knott_hall.OPENING_BOTTOM_Z - 1):
            self.assertFalse(
                any(
                    b.contains((self.cx, knott_hall.KH_Y2 - 8, z)) for b in self.brushes
                ),
                z,
            )

    def test_the_wall_below_the_sill_is_still_solid(self):
        self.assertTrue(
            any(
                b.contains(
                    (self.cx, knott_hall.KH_Y2 - 8, knott_hall.ENTRANCE_SILL_Z - 8)
                )
                for b in self.brushes
            )
        )


if __name__ == "__main__":
    unittest.main()
