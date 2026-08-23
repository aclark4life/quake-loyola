"""Generic multi-storey building helpers.

These were factored out of the retired west-campus dorm prototype (the
detailed shells with per-floor windows, gabled roofs, chimneys and
entrance grilles that used to live in ``west_campus.py``). Nothing here
knows about the dorms specifically — every function takes explicit
bounds and textures — so they can be reused when the dorms, or any other
multi-storey building, are rebuilt.
"""

from .primitives import box, box_with_hole, ramp_slab


def floor_levels(base_z, floor_h, floors, *, start_floor=1):
    """Yield ``(floor_index, deck_z)`` for each storey deck stacked from ``base_z``.

    ``deck_z`` is the walking surface of storey ``floor_index`` — the plane a
    player stands on, which is what :func:`floor_plate` builds down from and
    what :func:`~quake_loyola.geometry.prefabs.stairwell` expects in its
    ``floor_surfaces`` argument.

    This is *not* :func:`floor_window_levels`, which returns the window band
    inset within each storey; that band is offset up from the deck and is the
    wrong number to build a slab at.

    ``start_floor`` defaults to 1 because storey 0's deck is ``base_z`` itself
    — the ground, which is normally already terrain or a foundation slab, so
    plating it again would z-fight. Pass ``start_floor=0`` when you do want the
    ground included, as ``stairwell()`` does: it climbs from each surface to
    ``surface + floor_h``, so it needs the ground deck to build the first
    flight. The top of the building (``floor_index == floors``) is the roof and
    is never yielded.
    """
    if floor_h <= 0:
        raise ValueError(f"floor_levels: floor_h must be > 0, got {floor_h}")
    for floor_index in range(start_floor, floors):
        yield floor_index, base_z + floor_index * floor_h


def floor_plate(x1, y1, x2, y2, deck_z, t, tex, voids=(), **kw):
    """Return the brushes for one storey deck, minus any rectangular ``voids``.

    The slab hangs *below* its walking surface: it spans ``deck_z - t`` to
    ``deck_z``, so a ``deck_z`` from :func:`floor_levels` puts the player's
    feet exactly on ``deck_z``.

    ``voids`` are ``(x1, y1, x2, y2)`` rectangles to omit — stair and elevator
    penetrations, atrium wells. Each is clipped to the plate, and any that
    falls outside it entirely is dropped, so a caller can pass a shaft's full
    footprint without first working out which floors it actually crosses.

    Raises ``ValueError`` for a degenerate footprint or a non-positive
    thickness.
    """
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    if x1 == x2 or y1 == y2:
        raise ValueError(
            f"floor_plate: degenerate (zero-area) plate x=({x1}, {x2}) y=({y1}, {y2})"
        )
    if t <= 0:
        raise ValueError(f"floor_plate: t must be > 0, got {t}")

    zb, zt = deck_z - t, deck_z
    clamped = []
    for vx1, vy1, vx2, vy2 in voids:
        if vx1 > vx2:
            vx1, vx2 = vx2, vx1
        if vy1 > vy2:
            vy1, vy2 = vy2, vy1
        cx1, cx2 = max(vx1, x1), min(vx2, x2)
        cy1, cy2 = max(vy1, y1), min(vy2, y2)
        if cx1 < cx2 and cy1 < cy2:
            clamped.append((cx1, cy1, cx2, cy2))

    if not clamped:
        return [box(x1, y1, zb, x2, y2, zt, tex, **kw)]
    if len(clamped) == 1:
        vx1, vy1, vx2, vy2 = clamped[0]
        return box_with_hole(x1, y1, zb, x2, y2, zt, vx1, vy1, vx2, vy2, tex, **kw)

    # Two or more voids can't be expressed as one ring of four brushes, so cut
    # the plate on every void edge and keep the cells no void covers. This is
    # the XY twin of layered_wall()'s XZ split; it stays separate because that
    # one also retextures the faces an opening exposes, which a deck has no use
    # for, and because merging them would reorder existing wall brushes.
    xs = sorted({x1, x2} | {v[0] for v in clamped} | {v[2] for v in clamped})
    ys = sorted({y1, y2} | {v[1] for v in clamped} | {v[3] for v in clamped})
    out = []
    for cx1, cx2 in zip(xs, xs[1:], strict=False):
        for cy1, cy2 in zip(ys, ys[1:], strict=False):
            if any(
                vx1 <= cx1 and cx2 <= vx2 and vy1 <= cy1 and cy2 <= vy2
                for vx1, vy1, vx2, vy2 in clamped
            ):
                continue
            out.append(box(cx1, cy1, zb, cx2, cy2, zt, tex, **kw))
    return out


