# AGENTS.md — quake-loyola

A Quake 1 single-player and deathmatch map of the pedestrian bridge and Knott Hall at Loyola University Maryland, generated from Python with AI assistance.

## Project layout

| Path | Purpose |
|---|---|
| `generate_map.py` | Entry point — thin wrapper delegating to `quake_loyola.mapgen`, writes `loyola.map` |
| `src/quake_loyola/mapgen.py` | Actual module-assembly logic (`build_map`, `main`) — importable once pip-installed |
| `src/quake_loyola/` | Python package — geometry primitives, map builder, per-area modules |
| `src/quake_loyola/mapdata.py` | `MapBuilder` — collects brushes/entities and serialises to `.map` |
| `src/quake_loyola/geometry/` | Low-level brush / face construction helpers (package: primitives, structures, prefabs, buildings, entities, helpers) |
| `src/quake_loyola/constants/` | Shared numeric constants and texture names (package: world, textures, lighting, fonts, trees, ennis, bridge, streets, dorm, knott, derived) |
| `src/quake_loyola/bridge.py` | Bridge deck, arch spans, piers, parapets |
| `src/quake_loyola/knott_hall.py` | Knott Hall shell (walls, roof, fascia sign) |
| `src/quake_loyola/streets/` | Charles Street and surrounding road geometry (package: `shell`, `ennis`, `details`) |
| `src/quake_loyola/west_campus.py` | West-campus frontage (iron fence, brick wall, terrace walk) |
| `src/quake_loyola/terrain/` | Real-elevation / provisional ground-fill modules, one per quadrant (`knott_hall`, `ne`, `west_campus`) |
| `src/quake_loyola/entities/` | Single-player spawn point + teleport destination (single module: `__init__.py`; item/monster/light placement lives in the area modules that own the geometry they occupy) |
| `tests/` | pytest suite (geometry, mapdata, regression) |
| `justfile` | All build recipes (see below) |
| `ql` | Typer CLI entry point — `ql sky/fog/light/vis` / `ql conf ...` / `ql gen` / `ql build` (pip-installed via `[project.scripts]`) |
| `src/quake_loyola/config.py` | Build-setting defaults + `ql.toml` load/save |
| `src/quake_loyola/cli.py` | `ql` CLI implementation (Typer app) |
| `src/quake_loyola/build_presets.py` | Valid values for the `[build]` settings, and their validators |
| `src/quake_loyola/wads.py` | The project's WAD list + a minimal WAD2 reader (used to validate `sky`) |

## Workflow

### 1 — Generate the `.map` file

```bash
python generate_map.py
```

This writes `loyola.map`.

### 2 — Compile (fast, for iteration)

```bash
just compile-fast
```

Runs `qbsp` → `vis -fast` → `light`. Compiled output: `loyola.bsp` + `loyola.lit`.

### 3 — Compile (full quality)

```bash
just compile
```

Same pipeline without `-fast` vis; takes longer but produces better PVS.

### 4 — Deploy to Quake

```bash
just deploy
```

Copies `loyola.bsp` and `loyola.lit` to `/Applications/id1/maps/`.

### All-in-one

```bash
just          # runs: setup → generate → compile-fast → deploy
```

## Tests

```bash
just test
```

Runs the full pytest suite under `.venv/`. Tests cover geometry helpers, `MapBuilder` serialisation, and map-level regressions.

## Configuring the build

The `[build]` settings (sky, fog, lighting, vis/light quality) are stored in
`ql.toml` (repo root, tracked in git) and edited with the `ql` CLI — see the
module docstring of `src/quake_loyola/config.py`, `docs/cli.rst`, and the
README's "Configuring the build" section. There are no module on/off flags:
every area module is always built.

The settings changed most often have single-purpose commands; each prints the
current value and the valid ones when run with no argument:

```bash
ql sky sky_z1     # world sky texture (a plain WAD2 texture name)
ql fog high       # off/low/med/high, a number, or "default" (the light preset's own)
ql light dusk     # time-of-day lighting preset
ql vis full       # vis pass used by `ql build`
```

Everything else goes through `ql conf set <NAME> <value>`, and `ql conf show`
lists every setting with its default and valid values. `generate_map.py`
picks up `ql.toml` automatically through `constants/lighting.py` and
`constants/textures.py` at import time.

## Key conventions

