#!/usr/bin/env python3
"""Generate loyola.map — Loyola bridge + brutalist building Quake 1 deathmatch map.

Layout:
  - Rectangular open world (±1024 E-W × ±960 N-S), open sky
  - Road runs N-S under the bridge (like Charles Street at Loyola Maryland)
  - Bridge spans E-W at deck height ~144; arched stone pillars over the road
  - Brutalist building on south campus (X=-256 to 256, Y=-800 to -256, 4 floors)
    North face faces bridge; ground-level entrance at X=-64..64
    Lift shaft at center-north rises from ground through roof opening to rooftop
  - West arch teleports to east; east arch teleports to west
"""

import math

# ── Scale ─────────────────────────────────────────────────────────────────────
SCALE = 15.108  # Quake units per foot (1050 units = 69 ft 6 in arched span)


def ft(feet, inches=0):
    """Convert real-world feet (+ optional inches) to Quake units."""
    return round((feet + inches / 12) * SCALE)


# ── Textures ──────────────────────────────────────────────────────────────────
T_STONE = "city6_7"  # supporting pillars + arch ring
T_FLOOR = "afloor1_4"  # deck top surface
T_CEMENT = "wbrick1_5"  # parapet / bridge walls (cement look)
T_WALL = "tech03_1"  # building walls — ep1 military base
T_FLOOR_BLDG = "tech10_1"  # building floors and ceilings
T_METAL = "metal5_4"  # pillar cap trim
T_ROCK = "rock1_2"  # cave outer shell
T_SKY = "sky1"  # open sky ceiling
T_LAVA = "*lava1"  # torch flame
T_LIGHT_PANEL = "sfloor4_4"  # light panel
T_TELEPORT = "*teleport"  # teleport effect

# ── Bridge spine ──────────────────────────────────────────────────────────────
# Blueprint: 1050-unit arched span (69.5 ft), 750-unit flat approaches (49 ft 1 in)
# Scale: 1 ft ≈ 15.1 units  (derived from 1050 units = 69.5 ft)
BRX1, BRX2 = -525, 525  # arched span = 1050 units = 69 ft 6 in
BRY1, BRY2 = -136, 136  # N-S width = 272 units ≈ 18 ft
DZ1, DZ2 = 128, 144  # flat deck bottom / top (arch offsets added on top)

# ── Arch profile ──────────────────────────────────────────────────────────────
# Blueprint: pillar heights 19 ft (ends) → 26 ft (centre) → rise = 7 ft = 106 units
ARCH_RISE = 106  # centre rises 106 units = 7 ft above ends
ARCH_SEGS = 16  # segments approximating the curve
SEG_W = (BRX2 - BRX1) / ARCH_SEGS  # 65.625 units per segment


def arch_z(x):
    """Z offset above flat datum for parabolic arch at x."""
    xc = (BRX1 + BRX2) / 2.0
    half = (BRX2 - BRX1) / 2.0
    return ARCH_RISE * max(0.0, 1.0 - ((x - xc) / half) ** 2)


def dtop(x):
    return DZ2 + arch_z(x)  # deck surface Z at x


def dbot(x):
    return DZ1 + arch_z(x)  # deck bottom  Z at x


# ── Parapet + pillar dimensions (above deck surface) ─────────────────────────
PAR_H = ft(4)  # parapet wall height above deck = 4 ft = 60 units
PAR_W = ft(2, 6)  # parapet wall N-S width = 2 ft 6 in = 38 units
PIL_EXTRA = 32  # extra pillar post height above parapet (gameplay)
PIL_CAP_H = 8  # cap slab height
PIL_PYR_H = (
    8  # pyramid cap height on structural support piers (subtle concrete ornament)
)
PIL_PYR_W = 16  # pyramid base half-width (centred on cap slab)
P_HW = ft(2, 5.5)  # pillar post half-width = half of 4 ft 11 in = 37 units
P_CE = 17  # cap overhang each side = (7 ft 2 in - 4 ft 11 in) / 2

# ── Pillar X positions — 5 pillars (Pillar 1–5) ──────────────────────────────
# Blueprint: 5 labelled pillars; outer pair ≈ ±350, inner pair ≈ ±175, centre 0
PXS = [-350, -175, 0, 175, 350]  # pillar X positions (5 piers)
# Bridge support visibility: False = none, set of X positions = those piers only, True = all
# PXS = [-350, -175, 0, 175, 350]; add pairs from outermost in: {-350,350} → {-175,175} → {0}
SHOW_SUPPORTS = {-350, 350}  # outer pair (furthest from centre)

# ── World layout ──────────────────────────────────────────────────────────────
WALL_T = 16
FZ1, FZ2 = -16, 0
ROAD_X1, ROAD_X2 = -256, 256  # road channel E-W bounds (under bridge)
# Flat approach = 49 ft 1 in = 741 units per side of the 1050-unit arched span
# East side extended by one building width (500) to give the building room
BLDG_WIDTH = 500
WORLD_X1 = -(525 + 741)  # = -1266 (west end unchanged)
WORLD_X2 = 525 + 741 + BLDG_WIDTH  # = 1766  (east end extended)
WORLD_Y1, WORLD_Y2 = -960, 960  # full world N-S extent

