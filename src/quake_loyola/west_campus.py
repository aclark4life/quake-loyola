"""West-campus frontage: the hillside iron fence, brick wall, and terrace walk.

The dorm buildings themselves now live in ``dorms.py``.
"""

from .constants import WORLD_Y2
from .constants.bridge import BRIDGE_CENTER_SPAN_OFFSET
from .constants.derived import (
    BRIDGE_DZ2,
    CHARLES_Y1,
    DORM_FRONT_WALKWAY_SPUR_X1,
    DORM_FRONT_WALKWAY_SPUR_Y2,
    DORM_FRONT_WALKWAY_X1,
    DORM_FRONT_WALKWAY_X2,
    DORM_PIER_X,
    DORM_SOUTH2_Y2,
    DORM_WALL_S_Y2,
    FENCE_X1,
    FENCE_X2,
    FLOOR_Z2,
    SDORM_LIFT,
    WALL_T,
)
from .constants.dorm import (
    DORM_BRICK_GATE_H,
    DORM_BRICK_PILLAR_CAP_H,
    DORM_BRICK_PILLAR_CAP_OVH,
    DORM_BRICK_PILLAR_GAP,
    DORM_BRICK_PILLAR_H_OFFSET,
    DORM_BRICK_PILLAR_PROUD,
    DORM_BRICK_PILLAR_SEPARATION,
    DORM_BRICK_PILLAR_W,
    DORM_BRICK_WALL_HW,
    DORM_DOOR_OFF,
    DORM_DOOR_W,
)
from .constants.flags import (
    BRIDGE_ENABLED_SPAN_CENTER,
    WEST_CAMPUS_ENABLED_FENCE,
    WEST_CAMPUS_ENABLED_SIDEWALK,
    WEST_CAMPUS_ENABLED_TERRAIN,
    WEST_CAMPUS_ENABLED_WALL,
)
from .constants.textures import Textures
from .constants.world import FENCE_H, FENCE_SPACING
from .geometry import (
    box,
    brush_ent,
    iron_fence,
    ramp_slab_y,
)
from .terrain.west_campus import terrain_z, wct_y


def _build_iron_fence(ENTITIES):
    """Build the east-side iron fence for the west-campus frontage."""
    fence_brushes = []

    fence_y2 = WORLD_Y2 - WALL_T

    def fence_base_at(y):
        """Return the fence base height from the hillside terrain."""
        return terrain_z(FENCE_X1, y)

    rail_lo, rail_hi = FENCE_H - 28, FENCE_H - 26
    rail_ys = sorted(
        {CHARLES_Y1, fence_y2} | {y for y in wct_y if CHARLES_Y1 < y < fence_y2}
    )
    for ny1, ny2 in zip(rail_ys, rail_ys[1:], strict=False):
        b1, b2 = fence_base_at(ny1), fence_base_at(ny2)
        fence_brushes.append(
            ramp_slab_y(
                FENCE_X1,
                FENCE_X2,
                ny1,
                ny2,
                b1 + rail_lo,
                b2 + rail_lo,
                b1 + rail_hi,
                b2 + rail_hi,
                Textures.FENCE,
            )
        )

    picket_y = CHARLES_Y1
    picket_index = 0
    while True:
        picket_width = 8 if picket_index % 10 == 0 else 2
        if picket_y + picket_width > fence_y2:
            break
        fence_base = fence_base_at(picket_y)
        fence_brushes.append(
            box(
                FENCE_X1,
                picket_y,
                fence_base,
                FENCE_X2,
                picket_y + picket_width,
                fence_base + FENCE_H,
                Textures.FENCE,
            )
        )
        picket_y += FENCE_SPACING
        picket_index += 1

    pillar_hw = 24
    pillar_cx = (FENCE_X1 + FENCE_X2) // 2
    pillar_y1 = CHARLES_Y1 - pillar_hw
    pillar_y2 = CHARLES_Y1 + pillar_hw
    pillar_base = fence_base_at(CHARLES_Y1)
    cap_h = 10
    cap_ovh = 4
    pillar_top = pillar_base + FENCE_H + 12
    fence_brushes.append(
        box(
            pillar_cx - pillar_hw,
            pillar_y1,
            pillar_base,
            pillar_cx + pillar_hw,
            pillar_y2,
            pillar_top,
            Textures.BUILDING,
        )
    )
    fence_brushes.append(
        box(
            pillar_cx - pillar_hw - cap_ovh,
            pillar_y1 - cap_ovh,
            pillar_top,
            pillar_cx + pillar_hw + cap_ovh,
            pillar_y2 + cap_ovh,
            pillar_top + cap_h,
            Textures.BUILDING,
        )
    )

    if fence_brushes:
        ENTITIES.append(brush_ent("func_detail", fence_brushes))


