"""Terrain and access geometry around Knott Hall.

This module builds the Knott driveway, nearby hillside transitions, and the
support bent under the bridge span in front of the Knott Hall entrance.
"""

import math

from ..constants import (
    BRIDGE,
    BRIDGE_ARCH_X,
    BRIDGE_CENTER_SPAN_OFFSET,
    BRIDGE_SUPPORT_BEAM_H,
    BRIDGE_SUPPORT_HW,
    BRIDGE_SUPPORT_PIER_HALF_W,
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
    KNOTT_ENT_WALK_ZT1,
    ROAD_X2,
    STREET_CURB_JOINT_OFFSET,
    STREET_CURB_SLAB_LEN,
    STREET_SURFACE_T,
    STREET_SW_GAP,
    STREET_SW_JOINT_DROP,
    STREET_SW_SLAB_LEN,
    WALL_T,
    WORLD_X2_EXT,
    WORLD_Y1,
    Textures,
)
from ..geometry import (
    box,
    brush_ent,
    curb_seg,
    ramp_slab_y,
    recess_joint_tops,
    sidewalk_panel_spans,
    tri_prism,
    tri_ramp_prism,
)


def _kh_hill_profile():
    """Return the sampled Knott hillside X/Z profile used by terrain helpers."""
    _charles_verge_x2 = ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W
    return [
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


def _kh_hill_profile_z(x, hill_profile):
    """Return the absolute model Z of the sampled Knott hillside profile."""
    _flat_z = FLOOR_Z2 + CHARLES_WALK_H
    for (px1, pz1), (px2, pz2) in zip(hill_profile, hill_profile[1:], strict=False):
        if px1 <= x <= px2:
            t = (x - px1) / (px2 - px1) if px2 != px1 else 0.0
            return _flat_z + pz1 + t * (pz2 - pz1)
    return _flat_z + hill_profile[-1][1]


def _append_sloped_sidewalk_slab(
    brushes, x1, x2, y1, y2, top_z_s, top_z_n, surface_tex
):
    """Add one full-depth sloped sidewalk slab.

    The slab's east and west faces (``ts``) are the curb sides exposed to the
    driveway, so they take the walking surface's texture rather than ground.
    """
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
            ts=surface_tex,
        )
    )


def _append_flat_sidewalk_slab(brushes, x1, x2, y1, y2, z_base, z_top, surface_tex):
    """Add one full-depth flat sidewalk slab."""
    brushes.append(box(x1, y1, z_base, x2, y2, z_top, surface_tex))


def _append_tiled_sloped_sidewalk(
    brushes,
    x1,
    x2,
    y1,
    y2,
    top_z_s,
    top_z_n,
    surface_tex,
    slab_len=STREET_SW_SLAB_LEN,
    offset=0,
):
    """Tile a north-south sloped walk into panels, like the Charles St walks.

    Panels keep the run's overall slope, so the joints between them stay flush
    with the walking surface instead of stepping.
    """

    def _top_z(y):
        return top_z_s + (y - y1) * (top_z_n - top_z_s) / (y2 - y1)

    panels, joints = sidewalk_panel_spans(y1, y2, slab_len, STREET_SW_GAP, offset)
    for span, tex in [(panels, surface_tex), (joints, Textures.SIDEWALK_JOINT)]:
        for py1, py2 in span:
            _append_sloped_sidewalk_slab(
                brushes, x1, x2, py1, py2, _top_z(py1), _top_z(py2), tex
            )


def _append_tiled_flat_sidewalk_y(
    brushes,
    x1,
    x2,
    y1,
    y2,
    z_base,
    z_top,
    surface_tex,
    slab_len=STREET_SW_SLAB_LEN,
    offset=0,
):
    """Tile a north-south flat walk into panels, like the Charles St walks."""
    panels, joints = sidewalk_panel_spans(y1, y2, slab_len, STREET_SW_GAP, offset)
    for span, tex in [(panels, surface_tex), (joints, Textures.SIDEWALK_JOINT)]:
        for py1, py2 in span:
            _append_flat_sidewalk_slab(brushes, x1, x2, py1, py2, z_base, z_top, tex)


