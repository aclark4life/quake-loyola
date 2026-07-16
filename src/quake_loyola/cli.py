"""``ql`` — Typer CLI for configuring and running quake-loyola's build.

Run via the repo-root ``ql`` wrapper script (``./ql ...``), which puts
``src/`` and the repo root on ``sys.path`` the same way ``generate_map.py``
does, so no ``pip install`` step is required.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import typer

from . import config

# Resolved from cwd (not the installed package location) — `ql` is meant to
# be run from the repo root (same convention as `just`), whether installed
# via `pip install -e .` or run in-place via `sys.path` insertion.
REPO_ROOT = Path.cwd()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(
    help="quake-loyola build CLI — configure module/light flags and run the build.",
    context_settings=CONTEXT_SETTINGS,
)
config_app = typer.Typer(
    help="View or change build-time settings stored in ql.toml.",
    context_settings=CONTEXT_SETTINGS,
)
app.add_typer(config_app, name="conf")


def _parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in ("true", "1", "yes", "on"):
        return True
    if v in ("false", "0", "no", "off"):
        return False
    raise typer.BadParameter(f"Expected a boolean (true/false), got {value!r}")


@config_app.command("show")
def config_show() -> None:
    """List every flag and build setting, its effective value, and its default."""
    exists = config.CONFIG_PATH.exists()
    typer.echo(
        f"Config file: {config.CONFIG_PATH}"
        + ("" if exists else " (not created yet — showing defaults)")
    )
    typer.echo("\n[flags]")
    for name in sorted(config.DEFAULTS):
        value = config.get(name)
        default = config.DEFAULTS[name]
        marker = "*" if value != default else " "
        note = (
            "  (master: forces every BRIDGE_ENABLED_<section> flag on)"
            if name == "BRIDGE_ENABLED"
            else ""
        )
        typer.echo(f" {marker} {name:<34} = {str(value):<5} (default: {default}){note}")
    typer.echo("\n[build]")
    for name in sorted(config.BUILD_DEFAULTS):
        value = config.get_build(name)
        default = config.BUILD_DEFAULTS[name]
        marker = "*" if value != default else " "
        typer.echo(f" {marker} {name:<34} = {str(value):<5} (default: {default})")
    typer.echo("\n(* = overridden from its default via ql.toml)")


@config_app.command("get")
def config_get(name: str) -> None:
    """Print the effective value of a single flag or build setting."""
    name_u = name.upper()
    if name_u in config.DEFAULTS:
        typer.echo(str(config.get(name_u)))
    elif name in config.BUILD_DEFAULTS:
        typer.echo(str(config.get_build(name)))
    else:
        typer.echo(
            f"Unknown setting {name!r}. Run `ql conf show` for the full list.",
            err=True,
        )
        raise typer.Exit(code=1)


@config_app.command("set")
def config_set(name: str, value: str) -> None:
    """Set a flag (true/false) or build setting, persisted to ql.toml.

    Examples:
        ql conf set KNOTT_HALL_ENABLED true
        ql conf set bridge_enabled true       # names are case-insensitive
        ql conf set vis_mode full
        ql conf set light_extra true

    Note: BRIDGE_ENABLED is a convenience master switch — setting it true
    forces every BRIDGE_ENABLED_<section> flag (west_approach, center_span,
    east_approach, kh_span, east_ext) on too, overriding their individual
    settings.
    """
    name_u = name.upper()
    if name_u in config.DEFAULTS:
        parsed = _parse_bool(value)
        config.set_flag(name_u, parsed)
        typer.echo(f"{name_u} = {parsed}")
    elif name in config.BUILD_DEFAULTS:
        if name == "vis_mode":
            if value not in ("fast", "full"):
                raise typer.BadParameter("vis_mode must be 'fast' or 'full'")
            parsed_build: object = value
        else:
            parsed_build = _parse_bool(value)
        config.set_build(name, parsed_build)
        typer.echo(f"{name} = {parsed_build}")
    else:
        typer.echo(
            f"Unknown setting {name!r}. Run `ql conf show` for the full list.",
            err=True,
        )
        raise typer.Exit(code=1)


@config_app.command("reset")
def config_reset(
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip the confirmation prompt."
    ),
) -> None:
    """Delete ql.toml, reverting every flag/setting to its default."""
    if not config.CONFIG_PATH.exists():
        typer.echo("No ql.toml found — already using defaults.")
        raise typer.Exit()
    if not yes and not typer.confirm(
        f"Delete {config.CONFIG_PATH} and restore all defaults?"
    ):
        raise typer.Abort()
    config.reset()
    typer.echo("Reset to defaults.")


@config_app.command("path")
def config_path() -> None:
    """Print the path to ql.toml (whether or not it exists yet)."""
    typer.echo(str(config.CONFIG_PATH))


@app.command("gen")
def generate() -> None:
    """Write loyola.map from the current config-driven flag settings."""
    from .mapgen import main as _generate_main

    _generate_main()


@app.command()
def build(
    deploy: bool = typer.Option(
        True,
        help="Copy the compiled .bsp/.lit into the Quake maps directory afterwards.",
    ),
) -> None:
    """Generate + compile the map, honoring [build] settings from ql.toml
    (vis_mode: fast/full, light_extra: bool) — same tool pipeline as
    `just compile`/`just compile-fast`, but configurable without editing the
    justfile."""
    generate()

    tools_bin_candidates = sorted(REPO_ROOT.glob(".tools/ericw-tools-*/bin"))
    if not tools_bin_candidates:
        typer.echo(
            "ericw-tools not found under .tools/ — run `just install-tools` first.",
            err=True,
        )
        raise typer.Exit(code=1)
    tools_bin = tools_bin_candidates[0]

    vis_mode = config.get_build("vis_mode")
    light_extra = config.get_build("light_extra")

    subprocess.run([str(tools_bin / "qbsp"), "loyola.map"], cwd=REPO_ROOT, check=True)

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

    typer.echo("Build complete.")
