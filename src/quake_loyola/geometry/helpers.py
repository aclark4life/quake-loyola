"""Small shared geometry helpers."""

import math

from ..constants import BRIDGE_EAST_PIVOT_X, BRIDGE_EAST_SPAN_ANGLE


def east_y_shift(x: float) -> float:
    """Return the Y offset induced by the east bridge span's rotation at ``x``.

    Zero at and west of the span's pivot; grows linearly east of it per the
    span's fixed rotation angle.
    """
    pivot = BRIDGE_EAST_PIVOT_X
    if x <= pivot:
        return 0.0
    return -(x - pivot) * math.tan(math.radians(BRIDGE_EAST_SPAN_ANGLE))
