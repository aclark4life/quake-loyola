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
        ent("light", origin=f"{x} {y} {z}", light=light, _light_group="torch"),
        ent(flame_cls, origin=f"{x} {y} {z + flame_dz}", _light_group="torch"),
    ]


def torch_flame_only(
    x: float, y: float, z: float, flame_cls: str = "light_flame_large_yellow"
) -> Entity:
    """Build a standalone torch-flame entity (no accompanying light) at ``(x, y, z)``."""
    return ent(flame_cls, origin=f"{x} {y} {z}", _light_group="torch")
