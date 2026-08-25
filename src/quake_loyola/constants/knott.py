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
# Gap between each entrance-walkway support pillar's top and the beam it
# carries, filled with a SIDEWALK_JOINT seam like a sidewalk panel joint, so
# the pillar reads as its own poured element rather than continuous with the
# beam above it.
KNOTT_SUPPORT_PILLAR_JOINT_H = 4
KNOTT_Y1, KNOTT_Y2 = -1888, -233  # Bridge-facing facade bounds.
KNOTT_ROOF_T = 16
KNOTT_PARAPET_H = 24  # Raised lip around the roof edge, per satellite
# reference — the roof deck itself sits at the wall top (z2), with the
# parapet standing KNOTT_PARAPET_H above it, so the rim reads as proud of
# the roof without dipping the roof deck down into the window tops (which
# also stop at z2).
KNOTT_BUILDING_H = 1523  # Was 1640; net effect of two window panes removed
# (2 x 78 units) plus half a pane (39 units, EXTRA_BASE_H in knott_hall.py)
# added back so the ground-floor door/entrance is 1.5 panes tall instead of
# 1, with every other window pane on every wall staying exactly 78
# tall/unchanged.

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
KNOTT_DOOR_WALK_STEPS = 7
KNOTT_DOOR_WALK_PATH_PROUD = 2
KNOTT_DOOR_WALK_PATH_TAIL = 48
KNOTT_DOOR_WALK_RAIL_H = 44
KNOTT_DOOR_WALK_RAIL_T = 3
KNOTT_DOOR_WALK_RAIL_END = 16
KNOTT_DOOR_WALK_RAIL_OVH = 6

# Walk hugging the Knott north face east of that door, running on to the
# driveway. It stays level on the flat crest of the hillside, then drops the
# bank between the crest and the driveway as a single flight of steps. That
# bank is short and steep — it loses the whole crest height in under a
# hundred units — so the flight is steep to match: its rise is whatever
# divides the drop into ``KNOTT_EAST_WALK_RISERS`` even risers, and it is
# placed as far west as it can go without any tread cutting below the bank,
# which is what keeps it hugging the slope instead of standing off it. The
# last riser lands on the driveway's own west sidewalk, so only
# ``RISERS - 1`` treads are actually built.
KNOTT_EAST_WALK_W = 80
KNOTT_EAST_WALK_RISERS = 6
KNOTT_EAST_WALK_TREAD = 14
KNOTT_EAST_WALK_RAIL_H = 44
KNOTT_EAST_WALK_RAIL_T = 3
KNOTT_EAST_WALK_RAIL_END = 16
KNOTT_EAST_WALK_RAIL_OVH = 6

# Accessible ramp from the Knott driveway up to that east walk, which is the
# step-free way on to the north door. It leaves the driveway roadbed at the
# gutter, cutting the curb over its own width, climbs west along the foot of
# the Ennis walk until it is clear of the bridge piers, turns south on a
# level landing, and runs back down the hillside to meet the east walk's
# level run at the crest height.
#
# The route is derived rather than surveyed: the landing is placed wherever a
# ``1:KNOTT_RAMP_RISE_RUN`` grade puts it, working back from the two fixed
# ends. Two things constrain it. The west leg has to hug the Ennis walk —
# further south the hillside climbs 13% against the ramp's 8%, and the ramp
# would bury itself in the bank — so its north edge runs flush with that
# walk. And the south leg has to thread between the drop pillars under the
# bridge span, so the landing is pushed east until it clears the nearest
# pillar by ``KNOTT_RAMP_PILLAR_GAP``. That push fixes the run at roughly 900
# units, which is what stops the ramp reaching a true 1:12: carrying it down
# over the curb to the roadbed, rather than stopping it at the walk behind,
# spends a further curb's worth of rise on that same run.
# ``KNOTT_RAMP_RISE_RUN_MIN`` is the shallowest grade still worth building.
#
# Only the west leg's north side is railed, and it is the one side that has
# to be: the Ennis walk runs right along it, so the ramp climbs away from a
# walking surface and leaves a drop. The other three edges either retain the
# hillside or face the driveway at its own level. The rail is the accessible
# kind rather than the single pipe used beside a flight of steps -- a top
# rail with a lower one under it, turned through a half-round at each end so
# the pair closes into one long O, carried on ``KNOTT_RAMP_RAIL_POSTS``
# pillars that run the full height through both rails.
KNOTT_RAMP_W = 72
KNOTT_RAMP_RISE_RUN = 12
KNOTT_RAMP_RISE_RUN_MIN = 10
KNOTT_RAMP_PILLAR_GAP = 16
KNOTT_RAMP_RAIL_H = 44
KNOTT_RAMP_RAIL_T = 3
KNOTT_RAMP_RAIL_LOOP_H = 24
KNOTT_RAMP_RAIL_POSTS = 4
KNOTT_RAMP_RAIL_OVH = 6


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
