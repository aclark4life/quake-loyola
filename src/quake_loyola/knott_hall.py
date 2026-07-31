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
    KNOTT_ENABLED,
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
from .geometry import box, fascia_sign

WALL_T = 16
ROOF_T = 16
BUILDING_H = 1536  # Was 1344 (previously bumped from 1152/960); taller again.
CORNER_CUT_DEPTH = 160  # How far south (into the building) both notches cut.
CORNER_CUT_W_NE = 128  # East notch inset from X2.
CORNER_CUT_W_NW = 188  # West notch inset from X1 — moved east more than the NE side.

SHIFT_NORTH = 220  # Moved a little closer to the bridge deck (+Y).

# Widened to align the east/west walls with the outer pier faces of the
# Pier 4-Pier 5 bridge span facing Knott Hall (BRIDGE_ENABLED_SPAN_KH).
X1 = PIER4_X - BRIDGE_PILLAR_HW  # West wall flush with Pier 4's west face.
X2 = PIER5_X + BRIDGE_PILLAR_HW  # East wall flush with Pier 5's east face.
Y1 = KNOTT_Y1 + SHIFT_NORTH
Y2 = KNOTT_Y2 + SHIFT_NORTH

# The north edge steps in at both the NW and NE corners: the footprint is
# the union of a full-width lower rectangle (up to NOTCH_Y) and a narrower
# upper rectangle (NOTCH_Y to Y2, inset by CORNER_CUT_W_NW/NE on each side)
# rather than one plain rectangle. Both corners cut the same depth south
# (NOTCH_Y), but the west corner insets further east than the east corner.
NOTCH_Y = Y2 - CORNER_CUT_DEPTH
NORTH_X1 = X1 + CORNER_CUT_W_NW
NORTH_X2 = X2 - CORNER_CUT_W_NE

# The real terrain hillside slopes down noticeably (and non-linearly near
# the southeast corner) under the footprint — the _kh_hill_ground_z helper
# is only an approximation of the actual generated terrain mesh and
# underestimates how low it dips in places (real mesh reaches ~z10 near
# the SE corner vs. the helper's ~z44). Rather than chase the exact real
# minimum, walls extend down to WORLD_FLOOR_Z (-16), the base terrain fill
# level used everywhere else in the map, guaranteeing no gap regardless of
# local terrain undulation.
GROUND_Z = -16

# Front openings (all start at bridge-deck height and run up to the roof;
# below bridge-deck height the wall is solid): a center opening on the
# north wall, and matching openings on the south-facing notch-ledge walls
# (the walls that bound the NW/NE corner cuts from the south) flanking it.
# The center and west openings share the same size; the east one is
# narrower.
OPENING_BOTTOM_Z = BRIDGE_DZ2  # Openings start at bridge-deck level.
CENTER_OPENING_W = 140
CENTER_OPENING_OFFSET = 100  # Shift east, closer to the sign (but not past it).
WEST_OPENING_W = 96
EAST_OPENING_W = 56


def _wall_with_opening(x1, y1, x2, y2, z1, z2, open_w, bottom_z, tex, offset=0):
    """A thin wall (in Y) split around a centered opening above bridge level.

    The wall is solid from ``z1`` up to ``bottom_z`` (bridge-deck height);
    above that, an opening spans ``open_w`` in X, centered on the wall (plus
    ``offset``), up to ``z2``, with solid wall on either side of the
    opening.
    """
    cx = (x1 + x2) / 2 + offset
    ox1, ox2 = cx - open_w / 2, cx + open_w / 2
    boxes = []
    if bottom_z > z1:
        boxes.append(box(x1, y1, z1, x2, y2, bottom_z, tex))
    if x1 < ox1:
        boxes.append(box(x1, y1, bottom_z, ox1, y2, z2, tex))
    if ox2 < x2:
        boxes.append(box(ox2, y1, bottom_z, x2, y2, z2, tex))
    return boxes


