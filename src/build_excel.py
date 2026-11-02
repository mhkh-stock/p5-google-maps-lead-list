"""P5 — build the Excel lead list from the SQLite database."""
import sqlite3
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "data" / "processed" / "leads.db"
OUT = BASE / "outputs" / "leads_SAMPLE.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """SELECT business_name, niche, phone, website, address, city,
                  latitude, longitude, rating, osm_url
           FROM leads ORDER BY niche, business_name"""
    ).fetchall()
    summary = con.execute(
        """SELECT niche, COUNT(*),
                  SUM(CASE WHEN phone <> '' THEN 1 ELSE 0 END),
                  SUM(CASE WHEN website <> '' THEN 1 ELSE 0 END)
           FROM leads GROUP BY niche ORDER BY niche"""
    ).fetchall()
    con.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"
    headers = ["Business name", "Niche", "Phone", "Website", "Address",
               "City", "Latitude", "Longitude", "Rating (source)", "Source link"]
    ws.append(headers)
    for c in ws[1]:
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
    for r in rows:
        ws.append(list(r))
    ws.add_table(Table(displayName="Leads", ref=f"A1:J{1 + len(rows)}",
                       tableStyleInfo=TableStyleInfo(name="TableStyleMedium2")))
    widths = [30, 12, 18, 30, 70, 14, 12, 12, 14, 45]
    for col, w in zip("ABCDEFGHIJ", widths):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    sm = wb.create_sheet("Summary")
    sm.append(["Niche", "Leads", "With phone", "With website"])
    for c in sm[1]:
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
    for r in summary:
        sm.append(list(r))
    sm.append(["TOTAL", f"=SUM(B2:B{1 + len(summary)})",
               f"=SUM(C2:C{1 + len(summary)})", f"=SUM(D2:D{1 + len(summary)})"])
    for c in sm[1 + len(summary)]:
        c.font = Font(bold=True)
    sm.column_dimensions["A"].width = 14
    for col in "BCD":
        sm.column_dimensions[col].width = 14

    note = wb.create_sheet("Read me")
    note["A1"] = (
        "SAMPLE lead list — Gulberg, Lahore (cafes, restaurants, bakeries), "
        "sourced 1 Nov 2026 from OpenStreetMap (ODbL, (c) OSM contributors), "
        "NOT scraped from Google Maps. Ratings read 'n/a' because OSM has no "
        "ratings — they are never invented. Phone/website are blank where OSM "
        "has none; a real order enriches those fields from the client's own "
        "sources or the Google Places API (client's key). Same-name rows at "
        "different coordinates are separate branches, not duplicates."
    )
    from openpyxl.styles import Alignment
    note["A1"].alignment = Alignment(wrap_text=True, vertical="top")
    note.column_dimensions["A"].width = 110
    note.row_dimensions[1].height = 90

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"saved {OUT} with {len(rows)} leads")


if __name__ == "__main__":
    main()
