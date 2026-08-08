from ..constants import (
    DORM,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    ENTITIES_ENABLED_EXIT,
    FLOOR_Z2,
    NORTH_DORM_LIFT,
    WEST_CAMPUS_ENABLED_DORMS,
    Textures,
)
from ..geometry import (
    box,
    brush_ent,
    ent,
    render_text_flat,
    render_text_flat_x,
)


def _build_exit(ENTITIES):
    exit_start = len(ENTITIES)

    dorm_exit_xc = (DORM.x1 + DORM.x2) // 2
    _north2_y2 = DORM_NORTH_Y1
    _north2_y1 = _north2_y2 - (DORM_NORTH_Y2 - DORM_NORTH_Y1)
    dorm_exit_yc = (_north2_y1 + _north2_y2) // 2
    dorm_exit_hw = 64
    dorm_exit_z0 = FLOOR_Z2 + NORTH_DORM_LIFT
    dorm_exit_brush = box(
        dorm_exit_xc - dorm_exit_hw,
        dorm_exit_yc - dorm_exit_hw,
        dorm_exit_z0,
        dorm_exit_xc + dorm_exit_hw,
        dorm_exit_yc + dorm_exit_hw,
        dorm_exit_z0 + 112,
        Textures.TELEPORT,
    )
    ENTITIES.append(brush_ent("trigger_changelevel", dorm_exit_brush, map="loyola"))
    ENTITIES.append(brush_ent("func_illusionary", dorm_exit_brush))
    ENTITIES.append(
        ent(
            "light",
            origin=f"{dorm_exit_xc} {dorm_exit_yc} {dorm_exit_z0 + 56}",
            light="200",
            _color="0.4 0.6 1",
        )
    )

    frame_t = 16
    frame_d = 12
    ex1 = dorm_exit_xc - dorm_exit_hw
    ex2 = dorm_exit_xc + dorm_exit_hw
    portal_top = dorm_exit_z0 + 112

    exit_px_w, exit_px_h, exit_depth = 4, 2, 2

    exit_embed = 1
    exit_total = exit_depth + exit_embed
    exit_text_w = (4 * 5 - 1) * exit_px_w
    exit_x0 = dorm_exit_xc - exit_text_w // 2
    exit_z_base = portal_top + (frame_t - 6 * exit_px_h) // 2
    for face_yc, out_sign in [
        (dorm_exit_yc - dorm_exit_hw, -1),
        (dorm_exit_yc + dorm_exit_hw, +1),
    ]:
        fy1 = face_yc - frame_d // 2
        fy2 = face_yc + frame_d // 2
        for bx1, bx2, bz1, bz2 in [
            (ex1 - frame_t, ex1, dorm_exit_z0, portal_top + frame_t),
            (ex2, ex2 + frame_t, dorm_exit_z0, portal_top + frame_t),
            (ex1 - frame_t, ex2 + frame_t, portal_top, portal_top + frame_t),
        ]:
            ENTITIES.append(
                brush_ent(
                    "func_detail", box(bx1, fy1, bz1, bx2, fy2, bz2, Textures.CEMENT)
                )
            )

        if out_sign < 0:
            letter_text, y_face, do_mirror = "EXIT", fy1 - exit_depth, False
        else:
            letter_text, y_face, do_mirror = "EXIT"[::-1], fy2 - exit_embed, True
        letter_brushes = render_text_flat(
            letter_text,
            x0=exit_x0,
            y_face=y_face,
            z_base=exit_z_base,
            px_w=exit_px_w,
            px_h=exit_px_h,
            depth=exit_total,
            tex=Textures.LAVA,
            mirror=do_mirror,
        )
        if letter_brushes:
            ENTITIES.append(brush_ent("func_detail", letter_brushes))

    beam_y1 = dorm_exit_yc - dorm_exit_hw - frame_d // 2
    beam_y2 = dorm_exit_yc + dorm_exit_hw + frame_d // 2
    for bx1, bx2 in [(ex1 - frame_t, ex1), (ex2, ex2 + frame_t)]:
        ENTITIES.append(
            brush_ent(
                "func_detail",
                box(
                    bx1,
                    beam_y1,
                    portal_top,
                    bx2,
                    beam_y2,
                    portal_top + frame_t,
                    Textures.CEMENT,
                ),
            )
        )

    exit_y0 = dorm_exit_yc - exit_text_w // 2
    for x_face, letter_text, do_mirror in [
        (ex1 - frame_t - exit_depth, "EXIT"[::-1], True),
        (ex2 + frame_t - exit_embed, "EXIT", False),
    ]:
        lb = render_text_flat_x(
            letter_text,
            y0=exit_y0,
            x_face=x_face,
            z_base=exit_z_base,
            px_w=exit_px_w,
            px_h=exit_px_h,
            depth=exit_total,
            tex=Textures.LAVA,
            mirror=do_mirror,
        )
        if lb:
            ENTITIES.append(brush_ent("func_detail", lb))

    if not (ENTITIES_ENABLED_EXIT and WEST_CAMPUS_ENABLED_DORMS):
        del ENTITIES[exit_start:]


def _build_intermission(ENTITIES):
    if not (ENTITIES_ENABLED_EXIT and WEST_CAMPUS_ENABLED_DORMS):
        return
    ENTITIES.append(
        ent(
            "info_intermission",
            origin="-361 -500 350",
            mangle="-10 75 0",
        )
    )
