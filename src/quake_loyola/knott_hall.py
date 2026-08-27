"""Knott Hall shell: four walls, a roof, and all five storey floors.

Sized and placed against the real terrain modeled in
``terrain/knott_hall.py``. The interior was left as one big open volume so
the footprint and height could be iterated on before any floors, windows,
or interior detail were added; every storey is now decked. Ground and
entry land at ``GROUND_FLOOR_Z`` and ``ENTRY_FLOOR_Z`` — the north door's
threshold and the bridge-level entrance's sill, so you walk in level at
both — and the three above them land at ``UPPER_FLOOR_ZS``, the same beam
lines the facade's window grid already divides into. The old, more
detailed prototype (facade coursing, windows, elevator/stair core,
interior partitions) was retired; its generically reusable pieces
(stairwell, elevator shaft, corner window, fascia sign) now live in
``geometry/prefabs.py`` for reuse as the rest of the interior (stairs,
partitions) is added back here.
"""

from .constants import (
    BRIDGE_CENTER_SPAN_OFFSET,
    BRIDGE_DZ2,
    BRIDGE_PILLAR_HW,
    FLOOR_Z2,
    KNOTT_CORE_WALL_JOINT_D,
    KNOTT_CORE_WALL_JOINT_LEN,
    KNOTT_CORE_WALL_JOINT_W,
    KNOTT_LIFT_CAR_D,
    KNOTT_LIFT_CAR_GAP,
    KNOTT_LIFT_CAR_H,
    KNOTT_LIFT_CAR_SPEED,
    KNOTT_LIFT_CAR_T,
    KNOTT_LIFT_CAR_TARGET,
    KNOTT_LIFT_CAR_W,
    KNOTT_LIFT_CAR_WAIT,
    KNOTT_LIFT_SILL_PROUD,
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
from .constants import (
    KNOTT_BUILDING_H as BUILDING_H,
)
from .constants import (
    KNOTT_PARAPET_H as PARAPET_H,
)
from .constants import (
    KNOTT_ROOF_T as ROOF_T,
)
from .constants import (
    KNOTT_WALL_T as WALL_T,
)
from .geometry import (
    box,
    brush_ent,
    carve_box,
    fascia_sign,
    floor_plate,
    polygon_prism,
    wall_with_joints,
)

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
# The bridge-level entrance's own sill. The rest of the facade's opening
# grid starts a beam segment higher (OPENING_BOTTOM_Z above), which would
# leave the doorway standing a step proud of the deck outside it; the
# entrance alone drops to the deck surface so the crossing runs in level.
# The bridge assembly is translated by BRIDGE_CENTER_SPAN_OFFSET after it is
# built, so its deck at Knott sits that much above the nominal BRIDGE_DZ2.
ENTRANCE_SILL_Z = BRIDGE_DZ2 + BRIDGE_CENTER_SPAN_OFFSET[2]
CENTER_OPENING_W = 140
CENTER_OPENING_OFFSET = 100  # Shift east, closer to the sign (but not past it).
WEST_OPENING_W = 96
EAST_OPENING_W = 56
# Second, true-ground-level door (independent of the elevated bridge-deck
# entrance above) — east of the center door, giving direct outside access
# to the auditorium on the west side of the ground floor without a rider
# having to cut through it.
GROUND_DOOR_W = 160
GROUND_DOOR_H = 128
GROUND_DOOR_OFFSET = 132  # East of the center door's opening (offset 100).
# Widened westward from a 112-wide door at offset 180 (the east jamb stayed
# put), then shifted 24 west again so it sits clear of the wall's east end.
GROUND_DOOR_BOTTOM = 86  # Sill sits on the hillside crest (the terrain north
# of this wall is flat at this height before it falls away towards Ennis), so
# the door opens straight onto the walk outside at grade rather than onto a
# step. Kept in sync with terrain by test_bridge_knott_helpers.
# Absolute X bounds of that doorway, so the terrain module can line the
# stepped walk outside it up with the opening. Mirrors the centre-plus-offset
# maths _wall_with_opening() does for the north wall panel.
GROUND_DOOR_CX = (KH_NORTH_X1 + KH_NORTH_X2) / 2 + GROUND_DOOR_OFFSET
GROUND_DOOR_X1 = GROUND_DOOR_CX - GROUND_DOOR_W / 2
GROUND_DOOR_X2 = GROUND_DOOR_CX + GROUND_DOOR_W / 2
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


def _beam_zs(win_bottom, z2, segments):
    """Z heights of the horizontal cross beams dividing a window opening
    into ``segments`` equal panes between ``win_bottom`` and ``z2``.

    Shared by ``_side_windows`` and ``_wall_with_opening``, which otherwise
    each build boxes protruding along a different axis (X for the side
    walls' beams, Y for the front/notch walls'), so only this height
    calculation — not the box construction itself — is common between them.
    """
    seg_h = (z2 - win_bottom) / segments
    return [win_bottom + i * seg_h for i in range(1, segments)]


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
        beam_outer = outer_x + BEAM_PROUD * (1 if outer_x > inner_x else -1)
        bx1, bx2 = (inner_x, beam_outer) if outer_x > inner_x else (beam_outer, inner_x)
        for bz in _beam_zs(win_bottom, z2, segments):
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
    entrance_sill_z=None,
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

    ``entrance_sill_z``, if given and below ``bottom_z``, drops the
    entrance's sill that far by cutting the solid base band away under the
    opening, so the doorway starts at the bridge deck outside rather than a
    step above it.

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
    base = []
    if bottom_z > z1:
        if ground_door_w > 0:
            gcx = (x1 + x2) / 2 + ground_door_offset
            gx1, gx2 = gcx - ground_door_w / 2, gcx + ground_door_w / 2
            door_bottom = ground_door_bottom if ground_door_bottom is not None else z1
            door_top = door_bottom + (
                ground_door_h if ground_door_h is not None else bottom_z - z1
            )
            if gx1 > x1:
                base.append(box(x1, y1, z1, gx1, y2, bottom_z, tex))
            if gx2 < x2:
                base.append(box(gx2, y1, z1, x2, y2, bottom_z, tex))
            if door_bottom > z1:
                base.append(box(gx1, y1, z1, gx2, y2, door_bottom, tex))
            if door_top < bottom_z:
                base.append(box(gx1, y1, door_top, gx2, y2, bottom_z, tex))
        else:
            base.append(box(x1, y1, z1, x2, y2, bottom_z, tex))
    sill_cut = entrance and entrance_sill_z is not None and entrance_sill_z < bottom_z
    if sill_cut:
        base = carve_box(base, ox1, y1, entrance_sill_z, ox2, y2, bottom_z, tex)
    boxes.extend(base)
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
        # The jamb mullions run the full height of the opening, so they follow
        # the entrance's sill down rather than stopping where the rest of the
        # facade's grid starts.
        jamb_bottom = min(bottom_z, entrance_sill_z) if sill_cut else bottom_z
        for mx in positions:
            m_bottom = jamb_bottom if mx in edges else entrance_top
            mx -= MULLION_W / 2
            boxes.append(_mullion_prism(mx, y1, y2, m_bottom, z2, m_tex))
    if beams:
        b_tex = beam_tex if beam_tex is not None else (mullion_tex or tex)
        for bz in _beam_zs(win_bottom, z2, segments):
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
            entrance_sill_z=ENTRANCE_SILL_Z,
            ground_door_w=GROUND_DOOR_W,
            ground_door_offset=GROUND_DOOR_OFFSET,
            ground_door_h=GROUND_DOOR_H,
            ground_door_bottom=GROUND_DOOR_BOTTOM,
        ),
    ]
    return wall_brushes, west_detail, east_detail


