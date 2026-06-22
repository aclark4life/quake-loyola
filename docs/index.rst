quake-loyola
============

A procedurally-generated Quake 1 deathmatch map inspired by the pedestrian
bridge over Charles Street at Loyola University Maryland.

The entire map is authored in Python — no manual brush editing required.
Running ``python3 generate_map.py`` (or ``just generate``) writes
``loyola.map``, which is then compiled with the ericw-tools pipeline
(``qbsp → vis → light``) to produce a playable ``.bsp``.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   overview
   reference
   api
