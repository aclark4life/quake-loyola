QuakeC Integration
==================

This page documents the work done to integrate custom QuakeC (QC) into the
map, and why it was put on hold, so it can be resumed later.

Goal
----

The Charles Street pedestrian bridge is modelled as a ``func_train`` entity
that follows a path: west-ramp → bridge-deck → east-ramp.  At each corner
waypoint the train changes direction.  The goal was to rotate the *player's
view* to match the new heading whenever they are riding the platform, giving
a smooth "you are on a turning vehicle" sensation.

What was accomplished
---------------------

A complete QuakeC compile pipeline was set up and the custom ``progs.dat``
was confirmed to load in vkQuake 1.34.1.

Toolchain
~~~~~~~~~

* **gmqcc** — built from source at ``.tools/gmqcc/gmqcc``.
  Used with ``-std=fteqcc`` to compile the QC sources.
* **quake-tools qcc** — built from `Henrique194/quake-tools`_ (a modern C++
  port of the original id Software ``qcc``) at
  ``.tools/qcc-tools/build/qcc/qcc``.  Used to generate ``qc/progdefs.h``
  for CRC analysis.  Requires SDL2 (``brew install sdl2``).

.. _Henrique194/quake-tools: https://github.com/Henrique194/quake-tools

QC source base
~~~~~~~~~~~~~~

The ``qc/`` directory contains the original Quake QW (QuakeWorld) QC sources
from ``id-Software/Quake``, adapted to NQ (NetQuake / singleplayer).  The
following changes were required to make the ``progs.dat`` load in vkQuake:

**defs.qc — global variables (``globalvars_t``)**

* Removed ``entity newmis`` from the system-globals section (QW-only).
* Added ``float deathmatch``, ``float coop``, ``float teamplay`` to the
  system-globals section (present in NQ stock, absent from QW source).
* Removed duplicate ``deathmatch`` / ``teamplay`` from the non-system
  globals section (they had been defined twice after the fixes above).
* Fixed the ``rj`` global from a constant to a mutable ``float``.

**defs.qc — entity fields (``entvars_t``)**

* Removed ``.float lastruntime`` (QW-only field).
* Added ``.vector punchangle`` after ``.vector avelocity`` (NQ field).
* Added ``.float idealpitch`` after ``.float v_angle`` block (NQ field).
* Fixed ``droptofloor`` signature from ``float(entity e)`` to ``float()``.

**PROGHEADER_CRC**

vkQuake checks the ``crc`` field in the ``progs.dat`` header against the
hardcoded constant ``PROGHEADER_CRC = 5927``.  This CRC is computed by the
compiler from the text of the generated ``progdefs.h`` file (which contains
``globalvars_t`` and ``entvars_t`` struct definitions).  After the defs.qc
fixes above, gmqcc produces exactly CRC **5927** and the engine accepts the
file.

The CRC algorithm is CRC-16/CCITT: polynomial 0x1021, init 0xFFFF,
table-driven left-shift, no final XOR.

Deployment
~~~~~~~~~~

Because ``/Applications/id1/`` only has ``pak0.pak`` and ``pak1.pak``, a
custom ``pak2.pak`` is built by ``scripts/make_pak3.py`` and dropped into
``/Applications/id1/``.  Quake scans PAK files in numeric order, stopping at
the first gap, and higher-numbered PAKs win; so ``pak2.pak`` overrides both
stock PAK files.

The ``justfile`` recipes::

    just compile-qc    # runs gmqcc → writes progs.dat
    just deploy-qc     # wraps progs.dat in pak2.pak → /Applications/id1/pak2.pak

Train rotation feature
~~~~~~~~~~~~~~~~~~~~~~

``qc/plats.qc`` was modified:

* ``train_next()`` — computes the platform's new heading with
  ``vectoyaw(delta)`` and stores it in ``self.train_yaw``.
* ``train_wait()`` — calls ``train_rotate_riders()`` at each waypoint arrival.
* ``train_rotate_riders()`` — iterates all ``classname == "player"`` entities
  with ``find()``, checks Z-proximity to the platform, and sets
  ``rider.v_angle_y``, ``rider.angles_y``, ``rider.fixangle = TRUE``.

The rotation code compiles and the ``progs.dat`` loads, but the in-game view
rotation was not working as expected during the test session.

Where it was left
-----------------

* ``pak2.pak`` was **removed** from ``/Applications/id1/`` — the game runs
  with the stock ``progs.dat`` again.
* All QC source changes are committed in ``qc/`` and compile to CRC 5927.
* The custom ``.field .float train_yaw`` is declared in ``defs.qc`` but is
  **outside** ``end_sys_fields`` (in the non-system section) so it does not
  affect the CRC.

Resuming this work
------------------

**Finding a clean NQ QC base**

Two candidate sources were tried and rejected:

* **id-Software/quake-rerelease-qc** — This is the official rerelease (2021)
  NQ source, but it targets the enhanced rerelease engine and uses many
  extensions that gmqcc rejects: ``#0:ex_bprint`` style builtins,
  ``switch/case``, bot/debug-draw builtins, ``finaleFinished``, etc.

* **lavenderdotpet/LibreQuake** — A clean-room reimplementation that is
  structurally sound but also uses ``__NULL__``, ``#ifdef``/``#ifndef``,
  ``deathmatch_supermode()``, ``LOC_*`` string constants, and LQ-specific
  cutscene code — all incompatible with gmqcc in ``-std=fteqcc`` mode.

The id Software GPL release (``id-Software/Quake``) contains only the QW
and WinQuake C source; there is **no original id1 QC source** in that repo.
The original ``id1/`` QC was never published as a standalone GPL release —
it was distributed only inside the game's ``PAK0.PAK``.

**Practical conclusion:** The QW QC source (``id-Software/Quake qw-qc/``)
with targeted NQ compatibility fixes is the most viable base for gmqcc.
It compiles cleanly at CRC=5927 after the fixes documented above.
The missing pieces (``PlayerJump`` velocity, ``button2`` handling) were
simple one-line additions; no structural rewrite was needed.

**Resuming this work**

1. Investigate why ``train_rotate_riders()`` does not rotate the player view.
   Likely candidates:

   * The proximity check (Z delta) may be too tight — the player may not be
     detected as "on" the platform.
   * ``fixangle`` may need to be set every frame, not just at waypoint
     arrival.  Consider adding a ``think`` function on the player or polling
     in ``PlayerPreThink``.
   * The ``v_angle`` set in QC may be overridden by client-side mouse input
     before it takes effect.  A delta-rotation approach (rotate by the *yaw
     change* rather than setting an absolute angle) may be more robust.

2. Re-deploy::

       just compile-qc && just deploy-qc

3. When done, commit and push with::

       git commit --author="Jeffrey 'Alex' Clark <aclark@aclark.net>" ...

Key files
---------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Purpose
   * - ``qc/defs.qc``
     - Global / field declarations; must match NQ ``progdefs.h`` exactly for CRC
   * - ``qc/plats.qc``
     - ``func_train`` logic; contains ``train_rotate_riders()``
   * - ``qc/progs.src``
     - Compiler manifest; output path ``../progs.dat``
   * - ``scripts/make_pak3.py``
     - Builds a Quake PAK file from loose files
   * - ``justfile``
     - ``compile-qc`` and ``deploy-qc`` recipes
   * - ``.tools/gmqcc/gmqcc``
     - Compiler binary (built from source)
   * - ``.tools/qcc-tools/build/qcc/qcc``
     - Original-qcc port (used for CRC analysis / progdefs.h generation)
