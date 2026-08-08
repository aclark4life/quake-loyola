"""Tests for quake_loyola.build_presets — the single-source-of-truth name
tuples and validation helpers shared by config.py and cli.py."""

import pathlib
import tempfile
import unittest

from quake_loyola.build_presets import is_valid_fog_density, is_valid_sky
from quake_loyola.wads import sky_texture_names


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


class IsValidSkyTests(unittest.TestCase):
    """`sky` is a plain WAD2 texture name, not a named preset."""

    def test_sky_texture_names_are_valid(self):
        self.assertTrue(is_valid_sky("sky4"))
        self.assertTrue(is_valid_sky("sky_z1"))
        self.assertTrue(is_valid_sky("sky3_1"))

    def test_retired_preset_names_are_no_longer_valid(self):
        # "day"/"night" were the old sky_preset aliases; they aren't texture
        # names, so they must be rejected now (ql.toml files using them are
        # migrated by config._migrate_legacy_build instead).
        self.assertFalse(is_valid_sky("day"))
        self.assertFalse(is_valid_sky("night"))

    def test_non_sky_texture_name_is_invalid(self):
        # qbsp only compiles sky* textures as sky.
        self.assertFalse(is_valid_sky("bricka2_1"))

    def test_empty_string_is_invalid(self):
        self.assertFalse(is_valid_sky(""))

    def test_name_over_15_chars_is_invalid(self):
        # WAD2 texture names are limited to 15 chars (16-byte field minus NUL).
        self.assertFalse(is_valid_sky("sky" + "a" * 13))

    def test_name_with_illegal_characters_is_invalid(self):
        self.assertFalse(is_valid_sky("sky z1"))
        self.assertFalse(is_valid_sky("sky/z1"))

    def test_unknown_name_rejected_when_wads_are_readable(self):
        # With a root whose WADs can be read, a syntactically fine but
        # nonexistent texture is caught up front rather than at compile time.
        root = pathlib.Path(__file__).resolve().parent.parent
        if not sky_texture_names(root):
            self.skipTest("project WADs are not present in this checkout")
        self.assertTrue(is_valid_sky("sky4", root))
        self.assertFalse(is_valid_sky("skybanana", root))

    def test_unreadable_wads_fall_back_to_permissive_check(self):
        # A root with no WADs can't validate against real textures, so it
        # must accept any well-formed sky name rather than reject everything.
        with tempfile.TemporaryDirectory() as empty:
            self.assertTrue(is_valid_sky("sky_z1", pathlib.Path(empty)))
            self.assertFalse(is_valid_sky("nope", pathlib.Path(empty)))


if __name__ == "__main__":
    unittest.main()
