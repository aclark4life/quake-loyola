import math

from .constants import (
    BRIDGE_ARCH_X,
    BRIDGE_EAST_SPAN_ANGLE,
    Textures,
)
from .mapdata import Brush, Entity, Face
from .utils import swap_xy


def box(x1, y1, z1, x2, y2, z2, tex, tt=None, tb=None, tt_params="0 0 0 1 1"):
    """Axis-aligned rectangular brush. tex=sides, tt=top, tb=bottom (default to tex)."""
    tt = tt or tex
    tb = tb or tex
    return Brush(
        [
            Face((x1, y1, z1), (x1, y2, z1), (x1, y1, z2), tex),
            Face((x2, y1, z1), (x2, y1, z2), (x2, y2, z1), tex),
            Face((x1, y1, z1), (x1, y1, z2), (x2, y1, z1), tex),
            Face((x1, y2, z1), (x2, y2, z1), (x1, y2, z2), tex),
            Face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tb),
            Face((x1, y1, z2), (x1, y2, z2), (x2, y1, z2), tt, tt_params),
        ]
    )


def east_y_shift(x):
    """Southward Y shift (negative = south) for a given X east of the easternmost pier.
    Pivots at BRIDGE_ARCH_X[4] (= 2206); zero for x <= that pier."""
    pivot = BRIDGE_ARCH_X[4]
    if x <= pivot:
        return 0.0
    return -(x - pivot) * math.tan(math.radians(BRIDGE_EAST_SPAN_ANGLE))


def shear_box_y(x1, y1, z1, x2, y2, z2, s1, s2, tex, tt=None, tb=None):
    """Rectangular slab with Y-shear: at x=x1 the Y-range is [y1+s1, y2+s1],
    at x=x2 it is [y1+s2, y2+s2].  Negative s = southward shift."""
    tt = tt or tex
    tb = tb or tex
    y1a, y2a = y1 + s1, y2 + s1
    y1b, y2b = y1 + s2, y2 + s2
    return Brush(
        [
            Face((x1, y1a, z1), (x1, y2a, z1), (x1, y1a, z2), tex),  # -X west
            Face((x2, y1b, z1), (x2, y1b, z2), (x2, y2b, z1), tex),  # +X east
            Face((x1, y1a, z1), (x1, y1a, z2), (x2, y1b, z1), tex),  # south (angled)
            Face((x1, y2a, z1), (x2, y2b, z1), (x1, y2a, z2), tex),  # north (angled)
            Face((x1, y1a, z1), (x2, y1b, z1), (x1, y2a, z1), tb),  # bottom
            Face((x1, y1a, z2), (x1, y2a, z2), (x2, y1b, z2), tt),  # top
        ]
    )


def pyramid(x1, y1, z1, x2, y2, z2, tex):
    """Square pyramid: base x1..x2, y1..y2 at z=z1; apex at centre at z=z2."""
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    return Brush(
        [
            Face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tex),  # bottom
            Face((x2, y1, z1), (x1, y1, z1), (cx, cy, z2), tex),  # south
            Face((x1, y2, z1), (x2, y2, z1), (cx, cy, z2), tex),  # north
            Face((x1, y1, z1), (x1, y2, z1), (cx, cy, z2), tex),  # west
            Face((x2, y2, z1), (x2, y1, z1), (cx, cy, z2), tex),  # east
        ]
    )


def ramp_slab(
    x1, x2, y1, y2, zb1, zb2, zt1, zt2, tex, tt=None, tb=None, te=None, ts=None
):
    """Prismatic slab whose bottom and top faces are sloped in the X direction.
    zb1/zt1 = bottom/top Z at x=x1;  zb2/zt2 = bottom/top Z at x=x2.
    End-cap faces are omitted when an end tapers to a knife-edge (zb == zt there),
    keeping the brush valid as a 4- or 5-face wedge instead of a degenerate prism.
    te: texture for the -X/+X end-cap faces; defaults to tex.
    ts: texture for the -Y/+Y side faces (the triangular gable ends when the ridge
        runs along Y); defaults to tex."""
    tt = tt or tex
    tb = tb or tex
    te = te or tex
    ts = ts or tex
    faces = []
    if zt1 != zb1:
        faces.append(Face((x1, y1, zb1), (x1, y2, zb1), (x1, y1, zt1), te))  # -X
    if zt2 != zb2:
        faces.append(Face((x2, y1, zb2), (x2, y1, zt2), (x2, y2, zb2), te))  # +X
    faces += [
        Face((x1, y1, zb1), (x1, y1, zt1), (x2, y1, zb2), ts),  # -Y
        Face((x1, y2, zb1), (x2, y2, zb2), (x1, y2, zt1), ts),  # +Y
        Face((x1, y1, zb1), (x2, y1, zb2), (x1, y2, zb1), tb),  # sloped bottom
        Face((x1, y1, zt1), (x1, y2, zt1), (x2, y1, zt2), tt),  # sloped top
    ]
    return Brush(faces)


