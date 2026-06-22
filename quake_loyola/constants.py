import math
from dataclasses import dataclass

ARCH_RIN = 96
ARCH_ROUT = 136
ARCH_SLAB_W = 32
ARCH_STILT_H = 96

A_SEGS = 16

BRIDGE_ARCH_RISE = 144
BRIDGE_ACCESS_WALK_CENTER_X = 2120
BRIDGE_ACCESS_WALK_HALF_W = 32
BRIDGE_ACCESS_WALK_NORTH_OFFSET = 80
BRIDGE_ACCESS_WALK_PIER_CLEARANCE = 96
BRIDGE_BLK_H = 36
BRIDGE_BLK_HW = 24
BRIDGE_BLK_OVH = 0
BRIDGE_BLK_PIER_CLEARANCE = 4
BRIDGE_DECK_EAST_RECESS = 1
BRIDGE_DZ1, BRIDGE_DZ2 = (
    224,
    240,
)
BRIDGE_EAST_SHIFT_START = 0.0
BRIDGE_EAST_SPAN_ANGLE = 12.0
BRIDGE_FASCIA_PX_W, BRIDGE_FASCIA_PX_H = 4, 4
BRIDGE_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
BRIDGE_PAR_H = 40
BRIDGE_PIL_BASE_CAP_H = 6
BRIDGE_PIL_BASE_CAP_OVH = 5
BRIDGE_PIL_BASE_H = 24
BRIDGE_PIL_BASE_RAMP_H = 40
BRIDGE_PIL_CAP_H = 12
BRIDGE_PIL_CAP_IN_OVH = 4
BRIDGE_PIL_CAP_OUT_OVH = 20
BRIDGE_PIL_CAP_OVHNTR_R = (160, 90)
BRIDGE_PIL_EXTRA = 64
BRIDGE_PIER_FILL_OFFSET = 16
BRIDGE_PIL_INNER_R = (160, 84)
BRIDGE_PIL_OUTER_R = (140, 72)
BRIDGE_PIL_OVERHANG = 16
BRIDGE_PIL_PYR_H = 20
BRIDGE_PIL_PYR_W = 45
BRIDGE_SEG_SPAN_W = 32
BRIDGE_SQ_D = 1
BRIDGE_SQ_HH = 6
BRIDGE_SQ_HW = 8
BRIDGE_SUPPORT_BEAM_H = 20
BRIDGE_SUPPORT_HALF_W = 16
BRIDGE_SUPPORT_PIER_HALF_W = 20
BRIDGE_TELEPORT_ARCH_CLEARANCE = 8
BRIDGE_TELEPORT_ARCH_X1_OFFSET = 2
BRIDGE_TELEPORT_ARCH_X2_OFFSET = 18
BRIDGE_TELEPORT_DEST_Z = 40
BRIDGE_TORCH_CUP_H = 4
BRIDGE_TORCH_CUP_HW = 5
BRIDGE_TORCH_POST_H = 16
BRIDGE_TORCH_POST_HW = 3
BRIDGE_TUBE_GAP = 12
BRIDGE_TUBE_HW = 2
BRIDGE_TUBE_RISE = 10
BRIDGE_WALK_WALL = 32
BRIDGE_Y1, BRIDGE_Y2 = -136, 136

CHARLES_ARCH_RIN = 256
CHARLES_ARCH_RIN_PRE = 256
CHARLES_ARCH_ROUT_PRE = 312
CHARLES_ARCH_STILT = 96
CHARLES_ARCH_STILT_PRE = 96
CHARLES_ARCH_TRIG_INSET = 8
CHARLES_ARCH_W = 48
CHARLES_ARCH_W_PRE = 48
CHARLES_CRN_SEGS = 12
CHARLES_LAMP_POST_EAST_SETBACK = 48
CHARLES_PLT_H = 12
CHARLES_PLT_SPEED = 180
CHARLES_PLT_W = 128
CHARLES_RAMP_W = 64
CHARLES_WALK_H = 8
CHARLES_WALK_W = 80

