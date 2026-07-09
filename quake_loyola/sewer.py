"""Giant storm-sewer tunnel running the full length of Charles Street,
buried well below the road slab, with a manhole cover at street level for
player access.

Access is via a trigger_teleport pair (down through the manhole cover, and
back up from a nearby pad inside the tunnel) rather than a physically carved
vertical shaft through the road slab — this mirrors the bridge abutment's
teleport-arch entrance idiom elsewhere in the map and avoids having to split
apart the interlocking road/curb/lane-marking brushes built in streets.py.
"""

from .constants import (
    MANHOLE_COVER_T,
    MANHOLE_DEST_Z,
    MANHOLE_R,
    MANHOLE_RETURN_Y_OFFSET,
    MANHOLE_X,
    MANHOLE_Y,
    ROAD_Z,
    SEWER_CAP_T,
    SEWER_ENABLED,
    SEWER_LIGHT_SPACING,
    SEWER_RIN,
    SEWER_ROUT,
    SEWER_SEGS,
    SEWER_TEX,
    SEWER_Y1,
    SEWER_Y2,
    SEWER_ZC,
    Textures,
)
from .geometry import arch_seg_y, box, brush_ent, ent


def build():
    if not SEWER_ENABLED:
        return [], []
    BRUSHES = []
    ENTITIES = []

    # ── Tube walls — full 360° ring of wedge segments, extruded the entire
    # length of Charles St (SEWER_Y1..SEWER_Y2), circular cross-section in
    # the X-Z plane centred on the road's X=0 centreline. ──────────────────
    step = 360.0 / SEWER_SEGS
    for seg_index in range(SEWER_SEGS):
        a1, a2 = seg_index * step, (seg_index + 1) * step
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

    # ── End caps — solid plugs sealing the tube's north/south ends so the
    # tunnel doesn't open into the void beyond the modeled street span. ───
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

    # ── Manhole cover — visual disc at street level (func_illusionary) that
    # doubles as a trigger_teleport down into the tunnel below. ───────────
    cover_brush = box(
        MANHOLE_X - MANHOLE_R,
        MANHOLE_Y - MANHOLE_R,
        ROAD_Z - MANHOLE_COVER_T,
        MANHOLE_X + MANHOLE_R,
        MANHOLE_Y + MANHOLE_R,
        ROAD_Z,
        Textures.FENCE,
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_sewer_entry",
            origin=f"{MANHOLE_X} {MANHOLE_Y} {int(MANHOLE_DEST_Z)}",
            angle="0",
        )
    )
    ENTITIES.append(
        brush_ent("trigger_teleport", cover_brush, target="dest_sewer_entry")
    )
    ENTITIES.append(brush_ent("func_illusionary", cover_brush))

    # ── Return pad — a small trigger_teleport on the tunnel floor, offset
    # north of the landing spot so arriving players don't instantly bounce
    # back up, teleporting back to street level at the manhole. ───────────
    return_y = MANHOLE_Y + MANHOLE_RETURN_Y_OFFSET
    return_brush = box(
        MANHOLE_X - MANHOLE_R,
        return_y - MANHOLE_R,
        SEWER_ZC - SEWER_ROUT,
        MANHOLE_X + MANHOLE_R,
        return_y + MANHOLE_R,
        SEWER_ZC,
        Textures.FENCE,
    )
    ENTITIES.append(
        ent(
            "info_teleport_destination",
            targetname="dest_sewer_exit",
            origin=f"{MANHOLE_X} {MANHOLE_Y} {ROAD_Z + 24}",
            angle="0",
        )
    )
    ENTITIES.append(
        brush_ent("trigger_teleport", return_brush, target="dest_sewer_exit")
    )

    return BRUSHES, ENTITIES
