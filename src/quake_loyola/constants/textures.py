"""Texture-name constants used throughout the map generator.

``sky_preset`` selects the world sky texture from ``SKY_PRESETS``.
"""

from ..config import get_build as _get_build

# Build-setting values for ``sky_preset``.
SKY_PRESETS: dict[str, str] = {
    "day": "sky4",  # quake101.wad daytime sky
    "night": "sky1",  # quake101.wad nighttime sky
}

# Sorted valid ``sky_preset`` names for CLI validation and help text.
SKY_PRESET_NAMES: list[str] = sorted(SKY_PRESETS)


class Textures:
    BRICK = "bricka2_1"
    BRICK_KH = "city6_8"
    BUILDING = "city2_1"
    CEMENT = "sfloor3_2"
    FENCE = "metal4_4"
    CENTERLINE = "win_fbylw_01"  # Fullbright yellow stand-in for centerline paint.
    PARKING_STRIPE = "win_fbblu_01"  # Reads as a light parking-stripe texture in-game.
    ENNIS_PILLAR = "stn_f14_wht1"  # from makkon_stone.wad
    FLOOR = "sfloor3_2"
    FLOOR1 = "floor01_5lrg"  # from ad.wad; bridge deck walking surface
    DECK_EDGE = "dk3_floor1a"  # from ad.wad; deck edge strip
    FLOOR_KH = "sfloor3_2"
    GROUND = "ground1_1"
    HINT = "hint"
    MULCH = "grave13c"
    LAVA = "*lava1"
    PILLAR = "city6_8"
    RAIL = "metal5_4"
    ROAD = "thantech10_9"
    GABLE = "woodc1_cwht01"
    ROOF = "roofkell1"
    SHELF = "shelf_1"
    SIDEWALK = "sfloor3_2"
    SKY = SKY_PRESETS.get(_get_build("sky_preset"), None)
    if SKY is None:
        raise ValueError(
            f"sky_preset {_get_build('sky_preset')!r} is not a known preset "
            f"(known: {SKY_PRESET_NAMES}). Fix it with `ql conf set sky_preset "
            "<name>` or `ql conf reset`."
        )
    STONE = "sfloor3_2"
    TELEPORT = "*teleport"
    WHITE_STONE = "stn_f14_wht1"  # from makkon_stone.wad