# ── Building (south campus, brutalist tower) ─────────────────────────────────
# Pushed near the east world end; 64-unit gap between building and east wall
BLDG_X2 = WORLD_X2 - WALL_T - 64  # = 1686
BLDG_X1 = BLDG_X2 - BLDG_WIDTH  # = 1186
BLDG_CX = (BLDG_X1 + BLDG_X2) // 2  # = 1436
BLDG_Y1, BLDG_Y2 = -800, -256  # south of bridge south edge
BLDG_WALL = 16  # wall thickness
FLOOR_H = 128  # floor-to-floor height
BLDG_FLOORS = 4  # number of floors
# Building is in flat approach: deck = DZ2 = 144; 2nd floor aligns automatically
BLDG_GROUND_Z = max(FZ2, DZ2 - FLOOR_H - BLDG_WALL)  # = 0 (no hill needed)
BLDG_Z2 = BLDG_GROUND_Z + BLDG_FLOORS * FLOOR_H

# Sky ceiling must clear the building
WORLD_Z2 = max(640, BLDG_Z2 + 128)

# ── Walkway from bridge to building 2nd floor ────────────────────────────────
# Flat span at DZ2=144 (flat approach section); centered on building entrance
WALK_X1 = BLDG_CX - 64  # = 536
WALK_X2 = BLDG_CX + 64  # = 664
WALK_ZT1 = int(dtop(BLDG_CX))  # = DZ2 = 144 (flat approach, no arch rise)
WALK_ZT2 = BLDG_GROUND_Z + FLOOR_H + BLDG_WALL  # = 144 = WALK_ZT1 (flat)
# No ramp needed: BLDG_GROUND_Z = 0 = road level

# ── Arch segments ─────────────────────────────────────────────────────────────
A_SEGS = 16


# ── Geometry helpers ──────────────────────────────────────────────────────────
def fv(v):
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"


def pt(x, y, z):
    return f"( {fv(x)} {fv(y)} {fv(z)} )"


def face(p1, p2, p3, tex):
    return f"{pt(*p1)} {pt(*p2)} {pt(*p3)} {tex} 0 0 0 1 1"


def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None):
    tt = tt or tex
    tb = tb or tex
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1, z1), (x1, y2, z1), (x1, y1, z2), tex),
                face((x2, y1, z1), (x2, y1, z2), (x2, y2, z1), tex),
                face((x1, y1, z1), (x1, y1, z2), (x2, y1, z1), tex),
                face((x1, y2, z1), (x2, y2, z1), (x1, y2, z2), tex),
                face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tb),
                face((x1, y1, z2), (x1, y2, z2), (x2, y1, z2), tt),
            ]
        )
        + "\n}"
    )


def pyramid(x1, y1, z1, x2, y2, z2, tex):
    """Square pyramid: base x1..x2, y1..y2 at z=z1; apex at centre at z=z2."""
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tex),  # bottom
                face((x2, y1, z1), (x1, y1, z1), (cx, cy, z2), tex),  # south
                face((x1, y2, z1), (x2, y2, z1), (cx, cy, z2), tex),  # north
                face((x1, y1, z1), (x1, y2, z1), (cx, cy, z2), tex),  # west
                face((x2, y2, z1), (x2, y1, z1), (cx, cy, z2), tex),  # east
            ]
        )
        + "\n}"
    )


def ramp_slab(x1, x2, y1, y2, zb1, zb2, zt1, zt2, tex, tt=None, tb=None):
    """Prismatic slab whose bottom and top faces are sloped in the X direction.
    zb1/zt1 = bottom/top Z at x=x1;  zb2/zt2 = bottom/top Z at x=x2."""
    tt = tt or tex
    tb = tb or tex
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1, zb1), (x1, y2, zb1), (x1, y1, zt1), tex),  # -X
                face((x2, y1, zb2), (x2, y1, zt2), (x2, y2, zb2), tex),  # +X
                face((x1, y1, zb1), (x1, y1, zt1), (x2, y1, zb2), tex),  # -Y
                face((x1, y2, zb1), (x2, y2, zb2), (x1, y2, zt1), tex),  # +Y
                face((x1, y1, zb1), (x2, y1, zb2), (x1, y2, zb1), tb),  # sloped bottom
                face((x1, y1, zt1), (x1, y2, zt1), (x2, y1, zt2), tt),  # sloped top
            ]
        )
        + "\n}"
    )


def ramp_slab_y(x1, x2, y1, y2, zb1, zb2, zt1, zt2, tex, tt=None, tb=None):
    """Prismatic slab whose bottom and top faces are sloped in the Y direction.
    zb1/zt1 = bottom/top Z at y=y1;  zb2/zt2 = bottom/top Z at y=y2.
    y1 and y2 may be passed in either order."""
    # Normalise so y1 <= y2 (face normals assume this ordering)
    if y1 > y2:
        y1, y2 = y2, y1
        zb1, zb2 = zb2, zb1
        zt1, zt2 = zt2, zt1
    tt = tt or tex
    tb = tb or tex
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1, zb1), (x1, y2, zb2), (x1, y1, zt1), tex),  # -X
                face((x2, y1, zb1), (x2, y1, zt1), (x2, y2, zb2), tex),  # +X
                face((x1, y1, zb1), (x1, y1, zt1), (x2, y1, zb1), tex),  # -Y
                face((x1, y2, zb2), (x2, y2, zb2), (x1, y2, zt2), tex),  # +Y
                face((x1, y1, zb1), (x2, y1, zb1), (x1, y2, zb2), tb),  # sloped bottom
                face((x1, y1, zt1), (x1, y2, zt2), (x2, y1, zt1), tt),  # sloped top
            ]
        )
        + "\n}"
    )