def _interior_spans():
    """The building's interior footprint, as ``(x1, y1, x2, y2)`` rectangles.

    Knott is not a plain box: the north end is notched in from both sides,
    so the interior is an L/T shape that has to be tiled by rectangles.
    Split into 3 spans across the lower rectangle plus the upper (notched)
    one. The two outer lower spans are additionally inset by ``WALL_T`` on
    the north side, where the NW/NE notch-ledge walls stand; the middle
    span is the open transition into the upper rectangle and so can run
    flush to ``KH_NOTCH_Y``.

    Shared by the roof deck and the floor decks, which cover the same
    footprint at different heights — keeping one definition is what stops
    a future change to the notch from moving the roof but not the floors.
    """
    return (
        (KH_X1 + WALL_T, KH_Y1 + WALL_T, KH_NORTH_X1, KH_NOTCH_Y - WALL_T),
        (KH_NORTH_X1, KH_Y1 + WALL_T, KH_NORTH_X2, KH_NOTCH_Y),
        (KH_NORTH_X2, KH_Y1 + WALL_T, KH_X2 - WALL_T, KH_NOTCH_Y - WALL_T),
        (KH_NORTH_X1 + WALL_T, KH_NOTCH_Y, KH_NORTH_X2 - WALL_T, KH_Y2 - WALL_T),
    )


def _build_roof(roof_z1, roof_z2):
    """Build the roof deck brushes, inset behind the parapet ring.

    Covers :func:`_interior_spans` — see there for how the notched
    footprint is tiled.
    """
    return [
        box(x1, y1, roof_z1, x2, y2, roof_z2, Textures.ROOF_KH)
        for x1, y1, x2, y2 in _interior_spans()
    ]