DORM_DEPTH = 450
DORM_FENCE_OFFSET = 216
DORM_FRONT_WALKWAY_FENCE_OFFSET = 40
DORM_FRONT_WALKWAY_H = 6
DORM_FRONT_WALKWAY_W = 96
DORM_GABLE_DEPTH = 6
DORM_INNER_DOOR_H = 128
DORM_INNER_DOOR_HW = 56
DORM_BRICK_PILLAR_CAP_H = 10
DORM_BRICK_PILLAR_CAP_OVH = 1
DORM_BRICK_PILLAR_GAP = 96
DORM_BRICK_PILLAR_H_OFFSET = 80
DORM_BRICK_PILLAR_PROUD = 6
DORM_BRICK_PILLAR_SEPARATION = 380
DORM_BRICK_PILLAR_W = 56
DORM_BRICK_WALL_HALF_W = 12
DORM_BRICK_GATE_H = 96
DORM_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)
DORM_DOOR_OFF = 160
DORM_DOOR_W = 80
DORM_EMB_X2 = -1146
DORM_ENT_H = 100
DORM_ENT_HW = 48
DORM_FLOORS = 3
DORM_SLAB_T = 16
DORM_WALL = 16
DORM_WIN_HH = 44
DORM_WIN_HW = 36
DORM_WIN_MARGIN = 0  # gap between window frame bar and opening edge (0 = flush)
DORM_WIN_W, DORM_WIN_H, DORM_WIN_T = 20, 28, 3

DRAW_BRIDGE_FASCIA_TEXT = True

ENNIS_CURB_W = 8
ENNIS_CEMENT_WALL_CAP_H = 6
ENNIS_CEMENT_WALL_CAP_OVH = 2
ENNIS_CEMENT_WALL_H = 32
ENNIS_CEMENT_WALL_LAMP_POST_H = 160
ENNIS_CEMENT_WALL_PILLAR_EXTRA_H = 16
ENNIS_CEMENT_WALL_PILLAR_HW = 14
ENNIS_GATE_FENCE_BAR_T = 2
ENNIS_GATE_FENCE_HEIGHT = 96
ENNIS_GATE_FENCE_POST_W = 8
ENNIS_GATE_FENCE_SPACING = 16
ENNIS_GATE_FENCE_TOP_RAIL_DROP = 28
ENNIS_GATE_FENCE_TOP_RAIL_T = 2
ENNIS_PANEL_GAP = 8
ENNIS_PANEL_INNER_H = 12
ENNIS_PANEL_INNER_W = 28
ENNIS_PANEL_OUTER_H = 28
ENNIS_PANEL_OUTER_W = 48
ENNIS_HW = 160
ENNIS_PIL_BELL2_H = 27
ENNIS_PIL_BELL2_HW = (
    19  # tapered top section half-width (wider than before, less than post)
)
ENNIS_PIL_CAP_H = 3
ENNIS_PIL_CAP_OVH = 1
ENNIS_PIL_HW = 22
ENNIS_PIL_POST_H = 81
ENNIS_WALL_H = 96
ENNIS_WALL_PIL_H = 120
ENNIS_WALL_PIL_HW = 14
ENNIS_WALL_T = 8
ENNIS_WALL_X_OFFSET = 48

