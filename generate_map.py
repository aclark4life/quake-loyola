#!/usr/bin/env python3
"""Thin wrapper kept for backwards compatibility — the real implementation
now lives in ``quake_loyola.mapgen`` so it's importable once quake-loyola is
pip-installed (see ``ql gen`` / ``src/quake_loyola/cli.py``).

    python generate_map.py    # same as: ql gen
"""

import sys
from pathlib import Path

try:
    from quake_loyola.mapgen import build_map, build_map_text, main  # noqa: F401
except ModuleNotFoundError:
    # Fallback for running from a checkout without `pip install -e .`.
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from quake_loyola.mapgen import build_map, build_map_text, main  # noqa: F401

if __name__ == "__main__":
    main()
