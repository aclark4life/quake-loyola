import unittest

from mapdata import Brush, Entity, Face, MapBuilder, format_value, format_point


class FormattingTests(unittest.TestCase):
    def test_format_value_whole_numbers_render_as_ints(self):
        self.assertEqual(format_value(5), "5")
        self.assertEqual(format_value(5.0), "5")
        self.assertEqual(format_value(-16), "-16")
        self.assertEqual(format_value(0), "0")

    def test_format_value_fractions_use_six_sig_figs(self):
        self.assertEqual(format_value(2.5), "2.5")
        self.assertEqual(format_value(1.0 / 3.0), "0.333333")

    def test_format_point(self):
        self.assertEqual(format_point(1, 2, 3), "( 1 2 3 )")
        self.assertEqual(format_point(-16, 0, 2.5), "( -16 0 2.5 )")


class FaceTests(unittest.TestCase):
    def test_to_map_default_params(self):
        f = Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "city2_7")
        self.assertEqual(f.to_map(), "( 0 0 0 ) ( 0 1 0 ) ( 0 0 1 ) city2_7 0 0 0 1 1")

    def test_to_map_custom_params(self):
        f = Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "t", "8 0 0 2 2")
        self.assertEqual(f.to_map(), "( 0 0 0 ) ( 0 1 0 ) ( 0 0 1 ) t 8 0 0 2 2")

    def test_translated_shifts_all_points_and_keeps_tex(self):
        f = Face((0, 0, 0), (1, 0, 0), (0, 1, 0), "t", "p").translated(10, 20, 30)
        self.assertEqual(f.p1, (10, 20, 30))
        self.assertEqual(f.p2, (11, 20, 30))
        self.assertEqual(f.p3, (10, 21, 30))
        self.assertEqual(f.tex, "t")
        self.assertEqual(f.params, "p")


class BrushTests(unittest.TestCase):
    def _brush(self):
        return Brush(
            [
                Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "t"),
                Face((1, 0, 0), (1, 0, 1), (1, 1, 0), "t"),
            ]
        )

    def test_to_map_wraps_faces_in_braces(self):
        text = self._brush().to_map()
        lines = text.split("\n")
        self.assertEqual(lines[0], "{")
        self.assertEqual(lines[-1], "}")
        self.assertEqual(len(lines), 4)  # { + 2 faces + }

    def test_str_matches_to_map(self):
        b = self._brush()
        self.assertEqual(str(b), b.to_map())

    def test_translated_returns_new_brush(self):
        b = self._brush()
        moved = b.translated(0, 0, 5)
        self.assertIsNot(moved, b)
        self.assertEqual(moved.faces[0].p1, (0, 0, 5))
        self.assertEqual(b.faces[0].p1, (0, 0, 0))  # original untouched


class EntityTests(unittest.TestCase):
    def test_point_entity_field_order(self):
        e = Entity("info_player_start", {"origin": "0 0 24", "angle": "90"})
        self.assertEqual(
            e.to_map(),
            '{\n"classname" "info_player_start"\n"origin" "0 0 24"\n"angle" "90"\n}',
        )

    def test_brush_entity_includes_brushes(self):
        brush = Brush([Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "t")])
        e = Entity("func_detail", {}, [brush])
        text = e.to_map()
        self.assertIn('"classname" "func_detail"', text)
        self.assertIn(brush.to_map(), text)
        self.assertTrue(text.endswith("}"))

    def test_defaults_are_independent(self):
        a = Entity("a")
        b = Entity("b")
        a.fields["x"] = "1"
        a.brushes.append(object())
        self.assertEqual(b.fields, {})
        self.assertEqual(b.brushes, [])


class MapBuilderTests(unittest.TestCase):
    def test_accumulation(self):
        mb = MapBuilder()
        mb.add_brush(Brush([]))
        mb.add_brushes([Brush([]), Brush([])])
        mb.add_entity(Entity("a"))
        mb.add_entities([Entity("b"), Entity("c")])
        self.assertEqual(len(mb.brushes), 3)
        self.assertEqual(len(mb.entities), 3)

    def test_to_map_assembles_worldspawn_then_entities(self):
        mb = MapBuilder()
        box = Brush([Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "t")])
        mb.add_brush(box)
        mb.add_entity(Entity("info_player_start", {"origin": "0 0 0"}))
        text = mb.to_map({"wad": "w"})
        world = Entity("worldspawn", {"wad": "w"}, [box]).to_map()
        ip = Entity("info_player_start", {"origin": "0 0 0"}).to_map()
        self.assertEqual(text, world + "\n\n" + ip + "\n")

    def test_to_map_with_no_entities(self):
        mb = MapBuilder()
        text = mb.to_map({"wad": "w"})
        self.assertEqual(text, Entity("worldspawn", {"wad": "w"}, []).to_map() + "\n")


if __name__ == "__main__":
    unittest.main()
