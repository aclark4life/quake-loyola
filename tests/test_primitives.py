"""Tests for validation/edge-case branches in geometry/primitives.py that
aren't already exercised by tests/test_geometry.py's happy-path coverage —
degenerate-input guards, reversed-bound normalization, and empty-result
early-outs in the low-level brush constructors."""

import unittest

from quake_loyola.geometry import (
    arch_pie_seg,
    arch_seg,
    arch_seg_chord,
    box,
    box_with_hole,
    clip_poly_to_rect,
    curb_seg,
    polygon_prism,
    radial_fan_fills,
    ramp_slab,
    ramp_slab_y,
    slab_chamfered_y,
    tri_prism,
    tri_ramp_prism,
)
from quake_loyola.mapdata import Brush


class BoxNormalizationTests(unittest.TestCase):
    def test_box_normalizes_reversed_bounds(self):
        reversed_brush = box(10, 10, 10, 0, 0, 0, "tex")
        forward_brush = box(0, 0, 0, 10, 10, 10, "tex")
        # Same 8 corner positions regardless of argument order.
        reversed_pts = {p for f in reversed_brush.faces for p in (f.p1, f.p2, f.p3)}
        forward_pts = {p for f in forward_brush.faces for p in (f.p1, f.p2, f.p3)}
        self.assertEqual(reversed_pts, forward_pts)

    def test_box_rejects_zero_thickness_on_each_axis(self):
        for bounds in (
            (0, 0, 0, 0, 10, 10),
            (0, 0, 0, 10, 0, 10),
            (0, 0, 0, 10, 10, 0),
        ):
            with self.assertRaises(ValueError):
                box(*bounds, "tex")


class BoxWithHoleTests(unittest.TestCase):
    def test_normalizes_reversed_outer_and_hole_bounds(self):
        pieces = box_with_hole(10, 10, 0, 0, 0, 10, 6, 6, 2, 2, "tex")
        self.assertTrue(pieces)

    def test_hole_outside_outer_bounds_returns_single_box(self):
        # Hole entirely outside the outer box clamps to empty -> no opening.
        pieces = box_with_hole(0, 0, 0, 10, 10, 10, 20, 20, 30, 30, "tex")
        self.assertEqual(len(pieces), 1)


class PolygonPrismTests(unittest.TestCase):
    def test_rejects_fewer_than_three_points(self):
        with self.assertRaises(ValueError):
            polygon_prism([(0, 0), (1, 1)], 0, 10, "tex")

    def test_rejects_zero_height(self):
        with self.assertRaises(ValueError):
            polygon_prism([(0, 0), (1, 0), (1, 1)], 5, 5, "tex")

    def test_rejects_degenerate_collinear_polygon(self):
        with self.assertRaises(ValueError):
            polygon_prism([(0, 0), (1, 0), (2, 0)], 0, 10, "tex")

    def test_reverses_clockwise_winding(self):
        # Clockwise input should still build a valid brush (reversed
        # internally), not raise.
        brush = polygon_prism([(0, 0), (0, 1), (1, 0)], 0, 10, "tex")
        self.assertIsInstance(brush, Brush)


class ClipPolyToRectTests(unittest.TestCase):
    def test_polygon_fully_outside_rect_returns_empty(self):
        square = [(-10, -10), (-9, -10), (-9, -9), (-10, -9)]
        self.assertEqual(clip_poly_to_rect(square, 0, 0, 5, 5), [])

    def test_polygon_fully_inside_rect_is_unclipped_in_area(self):
        square = [(1, 1), (2, 1), (2, 2), (1, 2)]
        clipped = clip_poly_to_rect(square, 0, 0, 5, 5)
        self.assertEqual(len(clipped), 4)


class RadialFanFillsTests(unittest.TestCase):
    def test_rejects_fewer_than_three_segments(self):
        with self.assertRaises(ValueError):
            radial_fan_fills(0, 0, 10, -20, -20, 20, 20, 0, 10, "tex", n=2)

    def test_builds_fills_for_small_circle_in_large_rect(self):
        fills = radial_fan_fills(0, 0, 10, -50, -50, 50, 50, 0, 10, "tex", n=8)
        self.assertTrue(fills)


class RampSlabTests(unittest.TestCase):
    def test_normalizes_reversed_x_bounds_with_paired_z(self):
        forward = ramp_slab(0, 10, 0, 10, 0, 5, 20, 25, "tex")
        reversed_ = ramp_slab(10, 0, 0, 10, 5, 0, 25, 20, "tex")
        self.assertEqual(len(forward.faces), len(reversed_.faces))

    def test_rejects_zero_span_x(self):
        with self.assertRaises(ValueError):
            ramp_slab(5, 5, 0, 10, 0, 0, 20, 20, "tex")

    def test_rejects_zero_span_y(self):
        with self.assertRaises(ValueError):
            ramp_slab(0, 10, 5, 5, 0, 0, 20, 20, "tex")

    def test_rejects_zero_thickness_everywhere(self):
        with self.assertRaises(ValueError):
            ramp_slab(0, 10, 0, 10, 5, 5, 5, 5, "tex")

    def test_flat_ends_omit_end_cap_faces(self):
        # zt1 == zb1 (flat at x1 end) should still build without error and
        # skip that end-cap face while zt2 != zb2 keeps the other one.
        brush = ramp_slab(0, 10, 0, 10, 0, 0, 0, 20, "tex")
        self.assertIsInstance(brush, Brush)


