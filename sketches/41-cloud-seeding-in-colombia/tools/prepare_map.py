"""Turn the georeferenced map (GeoTIFF) into an inverted PNG for the page.

Usage:
    python3 tools/prepare_map.py path/to/bams-1520-0477-42_4_265-2_modified.tif

Writes data/map-1961.png (paper black, lines white) and data/map-1961.json
(the corners in degrees, read from the GeoTIFF tags). Needs Pillow only.

The GeoTIFF is in Web Mercator (EPSG:3857), the same projection as the web map,
so the four corners place it exactly. The pixels are not resampled.
"""

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent.parent
R = 6378137.0  # Web Mercator sphere radius, metres


def lon(x):
    return math.degrees(x / R)


def lat(y):
    return math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)


def main(src):
    im = Image.open(src)
    tags = im.tag_v2
    geokeys = tags.get(34735)
    if geokeys is None or 3857 not in geokeys:
        sys.exit("Expected a GeoTIFF in EPSG:3857 (WGS 84 / Pseudo-Mercator).")
    sx, sy, _ = tags[33550]                 # pixel size in metres
    _, _, _, x0, y0, _ = tags[33922]        # top-left corner in metres
    w, h = im.size
    x1, y1 = x0 + w * sx, y0 - h * sy

    # Invert: dark ink becomes white, white paper becomes black.
    grey = ImageOps.invert(im.convert("L"))
    # Push the faint paper tone to pure black and stretch the lines to full white.
    floor = 24
    grey = grey.point(lambda v: 0 if v <= floor else round((v - floor) * 255 / (255 - floor)))

    out = HERE / "data"
    out.mkdir(exist_ok=True)
    grey.save(out / "map-1961.png", optimize=True)
    corners = {
        "about": "Corners of map-1961.png in degrees (WGS 84), from the GeoTIFF tags (EPSG:3857).",
        "west": round(lon(x0), 6), "east": round(lon(x1), 6),
        "south": round(lat(y1), 6), "north": round(lat(y0), 6),
        "width_px": w, "height_px": h, "pixel_m": round(sx, 3),
    }
    (out / "map-1961.json").write_text(json.dumps(corners, indent=2) + "\n")
    print(corners)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
