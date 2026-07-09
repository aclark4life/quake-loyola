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

from .constants import (
    A_SEGS,
    ARCH_RIN,
    ARCH_ROUT,
    ARCH_SLAB_W,
    ARCH_STILT_H,
    BRIDGE,
    BRIDGE_ACCESS_WALK_CENTER_X,
    BRIDGE_ACCESS_WALK_HALF_W,
    BRIDGE_ACCESS_WALK_NORTH_OFFSET,
    BRIDGE_ACCESS_WALK_PIER_CLEARANCE,
    BRIDGE_ARCH_X,
    BRIDGE_BLK_H,
    BRIDGE_BLK_HW,
    BRIDGE_BLK_OVH,
    BRIDGE_BLK_PIER_CLEARANCE,
    BRIDGE_DECK_EAST_RECESS,
    BRIDGE_DZ1,
    BRIDGE_DZ2,
    BRIDGE_EAST_PIVOT_X,
    BRIDGE_EAST_SHIFT_END,
    BRIDGE_ENABLED,
    BRIDGE_ENABLED_CENTER_SPAN,
    BRIDGE_ENABLED_EAST_APPROACH,
    BRIDGE_ENABLED_EAST_EXT,
    BRIDGE_ENABLED_KH_SPAN,
    BRIDGE_ENABLED_WEST_APPROACH,
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
    BRIDGE_SEG_W,
    BRIDGE_SQ_D,
    BRIDGE_SQ_HH,
    BRIDGE_SQ_HW,
    BRIDGE_SUPPORT_BEAM_H,
    BRIDGE_SUPPORT_HALF_W,
    BRIDGE_SUPPORT_PIER_HALF_W,
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
    CHARLES_WALK_H,
    DRAW_BRIDGE_FASCIA_TEXT,
    ENNIS_SW_EDGE,
    FASCIA_FONT,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT,
    KNOTT_GROUND_Z,
    KNOTT_WALKWAY_ENABLED,
    PIER6_X,
    SHOW_SUPPORTS,
    STREET_SURFACE_T,
    WALK_X1,
    WALK_X2,
    WALK_ZT1,
    WALK_ZT2,
    WALL_T,
    WORLD_X1,
    WORLD_X2,
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
    arch_opening_lining,
    arch_plate_ring,
    arch_seg,
    arch_wall,
    box,
    brush_ent,
    east_y_shift,
    ent,
    pyramid,
    ramp_slab,
    ramp_slab_y,
    shear_box_y,
    shear_pyramid_y,
    square_opening_lining,
    square_opening_lining_sheared,
    square_wall,
    tile_face_plates,
    torch_flame_only,
)


