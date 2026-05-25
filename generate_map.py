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

# ── Textures ──────────────────────────────────────────────────────────────────
T_STONE = "city6_7"  # supporting pillars + arch ring
T_FLOOR = "afloor1_4"  # deck top surface
T_CEMENT = "wbrick1_5"  # parapet / bridge walls (cement look)
T_WALL = "bricka2_1"  # building walls
T_METAL = "metal5_4"  # pillar cap trim
T_ROCK = "rock1_2"  # cave outer shell
T_SKY = "sky1"  # open sky ceiling
T_LAVA = "*lava1"  # torch flame
T_LIGHT_PANEL = "sfloor4_4"  # light panel
T_TELEPORT = "*teleport"  # teleport effect

# ── Bridge spine ──────────────────────────────────────────────────────────────
BRX1, BRX2 = -512, 512
BRY1, BRY2 = -128, 128
DZ1, DZ2 = 128, 144  # flat deck bottom / top (arch offsets added on top)

# ── Arch profile ──────────────────────────────────────────────────────────────
ARCH_RISE = 64  # centre rises 64 units above ends
ARCH_SEGS = 16  # segments approximating the curve
SEG_W = (BRX2 - BRX1) // ARCH_SEGS  # 64 units per segment


def arch_z(x):
    """Z offset above flat datum for parabolic arch at x."""
    xc = (BRX1 + BRX2) / 2.0
    half = (BRX2 - BRX1) / 2.0
    return ARCH_RISE * max(0.0, 1.0 - ((x - xc) / half) ** 2)


def dtop(x):
    return DZ2 + arch_z(x)  # deck surface Z at x


def dbot(x):
    return DZ1 + arch_z(x)  # deck bottom  Z at x


# ── Parapet + pillar heights (above deck surface) ─────────────────────────────
PAR_H = 32  # parapet wall height above deck
PIL_EXTRA = 32  # lowered further from 40 for easier jumping
PIL_CAP_H = 8  # cap slab height
P_HW = 20  # pillar half-width in X
P_CE = 4  # cap overhang each side

# ── Pillar X positions ────────────────────────────────────────────────────────
PXS = [-384, -128, 128, 384]

# ── World layout ──────────────────────────────────────────────────────────────
WALL_T = 16
FZ1, FZ2 = -16, 0
ROAD_X1, ROAD_X2 = -256, 256  # road channel E-W bounds (under bridge)
WORLD_X1, WORLD_X2 = -1024, 1024  # full world E-W extent
WORLD_Y1, WORLD_Y2 = -960, 960  # full world N-S extent
WORLD_Z2 = 640  # sky ceiling height

# ── Building (south campus, brutalist tower) ─────────────────────────────────
BLDG_X1, BLDG_X2 = -256, 256  # centered under bridge (512 wide)
BLDG_Y1, BLDG_Y2 = -800, -256  # south of bridge south edge (BRY1=-128, 128-unit gap)
BLDG_WALL = 16  # wall thickness
FLOOR_H = 128  # floor-to-floor height
BLDG_FLOORS = 4  # number of floors
BLDG_Z2 = BLDG_FLOORS * FLOOR_H  # building top height = 512

# ── Arch segments ─────────────────────────────────────────────────────────────
A_SEGS = 8


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
    # Side walls removed to make arch freestanding
    # if y1 < -rout:
    #     brushes.append(box(x1, y1, floor_z, x2, -rout, ceil_z, tex))
    # if y2 > rout:
    #     brushes.append(box(x1, rout, floor_z, x2, y2, ceil_z, tex))
    brushes.append(box(x1, -rout, floor_z, x2, -rin, sprz, tex))
    brushes.append(box(x1, rin, floor_z, x2, rout, sprz, tex))
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
    box(WORLD_X1 + WALL_T, BRY2 - 24, DZ2, BRX1, BRY2, DZ2 + PAR_H, T_CEMENT)
)  # North west
B.append(
    box(WORLD_X1 + WALL_T, BRY1, DZ2, BRX1, BRY1 + 24, DZ2 + PAR_H, T_CEMENT)
)  # South west
B.append(
    box(BRX2, BRY2 - 24, DZ2, WORLD_X2 - WALL_T, BRY2, DZ2 + PAR_H, T_CEMENT)
)  # North east
B.append(
    box(BRX2, BRY1, DZ2, WORLD_X2 - WALL_T, BRY1 + 24, DZ2 + PAR_H, T_CEMENT)
)  # South east

for i in range(ARCH_SEGS):
    sx1 = BRX1 + i * SEG_W
    sx2 = sx1 + SEG_W
    pb1, pb2 = dtop(sx1), dtop(sx2)  # parapet base follows deck top
    pt1, pt2 = pb1 + PAR_H, pb2 + PAR_H  # parapet top = base + PAR_H
    # North parapet
    B.append(ramp_slab(sx1, sx2, BRY2 - 24, BRY2, pb1, pb2, pt1, pt2, T_CEMENT))
    # South parapet
    B.append(ramp_slab(sx1, sx2, BRY1, BRY1 + 24, pb1, pb2, pt1, pt2, T_CEMENT))


