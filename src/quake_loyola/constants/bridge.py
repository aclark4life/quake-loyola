"""Bridge (Charles St pedestrian bridge) constants and the BridgeSpec dataclass."""

from dataclasses import dataclass

BRIDGE_ARCH_RISE = 100
BRIDGE_ARCH_PIER_RISE = 82  # deck rise at the centre-span piers (PIER2/PIER3, ±525):
# the centre span arches from here up to BRIDGE_ARCH_RISE over Charles St (X=0); the
# two approach spans descend straight from here to 0 at the outer piers (ref/bridge08)
BRIDGE_ACCESS_WALK_CENTER_X = 2120
BRIDGE_ACCESS_WALK_HALF_W = 32
BRIDGE_ACCESS_WALK_NORTH_OFFSET = 80
BRIDGE_ACCESS_WALK_PIER_CLEARANCE = 96
BRIDGE_BLK_H = 36
BRIDGE_BLK_HW = 24
BRIDGE_BLK_OVH = 0
BRIDGE_BLK_PIER_CLEARANCE = 4
BRIDGE_DECK_EAST_RECESS = 1
BRIDGE_DZ1, BRIDGE_DZ2 = (
    256,
    272,
)  # raised 32 units (was 224/240) so the flat deck at KNOTT_ORIG_CX (WALK_ZT1) is
# level with the KH 2nd-floor walkway landing (WALK_ZT2); see KNOTT_GROUND_Z below,
# now a fixed hill-height anchor independent of this deck elevation.
BRIDGE_EAST_SHIFT_START = 0.0
BRIDGE_EAST_SPAN_ANGLE = 12.0
BRIDGE_FASCIA_PX_W, BRIDGE_FASCIA_PX_H = (
    4,
    4,
)  # sized to fit just inside the middle span's two exterior parapet
# blocks (cx=-276/276, half-width BRIDGE_BLK_HW=24, so inner edges at
# -252/252 -> 504 units of clearance); at px_w=5 the lettering was
# 531 units wide, overlapping those blocks — px_w=4 comes to 402 units.
BRIDGE_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
BRIDGE_PAR_H = 40
BRIDGE_PILLAR_BASE_CAP_H = 6
BRIDGE_PILLAR_BASE_CAP_OVH = 5
BRIDGE_PILLAR_BASE_H = 64  # solid plinth height before the arch opening starts (was 24 originally — raised so more stone shows at the pier base before the archway begins)
BRIDGE_PILLAR_BASE_RAMP_H = 80  # ramped-side plinth height (was 40 originally — kept the same 16-unit rise over BASE_H)
BRIDGE_PILLAR_CAP_H = 12
BRIDGE_PILLAR_CAP_IN_OVH = 4
BRIDGE_PILLAR_CAP_OUT_OVH = 20
BRIDGE_PILLAR_EXTRA = 64
BRIDGE_PIER_BASE_LIGHTS_ENABLED = False  # temporarily disabled — pier-base lights (some sit buried in the east-span fill)
BRIDGE_PIER_FILL_OFFSET = 16
BRIDGE_PILLAR_INNER_R = (160, 84)
BRIDGE_PILLAR_OUTER_R = (140, 72)
BRIDGE_PILLAR_OVERHANG = 16
# Decorative square cement plates on the interior (facing the opposite pillar
# across the opening) and exterior (facing outward) walls of each arch/square
# pier. See bridge.py "Pillar posts" — plates protrude slightly from the flat
# pillar wall for a panelled look.
BRIDGE_PIER_PLATE_SIZE = 34
BRIDGE_PIER_PLATE_GAP = 3
BRIDGE_PIER_PLATE_D = (
    1  # plate protrusion depth from the pillar wall (slight, flush-ish)
)
# Cement lining covering the inside surfaces (stilt/side walls + curved
# intrados or lintel underside) of each pier's arch/square opening — leaves
# a stone border at each opening end (margin) before the lining begins.
BRIDGE_PIER_LINING_MARGIN = 6
BRIDGE_PIER_LINING_THICK = 3
BRIDGE_PILLAR_PYR_H = 20
BRIDGE_SEG_SPAN_W = 32
BRIDGE_SQ_D = 1
BRIDGE_SQ_HH = 6
BRIDGE_SQ_HW = 8
BRIDGE_SUPPORT_BEAM_H = 20
BRIDGE_SUPPORT_HALF_W = 16
BRIDGE_SUPPORT_PIER_HALF_W = 20
BRIDGE_TELEPORT_ARCH_CLEARANCE = 8
BRIDGE_TELEPORT_ARCH_X1_OFFSET = 2
BRIDGE_TELEPORT_ARCH_X2_OFFSET = 18
BRIDGE_TELEPORT_DEST_Z = 40
BRIDGE_TORCH_CUP_H = 4
BRIDGE_TORCH_CUP_HW = 5
BRIDGE_TORCH_POST_H = 16
BRIDGE_TORCH_POST_HW = 3
BRIDGE_TUBE_GAP = 12
BRIDGE_TUBE_HW = 2
BRIDGE_TUBE_RISE = 10
BRIDGE_WALK_WALL = 32
BRIDGE_Y1, BRIDGE_Y2 = -148, 148  # 296-unit (~19.6 ft) deck; after the two 38-unit
# parapets, interior walking width = 220 units = ft_to_units(14,6) ≈ 14.5 ft

BRIDGE_CENTER_PIER_SPAN = 1050
BRIDGE_OUTER_PIER_SPAN = 721


@dataclass
class BridgeSpec:
    x1: int
    x2: int
    y1: int
    y2: int
    arch_rise: int
    parapet_h: int
    walk_wall: int