def arch_seg(xb, xf, yc, zc, rin, rout, t1d, t2d, tex):
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    yi, zi = yc + rin * cm, zc + rin * sm
    yo, zo = yc + rout * cm, zc + rout * sm
    return (
        "{\n"
        + "\n".join(
            [
                face((xf, yc, zc), (xf, yc, zc + 1), (xf, yc + 1, zc), tex),
                face((xb, yc, zc), (xb, yc + 1, zc), (xb, yc, zc + 1), tex),
                face((xf, yc, zc), (xf, yc + c1, zc + s1), (xb, yc, zc), tex),
                face((xf, yc, zc), (xb, yc, zc), (xf, yc + c2, zc + s2), tex),
                face((xf, yi, zi), (xb, yi, zi), (xf, yi - sm, zi + cm), tex),
                face((xf, yo, zo), (xf, yo - sm, zo + cm), (xb, yo, zo), tex),
            ]
        )
        + "\n}"
    )


def arch_pie_seg(xb, xf, yc, zc, rad, t1d, t2d, tex):
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    yo, zo = yc + rad * cm, zc + rad * sm
    return (
        "{\n"
        + "\n".join(
            [
                face((xf, yc, zc), (xf, yc, zc + 1), (xf, yc + 1, zc), tex),
                face((xb, yc, zc), (xb, yc + 1, zc), (xb, yc, zc + 1), tex),
                face((xf, yc, zc), (xf, yc + c1, zc + s1), (xb, yc, zc), tex),
                face((xf, yc, zc), (xb, yc, zc), (xf, yc + c2, zc + s2), tex),
                face((xf, yo, zo), (xf, yo - sm, zo + cm), (xb, yo, zo), tex),
            ]
        )
        + "\n}"
    )


def arch_fill(x1, x2, yc, floor_z, rin, segs, tex, stilt_h=None):
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h
    seg = 180.0 / segs
    brushes = []
    brushes.append(box(x1, -rin, floor_z, x2, rin, sprz, tex))
    for i in range(segs):
        brushes.append(
            arch_pie_seg(x1, x2, yc, float(sprz), rin, i * seg, (i + 1) * seg, tex)
        )
    return brushes


def arch_seg_y(yb, yf, xc, zc, rin, rout, t1d, t2d, tex):
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    xi, zi = xc + rin * cm, zc + rin * sm
    xo, zo = xc + rout * cm, zc + rout * sm
    return (
        "{\n"
        + "\n".join(
            [
                face((xc, yf, zc), (xc + 1, yf, zc), (xc, yf, zc + 1), tex),
                face((xc, yb, zc), (xc, yb, zc + 1), (xc + 1, yb, zc), tex),
                face((xc, yf, zc), (xc, yb, zc), (xc + c1, yf, zc + s1), tex),
                face((xc, yf, zc), (xc + c2, yf, zc + s2), (xc, yb, zc), tex),
                face((xi, yf, zi), (xi - sm, yf, zi + cm), (xi, yb, zi), tex),
                face((xo, yf, zo), (xo, yb, zo), (xo - sm, yf, zo + cm), tex),
            ]
        )
        + "\n}"
    )


def arch_pie_seg_y(yb, yf, xc, zc, rad, t1d, t2d, tex):
    t1, t2 = math.radians(t1d), math.radians(t2d)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    xo, zo = xc + rad * cm, zc + rad * sm
    return (
        "{\n"
        + "\n".join(
            [
                face((xc, yf, zc), (xc + 1, yf, zc), (xc, yf, zc + 1), tex),
                face((xc, yb, zc), (xc, yb, zc + 1), (xc + 1, yb, zc), tex),
                face((xc, yf, zc), (xc, yb, zc), (xc + c1, yf, zc + s1), tex),
                face((xc, yf, zc), (xc + c2, yf, zc + s2), (xc, yb, zc), tex),
                face((xo, yf, zo), (xo, yb, zo), (xo - sm, yf, zo + cm), tex),
            ]
        )
        + "\n}"
    )


def arch_fill_y(y1, y2, xc, floor_z, rin, segs, tex, stilt_h=None):
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h
    seg = 180.0 / segs
    brushes = []
    brushes.append(box(-rin, y1, floor_z, rin, y2, sprz, tex))
    for i in range(segs):
        brushes.append(
            arch_pie_seg_y(y1, y2, xc, float(sprz), rin, i * seg, (i + 1) * seg, tex)
        )
    return brushes


def arch_wall(x1, x2, y1, y2, floor_z, ceil_z, rin, rout, segs, tex, stilt_h=None):
    """Stone wall with arched opening centred at Y=0.

    stilt_h: height of straight sides before the arch springs (defaults to rin,
             giving a plain semicircle; set > rin for a tall stilted/gothic arch).
    """
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h  # Z where arch springs
    seg = 180.0 / segs
    brushes = []
    # Solid rock on either side of the arch (makes pier a solid mass, not freestanding)
    if y1 < -rout:
        brushes.append(box(x1, y1, floor_z, x2, -rout, ceil_z, tex))
    if y2 > rout:
        brushes.append(box(x1, rout, floor_z, x2, y2, ceil_z, tex))
    brushes.append(
        box(x1, -rout, floor_z, x2, -rin, ceil_z, tex)
    )  # south pillar, full height
    brushes.append(
        box(x1, rin, floor_z, x2, rout, ceil_z, tex)
    )  # north pillar, full height
    # Cap above arch crown: fills above the inner arc top
    brushes.append(box(x1, -rin, sprz + rin, x2, rin, ceil_z, tex))
    for i in range(segs):
        brushes.append(
            arch_seg(x1, x2, 0.0, float(sprz), rin, rout, i * seg, (i + 1) * seg, tex)
        )
    return brushes


