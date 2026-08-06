"""Higher-level wall, arch, tiling, and window geometry builders."""

import math

from ..mapdata import Brush, Face
from ..utils import swap_xy
from .primitives import (
    arch_pie_seg,
    arch_seg,
    arch_seg_chord,
    arch_seg_y,
    box,
    ramp_slab,
)


def sidewalk_panel_spans(v1, v2, slab_len, gap, offset=0):
    """Return the ``(panels, joints)`` spans tiling ``[v1, v2)`` into a walk.

    Panels are ``slab_len`` long and separated by ``gap``-wide joints. The last
    panel is truncated at ``v2`` and no trailing joint is emitted, so the run
    always ends flush with ``v2``. ``offset`` shifts the panel grid backwards by
    that many units, so a parallel run (a curb beside a walk, say) can be given
    joints that fall in different places. Returns two lists of ``(start, end)``
    pairs.
    """
    if slab_len <= 0:
        raise ValueError(f"sidewalk_panel_spans: slab_len must be > 0, got {slab_len}")
    if gap < 0:
        raise ValueError(f"sidewalk_panel_spans: gap must be >= 0, got {gap}")
    if offset < 0:
        raise ValueError(f"sidewalk_panel_spans: offset must be >= 0, got {offset}")
    panels, joints = [], []
    step = slab_len + gap
    v = v1 - offset % step
    while v < v2:
        panel_end = min(v + slab_len, v2)
        # An offset that lands inside a joint clips away the leading panel.
        if panel_end > max(v, v1):
            panels.append((max(v, v1), panel_end))
        v += step
        if v < v2:
            joints.append((max(panel_end, v1), min(v, v2)))
    return panels, joints


