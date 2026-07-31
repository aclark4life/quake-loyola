"""Tests for quake_loyola.mapgen.main() — the top-level "write loyola.map to
the repo root" entry point invoked by `ql gen` / `python generate_map.py`.
build_map()/build_map_text() themselves are already covered indirectly by
tests/test_regression.py's golden-output assertions."""

import unittest

from quake_loyola import config, mapgen


class MainWritesMapFileTests(unittest.TestCase):
    def test_main_writes_loyola_map_to_repo_root(self):
        map_path = config.REPO_ROOT / "loyola.map"
        if map_path.exists():
            map_path.unlink()
        try:
            mapgen.main()
            self.assertTrue(map_path.exists())
            text = map_path.read_text()
            self.assertIn("worldspawn", text)
            self.assertEqual(text, mapgen.build_map_text())
        finally:
            if map_path.exists():
                map_path.unlink()


if __name__ == "__main__":
    unittest.main()
