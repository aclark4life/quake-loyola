import math

SCALE = 15.108


def ft(feet, inches=0):
    """Convert real-world feet (+ optional inches) to Quake units."""
    return round((feet + inches / 12) * SCALE)


TEX_STONE = "sfloor3_2"

TEX_PILLAR = "city2_7"

TEX_FLOOR = "sfloor3_2"

TEX_CEMENT = "sfloor3_2"

TEX_ROAD = "azfloor1_1"

TEX_WALL = "city2_7"

TEX_FLOOR_KH = "sfloor3_2"

TEX_METAL = "city2_7"

TEX_GROUND = "ground1_1"

TEX_RAIL = "metal5_4"

TEX_SKY = "sky1"

TEX_LAVA = "*lava1"

TEX_TELEPORT = "*teleport"

TEX_BRICK = "bricka2_1"

TEX_WHITE_STONE = "sfloor3_2"

TEX_ROOF = "wgrnd1_5"

PB_Y1, PB_Y2 = -136, 136

PB_DZ1, PB_DZ2 = (
    224,
    240,
)

PB_ARCH_RISE = 144

SEG_SPAN_W = 32


def arch_z(x):
    """Z offset above flat datum for parabolic arch at x.

    Symmetric parabola centred at X=0 (Charles Street). Both sides degrade
    at the same rate, reaching zero at ±PB_X2 (1246 units). West of -1246
    the value clamps to zero (flat approach to world wall).
    """
    return PB_ARCH_RISE * max(0.0, 1.0 - (x / float(PB_X2)) ** 2)


def dtop(x):
    """Z coordinate of the deck surface (top face) at a given X position."""
    return PB_DZ2 + arch_z(x)


def dbot(x):
    """Z coordinate of the deck underside at a given X position."""
    return PB_DZ1 + arch_z(x)


PB_PAR_H = 40

PB_PAR_W = ft(2, 6)

PB_PIL_EXTRA = 64

PB_PIL_CAP_H = 12

PB_PIL_PYR_H = 20

PB_PIL_PYR_W = 45

PB_PIL_HW = ft(2, 5.5)

PB_PIL_CAP_OVH = 17

PB_PIL_CAP_IN_OVH = 4

PB_PIL_CAP_OUT_OVH = 20

PB_PIL_OVERHANG = 16

PB_PIL_BASE_H = 24

PB_PIL_BASE_RAMP_H = 40

PB_PIL_BASE_CAP_H = 6

PB_PIL_BASE_CAP_OVH = 5

SHOW_SUPPORTS = True

WALL_T = 16

FLOOR_Z1, FLOOR_Z2 = -16, 0

ROAD_X1, ROAD_X2 = -256, 256

KH_WIDTH = 640

WORLD_X1 = -1983

WORLD_X2 = 2976

WORLD_Y1, WORLD_Y2 = (
    -1984,
    1712,
)

KH_OFFSET = 90

KH_PIER_X = 1246

KH_NE_PIER_X = 2206

KH_X1 = KH_PIER_X - 130 + KH_OFFSET

KH_X2 = KH_NE_PIER_X + 32

KH_WIDTH = KH_X2 - KH_X1

KH_CX = (KH_X1 + KH_X2) // 2

KH_ORIG_CX = 1740 + KH_OFFSET

PB_X1 = WORLD_X1 + WALL_T

PB_X2 = KH_PIER_X

EAST_SPAN_ANGLE = 12.0

SEG_W = (PB_X2 - PB_X1) / SEG_SPAN_W

PB_ARCH_X = [
    -1246,  # Pier 1 — west abutment pier (top of embankment hill)
    -525,  # Pier 2
    525,  # Pier 3 (anchors Ennis Drive entrance pillars)
    KH_PIER_X,  # Pier 4 — west KH pier (arch span terminus)
    KH_NE_PIER_X,  # Pier 5 — east KH pier / NE pier
]

PIER1_X, PIER2_X, PIER3_X, PIER4_X, PIER5_X = PB_ARCH_X

KH_Y1, KH_Y2 = -1888, -256

KH_WALL = 16

KH_FLOOR_H = 160

KH_FLOORS = 5

INDENT = 80

KH_GROUND_Z = max(FLOOR_Z2, PB_DZ2 - KH_FLOOR_H - KH_WALL)

KH_Z2 = KH_GROUND_Z + KH_FLOORS * KH_FLOOR_H

