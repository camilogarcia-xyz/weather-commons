# 41 · Cloud seeding in Colombia

Author: Camilo · Started: 2026-11-09 · Status: sketch · Stack: static HTML + JS, Leaflet, CesiumJS

A map of the 1956–57 campaign against windstorms near Santa Marta, with ERA5 weather for 1956 laid over it. It asks: who decides when and where clouds are seeded in Colombia, and who lives with the rain that falls, or doesn't fall, as a result?

## Run

Online, once published: `https://camilogarcia-xyz.github.io/weather-commons/41-cloud-seeding-in-colombia/`

On your computer:

```bash
cd sketches/41-cloud-seeding-in-colombia
python -m http.server 8000
```

Then open http://localhost:8000.

To rebuild the data (Python 3; `prepare_map.py` needs Pillow):

```bash
python3 tools/prepare_map.py path/to/bams-1520-0477-42_4_265-2_modified.tif
python3 tools/fetch_era5.py
```

## 1. Event

In 1956 and 1957, W. E. Howell Associates ran a cloud-seeding campaign against windstorms in the banana plantations near Santa Marta, on the Caribbean coast of Colombia (López and Howell, 1961). This sketch starts from the study zone map in their article.

## 2. Simulate

An interactive map, with limited pan and zoom:

- a dark grey basemap (OpenStreetMap's standard tiles, turned grey and inverted);
- the study zone map from the 1961 article, placed by its georeferencing (Web Mercator corners) and inverted: paper black, lines white;
- one ERA5 layer at a time, or none: precipitation, temperature, wind speed, wind gust, cloud cover, water vapour and sea-level pressure (Open-Meteo has no CAPE, the energy available to storms, for ERA5 in 1956);
- a time slider through 1956, every 6 hours (1,464 times), with back and forward buttons.

Each ERA5 grid point is drawn as one 0.25° square (about 28 km), with no smoothing. Colours use scientific scales: one hue for amounts, two hues with a grey centre (the 1956 average for the area) for temperature and pressure. Ranges are fixed for the whole year (1st to 99th percentile), so a colour means the same on every date. Pointing at a square shows its value.

### Simulate v2: 3D

The same map and data on a 3D globe (CesiumJS, loaded from the jsDelivr CDN when the section comes into view):

- terrain from Re:Earth Terrain (no key needed), true scale;
- the 1961 map laid straight down onto the terrain (`data/map-1961-geo.png`, re-mapped from Web Mercator to even steps of latitude so it sits exactly at its georeferenced place);
- OpenStreetMap tiles, grey and darkened, around it;
- ERA5 as a sky of flat, see-through 0.25° squares at 5,000 m, with the same menu, time slider and colours as the 2D map;
- the view starts at 700 m over the Ciénaga Grande, west of the banana zone, looking east to the Sierra Nevada; you can move within about 0.6° of the map and up to 60 km high, never below the ground.

OpenTopography's SRTM 30 m was the first plan; it needs an account key and processing. Re:Earth Terrain was simpler and needs neither.

## 3. Situate

The zone runs from the Magdalena river and Barranquilla to the Sierra Nevada de Santa Marta and the César river. The banana zone lies on the Sierra's western slopes.

## 4. Narrate

The story in a few sentences. What can a viewer learn here, and what should they not conclude?

## Sources and limits

- **Study zone map** (cartographic, archival): Manuel E. López and Wallace E. Howell, "The Campaign Against Windstorms in the Banana Plantations Near Santa Marta, Colombia, 1956–57", *Bulletin of the American Meteorological Society* 42, no. 4 (April 1961): 265. © American Meteorological Society. Georeferenced by Camilo in Web Mercator (EPSG:3857), 164.9 m pixels, corners 75.04–72.81°W, 9.94–11.55°N. `tools/prepare_map.py` inverts it to `data/map-1961.png` without resampling. The GeoTIFF itself is not in git. The top of the page also shows five screenshots of the article (pages 265–274: abstract, Fig. 2 and Table 2, Fig. 4, section 6 on the seeding programme, Fig. 5), in `img/`, for discussion. **Permission to publish the figure and the screenshots: to check with the AMS.**
- **ERA5** (reanalysed): ERA5 hourly reanalysis, ECMWF / Copernicus Climate Change Service, licence CC BY 4.0. Served by the Open-Meteo historical weather API (`models=era5`, `elevation=nan` so no terrain correction, nearest grid point). 0.25° grid, 9.0–12.5°N, 76.0–72.0°W, 1956, every 6 hours. Precipitation is the 6-hour total, gust the 6-hour maximum, the rest the value at that time. Downloaded 2026-11-16 with `tools/fetch_era5.py`; details in `data/era5-1956.json`. Stored as 16-bit numbers (0.01 precision), checked against a direct request.
- **Basemap**: © OpenStreetMap contributors (ODbL), standard tiles from tile.openstreetmap.org, no key needed. Turned grey and inverted with a CSS filter. CARTO's dark tiles were used at first but now ask for a key.
- **Leaflet** 1.9.4 (BSD-2-Clause), copied into `lib/`.
- **Terrain (Simulate v2)** (observed, recent decades, not 1956): Re:Earth Terrain, https://terrain.reearth.land/ (code MIT), tileset `mapterhorn-egm08`: the Mapterhorn global elevation model, a blend of public elevation datasets (CC BY 4.0), with EGM2008 geoid heights (NGA). Which datasets and resolution apply here: to check. Loaded live, more detail as you zoom in; from far away peaks are averaged (the Sierra shows about 5,340 m, the real summit about 5,700 m). A young free service with no guarantee it stays up.
- **CesiumJS** 1.146.0 (Apache-2.0), from the jsDelivr CDN. Sky at 5,000 m above the WGS 84 ellipsoid (within about 10 m of sea level here).

Uncertainty: this download has no per-square uncertainty, so the page describes it for the whole layer, in its menu. 1956 is in ERA5's early years: no weather satellites, and few stations or weather balloons in northern Colombia. ERA5 rainfall and gusts are calculated by the model, not measured, and ERA5 tends to give too much rain over steep tropical mountains: some squares in the Sierra and the Andes reach over 8,000 mm for 1956. ECMWF publishes an ERA5 ensemble spread (uncertainty per place and time, about 63 km) through the Copernicus Climate Data Store; it could be added later.

What this sketch cannot show: where or when clouds were seeded, or whether seeding changed anything. Each ERA5 square is wider than the banana zone, so storms, valleys and the Sierra's slopes are averaged inside it.
