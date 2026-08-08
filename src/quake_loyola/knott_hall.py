"""Knott Hall shell: four walls and a roof, no floors.

Sized and placed against the real terrain modeled in
``terrain/knott_hall.py``. The interior is left as one big open volume so
the footprint and height can be iterated on before any floors, windows, or
interior detail are added. The old, more detailed prototype (facade
coursing, windows, elevator/stair core, interior partitions) was retired;
its generically reusable pieces (stairwell, elevator shaft, corner window,
fascia sign) now live in ``geometry/prefabs.py`` for reuse once floors are
added back here.
"""

from .constants import (
    BRIDGE_DZ2,
    BRIDGE_PILLAR_HW,
    KNOTT_SIGN_H,
    KNOTT_SIGN_PADDING,
    KNOTT_SIGN_PX_H,
    KNOTT_SIGN_PX_W,
    KNOTT_SIGN_TEXT,
    KNOTT_SIGN_Z_OFFSET,
    KNOTT_Y1,
    KNOTT_Y2,
    PIER4_X,
    PIER5_X,
    Textures,
)
from .geometry import box, brush_ent, fascia_sign, polygon_prism

WALL_T = 16
ROOF_T = 16
PARAPET_H = 24  # Raised lip around the roof edge, per satellite reference —
# the roof deck itself sits at the wall top (z2), with the parapet
# standing PARAPET_H above it, so the rim reads as proud of the roof
# without dipping the roof deck down into the window tops (which also
# stop at z2).
BUILDING_H = 1523  # Was 1640; net effect of two window panes removed (2 x
# 78 units) plus half a pane (39 units, EXTRA_BASE_H below) added back so
# the ground-floor door/entrance is 1.5 panes tall instead of 1, with every
# other window pane on every wall staying exactly 78 tall/unchanged.
CORNER_CUT_DEPTH = 160  # How far south (into the building) both notches cut.
CORNER_CUT_W_NE = 128  # East notch inset from KH_X2.
CORNER_CUT_W_NW = 188  # West notch inset from KH_X1 — moved east more than the NE side.

SHIFT_NORTH = 220  # Moved a little closer to the bridge deck (+Y).
SOUTH_EXTEND = 1088  # Extra length added to the south end (-Y): 160 to fit 3
# groups of 6 side windows (with 5 mullions each) plus 2 inter-group gaps,
# then a further 928 lengthening the whole hall southward (+25%, then +10%
# twice more). SIDE_WIN_W grew alongside it (48 -> 72, x1.5, tracking the
# 1815 -> 2743 length) so the side-wall window band scales with the building
# instead of being stranded in a sea of blank wall — _side_windows keeps the
# band centred on the wall on its own.

# Side-wall window layout (east/west walls, full bridge-deck-to-roof
# height, same style as the front openings): 3 groups of 6 windows per
# side, each group split by 5 mullions, with a ~4-window-wide gap between
# groups and a margin at each end.
SIDE_WIN_W = 72  # Width of each individual window pane.
SIDE_WIN_GROUPS = 3
SIDE_WINS_PER_GROUP = 6
SIDE_GROUP_GAP_WINS = 4  # Gap between groups, in window-widths.
SIDE_WIN_MARGIN = 32  # Margin from each end of the wall to the first/last
# window group.

# Widened to align the east/west walls with the outer pier faces of the
# Pier 4-Pier 5 bridge span facing Knott Hall (BRIDGE_ENABLED_SPAN_KH).
KH_X1 = PIER4_X - BRIDGE_PILLAR_HW  # West wall flush with Pier 4's west face.
KH_X2 = PIER5_X + BRIDGE_PILLAR_HW  # East wall flush with Pier 5's east face.
KH_Y1 = KNOTT_Y1 + SHIFT_NORTH - SOUTH_EXTEND
KH_Y2 = KNOTT_Y2 + SHIFT_NORTH

