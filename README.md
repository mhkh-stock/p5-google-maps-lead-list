# P5 — Google Maps Lead List (built the legal way)

**Area:** Gulberg, Lahore · **Niches:** cafes, restaurants, bakeries ·
**Sourced:** 1 Nov 2026 · **Status: SAMPLE delivery**
**Tools:** Python (stdlib urllib) · OpenStreetMap Nominatim API · SQLite · Excel
**Deliverable:** `outputs/leads_SAMPLE.xlsx` (74 leads)
**Database:** `data/processed/leads.db`

> ⚠️ **What this is and is not — read this first.** This lead list is
> **NOT scraped from Google Maps.** Scraping Google Maps breaks its
> terms of service, so this template never does it. The sample is
> sourced from **OpenStreetMap** (public data, ODbL licence, © OSM
> contributors) through its official Nominatim API, politely (1
> request/second, labelled User-Agent). The columns match the
> lead-list service spec — business, niche, phone, website, address,
> rating — and a real order fills the rating column from the
> **Google Places API with the client's own key**, never by inventing
> ratings. Here every rating honestly reads `n/a`, because OSM has no
> ratings.

## Business question it answers

> "Give me a list of businesses I can actually call, in this city and
> this niche."

A sales team that builds a call list by hand gets a handful of names
with stale numbers. This template pulls a whole area in one run,
stores every listing with its source link, and hands over a sortable
sheet — so the next run refreshes the list instead of rebuilding it.

## What is inside

| File | What it does |
|---|---|
| `outputs/leads_SAMPLE.xlsx` | The deliverable: Leads sheet (74 rows, Excel Table, filters on) + Summary sheet with live formulas + Read-me sheet |
| `data/processed/leads.db` | SQLite: `leads` (one row per OSM object) |
| `data/raw/leads_raw.json` | The raw API results, kept so the sheet can be audited back to source |
| `sql/schema.sql` | The leads schema |
| `src/fetch_leads.py` | The fetcher: Nominatim search per niche, details enrichment per listing, dedupe by OSM object |
| `src/build_excel.py` | Builds the Excel sheet from the database |
| `src/checks.py` | Data-quality checks as code — 11 checks, all passing |

## 3 key findings (from this sample)

1. **74 listings, 65 distinct names.** The 9 extra rows are not
   duplicates: same-name rows sit at different coordinates (e.g.
   Gourmet Bakers & Sweets ×3, Kitchen Cuisine ×3) — separate
   branches, each a real lead. *So what:* a lead list that dedupes
   by name alone would silently drop real branches; this one dedupes
   by OSM object instead.
2. **Contact info on OSM is thin — and that is the honest finding.**
   Only 5 of 74 listings carry a phone number and 4 carry a website.
   *So what:* a seller who promises "phone + website for every lead"
   from a free map source is overselling. The real service enriches
   contacts from the client's own sources or the Places API — the
   template says so in the package note instead of faking full
   coverage.
3. **Coverage is even across niches by design:** 25 cafes, 25
   bakeries, 24 restaurants (one restaurant search hit had no usable
   name and was dropped, not padded). *So what:* the fetcher takes a
   fixed cap per niche so no single niche crowds the list out.

## Verified numbers

| KPI | Value |
|---|---|
| Leads | 74 |
| Cafes / bakeries / restaurants | 25 / 25 / 24 |
| Distinct business names | 65 |
| With phone | 5 |
| With website | 4 |
| Ratings | all `n/a` (OSM has none — never invented) |
| Source date | 1 Nov 2026 |

Verification: `python3 src/checks.py` (11 checks pass) plus an
independent reopen of the Excel file — 74 rows, names matching the
database exactly, Summary totals as formulas.

## How to run it (under 5 steps)

1. Open `outputs/leads_SAMPLE.xlsx` — that is the deliverable.
2. To re-fetch: `python3 src/fetch_leads.py` (takes ~3 minutes at the
   polite 1 request/second rate; overwrites the database).
3. To rebuild the sheet: `python3 src/build_excel.py`.
4. To reuse it for a real client: change the niches and area in
   `src/fetch_leads.py`, and fill ratings/contacts from the Google
   Places API with the client's key — keep the schema, the Excel
   builder needs no changes.
5. To check the data: `python3 src/checks.py`.

## Tools

- Python 3 standard library only (the fetcher needs no pip installs)
- SQLite (lead store) · openpyxl (Excel builder only)

## Data source note

**OpenStreetMap data, fetched 1 Nov 2026** (© OpenStreetMap
contributors, ODbL 1.0). Business names, addresses and coordinates
belong to that public map. This sample is labelled SAMPLE because
the lead-list template — not the Gulberg listings — is what a client
buys.
