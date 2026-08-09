"""Tests for quake_loyola.constants.lighting — worldspawn lighting fields."""

import unittest

from quake_loyola.constants.lighting import LIGHTING_PRESETS, LightingPreset


class SunlightMangleTests(unittest.TestCase):
    """``_sunlight_mangle`` names the direction the sunlight *travels*.

    A sun at elevation E above the horizon shines downward, so the mangle
    pitch must be -E. Emitting +E aims the sun up at the sky, every trace to
    the sun escapes without lighting anything, and the whole map ends up lit
    by ``_minlight`` alone.
    """

    def test_pitch_is_negated_elevation(self):
        preset = LightingPreset(
            ambient="10",
            sunlight="200",
            sunlight_color="255 255 255",
            sunlight_dir="35 -180",
            sunlight_penumbra="10",
            fog="0 0 0 0",
        )
        self.assertEqual(preset.to_worldspawn()["_sunlight_mangle"], "-180 -35 0")

    def test_every_preset_points_the_sun_below_the_horizon(self):
        for name, preset in LIGHTING_PRESETS.items():
            with self.subTest(preset=name):
                _yaw, pitch, _roll = preset.to_worldspawn()["_sunlight_mangle"].split()
                self.assertLessEqual(
                    float(pitch),
                    0.0,
                    f"{name} aims the sun upward — the map would be minlight only",
                )
