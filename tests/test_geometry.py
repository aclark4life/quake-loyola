import unittest

from quake_loyola.geometry import (
    arch_seg,
    box,
    box_with_round_hole,
    brush_ent,
    corner_ramp,
    ent,
    gable_slats,
    iron_fence,
    layered_wall,
    make_pixel_tree,
    make_tree,
    octagon_column,
    polygon_prism,
    radial_fan_fills,
    ramp_slab_y,
    render_text_flat,
    render_text_flat_x,
    square_wall,
    tri_prism,
)
from quake_loyola.mapdata import Brush, Entity


class BoxTests(unittest.TestCase):
    def test_box_returns_brush_with_six_faces(self):
        b = box(-64, -64, 0, 64, 64, 64, "city2_7")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 6)

    def test_box_serialization_is_stable(self):
        expected = (
            "{\n"
            "( 0 0 0 ) ( 0 1 0 ) ( 0 0 1 ) t 0 0 0 1 1\n"
            "( 1 0 0 ) ( 1 0 1 ) ( 1 1 0 ) t 0 0 0 1 1\n"
            "( 0 0 0 ) ( 0 0 1 ) ( 1 0 0 ) t 0 0 0 1 1\n"
            "( 0 1 0 ) ( 1 1 0 ) ( 0 1 1 ) t 0 0 0 1 1\n"
            "( 0 0 0 ) ( 1 0 0 ) ( 0 1 0 ) t 0 0 0 1 1\n"
            "( 0 0 1 ) ( 0 1 1 ) ( 1 0 1 ) t 0 0 0 1 1\n"
            "}"
        )
        self.assertEqual(box(0, 0, 0, 1, 1, 1, "t").to_map(), expected)

    def test_box_distinct_top_bottom_textures(self):
        b = box(0, 0, 0, 1, 1, 1, "side", tt="top", tb="bot")
        self.assertEqual(b.faces[4].tex, "bot")  # -Z bottom
        self.assertEqual(b.faces[5].tex, "top")  # +Z top


class EntityHelperTests(unittest.TestCase):
    def test_ent_returns_point_entity(self):
        e = ent("item_health", origin="1 2 3")
        self.assertIsInstance(e, Entity)
        self.assertEqual(e.classname, "item_health")
        self.assertEqual(e.fields, {"origin": "1 2 3"})
        self.assertEqual(e.brushes, [])

    def test_brush_ent_with_list(self):
        bs = [box(0, 0, 0, 1, 1, 1, "t"), box(2, 2, 2, 3, 3, 3, "t")]
        e = brush_ent("func_detail", bs, foo="bar")
        self.assertIsInstance(e, Entity)
        self.assertEqual(len(e.brushes), 2)
        self.assertEqual(e.fields, {"foo": "bar"})

    def test_brush_ent_accepts_single_brush(self):
        e = brush_ent("func_wall", box(0, 0, 0, 1, 1, 1, "t"))
        self.assertEqual(len(e.brushes), 1)


