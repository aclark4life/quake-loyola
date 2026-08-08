"""West-campus dorms — cleared, pending a rebuild.

The dorm buildings that used to stand here (two north, two south, on the
hillside west of Charles St) have been removed so they can be rebuilt from
scratch, the same way Knott Hall's detailed prototype was retired before
being rebuilt. Nothing is emitted yet; this module is the placeholder the
rebuilt geometry will go into, and it stays wired into ``mapgen.MODULES``
so the rebuild only has to fill in :func:`build`.

The retired prototype's generically reusable pieces were factored out
first and are ready to use:

``geometry/buildings.py``
    ``floor_window_levels`` / ``floor_window_openings`` (per-storey window
    grids), ``wall_runs`` / ``frame_runs`` (spec-driven wall and trim
    batchers), ``gable_roof`` (plus its ``_west_half`` / ``_east_half``
    halves), ``chimney_stack``, ``transom_grille_ywall``, and
    ``straight_stair_x``.

``geometry/prefabs.py``
    ``exit_portal`` — the labelled ``EXIT`` teleport portal and its signed
    frame, which used to sit inside the second north dorm.

The footprint, height, lift, and terrace constants all survive in
``constants/dorm.py`` and ``constants/derived.py`` (``DORM``,
``DORM_NORTH_Y1``/``Y2``, ``DORM_NORTH2_Y1``/``Y2``, ``DORM_SOUTH1_*``,
``DORM_SOUTH2_*``, ``DORM_H``, ``DORM_ROOF_H``, ``NORTH_DORM_LIFT``,
``SDORM_LIFT``, ``SDORM_STAIR_*``), and are still consumed by the
west-campus terrain grid, the Charles St sky walls, and the frontage walk
— so the rebuilt buildings will land back on the same footprint.

There is no ``WEST_CAMPUS_ENABLED_DORMS`` flag any more; it was removed
along with the geometry rather than left behind as a toggle that does
nothing. Add a fresh flag when there is something to gate again.
"""


def build():
    """Build the west-campus dorms.

    Returns:
        tuple[list, list]: Always ``([], [])`` — the dorms are cleared
        pending a rebuild. See the module docstring.
    """
    return [], []
