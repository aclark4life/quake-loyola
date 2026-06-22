# AGENTS.md — quake-loyola

A Quake 1 deathmatch map of the pedestrian bridge and Knott Hall at Loyola University Maryland, generated entirely from Python.

## Project layout

| Path | Purpose |
|---|---|
| `generate_map.py` | Entry point — assembles all modules into `loyola.map` |
| `quake_loyola/` | Python package — geometry primitives, map builder, per-area modules |
| `quake_loyola/mapdata.py` | `MapBuilder` — collects brushes/entities and serialises to `.map` |
| `quake_loyola/geometry.py` | Low-level brush / face construction helpers |
| `quake_loyola/constants.py` | Shared numeric constants and texture names |
| `quake_loyola/bridge.py` | Bridge deck, arch spans, piers, parapets |
| `quake_loyola/knott_hall.py` | Knott Hall facade, windows, mullions |
| `quake_loyola/knott_terrain.py` | Terrain / embankment around Knott Hall |
| `quake_loyola/streets.py` | Charles Street and surrounding road geometry |
| `quake_loyola/west_campus.py` | West-campus buildings and terrain |
| `quake_loyola/entities.py` | Player spawns, items, lights |
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

- **Coordinate system** — Quake standard: X = east, Y = south, Z = up. All constants use Quake units (1 unit ≈ 1 inch).
- **Module structure** — each area module (e.g. `bridge.py`) exposes a single `build() -> (brushes, entities)` function. `generate_map.py` calls every module's `build()` and merges results.
- **Texture names** — defined in `quake_loyola/constants.py` (`Textures.*`). Always use the constants; do not hardcode texture strings in geometry modules.
- **No side effects in modules** — area modules must not write files or print output; all I/O lives in `generate_map.py`.
- **WADs** — `quake101.wad`, `ad.wad`, and `makkon_building.wad` must be present in the project root. `just setup` downloads the first two automatically.

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
