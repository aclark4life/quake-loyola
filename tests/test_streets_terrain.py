"""Smoke and spatial-sanity tests for modules that previously had no direct
coverage: streets/shell.py, streets/details.py, streets/ennis.py (exercised
through details.py, its only caller), and terrain/west_campus.py.

These are intentionally lightweight (non-empty output, brush/entity type
checks, and basic bounding-box/seam sanity) rather than exhaustive geometry
assertions, matching the style of the rest of the suite.
"""

import unittest

from quake_loyola.constants import (
    CHARLES_CROSSWALK_LEN,
    CHARLES_CROSSWALK_STRIPE_W,
    ENNIS_PULL_S,
    ENNIS_SW_EDGE,
    WALL_T,
    WORLD_Y2,
)
from quake_loyola.constants.textures import Textures
from quake_loyola.mapdata import Brush, Entity
from quake_loyola.streets import details, ennis, shell
from quake_loyola.terrain import knott_hall as knott_terrain
from quake_loyola.terrain import ne, west_campus
from quake_loyola.terrain._mesh_helpers import append_sampled_grid_mesh


class StreetWorldShellTests(unittest.TestCase):
    def test_build_returns_brushes_and_entities(self):
        brushes, entities = shell._build_street_world_shell()
        self.assertTrue(brushes)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))
        self.assertTrue(all(isinstance(e, Entity) for e in entities))

    def test_world_seal_returns_six_brushes(self):
        seal = shell._build_world_seal()
        self.assertEqual(len(seal), 6)
        self.assertTrue(all(isinstance(b, Brush) for b in seal))


class StreetDetailsTests(unittest.TestCase):
    def test_build_street_details_extends_shell_output(self):
        base_brushes, base_entities = shell._build_street_world_shell()
        brushes, entities = details._build_street_details(
            list(base_brushes), list(base_entities)
        )
        self.assertGreaterEqual(len(brushes), len(base_brushes))
        self.assertGreater(len(entities), len(base_entities))
        # Ennis Ave entrance features are built as part of street details
        # (streets/ennis.py has no build() of its own and is only called
        # from here), so a non-trivial entity count also exercises it.
        self.assertTrue(
            any(e.classname == "func_detail" for e in entities),
            "expected at least one func_detail entity from street details",
        )


class WestCampusTerrainTests(unittest.TestCase):
    def test_build_returns_brushes_with_no_entities(self):
        brushes, entities = west_campus.build()
        self.assertTrue(brushes)
        self.assertEqual(entities, [])
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_terrain_z_matches_quad_corner_samples(self):
        # Spot-check that terrain_z() reproduces the raw sampled grid corner
        # values exactly (bilinear interpolation at a grid vertex should
        # return that vertex's own value, not merely a float).
        expected = {
            (west_campus._wct_x[0], west_campus.wct_y[0]): west_campus._wct_cols[0][0],
            (west_campus._wct_x[0], west_campus.wct_y[-1]): west_campus._wct_cols[0][
                -1
            ],
            (west_campus._wct_x[-1], west_campus.wct_y[0]): west_campus._wct_cols[-1][
                0
            ],
            (west_campus._wct_x[-1], west_campus.wct_y[-1]): west_campus._wct_cols[-1][
                -1
            ],
        }
        for (x, y), expected_z in expected.items():
            z = west_campus.terrain_z(x, y)
            self.assertIsInstance(z, float)
            self.assertAlmostEqual(z, expected_z)


