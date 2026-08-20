"""Shared world-scale and cross-area geometry constants."""

ARCH_SLAB_W = 32

A_SEGS = 16


FENCE_H = 96
FENCE_SPACING = 16

FLOOR_Z1, FLOOR_Z2 = -16, 0

INDENT = 80

SCALE = 15.108

WORLD_EAST_BUFFER = 512

# How far south Ennis Rd — and everything anchored to it, including the
# northeast terrain grid and the masonry entrance wall — is pulled from its
# surveyed offset off the bridge, to tighten the gap between Knott Hall and
# Ennis. The world's north boundary stays put, so the iron fence run that
# continues north of the wall simply grows by the same amount.
ENNIS_PULL_S = 200
