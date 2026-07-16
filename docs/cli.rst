``ql`` CLI
==========

``ql`` is a `Typer <https://typer.tiangolo.com/>`_ console-script (installed
via ``pip install -e .``, see ``[project.scripts]`` in ``pyproject.toml``)
for configuring and running quake-loyola's build without editing
``ql.toml`` by hand. It's implemented in
:mod:`quake_loyola.cli`, backed by :mod:`quake_loyola.config`.

.. code-block:: bash

   pip install -e .       # installs the `ql` command + typer into your environment
   ql conf show

``just venv`` already runs ``pip install -e .`` for you, so ``.venv/bin/ql``
is ready to use after ``just test``/``just venv``.

Commands
--------

``ql gen``
~~~~~~~~~~

Write ``loyola.map`` from the current config-driven flag settings — same as
``just generate``, but config-aware.

``ql build``
~~~~~~~~~~~~

Generate + compile the map (``qbsp`` → ``vis`` → ``light``) and deploy the
result, honoring the ``[build]`` settings below (``vis_mode``,
``light_extra``) — the same pipeline as ``just compile``/``just
compile-fast``, but configurable without editing the ``justfile``.

.. code-block:: bash

   ql build                  # generate, compile, and deploy
   ql build --no-deploy      # skip copying the .bsp/.lit into the Quake maps dir

``ql conf show``
~~~~~~~~~~~~~~~~

List every flag and build setting, its effective value, and its default
(overridden values are marked with ``*``).

``ql conf get NAME``
~~~~~~~~~~~~~~~~~~~~

Print the effective value of a single flag or build setting.

``ql conf set``
~~~~~~~~~~~~~~~

Set one or more flags/build settings, persisted to ``ql.toml``. Accepts
either the legacy ``NAME VALUE`` form, or one or more ``NAME=VALUE`` pairs:

.. code-block:: bash

   ql conf set KNOTT_ENABLED true          # flip a module/light flag on or off
   ql conf set bridge_enabled true         # names are case-insensitive
   ql conf set vis_mode full               # "fast" (default) or "full" vis pass
   ql conf set light_extra true            # light -extra (2x2 supersampling)
   ql conf set lighting_preset dusk        # dawn/midday/golden_hour/dusk/overcast/night/bright/afternoon
   ql conf set fog_density high            # "default" (preset's own), off/low/med/high, or a custom float

   # Set several settings in one command:
   ql conf set vis_mode=full lighting_preset=dusk fog_density=high

``BRIDGE_ENABLED`` and ``WEST_CAMPUS_ENABLED`` are convenience master
switches — setting either ``true`` forces every one of their
``<AREA>_ENABLED_<section>`` sub-flags on too, overriding individual
settings.

``ql conf reset``
~~~~~~~~~~~~~~~~~

Delete ``ql.toml``, reverting every flag/setting to its default. Pass
``--yes``/``-y`` to skip the confirmation prompt.

``ql conf path``
~~~~~~~~~~~~~~~~

Print the path to ``ql.toml`` (whether or not it exists yet).

Reference
---------

.. automodule:: quake_loyola.cli
   :members:
   :undoc-members:

.. automodule:: quake_loyola.config
   :members:
   :undoc-members:
