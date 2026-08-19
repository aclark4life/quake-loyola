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

# Walk outside the ground-level north door. As at the building's own east
# entrance, the walk leaves the doorway at grade, runs level for a short
# stretch, drops a single short flight of steps with a pipe rail either
# side, and then continues to Ennis as a cement path laid on the hillside.
# The flight is placed by working out where its bottom tread lands the path
# on the hillside: the path lies at ground level, standing only
# ``KNOTT_DOOR_WALK_PATH_PROUD`` — its own slab thickness — above the
# surrounding grade. The hillside stops dead at the Ennis walk line, which
# this far west is an 8-unit drop onto open ground, so the path runs on a
# further ``KNOTT_DOOR_WALK_PATH_TAIL`` to ramp that ledge away rather than
# leaving the walker to step off it.
# The steps carry a thin pipe rail either side, running level for
# ``KNOTT_DOOR_WALK_RAIL_END`` past each end of the flight on a single post,
# which gives it the flattened S the real ones have. Each level end carries
# on ``KNOTT_DOOR_WALK_RAIL_OVH`` past its post rather than stopping on it.
KNOTT_DOOR_WALK_RISE = 8
KNOTT_DOOR_WALK_TREAD = 16
KNOTT_DOOR_WALK_STEPS = 6
KNOTT_DOOR_WALK_PATH_PROUD = 2
KNOTT_DOOR_WALK_PATH_TAIL = 48
KNOTT_DOOR_WALK_RAIL_H = 44
KNOTT_DOOR_WALK_RAIL_T = 3
KNOTT_DOOR_WALK_RAIL_END = 16
KNOTT_DOOR_WALK_RAIL_OVH = 6


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
