"""Giant storm-sewer tunnel running the full length of Charles Street.

The tunnel lives inside its own sealed "basement" chamber — a rectangle
extended below the existing world floor slab, entirely separate from the
map's ordinary ground/street geometry above. The tube floats inside that
chamber with clearance on all sides. The only connection between the two
worlds is a single vertical manhole shaft at street level: a real physical
round opening (not a teleport) punched straight down through the world
floor slab, the chamber's ceiling, and a short local gap in the tube's ring
wall, so a player can walk into the hole and fall straight down into the
tunnel below.
"""

import math

from .constants import (
    FLOOR_Z1,
    MANHOLE_COLLAR_H,
    MANHOLE_COLLAR_MARGIN,
    MANHOLE_R,
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
from .geometry import arch_seg_y, box, box_with_round_hole, ent


def build():
    if not SEWER_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # Manhole shaft footprint at street level — the manhole isn't centred
    # over the tube's own centreline (X=0); it sits off to one side, like a
    # real curb-lane manhole. MANHOLE_X must be within the tube's outer
    # radius for the shaft to actually reach the tube below.
    assert abs(MANHOLE_X) < SEWER_ROUT, "manhole must be within the tube's outer radius"

    # ── Chamber shell — a wholly separate sealed room extended below the
    # world floor, independent of the ordinary street/ground geometry above
    # except for the one manhole shaft hole through its ceiling. The ceiling
    # sits strictly *below* the world floor slab (FLOOR_Z1..FLOOR_Z2, built
    # in streets.py) rather than overlapping it, to avoid coplanar/overlap
    # artifacts at their shared footprint over Charles St. ────────────────
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
        box_with_round_hole(
            SEWER_ROOM_X1,
            SEWER_Y1,
            SEWER_ROOM_ZT,
            SEWER_ROOM_X2,
            SEWER_Y2,
            FLOOR_Z1,
            MANHOLE_X,
            MANHOLE_Y,
            MANHOLE_R,
            SEWER_TEX,
        )
    )  # chamber ceiling (SEWER_ROOM_ZT..FLOOR_Z1), with the round manhole
    # shaft hole punched through
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
    # the chamber with clearance on all sides. Angle 0°=+X, 90°=+Z (up), per
    # arch_seg_y's convention. A short local gap is left in whichever
    # wedge(s) the manhole shaft actually passes through overhead (near, but
    # not necessarily exactly at, the top of the ring, since the manhole is
    # offset from the tube's centreline) — and *only* across a narrow Y
    # window around MANHOLE_Y, not the tube's full length. ────────────────
    step = 360.0 / SEWER_SEGS
    # Angle (from tube centre) at which a vertical line through MANHOLE_X
    # crosses the outer wall, on the upper half of the ring.
    theta = math.degrees(math.acos(MANHOLE_X / SEWER_ROUT))
    half_w = math.degrees(math.asin(MANHOLE_R / SEWER_ROUT)) + 6  # + margin
    open_a1, open_a2 = theta - half_w, theta + half_w
    gap_y1, gap_y2 = MANHOLE_Y - MANHOLE_R - 8, MANHOLE_Y + MANHOLE_R + 8

    for seg_index in range(SEWER_SEGS):
        a1, a2 = seg_index * step, (seg_index + 1) * step
        opens_here = a2 > open_a1 and a1 < open_a2  # wedge angle overlaps the shaft
        if not opens_here:
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
            continue
        # This wedge is under the shaft — build it in up to 2 shorter pieces
        # along Y, leaving a gap only for the shaft's local width.
        if SEWER_Y1 < gap_y1:
            BRUSHES.append(
                arch_seg_y(
                    SEWER_Y1,
                    gap_y1,
                    0.0,
                    float(SEWER_ZC),
                    SEWER_RIN,
                    SEWER_ROUT,
                    a1,
                    a2,
                    SEWER_TEX,
                )
            )
        if gap_y2 < SEWER_Y2:
            BRUSHES.append(
                arch_seg_y(
                    gap_y2,
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

    # ── Manhole collar — a low decorative round rim at street level around
    # the shaft opening (raised lip, matching the shaft's real footprint). ─
    BRUSHES.extend(
        box_with_round_hole(
            MANHOLE_X - MANHOLE_R - MANHOLE_COLLAR_MARGIN,
            MANHOLE_Y - MANHOLE_R - MANHOLE_COLLAR_MARGIN,
            ROAD_Z,
            MANHOLE_X + MANHOLE_R + MANHOLE_COLLAR_MARGIN,
            MANHOLE_Y + MANHOLE_R + MANHOLE_COLLAR_MARGIN,
            ROAD_Z + MANHOLE_COLLAR_H,
            MANHOLE_X,
            MANHOLE_Y,
            MANHOLE_R,
            Textures.FENCE,
        )
    )

    return BRUSHES, ENTITIES