def floor_window_levels(base_z, floor_h, floors, win_hh, *, start_floor=0):
    """Yield ``(floor_index, z_bottom, z_top)`` for each floor's window band.

    The band of half-height ``win_hh`` is vertically centred within each
    ``floor_h``-tall storey stacked upwards from ``base_z``.
    """
    lo = (floor_h - win_hh * 2) // 2
    hi = lo + win_hh * 2
    for floor_index in range(start_floor, floors):
        floor_z = base_z + floor_index * floor_h
        yield floor_index, floor_z + lo, floor_z + hi


def floor_window_openings(
    centers,
    base_z,
    floor_h,
    floors,
    win_hw,
    win_hh,
    *,
    start_floor=0,
    double=False,
    include=None,
):
    """Return ``(span1, z_bottom, span2, z_top)`` openings for a wall face.

    Args:
        centers: Along-wall centre coordinates (X for a north/south face,
            Y for an east/west face).
        base_z: Ground-floor elevation of the building interior.
        floor_h: Storey height.
        floors: Total storey count.
        win_hw: Window half-width along the wall.
        win_hh: Window half-height.
        start_floor: First storey to punch windows into.
        double: Emit a pair of adjacent windows per centre instead of one.
        include: Optional ``(center, floor_index) -> bool`` filter.

    Returns:
        list[tuple]: Openings in the form accepted by
        :func:`~quake_loyola.geometry.structures.layered_wall` and friends.
    """
    openings = []
    for floor_index, zb, zt in floor_window_levels(
        base_z, floor_h, floors, win_hh, start_floor=start_floor
    ):
        for center in centers:
            if include and not include(center, floor_index):
                continue
            if double:
                openings.append((center - win_hw * 2, zb, center, zt))
                openings.append((center, zb, center + win_hw * 2, zt))
            else:
                openings.append((center - win_hw, zb, center + win_hw, zt))
    return openings


def wall_runs(face_specs, tex):
    """Return wall brushes for a list of ``(builder, args, openings)`` specs.

    Each spec's ``builder`` is a wall constructor such as
    :func:`~quake_loyola.geometry.structures.layered_wall` or
    :func:`~quake_loyola.geometry.structures.layered_wall_y`; it is called
    as ``builder(*args, openings, tex)``.
    """
    brushes = []
    for builder, args, openings in face_specs:
        brushes.extend(builder(*args, openings, tex))
    return brushes


def frame_runs(frame_specs, tex, *, fd, margin=0):
    """Return window/door trim brushes for a list of frame specs.

    Each spec is ``(builder, openings, wall_pos, wall_dir, kwargs)`` where
    ``builder`` is :func:`~quake_loyola.geometry.structures.win_frame_xwall`
    or :func:`~quake_loyola.geometry.structures.win_frame_ywall`, and each
    opening is ``(span1, z_bottom, span2, z_top)``.
    """
    brushes = []
    for builder, openings, wall_pos, wall_dir, kwargs in frame_specs:
        for span1, zb, span2, zt in openings:
            brushes += builder(
                span1,
                span2,
                zb,
                zt,
                wall_pos,
                wall_dir,
                tex,
                fd=fd,
                margin=margin,
                **kwargs,
            )
    return brushes


