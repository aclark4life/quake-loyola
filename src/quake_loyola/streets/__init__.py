"""Charles Street and surrounding road geometry.

Split into per-concern submodules: :mod:`shell` builds the base street
tunnel and manhole cutout, :mod:`ennis` builds the Ennis Ave entrance
features (called from :mod:`details`), and :mod:`details` builds crosswalks,
curbs, lamps, trees, driveways, and the rest of ``STREETS_ENABLED_DETAILS``.
"""

from ..constants.flags import STREETS_ENABLED_DETAILS
from .details import _build_street_details
from .shell import _build_street_world_shell


def build():
    """Build Charles Street and surrounding road geometry.

    Returns:
        tuple[list, list]: ``(brushes, entities)`` for the street network,
        including the roadway, sidewalks, tunnel, and related detail brushes.
    """
    BRUSHES, ENTITIES = _build_street_world_shell()
    if not STREETS_ENABLED_DETAILS:
        return BRUSHES, ENTITIES
    return _build_street_details(BRUSHES, ENTITIES)
