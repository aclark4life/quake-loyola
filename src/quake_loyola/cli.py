"""Typer CLI for viewing config, generating maps, and running builds.

Three layers, narrowest first:

* the shortcut commands ``ql sky`` / ``ql fog`` / ``ql light`` / ``ql vis`` —
  the handful of settings worth changing day to day. Run with no argument to
  print the current value and the valid ones.
* ``ql conf`` — show, set, and reset every build setting in ``ql.toml``.
* ``ql gen`` / ``ql build`` — run the pipeline.
"""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

import typer

from . import config
from .build_presets import (
    BUILD_ENUM_SETTINGS,
    FOG_DENSITY_NAMES,
    VIS_MODES,
    is_valid_fog_density,
    is_valid_sky,
    is_valid_skybox,
    sky_options,
    skybox_options,
)
from .skyboxes import env_dir

REPO_ROOT = config.REPO_ROOT

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(
    help="quake-loyola build CLI - configure the map and run the build.",
    context_settings=CONTEXT_SETTINGS,
    rich_markup_mode=None,
)
config_app = typer.Typer(
    help="View or change build-time settings stored in ql.toml.",
    context_settings=CONTEXT_SETTINGS,
    rich_markup_mode=None,
)
app.add_typer(config_app, name="conf")


def _build_options_hint(name: str) -> str:
    """Return a human-readable description of ``name``'s valid values.

    Single source of the "options: ..." text shared by ``ql conf show`` and
    each shortcut command's no-argument output, so the two can't drift.
    """
    if name in BUILD_ENUM_SETTINGS:
        return ", ".join(BUILD_ENUM_SETTINGS[name])
    if name == "fog_density":
        return (
            "default (the lighting preset's own fog), "
            f"{', '.join(FOG_DENSITY_NAMES)}, or a number (e.g. 0.05)"
        )
    if name == "sky":
        available = sky_options(REPO_ROOT)
        if available:
            return ", ".join(available)
        return "a sky texture name from a loaded WAD (e.g. sky4, sky_z1)"
    if name == "skybox":
        available = skybox_options()
        if available:
            return '"" (none), ' + ", ".join(available)
        return f'"" (none), or a skybox installed in {env_dir()}'
    if name == "light_extra":
        return "true, false"
    return ""


def _parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in ("true", "1", "yes", "on"):
        return True
    if v in ("false", "0", "no", "off"):
        return False
    raise typer.BadParameter(f"Expected a boolean (true/false), got {value!r}")


@config_app.command("show")
def config_show() -> None:
    """Show every build setting, its default, and its valid values."""
    try:
        exists = config.CONFIG_PATH.exists()
        typer.echo(
            f"Config file: {config.CONFIG_PATH}"
            + ("" if exists else " (not created yet - showing defaults)")
        )
        typer.echo("\n[build]")
        for name in sorted(config.BUILD_DEFAULTS):
            value = config.get_build(name)
            default = config.BUILD_DEFAULTS[name]
            marker = "*" if value != default else " "
            typer.echo(f" {marker} {name:<16} = {str(value):<8} (default: {default})")
            options = _build_options_hint(name)
            if options:
                for line in textwrap.wrap(
                    f"options: {options}",
                    width=76,
                    initial_indent=" " * 6,
                    subsequent_indent=" " * 15,
                ):
                    typer.echo(line)
        typer.echo("\n(* = overridden from its default via ql.toml)")
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@config_app.command("get")
def config_get(name: str) -> None:
    """Print the effective value of a single build setting."""
    name_l = name.lower()
    try:
        if name_l in config.BUILD_DEFAULTS:
            typer.echo(str(config.get_build(name_l)))
        else:
            typer.echo(
                f"Unknown setting {name!r}. Run `ql conf show` for the full list.",
                err=True,
            )
            raise typer.Exit(code=1)
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


