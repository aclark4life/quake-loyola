"""Valid values for the CLI/``ql.toml``-configurable ``[build]`` settings.

Kept independent of :mod:`quake_loyola.constants` (which owns the full
preset *data* — sunlight colors/angles, texture names, etc.) so that
:mod:`quake_loyola.config` can validate every ``[build]`` value up front
when ``ql.toml`` is loaded, and :mod:`quake_loyola.cli` can display/validate
those values, without importing (and thereby initializing) the whole
``constants`` package for config-only commands.

``constants.lighting`` imports the name tuples from here rather than
redefining them, so there is a single source of truth; it asserts its preset
dict's keys match at import time.

``lighting_preset`` is the one genuine *preset* left: it sets six correlated
worldspawn fields (sun color, sun angle, ambient, fog color, ...) that are
painful to set individually. Everything else here is a direct value — ``sky``
is a plain texture name, ``fog_density`` a level or a number.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from .skyboxes import is_valid_skybox_name, skybox_names
from .wads import SKY_TEXTURE_PREFIX, sky_texture_names

VIS_MODES: tuple[str, ...] = ("fast", "full")

LIGHTING_PRESET_NAMES: tuple[str, ...] = (
    "afternoon",
    "bright",
    "dawn",
    "dusk",
    "golden_hour",
    "midday",
    "night",
    "overcast",
)

FOG_DENSITY_NAMES: tuple[str, ...] = ("off", "low", "med", "high")

#: Former ``sky_preset`` values, kept only to migrate an older ``ql.toml``
#: (see ``config._migrate_legacy_build``). Set ``sky`` to a texture name
#: directly instead.
LEGACY_SKY_PRESETS: dict[str, str] = {"day": "sky4", "night": "sky1"}

# WAD2 texture names are ASCII, up to 15 chars (16-byte name field minus the
# NUL terminator), conventionally lowercase alnum/underscore — matches every
# sky texture across the project's WADs (sky1, sky4, sky3_1, sky_z1, ...).
_SKY_TEXTURE_NAME_RE = re.compile(r"[A-Za-z0-9_]{1,15}")

# Build settings whose validation is simply "must be one of these strings".
# Single source of truth for both `config._validate_build_values` (ql.toml
# load-time validation) and `cli._validate_one` (CLI-argument validation),
# so the two can't drift out of sync with each other.
BUILD_ENUM_SETTINGS: dict[str, tuple[str, ...]] = {
    "vis_mode": VIS_MODES,
    "lighting_preset": LIGHTING_PRESET_NAMES,
}


def is_valid_fog_density(value: str) -> bool:
    """Return True if ``value`` is a valid ``fog_density`` build setting.

    Valid values are ``"default"``, one of :data:`FOG_DENSITY_NAMES`, or a
    string parseable as a finite, non-negative float (a custom density
    override — fog density has no meaning as ``nan``/``inf``/negative).
    """
    if value == "default" or value in FOG_DENSITY_NAMES:
        return True
    try:
        parsed = float(value)
    except ValueError:
        return False
    return math.isfinite(parsed) and parsed >= 0


def is_valid_sky(value: str, root: Path | None = None) -> bool:
    """Return True if ``value`` names a usable sky texture.

    ``sky`` is a plain WAD2 texture name (``sky4``, ``sky_z1``, ...) rather
    than a named preset. A name must be syntactically valid *and* start with
    :data:`~quake_loyola.wads.SKY_TEXTURE_PREFIX`, since qbsp only compiles
    ``sky*`` textures as sky.

    When ``root`` is given, the name is additionally checked against the
    textures actually present in the project's WADs, so a typo is caught at
    ``ql conf set`` time instead of surfacing as a missing-texture warning
    during compilation. If no WAD can be read (they aren't downloaded yet,
    say) that check is skipped rather than rejecting every value.
    """
    if not _SKY_TEXTURE_NAME_RE.fullmatch(value):
        return False
    if not value.lower().startswith(SKY_TEXTURE_PREFIX):
        return False
    if root is None:
        return True
    available = sky_texture_names(root)
    return not available or value in available


def sky_options(root: Path | None = None) -> list[str]:
    """Return the sky textures available in the project's WADs, sorted.

    Empty when ``root`` is None or no WAD could be read; callers should fall
    back to describing the expected format instead of listing values.
    """
    if root is None:
        return []
    return sorted(sky_texture_names(root))


def is_valid_skybox(value: str) -> bool:
    """Return True if ``value`` names a usable environment skybox.

    ``""`` is valid and means "no skybox" — the engine falls back to drawing
    the ``sky`` texture, which is the project's default. Any other value must
    be a syntactically valid name *and*, when the ``gfx/env`` directory can be
    read, one that is actually installed there, so a typo is caught at
    ``ql skybox`` time instead of showing up as a black sky in game. If the
    directory is missing (Quake isn't installed on this machine, say) that
    check is skipped rather than rejecting every value.
    """
    if value == "":
        return True
    if not is_valid_skybox_name(value):
        return False
    available = skybox_names()
    return not available or value in available


def skybox_options() -> list[str]:
    """Return the skyboxes installed in ``gfx/env``, sorted.

    Empty when none are installed or the directory can't be read; callers
    should fall back to describing the expected format instead of listing
    values.
    """
    return sorted(skybox_names())
