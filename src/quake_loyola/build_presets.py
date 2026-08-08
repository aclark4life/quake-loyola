"""Names of valid values for CLI/``ql.toml``-configurable build settings.

Kept independent of :mod:`quake_loyola.constants` (which owns the full
preset *data* — sunlight colors/angles, texture names, etc.) so that
:mod:`quake_loyola.config` can validate every ``[build]`` value up front
when ``ql.toml`` is loaded, and :mod:`quake_loyola.cli` can display/validate
those values, without importing (and thereby initializing) the whole
``constants`` package for config-only commands.

``constants.lighting`` and ``constants.textures`` import the name tuples
from here rather than redefining them, so there is a single source of
truth; each asserts its preset dict's keys match at import time.
"""

import math
import re

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

SKY_PRESET_NAMES: tuple[str, ...] = ("day", "night")

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


def is_valid_sky_preset(value: str) -> bool:
    """Return True if ``value`` is a valid ``sky_preset`` build setting.

    Valid values are one of :data:`SKY_PRESET_NAMES` (looked up in
    ``Textures.SKY_PRESETS``), or a raw WAD2 skybox texture name (e.g.
    ``sky_z1``, ``sky3_1``) used as-is — letting any texture from a loaded
    WAD be tried as the world sky without adding a formal named preset for
    it.
    """
    return value in SKY_PRESET_NAMES or bool(_SKY_TEXTURE_NAME_RE.fullmatch(value))
