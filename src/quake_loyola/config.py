"""Load and persist build flags and CLI build settings from ``ql.toml``."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any


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
    "KNOTT_ENABLED": False,
    "KNOTT_ENABLED_NEW": True,
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
    "KNOTT_ENABLED_EXTERIOR": True,
    "KNOTT_ENABLED_INTERIOR": False,
    "KNOTT_ENABLED_MONSTERS": False,
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
    """Validate build-setting values that this module can check directly."""
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
    raw = _read_toml(path)
    flags = dict(raw.get("flags", {}))
    flags[name] = value
    raw["flags"] = flags
    _write_toml(path, raw)
    if path == CONFIG_PATH:
        FLAGS[name] = value


def set_build(name: str, value: Any, path: Path = CONFIG_PATH) -> None:
    check_load_error()
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
    """Delete ``ql.toml`` and restore in-memory defaults. Return True on removal."""
    global _LOAD_ERROR
    removed = False
    if path.exists():
        path.unlink()
        removed = True
    if path == CONFIG_PATH:
        FLAGS.clear()
        FLAGS.update(DEFAULTS)
        BUILD.clear()
        BUILD.update(BUILD_DEFAULTS)

        _LOAD_ERROR = None
    return removed
