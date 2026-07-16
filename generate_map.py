#!/usr/bin/env python3
"""Thin wrapper kept for backwards compatibility — the real implementation
now lives in ``quake_loyola.mapgen`` so it's importable once quake-loyola is
pip-installed (see ``ql generate`` / ``src/quake_loyola/cli.py``).

    python generate_map.py    # same as: ./ql generate
"""

import sys
from pathlib import Path

# Ensure src/ is on the path so quake_loyola is importable without installing it
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quake_loyola.mapgen import build_map, build_map_text, main  # noqa: F401,E402

if __name__ == "__main__":
    main()
