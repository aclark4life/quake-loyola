"""Tests for quake_loyola.build_presets — the single-source-of-truth name
tuples and validation helpers shared by config.py and cli.py."""

import unittest

from quake_loyola.build_presets import is_valid_fog_density


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


if __name__ == "__main__":
    unittest.main()
