# 41 · Cloud seeding in Colombia

Author: Camilo · Started: 2026-11-09 · Status: sketch · Stack: static HTML + JS, Leaflet

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

- a dark grey basemap (CARTO, lighter than usual);
- the study zone map from the 1961 article, placed by its georeferencing (Web Mercator corners) and inverted: paper black, lines white;
- one ERA5 layer at a time, or none: precipitation, temperature, wind speed, wind gust, cloud cover, water vapour, CAPE (the energy available to storms) and sea-level pressure;
- a time slider through 1956, every 6 hours (1,464 times), with back and forward buttons.

Each ERA5 grid point is drawn as one 0.25° square (about 28 km), with no smoothing. Colours use scientific scales: one hue for amounts, two hues with a grey centre (the 1956 average for the area) for temperature and pressure. Ranges are fixed for the whole year (1st to 99th percentile), so a colour means the same on every date. Pointing at a square shows its value.

## 3. Situate

The zone runs from the Magdalena river and Barranquilla to the Sierra Nevada de Santa Marta and the César river. The banana zone lies on the Sierra's western slopes.

## 4. Narrate

The story in a few sentences. What can a viewer learn here, and what should they not conclude?

## Sources and limits

- **Study zone map** (cartographic, archival): Manuel E. López and Wallace E. Howell, "The Campaign Against Windstorms in the Banana Plantations Near Santa Marta, Colombia, 1956–57", *Bulletin of the American Meteorological Society* 42, no. 4 (April 1961): 265. © American Meteorological Society. Georeferenced by Camilo in Web Mercator (EPSG:3857), 164.9 m pixels, corners 75.04–72.81°W, 9.94–11.55°N. `tools/prepare_map.py` inverts it to `data/map-1961.png` without resampling. The GeoTIFF itself is not in git. **Permission to publish the figure: to check with the AMS.**
- **ERA5** (reanalysed): ERA5 hourly reanalysis, ECMWF / Copernicus Climate Change Service, licence CC BY 4.0. Served by the Open-Meteo historical weather API (`models=era5`, `elevation=nan` so no terrain correction, nearest grid point). 0.25° grid, 9.0–12.5°N, 76.0–72.0°W, 1956, every 6 hours. Precipitation is the 6-hour total, gust the 6-hour maximum, the rest the value at that time. Download date in `data/era5-1956.json`; made by `tools/fetch_era5.py`. **Not downloaded yet:** the session that built this could not reach Open-Meteo.
- **Basemap**: © OpenStreetMap contributors, © CARTO. Made lighter with a CSS filter.
- **Leaflet** 1.9.4 (BSD-2-Clause), copied into `lib/`.

Uncertainty: this download has no per-square uncertainty, so the page describes it for the whole layer, in its menu. 1956 is in ERA5's early years: no weather satellites, and few stations or weather balloons in northern Colombia. ERA5 rainfall and gusts are calculated by the model, not measured. ECMWF publishes an ERA5 ensemble spread (uncertainty per place and time, about 63 km) through the Copernicus Climate Data Store; it could be added later.

What this sketch cannot show: where or when clouds were seeded, or whether seeding changed anything. Each ERA5 square is wider than the banana zone, so storms, valleys and the Sierra's slopes are averaged inside it.
