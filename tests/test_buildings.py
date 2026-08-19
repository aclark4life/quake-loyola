import unittest

from quake_loyola.geometry import buildings
from quake_loyola.geometry import entities as buildings_entities
from quake_loyola.geometry.primitives import box


def _BOX(z2=100):
    return box(0, 0, 0, 10, 10, z2, "tex")


def _pts(brush):
    """Return every plane-defining point of a brush."""
    return [p for f in brush.faces for p in (f.p1, f.p2, f.p3)]


class FloorWindowTests(unittest.TestCase):
    def test_levels_center_the_band_in_each_storey(self):
        levels = list(buildings.floor_window_levels(0, 128, 3, 44))
        self.assertEqual(len(levels), 3)
        for floor_index, zb, zt in levels:
            self.assertEqual(zt - zb, 88)
            floor_z = floor_index * 128
            self.assertEqual(zb - floor_z, zt - (floor_z + 128) + 128 - 88)

    def test_start_floor_skips_lower_storeys(self):
        self.assertEqual(
            [
                fl
                for fl, _, _ in buildings.floor_window_levels(
                    0, 128, 3, 44, start_floor=2
                )
            ],
            [2],
        )

    def test_openings_are_centered_on_each_center(self):
        openings = buildings.floor_window_openings([100], 0, 128, 1, 36, 44)
        self.assertEqual(len(openings), 1)
        s1, _, s2, _ = openings[0]
        self.assertEqual((s1, s2), (64, 136))

    def test_double_emits_an_adjacent_pair(self):
        openings = buildings.floor_window_openings([0], 0, 128, 1, 36, 44, double=True)
        self.assertEqual([(o[0], o[2]) for o in openings], [(-72, 0), (0, 72)])

    def test_include_filters_by_center_and_floor(self):
        openings = buildings.floor_window_openings(
            [0, 500], 0, 128, 2, 36, 44, include=lambda c, fl: c > 0 and fl == 1
        )
        self.assertEqual(len(openings), 1)


class WallAndFrameRunTests(unittest.TestCase):
    def test_wall_runs_passes_openings_and_texture_last(self):
        seen = []

        def fake_wall(a, b, openings, tex):
            seen.append((a, b, openings, tex))
            return ["brush"]

        out = buildings.wall_runs([(fake_wall, (1, 2), [("o",)])], "tex")
        self.assertEqual(out, ["brush"])
        self.assertEqual(seen, [(1, 2, [("o",)], "tex")])

    def test_frame_runs_expands_each_opening(self):
        seen = []

        def fake_frame(span1, span2, zb, zt, pos, direction, tex, **kw):
            seen.append((span1, span2, zb, zt, pos, direction, tex, kw))
            return ["f"]

        out = buildings.frame_runs(
            [
                (
                    fake_frame,
                    [(0, 10, 20, 30), (1, 11, 21, 31)],
                    99,
                    -1,
                    {"crossbar": True},
                )
            ],
            "tex",
            fd=16,
            margin=2,
        )
        self.assertEqual(out, ["f", "f"])
        self.assertEqual(seen[0][:6], (0, 20, 10, 30, 99, -1))
        self.assertEqual(seen[0][7], {"fd": 16, "margin": 2, "crossbar": True})


class GableRoofTests(unittest.TestCase):
    def test_gable_roof_returns_two_slabs(self):
        slabs = buildings.gable_roof(0, 50, 100, 0, 100, 200, 300, 16, "roof")
        self.assertEqual(len(slabs), 2)
        for slab in slabs:
            self.assertTrue(slab.faces)

    def test_halves_meet_at_the_ridge(self):
        west = buildings.gable_roof_west_half(0, 50, 0, 100, 200, 300, 16, "roof")
        east = buildings.gable_roof_east_half(50, 100, 0, 100, 200, 300, 216, "roof")
        west_zs = {p[2] for p in _pts(west)}
        east_zs = {p[2] for p in _pts(east)}
        self.assertIn(300, west_zs)
        self.assertIn(300, east_zs)


class ChimneyAndGrilleTests(unittest.TestCase):
    def test_chimney_stack_is_four_walls_around_an_open_flue(self):
        walls = buildings.chimney_stack(-10, -10, 10, 10, 0, 100, 4, "brick")
        self.assertEqual(len(walls), 4)
        xs = [p[0] for w in walls for p in _pts(w)]
        self.assertEqual((min(xs), max(xs)), (-14, 14))

    def test_transom_grille_has_two_beams_plus_mullions(self):
        brushes = buildings.transom_grille_ywall(
            0, 8, -48, 48, 100, 200, "gable", mullions=5
        )
        self.assertEqual(len(brushes), 7)


