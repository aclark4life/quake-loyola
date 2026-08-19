"""Generic multi-storey building helpers.

These were factored out of the retired west-campus dorm prototype (the
detailed shells with per-floor windows, gabled roofs, chimneys and
entrance grilles that used to live in ``west_campus.py``). Nothing here
knows about the dorms specifically — every function takes explicit
bounds and textures — so they can be reused when the dorms, or any other
multi-storey building, are rebuilt.
"""

from .primitives import box, ramp_slab


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
