import math

# ── Constant prefix legend ─────────────────────────────────────────────────────
#
#   A_           arch ring (generic — voussoir segments, radius, segment count)
#   ARCH_        pedestrian bridge arch profile dimensions (rin, rout, stilt, slab)
#   CHARLES_          Charles Street (the N-S road running under the bridge)
#   DRAW_        boolean feature-flag (enables/disables a drawn element)
#   ENNIS_          Ennis Parallel entrance (pillars, boundary wall, curbs)
#   FENCE_       iron fence (pickets, rails, spacing)
#   FLOOR_       world ground-plane Z levels (FLOOR_Z1 = bottom, FLOOR_Z2 = top)
#   KH_          Knott Hall (the main campus building south-east of the bridge)
#   BRIDGE_          Pedestrian Bridge (span, deck, piers, parapet, east approach)
#   PLAT_        Charles Street scrolling platform (func_train)
#   RH_          Residence Hall (the west-campus buildings flanking the bridge)
#   ROAD_        road surface extents and markings (X/Y limits, dash/gap lengths)
#   SHOW_        boolean feature-flag (shows/hides a map element)
#   TEX_         texture name string
#   WALK_        walkway connecting the bridge east end to Knott Hall 2nd floor
#   WALL_        structural wall thickness (generic)
#   WIN_         shared window geometry (Knott Hall / Residence Hall facades)
#   WORLD_       world bounding-box extents
#
# ──────────────────────────────────────────────────────────────────────────────

