"""
knott_terrain — hill terrain surrounding Knott Hall.

Geometry that physically grounds the Knott Hall building:
  • Back-road driveway east of Knott Hall (road/sidewalks/curbed junction
    corners connecting to Ennis Drive) — flat, not tied to hill height.
  • Hill fill/ramp/entrance-staircase model — REMOVED pending re-derivation
    against real-world topology (see docs/reference.rst, "Topology check").
    The old model assumed a single flat plateau at KNOTT_GROUND_Z; the real
    terrain climbs continuously toward Ennis Parallel. See the TODO near the
    bottom of build() for what needs to be rebuilt.

Kept separate from bridge.py (bridge/walkway structure) and
knott_hall.py (building walls, floors, interior) so each module has
a single clear responsibility.
"""

import math

from .constants import (
    CHARLES_RAMP_W,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    ENNIS_CURB_W,
    ENNIS_HW,
    ENNIS_SW_EDGE,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT,
    KNOTT_DRIVEWAY_CURB_BULGE_D,
    KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W,
    KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W,
    KNOTT_DRIVEWAY_CURB_CRN_R,
    KNOTT_DRIVEWAY_CURB_CRN_SEGS,
    KNOTT_DRIVEWAY_ES_X1,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_EXT_Y1,
    KNOTT_DRIVEWAY_EXT_Y2,
    KNOTT_DRIVEWAY_JCX_E,
    KNOTT_DRIVEWAY_JCX_W,
    KNOTT_DRIVEWAY_JCY,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_WS_X1,
    KNOTT_DRIVEWAY_WS_X2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_TERRAIN_ENABLED,
    ROAD_X2,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
)
from .geometry import (
    box,
    curb_seg,
    ramp_slab,
    ramp_slab_y,
    tri_prism,
    tri_ramp_prism,
)


