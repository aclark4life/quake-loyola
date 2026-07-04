Map Reference
=============

Real-world reference
--------------------

The map recreates the **pedestrian bridge over Charles Street** on Loyola
University Maryland's Evergreen campus in northern Baltimore
(39°20′46″N, 76°37′08″W).

- **The bridge** spans east–west over North Charles Street, which runs
  north–south through the 79-acre campus. The real bridge features Collegiate
  Gothic arched stonework connecting the west and east sides of campus.
- **Knott Hall** — formally the *Francis Xavier Knott, S.J. Knott Humanities
  Center* — is the oldest building on campus (1896). Originally a Tudor Revival
  private residence designed by Renwick, Aspinwall & Renwick for the Garrett
  family (heirs to the Baltimore & Ohio Railroad fortune), it was purchased by
  the Jesuits in 1921 and converted to academic use. The building sits east of
  Charles Street, south of the bridge.
- The campus was founded in 1852 and moved to its current "Evergreen" location
  in 1922. Notable alumni include Tom Clancy and Mark Bowden.

World scale
-----------

Quake units are converted to real-world feet via ``constants.SCALE = 15.108``
units per foot (``constants.ft_to_units(feet, inches)``). That works out to
**1 unit ≈ 0.79 inch** — close to, but not exactly, the "1 unit ≈ 1 inch"
rule of thumb used elsewhere in this project's documentation.

The world-shell rectangle (``WORLD_X1``/``WORLD_X2``/``WORLD_Y1``/``WORLD_Y2``
in ``constants.py``) was re-derived from pixel measurements against the
scale bars baked into the Google Maps screenshots in ``ref/`` (e.g.
``ref/gmaps-kh-satellite.png``'s 50 ft bar, ``ref/gmaps-campus-satellite-wide.png``'s
100 ft bar). Measuring from the west dorms' facade to Knott Hall's east
face/Ennis Parallel bend, and from Hopkins Court to E Cold Spring Ln, gives
an estimated real-world target footprint of:

- **~850 ft** east–west (X axis — dorms to Knott Hall/Ennis Parallel)
- **~710 ft** north–south (Y axis — Hopkins Court to E Cold Spring Ln)

These are rough estimates (±10–15%) from manual pixel-to-scale-bar
measurement, not a surveyed footprint. ``WORLD_X1``/``WORLD_X2``/``WORLD_Y1``/
``WORLD_Y2`` were scaled from their previous values to match this target
(X: -5135..7708 = 850 ft; Y: -6642..4085 = 710 ft), keeping Charles Street's
centerline at X=0. All other module geometry (bridge, dorms, Knott Hall,
terrain) is temporarily disabled via the master switches in ``constants.py``
(``BRIDGE_ENABLED``, ``WEST_CAMPUS_ENABLED``, ``KNOTT_TERRAIN_ENABLED``,
``KNOTT_HALL_ENABLED``, ``STREETS_DETAILS_ENABLED``, ``ENTITIES_ENABLED``)
while each area's own dimensions are re-derived against this new world size
from the ``ref/`` top-down views.

Terminology
-----------

Naming conventions
~~~~~~~~~~~~~~~~~~~

Constant names follow the pattern ``AREA_FEATURE_SUFFIX`` (e.g.
``BRIDGE_PILLAR_CAP_OVH`` = bridge pillar cap overhang). The full legend also
lives in the module docstring of :mod:`quake_loyola.constants`.

