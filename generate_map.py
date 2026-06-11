#!/usr/bin/env python3
"""Generate loyola.map — Loyola bridge + Knott Hall Quake 1 deathmatch map.

Layout:
  - Rectangular open world (±1024 E-W × ±960 N-S), open sky
  - Road runs N-S under the bridge (like Charles Street at Loyola Maryland)
  - Bridge spans E-W at deck height ~144; arched stone pillars over the road
  - Knott Hall on south campus (X=1186 to 1686, Y=-800 to -256, 4 floors)
    North face faces bridge; ground-level entrance at X=1308..1436
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
TEX_FLOOR_KH = "sfloor3_2"  # Knott Hall floors and ceilings
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
PB_Y1, PB_Y2 = -136, 136  # N-S width = 272 units ≈ 18 ft
PB_DZ1, PB_DZ2 = (
    224,
    240,
)  # flat deck bottom / top — raised for realistic road clearance (~22 ft)

# ── Arch profile ──────────────────────────────────────────────────────────────
# PB_X1/PB_X2 set after world/building bounds are known (arch spans full world width)
PB_ARCH_RISE = 144  # centre rise — matches reference photo arch crown (bridge08)
ARCH_SEGS = 32  # segments approximating the wider curve


def arch_z(x):
    """Z offset above flat datum for parabolic arch at x.

    Symmetric parabola centred at X=0 (Charles Street). Both sides degrade
    at the same rate, reaching zero at ±PB_X2 (1246 units). West of -1246
    the value clamps to zero (flat approach to world wall).
    """
    return PB_ARCH_RISE * max(0.0, 1.0 - (x / float(PB_X2)) ** 2)


def dtop(x):
    """Z coordinate of the deck surface (top face) at a given X position."""
    return PB_DZ2 + arch_z(x)  # deck surface Z at x


def dbot(x):
    """Z coordinate of the deck underside at a given X position."""
    return PB_DZ1 + arch_z(x)  # deck bottom  Z at x


# ── Parapet + pillar dimensions (above deck surface) ─────────────────────────
PB_PAR_H = 40  # parapet wall height above deck — lowered so player can jump on top
PB_PAR_W = ft(2, 6)  # parapet wall N-S width = 2 ft 6 in = 38 units
PB_PIL_EXTRA = 64  # extra pillar post height above parapet (gameplay)
PB_PIL_CAP_H = 12  # cap slab height
PB_PIL_PYR_H = 20  # pyramid cap height — visible triangular cement top
PB_PIL_PYR_W = 45  # pyramid base half-width — slightly wider than pillar (PB_PIL_HW=37)
PB_PIL_HW = ft(2, 5.5)  # pillar post half-width = half of 4 ft 11 in = 37 units
PB_PIL_CE = 17  # cap overhang each side = (7 ft 2 in - 4 ft 11 in) / 2
PB_PIL_CAP_IN_OVH = 4  # inward (deck-facing) overhang of cap slab past pillar post
PB_PIL_CAP_OUT_OVH = 20  # outward (N/S road-facing) overhang of cap slab
PB_PIL_OVERHANG = 16  # how far above-deck pillar tops extend beyond bridge N/S edges
PB_PIL_BASE_H = 24  # solid stone plinth at pier base below arch opening (~1.5 ft)
PB_PIL_BASE_RAMP_H = 40  # high side of ramped plinth — subtle incline, still jumpable
PB_PIL_BASE_CAP_H = 6  # cement cap slab thickness on top of each plinth
PB_PIL_BASE_CAP_OVH = 5  # cap overhang beyond plinth edges in X and Y (cornice)

# ── Pillar X positions — 2 pillars at the start of the curve + 1 east of Knott Hall
# Bridge support visibility: False = none, set of X positions = those piers only, True = all
SHOW_SUPPORTS = True

# ── World layout ──────────────────────────────────────────────────────────────
WALL_T = 16
FZ1, FZ2 = -16, 0
ROAD_X1, ROAD_X2 = -256, 256  # road channel E-W bounds (under bridge)
# Flat approach = 49 ft 1 in = 741 units per side of the 1050-unit arched span
KH_WIDTH = 640
WORLD_X1 = -1983  # west wall; PB_X1 = WORLD_X1+WALL_T = -1967, giving western span
# of 721 units (= PB_ARCH_X[2]→PB_ARCH_X[3] eastern span) so block spacing matches
WORLD_X2 = 2976  # east world wall; expanded to fit KH back road with NE pier at 2206
WORLD_Y1, WORLD_Y2 = (
    -1984,
    1712,
)  # extended south by 64 for landing area behind Knott Hall

# ── Knott Hall (south campus tower) ──────────────────────────────────────────
KH_OFFSET = 90  # eastward shift applied to entire building + walkway (aligns west window with west pier)
KH_PIER_X = 1246  # fixed pier/arch terminus (independent of building width)
KH_NE_PIER_X = 2206  # easternmost bridge pier; span 1246→2206 = 960 units = 6×160, 5 even sub-piers
KH_X1 = KH_PIER_X - 130 + KH_OFFSET  # = 1206
KH_X2 = KH_NE_PIER_X + 32  # = 2028 (east face = NE pier + original 32-unit gap)
KH_WIDTH = KH_X2 - KH_X1
KH_CX = (KH_X1 + KH_X2) // 2
# Entrance, walkway, stairs pinned near east side to keep west bulk dominant
KH_ORIG_CX = 1740 + KH_OFFSET  # = 1830 (shifted 64 units west from original 1894)
# Arch spans from west world wall to just west of Knott Hall west wall.
PB_X1 = WORLD_X1 + WALL_T  # west arch terminus at world edge
PB_X2 = KH_PIER_X  # east arch terminus at west pier
# Eastern flat span angles southward to match the real-life path curve (10–15°)
EAST_SPAN_ANGLE = 12.0  # degrees; pivot at x=PB_X2, east end shifts south
SEG_W = (PB_X2 - PB_X1) / ARCH_SEGS  # segment width for full-span arch
PB_ARCH_X = [
    -1246,  # west abutment pier (top of embankment hill)
    -525,
    525,
    KH_PIER_X,
    KH_NE_PIER_X,  # east pillar (aligned with KH east face)
]  # pillar X positions
KH_Y1, KH_Y2 = -1888, -256  # south of bridge south edge (3× north-south depth)
KH_WALL = 16  # wall thickness
KH_FLOOR_H = 160  # floor-to-floor height
KH_FLOORS = 5  # ground floor + 4 upper floors
INDENT = 80  # corner indentation depth
# Knott Hall sits on a hill so its 2nd floor aligns with the bridge walkway
KH_GROUND_Z = max(FZ2, PB_DZ2 - KH_FLOOR_H - KH_WALL)  # = 96
KH_Z2 = KH_GROUND_Z + KH_FLOORS * KH_FLOOR_H

# Sky ceiling must clear Knott Hall
WORLD_Z2 = max(640, KH_Z2 + 512)

# ── Walkway from bridge to Knott Hall 2nd floor ──────────────────────────────
KH_ENABLED = True  # re-enabled with pier-aligned north face windows
KH_WALKWAY_ENABLED = True  # re-connect walkway to Knott Hall 2nd floor
# Flat span at PB_DZ2 (flat approach section); pinned to original building centre
WALK_X1 = KH_ORIG_CX - 64
WALK_X2 = KH_ORIG_CX + 64
WALK_ZT1 = int(dtop(KH_ORIG_CX))  # deck surface Z at walkway X
WALK_ZT2 = KH_GROUND_Z + KH_FLOOR_H + KH_WALL  # 2nd floor entrance Z

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


def face(p1, p2, p3, tex, params="0 0 0 1 1"):
    """Return a Quake MAP brush face string from 3 coplanar points and a texture name."""
    return f"{pt(*p1)} {pt(*p2)} {pt(*p3)} {tex} {params}"


def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None, tt_params="0 0 0 1 1"):
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
                face((x1, y1, z2), (x1, y2, z2), (x2, y1, z2), tt, tt_params),
            ]
        )
        + "\n}"
    )


def east_y_shift(x):
    """Southward Y shift (negative = south) for a given X east of the easternmost pier.
    Pivots at PB_ARCH_X[4] (= 2206); zero for x <= that pier."""
    pivot = PB_ARCH_X[4]
    if x <= pivot:
        return 0.0
    return -(x - pivot) * math.tan(math.radians(EAST_SPAN_ANGLE))


def shear_box_y(x1, y1, z1, x2, y2, z2, s1, s2, tex, tt=None, tb=None):
    """Rectangular slab with Y-shear: at x=x1 the Y-range is [y1+s1, y2+s1],
    at x=x2 it is [y1+s2, y2+s2].  Negative s = southward shift."""
    tt = tt or tex
    tb = tb or tex
    y1a, y2a = y1 + s1, y2 + s1
    y1b, y2b = y1 + s2, y2 + s2
    return (
        "{\n"
        + "\n".join(
            [
                face((x1, y1a, z1), (x1, y2a, z1), (x1, y1a, z2), tex),  # -X west
                face((x2, y1b, z1), (x2, y1b, z2), (x2, y2b, z1), tex),  # +X east
                face(
                    (x1, y1a, z1), (x1, y1a, z2), (x2, y1b, z1), tex
                ),  # south (angled)
                face(
                    (x1, y2a, z1), (x2, y2b, z1), (x1, y2a, z2), tex
                ),  # north (angled)
                face((x1, y1a, z1), (x2, y1b, z1), (x1, y2a, z1), tb),  # bottom
                face((x1, y1a, z2), (x1, y2a, z2), (x2, y1b, z2), tt),  # top
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
    y1 and y2 may be passed in either order.
    When one end tapers to a knife-edge (zb==zt), that end face is omitted so
    the brush remains valid (5-face wedge instead of a degenerate 6-face prism)."""
    # Normalise so y1 <= y2 (face normals assume this ordering)
    if y1 > y2:
        y1, y2 = y2, y1
        zb1, zb2 = zb2, zb1
        zt1, zt2 = zt2, zt1
    tt = tt or tex
    tb = tb or tex
    faces = [
        face((x1, y1, zb1), (x1, y2, zb2), (x1, y1, zt1), tex),  # -X
        face((x2, y1, zb1), (x2, y1, zt1), (x2, y2, zb2), tex),  # +X
        face((x1, y1, zb1), (x2, y1, zb1), (x1, y2, zb2), tb),  # sloped bottom
        face((x1, y1, zt1), (x1, y2, zt2), (x2, y1, zt1), tt),  # sloped top
    ]
    # Only emit end-cap faces when the end has non-zero thickness
    if zt1 != zb1:
        faces.append(face((x1, y1, zb1), (x1, y1, zt1), (x2, y1, zb1), tex))  # -Y
    if zt2 != zb2:
        faces.append(face((x1, y2, zb2), (x2, y2, zb2), (x1, y2, zt2), tex))  # +Y
    return "{\n" + "\n".join(faces) + "\n}"


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


def make_tree(cx, cy, base_z):
    """Cartoon tree: brown trunk + three stacked ground-texture pyramids."""
    TEX_TRUNK = "bricka2_1"
    TEX_FOLIAGE = TEX_GROUND
    brushes = []
    # Trunk — 10×10, 56 units tall
    brushes.append(box(cx - 5, cy - 5, base_z, cx + 5, cy + 5, base_z + 56, TEX_TRUNK))
    # Lower foliage pyramid — wide base
    brushes.append(
        pyramid(
            cx - 40, cy - 40, base_z + 32, cx + 40, cy + 40, base_z + 80, TEX_FOLIAGE
        )
    )
    # Middle foliage pyramid
    brushes.append(
        pyramid(
            cx - 28, cy - 28, base_z + 64, cx + 28, cy + 28, base_z + 108, TEX_FOLIAGE
        )
    )
    # Upper foliage pyramid — narrow tip
    brushes.append(
        pyramid(
            cx - 16, cy - 16, base_z + 92, cx + 16, cy + 16, base_z + 128, TEX_FOLIAGE
        )
    )
    return brushes


def make_giant_tree(cx, cy, base_z, total_h=700):
    """Giant cartoon tree scaled to total_h units — trunk + three stacked foliage layers."""
    TEX_TRUNK = "bricka2_1"
    TEX_FOLIAGE = TEX_GROUND
    brushes = []
    trunk_h = int(total_h * 0.45)
    # Trunk — wider than small trees
    brushes.append(
        box(cx - 12, cy - 12, base_z, cx + 12, cy + 12, base_z + trunk_h, TEX_TRUNK)
    )
    # Lower foliage — wide base, starts halfway up trunk
    l0 = int(trunk_h * 0.5)
    l1 = int(total_h * 0.57)
    brushes.append(
        pyramid(
            cx - 160,
            cy - 160,
            base_z + l0,
            cx + 160,
            cy + 160,
            base_z + l1,
            TEX_FOLIAGE,
        )
    )
    # Middle foliage
    m0 = int(total_h * 0.48)
    m1 = int(total_h * 0.78)
    brushes.append(
        pyramid(
            cx - 110,
            cy - 110,
            base_z + m0,
            cx + 110,
            cy + 110,
            base_z + m1,
            TEX_FOLIAGE,
        )
    )
    # Upper foliage — narrow tip
    u0 = int(total_h * 0.70)
    u1 = total_h
    brushes.append(
        pyramid(
            cx - 60, cy - 60, base_z + u0, cx + 60, cy + 60, base_z + u1, TEX_FOLIAGE
        )
    )
    return brushes


