"""Charles Street and surrounding road geometry.

Split into per-concern submodules: :mod:`shell` builds the base street
tunnel and manhole cutout, :mod:`ennis` builds the Ennis Ave entrance
features (called from :mod:`details`), and :mod:`details` builds crosswalks,
curbs, lamps, trees, driveways, and the rest of the street detailing.
"""

from .details import _build_street_details
from .shell import _build_street_world_shell, _build_world_seal


def build():
    """Build Charles Street and surrounding road geometry.

    Returns:
        tuple[list, list]: ``(brushes, entities)`` for the street network,
        including the roadway, sidewalks, tunnel, and related detail brushes.
    """
    BRUSHES, ENTITIES = _build_street_world_shell()
    BRUSHES, ENTITIES = _build_street_details(BRUSHES, ENTITIES)
    # The world-seal brushes are global leak-prevention geometry rather than
    # cosmetic detailing, so they are built separately from the details above.
    BRUSHES.extend(_build_world_seal())
    return BRUSHES, ENTITIES