**Area prefixes:** ``BRIDGE_``, ``KNOTT_``, ``ENNIS_``, ``DORM_``,
``CHARLES_``, ``STREET_``, ``ROAD_``, ``WORLD_``, ``ARCH_``.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Suffix
     - Meaning
   * - ``X1``/``X2``, ``Y1``/``Y2``, ``Z1``/``Z2``
     - Min/max extent of a box along that axis (``1`` = lower coordinate,
       ``2`` = higher).
   * - ``DZ1``/``DZ2``
     - Bridge deck Z bottom / top.
   * - ``ZB``/``ZT``
     - Z bottom / Z top of a feature.
   * - ``CX``/``CY``
     - Centre X / centre Y of a feature.
   * - ``XS``/``YS``
     - A *list* (plural) of X or Y positions.
   * - ``N``/``S``/``E`` (e.g. ``NY``)
     - Compass direction (Quake: −Y = north, +Y = south, +X = east);
       ``NY`` = north-edge Y.
   * - ``H`` / ``HH``
     - Height / half-height.
   * - ``W`` / ``HW``
     - Width / half-width.
   * - ``T`` / ``R`` / ``D``
     - Thickness / radius / depth.
   * - ``OVH`` / ``EXTRA`` / ``PROUD``
     - Overhang / extra padding / how far a feature protrudes from its face.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Feature
     - Meaning
   * - ``PILLAR`` / ``BLK`` / ``SQ`` / ``PYR``
     - Pillar / block / square / pyramid.
   * - ``ENT`` / ``WIN`` / ``DIV`` / ``PLT`` / ``BR``
     - Entrance / window / road divider / platform / back road.
   * - ``DRIVEWAY_WS`` / ``_RD`` / ``_ES``
     - West-side / road / east-side sections of the Knott driveway
       (ordered west→east).
   * - ``BIY``
     - Knott building-interior Y (inner wall face).
   * - ``ORIG``
     - Original (pre-extension) reference, e.g. ``KNOTT_ORIG_CX``.
   * - ``KH``
     - Knott Hall (e.g. the ``FLOOR_KH`` texture).

Bridge structure
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Term
     - Description
   * - **Arch span**
     - The curved centre deck section over Charles Street, X ∈ [−525, +525]
       (``BRIDGE_ARCH_X[1]`` … ``BRIDGE_ARCH_X[2]``), a shallow parabola cresting
       at X=0. The two approach spans (±525 … ±1246) descend as straight rakes to
       the outer piers (ref/bridge08).
   * - **Flat approach**
     - Straight deck west of −1246, extending to the world wall at constant Z.
   * - **Deck**
     - The walkable surface. ``deck_top_z(x)`` = top face Z, ``deck_bot_z(x)`` =
       bottom face Z; slab thickness ``BRIDGE_DZ2 − BRIDGE_DZ1`` = 16 units.
   * - **Arch rise**
     - Height the deck crown is raised above the flat datum
       (``BRIDGE_ARCH_RISE = 100`` units at X=0, ``BRIDGE_ARCH_PIER_RISE = 82``
       at the centre piers).
   * - **Parapet**
     - Low stone wall along the deck's north/south edges,
       ``BRIDGE_PAR_H = 40`` units tall. Players can jump onto it.

Pier numbering
~~~~~~~~~~~~~~

The bridge has five piers, numbered west to east. This naming is used
consistently in the code (``PIER1_X`` … ``PIER5_X``).

.. list-table::
   :header-rows: 1
   :widths: 10 20 15 55

   * - Pier
     - Code constant
     - X position
     - Notes
   * - **Pier 1**
     - ``PIER1_X``
     - −1246
     - West abutment pier — embedded in the embankment hill; flanked by the
       abutment building.
   * - **Pier 2**
     - ``PIER2_X``
     - −525
     - Second pier west of centre.
   * - **Pier 3**
     - ``PIER3_X``
     - 525
     - Centre-east pier — anchors the Ennis Drive entrance pillars.
   * - **Pier 4**
     - ``PIER4_X``
     - 1246
     - West KH pier — marks the eastern end of the main arch span
       (``BRIDGE_X2 = KNOTT_PIER_X``).
   * - **Pier 5**
     - ``PIER5_X``
     - 2206
     - East KH / NE pier — easternmost pier, aligned with the Knott Hall east
       face; the bridge deck angles south from here. The accessible walkway
       runs along its west face.