class StairTests(unittest.TestCase):
    def test_straight_stair_x_ascends_eastward(self):
        steps = buildings.straight_stair_x(0, 0, 10, 0, 16, 4, 16, 32, "ground")
        self.assertEqual(len(steps), 4)
        tops = [max(p[2] for p in _pts(s)) for s in steps]
        self.assertEqual(tops, [16, 32, 48, 64])
        bottoms = {min(p[2] for p in _pts(s)) for s in steps}
        self.assertEqual(bottoms, {0})

    def test_straight_stair_x_descends_on_a_negative_rise(self):
        steps = buildings.straight_stair_x(0, 0, 10, -16, 48, 4, -16, 32, "ground")
        tops = [max(p[2] for p in _pts(s)) for s in steps]
        self.assertEqual(tops, [48, 32, 16, 0])
        bottoms = {min(p[2] for p in _pts(s)) for s in steps}
        self.assertEqual(bottoms, {-16})

    def test_straight_stair_y_is_the_x_run_rotated(self):
        steps = buildings.straight_stair_y(0, 10, 0, -16, 48, 4, -16, 32, "ground")
        tops = [max(p[2] for p in _pts(s)) for s in steps]
        self.assertEqual(tops, [48, 32, 16, 0])
        runs = [(min(p[1] for p in _pts(s)), max(p[1] for p in _pts(s))) for s in steps]
        self.assertEqual(runs, [(0, 32), (32, 64), (64, 96), (96, 128)])
        for s in steps:
            self.assertEqual(min(p[0] for p in _pts(s)), 0)
            self.assertEqual(max(p[0] for p in _pts(s)), 10)


if __name__ == "__main__":
    unittest.main()


class TeleportPadTests(unittest.TestCase):
    def test_pairs_a_trigger_with_a_glow(self):
        brush = _BOX()
        pad = buildings_entities.teleport_pad([brush], "dest_x")
        self.assertEqual(
            [e.classname for e in pad], ["trigger_teleport", "func_illusionary"]
        )
        self.assertEqual(pad[0].fields["target"], "dest_x")

    def test_glow_defaults_to_the_trigger_brushes(self):
        brush = _BOX()
        trigger, glow = buildings_entities.teleport_pad([brush], "dest_x")
        self.assertEqual(trigger.brushes, glow.brushes)

    def test_separate_glow_brushes_are_used_for_the_illusionary_only(self):
        trigger_brush, glow_brush = _BOX(), _BOX(z2=200)
        trigger, glow = buildings_entities.teleport_pad(
            [trigger_brush], "dest_x", [glow_brush]
        )
        self.assertEqual(trigger.brushes, [trigger_brush])
        self.assertEqual(glow.brushes, [glow_brush])

    def test_accepts_a_bare_brush(self):
        pad = buildings_entities.teleport_pad(_BOX(), "dest_x")
        self.assertEqual(len(pad[0].brushes), 1)


class PathLoopTests(unittest.TestCase):
    def test_corners_are_numbered_from_one_and_form_a_closed_ring(self):
        corners = buildings_entities.path_loop(
            "cs_pc", [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
        )
        self.assertEqual(
            [c.fields["targetname"] for c in corners], ["cs_pc1", "cs_pc2", "cs_pc3"]
        )
        self.assertEqual(
            [c.fields["target"] for c in corners], ["cs_pc2", "cs_pc3", "cs_pc1"]
        )
        self.assertTrue(all(c.classname == "path_corner" for c in corners))

    def test_origins_are_serialized_in_order(self):
        corners = buildings_entities.path_loop("p", [(1, 2, 3), (4, 5, 6)])
        self.assertEqual([c.fields["origin"] for c in corners], ["1 2 3", "4 5 6"])

    def test_single_corner_targets_itself(self):
        (corner,) = buildings_entities.path_loop("p", [(0, 0, 0)])
        self.assertEqual(corner.fields["target"], "p1")

    def test_empty_points_raises(self):
        with self.assertRaises(ValueError):
            buildings_entities.path_loop("p", [])
