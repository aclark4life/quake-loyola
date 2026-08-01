import hashlib
import unittest

import generate_map
from quake_loyola import entities, mapgen, maryland_hall, streets, west_campus
from quake_loyola.mapdata import Entity
from quake_loyola.terrain import knott_hall as knott_terrain
from quake_loyola.terrain import maryland as maryland_terrain

# Golden values captured from the known-good map output with every
# config.py flag/build setting at its hardcoded default (a local, gitignored
# ql.toml with overrides would otherwise change brush/entity counts and the
# hash out from under these tests — tests/conftest.py isolates the whole
# session from any such file, so this stays deterministic).
EXPECTED_BRUSHES = 1276
EXPECTED_ENTITIES = 102
EXPECTED_MD5 = "73ef69887d8c99deb40d308c2d146b1e"


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
    """entities.build() always runs its full ~1700-line placement logic now,
    but every per-group ENTITIES_ENABLED_<group> flag defaults to False in
    normal map generation (or the tests above). Force them on here so each
    group actually gets exercised and basic entity-placement invariants are
    checked.
    """

    _ENTITY_GROUP_FLAGS = (
        "ENTITIES_ENABLED_TELEPORTS",
        "ENTITIES_ENABLED_DM_SPAWNS",
        "ENTITIES_ENABLED_WEAPONS",
        "ENTITIES_ENABLED_AMMO",
        "ENTITIES_ENABLED_HEALTH",
        "ENTITIES_ENABLED_MONSTERS",
        "ENTITIES_ENABLED_VEGETATION",
        "ENTITIES_ENABLED_PLATFORM",
        "ENTITIES_ENABLED_EXIT",
    )

    def setUp(self):
        names = self._ENTITY_GROUP_FLAGS
        self._saved = {name: getattr(entities, name) for name in names}
        for name in self._ENTITY_GROUP_FLAGS:
            setattr(entities, name, True)

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

    def test_knott_monsters_placed_when_enabled(self):
        # ENTITIES_ENABLED_MONSTERS gates ogre/knight placement — exercise
        # that branch explicitly rather than relying on it being
        # incidentally covered by other flags.
        _, ents = entities.build()
        monster_classes = {"monster_ogre", "monster_knight"}
        monsters = [e for e in ents if e.classname in monster_classes]
        self.assertTrue(monsters, "expected at least one monster entity")

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


class KnottTerrainToggleTests(unittest.TestCase):
    """KNOTT_ENABLED_TERRAIN must be safely toggleable in either direction:
    streets.py falls back to flat, flush-with-sidewalk ground on the east
    side of Charles St when the flag is off (see the verge-fill comments in
    streets.py), so disabling KH terrain should never leave a gap, leak, or
    otherwise break map generation — it should just remove the hill/driveway
    detail and hand that area back to the plain verge fill.
    """

    def setUp(self):
        self._saved = {
            (
                knott_terrain,
                "KNOTT_ENABLED_TERRAIN",
            ): knott_terrain.KNOTT_ENABLED_TERRAIN,
            (streets, "KNOTT_ENABLED_TERRAIN"): streets.KNOTT_ENABLED_TERRAIN,
        }

    def tearDown(self):
        for (module, name), value in self._saved.items():
            setattr(module, name, value)

    def _build_with_flag(self, enabled):
        knott_terrain.KNOTT_ENABLED_TERRAIN = enabled
        streets.KNOTT_ENABLED_TERRAIN = enabled
        return generate_map.build_map()

    def test_enabled_and_disabled_both_build_cleanly(self):
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                mb = self._build_with_flag(enabled)
                self.assertTrue(mb.brushes, "expected at least one brush")

    def test_disabling_removes_knott_terrain_brushes_only(self):
        enabled_count = len(self._build_with_flag(True).brushes)
        disabled_count = len(self._build_with_flag(False).brushes)
        self.assertLess(
            disabled_count,
            enabled_count,
            "disabling KH terrain should reduce brush count (hill/driveway "
            "detail removed), not leave stray geometry behind",
        )
        self.assertGreater(
            disabled_count,
            0,
            "disabling KH terrain should still leave the street/world-shell "
            "geometry intact",
        )


