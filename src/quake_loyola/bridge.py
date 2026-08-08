"""Build the pedestrian bridge over Charles Street.

This module generates the bridge deck, parapets, piers, archwork,
abutment teleports, and fascia lettering between west campus and Knott Hall.
"""

from .constants.bridge import (
    BRIDGE_ABUTMENT_CEMENT_MAX_H,
    BRIDGE_ABUTMENT_CEMENT_RIN,
    BRIDGE_ABUTMENT_CEMENT_X1_OFFSET,
    BRIDGE_ABUTMENT_CEMENT_X2_OFFSET,
    BRIDGE_ABUTMENT_RAMP_CAP_H,
    BRIDGE_ABUTMENT_RAMP_HIGH_H,
    BRIDGE_ABUTMENT_RAMP_LOW_H,
    BRIDGE_BANNER_CORNER_INSET,
    BRIDGE_BANNER_GAP,
    BRIDGE_BANNER_H,
    BRIDGE_BANNER_MAST_PROUD,
    BRIDGE_BANNER_MAST_T,
    BRIDGE_BANNER_T,
    BRIDGE_BANNER_TOP_Z,
    BRIDGE_BANNER_W,
    BRIDGE_BASE_LIGHT_BRIGHTNESS,
    BRIDGE_BASE_LIGHT_D,
    BRIDGE_BASE_LIGHT_H,
    BRIDGE_BASE_LIGHT_HW,
    BRIDGE_BASE_LIGHT_Z_LIFT,
    BRIDGE_BLK_H,
    BRIDGE_BLK_HW,
    BRIDGE_BLK_INSET,
    BRIDGE_BLK_OVH,
    BRIDGE_BLK_PIER_CLEARANCE,
    BRIDGE_CENTER_SPAN_OFFSET,
    BRIDGE_CENTER_SPAN_PIER_EMBED,
    BRIDGE_DECK_CROSS_STRIP_DROP,
    BRIDGE_DECK_CROSS_STRIP_H,
    BRIDGE_DECK_CROSS_STRIP_HW,
    BRIDGE_DECK_EDGE_CEMENT_W,
    BRIDGE_DZ1,
    BRIDGE_DZ2,
    BRIDGE_FASCIA_PX_H,
    BRIDGE_FASCIA_PX_W,
    BRIDGE_FASCIA_TEXT,
    BRIDGE_JOINT_CEMENT_W,
    BRIDGE_JOINT_GAP_HW,
    BRIDGE_JOINT_METAL_HW,
    BRIDGE_PIER_FILL_OFFSET,
    BRIDGE_PIER_LINING_MARGIN,
    BRIDGE_PIER_LINING_THICK,
    BRIDGE_PIER_PLATE_D,
    BRIDGE_PIER_PLATE_GAP,
    BRIDGE_PIER_PLATE_SIZE,
    BRIDGE_PILLAR_BASE_CAP_H,
    BRIDGE_PILLAR_BASE_CAP_OVH,
    BRIDGE_PILLAR_BASE_H,
    BRIDGE_PILLAR_BASE_RAMP_H,
    BRIDGE_PILLAR_CAP_H,
    BRIDGE_PILLAR_CAP_IN_OVH,
    BRIDGE_PILLAR_CAP_OUT_OVH,
    BRIDGE_PILLAR_EXTRA,
    BRIDGE_PILLAR_INNER_R,
    BRIDGE_PILLAR_OUTER_R,
    BRIDGE_PILLAR_OVERHANG,
    BRIDGE_PILLAR_PYR_H,
    BRIDGE_PILLAR_SEAM_D,
    BRIDGE_PILLAR_SEAM_HW,
    BRIDGE_SQ_D,
    BRIDGE_SQ_HH,
    BRIDGE_SQ_HW,
    BRIDGE_SQ_LINTEL_H,
    BRIDGE_SQ_LINTEL_STONE_H,
    BRIDGE_TELEPORT_ARCH_CLEARANCE,
    BRIDGE_TELEPORT_ARCH_X1_OFFSET,
    BRIDGE_TELEPORT_ARCH_X2_OFFSET,
    BRIDGE_TELEPORT_DEST_Z,
    BRIDGE_TORCH_CUP_H,
    BRIDGE_TORCH_CUP_HW,
    BRIDGE_TORCH_POST_H,
    BRIDGE_TORCH_POST_HW,
    BRIDGE_TUBE_GAP,
    BRIDGE_TUBE_HW,
    BRIDGE_TUBE_RISE,
    PIER6_ROTATION_DEG,
    PIER6_ROTATION_MARGIN,
)
from .constants.derived import (
    BRIDGE,
    BRIDGE_ARCH_X,
    BRIDGE_PAR_W,
    BRIDGE_PIER_GROUND_Z,
    BRIDGE_PILLAR_HW,
    BRIDGE_PILLAR_PYR_W,
    BRIDGE_SEG_W,
    KNOTT_ENT_WALK_X1,
    PIER2_X,
    PIER3_X,
    PIER4_X,
    PIER5_X,
    PIER6_X,
    WORLD_X1,
    WORLD_X2_EXT,
    deck_bot_z,
    deck_top_z,
    pier6_east_face_x_at_y,
    pier6_west_face_x_at_y,
)
from .constants.flags import (
    BRIDGE_ENABLED_FASCIA_TEXT,
    BRIDGE_ENABLED_SPAN_CENTER,
    BRIDGE_ENABLED_SPAN_EAST_APPROACH,
    BRIDGE_ENABLED_SPAN_EAST_EXT,
    BRIDGE_ENABLED_SPAN_KH,
    BRIDGE_ENABLED_SPAN_WEST_APPROACH,
    BRIDGE_ENABLED_SUPPORTS,
    ENTITIES_ENABLED_TELEPORTS,
)
from .constants.fonts import FASCIA_FONT
from .constants.textures import Textures
from .constants.world import (
    A_SEGS,
    FLOOR_Z2,
)
from .geometry import (
    arch_fill,
    arch_plate_ring,
    arch_wall,
    box,
    brush_ent,
    east_y_shift,
    ent,
    pyramid,
    ramp_slab,
    square_wall,
    taper_box_x,
    tile_face_plates,
    torch_flame_only,
)


def _section_x_ranges():
    """Return the pier-to-pier X span for each bridge section."""
    return {
        "west_approach": (BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1]),
        "center_span": (BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]),
        "east_approach": (BRIDGE_ARCH_X[2], BRIDGE_ARCH_X[3]),
        "kh_span": (BRIDGE_ARCH_X[3], BRIDGE_ARCH_X[4]),
        "east_ext": (BRIDGE_ARCH_X[4], BRIDGE_ARCH_X[5]),
    }


_SECTION_ORDER = [
    "west_approach",
    "center_span",
    "east_approach",
    "kh_span",
    "east_ext",
]


def _boundary_owner(left_name, right_name, enabled_names):
    """Return which adjacent section owns a shared boundary pier.

    center_span takes priority; other boundaries prefer the section nearer
    center_span, with a fallback to whichever candidate is enabled.
    """
    if right_name == "center_span":
        preferred, fallback = right_name, left_name
    elif left_name == "center_span":
        preferred, fallback = left_name, right_name
    else:
        preferred, fallback = left_name, right_name
    return preferred if preferred in enabled_names else fallback


def _section_accept_ranges(enabled_names, margin):
    """Return per-section X acceptance windows for the enabled bridge sections.

    Each boundary pier belongs to exactly one enabled section, so the windows
    partition the bridge without duplicating or dropping pier geometry.
    """
    section_piers = _section_x_ranges()
    ranges = {}
    for idx, name in enumerate(_SECTION_ORDER):
        px1, px2 = section_piers[name]
        if idx == 0:
            # Extend all the way to the world edge so the west
            # abutment/teleport geometry (built out at WORLD_X1, far beyond
            # the first pier's pillar-overhang margin) isn't dropped when
            # section filtering is active.
            ax1 = WORLD_X1
        else:
            owner = _boundary_owner(_SECTION_ORDER[idx - 1], name, enabled_names)
            ax1 = px1 - margin if owner == name else px1
        if idx == len(_SECTION_ORDER) - 1:
            # Symmetric with the west edge above: reach WORLD_X2_EXT so the
            # east abutment/teleport geometry isn't dropped either.
            ax2 = WORLD_X2_EXT
        else:
            owner = _boundary_owner(name, _SECTION_ORDER[idx + 1], enabled_names)
            ax2 = px2 + margin if owner == name else px2
        ranges[name] = (ax1, ax2)
    return ranges


def _pier_survives_section_filter(pier_x, enabled_names):
    """True if the pier at ``pier_x`` is kept by ``_filter_sections``.

    Geometry appended *after* filtering (the pier banners) has to make the
    same ownership decision itself, or it ends up hanging in mid-air over a
    pier that was filtered out.
    """
    margin = BRIDGE_PILLAR_HW + BRIDGE_PILLAR_OVERHANG + PIER6_ROTATION_MARGIN
    accept_ranges = _section_accept_ranges(enabled_names, margin)
    return any(
        ax1 <= pier_x <= ax2
        for name, (ax1, ax2) in accept_ranges.items()
        if name in enabled_names
    )


