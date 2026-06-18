"""Small, general-purpose helpers shared across the package.

Pure formatting helpers (format_value, format_point) and a generic geometric
transform (swap_xy) used by the shape constructors in geometry.py.
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


def iron_fence(
    segments,
    x1,
    x2,
    tex,
    z_base,
    height=80,
    spacing=16,
    circle_rin=5,
    circle_rout=8,
):
    """Build an iron fence for each (y1, y2) span in segments.

    Each span gets a top rail, a second crossbeam a few inches below it,
    vertical pickets (every spacing units; every 10th is a wider post), and a
    small decorative circle (8-segment octagon ring) in the gap between every
    pair of pickets, sitting in the Z gap between the two top rails.

    Returns a flat list of brushes; the caller groups them into a func_detail.
    """
    # Imported here to avoid a circular import: geometry.py imports swap_xy
    # from this module at load time.
    from .geometry import arch_seg, box

    brushes = []
    circle_cz = z_base + height - 8  # midpoint of the gap between the two beams
    for fy1, fy2 in segments:
        # Top rail
        brushes.append(box(x1, fy1, z_base + height - 2, x2, fy2, z_base + height, tex))
        # Second crossbeam — a few inches below the top rail
        brushes.append(
            box(x1, fy1, z_base + height - 16, x2, fy2, z_base + height - 14, tex)
        )
        picket_y = fy1
        picket_index = 0
        while picket_y + 2 <= fy2:
            picket_w = 8 if picket_index % 10 == 0 else 2
            brushes.append(
                box(x1, picket_y, z_base, x2, picket_y + picket_w, z_base + height, tex)
            )
            picket_y += spacing
            picket_index += 1
        # Proper iron circle (8-segment octagon ring) in every gap between
        # adjacent pickets, sitting in the Z gap between the two top rails
        circle_cy = fy1 + spacing // 2
        while circle_cy + circle_rout <= fy2:
            # 8 arch_seg calls × 45° = full 360° circle ring in the Y-Z plane
            for seg_i in range(8):
                brushes.append(
                    arch_seg(
                        x1,
                        x2,
                        circle_cy,
                        float(circle_cz),
                        circle_rin,
                        circle_rout,
                        seg_i * 45,
                        (seg_i + 1) * 45,
                        tex,
                    )
                )
            circle_cy += spacing
    return brushes