def _build_brick_wall(BRUSHES, ENTITIES):
    """Build the west brick wall, gate, pillars, and pier-side fence run."""

    wall_hw = DORM_BRICK_WALL_HW

    if BRIDGE_ENABLED_SPAN_CENTER:
        wall_shift_y = BRIDGE_CENTER_SPAN_OFFSET[1]
        wall_shift_z = BRIDGE_CENTER_SPAN_OFFSET[2]
    else:
        wall_shift_y = 0
        wall_shift_z = 0
    bridge_top_z = BRIDGE_DZ2 + wall_shift_z
    wall_start_y = DORM_SOUTH2_Y2 + wall_shift_y
    s_door_y = DORM_SOUTH2_Y2 + DORM_DOOR_OFF + wall_shift_y
    wall_end_y = DORM_WALL_S_Y2 + wall_shift_y

    gate_base = FLOOR_Z2 + SDORM_LIFT
    gate_top = gate_base + DORM_BRICK_GATE_H

    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            wall_start_y,
            FLOOR_Z2,
            DORM_PIER_X + wall_hw,
            s_door_y - DORM_DOOR_W // 2,
            bridge_top_z,
            Textures.BUILDING,
        )
    )
    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            s_door_y + DORM_DOOR_W // 2,
            FLOOR_Z2,
            DORM_PIER_X + wall_hw,
            wall_end_y,
            bridge_top_z,
            Textures.BUILDING,
        )
    )
    BRUSHES.append(
        box(
            DORM_PIER_X - wall_hw,
            s_door_y - DORM_DOOR_W // 2,
            gate_top,
            DORM_PIER_X + wall_hw,
            s_door_y + DORM_DOOR_W // 2,
            bridge_top_z,
            Textures.BUILDING,
        )
    )

    pillar_w = DORM_BRICK_PILLAR_W
    pillar_proud = DORM_BRICK_PILLAR_PROUD
    pillar_h = bridge_top_z + DORM_BRICK_PILLAR_H_OFFSET
    px1 = DORM_PIER_X - wall_hw - pillar_proud
    px2 = DORM_PIER_X + wall_hw + pillar_proud
    cap_h = DORM_BRICK_PILLAR_CAP_H
    cap_overhang = DORM_BRICK_PILLAR_CAP_OVH
    door_north = s_door_y + DORM_DOOR_W // 2
    for py1, py2 in [
        (
            door_north + DORM_BRICK_PILLAR_GAP,
            door_north + DORM_BRICK_PILLAR_GAP + pillar_w,
        ),
        (
            door_north
            + DORM_BRICK_PILLAR_GAP
            + pillar_w
            + DORM_BRICK_PILLAR_SEPARATION,
            door_north
            + DORM_BRICK_PILLAR_GAP
            + pillar_w
            + DORM_BRICK_PILLAR_SEPARATION
            + pillar_w,
        ),
    ]:
        pillar_brushes = [
            box(px1, py1, FLOOR_Z2, px2, py2, pillar_h, Textures.BUILDING),
            box(
                px1 - cap_overhang,
                py1 - cap_overhang,
                pillar_h,
                px2 + cap_overhang,
                py2 + cap_overhang,
                pillar_h + cap_h,
                Textures.BUILDING,
            ),
        ]
        ENTITIES.append(brush_ent("func_detail", pillar_brushes))
    fence_brushes = iron_fence(
        [
            (wall_start_y, s_door_y - DORM_DOOR_W // 2),
            (
                s_door_y - DORM_DOOR_W // 2,
                s_door_y + DORM_DOOR_W // 2,
            ),
            (s_door_y + DORM_DOOR_W // 2, wall_end_y),
        ],
        DORM_PIER_X - 1,
        DORM_PIER_X + 1,
        Textures.FENCE,
        bridge_top_z,
    )
    if fence_brushes:
        ENTITIES.append(brush_ent("func_detail", fence_brushes))


def _build_sidewalk(BRUSHES):
    """Build the dorm-front terrace walk and its north spur.

    The walkway is tiled into square panels, extends south to CHARLES_Y1,
    and uses a terrain-following curb along its east edge.
    """
    walk_lift = SDORM_LIFT - 10
    _SW_SLAB_LEN = 80
    _SW_GAP = 2
    _CURB_W = 8
    _CURB_GAP = 2

    def slabs_y(x1, x2, y1, y2):
        """Tile a flat north-south run into square panels."""
        brushes = []
        step = _SW_SLAB_LEN + _SW_GAP
        y = y1
        while y > y2:
            sy2 = max(y - _SW_SLAB_LEN, y2)
            brushes.append(
                box(x1, sy2, FLOOR_Z2, x2, y, FLOOR_Z2 + walk_lift, Textures.STONE)
            )
            y -= step
        return brushes

    def curb_y(x1, x2, y1, y2):
        """Build a terrain-following curb along a north-south run."""
        brushes = []
        curb_cx = (x1 + x2) / 2
        ys = sorted({y1, y2} | {y for y in wct_y if y2 < y < y1}, reverse=True)
        for ny1, ny2 in zip(ys, ys[1:], strict=False):
            b1, b2 = terrain_z(curb_cx, ny1), terrain_z(curb_cx, ny2)
            brushes.append(
                ramp_slab_y(
                    x1,
                    x2,
                    ny1,
                    ny2,
                    b1,
                    b2,
                    FLOOR_Z2 + walk_lift,
                    FLOOR_Z2 + walk_lift,
                    Textures.STONE,
                )
            )
        return brushes

    walk = []

    walk.extend(
        slabs_y(
            DORM_FRONT_WALKWAY_X1, DORM_FRONT_WALKWAY_X2, DORM_SOUTH2_Y2, CHARLES_Y1
        )
    )

    walk.extend(
        slabs_y(
            DORM_FRONT_WALKWAY_SPUR_X1,
            DORM_FRONT_WALKWAY_X2,
            DORM_FRONT_WALKWAY_SPUR_Y2,
            DORM_SOUTH2_Y2,
        )
    )

    curb_x1 = DORM_FRONT_WALKWAY_X2 + _CURB_GAP
    curb_x2 = curb_x1 + _CURB_W
    walk.extend(curb_y(curb_x1, curb_x2, DORM_FRONT_WALKWAY_SPUR_Y2, CHARLES_Y1))
    BRUSHES.extend(walk)


def build():
    """Build west-campus buildings and terrain.

    Returns:
        tuple[list, list]: ``(brushes, entities)`` for the west-campus area,
        gated by the relevant ``WEST_CAMPUS_ENABLED_*`` config flags.
    """
    BRUSHES = []
    ENTITIES = []

    if (
        WEST_CAMPUS_ENABLED_FENCE
        or WEST_CAMPUS_ENABLED_WALL
        or WEST_CAMPUS_ENABLED_SIDEWALK
    ) and not WEST_CAMPUS_ENABLED_TERRAIN:
        raise ValueError(
            "west_campus.build(): WEST_CAMPUS_ENABLED_FENCE/WALL/SIDEWALK "
            "follow the real hillside terrain and require "
            "WEST_CAMPUS_ENABLED_TERRAIN to also be on — enable it (or "
            "disable the fence/wall/sidewalk) via `ql conf set`."
        )

    if WEST_CAMPUS_ENABLED_FENCE:
        _build_iron_fence(ENTITIES)

    if WEST_CAMPUS_ENABLED_WALL:
        _build_brick_wall(BRUSHES, ENTITIES)

    if WEST_CAMPUS_ENABLED_SIDEWALK:
        _build_sidewalk(BRUSHES)

    return BRUSHES, ENTITIES
