# quake-loyola

A Quake 1 deathmatch map inspired by the pedestrian bridge at Loyola University Maryland.

## Files

| File | Description |
|---|---|
| `loyola.map` | Map source (TrenchBroom / Quake 1 `.map` format) |
| `generate_map.py` | Python script that generates the `.map` from scratch |

## Map layout

```
[West Campus] ──── bridge span ──── [Knott Hall]
              ↑arch              arch↑
      5 stone pillars supporting the span
```

- **Bridge span**: 1050-unit arched span (69.5 ft), deck at Z 128–144.
- **Entry arch gates**: Semicircular stone arch portals at each end (16 voussoir segments) with teleport fields.
- **Stone pillars**: 5 supporting piers (only 2 visible by default) with narrow arched openings.
- **Knott Hall**: A 4-story brutalist tower on the south campus, featuring vertical "fins" on its north facade.
- **Charles Street**: Road surface running N-S under the bridge.
- **Sky**: `sky1` ceiling, sealed outer box.

## Textures required

All textures come from the stock Quake data files. Extract `quake101.wad` from your Quake `PAK0.PAK` / `PAK1.PAK` files and place it alongside the `.map` file before compiling.

| Surface | Texture name |
|---|---|
| Bridge deck | `sfloor3_2` |
| Stone pillars, arch | `city6_7` |
| Knott Hall walls | `tech03_1` |
| Road surface | `stone1_7` |
| Ravine floor | `rock1_2` |
| Sky surfaces | `sky1` |

## Entities

| Entity | Qty | Location |
|---|---|---|
| `info_player_deathmatch` | 14 | Scattered across bridge, campus, and hall |
| `weapon_rocketlauncher` | 4 | Bridge deck, Knott Hall (Floors 1 & 3), East campus |
| `item_health` | 3 | Bridge deck, Hall entrance, Hall 2nd floor |
| `light` | ~20 | Pillar caps, hall interior/exterior, road, and teleport arches |
| `func_plat` | 1 | Lift shaft inside Knott Hall |

## Compiling

You need **ericw-tools v0.18.1** or later: [github.com/ericwa/ericw-tools/releases](https://github.com/ericwa/ericw-tools/releases).  
Place `quake101.wad` in the same directory as the `.map` file, then:

```bash
# 1. BSP (geometry)
qbsp loyola.map

# 2. Visibility (inter-leaf vis — speeds up rendering significantly)
vis loyola.bsp

# 3. Lighting
light loyola.bsp
```

The compiled `loyola.bsp` goes in your Quake `id1/maps/` directory.

## Loading in Quake

```
quake -game id1 +map loyola
```

Or from the console:
```
map loyola
```

## Editing in TrenchBroom

TrenchBroom is pre-configured for this project. The following files are written to
TrenchBroom's app-support folder and are **not** committed to the repo (they reference
absolute paths on your machine):

| File | Location |
|---|---|
| Game path | `~/Library/Application Support/TrenchBroom/Preferences.json` |
| Compile profiles | `~/Library/Application Support/TrenchBroom/games/Quake/CompilationProfiles.cfg` |
| Engine profile | `~/Library/Application Support/TrenchBroom/games/Quake/GameEngineProfiles.cfg` |

### Game path (`Preferences.json`)

```json
{
    "Games/Quake/Path": "/Applications"
}
```

Points TrenchBroom at the directory that contains `id1/` (PAK files, WADs, compiled maps).

### Compile profiles (`CompilationProfiles.cfg`)

Both profiles use `${MAP_DIR_PATH}` as the working directory so ericw-tools picks up
`quake101.wad` from the same folder as the `.map` file.

**Full Build** — qbsp → vis → light → copy to `/Applications/id1/maps/`  
**Fast Build** — qbsp only → copy (quick geometry iteration)

Tool paths point to `~/Downloads/ericw-tools-v0.18.1-Darwin/bin/`.  
The compiled BSP is copied to `/Applications/id1/maps/` after each build.

### Engine profile (`GameEngineProfiles.cfg`)

Launches vkQuake with:

```
/Applications/vkQuake.app/Contents/MacOS/vkQuake -basedir /Applications +map ${MAP_BASE_NAME}
```

### Workflow

1. Open `loyola.map` in TrenchBroom (**File → Open**).
2. Edit brushes / entities as needed.
3. **Run → Compile Map** → choose *Full Build* or *Fast Build*.
4. **Run → Launch Engine** → choose *vkQuake* to test immediately.

## Regenerating the map

```bash
python3 generate_map.py
```

This rewrites `loyola.map` from scratch. Edit constants at the top of the script to change dimensions, arch radius, pillar count, etc.
