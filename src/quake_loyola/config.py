"""Load and persist the CLI build settings from ``ql.toml``.

Note on staleness: ``ql.toml`` is read once, at import time, into ``BUILD``
below. Downstream modules (e.g. ``constants.lighting``) resolve their own
module-level constants from that dict at *their* import time too, and are
not re-evaluated afterwards. ``set_build()`` keeps ``BUILD`` itself in sync
for any code that calls ``config.get_build()`` directly, but it does
**not** retroactively update already-imported constants. This
is safe for the ``ql`` CLI, where each invocation is a fresh process (see
``cli.py``), but callers embedding this package as a library and mutating
config programmatically mid-process should re-import the affected modules
(or spawn a subprocess) rather than expect in-place updates.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Any

from .build_presets import (
    BUILD_ENUM_SETTINGS,
    FOG_DENSITY_NAMES,
    LEGACY_SKY_PRESETS,
    is_valid_fog_density,
    is_valid_sky,
    is_valid_skybox,
    sky_options,
    skybox_options,
)
from .skyboxes import env_dir


def _find_repo_root(start: Path) -> Path:
    """Walk upward from ``start`` and return the nearest repo-root marker.

    If no ``pyproject.toml``/``.git`` marker is found in ``start`` or any of
    its parents, ``start`` itself is used as a fallback (this lets ``ql`` be
    run in an arbitrary working directory as its own self-contained
    "project" — e.g. tests isolate themselves this way with a ``tmp_path``).
    A warning is printed in that case so the fallback is never silent.
    """
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    print(
        f"quake_loyola: no pyproject.toml/.git found above {start} — "
        f"treating {start} itself as the project root for ql.toml/loyola.map.",
        file=sys.stderr,
    )
    return start


REPO_ROOT = _find_repo_root(Path.cwd())
CONFIG_PATH = REPO_ROOT / "ql.toml"


BUILD_DEFAULTS: dict[str, Any] = {
    "vis_mode": "fast",
    "light_extra": False,
    "lighting_preset": "bright",
    "fog_density": "default",
    "sky": "sky4",
    "skybox": "",
}


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _read_toml_safe(path: Path) -> dict[str, Any]:
    """Read ``path`` as TOML, converting a parse failure to ``RuntimeError``.

    Callers that mutate an existing ``ql.toml`` (``set_build``/``set_many``)
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

    Rejects a non-table section, unknown keys, and boolean values that
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


_MIGRATION_WARNED: set[str] = set()


def _migrate_legacy_build(data: Any) -> Any:
    """Rewrite retired ``[build]`` keys in ``data`` onto their current names.

    ``sky_preset`` (a two-entry ``day``/``night`` alias table over a texture
    name) was replaced by the plain ``sky`` texture name. Without this, an
    older ``ql.toml`` would fail :func:`_validate_section`'s unknown-key check
    with a bare "unknown key" error, so migrate it and warn once instead. The
    value is only carried over when ``sky`` isn't already set explicitly.
    """
    if not isinstance(data, dict) or "sky_preset" not in data:
        return data
    migrated = dict(data)
    legacy = str(migrated.pop("sky_preset"))
    migrated.setdefault("sky", LEGACY_SKY_PRESETS.get(legacy, legacy))
    if "sky_preset" not in _MIGRATION_WARNED:
        _MIGRATION_WARNED.add("sky_preset")
        print(
            "quake_loyola: ql.toml [build] sky_preset is retired — using "
            f'sky = "{migrated["sky"]}" instead. Run '
            f"`ql sky {migrated['sky']}` to rewrite ql.toml and silence this.",
            file=sys.stderr,
        )
    return migrated


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
    if "sky" in data and not is_valid_sky(str(data["sky"]), REPO_ROOT):
        available = sky_options(REPO_ROOT)
        expected = (
            f"one of {available}"
            if available
            else "a sky texture name (letters/digits/underscore, 1-15 chars, "
            "starting with 'sky')"
        )
        raise ValueError(f"ql.toml [build] sky must be {expected}, got {data['sky']!r}")
    if "skybox" in data and not is_valid_skybox(str(data["skybox"])):
        available = skybox_options()
        expected = (
            f'"" (no skybox) or one of {available}'
            if available
            else f'"" (no skybox) or the name of a skybox installed in {env_dir()}'
        )
        raise ValueError(
            f"ql.toml [build] skybox must be {expected}, got {data['skybox']!r}"
        )
    if "light_extra" in data and not isinstance(data["light_extra"], bool):
        raise TypeError(
            f"ql.toml [build] light_extra must be a bool, "
            f"got {type(data['light_extra']).__name__}"
        )
    return data