Pier / pillar components
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Term
     - Description
   * - **Pier**
     - The full stone support structure rising from the ground to the bridge
       deck. Consists of an arch wall base, pillar post, and cap.
   * - **Arch wall**
     - The lower stone mass of the pier (ground to deck underside). Contains
       the arch opening; built from ``arch_wall()``.
   * - **Arch opening**
     - The semicircular hollow in the arch wall. Inner radius ``rin`` sets the
       opening size; outer radius ``rout`` sets the stone ring thickness.
   * - **Arch ring**
     - The annular stone band surrounding the arch opening, composed of
       trapezoidal voussoir segments.
   * - **Voussoir**
     - One wedge-shaped brush segment of the arch ring, generated by
       ``arch_seg()``.
   * - **Stilt height**
     - Straight vertical section below the arch spring point (``sprz``). Raises
       the arch opening above ground on tall piers.
   * - **Arch crown**
     - The topmost point of the arch ring (``sprz + rout``). Should be flush
       with the deck underside (``deck_bot_z``).
   * - **Cap**
     - Solid box filling the area above the arch inner crown and below the deck
       underside, bridging the gap in the centre of the opening.
   * - **Pillar post**
     - Stone column above the deck surface, extending ``BRIDGE_PILLAR_EXTRA``
       units above the parapet.
   * - **Overhang**
     - How far the pier stone extends beyond the bridge's N/S edges
        (``BRIDGE_PILLAR_OVERHANG = 16`` units).

Knott Hall
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Term
     - Description
   * - **Mullion**
     - Vertical protruding cement post flanking a window opening on Knott
       Hall's north facade. Mullions sit just outside each window opening (not
       inside) so players can pass through. Width = 12 units, protrusion = 12
       units.
   * - **Recessed window**
     - Window set back in the NW or NE indented corner of the north facade.
       Each opening is 48 units wide, framed by mullions on the outer edges.
   * - **Indentation**
     - 80-unit corner notch cut from the NW and NE corners of the north face,
       creating a recessed alcove with its own back wall and window.
   * - **Walkway bent**
     - The cement support structure under the bridge approach in front of Knott
       Hall. Consists of a horizontal cap beam running along the south bridge
       edge (Pier 4 → Pier 5) with 5 vertical drop piers reaching to ground
       level. Only present when ``KNOTT_WALKWAY_ENABLED = True``.
   * - **Accessible walkway**
     - The small N-S cement path running along the west face of Pier 5, from
       the Knott Hall north face up to the bridge south edge. A short E-W ramp
       at the north end wraps around Pier 5 and connects to the back-road west
       sidewalk. Generated alongside the main walkway when
       ``KNOTT_WALKWAY_ENABLED = True``.

Street / road
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Term
     - Description
   * - **Verge**
     - The strip of land between the road edge and the sidewalk. In the real
       world this is often grass; here it is a raised ground-textured slab flush
       with the sidewalk height.
   * - **Teleport arch**
     - Decorative stone arch portal at each end of the bridge with a trigger
       field. West arch teleports to east; east to west.
   * - **Post**
     - Straight vertical stone column on each side of a teleport arch opening.
   * - **Lintel**
     - The horizontal beam spanning the top of an opening (door, window, or
       portal), resting on the two vertical posts.

Map layout
----------

.. code-block:: text

   [West Campus] ──── bridge span ──── [Knott Hall]
                 ↑arch              arch↑
         5 stone pillars supporting the span

- **Bridge span**: arched deck over Charles Street, crown at X=0; deck top
  ranges Z 240 (flat approach) → 384 (crown).
- **Entry arch gates**: Semicircular stone arch portals at each end with
  teleport fields.
- **Stone pillars**: 5 supporting piers with narrow arched openings.
- **Knott Hall**: A 5-story tower on the south campus, featuring
  vertical "fins" on its north facade.
- **Charles Street**: Road surface running N-S under the bridge.
- **Sky**: ``sky1`` ceiling, sealed outer box.

Spatial hierarchy
~~~~~~~~~~~~~~~~~

