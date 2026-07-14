import math
import random

from ..constants import FASCIA_FONT, TREE_PROFILES, Textures
from ..mapdata import Brush, Face
from .primitives import arch_seg, box, curb_seg, pyramid


def make_tree(cx, cy, base_z):
    TEX_TRUNK, TEX_FOLIAGE = Textures.BRICK, Textures.GROUND
    return [
        box(cx - 5, cy - 5, base_z, cx + 5, cy + 5, base_z + 56, TEX_TRUNK),
        pyramid(
            cx - 40, cy - 40, base_z + 32, cx + 40, cy + 40, base_z + 80, TEX_FOLIAGE
        ),
        pyramid(
            cx - 28, cy - 28, base_z + 64, cx + 28, cy + 28, base_z + 108, TEX_FOLIAGE
        ),
        pyramid(
            cx - 16, cy - 16, base_z + 92, cx + 16, cy + 16, base_z + 128, TEX_FOLIAGE
        ),
    ]


def make_giant_tree(cx, cy, base_z, total_h=700):
    TEX_TRUNK, TEX_FOLIAGE = Textures.BRICK, Textures.GROUND
    trunk_h, l0, l1 = int(total_h * 0.45), int(total_h * 0.225), int(total_h * 0.57)
    m0, m1 = int(total_h * 0.48), int(total_h * 0.78)
    u0, u1 = int(total_h * 0.70), total_h
    return [
        box(cx - 12, cy - 12, base_z, cx + 12, cy + 12, base_z + trunk_h, TEX_TRUNK),
        pyramid(
            cx - 160,
            cy - 160,
            base_z + l0,
            cx + 160,
            cy + 160,
            base_z + l1,
            TEX_FOLIAGE,
        ),
        pyramid(
            cx - 110,
            cy - 110,
            base_z + m0,
            cx + 110,
            cy + 110,
            base_z + m1,
            TEX_FOLIAGE,
        ),
        pyramid(
            cx - 60, cy - 60, base_z + u0, cx + 60, cy + 60, base_z + u1, TEX_FOLIAGE
        ),
    ]


def make_bush(cx, cy, base_z, size=24):
    return [
        box(cx - 6, cy - 6, base_z, cx + 6, cy + 6, base_z + 10, Textures.GROUND),
        box(
            cx - size,
            cy - size,
            base_z + 10,
            cx + size,
            cy + size,
            base_z + size + 10,
            Textures.GROUND,
        ),
        pyramid(
            cx - size + 4,
            cy - size + 4,
            base_z + size + 6,
            cx + size - 4,
            cy + size - 4,
            base_z + size + 20,
            Textures.GROUND,
        ),
    ]


def octagon_column(cx, cy, z0, z1, radius, tex):
    faces, N = [], 8
    for i in range(N):
        theta = math.pi * 2 * i / N
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        qx, qy = cx + radius * cos_t, cy + radius * sin_t
        faces.append(
            Face((qx, qy, z0), (qx, qy, z0 + 1), (qx - sin_t, qy + cos_t, z0), tex)
        )
    faces.append(Face((cx, cy, z1), (cx + 1, cy, z1), (cx, cy - 1, z1), tex))
    faces.append(Face((cx, cy, z0), (cx + 1, cy, z0), (cx, cy + 1, z0), tex))
    return Brush(faces)


