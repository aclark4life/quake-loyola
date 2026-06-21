import math

from .constants import (
    BRIDGE_ARCH_X,
    BRIDGE_EAST_SPAN_ANGLE,
    FASCIA_FONT,
    Textures,
)
from .mapdata import Brush, Entity, Face
from .utils import swap_xy


def box(
    x1,
    y1,
    z1,
    x2,
    y2,
    z2,
    tex,
    tt=None,
    tb=None,
    tt_params="0 0 0 1 1",
    tw=None,
    te=None,
    ts=None,
    tn=None,
):
    """Axis-aligned rectangular brush.
    tex=all sides (default).  Per-face overrides:
      tt=top, tb=bottom, tw=-X (west), te=+X (east), ts=-Y (south), tn=+Y (north).
    """
    tt = tt or tex
    tb = tb or tex
    tw = tw or tex
    te = te or tex
    ts = ts or tex
    tn = tn or tex
    return Brush(
        [
            Face((x1, y1, z1), (x1, y2, z1), (x1, y1, z2), tw),  # -X west
            Face((x2, y1, z1), (x2, y1, z2), (x2, y2, z1), te),  # +X east
            Face((x1, y1, z1), (x1, y1, z2), (x2, y1, z1), ts),  # -Y south
            Face((x1, y2, z1), (x2, y2, z1), (x1, y2, z2), tn),  # +Y north
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

    ``zb1``/``zt1`` = bottom/top Z at x=x1; ``zb2``/``zt2`` = bottom/top Z at x=x2.
    End-cap faces are omitted when an end tapers to a knife-edge (zb == zt there),
    keeping the brush valid as a 4- or 5-face wedge instead of a degenerate prism.

    ``te``: texture for the -X/+X end-cap faces; defaults to *tex*.
    ``ts``: texture for the -Y/+Y side faces (triangular gable ends when the ridge
    runs along Y); defaults to *tex*."""
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


def corner_ramp(x_hi, x_lo, y_hi, y_lo, z_base, z_hi, tex, tt=None):
    """Tetrahedral corner ramp: a single tilted top plane that is high at the
    (x_hi, y_hi) corner (z_hi) and falls to z_base along BOTH far edges — the
    x_lo edge and the y_lo edge. The descending diagonal runs from (x_hi, y_lo)
    to (x_lo, y_hi); the (x_lo, y_lo) corner is left at grade (not covered).

    Used to blend a raised terrace corner down to grade in two directions at
    once. Requires x_hi < x_lo, y_hi < y_lo, z_base < z_hi (matches the winding
    derived below)."""
    tt = tt or tex
    a = (x_hi, y_hi, z_hi)  # raised apex
    b = (x_hi, y_hi, z_base)
    c = (x_hi, y_lo, z_base)
    d = (x_lo, y_hi, z_base)
    return Brush(
        [
            Face(b, d, c, tex),  # bottom (−Z)
            Face(a, b, c, tex),  # x_hi face (−X)
            Face(a, d, b, tex),  # y_hi face (−Y)
            Face(a, c, d, tt),  # slanted top
        ]
    )


def gable_slats(
    bx1, bx2, apex_x, eave_z, ridge_z, slab_t, yface, depth, tex, n=24, gap=2, min_w=6
):
    """Decorative horizontal wood slats laid over a triangular gable end.

    The gable lies in the X-Z plane at y=yface: its base runs bx1..bx2 at
    z=eave_z and tapers to the ridge apex at x=apex_x, z=ridge_z (the lowest
    slab_t units of the side edges stay vertical, matching the roof slab).
    Planks extend inward by ``depth`` (outer face flush with yface) and stack
    in n bands separated by gap-unit shadow grooves; bands narrower than
    min_w near the apex are skipped."""
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


def entrance_arch_xwall(
    cx,
    base_z,
    ent_hw,
    ent_h,
    face_y,
    out_sign,
    tex,
    pillar_w=10,
    pillar_d=10,
    lintel_h=12,
    arch_h=48,
    arch_t=8,
):
    """Two pillars + A-frame pediment with crossbeams over an entrance in an X-normal wall.
    cx: X centre of entrance; base_z: Z floor level; ent_hw: half-width; ent_h: height.
    face_y: Y of outer wall face; out_sign: -1 protrudes south (-Y), +1 protrudes north (+Y)."""
    ya, yb = sorted((face_y, face_y + out_sign * pillar_d))
    lx1, lx2 = cx - ent_hw - pillar_w, cx - ent_hw
    rx1, rx2 = cx + ent_hw, cx + ent_hw + pillar_w
    pz2 = base_z + ent_h + lintel_h
    eave_z, ridge_z = pz2, pz2 + arch_h
    brushes = [
        box(lx1, ya, base_z, lx2, yb, pz2, tex),  # left pillar
        box(rx1, ya, base_z, rx2, yb, pz2, tex),  # right pillar
        box(lx1, ya, base_z + ent_h, rx2, yb, pz2, tex),  # lintel
        ramp_slab(
            lx1, cx, ya, yb, eave_z, eave_z, eave_z + arch_t, ridge_z, tex
        ),  # left gable
        ramp_slab(
            cx, rx2, ya, yb, eave_z, eave_z, ridge_z, eave_z + arch_t, tex
        ),  # right gable
    ]
    # Capstone slats overhang the gable/pillar in all directions
    overhang, slat_h, side_ov = 3, 5, 2
    ya_cap = ya - overhang if out_sign < 0 else ya
    yb_cap = yb + overhang if out_sign > 0 else yb
    # Two decorative cross beams at the top of the door / base of the A-frame
    beam_h, beam_gap, upper_rise = 2, 9, 6
    brushes += [
        box(
            lx1 - side_ov,
            ya_cap,
            eave_z + upper_rise,
            rx2 + side_ov,
            yb_cap,
            eave_z + upper_rise + beam_h,
            tex,
        ),  # upper beam
        box(
            lx1 - side_ov,
            ya_cap,
            eave_z - beam_gap - beam_h,
            rx2 + side_ov,
            yb_cap,
            eave_z - beam_gap,
            tex,
        ),  # lower beam
    ]
    # Extrapolate slat-bottom Z at the extended side edges (continue gable slope outward)
    half_span = ent_hw + pillar_w  # = cx - lx1 = rx2 - cx
    slat_drop = side_ov * (arch_h - arch_t) // half_span
    zb_ext = eave_z + arch_t - slat_drop  # slat bottom at extended left/right corners
    zt_ext = zb_ext + slat_h
    brushes += [
        ramp_slab(
            lx1 - side_ov,
            cx,
            ya_cap,
            yb_cap,
            zb_ext,
            ridge_z,
            zt_ext,
            ridge_z + slat_h,
            tex,
        ),  # left slat
        ramp_slab(
            cx,
            rx2 + side_ov,
            ya_cap,
            yb_cap,
            ridge_z,
            zb_ext,
            ridge_z + slat_h,
            zt_ext,
            tex,
        ),  # right slat
    ]
    return brushes


def entrance_arch_ywall(
    cy,
    base_z,
    ent_hw,
    ent_h,
    face_x,
    out_sign,
    tex,
    pillar_w=10,
    pillar_d=10,
    lintel_h=12,
    arch_h=48,
    arch_t=8,
):
    """Two pillars + A-frame pediment with crossbeams over an entrance in a Y-normal wall.
    cy: Y centre of entrance; base_z: Z floor level; ent_hw: half-width; ent_h: height.
    face_x: X of outer wall face; out_sign: +1 protrudes east (+X), -1 protrudes west (-X)."""
    xa, xb = sorted((face_x, face_x + out_sign * pillar_d))
    ly1, ly2 = cy - ent_hw - pillar_w, cy - ent_hw
    ry1, ry2 = cy + ent_hw, cy + ent_hw + pillar_w
    pz2 = base_z + ent_h + lintel_h
    eave_z, ridge_z = pz2, pz2 + arch_h
    brushes = [
        box(xa, ly1, base_z, xb, ly2, pz2, tex),  # left pillar
        box(xa, ry1, base_z, xb, ry2, pz2, tex),  # right pillar
        box(xa, ly1, base_z + ent_h, xb, ry2, pz2, tex),  # lintel
        ramp_slab_y(
            xa, xb, ly1, cy, eave_z, eave_z, eave_z + arch_t, ridge_z, tex
        ),  # left gable
        ramp_slab_y(
            xa, xb, cy, ry2, eave_z, eave_z, ridge_z, eave_z + arch_t, tex
        ),  # right gable
    ]
    # Capstone slats overhang the gable/pillar in all directions
    overhang, slat_h, side_ov = 3, 5, 2
    xa_cap = xa - overhang if out_sign < 0 else xa
    xb_cap = xb + overhang if out_sign > 0 else xb
    # Two decorative cross beams at the top of the door / base of the A-frame
    beam_h, beam_gap, upper_rise = 2, 9, 6
    brushes += [
        box(
            xa_cap,
            ly1 - side_ov,
            eave_z + upper_rise,
            xb_cap,
            ry2 + side_ov,
            eave_z + upper_rise + beam_h,
            tex,
        ),  # upper beam
        box(
            xa_cap,
            ly1 - side_ov,
            eave_z - beam_gap - beam_h,
            xb_cap,
            ry2 + side_ov,
            eave_z - beam_gap,
            tex,
        ),  # lower beam
    ]
    # Extrapolate slat-bottom Z at the extended side edges (continue gable slope outward)
    half_span = ent_hw + pillar_w  # = cy - ly1 = ry2 - cy
    slat_drop = side_ov * (arch_h - arch_t) // half_span
    zb_ext = eave_z + arch_t - slat_drop  # slat bottom at extended left/right corners
    zt_ext = zb_ext + slat_h
    brushes += [
        ramp_slab_y(
            xa_cap,
            xb_cap,
            ly1 - side_ov,
            cy,
            zb_ext,
            ridge_z,
            zt_ext,
            ridge_z + slat_h,
            tex,
        ),  # left slat
        ramp_slab_y(
            xa_cap,
            xb_cap,
            cy,
            ry2 + side_ov,
            ridge_z,
            zb_ext,
            ridge_z + slat_h,
            zt_ext,
            tex,
        ),  # right slat
    ]
    return brushes


def win_frame_xwall(
    xl,
    xr,
    zb,
    zt,
    face_y,
    out_sign,
    tex,
    fw=4,
    fd=4,
    margin=2,
    crossbar=True,
    bottom=True,
    inner_gap=0,
    ifw=None,
    inner_recess=2,
):
    """Double window frame (outer + inner) inside a window opening in an X-normal wall.

    Produces two concentric rectangular frames.  The outer frame is inset by
    *margin* from the opening edges; the inner frame is inset a further
    ``fw + inner_gap`` from the outer frame edges and recessed ``inner_recess``
    units back from the wall face so it sits visibly behind the outer frame.
    The crossbar (horizontal mullion) is centered in the wall depth (at ``fd//2``)
    so it appears recessed and mid-plane.

    ``fw``: outer frame bar width; ``ifw``: inner frame bar width (defaults to
    ``fw - 1``); ``fd``: protrusion depth; ``margin``: gap between outer bar and
    opening edge; ``inner_gap``: lateral clearance between the two frames (0 = flush);
    ``inner_recess``: how far the inner frame's face sits behind the outer face.
    ``crossbar``: add a mullion dividing the inner pane into upper/lower halves.
    ``bottom``: include bottom bars (set False for doorways at floor level — the
    inner side bars then run all the way to floor level like the outer ones)."""
    if ifw is None:
        ifw = max(fw - 1, 2)
    ya, yb = sorted((face_y, face_y + out_sign * fd))
    # Inner frame centered in wall depth: equal recess from front and back faces.
    jya, jyb = sorted(
        (face_y + out_sign * inner_recess, face_y + out_sign * (fd - inner_recess))
    )
    ix1, ix2 = xl + margin, xr - margin
    iz1, iz2 = zb + margin, zt - margin

    # Outer frame
    bars = [box(ix1, ya, iz2 - fw, ix2, yb, iz2, tex)]  # top
    if bottom:
        bars.append(box(ix1, ya, iz1, ix2, yb, iz1 + fw, tex))  # bottom
    bars += [
        box(ix1, ya, iz1, ix1 + fw, yb, iz2, tex),  # left
        box(ix2 - fw, ya, iz1, ix2, yb, iz2, tex),  # right
    ]

    # Inner frame — inset by (fw + inner_gap) from outer frame laterally, and
    # recessed inner_recess units from the wall face.
    # When bottom=False (doorway), inner side bars run from floor level so the
    # two U-shapes share the same base.
    jx1 = ix1 + fw + inner_gap
    jx2 = ix2 - fw - inner_gap
    jz1 = iz1 + fw + inner_gap if bottom else iz1
    jz2 = iz2 - fw - inner_gap
    if jx2 - jx1 > 2 * ifw and jz2 - jz1 > 2 * ifw:
        bars.append(box(jx1, jya, jz2 - ifw, jx2, jyb, jz2, tex))  # top
        if bottom:
            bars.append(box(jx1, jya, jz1, jx2, jyb, jz1 + ifw, tex))  # bottom
        bars += [
            box(jx1, jya, jz1, jx1 + ifw, jyb, jz2, tex),  # left
            box(jx2 - ifw, jya, jz1, jx2, jyb, jz2, tex),  # right
        ]
        if crossbar:
            cb = max(ifw // 2, 2)  # crossbar height ≈ half the inner frame-bar width
            zc = (jz1 + jz2) // 2
            # Crossbar centered in wall depth (fd//2) and recessed from the face.
            cr = fd // 2 - ifw // 2
            cya, cyb = sorted((face_y + out_sign * cr, face_y + out_sign * (cr + ifw)))
            bars.append(box(jx1, cya, zc - cb // 2, jx2, cyb, zc + cb - cb // 2, tex))
    return bars


def win_frame_ywall(
    yl,
    yr,
    zb,
    zt,
    face_x,
    out_sign,
    tex,
    fw=4,
    fd=4,
    margin=2,
    crossbar=True,
    bottom=True,
    inner_gap=0,
    ifw=None,
    inner_recess=2,
):
    """Double window frame (outer + inner) inside a window opening in a Y-normal wall.

    Produces two concentric rectangular frames.  The outer frame is inset by
    *margin* from the opening edges; the inner frame is inset a further
    ``fw + inner_gap`` from the outer frame edges and recessed ``inner_recess``
    units back from the wall face so it sits visibly behind the outer frame.
    The crossbar (horizontal mullion) is centered in the wall depth (at ``fd//2``)
    so it appears recessed and mid-plane.

    ``fw``: outer frame bar width; ``ifw``: inner frame bar width (defaults to
    ``fw - 1``); ``fd``: protrusion depth; ``margin``: gap between outer bar and
    opening edge; ``inner_gap``: lateral clearance between the two frames (0 = flush);
    ``inner_recess``: how far the inner frame's face sits behind the outer face.
    ``crossbar``: add a mullion dividing the inner pane into upper/lower halves.
    ``bottom``: include bottom bars (set False for doorways at floor level — the
    inner side bars then run all the way to floor level like the outer ones)."""
    if ifw is None:
        ifw = max(fw - 1, 2)
    xa, xb = sorted((face_x, face_x + out_sign * fd))
    # Inner frame centered in wall depth: equal recess from front and back faces.
    jxa, jxb = sorted(
        (face_x + out_sign * inner_recess, face_x + out_sign * (fd - inner_recess))
    )
    iy1, iy2 = yl + margin, yr - margin
    iz1, iz2 = zb + margin, zt - margin

    # Outer frame
    bars = [box(xa, iy1, iz2 - fw, xb, iy2, iz2, tex)]  # top
    if bottom:
        bars.append(box(xa, iy1, iz1, xb, iy2, iz1 + fw, tex))  # bottom
    bars += [
        box(xa, iy1, iz1, xb, iy1 + fw, iz2, tex),  # left
        box(xa, iy2 - fw, iz1, xb, iy2, iz2, tex),  # right
    ]

    # Inner frame — inset by (fw + inner_gap) from outer frame laterally, and
    # recessed inner_recess units from the wall face.
    # When bottom=False (doorway), inner side bars run from floor level.
    jy1 = iy1 + fw + inner_gap
    jy2 = iy2 - fw - inner_gap
    jz1 = iz1 + fw + inner_gap if bottom else iz1
    jz2 = iz2 - fw - inner_gap
    if jy2 - jy1 > 2 * ifw and jz2 - jz1 > 2 * ifw:
        bars.append(box(jxa, jy1, jz2 - ifw, jxb, jy2, jz2, tex))  # top
        if bottom:
            bars.append(box(jxa, jy1, jz1, jxb, jy2, jz1 + ifw, tex))  # bottom
        bars += [
            box(jxa, jy1, jz1, jxb, jy1 + ifw, jz2, tex),  # left
            box(jxa, jy2 - ifw, jz1, jxb, jy2, jz2, tex),  # right
        ]
        if crossbar:
            cb = max(ifw // 2, 2)  # crossbar height ≈ half the inner frame-bar width
            zc = (jz1 + jz2) // 2
            # Crossbar centered in wall depth (fd//2) and recessed from the face.
            cr = fd // 2 - ifw // 2
            cxa, cxb = sorted((face_x + out_sign * cr, face_x + out_sign * (cr + ifw)))
            bars.append(box(cxa, jy1, zc - cb // 2, cxb, jy2, zc + cb - cb // 2, tex))
    return bars


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

    ``freestanding=True``: posts stop at spring height, no cap above crown, no side fill.

    ``stilt_h``: height of straight sides before the arch springs (defaults to rin,
    giving a plain semicircle; set > rin for a tall stilted/gothic arch).

    ``overhang``: extra Y extent on the rectangular pillar portions beyond ±rout.

    ``base_h``: solid stone plinth height at ground level — arch opening starts above this.

    ``base_ramp``: if given, a (zt_x1, zt_x2) tuple — replaces the flat base_h box with
    a ramp_slab whose top slopes from zt_x1 at x=x1 to zt_x2 at x=x2.
    base_h is ignored when base_ramp is set.

    ``base_cap_h``: thin slab placed on top of the plinth (flat or ramped) in base_cap_tex.

    ``base_cap_tex``: texture for the cap slab (defaults to tex).

    ``base_cap_ovh``: how far the cap extends beyond the plinth in X and Y (cornice effect).
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


def render_text_flat_x(text, y0, x_face, z_base, px_w, px_h, depth, tex, mirror=False):
    """Like render_text_flat but text advances in +Y and protrudes in +X from x_face.

    Use for east/west-facing surfaces. For a surface viewed from the west (facing east),
    pass text[::-1] and mirror=True so glyphs read correctly left-to-right.

    Consecutive lit pixels in a row are merged into a single box so dense glyphs (e.g. E)
    don't generate internal T-junctions that sparkle/garble at render time.
    """
    cols = 4
    rows = 6
    char_w = (cols + 1) * px_w
    brushes = []
    for ci, ch in enumerate(text):
        bitmap = FASCIA_FONT.get(ch, FASCIA_FONT[" "])
        cy = y0 + ci * char_w
        for row_i, row_bits in enumerate(bitmap):
            z = z_base + (rows - 1 - row_i) * px_h
            run_start = None
            for col_i in range(cols + 1):
                src_col = (cols - 1 - col_i) if mirror else col_i
                lit = col_i < cols and (row_bits & (1 << (cols - 1 - src_col)))
                if lit and run_start is None:
                    run_start = col_i
                elif not lit and run_start is not None:
                    py1 = cy + run_start * px_w
                    py2 = cy + col_i * px_w
                    brushes.append(
                        box(x_face, py1, z, x_face + depth, py2, z + px_h, tex)
                    )
                    run_start = None
    return brushes


def render_text_flat(text, x0, y_face, z_base, px_w, px_h, depth, tex, mirror=False):
    """Render text as pixel-font raised boxes on a flat wall surface.

    Characters advance left-to-right in +X; rows stack upward in +Z from z_base.
    Each character cell is (4+1)*px_w units wide; glyphs are 4 columns × 6 rows.
    depth: how far each pixel box protrudes in +Y from y_face.
    mirror=True flips each glyph horizontally — combine with text[::-1] to make
    text readable on a surface viewed from the -Y direction (e.g., north face).
    """
    cols = 4
    rows = 6
    char_w = (cols + 1) * px_w
    brushes = []
    for ci, ch in enumerate(text):
        bitmap = FASCIA_FONT.get(ch, FASCIA_FONT[" "])
        cx = x0 + ci * char_w
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