class RampSlabYTests(unittest.TestCase):
    def test_normalizes_reversed_y_bounds_with_paired_z(self):
        forward = ramp_slab_y(0, 10, 0, 10, 0, 5, 20, 25, "tex")
        reversed_ = ramp_slab_y(0, 10, 10, 0, 5, 0, 25, 20, "tex")
        self.assertEqual(len(forward.faces), len(reversed_.faces))


class SlabChamferedYTests(unittest.TestCase):
    def test_normalizes_reversed_y_bounds(self):
        forward = slab_chamfered_y(0, 10, 0, 10, 0, 20, 25, "tex")
        reversed_ = slab_chamfered_y(0, 10, 10, 0, 0, 25, 20, "tex")
        self.assertEqual(len(forward.faces), len(reversed_.faces))


class TriPrismTests(unittest.TestCase):
    def test_rejects_z1_greater_or_equal_z2(self):
        with self.assertRaises(ValueError):
            tri_prism(0, 0, 1, 0, 0, 1, 10, 10, "tex")

    def test_rejects_degenerate_collinear_triangle(self):
        with self.assertRaises(ValueError):
            tri_prism(0, 0, 1, 0, 2, 0, 0, 10, "tex")

    def test_rejects_clockwise_winding(self):
        with self.assertRaises(ValueError):
            tri_prism(0, 0, 0, 1, 1, 0, 0, 10, "tex")

    def test_accepts_counter_clockwise_winding(self):
        brush = tri_prism(0, 0, 1, 0, 0, 1, 0, 10, "tex")
        self.assertIsInstance(brush, Brush)


class TriRampPrismTests(unittest.TestCase):
    def test_rejects_degenerate_collinear_triangle(self):
        with self.assertRaises(ValueError):
            tri_ramp_prism(0, 0, 1, 0, 2, 0, 0, 5, 5, 5, "tex")

    def test_rejects_clockwise_winding(self):
        with self.assertRaises(ValueError):
            tri_ramp_prism(0, 0, 0, 1, 1, 0, 0, 5, 5, 5, "tex")

    def test_rejects_zbot_above_minimum_apex_height(self):
        with self.assertRaises(ValueError):
            tri_ramp_prism(0, 0, 1, 0, 0, 1, 10, 5, 5, 5, "tex")

    def test_accepts_valid_ramp_triangle(self):
        brush = tri_ramp_prism(0, 0, 1, 0, 0, 1, 0, 5, 6, 7, "tex")
        self.assertIsInstance(brush, Brush)


class ArchSegValidationTests(unittest.TestCase):
    def test_rejects_invalid_radius_ordering(self):
        with self.assertRaises(ValueError):
            arch_seg(0, 10, 0, 0, 10, 5, 0, 90, "tex")

    def test_rejects_non_increasing_angles(self):
        with self.assertRaises(ValueError):
            arch_seg(0, 10, 0, 0, 5, 10, 90, 0, "tex")

    def test_rejects_zero_depth_segment(self):
        with self.assertRaises(ValueError):
            arch_seg(5, 5, 0, 0, 5, 10, 0, 90, "tex")


class ArchSegChordValidationTests(unittest.TestCase):
    def test_rejects_invalid_radius_ordering(self):
        with self.assertRaises(ValueError):
            arch_seg_chord(0, 10, 0, 0, 10, 5, 0, 90, "tex")

    def test_rejects_non_increasing_angles(self):
        with self.assertRaises(ValueError):
            arch_seg_chord(0, 10, 0, 0, 5, 10, 90, 0, "tex")

    def test_rejects_zero_depth_segment(self):
        with self.assertRaises(ValueError):
            arch_seg_chord(5, 5, 0, 0, 5, 10, 0, 90, "tex")


class CurbSegValidationTests(unittest.TestCase):
    def test_rejects_invalid_radius_ordering(self):
        with self.assertRaises(ValueError):
            curb_seg(0, 0, 0, 10, 10, 5, 0, 90, "tex")

    def test_rejects_non_increasing_angles(self):
        with self.assertRaises(ValueError):
            curb_seg(0, 0, 0, 10, 5, 10, 90, 0, "tex")

    def test_rejects_zero_height_segment(self):
        with self.assertRaises(ValueError):
            curb_seg(0, 0, 5, 5, 5, 10, 0, 90, "tex")


class ArchPieSegValidationTests(unittest.TestCase):
    def test_rejects_non_positive_radius(self):
        with self.assertRaises(ValueError):
            arch_pie_seg(0, 10, 0, 0, 0, 0, 90, "tex")

    def test_rejects_non_increasing_angles(self):
        with self.assertRaises(ValueError):
            arch_pie_seg(0, 10, 0, 0, 10, 90, 0, "tex")

    def test_rejects_zero_depth_segment(self):
        with self.assertRaises(ValueError):
            arch_pie_seg(5, 5, 0, 0, 10, 0, 90, "tex")


if __name__ == "__main__":
    unittest.main()
