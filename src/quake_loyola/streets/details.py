import math

from ..constants.derived import (
    CHARLES_CRN_R,
    CHARLES_LAMP_POST_H,
    CHARLES_LAMP_POST_XS,
    CHARLES_LAMP_POST_YS,
    ENNIS_CEMENT_X2,
    ENNIS_GATE_X2,
    ENNIS_PILLAR_X1,
    ENNIS_SW_EDGE,
    ENNIS_Y,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    KNOTT_DRIVEWAY_CURB_CRN_R,
    KNOTT_DRIVEWAY_CURB_CRN_SEGS,
    KNOTT_DRIVEWAY_ES_X1,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_EXT_Y2,
    KNOTT_DRIVEWAY_JCX_E,
    KNOTT_DRIVEWAY_JCX_X1,
    KNOTT_DRIVEWAY_JCY,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_WS_X1,
    KNOTT_DRIVEWAY_WS_X2,
    MANHOLE_R,
    MANHOLE_X,
    MANHOLE_Y,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
)
from ..constants.ennis import (
    ENNIS_CURB_BULGE_LEN,
    ENNIS_CURB_W,
    ENNIS_DIVIDER_EXTRA_N,
    ENNIS_HW,
    ENNIS_PILLAR_HW,
    ENNIS_WALL_PILLAR_HW,
    ENNIS_WALL_T,
    ENNIS_WALL_X_OFFSET,
    ENNIS_WIDEN_N,
)
from ..constants.flags import (
    KNOTT_ENABLED_TERRAIN,
    NE_ENABLED_TERRAIN,
    WEST_CAMPUS_ENABLED_TERRAIN,
)
from ..constants.streets import (
    CHARLES_CRN_SEGS,
    CHARLES_RAMP_W,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    CROSSWALK_GAP_W,
    CROSSWALK_LEN,
    CROSSWALK_STRIPE_W,
    ROAD_X1,
    ROAD_X2,
    STREET_CHARLES_CURB_W,
    STREET_DIV_HW,
    STREET_DIV_LINE_HW,
    STREET_ENNIS_DIV_HW,
    STREET_SURFACE_T,
)
from ..constants.textures import (
    Textures,
)
from ..constants.world import (
    FLOOR_Z1,
    FLOOR_Z2,
)
from ..geometry import (
    box,
    box_with_round_hole,
    brush_ent,
    curb_seg,
    ramp_slab_y,
    torch_flame,
    tri_prism,
)
from .ennis import _build_ennis_entrance_features


