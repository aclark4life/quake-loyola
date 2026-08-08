import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import generate_map
from quake_loyola import dorms, entities, mapgen, maryland_hall, streets, west_campus
from quake_loyola.mapdata import Entity
from quake_loyola.terrain import knott_hall as knott_terrain
from quake_loyola.terrain import maryland as maryland_terrain

# Golden values captured from the known-good map output with every
# config.py flag/build setting at its hardcoded default (a local, gitignored
# ql.toml with overrides would otherwise change brush/entity counts and the
# hash out from under these tests — tests/conftest.py isolates the whole
# session from any such file, so this stays deterministic).
EXPECTED_BRUSHES = 1461
EXPECTED_ENTITIES = 106
EXPECTED_MD5 = "ab25eabf52d6caf48f051c773aaa7b34"

# Per-classname entity counts at the same golden state as EXPECTED_ENTITIES/
# EXPECTED_MD5 above. A plain count/hash mismatch only says "something
# changed" with no clue what; breaking it down by classname pinpoints which
# entity type moved, without needing a full checked-in golden .map file.
# Keep in sync with the totals above (and re-derive by hand, the same way,
# if you intentionally change entity output — this has no independent
# oracle either).
EXPECTED_ENTITY_CLASSNAME_COUNTS = {
    "func_detail": 13,
    "func_illusionary": 5,
    "info_player_start": 1,
    "info_teleport_destination": 1,
    "light": 63,
    "light_flame_large_yellow": 16,
    "trigger_hurt": 6,
    "trigger_teleport": 1,
}


class MapRegressionTests(unittest.TestCase):
    def test_brush_and_entity_counts(self):
        mb = generate_map.build_map()
        self.assertEqual(len(mb.brushes), EXPECTED_BRUSHES)
        self.assertEqual(len(mb.entities), EXPECTED_ENTITIES)

    def test_entity_classname_counts_match_golden_breakdown(self):
        mb = generate_map.build_map()
        counts = dict(Counter(e.classname for e in mb.entities))
        self.assertEqual(counts, EXPECTED_ENTITY_CLASSNAME_COUNTS)

    def test_map_text_matches_golden_hash(self):
        text = generate_map.build_map_text()
        digest = hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()
        self.assertEqual(digest, EXPECTED_MD5)

    def test_build_is_deterministic_across_processes(self):
        """Calling build_map_text() twice in the same process (the previous
        version of this test) can never actually catch non-determinism:
        any change to the function makes both sides identical regardless of
        whether the output is order-dependent. Instead, run the build in two
        fresh subprocesses with different PYTHONHASHSEED values (which
        perturbs set/frozenset iteration order, a common source of
        accidental non-determinism) and assert the resulting .map text
        hashes match — this actually exercises cross-run determinism rather
        than comparing a function to itself.
        """
        repo_root = Path(__file__).resolve().parent.parent
        script = (
            "import hashlib; "
            "import generate_map; "
            "print(hashlib.md5("
            "generate_map.build_map_text().encode(), usedforsecurity=False"
            ").hexdigest())"
        )
        digests = set()
        for seed in ("0", "1"):
            with tempfile.TemporaryDirectory() as tmp_cwd:
                result = subprocess.run(
                    [sys.executable, "-c", script],
                    cwd=tmp_cwd,
                    env={
                        **os.environ,
                        "PYTHONHASHSEED": seed,
                        "PYTHONPATH": os.pathsep.join(
                            [str(repo_root), str(repo_root / "src")]
                        ),
                    },
                    capture_output=True,
                    text=True,
                    check=True,
                )
                digests.add(result.stdout.strip())
        self.assertEqual(
            len(digests), 1, f"non-deterministic output across hash seeds: {digests}"
        )


