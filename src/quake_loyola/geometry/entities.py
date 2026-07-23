"""Helpers for point entities and brush entities."""

from ..mapdata import Brush, Entity


def ent(cls, **kw):
    return Entity(cls, dict(kw))


def brush_ent(cls, brushes, **kw):
    if isinstance(brushes, Brush):
        brushes = [brushes]
    return Entity(cls, dict(kw), list(brushes))


def torch_flame(x, y, z, light="300", flame_dz=4, flame_cls="light_flame_large_yellow"):
    return [
        ent("light", origin=f"{x} {y} {z}", light=light, _light_group="torch"),
        ent(flame_cls, origin=f"{x} {y} {z + flame_dz}", _light_group="torch"),
    ]


def torch_flame_only(x, y, z, flame_cls="light_flame_large_yellow"):
    return ent(flame_cls, origin=f"{x} {y} {z}", _light_group="torch")