def punch_manhole_detail(brushes):
    """Cut the manhole opening through overlapping thin detail slabs.

    Brushes fully inside the hole are dropped; overlapping box slabs are
    rebuilt with box_with_round_hole(). Two independently-generated road
    slabs (e.g. Charles St. and Ennis Rd.) can physically overlap in this
    thin surface layer near the intersection, so each may be individually
    diced against the same manhole circle — de-duplicate the resulting
    brushes so identical wedges aren't emitted twice.
    """
    out = []
    seen = set()

    def _emit(brush):
        key = brush.to_map()
        if key in seen:
            return
        seen.add(key)
        out.append(brush)

    for b in brushes:
        pts = [p for f in b.faces for p in (f.p1, f.p2, f.p3)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        z1, z2 = min(zs), max(zs)
        is_thin_surface_layer = z1 >= FLOOR_Z2 - 1 and z2 <= FLOOR_Z2 + 20
        if not is_thin_surface_layer:
            _emit(b)
            continue

        def _dist(px, py):
            return math.hypot(px - MANHOLE_X, py - MANHOLE_Y)

        corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
        entirely_inside_circle = all(_dist(px, py) <= MANHOLE_R for px, py in corners)
        overlaps_circle_bbox = (
            x1 <= MANHOLE_X + MANHOLE_R
            and x2 >= MANHOLE_X - MANHOLE_R
            and y1 <= MANHOLE_Y + MANHOLE_R
            and y2 >= MANHOLE_Y - MANHOLE_R
        )
        if entirely_inside_circle:
            continue
        elif overlaps_circle_bbox and len(b.faces) == 6:
            tex = b.faces[0].tex
            tt_params = b.faces[-1].params
            for wedge in box_with_round_hole(
                x1,
                y1,
                z1,
                x2,
                y2,
                z2,
                MANHOLE_X,
                MANHOLE_Y,
                MANHOLE_R,
                tex,
                tt_params=tt_params,
            ):
                _emit(wedge)
        else:
            _emit(b)
    return out


def _build_street_details(BRUSHES, ENTITIES):
    """Build the detailed roadway, sidewalks, markings, and street fixtures."""

    DETAIL_BRUSHES = []
    _world_brushes = BRUSHES
    BRUSHES = DETAIL_BRUSHES

    CHARLES_Y1 = WORLD_Y1 + WALL_T
    CHARLES_Y2 = WORLD_Y2 - WALL_T

    def ranges_excluding(v1, v2, ex1, ex2):
        """Return the subranges of [v1, v2) that lie outside [ex1, ex2)."""
        ranges = []
        if ex1 > v1:
            ranges.append((v1, min(ex1, v2)))
        if ex2 < v2:
            ranges.append((max(ex2, v1), v2))
        return ranges

    CHARLES_CROSSING_Y2 = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
    CHARLES_CROSSING_Y1 = CHARLES_CROSSING_Y2 - CROSSWALK_LEN
    CHARLES_CROSSING_MID = (CHARLES_CROSSING_Y1 + CHARLES_CROSSING_Y2) / 2

    ENNIS_X1 = ROAD_X1
    ENNIS_X2 = WORLD_X2_EXT - WALL_T

    ENNIS_CROSSING_X1 = ROAD_X2
    ENNIS_CROSSING_X2 = ROAD_X2 + CHARLES_WALK_W

    ROAD_CX = (ROAD_X1 + ROAD_X2) / 2
    WEST_LANE_LINE_X = (ROAD_X1 + ROAD_CX - STREET_DIV_HW) / 2
    EAST_LANE_LINE_X = (ROAD_CX + STREET_DIV_HW + ROAD_X2) / 2

    _SW_SLAB_LEN = 80
    _SW_GAP = 2

    def sw_slabs_y(
        brushes,
        x1,
        x2,
        y1,
        y2,
        z_base,
        z_top,
        tex,
        tt_params="0 0 0 1 1",
        tile_overrides=None,
    ):
        """Tile a north-south sidewalk strip into panels.

        `tile_overrides` swaps textures for specific panel starts, and seamless
        textures are merged into continuous runs.
        """
        _seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
        step = _SW_SLAB_LEN + _SW_GAP
        segments = []
        y = y1
        while y < y2:
            sy2 = min(y + _SW_SLAB_LEN, y2)
            panel_tex = tex
            if tile_overrides:
                for oy, otex in tile_overrides:
                    if abs(oy - y) < 1:
                        panel_tex = otex
                        break
            if segments and segments[-1][2] == panel_tex and panel_tex in _seamless_tex:
                segments[-1][1] = sy2
            else:
                segments.append([y, sy2, panel_tex])
            y += step
        for seg_y1, seg_y2, panel_tex in segments:
            brushes.append(
                box(
                    x1,
                    seg_y1,
                    z_base,
                    x2,
                    seg_y2,
                    z_top,
                    panel_tex,
                    tt_params=tt_params,
                )
            )
        for (_, prev_end, _), (next_start, _, _) in zip(
            segments, segments[1:], strict=False
        ):
            if next_start > prev_end:
                brushes.append(
                    box(
                        x1,
                        prev_end,
                        z_base,
                        x2,
                        next_start,
                        z_top,
                        Textures.SIDEWALK_JOINT,
                    )
                )

    def sw_slabs_x(
        brushes,
        x1,
        x2,
        y1,
        y2,
        z_base,
        z_top,
        tex,
        tt_params="0 0 0 1 1",
        tex_from_x=None,
        tex_ranges=None,
    ):
        """Tile an east-west sidewalk strip into panels.

        `tex_from_x` and `tex_ranges` override textures by position, and
        seamless textures are merged into continuous runs.
        """
        _seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
        step = _SW_SLAB_LEN + _SW_GAP
        segments = []
        x = x1
        while x < x2:
            sx2 = min(x + _SW_SLAB_LEN, x2)
            panel_tex = tex
            if tex_from_x is not None and x >= tex_from_x[0]:
                panel_tex = tex_from_x[1]
            pieces = [[x, sx2, panel_tex, tt_params, None]]
            if tex_ranges:
                for rspec in tex_ranges:
                    rx1, rx2, rtex = rspec[0], rspec[1], rspec[2]
                    rparams = rspec[3] if len(rspec) > 3 else tt_params
                    r_inset = rspec[4] if len(rspec) > 4 else None
                    new_pieces = []
                    for px1, px2, ptex, pparams, pinset in pieces:
                        ox1, ox2 = max(px1, rx1), min(px2, rx2)
                        if ox1 >= ox2:
                            new_pieces.append([px1, px2, ptex, pparams, pinset])
                            continue
                        if px1 < ox1:
                            new_pieces.append([px1, ox1, ptex, pparams, pinset])
                        new_pieces.append([ox1, ox2, rtex, rparams, r_inset])
                        if ox2 < px2:
                            new_pieces.append([ox2, px2, ptex, pparams, pinset])
                    pieces = new_pieces
            for px1, px2, ptex, pparams, pinset in pieces:
                if (
                    segments
                    and segments[-1][2] == ptex
                    and segments[-1][3] == pparams
                    and segments[-1][4] == pinset
                    and ptex in _seamless_tex
                ):
                    segments[-1][1] = px2
                else:
                    segments.append([px1, px2, ptex, pparams, pinset])
            x += step
        for seg_x1, seg_x2, panel_tex, panel_params, y_north_inset in segments:
            seg_y2 = y2 - y_north_inset if y_north_inset else y2
            brushes.append(
                box(
                    seg_x1,
                    y1,
                    z_base,
                    seg_x2,
                    seg_y2,
                    z_top,
                    panel_tex,
                    tt_params=panel_params,
                )
            )
            if y_north_inset:
                brushes.append(
                    box(
                        seg_x1,
                        seg_y2,
                        z_base,
                        seg_x2,
                        y2,
                        z_top,
                        tex,
                        tt_params=tt_params,
                    )
                )
        for (_, prev_end, _, _, _), (next_start, _, _, _, _) in zip(
            segments, segments[1:], strict=False
        ):
            if next_start > prev_end:
                brushes.append(
                    box(
                        prev_end,
                        y1,
                        z_base,
                        next_start,
                        y2,
                        z_top,
                        Textures.SIDEWALK_JOINT,
                    )
                )

    def _append_charles_road_surfaces():
        """Add the Charles Street travel lanes around the pedestrian crossing."""
        for lane_x1, lane_x2 in (
            (ROAD_X1, WEST_LANE_LINE_X - STREET_DIV_LINE_HW),
            (
                WEST_LANE_LINE_X + STREET_DIV_LINE_HW,
                ROAD_CX - STREET_DIV_HW,
            ),
            (
                ROAD_CX + STREET_DIV_HW,
                EAST_LANE_LINE_X - STREET_DIV_LINE_HW,
            ),
            (EAST_LANE_LINE_X + STREET_DIV_LINE_HW, ROAD_X2),
        ):
            for lane_y1, lane_y2 in ranges_excluding(
                CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
            ):
                BRUSHES.append(
                    box(
                        lane_x1,
                        lane_y1,
                        FLOOR_Z2,
                        lane_x2,
                        lane_y2,
                        FLOOR_Z2 + STREET_SURFACE_T,
                        Textures.ROAD,
                    )
                )

    def _append_charles_sidewalks_and_curbs():
        """Add Charles Street sidewalks, curb cuts, and ramp slabs."""
        CHARLES_CURB_CUT_LEN = 2 * (_SW_SLAB_LEN + _SW_GAP)
        CHARLES_CURB_CUT_Y2 = CHARLES_CROSSING_MID + CHARLES_CURB_CUT_LEN
        CHARLES_CURB_RAMP_Y2 = CHARLES_CURB_CUT_Y2 + _SW_SLAB_LEN
        sw_slabs_y(
            BRUSHES,
            ROAD_X1 - CHARLES_WALK_W,
            ROAD_X1,
            CHARLES_CROSSING_MID,
            CHARLES_CURB_CUT_Y2,
            FLOOR_Z2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.SIDEWALK,
        )
        BRUSHES.append(
            ramp_slab_y(
                ROAD_X1 - CHARLES_WALK_W,
                ROAD_X1,
                CHARLES_CURB_CUT_Y2,
                CHARLES_CURB_RAMP_Y2,
                FLOOR_Z2,
                FLOOR_Z2,
                FLOOR_Z2 + STREET_SURFACE_T,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )
        _CHARLES_CURB_CAP_D = 8
        _CHARLES_CURB_GAP = 2
        sw_slabs_y(
            BRUSHES,
            ROAD_X1 - CHARLES_WALK_W,
            ROAD_X1 - _CHARLES_CURB_CAP_D - _CHARLES_CURB_GAP,
            CHARLES_CURB_RAMP_Y2 + _SW_GAP,
            CHARLES_Y2,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
        BRUSHES.append(
            box(
                ROAD_X1 - _CHARLES_CURB_CAP_D - _CHARLES_CURB_GAP,
                CHARLES_CURB_RAMP_Y2 + _SW_GAP,
                FLOOR_Z2,
                ROAD_X1 - _CHARLES_CURB_CAP_D,
                CHARLES_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK_JOINT,
            )
        )
        BRUSHES.append(
            box(
                ROAD_X1 - _CHARLES_CURB_CAP_D,
                CHARLES_CURB_RAMP_Y2 + _SW_GAP,
                FLOOR_Z2 + STREET_SURFACE_T,
                ROAD_X1,
                CHARLES_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )
        BRUSHES.append(
            box(
                ROAD_X1 - CHARLES_WALK_W,
                CHARLES_CROSSING_MID,
                FLOOR_Z2 + STREET_SURFACE_T,
                ROAD_X1,
                CHARLES_CROSSING_MID + 4,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )
        _RW_X2 = ROAD_X1 - CHARLES_WALK_W
        _RW_X1 = _RW_X2 - STREET_CHARLES_CURB_W
        BRUSHES.append(
            box(
                _RW_X1,
                CHARLES_CROSSING_MID,
                FLOOR_Z2 + STREET_SURFACE_T,
                _RW_X2,
                CHARLES_CURB_CUT_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )
        BRUSHES.append(
            ramp_slab_y(
                _RW_X1,
                _RW_X2,
                CHARLES_CURB_CUT_Y2,
                CHARLES_CURB_RAMP_Y2,
                FLOOR_Z2 + STREET_SURFACE_T,
                FLOOR_Z2 + CHARLES_WALK_H - STREET_SURFACE_T,
                FLOOR_Z2 + CHARLES_WALK_H,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )
        BRUSHES.append(
            box(
                ROAD_X1 - STREET_CHARLES_CURB_W,
                CHARLES_Y1,
                FLOOR_Z2,
                ROAD_X1,
                CHARLES_CROSSING_MID,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )
        BRUSHES.append(
            box(
                ROAD_X1 - CHARLES_WALK_W,
                CHARLES_Y1,
                FLOOR_Z2,
                ROAD_X1 - STREET_CHARLES_CURB_W,
                CHARLES_CROSSING_MID,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        for _seg_y1, _seg_y2, _seg_overrides in (
            (
                CHARLES_Y1,
                ENNIS_Y - ENNIS_HW - CHARLES_WALK_W,
                [(508, Textures.WHITE_STONE)],
            ),
            (ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W, CHARLES_Y2, None),
        ):
            sw_slabs_y(
                BRUSHES,
                ROAD_X2 + _CHARLES_CURB_CAP_D + _CHARLES_CURB_GAP,
                ROAD_X2 + CHARLES_WALK_W,
                _seg_y1,
                _seg_y2,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
                tile_overrides=_seg_overrides,
            )
            BRUSHES.append(
                box(
                    ROAD_X2 + _CHARLES_CURB_CAP_D,
                    _seg_y1,
                    FLOOR_Z2,
                    ROAD_X2 + _CHARLES_CURB_CAP_D + _CHARLES_CURB_GAP,
                    _seg_y2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.SIDEWALK_JOINT,
                )
            )
            BRUSHES.append(
                box(
                    ROAD_X2,
                    _seg_y1,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    ROAD_X2 + _CHARLES_CURB_CAP_D,
                    _seg_y2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.SIDEWALK,
                )
            )

    ENNIS_ROAD_TT_PARAMS = "0 0 90 1 1"
    _ennis_center_y = ENNIS_Y + ENNIS_WIDEN_N / 2 + ENNIS_DIVIDER_EXTRA_N

    def _append_ennis_road_and_sidewalks():
        """Add Ennis Road surfaces, dividers, sidewalks, and the curb bulge."""
        for wx1, wx2 in ranges_excluding(
            ENNIS_X1, ROAD_X2 + CHARLES_WALK_W, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
        ):
            BRUSHES.append(
                box(
                    wx1,
                    ENNIS_Y - ENNIS_HW,
                    FLOOR_Z2,
                    wx2,
                    _ennis_center_y - STREET_ENNIS_DIV_HW,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.ROAD,
                    tt_params=ENNIS_ROAD_TT_PARAMS,
                )
            )
        for road_x1, road_x2 in [
            (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1),
            (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2),
        ]:
            BRUSHES.append(
                box(
                    road_x1,
                    ENNIS_Y - ENNIS_HW,
                    FLOOR_Z2,
                    road_x2,
                    _ennis_center_y - STREET_ENNIS_DIV_HW,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.ROAD,
                    tt_params=ENNIS_ROAD_TT_PARAMS,
                )
            )
        BRUSHES.append(
            box(
                KNOTT_DRIVEWAY_CORRIDOR_X1,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2,
                KNOTT_DRIVEWAY_CORRIDOR_X2,
                _ennis_center_y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        for nx1, nx2 in ranges_excluding(
            ENNIS_X1, ENNIS_X2, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
        ):
            BRUSHES.append(
                box(
                    nx1,
                    _ennis_center_y + STREET_ENNIS_DIV_HW,
                    FLOOR_Z2,
                    nx2,
                    ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.ROAD,
                    tt_params=ENNIS_ROAD_TT_PARAMS,
                )
            )
        _ENNIS_CURB_CAP_D = 8
        _ENNIS_CURB_GAP = 2
        _ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
        _bw_cx = _ennis_wall_x1 + ENNIS_WALL_T // 2
        sw_slabs_x(
            BRUSHES,
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=ENNIS_ROAD_TT_PARAMS,
            tex_ranges=[
                (
                    _bw_cx - ENNIS_WALL_PILLAR_HW + 4,
                    ENNIS_PILLAR_X1,
                    Textures.WHITE_STONE,
                    ENNIS_ROAD_TT_PARAMS,
                ),
                (ENNIS_PILLAR_X1, ENNIS_GATE_X2, Textures.MULCH),
                (ENNIS_GATE_X2, ENNIS_X2, Textures.GROUND),
            ],
        )
        _CURB_BULGE_X1 = ENNIS_CEMENT_X2
        _CURB_BULGE_LEN = ENNIS_CURB_BULGE_LEN
        _CURB_BULGE_X2 = _CURB_BULGE_X1 + _CURB_BULGE_LEN
        BRUSHES.append(
            box(
                ROAD_X2 + CHARLES_WALK_W,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
                FLOOR_Z2,
                _CURB_BULGE_X1,
                ENNIS_Y
                + ENNIS_HW
                + ENNIS_WIDEN_N
                + _ENNIS_CURB_CAP_D
                + _ENNIS_CURB_GAP,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK_JOINT,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        BRUSHES.append(
            box(
                _CURB_BULGE_X2,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
                FLOOR_Z2,
                ENNIS_X2,
                ENNIS_Y
                + ENNIS_HW
                + ENNIS_WIDEN_N
                + _ENNIS_CURB_CAP_D
                + _ENNIS_CURB_GAP,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK_JOINT,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        _CURB_BULGE_HALF_LEN = _CURB_BULGE_LEN / 2
        _CURB_BULGE_DEPTH = _CURB_BULGE_HALF_LEN / 2
        _CURB_BULGE_CX = (_CURB_BULGE_X1 + _CURB_BULGE_X2) / 2
        _CURB_BULGE_SEGMENTS = 24
        _CURB_BULGE_FAR_Y = (
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D + _ENNIS_CURB_GAP
        )
        BRUSHES.append(
            box(
                ROAD_X2 + CHARLES_WALK_W,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
                FLOOR_Z2 + STREET_SURFACE_T,
                _CURB_BULGE_X1,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        _bulge_step = _CURB_BULGE_LEN / _CURB_BULGE_SEGMENTS

        def _bulge_depth_at(bx):
            bdx = bx - _CURB_BULGE_CX
            _t = max(1 - (bdx / _CURB_BULGE_HALF_LEN) ** 2, 0)
            return _CURB_BULGE_DEPTH * math.sqrt(_t)

        for _bi in range(_CURB_BULGE_SEGMENTS):
            _bx1 = _CURB_BULGE_X1 + _bi * _bulge_step
            _bx2 = _bx1 + _bulge_step
            _bd1 = _bulge_depth_at(_bx1)
            _bd2 = _bulge_depth_at(_bx2)
            _outer1_y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - _bd1
            _outer2_y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - _bd2
            _inner1_y = _outer1_y + _ENNIS_CURB_CAP_D
            _inner2_y = _outer2_y + _ENNIS_CURB_CAP_D
            _z1, _z2 = FLOOR_Z2 + STREET_SURFACE_T, FLOOR_Z2 + CHARLES_WALK_H
            BRUSHES.append(
                tri_prism(
                    _bx1,
                    _outer1_y,
                    _bx2,
                    _outer2_y,
                    _bx2,
                    _inner2_y,
                    _z1,
                    _z2,
                    Textures.SIDEWALK,
                )
            )
            BRUSHES.append(
                tri_prism(
                    _bx1,
                    _outer1_y,
                    _bx2,
                    _inner2_y,
                    _bx1,
                    _inner1_y,
                    _z1,
                    _z2,
                    Textures.SIDEWALK,
                )
            )
            if _bd1 > 0 or _bd2 > 0:
                BRUSHES.append(
                    tri_prism(
                        _bx1,
                        _inner1_y,
                        _bx2,
                        _inner2_y,
                        _bx2,
                        _CURB_BULGE_FAR_Y,
                        FLOOR_Z2,
                        _z2,
                        Textures.GROUND,
                    )
                )
                BRUSHES.append(
                    tri_prism(
                        _bx1,
                        _inner1_y,
                        _bx2,
                        _CURB_BULGE_FAR_Y,
                        _bx1,
                        _CURB_BULGE_FAR_Y,
                        FLOOR_Z2,
                        _z2,
                        Textures.GROUND,
                    )
                )
        BRUSHES.append(
            box(
                _CURB_BULGE_X2,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
                FLOOR_Z2 + STREET_SURFACE_T,
                ENNIS_X2,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + _ENNIS_CURB_CAP_D,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        _west_curb_x1 = ROAD_X2 + CHARLES_WALK_W
        _west_sw_d = CHARLES_WALK_W * 2 + 56
        _west_y1 = ENNIS_SW_EDGE + CHARLES_WALK_W - _west_sw_d
        _west_y2 = ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D - _ENNIS_CURB_GAP
        _west_north_y1 = _west_y2 - _SW_SLAB_LEN
        BRUSHES.append(
            box(
                _west_curb_x1,
                _west_y1,
                FLOOR_Z2,
                _west_curb_x1 + _SW_SLAB_LEN,
                _west_north_y1,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.WHITE_STONE,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        BRUSHES.append(
            box(
                _west_curb_x1,
                _west_north_y1,
                FLOOR_Z2,
                _west_curb_x1 + _SW_SLAB_LEN,
                _west_y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.CEMENT,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        for curb_x1, curb_x2, _sw_d, _tile_x1, _tex_from_x in (
            (
                _west_curb_x1,
                KNOTT_DRIVEWAY_WS_X1,
                CHARLES_WALK_W * 2 + 56,
                _west_curb_x1 + _SW_SLAB_LEN + _SW_GAP,
                (_west_curb_x1 + _SW_SLAB_LEN + _SW_GAP, Textures.WHITE_STONE),
            ),
            (
                KNOTT_DRIVEWAY_ES_X2,
                ENNIS_X2,
                CHARLES_WALK_W,
                KNOTT_DRIVEWAY_ES_X2,
                None,
            ),
        ):
            sw_slabs_x(
                BRUSHES,
                _tile_x1,
                curb_x2,
                ENNIS_SW_EDGE + CHARLES_WALK_W - _sw_d,
                ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D - _ENNIS_CURB_GAP,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
                tt_params=ENNIS_ROAD_TT_PARAMS,
                tex_from_x=_tex_from_x,
            )
            BRUSHES.append(
                box(
                    curb_x1,
                    ENNIS_SW_EDGE
                    + CHARLES_WALK_W
                    - _ENNIS_CURB_CAP_D
                    - _ENNIS_CURB_GAP,
                    FLOOR_Z2,
                    curb_x2,
                    ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.SIDEWALK_JOINT,
                    tt_params=ENNIS_ROAD_TT_PARAMS,
                )
            )
            BRUSHES.append(
                box(
                    curb_x1,
                    ENNIS_SW_EDGE + CHARLES_WALK_W - _ENNIS_CURB_CAP_D,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    curb_x2,
                    ENNIS_SW_EDGE + CHARLES_WALK_W,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.SIDEWALK,
                    tt_params=ENNIS_ROAD_TT_PARAMS,
                )
            )

    def _append_street_markings():
        """Add centerlines, lane stripes, and both crosswalks as func_detail."""
        dash_brushes = []
        _centerline_gap_hw = 2
        for line_x1, line_x2 in (
            (ROAD_CX - STREET_DIV_HW, ROAD_CX - _centerline_gap_hw),
            (ROAD_CX + _centerline_gap_hw, ROAD_CX + STREET_DIV_HW),
        ):
            for line_y1, line_y2 in ranges_excluding(
                CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
            ):
                dash_brushes.append(
                    box(
                        line_x1,
                        line_y1,
                        FLOOR_Z2,
                        line_x2,
                        line_y2,
                        FLOOR_Z2 + STREET_SURFACE_T,
                        Textures.CENTERLINE,
                    )
                )
        for gap_y1, gap_y2 in ranges_excluding(
            CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
        ):
            dash_brushes.append(
                box(
                    ROAD_CX - _centerline_gap_hw,
                    gap_y1,
                    FLOOR_Z2,
                    ROAD_CX + _centerline_gap_hw,
                    gap_y2,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.ROAD,
                )
            )
        for lane_line_x in (WEST_LANE_LINE_X, EAST_LANE_LINE_X):
            tex_offset_x = WEST_LANE_LINE_X - lane_line_x
            divider_tt_params = f"{tex_offset_x} 0 0 1 1"
            for seg_y1, seg_y2 in ranges_excluding(
                CHARLES_Y1, CHARLES_Y2, CHARLES_CROSSING_Y1, CHARLES_CROSSING_Y2
            ):
                dash_brushes.append(
                    box(
                        lane_line_x - STREET_DIV_LINE_HW,
                        seg_y1,
                        FLOOR_Z2,
                        lane_line_x + STREET_DIV_LINE_HW,
                        seg_y2,
                        FLOOR_Z2 + STREET_SURFACE_T,
                        Textures.PARKING_STRIPE,
                        tt_params=divider_tt_params,
                    )
                )
        _cx = ROAD_X1
        _stripe_on = True
        while _cx < ROAD_X2:
            next_cx = min(
                _cx + (CROSSWALK_STRIPE_W if _stripe_on else CROSSWALK_GAP_W), ROAD_X2
            )
            dash_brushes.append(
                box(
                    _cx,
                    CHARLES_CROSSING_Y1,
                    FLOOR_Z2,
                    next_cx,
                    CHARLES_CROSSING_Y2,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.PARKING_STRIPE if _stripe_on else Textures.ROAD,
                )
            )
            _cx = next_cx
            _stripe_on = not _stripe_on
        _ennis_line_hw = STREET_DIV_LINE_HW
        _ennis_line_x1 = ENNIS_PILLAR_X1 + ENNIS_PILLAR_HW
        for gx1, gx2 in ranges_excluding(
            ROAD_X2, _ennis_line_x1, ENNIS_CROSSING_X1, ENNIS_CROSSING_X2
        ):
            dash_brushes.append(
                box(
                    gx1,
                    _ennis_center_y - STREET_ENNIS_DIV_HW,
                    FLOOR_Z2,
                    gx2,
                    _ennis_center_y + STREET_ENNIS_DIV_HW,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.ROAD,
                    tt_params=ENNIS_ROAD_TT_PARAMS,
                )
            )
        dash_brushes.append(
            box(
                _ennis_line_x1,
                _ennis_center_y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                ENNIS_X2,
                _ennis_center_y - _ennis_line_hw,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        dash_brushes.append(
            box(
                _ennis_line_x1,
                _ennis_center_y - _ennis_line_hw,
                FLOOR_Z2,
                ENNIS_X2,
                _ennis_center_y + _ennis_line_hw,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.CENTERLINE,
            )
        )
        dash_brushes.append(
            box(
                _ennis_line_x1,
                _ennis_center_y + _ennis_line_hw,
                FLOOR_Z2,
                ENNIS_X2,
                _ennis_center_y + STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=ENNIS_ROAD_TT_PARAMS,
            )
        )
        _ey = ENNIS_Y - ENNIS_HW
        _ennis_crossing_y2 = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N
        _stripe_on = True
        while _ey < _ennis_crossing_y2:
            next_ey = min(
                _ey + (CROSSWALK_STRIPE_W if _stripe_on else CROSSWALK_GAP_W),
                _ennis_crossing_y2,
            )
            dash_brushes.append(
                box(
                    ENNIS_CROSSING_X1,
                    _ey,
                    FLOOR_Z2,
                    ENNIS_CROSSING_X2,
                    next_ey,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.PARKING_STRIPE if _stripe_on else Textures.ROAD,
                    tt_params=ENNIS_ROAD_TT_PARAMS if not _stripe_on else "0 0 0 1 1",
                )
            )
            _ey = next_ey
            _stripe_on = not _stripe_on
        if dash_brushes:
            ENTITIES.append(
                brush_ent("func_detail", punch_manhole_detail(dash_brushes))
            )

    def _append_intersection_corners():
        """Add the southeast and northeast Charles/Ennis corner geometry."""
        cx_se = ROAD_X2 + CHARLES_CRN_R
        cy_se = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
        BRUSHES.append(
            box(
                ROAD_X2,
                cy_se,
                FLOOR_Z2,
                cx_se,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
            )
        )
        for corner_index in range(CHARLES_CRN_SEGS):
            angle_start = math.radians(90 + corner_index * 90 / CHARLES_CRN_SEGS)
            angle_end = math.radians(90 + (corner_index + 1) * 90 / CHARLES_CRN_SEGS)
            arc_x0, arc_y0 = (
                cx_se + CHARLES_CRN_R * math.cos(angle_start),
                cy_se + CHARLES_CRN_R * math.sin(angle_start),
            )
            arc_x1, arc_y1 = (
                cx_se + CHARLES_CRN_R * math.cos(angle_end),
                cy_se + CHARLES_CRN_R * math.sin(angle_end),
            )
            BRUSHES.append(
                tri_prism(
                    cx_se,
                    cy_se,
                    arc_x0,
                    arc_y0,
                    arc_x1,
                    arc_y1,
                    FLOOR_Z2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.SIDEWALK,
                )
            )

        cx_ne = ROAD_X2 + CHARLES_CRN_R
        cy_ne = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_CRN_R
        BRUSHES.append(
            box(
                ROAD_X2,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
                FLOOR_Z2,
                cx_ne,
                cy_ne,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
            )
        )
        for corner_index in range(CHARLES_CRN_SEGS):
            angle_start = math.radians(180 + corner_index * 90 / CHARLES_CRN_SEGS)
            angle_end = math.radians(180 + (corner_index + 1) * 90 / CHARLES_CRN_SEGS)
            arc_x0, arc_y0 = (
                cx_ne + CHARLES_CRN_R * math.cos(angle_start),
                cy_ne + CHARLES_CRN_R * math.sin(angle_start),
            )
            arc_x1, arc_y1 = (
                cx_ne + CHARLES_CRN_R * math.cos(angle_end),
                cy_ne + CHARLES_CRN_R * math.sin(angle_end),
            )
            BRUSHES.append(
                tri_prism(
                    cx_ne,
                    cy_ne,
                    arc_x0,
                    arc_y0,
                    arc_x1,
                    arc_y1,
                    FLOOR_Z2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.SIDEWALK,
                )
            )

    def _append_verges_and_driveway_surfaces():
        """Add verge fill, driveway fills, and curb arcs south of Ennis Road."""
        _west_verge_x1 = (
            ROAD_X1 - CHARLES_WALK_W - CHARLES_RAMP_W
            if WEST_CAMPUS_ENABLED_TERRAIN
            else WORLD_X1 + WALL_T
        )
        _east_verge_x2 = WORLD_X2_EXT - WALL_T
        BRUSHES.append(
            box(
                _west_verge_x1,
                CHARLES_Y1,
                FLOOR_Z2,
                ROAD_X1 - CHARLES_WALK_W,
                CHARLES_Y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        _west_verge_y2 = ENNIS_SW_EDGE - CHARLES_WALK_W
        _east_verge_segs = (
            [
                (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, _west_verge_y2),
                (KNOTT_DRIVEWAY_CORRIDOR_X2, _east_verge_x2, ENNIS_SW_EDGE),
            ]
            if KNOTT_ENABLED_TERRAIN
            else [
                (ROAD_X2 + CHARLES_WALK_W, KNOTT.x2, _west_verge_y2),
                (KNOTT.x2, _east_verge_x2, ENNIS_SW_EDGE),
            ]
        )
        for _evx1, _evx2, _evy2 in _east_verge_segs:
            BRUSHES.append(
                box(
                    _evx1,
                    CHARLES_Y1,
                    FLOOR_Z2,
                    _evx2,
                    _evy2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.GROUND,
                )
            )
        if not NE_ENABLED_TERRAIN:
            BRUSHES.append(
                box(
                    ROAD_X2 + CHARLES_WALK_W,
                    ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
                    FLOOR_Z2,
                    ENNIS_X2,
                    CHARLES_Y2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.GROUND,
                )
            )

        _VERGE_CEMENT_X1 = ROAD_X2 + CHARLES_WALK_W
        _VERGE_CEMENT_X2 = _VERGE_CEMENT_X1 + _SW_SLAB_LEN
        for vx1, vx2, vtex in [
            (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, Textures.GROUND),
            (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2, Textures.MULCH),
        ]:
            vy1 = ENNIS_SW_EDGE + CHARLES_WALK_W
            vy2 = ENNIS_Y - ENNIS_HW - ENNIS_CURB_W
            if vtex == Textures.GROUND:
                BRUSHES.append(
                    box(
                        _VERGE_CEMENT_X1,
                        vy1,
                        FLOOR_Z1,
                        _VERGE_CEMENT_X2,
                        vy2,
                        FLOOR_Z2 + CHARLES_WALK_H,
                        Textures.CEMENT,
                    )
                )
                BRUSHES.append(
                    box(
                        _VERGE_CEMENT_X2,
                        vy1,
                        FLOOR_Z1,
                        vx2,
                        vy2,
                        FLOOR_Z2 + CHARLES_WALK_H,
                        vtex,
                    )
                )
            else:
                BRUSHES.append(
                    box(
                        vx1,
                        vy1,
                        FLOOR_Z1,
                        vx2,
                        vy2,
                        FLOOR_Z2 + CHARLES_WALK_H,
                        vtex,
                    )
                )

        for vx1, vx2 in [
            (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1),
            (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2),
        ]:
            BRUSHES.append(
                box(
                    vx1,
                    ENNIS_Y - ENNIS_HW - ENNIS_CURB_W,
                    FLOOR_Z1,
                    vx2,
                    ENNIS_Y - ENNIS_HW,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )

        if not KNOTT_ENABLED_TERRAIN:
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_WS_X1,
                    ENNIS_SW_EDGE,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_WS_X2,
                    ENNIS_SW_EDGE + CHARLES_WALK_W,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_RD_X1,
                    ENNIS_SW_EDGE,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_RD_X2,
                    ENNIS_SW_EDGE + CHARLES_WALK_W,
                    FLOOR_Z2 + 2,
                    Textures.ROAD,
                )
            )
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_ES_X1,
                    ENNIS_SW_EDGE,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_ES_X2,
                    ENNIS_SW_EDGE + CHARLES_WALK_W,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_WS_X1,
                    ENNIS_SW_EDGE + CHARLES_WALK_W,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_WS_X2 - ENNIS_CURB_W,
                    KNOTT_DRIVEWAY_EXT_Y2,
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
                    KNOTT_DRIVEWAY_EXT_Y2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_ES_X1 + ENNIS_CURB_W,
                    ENNIS_SW_EDGE + CHARLES_WALK_W,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_ES_X2,
                    KNOTT_DRIVEWAY_EXT_Y2,
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
                    KNOTT_DRIVEWAY_EXT_Y2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_RD_X1,
                    ENNIS_SW_EDGE + CHARLES_WALK_W,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_RD_X2,
                    ENNIS_Y - ENNIS_HW,
                    FLOOR_Z2 + 2,
                    Textures.ROAD,
                )
            )
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_WS_X1,
                    KNOTT_DRIVEWAY_EXT_Y2,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_RD_X1,
                    KNOTT_DRIVEWAY_JCY,
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
                        KNOTT_DRIVEWAY_EXT_Y2,
                        KNOTT_DRIVEWAY_JCX_X1 + _r_inner * math.cos(t0),
                        KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t0),
                        KNOTT_DRIVEWAY_JCX_X1 + _r_inner * math.cos(t1),
                        KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t1),
                        FLOOR_Z2,
                        FLOOR_Z2 + CHARLES_WALK_H,
                        Textures.GROUND,
                    )
                )
                BRUSHES.append(
                    curb_seg(
                        KNOTT_DRIVEWAY_JCX_X1,
                        KNOTT_DRIVEWAY_EXT_Y2,
                        FLOOR_Z2,
                        FLOOR_Z2 + CHARLES_WALK_H,
                        _r_inner,
                        _r_outer,
                        a0,
                        a1,
                        Textures.CEMENT,
                    )
                )
            BRUSHES.append(
                box(
                    KNOTT_DRIVEWAY_ES_X1,
                    KNOTT_DRIVEWAY_EXT_Y2,
                    FLOOR_Z2,
                    KNOTT_DRIVEWAY_ES_X2,
                    KNOTT_DRIVEWAY_JCY,
                    FLOOR_Z2 + 2,
                    Textures.ROAD,
                )
            )
            for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
                ea0 = 90 + corner_index * _seg_deg
                ea1 = 90 + (corner_index + 1) * _seg_deg
                t0, t1 = math.radians(ea0), math.radians(ea1)
                BRUSHES.append(
                    tri_prism(
                        KNOTT_DRIVEWAY_JCX_E,
                        KNOTT_DRIVEWAY_EXT_Y2,
                        KNOTT_DRIVEWAY_JCX_E + _r_inner * math.cos(t0),
                        KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t0),
                        KNOTT_DRIVEWAY_JCX_E + _r_inner * math.cos(t1),
                        KNOTT_DRIVEWAY_EXT_Y2 + _r_inner * math.sin(t1),
                        FLOOR_Z2,
                        FLOOR_Z2 + CHARLES_WALK_H,
                        Textures.MULCH,
                    )
                )
                BRUSHES.append(
                    curb_seg(
                        KNOTT_DRIVEWAY_JCX_E,
                        KNOTT_DRIVEWAY_EXT_Y2,
                        FLOOR_Z2,
                        FLOOR_Z2 + CHARLES_WALK_H,
                        _r_inner,
                        _r_outer,
                        ea0,
                        ea1,
                        Textures.CEMENT,
                    )
                )

    def _append_ennis_entrance_detail_features():
        """Append Ennis entrance walls, gates, and flames from west-campus code."""
        ennis_brushes, ennis_entities = _build_ennis_entrance_features()
        BRUSHES.extend(ennis_brushes)
        ENTITIES.extend(ennis_entities)

    def _append_lamp_details():
        """Add Charles Street lamp-post detail brushes and flame entities."""
        for lamp_x in CHARLES_LAMP_POST_XS:
            for lamp_y in CHARLES_LAMP_POST_YS:
                pole_top_z = FLOOR_Z2 + CHARLES_LAMP_POST_H
                DETAIL_BRUSHES.append(
                    box(
                        lamp_x - 2,
                        lamp_y - 2,
                        FLOOR_Z2,
                        lamp_x + 2,
                        lamp_y + 2,
                        pole_top_z,
                        Textures.PILLAR,
                    )
                )
                DETAIL_BRUSHES.append(
                    box(
                        lamp_x - 3,
                        lamp_y - 3,
                        pole_top_z,
                        lamp_x + 3,
                        lamp_y + 3,
                        pole_top_z + 16,
                        Textures.CEMENT,
                    )
                )
                DETAIL_BRUSHES.append(
                    box(
                        lamp_x - 5,
                        lamp_y - 5,
                        pole_top_z + 16,
                        lamp_x + 5,
                        lamp_y + 5,
                        pole_top_z + 20,
                        Textures.BRICK,
                    )
                )
                flame_z = pole_top_z + 20
                ENTITIES.extend(torch_flame(lamp_x, lamp_y, flame_z))

    _append_charles_road_surfaces()
    _append_charles_sidewalks_and_curbs()
    _append_ennis_road_and_sidewalks()
    _append_street_markings()
    _append_intersection_corners()
    _append_verges_and_driveway_surfaces()
    _append_ennis_entrance_detail_features()

    BRUSHES = _world_brushes

    _append_lamp_details()

    if DETAIL_BRUSHES:
        DETAIL_BRUSHES = punch_manhole_detail(DETAIL_BRUSHES)
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))

    # NOTE: the global world-seal brushes used to live here, but that made
    # leak-prevention geometry conditional on STREETS_ENABLED_DETAILS. They
    # now live in shell.py::_build_world_seal() and are always built by
    # streets/__init__.py::build() regardless of this flag.

    return BRUSHES, ENTITIES