def gable_roof_west_half(x1, cx, y1, y2, eave_z, ridge_z, slab_t, tex, ts=None):
    """Return the west (rising) slab of a gabled roof ridged at ``cx``."""
    return ramp_slab(
        x1, cx, y1, y2, eave_z, eave_z, eave_z + slab_t, ridge_z, tex, ts=ts
    )


def gable_roof_east_half(cx, x2, y1, y2, eave_z, ridge_z, top_z, tex, ts=None):
    """Return the east (falling) slab of a gabled roof ridged at ``cx``.

    ``top_z`` is the slab's top elevation at ``x2``; pass
    ``eave_z + slab_t`` for a symmetric roof, or a lower value to shave the
    east slope (e.g. to clear a chimney).
    """
    return ramp_slab(cx, x2, y1, y2, eave_z, eave_z, ridge_z, top_z, tex, ts=ts)


def gable_roof(x1, cx, x2, y1, y2, eave_z, ridge_z, slab_t, tex, ts=None):
    """Return both slabs of a symmetric gabled roof ridged at ``cx``."""
    return [
        gable_roof_west_half(x1, cx, y1, y2, eave_z, ridge_z, slab_t, tex, ts=ts),
        gable_roof_east_half(
            cx, x2, y1, y2, eave_z, ridge_z, eave_z + slab_t, tex, ts=ts
        ),
    ]


def chimney_stack(x1, y1, x2, y2, z1, z2, wall_t, tex):
    """Return the four walls of a hollow chimney stack.

    ``x1..x2`` / ``y1..y2`` bound the flue; the masonry sits outside it,
    thickened by ``wall_t`` on every side.
    """
    return [
        box(x1 - wall_t, y1 - wall_t, z1, x2 + wall_t, y1, z2, tex),
        box(x1 - wall_t, y2, z1, x2 + wall_t, y2 + wall_t, z2, tex),
        box(x1 - wall_t, y1, z1, x1, y2, z2, tex),
        box(x2, y1, z1, x2 + wall_t, y2, z2, tex),
    ]


def transom_grille_ywall(
    x_face, depth, y1, y2, z1, z2, tex, *, beam_h=6, mull_w=6, mullions=5
):
    """Return a mullioned transom grille set into an east/west wall face.

    The grille is a thin plate centred on ``x_face`` spanning ``y1..y2``,
    with a beam at ``z1`` and ``z2`` and ``mullions`` evenly spaced
    vertical bars between them.
    """
    gx1 = x_face - depth / 2
    gx2 = x_face + depth / 2
    brushes = [
        box(gx1, y1, z1 - beam_h, gx2, y2, z1, tex),
        box(gx1, y1, z2 - beam_h, gx2, y2, z2, tex),
    ]
    span = y2 - y1
    for k in range(mullions):
        my = y1 + span * k // max(mullions - 1, 1)
        brushes.append(box(gx1, my - mull_w // 2, z1, gx2, my + mull_w // 2, z2, tex))
    return brushes


def straight_stair_x(x1, y1, y2, base_z, top_z, steps, rise, run, tex):
    """Return a straight stair run along +X.

    The first tread's top sits at ``top_z`` and each one after it steps by
    ``rise`` — negative to descend eastward. Every tread is solid down to
    ``base_z``, so a run laid on a hillside doubles as its own retaining
    structure and stays walkable from either end.
    """
    return [
        box(
            x1 + i * run,
            y1,
            base_z,
            x1 + (i + 1) * run,
            y2,
            top_z + i * rise,
            tex,
        )
        for i in range(steps)
    ]


def straight_stair_y(x1, x2, y1, base_z, top_z, steps, rise, run, tex):
    """Return a straight stair run along +Y — ``straight_stair_x`` rotated.

    ``rise`` is negative to descend northward, which is how the hillside
    walks use it.
    """
    return [
        box(
            x1,
            y1 + i * run,
            base_z,
            x2,
            y1 + (i + 1) * run,
            top_z + i * rise,
            tex,
        )
        for i in range(steps)
    ]