def arch_wall_y(y1, y2, x1, x2, floor_z, ceil_z, rin, rout, segs, tex, stilt_h=None):
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h
    seg = 180.0 / segs
    brushes = []
    # Side walls removed to make arch freestanding
    # if x1 < -rout:
    #     brushes.append(box(x1, y1, floor_z, -rout, y2, ceil_z, tex))
    # if x2 > rout:
    #     brushes.append(box(rout, y1, floor_z, x2, y2, ceil_z, tex))
    brushes.append(box(-rout, y1, floor_z, -rin, y2, sprz, tex))
    brushes.append(box(rin, y1, floor_z, rout, y2, sprz, tex))
    for i in range(segs):
        brushes.append(
            arch_seg_y(y1, y2, 0.0, float(sprz), rin, rout, i * seg, (i + 1) * seg, tex)
        )
    return brushes


def ent(cls, **kw):
    lines = ["{", f'"classname" "{cls}"']
    for k, v in kw.items():
        lines.append(f'"{k}" "{v}"')
    lines.append("}")
    return "\n".join(lines)


def brush_ent(cls, brushes, **kw):
    lines = ["{", f'"classname" "{cls}"']
    for k, v in kw.items():
        lines.append(f'"{k}" "{v}"')
    for b in brushes:
        # Each b is a string "{\n...\n}" from box/ramp_slab
        # Keep the braces for the brush within the entity
        lines.append(b)
    lines.append("}")
    return "\n".join(lines)


def layered_wall(x1, y1, z1, x2, y2, z2, openings, tex):
    """Wall slab (thin in Y) with rectangular cutouts.
    openings: list of (ox1, oz1, ox2, oz2) — regions to omit in the x,z plane.
    """
    xs = sorted({x1, x2} | {o[0] for o in openings} | {o[2] for o in openings})
    zs = sorted({z1, z2} | {o[1] for o in openings} | {o[3] for o in openings})
    brushes = []
    for xi in range(len(xs) - 1):
        for zi in range(len(zs) - 1):
            cx1, cx2 = xs[xi], xs[xi + 1]
            cz1, cz2 = zs[zi], zs[zi + 1]
            covered = any(
                o[0] <= cx1 and cx2 <= o[2] and o[1] <= cz1 and cz2 <= o[3]
                for o in openings
            )
            if not covered:
                brushes.append(box(cx1, y1, cz1, cx2, y2, cz2, tex))
    return brushes


def layered_wall_y(y1, x1, z1, y2, x2, z2, openings, tex):
    """Wall slab (thin in X) with rectangular cutouts.
    openings: list of (oy1, oz1, oy2, oz2) — regions to omit in the y,z plane.
    """
    ys = sorted({y1, y2} | {o[0] for o in openings} | {o[2] for o in openings})
    zs = sorted({z1, z2} | {o[1] for o in openings} | {o[3] for o in openings})
    brushes = []
    for yi in range(len(ys) - 1):
        for zi in range(len(zs) - 1):
            cy1, cy2 = ys[yi], ys[yi + 1]
            cz1, cz2 = zs[zi], zs[zi + 1]
            covered = any(
                o[0] <= cy1 and cy2 <= o[2] and o[1] <= cz1 and cz2 <= o[3]
                for o in openings
            )
            if not covered:
                brushes.append(box(x1, cy1, cz1, x2, cy2, cz2, tex))
    return brushes


# ── Build world brushes ───────────────────────────────────────────────────────
B = []

# ════════════════════════════════════════════════════════════════════════════════
# RECTANGULAR WORLD SHELL — floor, 4 outer walls, sky ceiling
# ════════════════════════════════════════════════════════════════════════════════
B.append(box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y2, FZ2, T_ROCK))  # floor
B.append(
    box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X1 + WALL_T, WORLD_Y2, WORLD_Z2, T_ROCK)
)  # W wall
B.append(
    box(WORLD_X2 - WALL_T, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y2, WORLD_Z2, T_ROCK)
)  # E wall
B.append(
    box(WORLD_X1, WORLD_Y2 - WALL_T, FZ1, WORLD_X2, WORLD_Y2, WORLD_Z2, T_ROCK)
)  # N wall
B.append(
    box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y1 + WALL_T, WORLD_Z2, T_ROCK)
)  # S wall
B.append(
    box(WORLD_X1, WORLD_Y1, WORLD_Z2 - WALL_T, WORLD_X2, WORLD_Y2, WORLD_Z2, T_SKY)
)  # sky

# ════════════════════════════════════════════════════════════════════════════════
# ARCHED BRIDGE DECK — extended to map boundaries OX1, OX2
# ════════════════════════════════════════════════════════════════════════════════
# Extend bridge deck to both world edges
B.append(
    box(WORLD_X1 + WALL_T, BRY1, DZ1, BRX1, BRY2, DZ2, T_STONE, tt=T_FLOOR, tb=T_FLOOR)
)
B.append(
    box(BRX2, BRY1, DZ1, WORLD_X2 - WALL_T, BRY2, DZ2, T_STONE, tt=T_FLOOR, tb=T_FLOOR)
)

for i in range(ARCH_SEGS):
    sx1 = BRX1 + i * SEG_W
    sx2 = sx1 + SEG_W
    B.append(
        ramp_slab(
            sx1,
            sx2,
            BRY1,
            BRY2,
            dbot(sx1),
            dbot(sx2),
            dtop(sx1),
            dtop(sx2),
            T_STONE,
            tt=T_FLOOR,
            tb=T_FLOOR,
        )
    )