# The north edge steps in at both the NW and NE corners: the footprint is
# the union of a full-width lower rectangle (up to KH_NOTCH_Y) and a narrower
# upper rectangle (KH_NOTCH_Y to KH_Y2, inset by CORNER_CUT_W_NW/NE on each side)
# rather than one plain rectangle. Both corners cut the same depth south
# (KH_NOTCH_Y), but the west corner insets further east than the east corner.
KH_NOTCH_Y = KH_Y2 - CORNER_CUT_DEPTH
KH_NORTH_X1 = KH_X1 + CORNER_CUT_W_NW
KH_NORTH_X2 = KH_X2 - CORNER_CUT_W_NE

# The real terrain hillside slopes down noticeably (and non-linearly near
# the southeast corner) under the footprint — the _kh_hill_ground_z helper
# is only an approximation of the actual generated terrain mesh and
# underestimates how low it dips in places (real mesh reaches ~z10 near
# the SE corner vs. the helper's ~z44). Rather than chase the exact real
# minimum, walls extend down to WORLD_FLOOR_Z (-16), the base terrain fill
# level used everywhere else in the map, guaranteeing no gap regardless of
# local terrain undulation.
KH_GROUND_Z = -16

# Front openings (start one beam segment (104 units) above bridge-deck
# height and run up to the roof; below that the wall is solid, including
# across the deck itself): a center opening on the north wall, and
# matching openings on the south-facing notch-ledge walls (the walls that
# bound the NW/NE corner cuts from the south) flanking it. The center and
# west openings share the same size; the east one is narrower.
OPENING_BOTTOM_Z = BRIDGE_DZ2 + 104  # Bumped up one beam segment (104 units)
# so the former bottom-most opening segment is now the top-most segment
# instead (paired with the BUILDING_H reduction above).
CENTER_OPENING_W = 140
CENTER_OPENING_OFFSET = 100  # Shift east, closer to the sign (but not past it).
WEST_OPENING_W = 96
EAST_OPENING_W = 56
# Second, true-ground-level door (independent of the elevated bridge-deck
# entrance above) — east of the center door, giving direct outside access
# to the auditorium on the west side of the ground floor without a rider
# having to cut through it.
GROUND_DOOR_W = 112
GROUND_DOOR_H = 128
GROUND_DOOR_OFFSET = 180  # East of the center door's opening (offset 100).
GROUND_DOOR_BOTTOM = 100  # Raised above the building's foundation footer to
# roughly match real grade near the north wall (terrain there sits well
# above KH_GROUND_Z).
MULLION_W = 22  # Vertical divider (base) thickness, bumped up from the
# historical KH value (12) for better visibility.
MULLION_PROUD = 12  # How far the mullion's pointed edge projects past the wall.
# Divider counts per opening, east to west. 2 dividers sit at the opening's
# edges; 3 dividers add one more centered between them.
EAST_OPENING_MULLIONS = 2
CENTER_OPENING_MULLIONS = 3
WEST_OPENING_MULLIONS = 3

