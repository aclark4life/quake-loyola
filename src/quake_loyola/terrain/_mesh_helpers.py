"""Shared helpers for meshing sampled terrain height grids."""

from ..geometry import extend_terrain_row_overlap


def append_sampled_grid_mesh(
    brushes,
    x_grid,
    y_grid,
    height_cols,
    *,
    overlap,
    texture,
    build_cell_brushes,
):
    """Append terrain brushes for one sampled height grid."""

    for (x1, col1), (x2, col2) in zip(
        zip(x_grid, height_cols, strict=False),
        zip(x_grid[1:], height_cols[1:], strict=False),
        strict=False,
    ):
        for i in range(len(y_grid) - 1):
            y1, y2 = y_grid[i], y_grid[i + 1]
            z_nw, z_sw = col1[i], col1[i + 1]
            z_ne, z_se = col2[i], col2[i + 1]
            if i < len(y_grid) - 2:
                y2, z_sw, z_se = extend_terrain_row_overlap(
                    y1,
                    y2,
                    z_nw,
                    z_sw,
                    z_ne,
                    z_se,
                    overlap,
                )
            brushes.extend(
                build_cell_brushes(
                    x1,
                    x2,
                    y1,
                    y2,
                    z_nw,
                    z_sw,
                    z_ne,
                    z_se,
                    texture,
                )
            )
