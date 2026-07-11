import sys
from collections import deque
from pathlib import Path

# Ensure the project root and src/ are on the path
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "src"))

from generate_map import build_map
from quake_loyola.constants import WORLD_X1, WORLD_X2, WORLD_Y1, WORLD_Y2, WORLD_Z2


def check_leaks():
    mb = build_map()
    world_brushes = mb.brushes

    # Origins of non-worldspawn entities
    entities = []
    for ent in mb.entities:
        if "origin" in ent.fields:
            coords = [float(x) for x in ent.fields["origin"].split()]
            if len(coords) == 3:
                entities.append((ent.classname, tuple(coords)))

    print(
        f"Checking {len(entities)} entities against {len(world_brushes)} world brushes..."
    )

    # 1. Stuck check (simple)
    stuck = []
    for cls, origin in entities:
        for b in world_brushes:
            if b.contains(origin):
                stuck.append((cls, origin))
                break

    if stuck:
        print(f"Found {len(stuck)} STUCK entities (inside brushes):")
        for cls, origin in stuck[:10]:
            print(f"  * {cls} at {origin}")
        if len(stuck) > 10:
            print(f"  ... and {len(stuck) - 10} more.")

    # 2. Leak check (flood fill)
    # Use a step that matches the seal thickness (ST=64)
    STEP = 64

    # Align grid with the safety seal from streets.py
    # seal_x1, seal_x2 = WORLD_X1 - 256, WORLD_X2_EXT + 256
    # seal_y1, seal_y2 = WORLD_Y1 - 256, WORLD_Y2 + 256
    # seal_z1, seal_z2 = BASEMENT_FLOOR_Z1 - 256, WORLD_Z2 + 512
    # BASEMENT_FLOOR_Z1 = -(WORLD_Z2 + 512)

    # We need WORLD_X2_EXT and BASEMENT_FLOOR_Z1
    from quake_loyola.constants import WORLD_X2_EXT

    BASEMENT_FLOOR_Z1 = -(WORLD_Z2 + 512)

    MIN_X, MAX_X = WORLD_X1 - 256 - STEP, WORLD_X2_EXT + 256 + STEP
    MIN_Y, MAX_Y = WORLD_Y1 - 256 - STEP, WORLD_Y2 + 256 + STEP
    MIN_Z, MAX_Z = BASEMENT_FLOOR_Z1 - 256 - STEP, WORLD_Z2 + 512 + STEP

    NX = int((MAX_X - MIN_X) // STEP) + 1
    NY = int((MAX_Y - MIN_Y) // STEP) + 1
    NZ = int((MAX_Z - MIN_Z) // STEP) + 1

    print(f"Grid size: {NX}x{NY}x{NZ} ({NX * NY * NZ} cells, STEP={STEP})")

    def grid_to_world(ix, iy, iz):
        return (
            MIN_X + ix * STEP + STEP / 2,
            MIN_Y + iy * STEP + STEP / 2,
            MIN_Z + iz * STEP + STEP / 2,
        )

    def world_to_grid(x, y, z):
        return (
            int((x - MIN_X) // STEP),
            int((y - MIN_Y) // STEP),
            int((z - MIN_Z) // STEP),
        )

    # Pre-calculate bboxes and expand them slightly for robustness
    expanded_bboxes = []
    for b in world_brushes:
        bmin, bmax = b.get_bbox()
        expanded_bboxes.append(
            (
                (bmin[0] - 0.1, bmin[1] - 0.1, bmin[2] - 0.1),
                (bmax[0] + 0.1, bmax[1] + 0.1, bmax[2] + 0.1),
            )
        )

    reachable = set()
    queue = deque()
    # Boundary seeds
    for ix in range(NX):
        for iy in range(NY):
            queue.append((ix, iy, 0))
            queue.append((ix, iy, NZ - 1))
    for ix in range(NX):
        for iz in range(1, NZ - 1):
            queue.append((ix, 0, iz))
            queue.append((ix, NY - 1, iz))
    for iy in range(1, NY - 1):
        for iz in range(1, NZ - 1):
            queue.append((0, iy, iz))
            queue.append((NX - 1, iy, iz))

    solid_cache = {}

    def is_solid(ix, iy, iz):
        if (ix, iy, iz) in solid_cache:
            return solid_cache[(ix, iy, iz)]
        p = grid_to_world(ix, iy, iz)
        res = False
        for i, b in enumerate(world_brushes):
            bmin, bmax = expanded_bboxes[i]
            if (
                bmin[0] <= p[0] <= bmax[0]
                and bmin[1] <= p[1] <= bmax[1]
                and bmin[2] <= p[2] <= bmax[2]
            ):
                if b.contains(p):
                    res = True
                    break
        solid_cache[(ix, iy, iz)] = res
        return res

    print("Running flood fill...")
    processed = 0
    while queue:
        curr = queue.popleft()
        if curr in reachable:
            continue
        ix, iy, iz = curr
        if not (0 <= ix < NX and 0 <= iy < NY and 0 <= iz < NZ):
            continue

        if not is_solid(ix, iy, iz):
            reachable.add(curr)
            processed += 1
            if processed % 100000 == 0:
                print(f"  ... visited {processed} cells")
            for dx, dy, dz in [
                (1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1),
            ]:
                neighbor = (ix + dx, iy + dy, iz + dz)
                if neighbor not in reachable:
                    queue.append(neighbor)

    print(f"Reachable void cells: {len(reachable)}")

    leaks = []
    for cls, origin in entities:
        g = world_to_grid(*origin)
        if g in reachable:
            leaks.append((cls, origin))

    if leaks:
        print(f"Found {len(leaks)} LEAKING entities (can reach the void):")
        for cls, origin in leaks[:10]:
            print(f"  * {cls} at {origin}")
        if len(leaks) > 10:
            print(f"  ... and {len(leaks) - 10} more.")
    else:
        print("No leaks detected!")


if __name__ == "__main__":
    check_leaks()
