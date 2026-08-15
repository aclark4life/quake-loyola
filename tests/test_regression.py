import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import generate_map
from quake_loyola import entities, streets, west_campus
from quake_loyola.terrain import knott_hall as knott_terrain

# Golden values captured from the known-good map output with every
# config.py build setting at its hardcoded default (a local, gitignored
# ql.toml with overrides would otherwise change brush/entity counts and the
# hash out from under these tests — tests/conftest.py isolates the whole
# session from any such file, so this stays deterministic).
EXPECTED_BRUSHES = 1150
EXPECTED_ENTITIES = 106
EXPECTED_MD5 = "d4c32f737ca7801c72e414658f866a2c"

# Per-classname entity counts at the same golden state as EXPECTED_ENTITIES/
# EXPECTED_MD5 above. A plain count/hash mismatch only says "something
# changed" with no clue what; breaking it down by classname pinpoints which
# entity type moved, without needing a full checked-in golden .map file.
# scripts/update_golden.py rewrites this block along with the totals above,
# so it stays in sync — but it has no independent oracle either, so review
# the printed delta before blessing it.
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
    """Basic invariants for the point entities emitted by entities.build()."""

    def test_spawns_have_valid_origin_and_angle(self):
        _, ents = entities.build()
        spawns = [e for e in ents if e.classname == "info_player_start"]
        self.assertTrue(spawns, "expected at least one spawn entity")
        for e in spawns:
            self.assertIn("origin", e.fields)
            # "angle" must be a real Quake yaw (degrees CCW from +X, i.e.
            # east) so a stray non-numeric value or an out-of-range
            # placeholder doesn't silently leave a spawn facing undefined.
            angle = float(e.fields["angle"])
            self.assertGreaterEqual(angle, 0)
            self.assertLess(angle, 360)

    def test_no_duplicate_point_entity_origins(self):
        # Spawn points must not coincide with each other or with a teleport
        # destination — that combination risks a guaranteed telefrag as
        # players continuously materialize on top of a fixed spawn point.
        _, ents = entities.build()
        spawn_origins = [
            e.fields.get("origin") for e in ents if e.classname == "info_player_start"
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


class TeleportWiringTests(unittest.TestCase):
    """Every trigger_teleport in the assembled map must reach a real
    destination — a typo in "target" compiles fine but drops players at
    Quake's (0 0 0) map origin at runtime."""

    def setUp(self):
        self.entities = generate_map.build_map().entities

    def test_trigger_teleport_targets_resolve(self):
        dest_names = {
            e.fields.get("targetname")
            for e in self.entities
            if e.classname == "info_teleport_destination"
        }
        teleporters = [e for e in self.entities if e.classname == "trigger_teleport"]
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

    def test_trigger_teleport_brushes_have_nonzero_volume(self):
        # A degenerate (zero-thickness) trigger brush would still pass the
        # target-resolution test above (it only checks entity fields) but
        # would silently make the trigger untouchable in-game.
        triggers = [e for e in self.entities if e.classname == "trigger_teleport"]
        self.assertTrue(triggers, "expected at least one trigger_teleport")
        for e in triggers:
            self.assertTrue(
                e.brushes, f"trigger_teleport entity has no brushes: {e.fields}"
            )
            for b in e.brushes:
                (x1, y1, z1), (x2, y2, z2) = b.get_bbox()
                self.assertLess(x1, x2, "trigger_teleport brush has zero X extent")
                self.assertLess(y1, y2, "trigger_teleport brush has zero Y extent")
                self.assertLess(z1, z2, "trigger_teleport brush has zero Z extent")


class AreaBuildSmokeTests(unittest.TestCase):
    """Each area module must emit geometry — a build() that silently returns
    nothing would still pass a leak check but drop a whole area of the map."""

    def test_knott_terrain_builds_geometry(self):
        brushes, _ = knott_terrain.build()
        self.assertTrue(brushes, "expected Knott Hall terrain geometry")

    def test_west_campus_frontage_builds_geometry(self):
        brushes, _ = west_campus.build()
        self.assertTrue(brushes, "expected west-campus frontage geometry")

    def test_streets_build_geometry_and_details(self):
        brushes, ents = streets.build()
        self.assertTrue(brushes, "expected street geometry")
        self.assertIn("func_detail", [e.classname for e in ents])


if __name__ == "__main__":
    unittest.main()
