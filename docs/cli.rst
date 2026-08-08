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

The CLI has three layers, narrowest first: the shortcut commands for the
handful of settings worth changing day to day, ``ql conf`` for the full
surface (including the ~35 module/light flags), and ``ql gen``/``ql build``
to run the pipeline.

Shortcut commands
~~~~~~~~~~~~~~~~~

``ql sky``, ``ql fog``, ``ql light``, and ``ql vis`` each set a single
``[build]`` setting. Run one with no argument to print the current value
and every valid one:

.. code-block:: bash

   ql sky                # show the current sky + every sky texture in the WADs
   ql sky sky_z1         # set the world sky texture
   ql fog high           # off/low/med/high, a number like 0.05, or "default"
   ql light dusk         # time-of-day lighting preset
   ql vis full           # "fast" (default) or "full" vis pass

``sky`` is a plain WAD2 texture name, not a named preset. It is validated
against the textures actually present in the project's WADs (see
:mod:`quake_loyola.wads`), so a typo is caught at ``ql sky`` time rather
than surfacing as a missing-texture warning during compilation. Names must
start with ``sky`` since qbsp only compiles ``sky*`` textures as sky.

``fog`` accepts ``default``, meaning "use whatever fog the current
``lighting_preset`` defines"; any other value overrides it. Note that
``default`` and ``off`` are different — ``off`` disables fog outright.

``light`` remains a named preset because it sets six correlated worldspawn
fields at once (sun color and angle, ambient level, fog color).

.. note::

   ``sky_preset`` (a two-entry ``day``/``night`` alias table over a texture
   name) was replaced by ``sky``. An existing ``ql.toml`` using it keeps
   working — the value is migrated on load, with a warning — but new
   configuration should set ``sky`` directly.

``ql gen``
~~~~~~~~~~

Write ``loyola.map`` from the current config-driven flag settings — same as
``just generate``, but config-aware.

``ql build``
~~~~~~~~~~~~

Generate + compile the map (``qbsp`` → ``vis`` → ``light``) and deploy the
result, honoring the ``vis_mode`` and ``light_extra`` build settings.

.. code-block:: bash

   ql build                  # generate, compile, and deploy
   ql build --no-deploy      # skip copying the .bsp/.lit into the Quake maps dir
   ql build --no-gen         # compile the existing loyola.map as-is
   ql build --vis full       # override vis_mode for this run only
   ql build --extra          # override light_extra for this run only

``just compile`` and ``just compile-fast`` call ``ql build --vis full``
/ ``--vis fast`` (with ``--no-gen --no-deploy``), so there is a single
implementation of the pipeline and the recipe name always wins over
``ql.toml``'s ``vis_mode``.

``ql conf show``
~~~~~~~~~~~~~~~~

List the build settings, their effective values, defaults, and valid values
(overridden values are marked with ``*``). Pass ``--all``/``-a`` to also list
the module/light flags, which are hidden by default to keep the output
readable.

``ql conf get NAME``
~~~~~~~~~~~~~~~~~~~~

Print the effective value of a single flag or build setting.

``ql conf set``
~~~~~~~~~~~~~~~

Set one or more flags/build settings, persisted to ``ql.toml``. Accepts
either the ``NAME VALUE`` form, or one or more ``NAME=VALUE`` pairs:

.. code-block:: bash

   ql conf set KNOTT_ENABLED true          # flip a module/light flag on or off
   ql conf set knott_enabled true          # names are case-insensitive
   ql conf set light_extra true            # light -extra (2x2 supersampling)
   ql conf set sky sky_z1                  # same as `ql sky sky_z1`

   # Set several settings in one command:
   ql conf set vis_mode=full lighting_preset=dusk fog_density=high

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

.. automodule:: quake_loyola.build_presets
   :members:
   :undoc-members:

.. automodule:: quake_loyola.wads
   :members:
   :undoc-members:
