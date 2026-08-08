"""Tests for quake_loyola.constants.textures — specifically the
sky_preset -> skybox texture mapping used by Textures.SKY (see
constants/textures.py's module docstring / config.py's sky_preset entry
in BUILD_DEFAULTS)."""

from quake_loyola import config
from quake_loyola.constants.textures import SKY_PRESET_NAMES, SKY_PRESETS, Textures


def test_sky_presets_cover_day_and_night():
    assert set(SKY_PRESETS) == {"day", "night"}
    assert SKY_PRESET_NAMES == sorted(SKY_PRESETS)


def test_sky_presets_use_distinct_textures():
    # day and night must map to different skybox textures, otherwise the
    # setting would have no visible effect.
    assert SKY_PRESETS["day"] != SKY_PRESETS["night"]


def test_textures_sky_matches_default_build_setting():
    # Textures.SKY is resolved at import time from the sky_preset build
    # setting (default "day" — see config.BUILD_DEFAULTS). tests/conftest.py
    # isolates the whole test session from any local ql.toml, so this
    # reflects the hardcoded default deterministically.
    assert (
        config.get_build("sky_preset") == config.BUILD_DEFAULTS["sky_preset"] == "day"
    )
    assert Textures.SKY == SKY_PRESETS["day"]
