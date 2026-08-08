"""Helpers for point entities and brush entities."""

from ..mapdata import Brush, Entity


def ent(cls: str, **kw) -> Entity:
    """Build a point entity of classname ``cls`` from keyword key/value pairs."""
    return Entity(cls, dict(kw))


def brush_ent(cls: str, brushes: Brush | list[Brush], **kw) -> Entity:
    """Build a brush entity of classname ``cls`` wrapping one or more brushes."""
    if isinstance(brushes, Brush):
        brushes = [brushes]
    return Entity(cls, dict(kw), list(brushes))


def torch_flame(
    x: float,
    y: float,
    z: float,
    light: str = "300",
    flame_dz: float = 4,
    flame_cls: str = "light_flame_large_yellow",
) -> list[Entity]:
    """Build a light + torch-flame entity pair at ``(x, y, z)``."""
    return [
        ent("light", origin=f"{x} {y} {z}", light=light),
        ent(flame_cls, origin=f"{x} {y} {z + flame_dz}"),
    ]


def torch_flame_only(
    x: float, y: float, z: float, flame_cls: str = "light_flame_large_yellow"
) -> Entity:
    """Build a standalone torch-flame entity (no accompanying light) at ``(x, y, z)``."""
    return ent(flame_cls, origin=f"{x} {y} {z}")


def teleport_pad(
    trigger_brushes: Brush | list[Brush],
    target: str,
    glow_brushes: Brush | list[Brush] | None = None,
) -> list[Entity]:
    """Build a teleport trigger plus its visible glow volume.

    Every teleport in the map pairs a ``trigger_teleport`` with a
    ``func_illusionary`` so the player can see where the trigger is. The
    two usually share one brush set, but arch-mounted teleports use a
    plain box for the trigger and an arch-shaped fill for the glow.

    Args:
        trigger_brushes: Brushes forming the touchable trigger volume.
        target: ``targetname`` of the ``info_teleport_destination``.
        glow_brushes: Brushes for the visible glow. Defaults to
            ``trigger_brushes``.

    Returns:
        list[Entity]: The ``trigger_teleport`` followed by its
        ``func_illusionary``, in that order.
    """
    return [
        brush_ent("trigger_teleport", trigger_brushes, target=target),
        brush_ent(
            "func_illusionary",
            trigger_brushes if glow_brushes is None else glow_brushes,
        ),
    ]


def path_loop(prefix: str, points) -> list[Entity]:
    """Build a closed ring of ``path_corner`` entities for a ``func_train``.

    Corners are named ``f"{prefix}1"`` .. ``f"{prefix}N"`` and each targets
    the next, with the last wrapping back to the first. Chaining them here
    rather than by hand keeps the ring from silently breaking when a corner
    is inserted, removed, or reordered.

    Args:
        prefix: Targetname prefix; corners are numbered from 1.
        points: Iterable of ``(x, y, z)`` corner origins, in travel order.

    Returns:
        list[Entity]: One ``path_corner`` per point, in the given order.
    """
    points = list(points)
    if not points:
        raise ValueError("path_loop(): needs at least one path corner")
    names = [f"{prefix}{i + 1}" for i in range(len(points))]
    return [
        ent(
            "path_corner",
            targetname=name,
            target=names[(i + 1) % len(names)],
            origin=f"{x} {y} {z}",
        )
        for i, (name, (x, y, z)) in enumerate(zip(names, points, strict=True))
    ]
