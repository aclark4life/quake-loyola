"""Bridge (Charles St pedestrian bridge) constants and the BridgeSpec dataclass."""

from dataclasses import dataclass

from ..config import get as _flag

BRIDGE_ARCH_PIER_RISE = 82  # deck rise at the centre-span piers (PIER2/PIER3):
# the two approach spans descend straight from here to 0 at the outer piers
# (ref/bridge08).
BRIDGE_ARCH_RISE = 100  # deck rise over Charles St (X=0), restored per user
# request after the flat-deck experiment (BRIDGE_ARCH_RISE == BRIDGE_ARCH_PIER_RISE)
# removed the visible parabolic curve/crest across the centre span. Back to a
# ~6.6 ft crest at X=0 above the BRIDGE_ARCH_PIER_RISE=82 level at the piers.
BRIDGE_ACCESS_WALK_CENTER_X = 2120
BRIDGE_ACCESS_WALK_HALF_W = 32
BRIDGE_ACCESS_WALK_NORTH_OFFSET = 80
BRIDGE_ACCESS_WALK_PIER_CLEARANCE = 96
BRIDGE_BLK_H = 36
BRIDGE_BLK_HW = 32  # half-width (X) of each parapet cap block — widened from 24
# so the block reads as a clearly rectangular slab (64 wide x 36 tall) rather
# than a near-square one, viewed face-on from the north/south.
BRIDGE_BLK_OVH = 0
BRIDGE_BLK_INSET = 4  # inset (Y) of each parapet cap block from both faces of the
# parapet wall it sits on, so the block reads as visibly thinner than the wall
# instead of flush/matching its full thickness.
BRIDGE_BLK_PIER_CLEARANCE = 4
BRIDGE_BASE_LIGHT_HW = 32  # half-width of the small wall light fixture mounted at
# the base of each parapet-block wall segment, on the inside (walkway-facing)
# face, right above the deck floor. 64x64 to match the light1_4 texture size.
BRIDGE_BASE_LIGHT_H = 64  # rise above the deck floor (matches texture size)
BRIDGE_BASE_LIGHT_D = 2  # protrusion into the walkway from the inner wall face
BRIDGE_BASE_LIGHT_Z_LIFT = 12  # raise the fixture up from the deck floor a bit
BRIDGE_BASE_LIGHT_BRIGHTNESS = "150"  # subtle low uplight, not a strong light source
BRIDGE_DECK_EAST_RECESS = 1
BRIDGE_DECK_EDGE_CEMENT_W = 16  # width of the cement margin kept along each side
# (north/south) of the deck's wood-textured (GABLE) underside — a small strip of
# the original cement/stone edge beam remains visible on both sides rather than
# the whole underside being wood.
BRIDGE_DECK_CROSS_STRIP_HW = BRIDGE_BLK_HW  # half-width (X) of each deck-bottom
# cross strip — matches the parapet block's own half-width so the strip (same
# GABLE wood texture as the underside, rotated 90°) reads as a transverse
# joist directly under that block.
BRIDGE_DECK_CROSS_STRIP_DROP = 1  # units the cross-strip decal hangs below the
# structural deck-bottom face — just enough to avoid z-fighting against it
# while still reading as flush from normal viewing distance. Built as a
# separate non-solid (func_illusionary) brush rather than by splitting the
# structural deck slab itself, since splitting the previously-unified flat
# spans there caused qbsp "WARNING 12: New portal was clipped away" and
# actual missing polygons in-game.
BRIDGE_DECK_CROSS_STRIP_H = 4  # thickness of the cross-strip decal brush
BRIDGE_DZ1, BRIDGE_DZ2 = (
    256,
    272,
)  # raised 32 units (was 224/240) so the flat deck at KNOTT_ORIG_CX (WALK_ZT1) was
# level with the KH 2nd-floor walkway landing (WALK_ZT2) at the time of this
# change; see KNOTT_GROUND_Z below, now a fixed hill-height anchor independent of
# this deck elevation — a later 64->221 re-measurement of KNOTT_GROUND_Z moved
# WALK_ZT2 up without a matching re-derivation here, so WALK_ZT1 and WALK_ZT2 are
# no longer equal (see the WALK_ZT1/derived.py comment for the current gap and
# why the walkway connector still works via a sloped ramp).
BRIDGE_EAST_SPAN_ANGLE = 12.0
BRIDGE_FASCIA_PX_W, BRIDGE_FASCIA_PX_H = (
    4,
    4,
)  # sized to fit just inside the middle span's two exterior parapet
# blocks (cx=-276/276, half-width BRIDGE_BLK_HW=32, so inner edges at
# -244/244 -> 488 units of clearance); at px_w=5 the lettering was
# 531 units wide, overlapping those blocks — px_w=4 comes to 402 units.
BRIDGE_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
BRIDGE_PAR_H = 40
BRIDGE_PILLAR_BASE_CAP_H = 5  # doubled from 2.5 for a more substantial cap slab.
BRIDGE_PILLAR_BASE_CAP_OVH = 5
BRIDGE_PILLAR_BASE_H = 0.5  # solid plinth height before the arch opening starts —
# trimmed a little further from 1 (was lowered from 2, 4, 8, 24, then 64
# before that) to bring the stone below the arch opening down about as far as
# it can go, matching the low, minimal plinth seen in ref/bridge04.png and
# ref/bridge08.png. Kept slightly above 0 (rather than fully flush with the
# ground) since an exact 0 produces a degenerate zero-height ramp edge that
# crashes qbsp's hull expansion (CheckFace: coordinate out of range) — this is
# about as low as it can go without hitting that crash.
BRIDGE_PILLAR_BASE_RAMP_H = 25.5  # ramped-side plinth height — rise over BASE_H
# shrunk further from 37 to 25 units per user request to reduce the stone below
# the arch opening a little more (was a ~27° slope after the 45°-was-too-steep
# feedback; keeps a similar but shorter ramp).
BRIDGE_PILLAR_CAP_H = 12  # restored to the original 12 — the below-deck stone
# reduction (BASE_H/BASE_RAMP_H/BASE_CAP_H above) stays, but the user asked to
# undo today's above-deck pillar-post/cap reduction entirely.
BRIDGE_PILLAR_CAP_IN_OVH = 4
BRIDGE_PILLAR_CAP_OUT_OVH = 20
BRIDGE_PILLAR_EXTRA = 64  # restored to the original 64 — see BRIDGE_PILLAR_CAP_H
# note above; the pillar tops read as too short at 26, so the above-deck
# reduction from today is undone while the below-deck plinth reduction and the
# arch-opening crown trim (BRIDGE_PILLAR_INNER_R/OUTER_R below) remain.
BRIDGE_ENABLED_PIER_BASE_LIGHTS = _flag(
    "BRIDGE_ENABLED_PIER_BASE_LIGHTS"
)  # temporarily disabled — pier-base lights (some sit buried in the east-span fill)
BRIDGE_PIER_FILL_OFFSET = 16
BRIDGE_PILLAR_INNER_R = (144, 84)  # rout trimmed from 160 to 144 — a small ~10%
# reduction in the arch opening's own clear height (crown rises less above the
# springline), matching the flatter/lower pointed-arch crown in ref/bridge04.png
# and ref/bridge08.png; rin (opening half-width) unchanged.
BRIDGE_PILLAR_OUTER_R = (126, 72)  # rout trimmed from 140 to 126, same ~10% cut as
# BRIDGE_PILLAR_INNER_R above; rin unchanged.
BRIDGE_PILLAR_OVERHANG = 16
BRIDGE_PILLAR_SEAM_HW = 3  # half-width (X) of the thin cement mortar-seam strip
# down the middle of each above-deck pillar post's walkway-facing (inside) face
BRIDGE_PILLAR_SEAM_D = 1  # protrusion of the seam strip out from that face,
# toward the walkway, so it's visible while walking past instead of flush
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
BRIDGE_SQ_LINTEL_TILE_H = 34  # height of the tiled band directly above Pier 6's
# square opening — a single row of BRIDGE_PIER_PLATE_SIZE (34) tiles, spanning
# the full pier width in one row rather than stacking multiple rows.
BRIDGE_SQ_LINTEL_STONE_H = 32  # plain stone course above the tiled band, below
# the pier ceiling/deck underside — reads as a stone coping capping the tiles
# rather than tiles running all the way up to the ceiling.
BRIDGE_SQ_LINTEL_H = (
    BRIDGE_SQ_LINTEL_TILE_H + BRIDGE_SQ_LINTEL_STONE_H
)  # total solid lintel height above Pier 6's square opening (was hardcoded to
# 16 — too thin for even a single 34-unit tile row to fit; tile_grid_origins()
# returns zero tiles whenever the target area is shorter than one tile).
BRIDGE_PILLAR_PYR_H = 20
BRIDGE_SEG_SPAN_W = 32
BRIDGE_SQ_D = 1
BRIDGE_SQ_HH = 6
BRIDGE_SQ_HW = 8
BRIDGE_SUPPORT_BEAM_H = 20
BRIDGE_SUPPORT_HALF_W = 16
BRIDGE_SUPPORT_PIER_HALF_W = 20
BRIDGE_TELEPORT_ARCH_X1_OFFSET = 2  # inset from the pier's west face — small, this
# recess is a hidden/secret teleport, not a player-visible feature.
BRIDGE_TELEPORT_ARCH_X2_OFFSET = 18  # 16-unit slab thickness
BRIDGE_TELEPORT_ARCH_CLEARANCE = 8  # gap kept between the teleport arch's crown and
# the underside of the deck above.
BRIDGE_TELEPORT_DEST_Z = 40