.. code-block:: text

   World shell
   ├── Charles Street (N–S road, runs full Y extent)
   │   ├── West sidewalk & curb
   │   ├── East sidewalk & curb
   │   ├── South arch teleport gate  ──→ bridge deck centre
   │   └── North arch teleport gate  ──→ bridge deck centre
   ├── Ennis Road (E–W road, T-junction north of bridge)
   │   └── Ennis Drive entrance pillars & boundary wall
   ├── West campus buildings
   │   ├── Abutment building (3-floor brick, west end of bridge)
   │   ├── North building (gabled, north side of Ennis Road)
   │   ├── South building 1 & South building 2
   │   └── Iron fence (east face of west buildings)
   ├── Embankment (sloped ground ramp from road level up to bridge deck Z)
   ├── Bridge (E–W span over Charles Street, deck top Z 240 → 384 at crown)
   │   ├── Arch deck (span segments BRIDGE_X1 → BRIDGE_X2, parabolic rise)
   │   ├── Parapet walls (N & S edges, full span)
   │   ├── Stone piers ×5 (at BRIDGE_ARCH_X[] positions)
   │   │   └── each: arch wall → voussoir ring → cap → pillar post
   │   ├── West teleport arch (X = BRIDGE_X1 / west world wall)
   │   └── East teleport arch (X = east world wall)
   ├── Walkway (flat slab, bridge east end → Knott Hall 2nd floor)
   │   ├── Walkway bent (cap beam + 5 drop piers)
   │   └── Accessible walkway (N-S path along Pier 5 + E-W ramp)
   ├── Knott Hall (south campus tower, X 1206–2238)
   │   ├── Outer walls (5 floors + roof)
   │   ├── Interior floors, hallway & rooms
   │   ├── Elevator (func_plat) inside lift shaft
   │   ├── Entrance staircase & railings (north face, ground level)
   │   └── Fascia lettering ("LOYOLA UNIVERSITY MARYLAND")
   └── Campus lamp posts (along Charles Street)

Teleport connections
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - Trigger location
     - ``targetname``
     - Destination
   * - West arch — deck level
     - ``dest_east``
     - North building rooftop (west campus)
   * - West arch — ground level
     - ``dest_east``
     - North building rooftop (west campus)
   * - East arch — deck level
     - ``dest_west``
     - Knott Hall rooftop
   * - East arch — ground level
     - ``dest_east_deck``
     - Flat deck, just west of east arch
   * - Abutment arch (Y = 0, deck)
     - ``dest_abutment_deck``
     - Bridge deck above abutment pier
   * - Charles St south arch gate
     - ``dest_south_dorm_roof``
     - South dorm A-frame ridge
   * - Charles St north arch gate
     - ``dest_dorm_roof``
     - North dorm A-frame ridge
   * - Ennis east arch (east world wall)
     - ``dest_kh_drive_south``
     - Knott Hall rooftop
   * - Knott driveway arch
     - ``dest_ennis_east``
     - Knott Hall rooftop

Structural dependencies
~~~~~~~~~~~~~~~~~~~~~~~

These constants are "load-bearing" across multiple objects; changing one
cascades.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Constant
     - Objects affected
   * - ``CHARLES_CRN_R``, ``CHARLES_CRN_SEGS``
     - Charles/Ennis and Knott back-road corner radii / arc tessellation.
   * - ``CHARLES_RAMP_W``
     - Charles Street sidewalk ramp width; affects the east/west curb ramps.
   * - ``CHARLES_WALK_H``, ``CHARLES_WALK_W``
     - Charles Street sidewalk height/width; cascade into Ennis curbs, the
       Ennis wall setback, fence placement, Knott Hall terrain ramps, and
       the back-road sidewalks.
   * - ``CHARLES_Y1``, ``CHARLES_Y2``
     - Charles Street south/north extents; anchor road surface, sidewalk/fence
       spans, embankment ends, and north/south street arch teleports.
   * - ``KNOTT_FLOOR_H``
     - All Knott Hall floor Z levels, walkway alignment, spawn heights, weapon
       placement.
   * - ``KNOTT_PIER_X``
     - Fixed Knott Hall-side bridge pier; anchors ``BRIDGE_X2``,
       ``BRIDGE_ARCH_X[3]``, and east lamp placement.
   * - ``KNOTT_X1/X2``, ``KNOTT_Y1/Y2``
     - Knott Hall footprint; moving it requires updating walkway, back road,
       hill terrain, east-arch teleport destination.
   * - ``BRIDGE_ARCH_RISE``
     - Deck crown height; shifts pier heights per X, deck spawn Z,
       parapet-top Z.
   * - ``BRIDGE_ARCH_X[]``
     - Pier X positions; ``BRIDGE_ARCH_X[0]`` pins the abutment building X.
   * - ``BRIDGE_DZ1``, ``BRIDGE_DZ2``
     - Flat deck Z, all pier heights, teleport arch spring height, walkway Z.
   * - ``BRIDGE_PILLAR_HW``
     - Pier post half-width; affects arch wall extents, cap size, overhang,
       and brick wall X positions.
   * - ``BRIDGE_Y1``, ``BRIDGE_Y2``
     - Parapet N/S position, teleport arch Y opening size, walkway Y start,
       Ennis Road reference Y.
   * - ``DORM_FLOORS``
     - Dormitory floor count; shared by all west-campus residence buildings.
   * - ``WORLD_X1/X2``
     - Derives ``BRIDGE_X1``; resizing the world changes the arch span and all
       wall-relative positions.

