#!/usr/bin/env python3
"""Generate loyola.map — Loyola bridge + Knott Hall Quake 1 deathmatch map.

Layout:
  - Rectangular open world (±1024 E-W × ±960 N-S), open sky
  - Road runs N-S under the bridge (like Charles Street at Loyola Maryland)
  - Bridge spans E-W at deck height ~144; arched stone pillars over the road
  - Knott Hall on south campus (X=1186 to 1686, Y=-800 to -256, 4 floors)
    North face faces bridge; ground-level entrance at X=1372..1500
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
T_STONE = "sfloor3_2"  # general bridge structure (cement/stone look)
T_PILLAR = "city2_7"  # supporting pillars (concrete, matches Knott Hall)
T_FLOOR = "sfloor3_2"  # deck top surface
T_CEMENT = "sfloor3_2"  # parapet / bridge walls
T_ROAD = "wgrnd1_5"  # road surface
T_WALL = "city2_7"  # Knott Hall walls — city-style concrete wall
T_FLOOR_BLDG = "sfloor3_2"  # Knott Hall floors and ceilings
T_METAL = "city2_7"  # elevator doors (matches walls)
T_ROCK = "rock1_2"  # cave outer shell
T_SKY = "sky1"  # open sky ceiling
T_LAVA = "*lava1"  # torch flame
T_LIGHT_PANEL = "sfloor4_4"  # light panel
T_TELEPORT = "*teleport"  # teleport effect
T_BRICK = "bricka2_1"  # brick retaining wall (abutment pier west face)

# ── Bridge spine ──────────────────────────────────────────────────────────────
# Blueprint: 1050-unit arched span (69.5 ft), 750-unit flat approaches (49 ft 1 in)
# Scale: 1 ft ≈ 15.1 units  (derived from 1050 units = 69.5 ft)
BRY1, BRY2 = -136, 136  # N-S width = 272 units ≈ 18 ft
DZ1, DZ2 = (
    208,
    224,
)  # flat deck bottom / top — raised for realistic road clearance (~14 ft)

# ── Arch profile ──────────────────────────────────────────────────────────────
# BRX1/BRX2 set after world/building bounds are known (arch spans full world width)
ARCH_RISE = 96  # centre rise — modest crown over flat approaches
ARCH_SEGS = 32  # segments approximating the wider curve


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
PAR_H = 32  # parapet wall height above deck — low enough to jump onto
PAR_W = ft(2, 6)  # parapet wall N-S width = 2 ft 6 in = 38 units
PIL_EXTRA = 64  # extra pillar post height above parapet (gameplay)
PIL_CAP_H = 12  # cap slab height
PIL_PYR_H = 20  # pyramid cap height — visible triangular cement top
PIL_PYR_W = 45  # pyramid base half-width — slightly wider than pillar (P_HW=37)
P_HW = ft(2, 5.5)  # pillar post half-width = half of 4 ft 11 in = 37 units
P_CE = 17  # cap overhang each side = (7 ft 2 in - 4 ft 11 in) / 2
PIL_OVERHANG = 16  # how far above-deck pillar tops extend beyond bridge N/S edges

# ── Pillar X positions — 2 pillars at the start of the curve + 1 east of Knott Hall
# Bridge support visibility: False = none, set of X positions = those piers only, True = all
SHOW_SUPPORTS = True

# ── World layout ──────────────────────────────────────────────────────────────
WALL_T = 16
FZ1, FZ2 = -16, 0
ROAD_X1, ROAD_X2 = -256, 256  # road channel E-W bounds (under bridge)
# Flat approach = 49 ft 1 in = 741 units per side of the 1050-unit arched span
BLDG_WIDTH = 640
WORLD_X1 = -1983  # west wall; BRX1 = WORLD_X1+WALL_T = -1967, giving western span
# of 721 units (= PXS[2]→PXS[3] eastern span) so block spacing matches
WORLD_X2 = 525 + 741 + BLDG_WIDTH + 32  # east world edge, tight around building
WORLD_Y1, WORLD_Y2 = -2048, 960  # full world N-S extent (expanded south for Knott Hall)

# ── Knott Hall (south campus tower) ──────────────────────────────────────────
# Flush against the east world wall
BLDG_X2 = WORLD_X2 - WALL_T - 16  # 16 units clearance from east sky wall
BLDG_X1 = BLDG_X2 - BLDG_WIDTH
BLDG_CX = (BLDG_X1 + BLDG_X2) // 2
# Arch spans from west world wall all the way to just west of Knott Hall pillar
BRX1 = WORLD_X1 + WALL_T  # west arch terminus at world edge
BRX2 = BLDG_X1 - 20  # east arch terminus at Knott Hall pillar
SEG_W = (BRX2 - BRX1) / ARCH_SEGS  # segment width for full-span arch
PXS = [
    -1246,  # west abutment pier (top of embankment hill)
    -525,
    525,
    BLDG_X1 - 20,
]  # pillar X positions
BLDG_Y1, BLDG_Y2 = -1888, -256  # south of bridge south edge (3× north-south depth)
BLDG_WALL = 16  # wall thickness
FLOOR_H = 128  # floor-to-floor height
BLDG_FLOORS = 5  # number of floors
# Knott Hall is in flat approach: deck = DZ2 = 144; 2nd floor aligns automatically
BLDG_GROUND_Z = max(FZ2, DZ2 - FLOOR_H - BLDG_WALL)  # = 0 (no hill needed)
BLDG_Z2 = BLDG_GROUND_Z + BLDG_FLOORS * FLOOR_H

# Sky ceiling must clear Knott Hall
WORLD_Z2 = max(640, BLDG_Z2 + 128)

# ── Walkway from bridge to Knott Hall 2nd floor ──────────────────────────────
# Flat span at DZ2=144 (flat approach section); centered on hall entrance
WALK_X1 = BLDG_CX - 64  # = 536
WALK_X2 = BLDG_CX + 64  # = 664
WALK_ZT1 = int(dtop(BLDG_CX))  # = DZ2 = 144 (flat approach, no arch rise)
WALK_ZT2 = BLDG_GROUND_Z + FLOOR_H + BLDG_WALL  # = 144 = WALK_ZT1 (flat)
# No ramp needed: BLDG_GROUND_Z = 0 = road level

# ── Arch segments ─────────────────────────────────────────────────────────────
A_SEGS = 32


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


def arch_wall(
    x1,
    x2,
    y1,
    y2,
    floor_z,
    ceil_z,
    rin,
    rout,
    segs,
    tex,
    stilt_h=None,
    overhang=0,
    base_h=0,
):
    """Stone wall with arched opening centred at Y=0.

    stilt_h: height of straight sides before the arch springs (defaults to rin,
             giving a plain semicircle; set > rin for a tall stilted/gothic arch).
    overhang: extra Y extent on the rectangular pillar portions beyond ±rout.
    base_h: solid stone plinth height at ground level — arch opening starts above this.
    """
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h  # Z where arch springs
    seg = 180.0 / segs
    brushes = []
    # Solid rock on either side of the arch (makes pier a solid mass, not freestanding)
    if y1 < -(rout + overhang):
        brushes.append(box(x1, y1, floor_z, x2, -(rout + overhang), ceil_z, tex))
    if y2 > (rout + overhang):
        brushes.append(box(x1, rout + overhang, floor_z, x2, y2, ceil_z, tex))
    brushes.append(
        box(x1, -(rout + overhang), floor_z, x2, -rin, ceil_z, tex)
    )  # south pillar, full height (extended by overhang)
    brushes.append(
        box(x1, rin, floor_z, x2, rout + overhang, ceil_z, tex)
    )  # north pillar, full height (extended by overhang)
    # Cap above arch crown: fills above the inner arc top
    brushes.append(box(x1, -rin, sprz + rin, x2, rin, ceil_z, tex))
    # Stone plinth at base — closes arch opening at ground level
    if base_h > 0:
        brushes.append(box(x1, -rin, floor_z, x2, rin, floor_z + base_h, tex))

    # Fill corner gaps where the arch ring (radius rout) doesn't reach the
    # rectangular junction of the pillars (at |y|=rin) and cap (at z=sprz+rin).
    if rout < rin * 1.41421356:
        h_side = math.sqrt(max(0, rout**2 - rin**2))
        # South-top corner
        brushes.append(box(x1, -rin, sprz + h_side, x2, -h_side, sprz + rin, tex))
        # North-top corner
        brushes.append(box(x1, h_side, sprz + h_side, x2, rin, sprz + rin, tex))

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
    box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X1 + WALL_T, WORLD_Y2, WORLD_Z2, T_SKY)
)  # W wall (sky-textured for open look)
B.append(
    box(WORLD_X2 - WALL_T, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y2, WORLD_Z2, T_SKY)
)  # E wall (sky-textured for open look)
B.append(
    box(WORLD_X1, WORLD_Y2 - WALL_T, FZ1, WORLD_X2, WORLD_Y2, WORLD_Z2, T_SKY)
)  # N wall (sky-textured for open look)
B.append(
    box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y1 + WALL_T, WORLD_Z2, T_SKY)
)  # S wall (sky-textured for open look)
B.append(
    box(WORLD_X1, WORLD_Y1, WORLD_Z2 - WALL_T, WORLD_X2, WORLD_Y2, WORLD_Z2, T_SKY)
)  # sky

# ════════════════════════════════════════════════════════════════════════════════
# CHARLES STREET — road surface, sidewalks, centre stripe
# Road runs N-S (full Y); road channel E-W = ROAD_X1..ROAD_X2
# ════════════════════════════════════════════════════════════════════════════════
_ROAD_Y1 = WORLD_Y1 + WALL_T
_ROAD_Y2 = WORLD_Y2 - WALL_T
_WALK_W = 80  # sidewalk width (E-W)
_WALK_H = 8  # sidewalk + curb height above road
_STRIPE_W = 6  # centre-line stripe half-width

# Road surface (2-unit overlay so it textures differently from surrounding ground)
B.append(box(ROAD_X1, _ROAD_Y1, FZ2, ROAD_X2, _ROAD_Y2, FZ2 + 2, T_ROAD))
# West sidewalk
B.append(
    box(ROAD_X1 - _WALK_W, _ROAD_Y1, FZ2, ROAD_X1, _ROAD_Y2, FZ2 + _WALK_H, T_CEMENT)
)
# East sidewalk
B.append(
    box(ROAD_X2, _ROAD_Y1, FZ2, ROAD_X2 + _WALK_W, _ROAD_Y2, FZ2 + _WALK_H, T_CEMENT)
)

# West embankment — rises from just west of the -525 pier to bridge deck height at BRX1.
# Starts at X=-560 (clear of the -525 pier base) so arch stone is not buried there.
_EMB_X2 = -1146  # starts just east of abutment pier, keeping stone base visible
B.append(
    ramp_slab(
        BRX1,
        _EMB_X2,
        _ROAD_Y1,
        _ROAD_Y2,
        FZ1,
        FZ1,
        DZ2,
        FZ2,
        T_ROCK,
        tt=T_ROCK,
    )
)

# Wall extending north from the abutment pier, deck height, city2_1 texture
# Door opening ~160 units north of the pier (visible in bridge10)
_ABUTMENT_X = min(PXS)  # = -1100
_NORTH_WALL_Y1 = BRY2 + PIL_OVERHANG  # north face of pier = 152
_SOUTH_WALL_Y2 = -(BRY2 + PIL_OVERHANG)  # south face of pier = -152
_DOOR_W = 80  # door opening width (~5 ft)
_DOOR_OFF = 160  # distance from pier face to door centre
_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)
# ── Abutment building dimensions (non-enterable brick buildings at N/S wall ends) ─
_AB_FLOORS = 3
_AB_H = _AB_FLOORS * FLOOR_H  # 384 units tall
_AB_D = 300  # building N-S depth
_AB_X2 = _ABUTMENT_X + P_HW + 32  # east face of building  = -1031
_AB_X1 = _AB_X2 - 288  # west face of building  = -1319
_NB_Y2 = WORLD_Y2 - WALL_T  # north building north face = 944
_NB_Y1 = _NB_Y2 - _AB_D  # north building south face = 644
_SB_Y1 = WORLD_Y1 + WALL_T  # south building south face = -2032
_SB_Y2 = _SB_Y1 + _AB_D  # south building north face = -1732
# North wall — two segments with door gap
B.append(
    box(
        _ABUTMENT_X - P_HW,
        _NORTH_WALL_Y1,
        FZ2,
        _ABUTMENT_X + P_HW,
        _NORTH_WALL_Y1 + _DOOR_OFF - _DOOR_W // 2,
        DZ2,
        "city2_1",
    )
)
B.append(
    box(
        _ABUTMENT_X - P_HW,
        _NORTH_WALL_Y1 + _DOOR_OFF + _DOOR_W // 2,
        FZ2,
        _ABUTMENT_X + P_HW,
        _NB_Y1,
        DZ2,
        "city2_1",
    )
)
# North door lintel (top of opening)
B.append(
    box(
        _ABUTMENT_X - P_HW,
        _NORTH_WALL_Y1 + _DOOR_OFF - _DOOR_W // 2,
        FZ2 + _DOOR_H,
        _ABUTMENT_X + P_HW,
        _NORTH_WALL_Y1 + _DOOR_OFF + _DOOR_W // 2,
        DZ2,
        "city2_1",
    )
)
# South wall — two segments with door gap
B.append(
    box(
        _ABUTMENT_X - P_HW,
        _SOUTH_WALL_Y2 - _DOOR_OFF + _DOOR_W // 2,
        FZ2,
        _ABUTMENT_X + P_HW,
        _SOUTH_WALL_Y2,
        DZ2,
        "city2_1",
    )
)
B.append(
    box(
        _ABUTMENT_X - P_HW,
        _SB_Y2,
        FZ2,
        _ABUTMENT_X + P_HW,
        _SOUTH_WALL_Y2 - _DOOR_OFF - _DOOR_W // 2,
        DZ2,
        "city2_1",
    )
)
# South door lintel
B.append(
    box(
        _ABUTMENT_X - P_HW,
        _SOUTH_WALL_Y2 - _DOOR_OFF - _DOOR_W // 2,
        FZ2 + _DOOR_H,
        _ABUTMENT_X + P_HW,
        _SOUTH_WALL_Y2 - _DOOR_OFF + _DOOR_W // 2,
        DZ2,
        "city2_1",
    )
)

# ════════════════════════════════════════════════════════════════════════════════
# ABUTMENT BUILDINGS — non-enterable 3-floor brick buildings at N/S wall ends
# ════════════════════════════════════════════════════════════════════════════════


def _win_row(n, lo, hi):
    """Evenly-spaced window centre positions."""
    step = (hi - lo) / n
    return [lo + step * (i + 0.5) for i in range(n)]


_WIN_W, _WIN_H, _WIN_T = 20, 28, 3  # window half-width, half-height, trim depth


def _abutment_bldg_windows(bx1, bx2, by1, by2, bz1, floors, skip_n=False, skip_s=False):
    """Protruding T_CEMENT window-trim panels on the visible faces of a solid brick box."""
    brushes = []
    nx = max(2, (bx2 - bx1) // 80)  # windows per floor along X
    ny = max(1, (by2 - by1) // 80)  # windows per floor along Y
    for fl in range(floors):
        wz = bz1 + fl * FLOOR_H + FLOOR_H // 2
        if not skip_s:  # south face — protrude outward in -Y
            for wx in _win_row(nx, bx1 + 40, bx2 - 40):
                brushes.append(
                    box(
                        wx - _WIN_W,
                        by1 - _WIN_T,
                        wz - _WIN_H,
                        wx + _WIN_W,
                        by1,
                        wz + _WIN_H,
                        T_CEMENT,
                    )
                )
        if not skip_n:  # north face — protrude outward in +Y
            for wx in _win_row(nx, bx1 + 40, bx2 - 40):
                brushes.append(
                    box(
                        wx - _WIN_W,
                        by2,
                        wz - _WIN_H,
                        wx + _WIN_W,
                        by2 + _WIN_T,
                        wz + _WIN_H,
                        T_CEMENT,
                    )
                )
        for wy in _win_row(ny, by1 + 40, by2 - 40):  # east face — protrude in +X
            brushes.append(
                box(
                    bx2,
                    wy - _WIN_W,
                    wz - _WIN_H,
                    bx2 + _WIN_T,
                    wy + _WIN_W,
                    wz + _WIN_H,
                    T_CEMENT,
                )
            )
        for wy in _win_row(ny, by1 + 40, by2 - 40):  # west face — protrude in -X
            brushes.append(
                box(
                    bx1 - _WIN_T,
                    wy - _WIN_W,
                    wz - _WIN_H,
                    bx1,
                    wy + _WIN_W,
                    wz + _WIN_H,
                    T_CEMENT,
                )
            )
    return brushes


# North building: south face at Y=644, north face flush with world wall at Y=944
B.append(box(_AB_X1, _NB_Y1, FZ2, _AB_X2, _NB_Y2, FZ2 + _AB_H, "city2_1"))
B.extend(
    _abutment_bldg_windows(_AB_X1, _AB_X2, _NB_Y1, _NB_Y2, FZ2, _AB_FLOORS, skip_n=True)
)

# South building: north face at Y=-1732, south face flush with world wall at Y=-2032
B.append(box(_AB_X1, _SB_Y1, FZ2, _AB_X2, _SB_Y2, FZ2 + _AB_H, "city2_1"))
B.extend(
    _abutment_bldg_windows(_AB_X1, _AB_X2, _SB_Y1, _SB_Y2, FZ2, _AB_FLOORS, skip_s=True)
)


# ════════════════════════════════════════════════════════════════════════════════
# West flat approach removed — arch now starts at world edge
# East flat stub from arch terminus to building entrance
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

# ── Parapet walls — west flat approach removed; east flat stub only ───────────
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

# ── Parapet cement blocks (decorative posts atop parapet walls) ───────────────
_BLK_HW = 24  # block half-width in X (48 units wide along bridge)
_BLK_H = 36  # block height above parapet top
_BLK_OVH = 6  # how far blocks protrude outward past bridge N/S edge
_PIR_M = P_HW + _BLK_HW + 4  # clearance from pier centre to block centre


def _add_parapet_blocks(
    x_start, x_end, n, west_margin=None, east_margin=None, n_south=None
):
    """Add evenly-spaced cement blocks atop N and S parapets in a bridge span.

    n_south defaults to n.  South blocks that overlap the walkway gap
    (WALK_X1..WALK_X2) are skipped automatically.
    """
    n_s = n if n_south is None else n_south
    mx0 = west_margin if west_margin is not None else _PIR_M
    mx1 = east_margin if east_margin is not None else _PIR_M
    x0 = x_start + mx0
    x1 = x_end - mx1
    for k in range(n):
        cx = x0 + (x1 - x0) * (k + 1) / (n + 1)
        # Use minimum parapet top across block width so block never floats above parapet
        bz = min(dtop(cx - _BLK_HW), dtop(cx), dtop(cx + _BLK_HW)) + PAR_H
        B.append(
            box(
                cx - _BLK_HW,
                BRY2 - PAR_W,
                bz,
                cx + _BLK_HW,
                BRY2 + _BLK_OVH,
                bz + _BLK_H,
                T_CEMENT,
            )
        )
    for k in range(n_s):
        cx = x0 + (x1 - x0) * (k + 1) / (n_s + 1)
        bz = min(dtop(cx - _BLK_HW), dtop(cx), dtop(cx + _BLK_HW)) + PAR_H
        if not (cx - _BLK_HW < WALK_X2 and cx + _BLK_HW > WALK_X1):
            B.append(
                box(
                    cx - _BLK_HW,
                    BRY1 - _BLK_OVH,
                    bz,
                    cx + _BLK_HW,
                    BRY1 + PAR_W,
                    bz + _BLK_H,
                    T_CEMENT,
                )
            )


# Western span (BRX1 → PXS[0]): no blocks — open span
# Span 2 (PXS[0] → PXS[1]): eastern span 1, 3 blocks
_add_parapet_blocks(PXS[0], PXS[1], 3)
# Middle span (PXS[1] → PXS[2]): 4 blocks
_add_parapet_blocks(PXS[1], PXS[2], 4)
# Eastern span 2 (PXS[2] → PXS[3]): 3 blocks
_add_parapet_blocks(PXS[2], PXS[3], 3)
# East flat span in front of Knott Hall: 3 north, 2 south (south has walkway gap)
_add_parapet_blocks(
    BRX2,
    WORLD_X2 - WALL_T,
    3,
    west_margin=_BLK_HW + 8,
    east_margin=32 + _BLK_HW + 8,
    n_south=2,
)


# ── Parapet handrail tubes (two 4×4 rods stacked, through parapet blocks/pillars) ─
_TUBE_HW = 2  # half-width of tube in Y and Z (4 units total)
_TUBE_RISE = 10  # raise tubes above parapet top
_TUBE_GAP = 12  # vertical gap between tube centres
_TUBE_NY1 = BRY2 - PAR_W // 2 - _TUBE_HW
_TUBE_NY2 = _TUBE_NY1 + _TUBE_HW * 2
_TUBE_SY1 = BRY1 + PAR_W // 2 - _TUBE_HW
_TUBE_SY2 = _TUBE_SY1 + _TUBE_HW * 2

for _tube_z_extra in [_TUBE_RISE, _TUBE_RISE + _TUBE_GAP]:
    for _i in range(ARCH_SEGS):
        _sx1 = BRX1 + _i * SEG_W
        _sx2 = _sx1 + SEG_W
        _zb1 = dtop(_sx1) + PAR_H + _tube_z_extra
        _zb2 = dtop(_sx2) + PAR_H + _tube_z_extra
        B.append(
            ramp_slab(
                _sx1,
                _sx2,
                _TUBE_NY1,
                _TUBE_NY2,
                _zb1,
                _zb2,
                _zb1 + _TUBE_HW * 2,
                _zb2 + _TUBE_HW * 2,
                T_PILLAR,
            )
        )
        if not (_sx1 < WALK_X2 and _sx2 > WALK_X1):
            B.append(
                ramp_slab(
                    _sx1,
                    _sx2,
                    _TUBE_SY1,
                    _TUBE_SY2,
                    _zb1,
                    _zb2,
                    _zb1 + _TUBE_HW * 2,
                    _zb2 + _TUBE_HW * 2,
                    T_PILLAR,
                )
            )
    # East flat section
    _tbz = DZ2 + PAR_H + _tube_z_extra
    _x_east_end = WORLD_X2 - WALL_T
    B.append(
        box(
            BRX2, _TUBE_NY1, _tbz, _x_east_end, _TUBE_NY2, _tbz + _TUBE_HW * 2, T_PILLAR
        )
    )
    B.append(
        box(BRX2, _TUBE_SY1, _tbz, WALK_X1, _TUBE_SY2, _tbz + _TUBE_HW * 2, T_PILLAR)
    )
    B.append(
        box(
            WALK_X2,
            _TUBE_SY1,
            _tbz,
            _x_east_end,
            _TUBE_SY2,
            _tbz + _TUBE_HW * 2,
            T_PILLAR,
        )
    )


# ── Pillar posts (stone piers with arches) ───────────────────────────────────
# Each pillar position now features a narrow arched pier supporting the deck.
# Arch openings span most of the bridge N-S width (BRY2=136, bridge=272 units)
# rin = half-width of clear opening; rout = outer radius of arch ring
_OUTER_R = (117, 80)  # narrower outer piers flanking road
_INNER_R = (131, 90)  # slightly wider inner piers
_CENTR_R = (128, 100)  # widest opening at centre
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

        # Width of the pier in X (matches pillar post width)
        x1, x2 = px - P_HW, px + P_HW

        # Arch opening varies by pillar type (outer / inner / centre)
        if px == 0:
            a_rout, a_rin = _CENTR_R
        elif abs(px) == max(abs(p) for p in PXS):
            a_rout, a_rin = _OUTER_R
        else:
            a_rout, a_rin = _INNER_R
        a_stilt = int(pdeck) - a_rout - FZ2 - 16
        if a_stilt < 0:
            # Arch would overshoot the bridge bottom; cap rout so the crown
            # lands exactly at ceil_z (bridge deck underside).
            a_rout = int(pdeck) - FZ2 - 16
            a_stilt = 0

        # Compute arch body overhang so the pier always extends PIL_OVERHANG units
        # past the bridge edges, regardless of a_rout (outer piers have small rout).
        _arch_overhang = max(PIL_OVERHANG, BRY2 + PIL_OVERHANG - a_rout)

        # Add the arched pier structure (overhang extends pillar boxes past bridge)
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
                T_PILLAR,
                stilt_h=a_stilt,
                overhang=_arch_overhang,
                base_h=32,
            )
        )

        # Pillar tops (above deck, extend PIL_OVERHANG past bridge edges and inward)
        _pil_out = BRY2 + PIL_OVERHANG  # always overhang past bridge edge
        # North pillar top
        B.append(
            box(
                px - P_HW,
                BRY2 - PAR_W - PIL_OVERHANG,
                pdeck,
                px + P_HW,
                _pil_out,
                ppil,
                T_PILLAR,
            )
        )

        # South pillar top
        B.append(
            box(
                px - P_HW,
                -_pil_out,
                pdeck,
                px + P_HW,
                BRY1 + PAR_W + PIL_OVERHANG,
                ppil,
                T_PILLAR,
            )
        )

        # Fill gap between pier top and deck surface in the overhang zone
        pier_top_z = int(pdeck) - 16
        B.append(box(x1, BRY2, pier_top_z, x2, _pil_out, pdeck, T_PILLAR))  # north
        B.append(box(x1, -_pil_out, pier_top_z, x2, BRY1, pdeck, T_PILLAR))  # south

        # Cement cap slab + pyramid on top of each stone pillar post
        _cap_x1, _cap_x2 = px - PIL_PYR_W, px + PIL_PYR_W
        _n_cy1 = BRY2 - PAR_W - PIL_OVERHANG
        _n_cy2 = BRY2 + PIL_OVERHANG
        _s_cy1 = BRY1 - PIL_OVERHANG
        _s_cy2 = BRY1 + PAR_W + PIL_OVERHANG
        # Cap slabs (flat cement base)
        B.append(box(_cap_x1, _n_cy1, ppil, _cap_x2, _n_cy2, pcap, T_CEMENT))
        B.append(box(_cap_x1, _s_cy1, ppil, _cap_x2, _s_cy2, pcap, T_CEMENT))
        # Pyramids on top of cap slabs
        B.append(
            pyramid(_cap_x1, _n_cy1, pcap, _cap_x2, _n_cy2, pcap + PIL_PYR_H, T_CEMENT)
        )
        B.append(
            pyramid(_cap_x1, _s_cy1, pcap, _cap_x2, _s_cy2, pcap + PIL_PYR_H, T_CEMENT)
        )

        # Abutment pier (westernmost): solid cement fill + arch teleport on west face
        if px == min(PXS):
            # Cement fill starts 16 units east of pier face to make room for arch
            B.append(box(x1 + 16, -a_rin, FZ2, x2, a_rin, int(pdeck) - 16, T_CEMENT))
            # Arch-shaped teleport flush with the west face (recessed into pier)
            _tele_stilt = pier_top_z - FZ2 - a_rin - 8
            _abutment_tele_brush = arch_fill(
                x1 + 2,
                x1 + 18,
                0.0,
                FZ2,
                a_rin,
                A_SEGS,
                T_TELEPORT,
                stilt_h=_tele_stilt,
            )
            _abutment_tele_dest_z = int(pdeck) + 40  # spawn height above deck

# ── Teleport Arches at both ends of bridge ───────────────────────────────────
T_ARCH_RIN = 96
T_ARCH_ROUT = 136  # Fills the bridge width (updated to match BRY2=136)
T_ARCH_STILT = 96  # Height of straight sides before arch springs
T_ARCH_W = 32  # Thickness of the arch in X

for _ex in [WORLD_X1 + WALL_T, WORLD_X2 - WALL_T - T_ARCH_W]:
    _xb, _xf = _ex, _ex + T_ARCH_W
    _sprz = DZ2 + T_ARCH_STILT  # Z where arch curve begins
    _post_w = T_ARCH_ROUT - T_ARCH_RIN  # post thickness in Y
    # South post (extends to ground floor, with overhang)
    B.append(box(_xb, BRY1 - PIL_OVERHANG, FZ2, _xf, BRY1 + _post_w, _sprz, T_PILLAR))
    # North post (extends to ground floor, with overhang)
    B.append(box(_xb, BRY2 - _post_w, FZ2, _xf, BRY2 + PIL_OVERHANG, _sprz, T_PILLAR))
    # Arch ring segments (rounded top, with overhang)
    _seg = 180.0 / A_SEGS
    for i in range(A_SEGS):
        B.append(
            arch_seg(
                _xb,
                _xf,
                0.0,
                float(_sprz),
                T_ARCH_RIN,
                T_ARCH_ROUT + PIL_OVERHANG,
                i * _seg,
                (i + 1) * _seg,
                T_PILLAR,
            )
        )

# ── Attached glow panel beneath arch centre ─────────────────────────────────
# Attached to bridge bottom (dbot(0) = 192). Size reduced to 1/4 (48x48).
PANEL_Z = int(dbot(0)) - 4
B.append(box(-24, -24, PANEL_Z, 24, 24, PANEL_Z + 4, T_LIGHT_PANEL))

# ── Under-bridge light panels along flat approaches ──────────────────────────
_UNDER_PANEL_Z = DZ1 - 4  # just below flat deck bottom
# West flat approach removed — no under-bridge panels on west side
for rx in range(BRX2 + 200, WORLD_X2 - 100, 200):
    B.append(
        box(
            rx - 24, -24, _UNDER_PANEL_Z, rx + 24, 24, _UNDER_PANEL_Z + 4, T_LIGHT_PANEL
        )
    )

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
    # Skip south panel if it's in the walkway gap
    if not (WALK_X1 - 8 <= px <= WALK_X2 + 8):
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
# KNOTT HALL — south campus, 4-floor playable tower
# Footprint: X=1186 to 1686, Y=-800 to -256, Z=0 to 512
# North face faces the bridge; ground-level entrance at X=1372..1500
# Lift shaft at center-north rises from ground to rooftop
# ════════════════════════════════════════════════════════════════════════════════

# ── Hill terrain under Knott Hall ─────────────────────────────────────────────
# Bridge deck is raised; building sits on a hill so its 2nd floor meets the walkway.
if BLDG_GROUND_Z > FZ2:
    # Solid hill fill under the entire building footprint
    B.append(box(BLDG_X1, BLDG_Y1, FZ2, BLDG_X2, BLDG_Y2, BLDG_GROUND_Z, T_ROCK))
    # Sloped ramp on the north face — player can walk up from road to building entrance
    _ramp_y1 = BLDG_Y2  # north face of building
    _ramp_y2 = min(BLDG_Y2 + BLDG_GROUND_Z * 2, BRY1 - 16)  # ramp extent north
    B.append(
        ramp_slab_y(
            BLDG_X1,
            BLDG_X2,
            _ramp_y1,
            _ramp_y2,
            FZ2,
            FZ2,
            BLDG_GROUND_Z,
            FZ2,
            T_ROCK,
            tt=T_ROAD,
        )
    )
_bix1 = BLDG_X1 + BLDG_WALL  # interior west
_bix2 = BLDG_X2 - BLDG_WALL  # interior east
_biy1 = BLDG_Y1 + BLDG_WALL  # interior south = -784
_biy2 = BLDG_Y2 - BLDG_WALL  # interior north = -272

# Entrance doorway — centred on building (BLDG_CX ± 64)
_ENT_X1, _ENT_X2 = BLDG_CX - 64, BLDG_CX + 64  # = 1372, 1500

# Lift shaft east of entrance: 16 units east of _ENT_X2, 128 wide
_stx1, _stx2 = _ENT_X2 + 16, _ENT_X2 + 16 + 128  # = 1516, 1644
_sty1, _sty2 = _biy2 - 128, _biy2  # Y: -400 to -272

# ── Outer walls ──────────────────────────────────────────────────────────────

# South wall — solid back wall
B.append(
    box(BLDG_X1, BLDG_Y1, BLDG_GROUND_Z, BLDG_X2, BLDG_Y1 + BLDG_WALL, BLDG_Z2, T_WALL)
)

# North-West Indentation (Corner Notch)
INDENT = 80
# North wall — faces bridge; ground entrance + 2nd-floor walkway opening
_door_n = [
    (_ENT_X1, BLDG_GROUND_Z, _ENT_X2, BLDG_GROUND_Z + FLOOR_H)
]  # ground entrance
_door_2 = [
    (_ENT_X1, WALK_ZT2, _ENT_X2, BLDG_GROUND_Z + FLOOR_H * 2)
]  # walkway entrance
B.extend(
    layered_wall(
        BLDG_X1 + INDENT,
        BLDG_Y2 - BLDG_WALL,
        BLDG_GROUND_Z,
        BLDG_X2 - INDENT,
        BLDG_Y2,
        BLDG_Z2,
        _door_n + _door_2,
        T_WALL,
    )
)

# NW Indentation inner walls
B.append(
    box(
        BLDG_X1,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X1 + INDENT,
        BLDG_Y2 - INDENT + BLDG_WALL,
        BLDG_Z2,
        T_WALL,
    )
)
B.append(
    box(
        BLDG_X1 + INDENT - BLDG_WALL,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X1 + INDENT,
        BLDG_Y2,
        BLDG_Z2,
        T_WALL,
    )
)

# NE Indentation inner walls (mirror of NW)
B.append(
    box(
        BLDG_X2 - INDENT,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X2,
        BLDG_Y2 - INDENT + BLDG_WALL,
        BLDG_Z2,
        T_WALL,
    )
)
B.append(
    box(
        BLDG_X2 - INDENT,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X2 - INDENT + BLDG_WALL,
        BLDG_Y2,
        BLDG_Z2,
        T_WALL,
    )
)

# ── Brutalist Fins (All Exposed Facades) — currently disabled ─────────────────

# East and West walls — solid, stopping short of NE/NW cutouts
B.append(
    box(
        BLDG_X2 - BLDG_WALL,
        BLDG_Y1,
        BLDG_GROUND_Z,
        BLDG_X2,
        BLDG_Y2 - INDENT,
        BLDG_Z2,
        T_WALL,
    )
)
B.append(
    box(
        BLDG_X1,
        BLDG_Y1,
        BLDG_GROUND_Z,
        BLDG_X1 + BLDG_WALL,
        BLDG_Y2 - INDENT,
        BLDG_Z2,
        T_WALL,
    )
)

# Roof — open above lift shaft, clipped for NW indentation
B.append(
    box(
        BLDG_X1,
        BLDG_Y1,
        BLDG_Z2,
        _stx1,
        BLDG_Y2 - INDENT,
        BLDG_Z2 + BLDG_WALL,
        T_FLOOR_BLDG,
    )
)  # west bulk
B.append(
    box(
        BLDG_X1 + INDENT,
        BLDG_Y2 - INDENT,
        BLDG_Z2,
        _stx1,
        BLDG_Y2,
        BLDG_Z2 + BLDG_WALL,
        T_FLOOR_BLDG,
    )
)  # west north-strip
B.append(
    box(
        _stx2,
        BLDG_Y1,
        BLDG_Z2,
        BLDG_X2,
        BLDG_Y2 - INDENT,
        BLDG_Z2 + BLDG_WALL,
        T_FLOOR_BLDG,
    )
)  # east bulk
B.append(
    box(
        _stx2,
        BLDG_Y2 - INDENT,
        BLDG_Z2,
        BLDG_X2 - INDENT,
        BLDG_Y2,
        BLDG_Z2 + BLDG_WALL,
        T_FLOOR_BLDG,
    )
)  # east north-strip (NE cutout)
B.append(
    box(_stx1, BLDG_Y1, BLDG_Z2, _stx2, _sty1, BLDG_Z2 + BLDG_WALL, T_FLOOR_BLDG)
)  # south of shaft

# ── Interior floor slabs (floors 0-3, lift shaft opening in center-north) ────
# Floor 0 (ground): full slab with no shaft opening, clipped for NW indentation
_sz0 = BLDG_GROUND_Z
_st0 = _sz0 + BLDG_WALL
B.append(box(_bix1, _biy1, _sz0, _bix2, BLDG_Y2 - INDENT, _st0, T_FLOOR_BLDG))
B.append(
    box(
        _bix1 + INDENT,
        BLDG_Y2 - INDENT,
        _sz0,
        _bix2 - INDENT,
        _biy2,
        _st0,
        T_FLOOR_BLDG,
    )
)

for _f in range(1, BLDG_FLOORS):
    _sz = BLDG_GROUND_Z + _f * FLOOR_H
    _st = _sz + BLDG_WALL
    # South bulk
    B.append(box(_bix1, _biy1, _sz, _bix2, _sty1, _st, T_FLOOR_BLDG))
    # West of shaft, clipped for NW indentation
    B.append(box(_bix1, _sty1, _sz, _stx1, BLDG_Y2 - INDENT, _st, T_FLOOR_BLDG))
    B.append(
        box(_bix1 + INDENT, BLDG_Y2 - INDENT, _sz, _stx1, _biy2, _st, T_FLOOR_BLDG)
    )
    # East of shaft, clipped for NE indentation
    B.append(box(_stx2, _sty1, _sz, _bix2, BLDG_Y2 - INDENT, _st, T_FLOOR_BLDG))
    B.append(
        box(_stx2, BLDG_Y2 - INDENT, _sz, _bix2 - INDENT, _biy2, _st, T_FLOOR_BLDG)
    )

# ── Elevator Shaft Enclosure ──────────────────────────────────────────────
# Walls around the lift shaft (_stx1.._stx2, _sty1.._sty2)
_shaft_wall = 8
# Doorways for each floor (on the West side — immediate left when entering)
_shaft_doors_w = [
    (
        _sty1 + 16,
        BLDG_GROUND_Z + _f * FLOOR_H,
        _sty2 - 16,
        BLDG_GROUND_Z + _f * FLOOR_H + 96,
    )
    for _f in range(BLDG_FLOORS)
]

# Shaft North wall (internal, solid)
B.append(box(_stx1, _sty2, BLDG_GROUND_Z, _stx2, _sty2 + _shaft_wall, BLDG_Z2, T_WALL))
# Shaft South wall (internal, solid)
B.append(box(_stx1, _sty1 - _shaft_wall, BLDG_GROUND_Z, _stx2, _sty1, BLDG_Z2, T_WALL))
# Shaft West wall (internal, with door openings — faces entrance)
B.extend(
    layered_wall_y(
        _sty1,
        _stx1 - _shaft_wall,
        BLDG_GROUND_Z,
        _sty2,
        _stx1,
        BLDG_Z2,
        _shaft_doors_w,
        T_WALL,
    )
)
# Shaft East wall (internal)
B.append(box(_stx2, _sty1, BLDG_GROUND_Z, _stx2 + _shaft_wall, _sty2, BLDG_Z2, T_WALL))

DRAW_FASCIA_TEXT = False  # Set True to re-enable (slow to compile)

# ── "LOYOLA UNIVERSITY MARYLAND" fascia lettering ────────────────────────────
# Fascia panel follows the arch: one box per character hanging from dbot(x)
_FAS_Y1, _FAS_Y2 = BRY1 - 6, BRY1  # 6 units thick, flush with south face
_FAS_Y3, _FAS_Y4 = BRY2, BRY2 + 6  # north face panel
_FAS_X1, _FAS_X2 = -500, 500  # between the two road piers
_PX_W, _PX_H = 4, 4
_FONT_ROWS = 6
_TEXT = "LOYOLA UNIVERSITY MARYLAND"
_CHAR_W = (4 + 1) * _PX_W  # 4 cols + 1 gap
_TOTAL_W = len(_TEXT) * _CHAR_W - _PX_W
_TEXT_X0 = 0 - _TOTAL_W // 2

# Background fascia: per-character strip following arch curve, on south parapet face
for _ci, _ch in enumerate(_TEXT if DRAW_FASCIA_TEXT else []):
    _cx = _TEXT_X0 + _ci * _CHAR_W
    _cx2 = _cx + 4 * _PX_W
    _x_mid = (_cx + _cx2) / 2
    _z_bot = int(dbot(_x_mid))  # deck soffit at this X
    _z_top = int(dtop(_x_mid)) + PAR_H  # parapet top at this X
    if _cx2 > _cx:
        B.append(box(_cx, _FAS_Y1, _z_bot, _cx2, _FAS_Y2, _z_top, T_STONE))
        B.append(box(_cx, _FAS_Y3, _z_bot, _cx2, _FAS_Y4, _z_top, T_STONE))

_FONT = {
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


def _render_text_fascia(text, x0, y_face, px_w, px_h, depth, tex, mirror=False):
    """Render text as pixel-font raised boxes on a fascia face.
    Each character's Z is computed from dtop(x) so letters follow the arch curve.
    mirror=True flips each glyph horizontally (needed for north-facing surface)."""
    cols = 4
    rows = 6
    char_w = (cols + 1) * px_w  # 4 cols + 1 gap

    brushes = []
    for ci, ch in enumerate(text):
        bitmap = _FONT.get(ch, _FONT[" "])
        cx = x0 + ci * char_w
        x_mid = cx + (cols * px_w) / 2
        z_top = int(dtop(x_mid)) + PAR_H  # top of parapet face at this X
        for row_i, row_bits in enumerate(bitmap):
            z = z_top - row_i * px_h
            for col_i in range(cols):
                src_col = (cols - 1 - col_i) if mirror else col_i
                if row_bits & (1 << (cols - 1 - src_col)):
                    px = cx + col_i * px_w
                    brushes.append(
                        box(px, y_face - depth, z - px_h, px + px_w, y_face, z, tex)
                    )
    return brushes


_letter_brushes = (
    (
        _render_text_fascia(
            _TEXT,
            x0=_TEXT_X0,
            y_face=_FAS_Y1,
            px_w=_PX_W,
            px_h=_PX_H,
            depth=4,
            tex=T_LIGHT_PANEL,
        )
        + _render_text_fascia(
            _TEXT[::-1],
            x0=_TEXT_X0,
            y_face=_FAS_Y4 + 4,
            px_w=_PX_W,
            px_h=_PX_H,
            depth=4,
            tex=T_LIGHT_PANEL,
            mirror=True,
        )
    )
    if DRAW_FASCIA_TEXT
    else []
)

# ── Worldspawn ────────────────────────────────────────────────────────────────
worldspawn = (
    "{\n"
    '"classname" "worldspawn"\n'
    '"wad" "quake101.wad"\n'
    '"message" "Loyola Bridge & Knott Hall"\n'
    f'"sky" "{T_SKY}"\n'
    '"ambient" "60"\n'
    '"_sunlight" "220"\n'
    '"_sunlight_color" "255 245 210"\n'
    '"_sunlight_dir" "60 -60"\n'
    '"_sunlight_penumbra" "8"\n'
    '"dmflags" "128"\n' + "\n".join(B) + "\n}"
)

# ── Entities ──────────────────────────────────────────────────────────────────
E = []
# Letter brushes as func_detail — don't split vis BSP tree, keeps compile fast
if _letter_brushes:
    E.append(brush_ent("func_detail", _letter_brushes))
DECK_Z = dtop(0) + 8  # centre of arch deck + a bit (spawn/item height)
ROAD_Z = FZ2 + 8

# Abutment pier teleport — arch opening teleports up to bridge deck above
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_abutment_deck",
        origin=f"{min(PXS)} 0 {_abutment_tele_dest_z}",
        angle="0",
    )
)
E.append(
    brush_ent("trigger_teleport", _abutment_tele_brush, target="dest_abutment_deck")
)
E.append(brush_ent("func_illusionary", _abutment_tele_brush))

# Teleport destinations — west arch ↔ east arch
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_east",
        origin=f"{(_AB_X1 + _AB_X2) // 2} {(_NB_Y1 + _NB_Y2) // 2} {int(FZ2 + _AB_H + 40)}",
        angle="270",  # facing south toward the bridge
    )
)
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_west",
        origin=f"{BLDG_X1 - 200} {BLDG_Y1 + 64} {int(FZ2 + 24)}",
        angle="180",  # facing west, toward Charles Street
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

# West lower trigger (ground floor — simple box between posts)
_wlx1 = WORLD_X1 + WALL_T
_wlx2 = _wlx1 + T_ARCH_W
west_lower = [box(_wlx1, -T_ARCH_RIN, FZ2, _wlx2, T_ARCH_RIN, DZ2, T_TELEPORT)]
E.append(brush_ent("trigger_teleport", west_lower, target="dest_east"))
E.append(brush_ent("func_illusionary", west_lower))

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

# East lower trigger (ground floor — teleports up to bridge deck above)
_elx1 = WORLD_X2 - WALL_T - T_ARCH_W
_elx2 = WORLD_X2 - WALL_T
_east_lower_deck_x = _elx1 - 64  # west of the arch, on the flat deck approach
E.append(
    ent(
        "info_teleport_destination",
        targetname="dest_east_deck",
        origin=f"{_east_lower_deck_x} 0 {int(DZ2 + 40)}",
        angle="180",
    )
)
east_lower = [box(_elx1, -T_ARCH_RIN, FZ2, _elx2, T_ARCH_RIN, DZ2, T_TELEPORT)]
E.append(brush_ent("trigger_teleport", east_lower, target="dest_east_deck"))
E.append(brush_ent("func_illusionary", east_lower))


# ── Elevator Doors (func_door) for each floor ─────────────────────────────
for _f in range(BLDG_FLOORS):
    # Floor surface Z
    _floor_surface_z = BLDG_GROUND_Z + _f * FLOOR_H + BLDG_WALL
    _dz1 = _floor_surface_z
    _dz2 = _dz1 + 80  # slightly shorter door (80 units)
    _tname = f"elevator_door_{_f}"

    # Door leaf — on West face of shaft (facing entrance)
    _d_brush = [box(_stx1 - 2, _sty1 + 16, _dz1, _stx1 + 2, _sty2 - 16, _dz2, T_METAL)]
    E.append(
        brush_ent(
            "func_door", _d_brush, targetname=_tname, angle="-1", speed="300", wait="3"
        )
    )

    # Trigger zone — west of the door (in front of it)
    _tr_brush = [
        box(_stx1 - 48, _sty1 + 8, _dz1, _stx1 - 2, _sty2 - 8, _dz2, "trigger")
    ]
    E.append(brush_ent("trigger_multiple", _tr_brush, target=_tname, wait="1"))

E.append(
    ent(
        "info_player_start",
        origin=f"{BLDG_CX} {BRY1 + PAR_W + 32} {int(DZ2 + 24)}",
        angle="180",
    )
)

_bcy = (BLDG_Y1 + BLDG_Y2) // 2  # Knott Hall center Y = -528

for pos in [
    # Bridge deck
    (0, 0, int(dtop(0) + 32)),
    (-160, 0, int(dtop(-160) + 32)),
    (160, 0, int(dtop(160) + 32)),
    (-320, 0, int(dtop(-320) + 32)),
    (320, 0, int(dtop(320) + 32)),
    # Walkway mid-point
    (BLDG_CX, (BRY1 + BLDG_Y2) // 2, int(WALK_ZT1 + 32)),
    # Knott Hall ground floor (near entrance)
    (BLDG_CX, BLDG_Y2 - 64, BLDG_GROUND_Z + 40),
    # Knott Hall upper floors
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
        pcap = pbase + PAR_H + PIL_EXTRA + PIL_CAP_H + PIL_PYR_H  # top of pyramid
        cy_n = BRY2 - PAR_W // 2  # centred on north pillar cap
        cy_s = BRY1 + PAR_W // 2  # centred on south pillar cap
        E.append(
            ent("light", origin=f"{px} {cy_n} {int(pcap + 20)}", light="300", style="1")
        )
        E.append(
            ent("light", origin=f"{px} {cy_s} {int(pcap + 20)}", light="300", style="1")
        )
        # Flames on pillar tops — raised above pyramid apex so they visually sit on top
        E.append(
            ent("light_flame_large_yellow", origin=f"{px} {cy_n} {int(pcap + 24)}")
        )
        E.append(
            ent("light_flame_large_yellow", origin=f"{px} {cy_s} {int(pcap + 24)}")
        )
        # Damaging trigger at each flame — hurts players who walk into the fire
        for cy in [cy_n, cy_s]:
            _fhb = box(
                px - 16,
                cy - 16,
                int(pcap + 24),
                px + 16,
                cy + 16,
                int(pcap) + 64,
                T_SKY,
            )
            E.append(brush_ent("trigger_hurt", [_fhb], dmg="10"))

# Panel glow
for px in panel_xs:
    pbase = dtop(px)
    ph = int(pbase + PAR_H // 2)
    E.append(ent("light", origin=f"{px} {BRY2 - 30} {ph}", light="180"))
    if not (WALK_X1 - 8 <= px <= WALK_X2 + 8):
        E.append(ent("light", origin=f"{px} {BRY1 + 30} {ph}", light="180"))

# Lift (func_plat) — rides from ground floor up through roof opening to rooftop
_lift_travel = BLDG_Z2 - (BLDG_GROUND_Z + BLDG_WALL)
_lift_brush = [
    box(
        _stx1 + 2,
        _sty1 + 2,
        BLDG_Z2 - 8,
        _stx2 - 2,
        _sty2 - 2,
        BLDG_Z2,
        T_FLOOR_BLDG,
    )
]
E.append(brush_ent("func_plat", _lift_brush, height=str(_lift_travel), speed="200"))

# Knott Hall interior lights — one per floor centred
_bcy = (BLDG_Y1 + BLDG_Y2) // 2  # -528
for _f in range(BLDG_FLOORS):
    _lz = BLDG_GROUND_Z + _f * FLOOR_H + FLOOR_H // 2
    E.append(ent("light", origin=f"{BLDG_CX + 80}  {_bcy} {_lz}", light="280"))
    E.append(ent("light", origin=f"{BLDG_CX - 80} {_bcy} {_lz}", light="280"))

# Knott Hall window glow (exterior, east + west faces)
for _f in range(BLDG_FLOORS):
    _lz = BLDG_GROUND_Z + _f * FLOOR_H + 56
    for _wy in [BLDG_Y1 + 80 + _i * 192 + 16 for _i in range(3)]:
        E.append(ent("light", origin=f"{BLDG_X2 + 10} {_wy} {_lz}", light="120"))
        E.append(ent("light", origin=f"{BLDG_X1 - 10} {_wy} {_lz}", light="120"))

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

# Additional under-bridge lights along flat approaches
for rx in range(WORLD_X1 + 200, BRX1, 200):
    E.append(ent("light", origin=f"{rx} 0 64", light="200"))
for rx in range(BRX2 + 200, WORLD_X2 - 100, 200):
    E.append(ent("light", origin=f"{rx} 0 64", light="200"))

# ── Write ─────────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(E) + "\n"
with open("loyola.map", "w") as fh:
    fh.write(map_text)
print(f"loyola.map written — {len(B)} worldspawn brushes, {len(E)} entities")