# West-abutment pier (min(BRIDGE_ARCH_X)) plinth: a single stone base + cement cap
# ramp spans the ENTIRE pier face flush (x1 to x2, no inset) — high at the west
# face (the "starting point" of the slanted ramp) descending to a lower, but
# still-visible-thickness, cap at the east face — matching the ramped-plinth
# style used on every other pier, just taller since this pier hosts two full
# recessed openings (west teleport, east cement) instead of a walkable archway.
# Both openings' floors sit on TOP of this shared ramp/cap, so raising the ramp
# automatically shortens each opening's own visible height.
BRIDGE_ABUTMENT_RAMP_HIGH_H = 40  # ramp height at the west face (x1) — a bit
# taller than BRIDGE_ABUTMENT_RAMP_LOW_H so the cap still visibly slopes down
# west->east (matching every other pier's ramped-plinth look) while staying
# low enough for a player to reach the top with a normal jump (was 64, too
# tall to jump up onto and mismatched with the east face; dropping to 24
# flattened the slope entirely — see BRIDGE_ABUTMENT_RAMP_LOW_H's history).
# The (hidden) west teleport opening's floor tracks this and shrinks back
# down a bit to match.
BRIDGE_ABUTMENT_RAMP_LOW_H = 24  # ramp height at the east face (x2)
BRIDGE_ABUTMENT_RAMP_CAP_H = 12  # cap thickness — uniform along the full ramp length
# (not tapering to 0) so it stays clearly visible everywhere, including at the
# east/low end.

