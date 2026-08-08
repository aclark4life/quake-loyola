"""Texture-name constants used throughout the map generator.

The world sky comes from the ``sky`` build setting, which is a plain WAD2
texture name (``sky4``, ``sky_z1``, ...) validated against the project's WADs
by ``build_presets.is_valid_sky``.
"""

from ..config import get_build as _get_build


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
    WHITE_STONE = "stn_f14_wht1"  # from makkon_stone.wad
    WINDOW_KH = "{win01_1brk1b"  # from ad.wad; masked (alpha) window pane texture
