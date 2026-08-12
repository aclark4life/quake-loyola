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
    ENNIS_X1,
    ENNIS_Y,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_WS_X1,
    MANHOLE_R,
    MANHOLE_X,
    MANHOLE_Y,
    WALL_T,
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
from ..constants.streets import (
    CHARLES_CRN_SEGS,
    CHARLES_CROSSWALK_LEN,
    CHARLES_CROSSWALK_STRIPE_W,
    CHARLES_RAMP_W,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    CROSSWALK_GAP_W,
    CROSSWALK_LEN,
    CROSSWALK_STRIPE_W,
    ENNIS_CROSSWALK_E_OFFSET,
    ROAD_X1,
    ROAD_X2,
    STREET_CHARLES_CURB_W,
    STREET_CURB_JOINT_OFFSET,
    STREET_CURB_SLAB_LEN,
    STREET_DIV_GAP_HW,
    STREET_DIV_HW,
    STREET_DIV_LINE_HW,
    STREET_ENNIS_DIV_HW,
    STREET_LANE_DASH_GAP,
    STREET_LANE_DASH_LEN,
    STREET_LANE_DASH_MIN,
    STREET_SURFACE_T,
    STREET_SW_GAP,
    STREET_SW_SLAB_LEN,
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
    polygon_prism,
    ramp_slab_y,
    sidewalk_panel_spans,
    torch_flame,
    tri_prism,
)
from .ennis import _build_ennis_entrance_features

# Depth of the Charles curb cap in from the road edge, and the width of the
# joint scored between that cap and the sidewalk panels behind it. Shared by
# the straight runs and the rounded intersection corners so the joint lands
# at the same offset all the way around.
CHARLES_CURB_CAP_D = 8
CHARLES_CURB_GAP = 2


def punch_manhole_detail(brushes, seen=None):
    """Cut the manhole opening through overlapping thin detail slabs.

    Brushes fully inside the hole are dropped; overlapping box slabs are
    rebuilt with box_with_round_hole(). Two independently-generated road
    slabs (e.g. Charles St. and Ennis Rd.) can physically overlap in this
    thin surface layer near the intersection, so each may be individually
    diced against the same manhole circle — de-duplicate the resulting
    brushes so identical wedges aren't emitted twice.

    The same overlap happens *between* calls: the lane markings and the road
    surfaces are punched separately into two func_detail entities, and both
    dice the same circle. Pass a shared ``seen`` set across those calls so a
    wedge already emitted by one is skipped by the other instead of being
    stacked coincident with it.
    """
    out = []
    seen = set() if seen is None else seen

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