def make_bush(cx, cy, base_z, size=24):
    """Cartoon bush: raised rectangular body with a small pyramid cap."""
    brushes = []
    # Short legs lifting it off the ground
    brushes.append(box(cx - 6, cy - 6, base_z, cx + 6, cy + 6, base_z + 10, TEX_GROUND))
    # Main rectangular body
    brushes.append(
        box(
            cx - size,
            cy - size,
            base_z + 10,
            cx + size,
            cy + size,
            base_z + size + 10,
            TEX_GROUND,
        )
    )
    # Small pyramid cap — just a hint of taper
    brushes.append(
        pyramid(
            cx - size + 4,
            cy - size + 4,
            base_z + size + 6,
            cx + size - 4,
            cy + size - 4,
            base_z + size + 20,
            TEX_GROUND,
        )
    )
    return brushes


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
    brushes.append(box(x1, yc - rin, floor_z, x2, yc + rin, sprz, tex))
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
    base_ramp=None,
    base_cap_h=0,
    base_cap_tex=None,
    base_cap_ovh=0,
):
    """Stone wall with arched opening centred at Y=0.

    stilt_h: height of straight sides before the arch springs (defaults to rin,
             giving a plain semicircle; set > rin for a tall stilted/gothic arch).
    overhang: extra Y extent on the rectangular pillar portions beyond ±rout.
    base_h: solid stone plinth height at ground level — arch opening starts above this.
    base_ramp: if given, a (zt_x1, zt_x2) tuple — replaces the flat base_h box with a
               ramp_slab whose top slopes from zt_x1 at x=x1 to zt_x2 at x=x2.
               base_h is ignored when base_ramp is set.
    base_cap_h: thin slab placed on top of the plinth (flat or ramped) in base_cap_tex.
    base_cap_tex: texture for the cap slab (defaults to tex).
    base_cap_ovh: how far the cap extends beyond the plinth in X and Y (cornice effect).
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
    if base_ramp is not None:
        zt1, zt2 = base_ramp
        brushes.append(ramp_slab(x1, x2, -rin, rin, floor_z, floor_z, zt1, zt2, tex))
        if base_cap_h > 0:
            cap_tex = base_cap_tex or tex
            cx1, cx2 = x1 - base_cap_ovh, x2 + base_cap_ovh
            crin = rin + base_cap_ovh
            brushes.append(
                ramp_slab(
                    cx1,
                    cx2,
                    -crin,
                    crin,
                    zt1,
                    zt2,
                    zt1 + base_cap_h,
                    zt2 + base_cap_h,
                    cap_tex,
                )
            )
    elif base_h > 0:
        brushes.append(box(x1, -rin, floor_z, x2, rin, floor_z + base_h, tex))
        if base_cap_h > 0:
            cap_tex = base_cap_tex or tex
            cx1, cx2 = x1 - base_cap_ovh, x2 + base_cap_ovh
            crin = rin + base_cap_ovh
            brushes.append(
                box(
                    cx1,
                    -crin,
                    floor_z + base_h,
                    cx2,
                    crin,
                    floor_z + base_h + base_cap_h,
                    cap_tex,
                )
            )

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
CS_Y1 = WORLD_Y1 + WALL_T
CS_Y2 = WORLD_Y2 - WALL_T
CS_WALK_W = 80  # sidewalk width (E-W)
CS_WALK_H = 8  # sidewalk + curb height above road
CS_STRIPE_W = 6  # centre-line stripe half-width

# ── Ennis Road (E-W, parallel to bridge, north side) ──
# Runs from Charles Street west edge (ROAD_X1) east to the world wall, dead-ending there.
# Half as wide as Charles Street (512/2=256 total → HW=128), north of bridge.
EP_Y = PB_Y2 + 800  # 936: centred 800 units north of bridge north edge
EP_HW = 160  # road half-width → 320-unit carriageway (~21 ft, matches reference)
EP_X1 = ROAD_X1  # start at west edge of Charles St to form T-junction
EP_X2 = WORLD_X2 - WALL_T  # dead-end at east world wall
EP_SW_EDGE = EP_Y - EP_HW - 3 * CS_WALK_W - 32  # Ennis south sidewalk outer edge
# Back road corridor X extents — defined here for road/curb brush splits below
KH_BR_CORRIDOR_X1 = KH_X2  # west edge of corridor gap
KH_BR_CORRIDOR_X2 = KH_X2 + CS_WALK_W + 2 * 128 + CS_WALK_W  # east edge
_EP_CURB_W = 8  # south Ennis curb strip width (N-S)

# Road surface — split either side of centre divider slot (_div_hw wide)
_div_hw = 4  # half-width of Charles St divider slot
_div_ep_hw = 16  # half-width of Ennis divider slot (wider for rune1_lig2 white)
BRUSHES.append(box(ROAD_X1, CS_Y1, FZ2, -_div_hw, CS_Y2, FZ2 + 2, TEX_ROAD))
BRUSHES.append(box(_div_hw, CS_Y1, FZ2, ROAD_X2, CS_Y2, FZ2 + 2, TEX_ROAD))
CS_SWALK_START = PB_Y2 + 200  # sidewalk starts north of bridge
# West sidewalk — north of bridge
BRUSHES.append(
    box(
        ROAD_X1 - CS_WALK_W,
        CS_SWALK_START,
        FZ2,
        ROAD_X1,
        CS_Y2,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)
# West curb — south section up to sidewalk start
BRUSHES.append(
    box(ROAD_X1 - 8, CS_Y1, FZ2, ROAD_X1, CS_SWALK_START, FZ2 + CS_WALK_H, TEX_CEMENT)
)
# Raised ground west of curb — rock/ground texture, flush with sidewalk
BRUSHES.append(
    box(
        ROAD_X1 - CS_WALK_W,
        CS_Y1,
        FZ2,
        ROAD_X1 - 8,
        CS_SWALK_START,
        FZ2 + CS_WALK_H,
        TEX_GROUND,
    )
)
# East sidewalk — split into two segments, trimmed CS_WALK_W short of each corner
BRUSHES.append(
    box(
        ROAD_X2,
        CS_Y1,
        FZ2,
        ROAD_X2 + CS_WALK_W,
        EP_Y - EP_HW - CS_WALK_W,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)
BRUSHES.append(
    box(
        ROAD_X2,
        EP_Y + EP_HW + CS_WALK_W,
        FZ2,
        ROAD_X2 + CS_WALK_W,
        CS_Y2,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)

# ── Ennis Road brushes ──
# Road surface — split around centre divider slot and south curb strip (Y=776–784)
# West section (near Charles St, no curb strip here)
BRUSHES.append(
    box(
        EP_X1,
        EP_Y - EP_HW,
        FZ2,
        ROAD_X2 + CS_WALK_W,
        EP_Y - _div_ep_hw,
        FZ2 + 2,
        TEX_ROAD,
    )
)
# Main east sections — full south extent to road edge
for _rx1, _rx2 in [
    (ROAD_X2 + CS_WALK_W, KH_BR_CORRIDOR_X1),
    (KH_BR_CORRIDOR_X2, EP_X2),
]:
    BRUSHES.append(
        box(
            _rx1,
            EP_Y - EP_HW,
            FZ2,
            _rx2,
            EP_Y - _div_ep_hw,
            FZ2 + 2,
            TEX_ROAD,
        )
    )
# Corridor gap section (back road entrance, no curb strip)
BRUSHES.append(
    box(
        KH_BR_CORRIDOR_X1,
        EP_Y - EP_HW,
        FZ2,
        KH_BR_CORRIDOR_X2,
        EP_Y - _div_ep_hw,
        FZ2 + 2,
        TEX_ROAD,
    )
)
BRUSHES.append(box(EP_X1, EP_Y, FZ2, EP_X2, EP_Y + EP_HW, FZ2 + 2, TEX_ROAD))
# North curb — offset east by CS_WALK_W to cut corner square
BRUSHES.append(
    box(
        ROAD_X2 + CS_WALK_W,
        EP_Y + EP_HW,
        FZ2,
        EP_X2,
        EP_Y + EP_HW + CS_WALK_W,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)
# South curb — split into two segments with a gap for the back road entrance
# West segment: Charles St east sidewalk to back road west sidewalk
BRUSHES.append(
    box(
        ROAD_X2 + CS_WALK_W,
        EP_SW_EDGE,
        FZ2,
        KH_X2,
        EP_SW_EDGE + CS_WALK_W,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)
# East segment: back road east sidewalk east to world wall
# KH_BR_ES_X2 = KH_X2 + CS_WALK_W + 2*128 + CS_WALK_W (computed inline to avoid forward-ref)
BRUSHES.append(
    box(
        KH_X2 + CS_WALK_W + 2 * 128 + CS_WALK_W,
        EP_SW_EDGE,
        FZ2,
        EP_X2,
        EP_SW_EDGE + CS_WALK_W,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)

# ── Lane dividers — dashed sfloor3_2 flush inserts in carved road slots ───────
TEX_DIVIDER = "sfloor3_2"
_DASH = 64  # dash length
_GAP = 64  # gap length (filled with road tex)
# Charles Street — dashed N-S, two sections either side of bridge
for _sec_y1, _sec_y2 in [(CS_Y1, PB_Y1), (PB_Y2, CS_Y2)]:
    _y = _sec_y1
    _dash_on = True
    while _y < _sec_y2:
        _y2 = min(_y + (_DASH if _dash_on else _GAP), _sec_y2)
        _tex = TEX_DIVIDER if _dash_on else TEX_ROAD
        BRUSHES.append(box(-_div_hw, _y, FZ2, _div_hw, _y2, FZ2 + 2, _tex))
        _y = _y2
        _dash_on = not _dash_on
# Ennis Road — dashed E-W from Charles St east to world wall
_x = ROAD_X2
_dash_on = True
while _x < EP_X2:
    _x2 = min(_x + (_DASH if _dash_on else _GAP), EP_X2)
    _tex = TEX_DIVIDER if _dash_on else TEX_ROAD
    BRUSHES.append(box(_x, EP_Y - _div_ep_hw, FZ2, _x2, EP_Y, FZ2 + 2, _tex))
    _x = _x2
    _dash_on = not _dash_on

# ── Rounded intersection corners (Charles & Ennis) ───────────────────────────
# Arc center at the OUTER (far) corner so the curve faces outward toward the road.
# Each corner: road box fills the cut square, cement arc fans sit on top.
CS_CRN_R = CS_WALK_W  # corner radius = sidewalk width
CS_CRN_SEGS = 12  # segments per arc (12 × 7.5° = 90°)

# SE corner: far corner is at SE of cut square
cx_se = ROAD_X2 + CS_CRN_R
cy_se = EP_Y - EP_HW - CS_CRN_R
BRUSHES.append(box(ROAD_X2, cy_se, FZ2, cx_se, EP_Y - EP_HW, FZ2 + 2, TEX_ROAD))
# Arc sweeps CCW from 90° (north) to 180° (west)
for _i in range(CS_CRN_SEGS):
    _a0 = math.radians(90 + _i * 90 / CS_CRN_SEGS)
    _a1 = math.radians(90 + (_i + 1) * 90 / CS_CRN_SEGS)
    _px0, _py0 = cx_se + CS_CRN_R * math.cos(_a0), cy_se + CS_CRN_R * math.sin(_a0)
    _px1, _py1 = cx_se + CS_CRN_R * math.cos(_a1), cy_se + CS_CRN_R * math.sin(_a1)
    BRUSHES.append(
        tri_prism(
            cx_se, cy_se, _px0, _py0, _px1, _py1, FZ2, FZ2 + CS_WALK_H, TEX_CEMENT
        )
    )

# NE corner: far corner is at NE of cut square
cx_ne = ROAD_X2 + CS_CRN_R
cy_ne = EP_Y + EP_HW + CS_CRN_R
BRUSHES.append(box(ROAD_X2, EP_Y + EP_HW, FZ2, cx_ne, cy_ne, FZ2 + 2, TEX_ROAD))
# Arc sweeps CCW from 180° (west) to 270° (south)
for _i in range(CS_CRN_SEGS):
    _a0 = math.radians(180 + _i * 90 / CS_CRN_SEGS)
    _a1 = math.radians(180 + (_i + 1) * 90 / CS_CRN_SEGS)
    _px0, _py0 = cx_ne + CS_CRN_R * math.cos(_a0), cy_ne + CS_CRN_R * math.sin(_a0)
    _px1, _py1 = cx_ne + CS_CRN_R * math.cos(_a1), cy_ne + CS_CRN_R * math.sin(_a1)
    BRUSHES.append(
        tri_prism(
            cx_ne, cy_ne, _px0, _py0, _px1, _py1, FZ2, FZ2 + CS_WALK_H, TEX_CEMENT
        )
    )

# ── Sidewalk ramps — smooth ground-to-sidewalk transitions ───────────────────
CS_RAMP_W = 64  # ramp width in units

# West ramp — slopes from ground up to west sidewalk edge (full N-S extent)
BRUSHES.append(
    ramp_slab(
        ROAD_X1 - CS_WALK_W - CS_RAMP_W,
        ROAD_X1 - CS_WALK_W,
        CS_Y1,
        CS_Y2,
        FZ1,
        FZ1,
        FZ2,
        FZ2 + CS_WALK_H,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# East ramp — south of Ennis Road
BRUSHES.append(
    ramp_slab(
        ROAD_X2 + CS_WALK_W,
        ROAD_X2 + CS_WALK_W + CS_RAMP_W,
        CS_Y1,
        EP_SW_EDGE,
        FZ1,
        FZ1,
        FZ2 + CS_WALK_H,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# East ramp — north of Ennis Road
BRUSHES.append(
    ramp_slab(
        ROAD_X2 + CS_WALK_W,
        ROAD_X2 + CS_WALK_W + CS_RAMP_W,
        EP_Y + EP_HW + CS_WALK_W,
        CS_Y2,
        FZ1,
        FZ1,
        FZ2 + CS_WALK_H,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# Ennis north ramp — slopes from north curb edge down going north
BRUSHES.append(
    ramp_slab_y(
        ROAD_X2 + CS_WALK_W,
        EP_X2,
        EP_Y + EP_HW + CS_WALK_W,
        EP_Y + EP_HW + CS_WALK_W + CS_RAMP_W,
        FZ1,
        FZ1,
        FZ2 + CS_WALK_H,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# (Ramp zone south of Ennis sidewalk covered by world floor — no fill needed)

# Verge fill — ground between road south edge and sidewalk inner edge, flush with sidewalk
# Split around back road corridor gap (KH_BR_CORRIDOR_X1..KH_BR_CORRIDOR_X2)
# SE corner (east of back road) uses gravel3c (mulch bed)
for _vx1, _vx2, _vtex in [
    (ROAD_X2 + CS_WALK_W, KH_BR_CORRIDOR_X1, TEX_GROUND),
    (KH_BR_CORRIDOR_X2, EP_X2, "grave13c"),
]:
    BRUSHES.append(
        box(
            _vx1,
            EP_SW_EDGE + CS_WALK_W,
            FZ1,
            _vx2,
            EP_Y - EP_HW - _EP_CURB_W,
            FZ2 + CS_WALK_H,
            _vtex,
        )
    )

# Cement curb strip — last 8 units of verge at road edge, flush with verge surface
for _vx1, _vx2 in [
    (ROAD_X2 + CS_WALK_W, KH_BR_CORRIDOR_X1),
    (KH_BR_CORRIDOR_X2, EP_X2),
]:
    BRUSHES.append(
        box(
            _vx1,
            EP_Y - EP_HW - _EP_CURB_W,
            FZ1,
            _vx2,
            EP_Y - EP_HW,
            FZ2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )

# ── Ennis Drive entrance pillars (white stone columns flanking Charles St entrance) ──
EP_PIL_HW = 22  # pillar half-width (was 30, ×0.75)
EP_PIL_OFFSET = CS_WALK_W + 20
EP_PIL_X1 = (
    PB_ARCH_X[2] - EP_PIL_HW
)  # align pillar centre with closest bridge pier (X=525)
EP_PIL_X2 = PB_ARCH_X[2] + EP_PIL_HW
EP_PIL_ZB = FZ2
EP_PIL_POST_H = 81  # post height (was 108, ×0.75)
EP_PIL_CAP_OVH = 1
EP_PIL_CAP_H = 3

# Bell shape — cap divider + single tapered step (no flare, no tip):
#      |  |      step 2: hw=16, h=27
#  ====+==+====  cap:    hw=23, h=1
#      |  |      post:   hw=22, h=81
EP_PIL_BELL2_HW = (
    19  # tapered top section half-width (wider than before, less than post)
)
EP_PIL_BELL2_H = 27  # tapered top section height (was 36, ×0.75)

for _epy in (EP_Y - EP_HW - EP_PIL_HW, EP_Y + EP_HW + EP_PIL_HW):
    ennis_pil_cx = EP_PIL_X1 + EP_PIL_HW  # pillar centre X
    _cap_hw = EP_PIL_HW + EP_PIL_CAP_OVH  # = 40

    # Post
    _base_h = EP_PIL_POST_H // 3  # bottom base = lower third of post
    # Bottom base — same width as cap, gives plinth effect
    BRUSHES.append(
        box(
            ennis_pil_cx - _cap_hw,
            _epy - _cap_hw,
            EP_PIL_ZB,
            ennis_pil_cx + _cap_hw,
            _epy + _cap_hw,
            EP_PIL_ZB + _base_h,
            TEX_WHITE_STONE,
        )
    )
    # Upper post — narrower, sits on bottom base
    BRUSHES.append(
        box(
            EP_PIL_X1,
            _epy - EP_PIL_HW,
            EP_PIL_ZB + _base_h,
            EP_PIL_X2,
            _epy + EP_PIL_HW,
            EP_PIL_ZB + EP_PIL_POST_H,
            TEX_WHITE_STONE,
        )
    )
    # Thin cap divider — overhangs post on all sides
    _cap_z = EP_PIL_ZB + EP_PIL_POST_H
    BRUSHES.append(
        box(
            ennis_pil_cx - _cap_hw,
            _epy - _cap_hw,
            _cap_z,
            ennis_pil_cx + _cap_hw,
            _epy + _cap_hw,
            _cap_z + EP_PIL_CAP_H,
            TEX_WHITE_STONE,
        )
    )
    # Bell step 2 — tapered top, narrower than post
    _b2_z = _cap_z + EP_PIL_CAP_H
    BRUSHES.append(
        box(
            ennis_pil_cx - EP_PIL_BELL2_HW,
            _epy - EP_PIL_BELL2_HW,
            _b2_z,
            ennis_pil_cx + EP_PIL_BELL2_HW,
            _epy + EP_PIL_BELL2_HW,
            _b2_z + EP_PIL_BELL2_H,
            TEX_WHITE_STONE,
        )
    )
    # Torch base above pyramid apex — narrow post + brick cup (matches bridge pillars)
    _ennis_pil_apex = _b2_z + EP_PIL_BELL2_H
    ennis_pil_cx = EP_PIL_X1 + EP_PIL_HW
    BRUSHES.append(
        box(
            ennis_pil_cx - 3,
            _epy - 3,
            _ennis_pil_apex,
            ennis_pil_cx + 3,
            _epy + 3,
            _ennis_pil_apex + 16,
            TEX_CEMENT,
        )
    )
    BRUSHES.append(
        box(
            ennis_pil_cx - 5,
            _epy - 5,
            _ennis_pil_apex + 16,
            ennis_pil_cx + 5,
            _epy + 5,
            _ennis_pil_apex + 20,
            TEX_BRICK,
        )
    )

# ── Ennis Drive L-shaped campus boundary wall (north side of entrance) ────────
# city2_1 brick wall from near Charles St sidewalk east to pillar, then turns north.
# Starts with a small grass gap east of the sidewalk.
EP_WALL_T = 8  # wall thickness
EP_WALL_H = 96  # wall height — matches iron fence
bw_ny = EP_Y + EP_HW + EP_PIL_HW * 2  # south face Y (flush with north pillar)
bw_x1 = ROAD_X2 + CS_WALK_W + 48  # ~48u east of sidewalk (more grass)
bwex2 = PB_ARCH_X[2] + EP_PIL_HW + 80  # E-W wall extends past stone pillar
bw_ny2 = bw_ny + 200  # north segment length
# East-running segment (south base of L)
BRUSHES.append(
    box(bw_x1, bw_ny, FZ2, bwex2, bw_ny + EP_WALL_T, FZ2 + EP_WALL_H, "city2_1")
)
# North-turning segment — south half brick, north half iron fence
bw_mid_y = (bw_ny + WORLD_Y2 - WALL_T) // 2  # midpoint of north segment
BRUSHES.append(
    box(
        bw_x1,
        bw_ny,
        FZ2,
        bw_x1 + EP_WALL_T,
        bw_mid_y,
        FZ2 + EP_WALL_H,
        "city2_1",
    )
)
# North half — iron fence matching west-side style (FNC_* constants defined later)
_gfx1 = bw_x1 + EP_WALL_T // 2 - 1  # centre the pickets on the wall line
_gfx2 = _gfx1 + 2
_g_fnc_h = 96
_g_fnc_spacing = 16
_g_fnc_tex = "metal4_4"
# Top rail
BRUSHES.append(
    box(
        _gfx1,
        bw_mid_y,
        FZ2 + _g_fnc_h - 28,
        _gfx2,
        WORLD_Y2 - WALL_T,
        FZ2 + _g_fnc_h - 26,
        _g_fnc_tex,
    )
)
# Pickets
_gpy = bw_mid_y
_gpi = 0
while _gpy + 2 <= WORLD_Y2 - WALL_T:
    _gpw = 8 if _gpi % 10 == 0 else 2
    BRUSHES.append(
        box(_gfx1, _gpy, FZ2, _gfx2, _gpy + _gpw, FZ2 + _g_fnc_h, _g_fnc_tex)
    )
    _gpy += _g_fnc_spacing
    _gpi += 1

# ── Decorative iron panels on west face of brick wall, sitting ON TOP of wall ──
# Panels protrude above wall top; rectangles are horizontal (wider than tall).
_pf_x1 = bw_x1 - 2  # protrude 2 units from west face
_pf_x2 = bw_x1
_p_t = 2  # bar thickness
_p_ow = 48  # outer frame Y width (wide = horizontal)
_p_oh = 28  # outer frame Z height (shorter than wide)
_p_iw = 28  # inner frame Y width
_p_ih = 12  # inner frame Z height
_p_z1 = FZ2 + EP_WALL_H  # panels start at wall top
_p_zctr = _p_z1 + _p_oh // 2  # Z centre above wall top
_p_spacing = _p_ow + 16  # centre-to-centre spacing

# Snap bw_mid_y to the north edge of the last full panel that fits in the original half-space
_p_avail = bw_mid_y - bw_ny
_p_count = max(
    1, (_p_avail + _p_ow) // (_p_ow + 8)
)  # at least 8-unit gap between panels
_p_spacing = _p_avail // _p_count  # evenly distribute N panels across the brick space

# Start first panel so its south edge aligns exactly with bw_ny (no overhang)
_p_cy = bw_ny + _p_spacing // 2
_p_drawn = 0
while _p_drawn < _p_count:
    _pw = _p_ow
    _piw = _p_iw

    y1_o = _p_cy - _pw // 2
    y2_o = _p_cy + _pw // 2
    z1_o = _p_zctr - _p_oh // 2
    z2_o = _p_zctr + _p_oh // 2
    y1_i = _p_cy - _piw // 2
    y2_i = _p_cy + _piw // 2
    z1_i = _p_zctr - _p_ih // 2
    z2_i = _p_zctr + _p_ih // 2

    # Outer rectangle
    BRUSHES.append(
        box(_pf_x1, y1_o, z1_o, _pf_x2, y2_o, z1_o + _p_t, _g_fnc_tex)
    )  # bottom
    BRUSHES.append(
        box(_pf_x1, y1_o, z2_o - _p_t, _pf_x2, y2_o, z2_o, _g_fnc_tex)
    )  # top
    BRUSHES.append(
        box(_pf_x1, y1_o, z1_o, _pf_x2, y1_o + _p_t, z2_o, _g_fnc_tex)
    )  # left
    BRUSHES.append(
        box(_pf_x1, y2_o - _p_t, z1_o, _pf_x2, y2_o, z2_o, _g_fnc_tex)
    )  # right
    # Inner rectangle
    BRUSHES.append(
        box(_pf_x1, y1_i, z1_i, _pf_x2, y2_i, z1_i + _p_t, _g_fnc_tex)
    )  # bottom
    BRUSHES.append(
        box(_pf_x1, y1_i, z2_i - _p_t, _pf_x2, y2_i, z2_i, _g_fnc_tex)
    )  # top
    BRUSHES.append(
        box(_pf_x1, y1_i, z1_i, _pf_x2, y1_i + _p_t, z2_i, _g_fnc_tex)
    )  # left
    BRUSHES.append(
        box(_pf_x1, y2_i - _p_t, z1_i, _pf_x2, y2_i, z2_i, _g_fnc_tex)
    )  # right
    # Diagonal corner connectors: each inner corner → corresponding outer corner
    BRUSHES.append(
        ramp_slab_y(
            _pf_x1, _pf_x2, y1_o, y1_i, z1_o, z1_i, z1_o + _p_t, z1_i + _p_t, _g_fnc_tex
        )
    )  # bottom-left
    BRUSHES.append(
        ramp_slab_y(
            _pf_x1, _pf_x2, y2_i, y2_o, z1_i, z1_o, z1_i + _p_t, z1_o + _p_t, _g_fnc_tex
        )
    )  # bottom-right
    BRUSHES.append(
        ramp_slab_y(
            _pf_x1, _pf_x2, y1_o, y1_i, z2_o - _p_t, z2_i - _p_t, z2_o, z2_i, _g_fnc_tex
        )
    )  # top-left
    BRUSHES.append(
        ramp_slab_y(
            _pf_x1, _pf_x2, y2_i, y2_o, z2_i - _p_t, z2_o - _p_t, z2_i, z2_o, _g_fnc_tex
        )
    )  # top-right
    # Connector to next panel at mid-Z
    _conn_y2_p = _p_cy + _p_spacing - _p_ow // 2
    if _p_drawn + 1 < _p_count:
        BRUSHES.append(
            box(
                _pf_x1,
                y2_o,
                _p_zctr - _p_t // 2,
                _pf_x2,
                _conn_y2_p,
                _p_zctr + _p_t // 2,
                _g_fnc_tex,
            )
        )
    _p_cy += _p_spacing
    _p_drawn += 1
# Corner pillar — square brick post at the L junction, wider than wall
EP_WALL_PIL_HW = 14  # pillar half-width (28 units square)
EP_WALL_PIL_H = 120  # pillar height — taller than wall
bw_cx = bw_x1 + EP_WALL_T // 2  # pillar centre X (wall centre)
bw_cy = bw_ny + EP_WALL_T // 2  # pillar centre Y (wall centre)
BRUSHES.append(
    box(
        bw_cx - EP_WALL_PIL_HW,
        bw_cy - EP_WALL_PIL_HW,
        FZ2,
        bw_cx + EP_WALL_PIL_HW,
        bw_cy + EP_WALL_PIL_HW,
        FZ2 + EP_WALL_PIL_H,
        "city2_1",
    )
)
# Cement collar — same width as pillar, sits between brick post and cap slab
BRUSHES.append(
    box(
        bw_cx - EP_WALL_PIL_HW,
        bw_cy - EP_WALL_PIL_HW,
        FZ2 + EP_WALL_PIL_H,
        bw_cx + EP_WALL_PIL_HW,
        bw_cy + EP_WALL_PIL_HW,
        FZ2 + EP_WALL_PIL_H + 6,
        TEX_CEMENT,
    )
)
# Square cap slab, then shallow pyramid on top
BRUSHES.append(
    box(
        bw_cx - EP_WALL_PIL_HW - 1,
        bw_cy - EP_WALL_PIL_HW - 1,
        FZ2 + EP_WALL_PIL_H + 6,
        bw_cx + EP_WALL_PIL_HW + 1,
        bw_cy + EP_WALL_PIL_HW + 1,
        FZ2 + EP_WALL_PIL_H + 10,
        TEX_CEMENT,
    )
)
BRUSHES.append(
    pyramid(
        bw_cx - EP_WALL_PIL_HW - 1,
        bw_cy - EP_WALL_PIL_HW - 1,
        FZ2 + EP_WALL_PIL_H + 10,
        bw_cx + EP_WALL_PIL_HW + 1,
        bw_cy + EP_WALL_PIL_HW + 1,
        FZ2 + EP_WALL_PIL_H + 16,
        TEX_CEMENT,
    )
)

# ── East-running iron gate along Ennis Drive (from brick wall end to ~halfway east) ──
# Built as func_detail to avoid BSP portal overflow from pickets in open space.
_ew_x1 = bwex2  # starts at east end of brick wall
_ew_x2 = (bwex2 + WORLD_X2 - WALL_T) // 2  # ends halfway to east world wall
_ew_fy1 = bw_ny + EP_WALL_T // 2 - 1  # Y centre of fence line
_ew_fy2 = _ew_fy1 + 2
_ew_fence_brushes = []
# Top rail
_ew_fence_brushes.append(
    box(
        _ew_x1,
        _ew_fy1,
        FZ2 + _g_fnc_h - 28,
        _ew_x2,
        _ew_fy2,
        FZ2 + _g_fnc_h - 26,
        _g_fnc_tex,
    )
)
# Pickets — 2-wide every 16, 8-wide posts every 10th
_ewpx = _ew_x1
_ewpi = 0
while _ewpx + 2 <= _ew_x2:
    _ewpw = 8 if _ewpi % 10 == 0 else 2
    _ew_fence_brushes.append(
        box(_ewpx, _ew_fy1, FZ2, _ewpx + _ewpw, _ew_fy2, FZ2 + _g_fnc_h, _g_fnc_tex)
    )
    _ewpx += _g_fnc_spacing
    _ewpi += 1


# ── Cement parapet wall — east half of Ennis Drive (iron fence end to east world wall) ──
_cw_x1 = _ew_x2  # starts where iron fence ends
_cw_x2 = WORLD_X2 - WALL_T  # east world wall inner face
_cw_fy1 = bw_ny  # south face
_cw_fy2 = bw_ny + EP_WALL_T  # north face
_cw_h = 32  # parapet height — low enough to jump over
_cw_pil_hw = 14  # pillar half-width
_cw_pil_h = _cw_h + 16  # pillar slightly taller than wall
# Wall body
BRUSHES.append(box(_cw_x1, _cw_fy1, FZ2, _cw_x2, _cw_fy2, FZ2 + _cw_h, TEX_CEMENT))
# Cap slab (slightly proud on all sides)
BRUSHES.append(
    box(
        _cw_x1,
        _cw_fy1 - 2,
        FZ2 + _cw_h,
        _cw_x2,
        _cw_fy2 + 2,
        FZ2 + _cw_h + 6,
        TEX_CEMENT,
    )
)
# Pillars at each end
_cw_lamp_posts = []
for _px in (_cw_x1, _cw_x2):
    _pcy = (_cw_fy1 + _cw_fy2) // 2
    BRUSHES.append(
        box(
            _px - _cw_pil_hw,
            _pcy - _cw_pil_hw,
            FZ2,
            _px + _cw_pil_hw,
            _pcy + _cw_pil_hw,
            FZ2 + _cw_pil_h,
            TEX_CEMENT,
        )
    )
    # Cap slab on pillar
    BRUSHES.append(
        box(
            _px - _cw_pil_hw - 2,
            _pcy - _cw_pil_hw - 2,
            FZ2 + _cw_pil_h,
            _px + _cw_pil_hw + 2,
            _pcy + _cw_pil_hw + 2,
            FZ2 + _cw_pil_h + 6,
            TEX_CEMENT,
        )
    )
    # Lamppost pole
    _lp_base = FZ2 + _cw_pil_h + 6
    BRUSHES.append(
        box(_px - 3, _pcy - 3, _lp_base, _px + 3, _pcy + 3, _lp_base + 160, TEX_PILLAR)
    )
    # Lantern head — narrow shaft + wider cap
    BRUSHES.append(
        box(
            _px - 4,
            _pcy - 4,
            _lp_base + 160,
            _px + 4,
            _pcy + 4,
            _lp_base + 176,
            TEX_CEMENT,
        )
    )
    BRUSHES.append(
        box(
            _px - 7,
            _pcy - 7,
            _lp_base + 176,
            _px + 7,
            _pcy + 7,
            _lp_base + 180,
            TEX_CEMENT,
        )
    )
    _cw_lamp_posts.append((_px, _pcy, _lp_base + 180))


RH_FLOORS = 3
RH_H = RH_FLOORS * KH_FLOOR_H  # 384 units tall
RH_DEPTH = 600  # building N-S depth (doubled)
RH_PIER_X = min(PB_ARCH_X)  # = -1100
RH_X2 = RH_PIER_X + PB_PIL_HW + 32  # east face of building  = -1031
RH_X1 = RH_X2 - 576  # west face of building (doubled width)
RH_NORTH_Y2 = WORLD_Y2 - WALL_T - 150  # north building north face (shifted south)
RH_NORTH_Y1 = RH_NORTH_Y2 - RH_DEPTH  # north building south face
RH_SOUTH1_Y1 = WORLD_Y1 + WALL_T  # south building 1 south face = -2032
RH_SOUTH1_Y2 = RH_SOUTH1_Y1 + RH_DEPTH  # south building 1 north face = -1432
RH_SOUTH2_Y1 = RH_SOUTH1_Y2  # south building 2 south face = -1432
RH_SOUTH2_Y2 = RH_SOUTH2_Y1 + RH_DEPTH  # south building 2 north face = -832

# Starts at X=-560 (clear of the -525 pier base) so arch stone is not buried there.
RH_EMB_X2 = -1146  # starts just east of abutment pier, keeping stone base visible
# Interpolate ramp top-Z at the building's west face so the slope is continuous
emb_zt_at_ab_x1 = int(PB_DZ2 + (FZ2 - PB_DZ2) * (RH_X1 - PB_X1) / (RH_EMB_X2 - PB_X1))
# South segment — west of south buildings (through buildings' Y range)
BRUSHES.append(
    ramp_slab(
        PB_X1,
        RH_X1,
        CS_Y1,
        RH_SOUTH2_Y2,
        FZ1,
        FZ1,
        PB_DZ2,
        emb_zt_at_ab_x1,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# South segment — full width between south buildings and north building
BRUSHES.append(
    ramp_slab(
        PB_X1,
        RH_EMB_X2,
        RH_SOUTH2_Y2,
        RH_NORTH_Y1,
        FZ1,
        FZ1,
        PB_DZ2,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# Middle segment — only west of north building
BRUSHES.append(
    ramp_slab(
        PB_X1,
        RH_X1,
        RH_NORTH_Y1,
        RH_NORTH_Y2,
        FZ1,
        FZ1,
        PB_DZ2,
        emb_zt_at_ab_x1,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)
# North of north building — restore original ramp
BRUSHES.append(
    ramp_slab(
        PB_X1,
        RH_EMB_X2,
        RH_NORTH_Y2,
        CS_Y2,
        FZ1,
        FZ1,
        PB_DZ2,
        FZ2,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)

# Wall extending north from the abutment pier, deck height, city2_1 texture
# Door opening ~160 units north of the pier (visible in bridge10)
RH_WALL_N_Y1 = PB_Y2 + PB_PIL_OVERHANG  # north face of pier = 152
RH_WALL_S_Y2 = -(PB_Y2 + PB_PIL_OVERHANG)  # south face of pier = -152
RH_DOOR_W = 80  # door opening width (~5 ft)
RH_DOOR_OFF = 160  # distance from pier face to door centre
RH_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)
# (Building dimensions already defined above)
# South brick wall — from bridge pier south face to nearest south building, with door gap
# Door centered 160 units north of the building (closer to buildings)
s_door_y = RH_SOUTH2_Y2 + RH_DOOR_OFF  # door centre Y
BRUSHES.append(
    box(
        RH_PIER_X - PB_PIL_HW,
        RH_SOUTH2_Y2,
        FZ2,
        RH_PIER_X + PB_PIL_HW,
        s_door_y - RH_DOOR_W // 2,
        PB_DZ2,
        "city2_1",
    )
)
BRUSHES.append(
    box(
        RH_PIER_X - PB_PIL_HW,
        s_door_y + RH_DOOR_W // 2,
        FZ2,
        RH_PIER_X + PB_PIL_HW,
        RH_WALL_S_Y2,
        PB_DZ2,
        "city2_1",
    )
)
BRUSHES.append(
    box(
        RH_PIER_X - PB_PIL_HW,
        s_door_y - RH_DOOR_W // 2,
        FZ2 + RH_DOOR_H,
        RH_PIER_X + PB_PIL_HW,
        s_door_y + RH_DOOR_W // 2,
        PB_DZ2,
        "city2_1",
    )
)

# ════════════════════════════════════════════════════════════════════════════════
# ABUTMENT BUILDINGS — non-enterable 3-floor brick buildings at N/S wall ends
# ════════════════════════════════════════════════════════════════════════════════


def win_row(n, lo, hi):
    """Evenly-spaced window centre positions."""
    step = (hi - lo) / n
    return [lo + step * (i + 0.5) for i in range(n)]


RH_WIN_W, RH_WIN_H, RH_WIN_T = 20, 28, 3  # window half-width, half-height, trim depth


def abutment_bldg_windows(bx1, bx2, by1, by2, bz1, floors, skip_n=False, skip_s=False):
    """Protruding TEX_CEMENT window-trim panels on the visible faces of a solid brick box."""
    brushes = []
    nx = max(2, (bx2 - bx1) // 80)  # windows per floor along X
    ny = max(1, (by2 - by1) // 80)  # windows per floor along Y
    for fl in range(floors):
        wz = bz1 + fl * KH_FLOOR_H + KH_FLOOR_H // 2
        if not skip_s:  # south face — protrude outward in -Y
            for wx in win_row(nx, bx1 + 40, bx2 - 40):
                brushes.append(
                    box(
                        wx - RH_WIN_W,
                        by1 - RH_WIN_T,
                        wz - RH_WIN_H,
                        wx + RH_WIN_W,
                        by1,
                        wz + RH_WIN_H,
                        TEX_CEMENT,
                    )
                )
        if not skip_n:  # north face — protrude outward in +Y
            for wx in win_row(nx, bx1 + 40, bx2 - 40):
                brushes.append(
                    box(
                        wx - RH_WIN_W,
                        by2,
                        wz - RH_WIN_H,
                        wx + RH_WIN_W,
                        by2 + RH_WIN_T,
                        wz + RH_WIN_H,
                        TEX_CEMENT,
                    )
                )
        for wy in win_row(ny, by1 + 40, by2 - 40):  # east face — protrude in +X
            brushes.append(
                box(
                    bx2,
                    wy - RH_WIN_W,
                    wz - RH_WIN_H,
                    bx2 + RH_WIN_T,
                    wy + RH_WIN_W,
                    wz + RH_WIN_H,
                    TEX_CEMENT,
                )
            )
        for wy in win_row(ny, by1 + 40, by2 - 40):  # west face — protrude in -X
            brushes.append(
                box(
                    bx1 - RH_WIN_T,
                    wy - RH_WIN_W,
                    wz - RH_WIN_H,
                    bx1,
                    wy + RH_WIN_W,
                    wz + RH_WIN_H,
                    TEX_CEMENT,
                )
            )
    return brushes


# ── North building — hollow shell with windows, entrance, and gable roof ───────
RH_WALL = 16  # wall thickness
RH_WIN_HW = 36  # window half-width
RH_WIN_HH = 44  # window half-height
RH_ENT_HW = 48  # entrance half-width (96-unit wide doorway)
RH_ENT_H = 100  # entrance height

RH_CX = (RH_X1 + RH_X2) // 2  # building X center
RH_NORTH_CY = (RH_NORTH_Y1 + RH_NORTH_Y2) // 2  # building Y center (gable ridge line)

# Window X centers on south/north face: 2 left + 2 right of the entrance gap
rh_wx = [RH_X1 + (RH_CX - RH_ENT_HW - RH_X1) * k // 3 for k in [1, 2]] + [
    (RH_CX + RH_ENT_HW) + (RH_X2 - RH_CX - RH_ENT_HW) * k // 3 for k in [1, 2]
]
# Window Y centers on east/west face: 3 evenly spaced
rh_wy = [RH_NORTH_Y1 + (RH_NORTH_Y2 - RH_NORTH_Y1) * k // 4 for k in [1, 2, 3]]

rh_wz_lo = (KH_FLOOR_H - RH_WIN_HH * 2) // 2  # window sill offset within a floor
rh_wz_hi = rh_wz_lo + RH_WIN_HH * 2  # window head offset within a floor


def nb_wins_xz(wx_list):
    """Window openings (all floors) for X-facing wall (south/north)."""
    return [
        (
            wx - RH_WIN_HW,
            FZ2 + fl * KH_FLOOR_H + rh_wz_lo,
            wx + RH_WIN_HW,
            FZ2 + fl * KH_FLOOR_H + rh_wz_hi,
        )
        for fl in range(RH_FLOORS)
        for wx in wx_list
    ]


def nb_wins_yz(wy_list):
    """Window openings (all floors) for Y-facing wall (east/west)."""
    return [
        (
            wy - RH_WIN_HW,
            FZ2 + fl * KH_FLOOR_H + rh_wz_lo,
            wy + RH_WIN_HW,
            FZ2 + fl * KH_FLOOR_H + rh_wz_hi,
        )
        for fl in range(RH_FLOORS)
        for wy in wy_list
    ]


# South wall (faces bridge) — windows + ground-level entrance
rh_s_openings = nb_wins_xz(rh_wx) + [
    (RH_CX - RH_ENT_HW, FZ2, RH_CX + RH_ENT_HW, FZ2 + RH_ENT_H)
]
BRUSHES.extend(
    layered_wall(
        RH_X1,
        RH_NORTH_Y1,
        FZ2,
        RH_X2,
        RH_NORTH_Y1 + RH_WALL,
        FZ2 + RH_H,
        rh_s_openings,
        "city2_1",
    )
)
# North wall — windows only
BRUSHES.extend(
    layered_wall(
        RH_X1,
        RH_NORTH_Y2 - RH_WALL,
        FZ2,
        RH_X2,
        RH_NORTH_Y2,
        FZ2 + RH_H,
        nb_wins_xz(rh_wx),
        "city2_1",
    )
)
# East wall — windows + ground-level entrance (matches south buildings)
rh_e_openings = nb_wins_yz(rh_wy) + [
    (RH_NORTH_CY - RH_ENT_HW, FZ2, RH_NORTH_CY + RH_ENT_HW, FZ2 + RH_ENT_H)
]
BRUSHES.extend(
    layered_wall_y(
        RH_NORTH_Y1 + RH_WALL,
        RH_X2 - RH_WALL,
        FZ2,
        RH_NORTH_Y2 - RH_WALL,
        RH_X2,
        FZ2 + RH_H,
        rh_e_openings,
        "city2_1",
    )
)
# West wall — windows
BRUSHES.extend(
    layered_wall_y(
        RH_NORTH_Y1 + RH_WALL,
        RH_X1,
        FZ2,
        RH_NORTH_Y2 - RH_WALL,
        RH_X1 + RH_WALL,
        FZ2 + RH_H,
        nb_wins_yz(rh_wy),
        "city2_1",
    )
)
# Ceiling slab
BRUSHES.append(
    box(
        RH_X1,
        RH_NORTH_Y1,
        FZ2 + RH_H,
        RH_X2,
        RH_NORTH_Y2,
        FZ2 + RH_H + RH_WALL,
        "city2_1",
    )
)

# Gable (A-frame) roof — ridge runs N-S at building X center, KH_FLOOR_H above ceiling
RH_EAVE_Z = FZ2 + RH_H + RH_WALL  # top of ceiling slab = eave level
RH_RIDGE_Z = RH_EAVE_Z + KH_FLOOR_H  # ridge apex
RH_SLAB_T = 16  # roof slab thickness at eave
# West slope: flat bottom at eave_z, top slopes up to ridge at nb_cx
BRUSHES.append(
    ramp_slab(
        RH_X1,
        RH_CX,
        RH_NORTH_Y1,
        RH_NORTH_Y2,
        RH_EAVE_Z,
        RH_EAVE_Z,
        RH_EAVE_Z + RH_SLAB_T,
        RH_RIDGE_Z,
        TEX_ROOF,
    )
)
# East slope: top at ridge at nb_cx, slopes down to eave at AB_X2
BRUSHES.append(
    ramp_slab(
        RH_CX,
        RH_X2,
        RH_NORTH_Y1,
        RH_NORTH_Y2,
        RH_EAVE_Z,
        RH_EAVE_Z,
        RH_RIDGE_Z,
        RH_EAVE_Z + RH_SLAB_T,
        TEX_ROOF,
    )
)
# Interior floor — flat ground surface inside the building (covers the hill void)
BRUSHES.append(
    box(
        RH_X1 + RH_WALL,
        RH_NORTH_Y1 + RH_WALL,
        FZ1,
        RH_X2 - RH_WALL,
        RH_NORTH_Y2 - RH_WALL,
        FZ2,
        TEX_GROUND,
        tt=TEX_ROAD,
    )
)


# ── Two south buildings — exact copies of north building, stacked N-S ──────────
# Same X footprint (RH_X1..RH_X2), entrance on east face (faces Charles Street).


def make_south_bldg(by1, by2):
    """Build the south abutment building geometry (walls, roof, windows, entrance)
    between Y positions by1 (south) and by2 (north)."""
    bx1, bx2 = RH_X1, RH_X2
    cx = (bx1 + bx2) // 2
    ent_hw, ent_h = 48, 100
    wx_list = [bx1 + (cx - ent_hw - bx1) * k // 3 for k in [1, 2]] + [
        (cx + ent_hw) + (bx2 - cx - ent_hw) * k // 3 for k in [1, 2]
    ]
    wy_list = [by1 + (by2 - by1) * k // 4 for k in [1, 2, 3]]

    def wxz():
        return [
            (
                wx - RH_WIN_HW,
                FZ2 + fl * KH_FLOOR_H + rh_wz_lo,
                wx + RH_WIN_HW,
                FZ2 + fl * KH_FLOOR_H + rh_wz_hi,
            )
            for fl in range(RH_FLOORS)
            for wx in wx_list
        ]

    def wyz():
        return [
            (
                wy - RH_WIN_HW,
                FZ2 + fl * KH_FLOOR_H + rh_wz_lo,
                wy + RH_WIN_HW,
                FZ2 + fl * KH_FLOOR_H + rh_wz_hi,
            )
            for fl in range(RH_FLOORS)
            for wy in wy_list
        ]

    brushes = []
    # Interior floor
    brushes.append(
        box(
            bx1 + RH_WALL,
            by1 + RH_WALL,
            FZ1,
            bx2 - RH_WALL,
            by2 - RH_WALL,
            FZ2,
            TEX_GROUND,
            tt=TEX_ROAD,
        )
    )
    brushes.extend(
        layered_wall(bx1, by1, FZ2, bx2, by1 + RH_WALL, FZ2 + RH_H, wxz(), "city2_1")
    )
    brushes.extend(
        layered_wall(bx1, by2 - RH_WALL, FZ2, bx2, by2, FZ2 + RH_H, wxz(), "city2_1")
    )
    brushes.extend(
        layered_wall_y(
            by1 + RH_WALL,
            bx1,
            FZ2,
            by2 - RH_WALL,
            bx1 + RH_WALL,
            FZ2 + RH_H,
            wyz(),
            "city2_1",
        )
    )
    cy = (by1 + by2) // 2
    east_openings = wyz() + [(cy - ent_hw, FZ2, cy + ent_hw, FZ2 + ent_h)]
    brushes.extend(
        layered_wall_y(
            by1 + RH_WALL,
            bx2 - RH_WALL,
            FZ2,
            by2 - RH_WALL,
            bx2,
            FZ2 + RH_H,
            east_openings,
            "city2_1",
        )
    )
    brushes.append(box(bx1, by1, FZ2 + RH_H, bx2, by2, FZ2 + RH_H + RH_WALL, "city2_1"))
    eave_z, ridge_z, slab_t = (
        FZ2 + RH_H + RH_WALL,
        FZ2 + RH_H + RH_WALL + KH_FLOOR_H,
        16,
    )
    brushes.append(
        ramp_slab(bx1, cx, by1, by2, eave_z, eave_z, eave_z + slab_t, ridge_z, TEX_ROOF)
    )
    brushes.append(
        ramp_slab(cx, bx2, by1, by2, eave_z, eave_z, ridge_z, eave_z + slab_t, TEX_ROOF)
    )
    return brushes


BRUSHES.extend(make_south_bldg(RH_SOUTH1_Y1, RH_SOUTH1_Y2))
BRUSHES.extend(make_south_bldg(RH_SOUTH2_Y1, RH_SOUTH2_Y2))

# ── Iron fence along east face of west buildings ──────────────────────────
FNC_X1 = RH_X2 + 96  # well clear of building face
FNC_X2 = FNC_X1 + 2  # picket/rail thickness
FNC_H = 96  # fence height
FNC_SPACING = 16  # picket center-to-center
FNC_RAIL = 8  # rail thickness
FNC_TEX = "metal4_4"

for _fy1, _fy2 in [(CS_Y1, CS_Y2)]:
    # Top rail — thin, dropped so pickets extend above it
    BRUSHES.append(
        box(FNC_X1, _fy1, FZ2 + FNC_H - 28, FNC_X2, _fy2, FZ2 + FNC_H - 26, FNC_TEX)
    )
    # Pickets — thin (2 wide) with thick posts (8 wide) every 10th
    _py = _fy1
    _pi = 0
    while _py + 2 <= _fy2:
        _pw = 8 if _pi % 10 == 0 else 2
        BRUSHES.append(box(FNC_X1, _py, FZ2, FNC_X2, _py + _pw, FZ2 + FNC_H, FNC_TEX))
        _py += FNC_SPACING
        _pi += 1


# ════════════════════════════════════════════════════════════════════════════════
# West flat approach removed — arch now starts at world edge
# East flat stub from arch terminus to building entrance — angled southward
_es1 = 0.0  # no shift at the pier (pivot)
_es2 = east_y_shift(WORLD_X2 - WALL_T)  # full southward shift at east world wall
_ep = PB_ARCH_X[4]  # easternmost pier — where the angle begins
# Straight section: arch terminus → easternmost pier
BRUSHES.append(
    box(
        PB_X2,
        PB_Y1,
        PB_DZ1,
        _ep,
        PB_Y2,
        PB_DZ2,
        TEX_STONE,
        tt=TEX_FLOOR,
        tb=TEX_FLOOR,
    )
)
# Angled section: easternmost pier → east world wall
BRUSHES.append(
    shear_box_y(
        _ep,
        PB_Y1,
        PB_DZ1,
        WORLD_X2 - WALL_T,
        PB_Y2,
        PB_DZ2,
        _es1,
        _es2,
        TEX_STONE,
        tt=TEX_FLOOR,
        tb=TEX_FLOOR,
    )
)

for i in range(ARCH_SEGS):
    sx1 = PB_X1 + i * SEG_W
    sx2 = sx1 + SEG_W
    BRUSHES.append(
        ramp_slab(
            sx1,
            sx2,
            PB_Y1,
            PB_Y2,
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
# North east parapet: straight PB_X2→pier, then angled pier→world wall
BRUSHES.append(
    box(PB_X2, PB_Y2 - PB_PAR_W, PB_DZ2, _ep, PB_Y2, PB_DZ2 + PB_PAR_H, TEX_CEMENT)
)
BRUSHES.append(
    shear_box_y(
        _ep,
        PB_Y2 - PB_PAR_W,
        PB_DZ2,
        WORLD_X2 - WALL_T,
        PB_Y2,
        PB_DZ2 + PB_PAR_H,
        _es1,
        _es2,
        TEX_CEMENT,
    )
)  # North east
# South east — gap at WALK_X1..WALK_X2 for walkway connection to building
# West piece (PB_X2→WALK_X1): entirely before pier, straight
BRUSHES.append(
    box(PB_X2, PB_Y1, PB_DZ2, WALK_X1, PB_Y1 + PB_PAR_W, PB_DZ2 + PB_PAR_H, TEX_CEMENT)
)
# East piece (WALK_X2→world wall): straight to pier, then angled
BRUSHES.append(
    box(WALK_X2, PB_Y1, PB_DZ2, _ep, PB_Y1 + PB_PAR_W, PB_DZ2 + PB_PAR_H, TEX_CEMENT)
)
BRUSHES.append(
    shear_box_y(
        _ep,
        PB_Y1,
        PB_DZ2,
        WORLD_X2 - WALL_T,
        PB_Y1 + PB_PAR_W,
        PB_DZ2 + PB_PAR_H,
        _es1,
        _es2,
        TEX_CEMENT,
    )
)

for i in range(ARCH_SEGS):
    sx1 = PB_X1 + i * SEG_W
    sx2 = sx1 + SEG_W
    pb1, pb2 = dtop(sx1), dtop(sx2)  # parapet base follows deck top
    pt1, pt2 = pb1 + PB_PAR_H, pb2 + PB_PAR_H  # parapet top = base + PB_PAR_H
    # North parapet
    BRUSHES.append(
        ramp_slab(sx1, sx2, PB_Y2 - PB_PAR_W, PB_Y2, pb1, pb2, pt1, pt2, TEX_CEMENT)
    )
    # South parapet — omit any segment that overlaps the walkway gap (X=WALK_X1..WALK_X2)
    if not (sx1 < WALK_X2 and sx2 > WALK_X1):
        BRUSHES.append(
            ramp_slab(sx1, sx2, PB_Y1, PB_Y1 + PB_PAR_W, pb1, pb2, pt1, pt2, TEX_CEMENT)
        )

# ── Parapet cement blocks (decorative posts atop parapet walls) ───────────────
PBPB_BLK_HW = 24  # block half-width in X (48 units wide along bridge)
PB_BLK_H = 36  # block height above parapet top
PB_BLK_OVH = 0  # blocks flush with outer bridge wall
PB_BLK_PIR_M = PB_PIL_HW + PBPB_BLK_HW + 4  # clearance from pier centre to block centre


def add_parapet_blocks(
    x_start,
    x_end,
    n,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
    y_shift_fn=None,
):
    """Add evenly-spaced cement blocks atop N and S parapets in a bridge span.

    n_south defaults to n.  South blocks that overlap the walkway gap
    (WALK_X1..WALK_X2) are skipped automatically.
    east_margin_n overrides east_margin for north blocks only.
    y_shift_fn(cx) returns a southward Y offset for angled spans (e.g. east flat span).
    """
    n_s = n if n_south is None else n_south
    mx0 = west_margin if west_margin is not None else PB_BLK_PIR_M
    mx1 = east_margin if east_margin is not None else PB_BLK_PIR_M
    mx1_n = east_margin_n if east_margin_n is not None else mx1
    x0 = x_start + mx0
    x1_n = x_end - mx1_n
    x1_s = x_end - mx1
    for k in range(n):
        cx = x0 + (x1_n - x0) * (k + 1) / (n + 1)
        sy = y_shift_fn(cx) if y_shift_fn else 0.0
        # Use minimum parapet top across block width so block never floats above parapet
        bz = min(dtop(cx - PBPB_BLK_HW), dtop(cx), dtop(cx + PBPB_BLK_HW)) + PB_PAR_H
        BRUSHES.append(
            box(
                cx - PBPB_BLK_HW,
                PB_Y2 - PB_PAR_W + sy,
                bz,
                cx + PBPB_BLK_HW,
                PB_Y2 + PB_BLK_OVH + sy,
                bz + PB_BLK_H,
                TEX_CEMENT,
            )
        )
    for k in range(n_s):
        cx = x0 + (x1_s - x0) * (k + 1) / (n_s + 1)
        sy = y_shift_fn(cx) if y_shift_fn else 0.0
        bz = min(dtop(cx - PBPB_BLK_HW), dtop(cx), dtop(cx + PBPB_BLK_HW)) + PB_PAR_H
        if not (cx - PBPB_BLK_HW < WALK_X2 and cx + PBPB_BLK_HW > WALK_X1):
            BRUSHES.append(
                box(
                    cx - PBPB_BLK_HW,
                    PB_Y1 - PB_BLK_OVH + sy,
                    bz,
                    cx + PBPB_BLK_HW,
                    PB_Y1 + PB_PAR_W + sy,
                    bz + PB_BLK_H,
                    TEX_CEMENT,
                )
            )


# Western span (PB_X1 → PB_ARCH_X[0]): no blocks — open span
# Span 2 (PB_ARCH_X[0] → PB_ARCH_X[1]): eastern span 1, 3 blocks
add_parapet_blocks(PB_ARCH_X[0], PB_ARCH_X[1], 3)
# Middle span (PB_ARCH_X[1] → PB_ARCH_X[2]): 4 blocks
add_parapet_blocks(PB_ARCH_X[1], PB_ARCH_X[2], 4)
# Eastern span 2 (PB_ARCH_X[2] → PB_ARCH_X[3]): 3 blocks
add_parapet_blocks(PB_ARCH_X[2], PB_ARCH_X[3], 3)
# East flat span: west sub-span (PB_X2→PB_ARCH_X[4]) gets 3 north blocks; east sub-span open (matches ref)
add_parapet_blocks(
    PB_X2,
    PB_ARCH_X[4],
    3,
    west_margin=PBPB_BLK_HW + 8,
    n_south=0,
    y_shift_fn=east_y_shift,
)

# ── Decorative squares on parapet outer faces (one per block position) ────────
PB_SQ_HW = 8  # half-width in X (16 units wide)
PB_SQ_HH = 6  # half-height in Z (12 units tall)
PB_SQ_D = 1  # protrusion depth (1 unit proud)


def add_parapet_squares(
    x_start,
    x_end,
    n,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
    y_shift_fn=None,
):
    """Add raised decorative squares on parapet outer faces, same positions as blocks."""
    n_s = n if n_south is None else n_south
    mx0 = west_margin if west_margin is not None else PB_BLK_PIR_M
    mx1 = east_margin if east_margin is not None else PB_BLK_PIR_M
    mx1_n = east_margin_n if east_margin_n is not None else mx1
    x0 = x_start + mx0
    x1_n = x_end - mx1_n
    x1_s = x_end - mx1
    for k in range(n):
        cx = int(x0 + (x1_n - x0) * (k + 1) / (n + 1))
        sy = y_shift_fn(cx) if y_shift_fn else 0.0
        bz = (
            int(min(dtop(cx - PB_SQ_HW), dtop(cx), dtop(cx + PB_SQ_HW)))
            + PB_PAR_H
            + PB_BLK_H // 2
        )
        BRUSHES.append(
            box(
                cx - PB_SQ_HW,
                PB_Y2 + sy,
                bz - PB_SQ_HH,
                cx + PB_SQ_HW,
                PB_Y2 + PB_SQ_D + sy,
                bz + PB_SQ_HH,
                TEX_RAIL,
            )
        )
    for k in range(n_s):
        cx = int(x0 + (x1_s - x0) * (k + 1) / (n_s + 1))
        sy = y_shift_fn(cx) if y_shift_fn else 0.0
        if not (cx - PB_SQ_HW < WALK_X2 and cx + PB_SQ_HW > WALK_X1):
            bz = (
                int(min(dtop(cx - PB_SQ_HW), dtop(cx), dtop(cx + PB_SQ_HW)))
                + PB_PAR_H
                + PB_BLK_H // 2
            )
            BRUSHES.append(
                box(
                    cx - PB_SQ_HW,
                    PB_Y1 - PB_SQ_D + sy,
                    bz - PB_SQ_HH,
                    cx + PB_SQ_HW,
                    PB_Y1 + sy,
                    bz + PB_SQ_HH,
                    TEX_RAIL,
                )
            )


add_parapet_squares(PB_ARCH_X[0], PB_ARCH_X[1], 3)
add_parapet_squares(PB_ARCH_X[1], PB_ARCH_X[2], 4)
add_parapet_squares(PB_ARCH_X[2], PB_ARCH_X[3], 3)
add_parapet_squares(
    PB_X2,
    PB_ARCH_X[4],
    3,
    west_margin=PBPB_BLK_HW + 8,
    n_south=0,
    y_shift_fn=east_y_shift,
)
# South east of walkway: corner blocks only at each side of the opening
# Corner block on east side of walkway opening (west face flush with WALK_X2)
cx_walk_e = WALK_X2 + PBPB_BLK_HW
BRUSHES.append(
    box(
        cx_walk_e - PBPB_BLK_HW,
        PB_Y1 - PB_BLK_OVH,
        PB_DZ2 + PB_PAR_H,
        cx_walk_e + PBPB_BLK_HW,
        PB_Y1 + PB_PAR_W,
        PB_DZ2 + PB_PAR_H + PB_BLK_H,
        TEX_CEMENT,
    )
)
# Extra block on west side of walkway opening (east face flush with WALK_X1)
cx_walk_w = WALK_X1 - PBPB_BLK_HW
BRUSHES.append(
    box(
        cx_walk_w - PBPB_BLK_HW,
        PB_Y1 - PB_BLK_OVH,
        PB_DZ2 + PB_PAR_H,
        cx_walk_w + PBPB_BLK_HW,
        PB_Y1 + PB_PAR_W,
        PB_DZ2 + PB_PAR_H + PB_BLK_H,
        TEX_CEMENT,
    )
)


# ── Parapet handrail tubes (two 4×4 rods stacked, through parapet blocks/pillars) ─
PB_TUBE_HW = 2  # half-width of tube in Y and Z (4 units total)
PB_TUBE_RISE = 10  # raise tubes above parapet top
PB_TUBE_GAP = 12  # vertical gap between tube centres
tube_ny1 = PB_Y2 - PB_PAR_W // 2 - PB_TUBE_HW
tube_ny2 = tube_ny1 + PB_TUBE_HW * 2
tube_sy1 = PB_Y1 + PB_PAR_W // 2 - PB_TUBE_HW
tube_sy2 = tube_sy1 + PB_TUBE_HW * 2

for _tube_z_extra in [PB_TUBE_RISE, PB_TUBE_RISE + PB_TUBE_GAP]:
    for _i in range(ARCH_SEGS):
        _sx1 = PB_X1 + _i * SEG_W
        _sx2 = _sx1 + SEG_W
        _zb1 = dtop(_sx1) + PB_PAR_H + _tube_z_extra
        _zb2 = dtop(_sx2) + PB_PAR_H + _tube_z_extra
        BRUSHES.append(
            ramp_slab(
                _sx1,
                _sx2,
                tube_ny1,
                tube_ny2,
                _zb1,
                _zb2,
                _zb1 + PB_TUBE_HW * 2,
                _zb2 + PB_TUBE_HW * 2,
                TEX_RAIL,
            )
        )
        if not (_sx1 < WALK_X2 and _sx2 > WALK_X1):
            BRUSHES.append(
                ramp_slab(
                    _sx1,
                    _sx2,
                    tube_sy1,
                    tube_sy2,
                    _zb1,
                    _zb2,
                    _zb1 + PB_TUBE_HW * 2,
                    _zb2 + PB_TUBE_HW * 2,
                    TEX_RAIL,
                )
            )
    # East flat section — straight PB_X2→pier, angled pier→world wall
    _tbz = PB_DZ2 + PB_PAR_H + _tube_z_extra
    _x_east_end = WORLD_X2 - WALL_T
    # North tube: straight then angled
    BRUSHES.append(
        box(PB_X2, tube_ny1, _tbz, _ep, tube_ny2, _tbz + PB_TUBE_HW * 2, TEX_RAIL)
    )
    BRUSHES.append(
        shear_box_y(
            _ep,
            tube_ny1,
            _tbz,
            _x_east_end,
            tube_ny2,
            _tbz + PB_TUBE_HW * 2,
            _es1,
            _es2,
            TEX_RAIL,
        )
    )
    # South tube west piece (PB_X2→WALK_X1): before pier, straight
    BRUSHES.append(
        box(PB_X2, tube_sy1, _tbz, WALK_X1, tube_sy2, _tbz + PB_TUBE_HW * 2, TEX_RAIL)
    )
    # South tube east piece (WALK_X2→world wall): straight to pier, then angled
    BRUSHES.append(
        box(WALK_X2, tube_sy1, _tbz, _ep, tube_sy2, _tbz + PB_TUBE_HW * 2, TEX_RAIL)
    )
    BRUSHES.append(
        shear_box_y(
            _ep,
            tube_sy1,
            _tbz,
            _x_east_end,
            tube_sy2,
            _tbz + PB_TUBE_HW * 2,
            _es1,
            _es2,
            TEX_RAIL,
        )
    )


# ── Pillar posts (stone piers with arches) ───────────────────────────────────
# Each pillar position now features a narrow arched pier supporting the deck.
# Arch openings span most of the bridge N-S width (PB_Y2=136, bridge=272 units)
# rin = half-width of clear opening; rout = outer radius of arch ring
PB_PIL_OUTER_R = (140, 72)  # narrower outer piers flanking road
PB_PIL_INNER_R = (160, 84)  # slightly wider inner piers
PB_PIL_CENTR_R = (160, 90)  # widest opening at centre
if SHOW_SUPPORTS:
    for px in PB_ARCH_X:
        if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
            continue
        pdeck = dtop(px)  # deck surface at this X
        ppar = pdeck + PB_PAR_H  # parapet top
        ppil = ppar + PB_PIL_EXTRA  # pillar post top
        pcap = ppil + PB_PIL_CAP_H  # cap slab top
        cy_n = PB_Y2 - PB_PAR_W // 2  # north cap centre Y
        cy_s = PB_Y1 + PB_PAR_W // 2  # south cap centre Y

        # Width of the pier in X (matches pillar post width)
        x1, x2 = px - PB_PIL_HW, px + PB_PIL_HW

        # Arch opening varies by pillar type (outer / inner / centre)
        if px == 0:
            a_rout, a_rin = PB_PIL_CENTR_R
        elif abs(px) == max(abs(p) for p in PB_ARCH_X):
            a_rout, a_rin = PB_PIL_OUTER_R
        else:
            a_rout, a_rin = PB_PIL_INNER_R
        a_stilt = int(pdeck) - a_rout - FZ2 - 16
        if a_stilt < 0:
            # Arch would overshoot the bridge bottom; cap rout so the crown
            # lands exactly at ceil_z (bridge deck underside).
            a_rout = int(pdeck) - FZ2 - 16
            a_stilt = 0

        # Pin outer pier wall to exactly match the pillar tops above deck.
        # Cap a_rout so the arch ring never extends past PB_Y2 + PB_PIL_OVERHANG;
        # if rout was trimmed, recompute stilt so the arch crown still meets the deck.
        _max_rout = PB_Y2 + PB_PIL_OVERHANG
        if a_rout > _max_rout:
            a_rout = _max_rout
            a_stilt = int(pdeck) - a_rout - FZ2 - 16
        _arch_overhang = 0  # rout already reaches exactly the desired extent

        # Ramped plinth: outer piers ramp up on their outward face so players
        # can run up from outside. East piers: high east side; west piers: high west side.
        # Central / road piers get a flat plinth.
        if px > 0:
            # East of road — ramp slopes up toward east (low at x1, high at x2)
            _base_ramp = (FZ2 + PB_PIL_BASE_H, FZ2 + PB_PIL_BASE_RAMP_H)
        elif px < 0:
            # West of road — ramp slopes up toward west (high at x1, low at x2)
            _base_ramp = (FZ2 + PB_PIL_BASE_RAMP_H, FZ2 + PB_PIL_BASE_H)
        else:
            _base_ramp = None  # centre pier — flat plinth

        # Add pier structure — easternmost pier gets a square opening, rest are arched
        if px == max(PB_ARCH_X):
            # Overhang must reach PB_Y2+PB_PIL_OVERHANG to match pillar tops above deck
            _sq_overhang = PB_Y2 + PB_PIL_OVERHANG - a_rin
            BRUSHES.extend(
                square_wall(
                    x1,
                    x2,
                    PB_Y1,
                    PB_Y2,
                    FZ2,
                    int(pdeck) - 16,
                    a_rin,
                    TEX_PILLAR,
                    overhang=_sq_overhang,
                    base_h=PB_PIL_BASE_H,
                )
            )
        else:
            BRUSHES.extend(
                arch_wall(
                    x1,
                    x2,
                    PB_Y1,
                    PB_Y2,
                    FZ2,
                    int(pdeck) - 16,
                    a_rin,
                    a_rout,
                    A_SEGS,
                    TEX_PILLAR,
                    stilt_h=a_stilt,
                    overhang=_arch_overhang,
                    base_h=PB_PIL_BASE_H,
                    base_ramp=_base_ramp,
                    base_cap_h=0 if px == min(PB_ARCH_X) else PB_PIL_BASE_CAP_H,
                    base_cap_tex=TEX_CEMENT,
                    base_cap_ovh=PB_PIL_BASE_CAP_OVH,
                )
            )

        # Pillar tops (above deck, extend PB_PIL_OVERHANG past bridge edges and inward)
        _pil_out = PB_Y2 + PB_PIL_OVERHANG  # always overhang past bridge edge
        # North pillar top
        BRUSHES.append(
            box(
                px - PB_PIL_HW,
                PB_Y2 - PB_PAR_W - PB_PIL_OVERHANG,
                pdeck,
                px + PB_PIL_HW,
                _pil_out,
                ppil,
                TEX_PILLAR,
            )
        )

        # South pillar top
        BRUSHES.append(
            box(
                px - PB_PIL_HW,
                -_pil_out,
                pdeck,
                px + PB_PIL_HW,
                PB_Y1 + PB_PAR_W + PB_PIL_OVERHANG,
                ppil,
                TEX_PILLAR,
            )
        )

        # Fill gap between pier top and deck surface in the overhang zone
        pier_top_z = int(pdeck) - 16
        BRUSHES.append(
            box(x1, PB_Y2, pier_top_z, x2, _pil_out, pdeck, TEX_PILLAR)
        )  # north
        BRUSHES.append(
            box(x1, -_pil_out, pier_top_z, x2, PB_Y1, pdeck, TEX_PILLAR)
        )  # south

        # Cement cap slab + pyramid on top of each stone pillar post
        _cap_x1, _cap_x2 = px - PB_PIL_PYR_W, px + PB_PIL_PYR_W
        _n_cy1 = (
            PB_Y2 - PB_PAR_W - PB_PIL_OVERHANG - PB_PIL_CAP_IN_OVH
        )  # inward past pillar post
        _n_cy2 = PB_Y2 + PB_PIL_CAP_OUT_OVH  # outward (north/road-facing) edge
        _s_cy1 = PB_Y1 - PB_PIL_CAP_OUT_OVH  # outward (south/road-facing) edge
        _s_cy2 = (
            PB_Y1 + PB_PAR_W + PB_PIL_OVERHANG + PB_PIL_CAP_IN_OVH
        )  # inward past pillar post
        # Cap slabs (flat cement base)
        BRUSHES.append(box(_cap_x1, _n_cy1, ppil, _cap_x2, _n_cy2, pcap, TEX_CEMENT))
        BRUSHES.append(box(_cap_x1, _s_cy1, ppil, _cap_x2, _s_cy2, pcap, TEX_CEMENT))
        # Pyramids on top of cap slabs
        BRUSHES.append(
            pyramid(
                _cap_x1, _n_cy1, pcap, _cap_x2, _n_cy2, pcap + PB_PIL_PYR_H, TEX_CEMENT
            )
        )
        BRUSHES.append(
            pyramid(
                _cap_x1, _s_cy1, pcap, _cap_x2, _s_cy2, pcap + PB_PIL_PYR_H, TEX_CEMENT
            )
        )
        # Torch bases above pyramid apex — narrow post + wide cup
        _apex = pcap + PB_PIL_PYR_H
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
        if px == min(PB_ARCH_X):
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
TEX_ARCH_ROUT = 136  # Fills the bridge width (updated to match PB_Y2=136)
TEX_ARCH_STILT = 96  # Height of straight sides before arch springs
TEX_ARCH_W = 32  # Thickness of the arch in X

for _ex, _ayc in [
    (WORLD_X1 + WALL_T, 0.0),  # west arch — centred at y=0
    (WORLD_X2 - WALL_T - TEX_ARCH_W, _es2),  # east arch — shifted south with span
]:
    _xb, _xf = _ex, _ex + TEX_ARCH_W
    _sprz = PB_DZ2 + TEX_ARCH_STILT  # Z where arch curve begins
    _post_w = TEX_ARCH_ROUT - TEX_ARCH_RIN  # post thickness in Y
    # South post (extends to ground floor, with overhang)
    BRUSHES.append(
        box(
            _xb,
            PB_Y1 - PB_PIL_OVERHANG + _ayc,
            FZ2,
            _xf,
            PB_Y1 + _post_w + _ayc,
            _sprz,
            TEX_PILLAR,
        )
    )
    # North post (extends to ground floor, with overhang)
    BRUSHES.append(
        box(
            _xb,
            PB_Y2 - _post_w + _ayc,
            FZ2,
            _xf,
            PB_Y2 + PB_PIL_OVERHANG + _ayc,
            _sprz,
            TEX_PILLAR,
        )
    )
    # Arch ring segments (rounded top, with overhang)
    _seg = 180.0 / A_SEGS
    for i in range(A_SEGS):
        BRUSHES.append(
            arch_seg(
                _xb,
                _xf,
                _ayc,
                float(_sprz),
                TEX_ARCH_RIN,
                TEX_ARCH_ROUT + PB_PIL_OVERHANG,
                i * _seg,
                (i + 1) * _seg,
                TEX_PILLAR,
            )
        )


# ════════════════════════════════════════════════════════════════════════════════
# WALKWAY — flat bridge from south edge to building 2nd floor entrance
# X=-64..64, Y=PB_Y1..KH_Y2; flat at WALK_ZT1 = WALK_ZT2
# ════════════════════════════════════════════════════════════════════════════════
if KH_WALKWAY_ENABLED:
    wk_zb1 = WALK_ZT1 - KH_WALL  # slab bottom at bridge end
    wk_zb2 = WALK_ZT2 - KH_WALL  # slab bottom at building end
    BRUSHES.append(
        ramp_slab_y(
            WALK_X1,
            WALK_X2,
            PB_Y1,
            KH_Y2,
            wk_zb1,
            wk_zb2,
            WALK_ZT1,
            WALK_ZT2,
            TEX_CEMENT,
            tt=TEX_FLOOR,
        )
    )
    # Side rails slope with the ramp (32-unit thick walls so tubes sit centred)
    PBCS_WALK_WALL = 32
    BRUSHES.append(
        ramp_slab_y(
            WALK_X1 - PBCS_WALK_WALL,
            WALK_X1,
            PB_Y1,
            KH_Y2,
            wk_zb1,
            wk_zb2,
            WALK_ZT1 + PB_PAR_H,
            WALK_ZT2 + PB_PAR_H,
            TEX_CEMENT,
        )
    )
    BRUSHES.append(
        ramp_slab_y(
            WALK_X2,
            WALK_X2 + PBCS_WALK_WALL,
            PB_Y1,
            KH_Y2,
            wk_zb1,
            wk_zb2,
            WALK_ZT1 + PB_PAR_H,
            WALK_ZT2 + PB_PAR_H,
            TEX_CEMENT,
        )
    )
    # Handrail tubes along walkway sides, centred in the wall thickness
    for _tube_z_extra in [PB_TUBE_RISE, PB_TUBE_RISE + PB_TUBE_GAP]:
        _tbz = WALK_ZT1 + PB_PAR_H + _tube_z_extra
        _ww_cx = PBCS_WALK_WALL // 2
        BRUSHES.append(
            box(
                WALK_X1 - _ww_cx - PB_TUBE_HW,
                KH_Y2,
                _tbz,
                WALK_X1 - _ww_cx + PB_TUBE_HW,
                PB_Y1,
                _tbz + PB_TUBE_HW * 2,
                TEX_RAIL,
            )
        )
        BRUSHES.append(
            box(
                WALK_X2 + _ww_cx - PB_TUBE_HW,
                KH_Y2,
                _tbz,
                WALK_X2 + _ww_cx + PB_TUBE_HW,
                PB_Y1,
                _tbz + PB_TUBE_HW * 2,
                TEX_RAIL,
            )
        )


# ════════════════════════════════════════════════════════════════════════════════
# WALKWAY SUPPORT STRUCTURE — cement crossbeam + 5 piers under south end of walkway
# Mirrors real-life support visible under the KH bridge approach (ref: bridge01)
# ════════════════════════════════════════════════════════════════════════════════
if KH_WALKWAY_ENABLED:
    # Position just under the south edge of the bridge deck
    _sup_yc = PB_Y1  # south edge of bridge = -136
    _sup_hw = 16  # half-depth of beam/piers (N-S)
    _sup_y1 = _sup_yc - _sup_hw
    _sup_y2 = _sup_yc + _sup_hw
    # Beam sits just below the walkway slab bottom
    _beam_zt = WALK_ZT1 - KH_WALL  # bottom of walkway slab at bridge end
    _beam_h = 20
    _beam_zb = _beam_zt - _beam_h
    # Span between the two bridge arch piers flanking the walkway (east span)
    _beam_x1 = PB_ARCH_X[3]  # = 1246 (KH_PIER_X)
    _beam_x2 = PB_ARCH_X[4]  # = 2206
    # Horizontal crossbeam
    BRUSHES.append(
        box(_beam_x1, _sup_y1, _beam_zb, _beam_x2, _sup_y2, _beam_zt, TEX_CEMENT)
    )
    # 5 sub-piers: 3 evenly west of walkway gap, 2 evenly east — none in the gap
    _rail_x1 = WALK_X1 - PBCS_WALK_WALL  # west rail outer edge
    _rail_x2 = WALK_X2 + PBCS_WALK_WALL  # east rail outer edge
    _west_piers = [
        int(_beam_x1 + (_rail_x1 - _beam_x1) * f) for f in (0.28, 0.63, 0.93)
    ]
    _east_piers = [int(_rail_x2 + (_beam_x2 - _rail_x2) * f) for f in (0.25, 0.75)]
    _pier_xs = _west_piers + _east_piers
    _pier_hw = 20
    for _px in _pier_xs:
        BRUSHES.append(
            box(
                _px - _pier_hw,
                _sup_y1,
                FZ2,
                _px + _pier_hw,
                _sup_y2,
                _beam_zb,
                TEX_CEMENT,
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
if KH_GROUND_Z > FZ2:
    _west_ramp_x1 = ROAD_X2 + CS_WALK_W  # east edge of east sidewalk = 336
    _west_ramp_x2 = KH_X1  # ramp rises all the way to building west face
    _east_flat_x2 = WORLD_X2 - WALL_T  # flat hilltop extends to east world wall
    # Solid hill fill under the entire building footprint — split to exclude indent pockets
    # so indents are recessed at all heights down to ground level
    for _px1, _py1, _px2, _py2 in [
        (KH_X1 + INDENT, KH_Y1, KH_X2 - INDENT, KH_Y1 + INDENT),  # south strip
        (KH_X1, KH_Y1 + INDENT, KH_X2, KH_Y2 - INDENT),  # middle strip
        (KH_X1 + 2 * INDENT, KH_Y2 - INDENT, KH_X2 - INDENT, KH_Y2),  # north strip
    ]:
        BRUSHES.append(box(_px1, _py1, FZ2, _px2, _py2, KH_GROUND_Z, TEX_WALL))
    # NW indent floor — ground level and ground texture (open recessed pocket)
    BRUSHES.append(
        box(
            KH_X1,
            KH_Y2 - INDENT,
            FZ1,
            KH_X1 + 2 * INDENT,
            KH_Y2,
            FZ2 + CS_WALK_H,
            TEX_GROUND,
        )
    )
    # (No flat east fill — the back road section provides its own sloped fill there)
    # West hill — ramp from sidewalk height at Charles St up to building ground level
    _west_ramp_north = KH_Y2 - INDENT * 3 // 4
    BRUSHES.append(
        ramp_slab(
            _west_ramp_x1,
            _west_ramp_x2,
            WORLD_Y1 + WALL_T,
            _west_ramp_north,
            FZ1,
            FZ1,
            FZ2 + CS_WALK_H,
            KH_GROUND_Z,
            TEX_GROUND,
        )
    )
    # Flat ground from ramp north edge to building face (west of KH_X1)
    BRUSHES.append(
        box(
            _west_ramp_x1,
            _west_ramp_north,
            FZ1,
            _west_ramp_x2,
            KH_Y2,
            FZ2 + CS_WALK_H,
            TEX_GROUND,
        )
    )
    # South terrain fill — flat ground at building level behind south wall to east world edge
    BRUSHES.append(
        box(
            KH_X1,
            WORLD_Y1 + WALL_T,
            FZ1,
            WORLD_X2 - WALL_T,
            KH_Y1,
            KH_GROUND_Z,
            TEX_WALL,
        )
    )
    # Flat ground in front of KH (north face to Ennis sidewalk edge), flush with sidewalk
    # Split around KH entrance strip (KH_ENT_X1..KH_ENT_X2) to let cement apron show
    _kh_ent_x1 = KH_ORIG_CX - 64
    _kh_ent_x2 = KH_ORIG_CX + 64
    _east_ramp_x1 = _kh_ent_x2  # east of entrance opening
    _east_ramp_x2 = KH_X2 - INDENT  # west edge of NE indent
    _east_ramp_depth = 128  # N-S length of sloped sidewalk
    for _fx1, _fx2 in [
        (_west_ramp_x1, _kh_ent_x1),
        (_kh_ent_x2, KH_BR_CORRIDOR_X1),
        (KH_BR_CORRIDOR_X2, WORLD_X2 - WALL_T),
    ]:
        BRUSHES.append(
            box(_fx1, KH_Y2, FZ1, _fx2, EP_SW_EDGE, FZ2 + CS_WALK_H, TEX_GROUND)
        )
    # East of entrance: flat platform at walkway level + steps going east down to ground
    _ep_x1 = _east_ramp_x1  # KH_ENT_X2
    _ep_x2 = KH_X2
    _ep_plat_depth = 96  # N-S platform depth (wider)
    _ep_n_steps = 4
    _ep_step_rise = (KH_GROUND_Z - (FZ2 + CS_WALK_H)) // _ep_n_steps  # = 22
    _ep_step_depth = 24
    _ep_steps_w = _ep_n_steps * _ep_step_depth  # = 96
    _ep_step_x1 = _ep_x2 - _ep_steps_w  # steps recessed, end flush with east wall
    # Flat platform at KH_GROUND_Z (west of steps)
    BRUSHES.append(
        box(
            _ep_x1,
            KH_Y2,
            FZ1,
            _ep_step_x1,
            KH_Y2 + _ep_plat_depth,
            KH_GROUND_Z,
            TEX_CEMENT,
        )
    )
    # Steps going east (downhill in X), flush with KH east wall
    for _si in range(_ep_n_steps):
        _sz = KH_GROUND_Z - (_si + 1) * _ep_step_rise
        _sx1 = _ep_step_x1 + _si * _ep_step_depth
        _sx2 = _sx1 + _ep_step_depth
        BRUSHES.append(
            box(_sx1, KH_Y2, FZ1, _sx2, KH_Y2 + _ep_plat_depth, _sz, TEX_CEMENT)
        )
    # Small cement connector from step bottom to east sidewalk (across back road corridor)
    BRUSHES.append(
        box(
            KH_X2,
            KH_Y2,
            FZ1,
            KH_BR_CORRIDOR_X2,
            KH_Y2 + _ep_plat_depth,
            FZ2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )

_kh_brush_start = len(BRUSHES)  # checkpoint — trimmed below if KH_ENABLED is False

# ══════════════════════════════════════════════════════════════════════════════
# BACK ROAD — east of Knott Hall, slopes south to meet the back of the building
# Sidewalks with rounded north entrance corners (like Ennis Drive)
# Road slopes from Z=0 at the north entrance to KH_GROUND_Z at the back.
# ══════════════════════════════════════════════════════════════════════════════
KH_BR_HW = 128  # back road half-width (256-unit carriageway, like Ennis)
KH_BRCS_WALK_W = CS_WALK_W  # sidewalk width = 80 units (matches Charles St sidewalks)
KH_BRCS_CRN_R = CS_WALK_W  # corner radius = sidewalk width
KH_BRCS_CRN_SEGS = CS_CRN_SEGS  # 12 arc segments = 90°

# ── X extents (road runs N-S, east of building east wall) ──
KH_BR_WS_X1 = KH_X2  # west sidewalk west = building east wall = 1906
KH_BR_WS_X2 = KH_X2 + KH_BRCS_WALK_W  # west sidewalk east = road west edge = 1986
KH_BR_RD_X1 = KH_BR_WS_X2  # road west edge = 1986
KH_BR_RD_X2 = KH_BR_RD_X1 + 2 * KH_BR_HW  # road east edge = 2242
KH_BR_ES_X1 = KH_BR_RD_X2  # east sidewalk west = 2242
KH_BR_ES_X2 = KH_BR_RD_X2 + KH_BRCS_WALK_W  # east sidewalk east = 2322

# ── Y extents (north entrance → south back-wall) ──
KH_BR_Y1 = KH_Y1  # south end: back of building = -1888
KH_BR_Y2 = KH_Y2  # north end: north face of building = -256

# ── Elevation: road surface rises gradually from north (Z=0) to south (Z=hill top) ──
KH_BR_ZT_N = FZ2  # road top at north entrance = 0
KH_BR_ZT_S = KH_GROUND_Z  # road top at south/back     = 80

# Road surface — 2-unit textured overlay riding on sloped fill
BRUSHES.append(
    ramp_slab_y(
        KH_BR_RD_X1,
        KH_BR_RD_X2,
        KH_BR_Y1,
        KH_BR_Y2,
        FZ1,
        FZ1,
        KH_BR_ZT_S + 2,
        KH_BR_ZT_N + 2,
        TEX_ROAD,
        tt=TEX_ROAD,
    )
)
# Road fill — solid ground under road surface
BRUSHES.append(
    ramp_slab_y(
        KH_BR_RD_X1,
        KH_BR_RD_X2,
        KH_BR_Y1,
        KH_BR_Y2,
        FZ1,
        FZ1,
        KH_BR_ZT_S,
        KH_BR_ZT_N,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)

# West sidewalk (strip between building east wall and road) — slopes with road
BRUSHES.append(
    ramp_slab_y(
        KH_BR_WS_X1,
        KH_BR_WS_X2,
        KH_BR_Y1,
        KH_BR_Y2,
        FZ1,
        FZ1,
        KH_BR_ZT_S + CS_WALK_H,
        KH_BR_ZT_N + CS_WALK_H,
        TEX_CEMENT,
        tt=TEX_CEMENT,
    )
)
# West sidewalk fill
BRUSHES.append(
    ramp_slab_y(
        KH_BR_WS_X1,
        KH_BR_WS_X2,
        KH_BR_Y1,
        KH_BR_Y2,
        FZ1,
        FZ1,
        KH_BR_ZT_S,
        KH_BR_ZT_N,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)

# East sidewalk — slopes with road
BRUSHES.append(
    ramp_slab_y(
        KH_BR_ES_X1,
        KH_BR_ES_X2,
        KH_BR_Y1,
        KH_BR_Y2,
        FZ1,
        FZ1,
        KH_BR_ZT_S + CS_WALK_H,
        KH_BR_ZT_N + CS_WALK_H,
        TEX_CEMENT,
        tt=TEX_CEMENT,
    )
)
# East sidewalk fill
BRUSHES.append(
    ramp_slab_y(
        KH_BR_ES_X1,
        KH_BR_ES_X2,
        KH_BR_Y1,
        KH_BR_Y2,
        FZ1,
        FZ1,
        KH_BR_ZT_S,
        KH_BR_ZT_N,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)

# Terrain east of east sidewalk — south flat + sloped main section matching sidewalk
# South extension: flat at hill level
BRUSHES.append(
    box(
        KH_BR_ES_X2,
        WORLD_Y1 + WALL_T,
        FZ1,
        WORLD_X2 - WALL_T,
        KH_BR_Y1,
        KH_BR_ZT_S + CS_WALK_H,
        TEX_GROUND,
    )
)
# Main back road section: slopes with the sidewalk (88 at south → 8 at north)
BRUSHES.append(
    ramp_slab_y(
        KH_BR_ES_X2,
        WORLD_X2 - WALL_T,
        KH_BR_Y1,
        KH_BR_Y2,
        FZ1,
        FZ1,
        KH_BR_ZT_S + CS_WALK_H,
        KH_BR_ZT_N + CS_WALK_H,
        TEX_GROUND,
        tt=TEX_GROUND,
    )
)

# ── South extension — road + east sidewalk behind Knott Hall to world edge ──
BRUSHES.append(
    box(
        KH_X1,
        WORLD_Y1 + WALL_T,
        FZ1,
        KH_BR_ES_X1,
        KH_BR_Y1,
        KH_BR_ZT_S + 2,
        TEX_ROAD,
    )
)
BRUSHES.append(
    box(
        KH_BR_ES_X1,
        WORLD_Y1 + WALL_T,
        FZ1,
        KH_BR_ES_X2,
        KH_BR_Y1,
        KH_BR_ZT_S + CS_WALK_H,
        TEX_CEMENT,
    )
)

# ── Flat extension north from Knott Hall to Ennis south sidewalk ──────────────
KH_BR_EXT_Y1 = KH_BR_Y2  # = -256 (north face of building)
KH_BR_EXT_Y2 = EP_Y - EP_HW - CS_WALK_W  # = 328 (Ennis south sidewalk edge)

# Flat road surface
BRUSHES.append(
    box(KH_BR_RD_X1, KH_BR_EXT_Y1, FZ2, KH_BR_RD_X2, KH_BR_EXT_Y2, FZ2 + 2, TEX_ROAD)
)
# West sidewalk
BRUSHES.append(
    box(
        KH_BR_WS_X1,
        KH_BR_EXT_Y1,
        FZ2,
        KH_BR_WS_X2,
        KH_BR_EXT_Y2,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)
# East sidewalk
BRUSHES.append(
    box(
        KH_BR_ES_X1,
        KH_BR_EXT_Y1,
        FZ2,
        KH_BR_ES_X2,
        KH_BR_EXT_Y2,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)
# Terrain east of east sidewalk — flush with sidewalk top
BRUSHES.append(
    box(
        KH_BR_ES_X2,
        KH_BR_EXT_Y1,
        FZ1,
        WORLD_X2 - WALL_T,
        KH_BR_EXT_Y2,
        FZ2 + CS_WALK_H,
        TEX_GROUND,
    )
)

# Road patch filling the gap between back road end (Y=328) and Ennis road (Y=408)
# (This was previously the Ennis south sidewalk; now it's part of the road junction)
BRUSHES.append(
    box(
        KH_BR_RD_X1,
        KH_BR_EXT_Y2,
        FZ2,
        KH_BR_RD_X2,
        EP_Y - EP_HW,
        FZ2 + 2,
        TEX_ROAD,
    )
)

# ── Rounded corners where back road meets Ennis south (inside the junction) ───
# Centers at the back-road-facing (south) corners so the curved face points toward
# the back road — matching the Charles/Ennis corner style.
# West junction corner: center at SW corner (1906, 328), arc sweeps 0°→90°
KH_BR_JCX_W = KH_BR_WS_X1  # = 1906 (SW corner of cut square)
KH_BR_JCY = EP_Y - EP_HW  # = 408 (Ennis south road edge)
BRUSHES.append(
    box(KH_BR_WS_X1, KH_BR_EXT_Y2, FZ2, KH_BR_RD_X1, KH_BR_JCY, FZ2 + 2, TEX_ROAD)
)
for _i in range(KH_BRCS_CRN_SEGS):
    _a0 = math.radians(0 + _i * 90 / KH_BRCS_CRN_SEGS)
    _a1 = math.radians(0 + (_i + 1) * 90 / KH_BRCS_CRN_SEGS)
    _px0 = KH_BR_JCX_W + KH_BRCS_CRN_R * math.cos(_a0)
    _py0 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(_a0)
    _px1 = KH_BR_JCX_W + KH_BRCS_CRN_R * math.cos(_a1)
    _py1 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(_a1)
    BRUSHES.append(
        tri_prism(
            KH_BR_JCX_W,
            KH_BR_EXT_Y2,
            _px0,
            _py0,
            _px1,
            _py1,
            FZ2,
            FZ2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )

# East junction corner: center at SE corner (2322, 328), arc sweeps 90°→180°
KH_BR_JCX_E = KH_BR_ES_X2  # = 2322 (SE corner of cut square)
BRUSHES.append(
    box(KH_BR_ES_X1, KH_BR_EXT_Y2, FZ2, KH_BR_ES_X2, KH_BR_JCY, FZ2 + 2, TEX_ROAD)
)
for _i in range(KH_BRCS_CRN_SEGS):
    _a0 = math.radians(90 + _i * 90 / KH_BRCS_CRN_SEGS)
    _a1 = math.radians(90 + (_i + 1) * 90 / KH_BRCS_CRN_SEGS)
    _px0 = KH_BR_JCX_E + KH_BRCS_CRN_R * math.cos(_a0)
    _py0 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(_a0)
    _px1 = KH_BR_JCX_E + KH_BRCS_CRN_R * math.cos(_a1)
    _py1 = KH_BR_EXT_Y2 + KH_BRCS_CRN_R * math.sin(_a1)
    BRUSHES.append(
        tri_prism(
            KH_BR_JCX_E,
            KH_BR_EXT_Y2,
            _px0,
            _py0,
            _px1,
            _py1,
            FZ2,
            FZ2 + CS_WALK_H,
            TEX_CEMENT,
        )
    )

bix1 = KH_X1 + KH_WALL  # interior west
bix2 = KH_X2 - KH_WALL  # interior east
biy1 = KH_Y1 + KH_WALL  # interior south = -784
biy2 = KH_Y2 - KH_WALL  # interior north = -272

# Entrance doorway — pinned to original building centre, not current KH_CX
KH_ENT_X1, KH_ENT_X2 = KH_ORIG_CX - 64, KH_ORIG_CX + 64

# ── Entrance staircase ────────────────────────────────────────────────────────
KH_STEP_N = 5
KH_STEP_DEPTH = 24  # tread depth
KH_STAIR_OFFSET = 384  # distance from north wall to stair base
_step_base_z = FZ2 + CS_WALK_H  # steps start at apron surface height (8)
step_rise = (KH_GROUND_Z - _step_base_z) * 1 // KH_STEP_N  # distributed rise per step

# Flat cement platform between building and stairs
BRUSHES.append(
    box(
        KH_ENT_X1,
        KH_Y2,
        FZ2,
        KH_ENT_X2,
        KH_Y2 + KH_STAIR_OFFSET,
        KH_GROUND_Z,
        TEX_CEMENT,
    )
)

stair_y0 = KH_Y2 + KH_STAIR_OFFSET  # south edge of staircase
stair_y_end = stair_y0 + KH_STEP_N * KH_STEP_DEPTH  # north end of stairs (ground level)
for _si in range(KH_STEP_N):
    _sz2 = _step_base_z + (KH_GROUND_Z - _step_base_z) * (_si + 1) // KH_STEP_N
    _sy_n = stair_y0 + (KH_STEP_N - _si) * KH_STEP_DEPTH
    BRUSHES.append(
        box(
            KH_ENT_X1,
            stair_y0,
            _step_base_z,
            KH_ENT_X2,
            _sy_n,
            _sz2,
            TEX_CEMENT,
            tt=TEX_CEMENT,
        )
    )

# Cement sidewalk from stair base to Ennis south sidewalk — flush with ground fill
BRUSHES.append(
    box(
        KH_ENT_X1,
        stair_y_end,
        FZ1,
        KH_ENT_X2,
        EP_SW_EDGE,
        FZ2 + CS_WALK_H,
        TEX_CEMENT,
    )
)

# ── Stair side caps (cement cheek walls) ─────────────────────────────────────
# Solid sloped cement walls on each side of the staircase, top follows stair slope.
_cap_w = 24  # cheek wall thickness (X)
_cap_raise = 16  # extra height above stair slope
for _cx1, _cx2 in [
    (KH_ENT_X1 - _cap_w, KH_ENT_X1),  # west cheek
    (KH_ENT_X2, KH_ENT_X2 + _cap_w),  # east cheek
]:
    BRUSHES.append(
        ramp_slab_y(
            _cx1,
            _cx2,
            stair_y0,
            stair_y_end,
            FZ1,
            FZ1,
            KH_GROUND_Z + _cap_raise,
            _step_base_z + _cap_raise,
            TEX_CEMENT,
        )
    )

# ── Stair railings ────────────────────────────────────────────────────────────
KH_RAIL_H = 72  # stair handrail height
KH_RAIL_TEX = "metal4_4"
KH_RAIL_SPACING = 16
_post_w = 8  # post face width (X) — wide flat-facing
_post_d = 2  # post depth (Y)
_horiz_ext = 20  # length of level rail extension at top and bottom
for _rx_base, _is_west in [(KH_ENT_X1, True), (KH_ENT_X2, False)]:
    _z_top_plat = KH_GROUND_Z + KH_RAIL_H - 28
    _z_top_end = _step_base_z + KH_RAIL_H - 28
    _rx1 = _rx_base - _post_w if _is_west else _rx_base
    _rx2 = _rx_base if _is_west else _rx_base + _post_w

    # Sloped cross rail
    BRUSHES.append(
        ramp_slab_y(
            _rx1,
            _rx2,
            stair_y0,
            stair_y_end,
            _z_top_plat,
            _z_top_end,
            _z_top_plat + 2,
            _z_top_end + 2,
            KH_RAIL_TEX,
        )
    )

    # Horizontal extension at top (level with platform floor)
    BRUSHES.append(
        box(
            _rx1,
            stair_y0 - _horiz_ext,
            _z_top_plat,
            _rx2,
            stair_y0,
            _z_top_plat + 2,
            KH_RAIL_TEX,
        )
    )
    # Horizontal extension at bottom (level with apron floor)
    BRUSHES.append(
        box(
            _rx1,
            stair_y_end,
            _z_top_end,
            _rx2,
            stair_y_end + _horiz_ext,
            _z_top_end + 2,
            KH_RAIL_TEX,
        )
    )

    # Posts — wide flat-facing
    for _ry, _gz in [
        (stair_y0, KH_GROUND_Z),
        (stair_y_end, _step_base_z),
    ]:
        BRUSHES.append(
            box(_rx1, _ry, _gz, _rx2, _ry + _post_d, _gz + KH_RAIL_H - 26, KH_RAIL_TEX)
        )

# Lift shaft east of entrance: 16 units east of KH_ENT_X2, 128 wide
stx1, stx2 = KH_ENT_X2 + 16, KH_ENT_X2 + 16 + 128  # = 1516, 1644
sty1, sty2 = biy2 - 128, biy2  # Y: -400 to -272
# West stairwell extents defined after INDENT below

# ── Outer walls ──────────────────────────────────────────────────────────────
KHRH_WIN_HALF = 24  # half-width of recessed corner windows
KH_MULLION_W = 12  # mullion width
KH_MULLION_PRO = 12  # mullion protrusion depth

wstx2 = KH_ENT_X1 - 16  # west stairwell east edge
wstx1 = bix1 + 2 * INDENT  # west stairwell west edge — flush with NW indent corner
wsty2 = sty2  # stairwell north edge (same as east shaft)
wsty1 = biy2 - 256  # stairwell south edge — double depth (256 vs 128)

# South wall — mirrors north wall: indented SW/SE corners with recessed windows
# Main south face — hallway openings cut through at each floor level
s_wall_openings = [
    (
        KH_ENT_X1,
        KH_GROUND_Z + fl * KH_FLOOR_H + KH_WALL,
        KH_ENT_X2,
        KH_GROUND_Z + (fl + 1) * KH_FLOOR_H,
    )
    for fl in range(KH_FLOORS)
]
BRUSHES.extend(
    layered_wall(
        KH_X1 + INDENT,
        KH_Y1,
        KH_GROUND_Z,
        KH_X2 - INDENT,
        KH_Y1 + KH_WALL,
        KH_Z2,
        s_wall_openings,
        TEX_WALL,
    )
)
# SW Indentation inner walls — recessed back wall with centered 48-unit window
sw_win_cx = KH_X1 + INDENT // 2  # = 1306
BRUSHES.extend(
    layered_wall(
        KH_X1,
        KH_Y1 + INDENT - KH_WALL,
        FZ1,
        KH_X1 + INDENT,
        KH_Y1 + INDENT,
        KH_Z2,
        [
            (
                sw_win_cx - KHRH_WIN_HALF,
                KH_GROUND_Z + KH_FLOOR_H,
                sw_win_cx + KHRH_WIN_HALF,
                KH_Z2,
            )
        ],
        TEX_WALL,
    )
)
BRUSHES.append(
    box(
        KH_X1 + INDENT - KH_WALL,
        KH_Y1,
        FZ1,
        KH_X1 + INDENT,
        KH_Y1 + INDENT,
        KH_Z2,
        TEX_WALL,
    )
)
# SE Indentation inner walls — recessed back wall with centered 48-unit window
se_win_cx = KH_X2 - INDENT // 2  # = 1866
BRUSHES.extend(
    layered_wall(
        KH_X2 - INDENT,
        KH_Y1 + INDENT - KH_WALL,
        FZ1,
        KH_X2,
        KH_Y1 + INDENT,
        KH_Z2,
        [
            (
                se_win_cx - KHRH_WIN_HALF,
                KH_GROUND_Z + KH_FLOOR_H,
                se_win_cx + KHRH_WIN_HALF,
                KH_Z2,
            )
        ],
        TEX_WALL,
    )
)
BRUSHES.append(
    box(
        KH_X2 - INDENT,
        KH_Y1,
        FZ1,
        KH_X2 - INDENT + KH_WALL,
        KH_Y1 + INDENT,
        KH_Z2,
        TEX_WALL,
    )
)
# South mullions — protrude outward (south, -Y)
for _mx in [sw_win_cx - KHRH_WIN_HALF - KH_MULLION_W, sw_win_cx + KHRH_WIN_HALF]:
    BRUSHES.append(
        box(
            _mx,
            KH_Y1 + INDENT - KH_WALL,
            KH_GROUND_Z + KH_FLOOR_H,
            _mx + KH_MULLION_W,
            KH_Y1 + INDENT + KH_MULLION_PRO,
            KH_Z2,
            TEX_CEMENT,
        )
    )
for _mx in [se_win_cx - KHRH_WIN_HALF - KH_MULLION_W, se_win_cx + KHRH_WIN_HALF]:
    BRUSHES.append(
        box(
            _mx,
            KH_Y1 + INDENT - KH_WALL,
            KH_GROUND_Z + KH_FLOOR_H,
            _mx + KH_MULLION_W,
            KH_Y1 + INDENT + KH_MULLION_PRO,
            KH_Z2,
            TEX_CEMENT,
        )
    )
# Horizontal mullions — SW and SE south-face indentation windows, matching east/west walls
for _wx in [sw_win_cx, se_win_cx]:
    for _fl in range(1, KH_FLOORS):
        _mz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H // 2
        BRUSHES.append(
            box(
                _wx - KHRH_WIN_HALF,
                KH_Y1 + INDENT - KH_WALL,
                _mz,
                _wx + KHRH_WIN_HALF,
                KH_Y1 + INDENT + KH_MULLION_PRO,
                _mz + 4,
                TEX_RAIL,
            )
        )
# Floor-level mullions — SW and SE south-face windows
for _wx in [sw_win_cx, se_win_cx]:
    for _fl in range(1, KH_FLOORS + 1):
        _fz = KH_GROUND_Z + _fl * KH_FLOOR_H
        BRUSHES.append(
            box(
                _wx - KHRH_WIN_HALF,
                KH_Y1 + INDENT - KH_WALL,
                _fz - 4 if _fl > 0 else KH_GROUND_Z,
                _wx + KHRH_WIN_HALF,
                KH_Y1 + INDENT + KH_MULLION_PRO,
                (_fz if _fl > 0 else KH_GROUND_Z + 4),
                TEX_RAIL,
            )
        )
# North-West Indentation (Corner Notch)
# North wall — faces bridge; ground entrance + 2nd-floor walkway opening
door_n = [
    (KH_ENT_X1, KH_GROUND_Z, KH_ENT_X2, KH_GROUND_Z + KH_FLOOR_H)
]  # ground entrance
door_2 = [
    (KH_ENT_X1, WALK_ZT2, KH_ENT_X2, KH_GROUND_Z + KH_FLOOR_H * 2)
]  # walkway entrance
win_n = [
    (KH_ORIG_CX - 48, KH_GROUND_Z + KH_FLOOR_H * 2, KH_ORIG_CX - 6, KH_Z2),
    (KH_ORIG_CX + 6, KH_GROUND_Z + KH_FLOOR_H * 2, KH_ORIG_CX + 48, KH_Z2),
]  # two window slots centered over entrance doorway, split by center mullion
BRUSHES.extend(
    layered_wall(
        KH_X1 + 2 * INDENT,
        KH_Y2 - KH_WALL,
        KH_GROUND_Z,
        KH_X2 - INDENT,
        KH_Y2,
        KH_Z2,
        door_n + door_2 + win_n,
        TEX_WALL,
    )
)

# NW Indentation — 2×INDENT wide (extends west to KH_X1), two windows side by side
nw_win_cx1 = KH_X1 + INDENT // 2  # west window = 1246 (pier-aligned)
nw_win_cx2 = KH_X1 + INDENT + INDENT // 2  # east window = 1326
BRUSHES.extend(
    layered_wall(
        KH_X1,
        KH_Y2 - INDENT,
        FZ1,
        KH_X1 + 2 * INDENT,
        KH_Y2 - INDENT + KH_WALL,
        KH_Z2,
        [
            (
                nw_win_cx1 - KHRH_WIN_HALF,
                KH_GROUND_Z + KH_FLOOR_H,
                nw_win_cx1 + KHRH_WIN_HALF,
                KH_Z2,
            ),
            (
                nw_win_cx2 - KHRH_WIN_HALF,
                KH_GROUND_Z + KH_FLOOR_H,
                nw_win_cx2 + KHRH_WIN_HALF,
                KH_Z2,
            ),
        ],
        TEX_WALL,
    )
)
BRUSHES.append(
    box(
        KH_X1 + 2 * INDENT - KH_WALL,
        KH_Y2 - INDENT,
        FZ1,
        KH_X1 + 2 * INDENT,
        KH_Y2,
        KH_Z2,
        TEX_WALL,
    )
)

# NE Indentation inner walls (mirror of NW) — recessed back wall has a centered 48-unit window
ne_win_cx = KH_X2 - INDENT // 2  # = 1866
BRUSHES.extend(
    layered_wall(
        KH_X2 - INDENT,
        KH_Y2 - INDENT,
        FZ1,
        KH_X2,
        KH_Y2 - INDENT + KH_WALL,
        KH_Z2,
        [
            (
                ne_win_cx - KHRH_WIN_HALF,
                KH_GROUND_Z + KH_FLOOR_H,
                ne_win_cx + KHRH_WIN_HALF,
                KH_Z2,
            )
        ],
        TEX_WALL,
    )
)
BRUSHES.append(
    box(
        KH_X2 - INDENT,
        KH_Y2 - INDENT,
        FZ1,
        KH_X2 - INDENT + KH_WALL,
        KH_Y2,
        KH_Z2,
        TEX_WALL,
    )
)

# Front mullions — protruding sfloor3_2 posts on each side of the recessed windows
# and the narrow vertical window on the main north face. All protrude 12 units outward.
# NW recessed windows: mullions for both (west and east window in the wide NW indentation)
for _mx in [
    nw_win_cx1 - KHRH_WIN_HALF - KH_MULLION_W,
    nw_win_cx1 + KHRH_WIN_HALF,
    nw_win_cx2 - KHRH_WIN_HALF - KH_MULLION_W,
    nw_win_cx2 + KHRH_WIN_HALF,
]:
    BRUSHES.append(
        box(
            _mx,
            KH_Y2 - INDENT - KH_MULLION_PRO,
            KH_GROUND_Z + KH_FLOOR_H,
            _mx + KH_MULLION_W,
            KH_Y2 - INDENT + KH_WALL,
            KH_Z2,
            TEX_CEMENT,
        )
    )
# NE recessed window: mullions just outside the opening so player can fit through
for _mx in [ne_win_cx - KHRH_WIN_HALF - KH_MULLION_W, ne_win_cx + KHRH_WIN_HALF]:
    BRUSHES.append(
        box(
            _mx,
            KH_Y2 - INDENT - KH_MULLION_PRO,
            KH_GROUND_Z + KH_FLOOR_H,
            _mx + KH_MULLION_W,
            KH_Y2 - INDENT + KH_WALL,
            KH_Z2,
            TEX_CEMENT,
        )
    )
# Main front wall window win_n: mullions on each side and center post
win_n_x1, win_n_x2 = KH_ORIG_CX - 48, KH_ORIG_CX + 48
win_n_mid = KH_ORIG_CX - 6  # left edge of center mullion
for _mx in [win_n_x1 - KH_MULLION_W, win_n_mid, win_n_x2]:
    BRUSHES.append(
        box(
            _mx,
            KH_Y2 - KH_WALL,
            KH_GROUND_Z + KH_FLOOR_H * 2,
            _mx + KH_MULLION_W,
            KH_Y2 + KH_MULLION_PRO,
            KH_Z2,
            TEX_CEMENT,
        )
    )

# ── "Marion Burk Knott Hall" sign plaque — north face, 2nd floor level ───────
# Protruding cement slab, sized to fit pixel-font lettering
_sign_text = "MARION BURK KNOTT HALL"
_sign_px_w, _sign_px_h = 2, 4
_sign_char_w = (4 + 1) * _sign_px_w
_sign_total_w = len(_sign_text) * _sign_char_w - _sign_px_w  # = 436
_sign_hw = _sign_total_w // 2 + 4  # 4 unit padding each side = 222
_sign_cx = KH_X2 - INDENT - _sign_hw  # east edge flush with wall end
_sign_zb = KH_GROUND_Z + KH_FLOOR_H * 2 + 20  # just above 2nd floor line
_sign_zt = _sign_zb + 48  # 48 units tall
BRUSHES.append(
    box(
        _sign_cx - _sign_hw,
        KH_Y2,
        _sign_zb,
        _sign_cx + _sign_hw,
        KH_Y2 + 6,
        _sign_zt,
        TEX_CEMENT,
    )
)
# Letter brushes deferred — render_text_flat defined below

# ── Brutalist Fins (All Exposed Facades) — currently disabled ─────────────────

# East wall — three 120-unit wide floor-to-ceiling windows, matching west side
# Shared window layout variables (used for both east and west walls)
ww_half = 120
ww_wall_y1, ww_wall_y2 = KH_Y1, KH_Y2 - INDENT
ww_quarter = (ww_wall_y2 - ww_wall_y1) // 4
ww_c1 = ww_wall_y1 + ww_quarter
ww_c2 = ww_wall_y1 + 2 * ww_quarter
ww_c3 = ww_wall_y1 + 3 * ww_quarter
ww_div_w = 12
ww_protrude = 12
BRUSHES.extend(
    layered_wall_y(
        ww_wall_y1,
        KH_X2 - KH_WALL,
        KH_GROUND_Z,
        ww_wall_y2,
        KH_X2,
        KH_Z2,
        [
            (ww_c1 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c1 + ww_half, KH_Z2),
            (ww_c2 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c2 + ww_half, KH_Z2),
            (ww_c3 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c3 + ww_half, KH_Z2),
        ],
        TEX_WALL,
    )
)
# Vertical mullions — protrude 12 units east of wall face
for _wc in [ww_c1, ww_c2, ww_c3]:
    for _dy in [
        _wc - ww_half,  # left edge
        _wc - 48,  # interior left
        _wc + 36,  # interior right
        _wc + ww_half - ww_div_w,  # right edge
    ]:
        BRUSHES.append(
            box(
                KH_X2 - KH_WALL,
                _dy,
                KH_GROUND_Z + KH_FLOOR_H,
                KH_X2 + ww_protrude,
                _dy + ww_div_w,
                KH_Z2,
                TEX_CEMENT,
            )
        )

# Horizontal mullions — centered in each floor span for contrast, players still fit through
# Mid-floor Z leaves ~85 units clearance each side (player height = 56)
for _wc in [ww_c1, ww_c2, ww_c3]:
    for _fl in range(1, KH_FLOORS):
        _mz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H // 2
        BRUSHES.append(
            box(
                KH_X2 - KH_WALL,
                _wc - ww_half,
                _mz,
                KH_X2 + ww_protrude,
                _wc + ww_half,
                _mz + 4,
                TEX_RAIL,
            )
        )
# Floor-level mullions — sill at base of each floor (floors 1+), lintel at top of each floor
for _wc in [ww_c1, ww_c2, ww_c3]:
    for _fl in range(1, KH_FLOORS + 1):
        _fz = KH_GROUND_Z + _fl * KH_FLOOR_H
        BRUSHES.append(
            box(
                KH_X2 - KH_WALL,
                _wc - ww_half,
                _fz - 4 if _fl > 0 else KH_GROUND_Z,
                KH_X2 + ww_protrude,
                _wc + ww_half,
                (_fz if _fl > 0 else KH_GROUND_Z + 4),
                TEX_RAIL,
            )
        )

# West wall — three 120-unit wide floor-to-ceiling windows, evenly spread
BRUSHES.extend(
    layered_wall_y(
        ww_wall_y1,
        KH_X1,
        KH_GROUND_Z,
        ww_wall_y2,
        KH_X1 + KH_WALL,
        KH_Z2,
        [
            (ww_c1 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c1 + ww_half, KH_Z2),
            (ww_c2 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c2 + ww_half, KH_Z2),
            (ww_c3 - ww_half, KH_GROUND_Z + KH_FLOOR_H, ww_c3 + ww_half, KH_Z2),
        ],
        TEX_WALL,
    )
)
# Vertical mullions — protrude 12 units west of wall face
# 2 interior + 2 side mullions per window (4 total each)
for _wc in [ww_c1, ww_c2, ww_c3]:
    for _dy in [
        _wc - ww_half,  # left edge
        _wc - 48,  # interior left
        _wc + 36,  # interior right
        _wc + ww_half - ww_div_w,  # right edge
    ]:
        BRUSHES.append(
            box(
                KH_X1 - ww_protrude,
                _dy,
                KH_GROUND_Z + KH_FLOOR_H,
                KH_X1 + KH_WALL,
                _dy + ww_div_w,
                KH_Z2,
                TEX_CEMENT,
            )
        )

# Horizontal mullions — west wall, matching east
for _wc in [ww_c1, ww_c2, ww_c3]:
    for _fl in range(1, KH_FLOORS):
        _mz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H // 2
        BRUSHES.append(
            box(
                KH_X1 - ww_protrude,
                _wc - ww_half,
                _mz,
                KH_X1 + KH_WALL,
                _wc + ww_half,
                _mz + 4,
                TEX_RAIL,
            )
        )
# Floor-level mullions — west wall
for _wc in [ww_c1, ww_c2, ww_c3]:
    for _fl in range(1, KH_FLOORS + 1):
        _fz = KH_GROUND_Z + _fl * KH_FLOOR_H
        BRUSHES.append(
            box(
                KH_X1 - ww_protrude,
                _wc - ww_half,
                _fz - 4 if _fl > 0 else KH_GROUND_Z,
                KH_X1 + KH_WALL,
                _wc + ww_half,
                (_fz if _fl > 0 else KH_GROUND_Z + 4),
                TEX_RAIL,
            )
        )

# Horizontal mullions — win_n narrow slot window on main north face (floors 2–3)
for _fl in range(2, KH_FLOORS):
    _mz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H // 2
    BRUSHES.append(
        box(
            win_n_x1,
            KH_Y2 - KH_WALL,
            _mz,
            win_n_x2,
            KH_Y2 + KH_MULLION_PRO,
            _mz + 4,
            TEX_RAIL,
        )
    )
# Floor-level mullions — win_n
for _fl in range(2, KH_FLOORS + 1):
    _fz = KH_GROUND_Z + _fl * KH_FLOOR_H
    if _fz <= KH_Z2:
        BRUSHES.append(
            box(
                win_n_x1,
                KH_Y2 - KH_WALL,
                _fz - 4 if _fl > 0 else KH_GROUND_Z,
                win_n_x2,
                KH_Y2 + KH_MULLION_PRO,
                (_fz if _fl > 0 else KH_GROUND_Z + 4),
                TEX_RAIL,
            )
        )
for _wx, _wh in [
    (nw_win_cx1, KHRH_WIN_HALF),
    (nw_win_cx2, KHRH_WIN_HALF),
    (ne_win_cx, KHRH_WIN_HALF),
]:
    for _fl in range(1, KH_FLOORS):
        _mz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H // 2
        BRUSHES.append(
            box(
                _wx - _wh,
                KH_Y2 - INDENT - KH_MULLION_PRO,
                _mz,
                _wx + _wh,
                KH_Y2 - INDENT + KH_WALL,
                _mz + 4,
                TEX_RAIL,
            )
        )
# Floor-level mullions — NW/NE recessed north-face windows
for _wx, _wh in [
    (nw_win_cx1, KHRH_WIN_HALF),
    (nw_win_cx2, KHRH_WIN_HALF),
    (ne_win_cx, KHRH_WIN_HALF),
]:
    for _fl in range(1, KH_FLOORS + 1):
        _fz = KH_GROUND_Z + _fl * KH_FLOOR_H
        BRUSHES.append(
            box(
                _wx - _wh,
                KH_Y2 - INDENT - KH_MULLION_PRO,
                _fz - 4 if _fl > 0 else KH_GROUND_Z,
                _wx + _wh,
                KH_Y2 - INDENT + KH_WALL,
                (_fz if _fl > 0 else KH_GROUND_Z + 4),
                TEX_RAIL,
            )
        )

# Roof — open above lift shaft, clipped for NW indentation
BRUSHES.append(
    box(
        KH_X1,
        KH_Y1,
        KH_Z2,
        wstx1,
        KH_Y2 - INDENT,
        KH_Z2 + KH_WALL,
        TEX_FLOOR_KH,
    )
)  # far-west bulk
BRUSHES.append(
    box(
        KH_X1 + 2 * INDENT,
        KH_Y2 - INDENT,
        KH_Z2,
        wstx1,
        KH_Y2,
        KH_Z2 + KH_WALL,
        TEX_FLOOR_KH,
    )
)  # far-west north-strip
BRUSHES.append(
    box(wstx1, KH_Y1, KH_Z2, wstx2, wsty1, KH_Z2 + KH_WALL, TEX_FLOOR_KH)
)  # south of west stairwell
BRUSHES.append(
    box(wstx1, wsty2, KH_Z2, wstx2, KH_Y2, KH_Z2 + KH_WALL, TEX_FLOOR_KH)
)  # north of west stairwell
BRUSHES.append(
    box(wstx2, KH_Y1, KH_Z2, stx1, KH_Y2, KH_Z2 + KH_WALL, TEX_FLOOR_KH)
)  # between shafts (no indent — interior)
BRUSHES.append(
    box(
        stx2,
        KH_Y1,
        KH_Z2,
        KH_X2,
        KH_Y2 - INDENT,
        KH_Z2 + KH_WALL,
        TEX_FLOOR_KH,
    )
)  # east bulk
BRUSHES.append(
    box(
        stx2,
        KH_Y2 - INDENT,
        KH_Z2,
        KH_X2 - INDENT,
        KH_Y2,
        KH_Z2 + KH_WALL,
        TEX_FLOOR_KH,
    )
)  # east north-strip (NE cutout)
BRUSHES.append(
    box(stx1, KH_Y1, KH_Z2, stx2, sty1, KH_Z2 + KH_WALL, TEX_FLOOR_KH)
)  # south of shaft
BRUSHES.append(
    box(stx1, sty2, KH_Z2, stx2, KH_Y2, KH_Z2 + KH_WALL, TEX_FLOOR_KH)
)  # north of shaft (closes roof over north wall above shaft)

# ── Interior floor slabs (floors 0-3, lift shaft opening in center-north) ────
# Floor 0 (ground): full slab with no shaft opening, clipped for NW indentation
sz0 = KH_GROUND_Z
st0 = sz0 + KH_WALL
BRUSHES.append(box(KH_X1, KH_Y1, sz0, KH_X2, KH_Y2 - INDENT, st0, TEX_FLOOR_KH))
BRUSHES.append(
    box(
        KH_X1 + 2 * INDENT,
        KH_Y2 - INDENT,
        sz0,
        KH_X2 - INDENT,
        KH_Y2,
        st0,
        TEX_FLOOR_KH,
    )
)

for _f in range(1, KH_FLOORS):
    _sz = KH_GROUND_Z + _f * KH_FLOOR_H
    _st = _sz + KH_WALL
    # South bulk — full width up to stairwell's south wall
    BRUSHES.append(box(bix1, biy1, _sz, bix2, wsty1, _st, TEX_FLOOR_KH))
    # Stairwell south extension (wsty1..sty1): floor on either side, stairwell open
    BRUSHES.append(box(bix1, wsty1, _sz, wstx1, sty1, _st, TEX_FLOOR_KH))
    BRUSHES.append(box(wstx2, wsty1, _sz, bix2, sty1, _st, TEX_FLOOR_KH))
    # North zone (sty1..biy2): west of stairwell, clipped for NW indentation
    BRUSHES.append(box(bix1, sty1, _sz, wstx1, KH_Y2 - INDENT, _st, TEX_FLOOR_KH))
    BRUSHES.append(
        box(bix1 + 2 * INDENT, KH_Y2 - INDENT, _sz, wstx1, biy2, _st, TEX_FLOOR_KH)
    )
    # Between west stairwell and east shaft
    BRUSHES.append(box(wstx2, sty1, _sz, stx1, biy2, _st, TEX_FLOOR_KH))
    # East of shaft, clipped for NE indentation
    BRUSHES.append(box(stx2, sty1, _sz, bix2, KH_Y2 - INDENT, _st, TEX_FLOOR_KH))
    BRUSHES.append(
        box(stx2, KH_Y2 - INDENT, _sz, bix2 - INDENT, biy2, _st, TEX_FLOOR_KH)
    )

# ── Elevator Shaft Enclosure ──────────────────────────────────────────────
# Walls around the lift shaft (stx1..stx2, sty1..sty2)
shaft_wall = 8
# Door opening dimensions per floor (used for both wall openings and func_door entities)
shaft_door_h = KH_FLOOR_H  # door height matches floor-to-floor height
shaft_doors_w = [
    (
        sty1 + 16,
        KH_GROUND_Z + _f * KH_FLOOR_H,
        sty2 - 16,
        KH_GROUND_Z + _f * KH_FLOOR_H + shaft_door_h,
    )
    for _f in range(KH_FLOORS)
]

# Shaft North wall (internal, solid)
BRUSHES.append(box(stx1, sty2, KH_GROUND_Z, stx2, sty2 + shaft_wall, KH_Z2, TEX_WALL))
# Shaft South wall (internal, solid)
BRUSHES.append(box(stx1, sty1 - shaft_wall, KH_GROUND_Z, stx2, sty1, KH_Z2, TEX_WALL))
# Shaft West wall (internal, openings for each floor's door — flush with hallway east wall and shaft interior)
BRUSHES.extend(
    layered_wall_y(
        sty1,
        KH_ENT_X2,
        KH_GROUND_Z,
        sty2,
        stx1,
        KH_Z2,
        shaft_doors_w,
        TEX_WALL,
    )
)
# Shaft East wall (internal)
BRUSHES.append(box(stx2, sty1, KH_GROUND_Z, stx2 + shaft_wall, sty2, KH_Z2, TEX_WALL))

# ── West Stairwell Enclosure ──────────────────────────────────────────────────
# Walls around the west stairwell (wstx1..wstx2, wsty1..wsty2)
west_shaft_doors_w = [
    (
        sty1 + 16,  # same Y extents as east shaft doorway
        KH_GROUND_Z + _f * KH_FLOOR_H,
        sty2 - 16,
        KH_GROUND_Z + _f * KH_FLOOR_H + shaft_door_h,
    )
    for _f in range(KH_FLOORS)
]

# West stairwell North wall (internal, solid)
BRUSHES.append(
    box(wstx1, wsty2, KH_GROUND_Z, wstx2, wsty2 + shaft_wall, KH_Z2, TEX_WALL)
)
# West stairwell South wall (internal, solid)
BRUSHES.append(
    box(wstx1, wsty1 - shaft_wall, KH_GROUND_Z, wstx2, wsty1, KH_Z2, TEX_WALL)
)
# West stairwell East wall (internal, openings for each floor's door — flush both sides)
BRUSHES.extend(
    layered_wall_y(
        wsty1,
        wstx2,
        KH_GROUND_Z,
        wsty2,
        KH_ENT_X1,
        KH_Z2,
        west_shaft_doors_w,
        TEX_WALL,
    )
)
# West stairwell West wall (internal, solid)
BRUSHES.append(
    box(wstx1 - shaft_wall, wsty1, KH_GROUND_Z, wstx1, wsty2, KH_Z2, TEX_WALL)
)

# ── West Stairwell — Switchback Staircase ─────────────────────────────────────
# Stairs compressed to the shaft centre (192 u wide), leaving 88-unit flanks for
# half-floor platforms on the east and west sides.
#
# North lane (wst_midY..wsty2): enter east door, walk WEST, rise z0 → z_mid.
# West platform at z_mid (full shaft Y, 88 u wide) — turn-around landing.
# South lane (wsty1..wst_midY): walk EAST, rise z_mid → z_top.
#
# Step 0 of north lane and step 7 of south lane extend east to wstx2 so the
# door at each floor connects directly to the staircase.
# Loop runs KH_FLOORS times (fl 0→4) — top flight exits onto building roof.
WST_HALF_N = 8
WST_STEP_R = 10  # rise per step (≤ 18-unit Quake limit)
WST_TREAD_X = 24  # compressed tread depth: 8 × 24 = 192
PLAT_H = 8  # platform slab thickness
stair_cx = (wstx1 + wstx2) // 2  # shaft X centre
stair_x1 = stair_cx - WST_HALF_N * WST_TREAD_X // 2  # west edge of stairs
stair_x2 = stair_x1 + WST_HALF_N * WST_TREAD_X  # east edge of stairs
wst_midY = (wsty1 + wsty2) // 2  # Y lane divider = -400

for _fl in range(KH_FLOORS):
    _z0 = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_WALL  # floor surface Z
    _z_mid = _z0 + WST_HALF_N * WST_STEP_R  # half-floor Z (_z0 + 80)
    _z_top = _z0 + KH_FLOOR_H  # next floor surface Z (= exit level)

    # Entrance landing — flush with hallway floor, east of stair band (north lane).
    BRUSHES.append(
        box(stair_x2, wst_midY, _z0 - PLAT_H, wstx2, wsty2, _z0, TEX_FLOOR_KH)
    )
    # Exit landing — flush with next floor, east of stair band (south lane).
    BRUSHES.append(
        box(stair_x2, wsty1, _z_top - PLAT_H, wstx2, wst_midY, _z_top, TEX_FLOOR_KH)
    )

    # North lane: individual treads ascending westward (stair_x2 → stair_x1).
    for _i in range(WST_HALF_N):
        _sx_e = stair_x2 - _i * WST_TREAD_X
        _sx_w = stair_x2 - (_i + 1) * WST_TREAD_X
        _sz1 = _z0 + _i * WST_STEP_R
        BRUSHES.append(
            box(
                _sx_w,
                wst_midY,
                _sz1,
                _sx_e,
                wsty2,
                _sz1 + WST_STEP_R,
                TEX_WALL,
                tt=TEX_FLOOR_KH,
            )
        )

    # Half-floor west platform: turn-around landing, full shaft Y depth.
    BRUSHES.append(
        box(wstx1, wsty1, _z_mid - PLAT_H, stair_x1, wsty2, _z_mid, TEX_FLOOR_KH)
    )

    # South lane: individual treads ascending eastward (stair_x1 → stair_x2).
    for _i in range(WST_HALF_N):
        _sx_w = stair_x1 + _i * WST_TREAD_X
        _sx_e = _sx_w + WST_TREAD_X
        _sz1 = _z_mid + _i * WST_STEP_R
        BRUSHES.append(
            box(
                _sx_w,
                wsty1,
                _sz1,
                _sx_e,
                wst_midY,
                _sz1 + WST_STEP_R,
                TEX_WALL,
                tt=TEX_FLOOR_KH,
            )
        )


# ── West Stairwell — Iron Railings ────────────────────────────────────────────
# 2 end posts + 1 sloped cross rail per half-flight, central divider (wst_midY).
# Posts sit OUTSIDE the stair band (on the entrance area and west platform) so
# they never land on a tread.  Cross rail spans the full stair band between them.
WST_RAIL_H = 72  # handrail height above landing surface (bottom of rail = 68u, clears 56u player)
WST_POST_W = 4  # square post cross-section
WST_RAIL_T = 4  # cross-rail bar thickness

for _fl in range(KH_FLOORS):
    _z0 = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_WALL
    _z_mid = _z0 + WST_HALF_N * WST_STEP_R
    _z_top = _z_mid + WST_HALF_N * WST_STEP_R

    # ── North lane — south face (wst_midY) ────────────────────────────────
    # Lower post: east of stair band, in the entrance area
    BRUSHES.append(
        box(
            stair_x2,
            wst_midY,
            _z0,
            stair_x2 + WST_POST_W,
            wst_midY + WST_POST_W,
            _z0 + WST_RAIL_H,
            TEX_RAIL,
        )
    )
    # Upper post: west of stair band, on the west platform
    BRUSHES.append(
        box(
            stair_x1 - WST_POST_W,
            wst_midY,
            _z_mid,
            stair_x1,
            wst_midY + WST_POST_W,
            _z_mid + WST_RAIL_H,
            TEX_RAIL,
        )
    )
    # Sloped cross rail along center divider (high at west, low at east)
    BRUSHES.append(
        ramp_slab(
            stair_x1,
            stair_x2,
            wst_midY,
            wst_midY + WST_RAIL_T,
            _z_mid + WST_RAIL_H - WST_RAIL_T,
            _z0 + WST_RAIL_H - WST_RAIL_T,
            _z_mid + WST_RAIL_H,
            _z0 + WST_RAIL_H,
            TEX_RAIL,
        )
    )

    # ── South lane — north face (wst_midY) ────────────────────────────────
    # Lower post: west of stair band, on the west platform
    BRUSHES.append(
        box(
            stair_x1 - WST_POST_W,
            wst_midY - WST_POST_W,
            _z_mid,
            stair_x1,
            wst_midY,
            _z_mid + WST_RAIL_H,
            TEX_RAIL,
        )
    )
    # Upper post: east of stair band, in the entrance area
    BRUSHES.append(
        box(
            stair_x2,
            wst_midY - WST_POST_W,
            _z_top,
            stair_x2 + WST_POST_W,
            wst_midY,
            _z_top + WST_RAIL_H,
            TEX_RAIL,
        )
    )
    # Sloped cross rail along center divider (low at west, high at east)
    BRUSHES.append(
        ramp_slab(
            stair_x1,
            stair_x2,
            wst_midY - WST_RAIL_T,
            wst_midY,
            _z_mid + WST_RAIL_H - WST_RAIL_T,
            _z_top + WST_RAIL_H - WST_RAIL_T,
            _z_mid + WST_RAIL_H,
            _z_top + WST_RAIL_H,
            TEX_RAIL,
        )
    )


# Partition Y splits vary per floor so each floor has different room proportions.
room_splits = [-1072, -950, -1200, -850, -1300]  # partition Y per floor

wx1, wx2 = bix1, KH_ENT_X1 - KH_WALL  # west room X extents (1282..1506)
ex1, ex2 = KH_ENT_X2 + KH_WALL, bix2  # east room X extents (1666..1890)
wxc = (wx1 + wx2) // 2  # west room X center = 1394
exc = (ex1 + ex2) // 2  # east room X center = 1778

# Collect door openings in hallway walls across all floors
w_hall_openings = [
    (sty1, KH_GROUND_Z, sty2, KH_Z2)
]  # west stairwell gap — doorway size
e_hall_openings = [(sty1, KH_GROUND_Z, sty2, KH_Z2)]  # shaft gap always open

for _fl in range(KH_FLOORS):
    _fz1 = KH_GROUND_Z + _fl * KH_FLOOR_H
    _fz_surf = _fz1 + KH_WALL  # top of floor slab
    _split = room_splits[_fl]
    _sr_yc = (biy1 + _split) // 2  # south room Y center
    _nr_yc = (_split + KH_WALL + biy2) // 2  # north room Y center
    _dz2 = _fz_surf + 96  # door top
    w_hall_openings += [
        (_sr_yc - 32, _fz_surf, _sr_yc + 32, _dz2),
        (_nr_yc - 32, _fz_surf, _nr_yc + 32, _dz2),
    ]
    e_hall_openings += [
        (_sr_yc - 32, _fz_surf, _sr_yc + 32, _dz2),
        (_nr_yc - 32, _fz_surf, _nr_yc + 32, _dz2),
    ]

# West hallway wall with room door openings
BRUSHES.extend(
    layered_wall_y(
        biy1,
        KH_ENT_X1 - KH_WALL,
        KH_GROUND_Z,
        biy2,
        KH_ENT_X1,
        KH_Z2,
        w_hall_openings,
        TEX_WALL,
    )
)
# East hallway wall with room door openings + shaft opening
BRUSHES.extend(
    layered_wall_y(
        biy1,
        KH_ENT_X2,
        KH_GROUND_Z,
        biy2,
        KH_ENT_X2 + KH_WALL,
        KH_Z2,
        e_hall_openings,
        TEX_WALL,
    )
)

# Partition walls per floor (divide each side into 2 rooms, with connecting door)
for _fl in range(KH_FLOORS):
    _fz1 = KH_GROUND_Z + _fl * KH_FLOOR_H
    _fz2 = _fz1 + KH_FLOOR_H
    _fz_surf = _fz1 + KH_WALL
    _split = room_splits[_fl]
    _sp_y2 = _split + KH_WALL
    _pdz2 = _fz_surf + 96
    # West side partition wall with connecting door
    BRUSHES.extend(
        layered_wall(
            wx1,
            _split,
            _fz1,
            wx2,
            _sp_y2,
            _fz2,
            [(wxc - 32, _fz_surf, wxc + 32, _pdz2)],
            TEX_WALL,
        )
    )
    # East side partition wall with connecting door
    BRUSHES.extend(
        layered_wall(
            ex1,
            _split,
            _fz1,
            ex2,
            _sp_y2,
            _fz2,
            [(exc - 32, _fz_surf, exc + 32, _pdz2)],
            TEX_WALL,
        )
    )

if not KH_ENABLED:
    del BRUSHES[_kh_brush_start:]

DRAW_FASCIAKH_FASCIA_TEXT = True  # Set True to re-enable (slow to compile)

# ── "LOYOLA UNIVERSITY MARYLAND" fascia lettering ────────────────────────────
# Fascia panel follows the arch: one box per character hanging from dbot(x)
fas_y1, fas_y2 = PB_Y1 - 6, PB_Y1  # 6 units thick, flush with south face
fas_y3, fas_y4 = PB_Y2, PB_Y2 + 6  # north face panel
fas_x1, fas_x2 = -500, 500  # between the two road piers
KH_FASCIA_PX_W, KH_FASCIA_PX_H = 4, 4
KH_FASCIAKH_FASCIA_FONT_ROWS = 6
KH_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
char_w = (4 + 1) * KH_FASCIA_PX_W  # 4 cols + 1 gap
total_w = len(KH_FASCIA_TEXT) * char_w - KH_FASCIA_PX_W
text_x0 = 0 - total_w // 2

# No separate background fascia boxes — parapet wall face is the backdrop

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


def render_text_fascia(text, x0, y_face, px_w, px_h, depth, tex, mirror=False):
    """Render text as pixel-font raised boxes on a fascia face.
    Each character's Z is computed from dtop(x) so letters follow the arch curve.
    mirror=True flips each glyph horizontally (needed for north-facing surface)."""
    cols = 4
    rows = 6
    char_w = (cols + 1) * px_w  # 4 cols + 1 gap

    brushes = []
    for ci, ch in enumerate(text):
        bitmap = KH_FASCIA_FONT.get(ch, KH_FASCIA_FONT[" "])
        cx = x0 + ci * char_w
        x_mid = cx + (cols * px_w) / 2
        z_top = int(dtop(x_mid)) + PB_PAR_H - 14  # centred in parapet height
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


def render_text_flat(text, x0, y_face, z_base, px_w, px_h, depth, tex, mirror=False):
    """Render text as pixel-font raised boxes on a flat north-facing wall surface."""
    cols = 4
    rows = 6
    char_w_f = (cols + 1) * px_w
    brushes = []
    for ci, ch in enumerate(text):
        bitmap = KH_FASCIA_FONT.get(ch, KH_FASCIA_FONT[" "])
        cx = x0 + ci * char_w_f
        for row_i, row_bits in enumerate(bitmap):
            z = z_base + (rows - 1 - row_i) * px_h
            for col_i in range(cols):
                src_col = (cols - 1 - col_i) if mirror else col_i
                if row_bits & (1 << (cols - 1 - src_col)):
                    px = cx + col_i * px_w
                    brushes.append(
                        box(px, y_face, z, px + px_w, y_face + depth, z + px_h, tex)
                    )
    return brushes


# Raised pixel-font letters on the Knott Hall sign plaque
# Text reversed + mirrored so it reads correctly when viewed from north (facing south)
BRUSHES.extend(
    render_text_flat(
        _sign_text[::-1],
        x0=_sign_cx - _sign_total_w // 2,
        y_face=KH_Y2 + 6,
        z_base=_sign_zb + 14,  # centered: (48-20)//2 = 14
        px_w=_sign_px_w,
        px_h=_sign_px_h,
        depth=2,
        tex=TEX_RAIL,
        mirror=True,
    )
)

letter_brushes = (
    (
        render_text_fascia(
            KH_FASCIA_TEXT,
            x0=text_x0,
            y_face=PB_Y1,
            px_w=KH_FASCIA_PX_W,
            px_h=KH_FASCIA_PX_H,
            depth=1,
            tex=TEX_RAIL,
        )
        + render_text_fascia(
            KH_FASCIA_TEXT[::-1],
            x0=text_x0,
            y_face=PB_Y2 + 1,
            px_w=KH_FASCIA_PX_W,
            px_h=KH_FASCIA_PX_H,
            depth=1,
            tex=TEX_RAIL,
            mirror=True,
        )
    )
    if DRAW_FASCIAKH_FASCIA_TEXT
    else []
)

# ── Campus lamp posts (brush geometry) — along Charles Street (N-S) ──────────
CS_LAMP_POST_H = PB_DZ2 - 32  # pole height (~12 ft)
# Single lamp post — east sidewalk, at the SE corner of the Ennis Road intersection
CS_LAMP_POST_XS = [
    2158,
    1246,
]  # east sidewalk near Ennis (= NE pier − 48), and next pier west
lamp_post_ys = [EP_Y - EP_HW - 160]
for _lx in CS_LAMP_POST_XS:
    for _ly in lamp_post_ys:
        _pole_top = FZ2 + CS_LAMP_POST_H
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
PB_SPAN_CENTRES = [
    (PB_X1 + PB_ARCH_X[0]) // 2,
    (PB_ARCH_X[0] + PB_ARCH_X[1]) // 2,
    (PB_ARCH_X[1] + PB_ARCH_X[2]) // 2,
    (PB_ARCH_X[2] + PB_X2) // 2,
    (PB_X2 + PB_ARCH_X[4]) // 2,
    (PB_ARCH_X[4] + WORLD_X2 - WALL_T) // 2,
]
PB_PEND_XS = PB_SPAN_CENTRES

# ── N/S arch stone wall panels (must be added to B before worldspawn assembly) ──
CS_ARCH_RIN_PRE = 256  # inner radius = road half-width
CS_ARCH_ROUT_PRE = 312  # outer radius
CS_ARCH_STILT_PRE = 96  # stilt height
CS_ARCH_W_PRE = 48  # arch thickness in Y
CS_ARCH_WALL_W_PRE = 320  # stone wall width flanking road
cs_arch_top_pre = FZ2 + CS_ARCH_STILT_PRE + CS_ARCH_RIN_PRE  # = 352

for _pre_syb, _pre_syf in [
    (CS_Y1, CS_Y1 + CS_ARCH_W_PRE),
    (CS_Y2 - CS_ARCH_W_PRE, CS_Y2),
]:
    # Stone arch posts + ring
    BRUSHES.extend(
        arch_wall_y(
            _pre_syb,
            _pre_syf,
            WORLD_X1 + WALL_T,
            WORLD_X2 - WALL_T,
            FZ2,
            cs_arch_top_pre,
            CS_ARCH_RIN_PRE,
            CS_ARCH_ROUT_PRE,
            A_SEGS,
            TEX_STONE,
            stilt_h=CS_ARCH_STILT_PRE,
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
if letter_brushes:
    ENTITIES.append(brush_ent("func_detail", letter_brushes))
# Ennis east fence as func_detail — pickets in open space overflow BSP portals as worldspawn
ENTITIES.append(brush_ent("func_detail", _ew_fence_brushes))
DECK_Z = dtop(0) + 8  # centre of arch deck + a bit (spawn/item height)
ROAD_Z = FZ2 + 8


# ── Knott Hall room goodies — 2 items per room, varied per floor ──────────────
_kh_ent_start = len(ENTITIES)  # checkpoint — trimmed below if KH_ENABLED is False
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
for _fl in range(KH_FLOORS):
    _fz1 = KH_GROUND_Z + _fl * KH_FLOOR_H
    _item_z = _fz1 + KH_WALL + 24
    _light_z = _fz1 + KH_FLOOR_H - 24  # near ceiling
    _split = room_splits[_fl]
    _sr_yc = (biy1 + _split) // 2
    _nr_yc = (_split + KH_WALL + biy2) // 2
    for _side_xc in [wxc, exc]:
        for _ryc in [_sr_yc, _nr_yc]:
            # If west room north items land within 64 units of stairwell south wall, push south
            _safe_ryc = _ryc
            if _side_xc == wxc and _ryc == _nr_yc and _nr_yc > wsty1 - 64:
                _safe_ryc = wsty1 - 80
            ENTITIES.append(
                ent("light", origin=f"{_side_xc} {_safe_ryc} {_light_z}", light="250")
            )
            # Extra fill light at lower mid-height to reduce dark corners
            ENTITIES.append(
                ent(
                    "light",
                    origin=f"{_side_xc} {_safe_ryc} {_fz1 + KH_FLOOR_H // 2}",
                    light="150",
                )
            )
            ENTITIES.append(
                ent(
                    room_goodies[gi % len(room_goodies)],
                    origin=f"{_side_xc - 40} {_safe_ryc} {_item_z}",
                )
            )
            gi += 1
            ENTITIES.append(
                ent(
                    room_goodies[gi % len(room_goodies)],
                    origin=f"{_side_xc + 40} {_safe_ryc} {_item_z}",
                )
            )
            gi += 1

# ── West stairwell lights — ceiling + mid-flight + low fill per lane per floor ──────────
_wst_xc = (wstx1 + wstx2) // 2  # X centre of shaft
_wst_north_yc = (wst_midY + wsty2) // 2  # Y centre of north lane
_wst_south_yc = (wsty1 + wst_midY) // 2  # Y centre of south lane
for _fl in range(KH_FLOORS):
    _wst_lz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H - 24  # near ceiling
    _wst_mz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H // 2  # mid-flight
    _wst_loz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H // 4  # low fill
    for _lz in [_wst_lz, _wst_mz, _wst_loz]:
        ENTITIES.append(
            ent("light", origin=f"{_wst_xc} {_wst_north_yc} {_lz}", light="220")
        )
        ENTITIES.append(
            ent("light", origin=f"{_wst_xc} {_wst_south_yc} {_lz}", light="220")
        )

# ── Central hallway lights — 5 per floor along N-S corridor ─────────────────
_hall_xc = (KH_ENT_X1 + KH_ENT_X2) // 2  # hallway centre X
_hall_ys = [
    biy1 + (biy2 - biy1) * i // 4
    for i in range(1, 4)  # quarters: 25%, 50%, 75%
] + [
    biy1 + (biy2 - biy1) // 8,  # 12.5% (near south end)
    biy1 + (biy2 - biy1) * 7 // 8,  # 87.5% (near north end)
]
for _fl in range(KH_FLOORS):
    _hall_lz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H - 24
    for _ly in _hall_ys:
        ENTITIES.append(
            ent("light", origin=f"{_hall_xc} {_ly} {_hall_lz}", light="200")
        )

# ── Entrance corridor lights — one per floor in each doorway ─────────────────
_ent_xc = KH_ENT_X2 + 64  # east entrance corridor mid-X
_ent_yc = KH_Y2 - 48  # just inside north face
for _fl in range(KH_FLOORS):
    _ent_lz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_FLOOR_H - 24
    ENTITIES.append(ent("light", origin=f"{_hall_xc} {_ent_yc} {_ent_lz}", light="220"))

# ── Knott Hall bookshelves — scattered through rooms ─────────────────────────
KH_SHELF_H = 64  # height of shelf stack
KH_SHELF_D = 16  # depth (one wall-thickness)
KH_SHELF_W = 64  # width

shelf_offsets = [0, 0, 0, 0, 0]

for _fl in range(KH_FLOORS):
    _fz1 = KH_GROUND_Z + _fl * KH_FLOOR_H
    _fz_surf = _fz1 + KH_WALL
    _split = room_splits[_fl]
    _stex = "shelf_1"
    _xoff = shelf_offsets[_fl]

    for _sxc in [wxc, exc]:
        # South room: shelf against south wall — front faces south (-Y)
        _sp = _sxc + _xoff
        ENTITIES.append(
            brush_ent(
                "func_wall",
                [
                    box(
                        _sp - KH_SHELF_W // 2,
                        biy1,
                        _fz_surf,
                        _sp + KH_SHELF_W // 2,
                        biy1 + KH_SHELF_D,
                        _fz_surf + KH_SHELF_H,
                        "shelf_1",
                    )
                ],
            )
        )
        ENTITIES.append(
            ent(
                "light",
                origin=f"{_sp} {biy1 + 32} {_fz_surf + KH_SHELF_H + 24}",
                light="180",
            )
        )


if not KH_ENABLED:
    del ENTITIES[_kh_ent_start:]

ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_abutment_deck",
        origin=f"{min(PB_ARCH_X)} 0 {_abutment_tele_dest_z}",
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
        origin=f"{(RH_X1 + RH_X2) // 2} {(RH_NORTH_Y1 + RH_NORTH_Y2) // 2} {int(RH_RIDGE_Z + 40)}",
        angle="270",  # facing south toward the bridge
    )
)
ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_west",
        origin=f"{KH_CX} {(KH_Y1 + KH_Y2) // 2} {int(KH_Z2 + 40)}",
        angle="180",  # facing south, on Knott Hall rooftop
    )
)

# West arch trigger → east destination
west_brushes = arch_fill(
    WORLD_X1 + WALL_T,
    WORLD_X1 + WALL_T + TEX_ARCH_W,
    0.0,
    PB_DZ2,
    TEX_ARCH_RIN,
    A_SEGS,
    TEX_TELEPORT,
    stilt_h=TEX_ARCH_STILT,
)
ENTITIES.append(brush_ent("trigger_teleport", west_brushes, target="dest_east"))
ENTITIES.append(brush_ent("func_illusionary", west_brushes))

# West lower trigger (ground floor — simple box between posts)
wlx1 = WORLD_X1 + WALL_T
wlx2 = wlx1 + TEX_ARCH_W
west_lower = [box(wlx1, -TEX_ARCH_RIN, FZ2, wlx2, TEX_ARCH_RIN, PB_DZ2, TEX_TELEPORT)]
ENTITIES.append(brush_ent("trigger_teleport", west_lower, target="dest_east"))
ENTITIES.append(brush_ent("func_illusionary", west_lower))

# East arch trigger → west destination (shifted south to match angled span)
east_brushes = arch_fill(
    WORLD_X2 - WALL_T - TEX_ARCH_W,
    WORLD_X2 - WALL_T,
    _es2,
    PB_DZ2,
    TEX_ARCH_RIN,
    A_SEGS,
    TEX_TELEPORT,
    stilt_h=TEX_ARCH_STILT,
)
ENTITIES.append(brush_ent("trigger_teleport", east_brushes, target="dest_west"))
ENTITIES.append(brush_ent("func_illusionary", east_brushes))

# East lower trigger (ground floor — teleports up to bridge deck above)
elx1 = WORLD_X2 - WALL_T - TEX_ARCH_W
elx2 = WORLD_X2 - WALL_T
east_lower_deck_x = elx1 - 64  # west of the arch, on the flat deck approach
ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_east_deck",
        origin=f"{east_lower_deck_x} {int(_es2)} {int(PB_DZ2 + 40)}",
        angle="180",
    )
)
east_lower = [
    box(elx1, _es2 - TEX_ARCH_RIN, FZ2, elx2, _es2 + TEX_ARCH_RIN, PB_DZ2, TEX_TELEPORT)
]
ENTITIES.append(brush_ent("trigger_teleport", east_lower, target="dest_east_deck"))
ENTITIES.append(brush_ent("func_illusionary", east_lower))

# ── North & South Charles Street arch teleports → bridge deck centre ─────────
CS_ARCH_RIN = 256  # inner radius = road half-width
CS_ARCH_ROUT = 312  # outer radius (post thickness = 56, more substantial)
CS_ARCH_STILT = 96  # straight post height before arch springs
CS_ARCH_W = 48  # arch thickness in Y (thicker = more stone-like)

ENTITIES.append(
    ent(
        "info_teleport_destination",
        targetname="dest_bridge_mid",
        origin=f"0 0 {int(dtop(0) + 56)}",
        angle="0",
    )
)

CS_ARCH_TRIG_INSET = 8  # push trigger away from world walls and road surface
CS_ARCH_WALL_W = 320  # stone wall extends this far out from road edge on each side

for _syb, _syf, _trig_y1, _trig_y2 in [
    (
        CS_Y1,
        CS_Y1 + CS_ARCH_W,
        CS_Y1 + CS_ARCH_TRIG_INSET,
        CS_Y1 + CS_ARCH_W,
    ),  # south arch — trigger inset from south wall
    (
        CS_Y2 - CS_ARCH_W,
        CS_Y2,
        CS_Y2 - CS_ARCH_W,
        CS_Y2 - CS_ARCH_TRIG_INSET,
    ),  # north arch — trigger inset from north wall
]:
    _arch_top = FZ2 + CS_ARCH_STILT + CS_ARCH_RIN
    # Box trigger — reliable activation, inset from walls
    _ns_trig = [
        box(
            ROAD_X1 + CS_ARCH_TRIG_INSET,
            _trig_y1,
            FZ2 + 4,
            ROAD_X2 - CS_ARCH_TRIG_INSET,
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
        CS_ARCH_RIN,
        A_SEGS,
        TEX_TELEPORT,
        stilt_h=CS_ARCH_STILT,
    )
    ENTITIES.append(brush_ent("func_illusionary", _ns_glow))


ENTITIES.append(
    ent(
        "info_player_start",
        origin=f"{KH_CX} {PB_Y1 + PB_PAR_W + 32} {int(PB_DZ2 + 24)}",
        angle="180",
    )
)

bcy = (KH_Y1 + KH_Y2) // 2  # Knott Hall center Y = -528
RH_NORTH_CY = (RH_NORTH_Y1 + RH_NORTH_Y2) // 2  # north building center Y
RH_CX = (RH_X1 + RH_X2) // 2  # west buildings center X
RH_SOUTH1_CY = (RH_SOUTH1_Y1 + RH_SOUTH1_Y2) // 2  # south building 1 center Y
RH_SOUTH2_CY = (RH_SOUTH2_Y1 + RH_SOUTH2_Y2) // 2  # south building 2 center Y

# ── Deathmatch spawns — spread across all areas ──────────────────────────
for pos, angle in [
    # Bridge deck
    ((0, 0, int(dtop(0) + 32)), 180),
    ((-200, 0, int(dtop(-200) + 32)), 90),
    ((200, 0, int(dtop(200) + 32)), 270),
    ((-400, 0, int(dtop(-400) + 32)), 90),
    ((400, 0, int(dtop(400) + 32)), 270),
    # Walkway
    *([((KH_CX, (PB_Y1 + KH_Y2) // 2, int(WALK_ZT1 + 32)), 180)] if KH_ENABLED else []),
    # Knott Hall — ground, mid, upper floors
    *(
        [
            (
                ((KH_ENT_X1 + KH_ENT_X2) // 2, KH_Y2 - 80, KH_GROUND_Z + 40),
                180,
            ),  # entrance hallway, north
            ((KH_CX - 100, bcy, KH_GROUND_Z + KH_FLOOR_H + 40), 270),
            ((KH_CX + 100, bcy, KH_GROUND_Z + KH_FLOOR_H * 2 + 40), 90),
            ((KH_CX, KH_Y1 + 100, KH_GROUND_Z + KH_FLOOR_H * 3 + 40), 0),
            ((KH_CX, bcy, KH_GROUND_Z + KH_FLOOR_H * 4 + 40), 180),
            # Knott Hall rooftop
            ((KH_CX, bcy, KH_Z2 + 40), 180),
        ]
        if KH_ENABLED
        else []
    ),
    # Charles Street
    ((0, 300, ROAD_Z + 24), 180),
    ((0, -400, ROAD_Z + 24), 0),
    ((0, RH_SOUTH1_CY, ROAD_Z + 24), 270),
    # North building interior
    ((RH_CX, RH_NORTH_CY, FZ2 + 40), 90),
    ((RH_CX, RH_NORTH_CY, FZ2 + KH_FLOOR_H + 40), 90),
    # North building roof ridge
    ((RH_CX, RH_NORTH_CY, int(RH_RIDGE_Z + 40)), 90),
    # South buildings interiors
    ((RH_CX, RH_SOUTH1_CY, FZ2 + 40), 90),
    ((RH_CX, RH_SOUTH2_CY, FZ2 + 40), 90),
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
if KH_ENABLED:
    ENTITIES.append(
        ent(
            "weapon_rocketlauncher",
            origin=f"{KH_CX} {bcy} {KH_GROUND_Z + KH_FLOOR_H * 3 + 40}",
        )
    )
# Rocket launcher — west arch, north side
ENTITIES.append(
    ent("weapon_rocketlauncher", origin=f"{PB_ARCH_X[1]} {PB_Y1 - 48} {DECK_Z}")
)
# Remaining rocket launchers
for _rl_origin in [
    f"0 {EP_Y - EP_HW - 200} {ROAD_Z + 24}",  # Charles St, south of Ennis
    f"{PB_ARCH_X[2]} 0 {ROAD_Z + 24}",  # under bridge, mid span
    f"{int(_ew_x1 + (_ew_x2 - _ew_x1) // 2)} {bw_ny - 80} {FZ2 + 24}",  # Ennis fence midpoint
    f"{int(_cw_x1 + (_cw_x2 - _cw_x1) // 2)} {bw_ny - 80} {FZ2 + 24}",  # Ennis wall midpoint
    # Bridge deck — one per span
    f"{(PB_X1 + PB_ARCH_X[0]) // 2} 0 {DECK_Z}",  # span 1
    f"{(PB_ARCH_X[0] + PB_ARCH_X[1]) // 2} {PB_Y2 - 24} {DECK_Z}",  # span 2 south edge
    f"{(PB_ARCH_X[1] + PB_ARCH_X[2]) // 2} {PB_Y1 + 24} {DECK_Z}",  # span 3 north edge
    f"{(PB_ARCH_X[2] + PB_X2) // 2} 0 {DECK_Z}",  # span 4
    f"{(PB_X2 + PB_ARCH_X[4]) // 2} 0 {DECK_Z}",  # span 5 (east angled)
]:
    ENTITIES.append(ent("weapon_rocketlauncher", origin=_rl_origin))

# Super shotgun — spread around mid-tier locations
if KH_ENABLED:
    ENTITIES.append(
        ent("weapon_supershotgun", origin=f"{exc} {KH_Y2 - 80} {KH_GROUND_Z + 40}")
    )
ENTITIES.append(ent("weapon_supershotgun", origin=f"0 300 {ROAD_Z + 24}"))
ENTITIES.append(ent("weapon_supershotgun", origin=f"{RH_CX} {RH_SOUTH1_CY} {FZ2 + 40}"))

# Grenade launcher — Knott Hall floor 2, south building 2
if KH_ENABLED:
    ENTITIES.append(
        ent(
            "weapon_grenadelauncher",
            origin=f"{KH_CX} {bcy} {KH_GROUND_Z + KH_FLOOR_H * 2 + 40}",
        )
    )
ENTITIES.append(
    ent("weapon_grenadelauncher", origin=f"{RH_CX} {RH_SOUTH2_CY} {FZ2 + 40}")
)

# Nailgun — bridge approaches, Charles Street
ENTITIES.append(ent("weapon_nailgun", origin=f"-600 0 {ROAD_Z + 24}"))
ENTITIES.append(ent("weapon_nailgun", origin=f"600 0 {ROAD_Z + 24}"))
if KH_ENABLED:
    ENTITIES.append(
        ent("weapon_nailgun", origin=f"{KH_CX} {bcy} {KH_GROUND_Z + KH_FLOOR_H + 40}")
    )

# ── Ammo ──────────────────────────────────────────────────────────────────
for ax in PB_ARCH_X:
    ENTITIES.append(ent("item_rockets", origin=f"{ax} 0 {int(dtop(ax) + 8)}"))
for rx in [400, 800]:
    ENTITIES.append(ent("item_rockets", origin=f"{rx} 0 {ROAD_Z + 24}"))
    ENTITIES.append(ent("item_rockets", origin=f"-{rx} 0 {ROAD_Z + 24}"))
for _kf in range(1, KH_FLOORS):
    ENTITIES.append(
        ent(
            "item_rockets",
            origin=f"{KH_CX + 80} {bcy} {KH_GROUND_Z + _kf * KH_FLOOR_H + 40}",
        )
    )
ENTITIES.append(ent("item_shells", origin=f"0 -300 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_shells", origin=f"{RH_CX} {RH_NORTH_CY} {FZ2 + 40}"))
ENTITIES.append(ent("item_spikes", origin=f"-400 200 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_spikes", origin=f"400 -200 {ROAD_Z + 24}"))

# ── Health & Armor ────────────────────────────────────────────────────────
# Health — scattered throughout
ENTITIES.append(ent("item_health", origin=f"0 0 {DECK_Z}"))
ENTITIES.append(ent("item_health", origin=f"{exc} {KH_Y2 - 64} {KH_GROUND_Z + 40}"))
ENTITIES.append(
    ent("item_health", origin=f"{KH_CX} {bcy} {KH_GROUND_Z + KH_FLOOR_H * 2 + 40}")
)
ENTITIES.append(ent("item_health", origin=f"0 400 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_health", origin=f"0 -600 {ROAD_Z + 24}"))
ENTITIES.append(ent("item_health", origin=f"{RH_CX} {RH_SOUTH2_CY} {FZ2 + 40}"))
# Armor — contested locations
ENTITIES.append(ent("item_armor1", origin=f"-200 0 {DECK_Z}"))  # yellow armor on bridge
ENTITIES.append(
    ent("item_armor2", origin=f"{KH_CX} {bcy} {KH_GROUND_Z + KH_FLOOR_H * 4 + 40}")
)  # red armor top floor
ENTITIES.append(
    ent("item_armorInv", origin=f"{RH_CX} {RH_NORTH_CY} {int(RH_RIDGE_Z + 40)}")
)  # mega armor on roof ridge (teleport reward)

# Torch lights on pillar caps
if SHOW_SUPPORTS:
    for px in PB_ARCH_X:
        if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
            continue
        pbase = dtop(px)
        pcap = (
            pbase + PB_PAR_H + PB_PIL_EXTRA + PB_PIL_CAP_H + PB_PIL_PYR_H
        )  # top of pyramid
        cy_n = PB_Y2 - PB_PAR_W // 2  # centred on north pillar cap
        cy_s = PB_Y1 + PB_PAR_W // 2  # centred on south pillar cap
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
    for px in PB_ARCH_X:
        if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
            continue
        for _uy in [PB_Y2 + 30, PB_Y1 - 30]:
            ENTITIES.append(ent("light", origin=f"{px} {_uy} 16", light="200"))

# Campus lamp post lights — flame above brick cup, matching bridge pillar torches
for _lx in CS_LAMP_POST_XS:
    for _ly in lamp_post_ys:
        _pole_top = FZ2 + CS_LAMP_POST_H
        _flame_z = _pole_top + 20
        ENTITIES.append(ent("light", origin=f"{_lx} {_ly} {_flame_z}", light="300"))
        ENTITIES.append(
            ent("light_flame_large_yellow", origin=f"{_lx} {_ly} {_flame_z + 4}")
        )

# Ennis cement wall lamppost lights
for _lx, _ly, _lz in _cw_lamp_posts:
    ENTITIES.append(ent("light", origin=f"{_lx} {_ly} {_lz}", light="300"))
    ENTITIES.append(ent("light_flame_large_yellow", origin=f"{_lx} {_ly} {_lz + 4}"))

# Ennis entrance pillar torches — flame above brick cup on each stone pillar
ennis_pil_flame_z = EP_PIL_ZB + EP_PIL_POST_H + EP_PIL_CAP_H + EP_PIL_BELL2_H + 20
ennis_pil_cx = EP_PIL_X1 + EP_PIL_HW
for _epy in (EP_Y - EP_HW - EP_PIL_HW, EP_Y + EP_HW + EP_PIL_HW):
    ENTITIES.append(
        ent("light", origin=f"{ennis_pil_cx} {_epy} {ennis_pil_flame_z}", light="300")
    )
    ENTITIES.append(
        ent(
            "light_flame_large_yellow",
            origin=f"{ennis_pil_cx} {_epy} {ennis_pil_flame_z + 4}",
        )
    )

# Under-bridge amber pendant lights — flicker style, hang below deck
for _px in PB_PEND_XS:
    ENTITIES.append(
        ent("light", origin=f"{_px} 0 {int(dbot(_px)) - 20}", light="350", style="1")
    )

# Pier base lights — illuminate plinths and arch openings from just inside each pier
for _px in PB_ARCH_X:
    _pz = FZ2 + PB_PIL_BASE_RAMP_H + 60  # just above the plinth top, low in the arch
    ENTITIES.append(ent("light", origin=f"{_px} {PB_Y2 // 2} {_pz}", light="250"))
    ENTITIES.append(ent("light", origin=f"{_px} {PB_Y1 // 2} {_pz}", light="250"))

# Cement arch on east face of abutment pier (-1246) — three lights for good coverage
_ab_px = min(PB_ARCH_X)  # = -1246
_ab_arch_z = FZ2 + PB_PIL_BASE_H + 60  # mid-height of arch opening
ENTITIES.append(
    ent("light", origin=f"{_ab_px + PB_PIL_HW + 32} 0 {_ab_arch_z}", light="700")
)
ENTITIES.append(
    ent(
        "light",
        origin=f"{_ab_px + PB_PIL_HW + 32} {PB_Y2 // 2} {_ab_arch_z}",
        light="500",
    )
)
ENTITIES.append(
    ent(
        "light",
        origin=f"{_ab_px + PB_PIL_HW + 32} {PB_Y1 // 2} {_ab_arch_z}",
        light="500",
    )
)

# Light on underside of walkway slab illuminating the ramp below
if KH_WALKWAY_ENABLED:
    walk_mid_y = (PB_Y1 + KH_Y2) // 2
    walk_frac = (PB_Y1 - walk_mid_y) / float(PB_Y1 - KH_Y2)
    wk_zb1 = WALK_ZT1 - KH_WALL
    wk_zb2 = WALK_ZT2 - KH_WALL
    walk_bot_mid = int(wk_zb1 + walk_frac * (wk_zb2 - wk_zb1))
    ENTITIES.append(
        ent("light", origin=f"{KH_CX} {walk_mid_y} {walk_bot_mid - 8}", light="300")
    )

# Lift (func_plat) — rides from ground floor up through roof opening to rooftop
if KH_ENABLED:
    lift_travel = KH_Z2 - (KH_GROUND_Z + KH_WALL)
    lift_brush = [
        box(
            stx1 + 2,
            sty1 + 2,
            KH_Z2 - 8,
            stx2 - 2,
            sty2 - 2,
            KH_Z2,
            TEX_FLOOR_KH,
        )
    ]
    ENTITIES.append(
        brush_ent("func_plat", lift_brush, height=str(lift_travel), speed="200")
    )

# Interior lights for the three campus buildings (north + 2 south)
bldg_light_x = (RH_X1 + RH_X2) // 2
for _bly1, _bly2 in [
    (RH_NORTH_Y1, RH_NORTH_Y2),
    (RH_SOUTH1_Y1, RH_SOUTH1_Y2),
    (RH_SOUTH2_Y1, RH_SOUTH2_Y2),
]:
    _bly = (_bly1 + _bly2) // 2
    for _bfl in range(RH_FLOORS):
        _blz = FZ2 + _bfl * KH_FLOOR_H + KH_FLOOR_H // 2
        ENTITIES.append(
            ent("light", origin=f"{bldg_light_x} {_bly} {_blz}", light="200")
        )

# Interior lights for Knott Hall — 3×4 grid per floor
if KH_ENABLED:
    for _kfl in range(KH_FLOORS):
        _klz = KH_GROUND_Z + _kfl * KH_FLOOR_H + KH_FLOOR_H // 2
        for _kxi in [1, 2, 3]:
            _klx = KH_X1 + (KH_X2 - KH_X1) * _kxi // 4
            for _kyi in [1, 2, 3, 4]:
                _kly = KH_Y1 + (KH_Y2 - KH_Y1) * _kyi // 5
                ENTITIES.append(
                    ent("light", origin=f"{_klx} {_kly} {_klz}", light="150")
                )

# ── Cartoon trees as func_detail ─────────────────────────────────────────────
# Positions based on ref photos:
# - Dense forest behind cement/iron wall north of Ennis (bridge13, bridge02)
# - Large trees flanking Knott Hall on west side (bridge01, bridge10)
# - Trees along Ennis Parallel campus road (bridge02)
_tree_positions = [
    # Dense forest behind the north Ennis wall (north of bw_ny)
    (int(_ew_x1 + 100), bw_ny + 120),
    (int(_ew_x1 + 280), bw_ny + 200),
    (int(_ew_x1 + 460), bw_ny + 100),
    (int(_ew_x1 + 620), bw_ny + 280),
    (int(_ew_x1 + 800), bw_ny + 150),
    (int(_ew_x2 + 100), bw_ny + 120),
    (int(_ew_x2 + 320), bw_ny + 220),
    (int(_ew_x2 + 560), bw_ny + 100),
    (int(_ew_x2 + 780), bw_ny + 300),
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
_all_tree_brushes = []
for _tx, _ty in _tree_positions:
    _all_tree_brushes += make_tree(_tx, _ty, FZ2)
ENTITIES.append(brush_ent("func_detail", _all_tree_brushes))

# ── Giant trees along Charles Street — in front of Knott Hall only ───────────
# 5 trees in 2 rows: row of 2 closer to street, row of 3 closer to KH.
# Tree height matches Knott Hall (KH_Z2).
_cs_tree_h = KH_Z2
_kh_tree_span = KH_Y2 - KH_Y1
_cs_row_near = ROAD_X2 + CS_WALK_W + 300  # closer to Charles St
_cs_row_far = ROAD_X2 + CS_WALK_W + 560  # closer to KH
# Row of 2 — near row, 2 trees at 25% and 75% of KH Y span
_cs_row2_ys = [int(KH_Y1 + _kh_tree_span * f) for f in (0.25, 0.75)]
# Row of 3 — far row, 3 trees at 15%, 50%, 85%
_cs_row3_ys = [int(KH_Y1 + _kh_tree_span * f) for f in (0.15, 0.5, 0.85)]
_cs_giant_brushes = []
for _ty in _cs_row2_ys:
    _cs_giant_brushes += make_giant_tree(_cs_row_near, _ty, FZ2, _cs_tree_h)
for _ty in _cs_row3_ys:
    _cs_giant_brushes += make_giant_tree(_cs_row_far, _ty, FZ2, _cs_tree_h)
ENTITIES.append(brush_ent("func_detail", _cs_giant_brushes))


_bush_positions = [
    # Along north face of Ennis brick wall (campus grass side, not sidewalk)
    (bw_x1 + 60, bw_ny + EP_WALL_T + 40),
    (bw_x1 + 160, bw_ny + EP_WALL_T + 40),
    (bw_x1 + 260, bw_ny + EP_WALL_T + 40),
    (bw_x1 + 360, bw_ny + EP_WALL_T + 40),
    # Along north face of iron fence
    (int(_ew_x1 + 120), bw_ny + EP_WALL_T + 40),
    (int(_ew_x1 + 300), bw_ny + EP_WALL_T + 40),
    (int(_ew_x1 + 500), bw_ny + EP_WALL_T + 40),
    (int(_ew_x1 + 700), bw_ny + EP_WALL_T + 40),
    # Along north face of cement parapet wall
    (int(_cw_x1 + 120), bw_ny + EP_WALL_T + 40),
    (int(_cw_x1 + 320), bw_ny + EP_WALL_T + 40),
    (int(_cw_x1 + 560), bw_ny + EP_WALL_T + 40),
    # Along Knott Hall west face (outside building)
    (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2 - 200),
    (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2),
    (KH_X1 - 48, (KH_Y1 + KH_Y2) // 2 + 200),
    # Along west building east face (outside building)
    (RH_X2 + 48, -200),
    (RH_X2 + 48, 200),
    (RH_X2 + 48, 500),
]
_all_bush_brushes = []
for _bx, _by in _bush_positions:
    _all_bush_brushes += make_bush(_bx, _by, FZ2)
ENTITIES.append(brush_ent("func_detail", _all_bush_brushes))

# ── Charles Street scrolling platform — proper two-lane loop with quad damage ──
# Outbound: east lane north on Charles → south lane east on Ennis → east end
# Return:   west lane south on Charles ← north lane west on Ennis ← east end
# ── Charles Street platform — via back road, no Ennis lane switch ─────────────
# Route: Charles outbound (north) → right on Ennis → right onto back road →
#        south down hill → back up north → left on Ennis → Charles return (south)
_CS_PLT_W = 128  # platform width and depth
_CS_PLT_H = 12  # platform slab thickness
_CS_PLT_SPEED = 180  # units per second

_CS_PLT_X_OUT = ROAD_X2 // 4  # outbound Charles lane  (east,   X=+64)
_CS_PLT_X_RET = -(ROAD_X2 * 3 // 4)  # return  Charles lane   (west,   X=-192)
_CS_PLT_Y_S = CS_Y1 + _CS_PLT_W // 2 + 48  # south turnaround
_CS_PLT_Y_OUT = EP_Y - EP_HW + 16  # outbound Ennis lane (south Y≈792)
_CS_PLT_Y_RET = EP_Y + EP_HW // 8  # return  Ennis lane  (north Y≈956)
_CS_PLT_BR_X = KH_BR_RD_X1 + KH_BR_HW // 2  # right lane on back road (X≈2382)

# Z origin at each road surface (platform bottom + half thickness)
_oz_cs = ROAD_Z + _CS_PLT_H // 2  # Charles St   (= 14)
_oz_flat = FZ2 + 2 + _CS_PLT_H // 2  # Ennis / back road flat (= 8)
_oz_br_s = KH_BR_ZT_S + 2 + _CS_PLT_H // 2  # back road south / hill top (= 72)

# Platform brush — placed at pc1 (south end of outbound Charles lane)
_cs_plt_brush = box(
    _CS_PLT_X_OUT - _CS_PLT_W // 2,
    _CS_PLT_Y_S - _CS_PLT_W // 2,
    ROAD_Z,
    _CS_PLT_X_OUT + _CS_PLT_W // 2,
    _CS_PLT_Y_S + _CS_PLT_W // 2,
    ROAD_Z + _CS_PLT_H,
    TEX_FLOOR,
)
ENTITIES.append(
    brush_ent(
        "func_train",
        [_cs_plt_brush],
        target="cs_pc1",
        speed=str(_CS_PLT_SPEED),
        _minlight="255",
    )
)

# 9-corner loop:
# pc1 Charles south (out) → pc2 Ennis junction → pc3 back-road junction
# → pc4 top of slope → pc5 hill bottom (turn) → pc6 top of slope (return)
# → pc7 Ennis junction return → pc8 Charles/Ennis return → pc9 Charles south (ret) → pc1
for _pcn, _tx, _ty, _oz, _target in [
    ("cs_pc1", _CS_PLT_X_OUT, _CS_PLT_Y_S, _oz_cs, "cs_pc2"),
    ("cs_pc2", _CS_PLT_X_OUT, _CS_PLT_Y_OUT, _oz_flat, "cs_pc3"),
    ("cs_pc3", _CS_PLT_BR_X, _CS_PLT_Y_OUT, _oz_flat, "cs_pc4"),
    ("cs_pc4", _CS_PLT_BR_X, KH_BR_Y2, _oz_flat, "cs_pc5"),
    ("cs_pc5", _CS_PLT_BR_X, KH_BR_Y1, _oz_br_s, "cs_pc6"),
    ("cs_pc6", _CS_PLT_BR_X, KH_BR_Y2, _oz_flat, "cs_pc7"),
    ("cs_pc7", _CS_PLT_BR_X, _CS_PLT_Y_RET, _oz_flat, "cs_pc8"),
    ("cs_pc8", _CS_PLT_X_RET, _CS_PLT_Y_RET, _oz_flat, "cs_pc9"),
    ("cs_pc9", _CS_PLT_X_RET, _CS_PLT_Y_S, _oz_cs, "cs_pc1"),
]:
    ENTITIES.append(
        ent(
            "path_corner",
            targetname=_pcn,
            target=_target,
            origin=f"{_tx} {_ty} {_oz}",
        )
    )

# Quad damage at the hill top (south end of back road) — reward for the full loop
ENTITIES.append(
    ent(
        "item_artifact_super_damage",
        origin=f"{_CS_PLT_BR_X} {KH_BR_Y1} {_oz_br_s + _CS_PLT_H + 18}",
    )
)

# ── Rocket launchers along the platform route ─────────────────────────────────
_rl_h = _CS_PLT_H + 56  # hover height above road — clear of platform top + item bbox
_br_mid_y = (KH_BR_Y1 + KH_BR_Y2) // 2  # Y=-1072
_br_mid_z = (
    FZ2
    + 2
    + (KH_BR_ZT_S - KH_BR_ZT_N) * (_br_mid_y - KH_BR_Y2) // (KH_BR_Y1 - KH_BR_Y2)
)
for _rx, _ry, _rz in [
    # Charles outbound (south third, north third)
    (_CS_PLT_X_OUT, CS_Y1 + (CS_Y2 - CS_Y1) // 6, ROAD_Z + _rl_h),
    (_CS_PLT_X_OUT, CS_Y1 + (CS_Y2 - CS_Y1) * 2 // 6, ROAD_Z + _rl_h),
    # Ennis outbound (quarter, three-quarter)
    ((_CS_PLT_X_OUT + _CS_PLT_BR_X) // 3, _CS_PLT_Y_OUT, FZ2 + 2 + _rl_h),
    ((_CS_PLT_X_OUT + _CS_PLT_BR_X) * 2 // 3, _CS_PLT_Y_OUT, FZ2 + 2 + _rl_h),
    # Back road going south (midpoint)
    (_CS_PLT_BR_X, _br_mid_y, _br_mid_z + _rl_h),
    # Ennis return (midpoint)
    ((_CS_PLT_X_RET + _CS_PLT_BR_X) // 2, _CS_PLT_Y_RET, FZ2 + 2 + _rl_h),
    # Charles return (south third, north third)
    (_CS_PLT_X_RET, CS_Y1 + (CS_Y2 - CS_Y1) // 6, ROAD_Z + _rl_h),
    (_CS_PLT_X_RET, CS_Y1 + (CS_Y2 - CS_Y1) * 2 // 6, ROAD_Z + _rl_h),
]:
    ENTITIES.append(ent("weapon_rocketlauncher", origin=f"{_rx} {_ry} {_rz}"))

# ── Monsters ──────────────────────────────────────────────────────────────────
# Grunts patrol Charles Street and Ennis
_stand_z = ROAD_Z + 24
for _mx, _my, _mangle in [
    (ROAD_X1 + 64, -1200, 90),  # south Charles, west side heading north
    (ROAD_X2 - 64, -800, 270),  # south Charles, east side heading south
    (ROAD_X1 + 64, -300, 90),  # mid Charles, west side
    (ROAD_X2 - 64, 200, 270),  # mid Charles, east side
    (0, -1600, 90),  # far south Charles, centre
]:
    ENTITIES.append(
        ent("monster_knight", origin=f"{_mx} {_my} {_stand_z}", angle=str(_mangle))
    )

# Grunts on Ennis
for _mx, _my, _mangle in [
    (500, EP_Y - EP_HW + 40, 0),  # Ennis east, south lane
    (1200, EP_Y + EP_HW - 40, 180),  # Ennis east, north lane
    (1800, EP_Y - EP_HW + 40, 0),  # Ennis further east
]:
    ENTITIES.append(
        ent("monster_knight", origin=f"{_mx} {_my} {_stand_z}", angle=str(_mangle))
    )

# Ogres on the back road hill — like guards on the slope
_br_cx = (KH_BR_RD_X1 + KH_BR_RD_X2) // 2
for _my, _mz in [
    (-600, FZ2 + 2 + (64 * ((-600) - KH_BR_Y2) // (KH_BR_Y1 - KH_BR_Y2)) + 24),
    (-1200, FZ2 + 2 + (64 * ((-1200) - KH_BR_Y2) // (KH_BR_Y1 - KH_BR_Y2)) + 24),
    (KH_BR_Y1 + 64, KH_GROUND_Z + 2 + 24),  # top of hill near quad
]:
    ENTITIES.append(ent("monster_knight", origin=f"{_br_cx} {_my} {_mz}", angle="90"))

# Knights inside KH rooms — one per floor in each room
for _fl in range(KH_FLOORS):
    _fz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_WALL + 24
    _split = room_splits[_fl]
    _sr_yc = (biy1 + _split) // 2
    _nr_yc = (_split + KH_WALL + biy2) // 2
    for _rxc in [wxc, exc]:
        for _ryc in [_sr_yc, _nr_yc]:
            ENTITIES.append(
                ent("monster_knight", origin=f"{_rxc} {_ryc} {_fz}", angle="270")
            )

# Enforcers in the hallway — one per floor
_hall_xc = (KH_ENT_X1 + KH_ENT_X2) // 2
for _fl in range(KH_FLOORS):
    _fz = KH_GROUND_Z + _fl * KH_FLOOR_H + KH_WALL + 24
    _hall_yc = (biy1 + biy2) // 2
    ENTITIES.append(
        ent("monster_knight", origin=f"{_hall_xc} {_hall_yc} {_fz}", angle="180")
    )

# Enforcers on rooftop
for _rx, _ry in [
    (wxc, KH_Y2 - 80),
    (exc, KH_Y2 - 80),
    (KH_CX, KH_Y1 + 80),
    (wxc, KH_Y1 + 80),
]:
    ENTITIES.append(
        ent("monster_knight", origin=f"{_rx} {_ry} {KH_Z2 + 24}", angle="180")
    )

# ── Write ─────────────────────────────────────────────────────────────────────
map_text = worldspawn + "\n" + "\n".join(ENTITIES) + "\n"
with open("loyola.map", "w") as fh:
    fh.write(map_text)
print(
    f"loyola.map written — {len(BRUSHES)} worldspawn brushes, {len(ENTITIES)} entities"
)