def ramp_slab_y(
    x1, x2, y1, y2, zb1, zb2, zt1, zt2, tex, tt=None, tb=None, te=None, ts=None
):
    """Prismatic slab whose bottom and top faces are sloped in the Y direction.
    zb1/zt1 = bottom/top Z at y=y1;  zb2/zt2 = bottom/top Z at y=y2.
    y1 and y2 may be passed in either order.
    When one end tapers to a knife-edge (zb==zt), that end-cap face is omitted
    (delegated to ramp_slab's own conditional logic via the XY swap)."""
    # Normalise so y1 <= y2 before delegating
    if y1 > y2:
        y1, y2 = y2, y1
        zb1, zb2 = zb2, zb1
        zt1, zt2 = zt2, zt1
    return swap_xy(
        ramp_slab(y1, y2, x1, x2, zb1, zb2, zt1, zt2, tex, tt=tt, tb=tb, te=te, ts=ts)
    )


def gable_slats(
    bx1, bx2, apex_x, eave_z, ridge_z, slab_t, yface, depth, tex, n=6, gap=4, min_w=24
):
    """Decorative horizontal wood slats laid over a triangular gable end.
    The gable lies in the X-Z plane at y=yface: its base runs bx1..bx2 at
    z=eave_z and tapers to the ridge apex at x=apex_x, z=ridge_z (the lowest
    slab_t units of the side edges stay vertical, matching the roof slab).
    Planks stand proud of the face by |depth| (sign of depth = outward Y
    direction) and stack in n bands separated by gap-unit shadow grooves;
    bands narrower than min_w near the apex are skipped."""
    y0, y1 = sorted((yface, yface + depth))
    denom = ridge_z - (eave_z + slab_t)

    def edge_x(z):
        t = z - (eave_z + slab_t)
        if t <= 0:
            return bx1, bx2
        return bx1 + t * (apex_x - bx1) / denom, bx2 - t * (bx2 - apex_x) / denom

    band = (ridge_z - eave_z) / n
    brushes = []
    for i in range(n):
        z0 = eave_z + i * band
        z1 = z0 + band - gap
        xl0, xr0 = edge_x(z0)
        xl1, xr1 = edge_x(z1)
        if xr1 - xl1 < min_w:
            continue
        brushes.append(
            Brush(
                [
                    Face((xl0, y0, z0), (xl0, y1, z0), (xl1, y0, z1), tex),  # left end
                    Face((xr0, y0, z0), (xr1, y0, z1), (xr0, y1, z0), tex),  # right end
                    Face((xl0, y0, z0), (xl1, y0, z1), (xr0, y0, z0), tex),  # -Y
                    Face((xl0, y1, z0), (xr0, y1, z0), (xl1, y1, z1), tex),  # +Y
                    Face((xl0, y0, z0), (xr0, y0, z0), (xl0, y1, z0), tex),  # bottom
                    Face((xl1, y0, z1), (xl1, y1, z1), (xr1, y0, z1), tex),  # top
                ]
            )
        )
    return brushes


def tri_prism(ax, ay, bx, by, cx, cy, z1, z2, tex):
    """Triangular prism. Triangle (ax,ay)→(bx,by)→(cx,cy) must be CCW from above.
    Face winding: side normals point inward (left-perpendicular of each CCW edge).
    Bottom +Z (solid above), top -Z (solid below)."""
    return Brush(
        [
            Face((ax, ay, z2), (bx, by, z2), (ax, ay, z1), tex),  # side AB
            Face((bx, by, z2), (cx, cy, z2), (bx, by, z1), tex),  # side BC
            Face((cx, cy, z2), (ax, ay, z2), (cx, cy, z1), tex),  # side CA
            Face((ax, ay, z1), (bx, by, z1), (cx, cy, z1), tex),  # bottom (+Z)
            Face((ax, ay, z2), (cx, cy, z2), (bx, by, z2), tex),  # top (-Z)
        ]
    )


def make_tree(cx, cy, base_z):
    """Cartoon tree: brown trunk + three stacked ground-texture pyramids."""
    TEX_TRUNK = "bricka2_1"
    TEX_FOLIAGE = Textures.GROUND
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
    TEX_FOLIAGE = Textures.GROUND
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
    brushes.append(
        box(cx - 6, cy - 6, base_z, cx + 6, cy + 6, base_z + 10, Textures.GROUND)
    )
    # Main rectangular body
    brushes.append(
        box(
            cx - size,
            cy - size,
            base_z + 10,
            cx + size,
            cy + size,
            base_z + size + 10,
            Textures.GROUND,
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
            Textures.GROUND,
        )
    )
    return brushes


