"""Charles Street, Ennis Road, and crosswalk constants."""

CHARLES_ARCH_RIN = 256
CHARLES_ARCH_ROUT = 312
CHARLES_ARCH_STILT = 96
CHARLES_ARCH_TRIG_INSET = 8
CHARLES_ARCH_W = 48
CHARLES_CRN_SEGS = 12
CHARLES_LAMP_POST_EAST_SETBACK = 48
CHARLES_PLT_H = 12
CHARLES_PLT_SPEED = 180
CHARLES_PLT_W = 128
CHARLES_RAMP_W = 64
CHARLES_WALK_H = 8
CHARLES_WALK_W = 80

STREET_CHARLES_CURB_W = 8
STREET_DIV_HW = (
    6  # carved centerline slot half-width (doubled stripe thickness; see streets.py)
)
STREET_ENNIS_DIV_HW = 16
STREET_SURFACE_T = 2
ROAD_X1, ROAD_X2 = -606, 256
# Charles St carries a travel lane and a parking lane on each side.
STREET_DIV_LINE_HW = 2  # Half-width of each parking-lane stripe.

# Crosswalk stripe geometry.
CROSSWALK_LEN = 80  # Depth along the direction of travel.
CROSSWALK_STRIPE_W = 32  # Stripe width across the crossing.
CROSSWALK_GAP_W = 32  # Gap width between stripes.
