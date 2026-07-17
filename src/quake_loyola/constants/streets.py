"""Charles St / road / crosswalk constants (streets.py)."""

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

ROAD_DASH_LEN = 64
ROAD_GAP_LEN = 64
STREET_CHARLES_CURB_W = 8
STREET_DIV_HW = (
    6  # carved centerline slot half-width (doubled stripe thickness; see streets.py)
)
STREET_ENNIS_DIV_HW = 16
STREET_SURFACE_T = 2
ROAD_X1, ROAD_X2 = -306, 256
# ROAD_X1 shifted 50 units further west (was -256) to widen Charles St to the
# west, in step with the matching +50 bump to BRIDGE_CENTER_PIER_SPAN
# (constants/bridge.py) — the two move together so the Pier2-to-curb setback
# stays the same while the bridge's compressed centre span gets more room and
# everything already positioned relative to the west bridge pier group
# (DORM_PIER_X and its dependents) follows automatically.
# Charles St curb-to-curb width models 1 travel lane + 1 parking lane each side
# (see docs/reference.rst "Charles St width validation" + satellite re-check):
# parking lane nearest each curb, travel lane between it and the centerline.
# The parking/travel split (CHARLES_PARKING_LINE_X, streets.py) is derived
# from ROAD_X2/STREET_DIV_HW directly rather than a fixed lane width, so the
# two lanes come out equal width.
STREET_DIV_LINE_HW = 2  # half-width of each parking-lane stripe (dashed, white)

# ── Pedestrian crosswalks — thick white zebra stripes, flush with the road
# surface (carved out of the road/lane-marking brushes, same technique as the
# centerline and parking-lane stripes). See streets.py "PEDESTRIAN CROSSWALKS".
CROSSWALK_LEN = 80  # depth of the crossing along the direction of travel
CROSSWALK_STRIPE_W = 32  # width of each white stripe, across the crossing
CROSSWALK_GAP_W = 32  # gap between stripes (shows the road texture below)