WORLD_Z2 = max(640, KH_Z2 + 512)

KH_ENABLED = True

KH_WALKWAY_ENABLED = True

WALK_X1 = KH_ORIG_CX - 64

WALK_X2 = KH_ORIG_CX + 64

WALK_ZT1 = int(dtop(KH_ORIG_CX))

WALK_ZT2 = KH_GROUND_Z + KH_FLOOR_H + KH_WALL

A_SEGS = 32

CS_Y1 = WORLD_Y1 + WALL_T

CS_Y2 = WORLD_Y2 - WALL_T

CS_WALK_W = 80

CS_WALK_H = 8

CS_STRIPE_W = 6

EP_Y = PB_Y2 + 800

EP_HW = 160

EP_X1 = ROAD_X1

EP_X2 = WORLD_X2 - WALL_T

EP_SW_EDGE = EP_Y - EP_HW - 3 * CS_WALK_W - 32

KH_BR_CORRIDOR_X1 = KH_X2

KH_BR_CORRIDOR_X2 = KH_X2 + CS_WALK_W + 2 * 128 + CS_WALK_W

EP_CURB_W = 8

div_hw = 4

div_ep_hw = 16

CS_SWALK_START = PB_Y2 + 200

TEX_DIVIDER = "sfloor3_2"

DASH_LEN = 64

GAP_LEN = 64

divider_x = ROAD_X2

dash_on = True

CS_CRN_R = CS_WALK_W

CS_CRN_SEGS = 12

cx_se = ROAD_X2 + CS_CRN_R

cy_se = EP_Y - EP_HW - CS_CRN_R

cx_ne = ROAD_X2 + CS_CRN_R

cy_ne = EP_Y + EP_HW + CS_CRN_R

CS_RAMP_W = 64

EP_PIL_HW = 22

EP_PIL_OFFSET = CS_WALK_W + 20

EP_PIL_X1 = PB_ARCH_X[2] - EP_PIL_HW

EP_PIL_X2 = PB_ARCH_X[2] + EP_PIL_HW

EP_PIL_ZB = FLOOR_Z2

EP_PIL_POST_H = 81

EP_PIL_CAP_OVH = 1

EP_PIL_CAP_H = 3

EP_PIL_BELL2_HW = (
    19  # tapered top section half-width (wider than before, less than post)
)

EP_PIL_BELL2_H = 27

EP_WALL_T = 8

EP_WALL_H = 96

bw_ny = EP_Y + EP_HW + EP_PIL_HW * 2

bw_x1 = ROAD_X2 + CS_WALK_W + 48

bwex2 = PB_ARCH_X[2] + EP_PIL_HW + 80

bw_ny2 = bw_ny + 200

bw_mid_y = (bw_ny + WORLD_Y2 - WALL_T) // 2

gate_fence_x1 = bw_x1 + EP_WALL_T // 2 - 1

gate_fence_x2 = gate_fence_x1 + 2

gate_fence_height = 96

gate_fence_spacing = 16

gate_fence_tex = "metal4_4"

gate_picket_y = bw_mid_y

gate_picket_index = 0

panel_x1 = bw_x1 - 2

panel_x2 = bw_x1

panel_bar_thickness = 2

panel_outer_width = 48

panel_outer_height = 28

panel_inner_width = 28

panel_inner_height = 12

panel_z1 = FLOOR_Z2 + EP_WALL_H

panel_z_center = panel_z1 + panel_outer_height // 2

panel_spacing = panel_outer_width + 16

panel_available_span = bw_mid_y - bw_ny

panel_count = max(
    1, (panel_available_span + panel_outer_width) // (panel_outer_width + 8)
)

panel_spacing = panel_available_span // panel_count

panel_center_y = bw_ny + panel_spacing // 2

panels_drawn = 0

EP_WALL_PIL_HW = 14

EP_WALL_PIL_H = 120

bw_cx = bw_x1 + EP_WALL_T // 2

bw_cy = bw_ny + EP_WALL_T // 2

east_gate_x1 = bwex2

east_gate_x2 = (bwex2 + WORLD_X2 - WALL_T) // 2

east_gate_y1 = bw_ny + EP_WALL_T // 2 - 1

east_gate_y2 = east_gate_y1 + 2

east_gate_brushes = []

east_gate_picket_x = east_gate_x1