class StreetDetailLayoutTests(unittest.TestCase):
    def test_lane_boundaries_are_ordered_west_to_east(self):
        # A sign error here (e.g. swapping road_cx +/- STREET_DIV_HW) would
        # still let details._build_street_details() run without raising,
        # but would silently overlap or invert travel lanes. Assert the
        # full west-to-east ordering of the road's cross-section instead.
        layout = details._make_street_detail_layout()
        from quake_loyola.constants.derived import ROAD_X1, ROAD_X2
        from quake_loyola.constants.streets import STREET_DIV_HW, STREET_DIV_LINE_HW

        ordered = [
            ROAD_X1,
            layout["west_lane_line_x"] - STREET_DIV_LINE_HW,
            layout["west_lane_line_x"] + STREET_DIV_LINE_HW,
            layout["road_cx"] - STREET_DIV_HW,
            layout["road_cx"],
            layout["road_cx"] + STREET_DIV_HW,
            layout["east_lane_line_x"] - STREET_DIV_LINE_HW,
            layout["east_lane_line_x"] + STREET_DIV_LINE_HW,
            ROAD_X2,
        ]
        for a, b in zip(ordered, ordered[1:], strict=False):
            self.assertLess(a, b, f"street cross-section out of order: {ordered}")

    def test_lane_lines_are_broken_into_dashes(self):
        from quake_loyola.constants.streets import (
            STREET_DIV_LINE_HW,
            STREET_LANE_DASH_GAP,
            STREET_LANE_DASH_LEN,
            STREET_LANE_DASH_MIN,
        )

        layout = details._make_street_detail_layout()
        brushes = []
        details._append_charles_marking_brushes(brushes, layout)

        for lane_line_x in (layout["west_lane_line_x"], layout["east_lane_line_x"]):
            runs = self._runs_in_stripe_slot(brushes, lane_line_x, STREET_DIV_LINE_HW)
            dashes = [(y1, y2) for y1, y2, painted in runs if painted]
            gaps = [(y1, y2) for y1, y2, painted in runs if not painted]
            self.assertGreater(len(dashes), 5, "lane line is not broken up")
            self.assertGreater(len(gaps), 5, "lane line has no gaps between dashes")

            for y1, y2 in dashes:
                self.assertLessEqual(y2 - y1, STREET_LANE_DASH_LEN)
                self.assertGreaterEqual(
                    y2 - y1, STREET_LANE_DASH_MIN, "dash left as a stub"
                )
            # Every gap is a full dash gap except where the pattern is cut off:
            # the crossing and the street's own ends chop it mid-cycle, and a
            # dash clipped below STREET_LANE_DASH_MIN is dropped rather than
            # left as a stub, which shortens or lengthens the abutting gap.
            seg_bounds = {
                layout["charles_y1"],
                layout["charles_crossing_y1"],
                layout["charles_crossing_y2"],
                layout["charles_y2"],
            }
            for y1, y2 in gaps:
                if y1 in seg_bounds or y2 in seg_bounds:
                    self.assertLess(
                        y2 - y1, STREET_LANE_DASH_GAP + STREET_LANE_DASH_MIN
                    )
                    continue
                self.assertAlmostEqual(y2 - y1, STREET_LANE_DASH_GAP, places=3)

    def test_lane_line_slot_is_painted_end_to_end(self):
        # The road surface is carved away for the stripe's full length, so any
        # stretch the markings don't paint is a slot straight through to the
        # void. Only the pedestrian crossing may be left to another builder.
        from quake_loyola.constants.streets import STREET_DIV_LINE_HW

        layout = details._make_street_detail_layout()
        brushes = []
        details._append_charles_marking_brushes(brushes, layout)

        for lane_line_x in (layout["west_lane_line_x"], layout["east_lane_line_x"]):
            runs = self._runs_in_stripe_slot(brushes, lane_line_x, STREET_DIV_LINE_HW)
            self.assertEqual(runs[0][0], layout["charles_y1"])
            self.assertEqual(runs[-1][1], layout["charles_y2"])
            holes = [
                (a[1], b[0])
                for a, b in zip(runs, runs[1:], strict=False)
                if b[0] - a[1] > 1e-6
            ]
            self.assertEqual(
                holes,
                [(layout["charles_crossing_y1"], layout["charles_crossing_y2"])],
                "unpainted stretch of lane-line slot outside the crossing",
            )

    def test_both_lane_lines_keep_their_dashes_abreast(self):
        from quake_loyola.constants.streets import STREET_DIV_LINE_HW

        layout = details._make_street_detail_layout()
        brushes = []
        details._append_charles_marking_brushes(brushes, layout)
        west, east = (
            [
                (y1, y2)
                for y1, y2, painted in self._runs_in_stripe_slot(
                    brushes, x, STREET_DIV_LINE_HW
                )
                if painted
            ]
            for x in (layout["west_lane_line_x"], layout["east_lane_line_x"])
        )
        self.assertEqual(west, east)

    @staticmethod
    def _runs_in_stripe_slot(brushes, line_x, line_hw):
        """Return this stripe slot's (y1, y2, is_painted) runs, south to north."""
        runs = []
        for b in brushes:
            (x1, y1, _), (x2, y2, _) = b.get_bbox()
            if abs(x1 - (line_x - line_hw)) > 1e-6:
                continue
            if abs(x2 - (line_x + line_hw)) > 1e-6:
                continue
            painted = any(f.tex == Textures.PARKING_STRIPE for f in b.faces)
            runs.append((y1, y2, painted))
        return sorted(runs)

    def test_charles_crossing_sits_within_charles_span(self):
        layout = details._make_street_detail_layout()
        self.assertLess(layout["charles_y1"], layout["charles_crossing_y1"])
        self.assertLess(layout["charles_crossing_y1"], layout["charles_crossing_y2"])
        self.assertLess(layout["charles_crossing_y2"], layout["charles_y2"])

    def test_charles_crossing_stops_short_of_the_ennis_carriageway(self):
        # Ennis Rd paves its carriageway clear across Charles St at the same z
        # as the road markings, so a crossing stripe that reaches past the
        # Ennis south curb ends up coplanar with it and z-fights a crosswalk
        # stripe into the middle of the junction. Guard the band as a whole and
        # every stripe the stepped band actually emits.
        from quake_loyola.constants.derived import ENNIS_HW, ENNIS_Y

        junction_y = ENNIS_Y - ENNIS_HW
        layout = details._make_street_detail_layout()
        self.assertLessEqual(layout["charles_crossing_y2"], junction_y)
        self.assertLessEqual(layout["charles_crossing_north_w"], junction_y)

        dash_brushes = []
        details._append_charles_marking_brushes(dash_brushes, layout)
        stripes = [
            b
            for b in dash_brushes
            if any(f.tex == Textures.PARKING_STRIPE for f in b.faces)
        ]
        self.assertTrue(stripes)
        crossing_stripes = 0
        for brush in stripes:
            pts = [p for f in brush.faces for p in (f.p1, f.p2, f.p3)]
            xs = [p[0] for p in pts]
            if max(xs) - min(xs) != CHARLES_CROSSWALK_STRIPE_W:
                continue  # lane divider running the length of the street
            crossing_stripes += 1
            self.assertLessEqual(max(p[1] for p in pts), junction_y)
        self.assertGreater(crossing_stripes, 1)

    def test_charles_crossing_west_stripe_lands_in_the_lowered_entrance(self):
        # The point of stepping the band is that its west end lines up with
        # the lowered sidewalk entrance opposite it.
        layout = details._make_street_detail_layout()
        cut_y1, cut_y2 = layout["charles_crossing_mid"], layout["charles_curb_cut_y2"]
        stripe_y2 = layout["charles_crossing_north_w"]
        stripe_y1 = stripe_y2 - CHARLES_CROSSWALK_LEN
        self.assertLessEqual(cut_y1, stripe_y1)
        self.assertLessEqual(stripe_y2, cut_y2)

    def test_ennis_road_surfaces_begin_at_the_east_edge_of_charles(self):
        # Ennis Rd tees into Charles St rather than crossing it, so it has no
        # carriageway west of the Charles east kerb line.
        from quake_loyola.constants.derived import ROAD_X2

        layout = details._make_street_detail_layout()
        self.assertEqual(layout["ennis_x1"], ROAD_X2)

        brushes = []
        details._append_ennis_road_surfaces(brushes, layout)
        self.assertTrue(brushes)
        for b in brushes:
            (x1, _, _), _ = b.get_bbox()
            self.assertGreaterEqual(
                x1,
                ROAD_X2,
                "Ennis road surface reaches west of the Charles east kerb",
            )

    def test_the_charles_ennis_junction_is_paved_exactly_once(self):
        # Both streets used to pave the junction, coplanar and at the same z.
        # The Ennis surface is laid at 90 degrees to the Charles one, and it
        # won, so Charles visibly changed texture direction for the length of
        # the junction. Whichever won, two coincident surfaces z-fight.
        from quake_loyola.constants import ENNIS_WIDEN_N
        from quake_loyola.constants.derived import (
            ENNIS_HW,
            ENNIS_Y,
            ROAD_X1,
            ROAD_X2,
        )

        layout = details._make_street_detail_layout()
        surfaces = []
        details._append_charles_road_surfaces(surfaces, layout)
        details._append_ennis_road_surfaces(surfaces, layout)

        boxes = [b.get_bbox() for b in surfaces]
        south, north = ENNIS_Y - ENNIS_HW, ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N
        checked = 0
        for x in range(int(ROAD_X1) + 20, int(ROAD_X2), 100):
            for y in range(int(south) + 20, int(north), 60):
                covering = sum(
                    1
                    for (bx1, by1, _), (bx2, by2, _) in boxes
                    if bx1 <= x <= bx2 and by1 <= y <= by2
                )
                self.assertEqual(
                    covering,
                    1,
                    f"({x}, {y}) in the junction is paved by {covering} road "
                    f"surfaces; expected exactly one",
                )
                checked += 1
        self.assertGreater(checked, 20)


