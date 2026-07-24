"""Prototype Knott Hall shell: four walls and a roof, no floors.

This is a from-scratch replacement for the old ``knott_hall`` module (see
``knott_hall.py``), sized and placed against the real terrain modeled in
``terrain/knott_hall.py`` rather than the old flat ``KNOTT_GROUND_Z`` anchor.
The interior is left as one big open volume so the footprint and height can
be iterated on before any floors, windows, or interior detail are added.
Once this shape is settled, the old module and its constants can be triaged
and removed.
"""

from .constants import (
    BRIDGE_PILLAR_HW,
    KNOTT_ENABLED_NEW,
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
from .geometry import box, render_text_flat
from .terrain.knott_hall import kh_hill_ground_z

WALL_T = 16
ROOF_T = 16
BUILDING_H = 1344  # Was 1152 (previously bumped from 960); a little taller again.
CORNER_CUT_DEPTH = 160  # How far south (into the building) both notches cut.
CORNER_CUT_W_NE = 128  # East notch inset from X2.
CORNER_CUT_W_NW = 188  # West notch inset from X1 — moved east more than the NE side.

SHIFT_NORTH = 150  # A little further north (+Y).

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

# The real terrain hillside is flat under the whole footprint (see
# terrain/knott_hall.py's kh_hill_ground_z), so any corner gives the ground Z.
GROUND_Z = kh_hill_ground_z(X1, Y1)


def build():
    if not KNOTT_ENABLED_NEW:
        return [], []

    z1 = GROUND_Z
    z2 = z1 + BUILDING_H
    roof_z1 = z2
    roof_z2 = roof_z1 + ROOF_T

    brushes = [
        # West wall (lower rectangle only — stops at the NW notch)
        box(X1, Y1, z1, X1 + WALL_T, NOTCH_Y, z2, Textures.BRICK_KH),
        # East wall (lower rectangle only — stops at the NE notch)
        box(X2 - WALL_T, Y1, z1, X2, NOTCH_Y, z2, Textures.BRICK_KH),
        # South wall (between the two side walls)
        box(
            X1 + WALL_T,
            Y1,
            z1,
            X2 - WALL_T,
            Y1 + WALL_T,
            z2,
            Textures.BRICK_KH,
        ),
        # NW notch ledge (faces the cut-away square, north-facing)
        box(
            X1 + WALL_T,
            NOTCH_Y - WALL_T,
            z1,
            NORTH_X1,
            NOTCH_Y,
            z2,
            Textures.BRICK_KH,
        ),
        # NE notch ledge (faces the cut-away square, north-facing)
        box(
            NORTH_X2,
            NOTCH_Y - WALL_T,
            z1,
            X2 - WALL_T,
            NOTCH_Y,
            z2,
            Textures.BRICK_KH,
        ),
        # Upper rectangle west wall (inward face of the NW notch)
        box(NORTH_X1, NOTCH_Y, z1, NORTH_X1 + WALL_T, Y2, z2, Textures.BRICK_KH),
        # Upper rectangle east wall (inward face of the NE notch)
        box(NORTH_X2 - WALL_T, NOTCH_Y, z1, NORTH_X2, Y2, z2, Textures.BRICK_KH),
        # North wall (upper rectangle, between the two notches)
        box(
            NORTH_X1 + WALL_T,
            Y2 - WALL_T,
            z1,
            NORTH_X2 - WALL_T,
            Y2,
            z2,
            Textures.BRICK_KH,
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
    sign_char_w = (4 + 1) * KNOTT_SIGN_PX_W
    sign_total_w = len(KNOTT_SIGN_TEXT) * sign_char_w - KNOTT_SIGN_PX_W
    sign_half_w = sign_total_w // 2 + KNOTT_SIGN_PADDING
    sign_cx = NORTH_X2 - WALL_T - SIGN_EAST_MARGIN - sign_half_w
    sign_z1 = z1 + BUILDING_H // 2 - KNOTT_SIGN_H // 2 + KNOTT_SIGN_Z_OFFSET
    sign_z2 = sign_z1 + KNOTT_SIGN_H
    brushes.append(
        box(
            sign_cx - sign_half_w,
            Y2,
            sign_z1,
            sign_cx + sign_half_w,
            Y2 + 6,
            sign_z2,
            Textures.CEMENT,
        )
    )
    brushes.extend(
        render_text_flat(
            KNOTT_SIGN_TEXT[::-1],
            x0=sign_cx - sign_total_w // 2,
            y_face=Y2 + 6,
            z_base=sign_z1 + (KNOTT_SIGN_H - 6 * KNOTT_SIGN_PX_H) // 2,
            px_w=KNOTT_SIGN_PX_W,
            px_h=KNOTT_SIGN_PX_H,
            depth=2,
            tex=Textures.RAIL,
            mirror=True,
        )
    )

    return brushes, []