FASCIA_FONT = {
    "A": [0b0110, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
    "B": [0b1110, 0b1001, 0b1110, 0b1001, 0b1110, 0b0000],
    "C": [0b0111, 0b1000, 0b1000, 0b1000, 0b0111, 0b0000],
    "D": [0b1110, 0b1001, 0b1001, 0b1001, 0b1110, 0b0000],
    "E": [0b1111, 0b1000, 0b1110, 0b1000, 0b1111, 0b0000],
    "F": [0b1111, 0b1000, 0b1110, 0b1000, 0b1000, 0b0000],
    "G": [0b0111, 0b1000, 0b1011, 0b1001, 0b0111, 0b0000],
    "H": [0b1001, 0b1001, 0b1111, 0b1001, 0b1001, 0b0000],
    "I": [0b1110, 0b0100, 0b0100, 0b0100, 0b1110, 0b0000],
    "J": [0b0011, 0b0001, 0b0001, 0b1001, 0b0110, 0b0000],
    "K": [0b1001, 0b1010, 0b1100, 0b1010, 0b1001, 0b0000],
    "L": [0b1000, 0b1000, 0b1000, 0b1000, 0b1111, 0b0000],
    "M": [0b1001, 0b1111, 0b1111, 0b1001, 0b1001, 0b0000],
    "N": [0b1001, 0b1101, 0b1011, 0b1001, 0b1001, 0b0000],
    "O": [0b0110, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
    "P": [0b1110, 0b1001, 0b1110, 0b1000, 0b1000, 0b0000],
    "R": [0b1110, 0b1001, 0b1110, 0b1010, 0b1001, 0b0000],
    "S": [0b0111, 0b1000, 0b0110, 0b0001, 0b1110, 0b0000],
    "T": [0b1111, 0b0100, 0b0100, 0b0100, 0b0100, 0b0000],
    "U": [0b1001, 0b1001, 0b1001, 0b1001, 0b0110, 0b0000],
    "V": [0b1001, 0b1001, 0b1001, 0b0110, 0b0110, 0b0000],
    "W": [0b1001, 0b1001, 0b1111, 0b1111, 0b1001, 0b0000],
    "X": [0b1001, 0b0110, 0b0110, 0b0110, 0b1001, 0b0000],
    "Y": [0b1001, 0b0110, 0b0100, 0b0100, 0b0100, 0b0000],
    " ": [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000],
}

FENCE_H = 96
FENCE_SPACING = 16
FENCE_TEX = "metal4_4"

FLOOR_Z1, FLOOR_Z2 = -16, 0

INDENT = 80

KNOTT_DRIVEWAY_HW = 128
KNOTT_ENABLED = True
KNOTT_FLOORS = 5
KNOTT_FLOOR_H = 160
KNOTT_MULLION_PRO = 12
KNOTT_MULLION_W = 12
KNOTT_BUILDING_W = 1032
KNOTT_OFFSET = 90
KNOTT_WEST_TO_ORIG_CX = 624
KNOTT_WEST_TO_PIER_X = 40
KNOTT_RAIL_H = 72
KNOTT_RAIL_TEX = "metal4_4"
KNOTT_ROOM_SPLITS = [-1072, -950, -1200, -850, -1300]
KNOTT_SHELF_D = 16
KNOTT_SHELF_H = 64
KNOTT_SHELF_W = 64
KNOTT_SIGN_PX_W, KNOTT_SIGN_PX_H = 2, 4
KNOTT_SIGN_TEXT = "MARION BURK KNOTT HALL"
KNOTT_SIGN_H = 48
KNOTT_SIGN_PADDING = 4
KNOTT_SIGN_Z_OFFSET = 20
KNOTT_SIDE_WINDOW_DIV_W = 12
KNOTT_SIDE_WINDOW_HALF_W = 120
KNOTT_SIDE_WINDOW_INNER_LEFT = 48
KNOTT_SIDE_WINDOW_INNER_RIGHT = 36
KNOTT_SIDE_WINDOW_PROTRUSION = 12
KNOTT_SHAFT_WALL = 8
KNOTT_STAIRS_HALF_N = 8
KNOTT_STAIR_CAP_RAISE = 16
KNOTT_STAIR_CAP_W = 24
KNOTT_STAIRS_POST_W = 4
KNOTT_STAIRS_RAIL_H = 72
KNOTT_STAIRS_RAIL_T = 4
KNOTT_STAIRS_STEP_R = KNOTT_FLOOR_H // (2 * KNOTT_STAIRS_HALF_N)
KNOTT_STAIRS_TREAD_X = 24
KNOTT_STAIR_OFFSET = 384
KNOTT_STAIR_RAIL_EXTENSION = 20
KNOTT_STAIR_RAIL_POST_D = 2
KNOTT_STAIR_RAIL_POST_W = 8
KNOTT_STEP_DEPTH = 24
KNOTT_STEP_N = 5
KNOTT_WALKWAY_ENABLED = True
KNOTT_WALL = 16
KNOTT_FRONT_WINDOW_HALF_W = 48
KNOTT_FRONT_WINDOW_MULLION_HALF_GAP = 6
KNOTT_Y1, KNOTT_Y2 = -1888, -256

PLAT_H = 8

BRIDGE_CENTER_PIER_SPAN = 1050
BRIDGE_OUTER_PIER_SPAN = 721
ROAD_DASH_LEN = 64
ROAD_GAP_LEN = 64
STREET_CHARLES_CURB_W = 8
STREET_DIV_HW = 4
STREET_ENNIS_DIV_HW = 16
STREET_SURFACE_T = 2
ROAD_X1, ROAD_X2 = -256, 256

SCALE = 15.108

SHOW_SUPPORTS = True
WORLD_EAST_BUFFER = 512


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
        return {
            "ambient": self.ambient,
            "_sunlight": self.sunlight,
            "_sunlight_color": self.sunlight_color,
            "_sunlight_dir": self.sunlight_dir,
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
        sunlight_dir="10 -90",  # low on the western horizon
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
}

LIGHTING = LIGHTING_PRESETS["night"]


class Textures:
    BRICK = "bricka2_1"
    CEMENT = "sfloor3_2"
    EXIT = "z_exit"
    DIVIDER = "sfloor3_2"
    FLOOR = "sfloor3_2"
    FLOOR_KH = "sfloor3_2"
    GROUND = "ground1_1"
    LAVA = "*lava1"
    PILLAR = "city2_7"
    RAIL = "metal5_4"
    ROAD = "azfloor1_1"
    GABLE = "woodc1_cwht01"
    ROOF = "roofkell1"
    SKY = "sky1"
    STONE = "sfloor3_2"
    TELEPORT = "*teleport"
    WALL = "city2_7"
    WHITE_STONE = "sfloor3_2"


@dataclass
class KnottSpec:
    floors: int
    floor_h: int
    wall_t: int
    x1: int
    x2: int
    y1: int
    y2: int
    driveway_hw: int


@dataclass
class BridgeSpec:
    x1: int
    x2: int
    y1: int
    y2: int
    arch_rise: int
    parapet_h: int
    walk_wall: int


@dataclass
class DormSpec:
    floor_h: int
    floors: int
    wall_t: int
    depth: int
    x1: int
    x2: int


# ── Derived / Dependent Constants ─────────────────────────────────────────────
KNOTT_ENT_HALF_W = 64
KNOTT_STAIR_LANDING_GAP = 16
KNOTT_EAST_PIER_FACE_OFFSET = 32
KNOTT_SHAFT_X_OFFSET = 16
KNOTT_SHAFT_W = 128
KNOTT_SHAFT_Y_OFFSET = 128
# Bridge north edge → Ennis south curb offset; ENNIS_NORTH_OFFSET then adds half-width.
ENNIS_BRIDGE_TO_SOUTH_EDGE = 640
ENNIS_NORTH_OFFSET = ENNIS_BRIDGE_TO_SOUTH_EDGE + ENNIS_HW
CHARLES_LAMP_POST_SETBACK = 160
CHARLES_PLATFORM_ROAD_OFFSET = 16
ROAD_VERGE_BUFFER = 32
DORM_PIER_FACE_OFFSET = 32
BRIDGE_LAMP_POST_CLEARANCE = 32

CHARLES_CRN_R = CHARLES_WALK_W
ENNIS_PIL_ZB = FLOOR_Z2
KNOTT_DRIVEWAY_CURB_CRN_R = CHARLES_WALK_W
KNOTT_DRIVEWAY_CURB_CRN_SEGS = CHARLES_CRN_SEGS
KNOTT_DRIVEWAY_CURB_WALK_W = CHARLES_WALK_W
KNOTT_DRIVEWAY_ZT_N = FLOOR_Z2
# Treat the Knott west face as the root X anchor; nearby anchors derive from it.
KNOTT_X1 = 1206
KNOTT_PIER_X = KNOTT_X1 + KNOTT_WEST_TO_PIER_X
KNOTT_ORIG_CX = KNOTT_X1 + KNOTT_WEST_TO_ORIG_CX
KNOTT_ENT_X1, KNOTT_ENT_X2 = (
    KNOTT_ORIG_CX - KNOTT_ENT_HALF_W,
    KNOTT_ORIG_CX + KNOTT_ENT_HALF_W,
)
KNOTT_STAIRS_X2 = KNOTT_ENT_X1 - KNOTT_STAIR_LANDING_GAP

KNOTT_STAIRS_X1 = KNOTT_X1 + KNOTT_WALL + 2 * INDENT
KNOTT_WEST_ROOM_CX = (KNOTT_X1 + KNOTT_ENT_X1) // 2
KNOTT_X2 = KNOTT_X1 + KNOTT_BUILDING_W
KNOTT_NE_PIER_X = KNOTT_X2 - KNOTT_EAST_PIER_FACE_OFFSET
KNOTT_DRIVEWAY_CORRIDOR_X1 = KNOTT_X2
KNOTT_DRIVEWAY_CORRIDOR_X2 = (
    KNOTT_X2 + CHARLES_WALK_W + 2 * KNOTT_DRIVEWAY_HW + CHARLES_WALK_W
)
KNOTT_DRIVEWAY_WS_X1 = KNOTT_X2
KNOTT_DRIVEWAY_JCX_W = KNOTT_DRIVEWAY_WS_X1
KNOTT_DRIVEWAY_WS_X2 = KNOTT_X2 + KNOTT_DRIVEWAY_CURB_WALK_W
KNOTT_DRIVEWAY_RD_X1 = KNOTT_DRIVEWAY_WS_X2
CHARLES_PLT_BR_X = KNOTT_DRIVEWAY_RD_X1 + KNOTT_DRIVEWAY_HW // 2
KNOTT_DRIVEWAY_RD_X2 = KNOTT_DRIVEWAY_RD_X1 + 2 * KNOTT_DRIVEWAY_HW
KNOTT_DRIVEWAY_ES_X1 = KNOTT_DRIVEWAY_RD_X2
KNOTT_DRIVEWAY_ES_X2 = KNOTT_DRIVEWAY_RD_X2 + KNOTT_DRIVEWAY_CURB_WALK_W
KNOTT_DRIVEWAY_JCX_E = KNOTT_DRIVEWAY_ES_X2
KNOTT_CX = (KNOTT_X1 + KNOTT_X2) // 2
KNOTT_EAST_ROOM_CX = (KNOTT_ENT_X2 + KNOTT_X2) // 2
KNOTT_BIY1 = KNOTT_Y1 + KNOTT_WALL
KNOTT_BIY2 = KNOTT_Y2 - KNOTT_WALL
KNOTT_DRIVEWAY_Y1 = KNOTT_Y1
KNOTT_DRIVEWAY_Y2 = KNOTT_Y2
KNOTT_DRIVEWAY_EXT_Y1 = KNOTT_DRIVEWAY_Y2
KNOTT_STAIRS_Y1 = KNOTT_BIY2 - 256
# West bridge piers step back from the Knott pier using the two reference span widths.
PIER3_X = KNOTT_PIER_X - BRIDGE_OUTER_PIER_SPAN
PIER2_X = PIER3_X - BRIDGE_CENTER_PIER_SPAN
PIER1_X = PIER2_X - BRIDGE_OUTER_PIER_SPAN
BRIDGE_ARCH_X = [
    PIER1_X,  # Pier 1 — west abutment pier (top of embankment hill)
    PIER2_X,  # Pier 2
    PIER3_X,  # Pier 3 (anchors Ennis Drive entrance pillars)
    KNOTT_PIER_X,  # Pier 4 — west KH pier (arch span terminus)
    KNOTT_NE_PIER_X,  # Pier 5 — east KH pier / NE pier
]
CHARLES_LAMP_POST_XS = [
    KNOTT_NE_PIER_X - CHARLES_LAMP_POST_EAST_SETBACK,
    KNOTT_PIER_X,
]
ENNIS_GATE_X1 = BRIDGE_ARCH_X[2] + ENNIS_PIL_HW + 80
ENNIS_PIL_X1 = BRIDGE_ARCH_X[2] - ENNIS_PIL_HW
ENNIS_PIL_X2 = BRIDGE_ARCH_X[2] + ENNIS_PIL_HW
CHARLES_LAMP_POST_H = BRIDGE_DZ2 - BRIDGE_LAMP_POST_CLEARANCE
_KNOTT_GROUND_FLOOR_H = 160  # nominal floor height used to anchor building to bridge; independent of KNOTT_FLOOR_H
KNOTT_GROUND_Z = max(FLOOR_Z2, BRIDGE_DZ2 - _KNOTT_GROUND_FLOOR_H - KNOTT_WALL)
KNOTT_DRIVEWAY_ZT_S = KNOTT_GROUND_Z
KNOTT_Z2 = KNOTT_GROUND_Z + KNOTT_FLOORS * KNOTT_FLOOR_H
BRIDGE_X2 = KNOTT_PIER_X
CHARLES_SWALK_START = BRIDGE_Y2 + 200
ENNIS_Y = BRIDGE_Y2 + ENNIS_NORTH_OFFSET
CHARLES_LAMP_POST_YS = [ENNIS_Y - ENNIS_HW - CHARLES_LAMP_POST_SETBACK]
CHARLES_PLT_Y_OUT = ENNIS_Y - ENNIS_HW + CHARLES_PLATFORM_ROAD_OFFSET
CHARLES_PLT_Y_RET = ENNIS_Y + ENNIS_HW // 8
ENNIS_SW_EDGE = ENNIS_Y - ENNIS_HW - 3 * CHARLES_WALK_W - ROAD_VERGE_BUFFER
ENNIS_WALL_NY = ENNIS_Y + ENNIS_HW + ENNIS_PIL_HW * 2
KNOTT_DRIVEWAY_EXT_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_WALK_W
KNOTT_DRIVEWAY_JCY = ENNIS_Y - ENNIS_HW
PIER1_X, PIER2_X, PIER3_X, PIER4_X, PIER5_X = BRIDGE_ARCH_X
DORM_FLOOR_H = (
    128  # dorm-specific floor height (shorter than Knott's KNOTT_FLOOR_H=160)
)
DORM_ROOF_H = 192  # roof ridge rise above eave (independent of floor height)
DORM_H = DORM_FLOORS * DORM_FLOOR_H
DORM_PIER_X = min(BRIDGE_ARCH_X)
DORM_EAVE_Z = FLOOR_Z2 + DORM_H + DORM_WALL
DORM_RIDGE_Z = DORM_EAVE_Z + DORM_ROOF_H
DORM_WALL_N_Y1 = BRIDGE_Y2 + BRIDGE_PIL_OVERHANG
DORM_WALL_S_Y2 = -(BRIDGE_Y2 + BRIDGE_PIL_OVERHANG)
CHARLES_PLT_X_OUT = ROAD_X2 // 4
CHARLES_PLT_X_RET = -(ROAD_X2 * 3 // 4)
ENNIS_X1 = ROAD_X1
ROAD_Z = FLOOR_Z2 + 8

WALK_X1 = KNOTT_ORIG_CX - KNOTT_ENT_HALF_W
WALK_X2 = KNOTT_ORIG_CX + KNOTT_ENT_HALF_W
WALK_ZT2 = KNOTT_GROUND_Z + KNOTT_FLOOR_H + KNOTT_WALL
WALL_T = 16
WIN_HALF = 24
WORLD_X1 = -1983
BRIDGE_X1 = WORLD_X1 + WALL_T
BRIDGE_SEG_W = (BRIDGE_X2 - BRIDGE_X1) / BRIDGE_SEG_SPAN_W
WORLD_X2 = 2976
WORLD_X2_EXT = (
    WORLD_X2 + WORLD_EAST_BUFFER
)  # extended east boundary (world shell + Ennis only)
ENNIS_CEMENT_X2 = (
    WORLD_X2 - WALL_T - ARCH_SLAB_W // 2
)  # aligned with east teleport centre
ENNIS_GATE_X2 = (ENNIS_GATE_X1 + WORLD_X2_EXT - WALL_T) // 2
ENNIS_CEMENT_X1 = ENNIS_GATE_X2
ENNIS_CEMENT_LAMP_POSTS = [
    (ENNIS_CEMENT_X1, ENNIS_WALL_NY + ENNIS_WALL_T // 2, FLOOR_Z2 + 234),
    (ENNIS_CEMENT_X2, ENNIS_WALL_NY + ENNIS_WALL_T // 2, FLOOR_Z2 + 234),
]
ENNIS_X2 = WORLD_X2_EXT - WALL_T
BRIDGE_EAST_SHIFT_END = -((WORLD_X2 - WALL_T) - BRIDGE_ARCH_X[4]) * math.tan(
    math.radians(BRIDGE_EAST_SPAN_ANGLE)
)
BRIDGE_SPAN_CENTRES = [
    (BRIDGE_X1 + BRIDGE_ARCH_X[0]) // 2,
    (BRIDGE_ARCH_X[0] + BRIDGE_ARCH_X[1]) // 2,
    (BRIDGE_ARCH_X[1] + BRIDGE_ARCH_X[2]) // 2,
    (BRIDGE_ARCH_X[2] + BRIDGE_X2) // 2,
    (BRIDGE_X2 + BRIDGE_ARCH_X[4]) // 2,
    (BRIDGE_ARCH_X[4] + WORLD_X2 - WALL_T) // 2,
]
BRIDGE_PEND_XS = BRIDGE_SPAN_CENTRES
WORLD_Y1, WORLD_Y2 = (
    -1984,
    1712,
)
CHARLES_Y1 = WORLD_Y1 + WALL_T
CHARLES_PLT_Y_S = CHARLES_Y1 + CHARLES_PLT_W // 2 + 48
CHARLES_Y2 = WORLD_Y2 - WALL_T
DORM_NORTH_Y2 = WORLD_Y2 - WALL_T - 150
DORM_NORTH_Y1 = DORM_NORTH_Y2 - DORM_DEPTH
DORM_SOUTH1_Y1 = WORLD_Y1 + WALL_T
DORM_SOUTH1_Y2 = DORM_SOUTH1_Y1 + DORM_DEPTH
DORM_SOUTH1_CY = (DORM_SOUTH1_Y1 + DORM_SOUTH1_Y2) // 2
DORM_SOUTH2_Y1 = DORM_SOUTH1_Y2
DORM_SOUTH2_Y2 = DORM_SOUTH2_Y1 + DORM_DEPTH
DORM_SOUTH2_CY = (DORM_SOUTH2_Y1 + DORM_SOUTH2_Y2) // 2
WORLD_Z2 = max(640, KNOTT_Z2 + 512)
KNOTT_SHAFT_X1 = KNOTT_ENT_X2 + KNOTT_SHAFT_X_OFFSET
KNOTT_SHAFT_X2 = KNOTT_SHAFT_X1 + KNOTT_SHAFT_W
KNOTT_SHAFT_Y1, KNOTT_SHAFT_Y2 = KNOTT_BIY2 - KNOTT_SHAFT_Y_OFFSET, KNOTT_BIY2
KNOTT_STAIRS_Y2 = KNOTT_SHAFT_Y2
KNOTT_STAIRS_MID_Y = (KNOTT_STAIRS_Y1 + KNOTT_STAIRS_Y2) // 2
DORM_NORTH_CY = (DORM_NORTH_Y1 + DORM_NORTH_Y2) // 2
BRIDGE_EAST_PIVOT_X = BRIDGE_ARCH_X[4]


# ── Function-Derived Constants ────────────────────────────────────────────────
# Helper functions below; the constants computed from them follow at the end.
def arch_z_at(x):
    """Z offset above flat datum for parabolic arch at x.

    Symmetric parabola centred at X=0 (Charles Street). Both sides degrade
    at the same rate, reaching zero at ±BRIDGE_X2 (1246 units). West of -1246
    the value clamps to zero (flat approach to world wall).
    """
    return BRIDGE_ARCH_RISE * max(0.0, 1.0 - (x / float(BRIDGE_X2)) ** 2)


def deck_bot_z(x):
    """Z coordinate of the deck underside at a given X position."""
    return BRIDGE_DZ1 + arch_z_at(x)


def deck_top_z(x):
    """Z coordinate of the deck surface (top face) at a given X position."""
    return BRIDGE_DZ2 + arch_z_at(x)


def ft_to_units(feet, inches=0):
    """Convert real-world feet (+ optional inches) to Quake units."""
    return round((feet + inches / 12) * SCALE)


BRIDGE_DECK_Z = deck_top_z(0) + 8
WALK_ZT1 = int(deck_top_z(KNOTT_ORIG_CX))
BRIDGE_PAR_W = ft_to_units(2, 6)
BRIDGE_PIL_HW = ft_to_units(2, 5.5)
BRIDGE_BLK_PIR_M = BRIDGE_PIL_HW + BRIDGE_BLK_HW + 4
DORM_X2 = DORM_PIER_X + BRIDGE_PIL_HW + DORM_PIER_FACE_OFFSET
FENCE_X1 = DORM_X2 + DORM_FENCE_OFFSET
FENCE_X2 = FENCE_X1 + 2
DORM_X1 = DORM_X2 - 576
DORM_CX = (DORM_X1 + DORM_X2) // 2

KNOTT = KnottSpec(
    floors=KNOTT_FLOORS,
    floor_h=KNOTT_FLOOR_H,
    wall_t=KNOTT_WALL,
    x1=KNOTT_X1,
    x2=KNOTT_X2,
    y1=KNOTT_Y1,
    y2=KNOTT_Y2,
    driveway_hw=KNOTT_DRIVEWAY_HW,
)
BRIDGE = BridgeSpec(
    x1=BRIDGE_X1,
    x2=BRIDGE_X2,
    y1=BRIDGE_Y1,
    y2=BRIDGE_Y2,
    arch_rise=BRIDGE_ARCH_RISE,
    parapet_h=BRIDGE_PAR_H,
    walk_wall=BRIDGE_WALK_WALL,
)
DORM = DormSpec(
    floor_h=DORM_FLOOR_H,
    floors=DORM_FLOORS,
    wall_t=DORM_WALL,
    depth=DORM_DEPTH,
    x1=DORM_X1,
    x2=DORM_X2,
)


# South-dorm raised terrace + gentler frontage hill out to Charles Street.
# The south-dorm pad sits flat on a terrace at FLOOR_Z2 + SDORM_LIFT; east of the
# pad a gentle ramp descends to grade at SDORM_TOE_X (the "hill out to Charles St").
SDORM_LIFT = 128  # terrace height = new south-dorm floor level
SDORM_TERRACE_X2 = DORM_X2 + 216  # east edge of flat terrace (= south fence line)
SDORM_TOE_X = -400  # frontage ramp reaches grade (z=0) here, near the road
# N-S decline at/east of the front fence: from the brick wall's south pillar down
# to the north side of the bridge, so the iron fence stays connected to grade.
SDORM_SLOPE_Y_S = DORM_SOUTH2_Y2 + DORM_DOOR_OFF + DORM_DOOR_W // 2 + 96  # south pillar
SDORM_SLOPE_Y_N = BRIDGE_Y2  # north side of bridge
SDORM_WALL_X = DORM_PIER_X  # brick-wall centreline: divides the flat dorm pad (west)
# from the strip that declines north between the wall and the fence (east).

# South-dorm stairwell — steps cut into the south-dorm-1 footprint, descending west
# to the existing west-wall tunnel door, bridging the SDORM_LIFT drop down to the
# tunnel floor (z=0). The footprint below is carved out of both the terrace fill
# (streets.py) and the dorm interior floor (west_campus.py); the steps fill it.
SDORM_STAIR_HW = 40  # half-width (matches the west-wall door opening)
SDORM_STAIR_N = SDORM_LIFT // 16  # number of 16-high steps (= 8)
SDORM_STAIR_RISE = SDORM_LIFT // SDORM_STAIR_N  # per-step rise (= 16)
SDORM_STAIR_RUN = 32  # tread depth (E-W) per step
SDORM_STAIR_X1 = (
    DORM_X1 + KNOTT_STAIR_LANDING_GAP
)  # first-step / floor-hole west edge (= interior face)
SDORM_STAIR_X2 = SDORM_STAIR_X1 + SDORM_STAIR_N * SDORM_STAIR_RUN  # east edge of run
SDORM_STAIR_Y1 = DORM_SOUTH1_CY - SDORM_STAIR_HW
SDORM_STAIR_Y2 = DORM_SOUTH1_CY + SDORM_STAIR_HW

WORLDSPAWN_FIELDS = {
    "wad": "quake101.wad;ad.wad;makkon_building.wad",
    "message": "Loyola University Maryland - Charles Street Pedestrian Bridge",
    "sky": Textures.SKY,
    "dmflags": "128",
    **LIGHTING.to_worldspawn(),
}