class StreetShellBoundsTests(unittest.TestCase):
    def test_shell_brushes_stay_within_world_bounds(self):
        # Regression guard for the world-edge seam: street-shell geometry
        # must not extend past the world seal, or it would poke through
        # (or leave a gap at) the map boundary.
        from quake_loyola.constants.derived import (
            WORLD_X1,
            WORLD_X2_EXT,
            WORLD_Y1,
            WORLD_Y2,
        )

        brushes, _ = shell._build_street_world_shell()
        margin = 1.0
        for b in brushes:
            (x1, y1, _), (x2, y2, _) = b.get_bbox()
            self.assertGreaterEqual(x1, WORLD_X1 - margin)
            self.assertLessEqual(x2, WORLD_X2_EXT + margin)
            self.assertGreaterEqual(y1, WORLD_Y1 - margin)
            self.assertLessEqual(y2, WORLD_Y2 + margin)


class EnnisPullSouthTests(unittest.TestCase):
    """ENNIS_PULL_S drags Ennis Rd — and the northeast terrain grid and the
    masonry entrance wall with it — south to tighten the gap between Knott
    Hall and Ennis. The world's north boundary stays put, so the iron fence
    run north of the wall grows by the same amount.
    """

    def test_the_gap_to_knott_shrinks_by_the_pull(self):
        self.assertEqual(ENNIS_SW_EDGE - knott_terrain.KH_Y2, 800 - ENNIS_PULL_S)

    def test_the_northeast_grid_rows_stay_in_order(self):
        # Pulling Ennis south slides the five southern rows toward the ones
        # that stay at their surveyed positions. Let them cross and the mesh
        # winds backwards, which tri_ramp_prism rejects.
        for lo, hi in zip(ne._ne_y, ne._ne_y[1:], strict=False):
            self.assertLess(lo, hi, f"northeast grid rows out of order: {ne._ne_y}")

    def test_the_entrance_fence_still_reaches_the_world_boundary(self):
        brushes, _ = ennis._build_ennis_entrance_features()
        fence = [b.get_bbox() for b in brushes if b.faces[0].tex == Textures.FENCE]
        self.assertTrue(fence)
        self.assertEqual(max(maxs[1] for _, maxs in fence), WORLD_Y2 - WALL_T)

    """The sampled height grids must tile their domain exactly.

    Rows used to be stretched a few units past their own boundary to hide
    seams that the exact tiling means never existed. Overlapping rows
    interpenetrate, and those intersections produce BSP slivers that qbsp's
    outside fill can mark solid — a wall of ground from grade to sky, with no
    leak to explain it. These tests pin the invariant that replaced the two
    hand-tuned overlap widths.
    """

    def _assert_every_brush_stays_in_one_cell(self, brushes, x_grid, y_grid):
        xs = sorted(x_grid)
        ys = sorted(y_grid)
        margin = 1e-6
        for b in brushes:
            (bx1, by1, _), (bx2, by2, _) = b.get_bbox()
            cells = [
                (x1, x2, y1, y2)
                for x1, x2 in zip(xs, xs[1:], strict=False)
                for y1, y2 in zip(ys, ys[1:], strict=False)
                if bx1 >= x1 - margin
                and bx2 <= x2 + margin
                and by1 >= y1 - margin
                and by2 <= y2 + margin
            ]
            self.assertTrue(
                cells,
                f"terrain brush {(bx1, by1, bx2, by2)} spans past its own grid "
                f"cell — a row overlap has been reintroduced",
            )

    def test_west_campus_brushes_each_stay_inside_one_grid_cell(self):
        brushes, _ = west_campus.build()
        self.assertTrue(brushes)
        self._assert_every_brush_stays_in_one_cell(
            brushes, west_campus._wct_x, west_campus.wct_y
        )

    def test_northeast_brushes_each_stay_inside_one_grid_cell(self):
        brushes, _ = ne.build()
        self.assertTrue(brushes)
        self._assert_every_brush_stays_in_one_cell(brushes, ne._ne_x, ne._ne_y)

    def test_mesh_helper_never_emits_a_cell_outside_its_own_interval(self):
        # Drive the helper directly with a sloped synthetic grid, so the
        # invariant is pinned to the helper rather than to either grid's data.
        x_grid = [0, 100, 200]
        y_grid = [0, 100, 200, 300]
        cols = [[0, 10, 20, 30], [5, 15, 25, 35], [40, 30, 20, 10]]
        cells = []

        def record(x1, x2, y1, y2, *_corners_and_texture):
            cells.append((x1, x2, y1, y2))
            return []

        append_sampled_grid_mesh(
            [],
            x_grid,
            y_grid,
            cols,
            texture="t",
            build_cell_brushes=record,
        )

        self.assertEqual(len(cells), (len(x_grid) - 1) * (len(y_grid) - 1))
        for x1, x2, y1, y2 in cells:
            self.assertIn((x1, x2), list(zip(x_grid, x_grid[1:], strict=False)))
            self.assertIn((y1, y2), list(zip(y_grid, y_grid[1:], strict=False)))

    def test_adjacent_cells_read_the_same_height_for_the_edge_they_share(self):
        # This is what makes the mesh watertight without any overlap: the
        # corner heights a cell gets for its far edge must be bit-identical to
        # the ones its neighbour gets for its near edge. Re-projecting either
        # along a row's slope (the old overlap behaviour) breaks it.
        x_grid = [0, 100, 200]
        y_grid = [0, 100, 200, 300]
        cols = [[0, 10, 20, 30], [5, 15, 25, 35], [40, 30, 20, 10]]
        corners = {}

        def record(x1, _x2, y1, _y2, z_nw, z_sw, z_ne, z_se, _texture):
            corners[(x1, y1)] = (z_nw, z_sw, z_ne, z_se)
            return []

        append_sampled_grid_mesh(
            [], x_grid, y_grid, cols, texture="t", build_cell_brushes=record
        )

        for (x1, y1), (_z_nw, z_sw, z_ne, z_se) in corners.items():
            south = corners.get((x1, y1 + 100))
            if south is not None:
                self.assertEqual((z_sw, z_se), (south[0], south[2]))
            east = corners.get((x1 + 100, y1))
            if east is not None:
                self.assertEqual((z_ne, z_se), (east[0], east[1]))


if __name__ == "__main__":
    unittest.main()
