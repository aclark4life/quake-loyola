from ..constants import (
    BRIDGE,
    ENNIS_HW,
    ENNIS_WIDEN_N,
    ENNIS_Y,
    ENTITIES_ENABLED_MONSTERS,
    FLOOR_Z2,
    KNOTT,
    KNOTT_DRIVEWAY_RD_X1,
    KNOTT_DRIVEWAY_RD_X2,
    KNOTT_DRIVEWAY_Y1,
    KNOTT_DRIVEWAY_Y2,
    KNOTT_DRIVEWAY_ZT_N,
    KNOTT_DRIVEWAY_ZT_S,
    KNOTT_ENABLED_TERRAIN,
    KNOTT_ENABLED_WALKWAY,
    KNOTT_ENT_WALK_X1,
    KNOTT_ENT_WALK_X2,
    KNOTT_ENT_WALK_ZT1,
    KNOTT_ENT_WALK_ZT2,
    KNOTT_GROUND_Z,
    ROAD_X1,
    ROAD_X2,
    deck_top_z,
)
from ..geometry import (
    ent,
)
from ._common import ROAD_Z, _cs_offset


def _build_monsters(ENTITIES):
    monsters_start = len(ENTITIES)

    _og1_y, _og1_z = _cs_offset(-300, 0, int(deck_top_z(-300) + 8))
    _og2_y, _og2_z = _cs_offset(300, 0, int(deck_top_z(300) + 8))
    ENTITIES.append(ent("monster_ogre", origin=f"-300 {_og1_y} {_og1_z}", angle="90"))
    ENTITIES.append(ent("monster_ogre", origin=f"300 {_og2_y} {_og2_z}", angle="270"))

    ENTITIES.append(ent("monster_ogre", origin=f"0 200 {ROAD_Z + 24}", angle="180"))
    ENTITIES.append(ent("monster_ogre", origin=f"0 -600 {ROAD_Z + 24}", angle="0"))

    ENTITIES.append(ent("monster_ogre", origin=f"700 0 {ROAD_Z + 24}", angle="270"))

    ENTITIES.append(ent("monster_ogre", origin=f"-700 0 {ROAD_Z + 24}", angle="90"))

    if not ENTITIES_ENABLED_MONSTERS:
        del ENTITIES[monsters_start:]


def _build_monsters2(ENTITIES):
    monsters2_start = len(ENTITIES)

    monster_stand_z = ROAD_Z + 24
    for monster_x, monster_y, monster_angle in [
        (ROAD_X1 + 64, -1200, 90),
        (ROAD_X2 - 64, -800, 270),
        (ROAD_X1 + 64, -300, 90),
        (ROAD_X2 - 64, 200, 270),
        (0, -1600, 90),
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    for monster_x, monster_y, monster_angle in [
        (500, ENNIS_Y - ENNIS_HW + 40, 0),
        (1200, ENNIS_Y + ENNIS_HW + ENNIS_WIDEN_N - 40, 180),
        (1800, ENNIS_Y - ENNIS_HW + 40, 0),
    ]:
        ENTITIES.append(
            ent(
                "monster_knight",
                origin=f"{monster_x} {monster_y} {monster_stand_z}",
                angle=str(monster_angle),
            )
        )

    backroad_center_x = (KNOTT_DRIVEWAY_RD_X1 + KNOTT_DRIVEWAY_RD_X2) // 2
    _backroad_rise = KNOTT_DRIVEWAY_ZT_S - KNOTT_DRIVEWAY_ZT_N

    if KNOTT_ENABLED_TERRAIN:
        # The backroad driveway ground these knights stand on only exists
        # when the Knott driveway terrain is built.
        for ogre_y, ogre_z in [
            (
                -600,
                FLOOR_Z2
                + 2
                + (
                    _backroad_rise
                    * ((-600) - KNOTT_DRIVEWAY_Y2)
                    // (KNOTT_DRIVEWAY_Y1 - KNOTT_DRIVEWAY_Y2)
                )
                + 24,
            ),
            (
                -1200,
                FLOOR_Z2
                + 2
                + (
                    _backroad_rise
                    * ((-1200) - KNOTT_DRIVEWAY_Y2)
                    // (KNOTT_DRIVEWAY_Y1 - KNOTT_DRIVEWAY_Y2)
                )
                + 24,
            ),
            (KNOTT_DRIVEWAY_Y1 + 64, KNOTT_GROUND_Z + 2 + 24),
        ]:
            ENTITIES.append(
                ent(
                    "monster_knight",
                    origin=f"{backroad_center_x} {ogre_y} {ogre_z}",
                    angle="90",
                )
            )

    deck_center_z = int(deck_top_z(0)) + 24
    deck_p3_z = int(deck_top_z(525)) + 24
    for monster_x, monster_y, monster_z, monster_angle in [
        (0, *_cs_offset(0, 0, deck_center_z), 180),
        (525, *_cs_offset(525, 0, deck_p3_z), 0),
    ]:
        ENTITIES.append(
            ent(
                "monster_hell_knight",
                origin=f"{monster_x} {monster_y} {monster_z}",
                angle=str(monster_angle),
            )
        )

    if KNOTT_ENABLED_WALKWAY:
        walkway_mid_x = (KNOTT_ENT_WALK_X1 + KNOTT_ENT_WALK_X2) // 2
        walkway_mid_y = (BRIDGE.y1 + KNOTT.y2) // 2
        walkway_mid_z = (KNOTT_ENT_WALK_ZT1 + KNOTT_ENT_WALK_ZT2) // 2
        ENTITIES.append(
            ent(
                "monster_hell_knight",
                origin=f"{walkway_mid_x} {walkway_mid_y} {walkway_mid_z + 24}",
                angle="180",
            )
        )

        accessible_walk_z = KNOTT_GROUND_Z + 24
        # These two stand on the Knott hillside beside the walkway rather than
        # on the walkway slab itself (x=2120 is east of it), so they need the
        # terrain that supports them, not just the walkway.
        for accessible_walk_y, accessible_walk_angle in (
            [(-128, 90), (180, 270)] if KNOTT_ENABLED_TERRAIN else []
        ):
            ENTITIES.append(
                ent(
                    "monster_hell_knight",
                    origin=f"2120 {accessible_walk_y} {accessible_walk_z}",
                    angle=str(accessible_walk_angle),
                )
            )

    if not ENTITIES_ENABLED_MONSTERS:
        del ENTITIES[monsters2_start:]