# ── Parapet walls — extended to both world edges ──────────────────────────────
B.append(
    box(WORLD_X1 + WALL_T, BRY2 - PAR_W, DZ2, BRX1, BRY2, DZ2 + PAR_H, T_CEMENT)
)  # North west
B.append(
    box(WORLD_X1 + WALL_T, BRY1, DZ2, BRX1, BRY1 + PAR_W, DZ2 + PAR_H, T_CEMENT)
)  # South west
B.append(
    box(BRX2, BRY2 - PAR_W, DZ2, WORLD_X2 - WALL_T, BRY2, DZ2 + PAR_H, T_CEMENT)
)  # North east
# South east — gap at WALK_X1..WALK_X2 for walkway connection to building
B.append(box(BRX2, BRY1, DZ2, WALK_X1, BRY1 + PAR_W, DZ2 + PAR_H, T_CEMENT))
B.append(
    box(WALK_X2, BRY1, DZ2, WORLD_X2 - WALL_T, BRY1 + PAR_W, DZ2 + PAR_H, T_CEMENT)
)

for i in range(ARCH_SEGS):
    sx1 = BRX1 + i * SEG_W
    sx2 = sx1 + SEG_W
    pb1, pb2 = dtop(sx1), dtop(sx2)  # parapet base follows deck top
    pt1, pt2 = pb1 + PAR_H, pb2 + PAR_H  # parapet top = base + PAR_H
    # North parapet
    B.append(ramp_slab(sx1, sx2, BRY2 - PAR_W, BRY2, pb1, pb2, pt1, pt2, T_CEMENT))
    # South parapet — omit any segment that overlaps the walkway gap (X=WALK_X1..WALK_X2)
    if not (sx1 < WALK_X2 and sx2 > WALK_X1):
        B.append(ramp_slab(sx1, sx2, BRY1, BRY1 + PAR_W, pb1, pb2, pt1, pt2, T_CEMENT))


# ── Pillar posts (stone piers with arches) ───────────────────────────────────
# Each pillar position now features a narrow arched pier supporting the deck.
# Blueprint arch dimensions (rout = outer radius, rin = inner/opening radius):
#   Outer (Pillar 1/5): 7 ft 9 in total → rout=59;  2 ft 9 in opening  → rin=21
#   Inner (Pillar 2/4): 8 ft 8 in total → rout=65;  ~4 ft opening      → rin=30
#   Centre (Pillar 3): 13 ft   total → rout=98;  9 ft arch opening → rin=68
_OUTER_R = (136, 96)  # rout=BRY2: gap starts at h=96.3 > rin=96, capped by cap box
_INNER_R = (136, 96)
_CENTR_R = (136, 96)
if SHOW_SUPPORTS:
    for px in PXS:
        if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
            continue
        pdeck = dtop(px)  # deck surface at this X
        ppar = pdeck + PAR_H  # parapet top
        ppil = ppar + PIL_EXTRA  # pillar post top
        pcap = ppil + PIL_CAP_H  # cap slab top
        cy_n = BRY2 - PAR_W // 2  # north cap centre Y
        cy_s = BRY1 + PAR_W // 2  # south cap centre Y

        # Width of the pier in X (matches cap stone width)
        x1, x2 = px - P_HW - P_CE, px + P_HW + P_CE

        # Arch opening varies by pillar type (outer / inner / centre)
        if px == 0:
            a_rout, a_rin = _CENTR_R
        elif abs(px) == max(abs(p) for p in PXS):
            a_rout, a_rin = _OUTER_R
        else:
            a_rout, a_rin = _INNER_R
        a_stilt = int(pdeck) - a_rout - FZ2 - 16
        if a_stilt < 0:
            a_stilt = 0

        # Add the arched pier structure (spans BRY1 to BRY2)
        B.extend(
            arch_wall(
                x1,
                x2,
                BRY1,
                BRY2,
                FZ2,
                int(pdeck) - 16,
                a_rin,
                a_rout,
                A_SEGS,
                T_STONE,
                stilt_h=a_stilt,
            )
        )

        # Pillar tops (the parts that stick above the deck)
        # North pillar top + flat cap slab + small concrete pyramid
        B.append(box(px - P_HW, BRY2 - PAR_W, pdeck, px + P_HW, BRY2, ppil, T_STONE))
        B.append(box(x1, BRY2 - PAR_W - P_CE, ppil, x2, BRY2 + P_CE, pcap, T_STONE))
        B.append(
            pyramid(
                px - PIL_PYR_W,
                cy_n - PIL_PYR_W,
                pcap,
                px + PIL_PYR_W,
                cy_n + PIL_PYR_W,
                pcap + PIL_PYR_H,
                T_CEMENT,
            )
        )

        # South pillar top + flat cap slab + small concrete pyramid
        B.append(box(px - P_HW, BRY1, pdeck, px + P_HW, BRY1 + PAR_W, ppil, T_STONE))
        B.append(box(x1, BRY1 - P_CE, ppil, x2, BRY1 + PAR_W + P_CE, pcap, T_STONE))
        B.append(
            pyramid(
                px - PIL_PYR_W,
                cy_s - PIL_PYR_W,
                pcap,
                px + PIL_PYR_W,
                cy_s + PIL_PYR_W,
                pcap + PIL_PYR_H,
                T_CEMENT,
            )
        )

        # Torch flames on cap top
        B.append(
            box(px - 4, cy_n - 4, pcap, px + 4, cy_n + 4, pcap + 10, T_STONE, tt=T_LAVA)
        )
        B.append(
            box(px - 4, cy_s - 4, pcap, px + 4, cy_s + 4, pcap + 10, T_STONE, tt=T_LAVA)
        )

# ── Teleport Arches at both ends of bridge ───────────────────────────────────
T_ARCH_RIN = 96
T_ARCH_ROUT = 136  # Fills the bridge width (updated to match BRY2=136)
T_ARCH_STILT = 96  # Height of straight sides
T_ARCH_CEIL = DZ2 + T_ARCH_STILT + T_ARCH_RIN + 32  # Stone above the arch
T_ARCH_W = 32  # Thickness of the arch in X

