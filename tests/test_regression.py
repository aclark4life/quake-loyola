import hashlib
import unittest

import generate_map

# Golden values captured from the known-good map output. Update these
# deliberately (and review the .map diff) whenever the geometry changes.
EXPECTED_BRUSHES = 852
EXPECTED_ENTITIES = 538
EXPECTED_MD5 = "e57edd54e95400e2111463f3548581ab"


class MapRegressionTests(unittest.TestCase):
    def test_brush_and_entity_counts(self):
        mb = generate_map.build_map()
        self.assertEqual(len(mb.brushes), EXPECTED_BRUSHES)
        self.assertEqual(len(mb.entities), EXPECTED_ENTITIES)

    def test_map_text_matches_golden_hash(self):
        text = generate_map.build_map_text()
        digest = hashlib.md5(text.encode()).hexdigest()
        self.assertEqual(digest, EXPECTED_MD5)

    def test_build_is_deterministic(self):
        self.assertEqual(generate_map.build_map_text(), generate_map.build_map_text())


if __name__ == "__main__":
    unittest.main()
