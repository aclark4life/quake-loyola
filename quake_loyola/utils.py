"""Small, general-purpose helpers shared across the package.

Pure formatting helpers (format_value, format_point) and generic geometric
transforms (swap_xy, swap_xz) used by the shape constructors in geometry.py.
"""


def format_value(v):
    """Format a number as an integer string if whole, otherwise 6-sig-fig float."""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.6g}"


def format_point(x, y, z):
    """Return a Quake map point literal string '( x y z )'."""
    return f"( {format_value(x)} {format_value(y)} {format_value(z)} )"


def swap_xy(src):
    """Return a new Brush with X and Y coordinates swapped on every face.

    Swapping two coordinates is a reflection, which flips the handedness of the
    coordinate system and reverses each face's outward normal.  To compensate,
    p2 and p3 are also swapped so that the winding order — and therefore the
    outward normal direction — is preserved.
    """
    # Imported here to avoid a circular import: mapdata imports format_point
    # from this module at load time.
    from .mapdata import Brush, Face

    def swap(p):
        """Swap the X and Y components of a point, leaving Z unchanged."""
        return (p[1], p[0], p[2])

    return Brush(
        [
            Face(
                swap(face.p1),
                swap(face.p3),  # p3 before p2 cancels the reflection flip
                swap(face.p2),
                face.tex,
                face.params,
            )
            for face in src.faces
        ]
    )


def swap_xz(src):
    """Return a new Brush with X and Z coordinates swapped on every face.

    Same reflection-parity fix as ``swap_xy``, but swapping X and Z instead of
    X and Y (leaving Y unchanged).
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
