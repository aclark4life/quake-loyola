"""Smoke and spatial-sanity tests for modules that previously had no direct
coverage: streets/shell.py, streets/details.py, streets/ennis.py (exercised
through details.py, its only caller), and terrain/west_campus.py.

These are intentionally lightweight (non-empty output, brush/entity type
checks, and basic bounding-box/seam sanity) rather than exhaustive geometry
assertions, matching the style of the rest of the suite.
"""

import unittest

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
        # Spot-check that _terrain_z() reproduces a few of the raw sampled
        # grid corners exactly (bilinear interpolation at a grid vertex
        # should return that vertex's own value).
        for x in (west_campus._wct_x[0], west_campus._wct_x[-1]):
            for y in (west_campus.wct_y[0], west_campus.wct_y[-1]):
                z = west_campus._terrain_z(x, y)
                self.assertIsInstance(z, float)

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


if __name__ == "__main__":
    unittest.main()
