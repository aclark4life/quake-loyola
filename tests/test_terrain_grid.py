"""The west-campus terrain grid must stay aligned with Pier 2's footprint.

Regression test for a see-through hole on the north side of Pier 2. The
centre span is shifted north by ``BRIDGE_CENTER_SPAN_OFFSET``, putting the
pier base's north face at y=484, while the terrain grid had a row at y=500.
The pier punched through the ground and left a 90x16 strip of terrain top
face between its north face and the cell edge; qbsp dropped that sliver, so
the ground there was solid to walk on but rendered as a hole.

Keeping the grid row exactly on the pier face means there is no remainder to
drop. These tests pin that relationship rather than the literal 484, so
retuning the centre-span offset can't silently reopen the hole.
"""

import unittest

from quake_loyola.constants import (
    BRIDGE,
    BRIDGE_CENTER_SPAN_OFFSET,
    BRIDGE_PILLAR_OVERHANG,
)
from quake_loyola.terrain import west_campus


class WestCampusGridAlignmentTests(unittest.TestCase):
    def test_a_grid_row_sits_on_the_shifted_pier_north_face(self):
        pier_north_y = int(
            BRIDGE.y2 + BRIDGE_PILLAR_OVERHANG + BRIDGE_CENTER_SPAN_OFFSET[1]
        )
        self.assertIn(
            pier_north_y,
            west_campus.wct_y,
            "the terrain grid must have a row on Pier 2's north face, or the "
            "pier leaves a sliver of ground face that qbsp drops",
        )

    def test_grid_rows_run_north_to_south(self):
        self.assertEqual(west_campus.wct_y, sorted(west_campus.wct_y, reverse=True))

    def test_every_grid_row_has_an_elevation(self):
        for column in west_campus._wct_cols:
            self.assertEqual(len(column), len(west_campus.wct_y))