# Horizontal cross beams, same texture as the mullions but thinner (BEAM_H)
# and flat (not triangular), protruding only slightly (BEAM_PROUD). No floor
# plan exists yet, so beam
# heights are derived from an assumed 4 floors above bridge-deck level: one
# beam at each of the 3 floor lines, plus 3 more evenly spaced between each
# pair of floor lines (and below/above the end floor lines), i.e. the
# opening height is divided into NUM_FLOORS * BEAM_SEGMENTS_PER_FLOOR equal
# segments and a beam sits at every interior division line. Segments per
# floor bumped from 3 to 4 (seg_h ~78, down from ~104) so each window pane
# reads closer to square (matching the ~48-70-wide panes) without going as
# far as the ~52-tall panes from a 6-segment split, which looked too dense.
NUM_FLOORS = 4
BEAM_SEGMENTS_PER_FLOOR = 4  # 1 floor line + 3 in-between beams per floor.
# Two panes shorter than NUM_FLOORS * BEAM_SEGMENTS_PER_FLOOR (16 -> 14):
# the building's height (BUILDING_H above) is reduced by exactly two panes'
# worth, so the window/beam layout must divide the (now shorter) opening
# into two fewer equal segments to keep each pane's height (and therefore
# its near-square proportions) the same as before.
WINDOW_SEGMENTS = NUM_FLOORS * BEAM_SEGMENTS_PER_FLOOR - 2
BEAM_H = 2  # Beam thickness (much thinner than the mullions).
BEAM_PROUD = 4  # Protrusion past the wall's outer face so beams render
# distinctly instead of z-fighting with the coplanar window-fill brush.
# Half of the nominal ~78 pane height. On every wall, this band (right
# above OPENING_BOTTOM_Z, below the WINDOW_SEGMENTS-tall regular window
# grid) is normally solid — except on the entrance wall, where it's opened
# up as part of the door instead, making the ground-floor door/entrance
# 1.5 panes tall while every other pane stays exactly one nominal pane
# (78) tall.
EXTRA_BASE_H = 39

# Fascia sign tuning (north/bridge-facing wall) — mirrors the old KH
# module's sign but re-centered/re-leveled for this shell's footprint.
SIGN_EAST_MARGIN = 32  # Gap from the (narrower) north wall's east edge.
SIGN_PANEL_SCALE = 0.7  # Shrink the sign backing panel a little further.
SIGN_LETTER_SCALE = 0.7  # Shrink the lettering more, leaving side padding.
SIGN_SIDE_PADDING = 24  # Extra fixed gap between the glyphs and panel edge.
SIGN_Z_ADJUST = 32  # Lower the sign a little from its default offset.


def _mullion_prism(mx, y1, y2, bottom_z, top_z, tex):
    """A triangular (in cross-section) vertical mullion.

    Its flat base runs along the wall's inner face (``y1``); it tapers to a
    point projecting ``MULLION_PROUD`` past the wall's outer face (``y2``),
    pointy end facing outward.
    """
    pts = [
        (mx, y1),
        (mx + MULLION_W, y1),
        (mx + MULLION_W / 2, y2 + MULLION_PROUD),
    ]
    return polygon_prism(pts, bottom_z, top_z, tex)


def _cross_beam(x1, x2, y1, y2, bz, tex):
    """A horizontal cross beam, protruding a small amount past the wall face."""
    return box(x1, y1, bz - BEAM_H / 2, x2, y2 + BEAM_PROUD, bz + BEAM_H / 2, tex)