def _street_dash_runs(v1, v2, *, anchor, dash_len, gap_len, min_dash):
    """Tile ``[v1, v2)`` with a broken line's paint and gap runs.

    Returns ``(start, end, is_dash)`` covering the whole span with no holes —
    the caller must paint the gaps too, because the road surface is carved away
    along the stripe's full length and anything left unpainted would be a slot
    straight through to the void.

    The dash pattern is stepped off ``anchor`` rather than off ``v1``, so every
    run of the same line stays on one lattice however the street is chopped up
    by intersections, and parallel lines sharing an anchor stay abreast. A dash
    the span's end cuts shorter than ``min_dash`` is dropped rather than left
    as a stub.
    """

    period = dash_len + gap_len
    runs = []
    i = math.floor((v1 - anchor) / period)
    while True:
        dash_start = anchor + i * period
        dash_end = dash_start + dash_len
        i += 1
        if dash_start >= v2:
            break
        clipped1, clipped2 = max(dash_start, v1), min(dash_end, v2)
        if clipped2 > clipped1 and clipped2 - clipped1 >= min_dash:
            runs.append((clipped1, clipped2, True))
    filled = []
    cursor = v1
    for start, end, _ in runs:
        if start > cursor:
            filled.append((cursor, start, False))
        filled.append((start, end, True))
        cursor = end
    if cursor < v2:
        filled.append((cursor, v2, False))
    return filled


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
    # North edge of the east walk, and the anchor the crossing hangs off.
    charles_walk_edge_y = ENNIS_Y - ENNIS_HW - CHARLES_CRN_R
    charles_curb_cut_len = 2 * (STREET_SW_SLAB_LEN + STREET_SW_GAP)
    # The crossing steps south as it runs west to east: its west stripe sits in
    # the lowered sidewalk entrance on that side, its east stripe against the
    # east walk's north edge. The west end is capped at the Ennis Rd south curb
    # because Ennis paves its carriageway clear across Charles St at the same
    # z: a stripe reaching past ENNIS_Y - ENNIS_HW lands coplanar with that
    # surface, z-fighting a crosswalk stripe into the middle of the junction.
    charles_crossing_north_w = min(
        charles_walk_edge_y - CROSSWALK_LEN / 2 + charles_curb_cut_len,
        ENNIS_Y - ENNIS_HW,
    )
    # The lowered entrance is sized off the sidewalk's slab pitch and hangs off
    # the band's west end, so the two stay aligned wherever the cap lands.
    charles_curb_cut_y2 = charles_crossing_north_w
    charles_crossing_mid = charles_curb_cut_y2 - charles_curb_cut_len
    # y1/y2 are the band's full extent, which is what the road surface and the
    # lane markings cut themselves around.
    charles_crossing_y2 = charles_crossing_north_w
    charles_crossing_y1 = charles_walk_edge_y - CHARLES_CROSSWALK_LEN
    road_cx = (ROAD_X1 + ROAD_X2) / 2
    return {
        "charles_y1": charles_y1,
        "charles_y2": charles_y2,
        "charles_crossing_y1": charles_crossing_y1,
        "charles_crossing_y2": charles_crossing_y2,
        "charles_crossing_mid": charles_crossing_mid,
        "charles_crossing_north_w": charles_crossing_north_w,
        "charles_crossing_north_e": charles_walk_edge_y,
        "charles_curb_cut_y2": charles_curb_cut_y2,
        "charles_curb_ramp_y2": charles_curb_cut_y2 + STREET_SW_SLAB_LEN,
        "ennis_x1": ENNIS_X1,
        "ennis_x2": WORLD_X2_EXT - WALL_T,
        "ennis_crossing_x1": ROAD_X2 + ENNIS_CROSSWALK_E_OFFSET,
        "ennis_crossing_x2": ROAD_X2 + ENNIS_CROSSWALK_E_OFFSET + CHARLES_WALK_W,
        "road_cx": road_cx,
        "west_lane_line_x": (ROAD_X1 + road_cx - STREET_DIV_HW) / 2,
        "east_lane_line_x": (road_cx + STREET_DIV_HW + ROAD_X2) / 2,
        "sw_slab_len": STREET_SW_SLAB_LEN,
        "sw_gap": STREET_SW_GAP,
        "ennis_road_tt_params": "0 0 90 1 1",
        # The south Ennis walk in front of Knott Hall lays its paving on the
        # diagonal, like the bridge deck's main band, so the stone's courses
        # run across the walk instead of squaring up with the curb. It is also
        # the one surface in the map scaled below 1: at 1 texel per unit the
        # 512px stone's basketweave bricks come out 51 by 25 inches, so a
        # quarter scale brings them down to a believable 13 by 6 inches.
        "ennis_south_sw_tt_params": "0 0 45 0.25 0.25",
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


def _append_charles_curb_sections(brushes, layout, x1, x2, y1, y2, z_base, z_top):
    """Tile a Charles St curb run into poured sections.

    Curbs are poured in longer runs than the walk beside them, so they use
    STREET_CURB_SLAB_LEN with joints phase-shifted off the sidewalk grid by
    STREET_CURB_JOINT_OFFSET. Anchoring the phase to ``charles_y1`` keeps every
    curb piece on one grid — both sides of the street, and the runs either side
    of a crossing or of Ennis Rd — so each kerb line reads as a single pour.
    """
    step = STREET_CURB_SLAB_LEN + STREET_SW_GAP
    offset = (y1 - layout["charles_y1"] + STREET_CURB_JOINT_OFFSET) % step
    panels, joints = sidewalk_panel_spans(
        y1, y2, STREET_CURB_SLAB_LEN, STREET_SW_GAP, offset
    )
    for span, tex in ((panels, Textures.SIDEWALK), (joints, Textures.SIDEWALK_JOINT)):
        for py1, py2 in span:
            brushes.append(box(x1, py1, z_base, x2, py2, z_top, tex))


def _append_charles_west_sidewalks(
    brushes,
    layout,
    *,
    curb_cap_d,
    curb_gap,
    curb_cut_y2,
    curb_ramp_y2,
):
    """Append the west-side Charles crossing ramp, sidewalk, and curb return."""

    _append_street_sidewalk_slabs_y(
        brushes,
        ROAD_X1 - CHARLES_WALK_W,
        ROAD_X1,
        layout["charles_crossing_mid"],
        curb_cut_y2,
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
            curb_cut_y2,
            curb_ramp_y2,
            FLOOR_Z2,
            FLOOR_Z2,
            FLOOR_Z2 + STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    _append_street_sidewalk_slabs_y(
        brushes,
        ROAD_X1 - CHARLES_WALK_W,
        ROAD_X1 - curb_cap_d - curb_gap,
        curb_ramp_y2 + layout["sw_gap"],
        layout["charles_y2"],
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK,
        layout["sw_slab_len"],
        layout["sw_gap"],
    )
    brushes.append(
        box(
            ROAD_X1 - curb_cap_d - curb_gap,
            curb_ramp_y2 + layout["sw_gap"],
            FLOOR_Z2,
            ROAD_X1 - curb_cap_d,
            layout["charles_y2"],
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK_JOINT,
        )
    )
    # The curb is poured in its own sections, off the sidewalk's joint grid.
    _append_charles_curb_sections(
        brushes,
        layout,
        ROAD_X1 - curb_cap_d,
        ROAD_X1,
        curb_ramp_y2 + layout["sw_gap"],
        layout["charles_y2"],
        FLOOR_Z2 + STREET_SURFACE_T,
        FLOOR_Z2 + CHARLES_WALK_H,
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
            curb_cut_y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    brushes.append(
        ramp_slab_y(
            rw_x1,
            rw_x2,
            curb_cut_y2,
            curb_ramp_y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H - STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
        )
    )
    _append_charles_curb_sections(
        brushes,
        layout,
        ROAD_X1 - STREET_CHARLES_CURB_W,
        ROAD_X1,
        layout["charles_y1"],
        layout["charles_crossing_mid"],
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
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


def _append_charles_corner_ramp_tiles(
    brushes, seg_y1, *, slab_len, gap, curb_cap_d, curb_gap
):
    """Build the two Charles-side tiles between the NE corner and the walk.

    The NE intersection corner is flat at street grade for its whole extent,
    so the first tile north of it stays flat at that same low grade; the step
    back up to full sidewalk height happens across the tile after it, which
    slopes uniformly south to north. Both tiles are banded like the rest of
    the run — curb cap, curb joint, then walk panels — so the kerb line and
    its joint carry on unbroken from the corner's arc to the straight run,
    and the tiles' own expansion joints stop at the curb joint instead of
    running out into the street. Returns the Y the regular panels resume at.
    """
    flat_y2 = seg_y1 + slab_len
    ramp_y2 = flat_y2 + slab_len
    panel_y1 = ramp_y2 + gap
    lo, hi = FLOOR_Z2 + STREET_SURFACE_T, FLOOR_Z2 + CHARLES_WALK_H

    def band(x1, x2, y1, y2, z_south, z_north, tex):
        """Add one band of a tile, flat or sloped along Y."""
        if z_south == z_north:
            brushes.append(box(x1, y1, FLOOR_Z1, x2, y2, z_south, tex))
        else:
            brushes.append(
                ramp_slab_y(x1, x2, y1, y2, FLOOR_Z1, FLOOR_Z1, z_south, z_north, tex)
            )

    curb_x2 = ROAD_X2 + curb_cap_d
    walk_x1 = curb_x2 + curb_gap
    # Curb cap and its joint run the tiles' whole length as a single pour —
    # a curb return at a ramp is poured in one piece — rising out of the
    # flush corner exactly as the walk beside it does.
    for bx1, bx2, tex in (
        (ROAD_X2, curb_x2, Textures.SIDEWALK),
        (curb_x2, walk_x1, Textures.SIDEWALK_JOINT),
    ):
        band(bx1, bx2, seg_y1, flat_y2, lo, lo, tex)
        band(bx1, bx2, flat_y2, ramp_y2, lo, hi, tex)
        band(bx1, bx2, ramp_y2, panel_y1, hi, hi, tex)

    # Walk panels, each with an expansion joint cut out of its north end so
    # the tile boundaries — which the northeast terrain grid ties to — stay
    # exactly where they are. The ramp reaches full sidewalk height at its
    # north edge, so its joint is a flat slab.
    walk_x2 = ROAD_X2 + CHARLES_WALK_W
    band(walk_x1, walk_x2, seg_y1, flat_y2 - gap, lo, lo, Textures.SIDEWALK)
    band(walk_x1, walk_x2, flat_y2 - gap, flat_y2, lo, lo, Textures.SIDEWALK_JOINT)
    band(walk_x1, walk_x2, flat_y2, ramp_y2, lo, hi, Textures.SIDEWALK)
    band(walk_x1, walk_x2, ramp_y2, panel_y1, hi, hi, Textures.SIDEWALK_JOINT)
    return panel_y1


def _append_charles_east_sidewalks(brushes, layout, *, curb_cap_d, curb_gap):
    """Append the east-side Charles sidewalk panels and curb caps."""

    for seg_y1, seg_y2, seg_overrides, ramp_from_corner in (
        (
            layout["charles_y1"],
            ENNIS_Y - ENNIS_HW - CHARLES_WALK_W,
            None,
            False,
        ),
        (
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + CHARLES_WALK_W,
            layout["charles_y2"],
            None,
            True,
        ),
    ):
        panel_y1 = seg_y1
        if ramp_from_corner:
            panel_y1 = _append_charles_corner_ramp_tiles(
                brushes,
                seg_y1,
                slab_len=layout["sw_slab_len"],
                gap=layout["sw_gap"],
                curb_cap_d=curb_cap_d,
                curb_gap=curb_gap,
            )
        _append_street_sidewalk_slabs_y(
            brushes,
            ROAD_X2 + curb_cap_d + curb_gap,
            ROAD_X2 + CHARLES_WALK_W,
            panel_y1,
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
                ROAD_X2 + curb_cap_d,
                panel_y1,
                FLOOR_Z2,
                ROAD_X2 + curb_cap_d + curb_gap,
                seg_y2,
                FLOOR_Z2 + CHARLES_WALK_H,
                Textures.SIDEWALK_JOINT,
            )
        )
        _append_charles_curb_sections(
            brushes,
            layout,
            ROAD_X2,
            ROAD_X2 + curb_cap_d,
            panel_y1,
            seg_y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            FLOOR_Z2 + CHARLES_WALK_H,
        )


def _append_charles_sidewalks_and_curbs(brushes, layout):
    """Add Charles Street sidewalks, curb cuts, and curb ramp slabs."""
    charles_curb_cap_d = CHARLES_CURB_CAP_D
    charles_curb_gap = CHARLES_CURB_GAP
    _append_charles_west_sidewalks(
        brushes,
        layout,
        curb_cap_d=charles_curb_cap_d,
        curb_gap=charles_curb_gap,
        curb_cut_y2=layout["charles_curb_cut_y2"],
        curb_ramp_y2=layout["charles_curb_ramp_y2"],
    )
    _append_charles_east_sidewalks(
        brushes,
        layout,
        curb_cap_d=charles_curb_cap_d,
        curb_gap=charles_curb_gap,
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
    for road_seg_x1, road_seg_x2 in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, layout["ennis_x2"]),
    ]:
        # The crossing band now reaches east of ROAD_X2 + CHARLES_WALK_W, so
        # this segment has to be carved around it too, not just the one west
        # of that boundary.
        for road_x1, road_x2 in _street_detail_ranges_excluding(
            road_seg_x1,
            road_seg_x2,
            layout["ennis_crossing_x1"],
            layout["ennis_crossing_x2"],
        ):
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


def _append_ennis_north_sidewalk_strip(
    brushes, layout, *, curb_cap_d, curb_gap, ramp_x2
):
    """Append the straight north-side Ennis sidewalk tiles."""

    ennis_wall_x1 = ROAD_X2 + CHARLES_WALK_W + ENNIS_WALL_X_OFFSET
    bw_cx = ennis_wall_x1 + ENNIS_WALL_T // 2
    _append_street_sidewalk_slabs_x(
        brushes,
        ramp_x2,
        layout["ennis_x2"],
        ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d + curb_gap,
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


def _append_ennis_corner_ramp_extension(brushes, *, ramp_x2, curb_cap_d, curb_gap):
    """Flatten the NE corner's low grade east across the sidewalk's first two
    tiles, then step up to full sidewalk height where the regular sidewalk
    panels resume.

    The rounded NE corner is now flush with the street across its whole
    extent, so this strip carries that same low grade straight across —
    no ramp. A hard vertical step/curb (rather than a ramp) makes up the
    difference at ``ramp_x2``, where the full-height sidewalk resumes.

    The strip is still banded curb cap / curb joint / apron at the same
    offsets off the road edge as the corner's arc to its west and the raised
    Ennis curb to its east, so the kerb line reads continuously across it
    even though it lies flush here.
    """
    ramp_x1 = ROAD_X2 + CHARLES_WALK_W
    ramp_y1 = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N
    ramp_y2 = ramp_y1 + CHARLES_WALK_W
    ramp_lo = FLOOR_Z2 + STREET_SURFACE_T
    curb_y2 = ramp_y1 + curb_cap_d
    joint_y2 = curb_y2 + curb_gap
    for by1, by2, tex in (
        (ramp_y1, curb_y2, Textures.SIDEWALK),
        (curb_y2, joint_y2, Textures.SIDEWALK_JOINT),
        (joint_y2, ramp_y2, Textures.SIDEWALK),
    ):
        brushes.append(
            box(
                ramp_x1,
                by1,
                FLOOR_Z2,
                ramp_x2,
                by2,
                ramp_lo,
                tex,
            )
        )
    # The regular full-height sidewalk panel resumes immediately east of
    # ramp_x2 (built separately) at full sidewalk height, so the shared
    # boundary at ramp_x2 is already a hard vertical step/curb — no extra
    # riser geometry is needed.


def _append_ennis_curb_bulge(brushes, layout, *, curb_cap_d, curb_gap, ramp_x2):
    """Append the curved north-side Ennis curb bulge and its fill wedges."""

    curb_bulge_x1 = ENNIS_CEMENT_X2
    curb_bulge_len = ENNIS_CURB_BULGE_LEN
    curb_bulge_x2 = curb_bulge_x1 + curb_bulge_len
    brushes.append(
        box(
            ramp_x2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d,
            FLOOR_Z2,
            curb_bulge_x1,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d + curb_gap,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK_JOINT,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    brushes.append(
        box(
            curb_bulge_x2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d,
            FLOOR_Z2,
            layout["ennis_x2"],
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d + curb_gap,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK_JOINT,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    curb_bulge_half_len = curb_bulge_len / 2
    curb_bulge_depth = curb_bulge_half_len / 2
    curb_bulge_cx = (curb_bulge_x1 + curb_bulge_x2) / 2
    curb_bulge_segments = 24
    curb_bulge_far_y = ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d + curb_gap
    brushes.append(
        box(
            ramp_x2,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N,
            FLOOR_Z2 + STREET_SURFACE_T,
            curb_bulge_x1,
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d,
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
        inner1_y = outer1_y + curb_cap_d
        inner2_y = outer2_y + curb_cap_d
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
            ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N + curb_cap_d,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK,
            tt_params=layout["ennis_road_tt_params"],
        )
    )


def _append_ennis_north_sidewalks_and_curb_bulge(brushes, layout):
    """Add the north Ennis sidewalks, curb caps, and the curb bulge."""
    ennis_curb_cap_d = 8
    ennis_curb_gap = 2
    ramp_x2 = ROAD_X2 + CHARLES_WALK_W + 2 * layout["sw_slab_len"]
    _append_ennis_corner_ramp_extension(
        brushes,
        ramp_x2=ramp_x2,
        curb_cap_d=ennis_curb_cap_d,
        curb_gap=ennis_curb_gap,
    )
    _append_ennis_north_sidewalk_strip(
        brushes,
        layout,
        curb_cap_d=ennis_curb_cap_d,
        curb_gap=ennis_curb_gap,
        ramp_x2=ramp_x2,
    )
    _append_ennis_curb_bulge(
        brushes,
        layout,
        curb_cap_d=ennis_curb_cap_d,
        curb_gap=ennis_curb_gap,
        ramp_x2=ramp_x2,
    )


def _append_ennis_south_west_entry_slabs(brushes, layout, *, curb_cap_d, curb_gap):
    """Append the south-side westmost Ennis sidewalk slabs by Charles."""

    west_curb_x1 = ROAD_X2 + CHARLES_WALK_W
    west_sw_d = CHARLES_WALK_W * 2 + 56
    west_y1 = ENNIS_SW_EDGE + CHARLES_WALK_W - west_sw_d
    west_y2 = ENNIS_SW_EDGE + CHARLES_WALK_W - curb_cap_d - curb_gap
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


ENNIS_CURB_TEX_PARAMS = "0 0 0 0.25 0.25"


def _append_ennis_south_sidewalk_segment(
    brushes,
    layout,
    *,
    curb_x1,
    curb_x2,
    sidewalk_depth,
    tile_x1,
    tex_from_x,
    curb_cap_d,
    curb_gap,
):
    """Append one south-side Ennis sidewalk run with curb joint and cap."""

    _append_street_sidewalk_slabs_x(
        brushes,
        tile_x1,
        curb_x2,
        ENNIS_SW_EDGE + CHARLES_WALK_W - sidewalk_depth,
        ENNIS_SW_EDGE + CHARLES_WALK_W - curb_cap_d - curb_gap,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        Textures.SIDEWALK,
        layout["sw_slab_len"],
        layout["sw_gap"],
        tt_params=layout["ennis_south_sw_tt_params"],
        tex_from_x=tex_from_x,
    )
    brushes.append(
        box(
            curb_x1,
            ENNIS_SW_EDGE + CHARLES_WALK_W - curb_cap_d - curb_gap,
            FLOOR_Z2,
            curb_x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W - curb_cap_d,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.SIDEWALK_JOINT,
            tt_params=layout["ennis_road_tt_params"],
        )
    )
    # The curb reads as a row of stone blocks, so it skips the 90-degree
    # rotation the rest of the Ennis surfaces use and keeps the texture's own
    # block columns running along the curb. At the walk's quarter scale those
    # columns land 8 units apart, matching the curb's depth, so its cap and its
    # road-facing side both read as one row of square blocks. Every face takes
    # the scale, since the side is as visible from the road as the cap is from
    # the walk. The westmost tile stays plain sidewalk so the stone starts
    # where the tiled walk does.
    for slab_x1, slab_x2, slab_tex, slab_params, scale_sides in (
        (
            curb_x1,
            min(tile_x1, curb_x2),
            Textures.SIDEWALK,
            layout["ennis_road_tt_params"],
            False,
        ),
        (min(tile_x1, curb_x2), curb_x2, Textures.CURB, ENNIS_CURB_TEX_PARAMS, True),
    ):
        if slab_x1 >= slab_x2:
            continue
        face_params = (
            {
                side: slab_params
                for side in ("tw_params", "te_params", "ts_params", "tn_params")
            }
            if scale_sides
            else {}
        )
        brushes.append(
            box(
                slab_x1,
                ENNIS_SW_EDGE + CHARLES_WALK_W - curb_cap_d,
                FLOOR_Z2 + STREET_SURFACE_T,
                slab_x2,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z2 + CHARLES_WALK_H,
                slab_tex,
                tt_params=slab_params,
                **face_params,
            )
        )


def _append_ennis_south_sidewalks_and_curbs(brushes, layout):
    """Add the south Ennis sidewalks, curb joints, and curb slabs."""
    ennis_curb_cap_d = 8
    ennis_curb_gap = 2
    west_curb_x1 = ROAD_X2 + CHARLES_WALK_W
    _append_ennis_south_west_entry_slabs(
        brushes, layout, curb_cap_d=ennis_curb_cap_d, curb_gap=ennis_curb_gap
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
        _append_ennis_south_sidewalk_segment(
            brushes,
            layout,
            curb_x1=curb_x1,
            curb_x2=curb_x2,
            sidewalk_depth=sw_d,
            tile_x1=tile_x1,
            tex_from_x=tex_from_x,
            curb_cap_d=ennis_curb_cap_d,
            curb_gap=ennis_curb_gap,
        )


def _append_charles_marking_brushes(dash_brushes, layout):
    """Append Charles Street centerlines, lane stripes, and crosswalk."""

    for line_x1, line_x2 in (
        (layout["road_cx"] - STREET_DIV_HW, layout["road_cx"] - STREET_DIV_GAP_HW),
        (layout["road_cx"] + STREET_DIV_GAP_HW, layout["road_cx"] + STREET_DIV_HW),
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
                layout["road_cx"] - STREET_DIV_GAP_HW,
                gap_y1,
                FLOOR_Z2,
                layout["road_cx"] + STREET_DIV_GAP_HW,
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
            for run_y1, run_y2, is_dash in _street_dash_runs(
                seg_y1,
                seg_y2,
                anchor=layout["charles_y1"],
                dash_len=STREET_LANE_DASH_LEN,
                gap_len=STREET_LANE_DASH_GAP,
                min_dash=STREET_LANE_DASH_MIN,
            ):
                dash_brushes.append(
                    box(
                        lane_line_x - STREET_DIV_LINE_HW,
                        run_y1,
                        FLOOR_Z2,
                        lane_line_x + STREET_DIV_LINE_HW,
                        run_y2,
                        FLOOR_Z2 + STREET_SURFACE_T,
                        Textures.PARKING_STRIPE if is_dash else Textures.ROAD,
                        tt_params=divider_tt_params if is_dash else "0 0 0 1 1",
                    )
                )
    # The crossing steps south stripe by stripe as it runs west to east, so the
    # west end lands in the lowered sidewalk entrance and the east end against
    # the east walk. Every column still paints the full band depth, filling
    # whatever the stripe doesn't cover with road, because the road surface
    # itself is cut away around the band.
    band_y1, band_y2 = layout["charles_crossing_y1"], layout["charles_crossing_y2"]
    columns = []
    cx = ROAD_X1
    stripe_on = True
    while cx < ROAD_X2:
        next_cx = min(
            cx + (CHARLES_CROSSWALK_STRIPE_W if stripe_on else CROSSWALK_GAP_W),
            ROAD_X2,
        )
        columns.append((cx, next_cx, stripe_on))
        cx = next_cx
        stripe_on = not stripe_on
    stripe_count = sum(1 for _, _, on in columns if on)
    north_w, north_e = (
        layout["charles_crossing_north_w"],
        layout["charles_crossing_north_e"],
    )
    step = (north_w - north_e) / (stripe_count - 1) if stripe_count > 1 else 0
    stripe_i = 0
    for col_x1, col_x2, is_stripe in columns:
        if not is_stripe:
            dash_brushes.append(
                box(
                    col_x1,
                    band_y1,
                    FLOOR_Z2,
                    col_x2,
                    band_y2,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    Textures.ROAD,
                )
            )
            continue
        stripe_y2 = north_w - step * stripe_i
        stripe_y1 = stripe_y2 - CHARLES_CROSSWALK_LEN
        stripe_i += 1
        for seg_y1, seg_y2, seg_tex in (
            (band_y1, stripe_y1, Textures.ROAD),
            (stripe_y1, stripe_y2, Textures.PARKING_STRIPE),
            (stripe_y2, band_y2, Textures.ROAD),
        ):
            if seg_y2 <= seg_y1:
                continue
            dash_brushes.append(
                box(
                    col_x1,
                    seg_y1,
                    FLOOR_Z2,
                    col_x2,
                    seg_y2,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    seg_tex,
                )
            )


def _append_ennis_marking_brushes(dash_brushes, layout):
    """Append Ennis Road divider and crosswalk markings."""

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


def _append_street_markings(entities, layout, manhole_seen=None):
    """Add centerlines, lane stripes, and both crosswalks as func_detail."""
    dash_brushes = []
    _append_charles_marking_brushes(dash_brushes, layout)
    _append_ennis_marking_brushes(dash_brushes, layout)
    if dash_brushes:
        entities.append(
            brush_ent("func_detail", punch_manhole_detail(dash_brushes, manhole_seen))
        )


def _append_corner_arc_bands(
    brushes, cx, cy, angle_base, z1, z2, *, curb_cap_d, curb_gap
):
    """Tile a rounded intersection corner into radial bands.

    The corner is swept as an inner sidewalk wedge, the curb joint following
    the arc, and the curb cap itself, so the longitudinal joint of the
    straight runs (``curb_cap_d`` in from the road edge, ``curb_gap`` wide)
    carries on around the corner at the same offset. All three bands share
    the straight chords of the segment, so they stay watertight.
    """
    joint_r2 = CHARLES_CRN_R - curb_cap_d
    joint_r1 = joint_r2 - curb_gap

    def arc_pt(radius, angle_deg):
        angle = math.radians(angle_deg)
        return (cx + radius * math.cos(angle), cy + radius * math.sin(angle))

    for corner_index in range(CHARLES_CRN_SEGS):
        angle_start = angle_base + corner_index * 90 / CHARLES_CRN_SEGS
        angle_end = angle_base + (corner_index + 1) * 90 / CHARLES_CRN_SEGS
        inner_0, inner_1 = arc_pt(joint_r1, angle_start), arc_pt(joint_r1, angle_end)
        brushes.append(tri_prism(cx, cy, *inner_0, *inner_1, z1, z2, Textures.SIDEWALK))
        for r1, r2, tex in (
            (joint_r1, joint_r2, Textures.SIDEWALK_JOINT),
            (joint_r2, CHARLES_CRN_R, Textures.SIDEWALK),
        ):
            brushes.append(
                polygon_prism(
                    [
                        arc_pt(r1, angle_start),
                        arc_pt(r2, angle_start),
                        arc_pt(r2, angle_end),
                        arc_pt(r1, angle_end),
                    ],
                    z1,
                    z2,
                    tex,
                )
            )


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
    # This corner keeps full sidewalk height; only the kerb line is banded,
    # continuing the joint of the straight runs around the arc.
    _append_corner_arc_bands(
        brushes,
        cx_se,
        cy_se,
        90,
        FLOOR_Z2,
        FLOOR_Z2 + CHARLES_WALK_H,
        curb_cap_d=CHARLES_CURB_CAP_D,
        curb_gap=CHARLES_CURB_GAP,
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
    # Like the lowered sidewalk at the west end of the Charles crosswalk, this
    # corner drops to street grade so pedestrians stepping off the Ennis
    # crossing don't meet a curb. The whole rounded corner (apex and arc
    # alike) sits flush with the road; the step back up to full sidewalk
    # height happens on the adjoining tiles instead (a ramp on the Charles
    # side, a hard step/curb on the Ennis side). The curb joint is still
    # scored around the arc, continuing the one on the straight runs.
    _append_corner_arc_bands(
        brushes,
        cx_ne,
        cy_ne,
        180,
        FLOOR_Z2,
        FLOOR_Z2 + STREET_SURFACE_T,
        curb_cap_d=CHARLES_CURB_CAP_D,
        curb_gap=CHARLES_CURB_GAP,
    )


def _append_verge_fill_surfaces(brushes, layout):
    """Add the verge fill and curb apron surfaces south and east of Ennis."""
    west_verge_x1 = ROAD_X1 - CHARLES_WALK_W - CHARLES_RAMP_W
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
    east_verge_segs = [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, west_verge_y2),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, east_verge_x2, ENNIS_SW_EDGE),
    ]
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
    verge_cement_x1 = ROAD_X2 + CHARLES_WALK_W
    verge_cement_x2 = verge_cement_x1 + layout["sw_slab_len"]
    for vx1, vx2, vtex in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, Textures.GROUND),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, layout["ennis_x2"], Textures.MULCH),
    ]:
        vy1 = ENNIS_SW_EDGE + CHARLES_WALK_W
        vy2 = ENNIS_Y - ENNIS_HW - ENNIS_CURB_W
        if vtex == Textures.GROUND:
            # The cement pad east of the SE corner is the one piece of this
            # verge that meets the Ennis curb concrete-to-concrete, so it
            # carries the curb joint on its north edge, continuing the one
            # scored around the corner's arc. Further east the verge is
            # grass, which just abuts the curb with no joint.
            verge_joint_y1 = vy2 - CHARLES_CURB_GAP
            brushes.append(
                box(
                    verge_cement_x1,
                    vy1,
                    FLOOR_Z1,
                    verge_cement_x2,
                    verge_joint_y1,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.CEMENT,
                )
            )
            brushes.append(
                box(
                    verge_cement_x1,
                    verge_joint_y1,
                    FLOOR_Z1,
                    verge_cement_x2,
                    vy2,
                    FLOOR_Z2 + CHARLES_WALK_H,
                    Textures.SIDEWALK_JOINT,
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
    # Shared across both punch_manhole_detail() calls below so the markings and
    # the road surfaces don't each emit their own copy of the same wedges.
    manhole_seen = set()

    _append_charles_road_surfaces(detail_brushes, layout)
    _append_charles_sidewalks_and_curbs(detail_brushes, layout)
    _append_ennis_road_surfaces(detail_brushes, layout)
    _append_ennis_north_sidewalks_and_curb_bulge(detail_brushes, layout)
    _append_ennis_south_sidewalks_and_curbs(detail_brushes, layout)
    _append_street_markings(ENTITIES, layout, manhole_seen)
    _append_intersection_corners(detail_brushes)
    _append_verge_fill_surfaces(detail_brushes, layout)
    _append_ennis_entrance_detail_features(detail_brushes, ENTITIES)
    _append_lamp_details(detail_brushes, ENTITIES)

    if detail_brushes:
        detail_brushes = punch_manhole_detail(detail_brushes, manhole_seen)
        ENTITIES.append(brush_ent("func_detail", detail_brushes))

    # NOTE: the global world-seal brushes live in shell.py::_build_world_seal()
    # and are appended by streets/__init__.py::build().

    return BRUSHES, ENTITIES
