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
# Control joints scoring the cement partitions around each storey's bridge
# entrance, elevator, and stair lobby. Poured cement that long cracks unless
# it is given somewhere to: the panels are KNOTT_CORE_WALL_JOINT_LEN long,
# parted by a KNOTT_CORE_WALL_JOINT_W groove held KNOTT_CORE_WALL_JOINT_D
# back from both faces so it reads from either side of the wall.
# The elevator car running the lift shaft. It is a car rather than a bare
# platform: a floor, a ceiling, and four walls, the one facing the lobby
# opened for the shaft's own door to line up with. KNOTT_LIFT_CAR_T is the
# thickness of every one of those, and the clear height inside is what
# KNOTT_LIFT_CAR_H leaves between the floor and the ceiling.
KNOTT_LIFT_CAR_W = 128
KNOTT_LIFT_CAR_D = 128
KNOTT_LIFT_CAR_H = 160
KNOTT_LIFT_CAR_T = 8
# How far the car stands off the shaft wall, leaving the sill gap a real
# elevator has between car and landing. Well under the 32-unit player hull,
# so nobody can drop down it.
KNOTT_LIFT_CAR_GAP = 8
# How far the sill plate stands proud of the ground-storey deck. The deck
# runs solid under the shaft, so a recessed stripe would be buried in it and
# never drawn; a proud one reads from every angle and is far below the
# 18-unit step height, so nobody feels it underfoot.
KNOTT_LIFT_SILL_PROUD = 1
KNOTT_LIFT_CAR_SPEED = 200
KNOTT_LIFT_CAR_TARGET = "knott_lift_car"
# How long the car stands at the top storey before returning to the ground
# one. It is counted from the moment it arrives, not from the moment the
# passenger steps out, so it has to be long enough to get out in.
KNOTT_LIFT_CAR_WAIT = 8
KNOTT_CORE_WALL_JOINT_LEN = 96
KNOTT_CORE_WALL_JOINT_W = 2
KNOTT_CORE_WALL_JOINT_D = 2
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
# Flanking the flight, outside the walk rather than eating into its width,
# runs a cement cheek ``KNOTT_DOOR_WALK_CAP_W`` wide either side. Its cap
# meets the walk's own level at the top step and rakes down to
# ``KNOTT_DOOR_WALK_CAP_PROUD`` above the bottom step — shallower than the
# steps, so the cheek rises out of the walk as they fall away beneath it —
# running on level past both ends of the flight to carry the rail's posts.
# The joint scored between cheek and walk is sunk
# ``KNOTT_DOOR_WALK_CAP_JOINT_DROP`` rather than the shallow street-sidewalk
# drop: it is read along the top of a raised cheek rather than across a flat
# walk, so a groove deep enough to shadow is what makes it a line at all.
# The rail runs centred along the cap, its posts standing on it.
KNOTT_DOOR_WALK_RISE = 8
KNOTT_DOOR_WALK_TREAD = 16
KNOTT_DOOR_WALK_STEPS = 7
KNOTT_DOOR_WALK_PATH_PROUD = 2
KNOTT_DOOR_WALK_PATH_TAIL = 48
KNOTT_DOOR_WALK_RAIL_H = 44
KNOTT_DOOR_WALK_RAIL_T = 3
KNOTT_DOOR_WALK_RAIL_END = 16
KNOTT_DOOR_WALK_RAIL_OVH = 6
KNOTT_DOOR_WALK_CAP_W = 16
KNOTT_DOOR_WALK_CAP_PROUD = 8
KNOTT_DOOR_WALK_CAP_JOINT_DROP = 4

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
# The route is derived rather than surveyed: the landing is placed snug
# against the east-most drop pillar's own clearance, from which the west
# leg's run -- and the grade that run leaves -- follow. That keeps the south
# leg (and its rail) as short as the pillar allows, at whatever grade results.
# The west leg follows the Ennis walk regardless -- further south the
# hillside climbs 13% against the ramp's own grade, and the ramp would bury
# itself in the bank -- but it is pulled ``KNOTT_RAMP_SOUTH_SHIFT`` off the
# walk's edge so its south face meets Pier 5's stonework underneath it,
# rather than running flush against the walk. And the south leg has to
# thread between the drop pillars under the bridge span, so the landing
# sits ``KNOTT_RAMP_PILLAR_GAP`` clear of the nearest one.
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
KNOTT_RAMP_PILLAR_GAP = 16
# Pulls the whole ramp south, off the Ennis walk it would otherwise hug
# flush, until its south edge meets Pier 5's stonework beneath the west leg.
KNOTT_RAMP_SOUTH_SHIFT = 31
KNOTT_RAMP_RAIL_H = 44
KNOTT_RAMP_RAIL_T = 3
KNOTT_RAMP_RAIL_LOOP_H = 24
KNOTT_RAMP_RAIL_POSTS = 4
KNOTT_RAMP_RAIL_OVH = 6
# The rail also turns the corner at the landing's west edge and continues a
# short distance south along the south leg, still as one unbroken railing.
KNOTT_RAMP_RAIL_CORNER_RUN = 48


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