def build():
    if not KNOTT_ENABLED:
        return [], []

    z1 = GROUND_Z
    z2 = z1 + BUILDING_H
    roof_z1 = z2
    roof_z2 = roof_z1 + ROOF_T

    brushes = [
        # West wall (lower rectangle only — stops at the NW notch)
        box(X1, Y1, z1, X1 + WALL_T, NOTCH_Y, z2, Textures.PIER_STONE),
        # East wall (lower rectangle only — stops at the NE notch)
        box(X2 - WALL_T, Y1, z1, X2, NOTCH_Y, z2, Textures.PIER_STONE),
        # South wall (between the two side walls)
        box(
            X1 + WALL_T,
            Y1,
            z1,
            X2 - WALL_T,
            Y1 + WALL_T,
            z2,
            Textures.PIER_STONE,
        ),
        # NW notch ledge (faces the cut-away square, north-facing) — has the
        # west front opening above bridge-deck height.
        *_wall_with_opening(
            X1 + WALL_T,
            NOTCH_Y - WALL_T,
            NORTH_X1,
            NOTCH_Y,
            z1,
            z2,
            WEST_OPENING_W,
            OPENING_BOTTOM_Z,
            Textures.PIER_STONE,
        ),
        # NE notch ledge (faces the cut-away square, north-facing) — has the
        # (narrower) east front opening above bridge-deck height.
        *_wall_with_opening(
            NORTH_X2,
            NOTCH_Y - WALL_T,
            X2 - WALL_T,
            NOTCH_Y,
            z1,
            z2,
            EAST_OPENING_W,
            OPENING_BOTTOM_Z,
            Textures.PIER_STONE,
        ),
        # Upper rectangle west wall (inward face of the NW notch)
        box(NORTH_X1, NOTCH_Y, z1, NORTH_X1 + WALL_T, Y2, z2, Textures.PIER_STONE),
        # Upper rectangle east wall (inward face of the NE notch)
        box(NORTH_X2 - WALL_T, NOTCH_Y, z1, NORTH_X2, Y2, z2, Textures.PIER_STONE),
        # North wall (upper rectangle, between the two notches) — has the
        # center front opening above bridge-deck height, same size as the
        # west opening.
        *_wall_with_opening(
            NORTH_X1 + WALL_T,
            Y2 - WALL_T,
            NORTH_X2 - WALL_T,
            Y2,
            z1,
            z2,
            CENTER_OPENING_W,
            OPENING_BOTTOM_Z,
            Textures.PIER_STONE,
            offset=CENTER_OPENING_OFFSET,
        ),
        # Roof, lower rectangle
        box(X1, Y1, roof_z1, X2, NOTCH_Y, roof_z2, Textures.CEMENT),
        # Roof, upper (notched) rectangle
        box(NORTH_X1, NOTCH_Y, roof_z1, NORTH_X2, Y2, roof_z2, Textures.CEMENT),
    ]

    # Fascia sign on the north (bridge-facing) wall, mirroring the old KH
    # module's sign but re-centered/re-leveled for this shell's footprint
    # and height (no floors to anchor to here, so it's centered vertically).
    # Kept snug against the east edge of the (now-narrower) north wall.
    SIGN_EAST_MARGIN = 32
    PANEL_SCALE = 0.7  # shrink the sign backing panel a little further
    LETTER_SCALE = 0.7  # shrink the lettering more, leaving side padding
    SIDE_PADDING = 24  # extra fixed gap between the glyphs and panel edge
    sign_px_w = int(KNOTT_SIGN_PX_W * LETTER_SCALE)
    sign_px_h = int(KNOTT_SIGN_PX_H * LETTER_SCALE)
    sign_h = int(KNOTT_SIGN_H * PANEL_SCALE)
    sign_padding = int(KNOTT_SIGN_PADDING * PANEL_SCALE) + SIDE_PADDING
    sign_char_w = (4 + 1) * sign_px_w
    sign_total_w = len(KNOTT_SIGN_TEXT) * sign_char_w - sign_px_w
    # Panel is sized off the glyph width plus a fixed side gap (rather than
    # a second scale factor) so it always leaves visible padding, regardless
    # of how the letter pixel sizes happen to round.
    sign_half_w = sign_total_w // 2 + sign_padding
    sign_cx = NORTH_X2 - WALL_T - SIGN_EAST_MARGIN - sign_half_w
    SIGN_Z_ADJUST = 32  # Lower the sign a little from its default offset.
    sign_z_center = z1 + BUILDING_H // 2 + KNOTT_SIGN_Z_OFFSET + SIGN_Z_ADJUST
    brushes.extend(
        fascia_sign(
            KNOTT_SIGN_TEXT,
            sign_cx,
            Y2,
            sign_z_center,
            panel_h=sign_h,
            panel_padding=sign_padding,
            px_w=sign_px_w,
            px_h=sign_px_h,
            panel_tex=Textures.CEMENT,
            text_tex=Textures.RAIL,
        )
    )

    return brushes, []
