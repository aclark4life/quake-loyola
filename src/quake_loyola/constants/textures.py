"""Texture-name constants used throughout the map generator.

``sky_preset`` selects the world sky texture from ``SKY_PRESETS``.
"""

from ..build_presets import SKY_PRESET_NAMES as _SKY_PRESET_NAME_TUPLE
from ..config import get_build as _get_build

# Build-setting values for ``sky_preset``.
SKY_PRESETS: dict[str, str] = {
    "day": "sky4",  # quake101.wad daytime sky
    "night": "sky1",  # quake101.wad nighttime sky
}

# Sorted valid ``sky_preset`` names for CLI validation and help text.
SKY_PRESET_NAMES: list[str] = sorted(SKY_PRESETS)

# ``config.py`` validates ``sky_preset`` against ``build_presets`` before this
# module is ever imported, so this is an internal-consistency check (a
# mismatch here is a bug in this file) rather than user-facing validation.
assert SKY_PRESET_NAMES == sorted(_SKY_PRESET_NAME_TUPLE), (
    "SKY_PRESETS keys drifted from build_presets.SKY_PRESET_NAMES"
)


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
    FLOOR1 = "TF_Floor5_03"  # from mg1.wad; bridge deck walking surface
    DECK_EDGE = "dk3_floor1a"  # from ad.wad; deck edge strip
    GROUND = "ground1_1"
    HINT = "hint"
    MULCH = "grave13c"
    LAVA = "*lava1"
    PILLAR = "city6_8"
    PIER_STONE = "TF_Stone4"  # from mg1.wad; shared by bridge piers and KH walls
    FLOOR_KH = "sfloor3_2"
    RAIL = "metal5_4"
    ROAD = "thantech10_9"
    GABLE = "woodc1_cwht01"
    ROOF = "roofkell1"
    SHELF = "shelf_1"
    SIDEWALK = "sfloor3_2"
    SIDEWALK_JOINT = FENCE  # same texture as the iron fence; expansion-joint filler
    SKY = SKY_PRESETS[_get_build("sky_preset")]
    STONE = "sfloor3_2"
    TELEPORT = "*teleport"
    WHITE_STONE = "stn_f14_wht1"  # from makkon_stone.wad
    WINDOW_KH = "{win01_1brk1b"  # from ad.wad; masked (alpha) window pane texture
