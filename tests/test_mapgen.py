"""Tests for quake_loyola.mapgen.main() — the top-level "write loyola.map to
the repo root" entry point invoked by `ql gen` / `python generate_map.py`.
build_map()/build_map_text() themselves are already covered indirectly by
tests/test_regression.py's golden-output assertions."""

import tempfile
import unittest
import unittest.mock
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
        # The default (no-arg) path should actually write to config.REPO_ROOT,
        # not just declare it in the signature.
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo_root = Path(tmpdir)
            with unittest.mock.patch.object(mapgen.config, "REPO_ROOT", fake_repo_root):
                mapgen.main()
                written_path = fake_repo_root / "loyola.map"
                self.assertTrue(written_path.exists())
                self.assertEqual(written_path.read_text(), mapgen.build_map_text())


if __name__ == "__main__":
    unittest.main()
