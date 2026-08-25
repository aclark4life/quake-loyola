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
    KNOTT_DOOR_WALK_PATH_PROUD,
    KNOTT_DOOR_WALK_PATH_TAIL,
    KNOTT_DOOR_WALK_RAIL_END,
    KNOTT_DOOR_WALK_RAIL_H,
    KNOTT_DOOR_WALK_RAIL_OVH,
    KNOTT_DOOR_WALK_RAIL_T,
    KNOTT_DOOR_WALK_RISE,
    KNOTT_DOOR_WALK_STEPS,
    KNOTT_DOOR_WALK_TREAD,
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
    KNOTT_EAST_WALK_RAIL_END,
    KNOTT_EAST_WALK_RAIL_H,
    KNOTT_EAST_WALK_RAIL_OVH,
    KNOTT_EAST_WALK_RAIL_T,
    KNOTT_EAST_WALK_RISERS,
    KNOTT_EAST_WALK_TREAD,
    KNOTT_EAST_WALK_W,
    KNOTT_ENT_WALK_ZT1,
    KNOTT_RAMP_PILLAR_GAP,
    KNOTT_RAMP_RAIL_H,
    KNOTT_RAMP_RAIL_LOOP_H,
    KNOTT_RAMP_RAIL_OVH,
    KNOTT_RAMP_RAIL_POSTS,
    KNOTT_RAMP_RAIL_T,
    KNOTT_RAMP_RISE_RUN,
    KNOTT_RAMP_RISE_RUN_MIN,
    KNOTT_RAMP_W,
    KNOTT_SUPPORT_PILLAR_JOINT_H,
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
    carve_box,
    curb_seg,
    cut_sidewalk_joints,
    loop_railing_x,
    ramp_slab,
    ramp_slab_y,
    sidewalk_panel_spans,
    stair_railing_x,
    stair_railing_y,
    straight_stair_x,
    straight_stair_y,
    tri_prism,
    tri_ramp_prism,
)
from ..knott_hall import (
    BUILDING_H,
    GROUND_DOOR_BOTTOM,
    GROUND_DOOR_X1,
    GROUND_DOOR_X2,
    KH_GROUND_Z,
    KH_NORTH_X1,
    KH_NORTH_X2,
    KH_NOTCH_Y,
    KH_X1,
    KH_X2,
    KH_Y1,
    KH_Y2,
)
from ..knott_hall import (
    WALL_T as KH_WALL_T,
)