class CompositeShapeTests(unittest.TestCase):
    def test_make_tree_returns_four_brushes(self):
        brushes = make_tree(0, 0, 0)
        self.assertEqual(len(brushes), 4)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_square_wall_returns_brush_list(self):
        brushes = square_wall(-8, 8, -200, 200, 0, 128, 48, "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_ramp_slab_y_full_prism_has_six_faces(self):
        b = ramp_slab_y(0, 10, 0, 10, 0, 0, 5, 5, "t")
        self.assertEqual(len(b.faces), 6)

    def test_ramp_slab_y_knife_edge_drops_endcap(self):
        # zt2 == zb2 at the far end -> that end tapers to an edge, face omitted
        b = ramp_slab_y(0, 10, 0, 10, 0, 0, 5, 0, "t")
        self.assertEqual(len(b.faces), 5)

    def test_tri_prism_returns_five_faces(self):
        b = tri_prism(0, 0, 10, 0, 0, 10, 0, 20, "t")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 5)

    def test_corner_ramp_returns_four_faces(self):
        b = corner_ramp(10, 0, 10, 0, 0, 20, "t")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 4)

    def test_arch_seg_returns_six_faces(self):
        b = arch_seg(0, 10, 0, 0, 16, 32, 0, 45, "t")
        self.assertIsInstance(b, Brush)
        self.assertEqual(len(b.faces), 6)

    def test_octagon_column_returns_ten_faces(self):
        b = octagon_column(0, 0, 0, 64, 32, "t")
        self.assertIsInstance(b, Brush)
        # 8 side faces + top + bottom
        self.assertEqual(len(b.faces), 10)

    def test_layered_wall_omits_covered_cells_and_keeps_others(self):
        # A single opening exactly matching one grid cell should leave that cell
        # out of the result while still emitting the surrounding wall pieces.
        brushes = layered_wall(0, -8, 0, 100, 0, 100, [(40, 20, 60, 80)], "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))
        # No brush should span exactly the opening's x/z extent (it must be omitted)
        for b in brushes:
            pts = [p for f in b.faces for p in (f.p1, f.p2, f.p3)]
            xs = sorted({p[0] for p in pts})
            zs = sorted({p[2] for p in pts})
            self.assertFalse(
                min(xs) == 40 and max(xs) == 60 and min(zs) == 20 and max(zs) == 80
            )

    def test_layered_wall_no_openings_returns_single_slab(self):
        brushes = layered_wall(0, -8, 0, 100, 0, 100, [], "t")
        self.assertEqual(len(brushes), 1)


class GuardClauseTests(unittest.TestCase):
    def test_iron_fence_rejects_non_positive_spacing(self):
        with self.assertRaises(ValueError):
            iron_fence([(0, 100)], -8, 8, "t", 0, spacing=0)

    def test_gable_slats_rejects_zero_denominator(self):
        # ridge_z == eave_z + slab_t -> denom is zero, must raise instead of
        # hanging or dividing by zero deep inside edge_x().
        with self.assertRaises(ValueError):
            gable_slats(0, 100, 50, 0, 16, 16, 0, 8, "t")


class RoundHoleAndRadialFanTests(unittest.TestCase):
    def test_box_with_round_hole_returns_brushes_around_circle(self):
        pieces = box_with_round_hole(-64, -64, 0, 64, 64, 64, 0, 0, 16, "t", n=16)
        self.assertTrue(len(pieces) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in pieces))

    def test_radial_fan_fills_covers_corner_gaps(self):
        fills = radial_fan_fills(0, 0, 16, -64, -64, 64, 64, 0, 64, "t", n=16)
        self.assertTrue(len(fills) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in fills))

    def test_radial_fan_fills_rejects_too_few_segments(self):
        with self.assertRaises(ValueError):
            radial_fan_fills(0, 0, 16, -64, -64, 64, 64, 0, 64, "t", n=2)


class TextRenderingTests(unittest.TestCase):
    def test_render_text_flat_x_returns_brushes_for_nonblank_text(self):
        brushes = render_text_flat_x("A", 0, 0, 0, 4, 4, 2, "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_render_text_flat_returns_brushes_for_nonblank_text(self):
        brushes = render_text_flat("A", 0, 0, 0, 4, 4, 2, "t")
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_render_text_flat_blank_space_returns_no_brushes(self):
        self.assertEqual(render_text_flat(" ", 0, 0, 0, 4, 4, 2, "t"), [])


class PixelTreeTests(unittest.TestCase):
    def test_make_pixel_tree_returns_brushes(self):
        brushes = make_pixel_tree(0, 0, 0)
        self.assertTrue(len(brushes) > 0)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_make_pixel_tree_rejects_ring_segs_of_one(self):
        with self.assertRaises(ValueError):
            make_pixel_tree(0, 0, 0, ring_segs=1)


class PolygonPrismNormalizationTests(unittest.TestCase):
    def test_polygon_prism_normalizes_reversed_z_bounds(self):
        pts = [(0, 0), (10, 0), (10, 10), (0, 10)]
        a = polygon_prism(pts, 0, 20, "t")
        b = polygon_prism(pts, 20, 0, "t")
        self.assertEqual(len(a.faces), len(b.faces))

    def test_polygon_prism_rejects_degenerate_polygon(self):
        with self.assertRaises(ValueError):
            polygon_prism([(0, 0), (1, 0), (2, 0)], 0, 10, "t")

    def test_polygon_prism_rejects_zero_height(self):
        with self.assertRaises(ValueError):
            polygon_prism([(0, 0), (1, 0), (1, 1)], 5, 5, "t")


class PrimitiveValidationTests(unittest.TestCase):
    def test_tri_prism_rejects_clockwise_winding(self):
        with self.assertRaises(ValueError):
            tri_prism(0, 0, 0, 10, 10, 0, 0, 20, "t")

    def test_tri_prism_rejects_reversed_z(self):
        with self.assertRaises(ValueError):
            tri_prism(0, 0, 10, 0, 0, 10, 20, 0, "t")

    def test_arch_seg_rejects_reversed_radii(self):
        with self.assertRaises(ValueError):
            arch_seg(0, 10, 0, 0, 32, 16, 0, 45, "t")

    def test_arch_seg_rejects_reversed_angles(self):
        with self.assertRaises(ValueError):
            arch_seg(0, 10, 0, 0, 16, 32, 45, 0, "t")


if __name__ == "__main__":
    unittest.main()
