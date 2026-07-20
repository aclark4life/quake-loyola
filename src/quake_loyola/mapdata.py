"""Core Quake .map data model: Face, Brush, Entity, and a MapBuilder accumulator.

Geometry is represented as data (points, textures, key/values) and serialized to
Quake MAP text via to_map().  Shape constructors live in geometry.py; content
modules build these objects; generate_map.py assembles them through MapBuilder.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .utils import format_point, format_value

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

    def rotated_z(self, angle_deg: float, cx: float = 0.0, cy: float = 0.0) -> Face:
        """Return a copy rotated by angle_deg (degrees, positive = counter-
        clockwise looking down the -Z axis, i.e. standard math convention in
        the XY plane) about the vertical axis through (cx, cy). Z is
        unaffected.

        Rotated coordinates are snapped to the nearest 0.1 unit. Off-grid
        float coordinates from an arbitrary rotation angle are a known qbsp
        fragility (WARNING 12 "New portal was clipped away in
        CutNodePortals_r" plus outright missing/invisible polygons in-game),
        and snapping noticeably reduces it. A full integer snap was tried
        first but collapsed some of Pier 6's thin decorative tile-plate
        faces (sub-1-unit thick) into degenerate zero-area planes ("Brush
        plane with no normal"); 0.1-unit precision keeps those thin faces
        intact while still rounding away most of the floating-point noise
        that trips up qbsp's portal splitting."""
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        def r(p: Point) -> Point:
            x, y = p[0] - cx, p[1] - cy
            return (
                round(cx + x * cos_a - y * sin_a, 1),
                round(cy + x * sin_a + y * cos_a, 1),
                p[2],
            )

        return Face(r(self.p1), r(self.p2), r(self.p3), self.tex, self.params)

    def is_inside(self, p: Point, eps: float = 1e-4) -> bool:
        """Return True if point p is on the solid (positive) side of this face's plane."""
        v1 = (self.p2[0] - self.p1[0], self.p2[1] - self.p1[1], self.p2[2] - self.p1[2])
        v2 = (self.p3[0] - self.p1[0], self.p3[1] - self.p1[1], self.p3[2] - self.p1[2])
        normal = (
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0],
        )
        dot = (
            normal[0] * (p[0] - self.p1[0])
            + normal[1] * (p[1] - self.p1[1])
            + normal[2] * (p[2] - self.p1[2])
        )
        return dot >= -eps


@dataclass
class Brush:
    """A convex brush — an ordered list of Faces."""

    faces: list[Face]

    def to_map(self) -> str:
        return "{\n" + "\n".join(f.to_map() for f in self.faces) + "\n}"

    def contains(self, p: Point, eps: float = 1e-4) -> bool:
        """Return True if point p is inside the convex volume defined by all faces."""
        if not self.faces:
            raise ValueError("Brush.contains() called on a brush with no faces")
        return all(f.is_inside(p, eps) for f in self.faces)

    def get_bbox(self) -> tuple[Point, Point]:
        """Return an approximate (min_point, max_point) bounding box of this
        brush, derived from each Face's three plane-defining points.

        This is exact for axis-aligned box() brushes (every corner appears
        among the collected points), but for non-box brushes — e.g. prisms
        or arches whose faces have more vertices than the 3 used to define
        the plane — it can under-report the true extent, since vertices not
        chosen as plane-definition points are not considered. Treat this as
        a fast, conservative "face-point bounds", not a precise solid bbox.
        """
        if not self.faces:
            raise ValueError("Brush.get_bbox() called on a brush with no faces")
        pts = []
        for f in self.faces:
            pts.extend([f.p1, f.p2, f.p3])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def __str__(self) -> str:
        return self.to_map()

    def translated(self, dx: float, dy: float, dz: float) -> Brush:
        """Return a copy of this brush shifted by (dx, dy, dz)."""
        return Brush([f.translated(dx, dy, dz) for f in self.faces])

    def rotated_z(self, angle_deg: float, cx: float = 0.0, cy: float = 0.0) -> Brush:
        """Return a copy of this brush rotated angle_deg degrees about the
        vertical axis through (cx, cy) — see Face.rotated_z."""
        return Brush([f.rotated_z(angle_deg, cx, cy) for f in self.faces])


@dataclass
class Entity:
    """A Quake entity: classname, ordered key/value fields, and optional brushes.

    A point entity has no brushes; a brush entity (and worldspawn) carries them.
    """

    classname: str
    fields: dict[str, str] = field(default_factory=dict)
    brushes: list[Brush] = field(default_factory=list)

    def to_map(self) -> str:
        for k, v in [("classname", self.classname), *self.fields.items()]:
            if '"' in str(k) or '"' in str(v) or "\n" in str(k) or "\n" in str(v):
                raise ValueError(
                    f"Entity field {k!r}={v!r} contains a quote or newline, "
                    "which would corrupt MAP text serialization"
                )
        lines = ["{", f'"classname" "{self.classname}"']
        for k, v in self.fields.items():
            lines.append(f'"{k}" "{v}"')
        for b in self.brushes:
            lines.append(b.to_map())
        lines.append("}")
        return "\n".join(lines)

    def translated(self, dx: float, dy: float, dz: float) -> Entity:
        """Return a copy shifted by (dx, dy, dz) — brushes, and the "origin"
        field (if present) for point entities such as lights or teleport
        destinations."""
        fields = dict(self.fields)
        origin = fields.get("origin")
        if origin is not None:
            parts = origin.split()
            if len(parts) != 3:
                raise ValueError(
                    f'Entity "origin" field must have exactly 3 components, got {origin!r}'
                )
            try:
                ox, oy, oz = (float(v) for v in parts)
            except ValueError as exc:
                raise ValueError(
                    f'Entity "origin" field must contain numeric values, got {origin!r}'
                ) from exc
            fields["origin"] = (
                f"{format_value(ox + dx)} {format_value(oy + dy)} {format_value(oz + dz)}"
            )
        brushes = [b.translated(dx, dy, dz) for b in self.brushes]
        return Entity(self.classname, fields, brushes)

    def rotated_z(self, angle_deg: float, cx: float = 0.0, cy: float = 0.0) -> Entity:
        """Return a copy rotated angle_deg degrees about the vertical axis
        through (cx, cy) — brushes, and the "origin"/"angle" fields (if
        present) for point entities such as lights or torch flames. Z is
        unaffected. The "angle" field (Quake yaw, degrees, counter-clockwise
        from east looking down) is adjusted by the same amount so directional
        point entities keep facing the same relative way."""
        fields = dict(self.fields)
        origin = fields.get("origin")
        if origin is not None:
            parts = origin.split()
            if len(parts) != 3:
                raise ValueError(
                    f'Entity "origin" field must have exactly 3 components, got {origin!r}'
                )
            try:
                ox, oy, oz = (float(v) for v in parts)
            except ValueError as exc:
                raise ValueError(
                    f'Entity "origin" field must contain numeric values, got {origin!r}'
                ) from exc
            rad = math.radians(angle_deg)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            x, y = ox - cx, oy - cy
            nx = cx + x * cos_a - y * sin_a
            ny = cy + x * sin_a + y * cos_a
            fields["origin"] = (
                f"{format_value(nx)} {format_value(ny)} {format_value(oz)}"
            )
        angle = fields.get("angle")
        if angle is not None:
            try:
                fields["angle"] = format_value(float(angle) + angle_deg)
            except ValueError:
                pass
        brushes = [b.rotated_z(angle_deg, cx, cy) for b in self.brushes]
        return Entity(self.classname, fields, brushes)


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