east_gate_picket_index = 0

cement_wall_x1 = east_gate_x2

cement_wall_x2 = WORLD_X2 - WALL_T

cement_wall_y1 = bw_ny

cement_wall_y2 = bw_ny + EP_WALL_T

cement_wall_height = 32

cement_wall_pillar_half_width = 14

cement_wall_pillar_height = cement_wall_height + 16

cement_wall_lamp_posts = []

RH_FLOORS = 3

RH_H = RH_FLOORS * KH_FLOOR_H

RH_DEPTH = 600

RH_PIER_X = min(PB_ARCH_X)

RH_X2 = RH_PIER_X + PB_PIL_HW + 32

RH_X1 = RH_X2 - 576

RH_NORTH_Y2 = WORLD_Y2 - WALL_T - 150

RH_NORTH_Y1 = RH_NORTH_Y2 - RH_DEPTH

RH_SOUTH1_Y1 = WORLD_Y1 + WALL_T

RH_SOUTH1_Y2 = RH_SOUTH1_Y1 + RH_DEPTH

RH_SOUTH2_Y1 = RH_SOUTH1_Y2

RH_SOUTH2_Y2 = RH_SOUTH2_Y1 + RH_DEPTH

RH_EMB_X2 = -1146

emb_zt_at_ab_x1 = int(
    PB_DZ2 + (FLOOR_Z2 - PB_DZ2) * (RH_X1 - PB_X1) / (RH_EMB_X2 - PB_X1)
)

RH_WALL_N_Y1 = PB_Y2 + PB_PIL_OVERHANG

RH_WALL_S_Y2 = -(PB_Y2 + PB_PIL_OVERHANG)

RH_DOOR_W = 80

RH_DOOR_OFF = 160

RH_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)

s_door_y = RH_SOUTH2_Y2 + RH_DOOR_OFF

RH_WIN_W, RH_WIN_H, RH_WIN_T = 20, 28, 3

RH_WALL = 16

RH_WIN_HW = 36

RH_WIN_HH = 44

RH_ENT_HW = 48

RH_ENT_H = 100

RH_CX = (RH_X1 + RH_X2) // 2

RH_NORTH_CY = (RH_NORTH_Y1 + RH_NORTH_Y2) // 2

rh_wx = [RH_X1 + (RH_CX - RH_ENT_HW - RH_X1) * k // 3 for k in [1, 2]] + [
    (RH_CX + RH_ENT_HW) + (RH_X2 - RH_CX - RH_ENT_HW) * k // 3 for k in [1, 2]
]

