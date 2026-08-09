"""Texture-name constants used throughout the map generator.

The world sky comes from the ``sky`` build setting, which is a plain WAD2
texture name (``sky4``, ``sky_z1``, ...) validated against the project's WADs
by ``build_presets.is_valid_sky``.

:data:`SKYBOX` is the separate ``skybox`` build setting: the name of a six-image
environment skybox installed in the engine's ``gfx/env`` directory (see
``quake_loyola.skyboxes``). It is not a texture — when set, it becomes the
``sky`` *worldspawn key* (which engines read as a skybox name, never as a
texture name) and the engine draws it through the sky faces instead of
:attr:`Textures.SKY`. Empty means "no skybox", and the key is then omitted.
"""

from ..config import get_build as _get_build
from ..skyboxes import skybox_worldspawn_value as _skybox_worldspawn_value

SKYBOX = str(_get_build("skybox"))

#: What :data:`SKYBOX` has to be spelled as in worldspawn. Engines glue the
#: face suffix straight onto this (``gfx/env/`` + value + ``rt``), so it
#: carries the pack's trailing separator: ``mak_sunset1`` -> ``mak_sunset1_``.
SKYBOX_WORLDSPAWN = _skybox_worldspawn_value(SKYBOX)


class Textures:
    BRICK = "bricka2_1"
    BRICK_KH = "city6_8"
    BUILDING = "city2_1"
    CEMENT = "sfloor3_2"
    BANNER = "{TF_Banner1"  # from mg1.wad; masked (alpha) hanging banner
    CURB = "stn_t04a_wht1"  # from makkon_stone.wad; Ennis Rd curb slabs
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
    ROOF_KH = "gn_grey2"  # from alkaline.wad; KH roof deck
    JOINT_METAL = "gn_grey2"  # from alkaline.wad; bridge deck expansion-joint strip
    JOINT_GAP = "black"  # from quake101.wad; dark shadow-gap seam between joint plates
    SHELF = "shelf_1"
    SIDEWALK = "sfloor3_2"
    SIDEWALK_JOINT = JOINT_GAP  # dark shadow-gap seam between sidewalk tiles
    SKY = _get_build("sky")
    STONE = "sfloor3_2"
    TELEPORT = "*teleport"
    #: For brush entities the player never sees. Vanilla triggers zero their
    #: modelindex so nothing is drawn regardless, but the texture still picks
    #: the face's compile behaviour -- so it must not be SKY, which would put
    #: the trigger's faces into the map's sky and show the skybox through them.
    TRIGGER = "trigger"
    WHITE_STONE = "stn_f14_wht1"  # from makkon_stone.wad
    WINDOW_KH = "{win01_1brk1b"  # from ad.wad; masked (alpha) window pane texture