if _LOAD_ERROR is None:
    try:
        _build_raw = _validate_build_values(
            _validate_section(
                "build", _migrate_legacy_build(_raw.get("build", {})), BUILD_DEFAULTS
            )
        )
    except (TypeError, KeyError, ValueError) as exc:
        _build_raw = {}
        _LOAD_ERROR = exc
else:
    _build_raw = {}

BUILD: dict[str, Any] = {**BUILD_DEFAULTS, **_build_raw}


def non_default_overrides() -> dict[str, Any]:
    """Return every build setting whose effective value differs from its
    hardcoded ``config.py`` default, keyed by name.

    Used to surface ambient ``ql.toml`` state at the top of ``ql gen``/
    ``generate_map.py`` output — silent config drift between developers (or
    between an interactive session and a tool like ``scripts/update_golden.py``)
    is exactly what caused a golden-value regression once; always print this
    rather than letting a non-default ``ql.toml`` change output unannounced.
    """
    check_load_error()
    overrides: dict[str, Any] = {}
    for name, default in BUILD_DEFAULTS.items():
        if BUILD[name] != default:
            overrides[name] = BUILD[name]
    return overrides


def check_load_error() -> None:
    """Raise a user-facing error if ``ql.toml`` failed to load or validate."""
    if _LOAD_ERROR is not None:
        raise RuntimeError(
            f"{CONFIG_PATH} could not be loaded: {_LOAD_ERROR}. Fix it by "
            "hand, or run `ql conf reset` to delete it and restore defaults."
        ) from _LOAD_ERROR


def get_build(name: str) -> Any:
    """Return the effective value of a build-tool setting."""
    check_load_error()
    if name not in BUILD_DEFAULTS:
        raise KeyError(f"Unknown build setting {name!r} — not in config.BUILD_DEFAULTS")
    return BUILD[name]


def _section_as_dict(raw: dict[str, Any], section_name: str) -> dict[str, Any]:
    """Return ``raw[section_name]`` as a dict, or raise a clean, user-facing
    error if it exists but isn't a table (e.g. ``build = 5`` in ``ql.toml``).

    Without this check, ``dict(raw.get(section_name, {}))`` would raise a
    raw, confusing ``TypeError`` for non-dict/non-iterable values instead of
    the same clear error style used elsewhere in this module.
    """
    section = raw.get(section_name, {})
    if not isinstance(section, dict):
        raise RuntimeError(
            f"ql.toml [{section_name}] must be a table, got "
            f"{type(section).__name__}: {section!r}"
        )
    return dict(section)


def set_build(name: str, value: Any, path: Path = CONFIG_PATH) -> None:
    check_load_error()
    if name not in BUILD_DEFAULTS:
        raise KeyError(f"Unknown build setting {name!r} — not in config.BUILD_DEFAULTS")
    raw = _read_toml_safe(path)
    build = _migrate_legacy_build(_section_as_dict(raw, "build"))
    build[name] = value
    _validate_build_values(build)
    raw["build"] = build
    _write_toml_safe(path, raw)
    if path == CONFIG_PATH:
        BUILD[name] = value


def set_many(items: list[tuple[str, Any]], path: Path = CONFIG_PATH) -> None:
    """Apply several build-setting changes as a single read-validate-write.

    ``items`` is a list of ``(name, value)`` pairs. Unlike calling
    :func:`set_build` in a loop, this reads ``ql.toml`` once, applies every
    change to an in-memory copy, validates the whole result, and writes it
    back in one shot — so a later item failing validation (or the write
    itself failing) never leaves an earlier item's change persisted on its
    own.
    """
    check_load_error()
    for name, _value in items:
        if name not in BUILD_DEFAULTS:
            raise KeyError(
                f"Unknown build setting {name!r} — not in config.BUILD_DEFAULTS"
            )
    raw = _read_toml_safe(path)
    build = _migrate_legacy_build(_section_as_dict(raw, "build"))
    for name, value in items:
        build[name] = value
    _validate_build_values(build)
    raw["build"] = build
    _write_toml_safe(path, raw)
    if path == CONFIG_PATH:
        for name, value in items:
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
        BUILD.clear()
        BUILD.update(BUILD_DEFAULTS)

        _LOAD_ERROR = None
    return removed