for _ex in [WORLD_X1 + WALL_T, WORLD_X2 - WALL_T - T_ARCH_W]:
    _xb, _xf = _ex, _ex + T_ARCH_W
    B.extend(
        arch_wall(
            _xb,
            _xf,
            BRY1,
            BRY2,
            DZ2,
            T_ARCH_CEIL,
            T_ARCH_RIN,
            T_ARCH_ROUT,
            A_SEGS,
            T_STONE,
            stilt_h=T_ARCH_STILT,
        )
    )

# ── Attached glow panel beneath arch centre ─────────────────────────────────
# Attached to bridge bottom (dbot(0) = 192). Size reduced to 1/4 (48x48).
PANEL_Z = int(dbot(0)) - 4
B.append(box(-24, -24, PANEL_Z, 24, 24, PANEL_Z + 4, T_LIGHT_PANEL))

# ── Light panels on inner parapet face (arch-aware Z) ────────────────────────
panel_xs = []
all_x = [BRX1] + PXS + [BRX2]
for i in range(len(all_x) - 1):
    panel_xs.append((all_x[i] + all_x[i + 1]) // 2)
for px in panel_xs:
    pbase = dtop(px)
    ph = pbase + PAR_H // 2 - 10
    pt_ = ph + 20
    B.append(
        box(px - 8, BRY2 - PAR_W - 3, ph, px + 8, BRY2 - PAR_W, pt_, T_LIGHT_PANEL)
    )
    B.append(
        box(px - 8, BRY1 + PAR_W, ph, px + 8, BRY1 + PAR_W + 3, pt_, T_LIGHT_PANEL)
    )


# ════════════════════════════════════════════════════════════════════════════════
# WALKWAY — flat bridge from south edge to building 2nd floor entrance
# X=-64..64, Y=BRY1..BLDG_Y2; flat at WALK_ZT1 = WALK_ZT2
# ════════════════════════════════════════════════════════════════════════════════
_wk_zb1 = WALK_ZT1 - BLDG_WALL  # slab bottom at bridge end  = 192
_wk_zb2 = WALK_ZT2 - BLDG_WALL  # slab bottom at building end = 128
B.append(
    ramp_slab_y(
        WALK_X1,
        WALK_X2,
        BRY1,
        BLDG_Y2,
        _wk_zb1,
        _wk_zb2,
        WALK_ZT1,
        WALK_ZT2,
        T_CEMENT,
        tt=T_FLOOR,
    )
)
# Side rails slope with the ramp
B.append(
    ramp_slab_y(
        WALK_X1 - 16,
        WALK_X1,
        BRY1,
        BLDG_Y2,
        WALK_ZT1,
        WALK_ZT2,
        WALK_ZT1 + PAR_H,
        WALK_ZT2 + PAR_H,
        T_CEMENT,
    )
)
B.append(
    ramp_slab_y(
        WALK_X2,
        WALK_X2 + 16,
        BRY1,
        BLDG_Y2,
        WALK_ZT1,
        WALK_ZT2,
        WALK_ZT1 + PAR_H,
        WALK_ZT2 + PAR_H,
        T_CEMENT,
    )
)


# ════════════════════════════════════════════════════════════════════════════════
# BRUTALIST BUILDING — south campus, 4-floor playable tower
# Footprint: X=-256 to 256, Y=-800 to -256, Z=0 to 512
# North face faces the bridge; ground-level entrance at X=-64 to 64
# Lift shaft at center-north rises from ground to rooftop
# ════════════════════════════════════════════════════════════════════════════════
_bix1 = BLDG_X1 + BLDG_WALL  # interior west
_bix2 = BLDG_X2 - BLDG_WALL  # interior east
_biy1 = BLDG_Y1 + BLDG_WALL  # interior south = -784
_biy2 = BLDG_Y2 - BLDG_WALL  # interior north = -272

# Entrance doorway — centred on building (BLDG_CX ± 64)
_ENT_X1, _ENT_X2 = BLDG_CX - 64, BLDG_CX + 64  # = 536, 664

# Lift shaft east of entrance: 16 units east of _ENT_X2, 128 wide
_stx1, _stx2 = _ENT_X2 + 16, _ENT_X2 + 16 + 128  # = 680, 808
_sty1, _sty2 = _biy2 - 128, _biy2  # Y: -400 to -272

# ── Outer walls ──────────────────────────────────────────────────────────────
# BLDG_GROUND_Z = 0: building sits at road level, no hill needed

# South wall — solid back wall
B.append(
    box(BLDG_X1, BLDG_Y1, BLDG_GROUND_Z, BLDG_X2, BLDG_Y1 + BLDG_WALL, BLDG_Z2, T_WALL)
)

# North wall — faces bridge; ground entrance + 2nd-floor walkway opening + windows
_door_n = [
    (_ENT_X1, BLDG_GROUND_Z, _ENT_X2, BLDG_GROUND_Z + FLOOR_H)
]  # ground entrance
_door_2 = [
    (_ENT_X1, WALK_ZT2, _ENT_X2, BLDG_GROUND_Z + FLOOR_H * 2)
]  # walkway entrance
_win_n = [
    (
        BLDG_CX - 128,
        BLDG_GROUND_Z + _f * FLOOR_H + 32,
        BLDG_CX + 128,
        BLDG_GROUND_Z + _f * FLOOR_H + 80,
    )
    for _f in range(1, BLDG_FLOORS)
]
B.extend(
    layered_wall(
        BLDG_X1,
        BLDG_Y2 - BLDG_WALL,
        BLDG_GROUND_Z,
        BLDG_X2,
        BLDG_Y2,
        BLDG_Z2,
        _door_n + _door_2 + _win_n,
        T_WALL,
    )
)

# East and West walls — window openings (3 per floor along Y axis)
_win_yw = [(BLDG_Y1 + 80 + _i * 192, BLDG_Y1 + 112 + _i * 192) for _i in range(3)]
_win_yz = []
for _f in range(BLDG_FLOORS):
    for _wy1, _wy2 in _win_yw:
        _win_yz.append(
            (
                _wy1,
                BLDG_GROUND_Z + _f * FLOOR_H + 32,
                _wy2,
                BLDG_GROUND_Z + _f * FLOOR_H + 80,
            )
        )

B.extend(
    layered_wall_y(
        BLDG_Y1,
        BLDG_X2 - BLDG_WALL,
        BLDG_GROUND_Z,
        BLDG_Y2,
        BLDG_X2,
        BLDG_Z2,
        _win_yz,
        T_WALL,
    )
)
B.extend(
    layered_wall_y(
        BLDG_Y1,
        BLDG_X1,
        BLDG_GROUND_Z,
        BLDG_Y2,
        BLDG_X1 + BLDG_WALL,
        BLDG_Z2,
        _win_yz,
        T_WALL,
    )
)

# Roof — open above lift shaft
B.append(
    box(BLDG_X1, BLDG_Y1, BLDG_Z2, _stx1, BLDG_Y2, BLDG_Z2 + BLDG_WALL, T_FLOOR_BLDG)
)  # west
B.append(
    box(_stx2, BLDG_Y1, BLDG_Z2, BLDG_X2, BLDG_Y2, BLDG_Z2 + BLDG_WALL, T_FLOOR_BLDG)
)  # east
B.append(
    box(_stx1, BLDG_Y1, BLDG_Z2, _stx2, _sty1, BLDG_Z2 + BLDG_WALL, T_FLOOR_BLDG)
)  # south of shaft

# ── Interior floor slabs (floors 1-3, lift shaft opening in center-north) ────
for _f in range(1, BLDG_FLOORS):
    _sz = BLDG_GROUND_Z + _f * FLOOR_H
    _st = _sz + BLDG_WALL
    B.append(box(_bix1, _biy1, _sz, _bix2, _sty1, _st, T_FLOOR_BLDG))  # south bulk
    B.append(box(_bix1, _sty1, _sz, _stx1, _biy2, _st, T_FLOOR_BLDG))  # west of shaft
    B.append(box(_stx2, _sty1, _sz, _bix2, _biy2, _st, T_FLOOR_BLDG))  # east of shaft

# ── Worldspawn ────────────────────────────────────────────────────────────────
worldspawn = (
    "{\n"
    '"classname" "worldspawn"\n'
    '"wad" "quake101.wad"\n'
    '"message" "Loyola Bridge"\n'
    f'"sky" "{T_SKY}"\n'
    '"ambient" "40"\n'
    '"dmflags" "128"\n' + "\n".join(B) + "\n}"
)

# ── Entities ──────────────────────────────────────────────────────────────────
E = []
DECK_Z = dtop(0) + 8  # centre of arch deck + a bit (spawn/item height)
ROAD_Z = FZ2 + 8

# Teleport destinations — west arch ↔ east arch
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_east",
        origin=f"{WORLD_X2 - WALL_T - 64} 0 {int(DZ2 + 40)}",
        angle="180",
    )
)
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_west",
        origin=f"{WORLD_X1 + WALL_T + 64} 0 {int(DZ2 + 40)}",
        angle="0",
    )
)

