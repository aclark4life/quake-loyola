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


def _street_detail_ranges_excluding(v1, v2, ex1, ex2):
    """Return the subranges of [v1, v2) that lie outside [ex1, ex2)."""
    ranges = []
    if ex1 > v1:
        ranges.append((v1, min(ex1, v2)))
    if ex2 < v2:
        ranges.append((max(ex2, v1), v2))
    return ranges


def _append_street_sidewalk_slabs_y(
    brushes,
    x1,
    x2,
    y1,
    y2,
    z_base,
    z_top,
    tex,
    sw_slab_len,
    sw_gap,
    tt_params="0 0 0 1 1",
    tile_overrides=None,
):
    """Tile a north-south sidewalk strip into panels."""
    seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
    step = sw_slab_len + sw_gap
    segments = []
    y = y1
    while y < y2:
        sy2 = min(y + sw_slab_len, y2)
        panel_tex = tex
        if tile_overrides:
            for oy, otex in tile_overrides:
                if abs(oy - y) < 1:
                    panel_tex = otex
                    break
        if segments and segments[-1][2] == panel_tex and panel_tex in seamless_tex:
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


def _append_street_sidewalk_slabs_x(
    brushes,
    x1,
    x2,
    y1,
    y2,
    z_base,
    z_top,
    tex,
    sw_slab_len,
    sw_gap,
    tt_params="0 0 0 1 1",
    tex_from_x=None,
    tex_ranges=None,
):
    """Tile an east-west sidewalk strip into panels."""
    seamless_tex = (Textures.WHITE_STONE, Textures.MULCH, Textures.GROUND)
    step = sw_slab_len + sw_gap
    segments = []
    x = x1
    while x < x2:
        sx2 = min(x + sw_slab_len, x2)
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
                and ptex in seamless_tex
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


def _make_street_detail_layout():
    """Compute the shared local geometry values for street-detail helpers."""
    charles_y1 = WORLD_Y1 + WALL_T
    charles_y2 = WORLD_Y2 - WALL_T
    charles_crossing_y2 = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
    charles_crossing_y1 = charles_crossing_y2 - CROSSWALK_LEN
    road_cx = (ROAD_X1 + ROAD_X2) / 2
    return {
        "charles_y1": charles_y1,
        "charles_y2": charles_y2,
        "charles_crossing_y1": charles_crossing_y1,
        "charles_crossing_y2": charles_crossing_y2,
        "charles_crossing_mid": (charles_crossing_y1 + charles_crossing_y2) / 2,
        "ennis_x1": ROAD_X1,
        "ennis_x2": WORLD_X2_EXT - WALL_T,
        "ennis_crossing_x1": ROAD_X2,
        "ennis_crossing_x2": ROAD_X2 + CHARLES_WALK_W,
        "road_cx": road_cx,
        "west_lane_line_x": (ROAD_X1 + road_cx - STREET_DIV_HW) / 2,
        "east_lane_line_x": (road_cx + STREET_DIV_HW + ROAD_X2) / 2,
        "sw_slab_len": 80,
        "sw_gap": 2,
        "ennis_road_tt_params": "0 0 90 1 1",
        "ennis_center_y": ENNIS_Y + ENNIS_WIDEN_N / 2 + ENNIS_DIVIDER_EXTRA_N,
    }


