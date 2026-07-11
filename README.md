# quake-loyola

[![Documentation Status](https://readthedocs.org/projects/quake-loyola/badge/?version=latest)](https://quake-loyola.readthedocs.io/en/latest/)
[![View on Google Maps](https://img.shields.io/badge/Google%20Maps-View%20Location-4285F4?logo=googlemaps&logoColor=white)](https://maps.app.goo.gl/1TR7jd7fwHDz4P1z9)

A Quake 1 single-player and deathmatch map of the pedestrian bridge and Knott
Hall at Loyola University Maryland, generated from Python with AI assistance.

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

## Presentation

A Quake-themed [reveal.js](https://revealjs.com/) slide deck introduces the
project (`presentation/index.html`):

```bash
just present   # serves http://localhost:8000/presentation/
```

## Project layout

| Path | Purpose |
|---|---|
| `generate_map.py` | Entry point — assembles all modules into `loyola.map` |
| `src/quake_loyola/` | Python package — geometry primitives, map builder, per-area modules |
| `tests/` | pytest suite (geometry, mapdata, regression) |
| `justfile` | All build recipes |
| `docs/` | Sphinx documentation |
| `presentation/` | Quake-themed reveal.js slide deck |
