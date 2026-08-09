"""Trigger brush entities must never be textured with the sky.

Regression test for a bug where the bridge torches' ``trigger_hurt`` brushes
were built with ``Textures.SKY``, putting 24 stray sky faces at z 528-568 in
the middle of the map. Vanilla triggers zero their modelindex, so nothing was
drawn and the bug was invisible for a long time -- but qbsp still compiled
those faces as sky, and once an environment skybox was configured they became
six-sided holes showing the skybox through the bridge.

The sky belongs to the world seal (``streets/shell.py``) and to nothing else,
so this asserts on the whole map rather than just the bridge.
"""

import unittest

from quake_loyola.constants import Textures
from quake_loyola.mapgen import build_map


class TriggerTextureTests(unittest.TestCase):
    def setUp(self):
        self.builder = build_map()

    def test_no_entity_brush_is_textured_with_the_sky(self):
        for entity in self.builder.entities:
            for brush in getattr(entity, "brushes", None) or ():
                for face in brush.faces:
                    self.assertNotEqual(
                        face.tex,
                        Textures.SKY,
                        f"{entity.classname} has a sky face; the sky belongs "
                        "to the world seal only",
                    )

    def test_torch_hurt_triggers_use_the_trigger_texture(self):
        hurt = [e for e in self.builder.entities if e.classname == "trigger_hurt"]
        self.assertTrue(hurt, "expected the bridge torches' trigger_hurt brushes")
        for entity in hurt:
            for brush in entity.brushes:
                for face in brush.faces:
                    self.assertEqual(face.tex, Textures.TRIGGER)
