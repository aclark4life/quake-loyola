from .constants import (
    A_SEGS,
    BRIDGE_ARCH_X,
    BRIDGE_DZ2,
    BRIDGE_EAST_PIVOT_X,
    BRIDGE_EAST_SHIFT_END,
    BRIDGE_EAST_SHIFT_START,
    BRIDGE_PAR_H,
    BRIDGE_PAR_W,
    BRIDGE_PIL_BASE_CAP_H,
    BRIDGE_PIL_BASE_CAP_OVH,
    BRIDGE_PIL_BASE_H,
    BRIDGE_PIL_BASE_RAMP_H,
    BRIDGE_PIL_CAP_H,
    BRIDGE_PIL_CAP_IN_OVH,
    BRIDGE_PIL_CAP_OUT_OVH,
    BRIDGE_PIL_EXTRA,
    BRIDGE_PIL_HW,
    BRIDGE_PIL_OVERHANG,
    BRIDGE_PIL_PYR_H,
    BRIDGE_PIL_PYR_W,
    BRIDGE_SEG_SPAN_W,
    BRIDGE_SEG_W,
    BRIDGE_X1,
    BRIDGE_X2,
    BRIDGE_Y1,
    BRIDGE_Y2,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_SW_EDGE,
    FLOOR_Z1,
    FLOOR_Z2,
    INDENT,
    KH_DRIVEWAY_CORRIDOR_X1,
    KH_DRIVEWAY_CORRIDOR_X2,
    KH_GROUND_Z,
    KH_ORIG_CX,
    KH_WALKWAY_ENABLED,
    KH_WALL,
    KH_X1,
    KH_X2,
    KH_Y1,
    KH_Y2,
    ROAD_X2,
    SHOW_SUPPORTS,
    WALK_X1,
    WALK_X2,
    WALK_ZT1,
    WALK_ZT2,
    WALL_T,
    WORLD_X1,
    WORLD_X2,
    WORLD_Y1,
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
            WORLD_X2 - WALL_T,
            BRIDGE_Y2,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            BRIDGE_EAST_SHIFT_START,
            BRIDGE_EAST_SHIFT_END,
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
            WORLD_X2 - WALL_T,
            BRIDGE_Y1 + BRIDGE_PAR_W,
            BRIDGE_DZ2 + BRIDGE_PAR_H,
            BRIDGE_EAST_SHIFT_START,
            BRIDGE_EAST_SHIFT_END,
            Textures.CEMENT,
        )
    )

    for i in range(BRIDGE_SEG_SPAN_W):
        sx1 = BRIDGE_X1 + i * BRIDGE_SEG_W
        sx2 = sx1 + BRIDGE_SEG_W
        pb1, pb2 = deck_top_z(sx1), deck_top_z(sx2)  # parapet base follows deck top
        pt1, pt2 = (
            pb1 + BRIDGE_PAR_H,
            pb2 + BRIDGE_PAR_H,
        )  # parapet top = base + BRIDGE_PAR_H
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
    BRIDGE_BLK_HW = 24  # block half-width in X (48 units wide along bridge)
    BRIDGE_BLK_H = 36  # block height above parapet top
    BRIDGE_BLK_OVH = 0  # blocks flush with outer bridge wall
    BRIDGE_BLK_PIR_M = (
        BRIDGE_PIL_HW + BRIDGE_BLK_HW + 4
    )  # clearance from pier centre to block centre

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
        """Add evenly-spaced cement blocks atop N and S parapets in a bridge span.

        n_south defaults to n.  South blocks that overlap the walkway gap
        (WALK_X1..WALK_X2) are skipped automatically.
        east_margin_n overrides east_margin for north blocks only.
        y_shift_fn(cx) returns a southward Y offset for angled spans (e.g. east flat span).
        """
        n_s = n if n_south is None else n_south
        mx0 = west_margin if west_margin is not None else BRIDGE_BLK_PIR_M
        mx1 = east_margin if east_margin is not None else BRIDGE_BLK_PIR_M
        mx1_n = east_margin_n if east_margin_n is not None else mx1
        x0 = x_start + mx0
        x1_n = x_end - mx1_n
        x1_s = x_end - mx1
        for k in range(n):
            cx = x0 + (x1_n - x0) * (k + 1) / (n + 1)
            sy = y_shift_fn(cx) if y_shift_fn else 0.0
            # Use minimum parapet top across block width so block never floats above parapet
            bz = (
                min(
                    deck_top_z(cx - BRIDGE_BLK_HW),
                    deck_top_z(cx),
                    deck_top_z(cx + BRIDGE_BLK_HW),
                )
                + BRIDGE_PAR_H
            )
            BRUSHES.append(
                box(
                    cx - BRIDGE_BLK_HW,
                    BRIDGE_Y2 - BRIDGE_PAR_W + sy,
                    bz,
                    cx + BRIDGE_BLK_HW,
                    BRIDGE_Y2 + BRIDGE_BLK_OVH + sy,
                    bz + BRIDGE_BLK_H,
                    Textures.CEMENT,
                )
            )
        for k in range(n_s):
            cx = x0 + (x1_s - x0) * (k + 1) / (n_s + 1)
            sy = y_shift_fn(cx) if y_shift_fn else 0.0
            bz = (
                min(
                    deck_top_z(cx - BRIDGE_BLK_HW),
                    deck_top_z(cx),
                    deck_top_z(cx + BRIDGE_BLK_HW),
                )
                + BRIDGE_PAR_H
            )
            if not (cx - BRIDGE_BLK_HW < WALK_X2 and cx + BRIDGE_BLK_HW > WALK_X1):
                BRUSHES.append(
                    box(
                        cx - BRIDGE_BLK_HW,
                        BRIDGE_Y1 - BRIDGE_BLK_OVH + sy,
                        bz,
                        cx + BRIDGE_BLK_HW,
                        BRIDGE_Y1 + BRIDGE_PAR_W + sy,
                        bz + BRIDGE_BLK_H,
                        Textures.CEMENT,
                    )
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
    BRIDGE_SQ_HW = 8  # half-width in X (16 units wide)
    BRIDGE_SQ_HH = 6  # half-height in Z (12 units tall)
    BRIDGE_SQ_D = 1  # protrusion depth (1 unit proud)

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
        n_s = n if n_south is None else n_south
        mx0 = west_margin if west_margin is not None else BRIDGE_BLK_PIR_M
        mx1 = east_margin if east_margin is not None else BRIDGE_BLK_PIR_M
        mx1_n = east_margin_n if east_margin_n is not None else mx1
        x0 = x_start + mx0
        x1_n = x_end - mx1_n
        x1_s = x_end - mx1
        for k in range(n):
            cx = int(x0 + (x1_n - x0) * (k + 1) / (n + 1))
            sy = y_shift_fn(cx) if y_shift_fn else 0.0
            bz = (
                int(
                    min(
                        deck_top_z(cx - BRIDGE_SQ_HW),
                        deck_top_z(cx),
                        deck_top_z(cx + BRIDGE_SQ_HW),
                    )
                )
                + BRIDGE_PAR_H
                + BRIDGE_BLK_H // 2
            )
            BRUSHES.append(
                box(
                    cx - BRIDGE_SQ_HW,
                    BRIDGE_Y2 + sy,
                    bz - BRIDGE_SQ_HH,
                    cx + BRIDGE_SQ_HW,
                    BRIDGE_Y2 + BRIDGE_SQ_D + sy,
                    bz + BRIDGE_SQ_HH,
                    Textures.RAIL,
                )
            )
        for k in range(n_s):
            cx = int(x0 + (x1_s - x0) * (k + 1) / (n_s + 1))
            sy = y_shift_fn(cx) if y_shift_fn else 0.0
            if not (cx - BRIDGE_SQ_HW < WALK_X2 and cx + BRIDGE_SQ_HW > WALK_X1):
                bz = (
                    int(
                        min(
                            deck_top_z(cx - BRIDGE_SQ_HW),
                            deck_top_z(cx),
                            deck_top_z(cx + BRIDGE_SQ_HW),
                        )
                    )
                    + BRIDGE_PAR_H
                    + BRIDGE_BLK_H // 2
                )
                BRUSHES.append(
                    box(
                        cx - BRIDGE_SQ_HW,
                        BRIDGE_Y1 - BRIDGE_SQ_D + sy,
                        bz - BRIDGE_SQ_HH,
                        cx + BRIDGE_SQ_HW,
                        BRIDGE_Y1 + sy,
                        bz + BRIDGE_SQ_HH,
                        Textures.RAIL,
                    )
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
    BRIDGE_TUBE_HW = 2  # half-width of tube in Y and Z (4 units total)
    BRIDGE_TUBE_RISE = 10  # raise tubes above parapet top
    BRIDGE_TUBE_GAP = 12  # vertical gap between tube centres
    tube_ny1 = BRIDGE_Y2 - BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
    tube_ny2 = tube_ny1 + BRIDGE_TUBE_HW * 2
    tube_sy1 = BRIDGE_Y1 + BRIDGE_PAR_W // 2 - BRIDGE_TUBE_HW
    tube_sy2 = tube_sy1 + BRIDGE_TUBE_HW * 2

    for tube_z_offset in [BRIDGE_TUBE_RISE, BRIDGE_TUBE_RISE + BRIDGE_TUBE_GAP]:
        for span_index in range(BRIDGE_SEG_SPAN_W):
            span_x1 = BRIDGE_X1 + span_index * BRIDGE_SEG_W
            span_x2 = span_x1 + BRIDGE_SEG_W
            tube_z1 = deck_top_z(span_x1) + BRIDGE_PAR_H + tube_z_offset
            tube_z2 = deck_top_z(span_x2) + BRIDGE_PAR_H + tube_z_offset
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
    BRIDGE_PIL_OUTER_R = (140, 72)  # narrower outer piers flanking road
    BRIDGE_PIL_INNER_R = (160, 84)  # slightly wider inner piers
    BRIDGE_PIL_CAP_OVHNTR_R = (160, 90)  # widest opening at centre
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
                        px - 3,
                        torch_center_y - 3,
                        pyramid_apex_z,
                        px + 3,
                        torch_center_y + 3,
                        pyramid_apex_z + 16,
                        Textures.CEMENT,
                    )
                )
                # Wider brick cup/bracket at top holds the flame
                BRUSHES.append(
                    box(
                        px - 5,
                        torch_center_y - 5,
                        pyramid_apex_z + 16,
                        px + 5,
                        torch_center_y + 5,
                        pyramid_apex_z + 20,
                        Textures.BRICK,
                    )
                )

            # Abutment pier (westernmost): solid cement fill + arch teleport on west face
            if px == min(BRIDGE_ARCH_X):
                # Cement fill starts 16 units east of pier face to make room for arch
                BRUSHES.append(
                    box(
                        x1 + 16,
                        -a_rin,
                        FLOOR_Z2,
                        x2,
                        a_rin,
                        int(pdeck) - 16,
                        Textures.CEMENT,
                    )
                )
                # Arch-shaped teleport flush with the west face (recessed into pier)
                teleport_stilt_height = pier_top_z - FLOOR_Z2 - a_rin - 8
                abutment_teleport_brush = arch_fill(
                    x1 + 2,
                    x1 + 18,
                    0.0,
                    FLOOR_Z2,
                    a_rin,
                    A_SEGS,
                    Textures.TELEPORT,
                    stilt_h=teleport_stilt_height,
                )
                abutment_teleport_dest_z = int(pdeck) + 40  # spawn height above deck

    # ── Teleport Arches at both ends of bridge ───────────────────────────────────
    ARCH_RIN = 96
    ARCH_ROUT = 136  # Fills the bridge width (updated to match BRIDGE_Y2=136)
    ARCH_STILT_H = 96  # Height of straight sides before arch springs
    ARCH_SLAB_W = 32  # Thickness of the arch in X

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

    # ════════════════════════════════════════════════════════════════════════════════
    # WALKWAY — flat bridge from south edge to building 2nd floor entrance
    # X=-64..64, Y=BRIDGE_Y1..KH_Y2; flat at WALK_ZT1 = WALK_ZT2
    # ════════════════════════════════════════════════════════════════════════════════
    if KH_WALKWAY_ENABLED:
        wk_zb1 = WALK_ZT1 - KH_WALL  # slab bottom at bridge end
        wk_zb2 = WALK_ZT2 - KH_WALL  # slab bottom at building end
        BRUSHES.append(
            ramp_slab_y(
                WALK_X1,
                WALK_X2,
                BRIDGE_Y1,
                KH_Y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1,
                WALK_ZT2,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )
        # Side rails slope with the ramp (32-unit thick walls so tubes sit centred)
        PBCS_WALK_WALL = 32
        BRUSHES.append(
            ramp_slab_y(
                WALK_X1 - PBCS_WALK_WALL,
                WALK_X1,
                BRIDGE_Y1,
                KH_Y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1 + BRIDGE_PAR_H,
                WALK_ZT2 + BRIDGE_PAR_H,
                Textures.CEMENT,
            )
        )
        BRUSHES.append(
            ramp_slab_y(
                WALK_X2,
                WALK_X2 + PBCS_WALK_WALL,
                BRIDGE_Y1,
                KH_Y2,
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
            ww_cx = PBCS_WALK_WALL // 2
            BRUSHES.append(
                box(
                    WALK_X1 - ww_cx - BRIDGE_TUBE_HW,
                    KH_Y2,
                    tube_base_z,
                    WALK_X1 - ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE_Y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )
            BRUSHES.append(
                box(
                    WALK_X2 + ww_cx - BRIDGE_TUBE_HW,
                    KH_Y2,
                    tube_base_z,
                    WALK_X2 + ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE_Y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )

    # ════════════════════════════════════════════════════════════════════════════════
    # ACCESSIBLE WALKWAY — N-S cement path at KH ground floor level (Z=KH_GROUND_Z),
    # running alongside Pier 5 (west face).  Connects Knott Hall north face to the
    # bridge south edge, then wraps east via a short E-W ramp to the back-road west
    # sidewalk.  Provides ground-level access around Pier 5 without steps.
    # Spans Y=KH_Y2..BRIDGE_Y1 (KH north face → bridge south edge).
    # ════════════════════════════════════════════════════════════════════════════════
    if KH_WALKWAY_ENABLED:
        east_walk_center_x = 2120
        east_walk_half_width = 32
        east_walk_x2 = east_walk_center_x + east_walk_half_width  # 2152
        east_walk_y2 = (
            BRIDGE_Y2 + BRIDGE_PIL_OVERHANG + 96 + 80
        )  # north anchor: ramp moved 80 units north
        terrain_z2 = int(
            KH_GROUND_Z
            + (FLOOR_Z2 + CHARLES_WALK_H - KH_GROUND_Z)
            * (east_walk_y2 - (KH_Y2 + 96))
            / (ENNIS_SW_EDGE - (KH_Y2 + 96))
        )
        # E-W extension — slopes east from terrain level down to back road sidewalk (Z=8) at KH_X2
        east_walk_ext_y1 = east_walk_y2 - (east_walk_half_width * 2)
        east_walk_ext_y2 = east_walk_y2
        extension_terrain_z1 = int(
            KH_GROUND_Z
            + (FLOOR_Z2 + CHARLES_WALK_H - KH_GROUND_Z)
            * (east_walk_ext_y1 - (KH_Y2 + 96))
            / (ENNIS_SW_EDGE - (KH_Y2 + 96))
        )
        extension_terrain_z2 = terrain_z2
        extension_terrain_z_west = (
            extension_terrain_z1 + extension_terrain_z2
        ) // 2  # Z at west end (N-S path side)
        BRUSHES.append(
            ramp_slab(
                east_walk_x2,
                KH_X2,
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
    if KH_WALKWAY_ENABLED:
        # Position just under the south edge of the bridge deck
        support_y_center = BRIDGE_Y1  # south edge of bridge = -136
        support_half_width = 16  # half-depth of beam/piers (N-S)
        support_y1 = support_y_center - support_half_width
        support_y2 = support_y_center + support_half_width
        # Beam sits just below the walkway slab bottom
        beam_top_z = WALK_ZT1 - KH_WALL  # bottom of walkway slab at bridge end
        beam_height = 20
        beam_bottom_z = beam_top_z - beam_height
        # Span between the two bridge arch piers flanking the walkway (east span)
        beam_x1 = BRIDGE_ARCH_X[3]
        beam_x2 = BRIDGE_ARCH_X[4]
        # Horizontal crossbeam
        BRUSHES.append(
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
        rail_x1 = WALK_X1 - PBCS_WALK_WALL  # west rail outer edge
        rail_x2 = WALK_X2 + PBCS_WALK_WALL  # east rail outer edge
        west_support_piers = [
            int(beam_x1 + (rail_x1 - beam_x1) * f) for f in (0.28, 0.63, 0.93)
        ]
        east_support_piers = [
            int(rail_x2 + (beam_x2 - rail_x2) * f) for f in (0.0, 0.45)
        ]
        support_pier_xs = west_support_piers + east_support_piers
        support_pier_half_width = 20
        for pier_x in support_pier_xs:
            BRUSHES.append(
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

    # ════════════════════════════════════════════════════════════════════════════════
    # KNOTT HALL — south campus, 4-floor playable tower
    # Footprint: X=1186 to 1686, Y=-800 to -256, Z=0 to 512
    # North face faces the bridge; ground-level entrance at X=1372..1500
    # Lift shaft at center-north rises from ground to rooftop
    # ════════════════════════════════════════════════════════════════════════════════

    # ── Hill terrain under Knott Hall ─────────────────────────────────────────────
    # Bridge deck is raised; building sits on a hill so its 2nd floor meets the walkway.
    if KH_GROUND_Z > FLOOR_Z2:
        west_ramp_x1 = ROAD_X2 + CHARLES_WALK_W  # east edge of east sidewalk = 336
        west_ramp_x2 = KH_X1  # ramp rises all the way to building west face
        # Solid hill fill under the entire building footprint — split to exclude indent pockets
        # so indents are recessed at all heights down to ground level
        for fill_x1, fill_y1, fill_x2, fill_y2 in [
            (KH_X1 + INDENT, KH_Y1, KH_X2 - INDENT, KH_Y1 + INDENT),  # south strip
            (KH_X1, KH_Y1 + INDENT, KH_X2, KH_Y2 - INDENT),  # middle strip
            (KH_X1 + 2 * INDENT, KH_Y2 - INDENT, KH_X2 - INDENT, KH_Y2),  # north strip
        ]:
            BRUSHES.append(
                box(
                    fill_x1,
                    fill_y1,
                    FLOOR_Z2,
                    fill_x2,
                    fill_y2,
                    KH_GROUND_Z,
                    Textures.WALL,
                )
            )
        # NW indent floor — flush with exterior ground
        BRUSHES.append(
            box(
                KH_X1,
                KH_Y2 - INDENT,
                FLOOR_Z1,
                KH_X1 + 2 * INDENT,
                KH_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # (No flat east fill — the back road section provides its own sloped fill there)
        # West hill — ramp from sidewalk height at Charles St up to building ground level
        west_ramp_north_y = KH_Y2 - INDENT * 3 // 4
        BRUSHES.append(
            ramp_slab(
                west_ramp_x1,
                west_ramp_x2,
                WORLD_Y1 + WALL_T,
                west_ramp_north_y,
                FLOOR_Z1,
                FLOOR_Z1,
                FLOOR_Z2 + CHARLES_WALK_H,
                KH_GROUND_Z,
                Textures.GROUND,
            )
        )
        # Flat ground from ramp north edge to building face (west of KH_X1)
        BRUSHES.append(
            box(
                west_ramp_x1,
                west_ramp_north_y,
                FLOOR_Z1,
                west_ramp_x2,
                KH_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # South terrain fill — flat ground at building level behind south wall to east world edge
        BRUSHES.append(
            box(
                KH_X1,
                WORLD_Y1 + WALL_T,
                FLOOR_Z1,
                WORLD_X2 - WALL_T,
                KH_Y1,
                KH_GROUND_Z,
                Textures.WALL,
            )
        )
        # Flat ground in front of KH (north face to Ennis sidewalk edge), flush with sidewalk
        # Split around KH entrance strip (KH_ENT_X1..KH_ENT_X2) to let cement apron show.
        # Between Pier 4 (PIER4_X) and Pier 5 (PIER5_X): gradual slope from KH_GROUND_Z
        # at the north KH face (KH_Y2) down to sidewalk height at the Ennis sidewalk (ENNIS_SW_EDGE).
        kh_entry_x1 = KH_ORIG_CX - 64
        kh_entry_x2 = KH_ORIG_CX + 64
        east_ramp_x1 = kh_entry_x2  # east of entrance opening
        east_ramp_x2 = KH_X2 - INDENT  # west edge of NE indent
        east_platform_depth = (
            96  # N-S depth of side-step platform — slope must not cover this
        )
        # West section of seg1 — stays at sidewalk height (up to NW indent of KH)
        segment1_split_x = (
            KH_X1 + 2 * INDENT
        )  # = NW indent X, aligns raised ground with NW corner
        BRUSHES.append(
            box(
                west_ramp_x1,
                KH_Y2,
                FLOOR_Z1,
                segment1_split_x,
                ENNIS_SW_EDGE,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # East section of seg1 (NW indent → entrance) — slopes from KH_GROUND_Z at KH face to
        # sidewalk height at Ennis sidewalk
        BRUSHES.append(
            ramp_slab_y(
                segment1_split_x,
                kh_entry_x1,
                KH_Y2,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                FLOOR_Z1,
                KH_GROUND_Z,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # Seg2 (east of entrance to NE indent)
        # east_walk_ext_y1_val / east_walk_ext_y2_val bracket the E-W ramp (Y=264..328)
        east_walk_ext_y1_val = BRIDGE_Y2 + BRIDGE_PIL_OVERHANG + 96 + 80 - 64  # 264
        east_walk_ext_y2_val = BRIDGE_Y2 + BRIDGE_PIL_OVERHANG + 96 + 80  # 328

        # Terrain Z at the ramp Y-midpoint — this is the west-end height of the ramp
        def terrain_z_at(y):
            return int(
                KH_GROUND_Z
                + (FLOOR_Z2 + CHARLES_WALK_H - KH_GROUND_Z)
                * (y - (KH_Y2 + 96))
                / (ENNIS_SW_EDGE - (KH_Y2 + 96))
            )

        extension_terrain_z_west = (
            terrain_z_at(east_walk_ext_y1_val) + terrain_z_at(east_walk_ext_y2_val)
        ) // 2
        # Full sloped terrain Y=-160..264 (path zone starts at ramp south edge)
        BRUSHES.append(
            ramp_slab_y(
                kh_entry_x2,
                east_ramp_x2,
                KH_Y2 + east_platform_depth,
                east_walk_ext_y1_val,
                FLOOR_Z1,
                FLOOR_Z1,
                KH_GROUND_Z,
                terrain_z_at(east_walk_ext_y1_val),
                Textures.GROUND,
            )
        )
        # Accessible path pad — flat cement aligned with ramp (Y=264..328, Z=extension_terrain_z_west)
        BRUSHES.append(
            box(
                kh_entry_x2,
                east_walk_ext_y1_val,
                FLOOR_Z1,
                east_ramp_x2,
                east_walk_ext_y2_val,
                extension_terrain_z_west,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )
        # North section (Y=328..504): sloped terrain continues
        BRUSHES.append(
            ramp_slab_y(
                kh_entry_x2,
                east_ramp_x2,
                east_walk_ext_y2_val,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                FLOOR_Z1,
                terrain_z_at(east_walk_ext_y2_val),
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # NE indent ground — south of ramp (Y=-160..264): full ground, no cement needed
        BRUSHES.append(
            box(
                east_ramp_x2,
                KH_Y2 + east_platform_depth,
                FLOOR_Z1,
                KH_DRIVEWAY_CORRIDOR_X1,
                east_walk_ext_y1_val,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # North of E-W extension (restore ground fully)
        BRUSHES.append(
            box(
                east_ramp_x2,
                east_walk_ext_y2_val,
                FLOOR_Z1,
                KH_DRIVEWAY_CORRIDOR_X1,
                ENNIS_SW_EDGE,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # Seg3 (east of back-road corridor to world wall) — beyond Pier 5, stays at sidewalk height
        BRUSHES.append(
            box(
                KH_DRIVEWAY_CORRIDOR_X2,
                KH_Y2,
                FLOOR_Z1,
                WORLD_X2 - WALL_T,
                ENNIS_SW_EDGE,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        # East of entrance: flat platform at walkway level + steps going east down to ground
        east_platform_x1 = east_ramp_x1  # KH_ENT_X2
        east_platform_x2 = KH_X2
        east_step_count = 4
        east_step_rise = (KH_GROUND_Z - (FLOOR_Z2 + CHARLES_WALK_H)) // east_step_count
        east_step_depth = 24
        east_steps_width = east_step_count * east_step_depth
        east_steps_x1 = (
            east_platform_x2 - east_steps_width
        )  # steps recessed, end flush with east wall
        # Flat platform at KH_GROUND_Z (west of steps)
        BRUSHES.append(
            box(
                east_platform_x1,
                KH_Y2,
                FLOOR_Z1,
                east_steps_x1,
                KH_Y2 + east_platform_depth,
                KH_GROUND_Z,
                Textures.CEMENT,
            )
        )
        # Steps going east (downhill in X), flush with KH east wall
        for step_index in range(east_step_count):
            step_z = KH_GROUND_Z - (step_index + 1) * east_step_rise
            step_x1 = east_steps_x1 + step_index * east_step_depth
            step_x2 = step_x1 + east_step_depth
            BRUSHES.append(
                box(
                    step_x1,
                    KH_Y2,
                    FLOOR_Z1,
                    step_x2,
                    KH_Y2 + east_platform_depth,
                    step_z,
                    Textures.CEMENT,
                )
            )
        # Small cement connector — bridges step bottom to back road west sidewalk (32 units wide)
        BRUSHES.append(
            box(
                KH_X2,
                KH_Y2,
                FLOOR_Z1,
                KH_X2 + CHARLES_WALK_W,
                KH_Y2 + east_platform_depth,
                FLOOR_Z2 + CHARLES_WALK_H,
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
    return BRUSHES, ENTITIES
