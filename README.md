# quake-loyola

A Quake 1 deathmatch map inspired by the pedestrian bridge at Loyola University Maryland.

## Files

| File | Description |
|---|---|
| `loyola.map` | Map source (TrenchBroom / Quake 1 `.map` format) |
| `generate_map.py` | Python script that generates the `.map` from scratch |

## Map layout

```
[W Building] ──── bridge span ──── [E Building]
              ↑arch              arch↑
      pillars + railings all along
```

- **Bridge span**: 1024 × 256 units, deck at Z 128–144  
- **Entry arch gates**: semicircular stone arch portals at each end (8 voussoir segments)  
- **Stone pillars**: 8 total (4 per side) with metal caps  
- **Metal railings**: between every pillar pair  
- **Buildings**: hollow stone rooms at each end, connected flush to the deck  
- **Ravine**: open void below the bridge; rock floor  
- **Sky**: `sky4` dome, sealed outer box  

## Textures required

All textures come from the stock Quake data files. Extract `quake101.wad` from your Quake `PAK0.PAK` / `PAK1.PAK` files and place it alongside the `.map` file before compiling.

| Surface | Texture name |
|---|---|
| Bridge deck | `afloor1_4` |
| Stone pillars, arch | `stone1_5` |
| Building walls | `bricka2_1` |
| Pillar caps, railings | `metal5_4` |
| Ravine floor | `rock1_2` |
| Sky surfaces | `sky4` |

## Entities

| Entity | Qty | Location |
|---|---|---|
| `info_player_deathmatch` | 6 | 3 per building room |
| `weapon_supershotgun` | 1 | Bridge centre |
| `weapon_rocketlauncher` | 1 | Under west arch |
| `weapon_nailgun` | 1 | Under east arch |
| `item_health` | 3 | Bridge deck |
| `item_armortype` | 1 | West building |
| `light` | 9 | Above pillars, arch crowns, building interiors |

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
