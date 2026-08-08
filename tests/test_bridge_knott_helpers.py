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


if __name__ == "__main__":
    unittest.main()