def make_pixel_tree(
    cx,
    cy,
    base_z,
    profile="street",
    vox_size=24,
    fins=2,
    trunk_fins=None,
    trunk_solid=False,
    fin_jitter=0.0,
    fin_seed=0,
    ring_segs=0,
):
    _rng, _TEX = (
        random.Random(fin_seed),
        {"L": Textures.GROUND, "B": Textures.MULCH, "T": Textures.MULCH},
    )
    prof = TREE_PROFILES[profile] if isinstance(profile, str) else profile
    rows, cols, half = len(prof), max(len(r) for r in prof), vox_size // 2
    half_cols, _trunk_fins, brushes = (
        cols // 2,
        (trunk_fins if trunk_fins is not None else fins),
        [],
    )
    if trunk_solid:
        idx = [i for i, r in enumerate(prof) if "L" not in r]
        if idx:
            z1, z0 = (
                base_z + (rows - 1 - idx[0]) * vox_size + vox_size,
                base_z + (rows - 1 - idx[-1]) * vox_size,
            )
            tw = [
                len([i for i, ch in enumerate(r) if ch in _TEX])
                for r in prof
                if "L" not in r
            ]
            brushes.append(
                octagon_column(
                    cx, cy, z0, z1, (max(tw, default=4) // 2) * vox_size, Textures.MULCH
                )
            )
    for row_i, row_str in enumerate(prof):
        z0, z1, is_trunk = (
            base_z + (rows - 1 - row_i) * vox_size,
            base_z + (rows - 1 - row_i) * vox_size + vox_size,
            "L" not in row_str,
        )
        if is_trunk and trunk_solid:
            continue
        if not is_trunk and ring_segs > 0:
            sc = [i for i, ch in enumerate(row_str) if ch == "L"]
            if sc:
                outer_r = max(
                    max(
                        abs(c - half_cols) * vox_size, abs(c - half_cols + 1) * vox_size
                    )
                    for c in sc
                )
                for seg_i in range(ring_segs):
                    brushes.append(
                        curb_seg(
                            cx,
                            cy,
                            z0,
                            z1,
                            0,
                            outer_r,
                            360.0 * seg_i / ring_segs,
                            360.0 * (seg_i + 1) / ring_segs,
                            Textures.GROUND,
                        )
                    )
            continue
        row_fins = fins if not is_trunk else _trunk_fins
        for k in range(row_fins):
            angle = math.pi * k / row_fins + (math.pi / row_fins) * fin_jitter * (
                _rng.random() * 2 - 1
            )
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            if fin_jitter == 0.0 and (abs(sin_a) < 1e-9 or abs(cos_a) < 1e-9):
                run_start, run_tex = None, None
                for col_i in range(cols + 1):
                    ch = row_str[col_i] if col_i < len(row_str) else " "
                    tex = _TEX.get(ch)
                    if tex is not None and tex == run_tex:
                        pass
                    else:
                        if run_start is not None:
                            d0, d1 = (
                                (run_start - half_cols) * vox_size,
                                (col_i - half_cols) * vox_size,
                            )
                            if abs(sin_a) < 1e-9:
                                brushes.append(
                                    box(
                                        cx + d0,
                                        cy - half,
                                        z0,
                                        cx + d1,
                                        cy + half,
                                        z1,
                                        run_tex,
                                    )
                                )
                            else:
                                brushes.append(
                                    box(
                                        cx - half,
                                        cy + d0,
                                        z0,
                                        cx + half,
                                        cy + d1,
                                        z1,
                                        run_tex,
                                    )
                                )
                        run_start, run_tex = (col_i if tex is not None else None), tex
            else:
                for col_i, ch in enumerate(row_str):
                    if _TEX.get(ch):
                        d = (col_i - half_cols) * vox_size
                        brushes.append(
                            box(
                                int(cx + d * cos_a) - half,
                                int(cy + d * sin_a) - half,
                                z0,
                                int(cx + d * cos_a) + half,
                                int(cy + d * sin_a) + half,
                                z1,
                                _TEX[ch],
                            )
                        )
    return brushes


def render_text_flat_x(text, y0, x_face, z_base, px_w, px_h, depth, tex, mirror=False):
    cols, rows, brushes = 4, 6, []
    char_w = (cols + 1) * px_w
    for ci, ch in enumerate(text):
        bitmap, cy = FASCIA_FONT.get(ch, FASCIA_FONT[" "]), y0 + ci * char_w
        for row_i, row_bits in enumerate(bitmap):
            z, run_start = z_base + (rows - 1 - row_i) * px_h, None
            for col_i in range(cols + 1):
                src_col = (cols - 1 - col_i) if mirror else col_i
                lit = col_i < cols and (row_bits & (1 << (cols - 1 - src_col)))
                if lit and run_start is None:
                    run_start = col_i
                elif not lit and run_start is not None:
                    brushes.append(
                        box(
                            x_face,
                            cy + run_start * px_w,
                            z,
                            x_face + depth,
                            cy + col_i * px_w,
                            z + px_h,
                            tex,
                        )
                    )
                    run_start = None
    return brushes


def render_text_flat(text, x0, y_face, z_base, px_w, px_h, depth, tex, mirror=False):
    cols, rows, brushes = 4, 6, []
    char_w = (cols + 1) * px_w
    for ci, ch in enumerate(text):
        bitmap, cx = FASCIA_FONT.get(ch, FASCIA_FONT[" "]), x0 + ci * char_w
        for row_i, row_bits in enumerate(bitmap):
            z, run_start = z_base + (rows - 1 - row_i) * px_h, None
            for col_i in range(cols + 1):
                src_col = (cols - 1 - col_i) if mirror else col_i
                lit = col_i < cols and (row_bits & (1 << (cols - 1 - src_col)))
                if lit and run_start is None:
                    run_start = col_i
                elif not lit and run_start is not None:
                    brushes.append(
                        box(
                            cx + run_start * px_w,
                            y_face,
                            z,
                            cx + col_i * px_w,
                            y_face + depth,
                            z + px_h,
                            tex,
                        )
                    )
                    run_start = None
    return brushes


def iron_fence(
    segments, x1, x2, tex, z_base, height=80, spacing=16, circle_rin=5, circle_rout=8
):
    if spacing <= 0:
        raise ValueError(f"iron_fence: spacing must be > 0 (got {spacing})")
    brushes, circle_cz = [], z_base + height - 8
    for fy1, fy2 in segments:
        brushes.append(box(x1, fy1, z_base + height - 2, x2, fy2, z_base + height, tex))
        brushes.append(
            box(x1, fy1, z_base + height - 16, x2, fy2, z_base + height - 14, tex)
        )
        picket_y, picket_index = fy1, 0
        while True:
            picket_w = 8 if picket_index % 10 == 0 else 2
            if picket_y + picket_w > fy2:
                break
            brushes.append(
                box(x1, picket_y, z_base, x2, picket_y + picket_w, z_base + height, tex)
            )
            picket_y, picket_index = picket_y + spacing, picket_index + 1
        circle_cy = fy1 + spacing // 2
        while circle_cy + circle_rout <= fy2:
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
