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


def test_knott_floors_are_not_paved_in_the_exterior_cement():
    # FLOOR_KH used to be another alias for "sfloor3_2", the same string as
    # CEMENT/SIDEWALK/STONE, so a Knott interior deck would have rendered
    # identically to the pavement outside. The interior needs to read as
    # interior, so it must stay distinct from the exterior ground textures.
    exterior = {Textures.CEMENT, Textures.SIDEWALK, Textures.STONE, Textures.ROAD}
    assert Textures.FLOOR_KH not in exterior


def test_knott_floors_are_distinct_from_its_walls():
    # Floor and wall being one texture is the failure mode that makes an
    # interior read as a solid block, so pin those two apart. The floor
    # and the *roof* deliberately share gn_grey2 — both are slabs in the
    # same concrete stack — so they are not compared here.
    assert Textures.FLOOR_KH != Textures.BRICK_KH


def test_knott_floors_and_roof_share_one_slab_texture():
    # Deliberate, not an oversight: an interior floor tile made each
    # storey read as a finished room rather than as raw structure. If the
    # roof is ever retextured the decks should follow it.
    assert Textures.FLOOR_KH == Textures.ROOF_KH
