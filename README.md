# quake-loyola

A Quake 1 deathmatch map inspired by the pedestrian bridge at Loyola University Maryland.

## Files

| File | Description |
|---|---|
| `loyola_bridge.map` | Map source (TrenchBroom / Quake 1 `.map` format) |
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

All textures come from the stock `quake101.wad` (bundled with Quake):

| Surface | Texture name |
|---|---|
| Bridge deck top | `floor0_1` |
| Stone pillars, arch, buildings | `brown66` |
| Bridge deck underside / walls | `brown25` |
| Pillar caps, railings | `metal5_4` |
| Ravine floor | `rock1_1` |
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

You need the Quake compile tools: **qbsp**, **vis**, and **light**.  
Popular options: [ericw-tools](https://github.com/ericwa/ericw-tools) or [TyrUtils-ericw](https://github.com/ericwa/tyrutils-ericw).

```bash
# 1. BSP (geometry)
qbsp loyola_bridge.map

# 2. Visibility (inter-leaf vis — speeds up rendering significantly)
vis loyola_bridge.bsp

# 3. Lighting
light loyola_bridge.bsp
```

The compiled `loyola_bridge.bsp` goes in your Quake `id1/maps/` directory.

## Loading in Quake

```
quake -game id1 +map loyola_bridge
```

Or from the console:
```
map loyola_bridge
```

## Editing in TrenchBroom

1. Open TrenchBroom and set game to **Quake**.
2. Set your `quake101.wad` path under *Preferences → Quake → Game Path*.
3. Open `loyola_bridge.map` — all brushes load as worldspawn geometry.

## Regenerating the map

```bash
python3 generate_map.py
```

This rewrites `loyola_bridge.map` from scratch. Edit constants at the top of the script to change dimensions, arch radius, pillar count, etc.