def arch_seg(xb, xf, yc, zc, rin, rout, angle_start_deg, angle_end_deg, tex):
    """One wedge-shaped brush segment of a semicircular arch ring (X-aligned span).
    Angles angle_start_deg..angle_end_deg in degrees; centre at (yc, zc); inner/outer radii rin/rout."""
    t1, t2 = math.radians(angle_start_deg), math.radians(angle_end_deg)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    yi, zi = yc + rin * cm, zc + rin * sm
    yo, zo = yc + rout * cm, zc + rout * sm
    return Brush(
        [
            Face((xf, yc, zc), (xf, yc, zc + 1), (xf, yc + 1, zc), tex),
            Face((xb, yc, zc), (xb, yc + 1, zc), (xb, yc, zc + 1), tex),
            Face((xf, yc, zc), (xf, yc + c1, zc + s1), (xb, yc, zc), tex),
            Face((xf, yc, zc), (xb, yc, zc), (xf, yc + c2, zc + s2), tex),
            Face((xf, yi, zi), (xb, yi, zi), (xf, yi - sm, zi + cm), tex),
            Face((xf, yo, zo), (xf, yo - sm, zo + cm), (xb, yo, zo), tex),
        ]
    )


def arch_pie_seg(xb, xf, yc, zc, rad, angle_start_deg, angle_end_deg, tex):
    """Solid pie-slice brush for filling the interior of an arch (no inner hole).
    Used to create func_illusionary teleport glows and solid arch infill."""
    t1, t2 = math.radians(angle_start_deg), math.radians(angle_end_deg)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    yo, zo = yc + rad * cm, zc + rad * sm
    return Brush(
        [
            Face((xf, yc, zc), (xf, yc, zc + 1), (xf, yc + 1, zc), tex),
            Face((xb, yc, zc), (xb, yc + 1, zc), (xb, yc, zc + 1), tex),
            Face((xf, yc, zc), (xf, yc + c1, zc + s1), (xb, yc, zc), tex),
            Face((xf, yc, zc), (xb, yc, zc), (xf, yc + c2, zc + s2), tex),
            Face((xf, yo, zo), (xf, yo - sm, zo + cm), (xb, yo, zo), tex),
        ]
    )


def arch_fill(x1, x2, yc, floor_z, rin, segs, tex, stilt_h=None):
    """Solid arch fill (base box + pie segments) for an X-aligned arch opening.
    Used for trigger_teleport and func_illusionary brush entities."""
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h
    seg = 180.0 / segs
    brushes = []
    brushes.append(box(x1, yc - rin, floor_z, x2, yc + rin, sprz, tex))
    for seg_index in range(segs):
        brushes.append(
            arch_pie_seg(
                x1,
                x2,
                yc,
                float(sprz),
                rin,
                seg_index * seg,
                (seg_index + 1) * seg,
                tex,
            )
        )
    return brushes


def arch_seg_y(yb, yf, xc, zc, rin, rout, angle_start_deg, angle_end_deg, tex):
    """One wedge-shaped brush segment of a semicircular arch ring (Y-aligned span).
    Derived from arch_seg via XY swap."""
    return swap_xy(
        arch_seg(yb, yf, xc, zc, rin, rout, angle_start_deg, angle_end_deg, tex)
    )


def arch_pie_seg_y(yb, yf, xc, zc, rad, angle_start_deg, angle_end_deg, tex):
    """Solid pie-slice brush for a Y-aligned arch interior. Derived from arch_pie_seg via XY swap."""
    return swap_xy(
        arch_pie_seg(yb, yf, xc, zc, rad, angle_start_deg, angle_end_deg, tex)
    )