def _side_windows(x1, x2, wy1, wy2, z1, z2, bottom_z, tex, outer_x):
    """Windows (with mullions/beams) set into an east/west side wall.

    The wall runs from ``wy1`` to ``wy2`` in Y; ``x1``/``x2`` are the wall's
    X bounds and ``outer_x`` is whichever of them faces outward (used for
    the mullions' pointy tip and the beams' protrusion, mirroring
    ``_wall_with_opening``'s treatment of ``y2``). ``SIDE_WIN_GROUPS``
    groups of ``SIDE_WINS_PER_GROUP`` windows each (``SIDE_WIN_W`` wide,
    split by mullions at every internal division and gap of
    ``SIDE_GROUP_GAP_WINS`` window-widths between groups) run from
    ``bottom_z + EXTRA_BASE_H`` to ``z2`` (side walls have no
    entrance/door, so ``EXTRA_BASE_H`` is always a solid band here — see
    ``_wall_with_opening``), with solid wall on either side and below it.

    Returns ``(structural, detail)`` — the plain wall boxes (kept as
    worldspawn) and the window/mullion/beam brushes (returned separately so
    the caller can wrap them in a ``func_detail`` entity; the sheer number
    of thin overlapping brushes across a long wall span otherwise blows up
    vis portal counts).
    """
    win_bottom = bottom_z + EXTRA_BASE_H
    inner_x = x1 if outer_x == x2 else x2
    group_w = SIDE_WINS_PER_GROUP * SIDE_WIN_W
    gap_w = SIDE_GROUP_GAP_WINS * SIDE_WIN_W
    total_w = (
        2 * SIDE_WIN_MARGIN + SIDE_WIN_GROUPS * group_w + (SIDE_WIN_GROUPS - 1) * gap_w
    )
    wall_len = wy2 - wy1
    # Center the whole window band on the wall, absorbing any slack evenly.
    start_y = wy1 + (wall_len - total_w) / 2 + SIDE_WIN_MARGIN

    structural = []
    detail = []
    if bottom_z > z1:
        structural.append(box(x1, wy1, z1, x2, wy2, bottom_z, tex))
    if win_bottom > bottom_z:
        structural.append(box(x1, wy1, bottom_z, x2, wy2, win_bottom, tex))
    y = start_y
    prev_end = wy1
    for _g in range(SIDE_WIN_GROUPS):
        g_y1, g_y2 = y, y + group_w
        # Solid wall from the previous group's end (or wall start) up to
        # this group's start.
        if g_y1 > prev_end:
            structural.append(box(x1, prev_end, win_bottom, x2, g_y1, z2, tex))
        # Windows within the group, separated by mullions.
        for i in range(SIDE_WINS_PER_GROUP):
            wy_a = g_y1 + i * SIDE_WIN_W
            wy_b = wy_a + SIDE_WIN_W
            detail.append(box(x1, wy_a, win_bottom, x2, wy_b, z2, Textures.WINDOW_KH))
        for i in range(SIDE_WINS_PER_GROUP + 1):
            my = g_y1 + i * SIDE_WIN_W - MULLION_W / 2
            outer_pt_x = outer_x + MULLION_PROUD * (1 if outer_x > inner_x else -1)
            pts = [
                (inner_x, my),
                (inner_x, my + MULLION_W),
                (outer_pt_x, my + MULLION_W / 2),
            ]
            detail.append(polygon_prism(pts, win_bottom, z2, Textures.CEMENT))
        segments = WINDOW_SEGMENTS
        seg_h = (z2 - win_bottom) / segments
        beam_outer = outer_x + BEAM_PROUD * (1 if outer_x > inner_x else -1)
        bx1, bx2 = (inner_x, beam_outer) if outer_x > inner_x else (beam_outer, inner_x)
        for i in range(1, segments):
            bz = win_bottom + i * seg_h
            detail.append(
                box(
                    bx1,
                    g_y1,
                    bz - BEAM_H / 2,
                    bx2,
                    g_y2,
                    bz + BEAM_H / 2,
                    Textures.FENCE,
                )
            )
        prev_end = g_y2
        y = g_y2 + gap_w
    if prev_end < wy2:
        structural.append(box(x1, prev_end, win_bottom, x2, wy2, z2, tex))
    return structural, detail


