import random

from ..constants import (
    ARCH_SLAB_W,
    BRIDGE,
    CHARLES_WALK_W,
    DORM,
    DORM_SOUTH1_Y1,
    DORM_SOUTH2_Y2,
    ENNIS_CEMENT_X1,
    ENNIS_GATE_X1,
    ENNIS_HW,
    ENNIS_WALL_NY,
    ENNIS_WALL_T,
    ENNIS_Y,
    ENTITIES_ENABLED_VEGETATION,
    FLOOR_Z2,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_ORIG_CX,
    KNOTT_Z2,
    ROAD_X1,
    ROAD_X2,
    WALL_T,
    WORLD_X2,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
)
from ..geometry import (
    brush_ent,
    ent,
    make_bush,
    make_giant_tree,
    make_pixel_tree,
)


def _build_vegetation(ENTITIES):
    if not ENTITIES_ENABLED_VEGETATION:
        return

    _tree_cx = KNOTT.x1 - 200
    _tree_cy = (KNOTT.y1 + KNOTT.y2) // 2
    all_tree_brushes = make_pixel_tree(
        _tree_cx,
        _tree_cy,
        FLOOR_Z2,
        profile="large",
        vox_size=8,
        trunk_solid=True,
        ring_segs=12,
    )
    ENTITIES.append(brush_ent("func_detail", all_tree_brushes))

    for _lx, _ly, _lz, _intensity in [
        (_tree_cx, _tree_cy, FLOOR_Z2 + 24, 150),
        (_tree_cx - 96, _tree_cy, FLOOR_Z2 + 180, 200),
        (_tree_cx + 96, _tree_cy, FLOOR_Z2 + 180, 200),
    ]:
        ENTITIES.append(
            ent("light", origin=f"{_lx} {_ly} {_lz}", light=str(_intensity))
        )

    charles_tree_height = int(KNOTT_Z2 * 0.65)
    knott_tree_span = KNOTT.y2 - KNOTT.y1
    charles_tree_row_near_x = ROAD_X2 + CHARLES_WALK_W + 300
    charles_tree_row_far_x = ROAD_X2 + CHARLES_WALK_W + 560

    charles_tree_row2_ys = [int(KNOTT.y1 + knott_tree_span * f) for f in (0.25, 0.75)]

    charles_tree_row3_ys = [int(KNOTT.y1 + knott_tree_span * f) for f in (0.15, 0.85)]
    charles_giant_tree_brushes = []
    for tree_y in charles_tree_row2_ys:
        charles_giant_tree_brushes += make_giant_tree(
            charles_tree_row_near_x, tree_y, FLOOR_Z2, charles_tree_height
        )
    for tree_y in charles_tree_row3_ys:
        charles_giant_tree_brushes += make_giant_tree(
            charles_tree_row_far_x, tree_y, FLOOR_Z2, charles_tree_height
        )
    ENTITIES.append(brush_ent("func_detail", charles_giant_tree_brushes))

    kh_tree_rng = random.Random(7)
    kh_drive_tree_x = KNOTT_DRIVEWAY_ES_X2 + 80
    kh_drive_tree_spacing = 300
    kh_drive_tree_height = int(KNOTT_Z2 * 0.65)
    kh_drive_tree_brushes = []
    kh_grid_y = BRIDGE.y1 - kh_drive_tree_spacing
    while kh_grid_y >= KNOTT_DRIVEWAY_Y1:
        tree_x = kh_drive_tree_x + kh_tree_rng.randint(-40, 40)
        tree_y = kh_grid_y + kh_tree_rng.randint(-80, 80)
        tree_h = kh_drive_tree_height + kh_tree_rng.randint(-60, 60)
        if tree_y >= KNOTT_DRIVEWAY_Y2:
            tree_z = FLOOR_Z2
        else:
            kh_t = (KNOTT_DRIVEWAY_Y2 - tree_y) / (
                KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1
            )
            tree_z = int(
                KNOTT_DRIVEWAY_ZT_N + kh_t * (KNOTT_DRIVEWAY_ZT_S - KNOTT_DRIVEWAY_ZT_N)
            )
        kh_drive_tree_brushes += make_giant_tree(tree_x, tree_y, tree_z, tree_h)
        kh_grid_y -= kh_drive_tree_spacing
    ENTITIES.append(brush_ent("func_detail", kh_drive_tree_brushes))

    sdorm_front_tree_height = 520
    sdorm_front_tree_x = ROAD_X1 - 400
    sdorm_front_tree_y1 = DORM_SOUTH1_Y1 + 150
    sdorm_front_tree_y2 = DORM_SOUTH2_Y2 - 150
    sdorm_front_tree_brushes = []
    for tree_y in (sdorm_front_tree_y1, sdorm_front_tree_y2):
        sdorm_front_tree_brushes += make_giant_tree(
            sdorm_front_tree_x, tree_y, FLOOR_Z2, sdorm_front_tree_height
        )
    ENTITIES.append(brush_ent("func_detail", sdorm_front_tree_brushes))

    east_ground_tree_height = int(KNOTT_Z2 * 0.65)
    east_ground_spacing = 350
    east_ground_jitter = 120
    east_ground_buffer = 120
    east_ground_x1 = ROAD_X2 + CHARLES_WALK_W + east_ground_buffer
    east_ground_x2 = WORLD_X2_EXT - WALL_T - east_ground_buffer
    east_ground_y1 = ENNIS_WALL_NY + ENNIS_WALL_T + 200
    east_ground_y2 = WORLD_Y2 - WALL_T - east_ground_buffer

    tree_rng = random.Random(42)

    east_ground_giant_brushes = []
    grid_x = east_ground_x1
    while grid_x <= east_ground_x2:
        grid_y = east_ground_y1
        while grid_y <= east_ground_y2:
            tree_x = grid_x + tree_rng.randint(-east_ground_jitter, east_ground_jitter)
            tree_y = grid_y + tree_rng.randint(-east_ground_jitter, east_ground_jitter)
            tree_x = max(east_ground_x1, min(east_ground_x2, tree_x))
            tree_y = max(east_ground_y1, min(east_ground_y2, tree_y))
            east_ground_giant_brushes += make_giant_tree(
                tree_x, tree_y, FLOOR_Z2, east_ground_tree_height
            )
            grid_y += east_ground_spacing
        grid_x += east_ground_spacing
    ENTITIES.append(brush_ent("func_detail", east_ground_giant_brushes))

    east_side_tree_height = int(KNOTT_Z2 * 0.65)
    east_side_foliage_hw = 160
    _ennis_south = ENNIS_Y - ENNIS_HW
    _ennis_sw_edge = _ennis_south - 3 * CHARLES_WALK_W - 32
    east_tele_brushes = []
    et_rng = random.Random(43)
    et_x1 = WORLD_X2 + WALL_T + east_side_foliage_hw + 20
    et_x2 = WORLD_X2_EXT - WALL_T - east_side_foliage_hw
    et_y1 = WORLD_Y1 + WALL_T + 120
    et_y2 = _ennis_sw_edge - east_side_foliage_hw
    et_min_dist = 280
    et_placed = []
    for _ in range(300):
        cx = et_rng.randint(et_x1, et_x2)
        cy = et_rng.randint(et_y1, et_y2)
        if all(
            (cx - px) ** 2 + (cy - py) ** 2 >= et_min_dist**2 for px, py in et_placed
        ):
            et_placed.append((cx, cy))

    # Clear the tree nearest each end of the live Ennis east teleport arch
    # footprint (see entities/spawns.py:_append_ennis_east_teleport) so
    # vegetation never overlaps the teleport trigger/arch.
    _ennis_arch_x1 = WORLD_X2_EXT - WALL_T - ARCH_SLAB_W
    _ennis_arch_x2 = WORLD_X2_EXT - WALL_T
    for target in ((_ennis_arch_x1, ENNIS_Y), (_ennis_arch_x2, ENNIS_Y)):
        et_placed.sort(key=lambda p, t=target: (p[0] - t[0]) ** 2 + (p[1] - t[1]) ** 2)
        et_placed = et_placed[1:]
    for cx, cy in et_placed:
        east_tele_brushes += make_giant_tree(cx, cy, FLOOR_Z2, east_side_tree_height)
    ENTITIES.append(brush_ent("func_detail", east_tele_brushes))

    bush_positions = [
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 60, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 160, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 260, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        ((ROAD_X2 + CHARLES_WALK_W + 48) + 360, ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 120), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 300), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 500), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_GATE_X1 + 700), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 120), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 320), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (int(ENNIS_CEMENT_X1 + 560), ENNIS_WALL_NY + ENNIS_WALL_T + 40),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2 - 200),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2),
        (KNOTT.x1 - 48, (KNOTT.y1 + KNOTT.y2) // 2 + 200),
        (DORM.x2 + 48, -200),
        (DORM.x2 + 48, 200),
        (DORM.x2 + 48, 500),
    ]
    all_bush_brushes = []
    for bush_x, bush_y in bush_positions:
        all_bush_brushes += make_bush(bush_x, bush_y, FLOOR_Z2)

    knott_verge_y = ENNIS_Y - ENNIS_HW - 100
    knott_bush_spacing = 120
    knott_bush_buffer = 60
    knott_bush_size = 40
    knott_bush_jitter_x = 40
    knott_bush_jitter_y = 30
    knott_verge_brushes = []
    for verge_x1, verge_x2 in [
        (
            ROAD_X2 + CHARLES_WALK_W + knott_bush_buffer,
            KNOTT_ORIG_CX - 64 - knott_bush_buffer,
        ),
        (
            KNOTT_ORIG_CX + 64 + knott_bush_buffer,
            KNOTT_DRIVEWAY_CORRIDOR_X1 - knott_bush_buffer,
        ),
    ]:
        bush_x = verge_x1
        while bush_x <= verge_x2:
            jittered_x = bush_x + tree_rng.randint(
                -knott_bush_jitter_x, knott_bush_jitter_x
            )
            jittered_y = knott_verge_y + tree_rng.randint(
                -knott_bush_jitter_y, knott_bush_jitter_y
            )
            knott_verge_brushes += make_bush(
                jittered_x, jittered_y, FLOOR_Z2, size=knott_bush_size
            )
            bush_x += knott_bush_spacing
    all_bush_brushes += knott_verge_brushes

    ENTITIES.append(brush_ent("func_detail", all_bush_brushes))
