"""Placeholder Maryland Hall massing and terrain constants."""

from .derived import KNOTT_X1
from .knott import KNOTT_Y2

# OSM-derived full-scale footprint compressed to the east-campus stub scale.
_MARYLAND_COMPRESSION = 2.5  # East-campus compression factor.
_MARYLAND_X1_FULL_SCALE = 6385  # OSM-derived full-scale X1.
_MARYLAND_X2_FULL_SCALE = 8979
_MARYLAND_Y1_FULL_SCALE = 412
_MARYLAND_Y2_FULL_SCALE = 1622
MARYLAND_X1 = KNOTT_X1 + round(
    (_MARYLAND_X1_FULL_SCALE - KNOTT_X1) / _MARYLAND_COMPRESSION
)
MARYLAND_X2 = KNOTT_X1 + round(
    (_MARYLAND_X2_FULL_SCALE - KNOTT_X1) / _MARYLAND_COMPRESSION
)
MARYLAND_Y1 = KNOTT_Y2 + round(
    (_MARYLAND_Y1_FULL_SCALE - KNOTT_Y2) / _MARYLAND_COMPRESSION
)
MARYLAND_Y2 = KNOTT_Y2 + round(
    (_MARYLAND_Y2_FULL_SCALE - KNOTT_Y2) / _MARYLAND_COMPRESSION
)
MARYLAND_FLOORS = 3  # Maryland Hall stories.
MARYLAND_FLOOR_H = 128  # Matches dorm floor height.
MARYLAND_H = MARYLAND_FLOORS * MARYLAND_FLOOR_H
# Approximate terrain height at the Maryland Hall stub.
MARYLAND_GROUND_Z = 273

# terrain/maryland.py apron and slope dimensions.
MARYLAND_TERRAIN_MARGIN = 192
MARYLAND_TERRAIN_RAMP_W = 768
