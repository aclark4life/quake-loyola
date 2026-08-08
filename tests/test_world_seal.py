"""The global leak-seal brushes must always be part of the street build.

Regression test for a bug where the six global SKY leak-seal brushes lived
inside ``_build_street_details()``, so they were only built when the (now
removed) ``STREETS_ENABLED_DETAILS`` flag was on and the map could otherwise
be left unsealed. They now live in ``streets/shell.py::_build_world_seal()``
and are appended unconditionally by ``streets.build()``.
"""

import unittest

from quake_loyola import streets
from quake_loyola.constants import Textures


class WorldSealTests(unittest.TestCase):
    def test_street_build_includes_the_world_seal(self):
        brushes, _ = streets.build()
        sky_brushes = sum(
            1 for b in brushes if any(face.tex == Textures.SKY for face in b.faces)
        )
        self.assertGreaterEqual(sky_brushes, 6)
