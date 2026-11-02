# P5 — data note

## Source

OpenStreetMap via the Nominatim search + details APIs, fetched
1 Nov 2026. Licence: ODbL 1.0, © OpenStreetMap contributors.
Polite use: 1 request/second, labelled User-Agent, per Nominatim's
usage policy. No Google Maps scraping anywhere in this project.

## Files

- `raw/leads_raw.json` — the fetcher's output (74 listings), kept so
  the sheet audits back to source.
- `processed/leads.db` — SQLite `leads` table built from the raw JSON
  (schema in `../sql/schema.sql`).

## Coverage honesty

Phone present for 5/74 listings, website for 4/74, ratings for 0/74 —
that is what OSM actually holds for this area, not a gap in the
fetcher. A real order enriches contacts and ratings from the
client's own sources / the Google Places API (client's key); the
template's columns already have room for them.
