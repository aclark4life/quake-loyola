"""Terrain and access geometry around Knott Hall.

This module builds the Knott driveway, nearby hillside transitions, and the
optional pedestrian walkway and support bent that connect Knott Hall to the
bridge corridor.
"""

import math

from ..constants import (
    BRIDGE,
    BRIDGE_ACCESS_WALK_CENTER_X,
    BRIDGE_ACCESS_WALK_HW,
    BRIDGE_ACCESS_WALK_NORTH_OFFSET,
    BRIDGE_ACCESS_WALK_PIER_CLEARANCE,
    BRIDGE_ARCH_X,
    BRIDGE_CENTER_SPAN_OFFSET,
    BRIDGE_PILLAR_OVERHANG,
    BRIDGE_SUPPORT_BEAM_H,
    BRIDGE_SUPPORT_HW,
    BRIDGE_SUPPORT_PIER_HALF_W,
    BRIDGE_TUBE_GAP,
    BRIDGE_TUBE_HW,
    BRIDGE_TUBE_RISE,
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
    KNOTT_DRIVEWAY_JCX_X1,
    KNOTT_DRIVEWAY_JCY,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_WS_X1,
    KNOTT_DRIVEWAY_WS_X2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_ENABLED_TERRAIN,
    KNOTT_ENABLED_WALKWAY,
    KNOTT_ENABLED_WALKWAY_BENT,
    ROAD_X2,
    WALK_X1,
    WALK_X2,
    WALK_ZT1,
    WALK_ZT2,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
)
from ..geometry import (
    box,
    brush_ent,
    curb_seg,
    ramp_slab,
    ramp_slab_y,
    tri_prism,
    tri_ramp_prism,
)


