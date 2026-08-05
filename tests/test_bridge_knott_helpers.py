"""Focused unit tests for the knott_hall.py/bridge.py sub-builder helpers
extracted from their previously-oversized build() functions. These
complement the broader map-level regression coverage in
test_regression.py/test_build_toggles.py by exercising individual helpers
directly, with assertions on brush counts, bounding boxes, and basic
geometric invariants (rather than only the merged whole-map output).
"""

import unittest

from quake_loyola import bridge, knott_hall


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
            # The sign hangs off the north (KH_Y2) wall.
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

    def test_build_disabled_returns_empty(self):
        original = knott_hall.KNOTT_ENABLED
        knott_hall.KNOTT_ENABLED = False
        try:
            brushes, entities = knott_hall.build()
        finally:
            knott_hall.KNOTT_ENABLED = original
        self.assertEqual((brushes, entities), ([], []))


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


if __name__ == "__main__":
    unittest.main()
