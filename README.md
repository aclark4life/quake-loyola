# quake-loyola

[![CI](https://github.com/aclark4life/quake-loyola/actions/workflows/test.yml/badge.svg)](https://github.com/aclark4life/quake-loyola/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/quake-loyola/badge/?version=latest)](https://quake-loyola.readthedocs.io/en/latest/)
[![Google Maps](https://img.shields.io/badge/Google%20Maps-4285F4?logo=googlemaps&logoColor=white)](https://maps.app.goo.gl/kMYBXK4CLD4dfSGV7)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white)](https://youtu.be/Jr85JpCLgp8?si=kftormuGFAedw3xj&t=105)

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

## Configuring the build

Which modules get built (bridge, Knott Hall, terrain, lights, etc.) and a
couple of compile-time settings (vis/light quality) are controlled by the
`ql` CLI, backed by a `ql.toml` file at the repo root (gitignored — it's a
per-user override layer on top of the hardcoded defaults in
`src/quake_loyola/config.py`). Install it as a console-script:

```bash
pip install -e .       # installs the `ql` command + typer into your environment
ql conf show
```

```bash
ql conf show
ql conf set KNOTT_ENABLED true   # flip a module/light flag on or off
ql conf set vis_mode full             # "fast" (default) or "full" vis pass
ql conf set light_extra true          # light -extra (2x2 supersampling)
ql conf set lighting_preset dusk      # dawn/midday/golden_hour/dusk/overcast/night/bright/afternoon
ql conf set fog_density high          # "default" (preset's own), off/low/med/high, or a custom float
ql conf set sky_preset night          # day (default) or night
ql conf set vis_mode=full lighting_preset=dusk fog_density=high  # set several at once
ql conf get KNOTT_ENABLED
ql conf reset                         # delete ql.toml, back to defaults
ql gen                                  # same as `just generate`, but config-aware
ql build                                # generate + qbsp + vis + light + deploy,
                                           # using the [build] settings above
```

`generate_map.py` (and `just generate`) automatically pick up whatever is in
`ql.toml` too — `ql conf set ...` is just a convenient way to edit it.
`just venv` already runs `pip install -e .` for you, so `.venv/bin/ql` is
ready to use after `just test`/`just venv`.

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