def build():
    if not KNOTT_TERRAIN_ENABLED:
        return [], []
    BRUSHES = []

    # Sidewalk slab parameters: slab length and expansion-joint gap in Y.
    _SW_SLAB_LEN = 128  # ~8.5 ft per slab
    _SW_GAP = 2  # expansion joint width

    def road_section(brushes, x1, x2, top_z_s, top_z_n, surface_tex):
        # Single full-depth sloped slab: GROUND on every face except the top,
        # which carries the surface texture. Previously this was a thin surface
        # overlay riding on a separate GROUND fill, but the overlay's bottom
        # plane was exactly coplanar with the fill's top plane along the whole
        # slope — qbsp dropped the 2-unit-thin overlay's top face in favour of
        # the coincident GROUND face, so the road/sidewalk rendered as dirt.
        # One brush textured top=surface, sides/bottom=GROUND keeps the same
        # look (GROUND on the visible sloped sides, surface only on top) with
        # no coplanar seam to trip.
        brushes.append(
            ramp_slab_y(
                x1,
                x2,
                KNOTT_DRIVEWAY_Y1,
                KNOTT_DRIVEWAY_Y2,
                FLOOR_Z1,
                FLOOR_Z1,
                top_z_s,
                top_z_n,
                Textures.GROUND,
                tt=surface_tex,
            )
        )

    def sidewalk_slabs_sloped(brushes, x1, x2, y1, y2, top_z_s, top_z_n, surface_tex):
        """Tile a sloped sidewalk (y1..y2) as individual slab brushes with small
        expansion-joint gaps, giving the look of real concrete sidewalk panels.
        Each slab is _SW_SLAB_LEN long; joints are _SW_GAP wide. The top Z is
        linearly interpolated across the full y1..y2 span per slab edge."""
        total = y2 - y1
        step = _SW_SLAB_LEN + _SW_GAP
        y = y1
        while y < y2:
            sy1 = y
            sy2 = min(y + _SW_SLAB_LEN, y2)
            t1 = (sy1 - y1) / total
            t2 = (sy2 - y1) / total
            tz1 = top_z_s + t1 * (top_z_n - top_z_s)
            tz2 = top_z_s + t2 * (top_z_n - top_z_s)
            brushes.append(
                ramp_slab_y(
                    x1,
                    x2,
                    sy1,
                    sy2,
                    FLOOR_Z1,
                    FLOOR_Z1,
                    tz1,
                    tz2,
                    Textures.GROUND,
                    tt=surface_tex,
                )
            )
            y += step

    def sidewalk_slabs_flat(brushes, x1, x2, y1, y2, z_base, z_top, surface_tex):
        """Tile a flat sidewalk (y1..y2) as individual slab brushes with small
        expansion-joint gaps."""
        step = _SW_SLAB_LEN + _SW_GAP
        y = y1
        while y < y2:
            sy1 = y
            sy2 = min(y + _SW_SLAB_LEN, y2)
            brushes.append(box(x1, sy1, z_base, x2, sy2, z_top, surface_tex))
            y += step

    # ══════════════════════════════════════════════════════════════════════════════
    # BACK ROAD — east of Knott Hall, slopes south to meet the back of the building
    # Sidewalks with rounded north entrance corners (like Ennis Drive)
    # Road surface — full-depth GROUND slab textured ROAD on top (see road_section)
    road_section(
        BRUSHES,
        KNOTT_DRIVEWAY_RD_X1,
        KNOTT_DRIVEWAY_RD_X2,
        KNOTT_DRIVEWAY_ZT_S + 2,
        KNOTT_DRIVEWAY_ZT_N + 2,
        Textures.ROAD,
    )

    # West sidewalk (strip between building east wall and road) — slopes with road
    # Cut into individual slab panels with expansion joints for a real sidewalk look.
    sidewalk_slabs_sloped(
        BRUSHES,
        KNOTT_DRIVEWAY_WS_X1,
        KNOTT_DRIVEWAY_WS_X2,
        KNOTT_DRIVEWAY_Y1,
        KNOTT_DRIVEWAY_Y2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.CEMENT,
    )

    # East sidewalk — slopes with road
    # Cut into individual slab panels with expansion joints.
    sidewalk_slabs_sloped(
        BRUSHES,
        KNOTT_DRIVEWAY_ES_X1,
        KNOTT_DRIVEWAY_ES_X2,
        KNOTT_DRIVEWAY_Y1,
        KNOTT_DRIVEWAY_Y2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.CEMENT,
    )

    # ── Real-elevation south-edge interpolation (KNOTT.x1 → east driveway) ──
    # Only two real USGS samples exist along KNOTT_DRIVEWAY_Y1 east of Knott
    # Hall's west wall: KNOTT.x1 itself (267 z-units above flat grade) and one
    # further east near the driveway's far side (368, at x≈2700). Linear
    # interpolation between them replaces the old flat KNOTT_DRIVEWAY_ZT_S tie
    # everywhere it's used along this Y line (south corner grid, west-sidewalk
    # strip, south extension ground fill below).
    _sgrid_z = FLOOR_Z2 + CHARLES_WALK_H
    _south_edge_x0, _south_edge_z0 = KNOTT.x1, 66
    _south_edge_x1, _south_edge_z1 = 2700, 92

    def _south_edge_real(x):
        t = (x - _south_edge_x0) / (_south_edge_x1 - _south_edge_x0)
        return _sgrid_z + _south_edge_z0 + t * (_south_edge_z1 - _south_edge_z0)

    # Real USGS samples also show the driveway's flanking ground keeps
    # changing well past KNOTT_DRIVEWAY_Y1, all the way to the world's south
    # edge — a shallow dip, not the flat KNOTT_DRIVEWAY_ZT_S plateau the old
    # code assumed. These Y-profiles (west column near KNOTT.x1, east column
    # near the driveway's east side) drive the re-derived south extension
    # ground fills further below; the paved driveway lane and its sidewalks
    # (RD, WS, ES) are left flat — engineered/graded, no contrary evidence.
    _far_south_y = [KNOTT_DRIVEWAY_Y1, -3000, -4500, WORLD_Y1 + WALL_T]
    _far_south_z_west = [66, 44, 46, 31]  # real samples at x≈KNOTT.x1
    _far_south_z_east = [92, 57, 60, 35]  # real samples at x≈2700 (east of ES)
    # A chain of 3+ Y-segments sharing exact coincident boundary edges (each
    # segment's south edge = the next segment's north edge, bit-for-bit
    # identical XYZ) trips a qbsp portal-building edge case that produces a
    # real leak — confirmed by bisection: removing any single segment from an
    # otherwise-complete 3-segment column makes the leak vanish, but any
    # combination that leaves all 3 stacked and exactly coincident leaks
    # again. Every loop below that walks _far_south_y in 3+ segments extends
    # each non-final segment's south edge by _WRAMP_OVR units past its
    # "official" boundary (linearly extrapolating its own ramp slope for the
    # extra sliver), so consecutive segments overlap by a hair instead of
    # meeting on an exact shared plane.
    _WRAMP_OVR = 4

    # South corner grid (real-elevation, X=verge..KNOTT.x1 at Y1/Y2) and its
    # X-interpolation helper — moved up here (ahead of where its brushes are
    # actually emitted, further below) because the south extension and west-
    # sidewalk pieces above also need to read real Y2-edge heights from it.
    _charles_verge_x2 = ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W
    _sgrid = [
        # (x, z_at_y1, z_at_y2)
        (_charles_verge_x2, _sgrid_z, _sgrid_z),  # verge — tied flat both ends
        (700, _sgrid_z + 54, _sgrid_z + 68),  # 217 real (y=-1888); 275 interpolated
        (900, _sgrid_z + 59, _sgrid_z + 88),  # 237 interpolated; 352 real (y=-233)
        (
            KNOTT.x1,
            _sgrid_z + 66,
            _sgrid_z + 92,
        ),  # 267 real (y=-1888); 370 real (y=-233)
    ]

    def _south_edge_z(x):
        """Real-elevation Y2 (KNOTT_DRIVEWAY_Y2) boundary height at X, from
        the south-corner grid (_sgrid) — NOT flat. USGS samples there (e.g.
        +352 z-units at X=900) show the ground keeps climbing toward the
        driveway rather than tapering to grade, so this strip's south edge
        must match that instead of assuming flat_z."""
        for (gx1, _, gz1b), (gx2, _, gz2b) in zip(_sgrid, _sgrid[1:]):
            if gx1 <= x <= gx2:
                t = (x - gx1) / (gx2 - gx1) if gx2 != gx1 else 0.0
                return gz1b + t * (gz2b - gz1b)
        if x <= KNOTT.x1:
            return _sgrid[-1][2]
        # Beyond KNOTT.x1: taper linearly from the real value there down to
        # flat sidewalk grade by KNOTT_DRIVEWAY_WS_X1 — matching the "west of
        # west sidewalk" strip's own Y2 edge (built below), which tapers the
        # same way across this same X range.
        t = (x - KNOTT.x1) / (KNOTT_DRIVEWAY_WS_X1 - KNOTT.x1)
        t = min(max(t, 0.0), 1.0)
        return _sgrid[-1][2] + t * (_sgrid_z - _sgrid[-1][2])

    # Real elevation on both flanks of the driveway stays well above the
    # flat, engineered sidewalks/road (e.g. +353 z-units at KNOTT_DRIVEWAY_WS_X1,
    # Y1) — holding real elevation all the way to the sidewalk edge left an
    # unclimbable ~120-350 unit wall. A buffer zone tapers real elevation
    # back down to the sidewalk/road's own flat or sloped height instead,
    # turning that wall into a steep bank. Used by the south extension ground
    # fills (below) and the west/east-of-sidewalk strips (further below).
    _WS_TAPER_W = 200
    _ws_taper_x = KNOTT_DRIVEWAY_WS_X1 - _WS_TAPER_W
    _ES_TAPER_W = 200
    _es_taper_x = KNOTT_DRIVEWAY_ES_X2 + _ES_TAPER_W

    def _sidewalk_h(y):
        """Height of the WS/ES driveway sidewalks at Y (Y1..Y2 sloped range)."""
        t = (y - KNOTT_DRIVEWAY_Y1) / (KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1)
        zs = KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H
        zn = KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H
        return zs + t * (zn - zs)

    # Terrain east of east sidewalk — south flat + sloped main section matching sidewalk
    # South extension: re-derived from real elevation (was flat at hill level).
    # As with the west side, a taper buffer (_es_taper_x) eases the ground back
    # down to the sidewalk's flat height near ES_X2 instead of a sheer wall.
    # Unlike the west side, the real sample here was only taken at one X
    # (≈2700, just west of ES_X2) so it's treated as X-uniform beyond the
    # taper zone; the taper itself uses tri_ramp_prism (two triangles) so the
    # transition from flat to real is a gradual slope, not an abrupt step.
    _eg_flat = _sidewalk_h(KNOTT_DRIVEWAY_Y1)  # flat south of Y1, same as ES sidewalk
    for _seg_i, ((y1, z1), (y2, z2)) in enumerate(
        zip(
            zip(_far_south_y, _far_south_z_east),
            zip(_far_south_y[1:], _far_south_z_east[1:]),
        )
    ):
        ra1 = _sgrid_z + z1
        ra2 = _sgrid_z + z2
        # See _WRAMP_OVR note near the top of build() — overlap non-final
        # segments to avoid the qbsp coincident-boundary leak.
        if _seg_i < len(_far_south_y) - 2:
            y2_ext = y2 - _WRAMP_OVR
            ra2 = ra1 + (ra2 - ra1) * (y2_ext - y1) / (y2 - y1)
            y2 = y2_ext
        # Note: y2 < y1 here (_far_south_y decreases going south), the
        # opposite direction from the driveway-zone grids (Y1->Y2
        # increasing) elsewhere in this file — tri_ramp_prism requires its
        # (A,B,C) triangle to be CCW from above, so B/C (and their z values)
        # are swapped relative to those north-going grids to keep the
        # winding correct. Getting this backwards produces a brush qbsp
        # silently drops ("Couldn't create brush faces"), leaving a hole.
        BRUSHES.append(
            tri_ramp_prism(
                KNOTT_DRIVEWAY_ES_X2,
                y1,
                _es_taper_x,
                y2,
                _es_taper_x,
                y1,
                FLOOR_Z1,
                _eg_flat,
                ra2,
                ra1,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            tri_ramp_prism(
                KNOTT_DRIVEWAY_ES_X2,
                y1,
                KNOTT_DRIVEWAY_ES_X2,
                y2,
                _es_taper_x,
                y2,
                FLOOR_Z1,
                _eg_flat,
                _eg_flat,
                ra2,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            ramp_slab_y(
                _es_taper_x,
                WORLD_X2_EXT - WALL_T,
                y1,
                y2,
                FLOOR_Z1,
                FLOOR_Z1,
                ra1,
                ra2,
                Textures.GROUND,
                tt=Textures.GROUND,
            )
        )
    # Main back road section: slopes with the sidewalk. Y1 (south) edge now
    # ties to the real-elevation value used by the south extension fill below
    # (368 real, at x≈2700) instead of the old flat KNOTT_DRIVEWAY_ZT_S
    # assumption — avoids reintroducing a cliff at their shared Y1 seam. Also
    # tapered near ES_X2 (_es_taper_x) for the same reason as the south
    # extension fill above, using tri_ramp_prism so the flat-sidewalk-to-real
    # transition is gradual (not a step).
    _mr_z1s = _sidewalk_h(KNOTT_DRIVEWAY_Y1)
    _mr_z2s = _sidewalk_h(KNOTT_DRIVEWAY_Y2)
    _mr_z1r = _sgrid_z + _far_south_z_east[0]
    _mr_z2r = KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H
    BRUSHES.append(
        tri_ramp_prism(
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y1,
            _es_taper_x,
            KNOTT_DRIVEWAY_Y1,
            _es_taper_x,
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z1,
            _mr_z1s,
            _mr_z1r,
            _mr_z2r,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        tri_ramp_prism(
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y1,
            _es_taper_x,
            KNOTT_DRIVEWAY_Y2,
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z1,
            _mr_z1s,
            _mr_z2r,
            _mr_z2s,
            Textures.GROUND,
        )
    )
    BRUSHES.append(
        ramp_slab_y(
            _es_taper_x,
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            _sgrid_z + _far_south_z_east[0],
            KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    # ── South extension — ground behind Knott Hall, driveway + sidewalks continue south ──
    # The top of the hill south of the building is ground, not roadway; only the
    # actual driveway lane (RD_X1-RD_X2) and its flanking sidewalks (WS, ES)
    # extend back to the south world edge. The west ground fill is re-derived
    # from real elevation using a 4-column X grid (KNOTT.x1, 1650, 2100,
    # KNOTT_DRIVEWAY_WS_X1) — USGS EPQS samples at all 4 columns (see the
    # south_audit_* rows in docs/elevation_samples.csv) show real elevation
    # doesn't taper linearly from a single KNOTT.x1 sample the way the
    # original single-column-plus-taper version assumed; that undersampling
    # overshot real ground by 25-75 z-units in the middle of this strip. The
    # last column (KNOTT_DRIVEWAY_WS_X1) is held flat at the WS sidewalk's own
    # grade — no contrary evidence for the paved sidewalk itself — so real
    # elevation still eases down to it over the final ~400 units, same idea
    # as the taper used elsewhere, just backed by real samples the rest of
    # the way instead of a single extrapolated slope.
    _wg_flat = _sidewalk_h(KNOTT_DRIVEWAY_Y1)  # flat south of Y1
    _wg2_x = [KNOTT.x1, 1650, 2100, KNOTT_DRIVEWAY_WS_X1]
    _wg2_cols = [
        _far_south_z_west,
        [61, 48, 49, 32],  # real samples at x=1650
        [77, 51, 49, 32],  # real samples at x=2100
        [_wg_flat - _sgrid_z] * 4,  # flat WS sidewalk grade, all Y
    ]
    for (gx1, gcol1), (gx2, gcol2) in zip(
        zip(_wg2_x, _wg2_cols), zip(_wg2_x[1:], _wg2_cols[1:])
    ):
        for _seg_i in range(len(_far_south_y) - 1):
            y1, y2 = _far_south_y[_seg_i], _far_south_y[_seg_i + 1]
            gz1a = _sgrid_z + gcol1[_seg_i]
            gz1b = _sgrid_z + gcol1[_seg_i + 1]
            gz2a = _sgrid_z + gcol2[_seg_i]
            gz2b = _sgrid_z + gcol2[_seg_i + 1]
            # See _WRAMP_OVR note near the top of build() — overlap non-final
            # segments to avoid the qbsp coincident-boundary leak.
            if _seg_i < len(_far_south_y) - 2:
                y2_ext = y2 - _WRAMP_OVR
                t_ext = (y2_ext - y1) / (y2 - y1)
                gz1b = gz1a + (gz1b - gz1a) * t_ext
                gz2b = gz2a + (gz2b - gz2a) * t_ext
                y2 = y2_ext
            # Note: y2 < y1 here (_far_south_y decreases going south) — the
            # opposite direction from the driveway-zone grids elsewhere in
            # this file, so B/C (and their z values) are swapped relative to
            # those north-going grids to keep the CCW winding tri_ramp_prism
            # requires. See the matching note in the east-side loop above.
            BRUSHES.append(
                tri_ramp_prism(
                    gx1,
                    y1,
                    gx2,
                    y2,
                    gx2,
                    y1,
                    FLOOR_Z1,
                    gz1a,
                    gz2b,
                    gz2a,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_ramp_prism(
                    gx1,
                    y1,
                    gx1,
                    y2,
                    gx2,
                    y2,
                    FLOOR_Z1,
                    gz1a,
                    gz1b,
                    gz2b,
                    Textures.GROUND,
                )
            )
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_WS_X1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            KNOTT_DRIVEWAY_WS_X2,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_RD_X1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            KNOTT_DRIVEWAY_RD_X2,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_ZT_S + 2,
            Textures.ROAD,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── West ramp — blend the hill terrain back down to Charles St grade ───────
    # KNOTT_GROUND_Z (re-derived from real elevation data) sits well above the
    # Charles St sidewalk verge (streets.py, flush at FLOOR_Z2+CHARLES_WALK_H),
    # and nothing currently fills the gap between the verge's east edge and
    # KNOTT.x1 — without this, that gap is a sheer, unwalkable cliff.
    #
    # Two pieces close it:
    #  1. A flat-cross-section ramp for the south extension's Y range (where the
    #     hill sits at a constant KNOTT_GROUND_Z), sloping X from the verge edge
    #     up to KNOTT.x1.
    #  2. A tetrahedral corner ramp for the back-road's Y range, where the hill
    #     height itself already tapers from KNOTT_GROUND_Z (south) down to
    #     FLOOR_Z2 (north, at Ennis) — the wedge's apex sits at the hill's tall
    #     south corner and falls to grade on both the west (Charles) and north
    #     (Ennis) edges simultaneously, matching that taper instead of leaving a
    #     second cliff where a flat ramp would meet the sloped driveway.
    #
    # Both ends must be raised by CHARLES_WALK_H to be flush with the actual
    # verge/hilltop surfaces (which both ride CHARLES_WALK_H above their base
    # Z), not the bare FLOOR_Z2/KNOTT_GROUND_Z anchors — otherwise this ramp
    # sits a full curb-height below the ground it's supposed to connect.
    #
    # This piece's Y range (WORLD_Y1+WALL_T to KNOTT_DRIVEWAY_Y1) is re-derived
    # from real elevation samples at X=700 rather than held flat at
    # KNOTT_GROUND_Z: real data shows this strip also declines toward the
    # world's south edge (217 → 149 → 158 → 125, in the same z-unit scale used
    # throughout), not a constant plateau. The west (verge) edge stays tied to
    # flat grade — same simplification used elsewhere. A full X-grid (verge,
    # 700, 900, KNOTT.x1 — the same X breakpoints as _sgrid above) is used
    # instead of a simple 2-column interpolation: a straight verge→KNOTT.x1
    # line undershoots the real X=700/900 samples by ~100+ units (they sit on
    # a locally steeper rise, same shape as _sgrid immediately north of this
    # piece), which left a cliff right at the KNOTT_DRIVEWAY_Y1 seam between
    # this piece and _sgrid. The X=900 column has no south-side survey data,
    # so it's linearly interpolated between the real 700/1206 columns —
    # matching how _sgrid's own X=900 point was derived.
    _wg_t900 = (900 - 700) / (KNOTT.x1 - 700)
    _wgrid_z900 = [
        z700 + _wg_t900 * (z1206 - z700)
        for z700, z1206 in zip([54, 37, 39, 31], _far_south_z_west)
    ]
    _wgrid_x = [_charles_verge_x2, 700, 900, KNOTT.x1]
    _wgrid_cols = [
        [0, 0, 0, 0],
        [108, 74, 79, 62],
        _wgrid_z900,
        _far_south_z_west,
    ]
    # A chain of 3+ Y-segments sharing exact coincident boundary edges (each
    # segment's south edge = the next segment's north edge, bit-for-bit
    # identical XYZ) trips a qbsp portal-building edge case that produces a
    # real leak — confirmed by bisection: removing any single segment from an
    # otherwise-complete 3-segment column makes the leak vanish, but any
    # combination that leaves all 3 stacked and exactly coincident leaks
    # again. Nudging just the shared Y value didn't help either (the
    # coincidence is inherent to stacking flush segments, not tied to one
    # specific Y). See _WRAMP_OVR note near the top of build() — overlap
    # non-final segments to avoid the leak.
    for (wx1, wcol1), (wx2, wcol2) in zip(
        zip(_wgrid_x, _wgrid_cols), zip(_wgrid_x[1:], _wgrid_cols[1:])
    ):
        for i in range(len(_far_south_y) - 1):
            y1, y2 = _far_south_y[i], _far_south_y[i + 1]
            z1a, z1b = wcol1[i], wcol1[i + 1]
            z2a, z2b = wcol2[i], wcol2[i + 1]
            if i < len(_far_south_y) - 2:
                y2_ext = y2 - _WRAMP_OVR
                z1b = z1a + (z1b - z1a) * (y2_ext - y1) / (y2 - y1)
                z2b = z2a + (z2b - z2a) * (y2_ext - y1) / (y2 - y1)
                y2 = y2_ext
            # Note: y2 < y1 here (_far_south_y decreases going south) —
            # B/C (and their z values) are swapped relative to north-going
            # grids to keep the CCW winding tri_ramp_prism requires. See the
            # matching note in the south-extension loops above.
            BRUSHES.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx2,
                    y2,
                    wx2,
                    y1,
                    FLOOR_Z1,
                    _sgrid_z + z1a,
                    _sgrid_z + z2b,
                    _sgrid_z + z2a,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx1,
                    y2,
                    wx2,
                    y2,
                    FLOOR_Z1,
                    _sgrid_z + z1a,
                    _sgrid_z + z1b,
                    _sgrid_z + z2b,
                    Textures.GROUND,
                )
            )
    # ── South corner fill — real-elevation grid, replacing the old single-
    # apex corner_ramp ──
    # USGS EPQS samples across this footprint (docs/elevation_samples.csv)
    # show the real hillside does NOT taper down to grade approaching the
    # back-road/Ennis corridor (Y2) — if anything it climbs further, cresting
    # somewhere around Y=-1060 — so a single tetrahedral ramp falling to grade
    # on both far edges (the old corner_ramp call) was actively wrong here,
    # not just an approximation. This replaces it with a small triangulated
    # grid tied to real samples at (700/900/1206, -1888/-233), using a
    # flat-grade tie at the verge (X=400) to match the unconditional flat
    # Charles St sidewalk immediately west of it (same simplification used
    # for the north hill fill above — real data shows the verge itself isn't
    # flat either, but changing streets.py's sidewalk grade is out of scope
    # here). The Y1 edge (KNOTT_DRIVEWAY_Y1) now uses the real sample there
    # (267) rather than the old flat KNOTT_GROUND_Z tie-in, since the deep-
    # south ground fill below has also been re-derived from real data and
    # ties to this same value — no more seam to avoid. (_sgrid itself is
    # defined near the top of this function — needed earlier by the south
    # extension and west-sidewalk pieces above.)
    for (gx1, gz1a, gz1b), (gx2, gz2a, gz2b) in zip(_sgrid, _sgrid[1:]):
        BRUSHES.append(
            tri_ramp_prism(
                gx1,
                KNOTT_DRIVEWAY_Y1,
                gx2,
                KNOTT_DRIVEWAY_Y1,
                gx2,
                KNOTT_DRIVEWAY_Y2,
                FLOOR_Z1,
                gz1a,
                gz2a,
                gz2b,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            tri_ramp_prism(
                gx1,
                KNOTT_DRIVEWAY_Y1,
                gx2,
                KNOTT_DRIVEWAY_Y2,
                gx1,
                KNOTT_DRIVEWAY_Y2,
                FLOOR_Z1,
                gz1a,
                gz2b,
                gz1b,
                Textures.GROUND,
            )
        )

    # ── Terrain west of west sidewalk — mirrors "Terrain east of east sidewalk" ──
    # Fills the building-footprint strip between Knott Hall's west edge and the
    # driveway's west sidewalk. Its west edge (KNOTT.x1) must match the new
    # real-elevation south-corner grid built above — that grid now reaches a
    # real +370 z-units at (KNOTT.x1, KNOTT_DRIVEWAY_Y2), not the old flat
    # KNOTT_DRIVEWAY_ZT_N assumption, so keeping this strip's own old
    # X-uniform ramp_slab_y (same height across its whole width, regardless
    # of X) left a steep cliff right at KNOTT.x1 where the two met. The Y1
    # edge now also uses real-elevation values (_south_edge_real, defined
    # near the top of this function) instead of the old flat
    # KNOTT_DRIVEWAY_ZT_S assumption, matching the re-derived south corner
    # grid and south extension ground fill.
    #
    # Real elevation stays well above the flat, engineered driveway sidewalk
    # right up to its edge (e.g. +353 at KNOTT_DRIVEWAY_WS_X1, Y1) — holding
    # that all the way to X=WS_X1 left an unclimbable ~120-350 unit wall
    # against the sidewalk. A buffer zone (_WS_TAPER_W wide, defined near the
    # top of this function) tapers the real elevation back down to the
    # sidewalk's own sloped height (matching road_section's ZT_S→ZT_N slope
    # exactly) instead, turning that wall into a steep bank.
    for wx1, wx2 in ((KNOTT.x1, _ws_taper_x), (_ws_taper_x, KNOTT_DRIVEWAY_WS_X1)):
        real_edge = wx2 == KNOTT_DRIVEWAY_WS_X1
        z1a = _south_edge_real(wx1) if wx1 != KNOTT.x1 else _south_edge_real(KNOTT.x1)
        z1b = _sidewalk_h(KNOTT_DRIVEWAY_Y1) if real_edge else _south_edge_real(wx2)
        z2a = _sgrid[-1][2] if wx1 == KNOTT.x1 else _south_edge_z(wx1)
        z2b = _sidewalk_h(KNOTT_DRIVEWAY_Y2) if real_edge else _south_edge_z(wx2)
        BRUSHES.append(
            tri_ramp_prism(
                wx1,
                KNOTT_DRIVEWAY_Y1,
                wx2,
                KNOTT_DRIVEWAY_Y1,
                wx2,
                KNOTT_DRIVEWAY_Y2,
                FLOOR_Z1,
                z1a,
                z1b,
                z2b,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            tri_ramp_prism(
                wx1,
                KNOTT_DRIVEWAY_Y1,
                wx2,
                KNOTT_DRIVEWAY_Y2,
                wx1,
                KNOTT_DRIVEWAY_Y2,
                FLOOR_Z1,
                z1a,
                z2b,
                z2a,
                Textures.GROUND,
            )
        )

    # ── Terrain south of Ennis, east of Charles verge, west of the driveway ──
    # Fills the gap between the Charles St verge and the driveway's west
    # sidewalk, north of Knott Hall's footprint up to Ennis's south sidewalk.
    #
    # This strip's X range (verge..KNOTT_DRIVEWAY_WS_X1) spans directly under
    # the bridge's centre-span/east-approach corridor, and real elevation data
    # (docs/elevation_samples.csv "pier2_center_span_w".."knott_west_edge",
    # sampled along Y=0) shows the ground climbing ~20 ft from the Charles St
    # verge to Knott Hall's west edge, cresting and levelling off around
    # X=900 — not the flat plateau this used to be modelled as. Because all
    # of that survey data was taken along a single Y=0 line, the same X
    # profile is held for the whole Y range north of Y=0
    # (0..ENNIS_SW_EDGE) as a flat-in-Y plateau, and blended down to grade
    # south of Y=0 via a continuously *triangulated* ramp (below) rather than
    # stacked flat-topped tiers — a tiered design leaves a visible cliff at
    # every tier seam (a flat top can only step, never taper, in Y), whereas
    # triangulating each X-segment's south-to-north strip into two planar
    # wedges gives an exact, seamless slope: adjacent wedges share an edge
    # and that edge's corner heights outright, so there's no join to crack.
    #
    # Stops at ENNIS_SW_EDGE (the sidewalk's own south edge), not
    # ENNIS_SW_EDGE + CHARLES_WALK_W (its north edge) — the unconditional
    # Ennis south sidewalk strip built in streets.py already occupies that
    # CHARLES_WALK_W-wide band; overshooting into it buried the sidewalk
    # under this GROUND fill. streets.py's own verge fill picks up again
    # north of the sidewalk, so no gap is left.
    _flat_z = (
        FLOOR_Z2 + CHARLES_WALK_H
    )  # grade this strip tapers from at its south edge
    # (X, real Z units above the bridge-crossing baseline) — from
    # docs/elevation_samples.csv, Y=0 samples "pier2_center_span_w" (X=-525,
    # here re-anchored at the verge) through "knott_west_edge" (X=1206); held
    # flat from there to KNOTT_DRIVEWAY_WS_X1 (no Y=0 survey data past 1206,
    # and the 900-1206 ft samples already show the climb levelling off).
    #
    # The box's own west edge sits at _charles_verge_x2 — the hard boundary
    # with the (flat, road-grade) Charles St verge fill to its west. The real
    # X=400 sample is already +7.96 ft up, so anchoring the profile's very
    # first point there would butt a ~120-unit vertical wall straight against
    # flat sidewalk grade. Tying the profile to grade right at the edge and
    # reaching the real X=400 sample by a short interior offset (480) instead
    # keeps the same real data but turns that wall into a steep-but-sloped toe.
    _hill_profile = [
        (_charles_verge_x2, 0),  # tie to grade at the verge — no cliff at the box edge
        (_charles_verge_x2 + 80, 30),  # real X=400 sample, offset in to slope the toe
        (525, 42),  # Pier 3 (bridge centre-span east pier)
        (700, 67),
        (900, 78),  # crest — real elevation levels off from here on
        (KNOTT.x1, 78),  # X=1206, Knott Hall west edge
        # Taper down to flat sidewalk grade by KNOTT_DRIVEWAY_WS_X1 instead
        # of holding flat — the WS/RD/ES driveway junction north of Y2 (see
        # "West sidewalk — cement..." etc. below) is a paved, flat corridor
        # that runs the length of this hill's whole Y range (Y2 to Ennis),
        # and holding this profile flat all the way to the sidewalk left a
        # ~300-unit unclimbable cliff at its west edge for that entire
        # stretch. No real Y=0 survey data exists past X=1206 anyway.
        (KNOTT_DRIVEWAY_WS_X1, 0),
    ]

    def _hill_z(x):
        """Absolute model Z of the real-world hill profile at X (grade +
        piecewise-linear rise above it)."""
        for (px1, pz1), (px2, pz2) in zip(_hill_profile, _hill_profile[1:]):
            if px1 <= x <= px2:
                t = (x - px1) / (px2 - px1) if px2 != px1 else 0.0
                return _flat_z + pz1 + t * (pz2 - pz1)
        return _flat_z + _hill_profile[-1][1]

    # South of Y=0: continuous triangulated ramp from flat grade (matching

    # South of Y=0: continuous triangulated ramp from the south-corner grid's
    # real (non-flat) Y2 height up to the full X-profile by Y=0 — well south
    # of the bridge deck's own Y=-148..148 span, so the whole bridge sits on
    # fully-risen hill. Each X-segment's strip splits into two CCW triangles
    # sharing the diagonal from (px1, KNOTT_DRIVEWAY_Y2) to (px2, 0); their
    # outer edges match the south grid and the X-profile exactly, so
    # neighbouring segments and the Y=0 plateau join with no step.
    for (px1, _), (px2, _) in zip(_hill_profile, _hill_profile[1:]):
        z1, z2 = _hill_z(px1), _hill_z(px2)
        zs1, zs2 = _south_edge_z(px1), _south_edge_z(px2)
        BRUSHES.append(
            tri_ramp_prism(
                px1,
                KNOTT_DRIVEWAY_Y2,
                px2,
                KNOTT_DRIVEWAY_Y2,
                px2,
                0,
                FLOOR_Z1,
                zs1,
                zs2,
                z2,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            tri_ramp_prism(
                px1,
                KNOTT_DRIVEWAY_Y2,
                px2,
                0,
                px1,
                0,
                FLOOR_Z1,
                zs1,
                z2,
                z1,
                Textures.GROUND,
            )
        )
        # North of Y=0: mirror the south transition, tapering back down to
        # grade by ENNIS_SW_EDGE — the Ennis south sidewalk (streets.py)
        # sits flat there, so holding this strip at full height all the way
        # out to that line (as a flat plateau) left a cliff at the seam.
        # Real Y=0 samples don't cover this stretch, but campus quads
        # typically crest near the middle and slope down on both sides, so
        # mirroring the south ramp's shape is the best available approximation.
        BRUSHES.append(
            tri_ramp_prism(
                px1,
                0,
                px2,
                0,
                px2,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                z1,
                z2,
                _flat_z,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            tri_ramp_prism(
                px1,
                0,
                px2,
                ENNIS_SW_EDGE,
                px1,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                z1,
                _flat_z,
                _flat_z,
                Textures.GROUND,
            )
        )

    # ── Flat extension north from Knott Hall to Ennis south sidewalk ──────────────
    # Flat road surface
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_RD_X1,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_RD_X2,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )
    # West sidewalk — cement from back road up to the E/W Ennis approach sidewalk
    # Cut into slab panels with expansion joints for a real sidewalk look.
    sidewalk_slabs_flat(
        BRUSHES,
        KNOTT_DRIVEWAY_WS_X1,
        KNOTT_DRIVEWAY_WS_X2,
        KNOTT_DRIVEWAY_EXT_Y1,
        ENNIS_SW_EDGE + CHARLES_WALK_W,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.CEMENT,
    )
    # West sidewalk — ground from E/W Ennis approach sidewalk to NW junction
    # corner. The corner (and this sidewalk/curb pair) are pushed north by
    # KNOTT_DRIVEWAY_CURB_BULGE_D here — extending the curb north rather than
    # bulging its road-facing edge east — so the ground/curb both run up to
    # _west_ext_y2 instead of the unmodified KNOTT_DRIVEWAY_EXT_Y2.
    _west_ext_y2 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_BULGE_D
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_WS_X1,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
            _west_ext_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    # Cement curb strip along road edge of the ground section — thin (width
    # unchanged at ENNIS_CURB_W), just extended north alongside the ground.
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_WS_X2,
            _west_ext_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # East sidewalk — cement from back road down to E/W Ennis approach sidewalk
    # Cut into slab panels with expansion joints.
    sidewalk_slabs_flat(
        BRUSHES,
        KNOTT_DRIVEWAY_ES_X1,
        KNOTT_DRIVEWAY_ES_X2,
        KNOTT_DRIVEWAY_EXT_Y1,
        ENNIS_SW_EDGE + CHARLES_WALK_W,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.CEMENT,
    )
    # East sidewalk — mulch from E/W sidewalk to NE junction corner. Mirrors
    # the NW corner's push-north-by-KNOTT_DRIVEWAY_CURB_BULGE_D treatment, so
    # the mulch/curb both run up to _east_ext_y2 instead of the unmodified
    # KNOTT_DRIVEWAY_EXT_Y2.
    _east_ext_y2 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_BULGE_D
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_ES_X2,
            _east_ext_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.MULCH,
        )
    )
    # Cement curb strip on road-facing (west) edge of the mulch section
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
            _east_ext_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # Terrain east of east sidewalk — flat, level with the adjacent sidewalk
    # (FLOOR_Z2 + CHARLES_WALK_H) rather than climbing toward Ennis Parallel.
    # The previous version rose ~29 units toward the NE corner, leaving a step
    # where it met the flat mulch/cement sidewalk directly to its west.
    #
    # Split at the NE bulge's east edge (_e_taper_x1, defined further down)
    # so the strip directly behind the bulge (KNOTT_DRIVEWAY_ES_X2 to
    # _e_taper_x1) stops at the sidewalk's own south edge (ENNIS_SW_EDGE +
    # CHARLES_WALK_W) instead of KNOTT_DRIVEWAY_EXT_Y2 — leaving room for the
    # widened mulch fill (below) to reach all the way south, flush with the
    # NE corner sidewalk section, without overlapping this GROUND terrain.
    _e_bulge_x2 = (
        KNOTT_DRIVEWAY_JCX_E
        + KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W
        + KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W
    )
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z1,
            _e_bulge_x2,
            ENNIS_SW_EDGE,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    # Sidewalk headed east from the NE corner, at (2973, 528) — continues the
    # E/W Ennis approach sidewalk band (ENNIS_SW_EDGE to +CHARLES_WALK_W),
    # already CEMENT west of the driveway, out to the mulch bed's edge
    # (_e_bulge_x2) instead of leaving this stretch as bare GROUND.
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_JCX_E,
            ENNIS_SW_EDGE,
            FLOOR_Z2,
            _e_bulge_x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        box(
            _e_bulge_x2,
            KNOTT_DRIVEWAY_EXT_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )

    # Road patch filling the gap between back road end (Y=328) and Ennis road (Y=408)
    # (This was previously the Ennis south sidewalk; now it's part of the road junction)
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_RD_X1,
            KNOTT_DRIVEWAY_EXT_Y2,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_RD_X2,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )

    # ── Rounded corners where back road meets Ennis south (inside the junction) ───
    # Centers at the back-road-facing (south) corners so the curved face points toward
    # the back road — matching the Charles/Ennis corner style.
    # West junction corner: center at SW corner (1906, 328), arc sweeps 0°→90°
    # — background pushed north (and its far edge extended) to match the
    # corner's new center at _west_ext_y2.
    _west_jc_y2 = max(KNOTT_DRIVEWAY_JCY, _west_ext_y2 + KNOTT_DRIVEWAY_CURB_CRN_R)
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_WS_X1,
            _west_ext_y2,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_RD_X1,
            _west_jc_y2,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )
    # Radii unchanged from the base corner size — only the center (Y anchor)
    # moves north, so the curve itself doesn't bulge east; the arc's own
    # curvature (X shrinks back toward JCX_W as angle sweeps to 90°) is what
    # "slopes back to the curb" heading west.
    _r_outer = KNOTT_DRIVEWAY_CURB_CRN_R
    _r_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
    _seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
    # GROUND fill — pie slices from centre to INNER radius only
    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        a0 = corner_index * _seg_deg
        a1 = (corner_index + 1) * _seg_deg
        t0, t1 = math.radians(a0), math.radians(a1)
        BRUSHES.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_W,
                _west_ext_y2,
                KNOTT_DRIVEWAY_JCX_W + _r_inner * math.cos(t0),
                _west_ext_y2 + _r_inner * math.sin(t0),
                KNOTT_DRIVEWAY_JCX_W + _r_inner * math.cos(t1),
                _west_ext_y2 + _r_inner * math.sin(t1),
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
    # CEMENT curb ring — inner to outer radius, wedge segments with tangent-plane faces
    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        a0 = corner_index * _seg_deg
        a1 = (corner_index + 1) * _seg_deg
        BRUSHES.append(
            curb_seg(
                KNOTT_DRIVEWAY_JCX_W,
                _west_ext_y2,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                _r_inner,
                _r_outer,
                a0,
                a1,
                Textures.CEMENT,
            )
        )

    # Flat continuation west from the top of the curve, before sloping back
    # down — matches curve-top height for KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W.
    _peak_out_x, _peak_out_y = KNOTT_DRIVEWAY_JCX_W, _west_ext_y2 + _r_outer
    _peak_in_x, _peak_in_y = KNOTT_DRIVEWAY_JCX_W, _west_ext_y2 + _r_inner
    _base_out_y = KNOTT_DRIVEWAY_EXT_Y2 + _r_outer
    _base_in_y = KNOTT_DRIVEWAY_EXT_Y2 + _r_inner
    _flat_x1 = KNOTT_DRIVEWAY_JCX_W - KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W
    BRUSHES.append(
        box(
            _flat_x1,
            _peak_in_y,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_JCX_W,
            _peak_out_y,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        box(
            _flat_x1,
            _base_in_y,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_JCX_W,
            _peak_in_y,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    # Straight closing curb — slopes back down to the pre-bulge corner-top
    # position (JCX_W - FLAT_W - KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W offset,
    # EXT_Y2 + CRN_R) over a longer run than the bulge depth itself, for a
    # more subtle (gentler) slope. That landing point lines up flush with
    # the existing Charles/Ennis verge fill's north edge (streets.py), so
    # the GROUND wedge filled in behind the curb closes seamlessly with no
    # gap or overlap.
    _taper_x0 = _flat_x1 - KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W
    BRUSHES.append(
        tri_prism(
            _flat_x1,
            _peak_out_y,
            _taper_x0,
            _base_out_y,
            _taper_x0,
            _base_in_y,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        tri_prism(
            _flat_x1,
            _peak_out_y,
            _taper_x0,
            _base_in_y,
            _flat_x1,
            _peak_in_y,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # GROUND fill behind (south of) the closing curb
    BRUSHES.append(
        tri_prism(
            _flat_x1,
            _peak_in_y,
            _taper_x0,
            _base_in_y,
            _flat_x1,
            _base_in_y,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )

    # East junction corner: center at NE corner of east sidewalk (pushed north
    # to _east_ext_y2, mirroring the NW corner's bulge treatment), arc sweeps
    # 90°→180°.
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1,
            _east_ext_y2,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_JCY,
            FLOOR_Z2 + 2,
            Textures.ROAD,
        )
    )
    _er_outer = KNOTT_DRIVEWAY_CURB_CRN_R
    _er_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
    _e_seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        ea0 = 90 + corner_index * _e_seg_deg
        ea1 = 90 + (corner_index + 1) * _e_seg_deg
        t0, t1 = math.radians(ea0), math.radians(ea1)
        # MULCH fill — pie slices from centre to inner radius
        BRUSHES.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_E,
                _east_ext_y2,
                KNOTT_DRIVEWAY_JCX_E + _er_inner * math.cos(t0),
                _east_ext_y2 + _er_inner * math.sin(t0),
                KNOTT_DRIVEWAY_JCX_E + _er_inner * math.cos(t1),
                _east_ext_y2 + _er_inner * math.sin(t1),
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.MULCH,
            )
        )
        # CEMENT curb ring — inner to outer radius
        BRUSHES.append(
            curb_seg(
                KNOTT_DRIVEWAY_JCX_E,
                _east_ext_y2,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                _er_inner,
                _er_outer,
                ea0,
                ea1,
                Textures.CEMENT,
            )
        )

    # Flat continuation east from the top of the curve — mirrors the NW
    # corner's bulge (KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W / _TAPER_W), but using
    # MULCH instead of GROUND for the fill sections, matching the east side's
    # existing mulch convention. Triangle vertex order is reversed relative to
    # the NW version since mirroring across X flips winding from CCW to CW —
    # reversing restores CCW (required by tri_prism).
    _e_peak_out_y = _east_ext_y2 + _er_outer
    _e_peak_in_y = _east_ext_y2 + _er_inner
    _e_base_out_y = KNOTT_DRIVEWAY_EXT_Y2 + _er_outer
    _e_base_in_y = KNOTT_DRIVEWAY_EXT_Y2 + _er_inner
    _e_flat_x2 = KNOTT_DRIVEWAY_JCX_E + KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_JCX_E,
            _e_peak_in_y,
            FLOOR_Z2,
            _e_flat_x2,
            _e_peak_out_y,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_JCX_E,
            _e_base_in_y,
            FLOOR_Z2,
            _e_flat_x2,
            _e_peak_in_y,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.MULCH,
        )
    )
    # Straight closing curb — slopes back down to the pre-bulge corner-top
    # position, mirroring the NW taper.
    _e_taper_x1 = _e_flat_x2 + KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W
    BRUSHES.append(
        tri_prism(
            _e_taper_x1,
            _e_base_in_y,
            _e_taper_x1,
            _e_base_out_y,
            _e_flat_x2,
            _e_peak_out_y,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        tri_prism(
            _e_flat_x2,
            _e_peak_in_y,
            _e_taper_x1,
            _e_base_in_y,
            _e_flat_x2,
            _e_peak_out_y,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # MULCH fill behind (south of) the closing curb
    BRUSHES.append(
        tri_prism(
            _e_flat_x2,
            _e_base_in_y,
            _e_taper_x1,
            _e_base_in_y,
            _e_flat_x2,
            _e_peak_in_y,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.MULCH,
        )
    )
    # Widen the mulch further south so it reaches ENNIS_SW_EDGE +
    # CHARLES_WALK_W — the same south edge the NE corner sidewalk section
    # (east sidewalk mulch strip) stops at — instead of leaving a shorter
    # patch at KNOTT_DRIVEWAY_EXT_Y2 that doesn't line up with it. The
    # "Terrain east of east sidewalk" GROUND block (above) is split/trimmed
    # to this same edge under the bulge's footprint so there's no overlap.
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_JCX_E,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2,
            _e_taper_x1,
            _e_base_in_y,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.MULCH,
        )
    )

    # ── Hill terrain under Knott Hall — REMOVED, pending re-derivation ──────────
    # The previous hill-fill/ramp/entrance-staircase model assumed a single flat
    # plateau at KNOTT_GROUND_Z. The 2024 topology check (docs/reference.rst,
    # "Topology check" section) shows the real east side climbs continuously from
    # Knott Hall (~+7.2 ft) to Ennis Parallel (~+21.7 ft, ~360 ft further east) —
    # not a flat shelf. This section needs to be rebuilt against a sloped
    # elevation model before KNOTT_TERRAIN_ENABLED can be turned back on.
    #
    # TODO: rebuild hill fill + west ramp + north-face slope + entrance
    # staircase/platform using real elevation-derived Z values instead of a
    # single flat KNOTT_GROUND_Z constant.

    return BRUSHES, []
