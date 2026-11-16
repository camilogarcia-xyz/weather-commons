"""Download ERA5 for 1956 around the Sierra Nevada de Santa Marta and pack it for the page.

Usage:
    python3 tools/fetch_era5.py

Source: ERA5 hourly reanalysis (ECMWF / Copernicus Climate Change Service), served
by the Open-Meteo historical weather API (https://open-meteo.com/en/docs/historical-weather-api)
with models=era5. No account or key. Standard library only.

What it does:
- asks for every ERA5 grid point (0.25 degrees) from 9.0 to 12.5 N and 76.0 to 72.0 W,
  hour by hour from 1955-12-31 to 1956-12-31 (UTC);
- sets elevation=nan, so Open-Meteo does not correct temperature for terrain height
  and returns the ERA5 grid cell's own value;
- checks that each answer comes from the requested grid point;
- builds one frame every 6 hours (00, 06, 12, 18 UTC):
    precipitation   total of the 6 hours ending at the frame time
    wind gust       highest hourly gust in the 6 hours ending at the frame time
    all others      the value at the frame time
- no spatial smoothing or interpolation: one value per ERA5 cell.

Writes data/era5-1956.json (grid, times, units, scales) and one
data/era5-1956-<variable>.bin per variable: little-endian int16,
value = stored * scale + offset, -32768 = missing, ordered [time][row][col],
row 0 = northernmost.
"""

import json
import math
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "tools" / "cache"          # raw answers, ignored by git (see .gitignore)
OUT = HERE / "data"

STEP = 0.25
NORTH, SOUTH, WEST, EAST = 12.5, 9.0, -76.0, -72.0
LATS = [round(NORTH - i * STEP, 2) for i in range(int(round((NORTH - SOUTH) / STEP)) + 1)]
LONS = [round(WEST + j * STEP, 2) for j in range(int(round((EAST - WEST) / STEP)) + 1)]

START, END = "1955-12-31", "1956-12-31"
FRAME_HOURS = 6
BATCH = 15          # grid points per request
PAUSE = 8           # seconds between requests, to stay inside the free API limits

# key: (Open-Meteo name, label, unit, how a 6-hour frame is made, scale, offset)
VARIABLES = {
    "precipitation": ("precipitation", "Precipitation, 6-hour total", "mm", "sum", 0.01, 0.0),
    "temperature": ("temperature_2m", "Temperature at 2 m", "°C", "now", 0.01, 0.0),
    "wind": ("wind_speed_10m", "Wind speed at 10 m", "m/s", "now", 0.01, 0.0),
    "gust": ("wind_gusts_10m", "Wind gust at 10 m, 6-hour maximum", "m/s", "max", 0.01, 0.0),
    "cloud": ("cloud_cover", "Total cloud cover", "%", "now", 0.01, 0.0),
    "vapour": ("total_column_integrated_water_vapour", "Water vapour in the air column", "kg/m²", "now", 0.01, 0.0),
    "cape": ("cape", "Convective available potential energy (CAPE)", "J/kg", "now", 1.0, 0.0),
    "pressure": ("pressure_msl", "Pressure at sea level", "hPa", "now", 0.01, 1000.0),
}


