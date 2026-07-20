"""
bridge — pedestrian bridge over Charles Street.

Bridge structure spanning Charles Street between west campus and Knott Hall:
  • Arched deck slab and span segments following the deck_top_z curve
  • Parapet walls with decorative blocks and raised squares
  • Arch ribs/voussoirs, pillars, piers, and support beams
  • Teleport arches at the abutments and vis hint brushes
  • The "LOYOLA UNIVERSITY MARYLAND" parapet fascia lettering

Kept separate from knott_terrain.py (Knott Hall terrain) and
knott_hall.py (building walls, floors, interior) so each module has
a single clear responsibility.
"""

import math

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
    BRIDGE_EAST_PIVOT_X,
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
    FLOOR_Z1,
    FLOOR_Z2,
    PIER2_X,
    PIER3_X,
    PIER4_X,
    PIER5_X,
    PIER6_NOTCH_LEN,
    PIER6_ROTATION_DEG,
    PIER6_ROTATION_MARGIN,
    PIER6_X,
    STREET_SURFACE_T,
    WALK_X1,
    WALK_X2,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    WORLD_Z2,
    Textures,
    deck_bot_z,
    deck_top_z,
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
    shear_pyramid_y,
    square_wall,
    taper_box_y,
    tile_face_plates,
    torch_flame_only,
)


def _section_x_ranges():
    """Return the {section_name: (x1, x2)} pier-to-pier boundaries used to
    attribute geometry to a bridge section (see _filter_sections)."""
    return {
        "west_approach": (BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1]),
        "center_span": (BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]),
        "east_approach": (BRIDGE_ARCH_X[2], BRIDGE_ARCH_X[3]),
        "kh_span": (BRIDGE_ARCH_X[3], BRIDGE_ARCH_X[4]),
        "east_ext": (BRIDGE_ARCH_X[4], BRIDGE_ARCH_X[5]),
    }


# West-to-east chain order, matching _section_x_ranges' pier-to-pier layout.
# Used to resolve which of two adjacent sections owns their shared boundary
# pier (see _boundary_owner/_section_accept_ranges) so every pier is built by
# exactly one section — never duplicated, never dropped — however the
# individual section flags are combined.
_SECTION_ORDER = [
    "west_approach",
    "center_span",
    "east_approach",
    "kh_span",
    "east_ext",
]


def _boundary_owner(left_name, right_name, enabled_names):
    """Return which of two adjacent sections sharing an internal boundary
    pier should build it. center_span is always preferred (it's the anchor
    every other section connects to); for boundaries not touching
    center_span, the section closer to center_span (the left one, since our
    chain only extends outward to the east past center_span) is preferred.
    Falls back to whichever of the two IS enabled if the preferred owner
    isn't, so a shared pier is never silently dropped just because its
    usual owner is currently disabled."""
    if right_name == "center_span":
        preferred, fallback = right_name, left_name
    elif left_name == "center_span":
        preferred, fallback = left_name, right_name
    else:
        preferred, fallback = left_name, right_name
    return preferred if preferred in enabled_names else fallback


def _section_accept_ranges(enabled_names, margin):
    """Return {section_name: (x1, x2)} acceptance windows, one per section in
    _SECTION_ORDER, each extended by `margin` only on the sides where that
    section owns the bounding pier (per _boundary_owner) and pulled back by
    `margin` on sides owned by a neighbor. This makes the windows an exact,
    non-overlapping partition of the bridge's X extent — every pier
    (including internal boundary piers shared between two sections) is
    claimed by exactly one currently-enabled section, so filtering never
    duplicates or drops pier geometry, whichever sections are enabled."""
    section_piers = _section_x_ranges()
    ranges = {}
    for idx, name in enumerate(_SECTION_ORDER):
        px1, px2 = section_piers[name]
        if idx == 0:
            ax1 = px1 - margin  # outer terminus (Pier 1) — always owned
        else:
            owner = _boundary_owner(_SECTION_ORDER[idx - 1], name, enabled_names)
            # Owned: extend outward by margin to capture the full pier
            # brush width. Not owned: use the raw pier X (no pull-back) —
            # this still excludes the neighbor's pier brush (which extends
            # margin past px1 into *this* section) while leaving the full
            # deck/parapet run, which starts exactly at px1, untouched.
            ax1 = px1 - margin if owner == name else px1
        if idx == len(_SECTION_ORDER) - 1:
            ax2 = px2 + margin  # outer terminus (last pier) — always owned
        else:
            owner = _boundary_owner(name, _SECTION_ORDER[idx + 1], enabled_names)
            ax2 = px2 + margin if owner == name else px2
        ranges[name] = (ax1, ax2)
    return ranges


def _filter_sections(brushes, entities, enabled_names, extract_names=None):
    """Keep only geometry overlapping one of the named sections' pier-to-pier
    spans (each with a small margin to include the bounding piers — see
    _section_accept_ranges). Catches brushes already wrapped in func_detail
    entities (the bridge superstructure) as well as worldspawn brushes (e.g.
    hint brushes, which are dropped entirely — they're only useful when the
    full bridge exists).

    `enabled_names` is the full set of currently-enabled sections, used to
    resolve shared-boundary-pier ownership consistently even when only one
    section's geometry is being extracted (see `extract_names`).
    `extract_names`, if given, restricts the returned geometry to this
    subset of `enabled_names` — e.g. _shift_center_span() extracts one
    section at a time (to translate it independently) while still passing
    the full enabled_names so ownership resolves the same way it would for
    a single combined call. Defaults to `enabled_names` (i.e. return
    everything enabled).
    """
    if extract_names is None:
        extract_names = enabled_names
    # Extra allowance beyond the normal pillar footprint: Pier 6's below/
    # above-deck assembly is rotated PIER6_ROTATION_DEG about its own
    # center (see the per-pier loop), which pushes some of its brushes'
    # X-extent well past a straight pillar's — without this, full-
    # containment below would silently drop those brushes/entities out of
    # every section (they'd fit in none), which read as missing/invisible
    # geometry in-game. Piers are spaced hundreds of units apart, so this
    # extra margin is always far short of encroaching on a neighbor.
    margin = BRIDGE_PILLAR_HW + BRIDGE_PILLAR_OVERHANG + PIER6_ROTATION_MARGIN
    accept_ranges = _section_accept_ranges(enabled_names, margin)
    enabled_spans = [accept_ranges[name] for name in extract_names]

    def _in_any_span(b):
        xs = [p[0] for f in b.faces for p in (f.p1, f.p2, f.p3)]
        # Full containment (not just partial overlap) — otherwise long
        # adjacent-span deck/parapet segments that merely touch a pier
        # boundary (e.g. x=[-1246,-525]) would incorrectly pass.
        bx1, bx2 = min(xs), max(xs)
        return any(bx1 >= sx1 and bx2 <= sx2 for sx1, sx2 in enabled_spans)

    def _is_hint(b):
        return all(f.tex == Textures.HINT for f in b.faces)

    filtered_brushes = [b for b in brushes if _in_any_span(b) and not _is_hint(b)]
    new_entities = []
    for entdict in entities:
        if entdict.brushes:
            # Brush entity (func_detail, trigger_teleport, func_illusionary,
            # etc.) — keep only brushes overlapping an enabled span; drop
            # the whole entity if nothing survives (e.g. the west-abutment
            # teleport arch's trigger/illusionary brushes, which sit at
            # x≈-1265..-1281, well outside any enabled span).
            kept = [b for b in entdict.brushes if _in_any_span(b)]
            if kept:
                new_entities.append(
                    brush_ent(entdict.classname, kept, **entdict.fields)
                )
        else:
            # Point entity — keep only if its origin falls within an
            # enabled span (e.g. drop info_teleport_destination at the
            # west abutment when that section isn't enabled).
            origin = entdict.fields.get("origin")
            if origin is not None:
                ox = float(origin.split()[0])
                if not any(sx1 < ox < sx2 for sx1, sx2 in enabled_spans):
                    continue
            new_entities.append(entdict)
    return filtered_brushes, new_entities


