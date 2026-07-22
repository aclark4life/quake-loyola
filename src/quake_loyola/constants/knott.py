"""Knott Hall constants and the KnottSpec dataclass."""

from dataclasses import dataclass

from ..config import get as _flag
from .world import INDENT

KNOTT_DRIVEWAY_HW = 128
KNOTT_ENABLED_EXTERIOR = _flag(
    "KNOTT_ENABLED_EXTERIOR"
)  # KH exterior (walls, windows, roof, sign)
KNOTT_ENABLED_INTERIOR = _flag(
    "KNOTT_ENABLED_INTERIOR"
)  # temporarily disabled — KH interior (floor slabs, stairs, hallway walls, partitions)
KNOTT_ENABLED_MONSTERS = _flag(
    "KNOTT_ENABLED_MONSTERS"
)  # temporarily disabled — KH monsters (ogres + knights inside/on KH)
KNOTT_FLOORS = 5
KNOTT_FLOOR_H = 192
KNOTT_MULLION_PROUD = 12
KNOTT_MULLION_W = 12
KNOTT_BUILDING_W = 1280
KNOTT_WEST_TO_ORIG_CX = (
    (KNOTT_BUILDING_W + INDENT) // 2 + 64
)  # entrance + center window + bridge landing anchored on the true facade center;
# +64 shifts them east to match the curtain-wall position in the reference photos (ref/bridge01);
# capped so the accessible-entrance ramp still meets the fixed accessible path pad (X=2152)
KNOTT_WEST_TO_PIER_X = 40
KNOTT_ROOM_SPLITS = [-1072, -950, -1200, -850, -1300]
KNOTT_SHELF_D = 16
KNOTT_SHELF_H = 64
KNOTT_SHELF_W = 64
KNOTT_SIGN_PX_W, KNOTT_SIGN_PX_H = 3, 6
KNOTT_SIGN_TEXT = "MARION BURK KNOTT HALL"
KNOTT_SIGN_H = 72
KNOTT_SIGN_PADDING = 4
KNOTT_SIGN_Z_OFFSET = 20
KNOTT_SIDE_WINDOW_DIV_W = 12
KNOTT_SIDE_WINDOW_HALF_W = 120
KNOTT_SIDE_WINDOW_INNER_LEFT = 48
KNOTT_SIDE_WINDOW_INNER_RIGHT = 36
KNOTT_SIDE_WINDOW_PROTRUSION = 12
KNOTT_SHAFT_WALL = 8
KNOTT_STAIRS_HALF_N = 8
KNOTT_STAIRS_POST_W = 4
KNOTT_STAIRS_RAIL_H = 72
KNOTT_STAIRS_RAIL_T = 4
KNOTT_STAIRS_STEP_R = KNOTT_FLOOR_H // (2 * KNOTT_STAIRS_HALF_N)
KNOTT_STAIRS_TREAD_X = 24
KNOTT_ENABLED_WALKWAY = _flag("KNOTT_ENABLED_WALKWAY")
KNOTT_ENABLED_WALKWAY_BENT = _flag(
    "KNOTT_ENABLED_WALKWAY_BENT"
)  # concrete support bent (crossbeam + 5 drop piers) under the south edge of
# the KH span, independent of KNOTT_ENABLED_WALKWAY (the ramp/rails/tubes/
# accessible-walkway) so the bent can be reviewed/built on its own.
KNOTT_WALL = 16
KNOTT_FRONT_WINDOW_HALF_W = 48
KNOTT_FRONT_WINDOW_MULLION_HALF_GAP = 6
KNOTT_Y1, KNOTT_Y2 = -1888, -233  # KNOTT_Y2 shifts KH 23 units closer to the bridge,
# undoing the incidental walkway-span stretch introduced when BRIDGE_Y1 narrowed the
# deck (-136 -> -113, see commit 87a86f6); restores the walkway gap
# (KNOTT_Y2 - BRIDGE_Y1) to ~120 units, matching the near-flush bridge/KH landing
# seen in ref/gmaps-kh-streetview-east.png.


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