def _wall_with_opening(
    x1,
    y1,
    x2,
    y2,
    z1,
    z2,
    open_w,
    bottom_z,
    tex,
    offset=0,
    mullions=0,
    mullion_tex=None,
    fill_tex=None,
    beams=False,
    beam_tex=None,
    entrance=False,
    ground_door_w=0,
    ground_door_offset=0,
    ground_door_h=None,
    ground_door_bottom=None,
):
    """A thin wall (in Y) split around a centered opening above bridge level.

    The wall is solid from ``z1`` up to ``bottom_z`` (bridge-deck height);
    above that, an opening spans ``open_w`` in X, centered on the wall (plus
    ``offset``), up to ``z2``, with solid wall on either side of the
    opening. From ``bottom_z`` to ``bottom_z + EXTRA_BASE_H``, the opening
    itself is solid too — except when ``entrance`` is True, where it's
    opened up as part of the ground-level doorway instead, making the door
    1.5 panes tall while every other pane stays exactly one nominal pane
    tall. ``mullions`` triangular vertical dividers (pointy end facing
    outward past the wall's outer face, textured with ``mullion_tex``,
    defaulting to ``tex``) are placed across the opening's width — 2 sit at
    its edges, 3 add one more centered between them. If ``fill_tex`` is
    given, a thin masked (window-pane) brush fills the opening instead of
    leaving it fully open. If ``beams`` is True, thin horizontal cross beams
    (``BEAM_H`` thick, protruding ``BEAM_PROUD`` past the wall face,
    textured with ``beam_tex``, defaulting to ``mullion_tex``/``tex``) are
    placed at each interior division line of
    ``WINDOW_SEGMENTS`` equal segments spanning from
    ``bottom_z + EXTRA_BASE_H`` to the opening's height. If ``entrance`` is
    True, the lowest segment (plus the ``EXTRA_BASE_H`` band below it) is
    left fully open (no window fill, and any center — i.e. non-edge —
    mullion stops above it) to serve as a ground-level doorway.

    ``ground_door_w`` (if non-zero) cuts a second, independent doorway into
    the solid base band below ``bottom_z`` — i.e. at true ground level,
    unlike ``entrance`` (which only affects the elevated bridge-deck-height
    opening above). It's centered on the wall plus ``ground_door_offset``,
    left fully open from ``ground_door_bottom`` (defaulting to ``z1``) up
    to ``ground_door_bottom + ground_door_h`` (``ground_door_h`` defaults
    to the full base band height, ``bottom_z - z1``, if not given).
    """
    win_bottom = bottom_z + EXTRA_BASE_H
    cx = (x1 + x2) / 2 + offset
    ox1, ox2 = cx - open_w / 2, cx + open_w / 2
    segments = WINDOW_SEGMENTS
    seg_h = (z2 - win_bottom) / segments
    entrance_top = win_bottom + seg_h if entrance else win_bottom
    boxes = []
    if bottom_z > z1:
        if ground_door_w > 0:
            gcx = (x1 + x2) / 2 + ground_door_offset
            gx1, gx2 = gcx - ground_door_w / 2, gcx + ground_door_w / 2
            door_bottom = ground_door_bottom if ground_door_bottom is not None else z1
            door_top = door_bottom + (
                ground_door_h if ground_door_h is not None else bottom_z - z1
            )
            if gx1 > x1:
                boxes.append(box(x1, y1, z1, gx1, y2, bottom_z, tex))
            if gx2 < x2:
                boxes.append(box(gx2, y1, z1, x2, y2, bottom_z, tex))
            if door_bottom > z1:
                boxes.append(box(gx1, y1, z1, gx2, y2, door_bottom, tex))
            if door_top < bottom_z:
                boxes.append(box(gx1, y1, door_top, gx2, y2, bottom_z, tex))
        else:
            boxes.append(box(x1, y1, z1, x2, y2, bottom_z, tex))
    if x1 < ox1:
        boxes.append(box(x1, y1, bottom_z, ox1, y2, z2, tex))
    if ox2 < x2:
        boxes.append(box(ox2, y1, bottom_z, x2, y2, z2, tex))
    if not entrance and win_bottom > bottom_z:
        boxes.append(box(ox1, y1, bottom_z, ox2, y2, win_bottom, tex))
    if fill_tex is not None:
        if entrance_top > bottom_z:
            boxes.append(box(ox1, y1, entrance_top, ox2, y2, z2, fill_tex))
        else:
            boxes.append(box(ox1, y1, bottom_z, ox2, y2, z2, fill_tex))
    if mullions > 0:
        m_tex = mullion_tex if mullion_tex is not None else tex
        if mullions == 2:
            positions = [ox1, ox2]
        elif mullions == 3:
            positions = [ox1, (ox1 + ox2) / 2, ox2]
        else:
            gap = open_w / (mullions - 1)
            positions = [ox1 + i * gap for i in range(mullions)]
        edges = {ox1, ox2}
        for mx in positions:
            m_bottom = bottom_z if mx in edges else entrance_top
            mx -= MULLION_W / 2
            boxes.append(_mullion_prism(mx, y1, y2, m_bottom, z2, m_tex))
    if beams:
        b_tex = beam_tex if beam_tex is not None else (mullion_tex or tex)
        for i in range(1, segments):
            bz = win_bottom + i * seg_h
            boxes.append(_cross_beam(ox1, ox2, y1, y2, bz, b_tex))
    return boxes


