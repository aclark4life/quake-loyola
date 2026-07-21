"""The Textures table of WAD texture names used across every area module.

The sky texture (used on every sky-textured face in bridge.py/streets.py,
and as the worldspawn "sky" field) is selectable via the ``sky_preset``
build setting — ``"day"`` (default, quake101.wad's bright daytime ``sky4``) or
``"night"`` (quake101.wad's dark nighttime ``sky1``). Override with
``ql conf set sky_preset night`` or by editing ql.toml.
"""

from ..config import get_build as _get_build

# Named `sky_preset` build-setting values that map to a WAD sky texture name.
SKY_PRESETS: dict[str, str] = {
    "day": "sky4",  # quake101.wad — bright daytime sky
    "night": "sky1",  # quake101.wad — dark nighttime sky
}

# Sorted list of valid `sky_preset` build-setting values — used by the
# `ql conf set sky_preset <name>` CLI to validate input and by docs/help
# text without needing to import the full SKY_PRESETS dict.
SKY_PRESET_NAMES: list[str] = sorted(SKY_PRESETS)


class Textures:
    BRICK = "bricka2_1"
    BRICK_KH = "city6_8"
    BUILDING = "city2_1"
    CEMENT = "sfloor3_2"
    FENCE = "metal4_4"
    CENTERLINE = (
        "win_fbylw_01"  # fullbright yellow, stand-in for a yellow line marking texture
    )
    PARKING_STRIPE = (
        "win_fbblu_01"  # named "blu" but reads more white than blue in-game, so
        # it works fine as a stand-in for the white parking-lane stripe texture
    )
    ENNIS_PILLAR = "stn_f14_wht1"  # from makkon_stone.wad
    FLOOR = "sfloor3_2"
    FLOOR1 = "floor01_5lrg"  # from ad.wad — bridge deck walking surface
    DECK_EDGE = "dk3_floor1a"  # from ad.wad — thin edge strip along the deck walk
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
