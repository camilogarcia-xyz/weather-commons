# Notes

Working notes for sketch 41. Read this first. Date each entry, and move items to Done when they ship.

## Next

- Check with the AMS whether the 1961 figure can be published on the public site.
- Lab member: put the original GeoTIFF on Box with `node scripts/assets.mjs add 41 <path> --about "..."`.

## Decisions

- 2026-11-16: ERA5 every 6 hours for all of 1956, 0.25° squares, no smoothing. Rain = 6-hour total, gust = 6-hour max.
- 2026-11-16: ERA5 from Open-Meteo (cuts out just this area). Google's public ERA5 copy would mean about 50 GB of whole-globe downloads.
- 2026-11-16: map inverted (paper black, lines white) over a dark grey basemap; scientific colour scales.
- 2026-11-16: basemap from OpenStreetMap (no key), not CARTO.

## Questions

- Keep the sketch off the shared site until the AMS figure rights are checked. Merged only into Camilo's own copy for now.
- The question on the page is a draft written by Claude from the title. Camilo to rewrite it in their own words.
- Per-square uncertainty: ERA5 ensemble spread is on the Copernicus Climate Data Store (needs a free account and the host allowed). Add it?

## Done

- 2026-11-09: started from the template.
- 2026-11-09: first page: title, author, draft question, Sources and limits.
- 2026-11-16: replaced the synthetic wind with an interactive map: 1961 study zone map, ERA5 layer menu, 1956 time slider, uncertainty note. 
- 2026-11-16: ERA5 1956 downloaded from Open-Meteo: 7 layers, every 6 hours, no missing values. No CAPE for ERA5 on Open-Meteo.
- 2026-11-16: basemap switched from CARTO (now asks for an API key) to OpenStreetMap tiles, darkened with a CSS filter.