def arch_fill_y(y1, y2, xc, floor_z, rin, segs, tex, stilt_h=None):
    """Solid arch fill for a Y-aligned arch opening. Derived from arch_fill via XY swap."""
    return [
        swap_xy(b)
        for b in arch_fill(y1, y2, xc, floor_z, rin, segs, tex, stilt_h=stilt_h)
    ]


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
    yc=0.0,
    freestanding=False,
):
    """Stone wall with arched opening centred at Y=yc (default 0).
    freestanding=True: posts stop at spring height, no cap above crown, no side fill.

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
    pillar_top = sprz if freestanding else ceil_z
    # Solid rock on either side of the arch opening (omitted when freestanding)
    if not freestanding:
        if y1 < yc - (rout + overhang):
            brushes.append(
                box(x1, y1, floor_z, x2, yc - (rout + overhang), ceil_z, tex)
            )
        if y2 > yc + (rout + overhang):
            brushes.append(
                box(x1, yc + (rout + overhang), floor_z, x2, y2, ceil_z, tex)
            )
    brushes.append(
        box(x1, yc - (rout + overhang), floor_z, x2, yc - rin, pillar_top, tex)
    )  # south pillar
    brushes.append(
        box(x1, yc + rin, floor_z, x2, yc + (rout + overhang), pillar_top, tex)
    )  # north pillar
    # Cap above arch crown (omitted when freestanding)
    if not freestanding:
        brushes.append(box(x1, yc - rin, sprz + rin, x2, yc + rin, ceil_z, tex))
    # Stone plinth at base — closes arch opening at ground level
    if base_ramp is not None:
        zt1, zt2 = base_ramp
        brushes.append(
            ramp_slab(x1, x2, yc - rin, yc + rin, floor_z, floor_z, zt1, zt2, tex)
        )
        if base_cap_h > 0:
            cap_tex = base_cap_tex or tex
            cx1, cx2 = x1 - base_cap_ovh, x2 + base_cap_ovh
            crin = rin + base_cap_ovh
            brushes.append(
                ramp_slab(
                    cx1,
                    cx2,
                    yc - crin,
                    yc + crin,
                    zt1,
                    zt2,
                    zt1 + base_cap_h,
                    zt2 + base_cap_h,
                    cap_tex,
                )
            )
    elif base_h > 0:
        brushes.append(box(x1, yc - rin, floor_z, x2, yc + rin, floor_z + base_h, tex))
        if base_cap_h > 0:
            cap_tex = base_cap_tex or tex
            cx1, cx2 = x1 - base_cap_ovh, x2 + base_cap_ovh
            crin = rin + base_cap_ovh
            brushes.append(
                box(
                    cx1,
                    yc - crin,
                    floor_z + base_h,
                    cx2,
                    yc + crin,
                    floor_z + base_h + base_cap_h,
                    cap_tex,
                )
            )

    # Fill corner gaps where the arch ring (radius rout) doesn't reach the
    # rectangular junction of the pillars (at |y|=rin) and cap (at z=sprz+rin).
    # Omitted in freestanding mode — no cap means no corner to fill.
    if not freestanding and rout < rin * 1.41421356:
        h_side = math.sqrt(max(0, rout**2 - rin**2))
        # South-top corner
        brushes.append(
            box(x1, yc - rin, sprz + h_side, x2, yc - h_side, sprz + rin, tex)
        )
        # North-top corner
        brushes.append(
            box(x1, yc + h_side, sprz + h_side, x2, yc + rin, sprz + rin, tex)
        )

    for seg_index in range(segs):
        brushes.append(
            arch_seg(
                x1,
                x2,
                yc,
                float(sprz),
                rin,
                rout,
                seg_index * seg,
                (seg_index + 1) * seg,
                tex,
            )
        )
    return brushes


def arch_wall_y(
    y1, y2, x1, x2, floor_z, ceil_z, rin, rout, segs, tex, stilt_h=None, xc=0.0
):
    """Freestanding arch ring (posts + curved ring) aligned on the Y axis.
    Side walls are omitted so the arch stands alone without flanking fill.
    xc: centre X of the arch opening (default 0)."""
    stilt_h = rin if stilt_h is None else stilt_h
    sprz = floor_z + stilt_h
    seg = 180.0 / segs
    brushes = []
    brushes.append(box(xc - rout, y1, floor_z, xc - rin, y2, sprz, tex))
    brushes.append(box(xc + rin, y1, floor_z, xc + rout, y2, sprz, tex))
    for seg_index in range(segs):
        brushes.append(
            arch_seg_y(
                y1,
                y2,
                xc,
                float(sprz),
                rin,
                rout,
                seg_index * seg,
                (seg_index + 1) * seg,
                tex,
            )
        )
    return brushes


def ent(cls, **kw):
    """Return a point Entity for the given classname and key/value pairs."""
    return Entity(cls, dict(kw))


def brush_ent(cls, brushes, **kw):
    """Return a brush Entity wrapping one or more Brush objects."""
    if isinstance(brushes, Brush):
        brushes = [brushes]
    return Entity(cls, dict(kw), list(brushes))


def layered_wall(x1, y1, z1, x2, y2, z2, openings, tex):
    """Wall slab (thin in Y) with rectangular cutouts.
    openings: list of (ox1, oz1, ox2, oz2) — regions to omit in the x,z plane.
    """
    xs = sorted({x1, x2} | {o[0] for o in openings} | {o[2] for o in openings})
    zs = sorted({z1, z2} | {o[1] for o in openings} | {o[3] for o in openings})
    brushes = []
    for x_index in range(len(xs) - 1):
        for z_index in range(len(zs) - 1):
            cx1, cx2 = xs[x_index], xs[x_index + 1]
            cz1, cz2 = zs[z_index], zs[z_index + 1]
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
    Derived from layered_wall via XY swap."""
    return [swap_xy(b) for b in layered_wall(y1, x1, z1, y2, x2, z2, openings, tex)]
