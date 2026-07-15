"""Bridge (Charles St pedestrian bridge) constants and the BridgeSpec dataclass."""

from dataclasses import dataclass

BRIDGE_ARCH_PIER_RISE = 82  # deck rise at the centre-span piers (PIER2/PIER3):
# the two approach spans descend straight from here to 0 at the outer piers
# (ref/bridge08).
BRIDGE_ARCH_RISE = BRIDGE_ARCH_PIER_RISE  # deck rise over Charles St (X=0). Real
# street-view photos (ref/bridge01/04/08) show a flat, level deck across the road —
# no parabolic camber — so this now equals BRIDGE_ARCH_PIER_RISE, making
# arch_z_at()'s centre-span term a constant (flat) rather than a parabola. Was 100
# (a visible ~6.6 ft crest at X=0); confirmed via Playwright-captured Google Maps
# imagery + street-view refs that the real deck has no such rise — only the
# sub-deck pier openings are pointed/Gothic-arched, not the deck surface itself.
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
BRIDGE_PILLAR_BASE_H = 8  # solid plinth height before the arch opening starts — lowered
# from 64 (was 24 before that) to open up the arch opening's clear height, matching
# the tall, slender pointed-arch proportions seen in ref/bridge04.png and
# ref/bridge08.png. Kept slightly above 0 (rather than fully flush with the ground)
# since an exact 0 produces a degenerate zero-height ramp edge that crashes qbsp's
# hull expansion (CheckFace: coordinate out of range).
BRIDGE_PILLAR_BASE_RAMP_H = 24  # ramped-side plinth height — kept the same 16-unit
# rise over BASE_H as before, just shifted down along with it.
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

BRIDGE_CENTER_PIER_SPAN = 950  # PIER3 (Knott side) is pinned via KNOTT_PIER_X -
# BRIDGE_OUTER_PIER_SPAN and stays put (it anchors the hill profile's real-elevation
# "Pier 3" sample and the Ennis Drive entrance pillars/gate, so moving it has a much
# wider blast radius); this span only pulls PIER2 (west side, on flat/low terrain)
# east, from -525 to -425, tightening its setback from the Charles St curb (ROAD_X2
# =256) from ~269 to ~169 units. Was 1050, then briefly 850 (too tight/"squished"
# per playtest feedback — pulled the west pier further back out to 950).
# Playwright/Google-Maps + ref/bridge08 street-view comparison showed real piers
# sitting closer to the curb than the original 1050, but 850 overcorrected. Terrain
# under the new footprint (checked west_campus_terrain.terrain_z across PIER2_X +/-
# BRIDGE_PILLAR_HW) stays well above the pier's base Z (0), so no floating-pier
# risk from this move.
BRIDGE_OUTER_PIER_SPAN = 721
BRIDGE_CENTER_SPAN_OFFSET = (0.0, 320.0, 96.0)  # (dx, dy, dz) applied to just the
# centre span (PIER2..PIER3) in bridge.build(), independent of the other
# sections — for experimenting with its position (e.g. shifting it north/up)
# without moving the approach spans, piers, or terrain. (0, 0, 0) = no shift.
# See bridge.build_center_span() to build/inspect the span on its own.
BRIDGE_CENTER_SPAN_PIER_EMBED = 96  # extra depth subtracted from PIER2/PIER3's
# base Z when BRIDGE_CENTER_SPAN_OFFSET is non-zero, so the piers' plinths
# still reach well into the ground after the span is shifted away from the
# real-elevation terrain their original BRIDGE_PIER_GROUND_Z values were
# sampled against.


@dataclass
class BridgeSpec:
    x1: int
    x2: int
    y1: int
    y2: int
    arch_rise: int
    parapet_h: int
    walk_wall: int
