"""Tests for quake_loyola.constants.textures — specifically Textures.SKY,
which is resolved from the ``sky`` build setting (a plain WAD2 texture name;
see constants/textures.py's module docstring and config.py's BUILD_DEFAULTS).
"""

from quake_loyola import config
from quake_loyola.constants.textures import Textures
from quake_loyola.wads import SKY_TEXTURE_PREFIX


def test_textures_sky_matches_default_build_setting():
    # Textures.SKY is resolved at import time from the `sky` build setting.
    # tests/conftest.py isolates the whole test session from any local
    # ql.toml, so this reflects the hardcoded default deterministically.
    assert config.get_build("sky") == config.BUILD_DEFAULTS["sky"] == "sky4"
    assert Textures.SKY == "sky4"


def test_default_sky_is_a_sky_texture():
    # qbsp only compiles textures named sky* as sky, so the default must be
    # one — otherwise the map would render with a solid wall overhead.
    assert Textures.SKY.startswith(SKY_TEXTURE_PREFIX)
