"""Tests for the ``skybox`` build setting and skybox discovery."""

from __future__ import annotations

import pytest

from quake_loyola import build_presets, skyboxes


def _install(directory, name, suffixes=skyboxes.SKYBOX_FACE_SUFFIXES, ext=".tga"):
    for suffix in suffixes:
        (directory / f"{name}_{suffix}{ext}").write_bytes(b"")


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Point the skybox lookup at an empty temporary ``gfx/env``."""
    directory = tmp_path / "gfx" / "env"
    directory.mkdir(parents=True)
    monkeypatch.setenv("QUAKE_DIR", str(tmp_path))
    return directory


def test_env_dir_follows_quake_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("QUAKE_DIR", str(tmp_path))
    assert skyboxes.env_dir() == tmp_path / "gfx" / "env"


def test_env_dir_defaults_without_override(monkeypatch):
    monkeypatch.delenv("QUAKE_DIR", raising=False)
    assert skyboxes.env_dir() == skyboxes.DEFAULT_QUAKE_DIR / "gfx" / "env"


def test_complete_skybox_is_discovered(env):
    _install(env, "mak_sunset1")
    assert skyboxes.skybox_names() == {"mak_sunset1"}


def test_partial_skybox_is_ignored(env):
    """Five of six faces must not count — it would render as garbage."""
    _install(env, "half", suffixes=("bk", "dn", "ft", "lf", "rt"))
    assert skyboxes.skybox_names() == set()


def test_missing_env_dir_is_not_an_error(tmp_path, monkeypatch):
    monkeypatch.setenv("QUAKE_DIR", str(tmp_path / "nope"))
    assert skyboxes.skybox_names() == set()


def test_non_image_files_are_ignored(env):
    _install(env, "readme", ext=".txt")
    assert skyboxes.skybox_names() == set()


@pytest.mark.usefixtures("env")
def test_empty_skybox_is_valid_and_means_none():
    assert build_presets.is_valid_skybox("")


def test_installed_skybox_is_valid(env):
    _install(env, "mak_sunset1")
    assert build_presets.is_valid_skybox("mak_sunset1")


def test_uninstalled_skybox_is_rejected(env):
    _install(env, "mak_sunset1")
    assert not build_presets.is_valid_skybox("mak_sunset2")


@pytest.mark.usefixtures("env")
def test_validation_is_permissive_when_nothing_is_installed():
    """No pack installed means "can't check", not "everything is invalid"."""
    assert build_presets.is_valid_skybox("mak_sunset1")


@pytest.mark.parametrize("value", ["mak_sunset1", "a-b", "A1", "a" * 63])
def test_name_syntax_accepts_plain_names(value):
    assert skyboxes.is_valid_skybox_name(value)


@pytest.mark.parametrize("value", ["", "../etc/passwd", "has space", "a" * 64])
def test_name_syntax_rejects_anything_path_like(value):
    """The name is used verbatim as a filename stem, so keep it inert."""
    assert not skyboxes.is_valid_skybox_name(value)


def test_skybox_options_are_sorted(env):
    _install(env, "b_sky")
    _install(env, "a_sky")
    assert build_presets.skybox_options() == ["a_sky", "b_sky"]


def test_worldspawn_sky_key_carries_the_skybox_not_the_texture():
    """Engines read worldspawn "sky" as a skybox name, never as a texture.

    Writing the texture name there (which is what this project used to do)
    just sends the engine looking for a gfx/env file that cannot exist, so
    the key must be absent when no skybox is configured.
    """
    from quake_loyola import config
    from quake_loyola.constants import WORLDSPAWN_FIELDS

    skybox = config.get_build("skybox")
    if skybox:
        assert WORLDSPAWN_FIELDS["sky"] == skybox
    else:
        assert "sky" not in WORLDSPAWN_FIELDS
    assert "_skybox" not in WORLDSPAWN_FIELDS


def test_worldspawn_value_keeps_the_packs_underscore(env):
    """The engine glues the face suffix on with no separator of its own.

    ``gfx/env/%s%s`` + ``rt`` means "mak_sunset1" would look for
    ``gfx/env/mak_sunset1rt.tga``; the underscore has to come from the
    worldspawn value or the load silently fails.
    """
    _install(env, "mak_sunset1")
    assert skyboxes.skybox_worldspawn_value("mak_sunset1") == "mak_sunset1_"


def test_worldspawn_value_handles_a_separatorless_pack(env):
    """Some old packs are named ``space1rt.tga``; don't invent an underscore."""
    for suffix in skyboxes.SKYBOX_FACE_SUFFIXES:
        (env / f"space1{suffix}.tga").write_bytes(b"")
    assert skyboxes.skybox_names() == {"space1"}
    assert skyboxes.skybox_worldspawn_value("space1") == "space1"


@pytest.mark.usefixtures("env")
def test_worldspawn_value_falls_back_when_not_installed():
    """A build machine has no gfx/env, so assume the modern convention."""
    assert skyboxes.skybox_worldspawn_value("mak_sunset1") == "mak_sunset1_"
    assert skyboxes.skybox_worldspawn_value("already_") == "already_"


@pytest.mark.usefixtures("env")
def test_worldspawn_value_of_no_skybox_is_empty():
    assert skyboxes.skybox_worldspawn_value("") == ""


def test_prefixes_and_names_differ_only_by_the_separator(env):
    _install(env, "mak_sunset1")
    assert skyboxes.skybox_prefixes() == {"mak_sunset1_"}
    assert skyboxes.skybox_names() == {"mak_sunset1"}
