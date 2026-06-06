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
TEX_STONE = "sfloor3_2"  # general bridge structure (cement/stone look)
TEX_PILLAR = "city2_7"  # supporting pillars (concrete, matches Knott Hall)
TEX_FLOOR = "sfloor3_2"  # deck top surface
TEX_CEMENT = "sfloor3_2"  # parapet / bridge walls
TEX_ROAD = "azfloor1_1"  # road surface
TEX_WALL = "city2_7"  # Knott Hall walls — city-style concrete wall
TEX_FLOOR_BLDG = "sfloor3_2"  # Knott Hall floors and ceilings
TEX_METAL = "city2_7"  # elevator doors (matches walls)
TEX_GROUND = "ground1_1"  # ground/terrain surface
TEX_RAIL = "metal5_4"  # bridge and walkway railings
TEX_SKY = "sky1"  # open sky ceiling
TEX_LAVA = "*lava1"  # torch flame
TEX_TELEPORT = "*teleport"  # teleport effect
TEX_BRICK = "bricka2_1"  # brick retaining wall (abutment pier west face)
TEX_WHITE_STONE = "sfloor3_2"  # Ennis Drive entrance pillars
TEX_ROOF = "wgrnd1_5"  # street/road texture for roof

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
    """Z coordinate of the deck surface (top face) at a given X position."""
    return DZ2 + arch_z(x)  # deck surface Z at x


def dbot(x):
    """Z coordinate of the deck underside at a given X position."""
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
WORLD_X2 = (
    525 + 741 + BLDG_WIDTH + 32 + BLDG_WIDTH
)  # extended east by one Knott Hall width
WORLD_Y1, WORLD_Y2 = (
    -2048,
    1200,
)  # full world N-S extent (expanded north for Ennis wall)

# ── Knott Hall (south campus tower) ──────────────────────────────────────────
# Flush against the east world wall
BLDG_X2 = 1906  # fixed position regardless of world size
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
    1938,  # east pillar at old world edge
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
    """Format a number as an integer string if whole, otherwise 6-sig-fig float."""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"


def pt(x, y, z):
    """Return a Quake map point literal string '( x y z )'."""
    return f"( {fv(x)} {fv(y)} {fv(z)} )"


def face(p1, p2, p3, tex):
    """Return a Quake MAP brush face string from 3 coplanar points and a texture name."""
    return f"{pt(*p1)} {pt(*p2)} {pt(*p3)} {tex} 0 0 0 1 1"


def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None):
    """Axis-aligned rectangular brush. tex=sides, tt=top, tb=bottom (default to tex)."""
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


def shelf_box(x1, y1, z1, x2, y2, z2, tex_case, tex_front, front="y1"):
    """Box with tex_front on one face, tex_case on all others.
    front: which face is the display face — 'y1' (-Y south), 'y2' (+Y north),
                                             'x1' (-X west),  'x2' (+X east)."""
    tx1 = tex_front if front == "x1" else tex_case
    tx2 = tex_front if front == "x2" else tex_case
    ty1 = tex_front if front == "y1" else tex_case
    ty2 = tex_front if front == "y2" else tex_case
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1, z1), (x1, y2, z1), (x1, y1, z2), tx1),
                face((x2, y1, z1), (x2, y1, z2), (x2, y2, z1), tx2),
                face((x1, y1, z1), (x1, y1, z2), (x2, y1, z1), ty1),
                face((x1, y2, z1), (x2, y2, z1), (x1, y2, z2), ty2),
                face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tex_case),
                face((x1, y1, z2), (x1, y2, z2), (x2, y1, z2), tex_case),
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


def tri_prism(ax, ay, bx, by, cx, cy, z1, z2, tex):
    """Triangular prism. Triangle (ax,ay)→(bx,by)→(cx,cy) must be CCW from above.
    Face winding: side normals point inward (left-perpendicular of each CCW edge).
    Bottom +Z (solid above), top -Z (solid below)."""
    return (
        "{\n"
        + "\n".join(
            [
                face((ax, ay, z2), (bx, by, z2), (ax, ay, z1), tex),  # side AB
                face((bx, by, z2), (cx, cy, z2), (bx, by, z1), tex),  # side BC
                face((cx, cy, z2), (ax, ay, z2), (cx, cy, z1), tex),  # side CA
                face((ax, ay, z1), (bx, by, z1), (cx, cy, z1), tex),  # bottom (+Z)
                face((ax, ay, z2), (cx, cy, z2), (bx, by, z2), tex),  # top (-Z)
            ]
        )
        + "\n}"
    )


def arch_seg(xb, xf, yc, zc, rin, rout, t1d, t2d, tex):
    """One wedge-shaped brush segment of a semicircular arch ring (X-aligned span).
    Angles t1d..t2d in degrees; centre at (yc, zc); inner/outer radii rin/rout."""
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
    """Solid pie-slice brush for filling the interior of an arch (no inner hole).
    Used to create func_illusionary teleport glows and solid arch infill."""
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
    """Solid arch fill (base box + pie segments) for an X-aligned arch opening.
    Used for trigger_teleport and func_illusionary brush entities."""
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
    """One wedge-shaped brush segment of a semicircular arch ring (Y-aligned span).
    Mirror of arch_seg with X and Y roles swapped."""
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
    """Solid pie-slice brush for filling a Y-aligned arch interior. Mirror of arch_pie_seg."""
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
    """Solid arch fill for a Y-aligned arch opening. Mirror of arch_fill."""
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


def square_wall(x1, x2, y1, y2, floor_z, ceil_z, open_hw, tex, overhang=0, base_h=0):
    """Stone wall with a rectangular (square-topped) opening centred at Y=0.
    open_hw: half-width of the opening in Y.
    overhang: extra Y extent on pillar portions beyond ±open_hw.
    base_h: solid plinth height at ground level.
    """
    brushes = []
    _ext = open_hw + overhang
    if y1 < -_ext:
        brushes.append(box(x1, y1, floor_z, x2, -_ext, ceil_z, tex))
    if y2 > _ext:
        brushes.append(box(x1, _ext, floor_z, x2, y2, ceil_z, tex))
    brushes.append(box(x1, -_ext, floor_z, x2, -open_hw, ceil_z, tex))  # south pillar
    brushes.append(box(x1, open_hw, floor_z, x2, _ext, ceil_z, tex))  # north pillar
    brushes.append(box(x1, -open_hw, ceil_z - 16, x2, open_hw, ceil_z, tex))  # lintel
    if base_h > 0:
        brushes.append(box(x1, -open_hw, floor_z, x2, open_hw, floor_z + base_h, tex))
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
    """Freestanding arch ring (posts + curved ring) aligned on the Y axis.
    Side walls are omitted so the arch stands alone without flanking fill."""
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
    """Return a Quake MAP point entity string for the given classname and key/value pairs."""
    lines = ["{", f'"classname" "{cls}"']
    for k, v in kw.items():
        lines.append(f'"{k}" "{v}"')
    lines.append("}")
    return "\n".join(lines)


def brush_ent(cls, brushes, **kw):
    """Return a Quake MAP brush entity string wrapping one or more brush strings."""
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
BRUSHES = []

