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
    KNOTT_ENABLED_NEW,
    KNOTT_SIGN_H,
    KNOTT_SIGN_PADDING,
    KNOTT_SIGN_PX_H,
    KNOTT_SIGN_PX_W,
    KNOTT_SIGN_TEXT,
    KNOTT_SIGN_Z_OFFSET,
    KNOTT_X1,
    KNOTT_X2,
    KNOTT_Y1,
    KNOTT_Y2,
    Textures,
)
from .geometry import box, render_text_flat
from .terrain.knott_hall import kh_hill_ground_z

WALL_T = 16
ROOF_T = 16
BUILDING_H = 1344  # Was 1152 (previously bumped from 960); a little taller again.

# Adjustments layered on top of the shared KNOTT_X1/X2/Y1/Y2 footprint so this
# prototype can be nudged independently without disturbing the constants the
# rest of the map (bridge alignment, driveway, etc.) still relies on.
WIDEN_EAST = 100  # A little wider east/west, added on the east side only.
NARROW_WEST = 100  # A little less wide, trimmed from the west side.
SHIFT_EAST = 150  # A little further east (+X).
SHIFT_NORTH = 150  # A little further north (+Y).

# East edge stays anchored at KNOTT_X2 + SHIFT_EAST + WIDEN_EAST; only the
# west edge moves (east, i.e. narrower) to trim width off that side.
X2 = KNOTT_X2 + SHIFT_EAST + WIDEN_EAST
X1 = KNOTT_X1 + SHIFT_EAST + NARROW_WEST
Y1 = KNOTT_Y1 + SHIFT_NORTH
Y2 = KNOTT_Y2 + SHIFT_NORTH

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
        # West wall
        box(X1, Y1, z1, X1 + WALL_T, Y2, z2, Textures.BRICK_KH),
        # East wall
        box(X2 - WALL_T, Y1, z1, X2, Y2, z2, Textures.BRICK_KH),
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
        # North wall (between the two side walls)
        box(
            X1 + WALL_T,
            Y2 - WALL_T,
            z1,
            X2 - WALL_T,
            Y2,
            z2,
            Textures.BRICK_KH,
        ),
        # Roof, spanning the full footprint
        box(X1, Y1, roof_z1, X2, Y2, roof_z2, Textures.CEMENT),
    ]

    # Fascia sign on the north (bridge-facing) wall, mirroring the old KH
    # module's sign but re-centered/re-leveled for this shell's footprint
    # and height (no floors to anchor to here, so it's centered vertically).
    # Positioned toward the east end, stopping just short of the east wall.
    SIGN_EAST_MARGIN = 32
    sign_char_w = (4 + 1) * KNOTT_SIGN_PX_W
    sign_total_w = len(KNOTT_SIGN_TEXT) * sign_char_w - KNOTT_SIGN_PX_W
    sign_half_w = sign_total_w // 2 + KNOTT_SIGN_PADDING
    sign_cx = X2 - WALL_T - SIGN_EAST_MARGIN - sign_half_w
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
