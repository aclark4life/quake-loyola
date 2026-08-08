Architecture Overview
=====================

Data model
----------

All geometry is expressed through three dataclasses defined in
:mod:`quake_loyola.mapdata`:

* :class:`~quake_loyola.mapdata.Face` — a single brush face: three coplanar
  points that define a half-space, plus a texture name and alignment
  parameters.
* :class:`~quake_loyola.mapdata.Brush` — an ordered list of :class:`Face`
  objects that together bound a convex solid.
* :class:`~quake_loyola.mapdata.Entity` — a Quake entity: a ``classname``,
  a key/value dict of fields, and an optional list of :class:`Brush` objects
  (brush entities such as ``func_detail``; point entities carry no brushes).
* :class:`~quake_loyola.mapdata.MapBuilder` — accumulator that collects world
  brushes and entities, then serializes the whole scene as a ``.map`` document
  via :meth:`~quake_loyola.mapdata.MapBuilder.to_map`.

Shape constructors
------------------

:mod:`quake_loyola.geometry` contains all primitive shape builders that return
:class:`~quake_loyola.mapdata.Brush` (or lists of brushes / entities):

* ``box(x1, y1, z1, x2, y2, z2, tex, …)`` — axis-aligned rectangular prism.
* ``ramp_slab(…)`` — a wedge whose top surface slopes in the *X* direction.
* ``ramp_slab_y(…)`` — same wedge but sloping in the *Y* direction.
* ``arch_seg(…)`` — a single trapezoidal segment of a circular arch.
* ``arch_fill(…)`` — solid fill beneath an arch span.
* ``arch_wall(…)`` — a full arch wall built from ``arch_seg`` calls.
* ``pyramid(…)`` — four-sided pyramid (used for gable roofs and caps).
* ``layered_wall`` / ``layered_wall_y`` — multi-storey wall with optional
  window or door openings, returns a ``func_detail`` entity.
* ``iron_fence(…)`` (in :mod:`quake_loyola.utils`) — a decorative iron fence
  with rails, pickets, and octagonal ring ornaments.

All coordinates are in Quake map units.  The compile-time ``SCALE`` constant
(≈ 15.1 units per foot) relates them to real-world distances.

Constants
---------

Every numeric dimension lives in :mod:`quake_loyola.constants`.  Key groups:

* **World bounds** — ``WORLD_X1/X2``, ``WORLD_Y1/Y2``, ``WORLD_Z2`` define
  the skybox walls.
* **Bridge geometry** — ``BRIDGE_X1/X2``, ``BRIDGE_Y1/Y2``, arch radius,
  pillar dimensions, deck heights.
* **Dorm buildings** — ``DORM_X1/X2``, ``DORM_NORTH_Y1/Y2``,
  ``DORM_SOUTH1_*``, floor heights, embankment slopes.
* **Roads / streets** — ``ROAD_X1/X2``, ``FLOOR_Z1/Z2``.
* :class:`~quake_loyola.constants.Textures` — a namespace of texture name
  strings used throughout (``GROUND``, ``BRICK``, ``STONE``, etc.).

Module responsibilities
-----------------------

Each module's ``build()`` function returns ``(brushes, entities)`` and is
called in order by :func:`generate_map.build_map`:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Module
     - Responsibility
   * - :mod:`quake_loyola.streets`
     - Charles Street road surface, curbs, footpaths, world sky walls,
       and the embankment slopes on the south dorm side.
   * - :mod:`quake_loyola.west_campus`
     - West-campus frontage: the hillside iron fence, brick wall, and
       terrace walk.
   * - :mod:`quake_loyola.dorms`
     - Placeholder for the west-campus dormitories, which have been
       removed pending a rebuild; currently emits nothing.
   * - :mod:`quake_loyola.bridge`
     - The pedestrian bridge deck, arch ribs, pillars, railings, the
       east/west walkway approaches, and the "LOYOLA UNIVERSITY MARYLAND"
       parapet fascia lettering.
   * - :mod:`quake_loyola.terrain.knott_hall`
     - The Knott Hall hillside terrain, driveway corridor, and retaining
       walls on the east side of Charles Street.
   * - :mod:`quake_loyola.knott_hall`
     - Knott Hall building shell: walls, floors, roof, windows, interior.
   * - :mod:`quake_loyola.entities`
     - All Quake point entities: player spawns, deathmatch spawns, health /
       armour / weapon pickups, the exit teleporter and its frame.

Build pipeline
--------------

.. code-block:: text

    generate_map.py          ← assembles MapBuilder, writes loyola.map
         │
         ▼
    qbsp loyola.map          ← compiles brushes to BSP (ericw-tools)
         │
         ▼
    vis  loyola.bsp          ← computes potentially-visible sets
         │
         ▼
    light loyola.bsp         ← ray-traced lighting (sunlight + dynamic)
         │
         ▼
    loyola.bsp + loyola.lit  ← deployed to /Applications/id1/maps/

Use ``just compile-fast`` for quick iterations (``vis -fast``), or
``just compile`` for a full vis pass before a release.

Testing
-------

``tests/test_regression.py`` compares brush count, entity count, and the MD5
hash of the generated ``.map`` text against known-good golden values.
Changing any geometry or constant will break these tests; run ``just
update-golden`` to recompute and patch the golden values automatically, then
review the diff before committing.

``tests/test_mapdata.py`` and ``tests/test_geometry.py`` provide unit tests
for the data model and shape constructors respectively.

AI agent instructions
---------------------

``.github/copilot-instructions.md`` is the canonical reference for AI coding
agents (GitHub Copilot IDE, Copilot CLI, and others).  It covers the full
project layout, all ``just`` recipes, coding conventions, and the expected
map-change and commit workflow.

``AGENTS.md`` at the repo root is a one-line pointer to that file, providing
compatibility with agents that look for ``AGENTS.md`` by convention.
