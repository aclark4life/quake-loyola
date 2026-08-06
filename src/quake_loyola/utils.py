"""Shared formatting and coordinate-swap helpers."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mapdata import Brush


#: Magnitude below which a coordinate is treated as exactly zero. Trig-derived
#: coordinates (arch segments, rotated brushes) land on values like 6.1e-17
#: instead of 0; emitting those verbatim gives qbsp plane definitions with
#: meaningless sub-epsilon skew.
_ZERO_SNAP = 1e-9

#: Significant figures used when serialising non-integer coordinates. Six
#: sig-figs (the historical value) quantises a coordinate near 121.244444 to
#: 121.244 — an error of up to 5e-4 that qbsp reports as "Point ... off plane"
#: and "Healing degenerate edge", because brushes meshed from the same
#: interpolated surface no longer share exactly coplanar faces. Ten sig-figs
#: keeps the geometry the generator actually computed.
_SIG_FIGS = 10


def format_value(v: float) -> str:
    """Format a number as an integer string if whole, otherwise a 10-sig-fig float."""
    f = float(v)
    if abs(f) < _ZERO_SNAP:
        f = 0.0
    return str(int(f)) if f == int(f) else f"{f:.{_SIG_FIGS}g}"


def format_point(x: float, y: float, z: float) -> str:
    """Return a Quake map point literal string '( x y z )'."""
    return f"( {format_value(x)} {format_value(y)} {format_value(z)} )"


def swap_xy(src: "Brush") -> "Brush":
    """Return a new Brush with X and Y coordinates swapped on every face.

    Swapping two coordinates reflects the brush, so the face winding is also
    swapped to preserve outward normals.
    """

    from .mapdata import Brush, Face

    def swap(p):
        """Swap the X and Y components of a point, leaving Z unchanged."""
        return (p[1], p[0], p[2])

    return Brush(
        [
            Face(
                swap(face.p1),
                swap(face.p3),
                swap(face.p2),
                face.tex,
                face.params,
            )
            for face in src.faces
        ]
    )


def swap_xz(src: "Brush") -> "Brush":
    """Return a new Brush with X and Z coordinates swapped on every face.

    Same winding correction as ``swap_xy``, but swapping X and Z.
    """
    from .mapdata import Brush, Face

    def swap(p):
        """Swap the X and Z components of a point, leaving Y unchanged."""
        return (p[2], p[1], p[0])

    return Brush(
        [
            Face(
                swap(face.p1),
                swap(face.p3),
                swap(face.p2),
                face.tex,
                face.params,
            )
            for face in src.faces
        ]
    )
