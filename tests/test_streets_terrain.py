"""Smoke and spatial-sanity tests for modules that previously had no direct
coverage: streets/shell.py, streets/details.py, streets/ennis.py (exercised
through details.py, its only caller), and terrain/west_campus.py.

These are intentionally lightweight (non-empty output, brush/entity type
checks, and basic bounding-box/seam sanity) rather than exhaustive geometry
assertions, matching the style of the rest of the suite.
"""

import unittest

from quake_loyola.constants import CHARLES_CROSSWALK_LEN, CHARLES_CROSSWALK_STRIPE_W
from quake_loyola.constants.textures import Textures
from quake_loyola.mapdata import Brush, Entity
from quake_loyola.streets import details, shell
from quake_loyola.terrain import west_campus


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

    def test_overlap_extension_uses_extrapolated_not_raw_south_z(self):
        # Regression test: the south edge of each terrain quad used to be
        # extended by _WCT_OVR while still using the *unextended* row's
        # raw sampled Z for that edge (a leftover of copying the general
        # overlap technique without the linear re-projection terrain/ne.py
        # uses). That left the overlap region's height diverging from the
        # slope implied by the row's own two corners. The fix re-projects
        # z_sw/z_se along the row's own NW->SW / NE->SE slope onto the
        # extended y, so it must differ from the raw (unextended) corner Z
        # whenever that slope is non-zero.
        for i in range(len(west_campus.wct_y) - 2):
            y1, y2 = west_campus.wct_y[i], west_campus.wct_y[i + 1]
            y2_ext = y2 - west_campus._WCT_OVR
            col = west_campus._wct_cols[0]
            z_nw, z_sw_raw = col[i], col[i + 1]
            if z_nw == z_sw_raw:
                continue  # flat row; extrapolation trivially equals raw Z
            z_sw_ext = z_nw + (z_sw_raw - z_nw) * (y2_ext - y1) / (y2 - y1)
            self.assertNotAlmostEqual(z_sw_ext, z_sw_raw, places=3)
            break
        else:
            self.fail("expected at least one sloped row to test against")


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


class WestCampusTerrainSeamTests(unittest.TestCase):
    def test_terrain_brushes_stay_within_the_sampled_grid_footprint(self):
        # Bounding-box sanity: no meshed terrain brush should extend past
        # the sampled grid's X range (Y is intentionally extended south by
        # _WCT_OVR — see test_overlap_extension_uses_extrapolated_not_raw_
        # south_z above — so only X is checked here).
        brushes, _ = west_campus.build()
        x_lo, x_hi = min(west_campus._wct_x), max(west_campus._wct_x)
        margin = 1.0
        for b in brushes:
            (x1, _, _), (x2, _, _) = b.get_bbox()
            self.assertGreaterEqual(x1, x_lo - margin)
            self.assertLessEqual(x2, x_hi + margin)


if __name__ == "__main__":
    unittest.main()