def _build_walls(z1, z2):
    """Build the four wall groups (side windows, south, notch ledges, north
    opening) between ``z1`` (ground) and ``z2`` (roofline).

    Returns:
        tuple[list, list, list]: ``(wall_brushes, west_detail, east_detail)``
        — ``west_detail``/``east_detail`` are the func_detail side-window
        brushes, kept separate so ``build()`` can fold them into the same
        func_detail entity as the parapet.
    """
    west_struct, west_detail = _side_windows(
        KH_X1,
        KH_X1 + WALL_T,
        KH_Y1,
        KH_NOTCH_Y,
        z1,
        z2,
        OPENING_BOTTOM_Z,
        Textures.PIER_STONE,
        outer_x=KH_X1,
    )
    east_struct, east_detail = _side_windows(
        KH_X2 - WALL_T,
        KH_X2,
        KH_Y1,
        KH_NOTCH_Y,
        z1,
        z2,
        OPENING_BOTTOM_Z,
        Textures.PIER_STONE,
        outer_x=KH_X2,
    )

    wall_brushes = [
        # West wall (lower rectangle only — stops at the NW notch) — has
        # 3 groups of side windows.
        *west_struct,
        # East wall (lower rectangle only — stops at the NE notch) — has
        # 3 groups of side windows.
        *east_struct,
        # South wall (between the two side walls)
        box(
            KH_X1 + WALL_T,
            KH_Y1,
            z1,
            KH_X2 - WALL_T,
            KH_Y1 + WALL_T,
            z2,
            Textures.PIER_STONE,
        ),
        # NW notch ledge (faces the cut-away square, north-facing) — has the
        # west front opening above bridge-deck height.
        *_wall_with_opening(
            KH_X1 + WALL_T,
            KH_NOTCH_Y - WALL_T,
            KH_NORTH_X1,
            KH_NOTCH_Y,
            z1,
            z2,
            WEST_OPENING_W,
            OPENING_BOTTOM_Z,
            Textures.PIER_STONE,
            mullions=WEST_OPENING_MULLIONS,
            mullion_tex=Textures.CEMENT,
            fill_tex=Textures.WINDOW_KH,
            beams=True,
            beam_tex=Textures.FENCE,
        ),
        # NE notch ledge (faces the cut-away square, north-facing) — has the
        # (narrower) east front opening above bridge-deck height.
        *_wall_with_opening(
            KH_NORTH_X2,
            KH_NOTCH_Y - WALL_T,
            KH_X2 - WALL_T,
            KH_NOTCH_Y,
            z1,
            z2,
            EAST_OPENING_W,
            OPENING_BOTTOM_Z,
            Textures.PIER_STONE,
            mullions=EAST_OPENING_MULLIONS,
            mullion_tex=Textures.CEMENT,
            fill_tex=Textures.WINDOW_KH,
            beams=True,
            beam_tex=Textures.FENCE,
        ),
        # Upper rectangle west wall (inward face of the NW notch)
        box(
            KH_NORTH_X1,
            KH_NOTCH_Y,
            z1,
            KH_NORTH_X1 + WALL_T,
            KH_Y2,
            z2,
            Textures.PIER_STONE,
        ),
        # Upper rectangle east wall (inward face of the NE notch)
        box(
            KH_NORTH_X2 - WALL_T,
            KH_NOTCH_Y,
            z1,
            KH_NORTH_X2,
            KH_Y2,
            z2,
            Textures.PIER_STONE,
        ),
        # North wall (upper rectangle, between the two notches) — has the
        # center front opening above bridge-deck height, same size as the
        # west opening.
        *_wall_with_opening(
            KH_NORTH_X1 + WALL_T,
            KH_Y2 - WALL_T,
            KH_NORTH_X2 - WALL_T,
            KH_Y2,
            z1,
            z2,
            CENTER_OPENING_W,
            OPENING_BOTTOM_Z,
            Textures.PIER_STONE,
            offset=CENTER_OPENING_OFFSET,
            mullions=CENTER_OPENING_MULLIONS,
            mullion_tex=Textures.CEMENT,
            fill_tex=Textures.WINDOW_KH,
            beams=True,
            beam_tex=Textures.FENCE,
            entrance=True,
            ground_door_w=GROUND_DOOR_W,
            ground_door_offset=GROUND_DOOR_OFFSET,
            ground_door_h=GROUND_DOOR_H,
            ground_door_bottom=GROUND_DOOR_BOTTOM,
        ),
    ]
    return wall_brushes, west_detail, east_detail