FLOOR_T = 16  # Deck slab thickness, matching the roof's ROOF_T.

# The two floor lines the facade already fixes, so the decks land on
# heights the building's openings agree with rather than on new invented
# ones:
#
# - The ground storey sits at the north door's threshold. That door opens
#   straight onto the north walk, which ``_knott_door_walk_layout`` runs
#   level away from the doorway "at grade" — so a deck here is flush with
#   the pavement outside and you simply walk in onto it.
# - The entry storey sits on the bridge-level entrance's own sill. That
#   sill is deliberately dropped to the bridge deck's height at Knott
#   (ENTRANCE_SILL_Z) rather than to the facade's opening grid, so the
#   crossing runs in level — and the floor has to meet it there, or the
#   doorway gets a lip. The window sills stay a little above it at
#   OPENING_BOTTOM_Z, which reads as a normal upstand under the glazing.
GROUND_FLOOR_Z = GROUND_DOOR_BOTTOM
ENTRY_FLOOR_Z = ENTRANCE_SILL_Z

# The three floor lines above the entry storey are not new heights either —
# they are the same beam lines the facade's window grid already divides
# into at every ``BEAM_SEGMENTS_PER_FLOOR``-th division (see ``_beam_zs``
# and ``NUM_FLOORS``), so reusing that computation rather than re-deriving
# fresh heights is what keeps the decks landing exactly on the beam that
# already reads as a floor line on the outside of the building.
UPPER_FLOOR_ZS = _beam_zs(
    OPENING_BOTTOM_Z + EXTRA_BASE_H, KH_GROUND_Z + BUILDING_H, WINDOW_SEGMENTS
)[BEAM_SEGMENTS_PER_FLOOR - 1 :: BEAM_SEGMENTS_PER_FLOOR]

# The ground deck is poured straight onto the world ground slab that
# streets/shell.py lays across the whole map at FLOOR_Z1..FLOOR_Z2 — which
# is what already floors this interior, in bare dirt, and what the walls
# stand on (KH_GROUND_Z == FLOOR_Z1). Making it a full-depth slab rather
# than a FLOOR_T one is deliberate: the threshold is GROUND_FLOOR_Z above
# that slab, and a thin deck would leave a sealed, unreachable crawlspace
# under the storey for qbsp to carve up for nothing.
GROUND_FLOOR_T = GROUND_FLOOR_Z - FLOOR_Z2

# Service core: both shafts flush with the front (north) wall of the
# building, either side of the bridge entrance, so coming in off the
# bridge puts the stair on your left and the lift on your right and both
# openings read off the facade line.
#
# Both therefore fill a corner of the notched north bay — the stair its
# NW corner, the lift its NE one — and both run on south past KH_NOTCH_Y
# into the main floor, the stair because a switchback needs CORE_STAIR_D
# and the bay is only NOTCH_D deep, the lift to open its lobby up rather
# than leave the deck flush against it.
#
# This is looser than the retired prototype, which held the stair off the
# main block's west wall by 2 * INDENT and stopped both on the notch
# line. That setback put the stair's west edge 28 units west of the bay,
# where there is no building north of the notch to open into, so it could
# not have been taken to the facade.
# The bridge entrance the cores flank. Mirrors the arithmetic
# _wall_with_opening does internally for the same wall and offset.
ENTRANCE_CX = (KH_NORTH_X1 + WALL_T + KH_NORTH_X2 - WALL_T) / 2 + CENTER_OPENING_OFFSET
ENTRANCE_X1 = ENTRANCE_CX - CENTER_OPENING_W / 2
ENTRANCE_X2 = ENTRANCE_CX + CENTER_OPENING_W / 2

CORE_STAIR_D = 256  # Switchback depth: two half-flights either side of a landing.
NOTCH_D = (KH_Y2 - WALL_T) - KH_NOTCH_Y  # Depth of the notched north bay.
CORE_LIFT_W = 192  # Car plus its shaft walls, and a lobby to wait in.
# The bay alone would box the lobby in behind the notch line, with the
# deck resuming flush against its south edge. Running the void on past
# that line opens the lobby into the main floor instead.
CORE_LIFT_OVERRUN = 64  # How far south of the notch line the lift lobby opens.
# The lift shaft's own back wall aligns with the rest of the lobby's
# south line (CORE_WALL_Y, set by the deeper stair) rather than stopping
# short of it and reading as a stagger.
CORE_LIFT_D = CORE_STAIR_D
CORE_LIFT_X1 = KH_NORTH_X2 - WALL_T - CORE_LIFT_W

