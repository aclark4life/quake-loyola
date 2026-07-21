"""sample_elevation — real-world elevation sampling for terrain re-derivation.

Converts named Quake-space (X, Y) sample points to real-world lat/lon (using
the project's established ft/px scale and Charles St's measured compass
bearing), queries the USGS 3DEP Elevation Point Query Service, and writes the
results to a cached CSV so downstream terrain work doesn't need network
access on every run.

Anchor point: Charles St & Cold Spring Ln bus stop (39.3455N, 76.6221W),
taken to correspond to Quake (X=0, Y=CHARLES_Y1) — the south end of the
modeled Charles St corridor (see docs/reference.rst SS Orientation / World
scale / Topology check). This is a documented assumption, not a surveyed
tie-point; revisit if a better-anchored reference point becomes available.

Usage:
    python3 scripts/sample_elevation.py            # sample the default points
                                                     # below, write the CSV
    python3 scripts/sample_elevation.py --no-fetch  # recompute derived
                                                     # columns from the
                                                     # existing CSV only,
                                                     # no network access

Output: docs/elevation_samples.csv (checked into the repo so the build
pipeline and future terrain work can read cached values without hitting the
network).
"""

import argparse
import csv
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "src"))

from quake_loyola.constants import (  # noqa: E402
    BRIDGE_X1,
    CHARLES_WALK_W,
    CHARLES_Y1,
    CHARLES_Y2,
    DORM_CX,
    DORM_NORTH_Y1,
    DORM_NORTH_Y2,
    DORM_SOUTH1_Y1,
    DORM_SOUTH2_Y2,
    DORM_X1,
    DORM_X2,
    ENNIS_HW,
    ENNIS_Y,
    FENCE_X1,
    KNOTT,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    KNOTT_DRIVEWAY_ES_X2,
    KNOTT_DRIVEWAY_Y1,
    ROAD_X2,
    SCALE,
    WALL_T,
    WORLD_X1,
    WORLD_X2_EXT,
    WORLD_Y1,
    WORLD_Y2,
)

# ── Real-world anchor ────────────────────────────────────────────────────────
ANCHOR_LAT = 39.3455
ANCHOR_LON = -76.6221
ANCHOR_X = 0  # Charles St centerline (ROAD_X1/ROAD_X2 straddle X=0)
ANCHOR_Y = CHARLES_Y1  # south end of modeled Charles St corridor

# Charles St's measured real-world compass bearing (great-circle bearing
# between two geocoded points ~4 km apart) — the direction +Y (Quake north)
# maps to in real-world terms. See docs/reference.rst SS Orientation.
BEARING_DEG = 354.5

EARTH_RADIUS_FT = 20_902_231  # mean Earth radius in feet

EPQS_URL = "https://epqs.nationalmap.gov/v1/json"

OUTPUT_CSV = Path(__file__).resolve().parent.parent / "docs" / "elevation_samples.csv"

# Road-cut baseline used throughout docs/reference.rst's Topology check
# (the bridge crossing's lowest point, ~296 ft) — samples are reported both
# as raw elevation and as feet above/below this baseline.
BASELINE_FT = 296.0


def quake_to_latlon(x, y):
    """Convert a Quake-space (X, Y) point to real-world (lat, lon).

    Offsets from the anchor are rotated by BEARING_DEG (the real-world
    compass bearing of +Y) and converted feet -> degrees via a flat-earth
    approximation (adequate at this scale, ~1500 ft max offset).
    """
    dx_units = x - ANCHOR_X
    dy_units = y - ANCHOR_Y
    dx_ft = dx_units / SCALE
    dy_ft = dy_units / SCALE

    theta = math.radians(BEARING_DEG)
    # +Y (Quake north) maps to compass bearing BEARING_DEG; +X (Quake east)
    # maps to BEARING_DEG + 90.
    north_ft = dy_ft * math.cos(theta) + dx_ft * math.cos(theta + math.pi / 2)
    east_ft = dy_ft * math.sin(theta) + dx_ft * math.sin(theta + math.pi / 2)

    dlat = math.degrees(north_ft / EARTH_RADIUS_FT)
    dlon = math.degrees(
        east_ft / (EARTH_RADIUS_FT * math.cos(math.radians(ANCHOR_LAT)))
    )
    return ANCHOR_LAT + dlat, ANCHOR_LON + dlon


def fetch_elevation_ft(lat, lon, retries=3):
    """Query USGS 3DEP Elevation Point Query Service for elevation in feet."""
    params = urllib.parse.urlencode(
        {"x": lon, "y": lat, "units": "Feet", "wkid": 4326, "includeDate": "false"}
    )
    url = f"{EPQS_URL}?{params}"
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                import json

                data = json.loads(resp.read())
                return float(data["value"])
        except (urllib.error.URLError, KeyError, ValueError) as exc:
            last_err = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch elevation for ({lat}, {lon}): {last_err}")


