import math
import random

from .constants import (
    BRIDGE_ARCH_X,
    BRIDGE_EAST_SPAN_ANGLE,
    FASCIA_FONT,
    TREE_PROFILES,
    Textures,
)
from .mapdata import Brush, Entity, Face
from .utils import swap_xy, swap_xz


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

    ``tex`` sets all six faces. Per-face overrides: ``tt`` top, ``tb`` bottom,
    ``tw`` −X (west), ``te`` +X (east), ``ts`` −Y (south), ``tn`` +Y (north).
    """
    if tt is None:
        tt = tex
    if tb is None:
        tb = tex
    if tw is None:
        tw = tex
    if te is None:
        te = tex
    if ts is None:
        ts = tex
    if tn is None:
        tn = tex
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


def shear_box_z(x1, y1, z1, x2, y2, z2, s1, s2, tex):
    """Thin bar extruded uniformly along X (x1..x2) whose Y-range is sheared
    as a function of Z: at z=z1 the Y-range is [y1+s1, y2+s1], at z=z2 it is
    [y1+s2, y2+s2]. Derived from ``shear_box_y`` via an X/Z axis swap. Used
    for diagonal cross-brace bars (e.g. a decorative iron "X")."""
    return swap_xz(shear_box_y(z1, y1, x1, z2, y2, x2, s1, s2, tex))


def shear_pyramid_y(x1, y1, x2, y2, z1, z2, s1, s2, tex):
    """Square pyramid whose base has the same Y-shear as ``shear_box_y`` (base
    corners at x=x1 shifted by s1, at x=x2 shifted by s2), apex centred over the
    shifted base at z2. Use this instead of ``pyramid`` when the cap slab the
    pyramid sits on is itself sheared, so the diamond base lines up with the
    slab's parallelogram footprint instead of staying axis-aligned."""
    y1a, y2a = y1 + s1, y2 + s1
    y1b, y2b = y1 + s2, y2 + s2
    cx = (x1 + x2) / 2.0
    cy = (y1a + y2a + y1b + y2b) / 4.0
    apex = (cx, cy, z2)
    return Brush(
        [
            Face((x1, y1a, z1), (x2, y1b, z1), (x1, y2a, z1), tex),  # bottom
            Face((x2, y1b, z1), (x1, y1a, z1), apex, tex),  # south
            Face((x1, y2a, z1), (x2, y2b, z1), apex, tex),  # north
            Face((x1, y1a, z1), (x1, y2a, z1), apex, tex),  # west
            Face((x2, y2b, z1), (x2, y1b, z1), apex, tex),  # east
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


def slab_chamfered_y(x1, x2, y1, y2, zb, zt1, zt2, tex, tt=None, chamfer=4.0):
    """Y-aligned slab (flat bottom at ``zb``, top sloping from ``zt1`` at y=y1 to
    ``zt2`` at y=y2) with its top edge chamfered at BOTH the -Y and +Y ends.

    Built as the base ``ramp_slab_y`` prism plus two extra 45° cutting planes —
    one at each Y end — that shave the top corner into a bevel of height/width
    ``chamfer``. Used for sidewalk panels so the expansion-joint ends read as
    beveled rather than sharp square cuts. ``y1`` and ``y2`` may be given in
    either order."""
    if y1 > y2:
        y1, y2 = y2, y1
        zt1, zt2 = zt2, zt1
    brush = ramp_slab_y(x1, x2, y1, y2, zb, zb, zt1, zt2, tex, tt=tt)
    c = chamfer
    tt = tt or tex
    # -Y (south) end: plane through (y1, zt1-c) → (y1+c, zt1), normal +Y/+Z.
    brush.faces.append(
        Face((x1, y1, zt1 - c), (x1, y1 + c, zt1), (x2, y1, zt1 - c), tt)
    )
    # +Y (north) end: plane through (y2, zt2-c) → (y2-c, zt2), normal -Y/+Z.
    brush.faces.append(
        Face((x1, y2, zt2 - c), (x2, y2, zt2 - c), (x1, y2 - c, zt2), tt)
    )
    return brush


def corner_ramp(x_apex, y_apex, x_far, y_far, z_base, z_hi, tex, tt=None):
    """Tetrahedral corner ramp: a single tilted top plane that is high at the
    (x_apex, y_apex) corner (z_hi) and falls to z_base along BOTH far edges —
    the x_far edge and the y_far edge. The descending diagonal runs from
    (x_apex, y_far) to (x_far, y_apex); the (x_far, y_far) corner is left at
    grade (not covered).

    Used to blend a raised terrace corner down to grade in two directions at
    once — e.g. a hill plateau corner ramping down to street grade on its
    west edge and to a lower road grade on its north edge simultaneously.
    Works for the apex at any of the four corners (x_apex/x_far and
    y_apex/y_far may be given in either order); winding is corrected
    automatically based on which quadrant the apex sits in. Requires
    z_base < z_hi."""
    tt = tt or tex
    a = (x_apex, y_apex, z_hi)  # raised apex
    b = (x_apex, y_apex, z_base)
    c = (x_apex, y_far, z_base)
    d = (x_far, y_apex, z_base)
    # Face winding must give plane normals pointing INTO the brush (Quake's
    # face-plane convention — see box() for a worked example). Whether the
    # "canonical" ordering below or its reverse is correct depends on the
    # sign of (x_far - x_apex) * (y_far - y_apex): a single flipped axis
    # (product < 0) mirrors the brush and reverses every face's winding.
    flipped = (x_far - x_apex) * (y_far - y_apex) < 0
    if flipped:
        faces = [
            Face(b, c, d, tex),  # bottom (−Z)
            Face(a, c, b, tex),  # x_apex face
            Face(a, b, d, tex),  # y_apex face
            Face(a, d, c, tt),  # slanted top
        ]
    else:
        faces = [
            Face(b, d, c, tex),  # bottom (−Z)
            Face(a, b, c, tex),  # x_apex face
            Face(a, d, b, tex),  # y_apex face
            Face(a, c, d, tt),  # slanted top
        ]
    return Brush(faces)


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
    if denom == 0:
        raise ValueError(
            f"gable_slats: ridge_z ({ridge_z}) must differ from eave_z + slab_t ({eave_z + slab_t})"
        )

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


def tri_ramp_prism(ax, ay, bx, by, cx, cy, zbot, za, zb, zc, tex, tt=None):
    """Triangular prism with an independently-tilted top plane: each corner
    gets its own top height (za/zb/zc for the A/B/C corners respectively),
    instead of tri_prism's single shared top Z. Bottom is flat at zbot.

    Each side wall's 4 corners (two at zbot, two at that corner's own top Z)
    are still coplanar — the wall is the vertical plane containing that XY
    edge, and Z doesn't affect which vertical plane a point lies in — so this
    is a valid convex 5-face brush for any za/zb/zc combination, exactly like
    tri_prism. Used to build continuous (seam-matching) triangulated terrain
    patches: adjacent triangles sharing an edge and its two corner heights
    connect with no step, unlike stacking flat-topped tiers.

    Triangle (ax,ay)→(bx,by)→(cx,cy) must be CCW from above, matching
    tri_prism's convention."""
    tt = tt or tex
    return Brush(
        [
            Face((ax, ay, za), (bx, by, zb), (ax, ay, zbot), tex),  # side AB
            Face((bx, by, zb), (cx, cy, zc), (bx, by, zbot), tex),  # side BC
            Face((cx, cy, zc), (ax, ay, za), (cx, cy, zbot), tex),  # side CA
            Face((ax, ay, zbot), (bx, by, zbot), (cx, cy, zbot), tex),  # bottom (+Z)
            Face((ax, ay, za), (cx, cy, zc), (bx, by, zb), tt),  # top (-Z)
        ]
    )


def make_tree(cx, cy, base_z):
    """Cartoon tree: brown trunk + three stacked ground-texture pyramids."""
    TEX_TRUNK = Textures.BRICK
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
    TEX_TRUNK = Textures.BRICK
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


def _octagon_column(cx, cy, z0, z1, radius, tex):
    """Single octagonal-prism Brush approximating a vertical cylinder.

    8 side faces at 45° intervals; one brush for the full height z0→z1.
    Face normals point inward (toward the solid centre) per Quake .map convention
    where cross-product (p2-p1)×(p3-p1) points toward the solid interior.

    circumradius = radius  (distance from axis to each corner vertex)
    inradius     = radius * cos(π/8) ≈ 0.924 * radius  (face midpoint distance)
    """
    faces = []
    N = 8
    for i in range(N):
        theta = math.pi * 2 * i / N
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        qx = cx + radius * cos_t
        qy = cy + radius * sin_t
        # p1=Q@z0, p2=Q@z0+1 (+Z), p3=Q+tangent (-sin,cos,0)
        # cross=(0,0,1)×(-sin_t,cos_t,0)=(-cos_t,-sin_t,0)=inward ✓
        faces.append(
            Face((qx, qy, z0), (qx, qy, z0 + 1), (qx - sin_t, qy + cos_t, z0), tex)
        )
    # Top face  (z=z1): cross must point -Z (inward = downward)
    # (1,0,0)×(0,-1,0)=(0,0,-1) ✓
    faces.append(Face((cx, cy, z1), (cx + 1, cy, z1), (cx, cy - 1, z1), tex))
    # Bottom face (z=z0): cross must point +Z (inward = upward)
    # (1,0,0)×(0,1,0)=(0,0,1) ✓
    faces.append(Face((cx, cy, z0), (cx + 1, cy, z0), (cx, cy + 1, z0), tex))
    return Brush(faces)


def make_pixel_tree(
    cx,
    cy,
    base_z,
    profile="street",
    vox_size=24,
    fins=2,
    trunk_fins=None,
    trunk_solid=False,
    fin_jitter=0.0,
    fin_seed=0,
    ring_segs=0,
):
    """Voxel tree rendered as evenly-spaced billboard fins around a vertical axis.

    The tree profile is a list of strings from top to bottom (index 0 = crown
    tip).  Each character specifies the voxel material:
      'L' = leaf   (GROUND texture)
      'B' = branch (MULCH texture)
      'T' = trunk  (MULCH texture)
      ' ' = empty

    fins        : fins for leafy crown rows (rows containing 'L').
    trunk_fins  : fins for trunk/branch rows (no 'L'); defaults to fins.
    trunk_solid : when True, trunk rows (no 'L') are rendered as a round
                  voxel-circle column.  The radius is derived from the widest
                  solid run in the trunk profile rows.
    fin_jitter  : 0..1 — maximum random angular offset per fin as a fraction
                  of the fin spacing.  Breaks the star pattern; use 0.3–0.5.
    fin_seed    : RNG seed for fin_jitter (default 0, reproducible).
    ring_segs   : when > 0, crown rows are rendered as horizontal ring slices
                  (ring_segs curb_seg wedges per row, covering 360°) instead
                  of billboard fins.  This gives a truly circular cross-section
                  at every height with no gaps.  The outer radius per row is
                  derived from the widest 'L' span in the profile string.

    Args:
        cx, cy       : tree centre in the XY plane
        base_z       : bottom Z of the lowest voxel row
        profile      : key into TREE_PROFILES dict, or a list of strings directly
        vox_size     : Quake units per voxel (default 24)
        fins         : fins for leafy crown rows (default 2)
        trunk_fins   : fins for trunk/branch rows; None = same as fins
        trunk_solid  : render trunk as round voxel-circle column (default False)
        fin_jitter   : random angular jitter fraction (default 0.0 = even spacing)
        fin_seed     : RNG seed for reproducible jitter (default 0)
    """
    _rng = random

    _TEX = {
        "L": Textures.GROUND,
        "B": Textures.MULCH,
        "T": Textures.MULCH,
    }

    prof = TREE_PROFILES[profile] if isinstance(profile, str) else profile
    rows = len(prof)
    cols = max(len(r) for r in prof)
    half = vox_size // 2
    half_cols = cols // 2
    _trunk_fins = trunk_fins if trunk_fins is not None else fins

    brushes = []

    # Build round octagonal trunk as a single Brush spanning all trunk rows.
    if trunk_solid:
        trunk_row_indices = [i for i, r in enumerate(prof) if "L" not in r]
        if trunk_row_indices:
            top_i = trunk_row_indices[0]  # smallest index = highest Z
            bot_i = trunk_row_indices[-1]  # largest index  = lowest Z
            trunk_z1 = base_z + (rows - 1 - top_i) * vox_size + vox_size
            trunk_z0 = base_z + (rows - 1 - bot_i) * vox_size
            trunk_widths = []
            for row_str in prof:
                if "L" not in row_str:
                    solid = [i for i, ch in enumerate(row_str) if _TEX.get(ch)]
                    if solid:
                        trunk_widths.append(len(solid))
            r_vox = max(max(trunk_widths, default=4) // 2, 1)
            radius = r_vox * vox_size
            brushes.append(
                _octagon_column(cx, cy, trunk_z0, trunk_z1, radius, Textures.MULCH)
            )

    _rng.seed(fin_seed)

    for row_i, row_str in enumerate(prof):
        z0 = base_z + (rows - 1 - row_i) * vox_size
        z1 = z0 + vox_size
        is_trunk_row = "L" not in row_str

        # Trunk rows already handled by the single octagon brush above.
        if is_trunk_row and trunk_solid:
            continue

        # Ring-slice mode: render crown rows as horizontal circular discs.
        if not is_trunk_row and ring_segs > 0:
            solid_cols = [i for i, ch in enumerate(row_str) if ch == "L"]
            if solid_cols:
                outer_r = 0
                for c in solid_cols:
                    outer_r = max(
                        outer_r,
                        abs(c - half_cols) * vox_size,
                        abs(c - half_cols + 1) * vox_size,
                    )
                for seg_i in range(ring_segs):
                    a1 = 360.0 * seg_i / ring_segs
                    a2 = 360.0 * (seg_i + 1) / ring_segs
                    brushes.append(
                        curb_seg(cx, cy, z0, z1, 0, outer_r, a1, a2, Textures.GROUND)
                    )
            continue

        row_fins = fins if not is_trunk_row else _trunk_fins

        for k in range(row_fins):
            base_angle = math.pi * k / row_fins
            jitter = (math.pi / row_fins) * fin_jitter * (_rng.random() * 2 - 1)
            angle = base_angle + jitter
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            # Only use the fast merged path for exactly axis-aligned (no jitter).
            axis_aligned = fin_jitter == 0.0 and (
                abs(sin_a) < 1e-9 or abs(cos_a) < 1e-9
            )

            if axis_aligned:
                run_start = None
                run_tex = None
                for col_i in range(cols + 1):
                    ch = row_str[col_i] if col_i < len(row_str) else " "
                    tex = _TEX.get(ch)
                    if tex is not None and tex == run_tex:
                        pass
                    else:
                        if run_start is not None:
                            d0 = (run_start - half_cols) * vox_size
                            d1 = (col_i - half_cols) * vox_size
                            if abs(sin_a) < 1e-9:
                                brushes.append(
                                    box(
                                        cx + d0,
                                        cy - half,
                                        z0,
                                        cx + d1,
                                        cy + half,
                                        z1,
                                        run_tex,
                                    )
                                )
                            else:
                                brushes.append(
                                    box(
                                        cx - half,
                                        cy + d0,
                                        z0,
                                        cx + half,
                                        cy + d1,
                                        z1,
                                        run_tex,
                                    )
                                )
                        run_start = col_i if tex is not None else None
                        run_tex = tex
            else:
                for col_i, ch in enumerate(row_str):
                    tex = _TEX.get(ch)
                    if tex:
                        d = (col_i - half_cols) * vox_size
                        fx = int(cx + d * cos_a)
                        fy = int(cy + d * sin_a)
                        brushes.append(
                            box(fx - half, fy - half, z0, fx + half, fy + half, z1, tex)
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


def curb_seg(cx, cy, z1, z2, rin, rout, angle_start_deg, angle_end_deg, tex):
    """One wedge segment of a horizontal curved ring lying in the X-Y plane, extruded in Z.
    Derived from arch_seg via the coordinate mapping (arch_x→curb_z, arch_y→curb_x,
    arch_z→curb_y): each point (a,b,c) in arch_seg becomes (b,c,a) in curb_seg.
    Uses midpoint-normal tangent planes for inner/outer faces — no polygon jagging.
    Center at (cx, cy); angles measured CCW from +X."""
    t1, t2 = math.radians(angle_start_deg), math.radians(angle_end_deg)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    xi, yi = cx + rin * cm, cy + rin * sm
    xo, yo = cx + rout * cm, cy + rout * sm
    return Brush(
        [
            Face((cx, cy, z2), (cx, cy + 1, z2), (cx + 1, cy, z2), tex),  # top cap
            Face((cx, cy, z1), (cx + 1, cy, z1), (cx, cy + 1, z1), tex),  # bottom cap
            Face((cx, cy, z2), (cx + c1, cy + s1, z2), (cx, cy, z1), tex),  # radial t1
            Face((cx, cy, z2), (cx, cy, z1), (cx + c2, cy + s2, z2), tex),  # radial t2
            Face(
                (xi, yi, z2), (xi, yi, z1), (xi - sm, yi + cm, z2), tex
            ),  # inner curved
            Face(
                (xo, yo, z2), (xo - sm, yo + cm, z2), (xo, yo, z1), tex
            ),  # outer curved
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
    if segs <= 0:
        raise ValueError(f"segs must be > 0 (got {segs})")
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


def tile_grid_origins(width, height, tile=34, gap=3):
    """Centred grid of (x_offset, z_offset) origins for square tiles filling a
    width x height rectangle (both relative to 0,0). Shared by the plate
    helpers below and any custom (e.g. sheared) plate placement."""
    pitch = tile + gap
    nx = max(1, int((width + gap) // pitch))
    nz = max(1, int((height + gap) // pitch))
    total_x = nx * tile + (nx - 1) * gap
    total_z = nz * tile + (nz - 1) * gap
    ox = (width - total_x) / 2.0
    oz = (height - total_z) / 2.0
    return [(ox + i * pitch, oz + k * pitch) for i in range(nx) for k in range(nz)]


def tile_face_plates(x_face, thickness, y1, y2, z1, z2, tex, tile=34, gap=3):
    """Decorative grid of square plate brushes applied to a flat X-facing wall
    (e.g. the east/west end-face of a bridge pier).

    Fills the y1..y2 / z1..z2 rectangle with a centred grid of square tiles
    (pitch = tile + gap), each protruding from the flat face at ``x_face`` by
    ``thickness`` (sign gives the protrusion direction: positive grows toward
    +X, negative toward -X).
    """
    x1v, x2v = (
        (x_face, x_face + thickness) if thickness >= 0 else (x_face + thickness, x_face)
    )
    brushes = []
    for dy, dz in tile_grid_origins(y2 - y1, z2 - z1, tile=tile, gap=gap):
        ty1 = y1 + dy
        tz1 = z1 + dz
        brushes.append(box(x1v, ty1, tz1, x2v, ty1 + tile, tz1 + tile, tex))
    return brushes


def oriented_plate_x(x1, x2, cy, cz, half_tan, half_rad, angle_deg, tex):
    """Square (or rectangular) plate brush extruded along X, whose Y-Z
    cross-section is rotated by ``angle_deg`` around (cy, cz) instead of
    staying axis-aligned. ``half_tan``/``half_rad`` are half-extents along the
    rotated cross-section's own axes: the "tangential" axis (at angle_deg=0,
    this is +Z) and the "radial" axis (at angle_deg=0, this is +Y) — matching
    a point at (cy + radius, cz) on a circle, where the tangent direction is
    +Z and the radial direction is +Y. Used to build voussoir-style plates
    that rotate to follow an arch curve (see arch_plate_ring)."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)

    def corner(s_tan, s_rad):
        return (
            cy + s_rad * half_rad * ca - s_tan * half_tan * sa,
            cz + s_rad * half_rad * sa + s_tan * half_tan * ca,
        )

    # box()'s face winding assumes going A->B varies only the "Y-like" axis
    # (s_rad here) and A->C varies only the "Z-like" axis (s_tan here) — so
    # c10/c01 below are intentionally not a plain (su,sv) grid; they're
    # chosen to keep that same correspondence after rotation.
    c00 = corner(-1, -1)
    c10 = corner(-1, 1)
    c01 = corner(1, -1)
    c11 = corner(1, 1)

    def p(x, c):
        return (x, c[0], c[1])

    return Brush(
        [
            Face(p(x1, c00), p(x1, c10), p(x1, c01), tex),
            Face(p(x2, c00), p(x2, c01), p(x2, c10), tex),
            Face(p(x1, c00), p(x1, c01), p(x2, c00), tex),
            Face(p(x1, c10), p(x2, c10), p(x1, c11), tex),
            Face(p(x1, c00), p(x2, c00), p(x1, c10), tex),
            Face(p(x1, c01), p(x1, c11), p(x2, c01), tex),
        ]
    )


def arch_plate_ring(x_face, thickness, yc, zc, radius, tex, tile=34, gap=3):
    """Curved ring of small square decorative plates traced along a semicircular
    arc (centred at Y=yc, Z=zc, given ``radius``), applied to a flat X-facing
    wall (e.g. the east/west end-face of a bridge pier arch). Spans angle
    0..180deg, where 0deg = +Y spring point and 180deg = -Y spring point,
    mirroring arch_seg's convention — i.e. a voussoir-style ring tracing the
    arch curve above the opening. Each plate is rotated to match its own
    position angle (like a real voussoir stone, oriented radially) instead of
    staying axis-aligned.

    ``thickness``: protrusion from the flat face at ``x_face`` (sign gives
    the direction: positive toward +X, negative toward -X), same convention
    as tile_face_plates.
    """
    x1v, x2v = (
        (x_face, x_face + thickness) if thickness >= 0 else (x_face + thickness, x_face)
    )
    pitch = tile + gap
    segs = max(1, int((math.pi * radius) // pitch))
    step = 180.0 / segs
    brushes = []
    for seg_index in range(segs):
        angle_deg = (seg_index + 0.5) * step
        angle = math.radians(angle_deg)
        cy = yc + radius * math.cos(angle)
        cz = zc + radius * math.sin(angle)
        brushes.append(
            oriented_plate_x(x1v, x2v, cy, cz, tile / 2, tile / 2, angle_deg, tex)
        )
    return brushes


def square_wall(
    x1,
    x2,
    y1,
    y2,
    floor_z,
    ceil_z,
    open_hw,
    tex,
    overhang=0,
    base_h=0,
    yc=0.0,
    base_cap_h=0,
    base_cap_tex=None,
    base_cap_ovh=0,
):
    """Stone wall with a rectangular (square-topped) opening centred at Y=yc (default 0).
    open_hw: half-width of the opening in Y.
    overhang: extra Y extent on pillar portions beyond open_hw.
    base_h: solid plinth height at ground level.
    base_cap_h/base_cap_tex/base_cap_ovh: optional cement cap slab on top of plinth.
    """
    brushes = []
    ext = open_hw + overhang
    if y1 < yc - ext:
        brushes.append(box(x1, y1, floor_z, x2, yc - ext, ceil_z, tex))
    if y2 > yc + ext:
        brushes.append(box(x1, yc + ext, floor_z, x2, y2, ceil_z, tex))
    brushes.append(
        box(x1, yc - ext, floor_z, x2, yc - open_hw, ceil_z, tex)
    )  # south pillar
    brushes.append(
        box(x1, yc + open_hw, floor_z, x2, yc + ext, ceil_z, tex)
    )  # north pillar
    brushes.append(
        box(x1, yc - open_hw, ceil_z - 16, x2, yc + open_hw, ceil_z, tex)
    )  # lintel
    if base_h > 0:
        brushes.append(
            box(x1, yc - open_hw, floor_z, x2, yc + open_hw, floor_z + base_h, tex)
        )
        if base_cap_h > 0:
            cap_tex = base_cap_tex or tex
            cx1, cx2 = x1 - base_cap_ovh, x2 + base_cap_ovh
            crin = open_hw + base_cap_ovh
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
    if segs <= 0:
        raise ValueError(f"segs must be > 0 (got {segs})")
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
    if not freestanding and rout < rin * math.sqrt(2):
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
    if segs <= 0:
        raise ValueError(f"segs must be > 0 (got {segs})")
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


def torch_flame(x, y, z, light="300", flame_dz=4, flame_cls="light_flame_large_yellow"):
    """Return [light entity, flame entity] for a torch fixture, both tagged
    with the "torch" light group (see generate_map.py's LIGHT_GROUP_FLAGS) so
    they can be re-enabled together independent of other "light"-classname
    entities. The flame sits flame_dz above the light's own origin."""
    return [
        ent("light", origin=f"{x} {y} {z}", light=light, _light_group="torch"),
        ent(flame_cls, origin=f"{x} {y} {z + flame_dz}", _light_group="torch"),
    ]


def torch_flame_only(x, y, z, flame_cls="light_flame_large_yellow"):
    """Return a single flame entity (no separate light source — used where
    the flame model's own built-in light is enough), tagged with the "torch"
    light group like torch_flame()."""
    return ent(flame_cls, origin=f"{x} {y} {z}", _light_group="torch")


def layered_wall(x1, y1, z1, x2, y2, z2, openings, tex, ts=None, tn=None, tf=None):
    """Wall slab (thin in Y) with rectangular cutouts.
    openings: list of (ox1, oz1, ox2, oz2) — regions to omit in the x,z plane.
    ts: override texture for the south (-Y) face; tn: north (+Y) face.
    tf: texture for the reveal faces (jambs/lintels) exposed by openings.
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
                kw = {}
                if tf:
                    # Apply tf to faces that are exposed by an adjacent opening.
                    for o in openings:
                        # Left jamb: this piece's east face borders the opening on the left
                        if cx2 == o[0] and cz1 < o[3] and cz2 > o[1]:
                            kw["te"] = tf
                        # Right jamb: this piece's west face borders the opening on the right
                        if cx1 == o[2] and cz1 < o[3] and cz2 > o[1]:
                            kw["tw"] = tf
                        # Lintel soffit: this piece's bottom face is above the opening
                        if cz1 == o[3] and cx1 < o[2] and cx2 > o[0]:
                            kw["tb"] = tf
                        # Sill top: this piece's top face is below the opening
                        if cz2 == o[1] and cx1 < o[2] and cx2 > o[0]:
                            kw["tt"] = tf
                brushes.append(box(cx1, y1, cz1, cx2, y2, cz2, tex, ts=ts, tn=tn, **kw))
    return brushes


def layered_wall_y(y1, x1, z1, y2, x2, z2, openings, tex, tw=None, te=None):
    """Wall slab (thin in X) with rectangular cutouts.
    openings: list of (oy1, oz1, oy2, oz2) — regions to omit in the y,z plane.
    tw: override texture for the west (-X) face; te: east (+X) face.
    Derived from layered_wall via XY swap."""
    return [
        swap_xy(b)
        for b in layered_wall(y1, x1, z1, y2, x2, z2, openings, tex, ts=tw, tn=te)
    ]


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

    Consecutive lit pixels in a row are merged into a single box so dense glyphs
    (e.g. E) don't generate internal T-junctions that sparkle/garble at render time.
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
            run_start = None
            for col_i in range(cols + 1):
                src_col = (cols - 1 - col_i) if mirror else col_i
                lit = col_i < cols and (row_bits & (1 << (cols - 1 - src_col)))
                if lit and run_start is None:
                    run_start = col_i
                elif not lit and run_start is not None:
                    px1 = cx + run_start * px_w
                    px2 = cx + col_i * px_w
                    brushes.append(
                        box(px1, y_face, z, px2, y_face + depth, z + px_h, tex)
                    )
                    run_start = None
    return brushes


def iron_fence(
    segments,
    x1,
    x2,
    tex,
    z_base,
    height=80,
    spacing=16,
    circle_rin=5,
    circle_rout=8,
):
    """Build an iron fence for each (y1, y2) span in segments.

    Each span gets a top rail, a second crossbeam a few inches below it,
    vertical pickets (every spacing units; every 10th is a wider post), and a
    small decorative circle (8-segment octagon ring) in the gap between every
    pair of pickets, sitting in the Z gap between the two top rails.

    Returns a flat list of brushes; the caller groups them into a func_detail.
    """
    if spacing <= 0:
        raise ValueError(f"iron_fence: spacing must be > 0 (got {spacing})")
    brushes = []
    circle_cz = z_base + height - 8  # midpoint of the gap between the two beams
    for fy1, fy2 in segments:
        # Top rail
        brushes.append(box(x1, fy1, z_base + height - 2, x2, fy2, z_base + height, tex))
        # Second crossbeam — a few inches below the top rail
        brushes.append(
            box(x1, fy1, z_base + height - 16, x2, fy2, z_base + height - 14, tex)
        )
        picket_y = fy1
        picket_index = 0
        while True:
            picket_w = 8 if picket_index % 10 == 0 else 2
            if picket_y + picket_w > fy2:
                break
            brushes.append(
                box(x1, picket_y, z_base, x2, picket_y + picket_w, z_base + height, tex)
            )
            picket_y += spacing
            picket_index += 1
        # Proper iron circle (8-segment octagon ring) in every gap between
        # adjacent pickets, sitting in the Z gap between the two top rails
        circle_cy = fy1 + spacing // 2
        while circle_cy + circle_rout <= fy2:
            # 8 arch_seg calls × 45° = full 360° circle ring in the Y-Z plane
            for seg_i in range(8):
                brushes.append(
                    arch_seg(
                        x1,
                        x2,
                        circle_cy,
                        float(circle_cz),
                        circle_rin,
                        circle_rout,
                        seg_i * 45,
                        (seg_i + 1) * 45,
                        tex,
                    )
                )
            circle_cy += spacing
    return brushes