def _build_knott_terrain():
    """Build the Knott driveway slopes, hillside fills, and curb returns."""

    BRUSHES = []

    def sidewalk_slabs_sloped(brushes, x1, x2, y1, y2, top_z_s, top_z_n, surface_tex):
        """Add one full-depth sloped sidewalk slab."""
        brushes.append(
            ramp_slab_y(
                x1,
                x2,
                y1,
                y2,
                FLOOR_Z1,
                FLOOR_Z1,
                top_z_s,
                top_z_n,
                Textures.GROUND,
                tt=surface_tex,
            )
        )

    def sidewalk_slabs_flat(brushes, x1, x2, y1, y2, z_base, z_top, surface_tex):
        """Add one full-depth flat sidewalk slab."""
        brushes.append(box(x1, y1, z_base, x2, y2, z_top, surface_tex))

    # Single call site — inlined rather than wrapped, since a one-off helper
    # added indirection without any reuse.
    BRUSHES.append(
        ramp_slab_y(
            KNOTT_DRIVEWAY_RD_X1,
            KNOTT_DRIVEWAY_RD_X2,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            KNOTT_DRIVEWAY_ZT_S + 2,
            KNOTT_DRIVEWAY_ZT_N + 2,
            Textures.GROUND,
            tt=Textures.ROAD,
        )
    )

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

    _sgrid_z = FLOOR_Z2 + CHARLES_WALK_H
    _south_edge_x0, _south_edge_z0 = KNOTT.x1, 66
    _south_edge_x1, _south_edge_z1 = 2700, 92

    def _south_edge_real(x):
        t = (x - _south_edge_x0) / (_south_edge_x1 - _south_edge_x0)
        return _sgrid_z + _south_edge_z0 + t * (_south_edge_z1 - _south_edge_z0)

    _far_south_y = [KNOTT_DRIVEWAY_Y1, -3000, -4500, WORLD_Y1 + WALL_T]
    _far_south_z_west = [66, 44, 46, 31]
    _far_south_z_east = [92, 57, 60, 35]

    _WRAMP_OVR = 4

    _charles_verge_x2 = ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W
    _sgrid = [
        (_charles_verge_x2, _sgrid_z, _sgrid_z),
        (700, _sgrid_z + 54, _sgrid_z + 68),
        (900, _sgrid_z + 59, _sgrid_z + 88),
        (
            KNOTT.x1,
            _sgrid_z + 66,
            _sgrid_z + 92,
        ),
    ]

    def _south_edge_z(x):
        """Return the sampled south-corner grid height at ``KNOTT_DRIVEWAY_Y2``."""
        for (gx1, _, gz1b), (gx2, _, gz2b) in zip(_sgrid, _sgrid[1:], strict=False):
            if gx1 <= x <= gx2:
                t = (x - gx1) / (gx2 - gx1) if gx2 != gx1 else 0.0
                return gz1b + t * (gz2b - gz1b)
        if x <= KNOTT.x1:
            return _sgrid[-1][2]

        t = (x - KNOTT.x1) / (KNOTT_DRIVEWAY_WS_X1 - KNOTT.x1)
        t = min(max(t, 0.0), 1.0)
        return _sgrid[-1][2] + t * (_sgrid_z - _sgrid[-1][2])

    _WS_TAPER_W = 200
    _ws_taper_x = KNOTT_DRIVEWAY_WS_X1 - _WS_TAPER_W

    _ES_TAPER_W = 1000
    _es_taper_x = KNOTT_DRIVEWAY_ES_X2 + _ES_TAPER_W

    def _sidewalk_h(y):
        """Height of the WS/ES driveway sidewalks at Y (Y1..Y2 sloped range)."""
        t = (y - KNOTT_DRIVEWAY_Y1) / (KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1)
        zs = KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H
        zn = KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H
        return zs + t * (zn - zs)

    _eg_flat = _sidewalk_h(KNOTT_DRIVEWAY_Y1)
    for _seg_i, ((y1, z1), (y2, z2)) in enumerate(
        zip(
            zip(_far_south_y, _far_south_z_east, strict=False),
            zip(_far_south_y[1:], _far_south_z_east[1:], strict=False),
            strict=False,
        )
    ):
        ra1 = _sgrid_z + z1
        ra2 = _sgrid_z + z2

        if _seg_i < len(_far_south_y) - 2:
            y2_ext = y2 - _WRAMP_OVR
            ra2 = ra1 + (ra2 - ra1) * (y2_ext - y1) / (y2 - y1)
            y2 = y2_ext

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

    _wg_flat = _sidewalk_h(KNOTT_DRIVEWAY_Y1)
    _wg2_x = [KNOTT.x1, 1650, 2100, KNOTT_DRIVEWAY_WS_X1]
    _wg2_cols = [
        _far_south_z_west,
        [61, 48, 49, 32],
        [77, 51, 49, 32],
        [_wg_flat - _sgrid_z] * 4,
    ]
    for (gx1, gcol1), (gx2, gcol2) in zip(
        zip(_wg2_x, _wg2_cols, strict=False),
        zip(_wg2_x[1:], _wg2_cols[1:], strict=False),
        strict=False,
    ):
        for _seg_i in range(len(_far_south_y) - 1):
            y1, y2 = _far_south_y[_seg_i], _far_south_y[_seg_i + 1]
            gz1a = _sgrid_z + gcol1[_seg_i]
            gz1b = _sgrid_z + gcol1[_seg_i + 1]
            gz2a = _sgrid_z + gcol2[_seg_i]
            gz2b = _sgrid_z + gcol2[_seg_i + 1]

            if gx1 == KNOTT.x1 and _seg_i == 0:
                BRUSHES.append(
                    tri_ramp_prism(
                        gx1,
                        y1,
                        gx1,
                        y2,
                        gx2,
                        y1,
                        FLOOR_Z1,
                        gz1a,
                        gz1b,
                        gz2a,
                        Textures.GROUND,
                    )
                )
                BRUSHES.append(
                    tri_ramp_prism(
                        gx2,
                        y1,
                        gx1,
                        y2,
                        gx2,
                        y2,
                        FLOOR_Z1,
                        gz2a,
                        gz1b,
                        gz2b,
                        Textures.GROUND,
                    )
                )
            else:
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
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )

    _wg_t900 = (900 - 700) / (KNOTT.x1 - 700)
    _wgrid_z900 = [
        z700 + _wg_t900 * (z1206 - z700)
        for z700, z1206 in zip([54, 37, 39, 31], _far_south_z_west, strict=False)
    ]
    _wgrid_x = [_charles_verge_x2, 700, 900, KNOTT.x1]
    _wgrid_cols = [
        [0, 0, 0, 0],
        [108, 74, 79, 62],
        _wgrid_z900,
        _far_south_z_west,
    ]

    for (wx1, wcol1), (wx2, wcol2) in zip(
        zip(_wgrid_x, _wgrid_cols, strict=False),
        zip(_wgrid_x[1:], _wgrid_cols[1:], strict=False),
        strict=False,
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

    _sgrid_y2_ext = KNOTT_DRIVEWAY_Y2 + _WRAMP_OVR
    for (gx1, gz1a, gz1b), (gx2, gz2a, gz2b) in zip(_sgrid, _sgrid[1:], strict=False):
        _t = (_sgrid_y2_ext - KNOTT_DRIVEWAY_Y1) / (
            KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1
        )
        gz1b_ext = gz1a + (gz1b - gz1a) * _t
        gz2b_ext = gz2a + (gz2b - gz2a) * _t

        if gx2 == KNOTT.x1:
            BRUSHES.append(
                tri_ramp_prism(
                    gx1,
                    KNOTT_DRIVEWAY_Y1,
                    gx2,
                    KNOTT_DRIVEWAY_Y1,
                    gx1,
                    _sgrid_y2_ext,
                    FLOOR_Z1,
                    gz1a,
                    gz2a,
                    gz1b_ext,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_ramp_prism(
                    gx2,
                    KNOTT_DRIVEWAY_Y1,
                    gx2,
                    _sgrid_y2_ext,
                    gx1,
                    _sgrid_y2_ext,
                    FLOOR_Z1,
                    gz2a,
                    gz2b_ext,
                    gz1b_ext,
                    Textures.GROUND,
                )
            )
        else:
            BRUSHES.append(
                tri_ramp_prism(
                    gx1,
                    KNOTT_DRIVEWAY_Y1,
                    gx2,
                    KNOTT_DRIVEWAY_Y1,
                    gx2,
                    _sgrid_y2_ext,
                    FLOOR_Z1,
                    gz1a,
                    gz2a,
                    gz2b_ext,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_ramp_prism(
                    gx1,
                    KNOTT_DRIVEWAY_Y1,
                    gx2,
                    _sgrid_y2_ext,
                    gx1,
                    _sgrid_y2_ext,
                    FLOOR_Z1,
                    gz1a,
                    gz2b_ext,
                    gz1b_ext,
                    Textures.GROUND,
                )
            )

    _west_x_ovr = 0
    _east_x_ovr = 2
    # The Y span (KNOTT_DRIVEWAY_Y1..Y2) is ~1655 units; the surface is a
    # ruled (bilinear) slope that's linear in Y between the south (Y1) and
    # north (Y2) x-profiles, so it can be exactly subdivided into narrower
    # Y-strips without approximation error. A single full-span brush here
    # previously produced fall-through gaps in the compiled BSP collision
    # hull (qbsp clipnode precision issues on very large shallow slopes) —
    # see the west-side terrain fall-through investigation.
    _WRAMP_Y_SEGS = 8
    for wx1, wx2 in ((KNOTT.x1, _ws_taper_x), (_ws_taper_x, KNOTT_DRIVEWAY_WS_X1)):
        real_edge = wx2 == KNOTT_DRIVEWAY_WS_X1
        _is_first = wx1 == KNOTT.x1
        wx1n = wx1 - _west_x_ovr if _is_first else wx1
        wx2n = wx2 + _east_x_ovr if real_edge else wx2
        z1a = _south_edge_real(wx1n)
        z1b = _sidewalk_h(KNOTT_DRIVEWAY_Y1) if real_edge else _south_edge_real(wx2)
        z2a = _sgrid[-1][2] if _is_first else _south_edge_z(wx1)
        z2b = _sidewalk_h(KNOTT_DRIVEWAY_Y2) if real_edge else _south_edge_z(wx2)
        for _seg_i in range(_WRAMP_Y_SEGS):
            _t0 = _seg_i / _WRAMP_Y_SEGS
            _t1 = (_seg_i + 1) / _WRAMP_Y_SEGS
            _y0 = KNOTT_DRIVEWAY_Y1 + _t0 * (KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1)
            _y1 = KNOTT_DRIVEWAY_Y1 + _t1 * (KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1)
            _za0 = z1a + _t0 * (z2a - z1a)
            _za1 = z1a + _t1 * (z2a - z1a)
            _zb0 = z1b + _t0 * (z2b - z1b)
            _zb1 = z1b + _t1 * (z2b - z1b)
            BRUSHES.append(
                tri_ramp_prism(
                    wx1n,
                    _y0,
                    wx2n,
                    _y0,
                    wx2n,
                    _y1,
                    FLOOR_Z1,
                    _za0,
                    _zb0,
                    _zb1,
                    Textures.GROUND,
                )
            )
            BRUSHES.append(
                tri_ramp_prism(
                    wx1n,
                    _y0,
                    wx2n,
                    _y1,
                    wx1n,
                    _y1,
                    FLOOR_Z1,
                    _za0,
                    _zb1,
                    _za1,
                    Textures.GROUND,
                )
            )

    _flat_z = FLOOR_Z2 + CHARLES_WALK_H

    _hill_profile = [
        (_charles_verge_x2, 0),
        (_charles_verge_x2 + 80, 30),
        (525, 42),
        (700, 67),
        (900, 78),
        (KNOTT.x1, 78),
        (BRIDGE_ARCH_X[4], 78),
        (
            BRIDGE_ARCH_X[4] + 0.2 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.2**2 - 2 * 0.2**3)),
        ),
        (
            BRIDGE_ARCH_X[4] + 0.4 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.4**2 - 2 * 0.4**3)),
        ),
        (
            BRIDGE_ARCH_X[4] + 0.6 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.6**2 - 2 * 0.6**3)),
        ),
        (
            BRIDGE_ARCH_X[4] + 0.8 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.8**2 - 2 * 0.8**3)),
        ),
        (KNOTT_DRIVEWAY_WS_X1, 0),
    ]

    def _hill_z(x):
        """Absolute model Z of the real-world hill profile at X (grade +
        piecewise-linear rise above it)."""
        for (px1, pz1), (px2, pz2) in zip(
            _hill_profile, _hill_profile[1:], strict=False
        ):
            if px1 <= x <= px2:
                t = (x - px1) / (px2 - px1) if px2 != px1 else 0.0
                return _flat_z + pz1 + t * (pz2 - pz1)
        return _flat_z + _hill_profile[-1][1]

    _y0_ext = 0 + _WRAMP_OVR
    for (px1, _), (px2, _) in zip(_hill_profile, _hill_profile[1:], strict=False):
        z1, z2 = _hill_z(px1), _hill_z(px2)
        zs1, zs2 = _south_edge_z(px1), _south_edge_z(px2)
        _t0 = (_y0_ext - KNOTT_DRIVEWAY_Y2) / (0 - KNOTT_DRIVEWAY_Y2)
        z1_ext = zs1 + (z1 - zs1) * _t0
        z2_ext = zs2 + (z2 - zs2) * _t0
        BRUSHES.append(
            tri_ramp_prism(
                px1,
                KNOTT_DRIVEWAY_Y2,
                px2,
                KNOTT_DRIVEWAY_Y2,
                px2,
                _y0_ext,
                FLOOR_Z1,
                zs1,
                zs2,
                z2_ext,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            tri_ramp_prism(
                px1,
                KNOTT_DRIVEWAY_Y2,
                px2,
                _y0_ext,
                px1,
                _y0_ext,
                FLOOR_Z1,
                zs1,
                z2_ext,
                z1_ext,
                Textures.GROUND,
            )
        )

        _nx_ovr = 2 if px1 != _hill_profile[0][0] else 0
        px1n = px1 - _nx_ovr
        z1n = _hill_z(px1n) if _nx_ovr else z1
        BRUSHES.append(
            tri_ramp_prism(
                px1n,
                0,
                px2,
                0,
                px1n,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                z1n,
                z2,
                _flat_z,
                Textures.GROUND,
            )
        )
        BRUSHES.append(
            tri_ramp_prism(
                px2,
                0,
                px2,
                ENNIS_SW_EDGE,
                px1n,
                ENNIS_SW_EDGE,
                FLOOR_Z1,
                z2,
                _flat_z,
                _flat_z,
                Textures.GROUND,
            )
        )

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

    _r_outer = KNOTT_DRIVEWAY_CURB_CRN_R
    _r_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
    _seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS

    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        a0 = corner_index * _seg_deg
        a1 = (corner_index + 1) * _seg_deg
        t0, t1 = math.radians(a0), math.radians(a1)
        BRUSHES.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_X1,
                _west_ext_y2,
                KNOTT_DRIVEWAY_JCX_X1 + _r_inner * math.cos(t0),
                _west_ext_y2 + _r_inner * math.sin(t0),
                KNOTT_DRIVEWAY_JCX_X1 + _r_inner * math.cos(t1),
                _west_ext_y2 + _r_inner * math.sin(t1),
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )

    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        a0 = corner_index * _seg_deg
        a1 = (corner_index + 1) * _seg_deg
        BRUSHES.append(
            curb_seg(
                KNOTT_DRIVEWAY_JCX_X1,
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

    _peak_out_y = _west_ext_y2 + _r_outer
    _peak_in_y = _west_ext_y2 + _r_inner
    _base_out_y = KNOTT_DRIVEWAY_EXT_Y2 + _r_outer
    _base_in_y = KNOTT_DRIVEWAY_EXT_Y2 + _r_inner
    _flat_x1 = KNOTT_DRIVEWAY_JCX_X1 - KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W
    BRUSHES.append(
        box(
            _flat_x1,
            _peak_in_y,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_JCX_X1,
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
            KNOTT_DRIVEWAY_JCX_X1,
            _peak_in_y,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )

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

    _east_jc_y2 = max(KNOTT_DRIVEWAY_JCY, _east_ext_y2 + KNOTT_DRIVEWAY_CURB_CRN_R)
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X1,
            _east_ext_y2,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_ES_X2,
            _east_jc_y2,
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

    return BRUSHES


def build():
    """Build Knott Hall terrain plus any enabled walkway geometry."""

    walk_brushes, walk_entities = _build_walkway()
    if not KNOTT_ENABLED_TERRAIN:
        return walk_brushes, walk_entities
    terrain_brushes = _build_knott_terrain()
    return terrain_brushes + walk_brushes, walk_entities


def _kh_hill_ground_z(x, y):
    """Return the modeled Knott hillside ground height at ``(x, y)``."""
    _charles_verge_x2 = ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W
    _flat_z = FLOOR_Z2 + CHARLES_WALK_H
    _hill_profile = [
        (_charles_verge_x2, 0),
        (_charles_verge_x2 + 80, 30),
        (525, 42),
        (700, 67),
        (900, 78),
        (KNOTT.x1, 78),
        (BRIDGE_ARCH_X[4], 78),
        (
            BRIDGE_ARCH_X[4] + 0.2 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.2**2 - 2 * 0.2**3)),
        ),
        (
            BRIDGE_ARCH_X[4] + 0.4 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.4**2 - 2 * 0.4**3)),
        ),
        (
            BRIDGE_ARCH_X[4] + 0.6 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.6**2 - 2 * 0.6**3)),
        ),
        (
            BRIDGE_ARCH_X[4] + 0.8 * (KNOTT_DRIVEWAY_WS_X1 - BRIDGE_ARCH_X[4]),
            78 * (1 - (3 * 0.8**2 - 2 * 0.8**3)),
        ),
        (KNOTT_DRIVEWAY_WS_X1, 0),
    ]

    def _hill_z(px):
        for (px1, pz1), (px2, pz2) in zip(
            _hill_profile, _hill_profile[1:], strict=False
        ):
            if px1 <= px <= px2:
                t = (px - px1) / (px2 - px1) if px2 != px1 else 0.0
                return _flat_z + pz1 + t * (pz2 - pz1)
        return _flat_z + _hill_profile[-1][1]

    hz = _hill_z(x)
    if y <= 0:
        return hz
    if y >= ENNIS_SW_EDGE:
        return _flat_z
    t = y / ENNIS_SW_EDGE
    return hz + (_flat_z - hz) * t