# East-face decorative "cement opening" on the west-abutment pier: a solid,
# non-teleporting arch-shaped recess facing into the walkable west approach
# span — this is the player-visible feature (vs. the hidden west-face
# teleport arch above).
BRIDGE_ABUTMENT_CEMENT_X1_OFFSET = 40  # inset of the recess's inner (west) edge from
# the pier's east face (x2) — together with X2_OFFSET this sets a 32-unit-wide opening.
BRIDGE_ABUTMENT_CEMENT_X2_OFFSET = 8  # inset of the recess's outer (east) edge from
# the pier's east face — kept off x2 (not flush) so a stone rim shows around it.
BRIDGE_ABUTMENT_CEMENT_RIN = 48  # half-width/crown-rise of the visible cement arch —
# smaller than BRIDGE_PILLAR_OUTER_R's rin (72) so the "opening" reads as a modest
# doorway rather than spanning nearly the full pier height.
BRIDGE_ABUTMENT_CEMENT_MAX_H = 72  # total floor(above ramp/cap)-to-crown height of the
# cement arch.
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

BRIDGE_CENTER_PIER_SPAN = 1300  # PIER3 (Knott side, real GPS anchor — see
# docs/elevation_samples.csv "pier3_center_span_e") stays put when THIS span
# changes; this span only pulls PIER2 (west side, on flat/low terrain) west.
# Was 1050, then briefly 850 (too tight/"squished" per playtest feedback —
# pulled the west pier further back out to 950), then bumped +50 to 1000, then
# +100 to 1100, then +200 to 1300 (kept wanting it wider) — paired with a
# matching shift to ROAD_X1 (constants/streets.py, widening Charles St to the
# west by the same delta each time) so PIER2's setback from the curb stays
# ~169 units even as the centre span's own length grows. Everything positioned
# relative to the west pier group (DORM_PIER_X and its dependents) follows
# PIER2/PIER1 automatically.
# Playwright/Google-Maps + ref/bridge08 street-view comparison showed real piers
# sitting closer to the curb than the original 1050, but 850 overcorrected. Terrain
# under the new footprint (checked west_campus_terrain.terrain_z across PIER2_X +/-
# BRIDGE_PILLAR_HW) stays well above the pier's base Z (0), so no floating-pier
# risk from this move.
BRIDGE_OUTER_PIER_SPAN = 721  # KNOTT_PIER_X - PIER3_X: fixes PIER3 at its real
# GPS-surveyed position (docs/elevation_samples.csv "pier3_center_span_e",
# X=525) relative to the real Knott Hall west pier. Deliberately NOT the
# east span 2 length — see BRIDGE_EAST_SPAN2_LEN below, which governs PIER4
# independently so lengthening span 2 can't move PIER3/the centre span.
BRIDGE_EAST_SPAN2_LEN = 921  # East outer span (Pier3→Pier4) length. PIER4 is
# derived as PIER3_X + this value rather than pinned to KNOTT_PIER_X (the real
# KH west pier) — deliberately unpinned so this span can be lengthened without
# moving PIER3 (the real GPS anchor)/the centre span. Was 721 (implicitly,
# when PIER4 == KNOTT_PIER_X and PIER3 sat 721 west of it); bumped +200 to 921
# to match BRIDGE_WEST_OUTER_PIER_SPAN so both outer spans read as the same
# length, per playtest feedback. The resulting ~200-unit gap between PIER4 and
# the real KH west pier (KNOTT_PIER_X) is absorbed by the existing flat
# PIER4→PIER5 span (1208 units before this change, still 1008 after — plenty
# of clearance). Lamp posts / KH driveway / Ennis geometry reference
# KNOTT_PIER_X directly (not PIER4/BRIDGE_X2), so they're unaffected.
BRIDGE_WEST_OUTER_PIER_SPAN = 921  # west outer span (Pier1-Pier2) — only pulls
# PIER1 (west abutment, on flat/low terrain) further west; PIER2 stays put (it's
# governed by BRIDGE_CENTER_PIER_SPAN + BRIDGE_OUTER_PIER_SPAN off KNOTT_PIER_X).
# Was 721 (same as the east span, before the two were split apart), bumped +100
# to 821 per playtest feedback that the first (west) span felt short, then +100
# again to 921 (same feedback) — everything west of the west pier group
# (DORM_PIER_X and its dependents: fence, brick wall, sidewalk, terrain) follows
# PIER1_X automatically since DORM_PIER_X = min(BRIDGE_ARCH_X).
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
