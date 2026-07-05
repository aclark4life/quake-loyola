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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quake_loyola.constants import CHARLES_Y1, ENNIS_Y, KNOTT, SCALE  # noqa: E402

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

    for label, x, y, note in SAMPLE_POINTS:
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
