"""West-campus dorm building constants and the DormSpec dataclass."""

from dataclasses import dataclass

DORM_DEPTH = 450
DORM_FENCE_OFFSET = 216
DORM_FRONT_WALKWAY_FENCE_OFFSET = 40
DORM_FRONT_WALKWAY_W = 96
DORM_BRICK_PILLAR_CAP_H = 10
DORM_BRICK_PILLAR_CAP_OVH = 1
DORM_BRICK_PILLAR_GAP = 96
DORM_BRICK_PILLAR_H_OFFSET = 80
DORM_BRICK_PILLAR_PROUD = 6
DORM_BRICK_PILLAR_SEPARATION = 380
DORM_BRICK_PILLAR_W = 56
DORM_BRICK_WALL_HW = 12
DORM_BRICK_GATE_H = 96
DORM_DOOR_OFF = 160
DORM_DOOR_W = 80
DORM_FLOORS = 3
DORM_WALL_T = 16


@dataclass
class DormSpec:
    floor_h: int
    floors: int
    wall_t: int
    depth: int
    x1: int
    x2: int