class EntitiesBuildTests(unittest.TestCase):
    """entities.build() always runs its full ~1700-line placement logic now,
    but every per-group ENTITIES_ENABLED_<group> flag defaults to False in
    normal map generation (or the tests above). Force them on here so each
    group actually gets exercised and basic entity-placement invariants are
    checked.
    """

    # Each flag is monkeypatched on the submodule that actually references
    # it in its own module globals — ``entities`` is now a thin package that
    # dispatches to per-concern submodules (spawns/pickups/monsters/etc.),
    # so setting the attribute on ``entities`` itself would have no effect.
    _ENTITY_GROUP_FLAGS = (
        (entities.spawns, "ENTITIES_ENABLED_TELEPORTS"),
        (entities.spawns, "ENTITIES_ENABLED_DM_SPAWNS"),
        (entities.pickups, "ENTITIES_ENABLED_WEAPONS"),
        (entities.pickups, "ENTITIES_ENABLED_AMMO"),
        (entities.pickups, "ENTITIES_ENABLED_HEALTH"),
        (entities.monsters, "ENTITIES_ENABLED_MONSTERS"),
        (entities.vegetation, "ENTITIES_ENABLED_VEGETATION"),
        (entities.platform, "ENTITIES_ENABLED_PLATFORM"),
        # Geometry-gated flag: default False in normal generation, but the
        # walkway hell knights are only reachable when it is also on.
        (entities.monsters, "KNOTT_ENABLED_WALKWAY"),
    )

    def setUp(self):
        self._saved = {
            (mod, name): getattr(mod, name) for mod, name in self._ENTITY_GROUP_FLAGS
        }
        for mod, name in self._ENTITY_GROUP_FLAGS:
            setattr(mod, name, True)

    def tearDown(self):
        for (mod, name), value in self._saved.items():
            setattr(mod, name, value)

    def test_spawns_have_origin_and_angle(self):
        _, ents = entities.build()
        spawn_classes = {"info_player_start", "info_player_deathmatch"}
        spawns = [e for e in ents if e.classname in spawn_classes]
        self.assertTrue(spawns, "expected at least one spawn entity")
        for e in spawns:
            self.assertIn("origin", e.fields)
            self.assertIn("angle", e.fields)
            # "angle" must be a real Quake yaw (degrees CCW from +X, i.e.
            # east) so a stray non-numeric value or an out-of-range
            # placeholder doesn't silently leave a spawn facing undefined.
            angle = float(e.fields["angle"])
            self.assertGreaterEqual(angle, 0)
            self.assertLess(angle, 360)

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
        for e in monsters:
            self.assertIn("angle", e.fields)
            angle = float(e.fields["angle"])
            self.assertGreaterEqual(angle, 0)
            self.assertLess(angle, 360)

    def test_hell_knights_placed_with_valid_angles(self):
        # monster_hell_knight placements include both the always-on bridge
        # deck pair and the KNOTT_ENABLED_WALKWAY-gated walkway/accessible
        # spots (forced on for this test class) — assert all of them.
        _, ents = entities.build()
        hell_knights = [e for e in ents if e.classname == "monster_hell_knight"]
        self.assertGreaterEqual(
            len(hell_knights), 5, "expected deck + walkway hell knight placements"
        )
        for e in hell_knights:
            self.assertIn("origin", e.fields)
            angle = float(e.fields["angle"])
            self.assertGreaterEqual(angle, 0)
            self.assertLess(angle, 360)

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

    def test_trigger_teleport_targets_resolve(self):
        # Every trigger_teleport's "target" must name an actual
        # info_teleport_destination's "targetname" — a typo here compiles
        # fine but sends players to Quake's (0 0 0) map origin at runtime.
        _, ents = entities.build()
        dest_names = {
            e.fields.get("targetname")
            for e in ents
            if e.classname == "info_teleport_destination"
        }
        teleporters = [e for e in ents if e.classname == "trigger_teleport"]
        self.assertTrue(teleporters, "expected at least one trigger_teleport")
        for e in teleporters:
            target = e.fields.get("target")
            self.assertIsNotNone(
                target, f"trigger_teleport missing 'target' field: {e.fields}"
            )
            self.assertIn(
                target,
                dest_names,
                f"trigger_teleport target {target!r} has no matching "
                "info_teleport_destination targetname",
            )

    def test_platform_path_corner_chain_resolves(self):
        # func_train's "target" and every path_corner's "target" must name
        # an existing path_corner "targetname" — a broken link leaves the
        # platform stuck (or crashes to the map origin) instead of looping.
        _, ents = entities.build()
        path_corners = [e for e in ents if e.classname == "path_corner"]
        self.assertTrue(path_corners, "expected at least one path_corner")
        corner_names = {e.fields.get("targetname") for e in path_corners}

        trains = [e for e in ents if e.classname == "func_train"]
        self.assertTrue(trains, "expected at least one func_train")
        for e in trains:
            target = e.fields.get("target")
            self.assertIsNotNone(
                target, f"func_train missing 'target' field: {e.fields}"
            )
            self.assertIn(
                target,
                corner_names,
                f"func_train target {target!r} has no matching path_corner targetname",
            )

        for e in path_corners:
            targetname = e.fields.get("targetname")
            self.assertIsNotNone(
                targetname, f"path_corner missing 'targetname' field: {e.fields}"
            )
            target = e.fields.get("target")
            self.assertIsNotNone(
                target, f"path_corner {targetname!r} missing 'target' field"
            )
            self.assertIn(
                target,
                corner_names,
                f"path_corner {targetname!r} target {target!r} has no "
                "matching path_corner targetname — chain is broken",
            )

    def test_trigger_teleport_and_changelevel_brushes_have_nonzero_volume(self):
        # A code review found no coverage validating the actual brush
        # VOLUME of trigger_teleport/trigger_changelevel — a bug producing
        # a degenerate (zero-thickness) trigger brush would still pass the
        # target-resolution tests above (they only check entity fields),
        # but would silently make the trigger untouchable in-game.
        #
        # trigger_changelevel is not required: the map's only exit portal
        # lived inside the dorms and was removed with them, so it is only
        # validated if something re-adds it.
        _, ents = entities.build()
        for classname, required in (
            ("trigger_teleport", True),
            ("trigger_changelevel", False),
        ):
            triggers = [e for e in ents if e.classname == classname]
            if required:
                self.assertTrue(triggers, f"expected at least one {classname}")
            for e in triggers:
                self.assertTrue(
                    e.brushes, f"{classname} entity has no brushes: {e.fields}"
                )
                for b in e.brushes:
                    (x1, y1, z1), (x2, y2, z2) = b.get_bbox()
                    self.assertLess(x1, x2, f"{classname} brush has zero X extent")
                    self.assertLess(y1, y2, f"{classname} brush has zero Y extent")
                    self.assertLess(z1, z2, f"{classname} brush has zero Z extent")

    def test_platform_train_brush_starts_at_its_first_path_corner(self):
        # The func_train brush's initial position is placed directly at the
        # first path_corner it targets (rather than some other point on the
        # loop), so the platform doesn't visibly jump on level start. Verify
        # the brush's bbox center matches that path_corner's origin.
        _, ents = entities.build()
        trains = [e for e in ents if e.classname == "func_train"]
        path_corners = {
            e.fields["targetname"]: e.fields["origin"]
            for e in ents
            if e.classname == "path_corner"
        }
        self.assertTrue(trains, "expected at least one func_train")
        for e in trains:
            first_target = e.fields.get("target")
            self.assertIn(
                first_target,
                path_corners,
                f"func_train target {first_target!r} has no path_corner origin",
            )
            ox, oy, oz = (float(v) for v in path_corners[first_target].split())
            self.assertEqual(len(e.brushes), 1)
            (x1, y1, z1), (x2, y2, z2) = e.brushes[0].get_bbox()
            self.assertAlmostEqual((x1 + x2) / 2, ox, places=3)
            self.assertAlmostEqual((y1 + y2) / 2, oy, places=3)
            self.assertAlmostEqual((z1 + z2) / 2, oz, places=3)


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
            (
                streets.details,
                "KNOTT_ENABLED_TERRAIN",
            ): streets.details.KNOTT_ENABLED_TERRAIN,
        }

    def tearDown(self):
        for (module, name), value in self._saved.items():
            setattr(module, name, value)

    def _build_with_flag(self, enabled):
        knott_terrain.KNOTT_ENABLED_TERRAIN = enabled
        streets.details.KNOTT_ENABLED_TERRAIN = enabled
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


