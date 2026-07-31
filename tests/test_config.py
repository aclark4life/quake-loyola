"""Tests for quake_loyola.config — the ql.toml-backed flag/build-setting
override system used by the `ql conf` CLI and read by
constants/flags.py (and a few other constants modules) at import time."""

from quake_loyola import config


def test_defaults_load_without_config_file(tmp_path):
    """With no ql.toml present, every flag/build value should equal its
    hardcoded default."""
    missing = tmp_path / "does_not_exist.toml"
    raw = config._read_toml(missing)
    assert raw == {}
    # Also verify the actual default-merging logic that FLAGS/BUILD are
    # built from at import time: with no ql.toml, merging {} on top of
    # DEFAULTS/BUILD_DEFAULTS must reproduce the defaults exactly.
    merged_flags = {**config.DEFAULTS, **raw.get("flags", {})}
    merged_build = {**config.BUILD_DEFAULTS, **raw.get("build", {})}
    assert merged_flags == config.DEFAULTS
    assert merged_build == config.BUILD_DEFAULTS
    # And the live module-level FLAGS/BUILD (loaded once at process start,
    # from the isolated cwd set up by tests/conftest.py) reflect this too.
    assert config.FLAGS == config.DEFAULTS
    assert config.BUILD == config.BUILD_DEFAULTS


def test_set_and_get_flag_round_trips(tmp_path):
    path = tmp_path / "ql.toml"
    assert (
        config.get("KNOTT_ENABLED_WALKWAY") == config.DEFAULTS["KNOTT_ENABLED_WALKWAY"]
    )  # sanity
    config.set_flag("KNOTT_ENABLED_WALKWAY", True, path=path)
    raw = config._read_toml(path)
    assert raw["flags"]["KNOTT_ENABLED_WALKWAY"] is True
    # Re-merging on top of DEFAULTS should reflect the override.
    merged = {**config.DEFAULTS, **raw.get("flags", {})}
    assert merged["KNOTT_ENABLED_WALKWAY"] is True
    # Unrelated flags stay at their defaults.
    assert merged["BASEMENT_ENABLED"] == config.DEFAULTS["BASEMENT_ENABLED"]


def test_set_flag_rejects_unknown_name(tmp_path):
    path = tmp_path / "ql.toml"
    try:
        config.set_flag("NOT_A_REAL_FLAG", True, path=path)
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for unknown flag name")


def test_set_and_get_build_setting_round_trips(tmp_path):
    path = tmp_path / "ql.toml"
    config.set_build("vis_mode", "full", path=path)
    raw = config._read_toml(path)
    assert raw["build"]["vis_mode"] == "full"


def test_sky_preset_default_is_day():
    assert (
        config.get_build("sky_preset") == config.BUILD_DEFAULTS["sky_preset"] == "day"
    )


def test_set_and_get_sky_preset_round_trips(tmp_path):
    path = tmp_path / "ql.toml"
    config.set_build("sky_preset", "night", path=path)
    raw = config._read_toml(path)
    assert raw["build"]["sky_preset"] == "night"
    merged = {**config.BUILD_DEFAULTS, **raw.get("build", {})}
    assert merged["sky_preset"] == "night"
    # The global default (unaffected by a path-scoped write) stays "day".
    assert config.get_build("sky_preset") == "day"


def test_reset_removes_config_file(tmp_path):
    path = tmp_path / "ql.toml"
    config.set_flag("KNOTT_ENABLED_WALKWAY", True, path=path)
    assert path.exists()
    removed = config.reset(path=path)
    assert removed is True
    assert not path.exists()
    # Resetting again (nothing to remove) reports False, doesn't error.
    assert config.reset(path=path) is False