def build():
    # Per-section enable flags — each covers one span between adjacent piers.
    # BRIDGE_ENABLED is a convenience master: if True, every section is on,
    # regardless of its individual flag below.
    sections_enabled = {
        "west_approach": BRIDGE_ENABLED or BRIDGE_ENABLED_WEST_APPROACH,
        "center_span": BRIDGE_ENABLED or BRIDGE_ENABLED_CENTER_SPAN,
        "east_approach": BRIDGE_ENABLED or BRIDGE_ENABLED_EAST_APPROACH,
        "kh_span": BRIDGE_ENABLED or BRIDGE_ENABLED_KH_SPAN,
        "east_ext": BRIDGE_ENABLED or BRIDGE_ENABLED_EAST_EXT,
    }
    if not any(sections_enabled.values()):
        return [], []
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
    # ── Bridge deck slab — the walkable surface across the whole span ─────────────
    # Straight section: arch terminus → easternmost pier
    BRUSHES.append(
        box(
            BRIDGE.x2,
            BRIDGE.y1,
            BRIDGE_DZ1,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE.y2,
            BRIDGE_DZ2,
            Textures.STONE,
            tt=Textures.FLOOR,
            tb=Textures.FLOOR,
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
    for seg_x1, seg_x2 in [
        (BRIDGE_EAST_PIVOT_X, MID_PIER_X),
        (MID_PIER_X, DECK_EAST_END_X),
    ]:
        BRUSHES.append(
            shear_box_y(
                seg_x1,
                BRIDGE.y1,
                BRIDGE_DZ1,
                seg_x2,
                BRIDGE.y2,
                BRIDGE_DZ2,
                east_y_shift(seg_x1),
                east_y_shift(seg_x2),
                Textures.STONE,
                tt=Textures.FLOOR,
                tb=Textures.FLOOR,
            )
        )

    def iter_bridge_span_segments():
        # Only the curved centre span (PIER2..PIER3) is faceted; the flat west
        # approach and the two straight approach spans are emitted as single
        # segments so their collinear boundaries don't spawn redundant coplanar
        # portals (qbsp WARNING 12 — see the east-section note below).
        p1, p2, p3 = BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]
        n_center = max(1, round((p3 - p2) / BRIDGE_SEG_W))
        step = (p3 - p2) / n_center
        boundaries = [BRIDGE.x1, p1, p2]
        boundaries += [p2 + i * step for i in range(1, n_center)]
        boundaries += [p3, BRIDGE.x2]
        for sx1, sx2 in zip(boundaries, boundaries[1:]):
            db1, db2 = deck_bot_z(sx1), deck_bot_z(sx2)
            pb1, pb2 = deck_top_z(sx1), deck_top_z(sx2)
            pt1, pt2 = pb1 + BRIDGE.parapet_h, pb2 + BRIDGE.parapet_h
            yield sx1, sx2, db1, db2, pb1, pb2, pt1, pt2

    # Bridge span deck segments (arched profile following deck_top_z / deck_bot_z)
    for sx1, sx2, db1, db2, pb1, pb2, _, _ in iter_bridge_span_segments():
        BRUSHES.append(
            ramp_slab(
                sx1,
                sx2,
                BRIDGE.y1,
                BRIDGE.y2,
                db1,
                db2,
                pb1,
                pb2,
                Textures.STONE,
                tt=Textures.FLOOR,
                tb=Textures.FLOOR,
            )
        )
    # ── Parapet walls — west flat approach removed; east flat stub only ───────────
    # North east parapet: straight BRIDGE.x2→pier, then angled pier→world wall
    BRUSHES.append(
        box(
            BRIDGE.x2,
            BRIDGE.y2 - BRIDGE_PAR_W,
            BRIDGE_DZ2,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE.y2,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    _ws.append(
        shear_box_y(
            BRIDGE_EAST_PIVOT_X,
            BRIDGE.y2 - BRIDGE_PAR_W,
            BRIDGE_DZ2,
            PAR_EAST_END_X,
            BRIDGE.y2,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            east_y_shift(BRIDGE_EAST_PIVOT_X),
            east_y_shift(PAR_EAST_END_X),
            Textures.CEMENT,
        )
    )  # North east segment — single brush avoids split-point portal clipping
    # South east — gaps at WALK_X1..WALK_X2 and east_walk_x1..east_walk_x2 for walkway/accessible-walkway connections
    # West piece (BRIDGE.x2→WALK_X1): entirely before main walkway gap
    BRUSHES.append(
        box(
            BRIDGE.x2,
            BRIDGE.y1,
            BRIDGE_DZ2,
            WALK_X1,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    # East piece (WALK_X2→world wall): straight to pier, then angled
    BRUSHES.append(
        box(
            WALK_X2,
            BRIDGE.y1,
            BRIDGE_DZ2,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            Textures.CEMENT,
        )
    )
    _ws.append(
        shear_box_y(
            BRIDGE_EAST_PIVOT_X,
            BRIDGE.y1,
            BRIDGE_DZ2,
            PAR_EAST_END_X,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            east_y_shift(BRIDGE_EAST_PIVOT_X),
            east_y_shift(PAR_EAST_END_X),
            Textures.CEMENT,
        )
    )  # South east segment — single brush avoids split-point portal clipping

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
    BRIDGE_BLK_PIR_M = (
        BRIDGE_PILLAR_HW + BRIDGE_BLK_HW + BRIDGE_BLK_PIER_CLEARANCE
    )  # clearance from pier centre to block centre

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
            BRUSHES.append(north_brush(cx, sy, bz))
        for cx, sy, bz in iter_positions(n_s, x1_s):
            if not (cx - x_half_width < WALK_X2 and cx + x_half_width > WALK_X1):
                BRUSHES.append(south_brush(cx, sy, bz))

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
            """Tilted block following the arch — ramp_slab when sloped, box when flat."""
            zb1 = round(deck_top_z(cx - BRIDGE_BLK_HW) + BRIDGE.parapet_h)
            zb2 = round(deck_top_z(cx + BRIDGE_BLK_HW) + BRIDGE.parapet_h)
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
                cx, sy, BRIDGE.y2 - BRIDGE_PAR_W, BRIDGE.y2 + BRIDGE_BLK_OVH
            ),
            south_brush=lambda cx, sy, bz: _block(
                cx, sy, BRIDGE.y1 - BRIDGE_BLK_OVH, BRIDGE.y1 + BRIDGE_PAR_W
            ),
            west_margin=west_margin,
            east_margin=east_margin,
            n_south=n_south,
            east_margin_n=east_margin_n,
            y_shift_fn=y_shift_fn,
        )

    # Western span (BRIDGE.x1 → BRIDGE_ARCH_X[0]): no blocks — open span
    # Span 2 (BRIDGE_ARCH_X[0] → BRIDGE_ARCH_X[1]): eastern span 1, 3 blocks
    add_parapet_blocks(BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], 3)
    # Middle span (BRIDGE_ARCH_X[1] → BRIDGE_ARCH_X[2]): 4 blocks
    add_parapet_blocks(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
    # Eastern span 2 (BRIDGE_ARCH_X[2] → BRIDGE_ARCH_X[3]): 3 blocks
    add_parapet_blocks(BRIDGE_ARCH_X[2], BRIDGE_ARCH_X[3], 3)
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

    add_parapet_squares(BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], 3)
    add_parapet_squares(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
    add_parapet_squares(BRIDGE_ARCH_X[2], BRIDGE_ARCH_X[3], 3)
    add_parapet_squares(
        BRIDGE.x2,
        BRIDGE_ARCH_X[4],
        3,
        west_margin=BRIDGE_BLK_HW + 8,
        n_south=0,
        y_shift_fn=east_y_shift,
    )
    # South east of walkway: corner blocks only at each side of the opening
    # Corner block on east side of walkway opening (west face flush with WALK_X2)
    cx_walk_e = WALK_X2 + BRIDGE_BLK_HW
    BRUSHES.append(
        box(
            cx_walk_e - BRIDGE_BLK_HW,
            BRIDGE.y1 - BRIDGE_BLK_OVH,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            cx_walk_e + BRIDGE_BLK_HW,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h + BRIDGE_BLK_H,
            Textures.CEMENT,
        )
    )
    # Extra block on west side of walkway opening (east face flush with WALK_X1)
    cx_walk_w = WALK_X1 - BRIDGE_BLK_HW
    BRUSHES.append(
        box(
            cx_walk_w - BRIDGE_BLK_HW,
            BRIDGE.y1 - BRIDGE_BLK_OVH,
            BRIDGE_DZ2 + BRIDGE.parapet_h,
            cx_walk_w + BRIDGE_BLK_HW,
            BRIDGE.y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE.parapet_h + BRIDGE_BLK_H,
            Textures.CEMENT,
        )
    )

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
        # North tube: straight then two angled segments
        BRUSHES.append(
            box(
                BRIDGE.x2,
                tube_ny1,
                tube_base_z,
                BRIDGE_EAST_PIVOT_X,
                tube_ny2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        for seg_x1, seg_x2 in [
            (BRIDGE_EAST_PIVOT_X, MID_PIER_X),
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
        # South tube west piece (BRIDGE.x2→WALK_X1): before pier, straight
        BRUSHES.append(
            box(
                BRIDGE.x2,
                tube_sy1,
                tube_base_z,
                WALK_X1,
                tube_sy2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        # South tube east piece (WALK_X2→world wall): straight to pivot, then two angled segments
        BRUSHES.append(
            box(
                WALK_X2,
                tube_sy1,
                tube_base_z,
                BRIDGE_EAST_PIVOT_X,
                tube_sy2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        for seg_x1, seg_x2 in [
            (BRIDGE_EAST_PIVOT_X, MID_PIER_X),
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
    if SHOW_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if px == PIER6_X:
                continue  # built explicitly below as a duplicate of Pier 5
            if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
                continue
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
            # docstring in constants.py — so their base plinth is raised to sit
            # ON TOP of the existing (unmodified) real-elevation terrain there
            # instead of at the flat FLOOR_Z2 baseline used by every other pier.
            pier_floor_z = BRIDGE_PIER_GROUND_Z.get(px, FLOOR_Z2)

            # Arch opening varies by pillar type. The westernmost abutment, Pier 5
            # (KNOTT_NE_PIER_X), and the new Pier 6 use the wider outer radii;
            # interior piers use the inner radii.
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

            # Ramped plinth: outer piers ramp up on their outward face so players
            # can run up from outside. East piers: high east side; west piers: high west side.
            # No pier sits at x=0, so every pier gets a ramped plinth.
            if px > 0:
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

            # Add pier structure — BRIDGE_ARCH_X[4] (KNOTT_NE_PIER_X) and the new
            # mid-span pier get square openings; all other piers get rounded arches.
            if px in (BRIDGE_ARCH_X[4], max(BRIDGE_ARCH_X)):
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
                        base_h=BRIDGE_PILLAR_BASE_H,
                        base_cap_h=BRIDGE_PILLAR_BASE_CAP_H,
                        base_cap_tex=Textures.CEMENT,
                        base_cap_ovh=BRIDGE_PILLAR_BASE_CAP_OVH,
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
                        base_cap_h=0
                        if px == min(BRIDGE_ARCH_X)
                        else BRIDGE_PILLAR_BASE_CAP_H,
                        base_cap_tex=Textures.CEMENT,
                        base_cap_ovh=BRIDGE_PILLAR_BASE_CAP_OVH,
                    )
                )

            # ── Decorative square cement plates on the pier's east/west faces ──
            # Applied to the flat end-faces (x=x1 west, x=x2 east) of every
            # pier except the west abutment (min(BRIDGE_ARCH_X)), which has a
            # solid cement fill and teleport arch instead of an open archway.
            # Rounded-arch piers get a curved ring of plates tracing the arch
            # curve (voussoir style, radius mid-way between rin/rout); square-
            # opening piers get a straight row across the flat lintel area
            # above the opening instead (they have no curve to trace).
            if px != min(BRIDGE_ARCH_X):
                is_square_pier = px in (BRIDGE_ARCH_X[4], max(BRIDGE_ARCH_X))
                for face_x, protrude in (
                    (x1, -BRIDGE_PIER_PLATE_D),  # west face
                    (x2, BRIDGE_PIER_PLATE_D),  # east face
                ):
                    if is_square_pier:
                        BRUSHES.extend(
                            tile_face_plates(
                                face_x,
                                protrude,
                                -a_rin,
                                a_rin,
                                pier_ceiling_z
                                - 16,  # matches square_wall's lintel height
                                pier_ceiling_z,
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

                # Cement lining on the inside surfaces of the opening (side
                # walls + curved intrados or lintel underside), leaving a
                # stone border at each opening end. The bottom of the
                # opening already has a cement cap from base_cap_h above.
                if is_square_pier:
                    BRUSHES.extend(
                        square_opening_lining(
                            x1,
                            x2,
                            0.0,
                            pier_floor_z,
                            pier_ceiling_z - 16,
                            a_rin,
                            BRIDGE_PIER_LINING_THICK,
                            Textures.CEMENT,
                            margin=BRIDGE_PIER_LINING_MARGIN,
                        )
                    )
                else:
                    BRUSHES.extend(
                        arch_opening_lining(
                            x1,
                            x2,
                            0.0,
                            pier_floor_z,
                            pier_floor_z + a_stilt,
                            a_rin,
                            BRIDGE_PIER_LINING_THICK,
                            A_SEGS,
                            Textures.CEMENT,
                            margin=BRIDGE_PIER_LINING_MARGIN,
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

            # Fill gap between pier top and deck surface in the overhang zone
            pier_top_z = int(pdeck) - BRIDGE_PIER_FILL_OFFSET
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
            # Torch bases above pyramid apex — narrow post + wide cup
            pyramid_apex_z = pcap + BRIDGE_PILLAR_PYR_H
            for torch_center_y in [cy_n, cy_s]:
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
                # BRIDGE_ENABLED/SHOW_SUPPORTS, not entities.py's ENTITIES_ENABLED
                # master) so pier torches always render, matching streets.py's
                # own lamp-post/entrance-torch pattern of keeping decorative
                # lights alongside the geometry they sit on.
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

            # Abutment pier (westernmost): solid cement fill + arch teleport on west face
            if px == min(BRIDGE_ARCH_X):
                # Cement fill starts 16 units east of pier face to make room for arch
                BRUSHES.append(
                    box(
                        x1 + BRIDGE_PIER_FILL_OFFSET,
                        -a_rin,
                        FLOOR_Z2,
                        x2,
                        a_rin,
                        int(pdeck) - BRIDGE_PIER_FILL_OFFSET,
                        Textures.CEMENT,
                    )
                )
                # Arch-shaped teleport flush with the west face (recessed into pier)
                teleport_stilt_height = (
                    pier_top_z - FLOOR_Z2 - a_rin - BRIDGE_TELEPORT_ARCH_CLEARANCE
                )
                abutment_teleport_brush = arch_fill(
                    x1 + BRIDGE_TELEPORT_ARCH_X1_OFFSET,
                    x1 + BRIDGE_TELEPORT_ARCH_X2_OFFSET,
                    0.0,
                    FLOOR_Z2,
                    a_rin,
                    A_SEGS,
                    Textures.TELEPORT,
                    stilt_h=teleport_stilt_height,
                )
                abutment_teleport_dest_z = (
                    int(pdeck) + BRIDGE_TELEPORT_DEST_Z
                )  # spawn height above deck

    # ── Pier 6 — explicit duplicate of Pier 5 (KNOTT_NE_PIER_X) ─────────────────
    # Pier 5 uses square_wall + OUTER_R. Pier 6 is identical but sits in the angled
    # east span, so all Y coords are shifted south by east_y_shift(PIER6_X).
    if SHOW_SUPPORTS:
        px = PIER6_X
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
        a_rout, a_rin = BRIDGE_PILLAR_OUTER_R
        sq_overhang = BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG - a_rin
        # Relative shear at x1/x2 so the pier faces align with the angled deck direction.
        s1r = east_y_shift(x1) - py_shift
        s2r = east_y_shift(x2) - py_shift

        def sb(ya, yb, za, zb, tex):
            return shear_box_y(x1, ya, za, x2, yb, zb, s1r, s2r, tex)

        yc = py_shift
        ext = a_rin + sq_overhang
        # Main pier body (square opening, rotated to follow deck angle)
        BRUSHES.append(
            sb(yc - ext, yc - a_rin, FLOOR_Z2, pier_ceiling_z, Textures.PILLAR)
        )  # south pillar
        BRUSHES.append(
            sb(yc + a_rin, yc + ext, FLOOR_Z2, pier_ceiling_z, Textures.PILLAR)
        )  # north pillar
        BRUSHES.append(
            sb(
                yc - a_rin,
                yc + a_rin,
                pier_ceiling_z - 16,
                pier_ceiling_z,
                Textures.PILLAR,
            )
        )  # lintel
        if BRIDGE_PILLAR_BASE_H > 0:
            BRUSHES.append(
                sb(
                    yc - a_rin,
                    yc + a_rin,
                    FLOOR_Z2,
                    FLOOR_Z2 + BRIDGE_PILLAR_BASE_H,
                    Textures.PILLAR,
                )
            )  # base
            # Cement cap slab on top of base plinth (matches arch-pier base caps)
            if BRIDGE_PILLAR_BASE_CAP_H > 0:
                cap_crin = a_rin + BRIDGE_PILLAR_BASE_CAP_OVH
                BRUSHES.append(
                    shear_box_y(
                        px - BRIDGE_PILLAR_HW - BRIDGE_PILLAR_BASE_CAP_OVH,
                        yc - cap_crin,
                        FLOOR_Z2 + BRIDGE_PILLAR_BASE_H,
                        px + BRIDGE_PILLAR_HW + BRIDGE_PILLAR_BASE_CAP_OVH,
                        yc + cap_crin,
                        FLOOR_Z2 + BRIDGE_PILLAR_BASE_H + BRIDGE_PILLAR_BASE_CAP_H,
                        s1r,
                        s2r,
                        Textures.CEMENT,
                    )
                )  # base cap
        # Decorative square cement plates above the opening on the pier's
        # east/west end faces (square opening → straight row, no curve to
        # trace; see main pier loop above for the rounded-arch version). No
        # per-tile shear needed here since each face plate sits at a single
        # fixed X (the face itself), just offset in Y by that face's own
        # local shear (s1r for the west face at x1, s2r for the east face at x2).
        for face_x, y_shift, protrude in (
            (x1, s1r, -BRIDGE_PIER_PLATE_D),  # west face
            (x2, s2r, BRIDGE_PIER_PLATE_D),  # east face
        ):
            BRUSHES.extend(
                tile_face_plates(
                    face_x,
                    protrude,
                    yc + y_shift - a_rin,
                    yc + y_shift + a_rin,
                    pier_ceiling_z - 16,  # matches square_wall's lintel height
                    pier_ceiling_z,
                    Textures.CEMENT,
                    tile=BRIDGE_PIER_PLATE_SIZE,
                    gap=BRIDGE_PIER_PLATE_GAP,
                )
            )
        # Cement lining on the inside surfaces of the opening (sheared to
        # follow the angled deck), leaving a stone border at each opening
        # end. The bottom already has a cement cap from the base cap above.
        BRUSHES.extend(
            square_opening_lining_sheared(
                x1,
                x2,
                east_y_shift(x1),
                east_y_shift(x2),
                FLOOR_Z2,
                pier_ceiling_z - 16,
                a_rin,
                BRIDGE_PIER_LINING_THICK,
                Textures.CEMENT,
                margin=BRIDGE_PIER_LINING_MARGIN,
            )
        )
        if by1 < yc - ext:
            BRUSHES.append(sb(by1, yc - ext, FLOOR_Z2, pier_ceiling_z, Textures.PILLAR))
        if by2 > yc + ext:
            BRUSHES.append(sb(yc + ext, by2, FLOOR_Z2, pier_ceiling_z, Textures.PILLAR))
        pier_outer_y = by2 + BRIDGE_PILLAR_OVERHANG
        pier_top_z = int(pdeck) - BRIDGE_PIER_FILL_OFFSET
        # North pillar top (above deck)
        BRUSHES.append(
            sb(
                by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG,
                pier_outer_y,
                pdeck,
                ppil,
                Textures.PILLAR,
            )
        )
        # South pillar top (above deck)
        BRUSHES.append(
            sb(
                by1 - BRIDGE_PILLAR_OVERHANG,
                by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG,
                pdeck,
                ppil,
                Textures.PILLAR,
            )
        )
        # Fill gap between pier top and deck in the overhang zone
        BRUSHES.append(sb(by2, pier_outer_y, pier_top_z, pdeck, Textures.PILLAR))
        BRUSHES.append(
            sb(by1 - BRIDGE_PILLAR_OVERHANG, by1, pier_top_z, pdeck, Textures.PILLAR)
        )
        # Cement cap slabs
        cap_x1, cap_x2 = px - BRIDGE_PILLAR_PYR_W, px + BRIDGE_PILLAR_PYR_W
        north_cap_y1 = (
            by2 - BRIDGE_PAR_W - BRIDGE_PILLAR_OVERHANG - BRIDGE_PILLAR_CAP_IN_OVH
        )
        north_cap_y2 = by2 + BRIDGE_PILLAR_CAP_OUT_OVH
        south_cap_y1 = by1 - BRIDGE_PILLAR_CAP_OUT_OVH
        south_cap_y2 = (
            by1 + BRIDGE_PAR_W + BRIDGE_PILLAR_OVERHANG + BRIDGE_PILLAR_CAP_IN_OVH
        )
        sc1r = east_y_shift(cap_x1) - py_shift
        sc2r = east_y_shift(cap_x2) - py_shift
        BRUSHES.append(
            shear_box_y(
                cap_x1,
                north_cap_y1,
                ppil,
                cap_x2,
                north_cap_y2,
                pcap,
                sc1r,
                sc2r,
                Textures.CEMENT,
            )
        )
        BRUSHES.append(
            shear_box_y(
                cap_x1,
                south_cap_y1,
                ppil,
                cap_x2,
                south_cap_y2,
                pcap,
                sc1r,
                sc2r,
                Textures.CEMENT,
            )
        )
        # Pyramids — sheared the same as the cap slab beneath (was axis-aligned,
        # so the diamond base didn't line up with the slab's parallelogram top).
        BRUSHES.append(
            shear_pyramid_y(
                cap_x1,
                north_cap_y1,
                cap_x2,
                north_cap_y2,
                pcap,
                pcap + BRIDGE_PILLAR_PYR_H,
                sc1r,
                sc2r,
                Textures.CEMENT,
            )
        )
        BRUSHES.append(
            shear_pyramid_y(
                cap_x1,
                south_cap_y1,
                cap_x2,
                south_cap_y2,
                pcap,
                pcap + BRIDGE_PILLAR_PYR_H,
                sc1r,
                sc2r,
                Textures.CEMENT,
            )
        )
        # Torch bases (centred on shifted cap centres)
        pyramid_apex_z = pcap + BRIDGE_PILLAR_PYR_H
        for torch_center_y in [cy_n, cy_s]:
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
            # Flame decal + damaging trigger — see matching comment in the main
            # pier loop above for why this lives here instead of entities.py.
            flame_z = int(pyramid_apex_z + BRIDGE_TORCH_POST_H + BRIDGE_TORCH_CUP_H + 4)
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

    # ════════════════════════════════════════════════════════════════════════════════
    # WALKWAY — flat bridge from south edge to building 2nd floor entrance
    # X=-64..64, Y=BRIDGE.y1..KNOTT.y2; flat at WALK_ZT1 = WALK_ZT2
    # ════════════════════════════════════════════════════════════════════════════════
    if KNOTT_WALKWAY_ENABLED:
        wk_zb1 = WALK_ZT1 - KNOTT.wall_t  # slab bottom at bridge end
        wk_zb2 = WALK_ZT2 - KNOTT.wall_t  # slab bottom at building end
        BRUSHES.append(
            ramp_slab_y(
                WALK_X1,
                WALK_X2,
                BRIDGE.y1,
                KNOTT.y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1,
                WALK_ZT2,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )
        # Side rails slope with the ramp (32-unit thick walls so tubes sit centred)
        DETAIL_BRUSHES.append(
            ramp_slab_y(
                WALK_X1 - BRIDGE.walk_wall,
                WALK_X1,
                BRIDGE.y1,
                KNOTT.y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1 + BRIDGE.parapet_h,
                WALK_ZT2 + BRIDGE.parapet_h,
                Textures.CEMENT,
            )
        )
        DETAIL_BRUSHES.append(
            ramp_slab_y(
                WALK_X2,
                WALK_X2 + BRIDGE.walk_wall,
                BRIDGE.y1,
                KNOTT.y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1 + BRIDGE.parapet_h,
                WALK_ZT2 + BRIDGE.parapet_h,
                Textures.CEMENT,
            )
        )
        # Handrail tubes along walkway sides, centred in the wall thickness
        for tube_z_offset in [BRIDGE_TUBE_RISE, BRIDGE_TUBE_RISE + BRIDGE_TUBE_GAP]:
            tube_base_z = WALK_ZT1 + BRIDGE.parapet_h + tube_z_offset
            ww_cx = BRIDGE.walk_wall // 2
            DETAIL_BRUSHES.append(
                box(
                    WALK_X1 - ww_cx - BRIDGE_TUBE_HW,
                    KNOTT.y2,
                    tube_base_z,
                    WALK_X1 - ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE.y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )
            DETAIL_BRUSHES.append(
                box(
                    WALK_X2 + ww_cx - BRIDGE_TUBE_HW,
                    KNOTT.y2,
                    tube_base_z,
                    WALK_X2 + ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE.y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )

    # ════════════════════════════════════════════════════════════════════════════════
    # ACCESSIBLE WALKWAY — N-S cement path at KH ground floor level (Z=KNOTT_GROUND_Z),
    # running alongside Pier 5 (west face).  Connects Knott Hall north face to the
    # bridge south edge, then wraps east via a short E-W ramp to the back-road west
    # sidewalk.  Provides ground-level access around Pier 5 without steps.
    # Spans Y=KNOTT.y2..BRIDGE.y1 (KH north face → bridge south edge).
    # ════════════════════════════════════════════════════════════════════════════════
    if KNOTT_WALKWAY_ENABLED:
        east_walk_center_x = BRIDGE_ACCESS_WALK_CENTER_X
        east_walk_half_width = BRIDGE_ACCESS_WALK_HALF_W
        east_walk_x2 = east_walk_center_x + east_walk_half_width  # 2152
        east_walk_y2 = (
            BRIDGE.y2
            + BRIDGE_PILLAR_OVERHANG
            + BRIDGE_ACCESS_WALK_PIER_CLEARANCE
            + BRIDGE_ACCESS_WALK_NORTH_OFFSET
        )  # north anchor: ramp moved 80 units north
        terrain_z2 = int(
            KNOTT_GROUND_Z
            + (FLOOR_Z2 + CHARLES_WALK_H - KNOTT_GROUND_Z)
            * (east_walk_y2 - (KNOTT.y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
            / (ENNIS_SW_EDGE - (KNOTT.y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
        )
        # E-W extension — slopes east from terrain level down to back road sidewalk (Z=8) at KNOTT.x2
        east_walk_ext_y1 = east_walk_y2 - (east_walk_half_width * 2)
        east_walk_ext_y2 = east_walk_y2
        extension_terrain_z1 = int(
            KNOTT_GROUND_Z
            + (FLOOR_Z2 + CHARLES_WALK_H - KNOTT_GROUND_Z)
            * (east_walk_ext_y1 - (KNOTT.y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
            / (ENNIS_SW_EDGE - (KNOTT.y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
        )
        extension_terrain_z2 = terrain_z2
        extension_terrain_z_west = (
            extension_terrain_z1 + extension_terrain_z2
        ) // 2  # Z at west end (N-S path side)
        DETAIL_BRUSHES.append(
            ramp_slab(
                east_walk_x2,
                KNOTT.x2,
                east_walk_ext_y1,
                east_walk_ext_y2,
                FLOOR_Z1,
                FLOOR_Z1,
                extension_terrain_z_west,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )

    # ════════════════════════════════════════════════════════════════════════════════
    # WALKWAY BENT — cement cap beam + 5 drop piers under the south edge of the bridge
    # approach in front of Knott Hall.  Mirrors the real-life concrete support bent
    # visible under the KH bridge approach (ref: bridge01).
    # ════════════════════════════════════════════════════════════════════════════════
    if KNOTT_WALKWAY_ENABLED:
        # Position just under the south edge of the bridge deck, shifted north
        # so the beam sits fully under the deck (south face flush with deck edge)
        support_y_center = (
            BRIDGE.y1 + BRIDGE_SUPPORT_HALF_W
        )  # flush with south deck edge
        support_half_width = BRIDGE_SUPPORT_HALF_W  # half-depth of beam/piers (N-S)
        support_y1 = support_y_center - support_half_width
        support_y2 = support_y_center + support_half_width
        # Beam sits just below the walkway slab bottom
        beam_top_z = WALK_ZT1 - KNOTT.wall_t  # bottom of walkway slab at bridge end
        beam_height = BRIDGE_SUPPORT_BEAM_H
        beam_bottom_z = beam_top_z - beam_height
        # Span between the two bridge arch piers flanking the walkway (east span)
        beam_x1 = BRIDGE_ARCH_X[3]
        beam_x2 = BRIDGE_ARCH_X[4]
        # Horizontal crossbeam
        DETAIL_BRUSHES.append(
            box(
                beam_x1,
                support_y1,
                beam_bottom_z,
                beam_x2,
                support_y2,
                beam_top_z,
                Textures.CEMENT,
            )
        )
        # 5 sub-piers: 3 evenly west of walkway gap, 2 evenly east — none in the gap
        rail_x1 = WALK_X1 - BRIDGE.walk_wall  # west rail outer edge
        rail_x2 = WALK_X2 + BRIDGE.walk_wall  # east rail outer edge
        west_support_piers = [
            int(beam_x1 + (rail_x1 - beam_x1) * f) for f in (0.28, 0.63, 0.93)
        ]
        east_support_piers = [
            int(rail_x2 + (beam_x2 - rail_x2) * f) for f in (0.0, 0.45)
        ]
        support_pier_xs = west_support_piers + east_support_piers
        support_pier_half_width = BRIDGE_SUPPORT_PIER_HALF_W
        for pier_x in support_pier_xs:
            DETAIL_BRUSHES.append(
                box(
                    pier_x - support_pier_half_width,
                    support_y1,
                    FLOOR_Z2,
                    pier_x + support_pier_half_width,
                    support_y2,
                    beam_bottom_z,
                    Textures.CEMENT,
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
    text_x0 = 0 - total_w // 2

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
        if DRAW_BRIDGE_FASCIA_TEXT
        else []
    )
    if letter_brushes:
        ENTITIES.append(brush_ent("func_detail", letter_brushes))

    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))

    if not all(sections_enabled.values()):
        # Keep only geometry overlapping one of the *enabled* spans (each
        # Pier[i]..Pier[i+1] range, plus a small margin to include the
        # bounding piers). Applied last so it catches brushes already
        # wrapped in func_detail entities (the bridge superstructure) as
        # well as worldspawn brushes (e.g. hint brushes, which are dropped
        # entirely — they're only useful when the full bridge exists).
        margin = BRIDGE_PILLAR_HW + BRIDGE_PILLAR_OVERHANG
        section_piers = {
            "west_approach": (BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1]),
            "center_span": (BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]),
            "east_approach": (BRIDGE_ARCH_X[2], BRIDGE_ARCH_X[3]),
            "kh_span": (BRIDGE_ARCH_X[3], BRIDGE_ARCH_X[4]),
            "east_ext": (BRIDGE_ARCH_X[4], BRIDGE_ARCH_X[5]),
        }
        enabled_spans = [
            (px1 - margin, px2 + margin)
            for name, (px1, px2) in section_piers.items()
            if sections_enabled[name]
        ]

        def _in_any_span(b):
            xs = [p[0] for f in b.faces for p in (f.p1, f.p2, f.p3)]
            # Full containment (not just partial overlap) — otherwise long
            # adjacent-span deck/parapet segments that merely touch a pier
            # boundary (e.g. x=[-1246,-525]) would incorrectly pass.
            bx1, bx2 = min(xs), max(xs)
            return any(bx1 >= sx1 and bx2 <= sx2 for sx1, sx2 in enabled_spans)

        def _is_hint(b):
            return all(f.tex == Textures.HINT for f in b.faces)

        BRUSHES = [b for b in BRUSHES if _in_any_span(b) and not _is_hint(b)]
        new_entities = []
        for entdict in ENTITIES:
            if entdict.brushes:
                # Brush entity (func_detail, trigger_teleport, func_illusionary,
                # etc.) — keep only brushes overlapping an enabled span; drop
                # the whole entity if nothing survives (e.g. the west-abutment
                # teleport arch's trigger/illusionary brushes, which sit at
                # x≈-1265..-1281, well outside any enabled span).
                filtered = [b for b in entdict.brushes if _in_any_span(b)]
                if filtered:
                    new_entities.append(
                        brush_ent(entdict.classname, filtered, **entdict.fields)
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
        ENTITIES = new_entities

    return BRUSHES, ENTITIES
