from .constants import (
    A_SEGS,
    ARCH_RIN,
    ARCH_ROUT,
    ARCH_SLAB_W,
    ARCH_STILT_H,
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
    BRIDGE_EAST_SHIFT_START,
    BRIDGE_PAR_H,
    BRIDGE_PAR_W,
    BRIDGE_PIER_FILL_OFFSET,
    BRIDGE_PIL_BASE_CAP_H,
    BRIDGE_PIL_BASE_CAP_OVH,
    BRIDGE_PIL_BASE_H,
    BRIDGE_PIL_BASE_RAMP_H,
    BRIDGE_PIL_CAP_H,
    BRIDGE_PIL_CAP_IN_OVH,
    BRIDGE_PIL_CAP_OUT_OVH,
    BRIDGE_PIL_CAP_OVHNTR_R,
    BRIDGE_PIL_EXTRA,
    BRIDGE_PIL_HW,
    BRIDGE_PIL_INNER_R,
    BRIDGE_PIL_OUTER_R,
    BRIDGE_PIL_OVERHANG,
    BRIDGE_PIL_PYR_H,
    BRIDGE_PIL_PYR_W,
    BRIDGE_SEG_SPAN_W,
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
    BRIDGE_WALK_WALL,
    BRIDGE_X1,
    BRIDGE_X2,
    BRIDGE_Y1,
    BRIDGE_Y2,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_SW_EDGE,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT_GROUND_Z,
    KNOTT_WALKWAY_ENABLED,
    KNOTT_WALL,
    KNOTT_X2,
    KNOTT_Y2,
    SHOW_SUPPORTS,
    STREET_SURFACE_T,
    WALK_X1,
    WALK_X2,
    WALK_ZT1,
    WALK_ZT2,
    WALL_T,
    WORLD_X1,
    WORLD_X2,
    WORLD_Y1,
    WORLD_Y2,
    WORLD_Z2,
    Textures,
    deck_bot_z,
    deck_top_z,
)
from .geometry import (
    arch_fill,
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
    square_wall,
)


