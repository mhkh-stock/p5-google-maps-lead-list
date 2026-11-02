"""P5 — Lead list builder (SAMPLE).

Source: OpenStreetMap via the Nominatim search + details APIs.
Licence: ODbL 1.0, (c) OpenStreetMap contributors.

Why OSM and not Google Maps scraping: scraping Google Maps breaks its
terms of service, so this template does NOT scrape it. The columns match
the lead-list service spec (business, niche, phone, website, address),
and a real order fills the rating column from the Google Places API
(with the client's own API key) instead of inventing ratings. OSM has
no ratings, so the rating column here honestly reads "n/a".

Politeness: Nominatim's usage policy = max 1 request/second, with a
descriptive User-Agent. This script sleeps 1.1s between calls.
"""
import json
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw" / "leads_raw.json"
DB = BASE / "data" / "processed" / "leads.db"
SCHEMA = BASE / "sql" / "schema.sql"

UA = "hasho-portfolio-sample-p5/1.0 (portfolio demo; contact: portfolio sample)"
QUERIES = [
    ("cafe", "cafe in Gulberg, Lahore, Pakistan"),
    ("restaurant", "restaurant in Gulberg, Lahore, Pakistan"),
    ("bakery", "bakery in Gulberg, Lahore, Pakistan"),
]
PER_QUERY = 25


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search(query):
    params = urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": PER_QUERY, "addressdetails": 1}
    )
    return get_json(f"https://nominatim.openstreetmap.org/search?{params}")


def details(osm_type, osm_id):
    params = urllib.parse.urlencode(
        {
            "osmtype": osm_type[0].upper(),
            "osmid": osm_id,
            "format": "json",
            "addressdetails": 1,
            "extratags": 1,
        }
    )
    return get_json(f"https://nominatim.openstreetmap.org/details?{params}")


def pick(d, *keys):
    for k in keys:
        if d.get(k):
            return d[k]
    return ""


def main():
    seen = {}
    for niche, q in QUERIES:
        results = search(q)
        print(f"{niche}: {len(results)} search hits")
        for r in results:
            key = (r["osm_type"], r["osm_id"])
            if key not in seen:
                seen[key] = {"niche": niche, "search": r}
        time.sleep(1.1)

    leads = []
    for (osm_type, osm_id), item in seen.items():
        try:
            det = details(osm_type, osm_id)
        except Exception as exc:  # details are enrichment, not fatal
            print(f"details failed for {osm_type}/{osm_id}: {exc}")
            det = {}
        extra = det.get("extratags", {}) or {}
        s = item["search"]
        addr = s.get("address", {}) or {}
        leads.append(
            {
                "business_name": s.get("name") or det.get("localname") or "",
                "niche": item["niche"],
                "phone": pick(extra, "phone", "contact:phone"),
                "website": pick(extra, "website", "contact:website"),
                "address": s.get("display_name", ""),
                "city": addr.get("city") or addr.get("town") or addr.get("county") or "",
                "latitude": s.get("lat", ""),
                "longitude": s.get("lon", ""),
                "rating": "n/a",
                "osm_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
            }
        )
        time.sleep(1.1)

    leads = [x for x in leads if x["business_name"]]
    leads.sort(key=lambda x: (x["niche"], x["business_name"].lower()))
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(leads, indent=2, ensure_ascii=False), encoding="utf-8")

    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA.read_text())
    con.executemany(
        """INSERT INTO leads (business_name, niche, phone, website, address,
           city, latitude, longitude, rating, osm_url)
           VALUES (:business_name, :niche, :phone, :website, :address,
           :city, :latitude, :longitude, :rating, :osm_url)""",
        leads,
    )
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    con.close()
    print(f"leads saved: {n} -> {DB}")
    print(f"with phone: {sum(1 for x in leads if x['phone'])}; "
          f"with website: {sum(1 for x in leads if x['website'])}")


if __name__ == "__main__":
    main()
