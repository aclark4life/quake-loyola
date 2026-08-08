"""The project's texture WADs, and a minimal WAD2 directory reader.

This module is deliberately dependency-free (no ``constants`` import) so
:mod:`quake_loyola.build_presets` can use it to validate the ``sky`` build
setting against the textures that are actually available, without pulling in
the whole ``constants`` package for a config-only CLI command.

:data:`WAD_FILES` is the single source of truth for the WAD list: it is
joined into the worldspawn ``wad`` key by ``constants.derived`` and scanned
for sky textures by :func:`sky_texture_names`.
"""

from __future__ import annotations

import struct
from pathlib import Path

#: Texture WADs referenced by the map, in worldspawn ``wad`` key order.
#: ``just setup`` downloads ``quake101.wad`` and ``ad.wad``; the rest are
#: provided manually (see the README).
WAD_FILES: tuple[str, ...] = (
    "quake101.wad",
    "ad.wad",
    "makkon_building.wad",
    "ikwhite.wad",
    "makkon_stone.wad",
    "mg1.wad",
    "alkaline.wad",
    "makkon_nature.wad",
)

#: qbsp treats any texture whose name starts with this prefix as the sky.
SKY_TEXTURE_PREFIX = "sky"

_WAD2_MAGIC = b"WAD2"
_WAD2_HEADER = struct.Struct("<4sii")
_WAD2_DIR_ENTRY = struct.Struct("<iiiBBh16s")


def _read_wad_texture_names(path: Path) -> set[str]:
    """Return every texture name in the WAD2 file at ``path``.

    Returns an empty set for a missing, truncated, or non-WAD2 file — a
    damaged or absent WAD must never make config validation raise; the worst
    case is that validation falls back to being permissive.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return set()
    if len(data) < _WAD2_HEADER.size:
        return set()
    magic, count, dir_offset = _WAD2_HEADER.unpack_from(data)
    if magic != _WAD2_MAGIC or count < 0 or dir_offset < 0:
        return set()
    names: set[str] = set()
    for index in range(count):
        entry_offset = dir_offset + index * _WAD2_DIR_ENTRY.size
        if entry_offset + _WAD2_DIR_ENTRY.size > len(data):
            break
        *_unused, raw_name = _WAD2_DIR_ENTRY.unpack_from(data, entry_offset)
        name = raw_name.split(b"\0", 1)[0].decode("ascii", "ignore").strip()
        if name:
            names.add(name)
    return names


def sky_texture_names(root: Path) -> set[str]:
    """Return the sky textures available across :data:`WAD_FILES` under ``root``.

    Only names starting with :data:`SKY_TEXTURE_PREFIX` are returned, since
    those are the only ones qbsp will compile as sky. An empty set means no
    WAD could be read at all (they aren't downloaded yet, say), which callers
    should treat as "can't validate" rather than "nothing is valid".
    """
    names: set[str] = set()
    for wad in WAD_FILES:
        names |= _read_wad_texture_names(root / wad)
    return {name for name in names if name.lower().startswith(SKY_TEXTURE_PREFIX)}
