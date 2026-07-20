"""Ennis Road / Ennis Drive entrance constants (gate, fence, pillars, panels)."""

ENNIS_CURB_W = 8
ENNIS_CEMENT_WALL_CAP_H = 6
ENNIS_CEMENT_WALL_CAP_OVH = 2
ENNIS_CEMENT_WALL_H = 32
ENNIS_CEMENT_WALL_LAMP_POST_H = 160
ENNIS_CEMENT_WALL_PILLAR_EXTRA_H = 16
ENNIS_CEMENT_WALL_PILLAR_HW = 14
ENNIS_CURB_BULGE_LEN = 400  # ~ two car lengths; shared by the north curb's
# semi-circular bump-out (streets.py build()) and the cement wall extension
# that runs alongside it (streets.py build_ennis_entrance_features()), so the
# wall's new east end pillar/cap lines up with the far end of the curve.
ENNIS_CEMENT_WALL_PILLAR_SPACING = 800  # nominal spacing of the repeating
# straight-run pillars east of the curved bulge — same magnitude as the curb
# bulge length above, for a consistent rhythm. The final span is stretched
# slightly (never shortened) so the last pillar always lands exactly on the
# run's east endpoint rather than leaving an odd short leftover segment.
ENNIS_GATE_FENCE_BAR_T = 2
ENNIS_GATE_FENCE_HEIGHT = 96
ENNIS_GATE_FENCE_POST_W = 8
ENNIS_GATE_FENCE_SPACING = 16
ENNIS_GATE_FENCE_TOP_RAIL_DROP = 28
ENNIS_GATE_FENCE_TOP_RAIL_T = 2
ENNIS_GATE_FENCE_WEST_SHIFT = 24  # plain picket run sits this far west of the brick
# wall it used to butt against, so a short connector (post + cross rail) is needed
# to rejoin them at the south end of the picket run.
ENNIS_GATE_PANEL_COUNT = 12  # dozen decorative rectangular iron panels on the brick
ENNIS_GATE_PILLAR_LEG_T = 4  # leg thickness of the inverted-U (∩) separator pillars
ENNIS_GATE_PILLAR_OPENING_W = 12  # gap between the two legs of each ∩ pillar
ENNIS_GATE_PILLAR_GAP = 8  # clearance either side of a pillar, between it and a panel
ENNIS_GATE_PILLAR_EXTRA_H = 12  # how much taller the pillar is than a panel
ENNIS_GATE_PILLAR_CROSS_T = 2  # thickness of the decorative X cross-brace bars
ENNIS_PANEL_GAP = 8
ENNIS_PANEL_INNER_H = 12
ENNIS_PANEL_INNER_W = 28
ENNIS_PANEL_OUTER_H = 28
ENNIS_PANEL_OUTER_W = 48
ENNIS_PANEL_MOUNT_FOOT_DROP = 6  # how far the bracket drops onto the brick top
ENNIS_PANEL_MOUNT_FOOT_INSET = 6  # shift feet in from the corners toward center
ENNIS_HW = 160
# Extra width added to the road's north lane only (centerline/south lane
# unchanged) — makes room for the enlarged KH driveway junction bulges
# (KNOTT_DRIVEWAY_CURB_BULGE_D/FLAT_W). Everything anchored to the north
# edge (curb, sidewalk, verge, fence, wall, lamp posts, NE-quadrant terrain
# tie-in) shifts north by this amount along with it.
ENNIS_WIDEN_N = 64
# Extra nudge for the road's centerline/divider split point only (on top of
# the ENNIS_WIDEN_N / 2 curb-to-curb centering) — moves the stripe a bit
# further north without touching the curbs or overall road width.
ENNIS_DIVIDER_EXTRA_N = 16
ENNIS_PILLAR_BELL2_H = 27
ENNIS_PILLAR_BELL2_HW = (
    19  # tapered top section half-width (wider than before, less than post)
)
ENNIS_PILLAR_CAP_H = 3
ENNIS_PILLAR_CAP_OVH = 1
ENNIS_PILLAR_HW = 22
ENNIS_PILLAR_POST_H = 81
ENNIS_WALL_H = 96
ENNIS_WALL_PILLAR_H = (
    126  # 120 base + ENNIS_PANEL_MOUNT_FOOT_DROP, to stay taller than the raised gate
)
ENNIS_WALL_PILLAR_HW = 14
ENNIS_WALL_T = 8
ENNIS_WALL_X_OFFSET = 96