def _append_charles_road_surfaces(brushes, layout):
    """Add the Charles Street travel lanes around the pedestrian crossing."""
    for lane_x1, lane_x2 in (
        (ROAD_X1, layout["west_lane_line_x"] - STREET_DIV_LINE_HW),
        (
            layout["west_lane_line_x"] + STREET_DIV_LINE_HW,
            layout["road_cx"] - STREET_DIV_HW,
        ),
        (
            layout["road_cx"] + STREET_DIV_HW,
            layout["east_lane_line_x"] - STREET_DIV_LINE_HW,
        ),
        (layout["east_lane_line_x"] + STREET_DIV_LINE_HW, ROAD_X2),
    ):
        for lane_y1, lane_y2 in _street_detail_ranges_excluding(
            layout["charles_y1"],
            layout["charles_y2"],
            layout["charles_crossing_y1"],
            layout["charles_crossing_y2"],
        ):
            brushes.append(
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


def _append_charles_sidewalks_and_curbs(brushes, layout):
    """Add Charles Street sidewalks, curb cuts, and curb ramp slabs."""
    charles_curb_cut_len = 2 * (layout["sw_slab_len"] + layout["sw_gap"])
    charles_curb_cut_y2 = layout["charles_crossing_mid"] + charles_curb_cut_len
    charles_curb_ramp_y2 = charles_curb_cut_y2 + layout["sw_slab_len"]
    _append_street_sidewalk_slabs_y(
        brushes,
        ROAD_X1 - CHARLES_WALK_W,
        ROAD_X1,
        layout["charles_crossing_mid"],
        charles_curb_cut_y2,
        FLOOR_Z2,
        FLOOR_Z2 + STREET_SURFACE_T,
        Textures.SIDEWALK,
        layout["sw_slab_len"],
        layout["sw_gap"],
    )
    brushes.append(
        ramp_slab_y(
            ROAD_X1 - CHARLES_WALK_W,
            ROAD_X1,
            charles_curb_cut_y2,
            charles_curb_ramp_y2,
            FLOOR_Z2,
            FLOOR_Z2,
            FLOOR_Z2 + STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    charles_curb_cap_d = 8
    charles_curb_gap = 2
    _append_street_sidewalk_slabs_y(
        brushes,
        ROAD_X1 - CHARLES_WALK_W,
        ROAD_X1 - charles_curb_cap_d - charles_curb_gap,
        charles_curb_ramp_y2 + layout["sw_gap"],
        layout["charles_y2"],
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK,
        layout["sw_slab_len"],
        layout["sw_gap"],
    )
    brushes.append(
        box(
            ROAD_X1 - charles_curb_cap_d - charles_curb_gap,
            charles_curb_ramp_y2 + layout["sw_gap"],
            FLOOR_Z2,
            ROAD_X1 - charles_curb_cap_d,
            layout["charles_y2"],
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK_JOINT,
        )
    )
    brushes.append(
        box(
            ROAD_X1 - charles_curb_cap_d,
            charles_curb_ramp_y2 + layout["sw_gap"],
            FLOOR_Z2 + STREET_SURFACE_T,
            ROAD_X1,
            layout["charles_y2"],
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    brushes.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            layout["charles_crossing_mid"],
            FLOOR_Z2 + STREET_SURFACE_T,
            ROAD_X1,
            layout["charles_crossing_mid"] + 4,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    rw_x2 = ROAD_X1 - CHARLES_WALK_W
    rw_x1 = rw_x2 - STREET_CHARLES_CURB_W
    brushes.append(
        box(
            rw_x1,
            layout["charles_crossing_mid"],
            FLOOR_Z2 + STREET_SURFACE_T,
            rw_x2,
            charles_curb_cut_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    brushes.append(
        ramp_slab_y(
            rw_x1,
            rw_x2,
            charles_curb_cut_y2,
            charles_curb_ramp_y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H - STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    brushes.append(
        box(
            ROAD_X1 - STREET_CHARLES_CURB_W,
            layout["charles_y1"],
            FLOOR_Z2,
            ROAD_X1,
            layout["charles_crossing_mid"],
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    brushes.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            layout["charles_y1"],
            FLOOR_Z2,
            ROAD_X1 - STREET_CHARLES_CURB_W,
            layout["charles_crossing_mid"],
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    for seg_y1, seg_y2, seg_overrides in (
        (
            layout["charles_y1"],
            ENNIS_Y - ENNIS_HW - CHARLES_WALK_W,
            [(508, Textures.WHITE_STONE)],
        ),
        (
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
            layout["charles_y2"],
            None,
        ),
    ):
        _append_street_sidewalk_slabs_y(
            brushes,
            ROAD_X2 + charles_curb_cap_d + charles_curb_gap,
            ROAD_X2 + CHARLES_WALK_W,
            seg_y1,
            seg_y2,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            layout["sw_slab_len"],
            layout["sw_gap"],
            tile_overrides=seg_overrides,
        )
        brushes.append(
            box(
                ROAD_X2 + charles_curb_cap_d,
                seg_y1,
                FLOOR_Z2,
                ROAD_X2 + charles_curb_cap_d + charles_curb_gap,
                seg_y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK_JOINT,
            )
        )
        brushes.append(
            box(
                ROAD_X2,
                seg_y1,
                FLOOR_Z2 + STREET_SURFACE_T,
                ROAD_X2 + charles_curb_cap_d,
                seg_y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
            )
        )


def _append_ennis_road_surfaces(brushes, layout):
    """Add the Ennis Road travel surfaces on both sides of the center divider."""
    for wx1, wx2 in _street_detail_ranges_excluding(
        layout["ennis_x1"],
        ROAD_X2 + CHARLES_WALK_W,
        layout["ennis_crossing_x1"],
        layout["ennis_crossing_x2"],
    ):
        brushes.append(
            box(
                wx1,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2,
                wx2,
                layout["ennis_center_y"] - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=layout["ennis_road_tt_params"],
            )
        )
    for road_x1, road_x2 in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, layout["ennis_x2"]),
    ]:
        brushes.append(
            box(
                road_x1,
                ENNIS_Y - ENNIS_HW,
                FLOOR_Z2,
                road_x2,
                layout["ennis_center_y"] - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=layout["ennis_road_tt_params"],
            )
        )
    brushes.append(
        box(
            KNOTT_DRIVEWAY_CORRIDOR_X1,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_CORRIDOR_X2,
            layout["ennis_center_y"] - STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    for nx1, nx2 in _street_detail_ranges_excluding(
        layout["ennis_x1"],
        layout["ennis_x2"],
        layout["ennis_crossing_x1"],
        layout["ennis_crossing_x2"],
    ):
        brushes.append(
            box(
                nx1,
                layout["ennis_center_y"] + STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                nx2,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=layout["ennis_road_tt_params"],
            )
        )


def _append_ennis_north_sidewalks_and_curb_bulge(brushes, layout):
    """Add the north Ennis sidewalks, curb caps, and the curb bulge."""
    ennis_curb_cap_d = 8
    ennis_curb_gap = 2
    ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    bw_cx = ennis_wall_x1 + ENNIS_WALL_T // 2
    _append_street_sidewalk_slabs_x(
        brushes,
        ROAD_X2 + CHARLES_WALK_W,
        layout["ennis_x2"],
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d + ennis_curb_gap,
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK,
        layout["sw_slab_len"],
        layout["sw_gap"],
        tt_params=layout["ennis_road_tt_params"],
        tex_ranges=[
            (
                bw_cx - ENNIS_WALL_PILLAR_HW + 4,
                ENNIS_PILLAR_X1,
                Textures.WHITE_STONE,
                layout["ennis_road_tt_params"],
            ),
            (ENNIS_PILLAR_X1, ENNIS_GATE_X2, Textures.MULCH),
            (ENNIS_GATE_X2, layout["ennis_x2"], Textures.GROUND),
        ],
    )
    curb_bulge_x1 = ENNIS_CEMENT_X2
    curb_bulge_len = ENNIS_CURB_BULGE_LEN
    curb_bulge_x2 = curb_bulge_x1 + curb_bulge_len
    brushes.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d,
            FLOOR_Z2,
            curb_bulge_x1,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d + ennis_curb_gap,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK_JOINT,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    brushes.append(
        box(
            curb_bulge_x2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d,
            FLOOR_Z2,
            layout["ennis_x2"],
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d + ennis_curb_gap,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK_JOINT,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    curb_bulge_half_len = curb_bulge_len / 2
    curb_bulge_depth = curb_bulge_half_len / 2
    curb_bulge_cx = (curb_bulge_x1 + curb_bulge_x2) / 2
    curb_bulge_segments = 24
    curb_bulge_far_y = (
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d + ennis_curb_gap
    )
    brushes.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
            FLOOR_Z2 + STREET_SURFACE_T,
            curb_bulge_x1,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    bulge_step = curb_bulge_len / curb_bulge_segments

    def _bulge_depth_at(bx):
        bdx = bx - curb_bulge_cx
        bulge_t = max(1 - (bdx / curb_bulge_half_len) ** 2, 0)
        return curb_bulge_depth * math.sqrt(bulge_t)

    for bulge_index in range(curb_bulge_segments):
        bx1 = curb_bulge_x1 + bulge_index * bulge_step
        bx2 = bx1 + bulge_step
        bd1 = _bulge_depth_at(bx1)
        bd2 = _bulge_depth_at(bx2)
        outer1_y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - bd1
        outer2_y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - bd2
        inner1_y = outer1_y + ennis_curb_cap_d
        inner2_y = outer2_y + ennis_curb_cap_d
        z1, z2 = FLOOR_Z2 + STREET_SURFACE_T, FLOOR_Z2 + CHARLES_WALK_H
        brushes.append(
            tri_prism(
                bx1,
                outer1_y,
                bx2,
                outer2_y,
                bx2,
                inner2_y,
                z1,
                z2,
                Textures.SIDEWALK,
            )
        )
        brushes.append(
            tri_prism(
                bx1,
                outer1_y,
                bx2,
                inner2_y,
                bx1,
                inner1_y,
                z1,
                z2,
                Textures.SIDEWALK,
            )
        )
        if bd1 > 0 or bd2 > 0:
            brushes.append(
                tri_prism(
                    bx1,
                    inner1_y,
                    bx2,
                    inner2_y,
                    bx2,
                    curb_bulge_far_y,
                    FLOOR_Z2,
                    z2,
                    Textures.GROUND,
                )
            )
            brushes.append(
                tri_prism(
                    bx1,
                    inner1_y,
                    bx2,
                    curb_bulge_far_y,
                    bx1,
                    curb_bulge_far_y,
                    FLOOR_Z2,
                    z2,
                    Textures.GROUND,
                )
            )
    brushes.append(
        box(
            curb_bulge_x2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
            FLOOR_Z2 + STREET_SURFACE_T,
            layout["ennis_x2"],
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + ennis_curb_cap_d,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=layout["ennis_road_tt_params"],
        )
    )


def _append_ennis_south_sidewalks_and_curbs(brushes, layout):
    """Add the south Ennis sidewalks, curb joints, and curb slabs."""
    ennis_curb_cap_d = 8
    ennis_curb_gap = 2
    west_curb_x1 = ROAD_X2 + CHARLES_WALK_W
    west_sw_d = CHARLES_WALK_W * 2 + 56
    west_y1 = ENNIS_SW_EDGE + CHARLES_WALK_W - west_sw_d
    west_y2 = ENNIS_SW_EDGE + CHARLES_WALK_W - ennis_curb_cap_d - ennis_curb_gap
    west_north_y1 = west_y2 - layout["sw_slab_len"]
    brushes.append(
        box(
            west_curb_x1,
            west_y1,
            FLOOR_Z2,
            west_curb_x1 + layout["sw_slab_len"],
            west_north_y1,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.WHITE_STONE,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    brushes.append(
        box(
            west_curb_x1,
            west_north_y1,
            FLOOR_Z2,
            west_curb_x1 + layout["sw_slab_len"],
            west_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    for curb_x1, curb_x2, sw_d, tile_x1, tex_from_x in (
        (
            west_curb_x1,
            KNOTT_DRIVEWAY_WS_X1,
            CHARLES_WALK_W * 2 + 56,
            west_curb_x1 + layout["sw_slab_len"] + layout["sw_gap"],
            (
                west_curb_x1 + layout["sw_slab_len"] + layout["sw_gap"],
                Textures.WHITE_STONE,
            ),
        ),
        (
            KNOTT_DRIVEWAY_ES_X2,
            layout["ennis_x2"],
            CHARLES_WALK_W,
            KNOTT_DRIVEWAY_ES_X2,
            None,
        ),
    ):
        _append_street_sidewalk_slabs_x(
            brushes,
            tile_x1,
            curb_x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W - sw_d,
            ENNIS_SW_EDGE + CHARLES_WALK_W - ennis_curb_cap_d - ennis_curb_gap,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            layout["sw_slab_len"],
            layout["sw_gap"],
            tt_params=layout["ennis_road_tt_params"],
            tex_from_x=tex_from_x,
        )
        brushes.append(
            box(
                curb_x1,
                ENNIS_SW_EDGE + CHARLES_WALK_W - ennis_curb_cap_d - ennis_curb_gap,
                FLOOR_Z2,
                curb_x2,
                ENNIS_SW_EDGE + CHARLES_WALK_W - ennis_curb_cap_d,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK_JOINT,
                tt_params=layout["ennis_road_tt_params"],
            )
        )
        brushes.append(
            box(
                curb_x1,
                ENNIS_SW_EDGE + CHARLES_WALK_W - ennis_curb_cap_d,
                FLOOR_Z2 + STREET_SURFACE_T,
                curb_x2,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK,
                tt_params=layout["ennis_road_tt_params"],
            )
        )


def _append_street_markings(entities, layout):
    """Add centerlines, lane stripes, and both crosswalks as func_detail."""
    dash_brushes = []
    centerline_gap_hw = 2
    for line_x1, line_x2 in (
        (layout["road_cx"] - STREET_DIV_HW, layout["road_cx"] - centerline_gap_hw),
        (layout["road_cx"] + centerline_gap_hw, layout["road_cx"] + STREET_DIV_HW),
    ):
        for line_y1, line_y2 in _street_detail_ranges_excluding(
            layout["charles_y1"],
            layout["charles_y2"],
            layout["charles_crossing_y1"],
            layout["charles_crossing_y2"],
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
    for gap_y1, gap_y2 in _street_detail_ranges_excluding(
        layout["charles_y1"],
        layout["charles_y2"],
        layout["charles_crossing_y1"],
        layout["charles_crossing_y2"],
    ):
        dash_brushes.append(
            box(
                layout["road_cx"] - centerline_gap_hw,
                gap_y1,
                FLOOR_Z2,
                layout["road_cx"] + centerline_gap_hw,
                gap_y2,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
            )
        )
    for lane_line_x in (layout["west_lane_line_x"], layout["east_lane_line_x"]):
        tex_offset_x = layout["west_lane_line_x"] - lane_line_x
        divider_tt_params = f"{tex_offset_x} 0 0 1 1"
        for seg_y1, seg_y2 in _street_detail_ranges_excluding(
            layout["charles_y1"],
            layout["charles_y2"],
            layout["charles_crossing_y1"],
            layout["charles_crossing_y2"],
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
    cx = ROAD_X1
    stripe_on = True
    while cx < ROAD_X2:
        next_cx = min(
            cx + (CROSSWALK_STRIPE_W if stripe_on else CROSSWALK_GAP_W), ROAD_X2
        )
        dash_brushes.append(
            box(
                cx,
                layout["charles_crossing_y1"],
                FLOOR_Z2,
                next_cx,
                layout["charles_crossing_y2"],
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.PARKING_STRIPE if stripe_on else Textures.ROAD,
            )
        )
        cx = next_cx
        stripe_on = not stripe_on
    ennis_line_hw = STREET_DIV_LINE_HW
    ennis_line_x1 = ENNIS_PILLAR_X1 + ENNIS_PILLAR_HW
    for gx1, gx2 in _street_detail_ranges_excluding(
        ROAD_X2,
        ennis_line_x1,
        layout["ennis_crossing_x1"],
        layout["ennis_crossing_x2"],
    ):
        dash_brushes.append(
            box(
                gx1,
                layout["ennis_center_y"] - STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                gx2,
                layout["ennis_center_y"] + STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
                tt_params=layout["ennis_road_tt_params"],
            )
        )
    dash_brushes.append(
        box(
            ennis_line_x1,
            layout["ennis_center_y"] - STREET_ENNIS_DIV_HW,
            FLOOR_Z2,
            layout["ennis_x2"],
            layout["ennis_center_y"] - ennis_line_hw,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    dash_brushes.append(
        box(
            ennis_line_x1,
            layout["ennis_center_y"] - ennis_line_hw,
            FLOOR_Z2,
            layout["ennis_x2"],
            layout["ennis_center_y"] + ennis_line_hw,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.CENTERLINE,
        )
    )
    dash_brushes.append(
        box(
            ennis_line_x1,
            layout["ennis_center_y"] + ennis_line_hw,
            FLOOR_Z2,
            layout["ennis_x2"],
            layout["ennis_center_y"] + STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    ey = ENNIS_Y - ENNIS_HW
    ennis_crossing_y2 = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N
    stripe_on = True
    while ey < ennis_crossing_y2:
        next_ey = min(
            ey + (CROSSWALK_STRIPE_W if stripe_on else CROSSWALK_GAP_W),
            ennis_crossing_y2,
        )
        dash_brushes.append(
            box(
                layout["ennis_crossing_x1"],
                ey,
                FLOOR_Z2,
                layout["ennis_crossing_x2"],
                next_ey,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.PARKING_STRIPE if stripe_on else Textures.ROAD,
                tt_params=layout["ennis_road_tt_params"]
                if not stripe_on
                else "0 0 0 1 1",
            )
        )
        ey = next_ey
        stripe_on = not stripe_on
    if dash_brushes:
        entities.append(brush_ent("func_detail", punch_manhole_detail(dash_brushes)))


def _append_intersection_corners(brushes):
    """Add the southeast and northeast Charles/Ennis corner geometry."""
    cx_se = ROAD_X2 + CHARLES_CRN_R
    cy_se = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
    brushes.append(
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
        brushes.append(
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
    brushes.append(
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
        brushes.append(
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


def _append_verge_fill_surfaces(brushes, layout):
    """Add the verge fill and curb apron surfaces south and east of Ennis."""
    west_verge_x1 = (
        ROAD_X1 - CHARLES_WALK_W - CHARLES_RAMP_W
        if WEST_CAMPUS_ENABLED_TERRAIN
        else WORLD_X1 + WALL_T
    )
    east_verge_x2 = WORLD_X2_EXT - WALL_T
    brushes.append(
        box(
            west_verge_x1,
            layout["charles_y1"],
            FLOOR_Z2,
            ROAD_X1 - CHARLES_WALK_W,
            layout["charles_y2"],
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    west_verge_y2 = ENNIS_SW_EDGE - CHARLES_WALK_W
    east_verge_segs = (
        [
            (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, west_verge_y2),
            (KNOTT_DRIVEWAY_CORRIDOR_X2, east_verge_x2, ENNIS_SW_EDGE),
        ]
        if KNOTT_ENABLED_TERRAIN
        else [
            (ROAD_X2 + CHARLES_WALK_W, KNOTT.x2, west_verge_y2),
            (KNOTT.x2, east_verge_x2, ENNIS_SW_EDGE),
        ]
    )
    for evx1, evx2, evy2 in east_verge_segs:
        brushes.append(
            box(
                evx1,
                layout["charles_y1"],
                FLOOR_Z2,
                evx2,
                evy2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
    if not NE_ENABLED_TERRAIN:
        brushes.append(
            box(
                ROAD_X2 + CHARLES_WALK_W,
                ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
                FLOOR_Z2,
                layout["ennis_x2"],
                layout["charles_y2"],
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )

    verge_cement_x1 = ROAD_X2 + CHARLES_WALK_W
    verge_cement_x2 = verge_cement_x1 + layout["sw_slab_len"]
    for vx1, vx2, vtex in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, Textures.GROUND),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, layout["ennis_x2"], Textures.MULCH),
    ]:
        vy1 = ENNIS_SW_EDGE + CHARLES_WALK_W
        vy2 = ENNIS_Y - ENNIS_HW - ENNIS_CURB_W
        if vtex == Textures.GROUND:
            brushes.append(
                box(
                    verge_cement_x1,
                    vy1,
                    FLOOR_Z1,
                    verge_cement_x2,
                    vy2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )
            brushes.append(
                box(
                    verge_cement_x2,
                    vy1,
                    FLOOR_Z1,
                    vx2,
                    vy2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    vtex,
                )
            )
        else:
            brushes.append(
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
        (KNOTT_DRIVEWAY_CORRIDOR_X2, layout["ennis_x2"]),
    ]:
        brushes.append(
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


def _append_knott_driveway_surfaces(brushes):
    """Add the Knott driveway road fills and curved curb returns when exposed."""
    if KNOTT_ENABLED_TERRAIN:
        return
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    brushes.append(
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
    r_outer = KNOTT_DRIVEWAY_CURB_CRN_R
    r_inner = KNOTT_DRIVEWAY_CURB_CRN_R - ENNIS_CURB_W
    seg_deg = 90.0 / KNOTT_DRIVEWAY_CURB_CRN_SEGS
    for corner_index in range(KNOTT_DRIVEWAY_CURB_CRN_SEGS):
        a0 = corner_index * seg_deg
        a1 = (corner_index + 1) * seg_deg
        t0, t1 = math.radians(a0), math.radians(a1)
        brushes.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_X1,
                KNOTT_DRIVEWAY_EXT_Y2,
                KNOTT_DRIVEWAY_JCX_X1 + r_inner * math.cos(t0),
                KNOTT_DRIVEWAY_EXT_Y2 + r_inner * math.sin(t0),
                KNOTT_DRIVEWAY_JCX_X1 + r_inner * math.cos(t1),
                KNOTT_DRIVEWAY_EXT_Y2 + r_inner * math.sin(t1),
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.GROUND,
            )
        )
        brushes.append(
            curb_seg(
                KNOTT_DRIVEWAY_JCX_X1,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                r_inner,
                r_outer,
                a0,
                a1,
                Textures.CEMENT,
            )
        )
    brushes.append(
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
        ea0 = 90 + corner_index * seg_deg
        ea1 = 90 + (corner_index + 1) * seg_deg
        t0, t1 = math.radians(ea0), math.radians(ea1)
        brushes.append(
            tri_prism(
                KNOTT_DRIVEWAY_JCX_E,
                KNOTT_DRIVEWAY_EXT_Y2,
                KNOTT_DRIVEWAY_JCX_E + r_inner * math.cos(t0),
                KNOTT_DRIVEWAY_EXT_Y2 + r_inner * math.sin(t0),
                KNOTT_DRIVEWAY_JCX_E + r_inner * math.cos(t1),
                KNOTT_DRIVEWAY_EXT_Y2 + r_inner * math.sin(t1),
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.MULCH,
            )
        )
        brushes.append(
            curb_seg(
                KNOTT_DRIVEWAY_JCX_E,
                KNOTT_DRIVEWAY_EXT_Y2,
                FLOOR_Z2,
                FLOOR_Z2 + CHARLES_WALK_H,
                r_inner,
                r_outer,
                ea0,
                ea1,
                Textures.CEMENT,
            )
        )


def _append_ennis_entrance_detail_features(brushes, entities):
    """Append the Ennis entrance walls, gates, and flame fixtures."""
    ennis_brushes, ennis_entities = _build_ennis_entrance_features()
    brushes.extend(ennis_brushes)
    entities.extend(ennis_entities)


def _append_lamp_details(detail_brushes, entities):
    """Add Charles Street lamp-post detail brushes and flame entities."""
    for lamp_x in CHARLES_LAMP_POST_XS:
        for lamp_y in CHARLES_LAMP_POST_YS:
            pole_top_z = FLOOR_Z2 + CHARLES_LAMP_POST_H
            detail_brushes.append(
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
            detail_brushes.append(
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
            detail_brushes.append(
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
            entities.extend(torch_flame(lamp_x, lamp_y, flame_z))


def _build_street_details(BRUSHES, ENTITIES):
    """Build the detailed roadway, sidewalks, markings, and street fixtures."""
    detail_brushes = []
    layout = _make_street_detail_layout()

    _append_charles_road_surfaces(detail_brushes, layout)
    _append_charles_sidewalks_and_curbs(detail_brushes, layout)
    _append_ennis_road_surfaces(detail_brushes, layout)
    _append_ennis_north_sidewalks_and_curb_bulge(detail_brushes, layout)
    _append_ennis_south_sidewalks_and_curbs(detail_brushes, layout)
    _append_street_markings(ENTITIES, layout)
    _append_intersection_corners(detail_brushes)
    _append_verge_fill_surfaces(detail_brushes, layout)
    _append_knott_driveway_surfaces(detail_brushes)
    _append_ennis_entrance_detail_features(detail_brushes, ENTITIES)
    _append_lamp_details(detail_brushes, ENTITIES)

    if detail_brushes:
        detail_brushes = punch_manhole_detail(detail_brushes)
        ENTITIES.append(brush_ent("func_detail", detail_brushes))

    # NOTE: the global world-seal brushes used to live here, but that made
    # leak-prevention geometry conditional on STREETS_ENABLED_DETAILS. They
    # now live in shell.py::_build_world_seal() and are always built by
    # streets/__init__.py::build() regardless of this flag.

    return BRUSHES, ENTITIES
