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
    KNOTT_RAMP_PILLAR_GAP,
    KNOTT_RAMP_RISE_RUN,
    KNOTT_RAMP_RISE_RUN_MIN,
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


class KnottHallBuildTest(unittest.TestCase):
    def test_build_matches_sum_of_helper_parts(self):
        brushes, entities = knott_hall.build()
        wall_brushes, west_detail, east_detail = knott_hall._build_walls(
            knott_hall.KH_GROUND_Z, knott_hall.KH_GROUND_Z + knott_hall.BUILDING_H
        )
        z2 = knott_hall.KH_GROUND_Z + knott_hall.BUILDING_H
        roof_brushes = knott_hall._build_roof(z2, z2 + knott_hall.ROOF_T)
        sign_brushes = knott_hall._build_sign(knott_hall.KH_GROUND_Z)
        parapet_brushes = knott_hall._build_parapet(z2, z2 + knott_hall.PARAPET_H)

        self.assertEqual(
            len(brushes),
            len(wall_brushes) + len(roof_brushes) + len(sign_brushes),
        )
        self.assertEqual(len(entities), 1)
        self.assertEqual(
            len(entities[0].brushes),
            len(west_detail) + len(east_detail) + len(parapet_brushes),
        )


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

    def test_emits_a_beam_five_pillars_and_a_tie_beam(self):
        self.assertEqual(len(self.brushes), 7)

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

    def test_pillars_reach_the_hillside_below_the_beam(self):
        beam_bottom = (
            KNOTT_ENT_WALK_ZT1
            - KNOTT.wall_t
            + BRIDGE_CENTER_SPAN_OFFSET[2]
            - BRIDGE_SUPPORT_BEAM_H
        )
        pillars = [b for b in self.boxes if b[1][2] == beam_bottom]
        self.assertEqual(len(pillars), 5)
        for mins, maxs in pillars:
            ground = knott_terrain._kh_hill_ground_z((mins[0] + maxs[0]) / 2, maxs[1])
            self.assertLessEqual(mins[2], ground)
            self.assertGreater(mins[2], 0)


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

    def test_walk_lines_up_with_the_doorway(self):
        for mins, maxs in self.boxes:
            self.assertEqual(mins[0], knott_hall.GROUND_DOOR_X1)
            self.assertEqual(maxs[0], knott_hall.GROUND_DOOR_X2)

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
        path = next(b for b in self.paved if b.get_bbox()[1][1] == ENNIS_SW_EDGE)
        mins, maxs = path.get_bbox()
        self.assertEqual(mins[1], self.stair_y2)
        self.assertEqual(maxs[2], self.stair_z2)
        ends = [
            v[2]
            for face in path.faces
            for v in (face.p1, face.p2, face.p3)
            if v[1] == ENNIS_SW_EDGE and v[2] > FLOOR_Z1
        ]
        self.assertEqual(max(ends), self.flat_z)

    def test_path_ramps_the_hillside_ledge_away_at_the_bottom(self):
        tail = max(self.paved, key=lambda b: b.get_bbox()[1][1])
        mins, maxs = tail.get_bbox()
        self.assertEqual(mins[1], ENNIS_SW_EDGE)
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


class KnottEntranceWalkRailsTest(unittest.TestCase):
    """The pipe rails flanking those steps."""

    def setUp(self):
        self.brushes = []
        knott_terrain._append_knott_entrance_walk_rails(self.brushes)
        self.boxes = [b.get_bbox() for b in self.brushes]
        self.stair_y1, self.stair_y2, self.stair_z2 = (
            knott_terrain._knott_door_walk_layout()
        )

    def test_rails_flank_both_edges_of_the_steps(self):
        west = [b for b in self.boxes if b[0][0] == knott_hall.GROUND_DOOR_X1]
        east = [b for b in self.boxes if b[1][0] == knott_hall.GROUND_DOOR_X2]
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
        west = [b for b in self.boxes if b[0][0] == knott_hall.GROUND_DOOR_X1]
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

    def test_each_rail_end_overhangs_its_post(self):
        west = [b for b in self.boxes if b[0][0] == knott_hall.GROUND_DOOR_X1]
        posts = [b for b in west if b[1][1] - b[0][1] == KNOTT_DOOR_WALK_RAIL_T]
        top_post, bottom_post = sorted(posts)
        self.assertEqual(
            top_post[0][1] - min(b[0][1] for b in west), KNOTT_DOOR_WALK_RAIL_OVH
        )
        self.assertEqual(
            max(b[1][1] for b in west) - bottom_post[1][1], KNOTT_DOOR_WALK_RAIL_OVH
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
        self.assertEqual(min(b[0][0] for b in self.boxes), knott_hall.GROUND_DOOR_X2)
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
        # set back from that walk would bury itself in the bank.
        self.assertTrue(self.west)
        for mins, maxs in self.west:
            self.assertAlmostEqual(maxs[1], ENNIS_SW_EDGE)
            self.assertAlmostEqual(mins[1], ENNIS_SW_EDGE - KNOTT_RAMP_W)

    def test_both_legs_are_the_same_width(self):
        self.assertTrue(self.south)
        for mins, maxs in self.west:
            self.assertAlmostEqual(maxs[1] - mins[1], KNOTT_RAMP_W)
        for mins, maxs in self.south:
            self.assertAlmostEqual(maxs[0] - mins[0], KNOTT_RAMP_W)

    def test_the_grade_stays_within_the_accessible_range(self):
        self.assertLessEqual(self.grade, 1 / KNOTT_RAMP_RISE_RUN_MIN)
        self.assertGreaterEqual(self.grade, 1 / KNOTT_RAMP_RISE_RUN)
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

    def test_layout_rejects_a_grade_it_has_no_room_for(self):
        with mock.patch.object(knott_terrain, "KNOTT_RAMP_RISE_RUN", 40):
            with self.assertRaises(ValueError):
                knott_terrain._knott_ramp_layout()

    def test_layout_rejects_a_ramp_too_wide_for_the_hillside(self):
        with mock.patch.object(knott_terrain, "KNOTT_RAMP_W", 4 * ENNIS_SW_EDGE):
            with self.assertRaises(ValueError):
                knott_terrain._knott_ramp_layout()


if __name__ == "__main__":
    unittest.main()
