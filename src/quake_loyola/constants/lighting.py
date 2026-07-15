"""Time-of-day lighting/fog presets for worldspawn (LightingPreset, FogDensity)."""

from dataclasses import dataclass


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

LIGHTING = LIGHTING_PRESETS["bright"]
FOG_DENSITY: float | None = None  # use preset fog density
