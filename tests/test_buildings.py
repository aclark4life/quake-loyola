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


class FloorLevelTests(unittest.TestCase):
    def test_decks_stack_one_storey_apart_from_the_base(self):
        levels = list(buildings.floor_levels(221, 192, 5))
        self.assertEqual(
            levels, [(1, 221 + 192), (2, 221 + 384), (3, 221 + 576), (4, 221 + 768)]
        )

    def test_the_ground_deck_is_skipped_by_default(self):
        # Storey 0's deck is base_z itself -- already terrain or a foundation
        # slab -- so plating it again would z-fight.
        indices = [i for i, _ in buildings.floor_levels(0, 128, 3)]
        self.assertEqual(indices, [1, 2])
        self.assertNotIn(0, indices)

    def test_start_floor_zero_includes_the_ground_for_stairwell(self):
        levels = list(buildings.floor_levels(0, 128, 3, start_floor=0))
        self.assertEqual(levels, [(0, 0), (1, 128), (2, 256)])

    def test_the_roof_line_is_never_yielded(self):
        # floors=3 means decks 0,1,2 and a roof at 3*floor_h; the roof belongs
        # to the roof builder, not to the floor stack.
        zs = [z for _, z in buildings.floor_levels(0, 128, 3, start_floor=0)]
        self.assertNotIn(3 * 128, zs)

    def test_decks_are_not_the_window_band(self):
        # Regression guard: floor_window_levels() is inset within the storey,
        # so using it to place a slab would float the deck mid-storey.
        deck = dict(buildings.floor_levels(0, 128, 3, start_floor=0))
        for floor_index, zb, _zt in buildings.floor_window_levels(0, 128, 3, 44):
            self.assertNotEqual(deck[floor_index], zb)

    def test_a_non_positive_storey_height_is_rejected(self):
        with self.assertRaises(ValueError):
            list(buildings.floor_levels(0, 0, 3))


class FloorPlateTests(unittest.TestCase):
    def test_a_plate_hangs_below_its_walking_surface(self):
        (brush,) = buildings.floor_plate(0, 0, 256, 256, 400, 16, "tex")
        (_x1, _y1, z1), (_x2, _y2, z2) = brush.get_bbox()
        self.assertEqual((z1, z2), (384, 400))

    def test_one_void_becomes_a_ring_of_four(self):
        pieces = buildings.floor_plate(
            0, 0, 300, 300, 100, 8, "tex", voids=[(100, 100, 200, 200)]
        )
        self.assertEqual(len(pieces), 4)
        for b in pieces:
            (bx1, by1, _), (bx2, by2, _) = b.get_bbox()
            self.assertFalse(
                100 <= bx1 and bx2 <= 200 and 100 <= by1 and by2 <= 200,
                "a brush was emitted inside the void",
            )

    def test_two_voids_are_both_left_open(self):
        voids = [(50, 50, 100, 100), (200, 200, 250, 250)]
        pieces = buildings.floor_plate(0, 0, 300, 300, 100, 8, "tex", voids=voids)
        self.assertTrue(pieces)
        for b in pieces:
            (bx1, by1, _), (bx2, by2, _) = b.get_bbox()
            for vx1, vy1, vx2, vy2 in voids:
                self.assertFalse(
                    vx1 <= bx1 and bx2 <= vx2 and vy1 <= by1 and by2 <= vy2,
                    f"brush {(bx1, by1, bx2, by2)} sits inside void "
                    f"{(vx1, vy1, vx2, vy2)}",
                )

    def test_the_plate_is_covered_exactly_once(self):
        # Area conservation: the emitted cells must tile the plate minus the
        # voids, with no overlap (overlapping deck brushes make BSP slivers).
        voids = [(50, 50, 100, 100), (200, 200, 250, 250)]
        pieces = buildings.floor_plate(0, 0, 300, 300, 100, 8, "tex", voids=voids)
        area = 0
        for b in pieces:
            (bx1, by1, _), (bx2, by2, _) = b.get_bbox()
            area += (bx2 - bx1) * (by2 - by1)
        void_area = sum((vx2 - vx1) * (vy2 - vy1) for vx1, vy1, vx2, vy2 in voids)
        self.assertEqual(area, 300 * 300 - void_area)

    def test_a_void_outside_the_plate_is_dropped(self):
        # A shaft footprint can be handed to every floor without the caller
        # working out which ones it actually crosses.
        pieces = buildings.floor_plate(
            0, 0, 100, 100, 100, 8, "tex", voids=[(500, 500, 600, 600)]
        )
        self.assertEqual(len(pieces), 1)

    def test_a_void_is_clipped_to_the_plate(self):
        pieces = buildings.floor_plate(
            0, 0, 100, 100, 100, 8, "tex", voids=[(50, -50, 150, 50)]
        )
        area = 0
        for b in pieces:
            (bx1, by1, _), (bx2, by2, _) = b.get_bbox()
            area += (bx2 - bx1) * (by2 - by1)
        self.assertEqual(area, 100 * 100 - 50 * 50)

    def test_no_voids_is_a_single_slab(self):
        pieces = buildings.floor_plate(0, 0, 100, 100, 100, 8, "tex")
        self.assertEqual(len(pieces), 1)

    def test_degenerate_and_zero_thickness_plates_are_rejected(self):
        with self.assertRaises(ValueError):
            buildings.floor_plate(0, 0, 0, 100, 100, 8, "tex")
        with self.assertRaises(ValueError):
            buildings.floor_plate(0, 0, 100, 100, 100, 0, "tex")

    def test_a_deck_stack_plates_every_level(self):
        # The two helpers are meant to compose.
        plates = [
            b
            for _i, deck_z in buildings.floor_levels(221, 192, 5)
            for b in buildings.floor_plate(0, 0, 256, 256, deck_z, 16, "tex")
        ]
        self.assertEqual(len(plates), 4)
        tops = sorted(b.get_bbox()[1][2] for b in plates)
        self.assertEqual(tops, [413, 605, 797, 989])


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