# ── Pillar posts (stone piers with arches) ───────────────────────────────────
# Each pillar position now features a narrow arched pier supporting the deck.
for px in PXS:
    pdeck = dtop(px)  # deck surface at this X
    ppar = pdeck + PAR_H  # parapet top
    ppil = ppar + PIL_EXTRA  # pillar post top
    pcap = ppil + PIL_CAP_H  # cap slab top
    cy_n = BRY2 - 12  # north cap centre Y
    cy_s = BRY1 + 12  # south cap centre Y

    # Width of the pier in X (matches cap stone width)
    x1, x2 = px - P_HW - P_CE, px + P_HW + P_CE

    # Arch opening logic for the pier
    # Top of arch should be at dbot(px) = int(pdeck) - 16
    a_rout = 80
    a_rin = 64
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
    # North pillar top + cap
    B.append(box(px - P_HW, BRY2 - 24, pdeck, px + P_HW, BRY2, ppil, T_STONE))
    B.append(box(x1, BRY2 - 24 - P_CE, ppil, x2, BRY2 + P_CE, pcap, T_STONE))

    # South pillar top + cap
    B.append(box(px - P_HW, BRY1, pdeck, px + P_HW, BRY1 + 24, ppil, T_STONE))
    B.append(box(x1, BRY1 - P_CE, ppil, x2, BRY1 + 24 + P_CE, pcap, T_STONE))

    # Torch flames on cap top
    B.append(
        box(px - 4, cy_n - 4, pcap, px + 4, cy_n + 4, pcap + 10, T_STONE, tt=T_LAVA)
    )
    B.append(
        box(px - 4, cy_s - 4, pcap, px + 4, cy_s + 4, pcap + 10, T_STONE, tt=T_LAVA)
    )

# ── Teleport Arches at both ends of bridge ───────────────────────────────────
T_ARCH_RIN = 96
T_ARCH_ROUT = 128  # Fills the bridge width
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
    B.append(box(px - 8, BRY2 - 27, ph, px + 8, BRY2 - 24, pt_, T_LIGHT_PANEL))
    B.append(box(px - 8, BRY1 + 24, ph, px + 8, BRY1 + 27, pt_, T_LIGHT_PANEL))


# ════════════════════════════════════════════════════════════════════════════════
# BRUTALIST BUILDING — south campus, 4-floor playable tower
# Footprint: X=-256 to 256, Y=-800 to -256, Z=0 to 512
# North face faces the bridge; ground-level entrance at X=-64 to 64
# Lift shaft at center-north rises from ground to rooftop
# ════════════════════════════════════════════════════════════════════════════════
_bix1 = BLDG_X1 + BLDG_WALL  # interior west  = -240
_bix2 = BLDG_X2 - BLDG_WALL  # interior east  =  240
_biy1 = BLDG_Y1 + BLDG_WALL  # interior south = -784
_biy2 = BLDG_Y2 - BLDG_WALL  # interior north = -272

# Lift shaft at center-north (near entrance): X=-64 to 64, Y=-400 to -272
_stx1, _stx2 = -64, 64
_sty1, _sty2 = _biy2 - 128, _biy2  # Y: -400 to -272

# ── Outer walls ──────────────────────────────────────────────────────────────
# South wall — solid back wall
B.append(box(BLDG_X1, BLDG_Y1, FZ2, BLDG_X2, BLDG_Y1 + BLDG_WALL, BLDG_Z2, T_WALL))

# North wall — faces bridge; ground entrance (X=-64..64, Z=0..128) + upper windows
_door_n = [(_stx1, FZ2, _stx2, FLOOR_H)]  # ground entrance slot
_win_n = [
    (-128, _f * FLOOR_H + 32, 128, _f * FLOOR_H + 80) for _f in range(1, BLDG_FLOORS)
]
B.extend(
    layered_wall(
        BLDG_X1,
        BLDG_Y2 - BLDG_WALL,
        FZ2,
        BLDG_X2,
        BLDG_Y2,
        BLDG_Z2,
        _door_n + _win_n,
        T_WALL,
    )
)

# East and West walls — window openings (3 per floor along Y axis)
_win_yw = [(BLDG_Y1 + 80 + _i * 192, BLDG_Y1 + 112 + _i * 192) for _i in range(3)]
_win_yz = []
for _f in range(BLDG_FLOORS):
    for _wy1, _wy2 in _win_yw:
        _win_yz.append((_wy1, _f * FLOOR_H + 32, _wy2, _f * FLOOR_H + 80))

