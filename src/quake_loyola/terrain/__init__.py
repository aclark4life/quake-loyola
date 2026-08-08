"""Terrain builders for the map's quadrant-specific ground geometry.

Each submodule exposes ``build() -> (brushes, entities)``.

Sampled height grids (``ne``, ``west_campus``) are meshed by
``_mesh_helpers.append_sampled_grid_mesh``, which tiles the grid exactly: each
cell spans one ``x``/``y`` interval and reads its corner heights from the
shared sample table, so adjacent cells agree on the edge between them to the
bit and the surface is watertight without any fudging.

Do not reintroduce a row "overlap". Earlier revisions stretched each row's far
edge a few units past its boundary to hide seams that the exact tiling above
means never existed. The cost was real: overlapping rows interpenetrate near
their shared edge, and every one of those intersections is a thin sliver in
the BSP that qbsp's outside fill can fail to reach from any entity and mark
solid — producing a wall of ground texture running from grade to the sky, with
no leak reported to explain it. That bit the ``ne`` grid at two different
overlap widths and forced a hand-tuned magic number in each grid, one that had
to be re-swept whenever nearby geometry moved. Removing the overlap dropped
qbsp's "sides not found" from 123 to 107 and "edges degenerated" from 24 to 6,
and ``tests/test_streets_terrain.py`` now asserts that every meshed brush stays
inside its own cell so the fudging cannot creep back in.
"""

from . import knott_hall, ne, west_campus

__all__ = ["knott_hall", "ne", "west_campus"]
