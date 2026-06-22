# quake-loyola

A Quake 1 deathmatch map of the pedestrian bridge and Knott Hall at Loyola
University Maryland, generated entirely from Python.

![Screenshot](screenshot.png)

The map recreates the **pedestrian bridge over Charles Street** on Loyola's
Evergreen campus in northern Baltimore (39°20′46″N, 76°37′08″W), including
the arched stone bridge deck, five support piers, and the 1896 Knott Hall
building to the east.

## Quick start

```bash
brew install just        # if you don't have just yet
just                     # setup → generate → compile → deploy
```

### Individual steps

```bash
just setup          # download quake101.wad and ad.wad if missing
just generate       # run generate_map.py → loyola.map
just compile        # qbsp → vis → light (full vis pass)
just compile-fast   # qbsp → vis -fast → light (faster iteration)
just deploy         # copy loyola.bsp + loyola.lit to /Applications/id1/maps/
just test           # run the pytest suite
just update-golden  # recompute and patch golden hash/counts after geometry changes
```

ericw-tools are downloaded automatically to `.tools/` on first compile. WADs
are downloaded from Quaketastic automatically by `just setup`.

## Playing

```
quake -game id1 +map loyola
```

## Documentation

Full reference — map layout, terminology, structural dependencies, textures,
TrenchBroom setup, and architecture overview — is in the Sphinx docs:

```bash
just docs   # builds docs/_build/html/index.html
```

## Project layout

| Path | Purpose |
|---|---|
| `generate_map.py` | Entry point — assembles all modules into `loyola.map` |
| `quake_loyola/` | Python package — geometry primitives, map builder, per-area modules |
| `tests/` | pytest suite (geometry, mapdata, regression) |
| `justfile` | All build recipes |
| `docs/` | Sphinx documentation |
