"""Low-level convex brush constructors and clipping helpers."""

import math

from ..mapdata import Brush, Face
from ..utils import swap_xy, swap_xz


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
    tb_params="0 0 0 1 1",
    tw=None,
    te=None,
    ts=None,
    tn=None,
):
    """Return an axis-aligned rectangular brush.

    ``tex`` is the default face texture; ``tt``/``tb``/``tw``/``te``/``ts``/``tn``
    override the top, bottom, west, east, south, and north faces respectively.
    Raises ``ValueError`` if any span collapses to zero after min/max normalization.
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
    # Accept reversed min/max bounds by normalizing them before building the brush.
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    if z1 > z2:
        z1, z2 = z2, z1
    if x1 == x2 or y1 == y2 or z1 == z2:
        raise ValueError(
            f"box: degenerate (zero-thickness) brush "
            f"({x1}, {y1}, {z1}) - ({x2}, {y2}, {z2})"
        )
    return Brush(
        [
            Face((x1, y1, z1), (x1, y2, z1), (x1, y1, z2), tw),
            Face((x2, y1, z1), (x2, y1, z2), (x2, y2, z1), te),
            Face((x1, y1, z1), (x1, y1, z2), (x2, y1, z1), ts),
            Face((x1, y2, z1), (x2, y2, z1), (x1, y2, z2), tn),
            Face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tb, tb_params),
            Face((x1, y1, z2), (x1, y2, z2), (x2, y1, z2), tt, tt_params),
        ]
    )


def box_with_hole(x1, y1, z1, x2, y2, z2, hx1, hy1, hx2, hy2, tex, **kw):
    """Return up to four rectangular brushes for a box with an axis-aligned hole.

    The hole is clipped to the outer XY bounds; if nothing remains of it, this
    returns a single ``box()`` brush instead.
    """
    # Normalize outer and hole bounds before clipping the opening.
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    if hx1 > hx2:
        hx1, hx2 = hx2, hx1
    if hy1 > hy2:
        hy1, hy2 = hy2, hy1
    hx1, hx2 = max(hx1, x1), min(hx2, x2)
    hy1, hy2 = max(hy1, y1), min(hy2, y2)
    if hx1 >= hx2 or hy1 >= hy2:
        return [box(x1, y1, z1, x2, y2, z2, tex, **kw)]
    out = []
    if x1 < hx1:
        out.append(box(x1, y1, z1, hx1, y2, z2, tex, **kw))
    if hx2 < x2:
        out.append(box(hx2, y1, z1, x2, y2, z2, tex, **kw))
    if y1 < hy1:
        out.append(box(hx1, y1, z1, hx2, hy1, z2, tex, **kw))
    if hy2 < y2:
        out.append(box(hx1, hy2, z1, hx2, y2, z2, tex, **kw))
    return out


def polygon_prism(pts, z1, z2, tex):
    """Return a convex vertical prism extruded from an XY polygon.

    The footprint is rewound counter-clockwise if needed so side faces point
    outward. Raises ``ValueError`` for fewer than three points, zero height,
    zero-area footprints, or non-convex input.
    """
    if len(pts) < 3:
        raise ValueError(f"polygon_prism() requires at least 3 points, got {len(pts)}")
    if z1 == z2:
        raise ValueError(f"polygon_prism: degenerate (zero-height) prism at z={z1}")
    # Accept reversed Z bounds by normalizing them before building the prism.
    if z1 > z2:
        z1, z2 = z2, z1
    # Use counter-clockwise winding so the side faces point outward.
    signed_area2 = sum(
        pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
        for i in range(len(pts))
    )
    if abs(signed_area2) < 1e-6:
        raise ValueError(
            f"polygon_prism: degenerate (zero-area/collinear) polygon {pts}"
        )
    if signed_area2 < 0:
        pts = list(reversed(pts))
    n = len(pts)
    # A Brush is the intersection of its face half-spaces, which is only
    # convex if the footprint itself is convex; reject concave/self-
    # intersecting input rather than silently building the wrong solid.
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        cx, cy = pts[(i + 2) % n]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if cross < -1e-6:
            raise ValueError(
                f"polygon_prism: requires a convex polygon (a Brush is the "
                f"intersection of its face half-spaces), got a concave/"
                f"self-intersecting footprint {pts}"
            )
    faces = []
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        faces.append(Face((ax, ay, z2), (bx, by, z2), (ax, ay, z1), tex))
    (x0, y0), (x1_, y1_), (x2_, y2_) = pts[0], pts[1], pts[2]
    faces.append(Face((x0, y0, z1), (x1_, y1_, z1), (x2_, y2_, z1), tex))
    faces.append(Face((x0, y0, z2), (x2_, y2_, z2), (x1_, y1_, z2), tex))
    return Brush(faces)


def clip_poly_to_rect(poly, x1, y1, x2, y2):
    """Clip a 2D polygon to an axis-aligned rectangle in XY."""

    def clip_edge(pts, inside, intersect):
        """Clip a polygon ring against one half-plane."""
        out = []
        n = len(pts)
        for i in range(n):
            cur, prv = pts[i], pts[i - 1]
            cur_in, prv_in = inside(cur), inside(prv)
            if cur_in:
                if not prv_in:
                    out.append(intersect(prv, cur))
                out.append(cur)
            elif prv_in:
                out.append(intersect(prv, cur))
        return out

    def isect_x(p, q, xv):
        """Return the segment intersection with the vertical line ``x = xv``."""
        px, py = p
        qx, qy = q
        t = (xv - px) / (qx - px)
        return (xv, py + t * (qy - py))

    def isect_y(p, q, yv):
        """Return the segment intersection with the horizontal line ``y = yv``."""
        px, py = p
        qx, qy = q
        t = (yv - py) / (qy - py)
        return (px + t * (qx - px), yv)

    pts = list(poly)
    pts = clip_edge(pts, lambda p: p[0] >= x1, lambda p, q: isect_x(p, q, x1))
    if not pts:
        return []
    pts = clip_edge(pts, lambda p: p[0] <= x2, lambda p, q: isect_x(p, q, x2))
    if not pts:
        return []
    pts = clip_edge(pts, lambda p: p[1] >= y1, lambda p, q: isect_y(p, q, y1))
    if not pts:
        return []
    pts = clip_edge(pts, lambda p: p[1] <= y2, lambda p, q: isect_y(p, q, y2))
    return pts


def radial_fan_fills(cx, cy, r, x1, y1, x2, y2, z1, z2, tex, n=32):
    """Return convex prism fills between a circle and a clipping rectangle.

    The result is a list of pie-slice-derived brushes that fill the rectangular
    corners left after subtracting a round opening. Raises ``ValueError`` if
    ``n < 3``.
    """
    if n < 3:
        raise ValueError(f"radial_fan_fills: n must be >= 3, got {n}")
    sx1, sy1, sx2, sy2 = cx - r, cy - r, cx + r, cy + r
    verts = []
    box_pts = []
    for i in range(n):
        theta = 2 * math.pi * i / n
        dx, dy = math.cos(theta), math.sin(theta)
        vx, vy = cx + r * dx, cy + r * dy
        verts.append((vx, vy))
        candidates = []
        if dx > 0:
            candidates.append((sx2 - cx) / dx)
        elif dx < 0:
            candidates.append((sx1 - cx) / dx)
        if dy > 0:
            candidates.append((sy2 - cy) / dy)
        elif dy < 0:
            candidates.append((sy1 - cy) / dy)
        t = min(candidates)
        box_pts.append((cx + t * dx, cy + t * dy))
    fills = []
    for i in range(n):
        j = (i + 1) % n
        quad = [verts[j], verts[i], box_pts[i], box_pts[j]]
        clipped = clip_poly_to_rect(quad, x1, y1, x2, y2)
        deduped = []
        for p in clipped:
            if (
                not deduped
                or math.hypot(p[0] - deduped[-1][0], p[1] - deduped[-1][1]) > 1e-4
            ):
                deduped.append(p)
        if (
            len(deduped) > 1
            and math.hypot(
                deduped[0][0] - deduped[-1][0], deduped[0][1] - deduped[-1][1]
            )
            < 1e-4
        ):
            deduped.pop()
        clipped = deduped
        if len(clipped) < 3:
            continue
        area2 = sum(
            clipped[k][0] * clipped[(k + 1) % len(clipped)][1]
            - clipped[(k + 1) % len(clipped)][0] * clipped[k][1]
            for k in range(len(clipped))
        )
        if abs(area2) < 1e-6:
            continue
        fills.append(polygon_prism(clipped, z1, z2, tex))
    return fills


def box_with_round_hole(x1, y1, z1, x2, y2, z2, cx, cy, r, tex, n=32, **kw):
    """Return brushes for a box with a round XY opening approximated by ``n`` sides."""
    pieces = box_with_hole(
        x1, y1, z1, x2, y2, z2, cx - r, cy - r, cx + r, cy + r, tex, **kw
    )
    pieces += radial_fan_fills(cx, cy, r, x1, y1, x2, y2, z1, z2, tex, n)
    return pieces


def shear_box_y(
    x1, y1, z1, x2, y2, z2, s1, s2, tex, tt=None, tb=None, tb_params="0 0 0 1 1"
):
    """Return a box whose Y span is offset independently at ``x1`` and ``x2``.

    ``s1`` and ``s2`` shift both Y edges at the west and east ends, so the
    brush is sheared along X. Raises ``ValueError`` for any zero-thickness span.
    """
    tt, tb = tt or tex, tb or tex
    if x1 == x2 or y1 == y2 or z1 == z2:
        raise ValueError(
            f"shear_box_y: degenerate (zero-thickness) brush "
            f"({x1}, {y1}, {z1}) - ({x2}, {y2}, {z2})"
        )
    y1a, y2a = y1 + s1, y2 + s1
    y1b, y2b = y1 + s2, y2 + s2
    return Brush(
        [
            Face((x1, y1a, z1), (x1, y2a, z1), (x1, y1a, z2), tex),
            Face((x2, y1b, z1), (x2, y1b, z2), (x2, y2b, z1), tex),
            Face((x1, y1a, z1), (x1, y1a, z2), (x2, y1b, z1), tex),
            Face((x1, y2a, z1), (x2, y2b, z1), (x1, y2a, z2), tex),
            Face((x1, y1a, z1), (x2, y1b, z1), (x1, y2a, z1), tb, tb_params),
            Face((x1, y1a, z2), (x1, y2a, z2), (x2, y1b, z2), tt),
        ]
    )


def shear_box_z(x1, y1, z1, x2, y2, z2, s1, s2, tex):
    """Return ``shear_box_y()`` with X and Z swapped, i.e. sheared along Z."""
    return swap_xz(shear_box_y(z1, y1, x1, z2, y2, x2, s1, s2, tex))


def taper_box_y(
    x1,
    y1a,
    y2a,
    z1,
    x2,
    y1b,
    y2b,
    z2,
    tex,
    tt=None,
    tb=None,
    tt_params="0 0 0 1 1",
    tb_params="0 0 0 1 1",
):
    """Return a trapezoidal prism whose Y span is specified independently at x1 and x2.

    Unlike shear_box_y(), this accepts the south and north edges directly at each X
    endpoint, so the footprint can taper asymmetrically.
    """
    tt, tb = tt or tex, tb or tex
    if x1 == x2 or z1 == z2:
        raise ValueError(
            f"taper_box_y: degenerate (zero-thickness) brush x=({x1}, {x2}) "
            f"z=({z1}, {z2})"
        )
    if y1a == y2a and y1b == y2b:
        raise ValueError(
            f"taper_box_y: degenerate (zero-width everywhere) footprint "
            f"y=({y1a}, {y2a}) at x1, y=({y1b}, {y2b}) at x2"
        )
    faces = []
    # The x1/x2 end caps and the top/bottom faces all pick 3 points from the (up to 4)
    # corners at that Z/end. If one end's width collapses to zero (y1a == y2a or
    # y1b == y2b), the corners at that end coincide, so those faces must fall back to
    # the opposite end's corners to keep 3 distinct points (avoiding a degenerate face).
    if y1a != y2a:
        faces.append(Face((x1, y1a, z1), (x1, y2a, z1), (x1, y1a, z2), tex))
    if y1b != y2b:
        faces.append(Face((x2, y1b, z1), (x2, y1b, z2), (x2, y2b, z1), tex))
    faces += [
        Face((x1, y1a, z1), (x1, y1a, z2), (x2, y1b, z1), tex),
        Face((x1, y2a, z1), (x2, y2b, z1), (x1, y2a, z2), tex),
    ]
    if y1a != y2a:
        bottom = (x1, y1a, z1), (x2, y1b, z1), (x1, y2a, z1)
        top = (x1, y1a, z2), (x1, y2a, z2), (x2, y1b, z2)
    else:
        bottom = (x1, y1a, z1), (x2, y1b, z1), (x2, y2b, z1)
        top = (x1, y1a, z2), (x2, y1b, z2), (x2, y2b, z2)
    faces += [
        Face(*bottom, tb, tb_params),
        Face(*top, tt, tt_params),
    ]
    return Brush(faces)


def taper_box_x(
    y1,
    x1a,
    x2a,
    z1,
    y2,
    x1b,
    x2b,
    z2,
    tex,
    tt=None,
    tb=None,
    tt_params="0 0 0 1 1",
    tb_params="0 0 0 1 1",
):
    """Return taper_box_y() with the X and Y axes swapped.

    The X span is specified independently at y1 and y2, which produces a prism that
    tapers along Y instead of X.
    """
    return swap_xy(
        taper_box_y(
            y1,
            x1a,
            x2a,
            z1,
            y2,
            x1b,
            x2b,
            z2,
            tex,
            tt=tt,
            tb=tb,
            tt_params=tt_params,
            tb_params=tb_params,
        )
    )


def shear_pyramid_y(x1, y1, x2, y2, z1, z2, s1, s2, tex):
    """Return a pyramid whose rectangular base is Y-sheared between ``x1`` and ``x2``.

    ``s1`` and ``s2`` offset the two X-end cross-sections before the apex is
    placed at the averaged sheared center. Raises ``ValueError`` for zero spans.
    """
    if x1 == x2 or y1 == y2 or z1 == z2:
        raise ValueError(
            f"shear_pyramid_y: degenerate (zero-thickness) brush "
            f"x=({x1}, {x2}) y=({y1}, {y2}) z=({z1}, {z2})"
        )
    y1a, y2a = y1 + s1, y2 + s1
    y1b, y2b = y1 + s2, y2 + s2
    apex = ((x1 + x2) / 2.0, (y1a + y2a + y1b + y2b) / 4.0, z2)
    return Brush(
        [
            Face((x1, y1a, z1), (x2, y1b, z1), (x1, y2a, z1), tex),
            Face((x2, y1b, z1), (x1, y1a, z1), apex, tex),
            Face((x1, y2a, z1), (x2, y2b, z1), apex, tex),
            Face((x1, y1a, z1), (x1, y2a, z1), apex, tex),
            Face((x2, y2b, z1), (x2, y1b, z1), apex, tex),
        ]
    )


def pyramid(x1, y1, z1, x2, y2, z2, tex):
    """Return a rectangular pyramid with its apex at the box center on ``z2``.

    Raises ``ValueError`` if any axis span is zero.
    """
    if x1 == x2 or y1 == y2 or z1 == z2:
        raise ValueError(
            f"pyramid: degenerate (zero-thickness) brush "
            f"({x1}, {y1}, {z1}) - ({x2}, {y2}, {z2})"
        )
    cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    apex = (cx, cy, z2)
    return Brush(
        [
            Face((x1, y1, z1), (x2, y1, z1), (x1, y2, z1), tex),
            Face((x2, y1, z1), (x1, y1, z1), apex, tex),
            Face((x1, y2, z1), (x2, y2, z1), apex, tex),
            Face((x1, y1, z1), (x1, y2, z1), apex, tex),
            Face((x2, y2, z1), (x2, y1, z1), apex, tex),
        ]
    )


def ramp_slab(
    x1,
    x2,
    y1,
    y2,
    zb1,
    zb2,
    zt1,
    zt2,
    tex,
    tt=None,
    tb=None,
    te=None,
    tw=None,
    ts=None,
    tt_params="0 0 0 1 1",
    tb_params="0 0 0 1 1",
):
    """Return a slab whose top and bottom heights vary linearly along X.

    ``zb1``/``zt1`` apply at ``x1`` and ``zb2``/``zt2`` at ``x2``; ``tt``/``tb``
    override the top and bottom textures, while ``te``/``tw``/``ts`` control
    the east, west, and long side faces. Raises ``ValueError`` for zero X/Y span
    or zero thickness at both ends.
    """
    tt, tb, te, tw, ts = tt or tex, tb or tex, te or tex, tw or tex, ts or tex
    if x1 > x2:
        # Keep the slab ordered from x1 to x2 and swap the paired Z values with it.
        x1, x2 = x2, x1
        zb1, zb2 = zb2, zb1
        zt1, zt2 = zt2, zt1
        tw, te = te, tw
    if x1 == x2 or y1 == y2:
        raise ValueError(
            f"ramp_slab: degenerate (zero-span) brush x=({x1}, {x2}) y=({y1}, {y2})"
        )
    if zt1 == zb1 and zt2 == zb2:
        raise ValueError(
            f"ramp_slab: degenerate (zero-thickness everywhere) brush "
            f"zb=({zb1}, {zb2}) zt=({zt1}, {zt2}) — use box() for a flat slab"
        )
    faces = []
    if zt1 != zb1:
        faces.append(Face((x1, y1, zb1), (x1, y2, zb1), (x1, y1, zt1), tw))
    if zt2 != zb2:
        faces.append(Face((x2, y1, zb2), (x2, y1, zt2), (x2, y2, zb2), te))
    # The side (ts) faces are the sloped planes running along y1/y2. Their plane is
    # defined by any 3 distinct points among the 4 side corners; when the x1 end is
    # collapsed (zt1 == zb1) the (x1, zb1)/(x1, zt1) corners coincide, so fall back to
    # the x2 corners to keep the 3 chosen points distinct (and vice versa for x2).
    if zt1 != zb1:
        s1 = (x1, y1, zb1), (x1, y1, zt1), (x2, y1, zb2)
        s2 = (x1, y2, zb1), (x2, y2, zb2), (x1, y2, zt1)
    else:
        s1 = (x1, y1, zb1), (x2, y1, zb2), (x2, y1, zt2)
        s2 = (x1, y2, zb1), (x2, y2, zb2), (x2, y2, zt2)
    faces += [
        Face(*s1, ts),
        Face(*s2, ts),
        Face((x1, y1, zb1), (x2, y1, zb2), (x1, y2, zb1), tb, tb_params),
        Face((x1, y1, zt1), (x1, y2, zt1), (x2, y1, zt2), tt, tt_params),
    ]
    return Brush(faces)


def ramp_slab_y(
    x1,
    x2,
    y1,
    y2,
    zb1,
    zb2,
    zt1,
    zt2,
    tex,
    tt=None,
    tb=None,
    te=None,
    ts=None,
    tt_params="0 0 0 1 1",
):
    """Return ``ramp_slab()`` with the slope running along Y instead of X."""
    if y1 > y2:
        y1, y2 = y2, y1
        zb1, zb2 = zb2, zb1
        zt1, zt2 = zt2, zt1
    return swap_xy(
        ramp_slab(
            y1,
            y2,
            x1,
            x2,
            zb1,
            zb2,
            zt1,
            zt2,
            tex,
            tt=tt,
            tb=tb,
            te=te,
            ts=ts,
            tt_params=tt_params,
        )
    )


def slab_chamfered_y(x1, x2, y1, y2, zb, zt1, zt2, tex, tt=None, chamfer=4.0):
    """Return ``ramp_slab_y()`` with extra top faces beveling the two Y ends."""
    if y1 > y2:
        y1, y2 = y2, y1
        zt1, zt2 = zt2, zt1
    brush = ramp_slab_y(x1, x2, y1, y2, zb, zb, zt1, zt2, tex, tt=tt)
    c, tt = chamfer, tt or tex
    brush.faces.append(
        Face((x1, y1, zt1 - c), (x1, y1 + c, zt1), (x2, y1, zt1 - c), tt)
    )
    brush.faces.append(
        Face((x1, y2, zt2 - c), (x2, y2, zt2 - c), (x1, y2 - c, zt2), tt)
    )
    return brush


def corner_ramp(x_apex, y_apex, x_far, y_far, z_base, z_hi, tex, tt=None):
    """Return a triangular corner ramp rising from the far rectangle corner to one apex.

    The high corner sits at ``(x_apex, y_apex, z_hi)`` and the footprint extends
    to ``x_far`` and ``y_far``. Raises ``ValueError`` for zero height or footprint.
    """
    tt = tt or tex
    if z_base == z_hi:
        raise ValueError(
            f"corner_ramp: degenerate (zero-height) ramp z=({z_base}, {z_hi})"
        )
    if x_far == x_apex or y_far == y_apex:
        raise ValueError(
            f"corner_ramp: degenerate (zero-footprint) ramp "
            f"apex=({x_apex}, {y_apex}) far=({x_far}, {y_far})"
        )
    a, b, c, d = (
        (x_apex, y_apex, z_hi),
        (x_apex, y_apex, z_base),
        (x_apex, y_far, z_base),
        (x_far, y_apex, z_base),
    )
    if (x_far - x_apex) * (y_far - y_apex) < 0:
        faces = [
            Face(b, c, d, tex),
            Face(a, c, b, tex),
            Face(a, b, d, tex),
            Face(a, d, c, tt),
        ]
    else:
        faces = [
            Face(b, d, c, tex),
            Face(a, b, c, tex),
            Face(a, d, b, tex),
            Face(a, c, d, tt),
        ]
    return Brush(faces)


def tri_prism(ax, ay, bx, by, cx, cy, z1, z2, tex):
    """Return a prism extruded from a counter-clockwise XY triangle.

    Raises ``ValueError`` if ``z1 >= z2`` or if the triangle is collinear or
    clockwise-wound.
    """
    if z1 >= z2:
        raise ValueError(
            f"tri_prism: z1 must be < z2 (got z1={z1}, z2={z2}); "
            "swap z1/z2 rather than relying on silent inversion"
        )
    signed_area2 = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
    if abs(signed_area2) < 1e-6:
        raise ValueError(
            f"tri_prism: degenerate (zero-area/collinear) triangle "
            f"({ax}, {ay}), ({bx}, {by}), ({cx}, {cy})"
        )
    if signed_area2 < 0:
        raise ValueError(
            f"tri_prism: (a, b, c) must be wound counter-clockwise, got "
            f"clockwise winding for ({ax}, {ay}), ({bx}, {by}), ({cx}, {cy})"
        )
    return Brush(
        [
            Face((ax, ay, z2), (bx, by, z2), (ax, ay, z1), tex),
            Face((bx, by, z2), (cx, cy, z2), (bx, by, z1), tex),
            Face((cx, cy, z2), (ax, ay, z2), (cx, cy, z1), tex),
            Face((ax, ay, z1), (bx, by, z1), (cx, cy, z1), tex),
            Face((ax, ay, z2), (cx, cy, z2), (bx, by, z2), tex),
        ]
    )


def tri_ramp_prism(ax, ay, bx, by, cx, cy, zbot, za, zb, zc, tex, tt=None):
    """Return a triangular prism with a sloped top sampled at vertices ``a``, ``b``, ``c``.

    The base lies on ``zbot`` and the top face uses per-vertex heights
    ``za``/``zb``/``zc``. Raises ``ValueError`` for degenerate/clockwise
    footprints, for ``zbot`` above any top vertex, or for zero volume.
    """
    tt = tt or tex
    signed_area2 = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
    if abs(signed_area2) < 1e-6:
        raise ValueError(
            f"tri_ramp_prism: degenerate (zero-area/collinear) triangle "
            f"({ax}, {ay}), ({bx}, {by}), ({cx}, {cy})"
        )
    if signed_area2 < 0:
        raise ValueError(
            f"tri_ramp_prism: (a, b, c) must be wound counter-clockwise, got "
            f"clockwise winding for ({ax}, {ay}), ({bx}, {by}), ({cx}, {cy})"
        )
    if zbot > min(za, zb, zc):
        raise ValueError(
            f"tri_ramp_prism: zbot ({zbot}) must be <= za/zb/zc ({za}, {zb}, {zc})"
        )
    if zbot == max(za, zb, zc):
        raise ValueError(
            f"tri_ramp_prism: zbot ({zbot}) must be < at least one of "
            f"za/zb/zc ({za}, {zb}, {zc}), or the prism has zero volume"
        )
    return Brush(
        [
            Face((ax, ay, za), (bx, by, zb), (ax, ay, zbot), tex),
            Face((bx, by, zb), (cx, cy, zc), (bx, by, zbot), tex),
            Face((cx, cy, zc), (ax, ay, za), (cx, cy, zbot), tex),
            Face((ax, ay, zbot), (bx, by, zbot), (cx, cy, zbot), tex),
            Face((ax, ay, za), (cx, cy, zc), (bx, by, zb), tt),
        ]
    )


def arch_seg(xb, xf, yc, zc, rin, rout, angle_start_deg, angle_end_deg, tex):
    """Return an X-thickness annular arch segment in the YZ plane.

    ``angle_start_deg``/``angle_end_deg`` sweep around ``(yc, zc)`` from the
    positive Y axis toward positive Z. Raises ``ValueError`` for invalid radii,
    spans outside ``(0, 180]``, or reversed/degenerate X bounds.
    """
    if not (0 <= rin < rout):
        raise ValueError(
            f"arch_seg: requires 0 <= rin < rout, got rin={rin}, rout={rout}"
        )
    if angle_start_deg >= angle_end_deg:
        raise ValueError(
            f"arch_seg: requires angle_start_deg < angle_end_deg, got "
            f"{angle_start_deg} >= {angle_end_deg}"
        )
    if angle_end_deg - angle_start_deg > 180:
        raise ValueError(
            f"arch_seg: span must be <= 180 degrees (the wedge is bounded by "
            f"tangent planes at the midpoint angle, which is only valid for "
            f"spans up to a half-circle), got "
            f"{angle_end_deg - angle_start_deg}"
        )
    if xb == xf:
        raise ValueError(f"arch_seg: degenerate (zero-depth) segment at x={xb}")
    if xb > xf:
        raise ValueError(
            f"arch_seg: requires xb < xf, got xb={xb}, xf={xf}; reversed "
            "bounds would silently invert the segment's front/back faces"
        )
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


def arch_seg_chord(xb, xf, yc, zc, rin, rout, angle_start_deg, angle_end_deg, tex):
    """Return an X-thickness annular arch segment capped by endpoint chords.

    Unlike ``arch_seg()``, the inner and outer curved faces are bounded by
    planes through the start/end arc points. Raises ``ValueError`` under the
    same radius, angle-span, and X-bound preconditions as ``arch_seg()``.
    """
    if not (0 <= rin < rout):
        raise ValueError(
            f"arch_seg_chord: requires 0 <= rin < rout, got rin={rin}, rout={rout}"
        )
    if angle_start_deg >= angle_end_deg:
        raise ValueError(
            f"arch_seg_chord: requires angle_start_deg < angle_end_deg, got "
            f"{angle_start_deg} >= {angle_end_deg}"
        )
    if angle_end_deg - angle_start_deg > 180:
        raise ValueError(
            f"arch_seg_chord: span must be <= 180 degrees (the wedge is bounded "
            f"by tangent planes at the endpoints, which is only valid for "
            f"spans up to a half-circle), got "
            f"{angle_end_deg - angle_start_deg}"
        )
    if xb == xf:
        raise ValueError(f"arch_seg_chord: degenerate (zero-depth) segment at x={xb}")
    if xb > xf:
        raise ValueError(
            f"arch_seg_chord: requires xb < xf, got xb={xb}, xf={xf}; reversed "
            "bounds would silently invert the segment's front/back faces"
        )
    t1, t2 = math.radians(angle_start_deg), math.radians(angle_end_deg)
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    yi1, zi1 = yc + rin * c1, zc + rin * s1
    yi2, zi2 = yc + rin * c2, zc + rin * s2
    yo1, zo1 = yc + rout * c1, zc + rout * s1
    yo2, zo2 = yc + rout * c2, zc + rout * s2
    return Brush(
        [
            Face((xf, yc, zc), (xf, yc, zc + 1), (xf, yc + 1, zc), tex),
            Face((xb, yc, zc), (xb, yc + 1, zc), (xb, yc, zc + 1), tex),
            Face((xf, yc, zc), (xf, yc + c1, zc + s1), (xb, yc, zc), tex),
            Face((xf, yc, zc), (xb, yc, zc), (xf, yc + c2, zc + s2), tex),
            Face((xf, yi1, zi1), (xb, yi1, zi1), (xf, yi2, zi2), tex),
            Face((xf, yo1, zo1), (xf, yo2, zo2), (xb, yo1, zo1), tex),
        ]
    )


def curb_seg(cx, cy, z1, z2, rin, rout, angle_start_deg, angle_end_deg, tex):
    """Return a vertical annular curb segment extruded between ``z1`` and ``z2``.

    The arc is in the XY plane around ``(cx, cy)``. Raises ``ValueError`` for
    invalid radii, spans outside ``(0, 180]``, or reversed/degenerate Z bounds.
    """
    if not (0 <= rin < rout):
        raise ValueError(
            f"curb_seg: requires 0 <= rin < rout, got rin={rin}, rout={rout}"
        )
    if angle_start_deg >= angle_end_deg:
        raise ValueError(
            f"curb_seg: requires angle_start_deg < angle_end_deg, got "
            f"{angle_start_deg} >= {angle_end_deg}"
        )
    if angle_end_deg - angle_start_deg > 180:
        raise ValueError(
            f"curb_seg: span must be <= 180 degrees (the wedge is bounded by "
            f"tangent planes at the midpoint angle, which is only valid for "
            f"spans up to a half-circle), got "
            f"{angle_end_deg - angle_start_deg}"
        )
    if z1 == z2:
        raise ValueError(f"curb_seg: degenerate (zero-height) segment at z={z1}")
    if z1 > z2:
        raise ValueError(
            f"curb_seg: requires z1 < z2, got z1={z1}, z2={z2}; reversed "
            "bounds would silently invert the segment's top/bottom faces"
        )
    t1, t2 = math.radians(angle_start_deg), math.radians(angle_end_deg)
    tm = (t1 + t2) / 2.0
    c1, s1 = math.cos(t1), math.sin(t1)
    c2, s2 = math.cos(t2), math.sin(t2)
    cm, sm = math.cos(tm), math.sin(tm)
    xi, yi = cx + rin * cm, cy + rin * sm
    xo, yo = cx + rout * cm, cy + rout * sm
    return Brush(
        [
            Face((cx, cy, z2), (cx, cy + 1, z2), (cx + 1, cy, z2), tex),
            Face((cx, cy, z1), (cx + 1, cy, z1), (cx, cy + 1, z1), tex),
            Face((cx, cy, z2), (cx + c1, cy + s1, z2), (cx, cy, z1), tex),
            Face((cx, cy, z2), (cx, cy, z1), (cx + c2, cy + s2, z2), tex),
            Face((xi, yi, z2), (xi, yi, z1), (xi - sm, yi + cm, z2), tex),
            Face((xo, yo, z2), (xo - sm, yo + cm, z2), (xo, yo, z1), tex),
        ]
    )


def arch_pie_seg(xb, xf, yc, zc, rad, angle_start_deg, angle_end_deg, tex):
    """Return a solid pie-slice arch segment of radius ``rad`` and X thickness.

    This is the filled counterpart to ``arch_seg()`` with no inner radius.
    Raises ``ValueError`` for non-positive radius, spans outside ``(0, 180]``,
    or reversed/degenerate X bounds.
    """
    if rad <= 0:
        raise ValueError(f"arch_pie_seg: requires rad > 0, got rad={rad}")
    if angle_start_deg >= angle_end_deg:
        raise ValueError(
            f"arch_pie_seg: requires angle_start_deg < angle_end_deg, got "
            f"{angle_start_deg} >= {angle_end_deg}"
        )
    if angle_end_deg - angle_start_deg > 180:
        raise ValueError(
            f"arch_pie_seg: span must be <= 180 degrees (the wedge is bounded by "
            f"tangent planes at the midpoint angle, which is only valid for "
            f"spans up to a half-circle), got "
            f"{angle_end_deg - angle_start_deg}"
        )
    if xb == xf:
        raise ValueError(f"arch_pie_seg: degenerate (zero-depth) segment at x={xb}")
    if xb > xf:
        raise ValueError(
            f"arch_pie_seg: requires xb < xf, got xb={xb}, xf={xf}; reversed "
            "bounds would silently invert the segment's front/back faces"
        )
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


def arch_seg_y(yb, yf, xc, zc, rin, rout, angle_start_deg, angle_end_deg, tex):
    """Return ``arch_seg()`` with X and Y swapped, i.e. a segment extruded along Y."""
    return swap_xy(
        arch_seg(yb, yf, xc, zc, rin, rout, angle_start_deg, angle_end_deg, tex)
    )


def arch_pie_seg_y(yb, yf, xc, zc, rad, angle_start_deg, angle_end_deg, tex):
    """Return ``arch_pie_seg()`` with X and Y swapped, i.e. extruded along Y."""
    return swap_xy(
        arch_pie_seg(yb, yf, xc, zc, rad, angle_start_deg, angle_end_deg, tex)
    )