# ════════════════════════════════════════════════════════════════════════════════
# RECTANGULAR WORLD SHELL — floor, 4 outer walls, sky ceiling
# ════════════════════════════════════════════════════════════════════════════════
BRUSHES.append(
    box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y2, FZ2, TEX_GROUND)
)  # floor
BRUSHES.append(
    box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X1 + WALL_T, WORLD_Y2, WORLD_Z2, TEX_SKY)
)  # W wall
BRUSHES.append(
    box(WORLD_X2 - WALL_T, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y2, WORLD_Z2, TEX_SKY)
)  # E wall
BRUSHES.append(
    box(WORLD_X1, WORLD_Y2 - WALL_T, FZ1, WORLD_X2, WORLD_Y2, WORLD_Z2, TEX_SKY)
)  # N wall
BRUSHES.append(
    box(WORLD_X1, WORLD_Y1, FZ1, WORLD_X2, WORLD_Y1 + WALL_T, WORLD_Z2, TEX_SKY)
)  # S wall
BRUSHES.append(
    box(WORLD_X1, WORLD_Y1, WORLD_Z2 - WALL_T, WORLD_X2, WORLD_Y2, WORLD_Z2, TEX_SKY)
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

# ── Ennis Road (E-W, parallel to bridge, north side) ──
# Runs from Charles Street west edge (ROAD_X1) east to the world wall, dead-ending there.
# Half as wide as Charles Street (512/2=256 total → HW=128), north of bridge.
_ENNIS_Y = BRY2 + 400  # 536: centred 400 units north of bridge north edge
_ENNIS_HW = 128  # road half-width → 256-unit carriageway (half of Charles St's 512)
_ENNIS_X1 = ROAD_X1  # start at west edge of Charles St to form T-junction
_ENNIS_X2 = WORLD_X2 - WALL_T  # dead-end at east world wall

# Road surface (2-unit overlay so it textures differently from surrounding ground)
BRUSHES.append(box(ROAD_X1, _ROAD_Y1, FZ2, ROAD_X2, _ROAD_Y2, FZ2 + 2, TEX_ROAD))
_SWALK_START = BRY2 + 200  # sidewalk starts north of bridge
# West sidewalk — north of bridge
BRUSHES.append(
    box(
        ROAD_X1 - _WALK_W,
        _SWALK_START,
        FZ2,
        ROAD_X1,
        _ROAD_Y2,
        FZ2 + _WALK_H,
        TEX_CEMENT,
    )
)
# West curb — south section up to sidewalk start
BRUSHES.append(
    box(ROAD_X1 - 8, _ROAD_Y1, FZ2, ROAD_X1, _SWALK_START, FZ2 + _WALK_H, TEX_CEMENT)
)
# Raised ground west of curb — rock/ground texture, flush with sidewalk
BRUSHES.append(
    box(
        ROAD_X1 - _WALK_W,
        _ROAD_Y1,
        FZ2,
        ROAD_X1 - 8,
        _SWALK_START,
        FZ2 + _WALK_H,
        TEX_GROUND,
    )
)
# East sidewalk — split into two segments, trimmed _WALK_W short of each corner
BRUSHES.append(
    box(
        ROAD_X2,
        _ROAD_Y1,
        FZ2,
        ROAD_X2 + _WALK_W,
        _ENNIS_Y - _ENNIS_HW - _WALK_W,
        FZ2 + _WALK_H,
        TEX_CEMENT,
    )
)
BRUSHES.append(
    box(
        ROAD_X2,
        _ENNIS_Y + _ENNIS_HW + _WALK_W,
        FZ2,
        ROAD_X2 + _WALK_W,
        _ROAD_Y2,
        FZ2 + _WALK_H,
        TEX_CEMENT,
    )
)

# ── Ennis Road brushes ──
# Road surface (full length including intersection with Charles Street)
BRUSHES.append(
    box(
        _ENNIS_X1,
        _ENNIS_Y - _ENNIS_HW,
        FZ2,
        _ENNIS_X2,
        _ENNIS_Y + _ENNIS_HW,
        FZ2 + 2,
        TEX_ROAD,
    )
)
# North curb — offset east by _WALK_W to cut corner square
BRUSHES.append(
    box(
        ROAD_X2 + _WALK_W,
        _ENNIS_Y + _ENNIS_HW,
        FZ2,
        _ENNIS_X2,
        _ENNIS_Y + _ENNIS_HW + _WALK_W,
        FZ2 + _WALK_H,
        TEX_CEMENT,
    )
)
# South curb — offset east by _WALK_W to cut corner square
BRUSHES.append(
    box(
        ROAD_X2 + _WALK_W,
        _ENNIS_Y - _ENNIS_HW - _WALK_W,
        FZ2,
        _ENNIS_X2,
        _ENNIS_Y - _ENNIS_HW,
        FZ2 + _WALK_H,
        TEX_CEMENT,
    )
)

# ── Rounded intersection corners (Charles & Ennis) ───────────────────────────
# Arc center at the OUTER (far) corner so the curve faces outward toward the road.
# Each corner: road box fills the cut square, cement arc fans sit on top.
_CRN_R = _WALK_W  # corner radius = sidewalk width
_CRN_SEGS = 12  # segments per arc (12 × 7.5° = 90°)

# SE corner: far corner is at SE of cut square
_cx_se = ROAD_X2 + _CRN_R
_cy_se = _ENNIS_Y - _ENNIS_HW - _CRN_R
BRUSHES.append(
    box(ROAD_X2, _cy_se, FZ2, _cx_se, _ENNIS_Y - _ENNIS_HW, FZ2 + 2, TEX_ROAD)
)
# Arc sweeps CCW from 90° (north) to 180° (west)
for _i in range(_CRN_SEGS):
    _a0 = math.radians(90 + _i * 90 / _CRN_SEGS)
    _a1 = math.radians(90 + (_i + 1) * 90 / _CRN_SEGS)
    _px0, _py0 = _cx_se + _CRN_R * math.cos(_a0), _cy_se + _CRN_R * math.sin(_a0)
    _px1, _py1 = _cx_se + _CRN_R * math.cos(_a1), _cy_se + _CRN_R * math.sin(_a1)
    BRUSHES.append(
        tri_prism(
            _cx_se, _cy_se, _px0, _py0, _px1, _py1, FZ2, FZ2 + _WALK_H, TEX_CEMENT
        )
    )

# NE corner: far corner is at NE of cut square
_cx_ne = ROAD_X2 + _CRN_R
_cy_ne = _ENNIS_Y + _ENNIS_HW + _CRN_R
BRUSHES.append(
    box(ROAD_X2, _ENNIS_Y + _ENNIS_HW, FZ2, _cx_ne, _cy_ne, FZ2 + 2, TEX_ROAD)
)
# Arc sweeps CCW from 180° (west) to 270° (south)
for _i in range(_CRN_SEGS):
    _a0 = math.radians(180 + _i * 90 / _CRN_SEGS)
    _a1 = math.radians(180 + (_i + 1) * 90 / _CRN_SEGS)
    _px0, _py0 = _cx_ne + _CRN_R * math.cos(_a0), _cy_ne + _CRN_R * math.sin(_a0)
    _px1, _py1 = _cx_ne + _CRN_R * math.cos(_a1), _cy_ne + _CRN_R * math.sin(_a1)
    BRUSHES.append(
        tri_prism(
            _cx_ne, _cy_ne, _px0, _py0, _px1, _py1, FZ2, FZ2 + _WALK_H, TEX_CEMENT
        )
    )

# ── Sidewalk ramps — smooth ground-to-sidewalk transitions ───────────────────
_RAMP_W = 64  # ramp width in units

# West ramp — slopes from ground up to west sidewalk edge (full N-S extent)
BRUSHES.append(
    ramp_slab(
        ROAD_X1 - _WALK_W - _RAMP_W,
        ROAD_X1 - _WALK_W,
        _ROAD_Y1,
        _ROAD_Y2,
        FZ1,
        FZ1,
        FZ2,
        FZ2 + _WALK_H,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# East ramp — south of Ennis Road
BRUSHES.append(
    ramp_slab(
        ROAD_X2 + _WALK_W,
        ROAD_X2 + _WALK_W + _RAMP_W,
        _ROAD_Y1,
        _ENNIS_Y - _ENNIS_HW - _WALK_W,
        FZ1,
        FZ1,
        FZ2 + _WALK_H,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# East ramp — north of Ennis Road
BRUSHES.append(
    ramp_slab(
        ROAD_X2 + _WALK_W,
        ROAD_X2 + _WALK_W + _RAMP_W,
        _ENNIS_Y + _ENNIS_HW + _WALK_W,
        _ROAD_Y2,
        FZ1,
        FZ1,
        FZ2 + _WALK_H,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# Ennis north ramp — slopes from north curb edge down going north
BRUSHES.append(
    ramp_slab_y(
        ROAD_X2 + _WALK_W,
        _ENNIS_X2,
        _ENNIS_Y + _ENNIS_HW + _WALK_W,
        _ENNIS_Y + _ENNIS_HW + _WALK_W + _RAMP_W,
        FZ1,
        FZ1,
        FZ2 + _WALK_H,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# Ennis south ramp — slopes from south curb edge down going south
BRUSHES.append(
    ramp_slab_y(
        ROAD_X2 + _WALK_W,
        _ENNIS_X2,
        _ENNIS_Y - _ENNIS_HW - _WALK_W - _RAMP_W,
        _ENNIS_Y - _ENNIS_HW - _WALK_W,
        FZ1,
        FZ1,
        FZ2,
        FZ2 + _WALK_H,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)

# ── Ennis Drive entrance pillars (white stone columns flanking Charles St entrance) ──
_EPL_HW = 22  # pillar half-width (was 30, ×0.75)
_EPL_OFFSET = _WALK_W + 20
_EPL_X1 = PXS[2] - _EPL_HW  # align pillar centre with closest bridge pier (X=525)
_EPL_X2 = PXS[2] + _EPL_HW
_EPL_ZB = FZ2
_EPL_POST_H = 81  # post height (was 108, ×0.75)
_EPL_CAP_OVH = 1
_EPL_CAP_H = 3

# Bell shape — cap divider + single tapered step (no flare, no tip):
#      |  |      step 2: hw=16, h=27
#  ====+==+====  cap:    hw=23, h=1
#      |  |      post:   hw=22, h=81
_EPL_BELL2_HW = 19  # tapered top section half-width (wider than before, less than post)
_EPL_BELL2_H = 27  # tapered top section height (was 36, ×0.75)

for _epy in (_ENNIS_Y - _ENNIS_HW - _EPL_HW, _ENNIS_Y + _ENNIS_HW + _EPL_HW):
    _epl_cx = _EPL_X1 + _EPL_HW  # pillar centre X
    _cap_hw = _EPL_HW + _EPL_CAP_OVH  # = 40

    # Post
    _base_h = _EPL_POST_H // 3  # bottom base = lower third of post
    # Bottom base — same width as cap, gives plinth effect
    BRUSHES.append(
        box(
            _epl_cx - _cap_hw,
            _epy - _cap_hw,
            _EPL_ZB,
            _epl_cx + _cap_hw,
            _epy + _cap_hw,
            _EPL_ZB + _base_h,
            TEX_WHITE_STONE,
        )
    )
    # Upper post — narrower, sits on bottom base
    BRUSHES.append(
        box(
            _EPL_X1,
            _epy - _EPL_HW,
            _EPL_ZB + _base_h,
            _EPL_X2,
            _epy + _EPL_HW,
            _EPL_ZB + _EPL_POST_H,
            TEX_WHITE_STONE,
        )
    )
    # Thin cap divider — overhangs post on all sides
    _cap_z = _EPL_ZB + _EPL_POST_H
    BRUSHES.append(
        box(
            _epl_cx - _cap_hw,
            _epy - _cap_hw,
            _cap_z,
            _epl_cx + _cap_hw,
            _epy + _cap_hw,
            _cap_z + _EPL_CAP_H,
            TEX_WHITE_STONE,
        )
    )
    # Bell step 2 — tapered top, narrower than post
    _b2_z = _cap_z + _EPL_CAP_H
    BRUSHES.append(
        box(
            _epl_cx - _EPL_BELL2_HW,
            _epy - _EPL_BELL2_HW,
            _b2_z,
            _epl_cx + _EPL_BELL2_HW,
            _epy + _EPL_BELL2_HW,
            _b2_z + _EPL_BELL2_H,
            TEX_WHITE_STONE,
        )
    )
    # Torch base above pyramid apex — narrow post + brick cup (matches bridge pillars)
    _epl_apex = _b2_z + _EPL_BELL2_H
    _epl_cx = _EPL_X1 + _EPL_HW
    BRUSHES.append(
        box(
            _epl_cx - 3,
            _epy - 3,
            _epl_apex,
            _epl_cx + 3,
            _epy + 3,
            _epl_apex + 16,
            TEX_CEMENT,
        )
    )
    BRUSHES.append(
        box(
            _epl_cx - 5,
            _epy - 5,
            _epl_apex + 16,
            _epl_cx + 5,
            _epy + 5,
            _epl_apex + 20,
            TEX_BRICK,
        )
    )

# ── Ennis Drive L-shaped campus boundary wall (north side of entrance) ────────
# city2_1 brick wall from near Charles St sidewalk east to pillar, then turns north.
# Starts with a small grass gap east of the sidewalk.
_BW_T = 8  # wall thickness
_BW_H = 48  # wall height ≈ 3 ft
_BW_NY = _ENNIS_Y + _ENNIS_HW + _EPL_HW * 2  # south face Y (flush with north pillar)
_BW_X1 = ROAD_X2 + _WALK_W + 48  # ~48u east of sidewalk (more grass)
_BW_EX2 = PXS[2] + _EPL_HW + 80  # E-W wall extends past stone pillar
_BW_NY2 = _BW_NY + 200  # north segment length
# East-running segment (south base of L)
BRUSHES.append(
    box(_BW_X1, _BW_NY, FZ2, _BW_EX2, _BW_NY + _BW_T, FZ2 + _BW_H, "city2_1")
)
# North-turning segment — at the WEST end, runs north to world wall
BRUSHES.append(
    box(_BW_X1, _BW_NY, FZ2, _BW_X1 + _BW_T, WORLD_Y2 - WALL_T, FZ2 + _BW_H, "city2_1")
)
# Corner pillar — square brick post at the L junction, wider than wall
_BW_PIL_HW = 14  # pillar half-width (28 units square)
_BW_PIL_H = 64  # pillar height — taller than wall
_BW_CX = _BW_X1 + _BW_T // 2  # pillar centre X (wall centre)
_BW_CY = _BW_NY + _BW_T // 2  # pillar centre Y (wall centre)
BRUSHES.append(
    box(
        _BW_CX - _BW_PIL_HW,
        _BW_CY - _BW_PIL_HW,
        FZ2,
        _BW_CX + _BW_PIL_HW,
        _BW_CY + _BW_PIL_HW,
        FZ2 + _BW_PIL_H,
        "city2_1",
    )
)
# Cement collar — same width as pillar, sits between brick post and cap slab
BRUSHES.append(
    box(
        _BW_CX - _BW_PIL_HW,
        _BW_CY - _BW_PIL_HW,
        FZ2 + _BW_PIL_H,
        _BW_CX + _BW_PIL_HW,
        _BW_CY + _BW_PIL_HW,
        FZ2 + _BW_PIL_H + 6,
        TEX_CEMENT,
    )
)
# Square cap slab, then shallow pyramid on top
BRUSHES.append(
    box(
        _BW_CX - _BW_PIL_HW - 1,
        _BW_CY - _BW_PIL_HW - 1,
        FZ2 + _BW_PIL_H + 6,
        _BW_CX + _BW_PIL_HW + 1,
        _BW_CY + _BW_PIL_HW + 1,
        FZ2 + _BW_PIL_H + 10,
        TEX_CEMENT,
    )
)
BRUSHES.append(
    pyramid(
        _BW_CX - _BW_PIL_HW - 1,
        _BW_CY - _BW_PIL_HW - 1,
        FZ2 + _BW_PIL_H + 10,
        _BW_CX + _BW_PIL_HW + 1,
        _BW_CY + _BW_PIL_HW + 1,
        FZ2 + _BW_PIL_H + 16,
        TEX_CEMENT,
    )
)


# ── Abutment building dimensions (referenced by embankment split below) ────────
_AB_FLOORS = 3
_AB_H = _AB_FLOORS * FLOOR_H  # 384 units tall
_AB_D = 600  # building N-S depth (doubled)
_ABUTMENT_X = min(PXS)  # = -1100
_AB_X2 = _ABUTMENT_X + P_HW + 32  # east face of building  = -1031
_AB_X1 = _AB_X2 - 576  # west face of building (doubled width)
_NB_Y2 = WORLD_Y2 - WALL_T - 150  # north building north face (shifted south)
_NB_Y1 = _NB_Y2 - _AB_D  # north building south face
_SB_Y1 = WORLD_Y1 + WALL_T  # south building 1 south face = -2032
_SB_Y2 = _SB_Y1 + _AB_D  # south building 1 north face = -1432
_SB2_Y1 = _SB_Y2  # south building 2 south face = -1432
_SB2_Y2 = _SB2_Y1 + _AB_D  # south building 2 north face = -832

# Starts at X=-560 (clear of the -525 pier base) so arch stone is not buried there.
_EMB_X2 = -1146  # starts just east of abutment pier, keeping stone base visible
# Interpolate ramp top-Z at the building's west face so the slope is continuous
_emb_zt_at_ab_x1 = int(DZ2 + (FZ2 - DZ2) * (_AB_X1 - BRX1) / (_EMB_X2 - BRX1))
# South segment — west of south buildings (through buildings' Y range)
BRUSHES.append(
    ramp_slab(
        BRX1,
        _AB_X1,
        _ROAD_Y1,
        _SB2_Y2,
        FZ1,
        FZ1,
        DZ2,
        _emb_zt_at_ab_x1,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# South segment — full width between south buildings and north building
BRUSHES.append(
    ramp_slab(
        BRX1, _EMB_X2, _SB2_Y2, _NB_Y1, FZ1, FZ1, DZ2, FZ2, TEX_GROUND, tt=TEX_GROUND
    )
)
# Middle segment — only west of north building
BRUSHES.append(
    ramp_slab(
        BRX1,
        _AB_X1,
        _NB_Y1,
        _NB_Y2,
        FZ1,
        FZ1,
        DZ2,
        _emb_zt_at_ab_x1,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# North of north building — restore original ramp
BRUSHES.append(
    ramp_slab(
        BRX1, _EMB_X2, _NB_Y2, _ROAD_Y2, FZ1, FZ1, DZ2, FZ2, TEX_GROUND, tt=TEX_GROUND
    )
)

# Wall extending north from the abutment pier, deck height, city2_1 texture
# Door opening ~160 units north of the pier (visible in bridge10)
_NORTH_WALL_Y1 = BRY2 + PIL_OVERHANG  # north face of pier = 152
_SOUTH_WALL_Y2 = -(BRY2 + PIL_OVERHANG)  # south face of pier = -152
_DOOR_W = 80  # door opening width (~5 ft)
_DOOR_OFF = 160  # distance from pier face to door centre
_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)
# (Building dimensions already defined above)
# South brick wall — from bridge pier south face to nearest south building, with door gap
# Door centered 160 units north of the building (closer to buildings)
_s_door_y = _SB2_Y2 + _DOOR_OFF  # door centre Y
BRUSHES.append(
    box(
        _ABUTMENT_X - P_HW,
        _SB2_Y2,
        FZ2,
        _ABUTMENT_X + P_HW,
        _s_door_y - _DOOR_W // 2,
        DZ2,
        "city2_1",
    )
)
BRUSHES.append(
    box(
        _ABUTMENT_X - P_HW,
        _s_door_y + _DOOR_W // 2,
        FZ2,
        _ABUTMENT_X + P_HW,
        _SOUTH_WALL_Y2,
        DZ2,
        "city2_1",
    )
)
BRUSHES.append(
    box(
        _ABUTMENT_X - P_HW,
        _s_door_y - _DOOR_W // 2,
        FZ2 + _DOOR_H,
        _ABUTMENT_X + P_HW,
        _s_door_y + _DOOR_W // 2,
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
    """Protruding TEX_CEMENT window-trim panels on the visible faces of a solid brick box."""
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
                        TEX_CEMENT,
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
                        TEX_CEMENT,
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
                    TEX_CEMENT,
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
                    TEX_CEMENT,
                )
            )
    return brushes


# ── North building — hollow shell with windows, entrance, and gable roof ───────
_NB_WT = 16  # wall thickness
_NB_WW = 36  # window half-width
_NB_WH = 44  # window half-height
_NB_ENT_HW = 48  # entrance half-width (96-unit wide doorway)
_NB_ENT_H = 100  # entrance height

_nb_cx = (_AB_X1 + _AB_X2) // 2  # building X center
_nb_cy = (_NB_Y1 + _NB_Y2) // 2  # building Y center (gable ridge line)

# Window X centers on south/north face: 2 left + 2 right of the entrance gap
_nb_wx = [_AB_X1 + (_nb_cx - _NB_ENT_HW - _AB_X1) * k // 3 for k in [1, 2]] + [
    (_nb_cx + _NB_ENT_HW) + (_AB_X2 - _nb_cx - _NB_ENT_HW) * k // 3 for k in [1, 2]
]
# Window Y centers on east/west face: 3 evenly spaced
_nb_wy = [_NB_Y1 + (_NB_Y2 - _NB_Y1) * k // 4 for k in [1, 2, 3]]

_nb_wz_lo = (FLOOR_H - _NB_WH * 2) // 2  # window sill offset within a floor
_nb_wz_hi = _nb_wz_lo + _NB_WH * 2  # window head offset within a floor


def _nb_wins_xz(wx_list):
    """Window openings (all floors) for X-facing wall (south/north)."""
    return [
        (
            wx - _NB_WW,
            FZ2 + fl * FLOOR_H + _nb_wz_lo,
            wx + _NB_WW,
            FZ2 + fl * FLOOR_H + _nb_wz_hi,
        )
        for fl in range(_AB_FLOORS)
        for wx in wx_list
    ]


def _nb_wins_yz(wy_list):
    """Window openings (all floors) for Y-facing wall (east/west)."""
    return [
        (
            wy - _NB_WW,
            FZ2 + fl * FLOOR_H + _nb_wz_lo,
            wy + _NB_WW,
            FZ2 + fl * FLOOR_H + _nb_wz_hi,
        )
        for fl in range(_AB_FLOORS)
        for wy in wy_list
    ]


# South wall (faces bridge) — windows + ground-level entrance
_nb_s_openings = _nb_wins_xz(_nb_wx) + [
    (_nb_cx - _NB_ENT_HW, FZ2, _nb_cx + _NB_ENT_HW, FZ2 + _NB_ENT_H)
]
BRUSHES.extend(
    layered_wall(
        _AB_X1,
        _NB_Y1,
        FZ2,
        _AB_X2,
        _NB_Y1 + _NB_WT,
        FZ2 + _AB_H,
        _nb_s_openings,
        "city2_1",
    )
)
# North wall — windows only
BRUSHES.extend(
    layered_wall(
        _AB_X1,
        _NB_Y2 - _NB_WT,
        FZ2,
        _AB_X2,
        _NB_Y2,
        FZ2 + _AB_H,
        _nb_wins_xz(_nb_wx),
        "city2_1",
    )
)
# East wall — windows + ground-level entrance (matches south buildings)
_nb_e_openings = _nb_wins_yz(_nb_wy) + [
    (_nb_cy - _NB_ENT_HW, FZ2, _nb_cy + _NB_ENT_HW, FZ2 + _NB_ENT_H)
]
BRUSHES.extend(
    layered_wall_y(
        _NB_Y1 + _NB_WT,
        _AB_X2 - _NB_WT,
        FZ2,
        _NB_Y2 - _NB_WT,
        _AB_X2,
        FZ2 + _AB_H,
        _nb_e_openings,
        "city2_1",
    )
)
# West wall — windows
BRUSHES.extend(
    layered_wall_y(
        _NB_Y1 + _NB_WT,
        _AB_X1,
        FZ2,
        _NB_Y2 - _NB_WT,
        _AB_X1 + _NB_WT,
        FZ2 + _AB_H,
        _nb_wins_yz(_nb_wy),
        "city2_1",
    )
)
# Ceiling slab
BRUSHES.append(
    box(_AB_X1, _NB_Y1, FZ2 + _AB_H, _AB_X2, _NB_Y2, FZ2 + _AB_H + _NB_WT, "city2_1")
)

# Gable (A-frame) roof — ridge runs N-S at building X center, FLOOR_H above ceiling
_nb_eave_z = FZ2 + _AB_H + _NB_WT  # top of ceiling slab = eave level
_nb_ridge_z = _nb_eave_z + FLOOR_H  # ridge apex
_nb_slab_t = 16  # roof slab thickness at eave
# West slope: flat bottom at eave_z, top slopes up to ridge at nb_cx
BRUSHES.append(
    ramp_slab(
        _AB_X1,
        _nb_cx,
        _NB_Y1,
        _NB_Y2,
        _nb_eave_z,
        _nb_eave_z,
        _nb_eave_z + _nb_slab_t,
        _nb_ridge_z,
        TEX_ROOF,
    )
)
# East slope: top at ridge at nb_cx, slopes down to eave at AB_X2
BRUSHES.append(
    ramp_slab(
        _nb_cx,
        _AB_X2,
        _NB_Y1,
        _NB_Y2,
        _nb_eave_z,
        _nb_eave_z,
        _nb_ridge_z,
        _nb_eave_z + _nb_slab_t,
        TEX_ROOF,
    )
)
# Interior floor — flat ground surface inside the building (covers the hill void)
BRUSHES.append(
    box(
        _AB_X1 + _NB_WT,
        _NB_Y1 + _NB_WT,
        FZ1,
        _AB_X2 - _NB_WT,
        _NB_Y2 - _NB_WT,
        FZ2,
        TEX_GROUND,
        tt=TEX_ROAD,
    )
)


# ── Two south buildings — exact copies of north building, stacked N-S ──────────
# Same X footprint (_AB_X1.._AB_X2), entrance on east face (faces Charles Street).


def _make_south_bldg(by1, by2):
    """Build the south abutment building geometry (walls, roof, windows, entrance)
    between Y positions by1 (south) and by2 (north)."""
    bx1, bx2 = _AB_X1, _AB_X2
    cx = (bx1 + bx2) // 2
    ent_hw, ent_h = 48, 100
    wx_list = [bx1 + (cx - ent_hw - bx1) * k // 3 for k in [1, 2]] + [
        (cx + ent_hw) + (bx2 - cx - ent_hw) * k // 3 for k in [1, 2]
    ]
    wy_list = [by1 + (by2 - by1) * k // 4 for k in [1, 2, 3]]

    def wxz():
        return [
            (
                wx - _NB_WW,
                FZ2 + fl * FLOOR_H + _nb_wz_lo,
                wx + _NB_WW,
                FZ2 + fl * FLOOR_H + _nb_wz_hi,
            )
            for fl in range(_AB_FLOORS)
            for wx in wx_list
        ]

    def wyz():
        return [
            (
                wy - _NB_WW,
                FZ2 + fl * FLOOR_H + _nb_wz_lo,
                wy + _NB_WW,
                FZ2 + fl * FLOOR_H + _nb_wz_hi,
            )
            for fl in range(_AB_FLOORS)
            for wy in wy_list
        ]

    brushes = []
    # Interior floor
    brushes.append(
        box(
            bx1 + _NB_WT,
            by1 + _NB_WT,
            FZ1,
            bx2 - _NB_WT,
            by2 - _NB_WT,
            FZ2,
            TEX_GROUND,
            tt=TEX_ROAD,
        )
    )
    brushes.extend(
        layered_wall(bx1, by1, FZ2, bx2, by1 + _NB_WT, FZ2 + _AB_H, wxz(), "city2_1")
    )
    brushes.extend(
        layered_wall(bx1, by2 - _NB_WT, FZ2, bx2, by2, FZ2 + _AB_H, wxz(), "city2_1")
    )
    brushes.extend(
        layered_wall_y(
            by1 + _NB_WT,
            bx1,
            FZ2,
            by2 - _NB_WT,
            bx1 + _NB_WT,
            FZ2 + _AB_H,
            wyz(),
            "city2_1",
        )
    )
    cy = (by1 + by2) // 2
    east_openings = wyz() + [(cy - ent_hw, FZ2, cy + ent_hw, FZ2 + ent_h)]
    brushes.extend(
        layered_wall_y(
            by1 + _NB_WT,
            bx2 - _NB_WT,
            FZ2,
            by2 - _NB_WT,
            bx2,
            FZ2 + _AB_H,
            east_openings,
            "city2_1",
        )
    )
    brushes.append(
        box(bx1, by1, FZ2 + _AB_H, bx2, by2, FZ2 + _AB_H + _NB_WT, "city2_1")
    )
    eave_z, ridge_z, slab_t = FZ2 + _AB_H + _NB_WT, FZ2 + _AB_H + _NB_WT + FLOOR_H, 16
    brushes.append(
        ramp_slab(bx1, cx, by1, by2, eave_z, eave_z, eave_z + slab_t, ridge_z, TEX_ROOF)
    )
    brushes.append(
        ramp_slab(cx, bx2, by1, by2, eave_z, eave_z, ridge_z, eave_z + slab_t, TEX_ROOF)
    )
    return brushes


BRUSHES.extend(_make_south_bldg(_SB_Y1, _SB_Y2))
BRUSHES.extend(_make_south_bldg(_SB2_Y1, _SB2_Y2))

# ── Iron fence along east face of west buildings ──────────────────────────
_FNC_X1 = _AB_X2 + 96  # well clear of building face
_FNC_X2 = _FNC_X1 + 2  # picket/rail thickness
_FNC_H = 96  # fence height
_FNC_SPACING = 16  # picket center-to-center
_FNC_RAIL = 8  # rail thickness
_FNC_TEX = "metal4_4"

for _fy1, _fy2 in [(_ROAD_Y1, _ROAD_Y2)]:
    # Top rail — thin, dropped so pickets extend above it
    BRUSHES.append(
        box(
            _FNC_X1, _fy1, FZ2 + _FNC_H - 28, _FNC_X2, _fy2, FZ2 + _FNC_H - 26, _FNC_TEX
        )
    )
    # Pickets — thin (2 wide) with thick posts (8 wide) every 10th
    _py = _fy1
    _pi = 0
    while _py + 2 <= _fy2:
        _pw = 8 if _pi % 10 == 0 else 2
        BRUSHES.append(
            box(_FNC_X1, _py, FZ2, _FNC_X2, _py + _pw, FZ2 + _FNC_H, _FNC_TEX)
        )
        _py += _FNC_SPACING
        _pi += 1


# ════════════════════════════════════════════════════════════════════════════════
# West flat approach removed — arch now starts at world edge
# East flat stub from arch terminus to building entrance
BRUSHES.append(
    box(
        BRX2,
        BRY1,
        DZ1,
        WORLD_X2 - WALL_T,
        BRY2,
        DZ2,
        TEX_STONE,
        tt=TEX_FLOOR,
        tb=TEX_FLOOR,
    )
)

for i in range(ARCH_SEGS):
    sx1 = BRX1 + i * SEG_W
    sx2 = sx1 + SEG_W
    BRUSHES.append(
        ramp_slab(
            sx1,
            sx2,
            BRY1,
            BRY2,
            dbot(sx1),
            dbot(sx2),
            dtop(sx1),
            dtop(sx2),
            TEX_STONE,
            tt=TEX_FLOOR,
            tb=TEX_FLOOR,
        )
    )

# ── Parapet walls — west flat approach removed; east flat stub only ───────────
BRUSHES.append(
    box(BRX2, BRY2 - PAR_W, DZ2, WORLD_X2 - WALL_T, BRY2, DZ2 + PAR_H, TEX_CEMENT)
)  # North east
# South east — gap at WALK_X1..WALK_X2 for walkway connection to building
BRUSHES.append(box(BRX2, BRY1, DZ2, WALK_X1, BRY1 + PAR_W, DZ2 + PAR_H, TEX_CEMENT))
BRUSHES.append(
    box(WALK_X2, BRY1, DZ2, WORLD_X2 - WALL_T, BRY1 + PAR_W, DZ2 + PAR_H, TEX_CEMENT)
)

for i in range(ARCH_SEGS):
    sx1 = BRX1 + i * SEG_W
    sx2 = sx1 + SEG_W
    pb1, pb2 = dtop(sx1), dtop(sx2)  # parapet base follows deck top
    pt1, pt2 = pb1 + PAR_H, pb2 + PAR_H  # parapet top = base + PAR_H
    # North parapet
    BRUSHES.append(
        ramp_slab(sx1, sx2, BRY2 - PAR_W, BRY2, pb1, pb2, pt1, pt2, TEX_CEMENT)
    )
    # South parapet — omit any segment that overlaps the walkway gap (X=WALK_X1..WALK_X2)
    if not (sx1 < WALK_X2 and sx2 > WALK_X1):
        BRUSHES.append(
            ramp_slab(sx1, sx2, BRY1, BRY1 + PAR_W, pb1, pb2, pt1, pt2, TEX_CEMENT)
        )

# ── Parapet cement blocks (decorative posts atop parapet walls) ───────────────
_BLK_HW = 24  # block half-width in X (48 units wide along bridge)
_BLK_H = 36  # block height above parapet top
_BLK_OVH = 0  # blocks flush with outer bridge wall
_PIR_M = P_HW + _BLK_HW + 4  # clearance from pier centre to block centre


def _add_parapet_blocks(
    x_start,
    x_end,
    n,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
):
    """Add evenly-spaced cement blocks atop N and S parapets in a bridge span.

    n_south defaults to n.  South blocks that overlap the walkway gap
    (WALK_X1..WALK_X2) are skipped automatically.
    east_margin_n overrides east_margin for north blocks only.
    """
    n_s = n if n_south is None else n_south
    mx0 = west_margin if west_margin is not None else _PIR_M
    mx1 = east_margin if east_margin is not None else _PIR_M
    mx1_n = east_margin_n if east_margin_n is not None else mx1
    x0 = x_start + mx0
    x1_n = x_end - mx1_n
    x1_s = x_end - mx1
    for k in range(n):
        cx = x0 + (x1_n - x0) * (k + 1) / (n + 1)
        # Use minimum parapet top across block width so block never floats above parapet
        bz = min(dtop(cx - _BLK_HW), dtop(cx), dtop(cx + _BLK_HW)) + PAR_H
        BRUSHES.append(
            box(
                cx - _BLK_HW,
                BRY2 - PAR_W,
                bz,
                cx + _BLK_HW,
                BRY2 + _BLK_OVH,
                bz + _BLK_H,
                TEX_CEMENT,
            )
        )
    for k in range(n_s):
        cx = x0 + (x1_s - x0) * (k + 1) / (n_s + 1)
        bz = min(dtop(cx - _BLK_HW), dtop(cx), dtop(cx + _BLK_HW)) + PAR_H
        if not (cx - _BLK_HW < WALK_X2 and cx + _BLK_HW > WALK_X1):
            BRUSHES.append(
                box(
                    cx - _BLK_HW,
                    BRY1 - _BLK_OVH,
                    bz,
                    cx + _BLK_HW,
                    BRY1 + PAR_W,
                    bz + _BLK_H,
                    TEX_CEMENT,
                )
            )


# Western span (BRX1 → PXS[0]): no blocks — open span
# Span 2 (PXS[0] → PXS[1]): eastern span 1, 3 blocks
_add_parapet_blocks(PXS[0], PXS[1], 3)
# Middle span (PXS[1] → PXS[2]): 4 blocks
_add_parapet_blocks(PXS[1], PXS[2], 4)
# Eastern span 2 (PXS[2] → PXS[3]): 3 blocks
_add_parapet_blocks(PXS[2], PXS[3], 3)
# East flat span: west sub-span (BRX2→PXS[4]) gets 3 north blocks; east sub-span open (matches ref)
_add_parapet_blocks(BRX2, PXS[4], 3, west_margin=_BLK_HW + 8, n_south=0)

# ── Decorative squares on parapet outer faces (one per block position) ────────
_SQ_HW = 8  # half-width in X (16 units wide)
_SQ_HH = 6  # half-height in Z (12 units tall)
_SQ_D = 1  # protrusion depth (1 unit proud)


def _add_parapet_squares(
    x_start,
    x_end,
    n,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
):
    """Add raised decorative squares on parapet outer faces, same positions as blocks."""
    n_s = n if n_south is None else n_south
    mx0 = west_margin if west_margin is not None else _PIR_M
    mx1 = east_margin if east_margin is not None else _PIR_M
    mx1_n = east_margin_n if east_margin_n is not None else mx1
    x0 = x_start + mx0
    x1_n = x_end - mx1_n
    x1_s = x_end - mx1
    for k in range(n):
        cx = int(x0 + (x1_n - x0) * (k + 1) / (n + 1))
        bz = (
            int(min(dtop(cx - _SQ_HW), dtop(cx), dtop(cx + _SQ_HW)))
            + PAR_H
            + _BLK_H // 2
        )
        BRUSHES.append(
            box(
                cx - _SQ_HW,
                BRY2,
                bz - _SQ_HH,
                cx + _SQ_HW,
                BRY2 + _SQ_D,
                bz + _SQ_HH,
                TEX_RAIL,
            )
        )
    for k in range(n_s):
        cx = int(x0 + (x1_s - x0) * (k + 1) / (n_s + 1))
        if not (cx - _SQ_HW < WALK_X2 and cx + _SQ_HW > WALK_X1):
            bz = (
                int(min(dtop(cx - _SQ_HW), dtop(cx), dtop(cx + _SQ_HW)))
                + PAR_H
                + _BLK_H // 2
            )
            BRUSHES.append(
                box(
                    cx - _SQ_HW,
                    BRY1 - _SQ_D,
                    bz - _SQ_HH,
                    cx + _SQ_HW,
                    BRY1,
                    bz + _SQ_HH,
                    TEX_RAIL,
                )
            )


_add_parapet_squares(PXS[0], PXS[1], 3)
_add_parapet_squares(PXS[1], PXS[2], 4)
_add_parapet_squares(PXS[2], PXS[3], 3)
_add_parapet_squares(BRX2, PXS[4], 3, west_margin=_BLK_HW + 8, n_south=0)
# South east of walkway: corner blocks only at each side of the opening
# Corner block on east side of walkway opening (west face flush with WALK_X2)
_cx_walk_e = WALK_X2 + _BLK_HW
BRUSHES.append(
    box(
        _cx_walk_e - _BLK_HW,
        BRY1 - _BLK_OVH,
        DZ2 + PAR_H,
        _cx_walk_e + _BLK_HW,
        BRY1 + PAR_W,
        DZ2 + PAR_H + _BLK_H,
        TEX_CEMENT,
    )
)
# Extra block on west side of walkway opening (east face flush with WALK_X1)
_cx_walk_w = WALK_X1 - _BLK_HW
BRUSHES.append(
    box(
        _cx_walk_w - _BLK_HW,
        BRY1 - _BLK_OVH,
        DZ2 + PAR_H,
        _cx_walk_w + _BLK_HW,
        BRY1 + PAR_W,
        DZ2 + PAR_H + _BLK_H,
        TEX_CEMENT,
    )
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
        BRUSHES.append(
            ramp_slab(
                _sx1,
                _sx2,
                _TUBE_NY1,
                _TUBE_NY2,
                _zb1,
                _zb2,
                _zb1 + _TUBE_HW * 2,
                _zb2 + _TUBE_HW * 2,
                TEX_RAIL,
            )
        )
        if not (_sx1 < WALK_X2 and _sx2 > WALK_X1):
            BRUSHES.append(
                ramp_slab(
                    _sx1,
                    _sx2,
                    _TUBE_SY1,
                    _TUBE_SY2,
                    _zb1,
                    _zb2,
                    _zb1 + _TUBE_HW * 2,
                    _zb2 + _TUBE_HW * 2,
                    TEX_RAIL,
                )
            )
    # East flat section
    _tbz = DZ2 + PAR_H + _tube_z_extra
    _x_east_end = WORLD_X2 - WALL_T
    BRUSHES.append(
        box(
            BRX2, _TUBE_NY1, _tbz, _x_east_end, _TUBE_NY2, _tbz + _TUBE_HW * 2, TEX_RAIL
        )
    )
    BRUSHES.append(
        box(BRX2, _TUBE_SY1, _tbz, WALK_X1, _TUBE_SY2, _tbz + _TUBE_HW * 2, TEX_RAIL)
    )
    BRUSHES.append(
        box(
            WALK_X2,
            _TUBE_SY1,
            _tbz,
            _x_east_end,
            _TUBE_SY2,
            _tbz + _TUBE_HW * 2,
            TEX_RAIL,
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

        # Add pier structure — easternmost pier gets a square opening, rest are arched
        if px == max(PXS):
            # Overhang must reach BRY2+PIL_OVERHANG to match pillar tops above deck
            _sq_overhang = BRY2 + PIL_OVERHANG - a_rin
            BRUSHES.extend(
                square_wall(
                    x1,
                    x2,
                    BRY1,
                    BRY2,
                    FZ2,
                    int(pdeck) - 16,
                    a_rin,
                    TEX_PILLAR,
                    overhang=_sq_overhang,
                    base_h=32,
                )
            )
        else:
            BRUSHES.extend(
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
                    TEX_PILLAR,
                    stilt_h=a_stilt,
                    overhang=_arch_overhang,
                    base_h=32,
                )
            )

        # Pillar tops (above deck, extend PIL_OVERHANG past bridge edges and inward)
        _pil_out = BRY2 + PIL_OVERHANG  # always overhang past bridge edge
        # North pillar top
        BRUSHES.append(
            box(
                px - P_HW,
                BRY2 - PAR_W - PIL_OVERHANG,
                pdeck,
                px + P_HW,
                _pil_out,
                ppil,
                TEX_PILLAR,
            )
        )

        # South pillar top
        BRUSHES.append(
            box(
                px - P_HW,
                -_pil_out,
                pdeck,
                px + P_HW,
                BRY1 + PAR_W + PIL_OVERHANG,
                ppil,
                TEX_PILLAR,
            )
        )

        # Fill gap between pier top and deck surface in the overhang zone
        pier_top_z = int(pdeck) - 16
        BRUSHES.append(
            box(x1, BRY2, pier_top_z, x2, _pil_out, pdeck, TEX_PILLAR)
        )  # north
        BRUSHES.append(
            box(x1, -_pil_out, pier_top_z, x2, BRY1, pdeck, TEX_PILLAR)
        )  # south

        # Cement cap slab + pyramid on top of each stone pillar post
        _cap_x1, _cap_x2 = px - PIL_PYR_W, px + PIL_PYR_W
        _n_cy1 = BRY2 - PAR_W - PIL_OVERHANG
        _n_cy2 = BRY2 + PIL_OVERHANG
        _s_cy1 = BRY1 - PIL_OVERHANG
        _s_cy2 = BRY1 + PAR_W + PIL_OVERHANG
        # Cap slabs (flat cement base)
        BRUSHES.append(box(_cap_x1, _n_cy1, ppil, _cap_x2, _n_cy2, pcap, TEX_CEMENT))
        BRUSHES.append(box(_cap_x1, _s_cy1, ppil, _cap_x2, _s_cy2, pcap, TEX_CEMENT))
        # Pyramids on top of cap slabs
        BRUSHES.append(
            pyramid(
                _cap_x1, _n_cy1, pcap, _cap_x2, _n_cy2, pcap + PIL_PYR_H, TEX_CEMENT
            )
        )
        BRUSHES.append(
            pyramid(
                _cap_x1, _s_cy1, pcap, _cap_x2, _s_cy2, pcap + PIL_PYR_H, TEX_CEMENT
            )
        )
        # Torch bases above pyramid apex — narrow post + wide cup
        _apex = pcap + PIL_PYR_H
        for _tcy in [cy_n, cy_s]:
            # Narrow stone post (6x6) rising from pyramid tip
            BRUSHES.append(
                box(px - 3, _tcy - 3, _apex, px + 3, _tcy + 3, _apex + 16, TEX_CEMENT)
            )
            # Wider brick cup/bracket at top holds the flame
            BRUSHES.append(
                box(
                    px - 5,
                    _tcy - 5,
                    _apex + 16,
                    px + 5,
                    _tcy + 5,
                    _apex + 20,
                    TEX_BRICK,
                )
            )

        # Abutment pier (westernmost): solid cement fill + arch teleport on west face
        if px == min(PXS):
            # Cement fill starts 16 units east of pier face to make room for arch
            BRUSHES.append(
                box(x1 + 16, -a_rin, FZ2, x2, a_rin, int(pdeck) - 16, TEX_CEMENT)
            )
            # Arch-shaped teleport flush with the west face (recessed into pier)
            _tele_stilt = pier_top_z - FZ2 - a_rin - 8
            _abutment_tele_brush = arch_fill(
                x1 + 2,
                x1 + 18,
                0.0,
                FZ2,
                a_rin,
                A_SEGS,
                TEX_TELEPORT,
                stilt_h=_tele_stilt,
            )
            _abutment_tele_dest_z = int(pdeck) + 40  # spawn height above deck

# ── Teleport Arches at both ends of bridge ───────────────────────────────────
TEX_ARCH_RIN = 96
TEX_ARCH_ROUT = 136  # Fills the bridge width (updated to match BRY2=136)
TEX_ARCH_STILT = 96  # Height of straight sides before arch springs
TEX_ARCH_W = 32  # Thickness of the arch in X

for _ex in [WORLD_X1 + WALL_T, WORLD_X2 - WALL_T - TEX_ARCH_W]:
    _xb, _xf = _ex, _ex + TEX_ARCH_W
    _sprz = DZ2 + TEX_ARCH_STILT  # Z where arch curve begins
    _post_w = TEX_ARCH_ROUT - TEX_ARCH_RIN  # post thickness in Y
    # South post (extends to ground floor, with overhang)
    BRUSHES.append(
        box(_xb, BRY1 - PIL_OVERHANG, FZ2, _xf, BRY1 + _post_w, _sprz, TEX_PILLAR)
    )
    # North post (extends to ground floor, with overhang)
    BRUSHES.append(
        box(_xb, BRY2 - _post_w, FZ2, _xf, BRY2 + PIL_OVERHANG, _sprz, TEX_PILLAR)
    )
    # Arch ring segments (rounded top, with overhang)
    _seg = 180.0 / A_SEGS
    for i in range(A_SEGS):
        BRUSHES.append(
            arch_seg(
                _xb,
                _xf,
                0.0,
                float(_sprz),
                TEX_ARCH_RIN,
                TEX_ARCH_ROUT + PIL_OVERHANG,
                i * _seg,
                (i + 1) * _seg,
                TEX_PILLAR,
            )
        )


# ════════════════════════════════════════════════════════════════════════════════
# WALKWAY — flat bridge from south edge to building 2nd floor entrance
# X=-64..64, Y=BRY1..BLDG_Y2; flat at WALK_ZT1 = WALK_ZT2
# ════════════════════════════════════════════════════════════════════════════════
_wk_zb1 = WALK_ZT1 - BLDG_WALL  # slab bottom at bridge end  = 192
_wk_zb2 = WALK_ZT2 - BLDG_WALL  # slab bottom at building end = 128
BRUSHES.append(
    ramp_slab_y(
        WALK_X1,
        WALK_X2,
        BRY1,
        BLDG_Y2,
        _wk_zb1,
        _wk_zb2,
        WALK_ZT1,
        WALK_ZT2,
        TEX_CEMENT,
        tt=TEX_FLOOR,
    )
)
# Side rails slope with the ramp (32-unit thick walls so tubes sit centred)
_WALK_WALL = 32
BRUSHES.append(
    ramp_slab_y(
        WALK_X1 - _WALK_WALL,
        WALK_X1,
        BRY1,
        BLDG_Y2,
        _wk_zb1,
        _wk_zb2,
        WALK_ZT1 + PAR_H,
        WALK_ZT2 + PAR_H,
        TEX_CEMENT,
    )
)
BRUSHES.append(
    ramp_slab_y(
        WALK_X2,
        WALK_X2 + _WALK_WALL,
        BRY1,
        BLDG_Y2,
        _wk_zb1,
        _wk_zb2,
        WALK_ZT1 + PAR_H,
        WALK_ZT2 + PAR_H,
        TEX_CEMENT,
    )
)
# Handrail tubes along walkway sides, centred in the wall thickness
for _tube_z_extra in [_TUBE_RISE, _TUBE_RISE + _TUBE_GAP]:
    _tbz = WALK_ZT1 + PAR_H + _tube_z_extra
    _ww_cx = _WALK_WALL // 2  # offset from inner face to wall centre
    # West railing (centred in west wall)
    BRUSHES.append(
        box(
            WALK_X1 - _ww_cx - _TUBE_HW,
            BLDG_Y2,
            _tbz,
            WALK_X1 - _ww_cx + _TUBE_HW,
            BRY1,
            _tbz + _TUBE_HW * 2,
            TEX_RAIL,
        )
    )
    # East railing (centred in east wall)
    BRUSHES.append(
        box(
            WALK_X2 + _ww_cx - _TUBE_HW,
            BLDG_Y2,
            _tbz,
            WALK_X2 + _ww_cx + _TUBE_HW,
            BRY1,
            _tbz + _TUBE_HW * 2,
            TEX_RAIL,
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
    BRUSHES.append(
        box(BLDG_X1, BLDG_Y1, FZ2, BLDG_X2, BLDG_Y2, BLDG_GROUND_Z, TEX_GROUND)
    )
    # Sloped ramp on the north face — player can walk up from road to building entrance
    _ramp_y1 = BLDG_Y2  # north face of building
    _ramp_y2 = min(BLDG_Y2 + BLDG_GROUND_Z * 2, BRY1 - 16)  # ramp extent north
    BRUSHES.append(
        ramp_slab_y(
            BLDG_X1,
            BLDG_X2,
            _ramp_y1,
            _ramp_y2,
            FZ2,
            FZ2,
            BLDG_GROUND_Z,
            FZ2,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
    # Long ground ramp from east Charles Street sidewalk up to Knott Hall west wall
    _west_ramp_x1 = ROAD_X2 + _WALK_W  # east edge of east sidewalk = 336
    _west_ramp_x2 = BLDG_X1  # Knott Hall west wall = 1266
    BRUSHES.append(
        ramp_slab(
            _west_ramp_x1,
            _west_ramp_x2,
            BLDG_Y1,
            BLDG_Y2,
            FZ2,
            FZ2,
            FZ2 + _WALK_H,
            BLDG_GROUND_Z,
            TEX_GROUND,
            tt=TEX_GROUND,
        )
    )
_bix1 = BLDG_X1 + BLDG_WALL  # interior west
_bix2 = BLDG_X2 - BLDG_WALL  # interior east
_biy1 = BLDG_Y1 + BLDG_WALL  # interior south = -784
_biy2 = BLDG_Y2 - BLDG_WALL  # interior north = -272

# Entrance doorway — centred on building (BLDG_CX ± 64)
_ENT_X1, _ENT_X2 = BLDG_CX - 64, BLDG_CX + 64  # = 1372, 1500

# ── Entrance staircase ────────────────────────────────────────────────────────
_STEP_N = 10
_STEP_RISE = BLDG_GROUND_Z // _STEP_N  # 8 units per step
_STEP_DEPTH = 16  # 16 units per tread
_STAIR_OFFSET = 384  # distance from north wall to stair base

# Flat cement platform between building and stairs
BRUSHES.append(
    box(
        _ENT_X1,
        BLDG_Y2,
        FZ2,
        _ENT_X2,
        BLDG_Y2 + _STAIR_OFFSET,
        BLDG_GROUND_Z,
        TEX_CEMENT,
    )
)

_STAIR_Y0 = BLDG_Y2 + _STAIR_OFFSET  # south edge of staircase
_STAIR_Y_END = _STAIR_Y0 + _STEP_N * _STEP_DEPTH  # north end of stairs (ground level)
for _si in range(_STEP_N):
    _sz2 = FZ2 + (_si + 1) * _STEP_RISE
    _sy_n = _STAIR_Y0 + (_STEP_N - _si) * _STEP_DEPTH
    BRUSHES.append(
        box(_ENT_X1, _STAIR_Y0, FZ2, _ENT_X2, _sy_n, _sz2, TEX_CEMENT, tt=TEX_CEMENT)
    )

# Small cement apron from stair base to Ennis south sidewalk
_ENNIS_SW_EDGE = _ENNIS_Y - _ENNIS_HW - _WALK_W
BRUSHES.append(
    box(_ENT_X1, _STAIR_Y_END, FZ2, _ENT_X2, _ENNIS_SW_EDGE, FZ2 + _WALK_H, TEX_CEMENT)
)

# Lift shaft east of entrance: 16 units east of _ENT_X2, 128 wide
_stx1, _stx2 = _ENT_X2 + 16, _ENT_X2 + 16 + 128  # = 1516, 1644
_sty1, _sty2 = _biy2 - 128, _biy2  # Y: -400 to -272

# ── Outer walls ──────────────────────────────────────────────────────────────

# South wall — solid back wall
BRUSHES.append(
    box(
        BLDG_X1, BLDG_Y1, BLDG_GROUND_Z, BLDG_X2, BLDG_Y1 + BLDG_WALL, BLDG_Z2, TEX_WALL
    )
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
_win_n = [
    (BLDG_CX + 8, BLDG_GROUND_Z + FLOOR_H * 2, BLDG_CX + 56, BLDG_Z2)
]  # narrow vertical window slot above walkway entrance up to roof
BRUSHES.extend(
    layered_wall(
        BLDG_X1 + INDENT,
        BLDG_Y2 - BLDG_WALL,
        BLDG_GROUND_Z,
        BLDG_X2 - INDENT,
        BLDG_Y2,
        BLDG_Z2,
        _door_n + _door_2 + _win_n,
        TEX_WALL,
    )
)

# NW Indentation inner walls — recessed back wall has a centered 48-unit window
_nw_win_cx = BLDG_X1 + INDENT // 2  # = 1306
_win_half = 24
BRUSHES.extend(
    layered_wall(
        BLDG_X1,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X1 + INDENT,
        BLDG_Y2 - INDENT + BLDG_WALL,
        BLDG_Z2,
        [(_nw_win_cx - _win_half, BLDG_GROUND_Z, _nw_win_cx + _win_half, BLDG_Z2)],
        TEX_WALL,
    )
)
BRUSHES.append(
    box(
        BLDG_X1 + INDENT - BLDG_WALL,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X1 + INDENT,
        BLDG_Y2,
        BLDG_Z2,
        TEX_WALL,
    )
)

# NE Indentation inner walls (mirror of NW) — recessed back wall has a centered 48-unit window
_ne_win_cx = BLDG_X2 - INDENT // 2  # = 1866
BRUSHES.extend(
    layered_wall(
        BLDG_X2 - INDENT,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X2,
        BLDG_Y2 - INDENT + BLDG_WALL,
        BLDG_Z2,
        [(_ne_win_cx - _win_half, BLDG_GROUND_Z, _ne_win_cx + _win_half, BLDG_Z2)],
        TEX_WALL,
    )
)
BRUSHES.append(
    box(
        BLDG_X2 - INDENT,
        BLDG_Y2 - INDENT,
        BLDG_GROUND_Z,
        BLDG_X2 - INDENT + BLDG_WALL,
        BLDG_Y2,
        BLDG_Z2,
        TEX_WALL,
    )
)

# Front mullions — protruding sfloor3_2 posts on each side of the recessed windows
# and the narrow vertical window on the main north face. All protrude 12 units outward.
_fm_div = 12  # mullion width
_fm_pro = 12  # protrusion depth
# NW recessed window: mullions just outside the opening so player can fit through
for _mx in [_nw_win_cx - _win_half - _fm_div, _nw_win_cx + _win_half]:
    BRUSHES.append(
        box(
            _mx,
            BLDG_Y2 - INDENT - _fm_pro,
            BLDG_GROUND_Z,
            _mx + _fm_div,
            BLDG_Y2 - INDENT + BLDG_WALL,
            BLDG_Z2,
            TEX_CEMENT,
        )
    )
# NE recessed window: mullions just outside the opening so player can fit through
for _mx in [_ne_win_cx - _win_half - _fm_div, _ne_win_cx + _win_half]:
    BRUSHES.append(
        box(
            _mx,
            BLDG_Y2 - INDENT - _fm_pro,
            BLDG_GROUND_Z,
            _mx + _fm_div,
            BLDG_Y2 - INDENT + BLDG_WALL,
            BLDG_Z2,
            TEX_CEMENT,
        )
    )
# Main front wall narrow window _win_n: mullions just outside the opening so player can fit through
_win_n_x1, _win_n_x2 = BLDG_CX + 8, BLDG_CX + 56
for _mx in [_win_n_x1 - _fm_div, _win_n_x2]:
    BRUSHES.append(
        box(
            _mx,
            BLDG_Y2 - BLDG_WALL,
            BLDG_GROUND_Z + FLOOR_H * 2,
            _mx + _fm_div,
            BLDG_Y2 + _fm_pro,
            BLDG_Z2,
            TEX_CEMENT,
        )
    )

# ── Brutalist Fins (All Exposed Facades) — currently disabled ─────────────────

# East and West walls — solid, stopping short of NE/NW cutouts
BRUSHES.append(
    box(
        BLDG_X2 - BLDG_WALL,
        BLDG_Y1,
        BLDG_GROUND_Z,
        BLDG_X2,
        BLDG_Y2 - INDENT,
        BLDG_Z2,
        TEX_WALL,
    )
)

# West wall — two 120-unit wide floor-to-ceiling windows, evenly spread
# evenly spread: one at 1/6 and one at 3/6 of wall length
_ww_half = 120
_ww_wall_y1, _ww_wall_y2 = BLDG_Y1, BLDG_Y2 - INDENT
_ww_quarter = (_ww_wall_y2 - _ww_wall_y1) // 4
_ww_c1 = _ww_wall_y1 + _ww_quarter  # 1/4 along wall
_ww_c2 = _ww_wall_y1 + 2 * _ww_quarter  # 2/4 along wall
_ww_c3 = _ww_wall_y1 + 3 * _ww_quarter  # 3/4 along wall
BRUSHES.extend(
    layered_wall_y(
        _ww_wall_y1,
        BLDG_X1,
        BLDG_GROUND_Z,
        _ww_wall_y2,
        BLDG_X1 + BLDG_WALL,
        BLDG_Z2,
        [
            (_ww_c1 - _ww_half, BLDG_GROUND_Z, _ww_c1 + _ww_half, BLDG_Z2),
            (_ww_c2 - _ww_half, BLDG_GROUND_Z, _ww_c2 + _ww_half, BLDG_Z2),
            (_ww_c3 - _ww_half, BLDG_GROUND_Z, _ww_c3 + _ww_half, BLDG_Z2),
        ],
        TEX_WALL,
    )
)
# Vertical mullions — protrude 12 units west of wall face
# 2 interior + 2 side mullions per window (4 total each)
_ww_div_w = 12
_ww_protrude = 12  # how far they stick out past the wall face
for _wc in [_ww_c1, _ww_c2, _ww_c3]:
    for _dy in [
        _wc - _ww_half,  # left edge
        _wc - 48,  # interior left
        _wc + 36,  # interior right
        _wc + _ww_half - _ww_div_w,  # right edge
    ]:
        BRUSHES.append(
            box(
                BLDG_X1 - _ww_protrude,
                _dy,
                BLDG_GROUND_Z,
                BLDG_X1 + BLDG_WALL,
                _dy + _ww_div_w,
                BLDG_Z2,
                TEX_CEMENT,
            )
        )

# Roof — open above lift shaft, clipped for NW indentation
BRUSHES.append(
    box(
        BLDG_X1,
        BLDG_Y1,
        BLDG_Z2,
        _stx1,
        BLDG_Y2 - INDENT,
        BLDG_Z2 + BLDG_WALL,
        TEX_FLOOR_BLDG,
    )
)  # west bulk
BRUSHES.append(
    box(
        BLDG_X1 + INDENT,
        BLDG_Y2 - INDENT,
        BLDG_Z2,
        _stx1,
        BLDG_Y2,
        BLDG_Z2 + BLDG_WALL,
        TEX_FLOOR_BLDG,
    )
)  # west north-strip
BRUSHES.append(
    box(
        _stx2,
        BLDG_Y1,
        BLDG_Z2,
        BLDG_X2,
        BLDG_Y2 - INDENT,
        BLDG_Z2 + BLDG_WALL,
        TEX_FLOOR_BLDG,
    )
)  # east bulk
BRUSHES.append(
    box(
        _stx2,
        BLDG_Y2 - INDENT,
        BLDG_Z2,
        BLDG_X2 - INDENT,
        BLDG_Y2,
        BLDG_Z2 + BLDG_WALL,
        TEX_FLOOR_BLDG,
    )
)  # east north-strip (NE cutout)
BRUSHES.append(
    box(_stx1, BLDG_Y1, BLDG_Z2, _stx2, _sty1, BLDG_Z2 + BLDG_WALL, TEX_FLOOR_BLDG)
)  # south of shaft
BRUSHES.append(
    box(_stx1, _sty2, BLDG_Z2, _stx2, BLDG_Y2, BLDG_Z2 + BLDG_WALL, TEX_FLOOR_BLDG)
)  # north of shaft (closes roof over north wall above shaft)

# ── Interior floor slabs (floors 0-3, lift shaft opening in center-north) ────
# Floor 0 (ground): full slab with no shaft opening, clipped for NW indentation
_sz0 = BLDG_GROUND_Z
_st0 = _sz0 + BLDG_WALL
BRUSHES.append(
    box(BLDG_X1, BLDG_Y1, _sz0, BLDG_X2, BLDG_Y2 - INDENT, _st0, TEX_FLOOR_BLDG)
)
BRUSHES.append(
    box(
        BLDG_X1 + INDENT,
        BLDG_Y2 - INDENT,
        _sz0,
        BLDG_X2 - INDENT,
        BLDG_Y2,
        _st0,
        TEX_FLOOR_BLDG,
    )
)

for _f in range(1, BLDG_FLOORS):
    _sz = BLDG_GROUND_Z + _f * FLOOR_H
    _st = _sz + BLDG_WALL
    # South bulk
    BRUSHES.append(box(_bix1, _biy1, _sz, _bix2, _sty1, _st, TEX_FLOOR_BLDG))
    # West of shaft, clipped for NW indentation
    BRUSHES.append(box(_bix1, _sty1, _sz, _stx1, BLDG_Y2 - INDENT, _st, TEX_FLOOR_BLDG))
    BRUSHES.append(
        box(_bix1 + INDENT, BLDG_Y2 - INDENT, _sz, _stx1, _biy2, _st, TEX_FLOOR_BLDG)
    )
    # East of shaft, clipped for NE indentation
    BRUSHES.append(box(_stx2, _sty1, _sz, _bix2, BLDG_Y2 - INDENT, _st, TEX_FLOOR_BLDG))
    BRUSHES.append(
        box(_stx2, BLDG_Y2 - INDENT, _sz, _bix2 - INDENT, _biy2, _st, TEX_FLOOR_BLDG)
    )

# ── Elevator Shaft Enclosure ──────────────────────────────────────────────
# Walls around the lift shaft (_stx1.._stx2, _sty1.._sty2)
_shaft_wall = 8
# Door opening dimensions per floor (used for both wall openings and func_door entities)
_shaft_door_h = 96  # door height
_shaft_doors_w = [
    (
        _sty1 + 16,
        BLDG_GROUND_Z + _f * FLOOR_H,
        _sty2 - 16,
        BLDG_GROUND_Z + _f * FLOOR_H + _shaft_door_h,
    )
    for _f in range(BLDG_FLOORS)
]

# Shaft North wall (internal, solid)
BRUSHES.append(
    box(_stx1, _sty2, BLDG_GROUND_Z, _stx2, _sty2 + _shaft_wall, BLDG_Z2, TEX_WALL)
)
# Shaft South wall (internal, solid)
BRUSHES.append(
    box(_stx1, _sty1 - _shaft_wall, BLDG_GROUND_Z, _stx2, _sty1, BLDG_Z2, TEX_WALL)
)
# Shaft West wall (internal, openings for each floor's door)
BRUSHES.extend(
    layered_wall_y(
        _sty1,
        _stx1 - _shaft_wall,
        BLDG_GROUND_Z,
        _sty2,
        _stx1,
        BLDG_Z2,
        _shaft_doors_w,
        TEX_WALL,
    )
)
# Shaft East wall (internal)
BRUSHES.append(
    box(_stx2, _sty1, BLDG_GROUND_Z, _stx2 + _shaft_wall, _sty2, BLDG_Z2, TEX_WALL)
)

# ── Knott Hall hallway + rooms — 2 rooms per side per floor ──────────────────
# Partition Y splits vary per floor so each floor has different room proportions.
_room_splits = [-1072, -950, -1200, -850, -1300]  # partition Y per floor

_wx1, _wx2 = _bix1, _ENT_X1 - BLDG_WALL  # west room X extents (1282..1506)
_ex1, _ex2 = _ENT_X2 + BLDG_WALL, _bix2  # east room X extents (1666..1890)
_wxc = (_wx1 + _wx2) // 2  # west room X center = 1394
_exc = (_ex1 + _ex2) // 2  # east room X center = 1778

# Collect door openings in hallway walls across all floors
_w_hall_openings = []
_e_hall_openings = [(_sty1, BLDG_GROUND_Z, _sty2, BLDG_Z2)]  # shaft gap always open

for _fl in range(BLDG_FLOORS):
    _fz1 = BLDG_GROUND_Z + _fl * FLOOR_H
    _fz_surf = _fz1 + BLDG_WALL  # top of floor slab
    _split = _room_splits[_fl]
    _sr_yc = (_biy1 + _split) // 2  # south room Y center
    _nr_yc = (_split + BLDG_WALL + _biy2) // 2  # north room Y center
    _dz2 = _fz_surf + 96  # door top
    _w_hall_openings += [
        (_sr_yc - 32, _fz_surf, _sr_yc + 32, _dz2),
        (_nr_yc - 32, _fz_surf, _nr_yc + 32, _dz2),
    ]
    _e_hall_openings += [
        (_sr_yc - 32, _fz_surf, _sr_yc + 32, _dz2),
        (_nr_yc - 32, _fz_surf, _nr_yc + 32, _dz2),
    ]

# West hallway wall with room door openings
BRUSHES.extend(
    layered_wall_y(
        _biy1,
        _ENT_X1 - BLDG_WALL,
        BLDG_GROUND_Z,
        _biy2,
        _ENT_X1,
        BLDG_Z2,
        _w_hall_openings,
        TEX_WALL,
    )
)
# East hallway wall with room door openings + shaft opening
BRUSHES.extend(
    layered_wall_y(
        _biy1,
        _ENT_X2,
        BLDG_GROUND_Z,
        _biy2,
        _ENT_X2 + BLDG_WALL,
        BLDG_Z2,
        _e_hall_openings,
        TEX_WALL,
    )
)

# Partition walls per floor (divide each side into 2 rooms, with connecting door)
for _fl in range(BLDG_FLOORS):
    _fz1 = BLDG_GROUND_Z + _fl * FLOOR_H
    _fz2 = _fz1 + FLOOR_H
    _fz_surf = _fz1 + BLDG_WALL
    _split = _room_splits[_fl]
    _sp_y2 = _split + BLDG_WALL
    _pdz2 = _fz_surf + 96
    # West side partition wall with connecting door
    BRUSHES.extend(
        layered_wall(
            _wx1,
            _split,
            _fz1,
            _wx2,
            _sp_y2,
            _fz2,
            [(_wxc - 32, _fz_surf, _wxc + 32, _pdz2)],
            TEX_WALL,
        )
    )
    # East side partition wall with connecting door
    BRUSHES.extend(
        layered_wall(
            _ex1,
            _split,
            _fz1,
            _ex2,
            _sp_y2,
            _fz2,
            [(_exc - 32, _fz_surf, _exc + 32, _pdz2)],
            TEX_WALL,
        )
    )

DRAW_FASCIA_TEXT = True  # Set True to re-enable (slow to compile)

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

# No separate background fascia boxes — parapet wall face is the backdrop

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
        z_top = int(dtop(x_mid)) + PAR_H - 14  # centred in parapet height
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
            y_face=BRY1,
            px_w=_PX_W,
            px_h=_PX_H,
            depth=1,
            tex=TEX_RAIL,
        )
        + _render_text_fascia(
            _TEXT[::-1],
            x0=_TEXT_X0,
            y_face=BRY2 + 1,
            px_w=_PX_W,
            px_h=_PX_H,
            depth=1,
            tex=TEX_RAIL,
            mirror=True,
        )
    )
    if DRAW_FASCIA_TEXT
    else []
)

# ── Campus lamp posts (brush geometry) — along Charles Street (N-S) ──────────
_LAMP_POST_H = DZ2 - 32  # pole height (~12 ft)
# Single lamp post — east sidewalk, at the SE corner of the Ennis Road intersection
_LAMP_POST_XS = [1890, 1246]  # east sidewalk near Ennis, and next pier west
_lamp_post_ys = [_ENNIS_Y - _ENNIS_HW - 160]
for _lx in _LAMP_POST_XS:
    for _ly in _lamp_post_ys:
        _pole_top = FZ2 + _LAMP_POST_H
        # Narrow shaft
        BRUSHES.append(
            box(_lx - 2, _ly - 2, FZ2, _lx + 2, _ly + 2, _pole_top, TEX_PILLAR)
        )
        # Torch top — narrow post + brick cup (matches bridge pillar torches)
        BRUSHES.append(
            box(
                _lx - 3,
                _ly - 3,
                _pole_top,
                _lx + 3,
                _ly + 3,
                _pole_top + 16,
                TEX_CEMENT,
            )
        )
        BRUSHES.append(
            box(
                _lx - 5,
                _ly - 5,
                _pole_top + 16,
                _lx + 5,
                _ly + 5,
                _pole_top + 20,
                TEX_BRICK,
            )
        )

# ── Under-bridge pendant lights — one per span, no brush geometry ─────────────
_SPAN_CENTRES = [
    (BRX1 + PXS[0]) // 2,
    (PXS[0] + PXS[1]) // 2,
    (PXS[1] + PXS[2]) // 2,
    (PXS[2] + BRX2) // 2,
    (BRX2 + PXS[4]) // 2,
    (PXS[4] + WORLD_X2 - WALL_T) // 2,
]
_PEND_XS = _SPAN_CENTRES

# ── N/S arch stone wall panels (must be added to B before worldspawn assembly) ──
_NS_ARCH_RIN_PRE = 256  # inner radius = road half-width
_NS_ARCH_ROUT_PRE = 312  # outer radius
_NS_ARCH_STILT_PRE = 96  # stilt height
_NS_ARCH_W_PRE = 48  # arch thickness in Y
_NS_WALL_W_PRE = 320  # stone wall width flanking road
_NS_ARCH_TOP_PRE = FZ2 + _NS_ARCH_STILT_PRE + _NS_ARCH_RIN_PRE  # = 352

for _pre_syb, _pre_syf in [
    (_ROAD_Y1, _ROAD_Y1 + _NS_ARCH_W_PRE),
    (_ROAD_Y2 - _NS_ARCH_W_PRE, _ROAD_Y2),
]:
    # Stone arch posts + ring
    BRUSHES.extend(
        arch_wall_y(
            _pre_syb,
            _pre_syf,
            WORLD_X1 + WALL_T,
            WORLD_X2 - WALL_T,
            FZ2,
            _NS_ARCH_TOP_PRE,
            _NS_ARCH_RIN_PRE,
            _NS_ARCH_ROUT_PRE,
            A_SEGS,
            TEX_STONE,
            stilt_h=_NS_ARCH_STILT_PRE,
        )
    )

# ── Worldspawn ────────────────────────────────────────────────────────────────
worldspawn = (
    "{\n"
    '"classname" "worldspawn"\n'
    '"wad" "quake101.wad;ad.wad"\n'
    '"message" "Loyola Bridge & Knott Hall"\n'
    f'"sky" "{TEX_SKY}"\n'
    '"ambient" "60"\n'
    '"_sunlight" "220"\n'
    '"_sunlight_color" "255 245 210"\n'
    '"_sunlight_dir" "60 -60"\n'
    '"_sunlight_penumbra" "8"\n'
    '"dmflags" "128"\n'
    '"_fog" "0.03 0.5 0.5 0.6"\n' + "\n".join(BRUSHES) + "\n}"
)

# ── Entities ──────────────────────────────────────────────────────────────────
ENTITIES = []
# Letter brushes as func_detail — don't split vis BSP tree, keeps compile fast
if _letter_brushes:
    ENTITIES.append(brush_ent("func_detail", _letter_brushes))
DECK_Z = dtop(0) + 8  # centre of arch deck + a bit (spawn/item height)
ROAD_Z = FZ2 + 8

# ── Knott Hall hallway floor-up teleports ─────────────────────────────────────
# One teleport pad at the south dead-end of the hallway per floor.
# Floors 0-3 go up one floor; floor 4 loops back to ground.
_tele_hx1, _tele_hx2 = _ENT_X1, _ENT_X2  # hallway X
_tele_hy1, _tele_hy2 = _biy1, _biy1 + 48  # south trigger zone
_tele_hxc = (_tele_hx1 + _tele_hx2) // 2  # hallway X center
_tele_dest_y = _biy1 + 72  # just north of trigger zone

for _fl in range(BLDG_FLOORS):
    _fz1 = BLDG_GROUND_Z + _fl * FLOOR_H
    _fz_surf = _fz1 + BLDG_WALL
    _dest_fl = (_fl + 1) % BLDG_FLOORS
    _dest_fz1 = BLDG_GROUND_Z + _dest_fl * FLOOR_H
    _dest_surf = _dest_fz1 + BLDG_WALL  # top of destination floor slab
    _dest_z = _dest_fz1 + FLOOR_H // 2  # mid-floor height, well above slab
    _dest_y = _tele_dest_y
    if _fl == BLDG_FLOORS - 1:  # top floor → roof
        _dest_z = BLDG_Z2 + 40
        _dest_y = (_biy1 + _biy2) // 2
    _tname = f"knott_up_{_fl}"
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname=_tname,
            origin=f"{_tele_hxc} {_dest_y} {_dest_z}",
            angle="90",
        )
    )
    # Trigger pad — full floor height so it's easy to walk into
    _trig = box(
        _tele_hx1,
        _tele_hy1,
        _fz_surf,
        _tele_hx2,
        _tele_hy2,
        _fz1 + FLOOR_H,
        TEX_TELEPORT,
    )
    ENTITIES.append(brush_ent("trigger_teleport", [_trig], target=_tname))
    # Matching illusionary so the teleport texture is visible
    ENTITIES.append(brush_ent("func_illusionary", [_trig]))
    # Flickering light to mark the pad
    ENTITIES.append(
        ent(
            "light",
            origin=f"{_tele_hxc} {(_tele_hy1 + _tele_hy2) // 2} {_fz_surf + 64}",
            light="200",
            style="1",
        )
    )

# ── Knott Hall room goodies — 2 items per room, varied per floor ──────────────
_room_goodies = [
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
_gi = 0
for _fl in range(BLDG_FLOORS):
    _fz1 = BLDG_GROUND_Z + _fl * FLOOR_H
    _item_z = _fz1 + BLDG_WALL + 24
    _light_z = _fz1 + FLOOR_H - 24  # near ceiling
    _split = _room_splits[_fl]
    _sr_yc = (_biy1 + _split) // 2
    _nr_yc = (_split + BLDG_WALL + _biy2) // 2
    for _side_xc in [_wxc, _exc]:
        for _ryc in [_sr_yc, _nr_yc]:
            ENTITIES.append(
                ent("light", origin=f"{_side_xc} {_ryc} {_light_z}", light="250")
            )
            ENTITIES.append(
                ent(
                    _room_goodies[_gi % len(_room_goodies)],
                    origin=f"{_side_xc - 40} {_ryc} {_item_z}",
                )
            )
            _gi += 1
            ENTITIES.append(
                ent(
                    _room_goodies[_gi % len(_room_goodies)],
                    origin=f"{_side_xc + 40} {_ryc} {_item_z}",
                )
            )
            _gi += 1

# ── Knott Hall bookshelves — scattered through rooms ─────────────────────────
_SHELF_H = 64  # height of shelf stack
_SHELF_D = 16  # depth (one wall-thickness)
_SHELF_W = 64  # width

_shelf_offsets = [0, 0, 0, 0, 0]

for _fl in range(BLDG_FLOORS):
    _fz1 = BLDG_GROUND_Z + _fl * FLOOR_H
    _fz_surf = _fz1 + BLDG_WALL
    _split = _room_splits[_fl]
    _stex = "shelf_1"
    _xoff = _shelf_offsets[_fl]

    for _sxc in [_wxc, _exc]:
        # South room: shelf against south wall — front faces south (-Y)
        _sp = _sxc + _xoff
        ENTITIES.append(
            brush_ent(
                "func_wall",
                [
                    box(
                        _sp - _SHELF_W // 2,
                        _biy1,
                        _fz_surf,
                        _sp + _SHELF_W // 2,
                        _biy1 + _SHELF_D,
                        _fz_surf + _SHELF_H,
                        "shelf_1",
                    )
                ],
            )
        )
        ENTITIES.append(
            ent(
                "light",
                origin=f"{_sp} {_biy1 + 32} {_fz_surf + _SHELF_H + 24}",
                light="180",
            )
        )
        # North room: shelf against north wall — front faces north (+Y)
        _np = _sxc - _xoff
        _n_in_shaft = (
            _np + _SHELF_W // 2 > _stx1
            and _np - _SHELF_W // 2 < _stx2
            and _biy2 > _sty1
            and _biy2 - _SHELF_D < _sty2
        )
        if not _n_in_shaft:
            ENTITIES.append(
                brush_ent(
                    "func_wall",
                    [
                        box(
                            _np - _SHELF_W // 2,
                            _biy2 - _SHELF_D,
                            _fz_surf,
                            _np + _SHELF_W // 2,
                            _biy2,
                            _fz_surf + _SHELF_H,
                            "shelf_1",
                        )
                    ],
                )
            )
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{_np} {_biy2 - 32} {_fz_surf + _SHELF_H + 24}",
                    light="180",
                )
            )


ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_abutment_deck",
        origin=f"{min(PXS)} 0 {_abutment_tele_dest_z}",
        angle="0",
    )
)
ENTITIES.append(
    brush_ent("trigger_teleport", _abutment_tele_brush, target="dest_abutment_deck")
)
ENTITIES.append(brush_ent("func_illusionary", _abutment_tele_brush))

# Teleport destinations — west arch ↔ east arch
ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_east",
        origin=f"{(_AB_X1 + _AB_X2) // 2} {(_NB_Y1 + _NB_Y2) // 2} {int(_nb_ridge_z + 40)}",
        angle="270",  # facing south toward the bridge
    )
)
ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_west",
        origin=f"{BLDG_CX} {(BLDG_Y1 + BLDG_Y2) // 2} {int(BLDG_Z2 + 40)}",
        angle="180",  # facing south, on Knott Hall rooftop
    )
)

# West arch trigger → east destination
west_brushes = arch_fill(
    WORLD_X1 + WALL_T,
    WORLD_X1 + WALL_T + TEX_ARCH_W,
    0.0,
    DZ2,
    TEX_ARCH_RIN,
    A_SEGS,
    TEX_TELEPORT,
    stilt_h=TEX_ARCH_STILT,
)
ENTITIES.append(brush_ent("trigger_teleport", west_brushes, target="dest_east"))
ENTITIES.append(brush_ent("func_illusionary", west_brushes))

# West lower trigger (ground floor — simple box between posts)
_wlx1 = WORLD_X1 + WALL_T
_wlx2 = _wlx1 + TEX_ARCH_W
west_lower = [box(_wlx1, -TEX_ARCH_RIN, FZ2, _wlx2, TEX_ARCH_RIN, DZ2, TEX_TELEPORT)]
ENTITIES.append(brush_ent("trigger_teleport", west_lower, target="dest_east"))
ENTITIES.append(brush_ent("func_illusionary", west_lower))

# East arch trigger → west destination
east_brushes = arch_fill(
    WORLD_X2 - WALL_T - TEX_ARCH_W,
    WORLD_X2 - WALL_T,
    0.0,
    DZ2,
    TEX_ARCH_RIN,
    A_SEGS,
    TEX_TELEPORT,
    stilt_h=TEX_ARCH_STILT,
)
ENTITIES.append(brush_ent("trigger_teleport", east_brushes, target="dest_west"))
ENTITIES.append(brush_ent("func_illusionary", east_brushes))

# East lower trigger (ground floor — teleports up to bridge deck above)
_elx1 = WORLD_X2 - WALL_T - TEX_ARCH_W
_elx2 = WORLD_X2 - WALL_T
_east_lower_deck_x = _elx1 - 64  # west of the arch, on the flat deck approach
ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_east_deck",
        origin=f"{_east_lower_deck_x} 0 {int(DZ2 + 40)}",
        angle="180",
    )
)
east_lower = [box(_elx1, -TEX_ARCH_RIN, FZ2, _elx2, TEX_ARCH_RIN, DZ2, TEX_TELEPORT)]
ENTITIES.append(brush_ent("trigger_teleport", east_lower, target="dest_east_deck"))
ENTITIES.append(brush_ent("func_illusionary", east_lower))

# ── North & South Charles Street arch teleports → bridge deck centre ─────────
_NS_ARCH_RIN = 256  # inner radius = road half-width
_NS_ARCH_ROUT = 312  # outer radius (post thickness = 56, more substantial)
_NS_ARCH_STILT = 96  # straight post height before arch springs
_NS_ARCH_W = 48  # arch thickness in Y (thicker = more stone-like)

ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_bridge_mid",
        origin=f"0 0 {int(dtop(0) + 56)}",
        angle="0",
    )
)

_NS_TRIG_INSET = 8  # push trigger away from world walls and road surface
_NS_WALL_W = 320  # stone wall extends this far out from road edge on each side

for _syb, _syf, _trig_y1, _trig_y2 in [
    (
        _ROAD_Y1,
        _ROAD_Y1 + _NS_ARCH_W,
        _ROAD_Y1 + _NS_TRIG_INSET,
        _ROAD_Y1 + _NS_ARCH_W,
    ),  # south arch — trigger inset from south wall
    (
        _ROAD_Y2 - _NS_ARCH_W,
        _ROAD_Y2,
        _ROAD_Y2 - _NS_ARCH_W,
        _ROAD_Y2 - _NS_TRIG_INSET,
    ),  # north arch — trigger inset from north wall
]:
    _arch_top = FZ2 + _NS_ARCH_STILT + _NS_ARCH_RIN
    # Box trigger — reliable activation, inset from walls
    _ns_trig = [
        box(
            ROAD_X1 + _NS_TRIG_INSET,
            _trig_y1,
            FZ2 + 4,
            ROAD_X2 - _NS_TRIG_INSET,
            _trig_y2,
            _arch_top,
            TEX_TELEPORT,
        )
    ]
    ENTITIES.append(brush_ent("trigger_teleport", _ns_trig, target="dest_bridge_mid"))
    # Arch-shaped illusionary fill so the teleport glow looks like an arch
    _ns_glow = arch_fill_y(
        _syb,
        _syf,
        0.0,
        FZ2 + 4,
        _NS_ARCH_RIN,
        A_SEGS,
        TEX_TELEPORT,
        stilt_h=_NS_ARCH_STILT,
    )
    ENTITIES.append(brush_ent("func_illusionary", _ns_glow))


ENTITIES.append(
    ent(
        "info_player_start",
        origin=f"{BLDG_CX} {BRY1 + PAR_W + 32} {int(DZ2 + 24)}",
        angle="180",
    )
)

_bcy = (BLDG_Y1 + BLDG_Y2) // 2  # Knott Hall center Y = -528
_nb_cy_dm = (_NB_Y1 + _NB_Y2) // 2  # north building center Y
_nb_cx_dm = (_AB_X1 + _AB_X2) // 2  # west buildings center X
_sb1_cy = (_SB_Y1 + _SB_Y2) // 2  # south building 1 center Y
_sb2_cy = (_SB2_Y1 + _SB2_Y2) // 2  # south building 2 center Y

# ── Deathmatch spawns — spread across all areas ──────────────────────────
for pos, angle in [
    # Bridge deck
    ((0, 0, int(dtop(0) + 32)), 180),
    ((-200, 0, int(dtop(-200) + 32)), 90),
    ((200, 0, int(dtop(200) + 32)), 270),
    ((-400, 0, int(dtop(-400) + 32)), 90),
    ((400, 0, int(dtop(400) + 32)), 270),
    # Walkway
    ((BLDG_CX, (BRY1 + BLDG_Y2) // 2, int(WALK_ZT1 + 32)), 180),
    # Knott Hall — ground, mid, upper floors
    ((BLDG_CX, BLDG_Y2 - 80, BLDG_GROUND_Z + 40), 180),
    ((BLDG_CX - 100, _bcy, BLDG_GROUND_Z + FLOOR_H + 40), 270),
    ((BLDG_CX + 100, _bcy, BLDG_GROUND_Z + FLOOR_H * 2 + 40), 90),
    ((BLDG_CX, BLDG_Y1 + 100, BLDG_GROUND_Z + FLOOR_H * 3 + 40), 0),
    ((BLDG_CX, _bcy, BLDG_GROUND_Z + FLOOR_H * 4 + 40), 180),
    # Knott Hall rooftop
    ((BLDG_CX, _bcy, BLDG_Z2 + 40), 180),
    # Charles Street
    ((0, 300, ROAD_Z + 24), 180),
    ((0, -400, ROAD_Z + 24), 0),
    ((0, _sb1_cy, ROAD_Z + 24), 270),
    # North building interior
    ((_nb_cx_dm, _nb_cy_dm, FZ2 + 40), 90),
    ((_nb_cx_dm, _nb_cy_dm, FZ2 + FLOOR_H + 40), 90),
    # North building roof ridge
    ((_nb_cx_dm, _nb_cy_dm, int(_nb_ridge_z + 40)), 90),
    # South buildings interiors
    ((_nb_cx_dm, _sb1_cy, FZ2 + 40), 90),
    ((_nb_cx_dm, _sb2_cy, FZ2 + 40), 90),
    # Ground east/west of bridge
    ((800, 0, ROAD_Z + 24), 270),
    ((-800, 0, ROAD_Z + 24), 90),
]:
    ENTITIES.append(
        ent(
            "info_player_deathmatch",
            origin=f"{pos[0]} {pos[1]} {pos[2]}",
            angle=str(angle),
        )
    )

# ── Weapons ───────────────────────────────────────────────────────────────
# Rocket launcher — bridge centre (high value, exposed position)
ENTITIES.append(ent("weapon_rocketlauncher", origin=f"0 0 {DECK_Z}"))
# Rocket launcher — Knott Hall floor 3 (reward for climbing)
ENTITIES.append(
    ent(
        "weapon_rocketlauncher",
        origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H * 3 + 40}",
    )
)

# Super shotgun — spread around mid-tier locations
ENTITIES.append(
    ent("weapon_supershotgun", origin=f"{BLDG_CX} {BLDG_Y2 - 80} {BLDG_GROUND_Z + 40}")
)
ENTITIES.append(ent("weapon_supershotgun", origin=f"0 300 {ROAD_Z + 24}"))
ENTITIES.append(ent("weapon_supershotgun", origin=f"{_nb_cx_dm} {_sb1_cy} {FZ2 + 40}"))

# Grenade launcher — Knott Hall floor 2, south building 2
ENTITIES.append(
    ent(
        "weapon_grenadelauncher",
        origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H * 2 + 40}",
    )
)
ENTITIES.append(
    ent("weapon_grenadelauncher", origin=f"{_nb_cx_dm} {_sb2_cy} {FZ2 + 40}")
)

# Nailgun — bridge approaches, Charles Street
ENTITIES.append(ent("weapon_nailgun", origin=f"-600 0 {ROAD_Z + 24}"))
ENTITIES.append(ent("weapon_nailgun", origin=f"600 0 {ROAD_Z + 24}"))
ENTITIES.append(
    ent("weapon_nailgun", origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H + 40}")
)

# ── Ammo ──────────────────────────────────────────────────────────────────
for ax in PXS:
    ENTITIES.append(ent("item_rockets", origin=f"{ax} 0 {int(dtop(ax) + 8)}"))
for rx in [400, 800]:
    ENTITIES.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z + 24}"))
for _kf in range(1, BLDG_FLOORS):
    ENTITIES.append(
        ent(
            "item_rockets",
            origin=f"{BLDG_CX + 80} {_bcy} {BLDG_GROUND_Z + _kf * FLOOR_H + 40}",
        )
    )
ENTITIES.append(ent("item_shells", origin=f"0 -300 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_shells", origin=f"{_nb_cx_dm} {_nb_cy_dm} {FZ2 + 40}"))
ENTITIES.append(ent("item_spikes", origin=f"-400 200 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_spikes", origin=f"400 -200 {ROAD_Z + 24}"))

# ── Health & Armor ────────────────────────────────────────────────────────
# Health — scattered throughout
ENTITIES.append(ent("item_health", origin=f"0 0 {DECK_Z}"))
ENTITIES.append(
    ent("item_health", origin=f"{BLDG_CX} {BLDG_Y2 - 64} {BLDG_GROUND_Z + 40}")
)
ENTITIES.append(
    ent("item_health", origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H * 2 + 40}")
)
ENTITIES.append(ent("item_health", origin=f"0 400 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_health", origin=f"0 -600 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_health", origin=f"{_nb_cx_dm} {_sb2_cy} {FZ2 + 40}"))
# Armor — contested locations
ENTITIES.append(ent("item_armor1", origin=f"-200 0 {DECK_Z}"))  # yellow armor on bridge
ENTITIES.append(
    ent("item_armor2", origin=f"{BLDG_CX} {_bcy} {BLDG_GROUND_Z + FLOOR_H * 4 + 40}")
)  # red armor top floor
ENTITIES.append(
    ent("item_armorInv", origin=f"{_nb_cx_dm} {_nb_cy_dm} {int(_nb_ridge_z + 40)}")
)  # mega armor on roof ridge (teleport reward)

# Torch lights on pillar caps
if SHOW_SUPPORTS:
    for px in PXS:
        if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
            continue
        pbase = dtop(px)
        pcap = pbase + PAR_H + PIL_EXTRA + PIL_CAP_H + PIL_PYR_H  # top of pyramid
        cy_n = BRY2 - PAR_W // 2  # centred on north pillar cap
        cy_s = BRY1 + PAR_W // 2  # centred on south pillar cap
        # Flames on pillar tops — raised above pyramid apex so they visually sit on top
        ENTITIES.append(
            ent("light_flame_large_yellow", origin=f"{px} {cy_n} {int(pcap + 24)}")
        )
        ENTITIES.append(
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
                TEX_SKY,
            )
            ENTITIES.append(brush_ent("trigger_hurt", [_fhb], dmg="10"))

# Pillar base uplights — ground-level spots wash light up the pier faces
if SHOW_SUPPORTS:
    for px in PXS:
        if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
            continue
        for _uy in [BRY2 + 30, BRY1 - 30]:
            ENTITIES.append(ent("light", origin=f"{px} {_uy} 16", light="200"))

# Campus lamp post lights — flame above brick cup, matching bridge pillar torches
for _lx in _LAMP_POST_XS:
    for _ly in _lamp_post_ys:
        _pole_top = FZ2 + _LAMP_POST_H
        _flame_z = _pole_top + 20
        ENTITIES.append(ent("light", origin=f"{_lx} {_ly} {_flame_z}", light="300"))
        ENTITIES.append(
            ent("light_flame_large_yellow", origin=f"{_lx} {_ly} {_flame_z + 4}")
        )

# Ennis entrance pillar torches — flame above brick cup on each stone pillar
_epl_flame_z = _EPL_ZB + _EPL_POST_H + _EPL_CAP_H + _EPL_BELL2_H + 20
_epl_cx = _EPL_X1 + _EPL_HW
for _epy in (_ENNIS_Y - _ENNIS_HW - _EPL_HW, _ENNIS_Y + _ENNIS_HW + _EPL_HW):
    ENTITIES.append(
        ent("light", origin=f"{_epl_cx} {_epy} {_epl_flame_z}", light="300")
    )
    ENTITIES.append(
        ent("light_flame_large_yellow", origin=f"{_epl_cx} {_epy} {_epl_flame_z + 4}")
    )

# Under-bridge amber pendant lights — flicker style, hang below deck
for _px in _PEND_XS:
    ENTITIES.append(
        ent("light", origin=f"{_px} 0 {int(dbot(_px)) - 20}", light="200", style="1")
    )

# Light on underside of walkway slab illuminating the ramp below
_walk_mid_y = (BRY1 + BLDG_Y2) // 2
_walk_frac = (BRY1 - _walk_mid_y) / float(BRY1 - BLDG_Y2)
_walk_bot_mid = int(_wk_zb1 + _walk_frac * (_wk_zb2 - _wk_zb1))
ENTITIES.append(
    ent("light", origin=f"{BLDG_CX} {_walk_mid_y} {_walk_bot_mid - 8}", light="300")
)

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
        TEX_FLOOR_BLDG,
    )
]
ENTITIES.append(
    brush_ent("func_plat", _lift_brush, height=str(_lift_travel), speed="200")
)

# Interior lights for the three campus buildings (north + 2 south)
_bldg_light_x = (_AB_X1 + _AB_X2) // 2
for _bly1, _bly2 in [(_NB_Y1, _NB_Y2), (_SB_Y1, _SB_Y2), (_SB2_Y1, _SB2_Y2)]:
    _bly = (_bly1 + _bly2) // 2
    for _bfl in range(_AB_FLOORS):
        _blz = FZ2 + _bfl * FLOOR_H + FLOOR_H // 2
        ENTITIES.append(
            ent("light", origin=f"{_bldg_light_x} {_bly} {_blz}", light="200")
        )

# Interior lights for Knott Hall — 3×4 grid per floor
for _kfl in range(BLDG_FLOORS):
    _klz = BLDG_GROUND_Z + _kfl * FLOOR_H + FLOOR_H // 2
    for _kxi in [1, 2, 3]:
        _klx = BLDG_X1 + (BLDG_X2 - BLDG_X1) * _kxi // 4
        for _kyi in [1, 2, 3, 4]:
            _kly = BLDG_Y1 + (BLDG_Y2 - BLDG_Y1) * _kyi // 5
            ENTITIES.append(ent("light", origin=f"{_klx} {_kly} {_klz}", light="150"))

# ── Write ─────────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(ENTITIES) + "\n"
with open("loyola.map", "w") as fh:
    fh.write(map_text)
print(
    f"loyola.map written — {len(BRUSHES)} worldspawn brushes, {len(ENTITIES)} entities"
)