B.extend(
    layered_wall_y(
        BLDG_Y1, BLDG_X2 - BLDG_WALL, FZ2, BLDG_Y2, BLDG_X2, BLDG_Z2, _win_yz, T_WALL
    )
)
B.extend(
    layered_wall_y(
        BLDG_Y1, BLDG_X1, FZ2, BLDG_Y2, BLDG_X1 + BLDG_WALL, BLDG_Z2, _win_yz, T_WALL
    )
)

# Roof — open above lift shaft
B.append(
    box(BLDG_X1, BLDG_Y1, BLDG_Z2, _stx1, BLDG_Y2, BLDG_Z2 + BLDG_WALL, T_WALL)
)  # west
B.append(
    box(_stx2, BLDG_Y1, BLDG_Z2, BLDG_X2, BLDG_Y2, BLDG_Z2 + BLDG_WALL, T_WALL)
)  # east
B.append(
    box(_stx1, BLDG_Y1, BLDG_Z2, _stx2, _sty1, BLDG_Z2 + BLDG_WALL, T_WALL)
)  # south of shaft

# ── Interior floor slabs (floors 1-3, lift shaft opening in center-north) ────
for _f in range(1, BLDG_FLOORS):
    _sz = _f * FLOOR_H
    _st = _sz + BLDG_WALL
    B.append(box(_bix1, _biy1, _sz, _bix2, _sty1, _st, T_FLOOR))  # south bulk
    B.append(box(_bix1, _sty1, _sz, _stx1, _biy2, _st, T_FLOOR))  # west of shaft
    B.append(box(_stx2, _sty1, _sz, _bix2, _biy2, _st, T_FLOOR))  # east of shaft

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
    # Building ground floor (near entrance)
    (0, BLDG_Y2 - 64, ROAD_Z),
    # Building upper floors
    (0, _bcy, FLOOR_H + 40),
    (0, _bcy, FLOOR_H * 2 + 40),
    (0, _bcy, FLOOR_H * 3 + 40),
    # East/west campus ground
    (800, 0, ROAD_Z),
    (-800, 0, ROAD_Z),
    # Road under bridge
    (0, 300, ROAD_Z),
    (0, -400, ROAD_Z),
]:
    E.append(ent("info_player_deathmatch", origin=f"{pos[0]} {pos[1]} {pos[2]}"))

E.append(ent("weapon_rocketlauncher", origin=f"0 0 {DECK_Z}"))
E.append(ent("weapon_rocketlauncher", origin=f"0 {_bcy} {FLOOR_H + 40}"))
E.append(ent("weapon_rocketlauncher", origin=f"0 {_bcy} {FLOOR_H * 3 + 40}"))
E.append(ent("weapon_rocketlauncher", origin=f"800 0 {ROAD_Z}"))

for ax in [-384, -128, 128, 384]:
    E.append(ent("item_rockets", origin=f"{ax} 0 {int(dtop(ax) + 8)}"))
for _by in [_bcy - 80, _bcy + 80]:
    E.append(ent("item_rockets", origin=f"80 {_by} {FLOOR_H * 2 + 40}"))
    E.append(ent("item_rockets", origin=f"-80 {_by} {FLOOR_H * 2 + 40}"))
for rx in [600, 800]:
    E.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z}"))
    E.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z}"))

E.append(ent("item_health", origin=f"0 0 {DECK_Z}"))
E.append(ent("item_health", origin=f"0 {BLDG_Y2 - 64} {ROAD_Z}"))
E.append(ent("item_health", origin=f"0 {_bcy} {FLOOR_H * 2 + 40}"))

# Torch lights on pillar caps
for px in PXS:
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
_lift_travel = BLDG_Z2 - 8
_lift_brush = [
    box(_stx1 + 2, _sty1 + 2, BLDG_Z2 - 8, _stx2 - 2, _sty2 - 2, BLDG_Z2, T_FLOOR)
]
E.append(brush_ent("func_plat", _lift_brush, height=str(_lift_travel), speed="200"))

# Building interior lights — one per floor centred
_bcy = (BLDG_Y1 + BLDG_Y2) // 2  # -528
for _f in range(BLDG_FLOORS):
    _lz = _f * FLOOR_H + FLOOR_H // 2
    E.append(ent("light", origin=f"80  {_bcy} {_lz}", light="280"))
    E.append(ent("light", origin=f"-80 {_bcy} {_lz}", light="280"))

# Building window glow (exterior, east + west faces)
for _f in range(BLDG_FLOORS):
    _lz = _f * FLOOR_H + 56
    for _wy in [BLDG_Y1 + 80 + _i * 192 + 16 for _i in range(3)]:
        E.append(ent("light", origin=f"{BLDG_X2 + 10} {_wy} {_lz}", light="120"))
        E.append(ent("light", origin=f"{BLDG_X1 - 10} {_wy} {_lz}", light="120"))

# West campus ambient + east campus ambient
for _xx in [-800, 800]:
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
