"""Giant storm-sewer tunnel running the full length of Charles Street.

The tunnel lives inside its own sealed "basement" chamber — a rectangle
extended below the existing world floor slab, entirely separate from the
map's ordinary ground/street geometry above. The tube floats inside that
chamber with clearance on all sides. The only connection between the two
worlds is a single vertical manhole shaft at street level: a real physical
opening (not a teleport) punched straight down through the world floor slab,
the chamber's ceiling, and a matching gap in the top of the tube's ring
wall, so a player can walk into the hole and fall straight down into the
tunnel below.
"""

from .constants import (
    MANHOLE_COLLAR_H,
    MANHOLE_COLLAR_MARGIN,
    MANHOLE_R,
    MANHOLE_TUBE_OPEN_ANGLE1,
    MANHOLE_TUBE_OPEN_ANGLE2,
    MANHOLE_X,
    MANHOLE_Y,
    ROAD_Z,
    SEWER_CAP_T,
    SEWER_ENABLED,
    SEWER_LIGHT_SPACING,
    SEWER_RIN,
    SEWER_ROOM_CEIL_T,
    SEWER_ROOM_FLOOR_T,
    SEWER_ROOM_WALL_T,
    SEWER_ROOM_X1,
    SEWER_ROOM_X2,
    SEWER_ROOM_ZB,
    SEWER_ROOM_ZT,
    SEWER_ROUT,
    SEWER_SEGS,
    SEWER_TEX,
    SEWER_Y1,
    SEWER_Y2,
    SEWER_ZC,
    Textures,
)
from .geometry import arch_seg_y, box, box_with_hole, ent