class MarylandBuildTests(unittest.TestCase):
    """MARYLAND_ENABLED/MARYLAND_ENABLED_TERRAIN both default to False, so
    maryland_hall.py and terrain/maryland.py's real logic never runs in the
    default-config regression tests above. Force them on here so both
    branches actually get exercised.

    terrain/maryland.py's own build() only reads MARYLAND_ENABLED_TERRAIN —
    it is independent of maryland_hall.MARYLAND_ENABLED (the building flag),
    so terrain output must be identical whether the building is on or off.
    """

    def setUp(self):
        self._saved = {
            (maryland_hall, "MARYLAND_ENABLED"): maryland_hall.MARYLAND_ENABLED,
            (
                maryland_terrain,
                "MARYLAND_ENABLED_TERRAIN",
            ): maryland_terrain.MARYLAND_ENABLED_TERRAIN,
        }

    def tearDown(self):
        for (module, name), value in self._saved.items():
            setattr(module, name, value)

    def test_maryland_hall_builds_brushes_when_enabled(self):
        maryland_hall.MARYLAND_ENABLED = True
        brushes, _ = maryland_hall.build()
        self.assertTrue(brushes, "expected Maryland Hall to build brushes")

    def test_maryland_hall_builds_nothing_when_disabled(self):
        maryland_hall.MARYLAND_ENABLED = False
        brushes, ents = maryland_hall.build()
        self.assertEqual((brushes, ents), ([], []))

    def test_maryland_terrain_builds_when_terrain_flag_only(self):
        maryland_hall.MARYLAND_ENABLED = False
        maryland_terrain.MARYLAND_ENABLED_TERRAIN = True
        brushes, _ = maryland_terrain.build()
        self.assertTrue(
            brushes, "expected Maryland terrain mound with MARYLAND_ENABLED_TERRAIN"
        )

    def test_maryland_terrain_builds_nothing_when_terrain_disabled(self):
        # Regression: terrain must stay HINT-only whenever
        # MARYLAND_ENABLED_TERRAIN is off, even if the building itself is
        # enabled — the terrain flag must not be silently overridden.
        maryland_terrain.MARYLAND_ENABLED_TERRAIN = False
        for building_enabled in (False, True):
            with self.subTest(building_enabled=building_enabled):
                maryland_hall.MARYLAND_ENABLED = building_enabled
                brushes, ents = maryland_terrain.build()
                # Still returns a ring of invisible HINT brushes (to force a
                # BSP/portal split so the world floor doesn't exceed qbsp's
                # face-edge limit there) — not truly empty, but no entities
                # and no visible (non-HINT) geometry.
                self.assertEqual(ents, [])
                self.assertTrue(
                    all(f.tex == "hint" for b in brushes for f in b.faces),
                    "expected only HINT brushes when MARYLAND_ENABLED_TERRAIN is off",
                )


class WestCampusDormsBuildTests(unittest.TestCase):
    """WEST_CAMPUS_ENABLED_DORMS defaults to False, so west_campus.py's
    dorm-shell/walkway geometry (~1200 lines of build()) never runs in the
    default-config regression tests above. Force it on here so that branch
    actually gets exercised, and confirm the fence/wall/sidewalk-without-
    terrain guard still raises."""

    def setUp(self):
        self._saved = {
            name: getattr(west_campus, name)
            for name in (
                "WEST_CAMPUS_ENABLED_DORMS",
                "WEST_CAMPUS_ENABLED_FENCE",
                "WEST_CAMPUS_ENABLED_WALL",
                "WEST_CAMPUS_ENABLED_SIDEWALK",
                "WEST_CAMPUS_ENABLED_TERRAIN",
            )
        }

    def tearDown(self):
        for name, value in self._saved.items():
            setattr(west_campus, name, value)

    def test_dorms_disabled_builds_nothing_dorm_specific(self):
        west_campus.WEST_CAMPUS_ENABLED_DORMS = False
        brushes, _ = west_campus.build()
        self.assertTrue(brushes, "expected non-dorm west-campus geometry")

    def test_dorms_enabled_adds_brushes_and_entities(self):
        west_campus.WEST_CAMPUS_ENABLED_DORMS = False
        without_dorms = len(west_campus.build()[0])
        west_campus.WEST_CAMPUS_ENABLED_DORMS = True
        brushes, ents = west_campus.build()
        self.assertGreater(
            len(brushes),
            without_dorms,
            "enabling WEST_CAMPUS_ENABLED_DORMS should add dorm-shell brushes",
        )
        self.assertTrue(ents, "expected dorm-related entities (func_detail etc.)")

    def test_fence_without_terrain_raises(self):
        west_campus.WEST_CAMPUS_ENABLED_TERRAIN = False
        west_campus.WEST_CAMPUS_ENABLED_FENCE = True
        west_campus.WEST_CAMPUS_ENABLED_WALL = False
        west_campus.WEST_CAMPUS_ENABLED_SIDEWALK = False
        with self.assertRaises(ValueError):
            west_campus.build()


