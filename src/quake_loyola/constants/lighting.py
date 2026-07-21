"""Time-of-day lighting/fog presets for worldspawn (LightingPreset, FogDensity).

The active preset is chosen via the ``lighting_preset`` build setting (see
``config.BUILD_DEFAULTS``) — override it with
``ql conf set lighting_preset <name>`` (one of the keys in
``LIGHTING_PRESETS``, e.g. ``dawn``, ``midday``, ``golden_hour``, ``dusk``,
``overcast``, ``night``, ``bright``, ``afternoon``) or by editing ql.toml.

The fog *density* (independent of the preset's fog color) is controlled by
the ``fog_density`` build setting — ``"default"`` (use the preset's own
density), one of the named :class:`FogDensity` levels (``off``, ``low``,
``med``, ``high``), or a numeric string for a custom density. Set via
``ql conf set fog_density <value>``.
"""

from dataclasses import dataclass

from ..config import get_build as _get_build


@dataclass
class LightingPreset:
    """All worldspawn lighting and fog fields for a single time-of-day."""

    ambient: str
    sunlight: str
    sunlight_color: str
    sunlight_dir: str  # "pitch yaw" — pitch = elevation above horizon, yaw = azimuth
    sunlight_penumbra: str
    fog: str  # "density r g b"

    def to_worldspawn(self) -> dict:
        # NOTE: ericw-tools' light reads "_minlight" (not "ambient") for the
        # global fill light, and "_sunlight_mangle" as "yaw pitch roll" (not
        # "_sunlight_dir" as "pitch yaw") for the sun direction. Both of the old
        # key names were silently ignored by light, so ambient fill was always 0
        # and the sun always defaulted to straight down regardless of preset.
        pitch, yaw = self.sunlight_dir.split()
        mangle = f"{yaw} {pitch} 0"
        return {
            "_minlight": self.ambient,
            "_sunlight": self.sunlight,
            "_sunlight_color": self.sunlight_color,
            "_sunlight_mangle": mangle,
            "_sunlight_penumbra": self.sunlight_penumbra,
            "_fog": self.fog,
        }


class FogDensity:
    OFF = 0.00
    LOW = 0.03
    MED = 0.06
    HIGH = 0.10


# Named `fog_density` build-setting values that map to a FogDensity level —
# used by both the CLI (validation) and the lookup below.
FOG_DENSITY_NAMES: dict[str, float] = {
    "off": FogDensity.OFF,
    "low": FogDensity.LOW,
    "med": FogDensity.MED,
    "high": FogDensity.HIGH,
}


def make_fog(density: float, r: float, g: float, b: float) -> str:
    """Build a _fog worldspawn string from a FogDensity level and RGB color (0.0–1.0)."""
    return f"{density} {r} {g} {b}"


LIGHTING_PRESETS: dict[str, LightingPreset] = {
    "dawn": LightingPreset(
        ambient="30",
        sunlight="120",
        sunlight_color="255 200 140",  # pale orange
        sunlight_dir="8 -90",  # low on the eastern horizon
        sunlight_penumbra="40",
        fog=make_fog(FogDensity.LOW, 0.6, 0.5, 0.4),
    ),
    "midday": LightingPreset(
        ambient="90",
        sunlight="140",
        sunlight_color="255 245 210",  # warm white
        sunlight_dir="60 -60",
        sunlight_penumbra="30",
        fog=make_fog(FogDensity.LOW, 0.5, 0.5, 0.6),
    ),
    "golden_hour": LightingPreset(
        ambient="40",
        sunlight="160",
        sunlight_color="255 180 80",  # deep amber
        sunlight_dir="10 -120",  # low on the western horizon
        sunlight_penumbra="40",
        fog=make_fog(FogDensity.MED, 0.6, 0.4, 0.3),
    ),
    "dusk": LightingPreset(
        ambient="20",
        sunlight="100",
        sunlight_color="200 120 60",  # dusky orange-red
        sunlight_dir="5 -120",  # just below the horizon
        sunlight_penumbra="50",
        fog=make_fog(FogDensity.MED, 0.4, 0.3, 0.4),
    ),
    "overcast": LightingPreset(
        ambient="120",
        sunlight="0",
        sunlight_color="200 210 220",  # cool grey-white
        sunlight_dir="90 0",
        sunlight_penumbra="60",
        fog=make_fog(FogDensity.MED, 0.5, 0.5, 0.55),
    ),
    "night": LightingPreset(
        ambient="5",
        sunlight="20",
        sunlight_color="180 200 255",  # cool moonlight blue
        sunlight_dir="15 120",  # low moon, opposite side from sun
        sunlight_penumbra="10",
        fog=make_fog(FogDensity.HIGH, 0.05, 0.05, 0.15),  # dark blue-black
    ),
    "bright": LightingPreset(
        ambient="120",
        sunlight="255",
        sunlight_color="255 255 240",  # brilliant white with slight warmth
        sunlight_dir="75 -45",  # high sun, near overhead
        sunlight_penumbra="20",
        fog=make_fog(FogDensity.OFF, 0.5, 0.5, 0.6),
    ),
    "afternoon": LightingPreset(
        ambient="75",
        sunlight="160",
        sunlight_color="255 220 170",  # warm afternoon white
        sunlight_dir="35 -180",  # ~35° altitude, sun due south (Baltimore ~39°N)
        sunlight_penumbra="25",
        fog=make_fog(FogDensity.LOW, 0.5, 0.5, 0.6),
    ),
}

_lighting_preset_setting = _get_build("lighting_preset")
if _lighting_preset_setting not in LIGHTING_PRESETS:
    raise ValueError(
        f"lighting_preset {_lighting_preset_setting!r} is not a known preset "
        f"(known: {sorted(LIGHTING_PRESETS)}). Fix it with `ql conf set "
        "lighting_preset <name>` or `ql conf reset`."
    )
LIGHTING = LIGHTING_PRESETS[_lighting_preset_setting]

# "default" -> use the active preset's own fog density; a named level
# (off/low/med/high) -> that FogDensity constant; anything else -> parsed as
# a custom float. See config.BUILD_DEFAULTS["fog_density"] / cli.py for the
# validation that keeps this branch limited to those three shapes.
_fog_density_setting = _get_build("fog_density")
if _fog_density_setting == "default":
    FOG_DENSITY: float | None = None
elif _fog_density_setting in FOG_DENSITY_NAMES:
    FOG_DENSITY = FOG_DENSITY_NAMES[_fog_density_setting]
else:
    try:
        FOG_DENSITY = float(_fog_density_setting)
    except ValueError:
        raise ValueError(
            f"fog_density {_fog_density_setting!r} must be 'default', one "
            f"of {sorted(FOG_DENSITY_NAMES)}, or a numeric string. Fix it "
            "with `ql conf set fog_density <value>` or `ql conf reset`."
        ) from None

# Sorted list of valid `lighting_preset` build-setting values — used by the
# `ql conf set lighting_preset <name>` CLI to validate input and by docs/help
# text without needing to import the full LIGHTING_PRESETS dict.
LIGHTING_PRESET_NAMES: list[str] = sorted(LIGHTING_PRESETS)