def build():
    if not SEWER_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # Manhole shaft footprint — the square hole that connects the street
    # surface down into the chamber below.
    hx1, hx2 = MANHOLE_X - MANHOLE_R, MANHOLE_X + MANHOLE_R
    hy1, hy2 = MANHOLE_Y - MANHOLE_R, MANHOLE_Y + MANHOLE_R

    # ── Chamber shell — a wholly separate sealed room extended below the
    # world floor, independent of the ordinary street/ground geometry above
    # except for the one manhole shaft hole through its ceiling. ──────────
    BRUSHES.append(
        box(
            SEWER_ROOM_X1,
            SEWER_Y1,
            SEWER_ROOM_ZB - SEWER_ROOM_FLOOR_T,
            SEWER_ROOM_X2,
            SEWER_Y2,
            SEWER_ROOM_ZB,
            SEWER_TEX,
        )
    )  # chamber floor
    BRUSHES.extend(
        box_with_hole(
            SEWER_ROOM_X1,
            SEWER_Y1,
            SEWER_ROOM_ZT,
            SEWER_ROOM_X2,
            SEWER_Y2,
            SEWER_ROOM_ZT + SEWER_ROOM_CEIL_T,
            hx1,
            hy1,
            hx2,
            hy2,
            SEWER_TEX,
        )
    )  # chamber ceiling, with the manhole shaft hole punched through
    BRUSHES.append(
        box(
            SEWER_ROOM_X1 - SEWER_ROOM_WALL_T,
            SEWER_Y1 - SEWER_ROOM_WALL_T,
            SEWER_ROOM_ZB,
            SEWER_ROOM_X1,
            SEWER_Y2 + SEWER_ROOM_WALL_T,
            SEWER_ROOM_ZT,
            SEWER_TEX,
        )
    )  # chamber west wall
    BRUSHES.append(
        box(
            SEWER_ROOM_X2,
            SEWER_Y1 - SEWER_ROOM_WALL_T,
            SEWER_ROOM_ZB,
            SEWER_ROOM_X2 + SEWER_ROOM_WALL_T,
            SEWER_Y2 + SEWER_ROOM_WALL_T,
            SEWER_ROOM_ZT,
            SEWER_TEX,
        )
    )  # chamber east wall
    BRUSHES.append(
        box(
            SEWER_ROOM_X1,
            SEWER_Y1 - SEWER_ROOM_WALL_T,
            SEWER_ROOM_ZB,
            SEWER_ROOM_X2,
            SEWER_Y1,
            SEWER_ROOM_ZT,
            SEWER_TEX,
        )
    )  # chamber south end cap
    BRUSHES.append(
        box(
            SEWER_ROOM_X1,
            SEWER_Y2,
            SEWER_ROOM_ZB,
            SEWER_ROOM_X2,
            SEWER_Y2 + SEWER_ROOM_WALL_T,
            SEWER_ROOM_ZT,
            SEWER_TEX,
        )
    )  # chamber north end cap

    # ── Tube walls — full 360° ring of wedge segments, extruded the entire
    # length of Charles St (SEWER_Y1..SEWER_Y2), circular cross-section in
    # the X-Z plane centred on the road's X=0 centreline, floating inside
    # the chamber with clearance on all sides. A gap is left at the top
    # (around angle 90° = straight up) so the manhole shaft above drops
    # straight into the tube's hollow interior instead of just the
    # surrounding chamber air. ─────────────────────────────────────────────
    step = 360.0 / SEWER_SEGS
    for seg_index in range(SEWER_SEGS):
        a1, a2 = seg_index * step, (seg_index + 1) * step
        if a1 >= MANHOLE_TUBE_OPEN_ANGLE1 and a2 <= MANHOLE_TUBE_OPEN_ANGLE2:
            continue  # skip wedge(s) under the manhole shaft opening
        BRUSHES.append(
            arch_seg_y(
                SEWER_Y1,
                SEWER_Y2,
                0.0,
                float(SEWER_ZC),
                SEWER_RIN,
                SEWER_ROUT,
                a1,
                a2,
                SEWER_TEX,
            )
        )

    # ── Tube end caps — solid plugs sealing the tunnel's north/south ends
    # so it doesn't open into the chamber's end walls' seams. ─────────────
    BRUSHES.append(
        box(
            -SEWER_ROUT,
            SEWER_Y1 - SEWER_CAP_T,
            SEWER_ZC - SEWER_ROUT,
            SEWER_ROUT,
            SEWER_Y1,
            SEWER_ZC + SEWER_ROUT,
            SEWER_TEX,
        )
    )
    BRUSHES.append(
        box(
            -SEWER_ROUT,
            SEWER_Y2,
            SEWER_ZC - SEWER_ROUT,
            SEWER_ROUT,
            SEWER_Y2 + SEWER_CAP_T,
            SEWER_ZC + SEWER_ROUT,
            SEWER_TEX,
        )
    )

    # ── Interior lighting — evenly spaced point lights along the tunnel. ──
    y = SEWER_Y1 + SEWER_LIGHT_SPACING // 2
    while y < SEWER_Y2:
        ENTITIES.append(ent("light", origin=f"0 {int(y)} {int(SEWER_ZC)}", light="200"))
        y += SEWER_LIGHT_SPACING
    ENTITIES.append(
        ent(
            "light",
            origin=f"{MANHOLE_X} {MANHOLE_Y} {int(SEWER_ROOM_ZT) - 32}",
            light="150",
        )
    )  # extra light right under the manhole shaft opening

    # ── Manhole collar — a low decorative rim at street level around the
    # shaft opening (raised lip, matching the shaft's real footprint). ────
    BRUSHES.extend(
        box_with_hole(
            hx1 - MANHOLE_COLLAR_MARGIN,
            hy1 - MANHOLE_COLLAR_MARGIN,
            ROAD_Z,
            hx2 + MANHOLE_COLLAR_MARGIN,
            hy2 + MANHOLE_COLLAR_MARGIN,
            ROAD_Z + MANHOLE_COLLAR_H,
            hx1,
            hy1,
            hx2,
            hy2,
            Textures.FENCE,
        )
    )

    return BRUSHES, ENTITIES
