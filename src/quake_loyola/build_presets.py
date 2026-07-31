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

# Build settings whose validation is simply "must be one of these strings".
# Single source of truth for both `config._validate_build_values` (ql.toml
# load-time validation) and `cli._validate_one` (CLI-argument validation),
# so the two can't drift out of sync with each other.
BUILD_ENUM_SETTINGS: dict[str, tuple[str, ...]] = {
    "vis_mode": VIS_MODES,
    "lighting_preset": LIGHTING_PRESET_NAMES,
    "sky_preset": SKY_PRESET_NAMES,
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