# ── Sample points ────────────────────────────────────────────────────────────
# label, X, Y, note
SAMPLE_POINTS = [
    # East-west cross-section at the bridge crossing (baseline)
    ("bridge_crossing_road", 0, 0, "road cut / bridge crossing, section baseline"),
    ("west_dorms_hilltop", -1400, 0, "west dorms local hilltop"),
    ("pier1_west_abutment", -1246, 0, "Pier 1 — bridge west abutment"),
    ("pier2_center_span_w", -525, 0, "Pier 2 — west end of curved centre span"),
    ("pier3_center_span_e", 525, 0, "Pier 3 — east end of curved centre span"),
    ("knott_west_edge", KNOTT.x1, 0, "Knott Hall west edge"),
    ("ennis_parallel", KNOTT.x2 + 500, ENNIS_Y, "Ennis Parallel, east of Knott Hall"),
    # Knott Hall west-edge -> Ennis Parallel eastward climb (Phase 3 survey)
    ("knott_climb_0", KNOTT.x1, ENNIS_Y, "Knott Hall west edge, at Ennis Y"),
    ("knott_climb_1", KNOTT.x1 + 90, ENNIS_Y, "~90 ft east of Knott Hall west edge"),
    ("knott_climb_2", KNOTT.x2, ENNIS_Y, "Knott Hall east edge"),
    ("knott_climb_3", KNOTT.x2 + 250, ENNIS_Y, "midway to Ennis Parallel"),
    ("knott_climb_4", KNOTT.x2 + 500, ENNIS_Y, "Ennis Parallel"),
    # North-south Charles St grade (Phase 2 survey)
    ("charles_south", 0, CHARLES_Y1, "Charles St south end (Cold Spring Ln, anchor)"),
    ("charles_s1", 0, CHARLES_Y1 + 900, "Charles St, 1/5 north"),
    ("charles_s2", 0, CHARLES_Y1 + 1800, "Charles St, 2/5 north"),
    ("charles_mid", 0, (CHARLES_Y1 + 1696) // 2, "Charles St midpoint"),
    ("charles_s4", 0, 900, "Charles St, 4/5 north"),
    ("charles_north", 0, 1696, "Charles St north end (CHARLES_Y2)"),
]

# South-terrain audit grid (Charles verge -> east driveway sidewalk edge,
# KH driveway Y1 -> world south edge) — added to spot-check the re-derived
# south extension / west ramp / south corner fill fills against real USGS
# elevation, independent of the hand-picked _far_south_z_west/_east sample
# columns already baked into knott_terrain.py.
_SOUTH_AUDIT_X = [
    400,
    700,
    900,
    KNOTT.x1,
    1650,
    2100,
    KNOTT.x2,
    2700,
    KNOTT_DRIVEWAY_ES_X2,
]
_SOUTH_AUDIT_Y = [
    WORLD_Y1 + WALL_T,
    -5500,
    -4500,
    -3500,
    -3000,
    -2400,
    KNOTT_DRIVEWAY_Y1,
]
for _sy in _SOUTH_AUDIT_Y:
    for _sx in _SOUTH_AUDIT_X:
        SAMPLE_POINTS.append(
            (f"south_audit_x{_sx}_y{_sy}", _sx, _sy, "south terrain audit grid")
        )

# West-campus audit grid (dorm buildings north/south1/south2 + bridge west
# approach, west_campus.py) — no terrain-fill module exists for this area
# yet (WEST_CAMPUS_ENABLED is currently False); these samples are gathered
# up front so a future west_campus_terrain.py can be built from real
# elevation data from the start, the way knott_terrain.py's south extension
# was re-derived this session, instead of guessing a slope and re-deriving
# later.
_WCAMPUS_AUDIT_X = [BRIDGE_X1, DORM_X1, DORM_CX, DORM_X2, FENCE_X1]
_WCAMPUS_AUDIT_Y = [
    CHARLES_Y2,
    DORM_NORTH_Y2,
    DORM_NORTH_Y1,
    500,
    0,
    DORM_SOUTH2_Y2,
    DORM_SOUTH1_Y1,
    CHARLES_Y1,
]
for _wy in _WCAMPUS_AUDIT_Y:
    for _wx in _WCAMPUS_AUDIT_X:
        SAMPLE_POINTS.append(
            (f"wcampus_audit_x{_wx}_y{_wy}", _wx, _wy, "west campus audit grid")
        )

# West-campus EXTENSION grids — the initial west_campus_terrain.py grid only
# spanned BRIDGE_X1..FENCE_X1, leaving flat FLOOR_Z2 (the unconditional
# streets.py world floor) on both sides — real elevation doesn't drop to 0
# right at either edge, so that produced two new cliffs. These extend the
# survey in both directions using the same _WCAMPUS_AUDIT_Y rows:
#   - East: FENCE_X1 -> Charles St (X=0), where the ground actually reaches
#     the flat plaza/road grade.
#   - West: BRIDGE_X1 -> the world's west wall (WORLD_X1+WALL_T).
_WCAMPUS_EAST_X = [-700, -400, -100, 0]
_WCAMPUS_WEST_X = [-2500, -3500, -4500, WORLD_X1 + WALL_T]
for _wy in _WCAMPUS_AUDIT_Y:
    for _wx in _WCAMPUS_EAST_X + _WCAMPUS_WEST_X:
        SAMPLE_POINTS.append(
            (f"wcampus_ext_x{_wx}_y{_wy}", _wx, _wy, "west campus extension grid")
        )

# West-campus SOUTH/NORTH extension — the modeled "CHARLES_Y1/CHARLES_Y2"
# corridor anchors (imported above) mark the *documented survey* corridor
# ends, but streets.py's actual Charles St sidewalk/curb geometry runs the
# full world Y range (WORLD_Y1+WALL_T .. WORLD_Y2-WALL_T) — much further
# both south and north. west_campus_terrain.py's grid stopping at
# CHARLES_Y1/Y2 left real cliffs at both seams. These rows extend the
# survey out to the true world edges, reusing the same X columns as the
# main audit/extension grids (ROAD_X1 itself is skipped — the terrain now
# ties flush to the existing curb/sidewalk height there instead of real
# data, so no ROAD_X1 sample is needed).
_WCAMPUS_FARY = [4069, 2800, -3800, -5200, -6626]
_WCAMPUS_FARX = [
    WORLD_X1 + WALL_T,
    -4500,
    -3500,
    -2500,
    BRIDGE_X1,
    DORM_X1,
    DORM_CX,
    DORM_X2,
    FENCE_X1,
    -700,
    -400,
]
for _wy in _WCAMPUS_FARY:
    for _wx in _WCAMPUS_FARX:
        SAMPLE_POINTS.append(
            (
                f"wcampus_far_x{_wx}_y{_wy}",
                _wx,
                _wy,
                "west campus north/south extension",
            )
        )

# NE quadrant grid (north of Ennis Road, east of Charles St) — the last
# unmodeled area. streets.py currently fills this whole rectangle with one
# flat placeholder box (flush with the Charles St sidewalk height), the
# same "placeholder until the real terrain module exists" pattern the west
# campus verge used before west_campus_terrain.py replaced it. Bounds match
# that placeholder box exactly: X from the east sidewalk/curb edge out to
# the true east world wall, Y from Ennis Road's north curb out to the true
# north world wall (see streets.py's locally-shadowed ENNIS_X2/CHARLES_Y2 —
# the true world edges, not the constants.py survey-corridor anchors).
_NE_X = [
    ROAD_X2 + CHARLES_WALK_W,
    900,
    1700,
    KNOTT_DRIVEWAY_CORRIDOR_X1,
    KNOTT_DRIVEWAY_CORRIDOR_X2,
    3472,  # _EAST_FEATURES_X2_EXT - WALL_T (old ENNIS_X2 anchor / gate-arch area)
    5000,
    7300,
    WORLD_X2_EXT - WALL_T,
]
_NE_Y = [
    ENNIS_Y + ENNIS_HW + CHARLES_WALK_W,
    1546,
    CHARLES_Y2,
    2200,
    2800,
    3450,
    WORLD_Y2 - WALL_T,
]
for _ny in _NE_Y:
    for _nx in _NE_X:
        SAMPLE_POINTS.append((f"ne_quad_x{_nx}_y{_ny}", _nx, _ny, "NE quadrant grid"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Recompute derived columns from the existing CSV without network access.",
    )
    args = parser.parse_args()

    rows = []
    elevations = {}
    cached = {}
    if OUTPUT_CSV.exists():
        with OUTPUT_CSV.open(newline="") as f:
            for row in csv.DictReader(f):
                cached[row["label"]] = row

    for label, x, y, _note in SAMPLE_POINTS:
        lat, lon = quake_to_latlon(x, y)
        if args.no_fetch and label in cached:
            elev_ft = float(cached[label]["elevation_ft"])
        else:
            elev_ft = fetch_elevation_ft(lat, lon)
            print(
                f"{label}: ({lat:.6f}, {lon:.6f}) -> {elev_ft:.2f} ft", file=sys.stderr
            )
        elevations[label] = elev_ft

    # Use this run's own measured bridge-crossing elevation as the baseline
    # (rather than the fixed BASELINE_FT from the earlier informal notes) so
    # values stay internally consistent with this script's anchor/bearing
    # assumptions, which are only an approximation of the original ad hoc
    # methodology (see module docstring).
    baseline_ft = elevations.get("bridge_crossing_road", BASELINE_FT)

    for label, x, y, note in SAMPLE_POINTS:
        lat, lon = quake_to_latlon(x, y)
        elev_ft = elevations[label]
        ft_above_baseline = elev_ft - baseline_ft
        z_units = round(ft_above_baseline * SCALE)
        rows.append(
            {
                "label": label,
                "x": x,
                "y": y,
                "lat": f"{lat:.6f}",
                "lon": f"{lon:.6f}",
                "elevation_ft": f"{elev_ft:.2f}",
                "ft_above_baseline": f"{ft_above_baseline:.2f}",
                "z_units_above_baseline": z_units,
                "note": note,
            }
        )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "label",
                "x",
                "y",
                "lat",
                "lon",
                "elevation_ft",
                "ft_above_baseline",
                "z_units_above_baseline",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} samples to {OUTPUT_CSV}", file=sys.stderr)


if __name__ == "__main__":
    main()
