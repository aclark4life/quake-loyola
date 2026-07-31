"""Build the pedestrian bridge over Charles Street.

This module generates the bridge deck, parapets, piers, archwork,
abutment teleports, and fascia lettering between west campus and Knott Hall.
"""

from .constants import (
    A_SEGS,
    ARCH_RIN,
    ARCH_ROUT,
    ARCH_SLAB_W,
    ARCH_STILT_H,
    BRIDGE,
    BRIDGE_ABUTMENT_CEMENT_MAX_H,
    BRIDGE_ABUTMENT_CEMENT_RIN,
    BRIDGE_ABUTMENT_CEMENT_X1_OFFSET,
    BRIDGE_ABUTMENT_CEMENT_X2_OFFSET,
    BRIDGE_ABUTMENT_RAMP_CAP_H,
    BRIDGE_ABUTMENT_RAMP_HIGH_H,
    BRIDGE_ABUTMENT_RAMP_LOW_H,
    BRIDGE_ARCH_X,
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
    BRIDGE_DECK_EAST_RECESS,
    BRIDGE_DECK_EDGE_CEMENT_W,
    BRIDGE_DZ1,
    BRIDGE_DZ2,
    BRIDGE_EAST_SHIFT_END,
    BRIDGE_ENABLED_FASCIA_TEXT,
    BRIDGE_ENABLED_SPAN_CENTER,
    BRIDGE_ENABLED_SPAN_EAST_APPROACH,
    BRIDGE_ENABLED_SPAN_EAST_EXT,
    BRIDGE_ENABLED_SPAN_KH,
    BRIDGE_ENABLED_SPAN_WEST_APPROACH,
    BRIDGE_ENABLED_SUPPORTS,
    BRIDGE_FASCIA_PX_H,
    BRIDGE_FASCIA_PX_W,
    BRIDGE_FASCIA_TEXT,
    BRIDGE_PAR_W,
    BRIDGE_PIER_FILL_OFFSET,
    BRIDGE_PIER_GROUND_Z,
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
    BRIDGE_PILLAR_HW,
    BRIDGE_PILLAR_INNER_R,
    BRIDGE_PILLAR_OUTER_R,
    BRIDGE_PILLAR_OVERHANG,
    BRIDGE_PILLAR_PYR_H,
    BRIDGE_PILLAR_PYR_W,
    BRIDGE_PILLAR_SEAM_D,
    BRIDGE_PILLAR_SEAM_HW,
    BRIDGE_SEG_W,
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
    FASCIA_FONT,
    FLOOR_Z2,
    PIER2_X,
    PIER3_X,
    PIER4_X,
    PIER5_X,
    PIER6_ROTATION_DEG,
    PIER6_ROTATION_MARGIN,
    PIER6_X,
    WALK_X1,
    WALK_X2,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    Textures,
    deck_bot_z,
    deck_top_z,
    pier6_east_face_x_at_y,
    pier6_west_face_x_at_y,
)
from .geometry import (
    arch_fill,
    arch_plate_ring,
    arch_seg,
    arch_wall,
    box,
    brush_ent,
    east_y_shift,
    ent,
    pyramid,
    ramp_slab,
    shear_box_y,
    square_wall,
    taper_box_x,
    taper_box_y,
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
                if not any(sx1 < ox < sx2 for sx1, sx2 in enabled_spans):
                    continue
            new_entities.append(entdict)
    return filtered_brushes, new_entities


def _build_all():
    """Generate the full bridge geometry before section filtering."""
    BRUSHES = []
    ENTITIES = []
    DETAIL_BRUSHES = []
    _worldspawn_brushes = BRUSHES
    BRUSHES = DETAIL_BRUSHES

    BRIDGE_BLK_PIR_M = BRIDGE_PILLAR_HW + BRIDGE_BLK_HW + BRIDGE_BLK_PIER_CLEARANCE

    def _parapet_block_centers(x_start, x_end, n, west_margin=None, east_margin=None):
        """Return parapet-block centers using add_parapet_blocks() spacing."""
        mx0 = west_margin if west_margin is not None else BRIDGE_BLK_PIR_M
        mx1 = east_margin if east_margin is not None else BRIDGE_BLK_PIR_M
        x0 = x_start + mx0
        x1_lim = x_end - mx1
        return [x0 + (x1_lim - x0) * (k + 1) / (n + 1) for k in range(n)]

    CROSS_STRIP_X = sorted(
        _parapet_block_centers(
            BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], 3, west_margin=0, east_margin=0
        )
        + _parapet_block_centers(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
        + _parapet_block_centers(
            BRIDGE_ARCH_X[2], BRIDGE_ARCH_X[3], 3, west_margin=0, east_margin=0
        )
        + _parapet_block_centers(
            BRIDGE.x2, BRIDGE_ARCH_X[4], 3, west_margin=0, east_margin=0
        )
    )

    _dw_y1a = BRIDGE.y1
    _dw_y1b = BRIDGE.y1 + BRIDGE_PAR_W
    _dw_y1c = _dw_y1b + BRIDGE_DECK_EDGE_CEMENT_W
    _dw_y2c = BRIDGE.y2 - BRIDGE_PAR_W - BRIDGE_DECK_EDGE_CEMENT_W
    _dw_y2b = BRIDGE.y2 - BRIDGE_PAR_W
    _dw_y2a = BRIDGE.y2
    _DECK_BANDS = (
        (
            _dw_y1a,
            _dw_y1b,
            Textures.CEMENT,
            Textures.CEMENT,
            True,
            0,
            0,
        ),
        (
            _dw_y1b,
            _dw_y1c,
            Textures.DECK_EDGE,
            Textures.GABLE,
            True,
            0,
            0,
        ),
        (
            _dw_y1c,
            _dw_y2c,
            Textures.FLOOR1,
            Textures.GABLE,
            True,
            0,
            0,
        ),
        (
            _dw_y2c,
            _dw_y2b,
            Textures.DECK_EDGE,
            Textures.GABLE,
            False,
            0,
            0,
        ),
        (
            _dw_y2b,
            _dw_y2a,
            Textures.CEMENT,
            Textures.CEMENT,
            False,
            0,
            0,
        ),
    )
    _pier6_old_cutoff_x = PIER6_X - BRIDGE_PILLAR_HW

    def _pier6_west_pieces(
        x_start,
        ys1,
        ys2,
        z1,
        z2,
        tex,
        tt=None,
        tb=None,
        far=True,
        margin=0,
        margin2=None,
    ):
        """Return a box-plus-wedge run from x_start to Pier 6 across one Y band.

        `far` selects the rotated east or west face to follow. `margin` and
        `margin2` pull the wedge back from that target face at the band
        endpoints.
        """
        if margin2 is None:
            margin2 = margin
        pieces = [
            box(x_start, ys1, z1, _pier6_old_cutoff_x, ys2, z2, tex, tt=tt, tb=tb)
        ]
        face_x_at_y = pier6_east_face_x_at_y if far else pier6_west_face_x_at_y
        t1 = face_x_at_y(ys1) - margin
        t2 = face_x_at_y(ys2) - margin2
        pieces.append(
            taper_box_x(
                ys1,
                _pier6_old_cutoff_x,
                t1,
                z1,
                ys2,
                _pier6_old_cutoff_x,
                t2,
                z2,
                tex,
                tt=tt,
                tb=tb,
            )
        )
        return pieces

    for _ys1, _ys2, _tt, _tb, _far, _margin, _margin2 in _DECK_BANDS:
        BRUSHES.append(
            box(
                BRIDGE.x2,
                _ys1,
                BRIDGE_DZ1,
                PIER5_X,
                _ys2,
                BRIDGE_DZ2,
                Textures.STONE,
                tt=_tt,
                tb=_tb,
            )
        )
        BRUSHES.extend(
            _pier6_west_pieces(
                PIER5_X,
                _ys1,
                _ys2,
                BRIDGE_DZ1,
                BRIDGE_DZ2,
                Textures.STONE,
                tt=_tt,
                tb=_tb,
                far=_far,
                margin=_margin,
                margin2=_margin2,
            )
        )
    DECK_EAST_END_X = WORLD_X2_EXT - WALL_T - BRIDGE_DECK_EAST_RECESS
    PAR_EAST_END_X = WORLD_X2_EXT - WALL_T - ARCH_SLAB_W - BRIDGE_DECK_EAST_RECESS
    PIER6_EAST_X = PIER6_X + BRIDGE_PILLAR_HW
    _ws = _worldspawn_brushes

    for seg_x1, seg_x2 in [
        (PIER6_EAST_X, DECK_EAST_END_X),
    ]:
        for _ys1, _ys2, _tt, _tb, _far, _margin, _margin2 in _DECK_BANDS:
            BRUSHES.append(
                taper_box_y(
                    seg_x1,
                    _ys1 + east_y_shift(seg_x1),
                    _ys2 + east_y_shift(seg_x1),
                    BRIDGE_DZ1,
                    seg_x2,
                    _ys1 + east_y_shift(seg_x2),
                    _ys2 + east_y_shift(seg_x2),
                    BRIDGE_DZ2,
                    Textures.STONE,
                    tt=_tt,
                    tb=_tb,
                )
            )

    _p1, _p2, _p3 = BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]
    _n_center = max(1, round((_p3 - _p2) / BRIDGE_SEG_W))
    _step = (_p3 - _p2) / _n_center
    SPAN_BOUNDARIES = [BRIDGE.x1, _p1, _p2]
    SPAN_BOUNDARIES += [_p2 + i * _step for i in range(1, _n_center)]
    SPAN_BOUNDARIES += [_p3, BRIDGE.x2]

    def wall_tilt_z(cx, half_width):
        """Return the left and right top Z values using the local segment's slope."""
        bs = SPAN_BOUNDARIES
        cx_clamped = min(max(cx, bs[0]), bs[-1])
        for sx1, sx2 in zip(bs, bs[1:], strict=False):
            if sx1 <= cx_clamped <= sx2:
                z1, z2 = deck_top_z(sx1), deck_top_z(sx2)
                slope = (z2 - z1) / (sx2 - sx1) if sx2 != sx1 else 0.0
                t = (cx_clamped - sx1) / (sx2 - sx1) if sx2 != sx1 else 0.0
                zc = z1 + (z2 - z1) * t
                return zc - slope * half_width, zc + slope * half_width
        zc = deck_top_z(cx_clamped)
        return zc, zc

    def iter_bridge_span_segments():
        for sx1, sx2 in zip(SPAN_BOUNDARIES, SPAN_BOUNDARIES[1:], strict=False):
            db1, db2 = deck_bot_z(sx1), deck_bot_z(sx2)
            pb1, pb2 = deck_top_z(sx1), deck_top_z(sx2)
            pt1, pt2 = pb1 + BRIDGE.parapet_h, pb2 + BRIDGE.parapet_h
            yield sx1, sx2, db1, db2, pb1, pb2, pt1, pt2

    for sx1, sx2, db1, db2, pb1, pb2, _, _ in iter_bridge_span_segments():
        for _ys1, _ys2, _tt, _tb, _far, _margin, _margin2 in _DECK_BANDS:
            BRUSHES.append(
                ramp_slab(
                    sx1,
                    sx2,
                    _ys1,
                    _ys2,
                    db1,
                    db2,
                    pb1,
                    pb2,
                    Textures.STONE,
                    tt=_tt,
                    tb=_tb,
                )
            )

    _cross_strip_brushes = []
    for _cx in CROSS_STRIP_X:
        _strip_x1 = _cx - BRIDGE_DECK_CROSS_STRIP_HW
        _strip_x2 = _cx + BRIDGE_DECK_CROSS_STRIP_HW
        _strip_zt1 = deck_bot_z(_strip_x1) + BRIDGE_DECK_CROSS_STRIP_DROP
        _strip_zt2 = deck_bot_z(_strip_x2) + BRIDGE_DECK_CROSS_STRIP_DROP
        _cross_strip_brushes.append(
            ramp_slab(
                _strip_x1,
                _strip_x2,
                _dw_y1b,
                _dw_y2b,
                _strip_zt1 - BRIDGE_DECK_CROSS_STRIP_H,
                _strip_zt2 - BRIDGE_DECK_CROSS_STRIP_H,
                _strip_zt1,
                _strip_zt2,
                Textures.GABLE,
                tb_params="0 0 90 1 1",
            )
        )
    ENTITIES.append(brush_ent("func_illusionary", _cross_strip_brushes))

    BRUSHES.append(
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
    BRUSHES.extend(
        _pier6_west_pieces(
            PIER5_X,
            BRIDGE.y2 - BRIDGE_PAR_W,
            BRIDGE.y2,
            BRIDGE_DZ2,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
            far=False,
            margin=0,
            margin2=8,
        )
    )
    for _seg_x1, _seg_x2 in [
        (PIER6_EAST_X, PAR_EAST_END_X),
    ]:
        _ws.append(
            shear_box_y(
                _seg_x1,
                BRIDGE.y2 - BRIDGE_PAR_W,
                BRIDGE_DZ2,
                _seg_x2,
                BRIDGE.y2,
                BRIDGE_DZ2 + BRIDGE.parapet_h,
                east_y_shift(_seg_x1),
                east_y_shift(_seg_x2),
                Textures.CEMENT,
            )
        )
    _span4_west_mid = (BRIDGE.x2 + WALK_X1) / 2
    BRUSHES.append(
        box(
            BRIDGE.x2,
            BRIDGE.y1,
            BRIDGE_DZ2,
            _span4_west_mid,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    BRUSHES.extend(
        _pier6_west_pieces(
            PIER5_X,
            BRIDGE.y1,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    for _seg_x1, _seg_x2 in [
        (PIER6_EAST_X, PAR_EAST_END_X),
    ]:
        _ws.append(
            shear_box_y(
                _seg_x1,
                BRIDGE.y1,
                BRIDGE_DZ2,
                _seg_x2,
                BRIDGE.y1 + BRIDGE_PAR_W,
                BRIDGE_DZ2 + BRIDGE.parapet_h,
                east_y_shift(_seg_x1),
                east_y_shift(_seg_x2),
                Textures.CEMENT,
            )
        )

    for sx1, sx2, _, _, pb1, pb2, pt1, pt2 in iter_bridge_span_segments():
        BRUSHES.append(
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
        if not (sx1 < WALK_X2 and sx2 > WALK_X1):
            BRUSHES.append(
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

    def add_repeated_parapet_decorations(
        x_start,
        x_end,
        n,
        *,
        x_half_width,
        z_at_center,
        north_brush,
        south_brush,
        center_fn=lambda x: x,
        west_margin=None,
        east_margin=None,
        n_south=None,
        east_margin_n=None,
        y_shift_fn=None,
    ):
        """Place repeated north- and south-parapet decorations across a span."""
        n_s = n if n_south is None else n_south
        mx0 = west_margin if west_margin is not None else BRIDGE_BLK_PIR_M
        mx1 = east_margin if east_margin is not None else BRIDGE_BLK_PIR_M
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
                BRUSHES.append(brush)
        for cx, sy, bz in iter_positions(n_s, x1_s):
            if not (cx - x_half_width < WALK_X2 and cx + x_half_width > WALK_X1):
                brush = south_brush(cx, sy, bz)
                if brush is not None:
                    BRUSHES.append(brush)

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
        """Add evenly spaced parapet blocks across a bridge span."""

        def _block(cx, sy, y1_val, y2_val):
            """Return a parapet block aligned with the local deck slope."""
            zb1_raw, zb2_raw = wall_tilt_z(cx, BRIDGE_BLK_HW)
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

        add_repeated_parapet_decorations(
            x_start,
            x_end,
            n,
            x_half_width=BRIDGE_BLK_HW,
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
            west_margin=west_margin,
            east_margin=east_margin,
            n_south=n_south,
            east_margin_n=east_margin_n,
            y_shift_fn=y_shift_fn,
        )

    _span1_n = 3
    _span1_gap = (BRIDGE_ARCH_X[1] - BRIDGE_ARCH_X[0]) / (_span1_n + 1)
    assert _span1_gap >= BRIDGE_BLK_PIR_M, (
        f"Span 1 parapet-block gap ({_span1_gap:.1f}) is tighter than the minimum "
        f"pier clearance ({BRIDGE_BLK_PIR_M}) — reduce block count or shorten the "
        "even-margin spacing before it can safely use margin=0."
    )
    add_parapet_blocks(
        BRIDGE_ARCH_X[0],
        BRIDGE_ARCH_X[1],
        _span1_n,
        west_margin=0,
        east_margin=0,
    )
    add_parapet_blocks(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
    _span3_n = 3
    _span3_gap = (BRIDGE_ARCH_X[3] - BRIDGE_ARCH_X[2]) / (_span3_n + 1)
    assert _span3_gap >= BRIDGE_BLK_PIR_M, (
        f"Span 3 parapet-block gap ({_span3_gap:.1f}) is tighter than the minimum "
        f"pier clearance ({BRIDGE_BLK_PIR_M}) — reduce block count or shorten the "
        "even-margin spacing before it can safely use margin=0."
    )
    add_parapet_blocks(
        BRIDGE_ARCH_X[2],
        BRIDGE_ARCH_X[3],
        _span3_n,
        west_margin=0,
        east_margin=0,
    )
    _kh_span_n = 3
    _kh_span_gap = (BRIDGE_ARCH_X[4] - BRIDGE.x2) / (_kh_span_n + 1)
    assert _kh_span_gap >= BRIDGE_BLK_PIR_M, (
        f"KH span parapet-block gap ({_kh_span_gap:.1f}) is tighter than the "
        f"minimum pier clearance ({BRIDGE_BLK_PIR_M}) — reduce block count or "
        "shorten the even-margin spacing before it can safely use margin=0."
    )
    add_parapet_blocks(
        BRIDGE.x2,
        BRIDGE_ARCH_X[4],
        _kh_span_n,
        west_margin=0,
        east_margin=0,
        n_south=0,
        y_shift_fn=east_y_shift,
    )

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
        """Add raised parapet-face squares at the block positions."""
        add_repeated_parapet_decorations(
            x_start,
            x_end,
            n,
            x_half_width=BRIDGE_SQ_HW,
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
            center_fn=int,
            west_margin=west_margin,
            east_margin=east_margin,
            n_south=n_south,
            east_margin_n=east_margin_n,
            y_shift_fn=y_shift_fn,
        )

    def add_parapet_base_lights(
        x_start,
        x_end,
        n,
        west_margin=None,
        east_margin=None,
        n_south=None,
        east_margin_n=None,
        y_shift_fn=None,
    ):
        """Add parapet base lights at the decoration positions."""

        def _fixture(cx, sy, y_wall, y_dir):
            zb1_raw, zb2_raw = wall_tilt_z(cx, BRIDGE_BASE_LIGHT_HW)
            zb1 = round(zb1_raw) + BRIDGE_BASE_LIGHT_Z_LIFT
            zb2 = round(zb2_raw) + BRIDGE_BASE_LIGHT_Z_LIFT
            y1v = y_wall + sy
            y2v = y_wall + y_dir * BRIDGE_BASE_LIGHT_D + sy
            ylo, yhi = (y1v, y2v) if y1v <= y2v else (y2v, y1v)
            ENTITIES.append(
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

        add_repeated_parapet_decorations(
            x_start,
            x_end,
            n,
            x_half_width=BRIDGE_BASE_LIGHT_HW,
            z_at_center=lambda cx: int(deck_top_z(cx)),
            north_brush=lambda cx, sy, _bz: _fixture(
                cx, sy, BRIDGE.y2 - BRIDGE_PAR_W, -1
            ),
            south_brush=lambda cx, sy, _bz: _fixture(
                cx, sy, BRIDGE.y1 + BRIDGE_PAR_W, +1
            ),
            center_fn=int,
            west_margin=west_margin,
            east_margin=east_margin,
            n_south=n_south,
            east_margin_n=east_margin_n,
            y_shift_fn=y_shift_fn,
        )

    add_parapet_base_lights(
        BRIDGE_ARCH_X[0],
        BRIDGE_ARCH_X[1],
        _span1_n,
        west_margin=0,
        east_margin=0,
    )
    add_parapet_base_lights(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
    add_parapet_base_lights(
        BRIDGE_ARCH_X[2],
        BRIDGE_ARCH_X[3],
        _span3_n,
        west_margin=0,
        east_margin=0,
    )
    add_parapet_base_lights(
        BRIDGE.x2,
        BRIDGE_ARCH_X[4],
        _kh_span_n,
        west_margin=0,
        east_margin=0,
        n_south=0,
        y_shift_fn=east_y_shift,
    )

    add_parapet_squares(
        BRIDGE_ARCH_X[0],
        BRIDGE_ARCH_X[1],
        _span1_n,
        west_margin=0,
        east_margin=0,
    )
    add_parapet_squares(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
    add_parapet_squares(
        BRIDGE_ARCH_X[2],
        BRIDGE_ARCH_X[3],
        _span3_n,
        west_margin=0,
        east_margin=0,
    )
    add_parapet_squares(
        BRIDGE.x2,
        BRIDGE_ARCH_X[4],
        _kh_span_n,
        west_margin=0,
        east_margin=0,
        n_south=0,
        y_shift_fn=east_y_shift,
    )
    cx_wall_end = _span4_west_mid - BRIDGE_BLK_HW
    BRUSHES.append(
        box(
            cx_wall_end - BRIDGE_BLK_HW,
            BRIDGE.y1 - BRIDGE_BLK_OVH + BRIDGE_BLK_INSET,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            cx_wall_end + BRIDGE_BLK_HW,
            BRIDGE.y1 + BRIDGE_PAR_W - BRIDGE_BLK_INSET,
            BRIDGE_DZ2 + BRIDGE.parapet_h + BRIDGE_BLK_H,
            Textures.CEMENT,
        )
    )

    tube_ny1 = BRIDGE.y2 - BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
    tube_ny2 = tube_ny1 + BRIDGE_TUBE_HW * 2
    tube_sy1 = BRIDGE.y1 + BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
    tube_sy2 = tube_sy1 + BRIDGE_TUBE_HW * 2

    for tube_z_offset in [BRIDGE_TUBE_RISE, BRIDGE_TUBE_RISE + BRIDGE_TUBE_GAP]:
        for (
            span_x1,
            span_x2,
            _,
            _,
            _,
            _,
            tube_z1,
            tube_z2,
        ) in iter_bridge_span_segments():
            tube_z1 += tube_z_offset
            tube_z2 += tube_z_offset
            BRUSHES.append(
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
            if not (span_x1 < WALK_X2 and span_x2 > WALK_X1):
                BRUSHES.append(
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
        tube_base_z = BRIDGE_DZ2 + BRIDGE.parapet_h + tube_z_offset
        BRUSHES.append(
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
        BRUSHES.extend(
            _pier6_west_pieces(
                PIER5_X,
                tube_ny1,
                tube_ny2,
                tube_base_z,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
                far=False,
                margin=-4,
            )
        )
        for seg_x1, seg_x2 in [
            (PIER6_EAST_X, PAR_EAST_END_X),
        ]:
            BRUSHES.append(
                shear_box_y(
                    seg_x1,
                    tube_ny1,
                    tube_base_z,
                    seg_x2,
                    tube_ny2,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    east_y_shift(seg_x1),
                    east_y_shift(seg_x2),
                    Textures.RAIL,
                )
            )
        BRUSHES.append(
            box(
                BRIDGE.x2,
                tube_sy1,
                tube_base_z,
                _span4_west_mid,
                tube_sy2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        BRUSHES.extend(
            _pier6_west_pieces(
                PIER5_X,
                tube_sy1,
                tube_sy2,
                tube_base_z,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        for seg_x1, seg_x2 in [
            (PIER6_EAST_X, PAR_EAST_END_X),
        ]:
            BRUSHES.append(
                shear_box_y(
                    seg_x1,
                    tube_sy1,
                    tube_base_z,
                    seg_x2,
                    tube_sy2,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    east_y_shift(seg_x1),
                    east_y_shift(seg_x2),
                    Textures.RAIL,
                )
            )

    PIER5_LINTEL_GAP = 24
    if BRIDGE_ENABLED_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if (
                BRIDGE_ENABLED_SUPPORTS is not True
                and px not in BRIDGE_ENABLED_SUPPORTS
            ):
                continue
            _pier6_rot_bstart = len(BRUSHES) if px == PIER6_X else None
            _pier6_rot_estart = len(ENTITIES) if px == PIER6_X else None
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

            if px in (PIER2_X, PIER3_X) and BRIDGE_CENTER_SPAN_OFFSET != (
                0.0,
                0.0,
                0.0,
            ):
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

            pier5_lintel_gap = PIER5_LINTEL_GAP if px == PIER5_X else 0
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
            if px == max(BRIDGE_ARCH_X):
                sq_overhang = BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG - a_rin
                BRUSHES.extend(
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
                BRUSHES.extend(
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
                        base_cap_h=BRIDGE_ABUTMENT_RAMP_CAP_H
                        if px == min(BRIDGE_ARCH_X)
                        else BRIDGE_PILLAR_BASE_CAP_H,
                        base_cap_tex=Textures.CEMENT,
                        base_cap_ovh=BRIDGE_PILLAR_BASE_CAP_OVH,
                        recess=pier_recess,
                    )
                )

            if px in (
                PIER2_X,
                PIER3_X,
                PIER4_X,
                PIER5_X,
                PIER6_X,
            ) and BRIDGE_CENTER_SPAN_OFFSET != (
                0.0,
                0.0,
                0.0,
            ):
                footer_y1 = min(by1, -max_outer_radius)
                footer_y2 = max(by2, max_outer_radius)
                footer_depth = max(
                    BRIDGE_CENTER_SPAN_PIER_EMBED, BRIDGE_CENTER_SPAN_OFFSET[2]
                )
                BRUSHES.append(
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
            for face_x, protrude in (
                (x1, -BRIDGE_PIER_PLATE_D),
                (x2, BRIDGE_PIER_PLATE_D),
            ):
                if is_square_pier:
                    _tile_pitch = BRIDGE_PIER_PLATE_SIZE + BRIDGE_PIER_PLATE_GAP
                    BRUSHES.extend(
                        tile_face_plates(
                            face_x,
                            protrude,
                            by1 + _tile_pitch,
                            by2 - _tile_pitch,
                            pier_ceiling_z - BRIDGE_SQ_LINTEL_H,
                            pier_ceiling_z - BRIDGE_SQ_LINTEL_STONE_H,
                            Textures.CEMENT,
                            tile=BRIDGE_PIER_PLATE_SIZE,
                            gap=BRIDGE_PIER_PLATE_GAP,
                        )
                    )
                else:
                    BRUSHES.extend(
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

            pier_outer_y = by2 + BRIDGE_PILLAR_OVERHANG
            BRUSHES.append(
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

            BRUSHES.append(
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
            BRUSHES.append(
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
            BRUSHES.append(
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

            BRUSHES.append(
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
            BRUSHES.append(
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

            pier_top_z = int(pdeck) - BRIDGE_PIER_FILL_OFFSET
            if px != PIER6_X:
                BRUSHES.append(
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
            BRUSHES.append(
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

            cap_x1, cap_x2 = px - BRIDGE_PILLAR_PYR_W, px + BRIDGE_PILLAR_PYR_W
            north_cap_y1 = (
                by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG - BRIDGE_PILLAR_CAP_IN_OVH
            )
            north_cap_y2 = by2 + BRIDGE_PILLAR_CAP_OUT_OVH
            south_cap_y1 = by1 - BRIDGE_PILLAR_CAP_OUT_OVH
            south_cap_y2 = (
                by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG + BRIDGE_PILLAR_CAP_IN_OVH
            )
            BRUSHES.append(
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
            BRUSHES.append(
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
            BRUSHES.append(
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
            BRUSHES.append(
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
            torch_ys = [] if px in (PIER2_X, PIER3_X, PIER5_X) else [cy_n, cy_s]
            for torch_center_y in torch_ys:
                BRUSHES.append(
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
                BRUSHES.append(
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
                flame_z = int(
                    pyramid_apex_z + BRIDGE_TORCH_POST_H + BRIDGE_TORCH_CUP_H + 4
                )
                ENTITIES.append(torch_flame_only(px, torch_center_y, flame_z))
                fhb = box(
                    px - 16,
                    torch_center_y - 16,
                    flame_z,
                    px + 16,
                    torch_center_y + 16,
                    flame_z + 40,
                    Textures.SKY,
                )
                ENTITIES.append(brush_ent("trigger_hurt", [fhb], dmg="10"))

            if _pier6_rot_bstart is not None:
                BRUSHES[_pier6_rot_bstart:] = [
                    b.rotated_z(PIER6_ROTATION_DEG, px, py_shift)
                    for b in BRUSHES[_pier6_rot_bstart:]
                ]
                ENTITIES[_pier6_rot_estart:] = [
                    e.rotated_z(PIER6_ROTATION_DEG, px, py_shift)
                    for e in ENTITIES[_pier6_rot_estart:]
                ]
                BRUSHES.append(
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

            if px == min(BRIDGE_ARCH_X):
                ramp_top_west_z = (
                    pier_floor_z
                    + BRIDGE_ABUTMENT_RAMP_HIGH_H
                    + BRIDGE_ABUTMENT_RAMP_CAP_H
                )
                ramp_top_east_z = (
                    pier_floor_z
                    + BRIDGE_ABUTMENT_RAMP_LOW_H
                    + BRIDGE_ABUTMENT_RAMP_CAP_H
                )
                BRUSHES.append(
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
                    pier_top_z
                    - teleport_floor_z
                    - a_rin
                    - BRIDGE_TELEPORT_ARCH_CLEARANCE
                )
                abutment_teleport_brush = arch_fill(
                    x1 + BRIDGE_TELEPORT_ARCH_X1_OFFSET,
                    x1 + BRIDGE_TELEPORT_ARCH_X2_OFFSET,
                    0.0,
                    teleport_floor_z,
                    a_rin,
                    A_SEGS,
                    Textures.TELEPORT,
                    stilt_h=teleport_stilt_height,
                )
                abutment_teleport_dest_z = int(pdeck) + BRIDGE_TELEPORT_DEST_Z

                cem_rin = BRIDGE_ABUTMENT_CEMENT_RIN
                cem_floor_z = ramp_top_east_z
                cem_stilt_h = max(0, BRIDGE_ABUTMENT_CEMENT_MAX_H - cem_rin)
                cem_x1 = x2 - BRIDGE_ABUTMENT_CEMENT_X1_OFFSET
                cem_x2 = x2 - BRIDGE_ABUTMENT_CEMENT_X2_OFFSET
                BRUSHES.extend(
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

    for arch_x_start, arch_center_y in [
        (WORLD_X1 + WALL_T, 0.0),
        (
            WORLD_X2_EXT - WALL_T - ARCH_SLAB_W,
            BRIDGE_EAST_SHIFT_END,
        ),
    ]:
        arch_x1, arch_x2 = arch_x_start, arch_x_start + ARCH_SLAB_W
        arch_spring_z = BRIDGE_DZ2 + ARCH_STILT_H
        arch_post_width = ARCH_ROUT - ARCH_RIN
        BRUSHES.append(
            box(
                arch_x1,
                BRIDGE.y1 - BRIDGE_PILLAR_OVERHANG + arch_center_y,
                FLOOR_Z2,
                arch_x2,
                BRIDGE.y1 + arch_post_width + arch_center_y,
                arch_spring_z,
                Textures.PILLAR,
            )
        )
        BRUSHES.append(
            box(
                arch_x1,
                BRIDGE.y2 - arch_post_width + arch_center_y,
                FLOOR_Z2,
                arch_x2,
                BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG + arch_center_y,
                arch_spring_z,
                Textures.PILLAR,
            )
        )
        arch_segment_angle = 180.0 / A_SEGS
        for i in range(A_SEGS):
            BRUSHES.append(
                arch_seg(
                    arch_x1,
                    arch_x2,
                    arch_center_y,
                    float(arch_spring_z),
                    ARCH_RIN,
                    ARCH_ROUT + BRIDGE_PILLAR_OVERHANG,
                    i * arch_segment_angle,
                    (i + 1) * arch_segment_angle,
                    Textures.PILLAR,
                )
            )

    BRUSHES = _worldspawn_brushes
    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
        DETAIL_BRUSHES = []

    if "abutment_teleport_brush" in locals():
        ENTITIES.append(
            ent(
                "info_teleport_destination",
                targetname="dest_abutment_deck",
                origin=f"{min(BRIDGE_ARCH_X)} 0 {abutment_teleport_dest_z}",
                angle="0",
            )
        )
        ENTITIES.append(
            brush_ent(
                "trigger_teleport", abutment_teleport_brush, target="dest_abutment_deck"
            )
        )
        ENTITIES.append(brush_ent("func_illusionary", abutment_teleport_brush))

    _cols = 4
    _small_px = BRIDGE_FASCIA_PX_W - 1
    _n = len(BRIDGE_FASCIA_TEXT)
    _capital_pos = {
        i
        for i, ch in enumerate(BRIDGE_FASCIA_TEXT)
        if ch != " " and (i == 0 or BRIDGE_FASCIA_TEXT[i - 1] == " ")
    }
    _capital_pos_rev = {_n - 1 - i for i in _capital_pos}

    def _char_pw(i):
        return BRIDGE_FASCIA_PX_W if i in _capital_pos else _small_px

    total_w = sum((_cols + 1) * _char_pw(i) for i in range(_n)) - _char_pw(_n - 1)
    _fascia_cx = (PIER2_X + PIER3_X) // 2
    text_x0 = _fascia_cx - total_w // 2

    def render_text_fascia(
        text, x0, y_face, px_w, px_h, depth, tex, mirror=False, cap_pos=None
    ):
        """Return raised pixel-font brushes for text on a fascia face."""
        cols = 4
        rows = 6
        small_pw = px_w - 1
        small_ph = px_h - 1
        if cap_pos is None:
            cap_pos = _capital_pos

        brushes = []
        cx = x0
        for ci, ch in enumerate(text):
            cpw = px_w if ci in cap_pos else small_pw
            cph = px_h if ci in cap_pos else small_ph
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

    letter_brushes = (
        (
            render_text_fascia(
                BRIDGE_FASCIA_TEXT,
                x0=text_x0,
                y_face=BRIDGE.y1,
                px_w=BRIDGE_FASCIA_PX_W,
                px_h=BRIDGE_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
            )
            + render_text_fascia(
                BRIDGE_FASCIA_TEXT[::-1],
                x0=text_x0,
                y_face=BRIDGE.y2 + 1,
                px_w=BRIDGE_FASCIA_PX_W,
                px_h=BRIDGE_FASCIA_PX_H,
                depth=1,
                tex=Textures.RAIL,
                mirror=True,
                cap_pos=_capital_pos_rev,
            )
        )
        if BRIDGE_ENABLED_FASCIA_TEXT
        else []
    )
    if letter_brushes:
        ENTITIES.append(brush_ent("func_detail", letter_brushes))

    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))

    return BRUSHES, ENTITIES


def build():
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
    return BRUSHES, ENTITIES


def _shift_center_span(brushes, entities, enabled_names, offset):
    """Translate only the center span (plus any shared boundary piers it
    owns) by the configured offset; other enabled sections stay in place.

    ``BRIDGE_CENTER_SPAN_OFFSET`` is documented as "applied only to the
    center span" — other modules (west campus brick wall, dorm-adjacent
    entities, Knott walkway) independently read the same offset to align
    their own attachment points to the shifted span, so shifting every
    enabled section here would double-move those connections.

    Both extractions pass the same `enabled_names` to `_filter_sections` so
    the underlying acceptance windows are computed once and partition the
    bridge without overlap; only `extract_names` differs, so no brush is
    duplicated or dropped between the center-span and "other sections" sets.
    """
    dx, dy, dz = offset
    cs_brushes, cs_entities = _filter_sections(
        brushes, entities, enabled_names, extract_names=["center_span"]
    )
    other_names = [name for name in enabled_names if name != "center_span"]
    if other_names:
        other_brushes, other_entities = _filter_sections(
            brushes, entities, enabled_names, extract_names=other_names
        )
    else:
        other_brushes, other_entities = [], []
    cs_brushes = [b.translated(dx, dy, dz) for b in cs_brushes]
    cs_entities = [e.translated(dx, dy, dz) for e in cs_entities]
    return other_brushes + cs_brushes, other_entities + cs_entities


def _build_center_span(offset=(0.0, 0.0, 0.0)):
    """Return the center-span geometry, optionally translated by `offset`.

    This helper is separate from generate_map.py's module list and is meant
    for direct inspection or tests.
    """
    BRUSHES, ENTITIES = _build_all()
    BRUSHES, ENTITIES = _filter_sections(BRUSHES, ENTITIES, ["center_span"])
    dx, dy, dz = offset
    if (dx, dy, dz) != (0.0, 0.0, 0.0):
        BRUSHES = [b.translated(dx, dy, dz) for b in BRUSHES]
        ENTITIES = [e.translated(dx, dy, dz) for e in ENTITIES]
    return BRUSHES, ENTITIES