def tile_grid_origins(width, height, tile=34, gap=3):
    """Return centered lower-left origins for a rectangular tile grid.

    Returns an empty list when the face is smaller than a single tile in either
    dimension.
    """
    # A face smaller than one tile produces no tile brushes.
    if width < tile or height < tile:
        return []
    pitch = tile + gap
    nx, nz = max(1, int((width + gap) // pitch)), max(1, int((height + gap) // pitch))
    total_x, total_z = nx * tile + (nx - 1) * gap, nz * tile + (nz - 1) * gap
    ox, oz = (width - total_x) / 2.0, (height - total_z) / 2.0
    return [(ox + i * pitch, oz + k * pitch) for i in range(nx) for k in range(nz)]


def tile_face_plates(x_face, thickness, y1, y2, z1, z2, tex, tile=34, gap=3):
    """Return thin tile boxes laid out on a wall face at constant ``x_face``.

    Positive ``thickness`` extrudes toward +X and negative toward -X. Raises
    ``ValueError`` if ``thickness`` is zero.
    """
    if thickness == 0:
        raise ValueError("tile_face_plates: thickness must be non-zero")
    x1v, x2v = (
        (x_face, x_face + thickness) if thickness >= 0 else (x_face + thickness, x_face)
    )
    brushes = []
    for dy, dz in tile_grid_origins(y2 - y1, z2 - z1, tile=tile, gap=gap):
        ty1, tz1 = y1 + dy, z1 + dz
        brushes.append(box(x1v, ty1, tz1, x2v, ty1 + tile, tz1 + tile, tex))
    return brushes


def arch_plate_ring(x_face, thickness, yc, zc, rin, tex, tile=34, gap=3):
    """Return one tile-thick arch-ring plates centered on ``(yc, zc)``.

    The ring spans 180 degrees in the YZ plane and uses ``arch_seg_chord()``
    segments sized to roughly match the requested tile pitch.
    """
    x1v, x2v = (
        (x_face, x_face + thickness) if thickness >= 0 else (x_face + thickness, x_face)
    )
    r1, r2 = rin, rin + tile
    r_avg, pitch = (r1 + r2) / 2.0, tile + gap
    segs = max(1, int((math.pi * r_avg) // pitch))
    step = 180.0 / segs
    gap_deg = math.degrees(gap / r_avg) if r_avg > 0 else 0.0
    brushes = []
    for seg_index in range(segs):
        a1, a2 = (
            seg_index * step + gap_deg / 2.0,
            (seg_index + 1) * step - gap_deg / 2.0,
        )
        if a2 <= a1:
            a1, a2 = seg_index * step, (seg_index + 1) * step
        brushes.append(arch_seg_chord(x1v, x2v, yc, zc, r1, r2, a1, a2, tex))
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
    base_ramp=None,
    yc=0.0,
    base_cap_h=0,
    base_cap_tex=None,
    base_cap_ovh=0,
    recess=None,
    lintel_h=16,
    base_cap_y1=None,
    base_cap_y2=None,
):
    """Return a rectangular wall with a centered opening along Y.

    ``open_hw`` is the half-width of the opening about ``yc``; optional base,
    cap, and recess parameters add trim or a recessed jamb. Raises
    ``ValueError`` if a positive-depth recess omits its texture.
    """
    brushes, ext = [], open_hw + overhang
    if y1 < yc - ext:
        brushes.append(box(x1, y1, floor_z, x2, yc - ext, ceil_z, tex))
    if y2 > yc + ext:
        brushes.append(box(x1, yc + ext, floor_z, x2, y2, ceil_z, tex))
    recess_margin, recess_depth, recess_tex = recess if recess else (0, 0, None)
    if recess is not None and recess_depth > 0 and recess_tex is None:
        raise ValueError(
            "square_wall: recess requires a texture (got recess=(...,  ..., None))"
        )
    rx1, rx2 = x1 + recess_margin, x2 - recess_margin
    if recess is not None and recess_depth > 0 and rx2 > rx1:
        brushes.append(box(x1, yc - ext, floor_z, rx1, yc - open_hw, ceil_z, tex))
        brushes.append(box(rx2, yc - ext, floor_z, x2, yc - open_hw, ceil_z, tex))
        brushes.append(
            box(rx1, yc - ext, floor_z, rx2, yc - open_hw - recess_depth, ceil_z, tex)
        )
        brushes.append(
            box(
                rx1,
                yc - open_hw - recess_depth,
                floor_z,
                rx2,
                yc - open_hw,
                ceil_z,
                recess_tex,
            )
        )
        brushes.append(box(x1, yc + open_hw, floor_z, rx1, yc + ext, ceil_z, tex))
        brushes.append(box(rx2, yc + open_hw, floor_z, x2, yc + ext, ceil_z, tex))
        brushes.append(
            box(rx1, yc + open_hw + recess_depth, floor_z, rx2, yc + ext, ceil_z, tex)
        )
        brushes.append(
            box(
                rx1,
                yc + open_hw,
                floor_z,
                rx2,
                yc + open_hw + recess_depth,
                ceil_z,
                recess_tex,
            )
        )
        brushes.append(
            box(x1, yc - open_hw, ceil_z - lintel_h, rx1, yc + open_hw, ceil_z, tex)
        )
        brushes.append(
            box(rx2, yc - open_hw, ceil_z - lintel_h, x2, yc + open_hw, ceil_z, tex)
        )
        brushes.append(
            box(
                rx1,
                yc - open_hw,
                ceil_z - lintel_h,
                rx2,
                yc + open_hw,
                ceil_z - recess_depth,
                tex,
            )
        )
        brushes.append(
            box(
                rx1,
                yc - open_hw,
                ceil_z - recess_depth,
                rx2,
                yc + open_hw,
                ceil_z,
                recess_tex,
            )
        )
    else:
        if ext > open_hw:
            brushes.append(box(x1, yc - ext, floor_z, x2, yc - open_hw, ceil_z, tex))
            brushes.append(box(x1, yc + open_hw, floor_z, x2, yc + ext, ceil_z, tex))
        brushes.append(
            box(x1, yc - open_hw, ceil_z - lintel_h, x2, yc + open_hw, ceil_z, tex)
        )
    if base_ramp is not None:
        # Build the base and optional cap as ramps spanning the opening width.
        zt1, zt2 = base_ramp
        brushes.append(
            ramp_slab(
                x1, x2, yc - open_hw, yc + open_hw, floor_z, floor_z, zt1, zt2, tex
            )
        )
        if base_cap_h > 0:
            cap_tex, cx1, cx2, crin = (
                base_cap_tex or tex,
                x1 - base_cap_ovh,
                x2 + base_cap_ovh,
                open_hw + base_cap_ovh,
            )
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
        base_y1 = base_cap_y1 if base_cap_y1 is not None else yc - open_hw
        base_y2 = base_cap_y2 if base_cap_y2 is not None else yc + open_hw
        brushes.append(box(x1, base_y1, floor_z, x2, base_y2, floor_z + base_h, tex))
        if base_cap_h > 0:
            cap_tex, cx1, cx2, crin = (
                base_cap_tex or tex,
                x1 - base_cap_ovh,
                x2 + base_cap_ovh,
                open_hw + base_cap_ovh,
            )
            cy1 = base_cap_y1 if base_cap_y1 is not None else yc - crin
            cy2 = base_cap_y2 if base_cap_y2 is not None else yc + crin
            brushes.append(
                box(
                    cx1,
                    cy1,
                    floor_z + base_h,
                    cx2,
                    cy2,
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
    recess=None,
):
    """Return an arched wall opening centered on ``yc`` and extruded along X.

    The opening uses inner/outer radii ``rin``/``rout`` in the YZ plane, with
    optional stilts, base trim, overhang, and recesses. Raises ``ValueError``
    for non-positive ``segs``, reversed X bounds, or textured-recess misuse.
    """
    stilt_h = rin if stilt_h is None else stilt_h
    if segs <= 0:
        raise ValueError(f"arch_wall: segs must be > 0, got {segs}")
    if x1 >= x2:
        raise ValueError(
            f"arch_wall: requires x1 < x2, got x1={x1}, x2={x2}; reversed "
            "bounds would silently invert the arch segments"
        )
    sprz, seg = floor_z + stilt_h, 180.0 / segs
    brushes, pillar_top = [], sprz if freestanding else ceil_z
    if not freestanding:
        if y1 < yc - (rout + overhang):
            brushes.append(
                box(x1, y1, floor_z, x2, yc - (rout + overhang), ceil_z, tex)
            )
        if y2 > yc + (rout + overhang):
            brushes.append(
                box(x1, yc + (rout + overhang), floor_z, x2, y2, ceil_z, tex)
            )
    recess_margin, recess_depth, recess_tex = recess if recess else (0, 0, None)
    if recess is not None and recess_depth > 0 and recess_tex is None:
        raise ValueError(
            "arch_wall: recess requires a texture (got recess=(..., ..., None))"
        )
    rx1, rx2 = x1 + recess_margin, x2 - recess_margin
    has_recess = recess is not None and recess_depth > 0 and rx2 > rx1
    if has_recess:
        south_ya, south_yb = yc - (rout + overhang), yc - rin
        brushes += [
            box(x1, south_ya, floor_z, rx1, south_yb, pillar_top, tex),
            box(rx2, south_ya, floor_z, x2, south_yb, pillar_top, tex),
            box(rx1, south_ya, sprz, rx2, south_yb, pillar_top, tex),
            box(rx1, south_ya, floor_z, rx2, south_yb - recess_depth, sprz, tex),
            box(rx1, south_yb - recess_depth, floor_z, rx2, south_yb, sprz, recess_tex),
        ]
        north_ya, north_yb = yc + rin, yc + (rout + overhang)
        brushes += [
            box(x1, north_ya, floor_z, rx1, north_yb, pillar_top, tex),
            box(rx2, north_ya, floor_z, x2, north_yb, pillar_top, tex),
            box(rx1, north_ya, sprz, rx2, north_yb, pillar_top, tex),
            box(rx1, north_ya + recess_depth, floor_z, rx2, north_yb, sprz, tex),
            box(rx1, north_ya, floor_z, rx2, north_ya + recess_depth, sprz, recess_tex),
        ]
    else:
        brushes += [
            box(x1, yc - (rout + overhang), floor_z, x2, yc - rin, pillar_top, tex),
            box(x1, yc + rin, floor_z, x2, yc + (rout + overhang), pillar_top, tex),
        ]
    if not freestanding:
        brushes.append(box(x1, yc - rin, sprz + rin, x2, yc + rin, ceil_z, tex))
    if base_ramp is not None:
        zt1, zt2 = base_ramp
        brushes.append(
            ramp_slab(x1, x2, yc - rin, yc + rin, floor_z, floor_z, zt1, zt2, tex)
        )
        if base_cap_h > 0:
            cap_tex, cx1, cx2, crin = (
                base_cap_tex or tex,
                x1 - base_cap_ovh,
                x2 + base_cap_ovh,
                rin + base_cap_ovh,
            )
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
            cap_tex, cx1, cx2, crin = (
                base_cap_tex or tex,
                x1 - base_cap_ovh,
                x2 + base_cap_ovh,
                rin + base_cap_ovh,
            )
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
    if not freestanding and rout < rin * math.sqrt(2):
        h_side = math.sqrt(max(0, rout**2 - rin**2))
        brushes += [
            box(x1, yc - rin, sprz + h_side, x2, yc - h_side, sprz + rin, tex),
            box(x1, yc + h_side, sprz + h_side, x2, yc + rin, sprz + rin, tex),
        ]
    for i in range(segs):
        a1, a2 = i * seg, (i + 1) * seg
        if has_recess:
            brushes += [
                arch_seg(x1, rx1, yc, float(sprz), rin, rout, a1, a2, tex),
                arch_seg(rx2, x2, yc, float(sprz), rin, rout, a1, a2, tex),
                arch_seg_chord(
                    rx1, rx2, yc, float(sprz), rin + recess_depth, rout, a1, a2, tex
                ),
                arch_seg_chord(
                    rx1,
                    rx2,
                    yc,
                    float(sprz),
                    rin,
                    rin + recess_depth,
                    a1,
                    a2,
                    recess_tex,
                ),
            ]
        else:
            brushes.append(arch_seg(x1, x2, yc, float(sprz), rin, rout, a1, a2, tex))
    return brushes


def arch_wall_y(y1, y2, floor_z, rin, rout, segs, tex, stilt_h=None, xc=0.0):
    """Return ``arch_wall()``'s freestanding Y-extruded variant centered on ``xc``.

    Raises ``ValueError`` if ``segs <= 0`` or ``y1 >= y2``.
    """
    if segs <= 0:
        raise ValueError(f"arch_wall_y: segs must be > 0, got {segs}")
    if y1 >= y2:
        raise ValueError(
            f"arch_wall_y: requires y1 < y2, got y1={y1}, y2={y2}; "
            "reversed bounds would silently invert the arch segments"
        )
    stilt_h = rin if stilt_h is None else stilt_h
    sprz, seg = floor_z + stilt_h, 180.0 / segs
    brushes = [
        box(xc - rout, y1, floor_z, xc - rin, y2, sprz, tex),
        box(xc + rin, y1, floor_z, xc + rout, y2, sprz, tex),
    ]
    for i in range(segs):
        brushes.append(
            arch_seg_y(y1, y2, xc, float(sprz), rin, rout, i * seg, (i + 1) * seg, tex)
        )
    return brushes


def gable_slats(
    bx1, bx2, apex_x, eave_z, ridge_z, slab_t, yface, depth, tex, n=24, gap=2, min_w=6
):
    """Return stacked gable slats spanning from eave to ridge.

    The slats extrude from ``yface`` by ``depth`` and taper with the gable
    edges toward ``apex_x``. Raises ``ValueError`` for invalid counts, a flat
    roof profile, or gaps that collapse a slat band.
    """
    if n <= 0:
        raise ValueError(f"gable_slats: n must be > 0, got {n}")
    y0, y1 = sorted((yface, yface + depth))
    denom = ridge_z - (eave_z + slab_t)
    if denom == 0:
        raise ValueError(
            f"gable_slats: ridge_z ({ridge_z}) must differ from eave_z + slab_t ({eave_z + slab_t})"
        )

    def edge_x(z):
        """Return the left/right gable edge X positions at height ``z``."""
        t = z - (eave_z + slab_t)
        if t <= 0:
            return bx1, bx2
        return bx1 + t * (apex_x - bx1) / denom, bx2 - t * (bx2 - apex_x) / denom

    band, brushes = (ridge_z - eave_z) / n, []
    if gap >= band:
        raise ValueError(
            f"gable_slats: gap ({gap}) must be less than the per-slat band "
            f"({band}), or every slat collapses to zero/negative height"
        )
    for i in range(n):
        z0, z1 = eave_z + i * band, eave_z + (i + 1) * band - gap
        xl0, xr0 = edge_x(z0)
        xl1, xr1 = edge_x(z1)
        if xr1 - xl1 < min_w:
            continue
        brushes.append(
            Brush(
                [
                    Face((xl0, y0, z0), (xl0, y1, z0), (xl1, y0, z1), tex),
                    Face((xr0, y0, z0), (xr1, y0, z1), (xr0, y1, z0), tex),
                    Face((xl0, y0, z0), (xl1, y0, z1), (xr0, y0, z0), tex),
                    Face((xl0, y1, z0), (xr0, y1, z0), (xl1, y1, z1), tex),
                    Face((xl0, y0, z0), (xr0, y0, z0), (xl0, y1, z0), tex),
                    Face((xl1, y0, z1), (xl1, y1, z1), (xr1, y0, z1), tex),
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
    """Return a framed entrance with a peaked slab arch on an X-facing wall.

    ``face_y`` locates the wall plane and ``out_sign`` chooses whether the
    depth projects toward +Y or -Y.
    """
    ya, yb = sorted((face_y, face_y + out_sign * pillar_d))
    lx1, lx2, rx1, rx2 = (
        cx - ent_hw - pillar_w,
        cx - ent_hw,
        cx + ent_hw,
        cx + ent_hw + pillar_w,
    )
    pz2 = base_z + ent_h + lintel_h
    eave_z, ridge_z = pz2, pz2 + arch_h
    brushes = [
        box(lx1, ya, base_z, lx2, yb, pz2, tex),
        box(rx1, ya, base_z, rx2, yb, pz2, tex),
        box(lx1, ya, base_z + ent_h, rx2, yb, pz2, tex),
        ramp_slab(lx1, cx, ya, yb, eave_z, eave_z, eave_z + arch_t, ridge_z, tex),
        ramp_slab(cx, rx2, ya, yb, eave_z, eave_z, ridge_z, eave_z + arch_t, tex),
    ]
    overhang, slat_h, side_ov = 3, 5, 2
    ya_cap, yb_cap = (
        (ya - overhang if out_sign < 0 else ya),
        (yb + overhang if out_sign > 0 else yb),
    )
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
        ),
        box(
            lx1 - side_ov,
            ya_cap,
            eave_z - beam_gap - beam_h,
            rx2 + side_ov,
            yb_cap,
            eave_z - beam_gap,
            tex,
        ),
    ]
    half_span = ent_hw + pillar_w
    slat_drop = side_ov * (arch_h - arch_t) // half_span
    zb_ext, zt_ext = eave_z + arch_t - slat_drop, eave_z + arch_t - slat_drop + slat_h
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
        ),
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
        ),
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
    """Axis-swapped ``entrance_arch_xwall``: same geometry, X and Y swapped."""
    return [
        swap_xy(b)
        for b in entrance_arch_xwall(
            cy,
            base_z,
            ent_hw,
            ent_h,
            face_x,
            out_sign,
            tex,
            pillar_w=pillar_w,
            pillar_d=pillar_d,
            lintel_h=lintel_h,
            arch_h=arch_h,
            arch_t=arch_t,
        )
    ]


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
    inner_recess=1,
    _fname="win_frame_xwall",
):
    """Return a muntin-style window frame extruded off a wall at ``face_y``.

    ``out_sign`` selects the extrusion direction; ``fw``/``fd`` control the
    outer frame width and depth, and inner muntins are inset by
    ``inner_recess``. Raises ``ValueError`` if the requested inner recess
    leaves no positive muntin depth.
    """
    if ifw is None:
        ifw = max(fw - 1, 2)
    if fd <= 2 * inner_recess:
        raise ValueError(
            f"{_fname}: fd ({fd}) must be greater than "
            f"2 * inner_recess ({2 * inner_recess}), or the inner muntin "
            "depth collapses to zero or negative"
        )
    ya, yb = sorted((face_y, face_y + out_sign * fd))
    jya, jyb = sorted(
        (face_y + out_sign * inner_recess, face_y + out_sign * (fd - inner_recess))
    )
    ix1, ix2, iz1, iz2 = xl + margin, xr - margin, zb + margin, zt - margin
    bars = [box(ix1, ya, iz2 - fw, ix2, yb, iz2, tex)]
    if bottom:
        bars.append(box(ix1, ya, iz1, ix2, yb, iz1 + fw, tex))
    bars += [
        box(ix1, ya, iz1, ix1 + fw, yb, iz2, tex),
        box(ix2 - fw, ya, iz1, ix2, yb, iz2, tex),
    ]
    jx1, jx2, jz1, jz2 = (
        ix1 + fw + inner_gap,
        ix2 - fw - inner_gap,
        (iz1 + fw + inner_gap if bottom else iz1),
        iz2 - fw - inner_gap,
    )
    if jx2 - jx1 > 2 * ifw and jz2 - jz1 > 2 * ifw:
        bars += [
            box(jx1, jya, jz2 - ifw, jx2, jyb, jz2, tex),
            box(jx1, jya, jz1, jx1 + ifw, jyb, jz2, tex),
            box(jx2 - ifw, jya, jz1, jx2, jyb, jz2, tex),
        ]
        if bottom:
            bars.append(box(jx1, jya, jz1, jx2, jyb, jz1 + ifw, tex))
        if crossbar:
            cb, zc, cr = max(ifw // 2, 2), (jz1 + jz2) // 2, fd // 2 - ifw // 2
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
    inner_recess=1,
):
    """Axis-swapped ``win_frame_xwall``: same geometry, X and Y swapped."""
    return [
        swap_xy(b)
        for b in win_frame_xwall(
            yl,
            yr,
            zb,
            zt,
            face_x,
            out_sign,
            tex,
            fw=fw,
            fd=fd,
            margin=margin,
            crossbar=crossbar,
            bottom=bottom,
            inner_gap=inner_gap,
            ifw=ifw,
            inner_recess=inner_recess,
            _fname="win_frame_ywall",
        )
    ]


def arch_fill(x1, x2, yc, floor_z, rin, segs, tex, stilt_h=None):
    """Return a solid arched fill, not a ring, centered on ``yc``.

    It builds a rectangular stilt up to the spring line and then ``segs``
    filled pie-slice arch segments. Raises ``ValueError`` if ``segs <= 0`` or
    the X bounds are reversed or degenerate.
    """
    if segs <= 0:
        raise ValueError(f"arch_fill: segs must be > 0, got {segs}")
    if x1 >= x2:
        raise ValueError(
            f"arch_fill: requires x1 < x2, got x1={x1}, x2={x2}; reversed "
            "bounds would silently invert the arch segments"
        )
    stilt_h = rin if stilt_h is None else stilt_h
    sprz, seg, brushes = floor_z + stilt_h, 180.0 / segs, []
    brushes.append(box(x1, yc - rin, floor_z, x2, yc + rin, sprz, tex))
    for i in range(segs):
        brushes.append(
            arch_pie_seg(x1, x2, yc, float(sprz), rin, i * seg, (i + 1) * seg, tex)
        )
    return brushes


def arch_fill_y(y1, y2, xc, floor_z, rin, segs, tex, stilt_h=None):
    """Return ``arch_fill()`` with X and Y swapped."""
    return [
        swap_xy(b)
        for b in arch_fill(y1, y2, xc, floor_z, rin, segs, tex, stilt_h=stilt_h)
    ]


def layered_wall(x1, y1, z1, x2, y2, z2, openings, tex, ts=None, tn=None, tf=None):
    """Return a wall slab subdivided around rectangular XZ openings.

    ``openings`` are clamped to the wall bounds before subdivision. ``tf``
    retextures faces exposed to an opening, while ``ts``/``tn`` override the
    south and north exterior faces.
    """
    # Clamp each opening to the wall bounds before subdividing the slab.
    wx1, wx2 = min(x1, x2), max(x1, x2)
    wz1, wz2 = min(z1, z2), max(z1, z2)
    clamped = []
    for o in openings:
        ox1, ox2 = sorted((o[0], o[2]))
        oz1, oz2 = sorted((o[1], o[3]))
        ox1, ox2 = max(ox1, wx1), min(ox2, wx2)
        oz1, oz2 = max(oz1, wz1), min(oz2, wz2)
        if ox1 < ox2 and oz1 < oz2:
            clamped.append((ox1, oz1, ox2, oz2))
    openings = clamped
    xs = sorted({x1, x2} | {o[0] for o in openings} | {o[2] for o in openings})
    zs = sorted({z1, z2} | {o[1] for o in openings} | {o[3] for o in openings})
    brushes = []
    for x_i in range(len(xs) - 1):
        for z_i in range(len(zs) - 1):
            cx1, cx2, cz1, cz2 = xs[x_i], xs[x_i + 1], zs[z_i], zs[z_i + 1]
            if not any(
                o[0] <= cx1 and cx2 <= o[2] and o[1] <= cz1 and cz2 <= o[3]
                for o in openings
            ):
                kw = {}
                if tf:
                    for o in openings:
                        if cx2 == o[0] and cz1 < o[3] and cz2 > o[1]:
                            kw["te"] = tf
                        if cx1 == o[2] and cz1 < o[3] and cz2 > o[1]:
                            kw["tw"] = tf
                        if cz1 == o[3] and cx1 < o[2] and cx2 > o[0]:
                            kw["tb"] = tf
                        if cz2 == o[1] and cx1 < o[2] and cx2 > o[0]:
                            kw["tt"] = tf
                brushes.append(box(cx1, y1, cz1, cx2, y2, cz2, tex, ts=ts, tn=tn, **kw))
    return brushes


def layered_wall_y(y1, x1, z1, y2, x2, z2, openings, tex, tw=None, te=None):
    """Return ``layered_wall()`` with X and Y swapped."""
    return [
        swap_xy(b)
        for b in layered_wall(y1, x1, z1, y2, x2, z2, openings, tex, ts=tw, tn=te)
    ]
