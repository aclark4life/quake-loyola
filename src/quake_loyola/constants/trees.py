"""Voxel tree profiles rendered by geometry.make_pixel_tree()."""

# ── Voxel tree profiles ──────────────────────────────────────────────────────
# Each profile is a list of strings rendered top-to-bottom (index 0 = crown tip).
# Characters: 'L' = leaf (GROUND), 'B' = branch (MULCH), 'T' = trunk (MULCH),
#             ' ' = empty.  All strings in a profile must be the same width.
# Rendered by geometry.make_pixel_tree() as two perpendicular crossed fins.
TREE_PROFILES: dict[str, list[str]] = {
    # Narrow columnar tree — Baltimore ginkgo / street tree style
    "street": [
        "  LLL  ",
        " LLLLL ",
        "LLLLLLL",
        " LLLLL ",
        "  LLL  ",
        "  BBB  ",
        "  TTT  ",
        "  TTT  ",
        "  TTT  ",
        "  TTT  ",
    ],
    # Broad-crowned deciduous tree — red maple / oak style
    "deciduous": [
        "   LLL   ",
        "  LLLLL  ",
        " LLLLLLL ",
        "LLLLLLLLL",
        " LLLLLLL ",
        "  LLLLL  ",
        "   LBL   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
    ],
    # Conifer — pine / fir style
    "pine": [
        "    L    ",
        "   LLL   ",
        "  LLLLL  ",
        " LLLLLLL ",
        "  LLLLL  ",
        " LLLLLLL ",
        "LLLLLLLLL",
        "   BBB   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
        "   TTT   ",
    ],
    # Large detailed broad-crown tree — fine voxels (vox_size=8), 26 cols × 41 rows.
    # At vox_size=8: 208 units wide crown, 328 units tall.
    # Crown (rows 0-25) drops straight to trunk (rows 26-40), no branch zone.
    "large": [
        "            LL            ",  # row  0 — sparse crown tip
        "          LLLLLL          ",  # row  1
        "        LLLLLLLLLL        ",  # row  2
        "      LLLLLLLLLLLLLL      ",  # row  3
        "    LLLLLLLLLLLLLLLLLL    ",  # row  4
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row  5
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row  6
        " LLLLLLLLLLLLLLLLLLLLLLLL ",  # row  7
        "LLLLLLLLLLLLLLLLLLLLLLLLL ",  # row  8 — slight asymmetry
        "LLLLLLLLLLLLLLLLLLLLLLLLLL",  # row  9 — widest
        "LLLLLLLLLLLLLLLLLLLLLLLLLL",  # row 10
        " LLLLLLLLLLLLLLLLLLLLLLLL ",  # row 11
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row 12
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row 13
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row 14 — second swell
        " LLLLLLLLLLLLLLLLLLLLLLLL ",  # row 15
        "LLLLLLLLLLLLLLLLLLLLLLLLLL",  # row 16
        " LLLLLLLLLLLLLLLLLLLLLLL  ",  # row 17 — asymmetric droop
        "  LLLLLLLLLLLLLLLLLLLLLL  ",  # row 18
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row 19
        "    LLLLLLLLLLLLLLLLLL    ",  # row 20
        "   LLLLLLLLLLLLLLLLLLLL   ",  # row 21 — natural bulge
        "    LLLLLLLLLLLLLLLLLL    ",  # row 22
        "      LLLLLLLLLLLLLL      ",  # row 23
        "       LLLLLLLLLLLL       ",  # row 24
        "        LLLLLLLLL         ",  # row 25 — lower crown
        "           TTTT           ",  # row 26 — trunk begins (no branch zone)
        "           TTTT           ",  # row 27
        "           TTTT           ",  # row 28
        "           TTTT           ",  # row 29
        "           TTTT           ",  # row 30
        "           TTTT           ",  # row 31
        "           TTTT           ",  # row 32
        "           TTTT           ",  # row 33
        "           TTTT           ",  # row 34
        "           TTTT           ",  # row 35
        "           TTTT           ",  # row 36
        "           TTTT           ",  # row 37
        "           TTTT           ",  # row 38
        "           TTTT           ",  # row 39
        "           TTTT           ",  # row 40 — base
    ],
}
