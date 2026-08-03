"""Shared helpers used by several ``entities/*`` submodules."""

from ..constants import (
    BRIDGE_ARCH_X,
    BRIDGE_CENTER_SPAN_OFFSET,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    FLOOR_Z2,
)

ROAD_Z = FLOOR_Z2 + 8
_BRIDGE_X_MIN, _BRIDGE_X_MAX = min(BRIDGE_ARCH_X), max(BRIDGE_ARCH_X)
CS_X1, CS_X2 = BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]
_CS_DY, _CS_DZ = BRIDGE_CENTER_SPAN_OFFSET[1], BRIDGE_CENTER_SPAN_OFFSET[2]
DORM_SOUTH1_CY = (DORM_SOUTH1_Y1 + DORM_SOUTH1_Y2) // 2
DORM_SOUTH2_CY = (DORM_SOUTH2_Y1 + DORM_SOUTH2_Y2) // 2


def _cs_offset(x, y, z):
    """Apply the bridge center-span Y/Z offset to points within the arch span."""
    if _BRIDGE_X_MIN <= x <= _BRIDGE_X_MAX:
        return y + _CS_DY, z + _CS_DZ
    return y, z
