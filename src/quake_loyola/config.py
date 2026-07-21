"""User-configurable build-time settings.

Every boolean "master switch" flag that used to be hardcoded directly in
``constants/flags.py`` (and a handful of similar flags scattered in
``constants/bridge.py``, ``constants/knott.py``, ``constants/derived.py``) is
now looked up here instead. :data:`DEFAULTS` holds the fallback value for each
flag (identical to what was hardcoded before this module existed); anything
present in ``ql.toml`` (at the repository root) overrides its default.

This file has no dependency on the rest of ``quake_loyola`` so it can be
imported early (from ``constants/flags.py`` etc.) without any risk of a
circular import.

Edit ``ql.toml`` by hand, or use the ``ql conf`` CLI (see ``cli.py``):

    ql conf show                      # list every flag/setting
    ql conf set KNOTT_ENABLED true
    ql conf set vis_mode full
    ql conf set lighting_preset dusk
    ql conf set fog_density high
    ql conf set sky_preset night
    ql conf reset                      # delete ql.toml, back to defaults
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    """Walk upward from `start` looking for the repo root (marked by
    pyproject.toml or .git), so `ql`/`generate_map.py` resolve the same
    ql.toml/tools/build paths regardless of which subdirectory they're run
    from. Falls back to `start` itself if no marker is found (e.g. a repo
    checkout without .git, such as an extracted tarball), preserving the
    previous cwd-based behavior in that case."""
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    return start


# Resolved by walking up from the current working directory (not the
# installed package location) so this works whether quake_loyola is
# imported via `sys.path` insertion from a repo checkout (generate_map.py)
# or pip-installed into site-packages — either way, `ql`/`generate_map.py`
# find the same ql.toml no matter which subdirectory of the repo they're
# run from (same convention as `just`, which uses `justfile_directory()`).
REPO_ROOT = _find_repo_root(Path.cwd())
CONFIG_PATH = REPO_ROOT / "ql.toml"

# ════════════════════════════════════════════════════════════════════════
# Flag defaults — one entry per boolean switch, formerly hardcoded in
# constants/flags.py, constants/bridge.py, constants/knott.py, and
# constants/derived.py. Keys are the exact constant names used at their call
# sites so `ql conf set <NAME> <value>` maps 1:1 onto the Python constant.
# ════════════════════════════════════════════════════════════════════════
DEFAULTS: dict[str, bool] = {
    # -- module masters (constants/flags.py) --
    "BRIDGE_ENABLED_SPAN_WEST_APPROACH": True,
    "BRIDGE_ENABLED_SPAN_CENTER": True,
    "BRIDGE_ENABLED_SPAN_EAST_APPROACH": True,
    "BRIDGE_ENABLED_SPAN_KH": True,
    "BRIDGE_ENABLED_SPAN_EAST_EXT": True,
    "STREETS_ENABLED_DETAILS": True,
    "WEST_CAMPUS_ENABLED_DORMS": False,
    "WEST_CAMPUS_ENABLED_FENCE": True,
    "WEST_CAMPUS_ENABLED_TERRAIN": True,
    "WEST_CAMPUS_ENABLED_WALL": True,
    "WEST_CAMPUS_ENABLED_SIDEWALK": True,
    "NE_ENABLED_TERRAIN": True,
    "KNOTT_ENABLED_TERRAIN": True,
    "KNOTT_ENABLED": False,
    "ENTITIES_ENABLED_TELEPORTS": False,
    "ENTITIES_ENABLED_DM_SPAWNS": False,
    "ENTITIES_ENABLED_WEAPONS": False,
    "ENTITIES_ENABLED_AMMO": False,
    "ENTITIES_ENABLED_HEALTH": False,
    "ENTITIES_ENABLED_MONSTERS": False,
    "ENTITIES_ENABLED_VEGETATION": False,
    "ENTITIES_ENABLED_PLATFORM": False,
    "ENTITIES_ENABLED_EXIT": False,
    "MARYLAND_ENABLED": False,
    "MARYLAND_ENABLED_TERRAIN": False,
    # -- light-group masters (constants/flags.py) --
    "LIGHTS_ENABLED_TORCHES": True,
    "LIGHTS_ENABLED_DECK_WALL": True,
    "LIGHTS_ENABLED_PENDANTS": False,
    "LIGHTS_ENABLED_PIER_UPLIGHTS": False,
    "LIGHTS_ENABLED_ABUTMENT_ARCH": False,
    "LIGHTS_ENABLED_DORM_INTERIOR": False,
    "BASEMENT_ENABLED_LIGHTS": True,
    # -- misc display flags (constants/flags.py) --
    "BRIDGE_ENABLED_FASCIA_TEXT": True,
    "BRIDGE_ENABLED_SUPPORTS": True,
    # -- other module-local flags --
    "BRIDGE_ENABLED_PIER_BASE_LIGHTS": False,  # constants/bridge.py
    "KNOTT_ENABLED_EXTERIOR": True,  # constants/knott.py
    "KNOTT_ENABLED_INTERIOR": False,  # constants/knott.py
    "KNOTT_ENABLED_MONSTERS": False,  # constants/knott.py
    # Off by default — the KH pedestrian walkway/sidewalk/support bent are
    # opt-in extras layered on top of the KH terrain, not part of the core
    # map; enable explicitly with `ql conf set KNOTT_ENABLED_WALKWAY true`.
    "KNOTT_ENABLED_WALKWAY": False,  # constants/knott.py
    "BASEMENT_ENABLED": True,  # constants/derived.py
}

# ════════════════════════════════════════════════════════════════════════
# Build-tool settings — not Python constants, consumed by `ql build`
# (mirrors/extends the `just compile`/`just compile-fast` recipes).
# ════════════════════════════════════════════════════════════════════════
BUILD_DEFAULTS: dict[str, Any] = {
    "vis_mode": "fast",  # "fast" (vis -fast, quick iteration) or "full" (vis, full PVS)
    "light_extra": False,  # add light's -extra flag (2x2 supersampling, slower/higher quality)
    "lighting_preset": "bright",  # key into constants/lighting.py's LIGHTING_PRESETS (dawn, midday, golden_hour, dusk, overcast, night, bright, afternoon)
    "fog_density": "low",  # "default" (use the preset's own density), a named FogDensity level (off, low, med, high), or a custom float
    "sky_preset": "day",  # key into constants/textures.py's SKY_PRESETS (day, night) — which skybox texture is used on every sky-textured face
}


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _toml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    return json.dumps(str(value))


def _write_toml(path: Path, sections: dict[str, dict[str, Any]]) -> None:
    lines: list[str] = []
    for section, kv in sections.items():
        if not kv:
            continue
        lines.append(f"[{section}]")
        for key in sorted(kv):
            lines.append(f"{key} = {_toml_scalar(kv[key])}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n" if lines else "")


_LOAD_ERROR: Exception | None = None
try:
    _raw = _read_toml(CONFIG_PATH)
except tomllib.TOMLDecodeError as exc:
    _raw = {}
    _LOAD_ERROR = exc


def _validate_section(
    section_name: str, data: Any, allowed: dict[str, Any]
) -> dict[str, Any]:
    """Validate a loaded ql.toml section against its known keys/defaults.

    Rejects a non-table section, unknown keys, and boolean-flag values that
    aren't actually booleans (e.g. a string leaking through and becoming
    silently truthy downstream).
    """
    if not isinstance(data, dict):
        raise TypeError(
            f"ql.toml [{section_name}] must be a table, got {type(data).__name__}"
        )
    for key, value in data.items():
        if key not in allowed:
            raise KeyError(
                f"ql.toml [{section_name}] has unknown key {key!r} "
                f"(known: {sorted(allowed)})"
            )
        if isinstance(allowed[key], bool) and not isinstance(value, bool):
            raise TypeError(
                f"ql.toml [{section_name}] {key!r} must be a bool, "
                f"got {type(value).__name__}"
            )
    return data


def _validate_build_values(data: dict[str, Any]) -> dict[str, Any]:
    """A handful of extra semantic checks for [build] string settings that
    have a small, fixed set of valid values and no dependency on the rest of
    the package. (lighting_preset/sky_preset are validated where they're
    consumed, in constants/lighting.py and constants/textures.py, since
    those modules own the valid-name lists and this module cannot import
    them back without a circular import — they both import get_build from
    here.)
    """
    if "vis_mode" in data and data["vis_mode"] not in ("fast", "full"):
        raise ValueError(
            f"ql.toml [build] vis_mode must be 'fast' or 'full', "
            f"got {data['vis_mode']!r}"
        )
    return data


if _LOAD_ERROR is None:
    try:
        _flags_raw = _validate_section("flags", _raw.get("flags", {}), DEFAULTS)
        _build_raw = _validate_build_values(
            _validate_section("build", _raw.get("build", {}), BUILD_DEFAULTS)
        )
    except (TypeError, KeyError, ValueError) as exc:
        _flags_raw, _build_raw = {}, {}
        _LOAD_ERROR = exc
else:
    _flags_raw, _build_raw = {}, {}

FLAGS: dict[str, bool] = {**DEFAULTS, **_flags_raw}
BUILD: dict[str, Any] = {**BUILD_DEFAULTS, **_build_raw}


def check_load_error() -> None:
    """Raise a clear error if ql.toml failed to load/validate at import time.

    Deliberately NOT called by ``reset()``/``CONFIG_PATH`` access, so
    recovery commands (``ql conf reset``, ``ql conf path``) keep working
    even when ql.toml is malformed. Called by ``get()``/``get_build()`` so
    any command that actually needs a flag/setting value fails with one
    clear, actionable message instead of a raw parse traceback (or, worse,
    silently falling back to defaults without saying why).
    """
    if _LOAD_ERROR is not None:
        raise RuntimeError(
            f"{CONFIG_PATH} could not be loaded: {_LOAD_ERROR}. Fix it by "
            "hand, or run `ql conf reset` to delete it and restore defaults."
        ) from _LOAD_ERROR


def get(name: str) -> bool:
    """Return the effective value of a flag (default, overridden by ql.toml)."""
    check_load_error()
    if name not in DEFAULTS:
        raise KeyError(f"Unknown flag {name!r} — not in config.DEFAULTS")
    return FLAGS[name]


def get_build(name: str) -> Any:
    """Return the effective value of a build-tool setting."""
    check_load_error()
    if name not in BUILD_DEFAULTS:
        raise KeyError(f"Unknown build setting {name!r} — not in config.BUILD_DEFAULTS")
    return BUILD[name]


def set_flag(name: str, value: bool, path: Path = CONFIG_PATH) -> None:
    if name not in DEFAULTS:
        raise KeyError(f"Unknown flag {name!r} — not in config.DEFAULTS")
    raw = _read_toml(path)
    flags = dict(raw.get("flags", {}))
    flags[name] = value
    raw["flags"] = flags
    _write_toml(path, raw)
    if path == CONFIG_PATH:
        FLAGS[name] = value


def set_build(name: str, value: Any, path: Path = CONFIG_PATH) -> None:
    if name not in BUILD_DEFAULTS:
        raise KeyError(f"Unknown build setting {name!r} — not in config.BUILD_DEFAULTS")
    raw = _read_toml(path)
    build = dict(raw.get("build", {}))
    build[name] = value
    raw["build"] = build
    _write_toml(path, raw)
    if path == CONFIG_PATH:
        BUILD[name] = value


def reset(path: Path = CONFIG_PATH) -> bool:
    """Delete ql.toml, reverting every flag/setting to its default. Returns
    True if a file was actually removed."""
    global _LOAD_ERROR
    removed = False
    if path.exists():
        path.unlink()
        removed = True
    if path == CONFIG_PATH:
        # Repopulate the in-memory caches so config.get()/get_build() reflect
        # the defaults immediately, even within a long-lived process that
        # already read overridden values from the now-deleted file.
        FLAGS.clear()
        FLAGS.update(DEFAULTS)
        BUILD.clear()
        BUILD.update(BUILD_DEFAULTS)
        # A previously-broken ql.toml is now gone — clear the deferred load
        # error so get()/get_build() work again without restarting the
        # process (matters for the test suite / any long-lived caller).
        _LOAD_ERROR = None
    return removed
