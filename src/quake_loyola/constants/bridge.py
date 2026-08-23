"""Bridge (Charles St pedestrian bridge) constants and the BridgeSpec dataclass."""

from dataclasses import dataclass

BRIDGE_ARCH_PIER_RISE = 82  # Deck rise at Piers 2 and 3.
BRIDGE_ARCH_RISE = 100  # Deck rise at the center of Charles St.
BRIDGE_BLK_H = 36
BRIDGE_BLK_HW = 32  # Parapet cap block half-width.
BRIDGE_BLK_OVH = 0
BRIDGE_BLK_INSET = 4  # Inset from each parapet face.
BRIDGE_BLK_PIER_CLEARANCE = 4
BRIDGE_BASE_LIGHT_HW = 32  # Wall-light half-width.
BRIDGE_BASE_LIGHT_H = 64  # Wall-light height.
BRIDGE_BASE_LIGHT_D = 2  # Wall-light protrusion.
BRIDGE_BASE_LIGHT_Z_LIFT = 12  # Lift above the deck.
BRIDGE_BASE_LIGHT_BRIGHTNESS = "150"  # Subtle uplight.
BRIDGE_DECK_EDGE_CEMENT_W = 16  # Visible cement margin along each deck edge.
BRIDGE_DECK_CROSS_STRIP_HW = BRIDGE_BLK_HW  # Matches the parapet block half-width.
BRIDGE_DECK_CROSS_STRIP_DROP = 1  # Embed 1 unit to avoid coplanar faces.
BRIDGE_DECK_CROSS_STRIP_H = 2  # Decal thickness.
BRIDGE_JOINT_METAL_HW = 6  # Half-width of the center expansion-joint metal strip.
BRIDGE_JOINT_GAP_HW = 1  # Half-width of the dark joint-plate gap seam.
BRIDGE_JOINT_CEMENT_W = 20  # Width of each cement band flanking the metal strip.
BRIDGE_DZ1, BRIDGE_DZ2 = (
    256,
    272,
)  # Deck underside/top before the arch profile is applied.
BRIDGE_EAST_SPAN_ANGLE = 12.0
BRIDGE_FASCIA_PX_W, BRIDGE_FASCIA_PX_H = (
    4,
    4,
)  # Fascia pixel size.
BRIDGE_FASCIA_TEXT = "LOYOLA UNIVERSITY MARYLAND"
BRIDGE_PAR_H = 40
BRIDGE_PILLAR_BASE_CAP_H = 5  # Plinth cap height.
BRIDGE_PILLAR_BASE_CAP_OVH = 5
BRIDGE_PILLAR_BASE_H = 0.5  # Keep above 0 to avoid degenerate geometry.
BRIDGE_PILLAR_BASE_RAMP_H = 25.5  # Ramped plinth rise above BRIDGE_PILLAR_BASE_H.
BRIDGE_PILLAR_CAP_H = 12  # Pillar cap height.
BRIDGE_PILLAR_CAP_IN_OVH = 4
BRIDGE_PILLAR_CAP_OUT_OVH = 20
BRIDGE_PILLAR_EXTRA = 64  # Extra pillar height above the deck.
BRIDGE_PIER_FILL_OFFSET = 16
BRIDGE_PILLAR_INNER_R = (144, 84)  # (half-width, crown rise)
BRIDGE_PILLAR_OUTER_R = (126, 72)  # (half-width, crown rise)
BRIDGE_PILLAR_OVERHANG = 16
BRIDGE_PILLAR_SEAM_HW = 3  # Mortar-seam strip half-width.
BRIDGE_PILLAR_SEAM_D = 1  # Mortar-seam strip protrusion.

# Decorative plates on each pier face.
BRIDGE_PIER_PLATE_SIZE = 34
BRIDGE_PIER_PLATE_GAP = 3
BRIDGE_PIER_PLATE_D = 1  # Slight protrusion from the pillar wall.

# Banner hung from a horizontal mast on Pier 2's south face, facing Charles St.
# {TF_Banner1 is 64x128, and the banner is built to match at 1:1 so the whole
# image lands on it exactly once with no wrap.
BRIDGE_BANNER_W = 64
BRIDGE_BANNER_H = 128
BRIDGE_BANNER_T = 2
BRIDGE_BANNER_GAP = 4  # Clearance between the pier face and the banner's near edge.
BRIDGE_BANNER_TOP_Z = 152  # Banner top / mast underside, above the pier floor.
BRIDGE_BANNER_MAST_T = 6
BRIDGE_BANNER_MAST_PROUD = 8  # Mast overhang past the banner's outer edge.
BRIDGE_BANNER_CORNER_INSET = 40  # Half the depth of Pier 2's south corner column.

