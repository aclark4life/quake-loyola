import math

from .constants import (
    BRIDGE,
    BRIDGE_ARCH_X,
    BRIDGE_DZ2,
    BRIDGE_PIL_HW,
    BRIDGE_PIL_OVERHANG,
    CHARLES_CRN_R,
    CHARLES_CRN_SEGS,
    CHARLES_RAMP_W,
    CHARLES_SWALK_START,
    CHARLES_WALK_H,
    CHARLES_WALK_W,
    DORM,
    DORM_EMB_X2,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_PIER_X,
    DORM_SOUTH1_Y1,
    DORM_SOUTH1_Y2,
    DORM_SOUTH2_Y1,
    DORM_SOUTH2_Y2,
    ENNIS_CURB_W,
    ENNIS_HW,
    ENNIS_NORTH_OFFSET,
    ENNIS_SW_EDGE,
    ENNIS_Y,
    FLOOR_Z1,
    FLOOR_Z2,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    KNOTT_DRIVEWAY_ES_X2,
    ROAD_DASH_LEN,
    ROAD_GAP_LEN,
    ROAD_X1,
    ROAD_X2,
    SDORM_LIFT,
    SDORM_SLOPE_Y_N,
    SDORM_SLOPE_Y_S,
    SDORM_STAIR_X2,
    SDORM_STAIR_Y1,
    SDORM_STAIR_Y2,
    SDORM_TERRACE_X2,
    SDORM_TOE_X,
    SDORM_WALL_X,
    STREET_CHARLES_CURB_W,
    STREET_DIV_HW,
    STREET_ENNIS_DIV_HW,
    STREET_SURFACE_T,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
    WORLD_Z2,
    Textures,
)
from .geometry import (
    box,
    brush_ent,
    corner_ramp,
    ramp_slab,
    ramp_slab_y,
    tri_prism,
)
from .west_campus import build_ennis_entrance_features