# Clearance between the entrance opening and the stair. The lift's own
# setback is emergent — it falls out of cornering a CORE_LIFT_W car in a
# bay of this width — so the stair takes that same figure and the two
# land symmetrically about the door. (The prototype used a token 16,
# which dropped the stairwell immediately inside it.)
CORE_LANDING_GAP = CORE_LIFT_X1 - ENTRANCE_X2


def _core_voids():
    """The stair and lift shaft openings, as ``(x1, y1, x2, y2)`` rects.

    Both are cut as one vertical shaft through every deck above the lowest
    one, so a stair or car can run the full height of the building. Both
    open flush with the building's front wall, filling the west and east
    corners of the notched north bay and running on south out of it.
    """
    north = KH_Y2 - WALL_T
    return (
        (
            KH_NORTH_X1 + WALL_T,
            north - CORE_STAIR_D,
            ENTRANCE_X1 - CORE_LANDING_GAP,
            north,
        ),
        (
            CORE_LIFT_X1,
            north - CORE_LIFT_D,
            KH_NORTH_X2 - WALL_T,
            north,
        ),
    )


# Partition walling the notch bay (bridge entrance, stair, lift) off from
# the rest of each storey, so the lobby reads as its own room instead of an
# unbounded corner of the open floor plate.
#
# Three separate walls, not one: the center one carries the double door
# straight in from the bridge entrance and runs east-west, filling the gap
# between the two shafts; the stair and lift each get their own wall
# running north-south instead — perpendicular to the center one — with a
# single door in it, so reaching either means turning to face it rather
# than walking straight through it the same way as the main entrance.
CORE_WALL_T = WALL_T

# The center (double-door) wall. Set back to align with the back of the
# stair shaft (the deeper of the two — see _core_voids) so the whole notch
# bay reads as one consistent-depth lobby rather than the wall floating at
# an arbitrary depth partway into it. Spans only the gap between the two
# shafts — the stair and lift each wall off their own side of that gap
# instead.
_CORE_FRONT_Y = KH_Y2 - WALL_T  # Interior face of the front (entrance) wall.
CORE_WALL_Y = _CORE_FRONT_Y - CORE_STAIR_D
CORE_WALL_X1 = ENTRANCE_X1 - CORE_LANDING_GAP  # The stair void's east edge.
CORE_WALL_X2 = CORE_LIFT_X1  # The lift void's west edge.

CORE_DOOR_W = 128  # Wide enough to read as a double (two-leaf) door.
CORE_DOOR_H = 128
CORE_DOOR_X1 = ENTRANCE_CX - CORE_DOOR_W / 2
CORE_DOOR_X2 = ENTRANCE_CX + CORE_DOOR_W / 2

# The stair and lift walls run north-south from the building's front wall
# down to CORE_WALL_Y, meeting the center wall there so the lobby is fully
# enclosed on all three sides — no gap where a wall's own shaft happens to
# be shallower than the stairwell that set CORE_WALL_Y. Each door is
# centered between the front wall and CORE_WALL_Y, the lobby's own depth,
# so both are reachable from the lobby without first passing through the
# double door.

STAIR_WALL_X = CORE_WALL_X1  # Same line as the center wall's west edge.
STAIR_WALL_Y1 = CORE_WALL_Y
STAIR_WALL_Y2 = _CORE_FRONT_Y
STAIR_DOOR_W = 96  # Wide enough for two-way switchback traffic.
STAIR_DOOR_CY = (CORE_WALL_Y + _CORE_FRONT_Y) / 2
STAIR_DOOR_Y1 = STAIR_DOOR_CY - STAIR_DOOR_W / 2
STAIR_DOOR_Y2 = STAIR_DOOR_CY + STAIR_DOOR_W / 2
STAIR_DOOR_H = 128

LIFT_WALL_X = CORE_WALL_X2  # Same line as the center wall's east edge.
LIFT_WALL_Y1 = CORE_WALL_Y
LIFT_WALL_Y2 = _CORE_FRONT_Y
LIFT_DOOR_W = 96  # Wide enough for a wheelchair-accessible car and door swing.
LIFT_DOOR_CY = (CORE_WALL_Y + _CORE_FRONT_Y) / 2
LIFT_DOOR_Y1 = LIFT_DOOR_CY - LIFT_DOOR_W / 2
LIFT_DOOR_Y2 = LIFT_DOOR_CY + LIFT_DOOR_W / 2
LIFT_DOOR_H = 128

