"""Knott Hall constants and the KnottSpec dataclass."""

from dataclasses import dataclass

from .world import INDENT

KNOTT_DRIVEWAY_HW = 128
KNOTT_FLOORS = 5
KNOTT_FLOOR_H = 192
KNOTT_BUILDING_W = 1280
KNOTT_WEST_TO_ORIG_CX = (
    (KNOTT_BUILDING_W + INDENT) // 2 + 64
)  # Entrance, center window, and bridge landing center offset from the west facade.
KNOTT_WEST_TO_PIER_X = 40
KNOTT_SIGN_PX_W, KNOTT_SIGN_PX_H = 3, 6
KNOTT_SIGN_TEXT = "MARION BURK KNOTT HALL"
KNOTT_SIGN_H = 72
KNOTT_SIGN_PADDING = 4
KNOTT_SIGN_Z_OFFSET = 20
KNOTT_WALL_T = 16
KNOTT_Y1, KNOTT_Y2 = -1888, -233  # Bridge-facing facade bounds.


@dataclass
class KnottSpec:
    floors: int
    floor_h: int
    wall_t: int
    x1: int
    x2: int
    y1: int
    y2: int
    driveway_hw: int
