"""Tests for quake_loyola.config — the ql.toml-backed flag/build-setting
override system used by the `ql conf` CLI and read by
constants/flags.py (and a few other constants modules) at import time."""

import pytest

from quake_loyola import config


def test_defaults_load_without_config_file(tmp_path):
    """With no ql.toml present, every flag/build value should equal its
    hardcoded default."""
    missing = tmp_path / "does_not_exist.toml"
    raw = config._read_toml(missing)
    assert raw == {}
    # The live module-level FLAGS/BUILD (loaded once at process start, from
    # the isolated cwd set up by tests/conftest.py) must be the hardcoded
    # defaults — this is what the golden regression values assume.
    assert config.FLAGS == config.DEFAULTS
    assert config.BUILD == config.BUILD_DEFAULTS


def test_config_file_values_override_the_hardcoded_defaults(tmp_path):
    """The merge that FLAGS/BUILD are built from at import time must let a
    ql.toml value win over the default, and leave untouched keys alone."""
    path = tmp_path / "ql.toml"
    flag = next(name for name, value in config.DEFAULTS.items() if value is False)
    config._write_toml(path, {"flags": {flag: True}, "build": {"vis_mode": "full"}})
    raw = config._read_toml(path)

    merged_flags = {**config.DEFAULTS, **raw.get("flags", {})}
    merged_build = {**config.BUILD_DEFAULTS, **raw.get("build", {})}
    assert merged_flags[flag] is True
    assert merged_build["vis_mode"] == "full"
    assert config.BUILD_DEFAULTS["vis_mode"] == "fast"  # default left intact
    untouched = {k: v for k, v in merged_flags.items() if k != flag}
    assert untouched == {k: v for k, v in config.DEFAULTS.items() if k != flag}


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


def test_sky_default_is_sky4():
    assert config.get_build("sky") == config.BUILD_DEFAULTS["sky"] == "sky4"


def test_set_and_get_sky_round_trips(tmp_path):
    path = tmp_path / "ql.toml"
    config.set_build("sky", "sky1", path=path)
    raw = config._read_toml(path)
    assert raw["build"]["sky"] == "sky1"
    merged = {**config.BUILD_DEFAULTS, **raw.get("build", {})}
    assert merged["sky"] == "sky1"
    # The global default (unaffected by a path-scoped write) stays "sky4".
    assert config.get_build("sky") == "sky4"


def test_legacy_sky_preset_key_is_migrated(tmp_path):
    # An older ql.toml using the retired sky_preset key must keep working:
    # its value is mapped onto the `sky` texture name rather than failing
    # the unknown-key check.
    path = tmp_path / "ql.toml"
    path.write_text('[build]\nsky_preset = "night"\n')
    raw = config._read_toml(path)
    migrated = config._migrate_legacy_build(raw["build"])
    assert migrated == {"sky": "sky1"}


def test_legacy_sky_preset_passes_through_raw_texture_name():
    # sky_preset also accepted raw texture names; those carry over as-is.
    assert config._migrate_legacy_build({"sky_preset": "sky_z1"}) == {"sky": "sky_z1"}


def test_explicit_sky_wins_over_legacy_sky_preset():
    migrated = config._migrate_legacy_build({"sky_preset": "night", "sky": "sky_z1"})
    assert migrated == {"sky": "sky_z1"}


def test_reset_removes_config_file(tmp_path):
    path = tmp_path / "ql.toml"
    config.set_flag("KNOTT_ENABLED_WALKWAY", True, path=path)
    assert path.exists()
    removed = config.reset(path=path)
    assert removed is True
    assert not path.exists()
    # Resetting again (nothing to remove) reports False, doesn't error.
    assert config.reset(path=path) is False