def _build_roof(roof_z1, roof_z2):
    """Build the roof deck brushes, inset behind the parapet ring.

    Split into 3 spans along the north edge: the two outer spans (under
    the NW/NE notch-ledge walls) are additionally inset by ``WALL_T`` on
    the north side so they don't sit flush against those walls' inward
    faces; the middle span (open transition into the upper rectangle) can
    run flush to ``KH_NOTCH_Y`` since there's no wall face there.
    """
    return [
        box(
            KH_X1 + WALL_T,
            KH_Y1 + WALL_T,
            roof_z1,
            KH_NORTH_X1,
            KH_NOTCH_Y - WALL_T,
            roof_z2,
            Textures.ROOF_KH,
        ),
        box(
            KH_NORTH_X1,
            KH_Y1 + WALL_T,
            roof_z1,
            KH_NORTH_X2,
            KH_NOTCH_Y,
            roof_z2,
            Textures.ROOF_KH,
        ),
        box(
            KH_NORTH_X2,
            KH_Y1 + WALL_T,
            roof_z1,
            KH_X2 - WALL_T,
            KH_NOTCH_Y - WALL_T,
            roof_z2,
            Textures.ROOF_KH,
        ),
        # Roof, upper (notched) rectangle — inset behind the parapet ring.
        box(
            KH_NORTH_X1 + WALL_T,
            KH_NOTCH_Y,
            roof_z1,
            KH_NORTH_X2 - WALL_T,
            KH_Y2 - WALL_T,
            roof_z2,
            Textures.ROOF_KH,
        ),
    ]


