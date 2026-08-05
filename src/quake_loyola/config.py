"""Load and persist build flags and CLI build settings from ``ql.toml``.

Note on staleness: ``ql.toml`` is read once, at import time, into
``FLAGS``/``BUILD`` below. Downstream modules (e.g. ``constants.flags``,
``constants.lighting``) resolve their own module-level constants from those
dicts at *their* import time too, and are not re-evaluated afterwards.
``set_flag()``/``set_build()`` keep ``FLAGS``/``BUILD`` themselves in sync
for any code that calls ``config.get()``/``config.get_build()`` directly,
but they do **not** retroactively update already-imported constants. This
is safe for the ``ql`` CLI, where each invocation is a fresh process (see
``cli.py``), but callers embedding this package as a library and mutating
config programmatically mid-process should re-import the affected modules
(or spawn a subprocess) rather than expect in-place updates.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from .build_presets import (
    BUILD_ENUM_SETTINGS,
    FOG_DENSITY_NAMES,
    is_valid_fog_density,
)


def _find_repo_root(start: Path) -> Path:
    """Walk upward from ``start`` and return the nearest repo-root marker."""
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    return start


REPO_ROOT = _find_repo_root(Path.cwd())
CONFIG_PATH = REPO_ROOT / "ql.toml"


DEFAULTS: dict[str, bool] = {
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
    "KNOTT_ENABLED": True,
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
    "LIGHTS_ENABLED_TORCHES": True,
    "LIGHTS_ENABLED_DECK_WALL": True,
    "LIGHTS_ENABLED_PENDANTS": False,
    "LIGHTS_ENABLED_PIER_UPLIGHTS": False,
    "LIGHTS_ENABLED_ABUTMENT_ARCH": False,
    "LIGHTS_ENABLED_DORM_INTERIOR": False,
    "BASEMENT_ENABLED_LIGHTS": True,
    "BRIDGE_ENABLED_FASCIA_TEXT": True,
    "BRIDGE_ENABLED_SUPPORTS": True,
    "BRIDGE_ENABLED_PIER_BASE_LIGHTS": False,
    "KNOTT_ENABLED_WALKWAY": False,
    "KNOTT_ENABLED_WALKWAY_BENT": False,
    "BASEMENT_ENABLED": True,
}


BUILD_DEFAULTS: dict[str, Any] = {
    "vis_mode": "fast",
    "light_extra": False,
    "lighting_preset": "bright",
    "fog_density": "low",
    "sky_preset": "day",
}


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _read_toml_safe(path: Path) -> dict[str, Any]:
    """Read ``path`` as TOML, converting a parse failure to ``RuntimeError``.

    Callers that mutate an existing ``ql.toml`` (``set_flag``/``set_build``)
    must not let a raw ``tomllib.TOMLDecodeError`` or filesystem ``OSError``
    (e.g. permission denied) escape from a malformed or inaccessible file —
    every other config-loading failure in this module surfaces as
    ``RuntimeError`` (see ``check_load_error``), so this keeps that contract
    consistent for callers (e.g. ``ql conf set``) that only catch
    ``RuntimeError``.
    """
    try:
        return _read_toml(path)
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError(f"{path} could not be parsed: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"{path} could not be read: {exc}") from exc


def _toml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    return json.dumps(str(value))


def _write_toml(path: Path, sections: dict[str, dict[str, Any]]) -> None:
    lines: list[str] = []
    for section, kv in sections.items():
        if not isinstance(kv, dict):
            raise RuntimeError(
                f"{path} has a top-level key {section!r} that isn't a table "
                f"(got {type(kv).__name__}); fix it by hand, or run "
                "`ql conf reset` to delete it and restore defaults."
            )
        if not kv:
            continue
        lines.append(f"[{section}]")
        for key in sorted(kv):
            lines.append(f"{key} = {_toml_scalar(kv[key])}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n" if lines else "")


def _write_toml_safe(path: Path, sections: dict[str, dict[str, Any]]) -> None:
    """Write ``path`` as TOML, converting filesystem failures to ``RuntimeError``.

    Keeps the same error contract as :func:`_read_toml_safe` so callers
    (e.g. ``ql conf set``) that only catch ``RuntimeError`` see a clean,
    user-facing message instead of a raw ``OSError`` traceback when
    ``ql.toml`` can't be written (permission denied, disk full, etc.).
    """
    try:
        _write_toml(path, sections)
    except OSError as exc:
        raise RuntimeError(f"{path} could not be written: {exc}") from exc


_LOAD_ERROR: Exception | None = None
try:
    _raw = _read_toml(CONFIG_PATH)
except tomllib.TOMLDecodeError as exc:
    _raw = {}
    _LOAD_ERROR = exc
except OSError as exc:
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
    """Validate every build-setting value up front, at ``ql.toml`` load time.

    This is the single place all ``[build]`` values are checked, so a bad
    value always surfaces consistently as a ``RuntimeError`` from
    :func:`check_load_error` rather than as an uncaught ``ValueError`` from
    whichever ``constants`` submodule happens to read it first.
    """
    for setting, allowed in BUILD_ENUM_SETTINGS.items():
        if setting in data and data[setting] not in allowed:
            raise ValueError(
                f"ql.toml [build] {setting} must be one of {allowed}, "
                f"got {data[setting]!r}"
            )
    if "fog_density" in data and not is_valid_fog_density(str(data["fog_density"])):
        raise ValueError(
            f"ql.toml [build] fog_density must be 'default', one of "
            f"{FOG_DENSITY_NAMES}, or a numeric string, got "
            f"{data['fog_density']!r}"
        )
    if "light_extra" in data and not isinstance(data["light_extra"], bool):
        raise TypeError(
            f"ql.toml [build] light_extra must be a bool, "
            f"got {type(data['light_extra']).__name__}"
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
    """Raise a user-facing error if ``ql.toml`` failed to load or validate."""
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
    check_load_error()
    if name not in DEFAULTS:
        raise KeyError(f"Unknown flag {name!r} — not in config.DEFAULTS")
    raw = _read_toml_safe(path)
    flags = dict(raw.get("flags", {}))
    flags[name] = value
    _validate_section("flags", flags, DEFAULTS)
    raw["flags"] = flags
    _write_toml_safe(path, raw)
    if path == CONFIG_PATH:
        FLAGS[name] = value


def set_build(name: str, value: Any, path: Path = CONFIG_PATH) -> None:
    check_load_error()
    if name not in BUILD_DEFAULTS:
        raise KeyError(f"Unknown build setting {name!r} — not in config.BUILD_DEFAULTS")
    raw = _read_toml_safe(path)
    build = dict(raw.get("build", {}))
    build[name] = value
    _validate_build_values(build)
    raw["build"] = build
    _write_toml_safe(path, raw)
    if path == CONFIG_PATH:
        BUILD[name] = value


def reset(path: Path = CONFIG_PATH) -> bool:
    """Delete ``ql.toml`` and restore in-memory defaults. Return True on removal."""
    global _LOAD_ERROR
    removed = False
    if path.exists():
        try:
            path.unlink()
        except OSError as exc:
            raise RuntimeError(f"{path} could not be removed: {exc}") from exc
        removed = True
    if path == CONFIG_PATH:
        FLAGS.clear()
        FLAGS.update(DEFAULTS)
        BUILD.clear()
        BUILD.update(BUILD_DEFAULTS)

        _LOAD_ERROR = None
    return removed
