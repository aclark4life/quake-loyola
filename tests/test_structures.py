"""Tests for validation/edge-case branches in geometry/structures.py not
already exercised by tests/test_geometry.py's happy-path coverage:
degenerate-input guards, and the recess/base-cap/tf-frame-texture branches
of the higher-level wall/arch builders."""

import unittest

from quake_loyola.geometry import (
    arch_fill,
    arch_fill_y,
    arch_wall,
    gable_slats,
    layered_wall,
    layered_wall_y,
    square_wall,
)
from quake_loyola.mapdata import Brush


class ArchFillTests(unittest.TestCase):
    def test_rejects_non_positive_segs(self):
        with self.assertRaises(ValueError):
            arch_fill(0, 10, 0, 0, 20, 0, "tex")

    def test_builds_brushes_for_valid_input(self):
        brushes = arch_fill(0, 10, 0, 0, 20, 4, "tex")
        self.assertTrue(brushes)
        self.assertTrue(all(isinstance(b, Brush) for b in brushes))

    def test_arch_fill_y_swaps_axes_and_builds(self):
        brushes = arch_fill_y(0, 10, 0, 0, 20, 4, "tex")
        self.assertTrue(brushes)


class GableSlatsTests(unittest.TestCase):
    def test_rejects_non_positive_n(self):
        with self.assertRaises(ValueError):
            gable_slats(0, 100, 50, 0, 100, 4, 0, 20, "tex", n=0)

    def test_rejects_ridge_equal_to_eave_plus_slab(self):
        with self.assertRaises(ValueError):
            gable_slats(0, 100, 50, 0, 4, 4, 0, 20, "tex")

    def test_builds_slats_for_valid_gable(self):
        slats = gable_slats(0, 100, 50, 0, 100, 4, 0, 20, "tex")
        self.assertTrue(slats)


class LayeredWallTests(unittest.TestCase):
    def test_clamps_opening_outside_wall_bounds(self):
        # Opening entirely outside the wall footprint should be dropped
        # rather than producing an inverted/degenerate sub-brush.
        brushes = layered_wall(0, 0, 0, 100, 10, 100, [(200, 200, 300, 300)], "tex")
        self.assertTrue(brushes)

    def test_frame_texture_applied_at_opening_edges(self):
        # A single centered opening should trigger every tf-edge branch
        # (east/west/bottom/top) in the frame-texture pass.
        brushes = layered_wall(
            0, 0, 0, 100, 10, 100, [(30, 30, 70, 70)], "tex", tf="frame_tex"
        )
        self.assertTrue(brushes)
        frame_faces = [f for b in brushes for f in b.faces if f.tex == "frame_tex"]
        self.assertTrue(frame_faces, "expected at least one tf-textured face")

    def test_layered_wall_y_builds(self):
        brushes = layered_wall_y(0, 0, 0, 100, 10, 100, [(30, 30, 70, 70)], "tex")
        self.assertTrue(brushes)


class SquareWallRecessTests(unittest.TestCase):
    def test_builds_with_recess_opening(self):
        brushes = square_wall(
            0,
            100,
            -50,
            50,
            0,
            100,
            20,
            "tex",
            overhang=10,
            recess=(10, 4, "recess_tex"),
        )
        self.assertTrue(brushes)
        recess_faces = [f for b in brushes for f in b.faces if f.tex == "recess_tex"]
        self.assertTrue(recess_faces)

    def test_builds_with_base_ramp_and_cap(self):
        brushes = square_wall(
            0,
            100,
            -50,
            50,
            0,
            100,
            20,
            "tex",
            base_ramp=(0, 10),
            base_cap_h=4,
            base_cap_tex="cap_tex",
        )
        cap_faces = [f for b in brushes for f in b.faces if f.tex == "cap_tex"]
        self.assertTrue(cap_faces)

    def test_builds_with_base_h_and_cap_explicit_y(self):
        brushes = square_wall(
            0,
            100,
            -50,
            50,
            0,
            100,
            20,
            "tex",
            base_h=10,
            base_cap_h=4,
            base_cap_y1=-40,
            base_cap_y2=40,
        )
        self.assertTrue(brushes)


class ArchWallRecessAndCapTests(unittest.TestCase):
    def test_rejects_non_positive_segs(self):
        with self.assertRaises(ValueError):
            arch_wall(0, 100, -50, 50, 0, 100, 10, 20, 0, "tex")

    def test_builds_with_recess(self):
        brushes = arch_wall(
            0, 100, -50, 50, 0, 100, 10, 20, 4, "tex", recess=(10, 4, "recess_tex")
        )
        recess_faces = [f for b in brushes for f in b.faces if f.tex == "recess_tex"]
        self.assertTrue(recess_faces)

    def test_builds_with_base_ramp_and_cap(self):
        brushes = arch_wall(
            0,
            100,
            -50,
            50,
            0,
            100,
            10,
            20,
            4,
            "tex",
            base_ramp=(0, 10),
            base_cap_h=4,
            base_cap_tex="cap_tex",
        )
        cap_faces = [f for b in brushes for f in b.faces if f.tex == "cap_tex"]
        self.assertTrue(cap_faces)

    def test_builds_with_base_h_and_cap(self):
        brushes = arch_wall(
            0,
            100,
            -50,
            50,
            0,
            100,
            10,
            20,
            4,
            "tex",
            base_h=10,
            base_cap_h=4,
            base_cap_tex="cap_tex",
        )
        self.assertTrue(brushes)

    def test_pillars_filled_when_not_freestanding_and_close_radii(self):
        # rout < rin * sqrt(2) with freestanding=False triggers the extra
        # corner-fill pillar boxes.
        brushes = arch_wall(0, 100, -50, 50, 0, 100, 18, 20, 4, "tex")
        self.assertTrue(brushes)


if __name__ == "__main__":
    unittest.main()
