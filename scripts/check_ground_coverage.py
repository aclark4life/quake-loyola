"""check_ground_coverage — grid-scan the *entire* map for ground/floor gaps.

Unlike ``check_terrain_cliffs.py`` (which only looks at the Knott Hall
terrain slice), this walks every brush in the fully-assembled map
(``generate_map.build_map()``) and:

  * Collects every brush face that is a walkable top surface (floors,
    decks, roads, sidewalks, terrain, ramps, etc). Note: face normals in
    this codebase's ``Brush``/``Face`` representation point *inward* (into
    the solid) — see ``mapdata._face_plane``/``Face.is_inside`` — so a
    physical top surface has a normal pointing *down*, not up.
  * Projects each such brush's full vertex set to XY and reduces it to a
    convex hull, used as that face's footprint.
  * Samples a grid across the bounding box of all "ground-like" textured
    brushes (the nominal walkable area) and reports:
      - "holes": grid points with no covering top surface at all — the
        player would fall through to the void or a lower/interior space.
      - "cliffs": adjacent grid points whose height differs by more than
        ``JUMP_THRESHOLD`` — usually a misalignment, not a hole, but
        worth a look.

Caveat: only valid for brushes built from convex primitives (box,
ramp_slab, tri_ramp_prism, corner_ramp, etc.) where the top face is a
planar quad and the brush's overall XY hull matches that face's true
extent. Brushes with a non-rectangular top footprint smaller than their
overall hull (e.g. angled prism cuts) can produce a few false "coverage"
claims at the very edges — always sanity-check reported holes visually
in-game or against the source module before treating them as bugs.

Usage:
    python3 scripts/check_ground_coverage.py
"""

import sys
from pathlib import Path

_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "src"))

from generate_map import build_map
from quake_loyola.constants.textures import Textures

STEP = 16
JUMP_THRESHOLD = 80
UP_NORMAL_MIN = 0.5  # min |z-component| (of a unit normal) to call a face "top"
# NOTE: face normals in this codebase point *inward* (into the solid) — see
# Brush.is_inside()/mapdata._face_plane(). A physical top/walkable surface
# therefore has a normal pointing *down* (into the brush below it), and a
# bottom face has a normal pointing *up*. So "is this a top surface" means
# normal.z <= -UP_NORMAL_MIN, not >=.

GROUND_TEXTURES = {
    Textures.GROUND,
    Textures.SIDEWALK,
    Textures.CEMENT,
    Textures.STONE,
    Textures.ROAD,
    Textures.FLOOR,
    Textures.FLOOR1,
    Textures.FLOOR_KH,
    Textures.DECK_EDGE,
    Textures.MULCH,
    Textures.CENTERLINE,
    Textures.PARKING_STRIPE,
}


def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 2:
        return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def point_in_convex(poly, pt, eps=0.5):
    n = len(poly)
    if n < 3:
        return False
    sign = None
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        cr = (b[0] - a[0]) * (pt[1] - a[1]) - (b[1] - a[1]) * (pt[0] - a[0])
        if cr < -eps:
            if sign is None:
                sign = -1
            elif sign > 0:
                return False
        elif cr > eps:
            if sign is None:
                sign = 1
            elif sign < 0:
                return False
    return True


def face_normal(f):
    v1 = (f.p2[0] - f.p1[0], f.p2[1] - f.p1[1], f.p2[2] - f.p1[2])
    v2 = (f.p3[0] - f.p1[0], f.p3[1] - f.p1[1], f.p3[2] - f.p1[2])
    n = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    )
    mag = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
    if mag < 1e-9:
        return (0.0, 0.0, 0.0)
    return (n[0] / mag, n[1] / mag, n[2] / mag)


def plane_z(f, x, y):
    nx, ny, nz = face_normal(f)
    if abs(nz) < 1e-6:
        return None
    d = nx * f.p1[0] + ny * f.p1[1] + nz * f.p1[2]
    return (d - nx * x - ny * y) / nz


def main():
    mb = build_map()
    brushes = mb.brushes

    items = []  # (x1, x2, y1, y2, hull, face)
    ground_x1 = ground_x2 = ground_y1 = ground_y2 = None
    for b in brushes:
        pts = []
        for f in b.faces:
            pts.extend([f.p1[:2], f.p2[:2], f.p3[:2]])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        bx1, bx2, by1, by2 = min(xs), max(xs), min(ys), max(ys)

        is_ground = any(f.tex in GROUND_TEXTURES for f in b.faces)
        if is_ground:
            ground_x1 = bx1 if ground_x1 is None else min(ground_x1, bx1)
            ground_x2 = bx2 if ground_x2 is None else max(ground_x2, bx2)
            ground_y1 = by1 if ground_y1 is None else min(ground_y1, by1)
            ground_y2 = by2 if ground_y2 is None else max(ground_y2, by2)

        top_faces = [
            f
            for f in b.faces
            if face_normal(f)[2] <= -UP_NORMAL_MIN and f.tex in GROUND_TEXTURES
        ]
        if not top_faces:
            continue
        hull = convex_hull(pts)
        if len(hull) < 3:
            continue
        for f in top_faces:
            items.append((bx1, bx2, by1, by2, hull, f))

    print(f"{len(brushes)} brushes, {len(items)} upward-facing top surfaces")
    print(
        f"ground-textured bbox: x[{ground_x1:.0f}, {ground_x2:.0f}] "
        f"y[{ground_y1:.0f}, {ground_y2:.0f}]"
    )

    def height_at(x, y):
        best = None
        for x1, x2, y1, y2, hull, f in items:
            if x < x1 - 1 or x > x2 + 1 or y < y1 - 1 or y > y2 + 1:
                continue
            if not point_in_convex(hull, (x, y)):
                continue
            z = plane_z(f, x, y)
            if z is None:
                continue
            if best is None or z > best:
                best = z
        return best

    xs = list(range(int(ground_x1) + STEP, int(ground_x2), STEP))
    ys = list(range(int(ground_y1) + STEP, int(ground_y2), STEP))
    print(f"scanning {len(xs)} x {len(ys)} = {len(xs) * len(ys)} grid points...")

    grid = {}
    for i, gx in enumerate(xs):
        for gy in ys:
            grid[(gx, gy)] = height_at(gx, gy)
        if (i + 1) % 50 == 0:
            print(f"  ... {i + 1}/{len(xs)} columns")

    holes = [k for k, v in grid.items() if v is None]
    print(f"\nholes (no top surface): {len(holes)} / {len(grid)}")
    for h in sorted(holes)[:80]:
        print(" hole", h)
    if len(holes) > 80:
        print(f" ... and {len(holes) - 80} more")

    big_jumps = []
    for gx in xs:
        for gy in ys:
            z0 = grid[(gx, gy)]
            if z0 is None:
                continue
            for dx, dy in ((STEP, 0), (0, STEP)):
                nx, ny = gx + dx, gy + dy
                if (nx, ny) in grid:
                    z1 = grid[(nx, ny)]
                    if z1 is None:
                        continue
                    if abs(z1 - z0) > JUMP_THRESHOLD:
                        big_jumps.append((gx, gy, nx, ny, round(z0, 1), round(z1, 1)))
    print(f"\ncliffs (>{JUMP_THRESHOLD}u step): {len(big_jumps)}")
    for j in big_jumps[:60]:
        print(" cliff", j)
    if len(big_jumps) > 60:
        print(f" ... and {len(big_jumps) - 60} more")


if __name__ == "__main__":
    main()
