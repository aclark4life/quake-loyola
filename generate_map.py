#!/usr/bin/env python3
from constants import TEX_SKY

import streets
import west_campus
import bridge
import knott_hall
import entities


def main():
    BRUSHES = []
    ENTITIES = []
    for mod in [streets, west_campus, bridge, knott_hall, entities]:
        brushes, ents = mod.build()
        BRUSHES.extend(brushes)
        ENTITIES.extend(ents)

    worldspawn = (
        "{\n"
        '"classname" "worldspawn"\n'
        '"wad" "quake101.wad;ad.wad"\n'
        '"message" "Loyola Bridge & Knott Hall"\n'
        f'"sky" "{TEX_SKY}"\n'
        '"ambient" "60"\n'
        '"_sunlight" "220"\n'
        '"_sunlight_color" "255 245 210"\n'
        '"_sunlight_dir" "60 -60"\n'
        '"_sunlight_penumbra" "8"\n'
        '"dmflags" "128"\n'
        '"_fog" "0.03 0.5 0.5 0.6"\n' + "\n".join(BRUSHES) + "\n}"
    )
    map_text = worldspawn + "\n\n" + "\n\n".join(ENTITIES) + "\n"
    with open("loyola.map", "w") as f:
        f.write(map_text)
    print(
        f"loyola.map written — {len(BRUSHES)} worldspawn brushes, {len(ENTITIES)} entities"
    )


if __name__ == "__main__":
    main()
