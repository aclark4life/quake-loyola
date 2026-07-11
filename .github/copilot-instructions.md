# AGENTS.md — quake-loyola

A Quake 1 single-player and deathmatch map of the pedestrian bridge and Knott Hall at Loyola University Maryland, generated from Python with AI assistance.

## Project layout

| Path | Purpose |
|---|---|
| `generate_map.py` | Entry point — assembles all modules into `loyola.map` |
| `src/quake_loyola/` | Python package — geometry primitives, map builder, per-area modules |
| `src/quake_loyola/mapdata.py` | `MapBuilder` — collects brushes/entities and serialises to `.map` |
| `src/quake_loyola/geometry.py` | Low-level brush / face construction helpers |
| `src/quake_loyola/constants.py` | Shared numeric constants and texture names |
| `src/quake_loyola/bridge.py` | Bridge deck, arch spans, piers, parapets |
| `src/quake_loyola/knott_hall.py` | Knott Hall facade, windows, mullions |
| `src/quake_loyola/knott_terrain.py` | Terrain / embankment around Knott Hall |
| `src/quake_loyola/streets.py` | Charles Street and surrounding road geometry |
| `src/quake_loyola/west_campus.py` | West-campus buildings and terrain |
| `src/quake_loyola/entities.py` | Player spawns, items, lights |
| `tests/` | pytest suite (geometry, mapdata, regression) |
| `justfile` | All build recipes (see below) |

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

## Key conventions

- **Coordinate system** — X = east, Y = north, Z = up (per the module docstring of `src/quake_loyola/constants.py`; +Y is north, −Y is south). Quake +Y (north) is aligned with real-world true north to within ~5.5° (Charles St's actual compass bearing is ~354.5°, but the model treats it as running exactly along the Y-axis) — an accepted simplification. All constants use Quake units (1 unit ≈ 0.79 inch, see `docs/reference.rst` § World scale).
- **Naming conventions** — constant names are `AREA_FEATURE_SUFFIX`. Common suffixes: `X1/X2 Y1/Y2 Z1/Z2` = box min/max on an axis (1 = lower); `DZ1/DZ2` = deck Z bottom/top; `ZB/ZT` = z bottom/top; `CX/CY` = centre; `XS/YS` = list of positions; `N/S/E`/`NY` = compass direction; `H/HH` = height/half-height; `W/HW` = width/half-width; `T` thickness, `R` radius, `D` depth; `OVH` overhang, `PROUD` protrusion. Feature abbrevs: `PILLAR BLK SQ PYR ENT WIN DIV PLT BR`, `DRIVEWAY_WS/RD/ES` (west→east), `BIY` (Knott inner wall face), `ORIG` (pre-extension), `KH` (Knott Hall). Full legend: module docstring of `src/quake_loyola/constants.py` and `docs/reference.rst`.
- **Module structure** — each area module (e.g. `bridge.py`) exposes a single `build() -> (brushes, entities)` function. `generate_map.py` calls every module's `build()` and merges results.
- **Texture names** — defined in `src/quake_loyola/constants.py` (`Textures.*`). Always use the constants; do not hardcode texture strings in geometry modules.
- **No side effects in modules** — area modules must not write files or print output; all I/O lives in `generate_map.py`.
- **WADs** — `quake101.wad`, `ad.wad`, `makkon_building.wad`, `ikwhite.wad`, and `makkon_stone.wad` must be present in the project root. `just setup` downloads `quake101.wad` and `ad.wad` automatically; the others are provided manually.

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

### One committer at a time
Only one AI assistant — Auggie/Augment **or** Copilot, never both — should commit for a given change. Do not let both assistants create commits for the same change (e.g. one committing and the other amending, or both committing separately). Whichever assistant is actively working the task owns the commit; the other must not commit on top of it. Auggie has sometimes forgotten to add its `Co-authored-by: Augment` trailer — always double-check the trailer is present before pushing, regardless of which assistant is committing.

### Co-commit authorship
When committing on behalf of the user, always list the user as the **primary author** and the AI assistant as a **co-author** using the `Co-authored-by:` trailer:

```
git commit --author="Jeffrey 'Alex' Clark <aclark@aclark.net>" -F <msg-file>
```

Commit message trailer:
```
Co-authored-by: Augment <augment@augmentcode.com>
```

Never make the AI assistant the primary author.