def _validate_one(name: str, value: str) -> tuple[str, object]:
    """Validate a single NAME/value pair without persisting it.

    Return the ``(key, parsed_value)`` pair to hand to :func:`config.set_many`.
    """
    name_l = name.lower()
    if name_l in config.BUILD_DEFAULTS:
        if name_l in BUILD_ENUM_SETTINGS:
            allowed = BUILD_ENUM_SETTINGS[name_l]
            value_l = value.strip().lower()
            if value_l not in allowed:
                raise typer.BadParameter(f"{name_l} must be one of {allowed}")
            parsed_build: object = value_l
        elif name_l == "fog_density":
            stripped = value.strip()
            value_norm = (
                stripped.lower()
                if stripped.lower() in ("default", *FOG_DENSITY_NAMES)
                else stripped
            )
            if not is_valid_fog_density(value_norm):
                raise typer.BadParameter(
                    "fog_density must be 'default', one of "
                    f"{sorted(FOG_DENSITY_NAMES)}, or a finite, non-negative "
                    "numeric string"
                )
            parsed_build = value_norm
        elif name_l == "sky":
            value_norm = value.strip()
            if not is_valid_sky(value_norm, REPO_ROOT):
                raise typer.BadParameter(f"sky must be {_build_options_hint('sky')}")
            parsed_build = value_norm
        elif name_l == "skybox":
            value_norm = value.strip()
            if value_norm.lower() in ("none", "off", '""'):
                value_norm = ""
            if not is_valid_skybox(value_norm):
                raise typer.BadParameter(
                    f"skybox must be {_build_options_hint('skybox')}"
                )
            parsed_build = value_norm
        else:
            parsed_build = _parse_bool(value)
        return name_l, parsed_build
    else:
        typer.echo(
            f"Unknown setting {name!r}. Run `ql conf show` for the full list.",
            err=True,
        )
        raise typer.Exit(code=1)


_CONFIG_SET_EPILOG = """\b
Examples:
  ql conf set vis_mode full
  ql conf set light_extra true
  ql conf set lighting_preset dusk
  ql conf set fog_density high
  ql conf set sky sky_z1

\b
Multiple settings at once (NAME=VALUE form, space-separated):
  ql conf set vis_mode=full lighting_preset=dusk sky=sky_z1
"""


@config_app.command("set", epilog=_CONFIG_SET_EPILOG)
def config_set(
    args: list[str] = typer.Argument(
        ..., help="Either 'NAME VALUE', or one or more 'NAME=VALUE' pairs."
    ),
) -> None:
    """Set one or more build settings, persisted to ql.toml.

    For the settings you change most often there are shorter commands:
    ql sky, ql fog, ql light, and ql vis.
    """
    if len(args) == 2 and "=" not in args[0] and "=" not in args[1]:
        pairs = [(args[0], args[1])]
    else:
        pairs = []
        for arg in args:
            if "=" not in arg:
                raise typer.BadParameter(
                    f"Expected NAME=VALUE, got {arg!r} "
                    "(or pass exactly one 'NAME VALUE' pair)"
                )
            name, _, value = arg.partition("=")
            pairs.append((name, value))

    validated = [_validate_one(name, value) for name, value in pairs]
    try:
        config.set_many(validated)
        for key, parsed in validated:
            typer.echo(f"{key} = {parsed}")
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@config_app.command("reset")
def config_reset(
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip the confirmation prompt."
    ),
) -> None:
    """Delete ql.toml, reverting every build setting to its default."""
    if not config.CONFIG_PATH.exists():
        typer.echo("No ql.toml found — already using defaults.")
        raise typer.Exit()
    if not yes and not typer.confirm(
        f"Delete {config.CONFIG_PATH} and restore all defaults?"
    ):
        raise typer.Abort()
    try:
        config.reset()
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo("Reset to defaults.")


@config_app.command("path")
def config_path() -> None:
    """Print the path to ql.toml (whether or not it exists yet)."""
    typer.echo(str(config.CONFIG_PATH))