# The hillside's flat crest ends — and its north slope begins — at Knott's
# north wall. The crest used to stop at y = 0, 13 units north of the wall,
# which left the fill's 86-unit top coplanar with the entrance and east walks
# over that strip: a band of ground z-fighting the cement along the facade.
KH_CREST_Y = KH_Y2


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
    brushes, x1, x2, y1, y2, top_z_s, top_z_n, surface_tex, side_tex=None
):
    """Add one full-depth sloped sidewalk slab.

    The slab's east and west faces (``ts``) are the curb sides exposed to the
    driveway, so they take the walking surface's texture rather than ground.
    ``side_tex`` overrides that side texture independently of ``surface_tex``,
    so a joint's marker can be confined to the top face without also
    repainting the full-height exposed side below it.
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
            ts=side_tex or surface_tex,
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
    for span, tex, side_tex in [
        (panels, surface_tex, None),
        (joints, Textures.SIDEWALK_JOINT, surface_tex),
    ]:
        for py1, py2 in span:
            _append_sloped_sidewalk_slab(
                brushes, x1, x2, py1, py2, _top_z(py1), _top_z(py2), tex, side_tex
            )


def _append_sloped_ramp_slab_x(
    brushes, x1, x2, y1, y2, top_z_w, top_z_e, surface_tex, side_tex=None
):
    """Add one full-depth slab whose top slopes along X.

    The counterpart to ``_append_sloped_sidewalk_slab`` for an east-west run.
    Both long sides take the walking surface's texture: unlike a curbed walk,
    a ramp standing off the hillside shows cement all the way down. ``side_tex``
    overrides that side texture independently of ``surface_tex``, so a joint's
    marker stays confined to the top face instead of also repainting the
    full-height exposed side below it.
    """
    brushes.append(
        ramp_slab(
            x1,
            x2,
            y1,
            y2,
            FLOOR_Z1,
            FLOOR_Z1,
            top_z_w,
            top_z_e,
            Textures.GROUND,
            tt=surface_tex,
            ts=side_tex or surface_tex,
        )
    )


def _append_tiled_sloped_ramp_x(brushes, x1, x2, y1, y2, top_z_w, top_z_e, surface_tex):
    """Tile an east-west sloped run into panels, like the Ennis Rd walks."""

    def _top_z(x):
        return top_z_w + (x - x1) * (top_z_e - top_z_w) / (x2 - x1)

    panels, joints = sidewalk_panel_spans(x1, x2, STREET_SW_SLAB_LEN, STREET_SW_GAP)
    for span, tex, side_tex in [
        (panels, surface_tex, None),
        (joints, Textures.SIDEWALK_JOINT, surface_tex),
    ]:
        for px1, px2 in span:
            _append_sloped_ramp_slab_x(
                brushes, px1, px2, y1, y2, _top_z(px1), _top_z(px2), tex, side_tex
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
    _y0_ext = KH_CREST_Y + state["WRAMP_OVR"]

    for (px1, _), (px2, _) in zip(_hill_profile, _hill_profile[1:], strict=False):
        z1 = _kh_hill_profile_z(px1, _hill_profile)
        z2 = _kh_hill_profile_z(px2, _hill_profile)
        zs1, zs2 = _knott_south_edge_z(px1, state), _knott_south_edge_z(px2, state)
        _t0 = (_y0_ext - KNOTT_DRIVEWAY_Y2) / (KH_CREST_Y - KNOTT_DRIVEWAY_Y2)
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
                KH_CREST_Y,
                px2,
                KH_CREST_Y,
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
                KH_CREST_Y,
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
    # stone apron below, so these all stop at ENNIS_SW_EDGE — except where the
    # accessible ramp takes over: it comes down to the roadbed at the gutter,
    # cutting the curb, so the walk gives way to its deck at the cut.
    _curb_cut_y1 = _knott_ramp_curb_cut_y1()
    _append_tiled_flat_sidewalk_y(
        brushes,
        KNOTT_DRIVEWAY_WS_X1,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - STREET_SW_GAP,
        KNOTT_DRIVEWAY_EXT_Y1,
        _curb_cut_y1,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.CEMENT,
    )
    _append_flat_sidewalk_slab(
        brushes,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - STREET_SW_GAP,
        KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
        KNOTT_DRIVEWAY_EXT_Y1,
        _curb_cut_y1,
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
        (KNOTT_DRIVEWAY_EXT_Y1, _curb_cut_y1),
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


def _knott_door_walk_layout():
    """Return the north walk's ``(stair_y1, stair_y2, stair_z2)`` layout.

    The walk runs level from the doorway to ``stair_y1``, drops a single
    flight to ``stair_z2`` at ``stair_y2``, and finishes as a cement path
    laid down the hillside to the Ennis walk. The flight is placed where its
    bottom tread lands the path at ground level — a slab thickness proud of
    the hillside — so a taller flight sits further out towards Ennis.
    """
    flat_z = FLOOR_Z2 + CHARLES_WALK_H
    run = KNOTT_DOOR_WALK_STEPS * KNOTT_DOOR_WALK_TREAD
    stair_z2 = GROUND_DOOR_BOTTOM - KNOTT_DOOR_WALK_STEPS * KNOTT_DOOR_WALK_RISE
    if stair_z2 <= flat_z:
        raise ValueError(
            f"KNOTT_DOOR_WALK_STEPS={KNOTT_DOOR_WALK_STEPS} drops the walk to "
            f"{stair_z2}, at or below the Ennis walk at {flat_z}"
        )

    cx = (GROUND_DOOR_X1 + GROUND_DOOR_X2) / 2
    lo, hi = KH_Y2 + run, ENNIS_SW_EDGE
    for _ in range(64):
        mid = (lo + hi) / 2
        if _kh_hill_ground_z(cx, mid) + KNOTT_DOOR_WALK_PATH_PROUD > stair_z2:
            lo = mid
        else:
            hi = mid
    stair_y2 = 4 * math.ceil(hi / 4)
    if stair_y2 - run < KH_Y2:
        raise ValueError(
            f"KNOTT_DOOR_WALK_STEPS={KNOTT_DOOR_WALK_STEPS} needs the stair to "
            f"start at {stair_y2 - run}, south of the Knott north wall at "
            f"{KH_Y2}"
        )
    if stair_y2 >= ENNIS_SW_EDGE:
        raise ValueError(
            f"KNOTT_DOOR_WALK_STEPS={KNOTT_DOOR_WALK_STEPS} lands the stair at "
            f"y={stair_y2}, at or past the Ennis walk at {ENNIS_SW_EDGE}"
        )
    return stair_y2 - run, stair_y2, stair_z2


def _append_knott_entrance_walk(brushes):
    """Build the walk outside the Knott ground-level north door.

    The door opens at grade on the flat crest of the hillside, so the walk
    runs level off the threshold, takes a single flight of steps down where
    the hillside starts to fall away, and then follows the slope to Ennis as
    a plain cement path, ramping the last of the hillside's height away where
    it runs out onto open ground.

    A clip wedge rides the nosings of the flight. Without it the player's
    collision hull, expanded off the path's slope, catches on the bottom
    tread and the run up reads as a bump rather than a smooth ascent.
    """
    x1, x2 = GROUND_DOOR_X1, GROUND_DOOR_X2
    flat_z = FLOOR_Z2 + CHARLES_WALK_H
    stair_y1, stair_y2, stair_z2 = _knott_door_walk_layout()

    # The hillside fills are coarse enough that the crest strip crosses the
    # wall line a little above the modeled grade, leaving a lip of ground
    # standing through the cement on the threshold. Cut the level run's
    # footprint out of the ground before laying it, so the walk stands alone.
    brushes[:] = carve_box(
        brushes,
        x1,
        KH_Y2,
        FLOOR_Z1,
        x2,
        stair_y1,
        KH_GROUND_Z + BUILDING_H,
        Textures.GROUND,
    )

    _append_tiled_flat_sidewalk_y(
        brushes,
        x1,
        x2,
        KH_Y2,
        stair_y1,
        FLOOR_Z1,
        GROUND_DOOR_BOTTOM,
        Textures.CEMENT,
    )
    brushes.extend(
        straight_stair_y(
            x1,
            x2,
            stair_y1,
            FLOOR_Z1,
            GROUND_DOOR_BOTTOM - KNOTT_DOOR_WALK_RISE,
            KNOTT_DOOR_WALK_STEPS,
            -KNOTT_DOOR_WALK_RISE,
            KNOTT_DOOR_WALK_TREAD,
            Textures.CEMENT,
        )
    )
    brushes.append(
        ramp_slab_y(
            x1,
            x2,
            stair_y1,
            stair_y2,
            FLOOR_Z1,
            FLOOR_Z1,
            GROUND_DOOR_BOTTOM,
            stair_z2,
            Textures.CLIP,
        )
    )
    brushes.append(
        ramp_slab_y(
            x1,
            x2,
            stair_y2,
            ENNIS_SW_EDGE,
            FLOOR_Z1,
            FLOOR_Z1,
            stair_z2,
            flat_z,
            Textures.CEMENT,
        )
    )
    brushes.append(
        ramp_slab_y(
            x1,
            x2,
            ENNIS_SW_EDGE,
            ENNIS_SW_EDGE + KNOTT_DOOR_WALK_PATH_TAIL,
            FLOOR_Z1,
            FLOOR_Z1,
            flat_z,
            FLOOR_Z2,
            Textures.CEMENT,
        )
    )


def _append_knott_entrance_walk_rails(brushes):
    """Build the pipe rails flanking the north walk's flight of steps.

    Only the steps are railed, as at the building's east entrance: the level
    walk above them starts at grade by the door, and the path below them lies
    on the hillside. Each rail runs on level past both ends of the flight,
    where its only two posts stand.
    """
    stair_y1, stair_y2, stair_z2 = _knott_door_walk_layout()
    rail_t = KNOTT_DOOR_WALK_RAIL_T
    for rx1, rx2 in (
        (GROUND_DOOR_X1, GROUND_DOOR_X1 + rail_t),
        (GROUND_DOOR_X2 - rail_t, GROUND_DOOR_X2),
    ):
        brushes.extend(
            stair_railing_y(
                rx1,
                rx2,
                stair_y1,
                stair_y2,
                GROUND_DOOR_BOTTOM,
                stair_z2,
                KNOTT_DOOR_WALK_RAIL_H,
                Textures.RAIL,
                rail_t=rail_t,
                post_w=rail_t,
                end_run=KNOTT_DOOR_WALK_RAIL_END,
                post_ovh=KNOTT_DOOR_WALK_RAIL_OVH,
            )
        )


def _knott_east_walk_layout():
    """Return the east walk's ``(stair_x1, stair_x2, rise)`` layout.

    The walk runs level along the Knott north face to ``stair_x1``, then
    drops the bank to the driveway in ``KNOTT_EAST_WALK_RISERS`` even risers,
    the last of which lands on the driveway's west sidewalk at ``stair_x2``.
    The flight is placed as far west as it can go with every tread still at
    or above the bank, so it hugs the slope rather than standing off it.
    """
    flat_z = FLOOR_Z2 + CHARLES_WALK_H
    drop = GROUND_DOOR_BOTTOM - flat_z
    risers = KNOTT_EAST_WALK_RISERS
    if drop % risers:
        raise ValueError(
            f"KNOTT_EAST_WALK_RISERS={risers} does not divide the {drop}-unit "
            f"drop from the Knott crest at {GROUND_DOOR_BOTTOM} to the "
            f"driveway walk at {flat_z} into even risers"
        )
    rise = drop // risers
    tread = KNOTT_EAST_WALK_TREAD
    run = risers * tread
    walk_y2 = KH_Y2 + KNOTT_EAST_WALK_W
    # The bank is highest along the building face, so testing there tests the
    # whole width; each tread is lowest at its west edge, where it meets the
    # riser above it.
    east_limit = KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W - KNOTT_EAST_WALK_RAIL_END
    walk_x1 = 4 * math.ceil(GROUND_DOOR_X2 / 4)
    for stair_x1 in range(walk_x1, int(east_limit - run), 4):
        if all(
            GROUND_DOOR_BOTTOM - rise * (i + 1)
            >= _kh_hill_ground_z(stair_x1 + i * tread, KH_Y2)
            for i in range(risers - 1)
        ):
            break
    else:
        raise ValueError(
            f"no room for a {risers}-riser east walk flight of {tread}-unit "
            f"treads between the Knott north door and the driveway walk"
        )
    if _kh_hill_ground_z(stair_x1 + run, walk_y2) > flat_z:
        raise ValueError(
            f"the east walk flight lands at x={stair_x1 + run}, still on the "
            f"bank rather than at the driveway walk level of {flat_z}"
        )
    return stair_x1, stair_x1 + run, rise


def _append_knott_east_walk(brushes):
    """Build the walk running east from the Knott north door to the driveway.

    It hugs the building's north face across the flat crest of the hillside,
    then takes the bank down to the driveway in a single steep flight. The
    bottom riser steps straight onto the driveway's west sidewalk, so that
    walk serves as the flight's last tread and nothing is built there.
    """
    stair_x1, stair_x2, rise = _knott_east_walk_layout()
    y1, y2 = KH_Y2, KH_Y2 + KNOTT_EAST_WALK_W

    _append_tiled_flat_sidewalk_x(
        brushes,
        GROUND_DOOR_X2,
        stair_x1,
        y1,
        y2,
        FLOOR_Z1,
        GROUND_DOOR_BOTTOM,
        Textures.CEMENT,
    )
    brushes.extend(
        straight_stair_x(
            stair_x1,
            y1,
            y2,
            FLOOR_Z1,
            GROUND_DOOR_BOTTOM - rise,
            KNOTT_EAST_WALK_RISERS - 1,
            -rise,
            KNOTT_EAST_WALK_TREAD,
            Textures.CEMENT,
        )
    )


def _append_knott_east_walk_rails(brushes):
    """Build the pipe rails flanking the east walk's flight of steps.

    The flight is the steepest run on the hillside and both its sides stand
    clear of the building, so it is railed either side like the north one.
    """
    stair_x1, stair_x2, _rise = _knott_east_walk_layout()
    flat_z = FLOOR_Z2 + CHARLES_WALK_H
    rail_t = KNOTT_EAST_WALK_RAIL_T
    for ry1, ry2 in (
        (KH_Y2, KH_Y2 + rail_t),
        (KH_Y2 + KNOTT_EAST_WALK_W - rail_t, KH_Y2 + KNOTT_EAST_WALK_W),
    ):
        brushes.extend(
            stair_railing_x(
                ry1,
                ry2,
                stair_x1,
                stair_x2,
                GROUND_DOOR_BOTTOM,
                flat_z,
                KNOTT_EAST_WALK_RAIL_H,
                Textures.RAIL,
                rail_t=rail_t,
                post_w=rail_t,
                end_run=KNOTT_EAST_WALK_RAIL_END,
                post_ovh=KNOTT_EAST_WALK_RAIL_OVH,
            )
        )


def _knott_ramp_foot_z():
    """Return the Z the ramp's deck meets the driveway at.

    The ramp runs unbroken from the roadbed rather than stopping at the walk
    behind the curb, so its foot sits at the road surface and the curb is cut
    away over the ramp's width. That costs the run a curb's worth of extra
    rise, which is why the grade lands short of ``KNOTT_RAMP_RISE_RUN``.
    """
    return FLOOR_Z2 + STREET_SURFACE_T


def _knott_ramp_curb_cut_y1():
    """Return the Y the driveway's west walk and curb give way to the ramp.

    North of it the ramp's own deck is the walking surface all the way to the
    roadbed, so the walk, its joint, and the curb strip all stop here rather
    than running on to the Ennis walk and burying the cut.
    """
    return _knott_ramp_layout()[1] - KNOTT_RAMP_W / 2


def _knott_ramp_layout():
    """Return the accessible ramp's ``(turn_x, cy, corner_z, grade)``.

    The ramp's two ends are fixed: it leaves the driveway roadbed at the
    gutter and lands on the east walk's level run at the crest height. What is
    derived is where it turns between them. Working back from a
    ``1:KNOTT_RAMP_RISE_RUN`` grade gives the landing's X; the landing is then
    pushed east far enough to thread the south leg between the drop pillars
    under the bridge span, and the grade recomputed from the run that leaves.
    """
    hw = KNOTT_RAMP_W / 2
    foot_z = _knott_ramp_foot_z()
    rise = GROUND_DOOR_BOTTOM - foot_z

    cy = ENNIS_SW_EDGE - hw
    head_y = KH_Y2 + KNOTT_EAST_WALK_W
    south_run = (cy - hw) - head_y
    if south_run <= 0:
        raise ValueError(
            f"KNOTT_RAMP_W={KNOTT_RAMP_W} leaves no south leg between the "
            f"Ennis walk at {ENNIS_SW_EDGE} and the east walk at {head_y}"
        )

    foot_x = KNOTT_DRIVEWAY_WS_X2
    turn_x = foot_x - hw - (KNOTT_RAMP_RISE_RUN * rise - south_run)
    _sy1, _sy2, pillar_xs, pillar_hw = _knott_walkway_bent_layout()
    for pillar_x in sorted(pillar_xs):
        blocked_x1 = pillar_x - pillar_hw - KNOTT_RAMP_PILLAR_GAP - hw
        blocked_x2 = pillar_x + pillar_hw + KNOTT_RAMP_PILLAR_GAP + hw
        if blocked_x1 < turn_x < blocked_x2:
            turn_x = blocked_x2
    turn_x = 4 * math.ceil(turn_x / 4)

    west_run = foot_x - (turn_x + hw)
    if west_run <= 0:
        raise ValueError(
            f"the ramp's landing is derived at x={turn_x}, at or east of "
            f"its foot on the driveway walk at {foot_x}"
        )
    run = west_run + south_run
    if run < KNOTT_RAMP_RISE_RUN_MIN * rise:
        raise ValueError(
            f"the ramp only has {run} units of run for its {rise}-unit rise, "
            f"a 1:{run / rise:.1f} grade steeper than the "
            f"1:{KNOTT_RAMP_RISE_RUN_MIN} minimum"
        )

    walk_x1, stair_x1 = GROUND_DOOR_X2, _knott_east_walk_layout()[0]
    if turn_x - hw < walk_x1 or turn_x + hw > stair_x1:
        raise ValueError(
            f"the ramp's south leg spans x={turn_x - hw}..{turn_x + hw}, off "
            f"the east walk's level run of {walk_x1}..{stair_x1}"
        )
    return turn_x, cy, foot_z + west_run * rise / run, rise / run


def _append_knott_ramp(brushes):
    """Build the accessible ramp from the Knott driveway up to the east walk.

    Two legs and a landing: west along the foot of the Ennis walk, a level
    turn where it is clear of the bridge's drop pillars, then south down the
    hillside on to the east walk's level run, which carries on to the north
    door. Both legs are poured full depth from ``FLOOR_Z1``, so where the deck
    stands off the hillside the slab's own side is the retaining wall.
    """
    hw = KNOTT_RAMP_W / 2
    foot_x = KNOTT_DRIVEWAY_WS_X2
    turn_x, cy, corner_z, _grade = _knott_ramp_layout()

    _append_tiled_sloped_ramp_x(
        brushes,
        turn_x + hw,
        foot_x,
        cy - hw,
        cy + hw,
        corner_z,
        _knott_ramp_foot_z(),
        Textures.CEMENT,
    )
    brushes.append(
        box(
            turn_x - hw,
            cy - hw,
            FLOOR_Z1,
            turn_x + hw,
            cy + hw,
            corner_z,
            Textures.CEMENT,
        )
    )
    _append_tiled_sloped_sidewalk(
        brushes,
        turn_x - hw,
        turn_x + hw,
        KH_Y2 + KNOTT_EAST_WALK_W,
        cy - hw,
        GROUND_DOOR_BOTTOM,
        corner_z,
        Textures.CEMENT,
    )


def _append_knott_ramp_rails(brushes):
    """Build the guardrail along the north side of the ramp's west leg.

    That leg climbs away from the Ennis walk running alongside it, so it is
    the one edge of the ramp with a drop off it. The rail is the accessible
    kind — a top rail and a lower one closed into a long O — carried on
    pillars set in from each end so the O overhangs them.
    """
    hw = KNOTT_RAMP_W / 2
    turn_x, cy, corner_z, _grade = _knott_ramp_layout()
    brushes.extend(
        loop_railing_x(
            cy + hw - KNOTT_RAMP_RAIL_T,
            cy + hw,
            turn_x + hw,
            KNOTT_DRIVEWAY_WS_X2,
            corner_z,
            _knott_ramp_foot_z(),
            KNOTT_RAMP_RAIL_H,
            Textures.RAIL_STEEL,
            rail_t=KNOTT_RAMP_RAIL_T,
            loop_h=KNOTT_RAMP_RAIL_LOOP_H,
            posts=KNOTT_RAMP_RAIL_POSTS,
            post_w=KNOTT_RAMP_RAIL_T,
            post_ovh=KNOTT_RAMP_RAIL_OVH,
        )
    )


def _knott_walkway_bent_layout():
    """Return the bent's ``(support_y1, support_y2, pillar_xs, half_w)``.

    The drop pillars are shared geometry: the accessible ramp has to thread
    its south leg between two of them, so their stations are worked out here
    rather than inline in the builder.
    """
    _bent_dy = BRIDGE_CENTER_SPAN_OFFSET[1]
    support_y_center = BRIDGE.y1 + BRIDGE_SUPPORT_HW + _bent_dy

    beam_x1, beam_x2 = BRIDGE_ARCH_X[3], BRIDGE_ARCH_X[4]
    step = (beam_x2 - beam_x1) / 6
    pillar_xs = [int(beam_x1 + step * k) for k in (1, 2, 3, 4, 5)]

    # Pull the east-most support pillar in closer to the actual bridge pier at
    # beam_x2, instead of leaving it a full even-spacing step (~209 units)
    # away, and nudge its western neighbour east to open the gap between them.
    pillar_xs[-1] = int(beam_x2 - 140)
    pillar_xs[-2] = int(pillar_xs[-2] + 60)

    return (
        support_y_center - BRIDGE_SUPPORT_HW,
        support_y_center + BRIDGE_SUPPORT_HW,
        pillar_xs,
        BRIDGE_SUPPORT_PIER_HALF_W,
    )


def _append_knott_walkway_bent(brushes):
    """Build the support bent under the span in front of the Knott entrance.

    A cement beam tucked against the deck underside, carried by drop pillars
    down to the hillside, plus a tie beam running on from the last pillar to
    the Pier 5 wall at the span's east end. The beam is split into three
    even-length segments, with a thin SIDEWALK_JOINT_FILL seam between them,
    each pillar is capped with the same seam where it meets the beam's
    underside, and the eastern-most pillar gets a matching seam where the
    ground-level tie beam picks up, so the bent reads as several separately
    poured elements rather than one continuous mass, the same treatment
    sidewalk panels get.
    """
    _bent_dz = BRIDGE_CENTER_SPAN_OFFSET[2]

    support_y1, support_y2, support_pier_xs, support_pier_half_width = (
        _knott_walkway_bent_layout()
    )

    beam_top_z = KNOTT_ENT_WALK_ZT1 - KNOTT.wall_t + _bent_dz
    beam_height = BRIDGE_SUPPORT_BEAM_H
    beam_bottom_z = beam_top_z - beam_height

    beam_x2 = BRIDGE_ARCH_X[4]

    # The beam stops short of the Pier 4 wall (beam_x1) and starts flush with
    # the first drop pillar's west face, leaving the west end open to match the
    # real building.
    beam_start_x = support_pier_xs[0] - support_pier_half_width

    # Split the beam into three even-length segments, each separated by a
    # thin joint seam, rather than one long, continuous pour.
    joint_h = KNOTT_SUPPORT_PILLAR_JOINT_H
    joint_hw = joint_h / 2
    beam_span = beam_x2 - beam_start_x
    seg_len = beam_span / 3
    split_xs = [beam_start_x + seg_len, beam_start_x + 2 * seg_len]
    seg_x1 = beam_start_x
    for split_x in split_xs:
        brushes.append(
            box(
                seg_x1,
                support_y1,
                beam_bottom_z,
                split_x - joint_hw,
                support_y2,
                beam_top_z,
                Textures.CEMENT,
            )
        )
        brushes.append(
            box(
                split_x - joint_hw,
                support_y1,
                beam_bottom_z,
                split_x + joint_hw,
                support_y2,
                beam_top_z,
                Textures.SIDEWALK_JOINT_FILL,
            )
        )
        seg_x1 = split_x + joint_hw
    brushes.append(
        box(
            seg_x1,
            support_y1,
            beam_bottom_z,
            beam_x2,
            support_y2,
            beam_top_z,
            Textures.CEMENT,
        )
    )

    # Foot the pillars at the hillside height along the bent's downhill edge so
    # they bury into the slope rather than floating off its high side. Each
    # pillar stops KNOTT_SUPPORT_PILLAR_JOINT_H short of the beam's underside;
    # a thin joint slab fills that gap, marking the pillar as its own poured
    # element rather than a continuous pour with the beam above it.
    pillar_top_z = beam_bottom_z - KNOTT_SUPPORT_PILLAR_JOINT_H
    for pier_x in support_pier_xs:
        brushes.append(
            box(
                pier_x - support_pier_half_width,
                support_y1,
                _kh_hill_ground_z(pier_x, support_y2),
                pier_x + support_pier_half_width,
                support_y2,
                pillar_top_z,
                Textures.CEMENT,
            )
        )
        brushes.append(
            box(
                pier_x - support_pier_half_width,
                support_y1,
                pillar_top_z,
                pier_x + support_pier_half_width,
                support_y2,
                beam_bottom_z,
                Textures.SIDEWALK_JOINT_FILL,
            )
        )

    # East face of the last pier, where the ground-level tie beam picks up
    # and runs on to the Pier 5 wall. A thin joint seam separates the two,
    # same treatment as the beam segment joints above, rather than the tie
    # beam butting straight into (and overlapping) the pier.
    _last_pier_x = support_pier_xs[-1]
    _tie_joint_x1 = _last_pier_x + support_pier_half_width
    _tie_x1 = _tie_joint_x1 + joint_hw
    _tie_z = min(
        _kh_hill_ground_z(_tie_x1, support_y2),
        _kh_hill_ground_z(beam_x2, support_y2),
    )
    brushes.append(
        box(
            _tie_joint_x1,
            support_y1,
            _tie_z,
            _tie_joint_x1 + joint_h,
            support_y2,
            _tie_z + beam_height,
            Textures.SIDEWALK_JOINT_FILL,
        )
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


def _knott_interior_rects():
    """Return the rectangles the Knott Hall interior floor is made of.

    The footprint steps in at both north corners, so the inside is not one
    rectangle but two: the full-width lower hall up to the notch, and the
    narrower upper one between the notch ledges. Both are inset by the wall
    thickness, so the floor stops at the inside face of every wall.

    A third strip fills the ground door's own reveal, where the north wall is
    cut through: left out, the floor would stop at the inside face and the
    player would cross a band of raw hillside standing in the doorway.
    """
    return (
        (KH_X1 + KH_WALL_T, KH_Y1 + KH_WALL_T, KH_X2 - KH_WALL_T, KH_NOTCH_Y),
        (
            KH_NORTH_X1 + KH_WALL_T,
            KH_NOTCH_Y,
            KH_NORTH_X2 - KH_WALL_T,
            KH_Y2 - KH_WALL_T,
        ),
        (GROUND_DOOR_X1, KH_Y2 - KH_WALL_T, GROUND_DOOR_X2, KH_Y2),
    )


def _knott_interior_floor(brushes):
    """Cut the hillside out of the Knott interior and lay an even floor in it.

    The building is a shell with no floor of its own, so what the player
    walked on inside was the raw hillside: it runs from below the door sill
    at the northeast corner to well over a hundred units above it at the
    southeast, where the bank climbs behind the building. Nothing about that
    is visible from outside — the walls hide all of it — so the ground under
    the footprint is cut away entirely and replaced with one slab, level with
    the ground door's sill so the player walks straight in.

    The ground is cut through its full depth rather than only above the new
    floor: cutting at the floor line would slice every sloped prism along it
    and leave far more slivers behind than taking the whole column out does.
    The cut runs up to the roofline, so the hall is open above the slab
    however high the hillside stood there.
    """
    out = list(brushes)
    for x1, y1, x2, y2 in _knott_interior_rects():
        out = carve_box(
            out, x1, y1, FLOOR_Z1, x2, y2, KH_GROUND_Z + BUILDING_H, Textures.GROUND
        )
        out.append(
            box(
                x1,
                y1,
                FLOOR_Z1,
                x2,
                y2,
                GROUND_DOOR_BOTTOM,
                Textures.ROOF_KH,
                tt=Textures.ROOF_KH,
            )
        )
    return out


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
    _append_knott_entrance_walk(BRUSHES)
    _append_knott_east_walk(BRUSHES)
    _append_knott_ramp(BRUSHES)

    cut_sidewalk_joints(
        BRUSHES,
        STREET_SW_JOINT_DROP,
        Textures.SIDEWALK_JOINT,
        Textures.SIDEWALK_JOINT_FILL,
    )

    return _knott_interior_floor(BRUSHES)


def build():
    """Build the Knott Hall terrain, embankment, and driveway."""
    detail = []
    _append_knott_walkway_bent(detail)
    _append_knott_entrance_walk_rails(detail)
    _append_knott_east_walk_rails(detail)
    _append_knott_ramp_rails(detail)
    return _build_knott_terrain(), [brush_ent("func_detail", detail)]


def _kh_hill_ground_z(x, y):
    """Return the modeled Knott hillside ground height at ``(x, y)``."""
    _flat_z = FLOOR_Z2 + CHARLES_WALK_H
    _hill_profile = _kh_hill_profile()

    hz = _kh_hill_profile_z(x, _hill_profile)
    if y <= KH_CREST_Y:
        return hz
    if y >= ENNIS_SW_EDGE:
        return _flat_z
    t = (y - KH_CREST_Y) / (ENNIS_SW_EDGE - KH_CREST_Y)
    return hz + (_flat_z - hz) * t