# Both voids also need a wall closing their own south (back) edge, or the
# shaft reads as open-ended into the main floor beyond it instead of an
# enclosed shaft: the exterior walls bound the north side, STAIR_WALL_X /
# LIFT_WALL_X bound the side facing the lobby, but nothing yet stands at
# the void's own far end. Solid, full height, no door — nothing needs to
# walk through the back of a shaft.
_STAIR_VOID, _LIFT_VOID = _core_voids()
STAIR_SHAFT_X1, STAIR_SHAFT_Y1, STAIR_SHAFT_X2, _ = _STAIR_VOID
LIFT_SHAFT_X1, LIFT_SHAFT_Y1, LIFT_SHAFT_X2, _ = _LIFT_VOID

# The remaining fourth side of each shaft is its own exterior-wall side —
# the stair's west, the lift's east — which the building's outer wall
# happens to run flush against. That wall carries its own (differently
# textured) exterior face there, so the shaft still needs its own interior
# panel on that side to read as WALL_KH_INTERIOR on all four walls rather
# than showing the exterior wall's finish from inside the shaft.
STAIR_SHAFT_WEST_X = STAIR_SHAFT_X1
LIFT_SHAFT_EAST_X = LIFT_SHAFT_X2

# One entry per storey: (floor's own walking-surface Z, its ceiling — the
# underside of the next deck up, or the roof deck's underside for the top
# storey). Reusing FLOOR_T here (rather than GROUND_FLOOR_T, which only
# describes the ground deck's own thickness) is correct because it is the
# *next* storey's deck whose underside is being found, and every deck
# except the ground one is FLOOR_T thick.
FLOOR_ZS = (GROUND_FLOOR_Z, ENTRY_FLOOR_Z, *UPPER_FLOOR_ZS)
_FLOOR_ZS_ABOVE = (*FLOOR_ZS[1:], KH_GROUND_Z + BUILDING_H)
CORE_WALL_CEILINGS = tuple(
    z_above - (FLOOR_T if i < len(_FLOOR_ZS_ABOVE) - 1 else 0)
    for i, z_above in enumerate(_FLOOR_ZS_ABOVE)
)


def _wall_with_one_door(
    x1, y1, x2, y2, axis, door1, door2, door_h, floor_z, ceiling_z, tex
):
    """One storey's worth of a straight wall with a single door in it.

    ``axis`` is ``"x"`` for a wall that runs east-west (the door splits its
    ``x1``..``x2`` run, at ``door1``..``door2`` in X) or ``"y"`` for one that
    runs north-south (the door splits its ``y1``..``y2`` run instead).
    Returns the jamb brush(es) either side of the door plus the header
    brush over it.
    """
    brushes = []
    if axis == "x":
        if x1 < door1:
            brushes.append(box(x1, y1, floor_z, door1, y2, ceiling_z, tex))
        if door2 < x2:
            brushes.append(box(door2, y1, floor_z, x2, y2, ceiling_z, tex))
        brushes.append(box(door1, y1, floor_z + door_h, door2, y2, ceiling_z, tex))
    else:
        if y1 < door1:
            brushes.append(box(x1, y1, floor_z, x2, door1, ceiling_z, tex))
        if door2 < y2:
            brushes.append(box(x1, door2, floor_z, x2, y2, ceiling_z, tex))
        brushes.append(box(x1, door1, floor_z + door_h, x2, door2, ceiling_z, tex))
    return brushes


def _wall_run(brush):
    """Return a core-wall brush's ``(run_x, run, thickness)`` extents.

    A wall runs along whichever horizontal axis is its longer; the shorter
    one is its thickness. Both come back as ``(lo, hi)`` pairs.
    """
    (x1, y1, _), (x2, y2, _) = brush.get_bbox()
    if (x2 - x1) >= (y2 - y1):
        return True, (x1, x2), (y1, y2)
    return False, (y1, y2), (x1, x2)


def _core_wall_corner_joints(brush, brushes):
    """Return the run-axis positions ``brush`` is jointed at by its corners.

    A wall that dies into another one is jointed where the two meet: the
    groove goes on the inside of the corner, just clear of the wall being
    met, so the two pours part on a line rather than running into each other.
    Corners are found from the geometry itself -- any wall crossing this one
    at right angles and overlapping it -- so nothing has to be told where the
    partitions happen to meet.
    """
    run_x, (v1, v2), (t1, t2) = _wall_run(brush)
    joints = []
    for other in brushes:
        other_run_x, (o_run1, o_run2), (o1, o2) = _wall_run(other)
        if other_run_x == run_x:
            continue
        # It has to cross this wall's run and reach across its thickness.
        if not (o1 < v2 and v1 < o2 and o_run1 < t2 and t1 < o_run2):
            continue
        if o1 <= v1:
            joints.append(o2)
        elif o2 >= v2:
            joints.append(o1 - KNOTT_CORE_WALL_JOINT_W)
    # Two walls can die into the same corner -- a shaft's back and the lobby
    # wall it continues, say -- and that corner is still one joint.
    return list(dict.fromkeys(joints))