def _shortcut(setting: str, value: str | None) -> None:
    """Back the ``ql sky``/``fog``/``light``/``vis`` shortcut commands.

    With no ``value``, print the setting's current value and its valid ones;
    otherwise validate and persist it exactly as ``ql conf set`` would.
    """
    try:
        if value is None:
            current = config.get_build(setting)
            typer.echo(f"{setting} = {current}")
            options = _build_options_hint(setting)
            if options:
                typer.echo(f"options: {options}")
            return
        key, parsed = _validate_one(setting, value)
        config.set_many([(key, parsed)])
        typer.echo(f"{key} = {parsed}")
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@app.command("sky")
def sky(
    texture: str | None = typer.Argument(
        None,
        help="Sky texture name, e.g. sky4 or sky_z1. Omit to show the current one.",
    ),
) -> None:
    """Show or set the world sky texture (the 'sky' build setting)."""
    _shortcut("sky", texture)


@app.command("skybox")
def skybox(
    name: str | None = typer.Argument(
        None,
        help=(
            "Environment skybox name, e.g. mak_sunset1. Use 'none' to fall "
            "back to the sky texture. Omit to show the current one."
        ),
    ),
) -> None:
    """Show or set the environment skybox (the 'skybox' build setting).

    The images live in the engine's gfx/env directory, not in this repo; only
    skyboxes already installed there can be selected. This is a run-time
    engine feature, so TrenchBroom still shows the flat 'sky' texture.
    """
    _shortcut("skybox", name)


@app.command("fog")
def fog(
    density: str | None = typer.Argument(
        None,
        help=(
            "off/low/med/high, a number like 0.05, or 'default' to use the "
            "lighting preset's own fog. Omit to show the current value."
        ),
    ),
) -> None:
    """Show or set the fog density (the 'fog_density' build setting)."""
    _shortcut("fog_density", density)


@app.command("light")
def light(
    preset: str | None = typer.Argument(
        None,
        help="Time-of-day lighting preset. Omit to show the current one.",
    ),
) -> None:
    """Show or set the time-of-day lighting (the 'lighting_preset' setting).

    A preset sets every correlated worldspawn lighting field at once (sun
    color and angle, ambient level, fog color), which is why this one stays a
    named preset rather than a raw value.
    """
    _shortcut("lighting_preset", preset)


@app.command("vis")
def vis(
    mode: str | None = typer.Argument(
        None, help="'fast' or 'full'. Omit to show the current mode."
    ),
) -> None:
    """Show or set the vis pass used by 'ql build' (the 'vis_mode' setting)."""
    _shortcut("vis_mode", mode)