def request(points):
    q = {
        "latitude": ",".join(f"{la}" for la, _ in points),
        "longitude": ",".join(f"{lo}" for _, lo in points),
        "elevation": ",".join("nan" for _ in points),
        "start_date": START,
        "end_date": END,
        "hourly": ",".join(v[0] for v in VARIABLES.values()),
        "models": "era5",
        "timezone": "GMT",
        "wind_speed_unit": "ms",
        "cell_selection": "nearest",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(q)
    for attempt in range(8):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                data = json.load(r)
            return data if isinstance(data, list) else [data]
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code == 429 or e.code >= 500:
                wait = 60 * (attempt + 1)
                print(f"  {e.code}, waiting {wait} s: {body}", flush=True)
                time.sleep(wait)
                continue
            sys.exit(f"Open-Meteo refused the request ({e.code}): {body}")
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 15 * (attempt + 1)
            print(f"  network problem ({e}), waiting {wait} s", flush=True)
            time.sleep(wait)
    sys.exit("Open-Meteo did not answer after several tries. Run the script again; it resumes.")


def fetch_all():
    CACHE.mkdir(parents=True, exist_ok=True)
    points = [(la, lo) for la in LATS for lo in LONS]
    batches = [points[i:i + BATCH] for i in range(0, len(points), BATCH)]
    for n, batch in enumerate(batches):
        path = CACHE / f"batch-{n:03d}.json"
        if path.exists():
            continue
        print(f"batch {n + 1}/{len(batches)}", flush=True)
        answers = request(batch)
        if len(answers) != len(batch):
            sys.exit(f"Expected {len(batch)} answers, got {len(answers)}.")
        for (la, lo), a in zip(batch, answers):
            # Open-Meteo reports the grid point it used. It must be the one we asked for.
            if abs(a["latitude"] - la) > 0.02 or abs(a["longitude"] - lo) > 0.02:
                sys.exit(f"Asked for {la},{lo} but got {a['latitude']},{a['longitude']}.")
            a["requested"] = [la, lo]
        path.write_text(json.dumps(answers))
        time.sleep(PAUSE)
    cells = {}
    for n in range(len(batches)):
        for a in json.loads((CACHE / f"batch-{n:03d}.json").read_text()):
            cells[tuple(a["requested"])] = a
    return cells


def build(cells):
    first = next(iter(cells.values()))
    hours = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in first["hourly"]["time"]]
    index = {h: i for i, h in enumerate(hours)}
    t0 = datetime(1956, 1, 1, tzinfo=timezone.utc)
    frames = []
    t = t0
    while t.year == 1956:
        frames.append(t)
        t += timedelta(hours=FRAME_HOURS)

    meta = {
        "about": "ERA5 hourly reanalysis (ECMWF / Copernicus Climate Change Service), via the Open-Meteo "
                 "historical weather API (models=era5, elevation=nan), downloaded "
                 + datetime.now(timezone.utc).strftime("%Y-%m-%d") + ". Made by tools/fetch_era5.py.",
        "kind": "reanalysed",
        "grid": {"north": NORTH, "south": SOUTH, "west": WEST, "east": EAST, "step": STEP,
                 "rows": len(LATS), "cols": len(LONS),
                 "note": "Values are for grid points; each is drawn as a 0.25-degree square centred on its point."},
        "frames": [f.strftime("%Y-%m-%dT%H:%MZ") for f in frames],
        "frame_hours": FRAME_HOURS,
        "elevation_m": [[cells[(la, lo)].get("elevation") for lo in LONS] for la in LATS],
        "variables": {},
    }

    OUT.mkdir(exist_ok=True)
    for key, (name, label, unit, how, scale, offset) in VARIABLES.items():
        if name not in first["hourly"]:
            print(f"skip {key}: Open-Meteo has no {name} for ERA5", flush=True)
            continue
        stored, lo_v, hi_v, missing = [], math.inf, -math.inf, 0
        for f in frames:
            end = index[f]
            for la in LATS:
                for lo in LONS:
                    series = cells[(la, lo)]["hourly"][name]
                    if how == "now":
                        window = [series[end]]
                    else:
                        window = series[end - FRAME_HOURS + 1:end + 1]
                    if any(v is None for v in window):
                        stored.append(-32768)
                        missing += 1
                        continue
                    v = sum(window) if how == "sum" else max(window) if how == "max" else window[0]
                    lo_v, hi_v = min(lo_v, v), max(hi_v, v)
                    q = round((v - offset) / scale)
                    if not -32767 <= q <= 32767:
                        sys.exit(f"{key}: {v} does not fit the chosen scale.")
                    stored.append(q)
        if missing == len(stored):
            print(f"skip {key}: no values", flush=True)
            continue
        (OUT / f"era5-1956-{key}.bin").write_bytes(struct.pack(f"<{len(stored)}h", *stored))
        meta["variables"][key] = {
            "file": f"data/era5-1956-{key}.bin", "source_name": name, "label": label, "unit": unit,
            "frame": {"sum": "total of the 6 hours ending at the frame time",
                      "max": "highest hourly value in the 6 hours ending at the frame time",
                      "now": "value at the frame time"}[how],
            "scale": scale, "offset": offset, "min": lo_v, "max": hi_v, "missing": missing,
        }
        print(f"{key}: {lo_v:.2f} to {hi_v:.2f} {unit}, {missing} missing", flush=True)
    (OUT / "era5-1956.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    build(fetch_all())