def _score_core_walls(brushes):
    """Return the core walls' brushes re-poured with control joints in them.

    Every brush the core walls are made of is a plain box, so each can be
    handed straight to :func:`wall_with_joints` and comes back as the run of
    panels and recessed grooves that box would be poured as. Scoring them
    here, rather than at each call site, keeps the wall builders concerned
    only with where the walls and their openings are.
    """
    scored = []
    for brush in brushes:
        (x1, y1, z1), (x2, y2, z2) = brush.get_bbox()
        scored += wall_with_joints(
            x1,
            y1,
            z1,
            x2,
            y2,
            z2,
            Textures.WALL_KH_INTERIOR,
            Textures.SIDEWALK_JOINT_FILL,
            KNOTT_CORE_WALL_JOINT_LEN,
            KNOTT_CORE_WALL_JOINT_W,
            KNOTT_CORE_WALL_JOINT_D,
            extra=_core_wall_corner_joints(brush, brushes),
        )
    return scored


def _lift_car_bounds():
    """Return the car's ``(x1, y1, x2, y2)`` footprint in the lift shaft.

    Its lobby-facing side stands ``KNOTT_LIFT_CAR_GAP`` off the shaft wall's
    inside face, the sill gap a real elevator has between car and landing --
    narrow enough that the player hull bridges it rather than dropping down
    it. The other three sides run clear of the shaft, and the car is centred
    on the shaft door so its own opening lines up with the one it serves.
    """
    x1 = LIFT_WALL_X + CORE_WALL_T / 2 + KNOTT_LIFT_CAR_GAP
    return (
        x1,
        LIFT_DOOR_CY - KNOTT_LIFT_CAR_D / 2,
        x1 + KNOTT_LIFT_CAR_W,
        LIFT_DOOR_CY + KNOTT_LIFT_CAR_D / 2,
    )


def _build_lift_sill():
    """Plate the ground landing's sill gap in black.

    The gap the car stands off the shaft wall is only KNOTT_LIFT_CAR_GAP
    wide, and at the ground storey the deck runs solid underneath it, so
    there is nothing to see there: floor on both sides of a seam. This lays
    a stripe of Textures.JOINT_GAP across it so the gap reads as the gap it
    is. Only the ground storey gets one -- every deck above is cut away over
    the shaft, where the drop shows the gap by itself.
    """
    car_x1 = _lift_car_bounds()[0]
    x1 = car_x1 - KNOTT_LIFT_CAR_GAP
    z2 = FLOOR_ZS[0]
    return [
        box(
            x1,
            LIFT_DOOR_Y1,
            z2 - KNOTT_LIFT_CAR_T,
            car_x1,
            LIFT_DOOR_Y2,
            z2 + KNOTT_LIFT_SILL_PROUD,
            Textures.JOINT_GAP,
            tt=Textures.JOINT_GAP,
        )
    ]