def test_find_repo_root_finds_pyproject_marker(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert config._find_repo_root(nested) == tmp_path


def test_find_repo_root_finds_git_marker(tmp_path):
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "a"
    nested.mkdir()
    assert config._find_repo_root(nested) == tmp_path


def test_find_repo_root_falls_back_to_start_when_no_marker(tmp_path):
    lonely = tmp_path / "no_markers_here"
    lonely.mkdir()
    # tmp_path itself has no pyproject.toml/.git, and neither do its
    # ancestors up to the filesystem root in a CI sandbox — but rather than
    # depend on that, assert the walk at least reaches back to `lonely`
    # itself as a valid (if uninteresting) fallback candidate.
    result = config._find_repo_root(lonely)
    assert result == lonely or (result / "pyproject.toml").exists()


def test_read_toml_safe_wraps_decode_error_as_runtime_error(tmp_path):
    path = tmp_path / "broken.toml"
    path.write_text("this is not valid [[[ toml")
    with pytest.raises(RuntimeError, match="could not be parsed"):
        config._read_toml_safe(path)


def test_toml_scalar_formats_int_and_float():
    assert config._toml_scalar(5) == "5"
    assert config._toml_scalar(0.05) == "0.05"
    assert config._toml_scalar(True) == "true"
    assert config._toml_scalar(False) == "false"
    assert config._toml_scalar("night") == '"night"'


def test_write_toml_skips_empty_sections(tmp_path):
    path = tmp_path / "ql.toml"
    config._write_toml(path, {"flags": {}, "build": {"vis_mode": "full"}})
    text = path.read_text()
    assert "[flags]" not in text
    assert "[build]" in text
    assert "vis_mode" in text


def test_write_toml_all_empty_writes_empty_file(tmp_path):
    path = tmp_path / "ql.toml"
    config._write_toml(path, {"flags": {}, "build": {}})
    assert path.read_text() == ""


def test_write_toml_rejects_non_table_top_level_value(tmp_path):
    """A stray non-table top-level key (e.g. a scalar the user hand-added
    outside [flags]/[build]) must surface as a clean RuntimeError rather
    than an unhandled TypeError from iterating a non-dict value."""
    path = tmp_path / "ql.toml"
    with pytest.raises(RuntimeError, match="isn't a table"):
        config._write_toml(path, {"extra_scalar": 5, "flags": {"KNOTT_ENABLED": True}})


def test_set_flag_rejects_config_with_non_table_top_level_key(tmp_path):
    """set_flag must not let an unrelated non-table key in an existing
    ql.toml crash with a raw TypeError; it should raise RuntimeError so
    `ql conf set` (which only catches RuntimeError) reports it cleanly."""
    path = tmp_path / "ql.toml"
    path.write_text("extra_scalar = 5\n\n[flags]\nKNOTT_ENABLED = true\n")
    with pytest.raises(RuntimeError, match="isn't a table"):
        config.set_flag("KNOTT_ENABLED", False, path=path)


def test_validate_section_rejects_non_table():
    with pytest.raises(TypeError, match="must be a table"):
        config._validate_section("flags", "not a dict", config.DEFAULTS)


def test_validate_section_rejects_unknown_key():
    with pytest.raises(KeyError):
        config._validate_section("flags", {"NOT_A_REAL_FLAG": True}, config.DEFAULTS)


def test_validate_section_rejects_non_bool_flag_value():
    with pytest.raises(TypeError, match="must be a bool"):
        config._validate_section(
            "flags", {"KNOTT_ENABLED_WALKWAY": "yes"}, config.DEFAULTS
        )


def test_validate_build_values_rejects_bad_enum_setting():
    with pytest.raises(ValueError, match="must be one of"):
        config._validate_build_values({"vis_mode": "ultra"})


def test_validate_build_values_rejects_bad_fog_density():
    with pytest.raises(ValueError, match="fog_density"):
        config._validate_build_values({"fog_density": "extreme"})


def test_validate_build_values_rejects_non_bool_light_extra():
    with pytest.raises(TypeError, match="light_extra"):
        config._validate_build_values({"light_extra": "yes"})


def test_get_rejects_unknown_flag_name():
    with pytest.raises(KeyError):
        config.get("NOT_A_REAL_FLAG")


def test_get_build_rejects_unknown_setting_name():
    with pytest.raises(KeyError):
        config.get_build("not_a_real_setting")


def test_set_build_rejects_unknown_setting_name(tmp_path):
    path = tmp_path / "ql.toml"
    with pytest.raises(KeyError):
        config.set_build("not_a_real_setting", "x", path=path)
    assert not path.exists()


def test_set_flag_and_reset_update_in_memory_state_at_config_path():
    """When path == CONFIG_PATH (the default), set_flag()/reset() must keep
    FLAGS/BUILD themselves in sync for callers that read config.get()
    directly, not just the on-disk ql.toml."""
    original = config.get("KNOTT_ENABLED_WALKWAY")
    try:
        config.set_flag("KNOTT_ENABLED_WALKWAY", not original)
        assert config.get("KNOTT_ENABLED_WALKWAY") == (not original)
        assert config.FLAGS["KNOTT_ENABLED_WALKWAY"] == (not original)
    finally:
        removed = config.reset()
        assert removed is True
        assert (
            config.get("KNOTT_ENABLED_WALKWAY")
            == config.DEFAULTS["KNOTT_ENABLED_WALKWAY"]
        )


def test_set_build_updates_in_memory_state_at_config_path():
    try:
        config.set_build("vis_mode", "full")
        assert config.get_build("vis_mode") == "full"
        assert config.BUILD["vis_mode"] == "full"
    finally:
        config.reset()
        assert config.get_build("vis_mode") == "fast"


def test_set_many_applies_every_item_in_one_write(tmp_path):
    path = tmp_path / "ql.toml"
    config.set_many(
        [
            ("flag", "KNOTT_ENABLED_WALKWAY", False),
            ("build", "vis_mode", "full"),
        ],
        path=path,
    )
    raw = config._read_toml(path)
    assert raw["flags"]["KNOTT_ENABLED_WALKWAY"] is False
    assert raw["build"]["vis_mode"] == "full"


def test_set_many_persists_nothing_when_a_later_item_is_invalid(tmp_path):
    """set_many's whole reason to exist is that it validates the merged result
    before writing, so a bad item can't leave an earlier good one persisted.
    The CLI pre-validates every pair, so nothing else exercises this path."""
    path = tmp_path / "ql.toml"
    config.set_build("light_extra", True, path=path)
    before = path.read_text()

    with pytest.raises(ValueError):
        config.set_many(
            [
                ("flag", "KNOTT_ENABLED_WALKWAY", False),
                ("build", "vis_mode", "ultra"),
            ],
            path=path,
        )

    assert path.read_text() == before
    raw = config._read_toml(path)
    assert "KNOTT_ENABLED_WALKWAY" not in raw.get("flags", {})
    assert "vis_mode" not in raw.get("build", {})


def test_set_many_rejects_an_unknown_name_before_touching_the_file(tmp_path):
    path = tmp_path / "ql.toml"
    with pytest.raises(KeyError):
        config.set_many(
            [
                ("flag", "KNOTT_ENABLED_WALKWAY", False),
                ("flag", "NO_SUCH_FLAG", True),
            ],
            path=path,
        )
    assert not path.exists()
