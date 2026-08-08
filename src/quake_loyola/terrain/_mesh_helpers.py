"""Shared helpers for meshing sampled terrain height grids."""


def append_sampled_grid_mesh(
    brushes,
    x_grid,
    y_grid,
    height_cols,
    *,
    texture,
    build_cell_brushes,
):
    """Append terrain brushes for one sampled height grid.

    Cells tile the grid exactly: each one owns
    ``[x_grid[j], x_grid[j + 1]] x [y_grid[i], y_grid[i + 1]]`` and takes its
    four corner heights straight out of ``height_cols``. Neighbouring cells
    therefore read the *same* sampled height for the edge they share, so the
    meshed surface is watertight by construction.

    That is the invariant this module exists to preserve: no cell is stretched
    past its own boundary to paper over a seam, because there is no seam to
    paper over, and stretching one is actively harmful — see the
    ``quake_loyola.terrain`` package docstring.
    """

    for (x1, col1), (x2, col2) in zip(
        zip(x_grid, height_cols, strict=False),
        zip(x_grid[1:], height_cols[1:], strict=False),
        strict=False,
    ):
        for i in range(len(y_grid) - 1):
            brushes.extend(
                build_cell_brushes(
                    x1,
                    x2,
                    y_grid[i],
                    y_grid[i + 1],
                    col1[i],
                    col1[i + 1],
                    col2[i],
                    col2[i + 1],
                    texture,
                )
            )
