# Notes

Working notes for sketch 41. Read this first. Date each entry, and move items to Done when they ship.

## Next

- Download ERA5 with `python3 tools/fetch_era5.py` once archive-api.open-meteo.com is allowed in the session's network settings, then commit `data/era5-1956*`.
- Check with the AMS whether the 1961 figure can be published on the public site.
- Lab member: put the original GeoTIFF on Box with `node scripts/assets.mjs add 41 <path> --about "..."`.

## Decisions

- 2026-11-16: ERA5 every 6 hours for all of 1956, 0.25° squares, no smoothing. Rain = 6-hour total, gust = 6-hour max.
- 2026-11-16: ERA5 from Open-Meteo (cuts out just this area). Google's public ERA5 copy would mean about 50 GB of whole-globe downloads.
- 2026-11-16: map inverted (paper black, lines white) over a dark grey basemap; scientific colour scales.

## Questions

- The question on the page is a draft written by Claude from the title. Camilo to rewrite it in their own words.
- Per-square uncertainty: ERA5 ensemble spread is on the Copernicus Climate Data Store (needs a free account and the host allowed). Add it?

## Done

- 2026-11-09: started from the template.
- 2026-11-09: first page: title, author, draft question, Sources and limits.
- 2026-11-16: replaced the synthetic wind with an interactive map: 1961 study zone map, ERA5 layer menu, 1956 time slider, uncertainty note. Waiting for the ERA5 download.
