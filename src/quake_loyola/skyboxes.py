"""Environment skyboxes installed in the Quake directory.

A skybox is six ``.tga`` images (``<name>_bk``, ``_dn``, ``_ft``, ``_lf``,
``_rt``, ``_up``) living in ``gfx/env/`` inside the Quake directory, e.g. the
Makkon skybox pack. Setting the ``skybox`` build setting writes the name into
the ``sky`` *worldspawn key*, which modern engines (vkQuake, QuakeSpasm,
Ironwail, ...) honour in place of drawing the ``sky*`` texture on the map's
sky brushes.

Beware the collision of names: the ``sky`` *build setting* is a WAD texture,
but the ``sky`` *worldspawn key* is a skybox. That is the engines' convention
(``Sky_NewMap`` accepts ``sky``, ``skyname`` or ``qlsky``, all of them skybox
names); no engine has ever read a texture name from worldspawn, and qbsp does
not read the key at all. So the key is written only when a skybox is set --
otherwise the engine would search ``gfx/env`` for a texture name and fail.

Unlike the WAD textures the skybox images are *not* part of this repo — they
are hundreds of megabytes of art and belong in the engine's game directory —
so this module only discovers what is already installed. It is deliberately
dependency-free (no ``constants`` import) for the same reason
:mod:`quake_loyola.wads` is: :mod:`quake_loyola.build_presets` validates the
``skybox`` setting without initialising the whole ``constants`` package.

The sky *texture* still matters even with a skybox set: qbsp needs ``sky*``
faces to mark the map's sky, and TrenchBroom (which does not render skyboxes
at all) shows that texture in the editor. The skybox only changes what the
engine draws through those faces at run time.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

#: Default Quake directory, matching the ``quake_dir`` in the justfile and the
#: deploy target in :mod:`quake_loyola.cli`. Override with ``$QUAKE_DIR``.
DEFAULT_QUAKE_DIR = Path("/Applications/id1")

#: Skybox images live here, relative to the Quake directory.
ENV_SUBDIR = Path("gfx/env")

#: Suffixes an engine expects, one image per cube face.
SKYBOX_FACE_SUFFIXES: tuple[str, ...] = ("bk", "dn", "ft", "lf", "rt", "up")

#: Engines accept either extension; ``.tga`` is what the Makkon pack ships.
SKYBOX_EXTENSIONS: tuple[str, ...] = (".tga", ".png", ".pcx")

#: Skybox names are used verbatim as a filename stem, so keep them boring.
_SKYBOX_NAME_RE = re.compile(r"[A-Za-z0-9_-]{1,63}")


def quake_dir() -> Path:
    """Return the Quake directory, honouring a ``$QUAKE_DIR`` override."""
    override = os.environ.get("QUAKE_DIR")
    return Path(override) if override else DEFAULT_QUAKE_DIR


def env_dir() -> Path:
    """Return the directory skybox images are installed into."""
    return quake_dir() / ENV_SUBDIR


def skybox_prefixes(directory: Path | None = None) -> set[str]:
    """Return the filename prefix of every skybox fully installed here.

    The prefix is what the engine concatenates the face suffix onto, so it
    keeps whatever separator the pack uses — ``mak_sunset1_`` for the usual
    ``mak_sunset1_rt.tga`` layout, ``space1`` for a bare ``space1rt.tga``
    one. That distinction is the whole point of this function; see
    :func:`skybox_worldspawn_value`.

    A skybox counts as installed only when all six faces are present, so a
    half-copied pack can't be selected and then render as garbage in game.
    An empty set means nothing is installed *or* the directory is missing;
    callers should treat that as "can't validate", not "nothing is valid".
    """
    directory = env_dir() if directory is None else directory
    try:
        files = {entry.name.lower() for entry in directory.iterdir() if entry.is_file()}
    except OSError:
        return set()

    candidates: set[str] = set()
    for name in files:
        stem, _, extension = name.rpartition(".")
        if f".{extension}" not in SKYBOX_EXTENSIONS:
            continue
        for suffix in SKYBOX_FACE_SUFFIXES:
            if stem.endswith(suffix) and len(stem) > len(suffix):
                candidates.add(stem[: -len(suffix)])

    return {
        prefix
        for prefix in candidates
        if all(
            any(
                f"{prefix}{suffix}{extension}" in files
                for extension in SKYBOX_EXTENSIONS
            )
            for suffix in SKYBOX_FACE_SUFFIXES
        )
    }


def skybox_names(directory: Path | None = None) -> set[str]:
    """Return the human-facing name of every fully installed skybox.

    This is :func:`skybox_prefixes` with the separator trimmed, so the
    ``skybox`` build setting reads as ``mak_sunset1`` rather than the
    engine-level ``mak_sunset1_``.
    """
    return {prefix.rstrip("_") for prefix in skybox_prefixes(directory)}


def skybox_worldspawn_value(name: str, directory: Path | None = None) -> str:
    """Return the ``sky`` worldspawn value that loads skybox ``name``.

    Engines build each face path as ``gfx/env/`` + this value + a bare
    ``rt``/``bk``/``lf``/``ft``/``up``/``dn`` — there is **no** separator in
    the format string. So the value has to carry the pack's own separator,
    and ``mak_sunset1`` must go out as ``mak_sunset1_``; without the
    underscore the engine looks for ``gfx/env/mak_sunset1rt.tga``, fails to
    find it, and silently falls back to the scrolling sky texture.

    The separator is read back off the installed files rather than assumed.
    When the skybox isn't installed here (a build machine, say) fall back to
    the ``name_rt`` convention every modern pack uses.
    """
    if not name:
        return ""
    for prefix in skybox_prefixes(directory):
        if prefix.rstrip("_") == name.lower():
            return prefix
    return name if name.endswith("_") else f"{name}_"


def is_valid_skybox_name(value: str) -> bool:
    """Return True if ``value`` is syntactically usable as a skybox name."""
    return bool(_SKYBOX_NAME_RE.fullmatch(value))
