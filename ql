#!/usr/bin/env python3
"""Entry point for the quake-loyola build CLI. Run as ``./ql <command>``
(e.g. ``./ql config show``, ``./ql config set KNOTT_HALL_ENABLED true``,
``./ql generate``, ``./ql build``) — no ``pip install`` required, same
sys.path convention as generate_map.py."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from quake_loyola.cli import app  # noqa: E402

if __name__ == "__main__":
    app()
