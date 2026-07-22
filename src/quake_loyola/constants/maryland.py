"""Maryland Hall placeholder constants (PROVISIONAL, pending re-derivation)."""

from .derived import KNOTT_X1
from .knott import KNOTT_Y2

# ── Maryland Hall — PROVISIONAL placeholder anchor, pending re-derivation ──────
# Real building (OSM way 1019882993, operator "Loyola University Maryland"),
# east of Ennis Parallel near the Sellinger School of Business. Derived from
# OSM footprint GPS coordinates (not a pixel/satellite-screenshot measurement
# like other anchors in this file), converted via the real-world-ft -> Quake-
# unit transform anchored at KNOTT_X1/KNOTT_Y2 (SCALE = 15.108 units/ft) —
# validated to ~4% against the real Knott Hall footprint width, but the
# Y-axis correspondence is NOT independently cross-checked.
#
# That full-scale conversion (6385/8979/412/1622, below in a comment for
# reference) placed the block ~230 ft beyond the KH driveway/Ennis Drive
# corner — because Ennis/east-campus constants (_EAST_FEATURES_X2 etc.) were
# deliberately left at an older, ~2.4-2.6x more compressed scale than the
# rest of the map (ENNIS_Y could not be used to cross-check for the same
# reason). Left uncorrected, Maryland Hall would sit far past where Ennis
# Parallel/the rest of the modeled east campus ends. Rescaled here by /2.5
# (the middle of that ~2.4-2.6x range) relative to the KNOTT_X1/KNOTT_Y2
# anchor so the stub lands just past Ennis Parallel, consistent with the
# compressed geometry around it. Treat these values the way KNOTT_GROUND_Z
# used to be treated before its own re-derivation: a reasonable placeholder,
# not a verified measurement — re-derive against ref/ imagery before doing
# detailed facade work.
_MARYLAND_COMPRESSION = 2.5  # matches Ennis/east-campus's ~2.4-2.6x compression
_MARYLAND_X1_FULL_SCALE = 6385  # pre-compression OSM-derived value
_MARYLAND_X2_FULL_SCALE = 8979
_MARYLAND_Y1_FULL_SCALE = 412
_MARYLAND_Y2_FULL_SCALE = 1622
MARYLAND_X1 = KNOTT_X1 + round(
    (_MARYLAND_X1_FULL_SCALE - KNOTT_X1) / _MARYLAND_COMPRESSION
)
MARYLAND_X2 = KNOTT_X1 + round(
    (_MARYLAND_X2_FULL_SCALE - KNOTT_X1) / _MARYLAND_COMPRESSION
)
MARYLAND_Y1 = KNOTT_Y2 + round(
    (_MARYLAND_Y1_FULL_SCALE - KNOTT_Y2) / _MARYLAND_COMPRESSION
)
MARYLAND_Y2 = KNOTT_Y2 + round(
    (_MARYLAND_Y2_FULL_SCALE - KNOTT_Y2) / _MARYLAND_COMPRESSION
)
MARYLAND_FLOORS = 3  # real Maryland Hall is a 3-story academic building
MARYLAND_FLOOR_H = 128  # matches DORM_FLOOR_H; no facade detail derived yet
MARYLAND_H = MARYLAND_FLOORS * MARYLAND_FLOOR_H
# Ground level under the massing block. The hill keeps climbing east of Knott
# Hall (KNOTT_GROUND_Z=221) toward Ennis Parallel/Maryland Hall — re-measured
# via scripts/sample_elevation.py at +17.0 to +18.1 ft above the bridge-
# crossing baseline ("knott_climb_2".."knott_climb_4", 257 -> 273 units; see
# docs/elevation_samples.csv, current run). Without this, the stub sat flush
# with FLOOR_Z2 (0) and appeared sunk far below the surrounding terrain. 273
# is used as the far (Ennis-side) end of that climb ("ennis_parallel" /
# "knott_climb_4"), closest to Maryland Hall's real-world location.
MARYLAND_GROUND_Z = 273

# terrain/maryland.py — flat mound under/around the stub, sloping down to the
# surrounding FLOOR_Z2 plaza on all four sides so the building doesn't float
# on a bare cliff edge. MARGIN is the flat apron beyond the footprint before
# the slope starts; RAMP_W is the horizontal run of that slope — sized for a
# ~20.8° grade (291/768) so it's comfortably walkable in Quake, not the
# ~48.7° (291/256) wall the first pass produced. Both are rough placeholder
# values (no real-world grading data yet), sized only to stay clear of the
# Ennis Drive/east-campus features to the west (_EAST_FEATURES_X2=2976) and
# Ennis Road to the north (ENNIS_Y - ENNIS_HW=753) — see terrain/maryland.py
# for the actual geometry.
MARYLAND_TERRAIN_MARGIN = 192
MARYLAND_TERRAIN_RAMP_W = 768
