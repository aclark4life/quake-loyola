"""Tests for quake_loyola.build_presets — the single-source-of-truth name
tuples and validation helpers shared by config.py and cli.py."""

import unittest

from quake_loyola.build_presets import is_valid_fog_density, is_valid_sky_preset


class IsValidFogDensityTests(unittest.TestCase):
    def test_default_is_valid(self):
        self.assertTrue(is_valid_fog_density("default"))

    def test_named_preset_is_valid(self):
        self.assertTrue(is_valid_fog_density("low"))

    def test_custom_finite_nonnegative_float_is_valid(self):
        self.assertTrue(is_valid_fog_density("0.05"))
        self.assertTrue(is_valid_fog_density("0"))

    def test_non_numeric_string_is_invalid(self):
        self.assertFalse(is_valid_fog_density("extreme"))

    def test_negative_number_is_invalid(self):
        self.assertFalse(is_valid_fog_density("-1"))

    def test_nan_and_inf_are_invalid(self):
        self.assertFalse(is_valid_fog_density("nan"))
        self.assertFalse(is_valid_fog_density("inf"))


class IsValidSkyPresetTests(unittest.TestCase):
    def test_named_presets_are_valid(self):
        self.assertTrue(is_valid_sky_preset("day"))
        self.assertTrue(is_valid_sky_preset("night"))

    def test_raw_wad2_texture_name_is_valid(self):
        # Any texture from any loaded WAD can be tried without a formal
        # named preset for it.
        self.assertTrue(is_valid_sky_preset("sky_z1"))
        self.assertTrue(is_valid_sky_preset("sky3_1"))

    def test_empty_string_is_invalid(self):
        self.assertFalse(is_valid_sky_preset(""))

    def test_name_over_15_chars_is_invalid(self):
        # WAD2 texture names are limited to 15 chars (16-byte field minus NUL).
        self.assertFalse(is_valid_sky_preset("a" * 16))

    def test_name_with_illegal_characters_is_invalid(self):
        self.assertFalse(is_valid_sky_preset("not a texture"))
        self.assertFalse(is_valid_sky_preset("sky/z1"))


if __name__ == "__main__":
    unittest.main()