def _filter_sections(brushes, entities, enabled_names, extract_names=None):
    """Return only the geometry assigned to the selected bridge sections.

    `enabled_names` defines shared-pier ownership for the full enabled set.
    `extract_names`, when provided, limits the returned subset while keeping
    that ownership unchanged.
    """
    if extract_names is None:
        extract_names = enabled_names
    margin = BRIDGE_PILLAR_HW + BRIDGE_PILLAR_OVERHANG + PIER6_ROTATION_MARGIN
    accept_ranges = _section_accept_ranges(enabled_names, margin)
    enabled_spans = [accept_ranges[name] for name in extract_names]

    def _in_any_span(b):
        xs = [p[0] for f in b.faces for p in (f.p1, f.p2, f.p3)]
        bx1, bx2 = min(xs), max(xs)
        return any(bx1 >= sx1 and bx2 <= sx2 for sx1, sx2 in enabled_spans)

    def _is_hint(b):
        return all(f.tex == Textures.HINT for f in b.faces)

    filtered_brushes = [b for b in brushes if _in_any_span(b) and not _is_hint(b)]
    new_entities = []
    for entdict in entities:
        if entdict.brushes:
            kept = [b for b in entdict.brushes if _in_any_span(b)]
            if kept:
                new_entities.append(
                    brush_ent(entdict.classname, kept, **entdict.fields)
                )
        else:
            origin = entdict.fields.get("origin")
            if origin is not None:
                ox = float(origin.split()[0])
                if not any(sx1 <= ox <= sx2 for sx1, sx2 in enabled_spans):
                    continue
            new_entities.append(entdict)
    return filtered_brushes, new_entities


def _parapet_block_centers(
    x_start, x_end, n, bridge_blk_pir_m, west_margin=None, east_margin=None
):
    """Return parapet-block centers using add_parapet_blocks() spacing."""
    mx0 = west_margin if west_margin is not None else bridge_blk_pir_m
    mx1 = east_margin if east_margin is not None else bridge_blk_pir_m
    x0 = x_start + mx0
    x1_lim = x_end - mx1
    return [x0 + (x1_lim - x0) * (k + 1) / (n + 1) for k in range(n)]


def _pier6_west_pieces(
    x_start,
    ys1,
    ys2,
    z1,
    z2,
    tex,
    pier6_old_cutoff_x,
    tt=None,
    tb=None,
    far=True,
    margin=0,
    margin2=None,
    tt_params="0 0 0 1 1",
):
    """Return a box-plus-wedge run from x_start to Pier 6 across one Y band."""
    if margin2 is None:
        margin2 = margin
    pieces = [
        box(
            x_start,
            ys1,
            z1,
            pier6_old_cutoff_x,
            ys2,
            z2,
            tex,
            tt=tt,
            tb=tb,
            tt_params=tt_params,
        )
    ]
    face_x_at_y = pier6_east_face_x_at_y if far else pier6_west_face_x_at_y
    t1 = face_x_at_y(ys1) - margin
    t2 = face_x_at_y(ys2) - margin2
    pieces.append(
        taper_box_x(
            ys1,
            pier6_old_cutoff_x,
            t1,
            z1,
            ys2,
            pier6_old_cutoff_x,
            t2,
            z2,
            tex,
            tt=tt,
            tb=tb,
            tt_params=tt_params,
        )
    )
    return pieces


def _wall_tilt_z(span_boundaries, cx, half_width):
    """Return the left and right top Z values using the local segment's slope."""
    cx_clamped = min(max(cx, span_boundaries[0]), span_boundaries[-1])
    for sx1, sx2 in zip(span_boundaries, span_boundaries[1:], strict=False):
        if sx1 <= cx_clamped <= sx2:
            z1, z2 = deck_top_z(sx1), deck_top_z(sx2)
            slope = (z2 - z1) / (sx2 - sx1) if sx2 != sx1 else 0.0
            t = (cx_clamped - sx1) / (sx2 - sx1) if sx2 != sx1 else 0.0
            zc = z1 + (z2 - z1) * t
            return zc - slope * half_width, zc + slope * half_width
    zc = deck_top_z(cx_clamped)
    return zc, zc


def _iter_bridge_span_segments(span_boundaries):
    """Yield the deck and parapet Z spans for each bridge X segment."""
    for sx1, sx2 in zip(span_boundaries, span_boundaries[1:], strict=False):
        db1, db2 = deck_bot_z(sx1), deck_bot_z(sx2)
        pb1, pb2 = deck_top_z(sx1), deck_top_z(sx2)
        pt1, pt2 = pb1 + BRIDGE.parapet_h, pb2 + BRIDGE.parapet_h
        yield sx1, sx2, db1, db2, pb1, pb2, pt1, pt2


def _build_bridge_deck_slabs(
    brushes,
    entities,
    deck_bands,
    cross_strip_x,
    pier6_old_cutoff_x,
    span_boundaries,
    deck_band_y,
):
    """Build the bridge deck slabs, cross strips, and approach extension."""
    dw_y1b, dw_y2b = deck_band_y
    for ys1, ys2, tt, tb, far, margin, margin2, tt_params in deck_bands:
        brushes.append(
            box(
                BRIDGE.x2,
                ys1,
                BRIDGE_DZ1,
                PIER5_X,
                ys2,
                BRIDGE_DZ2,
                Textures.STONE,
                tt=tt,
                tb=tb,
                tt_params=tt_params,
            )
        )
        brushes.extend(
            _pier6_west_pieces(
                PIER5_X,
                ys1,
                ys2,
                BRIDGE_DZ1,
                BRIDGE_DZ2,
                Textures.STONE,
                pier6_old_cutoff_x,
                tt=tt,
                tb=tb,
                far=far,
                margin=margin,
                margin2=margin2,
                tt_params=tt_params,
            )
        )

    bridge_south_extension = 184
    brushes.append(
        box(
            BRIDGE.x2,
            BRIDGE.y1 - bridge_south_extension,
            BRIDGE_DZ1,
            PIER5_X,
            BRIDGE.y1,
            BRIDGE_DZ2,
            Textures.CEMENT,
        )
    )

    for sx1, sx2, db1, db2, pb1, pb2, _, _ in _iter_bridge_span_segments(
        span_boundaries
    ):
        for ys1, ys2, tt, tb, _far, _margin, _margin2, tt_params in deck_bands:
            brushes.append(
                ramp_slab(
                    sx1,
                    sx2,
                    ys1,
                    ys2,
                    db1,
                    db2,
                    pb1,
                    pb2,
                    Textures.STONE,
                    tt=tt,
                    tb=tb,
                    tt_params=tt_params,
                )
            )

    cross_strip_brushes = []
    for cx in cross_strip_x:
        strip_x1 = cx - BRIDGE_DECK_CROSS_STRIP_HW
        strip_x2 = cx + BRIDGE_DECK_CROSS_STRIP_HW
        strip_zt1 = deck_bot_z(strip_x1) + BRIDGE_DECK_CROSS_STRIP_DROP
        strip_zt2 = deck_bot_z(strip_x2) + BRIDGE_DECK_CROSS_STRIP_DROP
        cross_strip_brushes.append(
            ramp_slab(
                strip_x1,
                strip_x2,
                dw_y1b,
                dw_y2b,
                strip_zt1 - BRIDGE_DECK_CROSS_STRIP_H,
                strip_zt2 - BRIDGE_DECK_CROSS_STRIP_H,
                strip_zt1,
                strip_zt2,
                Textures.GABLE,
                tb_params="0 0 90 1 1",
            )
        )
    entities.append(brush_ent("func_illusionary", cross_strip_brushes))


def _build_bridge_expansion_joints(
    entities,
    deck_band_y,
):
    """Build the expansion-joint bands that cross the deck at each pier."""
    dw_y1c, dw_y2c = deck_band_y
    joint_brushes = []
    for px in BRIDGE_ARCH_X:
        rotated = px == PIER6_X
        if rotated:
            # Pier 6 is rotated about its own axis, so its joint has to lean
            # over to stay parallel to the pier. Shearing rather than rotating
            # keeps the band's ends square against the deck edges instead of
            # letting one end ride over the parapet and the other fall short.
            shear_cy = east_y_shift(px)
        m1, m2 = px - BRIDGE_JOINT_METAL_HW, px + BRIDGE_JOINT_METAL_HW
        g1, g2 = px - BRIDGE_JOINT_GAP_HW, px + BRIDGE_JOINT_GAP_HW
        c1w, c2w = m1 - BRIDGE_JOINT_CEMENT_W, m1
        c1e, c2e = m2, m2 + BRIDGE_JOINT_CEMENT_W
        t1w, t2w = c1w - BRIDGE_JOINT_CEMENT_W, c1w
        t1e, t2e = c2e, c2e + BRIDGE_JOINT_CEMENT_W
        joint_xs = [t1w, t2w, c1w, c2w, m1, g1, g2, m2, c1e, c2e, t1e, t2e]
        joint_zts = {x: deck_top_z(x) + BRIDGE_DECK_CROSS_STRIP_DROP for x in joint_xs}
        for x1, x2, tex, tb_params in (
            (t1w, t2w, Textures.DECK_EDGE, "0 0 0 1 1"),
            (c1w, c2w, Textures.CEMENT, "0 0 0 1 1"),
            (m1, g1, Textures.JOINT_METAL, "0 0 90 1 1"),
            (g1, g2, Textures.JOINT_GAP, "0 0 90 1 1"),
            (g2, m2, Textures.JOINT_METAL, "0 0 90 1 1"),
            (c1e, c2e, Textures.CEMENT, "0 0 0 1 1"),
            (t1e, t2e, Textures.DECK_EDGE, "0 0 0 1 1"),
        ):
            joint = ramp_slab(
                x1,
                x2,
                dw_y1c,
                dw_y2c,
                joint_zts[x1] - BRIDGE_DECK_CROSS_STRIP_H,
                joint_zts[x2] - BRIDGE_DECK_CROSS_STRIP_H,
                joint_zts[x1],
                joint_zts[x2],
                tex,
                tb_params=tb_params,
            )
            if rotated:
                joint = joint.sheared_x_by_y(-PIER6_ROTATION_DEG, shear_cy)
            joint_brushes.append(joint)
    entities.append(brush_ent("func_illusionary", joint_brushes))