def _build_lift_car():
    """Build the elevator car and the entity that runs it.

    A car, not a bare platform: a floor and a ceiling with four walls between
    them, the lobby-facing one opened to the same width and height as the
    shaft door it pulls up to.

    It is a ``func_door`` rather than the ``func_plat`` a lift is usually
    built from, because a plat's own trigger is fitted to the top of its
    brush: on a flat platform that is the surface you stand on, but on a car
    it is the roof, and a passenger standing on the floor inside would be
    below the trigger and never call it.

    The door is called by a ``trigger_multiple`` filling the car's inside,
    rather than by the field a door spawns for itself. That field is the
    car's own bounds grown by 60 units every way, which reaches out through
    the shaft door and into the lobby, so the car would leave as somebody
    walked up to it rather than once they were aboard. Touching the car
    directly is no good either: vanilla's ``door_touch`` opens nothing unless
    the door is a key door.
    It is built standing on the ground storey's deck rather than let down
    into it. That deck is the one the shafts are not cut through, so a car
    sunk flush into it would put its own floor in the same plane as the
    world's: whoever stepped in would be standing on the building, not on
    the car, and nothing would touch the door. The sill that leaves is a
    single step up at the ground landing, and the climb is measured to bring
    the car's floor level with the top storey's deck.

    It is decked and lined in the same grey the building's own floors and
    roof are: the car is part of the same poured structure, not a fitting
    brought in and finished separately.
    """
    x1, y1, x2, y2 = _lift_car_bounds()
    # Sunk so the car's floor comes out level with the storey deck rather
    # than an KNOTT_LIFT_CAR_T sill above it: you walk in, you don't step up.
    # The slab this buries it in is the one deck _build_floors leaves solid,
    # which is thick enough to swallow it whole, so only the two tops meet --
    # and they carry the same texture, aligned the same way.
    floor_z = FLOOR_ZS[0]
    base_z = floor_z - KNOTT_LIFT_CAR_T
    ceiling_z = base_z + KNOTT_LIFT_CAR_H - KNOTT_LIFT_CAR_T
    top_z = base_z + KNOTT_LIFT_CAR_H
    if ceiling_z - floor_z < LIFT_DOOR_H:
        raise ValueError(
            f"KNOTT_LIFT_CAR_H={KNOTT_LIFT_CAR_H} leaves only "
            f"{ceiling_z - floor_z} units of headroom in the car, less than "
            f"the {LIFT_DOOR_H}-unit shaft door it has to pull up to"
        )
    tex = Textures.ROOF_KH
    t = KNOTT_LIFT_CAR_T
    brushes = [
        box(x1, y1, base_z, x2, y2, floor_z, tex, tt=tex),
        box(x1, y1, ceiling_z, x2, y2, top_z, tex, tt=tex),
        box(x1, y1, floor_z, x2, y1 + t, ceiling_z, tex),
        box(x1, y2 - t, floor_z, x2, y2, ceiling_z, tex),
        box(x2 - t, y1 + t, floor_z, x2, y2 - t, ceiling_z, tex),
    ]
    brushes += _wall_with_one_door(
        x1,
        y1 + t,
        x1 + t,
        y2 - t,
        "y",
        LIFT_DOOR_Y1,
        LIFT_DOOR_Y2,
        LIFT_DOOR_H,
        floor_z,
        ceiling_z,
        tex,
    )
    # A door travels its own size along the move direction less the lip, so
    # the lip is what is left over once the climb is taken off the car's
    # height -- negative, since the climb is many times the car.
    travel = FLOOR_ZS[-1] - floor_z
    car = brush_ent(
        "func_door",
        brushes,
        targetname=KNOTT_LIFT_CAR_TARGET,
        angle="-1",
        lip=str(KNOTT_LIFT_CAR_H - travel),
        speed=str(KNOTT_LIFT_CAR_SPEED),
        wait=str(KNOTT_LIFT_CAR_WAIT),
        dmg="0",
    )
    call = brush_ent(
        "trigger_multiple",
        [
            box(
                x1 + t,
                y1 + t,
                floor_z,
                x2 - t,
                y2 - t,
                ceiling_z,
                Textures.TRIGGER,
            )
        ],
        target=KNOTT_LIFT_CAR_TARGET,
        wait="1",
    )
    return car, call