Textures
--------

All textures come from the community WADs. Download ``quake101.wad``,
``ad.wad``, and ``makkon_building.wad`` and place them alongside the ``.map``
file before compiling (``just setup`` downloads the first two automatically).
Names below are the ``Textures.*`` constants in :mod:`quake_loyola.constants`.

.. list-table::
   :header-rows: 1
   :widths: 45 30 25

   * - Surface
     - ``Textures`` field
     - Texture name
   * - Bridge deck, stone, cement
     - ``FLOOR`` / ``STONE`` / ``CEMENT``
     - ``sfloor3_2``
   * - Pillars, arches, walls
     - ``PILLAR`` / ``WALL``
     - ``city2_7``
   * - Building facades
     - ``BUILDING``
     - ``city2_1``
   * - Brickwork
     - ``BRICK``
     - ``bricka2_1``
   * - Ground / embankment
     - ``GROUND``
     - ``ground1_1``
   * - Road surface
     - ``ROAD``
     - ``azfloor1_1``
   * - Roofs
     - ``ROOF``
     - ``roofkell1``
   * - Sky surfaces
     - ``SKY``
     - ``sky1``

Entities
--------

.. list-table::
   :header-rows: 1
   :widths: 35 10 55

   * - Entity
     - Qty
     - Location
   * - ``info_player_deathmatch``
     - 22
     - Scattered across bridge, campus, and hall.
   * - ``weapon_rocketlauncher``
     - 19
     - Bridge deck, Knott Hall floors, and campus.
   * - ``item_health``
     - 14
     - Bridge deck, hall entrance, and hall floors.
   * - ``light``
     - ~480
     - Pillar caps, hall interior/exterior, road, and teleport arches.
   * - ``func_plat``
     - 1
     - Lift shaft inside Knott Hall.

Loading and editing
-------------------

Loading in Quake
~~~~~~~~~~~~~~~~

.. code-block:: text

   quake -game id1 +map loyola

Or from the in-game console:

.. code-block:: text

   map loyola

Manual compilation (without just)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download **ericw-tools v0.18.1** from
`github.com/ericwa/ericw-tools/releases <https://github.com/ericwa/ericw-tools/releases>`_
and place ``quake101.wad``, ``ad.wad``, and ``makkon_building.wad`` alongside
the ``.map`` file, then:

.. code-block:: bash

   qbsp loyola.map
   vis loyola.bsp
   light loyola.bsp

The compiled ``loyola.bsp`` goes in your Quake ``id1/maps/`` directory.

TrenchBroom
~~~~~~~~~~~

TrenchBroom is pre-configured for this project. The following files are
written to TrenchBroom's app-support folder and are **not** committed to the
repo (they reference absolute paths on your machine):

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Location
   * - Game path
     - ``~/Library/Application Support/TrenchBroom/Preferences.json``
   * - Compile profiles
     - ``~/Library/Application Support/TrenchBroom/games/Quake/CompilationProfiles.cfg``
   * - Engine profile
     - ``~/Library/Application Support/TrenchBroom/games/Quake/GameEngineProfiles.cfg``

Set the game path in ``Preferences.json``:

.. code-block:: json

   {
       "Games/Quake/Path": "/Applications"
   }

Both compile profiles use ``${MAP_DIR_PATH}`` as the working directory so
ericw-tools picks up ``quake101.wad`` from the same folder as the ``.map``
file.  Tool paths point to
``~/Downloads/ericw-tools-v0.18.1-Darwin/bin/``.

**Workflow**: open ``loyola.map`` → edit → **Run → Compile Map** → **Run →
Launch Engine** (vkQuake).
