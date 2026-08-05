"""Tests that each feature-toggle constant actually changes its module's
build() output — added because a code review found bridge/basement/
street-detail/NE-terrain/light-group toggles had no direct coverage (only
the golden regression test exercised them, indirectly, at their hardcoded
defaults).

These monkeypatch the module-level constant bound in each area module's own
namespace (the name each module imported via `from .constants import X`),
per the staleness note in quake_loyola.config's docstring: mutating
config.FLAGS after import does not retroactively update already-bound
constants, so tests must patch the bound name directly.
"""

import unittest

from quake_loyola import basement, bridge, mapgen, streets
from quake_loyola.terrain import ne as ne_terrain


class BridgeSpanToggleTests(unittest.TestCase):
    def test_disabling_all_spans_returns_empty(self):
        names = [
            "BRIDGE_ENABLED_SPAN_WEST_APPROACH",
            "BRIDGE_ENABLED_SPAN_CENTER",
            "BRIDGE_ENABLED_SPAN_EAST_APPROACH",
            "BRIDGE_ENABLED_SPAN_KH",
            "BRIDGE_ENABLED_SPAN_EAST_EXT",
        ]
        originals = {name: getattr(bridge, name) for name in names}
        for name in names:
            setattr(bridge, name, False)
        try:
            brushes, entities = bridge.build()
        finally:
            for name, value in originals.items():
                setattr(bridge, name, value)
        self.assertEqual((brushes, entities), ([], []))

    def test_disabling_one_span_reduces_output(self):
        # Bridge geometry is largely modeled as func_* brush entities rather
        # than raw world brushes, so a span toggle shows up as fewer
        # entities, not fewer top-level brushes.
        _, full_entities = bridge.build()
        original = bridge.BRIDGE_ENABLED_SPAN_WEST_APPROACH
        bridge.BRIDGE_ENABLED_SPAN_WEST_APPROACH = False
        try:
            _, partial_entities = bridge.build()
        finally:
            bridge.BRIDGE_ENABLED_SPAN_WEST_APPROACH = original
        self.assertLess(len(partial_entities), len(full_entities))


class BasementToggleTests(unittest.TestCase):
    def test_disabled_returns_empty(self):
        original = basement.BASEMENT_ENABLED
        basement.BASEMENT_ENABLED = False
        try:
            self.assertEqual(basement.build(), ([], []))
        finally:
            basement.BASEMENT_ENABLED = original

    def test_enabled_returns_geometry(self):
        original = basement.BASEMENT_ENABLED
        basement.BASEMENT_ENABLED = True
        try:
            brushes, _ = basement.build()
            self.assertGreater(len(brushes), 0)
        finally:
            basement.BASEMENT_ENABLED = original


class StreetDetailsToggleTests(unittest.TestCase):
    def test_world_seal_always_present_regardless_of_details_flag(self):
        # Regression test for a bug where the global SKY leak-seal brushes
        # lived inside _build_street_details() and were only built when
        # STREETS_ENABLED_DETAILS was True, so turning details off could
        # leave the map unsealed (a leak). The seal must always be present.
        original = streets.STREETS_ENABLED_DETAILS
        try:
            streets.STREETS_ENABLED_DETAILS = False
            disabled_brushes, _ = streets.build()
            streets.STREETS_ENABLED_DETAILS = True
            enabled_brushes, _ = streets.build()
        finally:
            streets.STREETS_ENABLED_DETAILS = original

        def sky_brush_count(brushes):
            from quake_loyola.constants import Textures

            return sum(
                1 for b in brushes if any(face.tex == Textures.SKY for face in b.faces)
            )

        self.assertGreaterEqual(sky_brush_count(disabled_brushes), 6)
        self.assertEqual(
            sky_brush_count(disabled_brushes), sky_brush_count(enabled_brushes)
        )

    def test_disabling_details_removes_detail_entities(self):
        # Top-level world BRUSHES no longer differ: the global leak-seal
        # brushes (previously only added when details were built) are now
        # always appended in streets/__init__.py regardless of this flag,
        # since they're leak-prevention geometry, not a cosmetic detail.
        # The actual cosmetic detail brushes (curbs, lamps, trees,
        # driveways, etc.) are wrapped into func_detail brush entities, so
        # the toggle's effect shows up in ENTITIES instead.
        full_brushes, full_entities = streets.build()
        original = streets.STREETS_ENABLED_DETAILS
        streets.STREETS_ENABLED_DETAILS = False
        try:
            reduced_brushes, reduced_entities = streets.build()
        finally:
            streets.STREETS_ENABLED_DETAILS = original
        self.assertEqual(len(reduced_brushes), len(full_brushes))
        self.assertLess(len(reduced_entities), len(full_entities))
        self.assertFalse(
            any(ent.classname == "func_detail" for ent in reduced_entities)
        )
        self.assertTrue(any(ent.classname == "func_detail" for ent in full_entities))


class NeTerrainToggleTests(unittest.TestCase):
    def test_disabled_returns_empty(self):
        original = ne_terrain.NE_ENABLED_TERRAIN
        ne_terrain.NE_ENABLED_TERRAIN = False
        try:
            self.assertEqual(ne_terrain.build(), ([], []))
        finally:
            ne_terrain.NE_ENABLED_TERRAIN = original

    def test_enabled_returns_geometry(self):
        original = ne_terrain.NE_ENABLED_TERRAIN
        ne_terrain.NE_ENABLED_TERRAIN = True
        try:
            brushes, _ = ne_terrain.build()
            self.assertGreater(len(brushes), 0)
        finally:
            ne_terrain.NE_ENABLED_TERRAIN = original


class LightGroupToggleTests(unittest.TestCase):
    """mapgen.build_map() filters light entities tagged with a
    ``_light_group`` fixture field through LIGHT_GROUP_FLAGS, independent of
    the per-area build() functions above."""

    def test_disabling_a_light_group_drops_only_that_groups_lights(self):
        original = dict(mapgen.LIGHT_GROUP_FLAGS)
        mapgen.LIGHT_GROUP_FLAGS["torch"] = False
        try:
            mb = mapgen.build_map()
        finally:
            mapgen.LIGHT_GROUP_FLAGS.clear()
            mapgen.LIGHT_GROUP_FLAGS.update(original)
        for e in mb.entities:
            self.assertNotEqual(e.fields.get("_light_group"), "torch")

    def test_enabling_a_light_group_keeps_that_groups_lights_untagged(self):
        # With every group enabled, no surviving light entity should still
        # carry the internal _light_group bookkeeping field.
        all_enabled = {name: True for name in mapgen.LIGHT_GROUP_FLAGS}
        original = dict(mapgen.LIGHT_GROUP_FLAGS)
        mapgen.LIGHT_GROUP_FLAGS.clear()
        mapgen.LIGHT_GROUP_FLAGS.update(all_enabled)
        try:
            mb = mapgen.build_map()
        finally:
            mapgen.LIGHT_GROUP_FLAGS.clear()
            mapgen.LIGHT_GROUP_FLAGS.update(original)
        for e in mb.entities:
            self.assertNotIn("_light_group", e.fields)


if __name__ == "__main__":
    unittest.main()
