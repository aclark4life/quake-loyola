"""Small shared geometry helpers."""

import math

from ..constants import BRIDGE_EAST_PIVOT_X, BRIDGE_EAST_SPAN_ANGLE


def east_y_shift(x):
    pivot = BRIDGE_EAST_PIVOT_X
    if x <= pivot:
        return 0.0
    return -(x - pivot) * math.tan(math.radians(BRIDGE_EAST_SPAN_ANGLE))