class KnottWalkwayBuildTests(unittest.TestCase):
    """KNOTT_ENABLED_WALKWAY/KNOTT_ENABLED_WALKWAY_BENT both default to
    False, so terrain/knott_hall.py's walkway/support-bent geometry never
    runs in the default-config regression tests above."""

    def setUp(self):
        self._saved = {
            name: getattr(knott_terrain, name)
            for name in ("KNOTT_ENABLED_WALKWAY", "KNOTT_ENABLED_WALKWAY_BENT")
        }

    def tearDown(self):
        for name, value in self._saved.items():
            setattr(knott_terrain, name, value)

    def test_walkway_disabled_builds_no_detail_entities(self):
        knott_terrain.KNOTT_ENABLED_WALKWAY = False
        knott_terrain.KNOTT_ENABLED_WALKWAY_BENT = False
        brushes, ents = knott_terrain.build()
        self.assertTrue(brushes, "expected base terrain brushes regardless")
        self.assertNotIn(
            "func_detail",
            [e.classname for e in ents],
            "no walkway func_detail expected with both flags off",
        )

    def test_walkway_enabled_adds_func_detail_entity(self):
        knott_terrain.KNOTT_ENABLED_WALKWAY = True
        knott_terrain.KNOTT_ENABLED_WALKWAY_BENT = False
        _, ents = knott_terrain.build()
        self.assertIn("func_detail", [e.classname for e in ents])

    def test_walkway_bent_enabled_adds_func_detail_entity(self):
        knott_terrain.KNOTT_ENABLED_WALKWAY = False
        knott_terrain.KNOTT_ENABLED_WALKWAY_BENT = True
        _, ents = knott_terrain.build()
        self.assertIn("func_detail", [e.classname for e in ents])


class LightGroupFilteringTests(unittest.TestCase):
    """mapgen.build_map()'s per-module light "_light_group" filtering
    (LIGHT_GROUP_FLAGS) is otherwise only covered incidentally through the
    full default build — exercise it directly against a fake module so the
    keep/drop/unknown-group branches are all checked explicitly."""

    class _FakeModule:
        @staticmethod
        def build():
            return [], [
                Entity("light", {"_light_group": "torch", "light": "200"}),
                Entity("light", {"_light_group": "pendant", "light": "200"}),
                Entity("light", {"light": "200"}),  # ungrouped, passes through
                Entity("info_player_start", {"origin": "0 0 0"}),
            ]

    def setUp(self):
        self._saved_modules = mapgen.MODULES
        self._saved_torch = mapgen.LIGHT_GROUP_FLAGS["torch"]
        self._saved_pendant = mapgen.LIGHT_GROUP_FLAGS["pendant"]
        mapgen.MODULES = [self._FakeModule]

    def tearDown(self):
        mapgen.MODULES = self._saved_modules
        mapgen.LIGHT_GROUP_FLAGS["torch"] = self._saved_torch
        mapgen.LIGHT_GROUP_FLAGS["pendant"] = self._saved_pendant

    def test_disabled_group_is_dropped_enabled_group_kept(self):
        mapgen.LIGHT_GROUP_FLAGS["torch"] = True
        mapgen.LIGHT_GROUP_FLAGS["pendant"] = False
        mb = mapgen.build_map()
        origins = [e.classname for e in mb.entities]
        self.assertEqual(origins.count("light"), 2)  # torch + ungrouped kept
        self.assertIn("info_player_start", origins)

    def test_unknown_light_group_raises(self):
        class _BadModule:
            @staticmethod
            def build():
                return [], [Entity("light", {"_light_group": "not_a_real_group"})]

        mapgen.MODULES = [_BadModule]
        with self.assertRaises(ValueError):
            mapgen.build_map()


if __name__ == "__main__":
    unittest.main()
