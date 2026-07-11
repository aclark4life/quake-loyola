"""West-campus dorm building constants and the DormSpec dataclass."""

from dataclasses import dataclass

DORM_DEPTH = 450
DORM_FENCE_OFFSET = 216
DORM_FRONT_WALKWAY_FENCE_OFFSET = 40
DORM_FRONT_WALKWAY_W = 96
DORM_GABLE_DEPTH = 6
DORM_INNER_DOOR_H = 128
DORM_INNER_DOOR_HW = 56
DORM_BRICK_PILLAR_CAP_H = 10
DORM_BRICK_PILLAR_CAP_OVH = 1
DORM_BRICK_PILLAR_GAP = 96
DORM_BRICK_PILLAR_H_OFFSET = 80
DORM_BRICK_PILLAR_PROUD = 6
DORM_BRICK_PILLAR_SEPARATION = 380
DORM_BRICK_PILLAR_W = 56
DORM_BRICK_WALL_HALF_W = 12
DORM_BRICK_GATE_H = 96
DORM_DOOR_H = (
    128  # door opening height — embankment rises ~56 units at wall, need clearance
)
DORM_DOOR_OFF = 160
DORM_DOOR_W = 80
DORM_EMB_X2 = -1146
DORM_ENT_H = 100
DORM_ENT_HW = 48
DORM_FLOORS = 3
DORM_SLAB_T = 16
DORM_WALL = 16
DORM_WIN_HH = 44
DORM_WIN_HW = 36
DORM_WIN_MARGIN = 0  # gap between window frame bar and opening edge (0 = flush)
DORM_WIN_W, DORM_WIN_H, DORM_WIN_T = 20, 28, 3


@dataclass
class DormSpec:
    floor_h: int
    floors: int
    wall_t: int
    depth: int
    x1: int
    x2: int