def build():
    BRUSHES = []
    ENTITIES = []
    DETAIL_BRUSHES = []
    # ════════════════════════════════════════════════════════════════════════════════
    # RECTANGULAR WORLD SHELL — floor, 4 outer walls, sky ceiling
    # ════════════════════════════════════════════════════════════════════════════════
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            FLOOR_Z2,
            Textures.GROUND,
        )
    )  # floor
    # W wall — split by Z so only the tunnel-height portion shows ground on its inner face.
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            BRIDGE_DZ2,
            Textures.SKY,
            te=Textures.GROUND,  # inner east face at tunnel height → ground
        )
    )  # W wall lower (tunnel height)
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            BRIDGE_DZ2,
            WORLD_X1 + WALL_T,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )  # W wall upper (above tunnel)
    BRUSHES.append(
        box(
            WORLD_X2_EXT - WALL_T,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )  # E wall
    # N wall — split at DORM.x1 (tunnel east boundary).  The inner (south) face is
    # split ALONG the tunnel ceiling-underside line, which slopes from
    # BRIDGE_DZ2-WALL_T at the world wall down to SDORM_LIFT at DORM.x1: ground on
    # the visible tunnel end-wall below that line, sky above it (the band above is
    # buried in the hillside slab / open sky), so no ground triangle pokes above
    # the hill.  This line is always below the hill roofline, so it stays hidden.
    BRUSHES.append(
        ramp_slab(
            WORLD_X1,
            DORM.x1,
            WORLD_Y2 - WALL_T,
            WORLD_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            Textures.SKY,
            ts=Textures.GROUND,  # inner south face = tunnel end-wall → ground
        )
    )  # N wall tunnel portal (ground up to the ceiling-underside line)
    BRUSHES.append(
        ramp_slab(
            WORLD_X1,
            DORM.x1,
            WORLD_Y2 - WALL_T,
            WORLD_Y2,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            WORLD_Z2,
            WORLD_Z2,
            Textures.SKY,
        )
    )  # N wall above the tunnel end-wall (sky, up to the world ceiling)
    BRUSHES.append(
        box(
            DORM.x1,
            WORLD_Y2 - WALL_T,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )  # N wall east of tunnel
    # S wall — mirror of N wall split (ground below the ceiling-underside line, sky above).
    BRUSHES.append(
        ramp_slab(
            WORLD_X1,
            DORM.x1,
            WORLD_Y1,
            WORLD_Y1 + WALL_T,
            FLOOR_Z1,
            FLOOR_Z1,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            Textures.SKY,
            ts=Textures.GROUND,  # inner north face = tunnel end-wall → ground
        )
    )  # S wall tunnel portal (ground up to the ceiling-underside line)
    BRUSHES.append(
        ramp_slab(
            WORLD_X1,
            DORM.x1,
            WORLD_Y1,
            WORLD_Y1 + WALL_T,
            BRIDGE_DZ2 - WALL_T,
            SDORM_LIFT,
            WORLD_Z2,
            WORLD_Z2,
            Textures.SKY,
        )
    )  # S wall above the tunnel end-wall (sky, up to the world ceiling)
    BRUSHES.append(
        box(
            DORM.x1,
            WORLD_Y1,
            FLOOR_Z1,
            WORLD_X2_EXT,
            WORLD_Y1 + WALL_T,
            WORLD_Z2,
            Textures.SKY,
        )
    )  # S wall east of tunnel
    BRUSHES.append(
        box(
            WORLD_X1,
            WORLD_Y1,
            WORLD_Z2 - WALL_T,
            WORLD_X2_EXT,
            WORLD_Y2,
            WORLD_Z2,
            Textures.SKY,
        )
    )  # sky
    # ── Non-sealing street furniture, markings, and decorative ground geometry ──
    # These are moved to DETAIL_BRUSHES to speed up vis and reduce portal fragmentation.
    _world_brushes = BRUSHES
    BRUSHES = DETAIL_BRUSHES

    # ════════════════════════════════════════════════════════════════════════════════
    # CHARLES STREET — road surface, sidewalks, centre stripe
    # Road runs N-S (full Y); road channel E-W = ROAD_X1..ROAD_X2
    # ════════════════════════════════════════════════════════════════════════════════
    CHARLES_Y1 = WORLD_Y1 + WALL_T
    CHARLES_Y2 = WORLD_Y2 - WALL_T

    # ── Ennis Road (E-W, parallel to bridge, north side) ──
    # Runs from Charles Street west edge (ROAD_X1) east to the world wall, dead-ending there.
    # Half as wide as Charles Street (512/2=256 total → HW=128), north of bridge.
    ENNIS_X1 = ROAD_X1  # start at west edge of Charles St to form T-junction
    ENNIS_X2 = WORLD_X2_EXT - WALL_T  # dead-end at east world wall
    # Back road corridor X extents — defined here for road/curb brush splits below

    # Road surface — split either side of centre divider slot (div_hw wide)
    BRUSHES.append(
        box(
            ROAD_X1,
            CHARLES_Y1,
            FLOOR_Z2,
            -STREET_DIV_HW,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    BRUSHES.append(
        box(
            STREET_DIV_HW,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X2,
            CHARLES_Y2,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # West sidewalk — north of bridge
    BRUSHES.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_SWALK_START,
            FLOOR_Z2,
            ROAD_X1,
            CHARLES_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # West curb — south section up to sidewalk start
    BRUSHES.append(
        box(
            ROAD_X1 - STREET_CHARLES_CURB_W,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X1,
            CHARLES_SWALK_START,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # Raised ground west of curb — rock/ground texture, flush with sidewalk
    BRUSHES.append(
        box(
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X1 - STREET_CHARLES_CURB_W,
            CHARLES_SWALK_START,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
        )
    )
    # East sidewalk — split into two segments, trimmed CHARLES_WALK_W short of each corner
    BRUSHES.append(
        box(
            ROAD_X2,
            CHARLES_Y1,
            FLOOR_Z2,
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y - ENNIS_HW - CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    BRUSHES.append(
        box(
            ROAD_X2,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            FLOOR_Z2,
            ROAD_X2 + CHARLES_WALK_W,
            CHARLES_Y2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Ennis Road brushes ──
    # Road surface — split around centre divider slot and south curb strip (Y=776–784)
    # West section (near Charles St, no curb strip here)
    BRUSHES.append(
        box(
            ENNIS_X1,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2,
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # Main east sections — full south extent to road edge
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
                ENNIS_Y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2 + STREET_SURFACE_T,
                Textures.ROAD,
            )
        )
    # Corridor gap section (back road entrance, no curb strip)
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_CORRIDOR_X1,
            ENNIS_Y - ENNIS_HW,
            FLOOR_Z2,
            KNOTT_DRIVEWAY_CORRIDOR_X2,
            ENNIS_Y - STREET_ENNIS_DIV_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    BRUSHES.append(
        box(
            ENNIS_X1,
            ENNIS_Y,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # North curb — offset east by CHARLES_WALK_W to cut corner square
    BRUSHES.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # South curb — split into two segments with a gap for the back road entrance
    # West segment: Charles St east sidewalk to back road west sidewalk
    BRUSHES.append(
        box(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_SW_EDGE,
            FLOOR_Z2,
            KNOTT.x2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )
    # East segment: back road east sidewalk east to world wall
    BRUSHES.append(
        box(
            KNOTT_DRIVEWAY_ES_X2,
            ENNIS_SW_EDGE,
            FLOOR_Z2,
            ENNIS_X2,
            ENNIS_SW_EDGE + CHARLES_WALK_W,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.CEMENT,
        )
    )

    # ── Lane dividers — dashed sfloor3_2 flush inserts in carved road slots ───────
    TEX_DIVIDER = "sfloor3_2"
    dash_brushes = []
    # Charles Street — dashed N-S, two sections either side of bridge
    for section_y1, section_y2 in [(CHARLES_Y1, BRIDGE.y1), (BRIDGE.y2, CHARLES_Y2)]:
        divider_y = section_y1
        dash_on = True
        while divider_y < section_y2:
            next_divider_y = min(
                divider_y + (ROAD_DASH_LEN if dash_on else ROAD_GAP_LEN), section_y2
            )
            divider_tex = TEX_DIVIDER if dash_on else Textures.ROAD
            dash_brushes.append(
                box(
                    -STREET_DIV_HW,
                    divider_y,
                    FLOOR_Z2,
                    STREET_DIV_HW,
                    next_divider_y,
                    FLOOR_Z2 + STREET_SURFACE_T,
                    divider_tex,
                )
            )
            divider_y = next_divider_y
            dash_on = not dash_on
    # Ennis Road — dashed E-W from Charles St east to world wall
    divider_x = ROAD_X2
    dash_on = True
    while divider_x < ENNIS_X2:
        next_divider_x = min(
            divider_x + (ROAD_DASH_LEN if dash_on else ROAD_GAP_LEN), ENNIS_X2
        )
        divider_tex = TEX_DIVIDER if dash_on else Textures.ROAD
        dash_brushes.append(
            box(
                divider_x,
                ENNIS_Y - STREET_ENNIS_DIV_HW,
                FLOOR_Z2,
                next_divider_x,
                ENNIS_Y,
                FLOOR_Z2 + STREET_SURFACE_T,
                divider_tex,
            )
        )
        divider_x = next_divider_x
        dash_on = not dash_on
    if dash_brushes:
        ENTITIES.append(brush_ent("func_detail", dash_brushes))

    # ── Rounded intersection corners (Charles & Ennis) ───────────────────────────
    # Arc center at the OUTER (far) corner so the curve faces outward toward the road.
    # Each corner: road box fills the cut square, cement arc fans sit on top.
    # SE corner: far corner is at SE of cut square
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
    # Arc sweeps CCW from 90° (north) to 180° (west)
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
                Textures.CEMENT,
            )
        )

    # NE corner: far corner is at NE of cut square
    cx_ne = ROAD_X2 + CHARLES_CRN_R
    cy_ne = ENNIS_Y + ENNIS_HW + CHARLES_CRN_R
    BRUSHES.append(
        box(
            ROAD_X2,
            ENNIS_Y + ENNIS_HW,
            FLOOR_Z2,
            cx_ne,
            cy_ne,
            FLOOR_Z2 + STREET_SURFACE_T,
            Textures.ROAD,
        )
    )
    # Arc sweeps CCW from 180° (west) to 270° (south)
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
                Textures.CEMENT,
            )
        )

    # ── Sidewalk ramps — smooth ground-to-sidewalk transitions ───────────────────
    # West ramp — slopes from ground up to west sidewalk edge (full N-S extent)
    BRUSHES.append(
        ramp_slab(
            ROAD_X1 - CHARLES_WALK_W - CHARLES_RAMP_W,
            ROAD_X1 - CHARLES_WALK_W,
            CHARLES_Y1,
            CHARLES_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2,
            FLOOR_Z2 + CHARLES_WALK_H,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # East ramp — south of Ennis Road
    BRUSHES.append(
        ramp_slab(
            ROAD_X2 + CHARLES_WALK_W,
            ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W,
            CHARLES_Y1,
            ENNIS_SW_EDGE,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # East ramp — north of Ennis Road
    BRUSHES.append(
        ramp_slab(
            ROAD_X2 + CHARLES_WALK_W,
            ROAD_X2 + CHARLES_WALK_W + CHARLES_RAMP_W,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            CHARLES_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # Ennis north ramp — slopes from north curb edge down going north
    BRUSHES.append(
        ramp_slab_y(
            ROAD_X2 + CHARLES_WALK_W,
            ENNIS_X2,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
            ENNIS_Y + ENNIS_HW + CHARLES_WALK_W + CHARLES_RAMP_W,
            FLOOR_Z1,
            FLOOR_Z1,
            FLOOR_Z2 + CHARLES_WALK_H,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # (Ramp zone south of Ennis sidewalk covered by world floor — no fill needed)

    # Verge fill — ground between road south edge and sidewalk inner edge, flush with sidewalk
    # Split around back road corridor gap (KNOTT_DRIVEWAY_CORRIDOR_X1..KNOTT_DRIVEWAY_CORRIDOR_X2)
    # SE corner (east of back road) uses gravel3c (mulch bed)
    for vx1, vx2, vtex in [
        (ROAD_X2 + CHARLES_WALK_W, KNOTT_DRIVEWAY_CORRIDOR_X1, Textures.GROUND),
        (KNOTT_DRIVEWAY_CORRIDOR_X2, ENNIS_X2, "grave13c"),
    ]:
        BRUSHES.append(
            box(
                vx1,
                ENNIS_SW_EDGE + CHARLES_WALK_W,
                FLOOR_Z1,
                vx2,
                ENNIS_Y - ENNIS_HW - ENNIS_CURB_W,
                FLOOR_Z2 + CHARLES_WALK_H,
                vtex,
            )
        )

    # Cement curb strip — last 8 units of verge at road edge, flush with verge surface
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

    ennis_brushes, ennis_entities = build_ennis_entrance_features()
    BRUSHES.extend(ennis_brushes)
    ENTITIES.extend(ennis_entities)

    # ── Embankment — hill under Dorm buildings ───────────────────────────────────
    # Large terrain feature that blocks visibility — restore worldspawn routing.
    BRUSHES = _world_brushes
    # Interpolate ramp top-Z at the building's west face so the slope is continuous
    emb_zt_at_ab_x1 = int(
        BRIDGE_DZ2
        + (FLOOR_Z2 - BRIDGE_DZ2) * (DORM.x1 - BRIDGE.x1) / (DORM_EMB_X2 - BRIDGE.x1)
    )
    # Same hill-slope interpolation at the building's east face — used where the
    # ramp must skip the (now hollow) building interior and only fill the narrow
    # east toe strip between the east wall and the embankment edge.
    emb_zt_at_dorm_x2 = int(
        BRIDGE_DZ2
        + (FLOOR_Z2 - BRIDGE_DZ2) * (DORM.x2 - BRIDGE.x1) / (DORM_EMB_X2 - BRIDGE.x1)
    )
    # Gap segment — east of the tunnel channel only (DORM.x1 to DORM_EMB_X2).
    # The entire strip west of DORM.x1 aligned with the dorm buildings is now open
    # tunnel volume that extends all the way to the world west wall; geometry for
    # that hollow is handled entirely in west_campus.py.
    DORM_NORTH2_Y1 = DORM_NORTH_Y1 - DORM.depth  # south face of north building 2
    BRUSHES.append(
        ramp_slab(
            DORM.x1,
            DORM_EMB_X2,
            DORM_SOUTH2_Y2,
            DORM_NORTH2_Y1,
            FLOOR_Z1,
            FLOOR_Z1,
            emb_zt_at_ab_x1,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
            ts=Textures.SKY,  # gable ends face N/S world boundary — show sky
        )
    )
    # North building cluster — east toe strip only (DORM.x2 to DORM_EMB_X2).
    # The building interior (DORM.x1 to DORM.x2) is left hollow (carved out of the
    # hill) so the north dorms are open rooms with a flat floor at tunnel level;
    # only the narrow strip east of the building wall is backfilled to grade.
    BRUSHES.append(
        ramp_slab(
            DORM.x2,
            DORM_EMB_X2,
            DORM_NORTH2_Y1,
            DORM_NORTH_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            emb_zt_at_dorm_x2,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # North of north building — east strip only (DORM.x1 to DORM_EMB_X2).
    # The west strip (BRIDGE.x1..DORM.x1) is now the tunnel north extension,
    # owned by west_campus.py, so this ramp starts at DORM.x1.
    # ts=SKY: south gable end at DORM_NORTH_Y2 is partially exposed in the
    # carved-out north dorm interior (north cluster ramp starts at DORM.x2).
    BRUSHES.append(
        ramp_slab(
            DORM.x1,
            DORM_EMB_X2,
            DORM_NORTH_Y2,
            CHARLES_Y2,
            FLOOR_Z1,
            FLOOR_Z1,
            emb_zt_at_ab_x1,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
            ts=Textures.SKY,  # gable end visible behind north dorms — show sky
        )
    )

    # ── South-dorm terrace + gentler frontage hill out to Charles Street ──────────
    # South of the bridge (Y up to BRIDGE.y1) raise a flat terrace under the south
    # dorms + brick-wall gate, then slope gently down to grade near the road. This
    # lifts the ground at the brick wall (decreasing its visible height while its
    # top stays at the bridge deck) and gives the dorms a level pad.
    terr_top = FLOOR_Z2 + SDORM_LIFT
    terr_y1 = WORLD_Y1 + WALL_T
    # Flat terrace pad — west of the brick wall (under the south dorms): level
    # crest south of the wall's south pillar, then declining north (below) so the
    # ground west of the wall drops to the bridge symmetrically with the east side.
    # The pad is split into a frame around the south-dorm-1 stairwell void (carved
    # full-height z=FLOOR_Z2..terr_top so the steps can descend to the tunnel).
    BRUSHES.extend(
        [
            box(
                DORM.x1,
                terr_y1,
                FLOOR_Z2,
                SDORM_WALL_X,
                SDORM_STAIR_Y1,
                terr_top,
                Textures.GROUND,
                tt=Textures.GROUND,
            ),
            box(
                DORM.x1,
                SDORM_STAIR_Y2,
                FLOOR_Z2,
                SDORM_WALL_X,
                SDORM_SLOPE_Y_S,
                terr_top,
                Textures.GROUND,
                tt=Textures.GROUND,
            ),
            box(
                SDORM_STAIR_X2,
                SDORM_STAIR_Y1,
                FLOOR_Z2,
                SDORM_WALL_X,
                SDORM_STAIR_Y2,
                terr_top,
                Textures.GROUND,
                tt=Textures.GROUND,
            ),
        ]
    )
    # N-S decline west of the wall: crest at the south pillar down to grade at the
    # north side of the bridge, matching the wall→fence strip on the east side.
    BRUSHES.append(
        ramp_slab_y(
            DORM.x1,
            SDORM_WALL_X,
            SDORM_SLOPE_Y_S,
            SDORM_SLOPE_Y_N,
            FLOOR_Z2,
            FLOOR_Z2,
            terr_top,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # Strip between the brick wall and the front fence: flat crest south of the
    # wall's south pillar, then declining north (below) so this strip drops to
    # grade toward the bridge along with the fence instead of ending in a cliff.
    BRUSHES.append(
        box(
            SDORM_WALL_X,
            terr_y1,
            FLOOR_Z2,
            SDORM_TERRACE_X2,
            SDORM_SLOPE_Y_S,
            terr_top,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # N-S decline of the wall→fence strip: crest (terr_top) at the south pillar
    # down to grade at the north side of the bridge, flat across the strip width.
    BRUSHES.append(
        ramp_slab_y(
            SDORM_WALL_X,
            SDORM_TERRACE_X2,
            SDORM_SLOPE_Y_S,
            SDORM_SLOPE_Y_N,
            FLOOR_Z2,
            FLOOR_Z2,
            terr_top,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # Gentle frontage ramp east of the pad (Charles-St hill), south of the brick
    # wall's south pillar. North of the pillar the frontage instead declines to the
    # north (corner wedge below), so the fence stays connected down to the bridge.
    BRUSHES.append(
        ramp_slab(
            SDORM_TERRACE_X2,
            SDORM_TOE_X,
            terr_y1,
            SDORM_SLOPE_Y_S,
            FLOOR_Z2,
            FLOOR_Z2,
            terr_top,
            FLOOR_Z2,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )
    # Corner wedge: at/east of the front fence, decline from the terrace crest at
    # the south pillar down to grade at the north side of the bridge. High at the
    # (fence, south-pillar) corner; falls to grade along both the north edge and
    # the road edge. Its south edge (crest→road, E-W) matches the frontage ramp
    # above, so the two meet seamlessly.
    BRUSHES.append(
        corner_ramp(
            SDORM_TERRACE_X2,
            SDORM_TOE_X,
            SDORM_SLOPE_Y_S,
            SDORM_SLOPE_Y_N,
            FLOOR_Z2,
            terr_top,
            Textures.GROUND,
            tt=Textures.GROUND,
        )
    )

    if DETAIL_BRUSHES:
        ENTITIES.append(brush_ent("func_detail", DETAIL_BRUSHES))
    return BRUSHES, ENTITIES