# West arch trigger → east destination
west_brushes = arch_fill(
    WORLD_X1 + WALL_T,
    WORLD_X1 + WALL_T + T_ARCH_W,
    0.0,
    DZ2,
    T_ARCH_RIN,
    A_SEGS,
    T_TELEPORT,
    stilt_h=T_ARCH_STILT,
)
E.append(brush_ent("trigger_teleport", west_brushes, target="dest_east"))
E.append(brush_ent("func_illusionary", west_brushes))

# East arch trigger → west destination
east_brushes = arch_fill(
    WORLD_X2 - WALL_T - T_ARCH_W,
    WORLD_X2 - WALL_T,
    0.0,
    DZ2,
    T_ARCH_RIN,
    A_SEGS,
    T_TELEPORT,
    stilt_h=T_ARCH_STILT,
)
E.append(brush_ent("trigger_teleport", east_brushes, target="dest_west"))
E.append(brush_ent("func_illusionary", east_brushes))


E.append(ent("info_player_start", origin=f"0 0 {int(dtop(0) + 32)}"))

_bcy = (BLDG_Y1 + BLDG_Y2) // 2  # building center Y = -528

for pos in [
    # Bridge deck
    (0, 0, int(dtop(0) + 32)),
    (-160, 0, int(dtop(-160) + 32)),
    (160, 0, int(dtop(160) + 32)),
    (-320, 0, int(dtop(-320) + 32)),
    (320, 0, int(dtop(320) + 32)),
    # Walkway mid-point
    (BLDG_CX, (BRY1 + BLDG_Y2) // 2, int(WALK_ZT1 + 32)),
    # Building ground floor (near entrance)
    (BLDG_CX, BLDG_Y2 - 64, BLDG_GROUND_Z + 40),
    # Building upper floors
    (BLDG_CX, _bcy, BLDG_GROUND_Z + FLOOR_H + 40),
    (BLDG_CX, _bcy, BLDG_GROUND_Z + FLOOR_H * 2 + 40),
    (BLDG_CX, _bcy, BLDG_GROUND_Z + FLOOR_H * 3 + 40),
    # East/west campus ground
    (1000, 0, ROAD_Z),
    (-1000, 0, ROAD_Z),
    # Road under bridge
    (0, 300, ROAD_Z),
    (0, -400, ROAD_Z),
]:
    E.append(ent("info_player_deathmatch", origin=f"{pos[0]} {pos[1]} {pos[2]}"))

E.append(ent("weapon_rocketlauncher", origin=f"0 0 {DECK_Z}"))
E.append(
    ent(
        "weapon_rocketlauncher",
        origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H + 40}",
    )
)
E.append(
    ent(
        "weapon_rocketlauncher",
        origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H * 3 + 40}",
    )
)
E.append(ent("weapon_rocketlauncher", origin=f"1000 0 {ROAD_Z}"))