def _append_tiled_flat_sidewalk_x(
    brushes,
    x1,
    x2,
    y1,
    y2,
    z_base,
    z_top,
    surface_tex,
    slab_len=STREET_SW_SLAB_LEN,
    offset=0,
):
    """Tile an east-west flat walk into panels, like the Ennis Rd walks."""
    panels, joints = sidewalk_panel_spans(x1, x2, slab_len, STREET_SW_GAP, offset)
    for span, tex in [(panels, surface_tex), (joints, Textures.SIDEWALK_JOINT)]:
        for px1, px2 in span:
            _append_flat_sidewalk_slab(brushes, px1, px2, y1, y2, z_base, z_top, tex)


def _knott_curb_phase(y1):
    """Return the joint offset keeping a curb run on the shared curb grid.

    The driveway curbs are built in several pieces; anchoring every piece to one
    grid based at ``KNOTT_DRIVEWAY_Y1`` makes them read as a single pour.
    """
    return (y1 - KNOTT_DRIVEWAY_Y1 + STREET_CURB_JOINT_OFFSET) % (
        STREET_CURB_SLAB_LEN + STREET_SW_GAP
    )


def _knott_terrain_state():
    """Return shared sampled terrain inputs used by the Knott terrain helpers."""
    _sgrid_z = FLOOR_Z2 + CHARLES_WALK_H
    _charles_verge_x2 = ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W
    _far_south_z_west = [66, 44, 46, 31]
    return {
        "sgrid_z": _sgrid_z,
        "south_edge_x0": KNOTT.x1,
        "south_edge_z0": 66,
        "south_edge_x1": 2700,
        "south_edge_z1": 92,
        "far_south_y": [KNOTT_DRIVEWAY_Y1, -3000, -4500, WORLD_Y1 + WALL_T],
        "far_south_z_west": _far_south_z_west,
        "far_south_z_east": [92, 57, 60, 35],
        "WRAMP_OVR": 4,  # Only for the ramp aprons at the junction itself; the
        # far_south_y segments below deliberately do NOT overlap. Consecutive
        # segments already share an exact Z at their common Y (the same
        # far_south_z_* sample serves as one segment's end and the next one's
        # start), so running a segment 4 units past its neighbour's start only
        # buried one sloped surface a hair under another and left qbsp
        # carving unbuildable slivers out of the seam (WARNING 12).
        "charles_verge_x2": _charles_verge_x2,
        "sgrid": [
            (_charles_verge_x2, _sgrid_z, _sgrid_z),
            (700, _sgrid_z + 54, _sgrid_z + 68),
            (900, _sgrid_z + 59, _sgrid_z + 88),
            (KNOTT.x1, _sgrid_z + 66, _sgrid_z + 92),
        ],
        "WS_TAPER_W": 200,
        "ws_taper_x": KNOTT_DRIVEWAY_WS_X1 - 200,
        "ES_TAPER_W": 1000,
        "es_taper_x": KNOTT_DRIVEWAY_ES_X2 + 1000,
    }


def _knott_south_edge_real(x, state):
    """Return the modeled south edge Z at the given X."""
    t = (x - state["south_edge_x0"]) / (state["south_edge_x1"] - state["south_edge_x0"])
    return (
        state["sgrid_z"]
        + state["south_edge_z0"]
        + t * (state["south_edge_z1"] - state["south_edge_z0"])
    )


