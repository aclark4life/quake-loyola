import math
from constants import *


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
    ext = open_hw + overhang
    if y1 < -ext:
        brushes.append(box(x1, y1, floor_z, x2, -ext, ceil_z, tex))
    if y2 > ext:
        brushes.append(box(x1, ext, floor_z, x2, y2, ceil_z, tex))
    brushes.append(box(x1, -ext, floor_z, x2, -open_hw, ceil_z, tex))  # south pillar
    brushes.append(box(x1, open_hw, floor_z, x2, ext, ceil_z, tex))  # north pillar
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


def win_row(n, lo, hi):
    """Evenly-spaced window centre positions."""
    step = (hi - lo) / n
    return [lo + step * (i + 0.5) for i in range(n)]


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
