"""Shared helpers used by several ``entities/*`` submodules."""

from ..constants import (
    BRIDGE_ARCH_X,
    BRIDGE_CENTER_SPAN_OFFSET,
    DORM_SOUTH1_CY,  # noqa: F401 - re-exported for entities/{monsters,pickups,spawns}.py
    DORM_SOUTH2_CY,  # noqa: F401 - re-exported for entities/{pickups,spawns}.py
    ROAD_Z,  # noqa: F401 - re-exported for entities/{lights,monsters,pickups,platform,spawns}.py
)

CS_X1, CS_X2 = BRIDGE_ARCH_X[1], BRIDGE_ARCH_X[2]
_CS_DY, _CS_DZ = BRIDGE_CENTER_SPAN_OFFSET[1], BRIDGE_CENTER_SPAN_OFFSET[2]


def _cs_offset(x, y, z):
    """Apply the bridge center-span Y/Z offset to points within the true
    center span (Pier 2 to Pier 3), matching BRIDGE_CENTER_SPAN_OFFSET's own
    "applied only to the center span" contract. Points in the outer spans
    (Pier 1-2, Pier 3-6) are left untouched."""
    if CS_X1 <= x <= CS_X2:
        return y + _CS_DY, z + _CS_DZ
    return y, z