# Cement lining on the interior faces of each opening.
BRIDGE_PIER_LINING_MARGIN = 6
BRIDGE_PIER_LINING_THICK = 3
BRIDGE_SQ_LINTEL_TILE_H = 34  # Tiled band above Pier 6's square opening.
BRIDGE_SQ_LINTEL_STONE_H = 32  # Stone course above the tile band.
BRIDGE_SQ_LINTEL_H = (
    BRIDGE_SQ_LINTEL_TILE_H + BRIDGE_SQ_LINTEL_STONE_H
)  # Total solid lintel height above Pier 6's square opening.
BRIDGE_PILLAR_PYR_H = 20
BRIDGE_SEG_SPAN_W = 32
BRIDGE_SQ_D = 1
BRIDGE_SQ_HH = 6
BRIDGE_SQ_HW = 8

# Support bent carrying the span in front of the Knott Hall entrance.
BRIDGE_SUPPORT_BEAM_H = 60  # Support beam height.
BRIDGE_SUPPORT_HW = 16
BRIDGE_SUPPORT_PIER_HALF_W = 25  # Support pier half-width.

# West-abutment plinth heights.
BRIDGE_ABUTMENT_RAMP_HIGH_H = 40  # West-face ramp height.
BRIDGE_ABUTMENT_RAMP_LOW_H = 24  # East-face ramp height.
BRIDGE_ABUTMENT_RAMP_CAP_H = 12  # Uniform ramp-cap thickness.

# East-face decorative recess on the west abutment.
BRIDGE_ABUTMENT_CEMENT_X1_OFFSET = 40  # Inner-edge inset from the east face.
BRIDGE_ABUTMENT_CEMENT_X2_OFFSET = 8  # Outer-edge inset from the east face.
BRIDGE_ABUTMENT_CEMENT_RIN = 48  # Visible cement arch half-width / crown rise.
BRIDGE_ABUTMENT_CEMENT_MAX_H = 72  # Height from ramp top to arch crown.
BRIDGE_TORCH_CUP_H = 4
BRIDGE_TORCH_CUP_HW = 5
BRIDGE_TORCH_POST_H = 16
BRIDGE_TORCH_POST_HW = 3
BRIDGE_TUBE_GAP = 12
BRIDGE_TUBE_HW = 2
BRIDGE_TUBE_RISE = 10
BRIDGE_WALK_WALL = 32
BRIDGE_Y1, BRIDGE_Y2 = -148, 148  # 296-unit deck width.

BRIDGE_CENTER_PIER_SPAN = 1300  # Span from Pier 2 to Pier 3.
BRIDGE_OUTER_PIER_SPAN = 721  # KNOTT_PIER_X - PIER3_X reference span.
BRIDGE_EAST_SPAN2_LEN = 921  # Span from Pier 3 to Pier 4.
BRIDGE_WEST_OUTER_PIER_SPAN = 921  # Span from Pier 1 to Pier 2.
BRIDGE_CENTER_SPAN_OFFSET = (
    0.0,
    320.0,
    96.0,
)  # (dx, dy, dz) requested for the center span; applied to the whole enabled
# bridge assembly (see bridge.py::_shift_center_span) so shared piers stay
# connected to non-center spans rather than tearing at the joint.
BRIDGE_CENTER_SPAN_PIER_EMBED = 96  # Extra pier embed when the center span is offset.
PIER6_ROTATION_DEG = -20  # Clockwise rotation in plan view.
PIER6_ROTATION_MARGIN = 150  # Extra section-filter margin for the rotated footprint.
BRIDGE_SOUTH_EXTENSION = 184  # How far south of BRIDGE.y1 the deck slab
# extends to close the gap at the Pier 5/Knott end.
PIER5_LINTEL_GAP = 24  # Extra gap over the lintel, applied only at Pier 5.


@dataclass
class BridgeSpec:
    x1: int
    x2: int
    y1: int
    y2: int
    arch_rise: int
    parapet_h: int
    walk_wall: int
