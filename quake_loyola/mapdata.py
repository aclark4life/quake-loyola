"""Core Quake .map data model: Face, Brush, Entity, and a MapBuilder accumulator.

Geometry is represented as data (points, textures, key/values) and serialized to
Quake MAP text via to_map().  Shape constructors live in geometry.py; content
modules build these objects; generate_map.py assembles them through MapBuilder.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .utils import format_point

# A 3-tuple of numeric coordinates (x, y, z).
Point = tuple[float, float, float]


@dataclass
class Face:
    """A single brush face: three coplanar points, a texture, and alignment params."""

    p1: Point
    p2: Point
    p3: Point
    tex: str
    params: str = "0 0 0 1 1"

    def to_map(self) -> str:
        return f"{format_point(*self.p1)} {format_point(*self.p2)} {format_point(*self.p3)} {self.tex} {self.params}"

    def translated(self, dx: float, dy: float, dz: float) -> Face:
        """Return a copy shifted by (dx, dy, dz)."""

        def t(p: Point) -> Point:
            return (p[0] + dx, p[1] + dy, p[2] + dz)

        return Face(t(self.p1), t(self.p2), t(self.p3), self.tex, self.params)


@dataclass
class Brush:
    """A convex brush — an ordered list of Faces."""

    faces: list[Face]

    def to_map(self) -> str:
        return "{\n" + "\n".join(f.to_map() for f in self.faces) + "\n}"

    def __str__(self) -> str:
        return self.to_map()

    def translated(self, dx: float, dy: float, dz: float) -> Brush:
        """Return a copy of this brush shifted by (dx, dy, dz)."""
        return Brush([f.translated(dx, dy, dz) for f in self.faces])


@dataclass
class Entity:
    """A Quake entity: classname, ordered key/value fields, and optional brushes.

    A point entity has no brushes; a brush entity (and worldspawn) carries them.
    """

    classname: str
    fields: dict[str, str] = field(default_factory=dict)
    brushes: list[Brush] = field(default_factory=list)

    def to_map(self) -> str:
        lines = ["{", f'"classname" "{self.classname}"']
        for k, v in self.fields.items():
            lines.append(f'"{k}" "{v}"')
        for b in self.brushes:
            lines.append(b.to_map())
        lines.append("}")
        return "\n".join(lines)


class MapBuilder:
    """Accumulates world brushes and entities, then serializes a full .map document."""

    def __init__(self) -> None:
        self.brushes: list[Brush] = []  # worldspawn geometry
        self.entities: list[Entity] = []

    def add_brush(self, brush: Brush) -> None:
        self.brushes.append(brush)

    def add_brushes(self, brushes: list[Brush]) -> None:
        self.brushes.extend(brushes)

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def add_entities(self, entities: list[Entity]) -> None:
        self.entities.extend(entities)

    def to_map(self, worldspawn_fields: dict[str, str]) -> str:
        """Serialize worldspawn (with the given fields + world brushes) plus all entities."""
        world = Entity("worldspawn", dict(worldspawn_fields), self.brushes)
        blocks = [world.to_map()] + [e.to_map() for e in self.entities]
        return "\n\n".join(blocks) + "\n"