@app.command("gen")
def generate() -> None:
    """Write loyola.map using the current build settings."""
    try:
        from .mapgen import main as _generate_main

        _generate_main()
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        typer.echo(f"Map assembly failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except OSError as exc:
        typer.echo(f"Write failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc


_ERICW_TOOLS_VERSION_RE = re.compile(
    r"ericw-tools-v?(\d+)\.(\d+)\.(\d+)"
    r"(?:-(alpha|beta|rc)(\d+))?"
    r"(?:-(\d+)-g[0-9a-f]+)?"
)

#: Lowest ericw-tools release this project will compile with, matching
#: ``ericw_version`` in the justfile. qbsp v0.18.1 drops and orphans faces on
#: Pier 6, producing see-through holes and invisible walls, so an older install
#: left lying around under .tools/ must never be selected.
_ERICW_TOOLS_MIN_VERSION = (2, 0, 0)

_ERICW_PRERELEASE_ORDER = {"alpha": 0, "beta": 1, "rc": 2}


def _ericw_tools_version(path: Path) -> tuple[int, int, int, int, int, int]:
    """Sort key for a ``.tools/ericw-tools-*`` directory by release version.

    Parses ``[v]MAJOR.MINOR.PATCH``, an optional ``-alphaN``/``-betaN``/``-rcN``
    prerelease, and an optional ``-N-gHASH`` dev-build commit count out of the
    directory name, so the newest install is picked even when installs aren't
    in lexicographic order (e.g. v0.9.0 vs v0.18.1, or 2.0.0-alpha11 vs
    v0.18.1). A final release sorts above any prerelease of the same version.
    Unparseable names sort lowest.
    """
    match = _ERICW_TOOLS_VERSION_RE.search(path.name)
    if not match:
        return (0, 0, 0, 0, 0, 0)
    major, minor, patch, pre_kind, pre_num, commits = match.groups()
    # 3 == a final release, which outranks every prerelease of that version.
    pre_rank = 3 if pre_kind is None else _ERICW_PRERELEASE_ORDER[pre_kind]
    return (
        int(major),
        int(minor),
        int(patch),
        pre_rank,
        int(pre_num or 0),
        int(commits or 0),
    )


def _find_ericw_tools_bin(repo_root: Path) -> Path | None:
    """Return the directory holding the ericw-tools binaries, or None.

    ``just install-tools`` unpacks the 2.x archives with the binaries at the
    top level of ``.tools/ericw-tools-<version>-<System>/``, while older 0.18.x
    builds nested them in a ``bin/`` subdirectory. Accept either layout, ignore
    anything older than the minimum supported release, and pick the newest of
    what's left.
    """
    candidates = []
    for tools_dir in repo_root.glob(".tools/ericw-tools-*"):
        if not tools_dir.name.endswith(f"-{platform.system()}"):
            continue
        if _ericw_tools_version(tools_dir)[:3] < _ERICW_TOOLS_MIN_VERSION:
            continue
        for tools_bin in (tools_dir, tools_dir / "bin"):
            if (tools_bin / "qbsp").is_file():
                candidates.append((_ericw_tools_version(tools_dir), tools_bin))
                break
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


@app.command()
def build(
    deploy: bool = typer.Option(
        True,
        help="Copy the compiled .bsp/.lit into the Quake maps directory afterwards.",
    ),
    gen: bool = typer.Option(
        True,
        "--gen/--no-gen",
        help="Regenerate loyola.map first. --no-gen compiles the existing one.",
    ),
    vis_mode: str | None = typer.Option(
        None,
        "--vis",
        help="Override the configured vis mode for this run only: fast or full.",
    ),
    light_extra: bool | None = typer.Option(
        None,
        "--extra/--no-extra",
        help="Override the configured light -extra setting for this run only.",
    ),
) -> None:
    """Generate and compile the map using the current build settings.

    The vis mode and light -extra setting come from ql.toml (see 'ql vis' and
    'ql conf set light_extra'); --vis/--extra override them for one run
    without persisting anything, which is how the justfile's compile and
    compile-fast recipes pin their vis pass.
    """
    if vis_mode is not None and vis_mode not in VIS_MODES:
        raise typer.BadParameter(f"--vis must be one of {', '.join(VIS_MODES)}")
    if gen:
        generate()

    tools_bin = _find_ericw_tools_bin(REPO_ROOT)
    if tools_bin is None:
        version = ".".join(str(part) for part in _ERICW_TOOLS_MIN_VERSION)
        typer.echo(
            f"ericw-tools {version} or newer not found under .tools/ — "
            "run `just install-tools` first.",
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        if vis_mode is None:
            vis_mode = config.get_build("vis_mode")
        if light_extra is None:
            light_extra = config.get_build("light_extra")

        subprocess.run(
            [str(tools_bin / "qbsp"), "-bsp2", "loyola.map"], cwd=REPO_ROOT, check=True
        )

        vis_cmd = [str(tools_bin / "vis")]
        if vis_mode == "fast":
            vis_cmd.append("-fast")
        vis_cmd.append("loyola.bsp")
        subprocess.run(vis_cmd, cwd=REPO_ROOT, check=True)

        light_cmd = [str(tools_bin / "light")]
        if light_extra:
            light_cmd.append("-extra")
        light_cmd.append("loyola.bsp")
        subprocess.run(light_cmd, cwd=REPO_ROOT, check=True)

        if deploy:
            maps_dir = Path("/Applications/id1/maps")
            maps_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO_ROOT / "loyola.bsp", maps_dir)
            shutil.copy(REPO_ROOT / "loyola.lit", maps_dir)
            typer.echo(f"Deployed to {maps_dir}")
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except subprocess.CalledProcessError as exc:
        typer.echo(
            f"{exc.cmd[0]} exited with code {exc.returncode} — see output above.",
            err=True,
        )
        raise typer.Exit(code=exc.returncode or 1) from exc
    except OSError as exc:
        typer.echo(f"Build/deploy failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("Build complete.")