def _build_walkway():
    """Build the Knott walkway, accessible path, and optional support bent."""
    BRUSHES = []
    DETAIL_BRUSHES = []

    if KNOTT_ENABLED_WALKWAY:
        wk_zb1 = WALK_ZT1 - KNOTT.wall_t
        wk_zb2 = WALK_ZT2 - KNOTT.wall_t
        BRUSHES.append(
            ramp_slab_y(
                WALK_X1,
                WALK_X2,
                BRIDGE.y1,
                KNOTT.y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1,
                WALK_ZT2,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )

        DETAIL_BRUSHES.append(
            ramp_slab_y(
                WALK_X1 - BRIDGE.walk_wall,
                WALK_X1,
                BRIDGE.y1,
                KNOTT.y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1 + BRIDGE.parapet_h,
                WALK_ZT2 + BRIDGE.parapet_h,
                Textures.CEMENT,
            )
        )
        DETAIL_BRUSHES.append(
            ramp_slab_y(
                WALK_X2,
                WALK_X2 + BRIDGE.walk_wall,
                BRIDGE.y1,
                KNOTT.y2,
                wk_zb1,
                wk_zb2,
                WALK_ZT1 + BRIDGE.parapet_h,
                WALK_ZT2 + BRIDGE.parapet_h,
                Textures.CEMENT,
            )
        )

        for tube_z_offset in [BRIDGE_TUBE_RISE, BRIDGE_TUBE_RISE + BRIDGE_TUBE_GAP]:
            tube_base_z = WALK_ZT1 + BRIDGE.parapet_h + tube_z_offset
            ww_cx = BRIDGE.walk_wall // 2
            DETAIL_BRUSHES.append(
                box(
                    WALK_X1 - ww_cx - BRIDGE_TUBE_HW,
                    KNOTT.y2,
                    tube_base_z,
                    WALK_X1 - ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE.y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )
            DETAIL_BRUSHES.append(
                box(
                    WALK_X2 + ww_cx - BRIDGE_TUBE_HW,
                    KNOTT.y2,
                    tube_base_z,
                    WALK_X2 + ww_cx + BRIDGE_TUBE_HW,
                    BRIDGE.y1,
                    tube_base_z + BRIDGE_TUBE_HW * 2,
                    Textures.RAIL,
                )
            )

        east_walk_center_x = BRIDGE_ACCESS_WALK_CENTER_X
        east_walk_half_width = BRIDGE_ACCESS_WALK_HW
        east_walk_x2 = east_walk_center_x + east_walk_half_width
        east_walk_y2 = (
            BRIDGE.y2
            + BRIDGE_PILLAR_OVERHANG
            + BRIDGE_ACCESS_WALK_PIER_CLEARANCE
            + BRIDGE_ACCESS_WALK_NORTH_OFFSET
        )
        terrain_z2 = int(_kh_hill_ground_z(east_walk_x2, east_walk_y2))

        east_walk_ext_y1 = east_walk_y2 - (east_walk_half_width * 2)
        east_walk_ext_y2 = east_walk_y2
        extension_terrain_z1 = int(_kh_hill_ground_z(east_walk_x2, east_walk_ext_y1))
        extension_terrain_z2 = terrain_z2
        extension_terrain_z_west = (extension_terrain_z1 + extension_terrain_z2) // 2
        DETAIL_BRUSHES.append(
            ramp_slab(
                east_walk_x2,
                KNOTT.x2,
                east_walk_ext_y1,
                east_walk_ext_y2,
                FLOOR_Z1,
                FLOOR_Z1,
                extension_terrain_z_west,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
                tt=Textures.FLOOR,
            )
        )

    if KNOTT_ENABLED_WALKWAY_BENT:
        _bent_dy, _bent_dz = BRIDGE_CENTER_SPAN_OFFSET[1], BRIDGE_CENTER_SPAN_OFFSET[2]

        support_y_center = BRIDGE.y1 + BRIDGE_SUPPORT_HW + _bent_dy
        support_half_width = BRIDGE_SUPPORT_HW
        support_y1 = support_y_center - support_half_width
        support_y2 = support_y_center + support_half_width

        beam_top_z = WALK_ZT1 - KNOTT.wall_t + _bent_dz
        beam_height = BRIDGE_SUPPORT_BEAM_H
        beam_bottom_z = beam_top_z - beam_height

        beam_x1 = BRIDGE_ARCH_X[3]
        beam_x2 = BRIDGE_ARCH_X[4]

        step = (beam_x2 - beam_x1) / 6
        support_pier_xs = [int(beam_x1 + step * k) for k in (1, 2, 3, 4, 5)]
        support_pier_half_width = BRIDGE_SUPPORT_PIER_HALF_W

        # Pull the east-most support pillar in closer to the actual bridge
        # pier at beam_x2, instead of leaving it a full even-spacing step
        # (~209 units) away.
        support_pier_xs[-1] = int(beam_x2 - 140)
        # Nudge the 2nd-most east pillar east a bit too, off its even
        # spacing, to open the gap toward its western neighbor.
        support_pier_xs[-2] = int(support_pier_xs[-2] + 60)

        # The beam itself stops short of the Pier 4 wall (beam_x1) and
        # instead starts flush with the first drop pier's west face,
        # leaving the west end open to match the real building (no beam
        # spans the gap before the first support pillar).
        beam_start_x = support_pier_xs[0] - support_pier_half_width

        DETAIL_BRUSHES.append(
            box(
                beam_start_x,
                support_y1,
                beam_bottom_z,
                beam_x2,
                support_y2,
                beam_top_z,
                Textures.CEMENT,
            )
        )

        support_y_center = (support_y1 + support_y2) / 2.0
        for pier_x in support_pier_xs:
            pier_ground_z = _kh_hill_ground_z(pier_x, support_y_center)
            DETAIL_BRUSHES.append(
                box(
                    pier_x - support_pier_half_width,
                    support_y1,
                    pier_ground_z,
                    pier_x + support_pier_half_width,
                    support_y2,
                    beam_bottom_z,
                    Textures.CEMENT,
                )
            )

        _tie_x1 = support_pier_xs[-1]
        _tie_z1 = _kh_hill_ground_z(_tie_x1, support_y_center)
        _tie_z2 = _kh_hill_ground_z(beam_x2, support_y_center)
        DETAIL_BRUSHES.append(
            ramp_slab(
                _tie_x1,
                beam_x2,
                support_y1,
                support_y2,
                _tie_z1,
                _tie_z2,
                _tie_z1 + beam_height,
                _tie_z2 + beam_height,
                Textures.CEMENT,
            )
        )

    ENTITIES = []
    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