for ax in PXS:
    E.append(ent("item_rockets", origin=f"{ax} 0 {int(dtop(ax) + 8)}"))
for _by in [_bcy - 80, _bcy + 80]:
    E.append(
        ent(
            "item_rockets",
            origin=f"{BLDG_CX + 80} {_by} {BLDG_GROUND_Z + FLOOR_H * 2 + 40}",
        )
    )
    E.append(
        ent(
            "item_rockets",
            origin=f"{BLDG_CX - 80} {_by} {BLDG_GROUND_Z + FLOOR_H * 2 + 40}",
        )
    )
for rx in [600, 1000]:
    E.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z}"))
    E.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z}"))

E.append(ent("item_health", origin=f"0 0 {DECK_Z}"))
E.append(ent("item_health", origin=f"{BLDG_CX} {BLDG_Y2 - 64} {BLDG_GROUND_Z + 40}"))
E.append(
    ent("item_health", origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H * 2 + 40}")
)

# Torch lights on pillar caps
if SHOW_SUPPORTS:
    for px in PXS:
        if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
            continue
        pbase = dtop(px)
        pcap = pbase + PAR_H + PIL_EXTRA + PIL_CAP_H
        cy_n = BRY2 - 12
        cy_s = BRY1 + 12
        E.append(
            ent("light", origin=f"{px} {cy_n} {int(pcap + 20)}", light="300", style="1")
        )
        E.append(
            ent("light", origin=f"{px} {cy_s} {int(pcap + 20)}", light="300", style="1")
        )

# Panel glow
for px in panel_xs:
    pbase = dtop(px)
    ph = int(pbase + PAR_H // 2)
    E.append(ent("light", origin=f"{px} {BRY2 - 30} {ph}", light="180"))
    E.append(ent("light", origin=f"{px} {BRY1 + 30} {ph}", light="180"))

# Lift (func_plat) — rides from ground floor up through roof opening to rooftop
_lift_travel = BLDG_FLOORS * FLOOR_H - 8  # travel distance (not absolute Z)
_lift_brush = [
    box(_stx1 + 2, _sty1 + 2, BLDG_Z2 - 8, _stx2 - 2, _sty2 - 2, BLDG_Z2, T_FLOOR_BLDG)
]
E.append(brush_ent("func_plat", _lift_brush, height=str(_lift_travel), speed="200"))

# Building interior lights — one per floor centred
_bcy = (BLDG_Y1 + BLDG_Y2) // 2  # -528
for _f in range(BLDG_FLOORS):
    _lz = BLDG_GROUND_Z + _f * FLOOR_H + FLOOR_H // 2
    E.append(ent("light", origin=f"{BLDG_CX + 80}  {_bcy} {_lz}", light="280"))
    E.append(ent("light", origin=f"{BLDG_CX - 80} {_bcy} {_lz}", light="280"))

# Building window glow (exterior, east + west faces)
for _f in range(BLDG_FLOORS):
    _lz = BLDG_GROUND_Z + _f * FLOOR_H + 56
    for _wy in [BLDG_Y1 + 80 + _i * 192 + 16 for _i in range(3)]:
        E.append(ent("light", origin=f"{BLDG_X2 + 10} {_wy} {_lz}", light="120"))
        E.append(ent("light", origin=f"{BLDG_X1 - 10} {_wy} {_lz}", light="120"))

# Walkway light — above the flat walkway
_wk_mid_y = (BRY1 + BLDG_Y2) // 2  # = -192
E.append(
    ent("light", origin=f"{BLDG_CX} {_wk_mid_y} {int(WALK_ZT1 + 60)}", light="260")
)

# West campus ambient + east campus ambient
for _xx in [-1000, 1000]:
    E.append(ent("light", origin=f"{_xx} 0 200", light="300"))

# Teleport arch lights — both ends
E.append(
    ent("light", origin=f"{WORLD_X1 + WALL_T + 64} 0 {int(DZ2 + 100)}", light="250")
)
E.append(
    ent("light", origin=f"{WORLD_X2 - WALL_T - 64} 0 {int(DZ2 + 100)}", light="250")
)

# Bridge end arch lights — illuminate the stone arch faces
for ex in [BRX1 + 20, BRX2 - 20]:
    E.append(ent("light", origin=f"{ex} 0 90", light="300"))

# Under-bridge road lights
E.append(
    ent("light", origin=f"0 0 {PANEL_Z - 10}", light="520", style="1")
)  # glow panel light
for rx in [-280, 280]:
    E.append(ent("light", origin=f"{rx} 0 64", light="160"))

# ── Write ─────────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(E) + "\n"
with open("loyola.map", "w") as fh:
    fh.write(map_text)
print(f"loyola.map written — {len(B)} worldspawn brushes, {len(E)} entities")
