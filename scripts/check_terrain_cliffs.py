"""check_terrain_cliffs — grid-scan the Knott Hall terrain for gaps/cliffs.

Loads brushes from ``quake_loyola.knott_terrain.build()`` (not the full map —
see caveat below), samples a grid across the Charles St -> Ennis Dr -> KH
driveway -> south world-edge rectangle, and reports:

  * "gaps": grid points with no covering terrain brush.
  * "cliffs": adjacent grid points whose height differs by more than
    ``JUMP_THRESHOLD`` units (an unwalkable/unclimbable step).

For each brush, all face vertices are projected to XY and reduced to a
convex hull; the brush's *last* face is evaluated as an infinite plane to
get the height at any point inside that hull. This is valid for every
primitive knott_terrain.py uses (box, tri_prism, tri_ramp_prism,
ramp_slab/ramp_slab_y all emit the "top" face last) but is NOT reliable for
arbitrary brushes elsewhere in the map (walls/buildings can have a
near-vertical last face) — do not point this at the full map's brush list.

Usage:
    python3 scripts/check_terrain_cliffs.py
"""

import sys
from pathlib import Path

# Ensure the project root is on the path when called from any directory.
sys.path.insert(0, str(Path(__file__).parent.parent))

from quake_loyola.constants import (
    CHARLES_RAMP_W,
    CHARLES_WALK_W,
    ENNIS_SW_EDGE,
    ROAD_X2,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y1,
)
from quake_loyola.knott_terrain import build as _kt_build

STEP = 32  # grid resolution, in Quake units
JUMP_THRESHOLD = 80  # unit height delta between adjacent grid cells flagged as a cliff


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


def plane_z(p1, p2, p3, x, y):
    v1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    v2 = (p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2])
    n = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    )
    if abs(n[2]) < 1e-6:
        return None
    d = -(n[0] * p1[0] + n[1] * p1[1] + n[2] * p1[2])
    return -(n[0] * x + n[1] * y + d) / n[2]


def main():
    brushes, _ = _kt_build()

    verge_x2 = ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W
    x_lo, x_hi = verge_x2, WORLD_X2_EXT - WALL_T
    y_lo, y_hi = WORLD_Y1 + WALL_T, ENNIS_SW_EDGE + CHARLES_WALK_W

    items = []
    for b in brushes:
        tf = b.faces[-1]
        pts = []
        for f in b.faces:
            pts.extend([f.p1[:2], f.p2[:2], f.p3[:2]])
        hull = convex_hull(pts)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        items.append((min(xs), max(xs), min(ys), max(ys), hull, tf))

    def height_at(x, y):
        best = None
        for x1, x2, y1, y2, hull, tf in items:
            if x < x1 - 1 or x > x2 + 1 or y < y1 - 1 or y > y2 + 1:
                continue
            if not point_in_convex(hull, (x, y)):
                continue
            z = plane_z(tf.p1, tf.p2, tf.p3, x, y)
            if z is None:
                continue
            if best is None or z > best:
                best = z
        return best

    xs = list(range(int(x_lo), int(x_hi), STEP))
    ys = list(range(int(y_lo), int(y_hi), STEP))
    grid = {(gx, gy): height_at(gx, gy) for gx in xs for gy in ys}

    none_count = sum(1 for v in grid.values() if v is None)
    print("total", len(grid), "none", none_count)

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

    print("big jump count", len(big_jumps))
    for j in big_jumps[:60]:
        print(j)

    none_pts = [k for k, v in grid.items() if v is None]
    if none_pts:
        xs2 = [p[0] for p in none_pts]
        ys2 = [p[1] for p in none_pts]
        print("gap x range", min(xs2), max(xs2))
        print("gap y range", min(ys2), max(ys2))
        print(sorted(none_pts)[:20])


if __name__ == "__main__":
    main()