- **Coordinate system** — X = east, Y = north, Z = up (per the module docstring of `src/quake_loyola/constants/__init__.py`; +Y is north, −Y is south). Quake +Y (north) is aligned with real-world true north to within ~5.5° (Charles St's actual compass bearing is ~354.5°, but the model treats it as running exactly along the Y-axis) — an accepted simplification. All constants use Quake units (1 unit ≈ 0.79 inch, see `docs/reference.rst` § World scale).
- **Naming conventions** — constant names are `AREA_FEATURE_SUFFIX`. Common suffixes: `X1/X2 Y1/Y2 Z1/Z2` = box min/max on an axis (1 = lower); `DZ1/DZ2` = deck Z bottom/top; `ZB/ZT` = z bottom/top; `CX/CY` = centre; `XS/YS` = list of positions; `N/S/E`/`NY` = compass direction; `H/HH` = height/half-height; `W/HW` = width/half-width; `T` thickness, `R` radius, `D` depth; `OVH` overhang, `PROUD` protrusion. Feature abbrevs: `PILLAR BLK SQ PYR ENT WIN DIV PLT BR`, `DRIVEWAY_WS/RD/ES` (west→east), `BIY` (Knott inner wall face), `ORIG` (pre-extension), `KH` (Knott Hall). Full legend: module docstring of `src/quake_loyola/constants/__init__.py` and `docs/reference.rst`.
- **Module structure** — each area module (e.g. `bridge.py`) exposes a single `build() -> (brushes, entities)` function. `mapgen.build_map()` (invoked via `generate_map.py` or `ql gen`) calls every module's `build()` and merges results.
- **Texture names** — defined in `src/quake_loyola/constants/textures.py` (`Textures.*`). Always use the constants; do not hardcode texture strings in geometry modules.
- **No side effects in area modules** — area modules (`bridge.py`, `knott_hall.py`, `west_campus.py`, `streets/`, `terrain/`, `entities/`, etc.) must not write files or print output. File writing/printing is confined to the entrypoint layer (`mapgen.main()`, shared by `generate_map.py` and `ql gen`), not to individual area modules.
- **WADs** — the list lives in `src/quake_loyola/wads.py` (`WAD_FILES`), which is the single source of truth for both the worldspawn `wad` key and the `sky` setting's validation: `quake101.wad`, `ad.wad`, `makkon_building.wad`, `ikwhite.wad`, `makkon_stone.wad`, `mg1.wad`, `alkaline.wad`, and `makkon_nature.wad` must be present in the project root. `just setup` downloads `quake101.wad` and `ad.wad` automatically; the others are provided manually.

## Dependencies

- Python 3.11+
- [`just`](https://github.com/casey/just) — task runner
- `ericw-tools` (qbsp / vis / light) — downloaded automatically by `just install-tools`
- pytest — installed into `.venv` by `just venv`

## Docs

```bash
just docs
```

Builds Sphinx HTML documentation into `docs/_build/html/`.

## Agent workflow

### Map changes
1. After every prompted change, always run the full pipeline — no exceptions, even for leak checks or intermediate validation:
   ```bash
   just generate && just compile-fast && just deploy
   ```
2. Never run `qbsp` alone as a substitute for the full pipeline. `compile-fast` runs `qbsp` → `vis -fast` → `light`; skipping `vis` or `light` leaves a stale `.bsp` in the Quake maps folder.
3. **Always run `just deploy` after every compile.** Skipping it leaves the in-game build out of sync with the compiled `.bsp`; in-game testing will reflect old geometry even though the source and local `.bsp` are up to date.
4. Wait for explicit confirmation before committing
5. Always commit **and** push together — never commit without pushing
6. If the map geometry changes, run the full verification pipeline including deploy:
   ```bash
   just generate && just compile-fast && just deploy && just update-golden && just test
   ```

### Co-commit authorship
When committing on behalf of the user, always list the user as the **primary author** and Copilot as a **co-author** using the `Co-authored-by:` trailer:

```
git commit --author="Jeffrey 'Alex' Clark <aclark@aclark.net>" -F <msg-file>
```

Commit message trailer:
```
Co-authored-by: Copilot (github-copilot-cli) <223556219+Copilot@users.noreply.github.com>
```

The app slug in parentheses matters. Two separate GitHub Apps both have the
login `Copilot`, and their emails differ only by the numeric ID prefix:

| App | Identity |
|---|---|
| Copilot CLI (this agent) | `Copilot (github-copilot-cli) <223556219+Copilot@users.noreply.github.com>` |
| Copilot coding agent (cloud) | `copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>` |

Without the slug both render as a bare "Copilot" in `git log` and are
indistinguishable. GitHub itself resolves co-authors by email, so the website
still shows two identically-named contributors regardless — the slug is for
reading the history locally.

Never make the AI assistant the primary author. A commit should carry exactly
one AI co-author trailer — never more than one.
