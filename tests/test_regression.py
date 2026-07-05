import hashlib
import unittest

import generate_map
from quake_loyola import entities

# Golden values captured from the known-good map output. Update these
# deliberately (and review the .map diff) whenever the geometry changes.
EXPECTED_BRUSHES = 13
EXPECTED_ENTITIES = 16
EXPECTED_MD5 = "376d8c5c4bbe724c67267bcb5316fbea"


class MapRegressionTests(unittest.TestCase):
    def test_brush_and_entity_counts(self):
        mb = generate_map.build_map()
        self.assertEqual(len(mb.brushes), EXPECTED_BRUSHES)
        self.assertEqual(len(mb.entities), EXPECTED_ENTITIES)

    def test_map_text_matches_golden_hash(self):
        text = generate_map.build_map_text()
        digest = hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()
        self.assertEqual(digest, EXPECTED_MD5)

    def test_build_is_deterministic(self):
        self.assertEqual(generate_map.build_map_text(), generate_map.build_map_text())


class EntitiesBuildTests(unittest.TestCase):
    """entities.build() only runs its full ~1700-line placement logic when
    ENTITIES_ENABLED is True, which is not the case in normal map generation
    (or the tests above). Force the flags on here so that path gets exercised
    and basic entity-placement invariants are checked.
    """

    def setUp(self):
        self._saved = {
            name: getattr(entities, name)
            for name in ("ENTITIES_ENABLED", "KNOTT_INTERIOR_ENABLED")
        }
        entities.ENTITIES_ENABLED = True
        entities.KNOTT_INTERIOR_ENABLED = True

    def tearDown(self):
        for name, value in self._saved.items():
            setattr(entities, name, value)

    def test_spawns_have_origin_and_angle(self):
        _, ents = entities.build()
        spawn_classes = {"info_player_start", "info_player_deathmatch"}
        spawns = [e for e in ents if e.classname in spawn_classes]
        self.assertTrue(spawns, "expected at least one spawn entity")
        for e in spawns:
            self.assertIn("origin", e.fields)
            self.assertIn("angle", e.fields)

    def test_lights_have_positive_intensity(self):
        _, ents = entities.build()
        lights = [e for e in ents if e.classname == "light"]
        self.assertTrue(lights, "expected at least one light entity")
        for e in lights:
            self.assertGreater(float(e.fields["light"]), 0)

    def test_no_duplicate_point_entity_origins(self):
        # Spawn points must not coincide with each other or with a teleport
        # destination — that combination risks a guaranteed telefrag as
        # players continuously materialize on top of a fixed spawn point.
        # (Weapons/items placed at spawn origins are a normal, intentional
        # Quake DM convention and are not flagged here. Multiple teleport
        # destinations deliberately sharing one hub landing spot — e.g.
        # several arches funneling onto the same rooftop — is also valid
        # and intentional, so only spawn-vs-teleport-destination overlap
        # is checked.)
        _, ents = entities.build()
        spawn_classes = {"info_player_start", "info_player_deathmatch"}
        spawn_origins = [
            e.fields.get("origin") for e in ents if e.classname in spawn_classes
        ]
        self.assertEqual(
            len(spawn_origins),
            len(set(spawn_origins)),
            "duplicate spawn-point origins",
        )
        teleport_dest_origins = {
            e.fields.get("origin")
            for e in ents
            if e.classname == "info_teleport_destination"
        }
        colliding = set(spawn_origins) & teleport_dest_origins
        self.assertFalse(
            colliding,
            f"spawn point(s) coincide with a teleport destination: {colliding}",
        )


if __name__ == "__main__":
    unittest.main()
