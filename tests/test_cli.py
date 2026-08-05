"""Tests for the `ql` CLI (src/quake_loyola/cli.py), focused on the
`ql conf` subcommands' validation of named-preset build settings
(sky_preset, lighting_preset, fog_density, vis_mode).

Each test invokes the CLI in a fresh subprocess (via `python -c`, with
PYTHONPATH pointed at src/ — same as pytest's own `pythonpath` config in
pyproject.toml, so this works whether or not the package is pip-installed)
with its cwd pointed at an isolated tmp_path, so `config.CONFIG_PATH`
(which is resolved from `Path.cwd()` at import time inside the subprocess)
never touches the real repo's ql.toml.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"


def run_ql(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(SRC_DIR)}
    return subprocess.run(
        [sys.executable, "-c", "from quake_loyola.cli import app; app()", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )


def test_conf_show_lists_sky_preset_options(tmp_path):
    result = run_ql("conf", "show", cwd=tmp_path)
    assert result.returncode == 0
    assert "sky_preset" in result.stdout
    assert "options: day, night" in result.stdout


def test_conf_get_sky_preset_default(tmp_path):
    result = run_ql("conf", "get", "sky_preset", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == "day"


def test_conf_set_sky_preset_night_round_trips(tmp_path):
    set_result = run_ql("conf", "set", "sky_preset", "night", cwd=tmp_path)
    assert set_result.returncode == 0
    assert "sky_preset = night" in set_result.stdout

    get_result = run_ql("conf", "get", "sky_preset", cwd=tmp_path)
    assert get_result.returncode == 0
    assert get_result.stdout.strip() == "night"

    assert (tmp_path / "ql.toml").exists()


def test_conf_set_sky_preset_rejects_invalid_value(tmp_path):
    result = run_ql("conf", "set", "sky_preset", "midnight", cwd=tmp_path)
    assert result.returncode != 0
    assert "sky_preset must be one of" in result.stdout + result.stderr
    # Nothing should have been persisted for an invalid value.
    assert not (tmp_path / "ql.toml").exists()


def test_conf_get_vis_mode_default(tmp_path):
    result = run_ql("conf", "get", "vis_mode", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == "fast"


def test_conf_set_vis_mode_full_round_trips(tmp_path):
    set_result = run_ql("conf", "set", "vis_mode", "full", cwd=tmp_path)
    assert set_result.returncode == 0
    assert "vis_mode = full" in set_result.stdout

    get_result = run_ql("conf", "get", "vis_mode", cwd=tmp_path)
    assert get_result.returncode == 0
    assert get_result.stdout.strip() == "full"


def test_conf_set_vis_mode_rejects_invalid_value(tmp_path):
    result = run_ql("conf", "set", "vis_mode", "ultra", cwd=tmp_path)
    assert result.returncode != 0
    assert "vis_mode must be" in result.stdout + result.stderr
    assert not (tmp_path / "ql.toml").exists()


def test_conf_get_lighting_preset_default(tmp_path):
    result = run_ql("conf", "get", "lighting_preset", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == "bright"


def test_conf_set_lighting_preset_dusk_round_trips(tmp_path):
    set_result = run_ql("conf", "set", "lighting_preset", "dusk", cwd=tmp_path)
    assert set_result.returncode == 0
    assert "lighting_preset = dusk" in set_result.stdout

    get_result = run_ql("conf", "get", "lighting_preset", cwd=tmp_path)
    assert get_result.returncode == 0
    assert get_result.stdout.strip() == "dusk"


def test_conf_set_lighting_preset_rejects_invalid_value(tmp_path):
    result = run_ql("conf", "set", "lighting_preset", "midnight_sun", cwd=tmp_path)
    assert result.returncode != 0
    assert "lighting_preset must be one of" in result.stdout + result.stderr
    assert not (tmp_path / "ql.toml").exists()


def test_conf_get_fog_density_default(tmp_path):
    result = run_ql("conf", "get", "fog_density", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == "default"


def test_conf_set_fog_density_named_round_trips(tmp_path):
    set_result = run_ql("conf", "set", "fog_density", "high", cwd=tmp_path)
    assert set_result.returncode == 0
    assert "fog_density = high" in set_result.stdout

    get_result = run_ql("conf", "get", "fog_density", cwd=tmp_path)
    assert get_result.returncode == 0
    assert get_result.stdout.strip() == "high"


def test_conf_set_fog_density_custom_float_round_trips(tmp_path):
    set_result = run_ql("conf", "set", "fog_density", "0.05", cwd=tmp_path)
    assert set_result.returncode == 0
    assert "fog_density = 0.05" in set_result.stdout

    get_result = run_ql("conf", "get", "fog_density", cwd=tmp_path)
    assert get_result.returncode == 0
    assert get_result.stdout.strip() == "0.05"


def test_conf_set_fog_density_rejects_invalid_value(tmp_path):
    result = run_ql("conf", "set", "fog_density", "extreme", cwd=tmp_path)
    assert result.returncode != 0
    assert "fog_density must be" in result.stdout + result.stderr
    assert not (tmp_path / "ql.toml").exists()


def test_gen_with_malformed_toml_fails_cleanly(tmp_path):
    # A hand-edited ql.toml with an invalid build value should surface a
    # single actionable RuntimeError message on `ql gen`, not a raw traceback
    # from whichever `constants` submodule happens to read it first.
    (tmp_path / "ql.toml").write_text('[build]\nlighting_preset = "midnight"\n')
    result = run_ql("gen", cwd=tmp_path)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "could not be loaded" in result.stderr
    assert "lighting_preset" in result.stderr


def test_build_with_malformed_toml_fails_cleanly(tmp_path):
    (tmp_path / "ql.toml").write_text('[build]\nsky_preset = "midnight"\n')
    result = run_ql("build", cwd=tmp_path)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "could not be loaded" in result.stderr


def test_build_without_ericw_tools_fails_cleanly(tmp_path):
    # No .tools/ericw-tools-*/bin under an isolated cwd — `ql build` should
    # generate the map, then fail with a clear, actionable message instead
    # of a stack trace when it can't find the compiler toolchain.
    result = run_ql("build", cwd=tmp_path)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "ericw-tools not found" in result.stdout + result.stderr
    # `ql gen` (called internally by `build`) should still have run and
    # written loyola.map before the toolchain check failed.
    assert (tmp_path / "loyola.map").exists()


def _install_fake_ericw_tools(tmp_path: Path) -> None:
    """Create fake, no-op qbsp/vis/light executables under an isolated
    tmp_path's .tools/, mimicking a real `just install-tools` layout, so
    `ql build` can exercise its success path without needing the real
    ericw-tools binaries. Each fake tool just creates the expected output
    files (loyola.bsp/.lit) and exits 0."""
    import stat

    tools_bin = tmp_path / ".tools" / f"ericw-tools-v0.18.1-{platform.system()}" / "bin"
    tools_bin.mkdir(parents=True)
    for name, outputs in (
        ("qbsp", ["loyola.bsp"]),
        ("vis", []),
        ("light", ["loyola.lit"]),
    ):
        script = tools_bin / name
        touch_cmds = "\n".join(f'touch "{out}"' for out in outputs)
        script.write_text(f"#!/bin/sh\n{touch_cmds}\nexit 0\n")
        script.chmod(script.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def test_build_success_path_compiles_without_deploying(tmp_path):
    # With fake ericw-tools binaries in place and --no-deploy, `ql build`
    # should run gen -> qbsp -> vis -> light successfully and skip the
    # /Applications/id1/maps deploy step (which isn't safe to touch in tests).
    _install_fake_ericw_tools(tmp_path)
    result = run_ql("build", "--no-deploy", cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Traceback" not in result.stderr
    assert (tmp_path / "loyola.map").exists()
    assert (tmp_path / "loyola.bsp").exists()
    assert (tmp_path / "loyola.lit").exists()
    assert "Deployed to" not in result.stdout


def test_conf_get_unknown_setting_fails_cleanly(tmp_path):
    result = run_ql("conf", "get", "not_a_real_setting", cwd=tmp_path)
    assert result.returncode != 0
    assert "Unknown setting" in result.stdout + result.stderr


def test_conf_set_unknown_setting_fails_cleanly(tmp_path):
    result = run_ql("conf", "set", "not_a_real_setting", "true", cwd=tmp_path)
    assert result.returncode != 0
    assert "Unknown setting" in result.stdout + result.stderr
    assert not (tmp_path / "ql.toml").exists()
