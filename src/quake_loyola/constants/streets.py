"""Charles Street, Ennis Road, and crosswalk constants."""

CHARLES_ARCH_RIN = 256
CHARLES_ARCH_ROUT = 312
CHARLES_ARCH_STILT = 96
CHARLES_ARCH_W = 48
CHARLES_CRN_SEGS = 12
CHARLES_LAMP_POST_EAST_SETBACK = 48
CHARLES_RAMP_W = 64
CHARLES_WALK_H = 8
CHARLES_WALK_W = 80

STREET_CHARLES_CURB_W = 8
# Sidewalk panel pitch: SW_SLAB_LEN of walking surface, then a dark
# SIDEWALK_JOINT stripe of SW_GAP. Shared by Charles St, Ennis Rd, and the
# Knott driveway walks so panels read as one paving system.
STREET_SW_SLAB_LEN = 80
STREET_SW_GAP = 2
# Curbs are poured in longer sections than sidewalk panels, and their joints
# are offset so they never line up with those of the walk running beside them.
STREET_CURB_SLAB_LEN = 124
STREET_CURB_JOINT_OFFSET = 60
STREET_DIV_HW = (
    6  # carved centerline slot half-width (doubled stripe thickness; see streets.py)
)
# Half-width of the unpainted gap down the middle of the carved centerline
# slot, which separates it into the two yellow lines of a double centerline.
STREET_DIV_GAP_HW = 2
STREET_ENNIS_DIV_HW = 16
STREET_SURFACE_T = 2
ROAD_X1, ROAD_X2 = -606, 256
# Charles St carries a travel lane and a parking lane on each side.
STREET_DIV_LINE_HW = 2  # Half-width of each parking-lane stripe.
# Those stripes are broken, as lane lines are on a real roadway. US practice
# (MUTCD) is a 1:3 line-to-gap ratio, drawn here as 10 ft of paint to 30 ft of
# road at SCALE = 15.108 units/ft. Both stripes are stepped off the same
# lattice so the dashes on either side of the street stay abreast of each
# other, and a dash clipped shorter than this by an intersection is dropped
# rather than left as a stub.
STREET_LANE_DASH_LEN = 151  # 10 ft
STREET_LANE_DASH_GAP = 453  # 30 ft
STREET_LANE_DASH_MIN = STREET_LANE_DASH_LEN // 3

# Crosswalk stripe geometry.
CROSSWALK_LEN = 80  # Depth along the direction of travel.
CROSSWALK_STRIPE_W = 32  # Stripe width across the crossing.
CROSSWALK_GAP_W = 32  # Gap width between stripes.
# Charles St's crossing is drawn at twice the Ennis crossing's stripe size, and
# its band steps south from west to east so the west end meets the lowered
# sidewalk entrance on that side. The gap between stripes stays at
# CROSSWALK_GAP_W, so the doubled stripes read as a chunkier zebra rather than
# just a coarser one.
CHARLES_CROSSWALK_LEN = 2 * CROSSWALK_LEN
CHARLES_CROSSWALK_STRIPE_W = 2 * CROSSWALK_STRIPE_W
