import unittest

from quake_loyola.mapdata import (
    Brush,
    Entity,
    Face,
    MapBuilder,
)
from quake_loyola.utils import format_point, format_value


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

    def test_to_map_rejects_newline_in_params(self):
        f = Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "t", "0 0 0 1 1\nworldspawn")
        with self.assertRaises(ValueError):
            f.to_map()

    def test_to_map_rejects_quote_in_params(self):
        f = Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "t", '0 0 0 1 1 "')
        with self.assertRaises(ValueError):
            f.to_map()

    def test_translated_shifts_all_points_and_keeps_tex(self):
        f = Face((0, 0, 0), (1, 0, 0), (0, 1, 0), "t", "p").translated(10, 20, 30)
        self.assertEqual(f.p1, (10, 20, 30))
        self.assertEqual(f.p2, (11, 20, 30))
        self.assertEqual(f.p3, (10, 21, 30))
        self.assertEqual(f.tex, "t")
        self.assertEqual(f.params, "p")

    def test_rotated_z_90_degrees_about_origin(self):
        # (1, 0, 5) rotated 90 degrees CCW about the Z axis through the
        # origin -> (0, 1, 5); Z is unaffected.
        f = Face((1, 0, 5), (2, 0, 5), (1, 1, 5), "t").rotated_z(90)
        self.assertEqual(f.p1, (0, 1, 5))
        self.assertEqual(f.p2, (0, 2, 5))
        self.assertEqual(f.p3, (-1, 1, 5))

    def test_rotated_z_snaps_to_tenth_unit(self):
        # A 30-degree rotation produces irrational coordinates; rotated_z
        # must snap them to the documented 0.1-unit grid rather than leaving
        # raw floating-point noise (see rotated_z's docstring).
        f = Face((10, 0, 0), (0, 0, 0), (0, 0, 1), "t").rotated_z(30)
        for coord in (f.p1[0], f.p1[1]):
            self.assertEqual(coord, round(coord, 1))

    def test_rotated_z_about_nonzero_center(self):
        f = Face((10, 10, 0), (11, 10, 0), (10, 11, 0), "t").rotated_z(
            180, cx=10, cy=10
        )
        self.assertEqual(f.p1, (10, 10, 0))
        self.assertEqual(f.p2, (9, 10, 0))
        self.assertEqual(f.p3, (10, 9, 0))

    def test_is_inside_true_for_point_on_solid_side(self):
        # Face with normal pointing toward +X; (1, 0, 0) is on the solid side.
        f = Face((0, 0, 0), (0, 1, 0), (0, 0, 1), "t")
        self.assertTrue(f.is_inside((1, 0, 0)))
        self.assertFalse(f.is_inside((-1, 0, 0)))


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

    def _unit_cube(self):
        from quake_loyola.geometry import box

        return box(0, 0, 0, 10, 10, 10, "t")

    def test_contains_true_for_interior_point(self):
        self.assertTrue(self._unit_cube().contains((5, 5, 5)))

    def test_contains_false_for_exterior_point(self):
        self.assertFalse(self._unit_cube().contains((50, 50, 50)))

    def test_contains_raises_on_empty_brush(self):
        with self.assertRaises(ValueError):
            Brush([]).contains((0, 0, 0))

    def test_get_bbox_matches_box_extents(self):
        lo, hi = self._unit_cube().get_bbox()
        for a, b in zip(lo, (0, 0, 0), strict=True):
            self.assertAlmostEqual(a, b)
        for a, b in zip(hi, (10, 10, 10), strict=True):
            self.assertAlmostEqual(a, b)

    def test_get_bbox_raises_on_empty_brush(self):
        with self.assertRaises(ValueError):
            Brush([]).get_bbox()

    def test_rotated_z_delegates_to_faces(self):
        b = self._unit_cube().rotated_z(90)
        self.assertEqual(len(b.faces), 6)
        self.assertIsInstance(b, Brush)


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

    def test_to_map_rejects_quote_in_field_value(self):
        e = Entity("light", {"targetname": 'bad"value'})
        with self.assertRaises(ValueError):
            e.to_map()

    def test_to_map_rejects_newline_in_field_value(self):
        e = Entity("light", {"targetname": "bad\nvalue"})
        with self.assertRaises(ValueError):
            e.to_map()

    def test_translated_shifts_origin_field(self):
        e = Entity("light", {"origin": "1 2 3"}).translated(10, 20, 30)
        self.assertEqual(e.fields["origin"], "11 22 33")

    def test_translated_rejects_malformed_origin(self):
        with self.assertRaises(ValueError):
            Entity("light", {"origin": "1 2"}).translated(1, 1, 1)

    def test_rotated_z_rotates_origin_and_angle(self):
        e = Entity("info_player_start", {"origin": "1 0 5", "angle": "0"}).rotated_z(90)
        self.assertEqual(e.fields["origin"], "0 1 5")
        self.assertEqual(e.fields["angle"], "90")

    def test_rotated_z_preserves_up_down_angle_sentinels(self):
        # Quake's angle=-1/-2 mean "straight up"/"straight down", not a yaw
        # value — a Z-axis rotation must leave them untouched.
        up = Entity("light", {"origin": "0 0 0", "angle": "-1"}).rotated_z(45)
        down = Entity("light", {"origin": "0 0 0", "angle": "-2"}).rotated_z(45)
        self.assertEqual(up.fields["angle"], "-1")
        self.assertEqual(down.fields["angle"], "-2")

    def test_rotated_z_rotates_brushes(self):
        brush = Brush([Face((1, 0, 0), (2, 0, 0), (1, 1, 0), "t")])
        e = Entity("func_detail", {}, [brush]).rotated_z(90)
        self.assertEqual(e.brushes[0].faces[0].p1, (0, 1, 0))

    def test_rotated_z_wraps_angle_into_0_360(self):
        e = Entity("info_teleport_destination", {"origin": "0 0 0", "angle": "350"})
        rotated = e.rotated_z(20)
        self.assertEqual(rotated.fields["angle"], "10")

    def test_rotated_z_wraps_mangle_yaw_into_0_360(self):
        e = Entity("info_intermission", {"origin": "0 0 0", "mangle": "-10 350 0"})
        rotated = e.rotated_z(20)
        pitch, yaw, roll = rotated.fields["mangle"].split()
        self.assertEqual(yaw, "10")
        self.assertEqual(pitch, "-10")
        self.assertEqual(roll, "0")


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
