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
``[build]`` surface, and ``ql gen``/``ql build`` to run the pipeline.

Shortcut commands
~~~~~~~~~~~~~~~~~

``ql sky``, ``ql skybox``, ``ql fog``, ``ql light``, and ``ql vis`` each set
a single ``[build]`` setting. Run one with no argument to print the current
value and every valid one:

.. code-block:: bash

   ql sky                # show the current sky + every sky texture in the WADs
   ql sky sky_z1         # set the world sky texture
   ql skybox mak_sunset1 # set the environment skybox ("none" to unset)
   ql fog high           # off/low/med/high, a number like 0.05, or "default"
   ql light dusk         # time-of-day lighting preset
   ql vis full           # "fast" (default) or "full" vis pass

``sky`` is a plain WAD2 texture name, not a named preset. It is validated
against the textures actually present in the project's WADs (see
:mod:`quake_loyola.wads`), so a typo is caught at ``ql sky`` time rather
than surfacing as a missing-texture warning during compilation. Names must
start with ``sky`` since qbsp only compiles ``sky*`` textures as sky.

``skybox`` is a different thing that stacks on top of ``sky`` rather than
replacing it. It names six images (``<name>_bk``, ``_dn``, ``_ft``, ``_lf``,
``_rt``, ``_up``) in the engine's ``gfx/env`` directory, and is written out
as the ``sky`` *worldspawn key*; engines draw that cubemap through the map's
sky faces at run time. The ``sky`` *texture* is still required, because its
``sky`` prefix is the only thing that tells qbsp which faces are sky at all.

.. warning::

   The two meanings of "sky" are easy to confuse. The ``sky`` **build
   setting** is a WAD texture name; the ``sky`` **worldspawn key** is a
   skybox name. That is the engines' convention (see ``Sky_NewMap`` in
   QuakeSpasm-derived ports, which accept ``sky``, ``skyname`` and
   ``qlsky``) — they have never read a texture name from worldspawn, and
   qbsp/vis/light never read the key at all. Writing the texture name there
   just makes the engine look for a ``gfx/env`` file that cannot exist, so
   the key is omitted entirely when no skybox is set.

.. note::

   The value written to worldspawn keeps the pack's trailing separator ---
   ``mak_sunset1`` goes out as ``mak_sunset1_``. Engines assemble each face
   path as ``gfx/env/%s%s`` against a bare ``rt``/``bk``/``lf``/``ft``/
   ``up``/``dn``, so without the underscore they look for
   ``gfx/env/mak_sunset1rt.tga``, fail, and fall back to the scrolling sky
   with no visible error. :func:`quake_loyola.skyboxes.skybox_worldspawn_value`
   reads the separator back off the installed files rather than assuming it.

The images are art assets rather than code and are not tracked in this repo
— install a pack into ``gfx/env`` under your Quake directory (``$QUAKE_DIR``,
default ``/Applications/id1``). :mod:`quake_loyola.skyboxes` discovers what
is installed there, and only a name whose six faces are *all* present is
accepted, so a half-copied pack can't be selected. Set it to ``""`` (or pass
``none``) to fall back to the plain sky texture.

.. note::

   A skybox is a run-time engine feature, so TrenchBroom does not render it.
   The editor keeps showing the flat ``sky`` texture on those faces.

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

Write ``loyola.map`` using the current build settings — same as
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

List every build setting, its effective value, default, and valid values
(overridden values are marked with ``*``).

``ql conf get NAME``
~~~~~~~~~~~~~~~~~~~~

Print the effective value of a single build setting.

``ql conf set``
~~~~~~~~~~~~~~~

Set one or more build settings, persisted to ``ql.toml``. Accepts either the
``NAME VALUE`` form, or one or more ``NAME=VALUE`` pairs:

.. code-block:: bash

   ql conf set vis_mode full               # "fast" or "full"
   ql conf set VIS_MODE full               # names are case-insensitive
   ql conf set light_extra true            # light -extra (2x2 supersampling)
   ql conf set sky sky_z1                  # same as `ql sky sky_z1`

   # Set several settings in one command:
   ql conf set vis_mode=full lighting_preset=dusk fog_density=high

``ql conf reset``
~~~~~~~~~~~~~~~~~

Delete ``ql.toml``, reverting every build setting to its default. Pass
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

.. automodule:: quake_loyola.skyboxes
   :members:
   :undoc-members:
