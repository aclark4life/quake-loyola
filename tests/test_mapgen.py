"""Tests for quake_loyola.mapgen.main() — the top-level "write loyola.map to
the repo root" entry point invoked by `ql gen` / `python generate_map.py`.
build_map()/build_map_text() themselves are already covered indirectly by
tests/test_regression.py's golden-output assertions."""

import tempfile
import unittest
from pathlib import Path

from quake_loyola import mapgen


class MainWritesMapFileTests(unittest.TestCase):
    def test_main_writes_loyola_map_to_repo_root(self):
        # Write to a temp path rather than the real repo root so this test
        # has no working-tree side effects.
        with tempfile.TemporaryDirectory() as tmpdir:
            map_path = Path(tmpdir) / "loyola.map"
            mapgen.main(path=map_path)
            self.assertTrue(map_path.exists())
            text = map_path.read_text()
            self.assertIn("worldspawn", text)
            self.assertEqual(text, mapgen.build_map_text())

    def test_main_defaults_to_repo_root(self):
        # The default (no-arg) path should still target the documented
        # repo-root location, without actually writing there in this test.
        import inspect

        sig = inspect.signature(mapgen.main)
        self.assertIn("path", sig.parameters)
        self.assertIsNone(sig.parameters["path"].default)


if __name__ == "__main__":
    unittest.main()
