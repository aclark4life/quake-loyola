"""Charles Street and surrounding road geometry.

Split into per-concern submodules: :mod:`shell` builds the base street
tunnel and manhole cutout, :mod:`ennis` builds the Ennis Ave entrance
features (called from :mod:`details`), and :mod:`details` builds crosswalks,
curbs, lamps, trees, driveways, and the rest of ``STREETS_ENABLED_DETAILS``.
"""

from ..constants.flags import STREETS_ENABLED_DETAILS
from .details import _build_street_details
from .shell import _build_street_world_shell, _build_world_seal


def build():
    """Build Charles Street and surrounding road geometry.

    Returns:
        tuple[list, list]: ``(brushes, entities)`` for the street network,
        including the roadway, sidewalks, tunnel, and related detail brushes.
    """
    BRUSHES, ENTITIES = _build_street_world_shell()
    if STREETS_ENABLED_DETAILS:
        BRUSHES, ENTITIES = _build_street_details(BRUSHES, ENTITIES)
    # The world-seal brushes are global leak-prevention geometry, not a
    # cosmetic detail, so they must always be built regardless of the
    # STREETS_ENABLED_DETAILS flag.
    BRUSHES.extend(_build_world_seal())
    return BRUSHES, ENTITIES