def _build_parapet(z2, parapet_z2):
    """Build the parapet lip: a raised rim tracing the wall footprint,
    standing ``PARAPET_H`` above the wall top/roof deck — matches the
    satellite reference showing a lip around the roof edge with the roof
    set slightly below it. Wrapped in func_detail (like the side-window
    detail) since it's a thin non-structural rim that doesn't need to
    affect vis/portal generation, and keeps qbsp's edge count for the
    standard BSP format in range.
    """
    return [
        box(
            KH_X1,
            KH_Y1,
            z2,
            KH_X1 + WALL_T,
            KH_NOTCH_Y,
            parapet_z2,
            Textures.PIER_STONE,
        ),
        box(
            KH_X2 - WALL_T,
            KH_Y1,
            z2,
            KH_X2,
            KH_NOTCH_Y,
            parapet_z2,
            Textures.PIER_STONE,
        ),
        box(
            KH_X1 + WALL_T,
            KH_Y1,
            z2,
            KH_X2 - WALL_T,
            KH_Y1 + WALL_T,
            parapet_z2,
            Textures.PIER_STONE,
        ),
        box(
            KH_X1 + WALL_T,
            KH_NOTCH_Y - WALL_T,
            z2,
            KH_NORTH_X1,
            KH_NOTCH_Y,
            parapet_z2,
            Textures.PIER_STONE,
        ),
        box(
            KH_NORTH_X2,
            KH_NOTCH_Y - WALL_T,
            z2,
            KH_X2 - WALL_T,
            KH_NOTCH_Y,
            parapet_z2,
            Textures.PIER_STONE,
        ),
        box(
            KH_NORTH_X1,
            KH_NOTCH_Y,
            z2,
            KH_NORTH_X1 + WALL_T,
            KH_Y2,
            parapet_z2,
            Textures.PIER_STONE,
        ),
        box(
            KH_NORTH_X2 - WALL_T,
            KH_NOTCH_Y,
            z2,
            KH_NORTH_X2,
            KH_Y2,
            parapet_z2,
            Textures.PIER_STONE,
        ),
        box(
            KH_NORTH_X1 + WALL_T,
            KH_Y2 - WALL_T,
            z2,
            KH_NORTH_X2 - WALL_T,
            KH_Y2,
            parapet_z2,
            Textures.PIER_STONE,
        ),
    ]


def _build_sign(z1):
    """Build the fascia sign on the north (bridge-facing) wall, mirroring
    the old KH module's sign but re-centered/re-leveled for this shell's
    footprint and height (no floors to anchor to here, so it's centered
    vertically). Kept snug against the east edge of the (now-narrower)
    north wall.
    """
    sign_px_w = int(KNOTT_SIGN_PX_W * SIGN_LETTER_SCALE)
    sign_px_h = int(KNOTT_SIGN_PX_H * SIGN_LETTER_SCALE)
    sign_h = int(KNOTT_SIGN_H * SIGN_PANEL_SCALE)
    sign_padding = int(KNOTT_SIGN_PADDING * SIGN_PANEL_SCALE) + SIGN_SIDE_PADDING
    sign_char_w = (4 + 1) * sign_px_w
    sign_total_w = len(KNOTT_SIGN_TEXT) * sign_char_w - sign_px_w
    # Panel is sized off the glyph width plus a fixed side gap (rather than
    # a second scale factor) so it always leaves visible padding, regardless
    # of how the letter pixel sizes happen to round.
    sign_half_w = sign_total_w // 2 + sign_padding
    sign_cx = KH_NORTH_X2 - WALL_T - SIGN_EAST_MARGIN - sign_half_w
    sign_z_center = z1 + BUILDING_H // 2 + KNOTT_SIGN_Z_OFFSET + SIGN_Z_ADJUST
    return fascia_sign(
        KNOTT_SIGN_TEXT,
        sign_cx,
        KH_Y2,
        sign_z_center,
        panel_h=sign_h,
        panel_padding=sign_padding,
        px_w=sign_px_w,
        px_h=sign_px_h,
        panel_tex=Textures.CEMENT,
        text_tex=Textures.RAIL,
    )


def build():
    """Build the Knott Hall shell: four walls and a roof, no floors.

    Returns:
        tuple[list, list]: ``(brushes, entities)`` for the building shell.
    """
    z1 = KH_GROUND_Z
    z2 = z1 + BUILDING_H
    parapet_z2 = z2 + PARAPET_H
    roof_z1 = z2
    roof_z2 = roof_z1 + ROOF_T

    wall_brushes, west_detail, east_detail = _build_walls(z1, z2)
    roof_brushes = _build_roof(roof_z1, roof_z2)
    parapet_detail = _build_parapet(z2, parapet_z2)
    sign_brushes = _build_sign(z1)

    brushes = [*wall_brushes, *roof_brushes, *sign_brushes]
    entities = [brush_ent("func_detail", west_detail + east_detail + parapet_detail)]

    return brushes, entities
