"""Shared formatting and coordinate-swap helpers."""


def format_value(v):
    """Format a number as an integer string if whole, otherwise 6-sig-fig float."""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"


def format_point(x, y, z):
    """Return a Quake map point literal string '( x y z )'."""
    return f"( {format_value(x)} {format_value(y)} {format_value(z)} )"


def swap_xy(src):
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


def swap_xz(src):
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