def _build_all():
    """Generate every bridge section's geometry, unfiltered. Callers (build(),
    build_center_span()) slice this down to whichever section(s) they want via
    _filter_sections()."""
    BRUSHES = []
    ENTITIES = []
    # Bridge superstructure (parapets, railings, arch voussoirs, teleport arches) is
    # collected into a func_detail entity below instead of worldspawn.  None of it
    # seals the level (the world shell does), so keeping it out of the BSP avoids the
    # extra portals that make full vis slow.  Appends below are temporarily redirected
    # to DETAIL_BRUSHES, then worldspawn routing is restored after the teleport arches.
    DETAIL_BRUSHES = []
    _worldspawn_brushes = BRUSHES
    BRUSHES = DETAIL_BRUSHES

    # ── Deck-bottom cross strips — one under each parapet block ───────────────────
    # A separate thin, non-solid func_illusionary decal per block position: same
    # GABLE (wood) texture as the longitudinal underside strip, rotated 90° so
    # its grain runs perpendicular to the bridge's length, hung
    # BRIDGE_DECK_CROSS_STRIP_DROP units below the structural deck-bottom face
    # so it reads as flush from the ground without z-fighting against the
    # structural slab. Built this way (a separate overlay, not by splitting the
    # structural deck slab in X) because splitting previously-unified flat deck
    # spans caused qbsp "WARNING 12: New portal was clipped away" and actual
    # missing polygons in-game — see the note by iter_bridge_span_segments()
    # below on why those spans are kept as single unsplit segments.
    # Positions are computed here (independent of the actual block-placement
    # closures defined later) purely from each span's block-count/margin.
    BRIDGE_BLK_PIR_M = (
        BRIDGE_PILLAR_HW + BRIDGE_BLK_HW + BRIDGE_BLK_PIER_CLEARANCE
    )  # clearance from pier centre to block centre

    def _parapet_block_centers(x_start, x_end, n, west_margin=None, east_margin=None):
        """Same spacing formula add_parapet_blocks uses for its north-side
        blocks (west_margin/east_margin default to the pier-clearance margin,
        BRIDGE_BLK_PIR_M, same as add_repeated_parapet_decorations below)."""
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
            BRIDGE.x2, BRIDGE_ARCH_X[4], 3, west_margin=BRIDGE_BLK_HW + 8
        )
    )

    # ── Bridge deck slab — the walkable surface across the whole span ─────────────
    # Straight section: arch terminus → easternmost pier
    # Split across Y into cement-margin / wood / cement-margin strips so a
    # small strip of cement remains visible on each side of the wood-textured
    # underside instead of the whole underside being wood.
    # The parapet walls sit ON TOP of the deck slab, spanning BRIDGE_PAR_W in
    # from each outer edge — so a texture split at the raw edge (BRIDGE.y1/y2)
    # is entirely hidden beneath the parapet's footprint and never visible to
    # a player. The visible edge-accent strip is placed just inside the
    # parapet's inner face instead, where the walkable surface actually
    # begins.
    _dw_y1a = BRIDGE.y1
    _dw_y1b = BRIDGE.y1 + BRIDGE_PAR_W  # inner face of south parapet
    _dw_y1c = _dw_y1b + BRIDGE_DECK_EDGE_CEMENT_W  # inner edge of visible strip
    _dw_y2c = BRIDGE.y2 - BRIDGE_PAR_W - BRIDGE_DECK_EDGE_CEMENT_W
    _dw_y2b = BRIDGE.y2 - BRIDGE_PAR_W  # inner face of north parapet
    _dw_y2a = BRIDGE.y2
    _DECK_BANDS = (
        (_dw_y1a, _dw_y1b, Textures.CEMENT, Textures.CEMENT),  # hidden under parapet
        (_dw_y1b, _dw_y1c, Textures.DECK_EDGE, Textures.GABLE),  # visible edge strip
        (_dw_y1c, _dw_y2c, Textures.FLOOR1, Textures.GABLE),  # visible walk centre
        (_dw_y2c, _dw_y2b, Textures.DECK_EDGE, Textures.GABLE),  # visible edge strip
        (_dw_y2b, _dw_y2a, Textures.CEMENT, Textures.CEMENT),  # hidden under parapet
    )
    for _ys1, _ys2, _tt, _tb in _DECK_BANDS:
        for _seg_x1, _seg_x2 in [(BRIDGE.x2, PIER5_X), (PIER5_X, BRIDGE_EAST_PIVOT_X)]:
            BRUSHES.append(
                box(
                    _seg_x1,
                    _ys1,
                    BRIDGE_DZ1,
                    _seg_x2,
                    _ys2,
                    BRIDGE_DZ2,
                    Textures.STONE,
                    tt=_tt,  # deck walking surface — thin edge strip along each side
                    tb=_tb,  # deck underside — wood (GABLE) with a cement edge margin
                )
            )
    # Angled section: easternmost pier → 1 unit inside the east arch face.
    # Split at BRIDGE_ARCH_X[5] (new mid-span pier) to keep brush sizes manageable
    # and give qbsp extra BSP splits in the extended east section.
    DECK_EAST_END_X = WORLD_X2_EXT - WALL_T - BRIDGE_DECK_EAST_RECESS
    PAR_EAST_END_X = WORLD_X2_EXT - WALL_T - ARCH_SLAB_W - BRIDGE_DECK_EAST_RECESS
    MID_PIER_X = BRIDGE_ARCH_X[5]  # x=2800 mid-span pier
    # Angled east section parapets go to worldspawn (not func_detail) to ensure
    # ericw-tools qbsp generates draw surfaces for the outer (Y-facing) faces.
    _ws = _worldspawn_brushes

    # Triangular deck notch around rotated Pier 6: the deck's north edge
    # recedes from MID_PIER_X (full width) to NOTCH_END_X (max recede), at
    # the same angle as PIER6_ROTATION_DEG so the cut visually lines up
    # with the rotated pier. There is no "recovering" leg back to full
    # width — past Pier 6 the deck has never visibly extended further than
    # this same short stub, so it just continues at the receded width.
    # Only the "north family" band boundaries (y2c/y2b/y2a) recede; the
    # south side (y1a/y1b/y1c) is untouched.
    NOTCH_END_X = MID_PIER_X + PIER6_NOTCH_LEN
    NOTCH_DROP = PIER6_NOTCH_LEN * abs(math.tan(math.radians(PIER6_ROTATION_DEG)))
    _NORTH_YS = {_dw_y2c, _dw_y2b, _dw_y2a}

    def _notch_drop(ys):
        return NOTCH_DROP if ys in _NORTH_YS else 0.0

    for _ys1, _ys2, _tt, _tb in _DECK_BANDS:
        # Receding leg: MID_PIER_X (full width) → NOTCH_END_X (max recede).
        # Only the bands fully within the receded north-family region
        # (both boundaries in _NORTH_YS) are built here — the south/centre
        # bands (which straddle or sit entirely outside the notch) are
        # skipped in this short stub: the rotated Pier 6 body already
        # occupies that footprint, so building them there just produced a
        # redundant sliver of overlapping geometry (the visible wedge
        # artifact at the pier).
        if _ys1 not in _NORTH_YS:
            continue
        BRUSHES.append(
            taper_box_y(
                MID_PIER_X,
                _ys1 + east_y_shift(MID_PIER_X),
                _ys2 + east_y_shift(MID_PIER_X),
                BRIDGE_DZ1,
                NOTCH_END_X,
                _ys1 + east_y_shift(NOTCH_END_X) - _notch_drop(_ys1),
                _ys2 + east_y_shift(NOTCH_END_X) - _notch_drop(_ys2),
                BRIDGE_DZ2,
                Textures.STONE,
                tt=_tt,
                tb=_tb,
            )
        )

    for seg_x1, seg_x2 in [
        (NOTCH_END_X, DECK_EAST_END_X),
    ]:
        for _ys1, _ys2, _tt, _tb in _DECK_BANDS:
            # Stays at the receded (max-recede) width the whole way — no
            # taper back to full width (see notch comment above).
            BRUSHES.append(
                taper_box_y(
                    seg_x1,
                    _ys1 + east_y_shift(seg_x1) - _notch_drop(_ys1),
                    _ys2 + east_y_shift(seg_x1) - _notch_drop(_ys2),
                    BRIDGE_DZ1,
                    seg_x2,
                    _ys1 + east_y_shift(seg_x2) - _notch_drop(_ys1),
                    _ys2 + east_y_shift(seg_x2) - _notch_drop(_ys2),
                    BRIDGE_DZ2,
                    Textures.STONE,
                    tt=_tt,  # deck walking surface — thin edge strip along each side
                    tb=_tb,  # deck underside — wood (GABLE) with a cement edge margin
                )
            )

    # Pier 6's north "fill gap between pier top and deck surface" skirt is
    # intentionally omitted here (unlike every other pier): with the deck
    # notch removed back to a single permanently-receded leg, the deck's
    # north edge simply stays pulled back for good past MID_PIER_X, so
    # there's open space there rather than a seam needing a filler patch.
    # Adding a skirt/taper of any size in this region (both the constant-
    # offset and exact-rotated-line versions were tried) only produced a
    # visible, wrong-shaped wedge — bigger skirts made it worse, so no
    # skirt at all is closest to correct.

    # Span-segment boundaries shared by the wall (iter_bridge_span_segments)
    # and the parapet decorations below, so decorative blocks always sit
    # exactly parallel to whichever single wall segment they rest on.
    _p1, _p2, _p3 = BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]
    _n_center = max(1, round((_p3 - _p2) / BRIDGE_SEG_W))
    _step = (_p3 - _p2) / _n_center
    SPAN_BOUNDARIES = [BRIDGE.x1, _p1, _p2]
    SPAN_BOUNDARIES += [_p2 + i * _step for i in range(1, _n_center)]
    SPAN_BOUNDARIES += [_p3, BRIDGE.x2]

    def wall_tilt_z(cx, half_width):
        """Z at cx-half_width and cx+half_width, extrapolated from the slope
        of the SINGLE wall segment containing cx (not sampled independently
        at each edge). Near a segment boundary (e.g. the shallow crest of the
        centre span), a block wide enough to straddle two segments would
        otherwise average in the far segment's different slope and end up
        visibly tilted at an angle that doesn't match the segment it's
        actually resting on — this keeps the block exactly parallel to that
        one segment instead."""
        bs = SPAN_BOUNDARIES
        cx_clamped = min(max(cx, bs[0]), bs[-1])
        for sx1, sx2 in zip(bs, bs[1:]):
            if sx1 <= cx_clamped <= sx2:
                z1, z2 = deck_top_z(sx1), deck_top_z(sx2)
                slope = (z2 - z1) / (sx2 - sx1) if sx2 != sx1 else 0.0
                t = (cx_clamped - sx1) / (sx2 - sx1) if sx2 != sx1 else 0.0
                zc = z1 + (z2 - z1) * t
                return zc - slope * half_width, zc + slope * half_width
        zc = deck_top_z(cx_clamped)  # unreachable fallback
        return zc, zc

    def iter_bridge_span_segments():
        # Only the curved centre span (PIER2..PIER3) is faceted; the flat west
        # approach and the two straight approach spans are emitted as single
        # segments so their collinear boundaries don't spawn redundant coplanar
        # portals (qbsp WARNING 12 — see the east-section note below).
        for sx1, sx2 in zip(SPAN_BOUNDARIES, SPAN_BOUNDARIES[1:]):
            db1, db2 = deck_bot_z(sx1), deck_bot_z(sx2)
            pb1, pb2 = deck_top_z(sx1), deck_top_z(sx2)
            pt1, pt2 = pb1 + BRIDGE.parapet_h, pb2 + BRIDGE.parapet_h
            yield sx1, sx2, db1, db2, pb1, pb2, pt1, pt2

    # Bridge span deck segments (arched profile following deck_top_z / deck_bot_z)
    for sx1, sx2, db1, db2, pb1, pb2, _, _ in iter_bridge_span_segments():
        for _ys1, _ys2, _tt, _tb in _DECK_BANDS:
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
                    tt=_tt,  # deck walking surface — thin edge strip along each side
                    tb=_tb,  # deck underside — wood (GABLE) with a cement edge margin
                )
            )

    # Cross-strip decals (see note above): one func_illusionary brush per
    # CROSS_STRIP_X position, spanning the same Y-extent as the longitudinal
    # wood band (_dw_y1b.._dw_y2b — stopping short of the parapet-hidden
    # edges, same as the rest of the underside), hung BRIDGE_DECK_CROSS_STRIP_DROP
    # units below the structural deck bottom at that X so it reads as flush without
    # being exactly coplanar with (and z-fighting against) the structural slab.
    _cross_strip_brushes = []
    for _cx in CROSS_STRIP_X:
        _strip_z2 = deck_bot_z(_cx) - BRIDGE_DECK_CROSS_STRIP_DROP
        _strip_z1 = _strip_z2 - BRIDGE_DECK_CROSS_STRIP_H
        _cross_strip_brushes.append(
            box(
                _cx - BRIDGE_DECK_CROSS_STRIP_HW,
                _dw_y1b,
                _strip_z1,
                _cx + BRIDGE_DECK_CROSS_STRIP_HW,
                _dw_y2b,
                _strip_z2,
                Textures.GABLE,
                tb_params="0 0 90 1 1",
            )
        )
    ENTITIES.append(brush_ent("func_illusionary", _cross_strip_brushes))

    # ── Parapet walls — west flat approach removed; east flat stub only ───────────
    # North east parapet: straight BRIDGE.x2→Pier5→pier6, then angled pier6→world
    # wall. Split at PIER5_X too (not just MID_PIER_X/PIER6_X below) since Pier 5
    # has its own flanking wall geometry at that X — an unsplit brush spanning
    # straight through it causes the same qbsp invisible-wall mis-clip described
    # below for Pier 6.
    for _seg_x1, _seg_x2 in [(BRIDGE.x2, PIER5_X), (PIER5_X, BRIDGE_EAST_PIVOT_X)]:
        BRUSHES.append(
            box(
                _seg_x1,
                BRIDGE.y2 - BRIDGE_PAR_W,
                BRIDGE_DZ2,
                _seg_x2,
                BRIDGE.y2,
                BRIDGE_DZ2 + BRIDGE.parapet_h,
                Textures.CEMENT,
            )
        )
    # Angled piece split at MID_PIER_X (=PIER6_X): Pier 6's own flanking wall
    # brushes (built by the general pier loop) occupy this same Y-range at
    # that X, so a single unsplit brush spanning straight through the pier
    # fully overlaps the pier's solid geometry there — qbsp then mis-clips
    # portals across that overlap, producing invisible-but-solid walls. The
    # deck bands above already split at MID_PIER_X for the same reason; this
    # matches that. The railing is further omitted from MID_PIER_X to
    # NOTCH_END_X to match the deck's triangular notch there (open railing
    # gap over the receded deck edge, prep for a future branch span).
    for _seg_x1, _seg_x2 in [
        (NOTCH_END_X, PAR_EAST_END_X),
    ]:
        _ws.append(
            shear_box_y(
                _seg_x1,
                BRIDGE.y2 - BRIDGE_PAR_W - NOTCH_DROP,
                BRIDGE_DZ2,
                _seg_x2,
                BRIDGE.y2 - NOTCH_DROP,
                BRIDGE_DZ2 + BRIDGE.parapet_h,
                east_y_shift(_seg_x1),
                east_y_shift(_seg_x2),
                Textures.CEMENT,
            )
        )
    # South east — gaps at WALK_X1..WALK_X2 and east_walk_x1..east_walk_x2 for walkway/accessible-walkway connections
    # West piece — wall stays attached to Pier 4, extending east to the
    # midpoint; opening continues from the midpoint to WALK_X1 for steps.
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
    # East piece (WALK_X2→Pier5) removed — south wall of span 4's east half
    # is now fully open for steps down to the ground.
    # Span 5 (Pier5→MID_PIER_X) straight piece — mirrors the north east
    # parapet's (PIER5_X, BRIDGE_EAST_PIVOT_X) segment; this side was
    # previously missing, leaving span 5's south edge with no deck wall.
    BRUSHES.append(
        box(
            PIER5_X,
            BRIDGE.y1,
            BRIDGE_DZ2,
            MID_PIER_X,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    # Angled piece split at MID_PIER_X (=PIER6_X) — same overlap reasoning as
    # the north east parapet above.
    for _seg_x1, _seg_x2 in [
        (MID_PIER_X, PAR_EAST_END_X),
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
        # North parapet
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
        # South parapet — omit any segment that overlaps the walkway gap (X=WALK_X1..WALK_X2)
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

    # ── Parapet cement blocks (decorative posts atop parapet walls) ───────────────
    # BRIDGE_BLK_PIR_M already computed above (deck-bottom cross-strip section)
    # using this same formula.

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
        """Place repeated decorations along the north/south parapets of a span."""
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
        """Add evenly-spaced cement blocks atop N and S parapets in a bridge span."""

        def _block(cx, sy, y1_val, y2_val):
            """Tilted block following the arch — ramp_slab when sloped, box when flat.
            Uses wall_tilt_z (the containing wall segment's own slope,
            extrapolated from the block's centre) instead of independently
            sampling deck_top_z at the block's own edges, so the block is
            always exactly parallel to the wall segment it rests on.
            Genuinely near-flat slopes (< 1 unit of total rise across the
            block) are snapped flat rather than rounded independently at
            each edge — independently rounding two close-but-different
            floats can otherwise manufacture a full 1-unit apparent tilt
            out of a true sub-unit slope (e.g. near the shallow crest of
            the centre span), which is exactly what reads as the block
            being tilted at the wrong angle relative to the wall."""
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
            north_brush=lambda cx, sy, bz: _block(
                cx,
                sy,
                BRIDGE.y2 - BRIDGE_PAR_W + BRIDGE_BLK_INSET,
                BRIDGE.y2 + BRIDGE_BLK_OVH - BRIDGE_BLK_INSET,
            ),
            south_brush=lambda cx, sy, bz: _block(
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

    # Western span (BRIDGE.x1 → BRIDGE_ARCH_X[0]): no blocks — open span
    # Span 2 (BRIDGE_ARCH_X[0] → BRIDGE_ARCH_X[1]): eastern span 1, 3 blocks.
    # Margin set to 0 (rather than the default fixed BRIDGE_BLK_PIR_M pier
    # clearance margin) so the n+1 gaps — pier-to-block AND block-to-block —
    # come out perfectly even, dividing the full pier-to-pier span equally.
    # The default clearance margin instead reserved extra pier-side space,
    # making the pier-to-block gaps visibly larger than the inter-block gaps
    # once this span was independently lengthened (BRIDGE_WEST_OUTER_PIER_SPAN).
    # Safe as long as the resulting gap exceeds the minimum pier clearance
    # (BRIDGE_BLK_PIR_M); true here (span/(n+1) = 230 >> ~73-unit clearance).
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
    # Middle span (BRIDGE_ARCH_X[1] → BRIDGE_ARCH_X[2]): 4 blocks — corrected
    # after re-checking ref/bridge08.png; the earlier 5th block (assumed to sit
    # in a foliage-obscured gap) was a miscount.
    add_parapet_blocks(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
    # Eastern span 2 (BRIDGE_ARCH_X[2] → BRIDGE_ARCH_X[3]): 3 blocks. Same
    # even-margin treatment as span 1 above — margin=0 so pier-to-block and
    # block-to-block gaps come out equal now that this span
    # (BRIDGE_OUTER_PIER_SPAN) was lengthened to match the west span.
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
    # East flat span: west sub-span (BRIDGE.x2→BRIDGE_ARCH_X[4]) gets 3 north blocks; east sub-span open (matches ref)
    add_parapet_blocks(
        BRIDGE.x2,
        BRIDGE_ARCH_X[4],
        3,
        west_margin=BRIDGE_BLK_HW + 8,
        n_south=0,
        y_shift_fn=east_y_shift,
    )

    # ── Decorative squares on parapet outer faces (one per block position) ────────
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

    # ── Base lights on parapet inner faces (one per block position) ──────────────
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
        """Add a small wall-light fixture + light entity at the base of each
        parapet-block wall segment, on the INSIDE (walkway-facing) face, right
        above the deck floor — same X positions as the blocks above, using
        wall_tilt_z (not deck_top_z + parapet_h) so the fixture sits flush
        with the wall's own base rather than at block height."""

        def _fixture(cx, sy, y_wall, y_dir):
            zb1_raw, zb2_raw = wall_tilt_z(cx, BRIDGE_BASE_LIGHT_HW)
            # Round each edge independently (rather than forcing a flat
            # average) so the fixture picks up even a slight tilt from the
            # curved centre span — it should rotate with the wall it's
            # mounted on, not just sit dead level everywhere.
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
            # Fixture geometry (brush) is dropped for now — only the light
            # entity itself is kept — per explicit request to pause the
            # visible fixture while iterating on texture/placement later.
            return None

        add_repeated_parapet_decorations(
            x_start,
            x_end,
            n,
            x_half_width=BRIDGE_BASE_LIGHT_HW,
            z_at_center=lambda cx: int(deck_top_z(cx)),
            north_brush=lambda cx, sy, bz: _fixture(
                cx, sy, BRIDGE.y2 - BRIDGE_PAR_W, -1
            ),
            south_brush=lambda cx, sy, bz: _fixture(
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
        3,
        west_margin=BRIDGE_BLK_HW + 8,
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
        3,
        west_margin=BRIDGE_BLK_HW + 8,
        n_south=0,
        y_shift_fn=east_y_shift,
    )
    # South east of walkway: corner blocks only at each side of the opening
    # East end cap: one corner block at the end of the kept west wall
    # segment (midpoint, X≈1666), capping the opening's west edge.
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
    # East opening (midpoint→Pier5) has no corner block — wall/blocks removed
    # there for the steps down to the ground.

    # ── Parapet handrail tubes (two 4×4 rods stacked, through parapet blocks/pillars) ─
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
        # East flat section — straight BRIDGE.x2→pier, angled pier→world wall
        # Split at MID_PIER_X to keep shear brushes short and aid BSP splitting.
        tube_base_z = BRIDGE_DZ2 + BRIDGE.parapet_h + tube_z_offset
        # North tube: straight (split at Pier5 too — see the parapet wall
        # comment above for why) then angled segment(s)
        for _seg_x1, _seg_x2 in [(BRIDGE.x2, PIER5_X), (PIER5_X, BRIDGE_EAST_PIVOT_X)]:
            BRUSHES.append(
                box(
                    _seg_x1,
                    tube_ny1,
                    tube_base_z,
                    _seg_x2,
                    tube_ny2,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )
        for seg_x1, seg_x2 in [
            (MID_PIER_X, PAR_EAST_END_X),
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
        # South tube west piece — matches the wall: stays attached to Pier 4,
        # extending east only to the midpoint.
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
        # South tube east piece (WALK_X2→Pier5) removed — no railing on the
        # open east half of span 4.
        # Span 5 (Pier5→MID_PIER_X) straight piece — mirrors the north
        # tube's (PIER5_X, BRIDGE_EAST_PIVOT_X) segment; matches the deck
        # wall fix above so span 5's south railing isn't floating with no
        # wall beneath it.
        BRUSHES.append(
            box(
                PIER5_X,
                tube_sy1,
                tube_base_z,
                MID_PIER_X,
                tube_sy2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        for seg_x1, seg_x2 in [
            (MID_PIER_X, PAR_EAST_END_X),
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

    # ── Pillar posts (stone piers with arches) ───────────────────────────────────
    # Each pillar position now features a narrow arched pier supporting the deck.
    # Arch openings span most of the bridge N-S width (BRIDGE.y2=113, bridge=226 units)
    # rin = half-width of clear opening; rout = outer radius of arch ring
    # Pier 5's arch crown is nudged slightly lower than a full-height arch would
    # otherwise land, so the opening doesn't feel like it's floating right up
    # against the deck underside.
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
            pdeck = deck_top_z(px)  # deck surface at this X
            ppar = pdeck + BRIDGE.parapet_h  # parapet top
            ppil = ppar + BRIDGE_PILLAR_EXTRA  # pillar post top
            pcap = ppil + BRIDGE_PILLAR_CAP_H  # cap slab top

            # For piers in the angled east section, shift all Y coords to follow the span.
            # east_y_shift returns 0 for all piers at or west of BRIDGE_EAST_PIVOT_X.
            py_shift = east_y_shift(px)
            by1 = BRIDGE.y1 + py_shift  # south edge of span at this pier
            by2 = BRIDGE.y2 + py_shift  # north edge of span at this pier

            cy_n = by2 - BRIDGE_PAR_W // 2  # north cap centre Y
            cy_s = by1 + BRIDGE_PAR_W // 2  # south cap centre Y

            # Width of the pier in X (matches pillar post width)
            x1, x2 = px - BRIDGE_PILLAR_HW, px + BRIDGE_PILLAR_HW

            # Ceiling Z — use the higher of the two pier face deck-bottoms so stone
            # is flush with the bridge underside across the full pier X extent.
            pier_ceiling_z = max(int(deck_bot_z(x1)), int(deck_bot_z(x2)))

            # Ground level this specific pier's base sits on. Center-span piers
            # (2 and 3) cross a real hillside — see BRIDGE_PIER_GROUND_Z's
            # docstring in constants.py — so their base plinth is normally raised
            # to sit ON TOP of the existing (unmodified) real-elevation terrain
            # there instead of at the flat FLOOR_Z2 baseline used by every other
            # pier. However, once BRIDGE_CENTER_SPAN_OFFSET relocates the whole
            # center span away from that hillside (making it a standalone
            # structure, no longer physically resting on the real terrain), the
            # BRIDGE_PIER_GROUND_Z values are stale for the new location — using
            # them here left the base plinth/cap sitting below the actual ground
            # at the new (offset) position, appearing to sink underground on the
            # west pier. Fall back to the flat FLOOR_Z2 baseline in that case,
            # same as every non-center-span pier.
            if px in (PIER2_X, PIER3_X) and BRIDGE_CENTER_SPAN_OFFSET != (
                0.0,
                0.0,
                0.0,
            ):
                pier_floor_z = FLOOR_Z2
            else:
                pier_floor_z = BRIDGE_PIER_GROUND_Z.get(px, FLOOR_Z2)

            # Arch opening varies by pillar type. The westernmost abutment,
            # Pier 5, and Pier 6 use the wider outer radii; interior piers use
            # the inner radii.
            if px in (min(BRIDGE_ARCH_X), BRIDGE_ARCH_X[4], max(BRIDGE_ARCH_X)):
                a_rout, a_rin = BRIDGE_PILLAR_OUTER_R
            else:
                a_rout, a_rin = BRIDGE_PILLAR_INNER_R
            a_stilt = pier_ceiling_z - a_rout - pier_floor_z
            if a_stilt < 0:
                # Arch would overshoot the bridge bottom; cap rout so the crown
                # lands exactly at ceil_z (bridge deck underside).
                a_rout = pier_ceiling_z - pier_floor_z
                a_stilt = 0

            # Pin outer pier wall to exactly match the pillar tops above deck.
            # Cap a_rout so the arch ring never extends past by2 + BRIDGE_PILLAR_OVERHANG;
            # if rout was trimmed, recompute stilt so the arch crown still meets the deck.
            max_outer_radius = BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG
            if a_rout > max_outer_radius:
                a_rout = max_outer_radius
                a_stilt = pier_ceiling_z - a_rout - pier_floor_z
            # Extend the straight rectangular sides (not the round arch ring) out to
            # max_outer_radius when rout falls short of it, so the below-deck pier
            # wall is flush with the pillar tops above deck instead of being
            # recessed behind them.
            arch_overhang = max(0, max_outer_radius - a_rout)

            # Pier 5's arch crown otherwise lands right at the deck underside.
            # Shrink the stilt height slightly (lowering the whole arch, crown
            # included) so the opening sits a bit lower and doesn't look like
            # it's floating right up against the deck.
            pier5_lintel_gap = PIER5_LINTEL_GAP if px == PIER5_X else 0
            a_stilt = max(0, a_stilt - pier5_lintel_gap)

            # Ramped plinth: outer piers ramp up on their outward face so players
            # can run up from outside. East piers: high east side; west piers: high west side.
            # No pier sits at x=0, so every pier gets a ramped plinth. The west
            # abutment (min(BRIDGE_ARCH_X)) is a solid dead-end (no walkable
            # archway) that hosts two recessed openings (west teleport, east
            # cement) instead — it gets the SAME kind of ramp, just taller
            # (BRIDGE_ABUTMENT_RAMP_HIGH_H/LOW_H) so both openings' floors can
            # sit on top of it, flush with the pier's true west/east faces
            # (not inset) and with the cap clearly visible along the whole span.
            if px == min(BRIDGE_ARCH_X):
                base_ramp = (
                    pier_floor_z + BRIDGE_ABUTMENT_RAMP_HIGH_H,
                    pier_floor_z + BRIDGE_ABUTMENT_RAMP_LOW_H,
                )
            elif px > 0:
                # East of road — ramp slopes up toward east (low at x1, high at x2)
                base_ramp = (
                    pier_floor_z + BRIDGE_PILLAR_BASE_H,
                    pier_floor_z + BRIDGE_PILLAR_BASE_RAMP_H,
                )
            else:
                # West of road — ramp slopes up toward west (high at x1, low at x2)
                base_ramp = (
                    pier_floor_z + BRIDGE_PILLAR_BASE_RAMP_H,
                    pier_floor_z + BRIDGE_PILLAR_BASE_H,
                )

            # Add pier structure — the new mid-span pier (max(BRIDGE_ARCH_X)) gets a
            # square opening; every other pier, including Pier 5, gets a rounded
            # arch. The west abutment (min(BRIDGE_ARCH_X)) has a solid cement fill
            # instead of an open archway, so it gets no cement opening lining.
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
                # Overhang must reach by2+BRIDGE_PILLAR_OVERHANG to match pillar tops above deck
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
                        Textures.PILLAR,
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
                        Textures.PILLAR,
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
                # The centre span (and, since every other currently-enabled
                # section now rides along with it as one rigid assembly —
                # see _shift_center_span — every pier from Pier 4 through
                # Pier 6 too) has been shifted away from the real-elevation
                # terrain BRIDGE_PIER_GROUND_Z was sampled against (see
                # BRIDGE_CENTER_SPAN_OFFSET). Rather than lowering pier_floor_z
                # itself (which would drag the visible base plinth/cap down
                # with it), extend a solid pillar stem below the existing base
                # — sized to exactly reach true (unshifted) ground once the
                # post-build Z shift is applied — so the visible cap/base stays
                # exactly where it was and the portion below the arch opening
                # visibly plants the pier on the ground instead of floating.
                # When the span is only shifted a small amount, fall back to
                # the minimum buried-embed depth so the stem still reaches
                # well into the ground. Span the full outer footprint
                # (±max_outer_radius, which the arch ring/overhang always
                # reaches — see above — and can exceed by1/by2) so the north
                # and south flared edges of the base are covered too. Pier 6's
                # square_wall, unlike arch_wall, never flares past by1/by2 (its
                # solid outer walls stop exactly there), so the wider
                # max_outer_radius allowance would only make the footer stick
                # out past the pier's own walls — narrow it to by1/by2 there
                # so the buried stem doesn't read as an oversized flared slab
                # under an otherwise slender pier.
                #
                # UPDATE: narrowing Pier 6's footer to by1/by2 made it read as
                # too narrow next to Piers 2-5 (which all use the wider
                # max_outer_radius footprint below the arch opening) — use the
                # same footprint as every other pier for visual consistency.
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
                        Textures.PILLAR,
                    )
                )

            # ── Decorative square cement plates on the pier's east/west faces ──
            # Applied to the flat end-faces (x=x1 west, x=x2 east) of every pier,
            # including the west abutment (min(BRIDGE_ARCH_X)) — even though its
            # opening is filled with cement + a teleport arch rather than being a
            # walkable passage, it still has the same rounded stone arch face as
            # the other round piers and should carry the same plate ring.
            # Rounded-arch piers get a curved ring of plates tracing the arch
            # curve (voussoir style, radius mid-way between rin/rout); square-
            # opening piers get a straight row across the flat lintel area
            # above the opening instead (they have no curve to trace).
            is_square_pier = px == max(BRIDGE_ARCH_X)
            for face_x, protrude in (
                (x1, -BRIDGE_PIER_PLATE_D),  # west face
                (x2, BRIDGE_PIER_PLATE_D),  # east face
            ):
                if is_square_pier:
                    # Inset one tile+gap pitch from each end so the row reads
                    # as one tile narrower on each side than the full pier
                    # width (the base cap below is the one meant to reach the
                    # full width — see base_cap_y1/y2 above).
                    _tile_pitch = BRIDGE_PIER_PLATE_SIZE + BRIDGE_PIER_PLATE_GAP
                    BRUSHES.extend(
                        tile_face_plates(
                            face_x,
                            protrude,
                            by1 + _tile_pitch,
                            by2 - _tile_pitch,
                            pier_ceiling_z
                            - BRIDGE_SQ_LINTEL_H,  # bottom of tiled band, flush
                            # with the bottom of square_wall's full lintel
                            pier_ceiling_z
                            - BRIDGE_SQ_LINTEL_STONE_H,  # top of tiled band —
                            # leaves a plain stone course above (part of the
                            # same solid lintel brush) instead of tiling all
                            # the way up to the ceiling/deck underside
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

            # Pillar tops (above deck, extend BRIDGE_PILLAR_OVERHANG past bridge edges and inward)
            pier_outer_y = (
                by2 + BRIDGE_PILLAR_OVERHANG
            )  # always overhang past bridge edge
            # North pillar top
            BRUSHES.append(
                box(
                    px - BRIDGE_PILLAR_HW,
                    by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG,
                    pdeck,
                    px + BRIDGE_PILLAR_HW,
                    pier_outer_y,
                    ppil,
                    Textures.PILLAR,
                )
            )

            # South pillar top
            BRUSHES.append(
                box(
                    px - BRIDGE_PILLAR_HW,
                    by1 - BRIDGE_PILLAR_OVERHANG,
                    pdeck,
                    px + BRIDGE_PILLAR_HW,
                    by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG,
                    ppil,
                    Textures.PILLAR,
                )
            )

            # Thin cement mortar-seam strip down the middle of each pillar
            # post's walkway-facing (inside) face — as if the stone posts
            # were assembled from two halves around a cement core, only
            # visible from the walkway. A separate protruding decal brush
            # (not a split of the post's own single brush) to avoid the
            # qbsp portal-clipping bug documented above the deck-bottom
            # cross-strip code.
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

            # Matching seam on the west-facing end of each post — visible to
            # a player walking the deck (approaching along the bridge), unlike
            # a true north/south exterior face which only faces out over the
            # void. Y-centred on the wall's exterior plane (by2/by1, the
            # "aligns with the wall exteriors" position), protruding out
            # past the post's west face (px - BRIDGE_PILLAR_HW) by
            # BRIDGE_PILLAR_SEAM_D. Runs the full post height, from the deck
            # up to the cap slab (pdeck to ppil), continuing down through the
            # wall's own height so it reads as one continuous seam rather
            # than stopping abruptly at the wall top.
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

            # Fill gap between pier top and deck surface in the overhang zone
            pier_top_z = int(pdeck) - BRIDGE_PIER_FILL_OFFSET
            # Pier 6's north fill is built separately (after rotation, as a
            # taper matching the deck notch slope) instead of here: this
            # box sits off to one side of the rotation pivot (at by2, far
            # from the pivot's y=py_shift), so sweeping it through the
            # rigid-body whole-pier rotation swings its inner edge away
            # from the deck's actual (fixed) edge at MID_PIER_X, opening a
            # gap/wedge there rather than closing one. See the taper piece
            # built alongside the deck notch below.
            if px != PIER6_X:
                BRUSHES.append(
                    box(x1, by2, pier_top_z, x2, pier_outer_y, pdeck, Textures.PILLAR)
                )  # north
            BRUSHES.append(
                box(
                    x1,
                    by1 - BRIDGE_PILLAR_OVERHANG,
                    pier_top_z,
                    x2,
                    by1,
                    pdeck,
                    Textures.PILLAR,
                )
            )  # south

            # Cement cap slab + pyramid on top of each stone pillar post
            cap_x1, cap_x2 = px - BRIDGE_PILLAR_PYR_W, px + BRIDGE_PILLAR_PYR_W
            north_cap_y1 = (
                by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG - BRIDGE_PILLAR_CAP_IN_OVH
            )  # inward past pillar post
            north_cap_y2 = (
                by2 + BRIDGE_PILLAR_CAP_OUT_OVH
            )  # outward (north/road-facing) edge
            south_cap_y1 = (
                by1 - BRIDGE_PILLAR_CAP_OUT_OVH
            )  # outward (south/road-facing) edge
            south_cap_y2 = (
                by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG + BRIDGE_PILLAR_CAP_IN_OVH
            )  # inward past pillar post
            # Cap slabs (flat cement base)
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
            # Pyramids on top of cap slabs
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
            # Torch bases above pyramid apex — narrow post + wide cup.
            # Piers 2/3/5 (PIER2_X/PIER3_X/PIER5_X) skip these: they don't
            # exist in real life, unlike the other piers' torches.
            pyramid_apex_z = pcap + BRIDGE_PILLAR_PYR_H
            torch_ys = [] if px in (PIER2_X, PIER3_X, PIER5_X) else [cy_n, cy_s]
            for torch_center_y in torch_ys:
                # Narrow stone post (6x6) rising from pyramid tip
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
                # Wider brick cup/bracket at top holds the flame
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
                # Flame decal + damaging trigger — built here (unconditional on
                # bridge.py's own BRIDGE_ENABLED_SUPPORTS, not any entities.py
                # per-group flag) so pier torches always render, matching
                # streets.py's own lamp-post/entrance-torch pattern of keeping
                # decorative lights alongside the geometry they sit on.
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
                # Rotate Pier 6's entire assembly — below-deck walls/footer/
                # lintel/base, and the above-deck pillar posts, mortar seams,
                # pyramid caps, and torches built for this same px above —
                # together as one rigid unit about the pier's own center.
                # Earlier this only rotated the below-deck body, leaving the
                # above-deck pillar posts (and the torches mounted on them)
                # in their old straight positions; that mismatch at the
                # deck-level seam was producing overlapping/mis-clipped
                # brushes there (reported as "invisible brushes" in-game).
                # Rotating everything together removes that seam entirely.
                # This is prep for a future new bridge span branching south
                # at ~PIER6_ROTATION_DEG from here.
                BRUSHES[_pier6_rot_bstart:] = [
                    b.rotated_z(PIER6_ROTATION_DEG, px, py_shift)
                    for b in BRUSHES[_pier6_rot_bstart:]
                ]
                ENTITIES[_pier6_rot_estart:] = [
                    e.rotated_z(PIER6_ROTATION_DEG, px, py_shift)
                    for e in ENTITIES[_pier6_rot_estart:]
                ]

            # Abutment pier (westernmost): solid cement fill, with two distinct
            # openings on opposite faces —
            #  * WEST face: a hidden arch-shaped teleport (never actually seen —
            #    it faces away from the bridge into unreachable terrain) that
            #    whisks the player up onto the deck.
            #  * EAST face: a purely decorative, solid cement "opening" (no
            #    teleport) facing into the walkable west-approach span — this
            #    is the feature players actually walk past and see.
            # Both openings sit on top of the shared stone base + cement cap
            # ramp (built generically for every pier, above, via base_ramp/
            # base_cap_h — tallest at the west face, descending toward the
            # east) so the stone is flush with the pier's true faces (not
            # inset) and the cap is visible along the whole span, starting
            # at the west face. pier_floor_z tracks the real hillside grade
            # here (see BRIDGE_PIER_GROUND_Z), so neither opening extends
            # below grade.
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
                # Cement fill leaves room on both faces for their respective
                # recessed openings, starting above the shared ramp/cap.
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

                # -- West face: hidden teleport arch (flush, no player-visible
                # framing needed since this face is never seen), floor raised
                # to sit on top of the ramp/cap's tall west end. --
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
                abutment_teleport_dest_z = (
                    int(pdeck) + BRIDGE_TELEPORT_DEST_Z
                )  # spawn height above deck

                # -- East face: decorative cement "opening" — inset from the
                # pier face (not flush) so a stone rim shows around it, sized
                # down from the pier's own arch opening so it reads as a
                # modest doorway, floor raised to sit on top of the ramp/
                # cap's lower east end.
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

    # ── Teleport Arches at both ends of bridge ───────────────────────────────────
    for arch_x_start, arch_center_y in [
        (WORLD_X1 + WALL_T, 0.0),  # west arch — centred at y=0
        (
            WORLD_X2_EXT - WALL_T - ARCH_SLAB_W,
            BRIDGE_EAST_SHIFT_END,
        ),  # east arch — shifted south with span
    ]:
        arch_x1, arch_x2 = arch_x_start, arch_x_start + ARCH_SLAB_W
        arch_spring_z = BRIDGE_DZ2 + ARCH_STILT_H  # Z where arch curve begins
        arch_post_width = ARCH_ROUT - ARCH_RIN  # post thickness in Y
        # South post (extends to ground floor, with overhang)
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
        # North post (extends to ground floor, with overhang)
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
        # Arch ring segments (rounded top, with overhang)
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

    # Restore worldspawn routing and emit the bridge superstructure as one func_detail
    # entity — excluded from BSP/vis portal generation, but still solid and rendered.
    BRUSHES = _worldspawn_brushes
    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
        DETAIL_BRUSHES = []

    # Add hint brushes to split the large open space around the bridge (vis optimization)
    # This prevents "Leaf with too many portals" errors after converting bridge to detail.
    BRUSHES.append(
        box(
            -STREET_SURFACE_T,
            WORLD_Y1,
            FLOOR_Z1,
            STREET_SURFACE_T,
            WORLD_Y2,
            WORLD_Z2,
            Textures.HINT,
        )
    )
    BRUSHES.append(
        box(
            BRIDGE_ARCH_X[1] - STREET_SURFACE_T,
            WORLD_Y1,
            FLOOR_Z1,
            BRIDGE_ARCH_X[1] + STREET_SURFACE_T,
            WORLD_Y2,
            WORLD_Z2,
            Textures.HINT,
        )
    )
    BRUSHES.append(
        box(
            BRIDGE_ARCH_X[2] - STREET_SURFACE_T,
            WORLD_Y1,
            FLOOR_Z1,
            BRIDGE_ARCH_X[2] + STREET_SURFACE_T,
            WORLD_Y2,
            WORLD_Z2,
            Textures.HINT,
        )
    )
    # North edge hint: limited to the straight section only (x≤BRIDGE_EAST_PIVOT_X).
    # In the angled east section the north parapet shifts northward (more negative Y), so
    # extending this hint beyond the pivot would place it inside the sheared parapet brush,
    # causing qbsp to cull the parapet's outer face (see-through wall bug).
    BRUSHES.append(
        box(
            WORLD_X1,
            BRIDGE.y1 - 4,
            FLOOR_Z1,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE.y1,
            WORLD_Z2,
            Textures.HINT,
        )
    )
    # South edge hint: same constraint — the south parapet shears with east_y_shift, so
    # the hint must not extend into the angled section beyond BRIDGE_EAST_PIVOT_X.
    BRUSHES.append(
        box(
            WORLD_X1,
            BRIDGE.y2,
            FLOOR_Z1,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE.y2 + 4,
            WORLD_Z2,
            Textures.HINT,
        )
    )

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

    # ── "LOYOLA UNIVERSITY MARYLAND" bridge fascia lettering ─────────────────────
    # Fascia panel follows the arch: one box per character hanging from deck_bot_z(x)
    # First letter of each word (L, U, M) stays at full pixel size; the rest shrink slightly.
    _cols = 4
    _small_px = BRIDGE_FASCIA_PX_W - 1  # one unit smaller than full size
    _n = len(BRIDGE_FASCIA_TEXT)
    # Word-initial positions in the forward text (L=0, U=7, M=18)
    _capital_pos = {
        i
        for i, ch in enumerate(BRIDGE_FASCIA_TEXT)
        if ch != " " and (i == 0 or BRIDGE_FASCIA_TEXT[i - 1] == " ")
    }
    # Mirror positions for the reversed text used on the north face
    _capital_pos_rev = {_n - 1 - i for i in _capital_pos}

    def _char_pw(i):
        return BRIDGE_FASCIA_PX_W if i in _capital_pos else _small_px

    total_w = sum((_cols + 1) * _char_pw(i) for i in range(_n)) - _char_pw(_n - 1)
    _fascia_cx = (PIER2_X + PIER3_X) // 2  # centre span midpoint — was hardcoded to 0
    # (Charles St centreline), which matched when PIER2/PIER3 were symmetric around
    # X=0. BRIDGE_CENTER_PIER_SPAN tightening only moved PIER2 (west), leaving the
    # span asymmetric (midpoint now 50, not 0), so the text needs to re-centre on
    # the actual span rather than the road.
    text_x0 = _fascia_cx - total_w // 2

    # No separate background fascia boxes — parapet wall face is the backdrop

    def render_text_fascia(
        text, x0, y_face, px_w, px_h, depth, tex, mirror=False, cap_pos=None
    ):
        """Render text as pixel-font raised boxes on a fascia face.
        Each character's Z is computed from deck_top_z(x) so letters follow the arch curve.
        cap_pos: set of character indices that render at full px size (others shrink by 1).
        mirror=True flips each glyph horizontally (needed for north-facing surface)."""
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
            # Bottom-align smaller glyphs with capitals
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
    # Per-section enable flags — each covers one span between adjacent piers.
    # There is no overall master; each span is toggled independently.
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
    """Translate the centre span plus every other currently-enabled section
    within a build() result by `offset`, as one rigid unit (piers included).
    The whole bridge is one continuous chain of pier-to-pier sections, so
    once the centre span moves, every enabled section on either side of it
    must move with it to stay connected at their shared piers — otherwise
    whichever section is left behind ends up detached from (and, since the
    offset here is +Y/+Z, visibly south of and below) the pier it's
    supposed to meet.

    _filter_sections()/_section_accept_ranges() now partition the bridge's
    piers exclusively — each internal boundary pier is claimed by exactly
    one currently-enabled section — so extracting each section's geometry
    one at a time via `extract_names` (while still passing the *full*
    enabled_names for consistent ownership resolution) can no longer double
    -count a shared pier; no manual de-dup step is needed.
    """
    dx, dy, dz = offset
    other_names = [n for n in enabled_names if n != "center_span"]
    result_b, result_e = [], []
    for name in other_names:
        sect_b, sect_e = _filter_sections(
            brushes, entities, enabled_names, extract_names=[name]
        )
        sect_b = [b.translated(dx, dy, dz) for b in sect_b]
        sect_e = [e.translated(dx, dy, dz) for e in sect_e]
        result_b.extend(sect_b)
        result_e.extend(sect_e)

    span_b, span_e = _filter_sections(
        brushes, entities, enabled_names, extract_names=["center_span"]
    )
    span_b = [b.translated(dx, dy, dz) for b in span_b]
    span_e = [e.translated(dx, dy, dz) for e in span_e]
    return result_b + span_b, result_e + span_e


def build_center_span(offset=(0.0, 0.0, 0.0)):
    """Return just the centre span's geometry — the curved arch over Charles
    St between the PIER2/PIER3 abutments (±525) — independent of the rest of
    the bridge. Pass an (dx, dy, dz) offset to translate the whole span,
    useful for experimenting with its position without touching the approach
    spans, piers, or terrain around it. Not wired into generate_map.py's
    MODULES list; call directly (e.g. from a script or test) when you want to
    build/inspect it on its own.
    """
    BRUSHES, ENTITIES = _build_all()
    BRUSHES, ENTITIES = _filter_sections(BRUSHES, ENTITIES, ["center_span"])
    dx, dy, dz = offset
    if (dx, dy, dz) != (0.0, 0.0, 0.0):
        BRUSHES = [b.translated(dx, dy, dz) for b in BRUSHES]
        ENTITIES = [e.translated(dx, dy, dz) for e in ENTITIES]
    return BRUSHES, ENTITIES