def _knott_south_edge_z(x, state):
    """Return the sampled south-corner grid height at ``KNOTT_DRIVEWAY_Y2``."""
    for (gx1, _, gz1b), (gx2, _, gz2b) in zip(
        state["sgrid"], state["sgrid"][1:], strict=False
    ):
        if gx1 <= x <= gx2:
            t = (x - gx1) / (gx2 - gx1) if gx2 != gx1 else 0.0
            return gz1b + t * (gz2b - gz1b)
    if x <= KNOTT.x1:
        return state["sgrid"][-1][2]

    t = (x - KNOTT.x1) / (KNOTT_DRIVEWAY_WS_X1 - KNOTT.x1)
    t = min(max(t, 0.0), 1.0)
    return state["sgrid"][-1][2] + t * (state["sgrid_z"] - state["sgrid"][-1][2])


def _knott_sidewalk_h(y):
    """Return the WS/ES driveway sidewalk height at the given Y."""
    t = (y - KNOTT_DRIVEWAY_Y1) / (KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1)
    zs = KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H
    zn = KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H
    return zs + t * (zn - zs)


def _append_knott_driveway_slabs(brushes):
    """Build the sloped driveway roadbed and both sidewalk slabs."""
    brushes.append(
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
    # The west side is a walk with an ENNIS_CURB_W curb along its road edge,
    # divided from it by a longitudinal joint.
    _append_tiled_sloped_sidewalk(
        brushes,
        KNOTT_DRIVEWAY_WS_X1,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - STREET_SW_GAP,
        KNOTT_DRIVEWAY_Y1,
        KNOTT_DRIVEWAY_Y2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.CEMENT,
    )
    _append_sloped_sidewalk_slab(
        brushes,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - STREET_SW_GAP,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
        KNOTT_DRIVEWAY_Y1,
        KNOTT_DRIVEWAY_Y2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.SIDEWALK_JOINT,
    )
    _append_tiled_sloped_sidewalk(
        brushes,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
        KNOTT_DRIVEWAY_WS_X2,
        KNOTT_DRIVEWAY_Y1,
        KNOTT_DRIVEWAY_Y2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.CEMENT,
        slab_len=STREET_CURB_SLAB_LEN,
        offset=_knott_curb_phase(KNOTT_DRIVEWAY_Y1),
    )
    # The east side is a curb rather than a sidewalk: an ENNIS_CURB_W cement
    # strip at the roadbed edge with ground behind it. It runs the full length
    # of the driveway and continues north through the extension (see
    # _append_knott_driveway_extension) up to the Ennis sidewalk.
    _append_tiled_sloped_sidewalk(
        brushes,
        KNOTT_DRIVEWAY_ES_X1,
        KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
        KNOTT_DRIVEWAY_Y1,
        KNOTT_DRIVEWAY_Y2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.CEMENT,
        slab_len=STREET_CURB_SLAB_LEN,
        offset=_knott_curb_phase(KNOTT_DRIVEWAY_Y1),
    )
    _append_sloped_sidewalk_slab(
        brushes,
        KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
        KNOTT_DRIVEWAY_ES_X2,
        KNOTT_DRIVEWAY_Y1,
        KNOTT_DRIVEWAY_Y2,
        KNOTT_DRIVEWAY_ZT_S + CHARLES_WALK_H,
        KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
        Textures.GROUND,
    )


def _append_knott_east_far_south_fill(brushes, state):
    """Build the east-side terrain quads south of the driveway junction."""
    _eg_flat = _knott_sidewalk_h(KNOTT_DRIVEWAY_Y1)
    for _seg_i, ((y1, z1), (y2, z2)) in enumerate(
        zip(
            zip(state["far_south_y"], state["far_south_z_east"], strict=False),
            zip(state["far_south_y"][1:], state["far_south_z_east"][1:], strict=False),
            strict=False,
        )
    ):
        ra1 = state["sgrid_z"] + z1
        ra2 = state["sgrid_z"] + z2

        brushes.append(
            tri_ramp_prism(
                KNOTT_DRIVEWAY_ES_X2,
                y1,
                state["es_taper_x"],
                y2,
                state["es_taper_x"],
                y1,
                FLOOR_Z1,
                _eg_flat,
                ra2,
                ra1,
                Textures.GROUND,
            )
        )
        brushes.append(
            tri_ramp_prism(
                KNOTT_DRIVEWAY_ES_X2,
                y1,
                KNOTT_DRIVEWAY_ES_X2,
                y2,
                state["es_taper_x"],
                y2,
                FLOOR_Z1,
                _eg_flat,
                _eg_flat,
                ra2,
                Textures.GROUND,
            )
        )
        brushes.append(
            ramp_slab_y(
                state["es_taper_x"],
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

    _mr_z1s = _knott_sidewalk_h(KNOTT_DRIVEWAY_Y1)
    _mr_z2s = _knott_sidewalk_h(KNOTT_DRIVEWAY_Y2)
    _mr_z1r = state["sgrid_z"] + state["far_south_z_east"][0]
    _mr_z2r = KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H
    brushes.append(
        tri_ramp_prism(
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y1,
            state["es_taper_x"],
            KNOTT_DRIVEWAY_Y1,
            state["es_taper_x"],
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z1,
            _mr_z1s,
            _mr_z1r,
            _mr_z2r,
            Textures.GROUND,
        )
    )
    brushes.append(
        tri_ramp_prism(
            KNOTT_DRIVEWAY_ES_X2,
            KNOTT_DRIVEWAY_Y1,
            state["es_taper_x"],
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
    brushes.append(
        ramp_slab_y(
            state["es_taper_x"],
            WORLD_X2_EXT - WALL_T,
            KNOTT_DRIVEWAY_Y1,
            KNOTT_DRIVEWAY_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            state["sgrid_z"] + state["far_south_z_east"][0],
            KNOTT_DRIVEWAY_ZT_N + CHARLES_WALK_H,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )


def _append_knott_west_far_south_fill(brushes, state):
    """Build the west-side terrain fill quads south of the driveway."""
    _wg_flat = _knott_sidewalk_h(KNOTT_DRIVEWAY_Y1)
    _wg2_x = [KNOTT.x1, 1650, 2100, KNOTT_DRIVEWAY_WS_X1]
    _wg2_cols = [
        state["far_south_z_west"],
        [61, 48, 49, 32],
        [77, 51, 49, 32],
        [_wg_flat - state["sgrid_z"]] * 4,
    ]
    for (gx1, gcol1), (gx2, gcol2) in zip(
        zip(_wg2_x, _wg2_cols, strict=False),
        zip(_wg2_x[1:], _wg2_cols[1:], strict=False),
        strict=False,
    ):
        for _seg_i in range(len(state["far_south_y"]) - 1):
            y1, y2 = state["far_south_y"][_seg_i], state["far_south_y"][_seg_i + 1]
            gz1a = state["sgrid_z"] + gcol1[_seg_i]
            gz1b = state["sgrid_z"] + gcol1[_seg_i + 1]
            gz2a = state["sgrid_z"] + gcol2[_seg_i]
            gz2b = state["sgrid_z"] + gcol2[_seg_i + 1]

            if gx1 == KNOTT.x1 and _seg_i == 0:
                brushes.append(
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
                brushes.append(
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
                brushes.append(
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
                brushes.append(
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

    brushes.append(
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


def _append_knott_west_grid_transitions(brushes, state):
    """Build the west-side transition quads between Charles and the driveway."""
    _wg_t900 = (900 - 700) / (KNOTT.x1 - 700)
    _wgrid_z900 = [
        z700 + _wg_t900 * (z1206 - z700)
        for z700, z1206 in zip(
            [54, 37, 39, 31], state["far_south_z_west"], strict=False
        )
    ]
    _wgrid_x = [state["charles_verge_x2"], 700, 900, KNOTT.x1]
    _wgrid_cols = [
        [0, 0, 0, 0],
        [108, 74, 79, 62],
        _wgrid_z900,
        state["far_south_z_west"],
    ]

    for (wx1, wcol1), (wx2, wcol2) in zip(
        zip(_wgrid_x, _wgrid_cols, strict=False),
        zip(_wgrid_x[1:], _wgrid_cols[1:], strict=False),
        strict=False,
    ):
        for i in range(len(state["far_south_y"]) - 1):
            y1, y2 = state["far_south_y"][i], state["far_south_y"][i + 1]
            z1a, z1b = wcol1[i], wcol1[i + 1]
            z2a, z2b = wcol2[i], wcol2[i + 1]
            brushes.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx2,
                    y2,
                    wx2,
                    y1,
                    FLOOR_Z1,
                    state["sgrid_z"] + z1a,
                    state["sgrid_z"] + z2b,
                    state["sgrid_z"] + z2a,
                    Textures.GROUND,
                )
            )
            brushes.append(
                tri_ramp_prism(
                    wx1,
                    y1,
                    wx1,
                    y2,
                    wx2,
                    y2,
                    FLOOR_Z1,
                    state["sgrid_z"] + z1a,
                    state["sgrid_z"] + z1b,
                    state["sgrid_z"] + z2b,
                    Textures.GROUND,
                )
            )

    _sgrid_y2_ext = KNOTT_DRIVEWAY_Y2 + state["WRAMP_OVR"]
    for (gx1, gz1a, gz1b), (gx2, gz2a, gz2b) in zip(
        state["sgrid"], state["sgrid"][1:], strict=False
    ):
        _t = (_sgrid_y2_ext - KNOTT_DRIVEWAY_Y1) / (
            KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1
        )
        gz1b_ext = gz1a + (gz1b - gz1a) * _t
        gz2b_ext = gz2a + (gz2b - gz2a) * _t

        if gx2 == KNOTT.x1:
            brushes.append(
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
            brushes.append(
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
            brushes.append(
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
            brushes.append(
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


def _append_knott_west_driveway_ramp(brushes, state):
    """Build the west driveway-to-hillside ramp strips."""
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
    for wx1, wx2 in (
        (KNOTT.x1, state["ws_taper_x"]),
        (state["ws_taper_x"], KNOTT_DRIVEWAY_WS_X1),
    ):
        real_edge = wx2 == KNOTT_DRIVEWAY_WS_X1
        _is_first = wx1 == KNOTT.x1
        wx1n = wx1 - _west_x_ovr if _is_first else wx1
        wx2n = wx2 + _east_x_ovr if real_edge else wx2
        z1a = _knott_south_edge_real(wx1n, state)
        z1b = (
            _knott_sidewalk_h(KNOTT_DRIVEWAY_Y1)
            if real_edge
            else _knott_south_edge_real(wx2, state)
        )
        z2a = state["sgrid"][-1][2] if _is_first else _knott_south_edge_z(wx1, state)
        z2b = (
            _knott_sidewalk_h(KNOTT_DRIVEWAY_Y2)
            if real_edge
            else _knott_south_edge_z(wx2, state)
        )
        for _seg_i in range(_WRAMP_Y_SEGS):
            _t0 = _seg_i / _WRAMP_Y_SEGS
            _t1 = (_seg_i + 1) / _WRAMP_Y_SEGS
            _y0 = KNOTT_DRIVEWAY_Y1 + _t0 * (KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1)
            _y1 = KNOTT_DRIVEWAY_Y1 + _t1 * (KNOTT_DRIVEWAY_Y2 - KNOTT_DRIVEWAY_Y1)
            _za0 = z1a + _t0 * (z2a - z1a)
            _za1 = z1a + _t1 * (z2a - z1a)
            _zb0 = z1b + _t0 * (z2b - z1b)
            _zb1 = z1b + _t1 * (z2b - z1b)
            brushes.append(
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
            brushes.append(
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


def _append_knott_hillside_profile_fill(brushes, state):
    """Build the Knott hillside profile quads north of the driveway."""
    _flat_z = FLOOR_Z2 + CHARLES_WALK_H
    _hill_profile = _kh_hill_profile()
    _y0_ext = 0 + state["WRAMP_OVR"]

    for (px1, _), (px2, _) in zip(_hill_profile, _hill_profile[1:], strict=False):
        z1 = _kh_hill_profile_z(px1, _hill_profile)
        z2 = _kh_hill_profile_z(px2, _hill_profile)
        zs1, zs2 = _knott_south_edge_z(px1, state), _knott_south_edge_z(px2, state)
        _t0 = (_y0_ext - KNOTT_DRIVEWAY_Y2) / (0 - KNOTT_DRIVEWAY_Y2)
        z1_ext = zs1 + (z1 - zs1) * _t0
        z2_ext = zs2 + (z2 - zs2) * _t0
        brushes.append(
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
        brushes.append(
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
        z1n = _kh_hill_profile_z(px1n, _hill_profile) if _nx_ovr else z1
        brushes.append(
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
        brushes.append(
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


def _append_ennis_walk_apron(brushes, x1, x2):
    """Carry the Ennis south walk across a driveway head at ``x1``..``x2``.

    Reproduces the banding the street module gives the rest of the south walk
    — stone walk, dark joint, then the decorative curb slab sitting on a ground
    backfill — so the aprons read as part of the same sidewalk.
    """
    _walk_y2 = ENNIS_SW_EDGE + CHARLES_WALK_W - ENNIS_CURB_W - STREET_SW_GAP
    _curb_y1 = ENNIS_SW_EDGE + CHARLES_WALK_W - ENNIS_CURB_W
    _append_tiled_flat_sidewalk_x(
        brushes,
        x1,
        x2,
        ENNIS_SW_EDGE,
        _walk_y2,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.WHITE_STONE,
    )
    _append_flat_sidewalk_slab(
        brushes,
        x1,
        x2,
        _walk_y2,
        _curb_y1,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK_JOINT,
    )
    # The curb slab pours from STREET_SURFACE_T up, as it does along the rest
    # of the run, so back it with ground to keep the band solid.
    brushes.append(
        box(
            x1,
            _curb_y1,
            FLOOR_Z2,
            x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.GROUND,
        )
    )
    brushes.append(
        box(
            x1,
            _curb_y1,
            FLOOR_Z2 + STREET_SURFACE_T,
            x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CURB,
        )
    )


def _append_knott_driveway_extension(brushes):
    """Build the Ennis-side driveway extension, sidewalks, and edge fills."""
    brushes.append(
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
    # South of the Ennis walk: the driveway's west sidewalk, its joint, and the
    # curb strip at the roadbed edge. The walk band itself is poured as one
    # stone apron below, so these all stop at ENNIS_SW_EDGE.
    _append_tiled_flat_sidewalk_y(
        brushes,
        KNOTT_DRIVEWAY_WS_X1,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - STREET_SW_GAP,
        KNOTT_DRIVEWAY_EXT_Y1,
        ENNIS_SW_EDGE,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.CEMENT,
    )
    _append_flat_sidewalk_slab(
        brushes,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - STREET_SW_GAP,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
        KNOTT_DRIVEWAY_EXT_Y1,
        ENNIS_SW_EDGE,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK_JOINT,
    )

    _west_ext_y2 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_BULGE_D
    # The Ennis walk crosses the driveway head banded like the walk either
    # side of it, matching the apron on the driveway's east side.
    _append_ennis_walk_apron(brushes, KNOTT_DRIVEWAY_WS_X1, KNOTT_DRIVEWAY_WS_X2)
    # The west curb resumes north of the walk and runs past its end to close
    # the bulge return.
    for _curb_y1, _curb_y2 in (
        (KNOTT_DRIVEWAY_EXT_Y1, ENNIS_SW_EDGE),
        (ENNIS_SW_EDGE + CHARLES_WALK_W, _west_ext_y2),
    ):
        _append_tiled_flat_sidewalk_y(
            brushes,
            KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
            KNOTT_DRIVEWAY_WS_X2,
            _curb_y1,
            _curb_y2,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
            slab_len=STREET_CURB_SLAB_LEN,
            offset=_knott_curb_phase(_curb_y1),
        )
    brushes.append(
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

    # Continue the driveway's east curb north: an ENNIS_CURB_W cement strip at
    # the roadbed edge backed by ground, up to the Ennis sidewalk, which then
    # crosses the full width in cement.
    _append_tiled_flat_sidewalk_y(
        brushes,
        KNOTT_DRIVEWAY_ES_X1,
        KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
        KNOTT_DRIVEWAY_EXT_Y1,
        ENNIS_SW_EDGE,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.CEMENT,
        slab_len=STREET_CURB_SLAB_LEN,
        offset=_knott_curb_phase(KNOTT_DRIVEWAY_EXT_Y1),
    )
    _append_flat_sidewalk_slab(
        brushes,
        KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
        KNOTT_DRIVEWAY_ES_X2,
        KNOTT_DRIVEWAY_EXT_Y1,
        ENNIS_SW_EDGE,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.GROUND,
    )
    _e_bulge_x2 = (
        KNOTT_DRIVEWAY_JCX_E
        + KNOTT_DRIVEWAY_CURB_BULGE_FLAT_W
        + KNOTT_DRIVEWAY_CURB_BULGE_TAPER_W
    )
    # The Ennis walk crosses the driveway apron banded like the rest of the
    # south walk. It stops at the driveway's east edge: east of there the
    # street module's own SE run owns the walk, joint, and curb, so carrying
    # this run past the bulge would bury them in overlapping cement.
    _append_ennis_walk_apron(brushes, KNOTT_DRIVEWAY_ES_X1, KNOTT_DRIVEWAY_ES_X2)
    # That run used to backfill under the street module's Ennis curb across the
    # bulge; the curb only pours from STREET_SURFACE_T up, so fill it here.
    brushes.append(
        box(
            KNOTT_DRIVEWAY_ES_X2,
            ENNIS_SW_EDGE + CHARLES_WALK_W - ENNIS_CURB_W,
            FLOOR_Z2,
            _e_bulge_x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.GROUND,
        )
    )

    _east_ext_y2 = KNOTT_DRIVEWAY_EXT_Y2 + KNOTT_DRIVEWAY_CURB_BULGE_D
    brushes.append(
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
    _append_tiled_flat_sidewalk_y(
        brushes,
        KNOTT_DRIVEWAY_ES_X1,
        KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
        ENNIS_SW_EDGE + CHARLES_WALK_W,
        _east_ext_y2,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.CEMENT,
        slab_len=STREET_CURB_SLAB_LEN,
        offset=_knott_curb_phase(ENNIS_SW_EDGE + CHARLES_WALK_W),
    )

    brushes.append(
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

    return _west_ext_y2, _east_ext_y2


def _append_knott_west_curb_return(brushes, _west_ext_y2):
    """Build the west curb bulge, corner arc, and junction road fill."""
    brushes.append(
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
    brushes.append(
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
        brushes.append(
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
        brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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


def _append_knott_east_curb_return(brushes, _east_ext_y2):
    """Build the east curb bulge, corner arc, and mulch-side taper."""
    _east_jc_y2 = max(KNOTT_DRIVEWAY_JCY, _east_ext_y2 + KNOTT_DRIVEWAY_CURB_CRN_R)
    brushes.append(
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
        brushes.append(
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
        brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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


def _append_knott_walkway_bent(brushes):
    """Build the support bent under the span in front of the Knott entrance.

    A cement beam tucked against the deck underside, carried by drop pillars
    down to the hillside, plus a tie beam running on from the last pillar to
    the Pier 5 wall at the span's east end.
    """
    _bent_dy, _bent_dz = BRIDGE_CENTER_SPAN_OFFSET[1], BRIDGE_CENTER_SPAN_OFFSET[2]

    support_y_center = BRIDGE.y1 + BRIDGE_SUPPORT_HW + _bent_dy
    support_y1 = support_y_center - BRIDGE_SUPPORT_HW
    support_y2 = support_y_center + BRIDGE_SUPPORT_HW

    beam_top_z = KNOTT_ENT_WALK_ZT1 - KNOTT.wall_t + _bent_dz
    beam_height = BRIDGE_SUPPORT_BEAM_H
    beam_bottom_z = beam_top_z - beam_height

    beam_x1 = BRIDGE_ARCH_X[3]
    beam_x2 = BRIDGE_ARCH_X[4]

    step = (beam_x2 - beam_x1) / 6
    support_pier_xs = [int(beam_x1 + step * k) for k in (1, 2, 3, 4, 5)]
    support_pier_half_width = BRIDGE_SUPPORT_PIER_HALF_W

    # Pull the east-most support pillar in closer to the actual bridge pier at
    # beam_x2, instead of leaving it a full even-spacing step (~209 units)
    # away, and nudge its western neighbour east to open the gap between them.
    support_pier_xs[-1] = int(beam_x2 - 140)
    support_pier_xs[-2] = int(support_pier_xs[-2] + 60)

    # The beam stops short of the Pier 4 wall (beam_x1) and starts flush with
    # the first drop pillar's west face, leaving the west end open to match the
    # real building.
    beam_start_x = support_pier_xs[0] - support_pier_half_width

    brushes.append(
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

    # Foot the pillars at the hillside height along the bent's downhill edge so
    # they bury into the slope rather than floating off its high side.
    for pier_x in support_pier_xs:
        brushes.append(
            box(
                pier_x - support_pier_half_width,
                support_y1,
                _kh_hill_ground_z(pier_x, support_y2),
                pier_x + support_pier_half_width,
                support_y2,
                beam_bottom_z,
                Textures.CEMENT,
            )
        )

    _tie_x1 = support_pier_xs[-1]
    _tie_z = min(
        _kh_hill_ground_z(_tie_x1, support_y2),
        _kh_hill_ground_z(beam_x2, support_y2),
    )
    brushes.append(
        box(
            _tie_x1,
            support_y1,
            _tie_z,
            beam_x2,
            support_y2,
            _tie_z + beam_height,
            Textures.CEMENT,
        )
    )


def _build_knott_terrain():
    BRUSHES = []
    state = _knott_terrain_state()

    _append_knott_driveway_slabs(BRUSHES)
    _append_knott_east_far_south_fill(BRUSHES, state)
    _append_knott_west_far_south_fill(BRUSHES, state)
    _append_knott_west_grid_transitions(BRUSHES, state)
    _append_knott_west_driveway_ramp(BRUSHES, state)
    _append_knott_hillside_profile_fill(BRUSHES, state)
    _west_ext_y2, _east_ext_y2 = _append_knott_driveway_extension(BRUSHES)
    _append_knott_west_curb_return(BRUSHES, _west_ext_y2)
    _append_knott_east_curb_return(BRUSHES, _east_ext_y2)

    recess_joint_tops(BRUSHES, STREET_SW_JOINT_DROP, Textures.SIDEWALK_JOINT)

    return BRUSHES


def build():
    """Build the Knott Hall terrain, embankment, and driveway."""
    bent = []
    _append_knott_walkway_bent(bent)
    return _build_knott_terrain(), [brush_ent("func_detail", bent)]


def _kh_hill_ground_z(x, y):
    """Return the modeled Knott hillside ground height at ``(x, y)``."""
    _flat_z = FLOOR_Z2 + CHARLES_WALK_H
    _hill_profile = _kh_hill_profile()

    hz = _kh_hill_profile_z(x, _hill_profile)
    if y <= 0:
        return hz
    if y >= ENNIS_SW_EDGE:
        return _flat_z
    t = y / ENNIS_SW_EDGE
    return hz + (_flat_z - hz) * t
