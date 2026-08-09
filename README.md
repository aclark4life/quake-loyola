# quake-loyola

[![CI](https://github.com/aclark4life/quake-loyola/actions/workflows/test.yml/badge.svg)](https://github.com/aclark4life/quake-loyola/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/quake-loyola/badge/?version=latest)](https://quake-loyola.readthedocs.io/en/latest/)
[![Google Maps](https://img.shields.io/badge/Google%20Maps-4285F4?logo=googlemaps&logoColor=white)](https://maps.app.goo.gl/DhqzsUa2x99KMbj89)
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

The `ql` CLI controls the build, backed by a `ql.toml` file at the repo root
(tracked in git — it's the current build's override layer on top of the
hardcoded defaults in `src/quake_loyola/config.py`). Install it as a
console-script:

```bash
pip install -e .       # installs the `ql` command + typer into your environment
```

### The settings you'll actually change

Five shortcut commands cover the day-to-day knobs. Run any of them with no
argument to print the current value and the valid ones:

```bash
ql sky                # show the current sky texture and every sky in the loaded WADs
ql sky sky_z1         # set it (a plain texture name — sky4, sky1, sky_z1, ...)
ql skybox mak_sunset1 # environment skybox; "none" falls back to the sky texture
ql fog high           # off/low/med/high, a number like 0.05, or "default"
ql light dusk         # time-of-day lighting: dawn/midday/golden_hour/dusk/...
ql vis full           # "fast" (default) or "full" vis pass, used by `ql build`
```

`ql fog default` means "use whatever fog the current `ql light` preset
defines"; any other value overrides it. `ql light` stays a named preset
because it sets six correlated worldspawn fields (sun color and angle,
ambient level, fog color) at once.

### Sky texture vs. skybox

They stack rather than compete, and you normally want both:

* **`ql sky`** picks a WAD2 texture whose name starts with `sky`. That prefix
  is how qbsp knows which faces are sky at all, so this setting is mandatory
  — and it's what TrenchBroom draws on those faces in the editor.
* **`ql skybox`** writes the `sky` worldspawn key, naming six images in the
  engine's `gfx/env` directory. Modern engines (vkQuake, QuakeSpasm,
  Ironwail) draw that cubemap *through* the sky faces at run time instead of
  the scrolling sky texture.

  Note the asymmetry: the *build setting* called `sky` is the texture, but
  the *worldspawn key* called `sky` is the skybox. That's the engines'
  convention, not ours — they've never read a texture name from worldspawn.
  qbsp ignores the key completely, so nothing is lost.

  The written value keeps the pack's trailing underscore (`mak_sunset1_`)
  because engines build each face path as `gfx/env/` + value + a bare `rt`,
  with no separator of their own. `ql skybox` takes the friendly name and
  works the separator out from the installed files.

The skybox images are art assets, not code — they are not tracked in this
repo. Install a pack (e.g. Makkon's) by unzipping it into `gfx/env` under
your Quake directory:

```bash
mkdir -p /Applications/id1/gfx/env
unzip -o makkon_skyboxes.zip -d /Applications/id1/gfx/env
ql skybox             # lists every skybox it found there
```

`ql skybox` only accepts a name whose six faces are all present, so a typo or
a half-copied pack is caught before the build instead of showing up as a
black sky in game. Set `$QUAKE_DIR` if your Quake directory isn't
`/Applications/id1`. Because a skybox is a run-time engine feature,
TrenchBroom does not render it — the editor keeps showing the flat sky
texture from `ql sky`.

### Everything else

```bash
ql conf show                     # every build setting, with its valid values
ql conf set light_extra true     # light -extra (2x2 supersampling)
ql conf set vis_mode=full lighting_preset=dusk fog_density=high  # several at once
ql conf get vis_mode
ql conf reset                    # delete ql.toml, back to defaults
```

### Running the build

```bash
ql gen                  # same as `just generate`, but config-aware
ql build                # generate + qbsp + vis + light + deploy
ql build --vis full     # override the configured vis mode for this run only
```

`just compile` and `just compile-fast` call `ql build` under the hood with
`--vis full` / `--vis fast`, so there's one implementation of the pipeline
and the recipe name always wins over `ql.toml`'s `vis_mode`.

`generate_map.py` (and `just generate`) automatically pick up whatever is in
`ql.toml` too — the CLI is just a convenient way to edit it. `just venv`
already runs `pip install -e .` for you, so `.venv/bin/ql` is ready to use
after `just test`/`just venv`.

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
