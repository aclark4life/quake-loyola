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