ARCH_RIN = 96
ARCH_ROUT = 136
ARCH_SLAB_W = 32
ARCH_STILT_H = 96
A_SEGS = 32
CHARLES_ARCH_RIN = 256
CHARLES_ARCH_RIN_PRE = 256
CHARLES_ARCH_ROUT_PRE = 312
CHARLES_ARCH_STILT = 96
CHARLES_ARCH_STILT_PRE = 96
CHARLES_ARCH_TRIG_INSET = 8
CHARLES_ARCH_W = 48
CHARLES_ARCH_W_PRE = 48
CHARLES_CRN_SEGS = 12
CHARLES_LAMP_POST_XS = [
    2158,
    1246,
]
CHARLES_PLT_H = 12
CHARLES_PLT_SPEED = 180
CHARLES_PLT_W = 128
CHARLES_RAMP_W = 64
CHARLES_WALK_H = 8
CHARLES_WALK_W = 80
CHARLES_CRN_R = CHARLES_WALK_W
DRAW_KH_FASCIA_TEXT = True
ENNIS_CURB_W = 8
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
FENCE_H = 96
FENCE_SPACING = 16
FENCE_TEX = "metal4_4"
FLOOR_Z1, FLOOR_Z2 = -16, 0
ENNIS_PIL_ZB = FLOOR_Z2
INDENT = 80
KH_BRCS_CRN_R = CHARLES_WALK_W
KH_BRCS_CRN_SEGS = CHARLES_CRN_SEGS
KH_BRCS_WALK_W = CHARLES_WALK_W
KH_BR_HW = 128
KH_BR_ZT_N = FLOOR_Z2
KH_ENABLED = True
KH_FASCIA_FONT = {
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
    "Y": [0b1001, 0b0110, 0b0100, 0b0100, 0b0100, 0b0000],
    " ": [0b0000, 0b0000, 0b0000, 0b0000, 0b0000, 0b0000],
}
KH_FASCIA_PX_W, KH_FASCIA_PX_H = 4, 4
KH_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
KH_FLOORS = 5
KH_FLOOR_H = 160
KH_MULLION_PRO = 12
KH_MULLION_W = 12
KH_NE_PIER_X = 2206
KH_OFFSET = 90
KH_ORIG_CX = 1740 + KH_OFFSET
KH_ENT_X1, KH_ENT_X2 = KH_ORIG_CX - 64, KH_ORIG_CX + 64
KH_PIER_X = 1246
KH_RAIL_H = 72
KH_RAIL_TEX = "metal4_4"
KH_ROOM_SPLITS = [-1072, -950, -1200, -850, -1300]
KH_SHELF_D = 16
KH_SHELF_H = 64
KH_SHELF_W = 64
KH_STAIRS_HALF_N = 8
KH_STAIRS_POST_W = 4
KH_STAIRS_RAIL_H = 72
KH_STAIRS_RAIL_T = 4
KH_STAIRS_STEP_R = 10
KH_STAIRS_TREAD_X = 24
KH_STAIRS_X2 = KH_ENT_X1 - 16
KH_STAIR_OFFSET = 384
KH_STEP_DEPTH = 24
KH_STEP_N = 5
KH_WALKWAY_ENABLED = True
KH_WALL = 16
KH_X1 = KH_PIER_X - 130 + KH_OFFSET
KH_STAIRS_X1 = KH_X1 + KH_WALL + 2 * INDENT
KH_WEST_ROOM_CX = (KH_X1 + KH_ENT_X1) // 2
KH_X2 = KH_NE_PIER_X + 32
KH_BR_CORRIDOR_X1 = KH_X2
KH_BR_CORRIDOR_X2 = KH_X2 + CHARLES_WALK_W + 2 * 128 + CHARLES_WALK_W
KH_BR_WS_X1 = KH_X2
KH_BR_JCX_W = KH_BR_WS_X1
KH_BR_WS_X2 = KH_X2 + KH_BRCS_WALK_W
KH_BR_RD_X1 = KH_BR_WS_X2
CHARLES_PLT_BR_X = KH_BR_RD_X1 + KH_BR_HW // 2
KH_BR_RD_X2 = KH_BR_RD_X1 + 2 * KH_BR_HW
KH_BR_ES_X1 = KH_BR_RD_X2
KH_BR_ES_X2 = KH_BR_RD_X2 + KH_BRCS_WALK_W
KH_BR_JCX_E = KH_BR_ES_X2
KH_CX = (KH_X1 + KH_X2) // 2
KH_EAST_ROOM_CX = (KH_ENT_X2 + KH_X2) // 2
KH_Y1, KH_Y2 = -1888, -256
KH_BIY1 = KH_Y1 + KH_WALL
KH_BIY2 = KH_Y2 - KH_WALL
KH_BR_Y1 = KH_Y1
KH_BR_Y2 = KH_Y2
KH_BR_EXT_Y1 = KH_BR_Y2
KH_STAIRS_Y1 = KH_BIY2 - 256
BRIDGE_BLK_HW = 24
BRIDGE_ARCH_RISE = 144
BRIDGE_ARCH_X = [
    -1246,  # Pier 1 — west abutment pier (top of embankment hill)
    -525,  # Pier 2
    525,  # Pier 3 (anchors Ennis Drive entrance pillars)
    KH_PIER_X,  # Pier 4 — west KH pier (arch span terminus)
    KH_NE_PIER_X,  # Pier 5 — east KH pier / NE pier
]
ENNIS_GATE_X1 = BRIDGE_ARCH_X[2] + ENNIS_PIL_HW + 80
ENNIS_PIL_X1 = BRIDGE_ARCH_X[2] - ENNIS_PIL_HW
ENNIS_PIL_X2 = BRIDGE_ARCH_X[2] + ENNIS_PIL_HW
BRIDGE_BLK_H = 36
BRIDGE_BLK_OVH = 0
BRIDGE_DZ1, BRIDGE_DZ2 = (
    224,
    240,
)
CHARLES_LAMP_POST_H = BRIDGE_DZ2 - 32
KH_GROUND_Z = max(FLOOR_Z2, BRIDGE_DZ2 - KH_FLOOR_H - KH_WALL)
KH_BR_ZT_S = KH_GROUND_Z
KH_Z2 = KH_GROUND_Z + KH_FLOORS * KH_FLOOR_H
BRIDGE_EAST_SHIFT_START = 0.0
BRIDGE_EAST_SPAN_ANGLE = 12.0
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
BRIDGE_PIL_INNER_R = (160, 84)
BRIDGE_PIL_OUTER_R = (140, 72)
BRIDGE_PIL_OVERHANG = 16
BRIDGE_PIL_PYR_H = 20
BRIDGE_PIL_PYR_W = 45
BRIDGE_SEG_SPAN_W = 32
BRIDGE_SQ_D = 1
BRIDGE_SQ_HH = 6
BRIDGE_SQ_HW = 8
BRIDGE_TUBE_GAP = 12
BRIDGE_TUBE_HW = 2
BRIDGE_TUBE_RISE = 10
BRIDGE_X2 = KH_PIER_X
BRIDGE_Y1, BRIDGE_Y2 = -136, 136
CHARLES_SWALK_START = BRIDGE_Y2 + 200
ENNIS_Y = BRIDGE_Y2 + 800
CHARLES_LAMP_POST_YS = [ENNIS_Y - ENNIS_HW - 160]
CHARLES_PLT_Y_OUT = ENNIS_Y - ENNIS_HW + 16
CHARLES_PLT_Y_RET = ENNIS_Y + ENNIS_HW // 8
ENNIS_SW_EDGE = ENNIS_Y - ENNIS_HW - 3 * CHARLES_WALK_W - 32
ENNIS_WALL_NY = ENNIS_Y + ENNIS_HW + ENNIS_PIL_HW * 2
KH_BR_EXT_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_WALK_W
KH_BR_JCY = ENNIS_Y - ENNIS_HW
PIER1_X, PIER2_X, PIER3_X, PIER4_X, PIER5_X = BRIDGE_ARCH_X
PLAT_H = 8
RH_DEPTH = 600
RH_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)
RH_DOOR_OFF = 160
RH_DOOR_W = 80
RH_EMB_X2 = -1146
RH_ENT_H = 100
RH_ENT_HW = 48
RH_FLOORS = 3
RH_H = RH_FLOORS * KH_FLOOR_H
RH_PIER_X = min(BRIDGE_ARCH_X)
RH_SLAB_T = 16
RH_WALL = 16
RH_EAVE_Z = FLOOR_Z2 + RH_H + RH_WALL
RH_RIDGE_Z = RH_EAVE_Z + KH_FLOOR_H
RH_WALL_N_Y1 = BRIDGE_Y2 + BRIDGE_PIL_OVERHANG
RH_WALL_S_Y2 = -(BRIDGE_Y2 + BRIDGE_PIL_OVERHANG)
RH_WIN_HH = 44
RH_WIN_HW = 36
RH_WIN_W, RH_WIN_H, RH_WIN_T = 20, 28, 3
ROAD_DASH_LEN = 64
ROAD_GAP_LEN = 64
ROAD_X1, ROAD_X2 = -256, 256
CHARLES_PLT_X_OUT = ROAD_X2 // 4
CHARLES_PLT_X_RET = -(ROAD_X2 * 3 // 4)
ENNIS_X1 = ROAD_X1
ROAD_Z = FLOOR_Z2 + 8
SCALE = 15.108
SHOW_SUPPORTS = True
TEX_BRICK = "bricka2_1"
TEX_CEMENT = "sfloor3_2"
TEX_DIVIDER = "sfloor3_2"
TEX_FLOOR = "sfloor3_2"
TEX_FLOOR_KH = "sfloor3_2"
TEX_GROUND = "ground1_1"
TEX_PILLAR = "city2_7"
TEX_RAIL = "metal5_4"
TEX_ROAD = "azfloor1_1"
TEX_ROOF = "wgrnd1_5"
TEX_SKY = "sky1"
TEX_STONE = "sfloor3_2"
TEX_TELEPORT = "*teleport"
TEX_WALL = "city2_7"
TEX_WHITE_STONE = "sfloor3_2"
WALK_X1 = KH_ORIG_CX - 64
WALK_X2 = KH_ORIG_CX + 64
WALK_ZT2 = KH_GROUND_Z + KH_FLOOR_H + KH_WALL
WALL_T = 16
WIN_HALF = 24
WORLD_X1 = -1983
BRIDGE_X1 = WORLD_X1 + WALL_T
BRIDGE_SEG_W = (BRIDGE_X2 - BRIDGE_X1) / BRIDGE_SEG_SPAN_W
WORLD_X2 = 2976
ENNIS_CEMENT_X2 = WORLD_X2 - WALL_T
ENNIS_GATE_X2 = (ENNIS_GATE_X1 + WORLD_X2 - WALL_T) // 2
ENNIS_CEMENT_X1 = ENNIS_GATE_X2
ENNIS_CEMENT_LAMP_POSTS = [
    (ENNIS_CEMENT_X1, ENNIS_WALL_NY + ENNIS_WALL_T // 2, FLOOR_Z2 + 234),
    (ENNIS_CEMENT_X2, ENNIS_WALL_NY + ENNIS_WALL_T // 2, FLOOR_Z2 + 234),
]
ENNIS_X2 = WORLD_X2 - WALL_T
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
RH_NORTH_Y2 = WORLD_Y2 - WALL_T - 150
RH_NORTH_Y1 = RH_NORTH_Y2 - RH_DEPTH
RH_SOUTH1_Y1 = WORLD_Y1 + WALL_T
RH_SOUTH1_Y2 = RH_SOUTH1_Y1 + RH_DEPTH
RH_SOUTH1_CY = (RH_SOUTH1_Y1 + RH_SOUTH1_Y2) // 2
RH_SOUTH2_Y1 = RH_SOUTH1_Y2
RH_SOUTH2_Y2 = RH_SOUTH2_Y1 + RH_DEPTH
RH_SOUTH2_CY = (RH_SOUTH2_Y1 + RH_SOUTH2_Y2) // 2
WORLD_Z2 = max(640, KH_Z2 + 512)


def arch_z(x):
    """Z offset above flat datum for parabolic arch at x.

    Symmetric parabola centred at X=0 (Charles Street). Both sides degrade
    at the same rate, reaching zero at ±BRIDGE_X2 (1246 units). West of -1246
    the value clamps to zero (flat approach to world wall).
    """
    return BRIDGE_ARCH_RISE * max(0.0, 1.0 - (x / float(BRIDGE_X2)) ** 2)


def dbot(x):
    """Z coordinate of the deck underside at a given X position."""
    return BRIDGE_DZ1 + arch_z(x)


def dtop(x):
    """Z coordinate of the deck surface (top face) at a given X position."""
    return BRIDGE_DZ2 + arch_z(x)


BRIDGE_DECK_Z = dtop(0) + 8
WALK_ZT1 = int(dtop(KH_ORIG_CX))


def ft(feet, inches=0):
    """Convert real-world feet (+ optional inches) to Quake units."""
    return round((feet + inches / 12) * SCALE)


BRIDGE_PAR_W = ft(2, 6)
BRIDGE_PIL_HW = ft(2, 5.5)
BRIDGE_BLK_PIR_M = BRIDGE_PIL_HW + BRIDGE_BLK_HW + 4
RH_X2 = RH_PIER_X + BRIDGE_PIL_HW + 32
FENCE_X1 = RH_X2 + 96
FENCE_X2 = FENCE_X1 + 2
RH_X1 = RH_X2 - 576
stx1, stx2 = KH_ENT_X2 + 16, KH_ENT_X2 + 16 + 128
sty1, sty2 = KH_BIY2 - 128, KH_BIY2
KH_STAIRS_Y2 = sty2
KH_STAIRS_MID_Y = (KH_STAIRS_Y1 + KH_STAIRS_Y2) // 2
RH_NORTH_CY = (RH_NORTH_Y1 + RH_NORTH_Y2) // 2
BRIDGE_EAST_PIVOT_X = BRIDGE_ARCH_X[4]
RH_CX = (RH_X1 + RH_X2) // 2