class DormsClearedTests(unittest.TestCase):
    """The dorm buildings were removed pending a rebuild; dorms.py is a
    placeholder that must stay wired into mapgen without emitting anything."""

    def test_build_returns_nothing(self):
        self.assertEqual(dorms.build(), ([], []))

    def test_module_is_still_registered_with_mapgen(self):
        self.assertIn(dorms, mapgen.MODULES)


class WestCampusFrontageBuildTests(unittest.TestCase):
    """Confirm the fence/wall/sidewalk-without-terrain guard still raises."""

    def setUp(self):
        self._saved = {
            name: getattr(west_campus, name)
            for name in (
                "WEST_CAMPUS_ENABLED_FENCE",
                "WEST_CAMPUS_ENABLED_WALL",
                "WEST_CAMPUS_ENABLED_SIDEWALK",
                "WEST_CAMPUS_ENABLED_TERRAIN",
            )
        }

    def tearDown(self):
        for name, value in self._saved.items():
            setattr(west_campus, name, value)

    def test_frontage_builds_geometry(self):
        brushes, _ = west_campus.build()
        self.assertTrue(brushes, "expected west-campus frontage geometry")

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
        knott_terrain.KNOTT_ENABLED_WALKWAY = True
        knott_terrain.KNOTT_ENABLED_WALKWAY_BENT = True
        _, ents = knott_terrain.build()
        self.assertIn("func_detail", [e.classname for e in ents])

    def test_walkway_bent_without_walkway_adds_nothing(self):
        # The support bent is documented as sitting "beneath the south edge
        # of the walkway span" — it must not be built when the walkway
        # itself is disabled, or it would be a free-standing support for
        # geometry that doesn't exist.
        knott_terrain.KNOTT_ENABLED_WALKWAY = False
        knott_terrain.KNOTT_ENABLED_WALKWAY_BENT = True
        brushes, ents = knott_terrain.build()
        self.assertNotIn("func_detail", [e.classname for e in ents])


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