def build():
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
            BRIDGE_X2,
            BRIDGE_Y1,
            BRIDGE_DZ1,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y2,
            BRIDGE_DZ2,
            Textures.STONE,
            tt=Textures.FLOOR,
            tb=Textures.FLOOR,
        )
    )
    # Angled section: easternmost pier → 1 unit inside the east arch face.
    # The east end is recessed to WORLD_X2 - WALL_T - 1 so the deck's east face is no
    # longer coplanar with the arch east face (eliminating z-fighting), while the arch
    # post geometry (X=2928–2960) still covers the deck's north/south edges so there is
    # no visible overhang on either side.
    DECK_EAST_END_X = WORLD_X2 - WALL_T - BRIDGE_DECK_EAST_RECESS
    BRUSHES.append(
        shear_box_y(
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y1,
            BRIDGE_DZ1,
            DECK_EAST_END_X,
            BRIDGE_Y2,
            BRIDGE_DZ2,
            BRIDGE_EAST_SHIFT_START,
            east_y_shift(DECK_EAST_END_X),
            Textures.STONE,
            tt=Textures.FLOOR,
            tb=Textures.FLOOR,
        )
    )

    def iter_bridge_span_segments():
        for i in range(BRIDGE_SEG_SPAN_W):
            sx1 = BRIDGE_X1 + i * BRIDGE_SEG_W
            sx2 = sx1 + BRIDGE_SEG_W
            db1, db2 = deck_bot_z(sx1), deck_bot_z(sx2)
            pb1, pb2 = deck_top_z(sx1), deck_top_z(sx2)
            pt1, pt2 = pb1 + BRIDGE_PAR_H, pb2 + BRIDGE_PAR_H
            yield sx1, sx2, db1, db2, pb1, pb2, pt1, pt2

    # Bridge span deck segments (arched profile following deck_top_z / deck_bot_z)
    for sx1, sx2, db1, db2, pb1, pb2, _, _ in iter_bridge_span_segments():
        BRUSHES.append(
            ramp_slab(
                sx1,
                sx2,
                BRIDGE_Y1,
                BRIDGE_Y2,
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
    # North east parapet: straight BRIDGE_X2→pier, then angled pier→world wall
    BRUSHES.append(
        box(
            BRIDGE_X2,
            BRIDGE_Y2 - BRIDGE_PAR_W,
            BRIDGE_DZ2,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y2,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        shear_box_y(
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y2 - BRIDGE_PAR_W,
            BRIDGE_DZ2,
            WORLD_X2 - WALL_T - ARCH_SLAB_W,
            BRIDGE_Y2,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            BRIDGE_EAST_SHIFT_START,
            east_y_shift(WORLD_X2 - WALL_T - ARCH_SLAB_W),
            Textures.CEMENT,
        )
    )  # North east
    # South east — gaps at WALK_X1..WALK_X2 and east_walk_x1..east_walk_x2 for walkway/accessible-walkway connections
    # West piece (BRIDGE_X2→WALK_X1): entirely before main walkway gap
    BRUSHES.append(
        box(
            BRIDGE_X2,
            BRIDGE_Y1,
            BRIDGE_DZ2,
            WALK_X1,
            BRIDGE_Y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            Textures.CEMENT,
        )
    )
    # East piece (WALK_X2→world wall): straight to pier, then angled
    BRUSHES.append(
        box(
            WALK_X2,
            BRIDGE_Y1,
            BRIDGE_DZ2,
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        shear_box_y(
            BRIDGE_EAST_PIVOT_X,
            BRIDGE_Y1,
            BRIDGE_DZ2,
            WORLD_X2 - WALL_T - ARCH_SLAB_W,
            BRIDGE_Y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            BRIDGE_EAST_SHIFT_START,
            east_y_shift(WORLD_X2 - WALL_T - ARCH_SLAB_W),
            Textures.CEMENT,
        )
    )

    for sx1, sx2, _, _, pb1, pb2, pt1, pt2 in iter_bridge_span_segments():
        # North parapet
        BRUSHES.append(
            ramp_slab(
                sx1,
                sx2,
                BRIDGE_Y2 - BRIDGE_PAR_W,
                BRIDGE_Y2,
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
                    BRIDGE_Y1,
                    BRIDGE_Y1 + BRIDGE_PAR_W,
                    pb1,
                    pb2,
                    pt1,
                    pt2,
                    Textures.CEMENT,
                )
            )

    # ── Parapet cement blocks (decorative posts atop parapet walls) ───────────────
    BRIDGE_BLK_PIR_M = (
        BRIDGE_PIL_HW + BRIDGE_BLK_HW + BRIDGE_BLK_PIER_CLEARANCE
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
        add_repeated_parapet_decorations(
            x_start,
            x_end,
            n,
            x_half_width=BRIDGE_BLK_HW,
            z_at_center=lambda cx: min(
                deck_top_z(cx - BRIDGE_BLK_HW),
                deck_top_z(cx),
                deck_top_z(cx + BRIDGE_BLK_HW),
            )
            + BRIDGE_PAR_H,
            north_brush=lambda cx, sy, bz: box(
                cx - BRIDGE_BLK_HW,
                BRIDGE_Y2 - BRIDGE_PAR_W + sy,
                bz,
                cx + BRIDGE_BLK_HW,
                BRIDGE_Y2 + BRIDGE_BLK_OVH + sy,
                bz + BRIDGE_BLK_H,
                Textures.CEMENT,
            ),
            south_brush=lambda cx, sy, bz: box(
                cx - BRIDGE_BLK_HW,
                BRIDGE_Y1 - BRIDGE_BLK_OVH + sy,
                bz,
                cx + BRIDGE_BLK_HW,
                BRIDGE_Y1 + BRIDGE_PAR_W + sy,
                bz + BRIDGE_BLK_H,
                Textures.CEMENT,
            ),
            west_margin=west_margin,
            east_margin=east_margin,
            n_south=n_south,
            east_margin_n=east_margin_n,
            y_shift_fn=y_shift_fn,
        )

    # Western span (BRIDGE_X1 → BRIDGE_ARCH_X[0]): no blocks — open span
    # Span 2 (BRIDGE_ARCH_X[0] → BRIDGE_ARCH_X[1]): eastern span 1, 3 blocks
    add_parapet_blocks(BRIDGE_ARCH_X[0], BRIDGE_ARCH_X[1], 3)
    # Middle span (BRIDGE_ARCH_X[1] → BRIDGE_ARCH_X[2]): 4 blocks
    add_parapet_blocks(BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2], 4)
    # Eastern span 2 (BRIDGE_ARCH_X[2] → BRIDGE_ARCH_X[3]): 3 blocks
    add_parapet_blocks(BRIDGE_ARCH_X[2], BRIDGE_ARCH_X[3], 3)
    # East flat span: west sub-span (BRIDGE_X2→BRIDGE_ARCH_X[4]) gets 3 north blocks; east sub-span open (matches ref)
    add_parapet_blocks(
        BRIDGE_X2,
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
            z_at_center=lambda cx: int(
                min(
                    deck_top_z(cx - BRIDGE_SQ_HW),
                    deck_top_z(cx),
                    deck_top_z(cx + BRIDGE_SQ_HW),
                )
            )
            + BRIDGE_PAR_H
            + BRIDGE_BLK_H // 2,
            north_brush=lambda cx, sy, bz: box(
                cx - BRIDGE_SQ_HW,
                BRIDGE_Y2 + sy,
                bz - BRIDGE_SQ_HH,
                cx + BRIDGE_SQ_HW,
                BRIDGE_Y2 + BRIDGE_SQ_D + sy,
                bz + BRIDGE_SQ_HH,
                Textures.RAIL,
            ),
            south_brush=lambda cx, sy, bz: box(
                cx - BRIDGE_SQ_HW,
                BRIDGE_Y1 - BRIDGE_SQ_D + sy,
                bz - BRIDGE_SQ_HH,
                cx + BRIDGE_SQ_HW,
                BRIDGE_Y1 + sy,
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
        BRIDGE_X2,
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
            BRIDGE_Y1 - BRIDGE_BLK_OVH,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            cx_walk_e + BRIDGE_BLK_HW,
            BRIDGE_Y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE_PAR_H + BRIDGE_BLK_H,
            Textures.CEMENT,
        )
    )
    # Extra block on west side of walkway opening (east face flush with WALK_X1)
    cx_walk_w = WALK_X1 - BRIDGE_BLK_HW
    BRUSHES.append(
        box(
            cx_walk_w - BRIDGE_BLK_HW,
            BRIDGE_Y1 - BRIDGE_BLK_OVH,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            cx_walk_w + BRIDGE_BLK_HW,
            BRIDGE_Y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE_PAR_H + BRIDGE_BLK_H,
            Textures.CEMENT,
        )
    )

    # ── Parapet handrail tubes (two 4×4 rods stacked, through parapet blocks/pillars) ─
    tube_ny1 = BRIDGE_Y2 - BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
    tube_ny2 = tube_ny1 + BRIDGE_TUBE_HW * 2
    tube_sy1 = BRIDGE_Y1 + BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
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
        # East flat section — straight BRIDGE_X2→pier, angled pier→world wall
        tube_base_z = BRIDGE_DZ2 + BRIDGE_PAR_H + tube_z_offset
        east_end_x = WORLD_X2 - WALL_T
        # North tube: straight then angled
        BRUSHES.append(
            box(
                BRIDGE_X2,
                tube_ny1,
                tube_base_z,
                BRIDGE_EAST_PIVOT_X,
                tube_ny2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        BRUSHES.append(
            shear_box_y(
                BRIDGE_EAST_PIVOT_X,
                tube_ny1,
                tube_base_z,
                east_end_x,
                tube_ny2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                BRIDGE_EAST_SHIFT_START,
                BRIDGE_EAST_SHIFT_END,
                Textures.RAIL,
            )
        )
        # South tube west piece (BRIDGE_X2→WALK_X1): before pier, straight
        BRUSHES.append(
            box(
                BRIDGE_X2,
                tube_sy1,
                tube_base_z,
                WALK_X1,
                tube_sy2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                Textures.RAIL,
            )
        )
        # South tube east piece (WALK_X2→world wall): straight to pier, then angled
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
        BRUSHES.append(
            shear_box_y(
                BRIDGE_EAST_PIVOT_X,
                tube_sy1,
                tube_base_z,
                east_end_x,
                tube_sy2,
                tube_base_z + BRIDGE_TUBE_HW * 2,
                BRIDGE_EAST_SHIFT_START,
                BRIDGE_EAST_SHIFT_END,
                Textures.RAIL,
            )
        )

    # ── Pillar posts (stone piers with arches) ───────────────────────────────────
    # Each pillar position now features a narrow arched pier supporting the deck.
    # Arch openings span most of the bridge N-S width (BRIDGE_Y2=136, bridge=272 units)
    # rin = half-width of clear opening; rout = outer radius of arch ring
    if SHOW_SUPPORTS:
        for px in BRIDGE_ARCH_X:
            if SHOW_SUPPORTS is not True and px not in SHOW_SUPPORTS:
                continue
            pdeck = deck_top_z(px)  # deck surface at this X
            ppar = pdeck + BRIDGE_PAR_H  # parapet top
            ppil = ppar + BRIDGE_PIL_EXTRA  # pillar post top
            pcap = ppil + BRIDGE_PIL_CAP_H  # cap slab top
            cy_n = BRIDGE_Y2 - BRIDGE_PAR_W // 2  # north cap centre Y
            cy_s = BRIDGE_Y1 + BRIDGE_PAR_W // 2  # south cap centre Y

            # Width of the pier in X (matches pillar post width)
            x1, x2 = px - BRIDGE_PIL_HW, px + BRIDGE_PIL_HW

            # Ceiling Z — use the higher of the two pier face deck-bottoms so stone
            # is flush with the bridge underside across the full pier X extent.
            pier_ceiling_z = max(int(deck_bot_z(x1)), int(deck_bot_z(x2)))

            # Arch opening varies by pillar type (outer / inner / centre)
            if px == 0:
                a_rout, a_rin = BRIDGE_PIL_CAP_OVHNTR_R
            elif abs(px) == max(abs(p) for p in BRIDGE_ARCH_X):
                a_rout, a_rin = BRIDGE_PIL_OUTER_R
            else:
                a_rout, a_rin = BRIDGE_PIL_INNER_R
            a_stilt = pier_ceiling_z - a_rout - FLOOR_Z2
            if a_stilt < 0:
                # Arch would overshoot the bridge bottom; cap rout so the crown
                # lands exactly at ceil_z (bridge deck underside).
                a_rout = pier_ceiling_z - FLOOR_Z2
                a_stilt = 0

            # Pin outer pier wall to exactly match the pillar tops above deck.
            # Cap a_rout so the arch ring never extends past BRIDGE_Y2 + BRIDGE_PIL_OVERHANG;
            # if rout was trimmed, recompute stilt so the arch crown still meets the deck.
            max_outer_radius = BRIDGE_Y2 + BRIDGE_PIL_OVERHANG
            if a_rout > max_outer_radius:
                a_rout = max_outer_radius
                a_stilt = pier_ceiling_z - a_rout - FLOOR_Z2
            arch_overhang = 0  # rout already reaches exactly the desired extent

            # Ramped plinth: outer piers ramp up on their outward face so players
            # can run up from outside. East piers: high east side; west piers: high west side.
            # Central / road piers get a flat plinth.
            if px > 0:
                # East of road — ramp slopes up toward east (low at x1, high at x2)
                base_ramp = (
                    FLOOR_Z2 + BRIDGE_PIL_BASE_H,
                    FLOOR_Z2 + BRIDGE_PIL_BASE_RAMP_H,
                )
            elif px < 0:
                # West of road — ramp slopes up toward west (high at x1, low at x2)
                base_ramp = (
                    FLOOR_Z2 + BRIDGE_PIL_BASE_RAMP_H,
                    FLOOR_Z2 + BRIDGE_PIL_BASE_H,
                )
            else:
                base_ramp = None  # centre pier — flat plinth

            # Add pier structure — easternmost pier gets a square opening, rest are arched
            if px == max(BRIDGE_ARCH_X):
                # Overhang must reach BRIDGE_Y2+BRIDGE_PIL_OVERHANG to match pillar tops above deck
                sq_overhang = BRIDGE_Y2 + BRIDGE_PIL_OVERHANG - a_rin
                BRUSHES.extend(
                    square_wall(
                        x1,
                        x2,
                        BRIDGE_Y1,
                        BRIDGE_Y2,
                        FLOOR_Z2,
                        pier_ceiling_z,
                        a_rin,
                        Textures.PILLAR,
                        overhang=sq_overhang,
                        base_h=BRIDGE_PIL_BASE_H,
                    )
                )
            else:
                BRUSHES.extend(
                    arch_wall(
                        x1,
                        x2,
                        BRIDGE_Y1,
                        BRIDGE_Y2,
                        FLOOR_Z2,
                        pier_ceiling_z,
                        a_rin,
                        a_rout,
                        A_SEGS,
                        Textures.PILLAR,
                        stilt_h=a_stilt,
                        overhang=arch_overhang,
                        base_h=BRIDGE_PIL_BASE_H,
                        base_ramp=base_ramp,
                        base_cap_h=0
                        if px == min(BRIDGE_ARCH_X)
                        else BRIDGE_PIL_BASE_CAP_H,
                        base_cap_tex=Textures.CEMENT,
                        base_cap_ovh=BRIDGE_PIL_BASE_CAP_OVH,
                    )
                )

            # Pillar tops (above deck, extend BRIDGE_PIL_OVERHANG past bridge edges and inward)
            pier_outer_y = (
                BRIDGE_Y2 + BRIDGE_PIL_OVERHANG
            )  # always overhang past bridge edge
            # North pillar top
            BRUSHES.append(
                box(
                    px - BRIDGE_PIL_HW,
                    BRIDGE_Y2 - BRIDGE_PAR_W - BRIDGE_PIL_OVERHANG,
                    pdeck,
                    px + BRIDGE_PIL_HW,
                    pier_outer_y,
                    ppil,
                    Textures.PILLAR,
                )
            )

            # South pillar top
            BRUSHES.append(
                box(
                    px - BRIDGE_PIL_HW,
                    -pier_outer_y,
                    pdeck,
                    px + BRIDGE_PIL_HW,
                    BRIDGE_Y1 + BRIDGE_PAR_W + BRIDGE_PIL_OVERHANG,
                    ppil,
                    Textures.PILLAR,
                )
            )

            # Fill gap between pier top and deck surface in the overhang zone
            pier_top_z = int(pdeck) - 16
            BRUSHES.append(
                box(x1, BRIDGE_Y2, pier_top_z, x2, pier_outer_y, pdeck, Textures.PILLAR)
            )  # north
            BRUSHES.append(
                box(
                    x1, -pier_outer_y, pier_top_z, x2, BRIDGE_Y1, pdeck, Textures.PILLAR
                )
            )  # south

            # Cement cap slab + pyramid on top of each stone pillar post
            cap_x1, cap_x2 = px - BRIDGE_PIL_PYR_W, px + BRIDGE_PIL_PYR_W
            north_cap_y1 = (
                BRIDGE_Y2 - BRIDGE_PAR_W - BRIDGE_PIL_OVERHANG - BRIDGE_PIL_CAP_IN_OVH
            )  # inward past pillar post
            north_cap_y2 = (
                BRIDGE_Y2 + BRIDGE_PIL_CAP_OUT_OVH
            )  # outward (north/road-facing) edge
            south_cap_y1 = (
                BRIDGE_Y1 - BRIDGE_PIL_CAP_OUT_OVH
            )  # outward (south/road-facing) edge
            south_cap_y2 = (
                BRIDGE_Y1 + BRIDGE_PAR_W + BRIDGE_PIL_OVERHANG + BRIDGE_PIL_CAP_IN_OVH
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
                    pcap + BRIDGE_PIL_PYR_H,
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
                    pcap + BRIDGE_PIL_PYR_H,
                    Textures.CEMENT,
                )
            )
            # Torch bases above pyramid apex — narrow post + wide cup
            pyramid_apex_z = pcap + BRIDGE_PIL_PYR_H
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

    # ── Teleport Arches at both ends of bridge ───────────────────────────────────
    for arch_x_start, arch_center_y in [
        (WORLD_X1 + WALL_T, 0.0),  # west arch — centred at y=0
        (
            WORLD_X2 - WALL_T - ARCH_SLAB_W,
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
                BRIDGE_Y1 - BRIDGE_PIL_OVERHANG + arch_center_y,
                FLOOR_Z2,
                arch_x2,
                BRIDGE_Y1 + arch_post_width + arch_center_y,
                arch_spring_z,
                Textures.PILLAR,
            )
        )
        # North post (extends to ground floor, with overhang)
        BRUSHES.append(
            box(
                arch_x1,
                BRIDGE_Y2 - arch_post_width + arch_center_y,
                FLOOR_Z2,
                arch_x2,
                BRIDGE_Y2 + BRIDGE_PIL_OVERHANG + arch_center_y,
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
                    ARCH_ROUT + BRIDGE_PIL_OVERHANG,
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
            "hint",
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
            "hint",
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
            "hint",
        )
    )
    BRUSHES.append(box(WORLD_X1, -140, FLOOR_Z1, WORLD_X2, -136, WORLD_Z2, "hint"))
    BRUSHES.append(box(WORLD_X1, 136, FLOOR_Z1, WORLD_X2, 140, WORLD_Z2, "hint"))

    # ════════════════════════════════════════════════════════════════════════════════
    # WALKWAY — flat bridge from south edge to building 2nd floor entrance
    # X=-64..64, Y=BRIDGE_Y1..KNOTT_Y2; flat at WALK_ZT1 = WALK_ZT2
    # ════════════════════════════════════════════════════════════════════════════════
    if KNOTT_WALKWAY_ENABLED:
        wk_zb1 = WALK_ZT1 - KNOTT_WALL  # slab bottom at bridge end
        wk_zb2 = WALK_ZT2 - KNOTT_WALL  # slab bottom at building end
        BRUSHES.append(
            ramp_slab_y(
                WALK_X1,
                WALK_X2,
                BRIDGE_Y1,
                KNOTT_Y2,
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
                WALK_X1 - BRIDGE_WALK_WALL,
                WALK_X1,
                BRIDGE_Y1,
                KNOTT_Y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1 + BRIDGE_PAR_H,
                WALK_ZT2 + BRIDGE_PAR_H,
                Textures.CEMENT,
            )
        )
        DETAIL_BRUSHES.append(
            ramp_slab_y(
                WALK_X2,
                WALK_X2 + BRIDGE_WALK_WALL,
                BRIDGE_Y1,
                KNOTT_Y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1 + BRIDGE_PAR_H,
                WALK_ZT2 + BRIDGE_PAR_H,
                Textures.CEMENT,
            )
        )
        # Handrail tubes along walkway sides, centred in the wall thickness
        for tube_z_offset in [BRIDGE_TUBE_RISE, BRIDGE_TUBE_RISE + BRIDGE_TUBE_GAP]:
            tube_base_z = WALK_ZT1 + BRIDGE_PAR_H + tube_z_offset
            ww_cx = BRIDGE_WALK_WALL // 2
            DETAIL_BRUSHES.append(
                box(
                    WALK_X1 - ww_cx - BRIDGE_TUBE_HW,
                    KNOTT_Y2,
                    tube_base_z,
                    WALK_X1 - ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE_Y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )
            DETAIL_BRUSHES.append(
                box(
                    WALK_X2 + ww_cx - BRIDGE_TUBE_HW,
                    KNOTT_Y2,
                    tube_base_z,
                    WALK_X2 + ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE_Y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )

    # ════════════════════════════════════════════════════════════════════════════════
    # ACCESSIBLE WALKWAY — N-S cement path at KH ground floor level (Z=KNOTT_GROUND_Z),
    # running alongside Pier 5 (west face).  Connects Knott Hall north face to the
    # bridge south edge, then wraps east via a short E-W ramp to the back-road west
    # sidewalk.  Provides ground-level access around Pier 5 without steps.
    # Spans Y=KNOTT_Y2..BRIDGE_Y1 (KH north face → bridge south edge).
    # ════════════════════════════════════════════════════════════════════════════════
    if KNOTT_WALKWAY_ENABLED:
        east_walk_center_x = BRIDGE_ACCESS_WALK_CENTER_X
        east_walk_half_width = BRIDGE_ACCESS_WALK_HALF_W
        east_walk_x2 = east_walk_center_x + east_walk_half_width  # 2152
        east_walk_y2 = (
            BRIDGE_Y2
            + BRIDGE_PIL_OVERHANG
            + BRIDGE_ACCESS_WALK_PIER_CLEARANCE
            + BRIDGE_ACCESS_WALK_NORTH_OFFSET
        )  # north anchor: ramp moved 80 units north
        terrain_z2 = int(
            KNOTT_GROUND_Z
            + (FLOOR_Z2 + CHARLES_WALK_H - KNOTT_GROUND_Z)
            * (east_walk_y2 - (KNOTT_Y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
            / (ENNIS_SW_EDGE - (KNOTT_Y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
        )
        # E-W extension — slopes east from terrain level down to back road sidewalk (Z=8) at KNOTT_X2
        east_walk_ext_y1 = east_walk_y2 - (east_walk_half_width * 2)
        east_walk_ext_y2 = east_walk_y2
        extension_terrain_z1 = int(
            KNOTT_GROUND_Z
            + (FLOOR_Z2 + CHARLES_WALK_H - KNOTT_GROUND_Z)
            * (east_walk_ext_y1 - (KNOTT_Y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
            / (ENNIS_SW_EDGE - (KNOTT_Y2 + BRIDGE_ACCESS_WALK_PIER_CLEARANCE))
        )
        extension_terrain_z2 = terrain_z2
        extension_terrain_z_west = (
            extension_terrain_z1 + extension_terrain_z2
        ) // 2  # Z at west end (N-S path side)
        DETAIL_BRUSHES.append(
            ramp_slab(
                east_walk_x2,
                KNOTT_X2,
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
        # Position just under the south edge of the bridge deck
        support_y_center = BRIDGE_Y1  # south edge of bridge = -136
        support_half_width = BRIDGE_SUPPORT_HALF_W  # half-depth of beam/piers (N-S)
        support_y1 = support_y_center - support_half_width
        support_y2 = support_y_center + support_half_width
        # Beam sits just below the walkway slab bottom
        beam_top_z = WALK_ZT1 - KNOTT_WALL  # bottom of walkway slab at bridge end
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
        rail_x1 = WALK_X1 - BRIDGE_WALK_WALL  # west rail outer edge
        rail_x2 = WALK_X2 + BRIDGE_WALK_WALL  # east rail outer edge
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
    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
