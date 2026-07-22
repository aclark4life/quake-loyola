"""Real-elevation / provisional ground-fill modules, one per map quadrant.

Each submodule exposes the same ``build() -> (brushes, entities)`` contract
as the top-level area modules (see ``mapgen.py``) and is kept separate so
each hill/mound (Knott Hall's vs. Maryland Hall's vs. the west-campus dorms'
vs. the NE quadrant's) can be enabled/disabled independently via its own
``*_ENABLED_TERRAIN`` flag.

Submodules
    ``knott_hall`` — hill terrain surrounding Knott Hall.
    ``maryland`` — ground mound under/around the Maryland Hall stub.
    ``ne`` — real-elevation ground fill for the NE quadrant (north of Ennis
        Road, east of Charles St).
    ``west_campus`` — real-elevation ground fill for the west campus dorm
        buildings and the bridge's west approach.
"""

from . import knott_hall, maryland, ne, west_campus

__all__ = ["knott_hall", "maryland", "ne", "west_campus"]
