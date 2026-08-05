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


def extend_terrain_row_overlap(y1, y2, z_near1, z_far1, z_near2, z_far2, overlap):
    """Extend a sampled terrain grid row's far (``y2``) edge by ``overlap``
    units past its surveyed position, interpolating the far Z values along
    the row's own (unextended) slope rather than reusing the unextended
    Z values.

    Adjacent terrain rows are built independently and only meet exactly at
    their surveyed edges; nudging the far edge slightly past that boundary
    (``overlap`` may be positive or negative depending on which way "far"
    runs for the grid in question) gives neighboring rows a sliver of
    overlap that hides seams, while staying on the same interpolated plane
    a query at the extended point would otherwise return — used by both
    ``terrain/ne.py`` and ``terrain/west_campus.py``.

    Returns:
        tuple: ``(y2_extended, z_far1_extended, z_far2_extended)``.
    """
    if y1 == y2:
        raise ValueError(
            "extend_terrain_row_overlap: y1 and y2 must differ (got "
            f"y1=y2={y1!r}) — a zero-width row has no slope to extend along"
        )
    y2_ext = y2 + overlap
    t = (y2_ext - y1) / (y2 - y1)
    z_far1_ext = z_near1 + (z_far1 - z_near1) * t
    z_far2_ext = z_near2 + (z_far2 - z_near2) * t
    return y2_ext, z_far1_ext, z_far2_ext
