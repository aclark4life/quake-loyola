import unittest

from quake_loyola.geometry import (
    box,
    brush_ent,
    ent,
    make_tree,
    ramp_slab_y,
    square_wall,
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


if __name__ == "__main__":
    unittest.main()