def _build_bridge_parapet_shells(
    brushes,
    pier6_old_cutoff_x,
    span_boundaries,
    span4_west_mid,
):
    """Build the continuous parapet walls along the deck edges.

    The south parapet stops at ``span4_west_mid`` rather than running the full
    length: that, together with the ``n_south=0`` passed for the spans beside
    Knott Hall, is what opens the south side up for the Knott connector walk.
    (Three ``KNOTT_ENT_WALK_X1/X2`` skip guards used to sit in the per-segment
    loops here and in the tube builder as well, but every span boundary those
    loops iterate ends at ``BRIDGE.x2``, well west of the walk, so they never
    fired; removing them left the generated map byte-identical.)
    """
    brushes.append(
        box(
            BRIDGE.x2,
            BRIDGE.y2 - BRIDGE_PAR_W,
            BRIDGE_DZ2,
            PIER5_X,
            BRIDGE.y2,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    brushes.extend(
        _pier6_west_pieces(
            PIER5_X,
            BRIDGE.y2 - BRIDGE_PAR_W,
            BRIDGE.y2,
            BRIDGE_DZ2,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
            pier6_old_cutoff_x,
            far=False,
            margin=0,
            margin2=8,
        )
    )
    brushes.append(
        box(
            BRIDGE.x2,
            BRIDGE.y1,
            BRIDGE_DZ2,
            span4_west_mid,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    brushes.extend(
        _pier6_west_pieces(
            PIER5_X,
            BRIDGE.y1,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
            pier6_old_cutoff_x,
        )
    )

    for sx1, sx2, _, _, pb1, pb2, pt1, pt2 in _iter_bridge_span_segments(
        span_boundaries
    ):
        brushes.append(
            ramp_slab(
                sx1,
                sx2,
                BRIDGE.y2 - BRIDGE_PAR_W,
                BRIDGE.y2,
                pb1,
                pb2,
                pt1,
                pt2,
                Textures.CEMENT,
            )
        )
        brushes.append(
            ramp_slab(
                sx1,
                sx2,
                BRIDGE.y1,
                BRIDGE.y1 + BRIDGE_PAR_W,
                pb1,
                pb2,
                pt1,
                pt2,
                Textures.CEMENT,
            )
        )


def _add_repeated_parapet_decorations(
    brushes,
    x_start,
    x_end,
    n,
    *,
    z_at_center,
    north_brush,
    south_brush,
    bridge_blk_pir_m,
    center_fn=lambda x: x,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
    y_shift_fn=None,
):
    """Place repeated north- and south-parapet decorations across a span."""
    n_s = n if n_south is None else n_south
    mx0 = west_margin if west_margin is not None else bridge_blk_pir_m
    mx1 = east_margin if east_margin is not None else bridge_blk_pir_m
    mx1_n = east_margin_n if east_margin_n is not None else mx1
    x0 = x_start + mx0
    x1_n = x_end - mx1_n
    x1_s = x_end - mx1

    def iter_positions(count, x_limit):
        for k in range(count):
            cx = center_fn(x0 + (x_limit - x0) * (k + 1) / (count + 1))
            sy = y_shift_fn(cx) if y_shift_fn else 0.0
            yield cx, sy, z_at_center(cx)

    for cx, sy, bz in iter_positions(n, x1_n):
        brush = north_brush(cx, sy, bz)
        if brush is not None:
            brushes.append(brush)
    for cx, sy, bz in iter_positions(n_s, x1_s):
        brush = south_brush(cx, sy, bz)
        if brush is not None:
            brushes.append(brush)


def _add_parapet_blocks(
    brushes,
    x_start,
    x_end,
    n,
    bridge_blk_pir_m,
    span_boundaries,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
    y_shift_fn=None,
):
    """Add evenly spaced parapet blocks across a bridge span."""

    def _block(cx, sy, y1_val, y2_val):
        """Return a parapet block aligned with the local deck slope."""
        zb1_raw, zb2_raw = _wall_tilt_z(span_boundaries, cx, BRIDGE_BLK_HW)
        if abs(zb2_raw - zb1_raw) < 1.0:
            zb1 = zb2 = round((zb1_raw + zb2_raw) / 2 + BRIDGE.parapet_h)
        else:
            zb1 = round(zb1_raw + BRIDGE.parapet_h)
            zb2 = round(zb2_raw + BRIDGE.parapet_h)
        y1v = y1_val + sy
        y2v = y2_val + sy
        if zb1 == zb2:
            return box(
                cx - BRIDGE_BLK_HW,
                y1v,
                zb1,
                cx + BRIDGE_BLK_HW,
                y2v,
                zb1 + BRIDGE_BLK_H,
                Textures.CEMENT,
            )
        return ramp_slab(
            cx - BRIDGE_BLK_HW,
            cx + BRIDGE_BLK_HW,
            y1v,
            y2v,
            zb1,
            zb2,
            zb1 + BRIDGE_BLK_H,
            zb2 + BRIDGE_BLK_H,
            Textures.CEMENT,
        )

    _add_repeated_parapet_decorations(
        brushes,
        x_start,
        x_end,
        n,
        z_at_center=lambda cx: (
            min(
                deck_top_z(cx - BRIDGE_BLK_HW),
                deck_top_z(cx),
                deck_top_z(cx + BRIDGE_BLK_HW),
            )
            + BRIDGE.parapet_h
        ),
        north_brush=lambda cx, sy, _bz: _block(
            cx,
            sy,
            BRIDGE.y2 - BRIDGE_PAR_W + BRIDGE_BLK_INSET,
            BRIDGE.y2 + BRIDGE_BLK_OVH - BRIDGE_BLK_INSET,
        ),
        south_brush=lambda cx, sy, _bz: _block(
            cx,
            sy,
            BRIDGE.y1 - BRIDGE_BLK_OVH + BRIDGE_BLK_INSET,
            BRIDGE.y1 + BRIDGE_PAR_W - BRIDGE_BLK_INSET,
        ),
        bridge_blk_pir_m=bridge_blk_pir_m,
        west_margin=west_margin,
        east_margin=east_margin,
        n_south=n_south,
        east_margin_n=east_margin_n,
        y_shift_fn=y_shift_fn,
    )


def _add_parapet_squares(
    brushes,
    x_start,
    x_end,
    n,
    bridge_blk_pir_m,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
    y_shift_fn=None,
):
    """Add raised parapet-face squares at the block positions."""
    _add_repeated_parapet_decorations(
        brushes,
        x_start,
        x_end,
        n,
        z_at_center=lambda cx: (
            int(
                min(
                    deck_top_z(cx - BRIDGE_SQ_HW),
                    deck_top_z(cx),
                    deck_top_z(cx + BRIDGE_SQ_HW),
                )
            )
            + BRIDGE.parapet_h
            + BRIDGE_BLK_H // 2
        ),
        north_brush=lambda cx, sy, bz: box(
            cx - BRIDGE_SQ_HW,
            BRIDGE.y2 + sy,
            bz - BRIDGE_SQ_HH,
            cx + BRIDGE_SQ_HW,
            BRIDGE.y2 + BRIDGE_SQ_D + sy,
            bz + BRIDGE_SQ_HH,
            Textures.RAIL,
        ),
        south_brush=lambda cx, sy, bz: box(
            cx - BRIDGE_SQ_HW,
            BRIDGE.y1 - BRIDGE_SQ_D + sy,
            bz - BRIDGE_SQ_HH,
            cx + BRIDGE_SQ_HW,
            BRIDGE.y1 + sy,
            bz + BRIDGE_SQ_HH,
            Textures.RAIL,
        ),
        bridge_blk_pir_m=bridge_blk_pir_m,
        center_fn=int,
        west_margin=west_margin,
        east_margin=east_margin,
        n_south=n_south,
        east_margin_n=east_margin_n,
        y_shift_fn=y_shift_fn,
    )


def _add_parapet_base_lights(
    brushes,
    entities,
    x_start,
    x_end,
    n,
    bridge_blk_pir_m,
    span_boundaries,
    west_margin=None,
    east_margin=None,
    n_south=None,
    east_margin_n=None,
    y_shift_fn=None,
):
    """Add parapet base lights at the decoration positions."""

    def _fixture(cx, sy, y_wall, y_dir):
        zb1_raw, zb2_raw = _wall_tilt_z(span_boundaries, cx, BRIDGE_BASE_LIGHT_HW)
        zb1 = round(zb1_raw) + BRIDGE_BASE_LIGHT_Z_LIFT
        zb2 = round(zb2_raw) + BRIDGE_BASE_LIGHT_Z_LIFT
        y1v = y_wall + sy
        y2v = y_wall + y_dir * BRIDGE_BASE_LIGHT_D + sy
        ylo, yhi = (y1v, y2v) if y1v <= y2v else (y2v, y1v)
        entities.append(
            ent(
                "light",
                origin=(
                    f"{cx} {(ylo + yhi) // 2} "
                    f"{int((zb1 + zb2) / 2) + BRIDGE_BASE_LIGHT_H // 2}"
                ),
                light=BRIDGE_BASE_LIGHT_BRIGHTNESS,
                _light_group="deck_wall",
            )
        )
        return None

    _add_repeated_parapet_decorations(
        brushes,
        x_start,
        x_end,
        n,
        z_at_center=lambda cx: int(deck_top_z(cx)),
        north_brush=lambda cx, sy, _bz: _fixture(cx, sy, BRIDGE.y2 - BRIDGE_PAR_W, -1),
        south_brush=lambda cx, sy, _bz: _fixture(cx, sy, BRIDGE.y1 + BRIDGE_PAR_W, +1),
        bridge_blk_pir_m=bridge_blk_pir_m,
        center_fn=int,
        west_margin=west_margin,
        east_margin=east_margin,
        n_south=n_south,
        east_margin_n=east_margin_n,
        y_shift_fn=y_shift_fn,
    )


def _build_bridge_parapet_light_spans(
    brushes, entities, bridge_blk_pir_m, span_boundaries, span_counts
):
    """Add parapet base lights across each bridge span."""

    span1_n, span3_n, kh_span_n = span_counts
    _add_parapet_base_lights(
        brushes,
        entities,
        BRIDGE_ARCH_X[0],
        BRIDGE_ARCH_X[1],
        span1_n,
        bridge_blk_pir_m,
        span_boundaries,
        west_margin=0,
        east_margin=0,
    )
    _add_parapet_base_lights(
        brushes,
        entities,
        BRIDGE_ARCH_X[1],
        BRIDGE_ARCH_X[2],
        4,
        bridge_blk_pir_m,
        span_boundaries,
    )
    _add_parapet_base_lights(
        brushes,
        entities,
        BRIDGE_ARCH_X[2],
        BRIDGE_ARCH_X[3],
        span3_n,
        bridge_blk_pir_m,
        span_boundaries,
        west_margin=0,
        east_margin=0,
    )
    _add_parapet_base_lights(
        brushes,
        entities,
        BRIDGE.x2,
        BRIDGE_ARCH_X[4],
        kh_span_n,
        bridge_blk_pir_m,
        span_boundaries,
        west_margin=0,
        east_margin=0,
        n_south=0,
        y_shift_fn=east_y_shift,
    )


def _build_bridge_parapet_square_brushes(brushes, bridge_blk_pir_m, span_counts):
    """Add parapet-face square details across each bridge span."""

    span1_n, span3_n, kh_span_n = span_counts
    _add_parapet_squares(
        brushes,
        BRIDGE_ARCH_X[0],
        BRIDGE_ARCH_X[1],
        span1_n,
        bridge_blk_pir_m,
        west_margin=0,
        east_margin=0,
    )
    _add_parapet_squares(
        brushes,
        BRIDGE_ARCH_X[1],
        BRIDGE_ARCH_X[2],
        4,
        bridge_blk_pir_m,
    )
    _add_parapet_squares(
        brushes,
        BRIDGE_ARCH_X[2],
        BRIDGE_ARCH_X[3],
        span3_n,
        bridge_blk_pir_m,
        west_margin=0,
        east_margin=0,
    )
    _add_parapet_squares(
        brushes,
        BRIDGE.x2,
        BRIDGE_ARCH_X[4],
        kh_span_n,
        bridge_blk_pir_m,
        west_margin=0,
        east_margin=0,
        n_south=0,
        y_shift_fn=east_y_shift,
    )


def _bridge_south_parapet_endcap_brush(span4_west_mid):
    """Return the terminal south parapet block before the Knott connector."""

    cx_wall_end = span4_west_mid - BRIDGE_BLK_HW
    return box(
        cx_wall_end - BRIDGE_BLK_HW,
        BRIDGE.y1 - BRIDGE_BLK_OVH + BRIDGE_BLK_INSET,
        BRIDGE_DZ2 + BRIDGE.parapet_h,
        cx_wall_end + BRIDGE_BLK_HW,
        BRIDGE.y1 + BRIDGE_PAR_W - BRIDGE_BLK_INSET,
        BRIDGE_DZ2 + BRIDGE.parapet_h + BRIDGE_BLK_H,
        Textures.CEMENT,
    )


def _bridge_railing_tube_y_bounds():
    """Return the north and south railing tube Y extents."""

    tube_ny1 = BRIDGE.y2 - BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
    tube_ny2 = tube_ny1 + BRIDGE_TUBE_HW * 2
    tube_sy1 = BRIDGE.y1 + BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
    tube_sy2 = tube_sy1 + BRIDGE_TUBE_HW * 2
    return tube_ny1, tube_ny2, tube_sy1, tube_sy2


def _add_bridge_span_tubes(
    brushes,
    span_boundaries,
    tube_ny1,
    tube_ny2,
    tube_sy1,
    tube_sy2,
    tube_z_offset,
):
    """Add sloped railing tube spans for one vertical offset."""

    for (
        span_x1,
        span_x2,
        _,
        _,
        _,
        _,
        tube_z1,
        tube_z2,
    ) in _iter_bridge_span_segments(span_boundaries):
        tube_z1 += tube_z_offset
        tube_z2 += tube_z_offset
        brushes.append(
            ramp_slab(
                span_x1,
                span_x2,
                tube_ny1,
                tube_ny2,
                tube_z1,
                tube_z2,
                tube_z1 + BRIDGE_TUBE_HW * 2,
                tube_z2 + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        brushes.append(
            ramp_slab(
                span_x1,
                span_x2,
                tube_sy1,
                tube_sy2,
                tube_z1,
                tube_z2,
                tube_z1 + BRIDGE_TUBE_HW * 2,
                tube_z2 + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )


def _add_bridge_pier6_connection_tubes(
    brushes,
    pier6_old_cutoff_x,
    span4_west_mid,
    tube_ny1,
    tube_ny2,
    tube_sy1,
    tube_sy2,
    tube_base_z,
):
    """Add the flat railing tube runs west of pier 6 for one offset."""

    brushes.append(
        box(
            BRIDGE.x2,
            tube_ny1,
            tube_base_z,
            PIER5_X,
            tube_ny2,
            tube_base_z + BRIDGE_TUBE_HW * 2,
            Textures.RAIL,
        )
    )
    brushes.extend(
        _pier6_west_pieces(
            PIER5_X,
            tube_ny1,
            tube_ny2,
            tube_base_z,
            tube_base_z + BRIDGE_TUBE_HW * 2,
            Textures.RAIL,
            pier6_old_cutoff_x,
            far=False,
            margin=-4,
        )
    )
    brushes.append(
        box(
            BRIDGE.x2,
            tube_sy1,
            tube_base_z,
            span4_west_mid,
            tube_sy2,
            tube_base_z + BRIDGE_TUBE_HW * 2,
            Textures.RAIL,
        )
    )
    brushes.extend(
        _pier6_west_pieces(
            PIER5_X,
            tube_sy1,
            tube_sy2,
            tube_base_z,
            tube_base_z + BRIDGE_TUBE_HW * 2,
            Textures.RAIL,
            pier6_old_cutoff_x,
        )
    )


def _build_bridge_superstructure(
    brushes,
    entities,
    bridge_blk_pir_m,
    pier6_old_cutoff_x,
    span_boundaries,
    span_counts,
    span4_west_mid,
):
    """Build the bridge parapet decorations and railing tubes."""

    _build_bridge_parapet_light_spans(
        brushes,
        entities,
        bridge_blk_pir_m,
        span_boundaries,
        span_counts,
    )
    _build_bridge_parapet_square_brushes(brushes, bridge_blk_pir_m, span_counts)
    brushes.append(_bridge_south_parapet_endcap_brush(span4_west_mid))

    tube_ny1, tube_ny2, tube_sy1, tube_sy2 = _bridge_railing_tube_y_bounds()
    for tube_z_offset in [BRIDGE_TUBE_RISE, BRIDGE_TUBE_RISE + BRIDGE_TUBE_GAP]:
        _add_bridge_span_tubes(
            brushes,
            span_boundaries,
            tube_ny1,
            tube_ny2,
            tube_sy1,
            tube_sy2,
            tube_z_offset,
        )
        _add_bridge_pier6_connection_tubes(
            brushes,
            pier6_old_cutoff_x,
            span4_west_mid,
            tube_ny1,
            tube_ny2,
            tube_sy1,
            tube_sy2,
            BRIDGE_DZ2 + BRIDGE.parapet_h + tube_z_offset,
        )


def _build_bridge_support_shell(brushes, ctx):
    """Build the pier arch/square shell, footing, and face plates."""
    px = ctx["px"]
    x1 = ctx["x1"]
    x2 = ctx["x2"]
    by1 = ctx["by1"]
    by2 = ctx["by2"]
    py_shift = ctx["py_shift"]
    pier_floor_z = ctx["pier_floor_z"]
    pier_ceiling_z = ctx["pier_ceiling_z"]
    a_rin = ctx["a_rin"]
    a_rout = ctx["a_rout"]
    a_stilt = ctx["a_stilt"]
    arch_overhang = ctx["arch_overhang"]
    base_ramp = ctx["base_ramp"]
    pier_recess = ctx["pier_recess"]
    max_outer_radius = ctx["max_outer_radius"]

    if px == max(BRIDGE_ARCH_X):
        sq_overhang = BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG - a_rin
        brushes.extend(
            square_wall(
                x1,
                x2,
                by1,
                by2,
                pier_floor_z,
                pier_ceiling_z,
                a_rin,
                Textures.PIER_STONE,
                overhang=sq_overhang,
                base_ramp=base_ramp,
                yc=py_shift,
                base_cap_h=BRIDGE_PILLAR_BASE_CAP_H,
                base_cap_tex=Textures.CEMENT,
                base_cap_ovh=BRIDGE_PILLAR_BASE_CAP_OVH,
                recess=pier_recess,
                lintel_h=BRIDGE_SQ_LINTEL_H,
            )
        )
    else:
        brushes.extend(
            arch_wall(
                x1,
                x2,
                by1,
                by2,
                pier_floor_z,
                pier_ceiling_z,
                a_rin,
                a_rout,
                A_SEGS,
                Textures.PIER_STONE,
                stilt_h=a_stilt,
                overhang=arch_overhang,
                base_h=BRIDGE_PILLAR_BASE_H,
                base_ramp=base_ramp,
                yc=py_shift,
                base_cap_h=(
                    BRIDGE_ABUTMENT_RAMP_CAP_H
                    if px == min(BRIDGE_ARCH_X)
                    else BRIDGE_PILLAR_BASE_CAP_H
                ),
                base_cap_tex=Textures.CEMENT,
                base_cap_ovh=BRIDGE_PILLAR_BASE_CAP_OVH,
                recess=pier_recess,
            )
        )

    if px in (PIER2_X, PIER3_X, PIER4_X, PIER5_X, PIER6_X) and (
        BRIDGE_CENTER_SPAN_OFFSET != (0.0, 0.0, 0.0)
    ):
        footer_y1 = min(by1, -max_outer_radius)
        footer_y2 = max(by2, max_outer_radius)
        footer_depth = max(BRIDGE_CENTER_SPAN_PIER_EMBED, BRIDGE_CENTER_SPAN_OFFSET[2])
        brushes.append(
            box(
                x1,
                footer_y1,
                pier_floor_z - footer_depth,
                x2,
                footer_y2,
                pier_floor_z,
                Textures.PIER_STONE,
            )
        )

    is_square_pier = px == max(BRIDGE_ARCH_X)
    for face_x, protrude in ((x1, -BRIDGE_PIER_PLATE_D), (x2, BRIDGE_PIER_PLATE_D)):
        if is_square_pier:
            tile_pitch = BRIDGE_PIER_PLATE_SIZE + BRIDGE_PIER_PLATE_GAP
            brushes.extend(
                tile_face_plates(
                    face_x,
                    protrude,
                    by1 + tile_pitch,
                    by2 - tile_pitch,
                    pier_ceiling_z - BRIDGE_SQ_LINTEL_H,
                    pier_ceiling_z - BRIDGE_SQ_LINTEL_STONE_H,
                    Textures.CEMENT,
                    tile=BRIDGE_PIER_PLATE_SIZE,
                    gap=BRIDGE_PIER_PLATE_GAP,
                )
            )
        else:
            brushes.extend(
                arch_plate_ring(
                    face_x,
                    protrude,
                    0.0,
                    pier_floor_z + a_stilt,
                    a_rin + 2,
                    Textures.CEMENT,
                    tile=BRIDGE_PIER_PLATE_SIZE,
                    gap=BRIDGE_PIER_PLATE_GAP,
                )
            )


def _build_bridge_support_pillar_masses(brushes, ctx):
    """Build the above-deck pier masses, seams, and fill blocks."""
    px = ctx["px"]
    x1 = ctx["x1"]
    x2 = ctx["x2"]
    by1 = ctx["by1"]
    by2 = ctx["by2"]
    pdeck = ctx["pdeck"]
    ppil = ctx["ppil"]
    pier_outer_y = ctx["pier_outer_y"]

    brushes.append(
        box(
            px - BRIDGE_PILLAR_HW,
            by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG,
            pdeck,
            px + BRIDGE_PILLAR_HW,
            pier_outer_y,
            ppil,
            Textures.PIER_STONE,
        )
    )

    brushes.append(
        box(
            px - BRIDGE_PILLAR_HW,
            by1 - BRIDGE_PILLAR_OVERHANG,
            pdeck,
            px + BRIDGE_PILLAR_HW,
            by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG,
            ppil,
            Textures.PIER_STONE,
        )
    )

    north_inside_y = by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG
    brushes.append(
        box(
            px - BRIDGE_PILLAR_SEAM_HW,
            north_inside_y - BRIDGE_PILLAR_SEAM_D,
            pdeck,
            px + BRIDGE_PILLAR_SEAM_HW,
            north_inside_y,
            ppil,
            Textures.CEMENT,
        )
    )
    south_inside_y = by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG
    brushes.append(
        box(
            px - BRIDGE_PILLAR_SEAM_HW,
            south_inside_y,
            pdeck,
            px + BRIDGE_PILLAR_SEAM_HW,
            south_inside_y + BRIDGE_PILLAR_SEAM_D,
            ppil,
            Textures.CEMENT,
        )
    )

    brushes.append(
        box(
            px - BRIDGE_PILLAR_HW - BRIDGE_PILLAR_SEAM_D,
            by2 - BRIDGE_PILLAR_SEAM_HW,
            pdeck,
            px - BRIDGE_PILLAR_HW,
            by2 + BRIDGE_PILLAR_SEAM_HW,
            ppil,
            Textures.CEMENT,
        )
    )
    brushes.append(
        box(
            px - BRIDGE_PILLAR_HW - BRIDGE_PILLAR_SEAM_D,
            by1 - BRIDGE_PILLAR_SEAM_HW,
            pdeck,
            px - BRIDGE_PILLAR_HW,
            by1 + BRIDGE_PILLAR_SEAM_HW,
            ppil,
            Textures.CEMENT,
        )
    )

    pier_top_z = ctx["pier_top_z"]
    if px != PIER6_X:
        brushes.append(
            box(
                x1,
                by2,
                pier_top_z,
                x2,
                pier_outer_y,
                pdeck,
                Textures.PIER_STONE,
            )
        )
    brushes.append(
        box(
            x1,
            by1 - BRIDGE_PILLAR_OVERHANG,
            pier_top_z,
            x2,
            by1,
            pdeck,
            Textures.PIER_STONE,
        )
    )


def _build_bridge_support_caps_and_torches(brushes, entities, ctx):
    """Build the pier caps, pyramids, and torch assemblies."""
    px = ctx["px"]
    by1 = ctx["by1"]
    by2 = ctx["by2"]
    cy_n = ctx["cy_n"]
    cy_s = ctx["cy_s"]
    ppil = ctx["ppil"]
    pcap = ctx["pcap"]

    cap_x1, cap_x2 = px - BRIDGE_PILLAR_PYR_W, px + BRIDGE_PILLAR_PYR_W
    north_cap_y1 = (
        by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG - BRIDGE_PILLAR_CAP_IN_OVH
    )
    north_cap_y2 = by2 + BRIDGE_PILLAR_CAP_OUT_OVH
    south_cap_y1 = by1 - BRIDGE_PILLAR_CAP_OUT_OVH
    south_cap_y2 = (
        by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG + BRIDGE_PILLAR_CAP_IN_OVH
    )
    brushes.append(
        box(
            cap_x1,
            north_cap_y1,
            ppil,
            cap_x2,
            north_cap_y2,
            pcap,
            Textures.CEMENT,
        )
    )
    brushes.append(
        box(
            cap_x1,
            south_cap_y1,
            ppil,
            cap_x2,
            south_cap_y2,
            pcap,
            Textures.CEMENT,
        )
    )
    brushes.append(
        pyramid(
            cap_x1,
            north_cap_y1,
            pcap,
            cap_x2,
            north_cap_y2,
            pcap + BRIDGE_PILLAR_PYR_H,
            Textures.CEMENT,
        )
    )
    brushes.append(
        pyramid(
            cap_x1,
            south_cap_y1,
            pcap,
            cap_x2,
            south_cap_y2,
            pcap + BRIDGE_PILLAR_PYR_H,
            Textures.CEMENT,
        )
    )
    pyramid_apex_z = pcap + BRIDGE_PILLAR_PYR_H
    torch_ys = [] if px in (PIER2_X, PIER3_X, PIER6_X) else [cy_n, cy_s]
    for torch_center_y in torch_ys:
        brushes.append(
            box(
                px - BRIDGE_TORCH_POST_HW,
                torch_center_y - BRIDGE_TORCH_POST_HW,
                pyramid_apex_z,
                px + BRIDGE_TORCH_POST_HW,
                torch_center_y + BRIDGE_TORCH_POST_HW,
                pyramid_apex_z + BRIDGE_TORCH_POST_H,
                Textures.CEMENT,
            )
        )
        brushes.append(
            box(
                px - BRIDGE_TORCH_CUP_HW,
                torch_center_y - BRIDGE_TORCH_CUP_HW,
                pyramid_apex_z + BRIDGE_TORCH_POST_H,
                px + BRIDGE_TORCH_CUP_HW,
                torch_center_y + BRIDGE_TORCH_CUP_HW,
                pyramid_apex_z + BRIDGE_TORCH_POST_H + BRIDGE_TORCH_CUP_H,
                Textures.BRICK,
            )
        )
        flame_z = int(pyramid_apex_z + BRIDGE_TORCH_POST_H + BRIDGE_TORCH_CUP_H + 4)
        entities.append(torch_flame_only(px, torch_center_y, flame_z))
        fhb = box(
            px - 16,
            torch_center_y - 16,
            flame_z,
            px + 16,
            torch_center_y + 16,
            flame_z + 40,
            Textures.SKY,
        )
        entities.append(brush_ent("trigger_hurt", [fhb], dmg="10"))


def _rotate_pier6_support_geometry(
    brushes, entities, ctx, pier6_rot_bstart, pier6_rot_estart
):
    """Rotate the Pier 6 geometry after building it in the unrotated frame."""
    if pier6_rot_bstart is None:
        return

    px = ctx["px"]
    py_shift = ctx["py_shift"]
    x1 = ctx["x1"]
    x2 = ctx["x2"]
    by2 = ctx["by2"]
    pier_top_z = ctx["pier_top_z"]
    pier_outer_y = ctx["pier_outer_y"]
    pdeck = ctx["pdeck"]

    brushes[pier6_rot_bstart:] = [
        b.rotated_z(PIER6_ROTATION_DEG, px, py_shift)
        for b in brushes[pier6_rot_bstart:]
    ]
    entities[pier6_rot_estart:] = [
        e.rotated_z(PIER6_ROTATION_DEG, px, py_shift)
        for e in entities[pier6_rot_estart:]
    ]
    brushes.append(
        box(
            x1,
            by2,
            pier_top_z,
            x2,
            pier_outer_y,
            pdeck,
            Textures.PIER_STONE,
        ).rotated_z(PIER6_ROTATION_DEG, px, py_shift)
    )


def _build_bridge_west_abutment_fill(brushes, teleport_state, ctx):
    """Build the west abutment fill and record the teleport geometry."""
    if ctx["px"] != min(BRIDGE_ARCH_X):
        return

    x1 = ctx["x1"]
    x2 = ctx["x2"]
    a_rin = ctx["a_rin"]
    pier_floor_z = ctx["pier_floor_z"]
    pier_top_z = ctx["pier_top_z"]
    pdeck = ctx["pdeck"]

    ramp_top_west_z = (
        pier_floor_z + BRIDGE_ABUTMENT_RAMP_HIGH_H + BRIDGE_ABUTMENT_RAMP_CAP_H
    )
    ramp_top_east_z = (
        pier_floor_z + BRIDGE_ABUTMENT_RAMP_LOW_H + BRIDGE_ABUTMENT_RAMP_CAP_H
    )
    brushes.append(
        box(
            x1 + BRIDGE_PIER_FILL_OFFSET,
            -a_rin,
            ramp_top_east_z,
            x2 - BRIDGE_PIER_FILL_OFFSET,
            a_rin,
            int(pdeck) - BRIDGE_PIER_FILL_OFFSET,
            Textures.CEMENT,
        )
    )

    teleport_floor_z = ramp_top_west_z
    teleport_stilt_height = (
        pier_top_z - teleport_floor_z - a_rin - BRIDGE_TELEPORT_ARCH_CLEARANCE
    )
    teleport_state["brush"] = arch_fill(
        x1 + BRIDGE_TELEPORT_ARCH_X1_OFFSET,
        x1 + BRIDGE_TELEPORT_ARCH_X2_OFFSET,
        0.0,
        teleport_floor_z,
        a_rin,
        A_SEGS,
        Textures.TELEPORT,
        stilt_h=teleport_stilt_height,
    )
    teleport_state["dest_z"] = int(pdeck) + BRIDGE_TELEPORT_DEST_Z

    cem_rin = BRIDGE_ABUTMENT_CEMENT_RIN
    cem_floor_z = ramp_top_east_z
    cem_stilt_h = max(0, BRIDGE_ABUTMENT_CEMENT_MAX_H - cem_rin)
    cem_x1 = x2 - BRIDGE_ABUTMENT_CEMENT_X1_OFFSET
    cem_x2 = x2 - BRIDGE_ABUTMENT_CEMENT_X2_OFFSET
    brushes.extend(
        arch_fill(
            cem_x1,
            cem_x2,
            0.0,
            cem_floor_z,
            cem_rin,
            A_SEGS,
            Textures.CEMENT,
            stilt_h=cem_stilt_h,
        )
    )


def _build_bridge_support_pier(brushes, entities, px, teleport_state):
    """Build one bridge support pier, including abutment specials."""
    pier5_lintel_gap_default = 24
    pier6_rot_bstart = len(brushes) if px == PIER6_X else None
    pier6_rot_estart = len(entities) if px == PIER6_X else None
    pdeck = deck_top_z(px)
    ppar = pdeck + BRIDGE.parapet_h
    ppil = ppar + BRIDGE_PILLAR_EXTRA
    pcap = ppil + BRIDGE_PILLAR_CAP_H

    py_shift = east_y_shift(px)
    by1 = BRIDGE.y1 + py_shift
    by2 = BRIDGE.y2 + py_shift

    cy_n = by2 - BRIDGE_PAR_W // 2
    cy_s = by1 + BRIDGE_PAR_W // 2

    x1, x2 = px - BRIDGE_PILLAR_HW, px + BRIDGE_PILLAR_HW

    pier_ceiling_z = max(int(deck_bot_z(x1)), int(deck_bot_z(x2)))

    if px in (PIER2_X, PIER3_X) and BRIDGE_CENTER_SPAN_OFFSET != (0.0, 0.0, 0.0):
        pier_floor_z = FLOOR_Z2
    else:
        pier_floor_z = BRIDGE_PIER_GROUND_Z.get(px, FLOOR_Z2)

    if px in (min(BRIDGE_ARCH_X), BRIDGE_ARCH_X[4], max(BRIDGE_ARCH_X)):
        a_rout, a_rin = BRIDGE_PILLAR_OUTER_R
    else:
        a_rout, a_rin = BRIDGE_PILLAR_INNER_R
    a_stilt = pier_ceiling_z - a_rout - pier_floor_z
    if a_stilt < 0:
        a_rout = pier_ceiling_z - pier_floor_z
        a_stilt = 0

    max_outer_radius = BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG
    if a_rout > max_outer_radius:
        a_rout = max_outer_radius
        a_stilt = pier_ceiling_z - a_rout - pier_floor_z
    arch_overhang = max(0, max_outer_radius - a_rout)

    pier5_lintel_gap = pier5_lintel_gap_default if px == PIER5_X else 0
    a_stilt = max(0, a_stilt - pier5_lintel_gap)

    if px == min(BRIDGE_ARCH_X):
        base_ramp = (
            pier_floor_z + BRIDGE_ABUTMENT_RAMP_HIGH_H,
            pier_floor_z + BRIDGE_ABUTMENT_RAMP_LOW_H,
        )
    elif px > 0:
        base_ramp = (
            pier_floor_z + BRIDGE_PILLAR_BASE_H,
            pier_floor_z + BRIDGE_PILLAR_BASE_RAMP_H,
        )
    else:
        base_ramp = (
            pier_floor_z + BRIDGE_PILLAR_BASE_RAMP_H,
            pier_floor_z + BRIDGE_PILLAR_BASE_H,
        )

    pier_recess = (
        None
        if px == min(BRIDGE_ARCH_X)
        else (
            BRIDGE_PIER_LINING_MARGIN,
            BRIDGE_PIER_LINING_THICK,
            Textures.CEMENT,
        )
    )
    pier_outer_y = by2 + BRIDGE_PILLAR_OVERHANG
    pier_top_z = int(pdeck) - BRIDGE_PIER_FILL_OFFSET
    ctx = {
        "px": px,
        "pdeck": pdeck,
        "ppil": ppil,
        "pcap": pcap,
        "py_shift": py_shift,
        "by1": by1,
        "by2": by2,
        "cy_n": cy_n,
        "cy_s": cy_s,
        "x1": x1,
        "x2": x2,
        "pier_ceiling_z": pier_ceiling_z,
        "pier_floor_z": pier_floor_z,
        "a_rout": a_rout,
        "a_rin": a_rin,
        "a_stilt": a_stilt,
        "max_outer_radius": max_outer_radius,
        "arch_overhang": arch_overhang,
        "base_ramp": base_ramp,
        "pier_recess": pier_recess,
        "pier_outer_y": pier_outer_y,
        "pier_top_z": pier_top_z,
    }
    _build_bridge_support_shell(brushes, ctx)
    _build_bridge_support_pillar_masses(brushes, ctx)
    _build_bridge_support_caps_and_torches(brushes, entities, ctx)
    _rotate_pier6_support_geometry(
        brushes, entities, ctx, pier6_rot_bstart, pier6_rot_estart
    )
    _build_bridge_west_abutment_fill(brushes, teleport_state, ctx)


def _build_bridge_supports(brushes, entities, teleport_state):
    """Build the bridge piers, abutments, torches, and teleport fill."""
    if BRIDGE_ENABLED_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if (
                BRIDGE_ENABLED_SUPPORTS is not True
                and px not in BRIDGE_ENABLED_SUPPORTS
            ):
                continue
            _build_bridge_support_pier(brushes, entities, px, teleport_state)


def _append_bridge_detail_entity(entities, detail_brushes):
    """Wrap the generated bridge geometry into the same func_detail entity."""
    if detail_brushes:
        entities.append(brush_ent("func_detail", detail_brushes))


def _append_bridge_teleport_entities(entities, teleport_state):
    """Append the west-abutment teleport entities when teleports are enabled."""
    if ENTITIES_ENABLED_TELEPORTS and teleport_state:
        entities.append(
            ent(
                "info_teleport_destination",
                targetname="dest_abutment_deck",
                origin=f"{min(BRIDGE_ARCH_X)} 0 {teleport_state['dest_z']}",
                angle="0",
            )
        )
        entities.append(
            brush_ent(
                "trigger_teleport", teleport_state["brush"], target="dest_abutment_deck"
            )
        )
        entities.append(brush_ent("func_illusionary", teleport_state["brush"]))


def _render_bridge_fascia(
    text, x0, y_face, px_w, px_h, depth, tex, capital_pos, mirror=False
):
    """Return raised pixel-font brushes for text on a bridge fascia face."""
    cols = 4
    rows = 6
    small_pw = px_w - 1
    small_ph = px_h - 1

    brushes = []
    cx = x0
    for ci, ch in enumerate(text):
        cpw = px_w if ci in capital_pos else small_pw
        cph = px_h if ci in capital_pos else small_ph
        char_w = (cols + 1) * cpw

        bitmap = FASCIA_FONT.get(ch, FASCIA_FONT[" "])
        x_mid = cx + (cols * cpw) / 2
        z_top_cap = int(deck_top_z(x_mid)) + BRIDGE.parapet_h - 14
        z_top = z_top_cap - rows * (px_h - cph)

        for row_i, row_bits in enumerate(bitmap):
            z = z_top - row_i * cph
            for col_i in range(cols):
                src_col = (cols - 1 - col_i) if mirror else col_i
                if row_bits & (1 << (cols - 1 - src_col)):
                    px = cx + col_i * cpw
                    brushes.append(
                        box(px, y_face - depth, z - cph, px + cpw, y_face, z, tex)
                    )
        cx += char_w
    return brushes


def _append_bridge_fascia_text(entities):
    """Append the fascia text detail entity using the original brush order."""
    cols = 4
    small_px = BRIDGE_FASCIA_PX_W - 1
    n_chars = len(BRIDGE_FASCIA_TEXT)
    capital_pos = {
        i
        for i, ch in enumerate(BRIDGE_FASCIA_TEXT)
        if ch != " " and (i == 0 or BRIDGE_FASCIA_TEXT[i - 1] == " ")
    }
    capital_pos_rev = {n_chars - 1 - i for i in capital_pos}

    def _char_pw(i):
        return BRIDGE_FASCIA_PX_W if i in capital_pos else small_px

    total_w = sum((cols + 1) * _char_pw(i) for i in range(n_chars)) - _char_pw(
        n_chars - 1
    )
    fascia_cx = (PIER2_X + PIER3_X) // 2
    text_x0 = fascia_cx - total_w // 2

    letter_brushes = (
        (
            _render_bridge_fascia(
                BRIDGE_FASCIA_TEXT,
                x0=text_x0,
                y_face=BRIDGE.y1,
                px_w=BRIDGE_FASCIA_PX_W,
                px_h=BRIDGE_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
                capital_pos=capital_pos,
            )
            + _render_bridge_fascia(
                BRIDGE_FASCIA_TEXT[::-1],
                x0=text_x0,
                y_face=BRIDGE.y2 + 1,
                px_w=BRIDGE_FASCIA_PX_W,
                px_h=BRIDGE_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
                capital_pos=capital_pos_rev,
                mirror=True,
            )
        )
        if BRIDGE_ENABLED_FASCIA_TEXT
        else []
    )
    if letter_brushes:
        entities.append(brush_ent("func_detail", letter_brushes))


def _bridge_cross_strip_x(bridge_blk_pir_m):
    """Return the sorted parapet-strip centers shared by the deck slabs."""

    return sorted(
        _parapet_block_centers(
            BRIDGE_ARCH_X[0],
            BRIDGE_ARCH_X[1],
            3,
            bridge_blk_pir_m,
            west_margin=0,
            east_margin=0,
        )
        + _parapet_block_centers(
            BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4, bridge_blk_pir_m
        )
        + _parapet_block_centers(
            BRIDGE_ARCH_X[2],
            BRIDGE_ARCH_X[3],
            3,
            bridge_blk_pir_m,
            west_margin=0,
            east_margin=0,
        )
        + _parapet_block_centers(
            BRIDGE.x2,
            BRIDGE_ARCH_X[4],
            3,
            bridge_blk_pir_m,
            west_margin=0,
            east_margin=0,
        )
    )


def _bridge_deck_bands():
    """Return the deck-band specs and inner expansion-joint bounds."""

    dw_y1a = BRIDGE.y1
    dw_y1b = BRIDGE.y1 + BRIDGE_PAR_W
    dw_y1c = dw_y1b + BRIDGE_DECK_EDGE_CEMENT_W
    dw_y2c = BRIDGE.y2 - BRIDGE_PAR_W - BRIDGE_DECK_EDGE_CEMENT_W
    dw_y2b = BRIDGE.y2 - BRIDGE_PAR_W
    dw_y2a = BRIDGE.y2
    deck_bands = (
        (dw_y1a, dw_y1b, Textures.CEMENT, Textures.CEMENT, True, 0, 0, "0 0 0 1 1"),
        (dw_y1b, dw_y1c, Textures.DECK_EDGE, Textures.GABLE, True, 0, 0, "0 0 0 1 1"),
        (dw_y1c, dw_y2c, Textures.FLOOR1, Textures.GABLE, True, 0, 0, "0 0 45 1 1"),
        (dw_y2c, dw_y2b, Textures.DECK_EDGE, Textures.GABLE, False, 0, 0, "0 0 0 1 1"),
        (dw_y2b, dw_y2a, Textures.CEMENT, Textures.CEMENT, False, 0, 0, "0 0 0 1 1"),
    )
    return deck_bands, (dw_y1c, dw_y2c)


def _bridge_span_boundaries():
    """Return the x boundaries for the deck-support span segmentation."""

    p1, p2, p3 = BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]
    n_center = max(1, round((p3 - p2) / BRIDGE_SEG_W))
    step = (p3 - p2) / n_center
    span_boundaries = [BRIDGE.x1, p1, p2]
    span_boundaries += [p2 + i * step for i in range(1, n_center)]
    span_boundaries += [p3, BRIDGE.x2]
    return span_boundaries


def _add_bridge_parapet_block_span(
    detail_brushes,
    bridge_blk_pir_m,
    span_boundaries,
    *,
    label,
    x1,
    x2,
    count,
    west_margin=None,
    east_margin=None,
    n_south=None,
    y_shift_fn=None,
):
    """Add one parapet-block span after checking its available spacing."""

    gap = (x2 - x1) / (count + 1)
    if west_margin == 0 and east_margin == 0 and gap < bridge_blk_pir_m:
        raise ValueError(
            f"{label} parapet-block gap ({gap:.1f}) is tighter than the minimum "
            f"pier clearance ({bridge_blk_pir_m}) — reduce block count or shorten the "
            "even-margin spacing before it can safely use margin=0."
        )

    kwargs = {}
    if west_margin is not None:
        kwargs["west_margin"] = west_margin
    if east_margin is not None:
        kwargs["east_margin"] = east_margin
    if n_south is not None:
        kwargs["n_south"] = n_south
    if y_shift_fn is not None:
        kwargs["y_shift_fn"] = y_shift_fn

    _add_parapet_blocks(
        detail_brushes,
        x1,
        x2,
        count,
        bridge_blk_pir_m,
        span_boundaries,
        **kwargs,
    )


def _add_bridge_parapet_block_spans(detail_brushes, bridge_blk_pir_m, span_boundaries):
    """Add the fixed parapet-block spans and return their per-span counts."""

    span1_n = 3
    _add_bridge_parapet_block_span(
        detail_brushes,
        bridge_blk_pir_m,
        span_boundaries,
        label="Span 1",
        x1=BRIDGE_ARCH_X[0],
        x2=BRIDGE_ARCH_X[1],
        count=span1_n,
        west_margin=0,
        east_margin=0,
    )
    _add_bridge_parapet_block_span(
        detail_brushes,
        bridge_blk_pir_m,
        span_boundaries,
        label="Span 2",
        x1=BRIDGE_ARCH_X[1],
        x2=BRIDGE_ARCH_X[2],
        count=4,
    )
    span3_n = 3
    _add_bridge_parapet_block_span(
        detail_brushes,
        bridge_blk_pir_m,
        span_boundaries,
        label="Span 3",
        x1=BRIDGE_ARCH_X[2],
        x2=BRIDGE_ARCH_X[3],
        count=span3_n,
        west_margin=0,
        east_margin=0,
    )
    kh_span_n = 3
    _add_bridge_parapet_block_span(
        detail_brushes,
        bridge_blk_pir_m,
        span_boundaries,
        label="KH span",
        x1=BRIDGE.x2,
        x2=BRIDGE_ARCH_X[4],
        count=kh_span_n,
        west_margin=0,
        east_margin=0,
        n_south=0,
        y_shift_fn=east_y_shift,
    )
    return span1_n, span3_n, kh_span_n


def _build_all():
    """Generate the full bridge geometry before section filtering."""
    worldspawn_brushes = []
    entities = []
    detail_brushes = []
    bridge_blk_pir_m = BRIDGE_PILLAR_HW + BRIDGE_BLK_HW + BRIDGE_BLK_PIER_CLEARANCE

    cross_strip_x = _bridge_cross_strip_x(bridge_blk_pir_m)
    deck_bands, deck_joint_y = _bridge_deck_bands()
    pier6_old_cutoff_x = PIER6_X - BRIDGE_PILLAR_HW
    span_boundaries = _bridge_span_boundaries()

    _build_bridge_deck_slabs(
        detail_brushes,
        entities,
        deck_bands,
        cross_strip_x,
        pier6_old_cutoff_x,
        span_boundaries,
        (BRIDGE.y1 + BRIDGE_PAR_W, BRIDGE.y2 - BRIDGE_PAR_W),
    )
    _build_bridge_expansion_joints(entities, deck_joint_y)

    span4_west_mid = (BRIDGE.x2 + KNOTT_ENT_WALK_X1) / 2
    _build_bridge_parapet_shells(
        detail_brushes,
        pier6_old_cutoff_x,
        span_boundaries,
        span4_west_mid,
    )

    span_counts = _add_bridge_parapet_block_spans(
        detail_brushes, bridge_blk_pir_m, span_boundaries
    )

    _build_bridge_superstructure(
        detail_brushes,
        entities,
        bridge_blk_pir_m,
        pier6_old_cutoff_x,
        span_boundaries,
        span_counts,
        span4_west_mid,
    )

    teleport_state = {}
    _build_bridge_supports(detail_brushes, entities, teleport_state)

    brushes = worldspawn_brushes
    _append_bridge_detail_entity(entities, detail_brushes)
    _append_bridge_teleport_entities(entities, teleport_state)
    _append_bridge_fascia_text(entities)

    return brushes, entities


def _append_bridge_pier_banner(entities, enabled_names, pier_x, x_dir, y_side):
    """Hang a banner from a horizontal mast off one center-span pier.

    Charles St runs north-south between Piers 2 and 3, so each mast projects
    off the pier's streetward face, out over the road, with the banner swinging
    below it like a flag. That leaves the banner's broad faces pointing north
    and south - the two directions traffic approaches from - and its silhouette
    readable end-on from the pier itself.

    Args:
        entities: Entity list to append the mast and banner to.
        enabled_names: Enabled bridge section names, used to decide whether the
            center-span offset applies.
        pier_x: X centre of the pier to hang from.
        x_dir: ``+1`` to project east off the pier, ``-1`` to project west.
        y_side: ``-1`` to hang from the south corner column, ``+1`` for north.

    Texture offsets are computed from the banner's final world position, after
    any center-span shift: ``Brush.translated`` moves the geometry but leaves
    texture alignment in world space, so an offset derived from pre-shift
    coordinates would slide the image off the banner.
    """
    if BRIDGE_ENABLED_SUPPORTS is not True and pier_x not in BRIDGE_ENABLED_SUPPORTS:
        return
    # The banners are appended after _filter_sections has run, so they have to
    # repeat its ownership test: without this, disabling the span that owns
    # Pier 2 or Pier 3 leaves its banner and mast floating over Charles St
    # with no pier behind them.
    if not _pier_survives_section_filter(pier_x, enabled_names):
        return
    shifted = (
        BRIDGE_CENTER_SPAN_OFFSET != (0.0, 0.0, 0.0) and "center_span" in enabled_names
    )
    _, dy, dz = BRIDGE_CENTER_SPAN_OFFSET if shifted else (0.0, 0.0, 0.0)

    x_face = pier_x + x_dir * BRIDGE_PILLAR_HW
    z_top = FLOOR_Z2 + BRIDGE_BANNER_TOP_Z + dz
    pier_corner_y = BRIDGE.y2 if y_side > 0 else BRIDGE.y1
    y_center = (
        pier_corner_y
        + y_side * (BRIDGE_PILLAR_OVERHANG - BRIDGE_BANNER_CORNER_INSET)
        + dy
    )
    x_near = x_face + x_dir * BRIDGE_BANNER_GAP
    x_far = x_near + x_dir * BRIDGE_BANNER_W
    x1, x2 = min(x_near, x_far), max(x_near, x_far)
    mast_hw = BRIDGE_BANNER_MAST_T / 2
    mast_tip = x_far + x_dir * BRIDGE_BANNER_MAST_PROUD

    entities.append(
        brush_ent(
            "func_detail",
            box(
                min(x_face, mast_tip),
                y_center - mast_hw,
                z_top,
                max(x_face, mast_tip),
                y_center + mast_hw,
                z_top + BRIDGE_BANNER_MAST_T,
                Textures.RAIL,
            ),
        )
    )
    # The banner reads as cloth, so it hangs non-solid; func_illusionary also
    # gets the masked texture rendered with its cutouts honoured.
    banner_params = f"{-x1 % BRIDGE_BANNER_W} {z_top % BRIDGE_BANNER_H} 0 1 1"
    entities.append(
        brush_ent(
            "func_illusionary",
            box(
                x1,
                y_center - BRIDGE_BANNER_T / 2,
                z_top - BRIDGE_BANNER_H,
                x2,
                y_center + BRIDGE_BANNER_T / 2,
                z_top,
                Textures.BANNER,
                ts_params=banner_params,
                tn_params=banner_params,
            ),
        )
    )


def build():
    """Build the pedestrian bridge: deck, arch spans, piers, and parapets.

    Individual spans (west approach, center, east approach) are toggled via
    the ``BRIDGE_ENABLED_SPAN_*`` config flags.

    Returns:
        tuple[list, list]: ``(brushes, entities)`` for the enabled bridge
        sections.
    """
    sections_enabled = {
        "west_approach": BRIDGE_ENABLED_SPAN_WEST_APPROACH,
        "center_span": BRIDGE_ENABLED_SPAN_CENTER,
        "east_approach": BRIDGE_ENABLED_SPAN_EAST_APPROACH,
        "kh_span": BRIDGE_ENABLED_SPAN_KH,
        "east_ext": BRIDGE_ENABLED_SPAN_EAST_EXT,
    }
    if not any(sections_enabled.values()):
        return [], []
    BRUSHES, ENTITIES = _build_all()
    enabled_names = [name for name, v in sections_enabled.items() if v]
    if not all(sections_enabled.values()):
        BRUSHES, ENTITIES = _filter_sections(BRUSHES, ENTITIES, enabled_names)
    if BRIDGE_CENTER_SPAN_OFFSET != (0.0, 0.0, 0.0) and "center_span" in enabled_names:
        BRUSHES, ENTITIES = _shift_center_span(
            BRUSHES, ENTITIES, enabled_names, BRIDGE_CENTER_SPAN_OFFSET
        )
    # Piers 2 and 3 flank Charles St, so their banners hang kitty-corner from
    # each other: Pier 2's off its south corner facing east into the road,
    # Pier 3's off its north corner facing west into the road.
    _append_bridge_pier_banner(ENTITIES, enabled_names, PIER2_X, x_dir=1, y_side=-1)
    _append_bridge_pier_banner(ENTITIES, enabled_names, PIER3_X, x_dir=-1, y_side=1)
    return BRUSHES, ENTITIES


def _shift_center_span(brushes, entities, enabled_names, offset):
    """Translate the center span and any other enabled sections by one offset.

    Shared piers stay connected because every enabled section moves as the
    same rigid assembly. Filter the full enabled set in a single pass rather
    than extracting each section separately and concatenating: per-section
    acceptance windows intentionally overlap their neighbor's near a shared
    pier (so the owning section's margin can capture boundary geometry),
    and extracting+translating each name individually would double up any
    brush that falls in that overlap band.
    """
    dx, dy, dz = offset
    sect_b, sect_e = _filter_sections(brushes, entities, enabled_names)
    sect_b = [b.translated(dx, dy, dz) for b in sect_b]
    sect_e = [e.translated(dx, dy, dz) for e in sect_e]
    return sect_b, sect_e