rh_wy = [RH_NORTH_Y1 + (RH_NORTH_Y2 - RH_NORTH_Y1) * k // 4 for k in [1, 2, 3]]

rh_wz_lo = (KH_FLOOR_H - RH_WIN_HH * 2) // 2

rh_wz_hi = rh_wz_lo + RH_WIN_HH * 2

RH_EAVE_Z = FLOOR_Z2 + RH_H + RH_WALL

RH_RIDGE_Z = RH_EAVE_Z + KH_FLOOR_H

RH_SLAB_T = 16

FNC_X1 = RH_X2 + 96

FNC_X2 = FNC_X1 + 2

FNC_H = 96

FNC_SPACING = 16

FNC_RAIL = 8

FNC_TEX = "metal4_4"

east_shift_start = 0.0

east_pivot_x = PB_ARCH_X[4]

PBPB_BLK_HW = 24

PB_BLK_H = 36

PB_BLK_OVH = 0

PB_BLK_PIR_M = PB_PIL_HW + PBPB_BLK_HW + 4

PB_SQ_HW = 8

PB_SQ_HH = 6

PB_SQ_D = 1

cx_walk_e = WALK_X2 + PBPB_BLK_HW

cx_walk_w = WALK_X1 - PBPB_BLK_HW

PB_TUBE_HW = 2

PB_TUBE_RISE = 10

PB_TUBE_GAP = 12

tube_ny1 = PB_Y2 - PB_PAR_W // 2 - PB_TUBE_HW

tube_ny2 = tube_ny1 + PB_TUBE_HW * 2

tube_sy1 = PB_Y1 + PB_PAR_W // 2 - PB_TUBE_HW

tube_sy2 = tube_sy1 + PB_TUBE_HW * 2

PB_PIL_OUTER_R = (140, 72)

PB_PIL_INNER_R = (160, 84)

PB_PIL_CAP_OVHNTR_R = (160, 90)

ARCH_RIN = 96

ARCH_ROUT = 136

ARCH_STILT_H = 96

ARCH_SLAB_W = 32

KH_BR_HW = 128

KH_BRCS_WALK_W = CS_WALK_W

KH_BRCS_CRN_R = CS_WALK_W

KH_BRCS_CRN_SEGS = CS_CRN_SEGS

KH_BR_WS_X1 = KH_X2

KH_BR_WS_X2 = KH_X2 + KH_BRCS_WALK_W

KH_BR_RD_X1 = KH_BR_WS_X2

KH_BR_RD_X2 = KH_BR_RD_X1 + 2 * KH_BR_HW

KH_BR_ES_X1 = KH_BR_RD_X2

KH_BR_ES_X2 = KH_BR_RD_X2 + KH_BRCS_WALK_W

KH_BR_Y1 = KH_Y1

KH_BR_Y2 = KH_Y2

KH_BR_ZT_N = FLOOR_Z2

KH_BR_ZT_S = KH_GROUND_Z

KH_BR_EXT_Y1 = KH_BR_Y2

KH_BR_EXT_Y2 = EP_Y - EP_HW - CS_WALK_W

KH_BR_JCX_W = KH_BR_WS_X1

KH_BR_JCY = EP_Y - EP_HW

KH_BR_JCX_E = KH_BR_ES_X2

bix1 = KH_X1 + KH_WALL

bix2 = KH_X2 - KH_WALL

biy1 = KH_Y1 + KH_WALL

biy2 = KH_Y2 - KH_WALL

KH_ENT_X1, KH_ENT_X2 = KH_ORIG_CX - 64, KH_ORIG_CX + 64

KH_STEP_N = 5

KH_STEP_DEPTH = 24

KH_STAIR_OFFSET = 384

stair_base_z = FLOOR_Z2 + CS_WALK_H

step_rise = (KH_GROUND_Z - stair_base_z) * 1 // KH_STEP_N

stair_y0 = KH_Y2 + KH_STAIR_OFFSET

stair_y_end = stair_y0 + KH_STEP_N * KH_STEP_DEPTH

cap_width = 24

cap_raise = 16

KH_RAIL_H = 72

KH_RAIL_TEX = "metal4_4"

KH_RAIL_SPACING = 16

post_width = 8

post_depth = 2

level_extension = 20

stx1, stx2 = KH_ENT_X2 + 16, KH_ENT_X2 + 16 + 128

sty1, sty2 = biy2 - 128, biy2

KHRH_WIN_HALF = 24

KH_MULLION_W = 12

KH_MULLION_PRO = 12

wstx2 = KH_ENT_X1 - 16

wstx1 = bix1 + 2 * INDENT

wsty2 = sty2

wsty1 = biy2 - 256

s_wall_openings = [
    (
        KH_ENT_X1,
        KH_GROUND_Z + fl * KH_FLOOR_H + KH_WALL,
        KH_ENT_X2,
        KH_GROUND_Z + (fl + 1) * KH_FLOOR_H,
    )
    for fl in range(KH_FLOORS)
]

sw_win_cx = KH_X1 + INDENT // 2

se_win_cx = KH_X2 - INDENT // 2

door_ground = [(KH_ENT_X1, KH_GROUND_Z, KH_ENT_X2, KH_GROUND_Z + KH_FLOOR_H)]

door_upper = [(KH_ENT_X1, WALK_ZT2, KH_ENT_X2, KH_GROUND_Z + KH_FLOOR_H * 2)]

win_n = [
    (KH_ORIG_CX - 48, KH_GROUND_Z + KH_FLOOR_H * 2, KH_ORIG_CX - 6, KH_Z2),
    (KH_ORIG_CX + 6, KH_GROUND_Z + KH_FLOOR_H * 2, KH_ORIG_CX + 48, KH_Z2),
]

nw_win_cx1 = KH_X1 + INDENT // 2

nw_win_cx2 = KH_X1 + INDENT + INDENT // 2

ne_win_cx = KH_X2 - INDENT // 2

win_n_x1, win_n_x2 = KH_ORIG_CX - 48, KH_ORIG_CX + 48

win_n_mid = KH_ORIG_CX - 6

sign_text = "MARION BURK KNOTT HALL"

sign_pixel_width, sign_pixel_height = 2, 4

sign_char_width = (4 + 1) * sign_pixel_width

sign_total_width = len(sign_text) * sign_char_width - sign_pixel_width

sign_half_width = sign_total_width // 2 + 4

sign_center_x = KH_X2 - INDENT - sign_half_width

sign_z1 = KH_GROUND_Z + KH_FLOOR_H * 2 + 20

sign_z2 = sign_z1 + 48

ww_half = 120

ww_wall_y1, ww_wall_y2 = KH_Y1, KH_Y2 - INDENT

ww_quarter = (ww_wall_y2 - ww_wall_y1) // 4

ww_c1 = ww_wall_y1 + ww_quarter

ww_c2 = ww_wall_y1 + 2 * ww_quarter

ww_c3 = ww_wall_y1 + 3 * ww_quarter

ww_div_w = 12

ww_protrude = 12

sz0 = KH_GROUND_Z

st0 = sz0 + KH_WALL

shaft_wall = 8

shaft_door_h = KH_FLOOR_H

shaft_door_openings = [
    (
        sty1 + 16,
        KH_GROUND_Z + floor_index * KH_FLOOR_H,
        sty2 - 16,
        KH_GROUND_Z + floor_index * KH_FLOOR_H + shaft_door_h,
    )
    for floor_index in range(KH_FLOORS)
]

west_shaft_door_openings = [
    (
        sty1 + 16,  # same Y extents as east shaft doorway
        KH_GROUND_Z + floor_index * KH_FLOOR_H,
        sty2 - 16,
        KH_GROUND_Z + floor_index * KH_FLOOR_H + shaft_door_h,
    )
    for floor_index in range(KH_FLOORS)
]

WST_HALF_N = 8

WST_STEP_R = 10

WST_TREAD_X = 24

PLAT_H = 8

stair_cx = (wstx1 + wstx2) // 2

stair_x1 = stair_cx - WST_HALF_N * WST_TREAD_X // 2

stair_x2 = stair_x1 + WST_HALF_N * WST_TREAD_X

wst_midY = (wsty1 + wsty2) // 2

WST_RAIL_H = 72

WST_POST_W = 4

WST_RAIL_T = 4

room_splits = [-1072, -950, -1200, -850, -1300]

wx1, wx2 = bix1, KH_ENT_X1 - KH_WALL

ex1, ex2 = KH_ENT_X2 + KH_WALL, bix2

wxc = (wx1 + wx2) // 2

exc = (ex1 + ex2) // 2

w_hall_openings = [(sty1, KH_GROUND_Z, sty2, KH_Z2)]

e_hall_openings = [(sty1, KH_GROUND_Z, sty2, KH_Z2)]

DRAW_KH_FASCIA_TEXT = True

fas_y1, fas_y2 = PB_Y1 - 6, PB_Y1

fas_y3, fas_y4 = PB_Y2, PB_Y2 + 6

fas_x1, fas_x2 = -500, 500

KH_FASCIA_PX_W, KH_FASCIA_PX_H = 4, 4

KH_FASCIAKH_FASCIA_FONT_ROWS = 6

KH_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"

char_w = (4 + 1) * KH_FASCIA_PX_W

total_w = len(KH_FASCIA_TEXT) * char_w - KH_FASCIA_PX_W

text_x0 = 0 - total_w // 2

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

CS_LAMP_POST_H = PB_DZ2 - 32

CS_LAMP_POST_XS = [
    2158,
    1246,
]

lamp_post_ys = [EP_Y - EP_HW - 160]

PB_SPAN_CENTRES = [
    (PB_X1 + PB_ARCH_X[0]) // 2,
    (PB_ARCH_X[0] + PB_ARCH_X[1]) // 2,
    (PB_ARCH_X[1] + PB_ARCH_X[2]) // 2,
    (PB_ARCH_X[2] + PB_X2) // 2,
    (PB_X2 + PB_ARCH_X[4]) // 2,
    (PB_ARCH_X[4] + WORLD_X2 - WALL_T) // 2,
]

PB_PEND_XS = PB_SPAN_CENTRES

CS_ARCH_RIN_PRE = 256

CS_ARCH_ROUT_PRE = 312

CS_ARCH_STILT_PRE = 96

CS_ARCH_W_PRE = 48

CS_ARCH_WALL_W_PRE = 320

cs_arch_top_pre = FLOOR_Z2 + CS_ARCH_STILT_PRE + CS_ARCH_RIN_PRE

DECK_Z = dtop(0) + 8

ROAD_Z = FLOOR_Z2 + 8

room_goodies = [
    "item_health",
    "weapon_supershotgun",
    "item_shells",
    "item_rockets",
    "weapon_nailgun",
    "item_spikes",
    "weapon_grenadelauncher",
    "item_health",
    "item_shells",
    "item_rockets",
    "item_health",
    "weapon_supershotgun",
    "item_spikes",
    "item_shells",
    "weapon_nailgun",
    "item_rockets",
    "item_health",
    "weapon_grenadelauncher",
    "item_shells",
    "item_spikes",
]

gi = 0

west_stair_center_x = (wstx1 + wstx2) // 2

west_stair_north_y = (wst_midY + wsty2) // 2

west_stair_south_y = (wsty1 + wst_midY) // 2

hall_center_x = (KH_ENT_X1 + KH_ENT_X2) // 2

hall_light_ys = [
    biy1 + (biy2 - biy1) * i // 4
    for i in range(1, 4)  # quarters: 25%, 50%, 75%
] + [
    biy1 + (biy2 - biy1) // 8,  # 12.5% (near south end)
    biy1 + (biy2 - biy1) * 7 // 8,  # 87.5% (near north end)
]

entry_corridor_x = KH_ENT_X2 + 64

entry_corridor_y = KH_Y2 - 48

KH_SHELF_H = 64

KH_SHELF_D = 16

KH_SHELF_W = 64

shelf_offsets = [0, 0, 0, 0, 0]

wlx1 = WORLD_X1 + WALL_T

wlx2 = wlx1 + ARCH_SLAB_W

elx1 = WORLD_X2 - WALL_T - ARCH_SLAB_W

elx2 = WORLD_X2 - WALL_T

east_lower_deck_x = elx1 - 64

CS_ARCH_RIN = 256

CS_ARCH_ROUT = 312

CS_ARCH_STILT = 96

CS_ARCH_W = 48

CS_ARCH_TRIG_INSET = 8

CS_ARCH_WALL_W = 320

kh_cy = (KH_Y1 + KH_Y2) // 2

RH_NORTH_CY = (RH_NORTH_Y1 + RH_NORTH_Y2) // 2

RH_CX = (RH_X1 + RH_X2) // 2

RH_SOUTH1_CY = (RH_SOUTH1_Y1 + RH_SOUTH1_Y2) // 2

RH_SOUTH2_CY = (RH_SOUTH2_Y1 + RH_SOUTH2_Y2) // 2

ennis_pil_flame_z = EP_PIL_ZB + EP_PIL_POST_H + EP_PIL_CAP_H + EP_PIL_BELL2_H + 20

ennis_pil_cx = EP_PIL_X1 + EP_PIL_HW

abutment_pier_x = min(PB_ARCH_X)

abutment_arch_z = FLOOR_Z2 + PB_PIL_BASE_H + 60

bldg_light_x = (RH_X1 + RH_X2) // 2

tree_positions = [
    # Trees flanking Knott Hall (west side — bridge01, bridge10)
    (RH_X1 - 80, -600),
    (RH_X1 - 200, -300),
    (RH_X1 - 80, 200),
    (RH_X1 - 200, 500),
    # Along Ennis Parallel (campus side, west of Charles St — bridge02)
    (ROAD_X1 - 200, bw_ny - 100),
    (ROAD_X1 - 400, bw_ny - 80),
    (ROAD_X1 - 600, bw_ny - 120),
]

all_tree_brushes = []

charles_tree_height = KH_Z2

kh_tree_span = KH_Y2 - KH_Y1

charles_tree_row_near_x = ROAD_X2 + CS_WALK_W + 300

charles_tree_row_far_x = ROAD_X2 + CS_WALK_W + 560

charles_tree_row2_ys = [int(KH_Y1 + kh_tree_span * f) for f in (0.25, 0.75)]

charles_tree_row3_ys = [int(KH_Y1 + kh_tree_span * f) for f in (0.15, 0.5, 0.85)]

charles_giant_tree_brushes = []

east_ground_tree_height = KH_Z2

east_ground_spacing = 350

east_ground_jitter = 120

east_ground_buffer = 120

east_ground_x1 = ROAD_X2 + CS_WALK_W + east_ground_buffer

east_ground_x2 = WORLD_X2 - WALL_T - east_ground_buffer

east_ground_y1 = bw_ny + EP_WALL_T + 200

east_ground_y2 = WORLD_Y2 - WALL_T - east_ground_buffer

east_ground_giant_brushes = []

grid_x = east_ground_x1

bush_positions = [
    # Along north face of Ennis brick wall (campus grass side, not sidewalk)
    (bw_x1 + 60, bw_ny + EP_WALL_T + 40),
    (bw_x1 + 160, bw_ny + EP_WALL_T + 40),
    (bw_x1 + 260, bw_ny + EP_WALL_T + 40),
    (bw_x1 + 360, bw_ny + EP_WALL_T + 40),
    # Along north face of iron fence
    (int(east_gate_x1 + 120), bw_ny + EP_WALL_T + 40),
    (int(east_gate_x1 + 300), bw_ny + EP_WALL_T + 40),
    (int(east_gate_x1 + 500), bw_ny + EP_WALL_T + 40),
    (int(east_gate_x1 + 700), bw_ny + EP_WALL_T + 40),
    # Along north face of cement parapet wall
    (int(cement_wall_x1 + 120), bw_ny + EP_WALL_T + 40),
    (int(cement_wall_x1 + 320), bw_ny + EP_WALL_T + 40),
    (int(cement_wall_x1 + 560), bw_ny + EP_WALL_T + 40),
    # Along Knott Hall west face (outside building)
    (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2 - 200),
    (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2),
    (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2 + 200),
    # Along west building east face (outside building)
    (RH_X2 + 48, -200),
    (RH_X2 + 48, 200),
    (RH_X2 + 48, 500),
]

all_bush_brushes = []

kh_verge_y = EP_Y - EP_HW - 100

kh_bush_spacing = 120

kh_bush_buffer = 60

kh_bush_size = 40

kh_bush_jitter_x = 40

kh_bush_jitter_y = 30

kh_verge_brushes = []

CS_PLT_W = 128

CS_PLT_H = 12

CS_PLT_SPEED = 180

CS_PLT_X_OUT = ROAD_X2 // 4

CS_PLT_X_RET = -(ROAD_X2 * 3 // 4)

CS_PLT_Y_S = CS_Y1 + CS_PLT_W // 2 + 48

CS_PLT_Y_OUT = EP_Y - EP_HW + 16

CS_PLT_Y_RET = EP_Y + EP_HW // 8

CS_PLT_BR_X = KH_BR_RD_X1 + KH_BR_HW // 2

platform_z_charles = ROAD_Z + CS_PLT_H // 2

platform_z_flat = FLOOR_Z2 + 2 + CS_PLT_H // 2

platform_z_backroad_south = KH_BR_ZT_S + 2 + CS_PLT_H // 2

rocket_hover_height = CS_PLT_H + 56

backroad_mid_y = (KH_BR_Y1 + KH_BR_Y2) // 2

backroad_mid_z = (
    FLOOR_Z2
    + 2
    + (KH_BR_ZT_S - KH_BR_ZT_N) * (backroad_mid_y - KH_BR_Y2) // (KH_BR_Y1 - KH_BR_Y2)
)

monster_stand_z = ROAD_Z + 24

backroad_center_x = (KH_BR_RD_X1 + KH_BR_RD_X2) // 2

hall_center_x = (KH_ENT_X1 + KH_ENT_X2) // 2

deck_center_z = int(dtop(0)) + 24

deck_p3_z = int(dtop(525)) + 24

walkway_mid_x = (PB_X2 + WALK_X1) // 2

accessible_walk_z = KH_GROUND_Z + 24

east_shift_start = 0.0
east_shift_end = -((WORLD_X2 - WALL_T) - PB_ARCH_X[4]) * math.tan(
    math.radians(EAST_SPAN_ANGLE)
)
east_pivot_x = PB_ARCH_X[4]

cement_wall_lamp_posts = [
    (
        cement_wall_x1,
        (cement_wall_y1 + cement_wall_y2) // 2,
        FLOOR_Z2 + cement_wall_pillar_height + 186,
    ),
    (
        cement_wall_x2,
        (cement_wall_y1 + cement_wall_y2) // 2,
        FLOOR_Z2 + cement_wall_pillar_height + 186,
    ),
]