def _build_core_wall_slabs():
    """Build the notch-bay partition: the center (double-door) wall plus
    the stair and lift's own perpendicular walls, storey by storey.

    Each wall is built as jamb brushes either side of its door plus a
    header brush over the opening, mirroring how the exterior walls build
    their openings, rather than one solid slab with a hole punched in it.
    Each comes back as one unbroken slab; :func:`_build_core_wall` scores
    them into panels afterwards.
    """
    cy1, cy2 = CORE_WALL_Y - CORE_WALL_T / 2, CORE_WALL_Y + CORE_WALL_T / 2
    sx1, sx2 = STAIR_WALL_X - CORE_WALL_T / 2, STAIR_WALL_X + CORE_WALL_T / 2
    lx1, lx2 = LIFT_WALL_X - CORE_WALL_T / 2, LIFT_WALL_X + CORE_WALL_T / 2
    stair_back_y1 = STAIR_SHAFT_Y1 - CORE_WALL_T / 2
    stair_back_y2 = STAIR_SHAFT_Y1 + CORE_WALL_T / 2
    lift_back_y1 = LIFT_SHAFT_Y1 - CORE_WALL_T / 2
    lift_back_y2 = LIFT_SHAFT_Y1 + CORE_WALL_T / 2
    stair_west_x1 = STAIR_SHAFT_WEST_X - CORE_WALL_T / 2
    stair_west_x2 = STAIR_SHAFT_WEST_X + CORE_WALL_T / 2
    lift_east_x1 = LIFT_SHAFT_EAST_X - CORE_WALL_T / 2
    lift_east_x2 = LIFT_SHAFT_EAST_X + CORE_WALL_T / 2
    tex = Textures.WALL_KH_INTERIOR
    brushes = []
    for floor_z, ceiling_z in zip(FLOOR_ZS, CORE_WALL_CEILINGS, strict=True):
        brushes += _wall_with_one_door(
            CORE_WALL_X1,
            cy1,
            CORE_WALL_X2,
            cy2,
            "x",
            CORE_DOOR_X1,
            CORE_DOOR_X2,
            CORE_DOOR_H,
            floor_z,
            ceiling_z,
            tex,
        )
        brushes += _wall_with_one_door(
            sx1,
            STAIR_WALL_Y1,
            sx2,
            STAIR_WALL_Y2,
            "y",
            STAIR_DOOR_Y1,
            STAIR_DOOR_Y2,
            STAIR_DOOR_H,
            floor_z,
            ceiling_z,
            tex,
        )
        brushes += _wall_with_one_door(
            lx1,
            LIFT_WALL_Y1,
            lx2,
            LIFT_WALL_Y2,
            "y",
            LIFT_DOOR_Y1,
            LIFT_DOOR_Y2,
            LIFT_DOOR_H,
            floor_z,
            ceiling_z,
            tex,
        )
        # Solid backs, closing off the shafts' own far ends — no door, so
        # a plain box rather than _wall_with_one_door.
        brushes.append(
            box(
                STAIR_SHAFT_X1,
                stair_back_y1,
                floor_z,
                STAIR_SHAFT_X2,
                stair_back_y2,
                ceiling_z,
                tex,
            )
        )
        brushes.append(
            box(
                LIFT_SHAFT_X1,
                lift_back_y1,
                floor_z,
                LIFT_SHAFT_X2,
                lift_back_y2,
                ceiling_z,
                tex,
            )
        )
        # The fourth side of each shaft, against the building's own
        # exterior wall — solid, no door, so the shaft reads as
        # WALL_KH_INTERIOR on all four sides rather than showing the
        # exterior wall's own finish from inside it.
        brushes.append(
            box(
                stair_west_x1,
                STAIR_SHAFT_Y1,
                floor_z,
                stair_west_x2,
                _CORE_FRONT_Y,
                ceiling_z,
                tex,
            )
        )
        brushes.append(
            box(
                lift_east_x1,
                LIFT_SHAFT_Y1,
                floor_z,
                lift_east_x2,
                _CORE_FRONT_Y,
                ceiling_z,
                tex,
            )
        )
    return brushes


def _build_core_wall():
    """Build the notch-bay partitions, scored with control joints.

    Poured cement this long is cast in panels rather than in one piece, so
    the slabs the wall builder lays down are re-poured as panels parted by
    recessed grooves.
    """
    return _score_core_walls(_build_core_wall_slabs())


def _build_floors():
    """Build the interior storey decks: all five of KNOTT_FLOORS.

    Ground and entry are pinned to the building's own doorways
    (``GROUND_FLOOR_Z``/``ENTRY_FLOOR_Z``); the three above them land on
    ``UPPER_FLOOR_ZS``, the same beam lines the facade's window grid
    already divides into.

    The lowest deck is left solid. It is the bottom of the shafts — the
    stair starts on it and the car lands on it — so cutting the core out
    of it would open a pit down onto the world ground slab underneath
    rather than a shaft. Every deck above it is cut, so a stair or car can
    run the full height of the building.

    Kept as worldspawn (not func_detail like the parapet): a full-footprint
    slab is exactly the kind of large opaque divider vis wants, to cut the
    interior into per-storey clusters instead of one building-sized leaf.
    """
    return [
        brush
        for deck_z, t, voids in (
            (GROUND_FLOOR_Z, GROUND_FLOOR_T, ()),
            (ENTRY_FLOOR_Z, FLOOR_T, _core_voids()),
            *((z, FLOOR_T, _core_voids()) for z in UPPER_FLOOR_ZS),
        )
        for x1, y1, x2, y2 in _interior_spans()
        for brush in floor_plate(
            x1, y1, x2, y2, deck_z, t, Textures.FLOOR_KH, voids=voids
        )
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
    """Build the Knott Hall shell: four walls, a roof, all five floors, the
    entrance/elevator/stair lobby partition, and the elevator car.

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
    floor_brushes = _build_floors()
    core_wall_brushes = _build_core_wall()
    parapet_detail = _build_parapet(z2, parapet_z2)
    sill_detail = _build_lift_sill()
    sign_brushes = _build_sign(z1)

    brushes = [
        *wall_brushes,
        *roof_brushes,
        *floor_brushes,
        *core_wall_brushes,
        *sign_brushes,
    ]
    entities = [
        brush_ent(
            "func_detail",
            west_detail + east_detail + parapet_detail + sill_detail,
        ),
        *_build_lift_car(),
    ]

    return brushes, entities
